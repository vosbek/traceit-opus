from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List
import traceback
import time

# Import the enhanced agent
from orchestrators.answer_agent import AnswerAgent, plan

app = FastAPI(title="Legacy Codebase Assistant", version="2.0")

class RunRequest(BaseModel):
    query: str

class CitationResponse(BaseModel):
    type: str  # "code", "sql", "doc"
    path: str
    lines: List[int] = [1, 1]
    repo: str = ""
    sha: str = ""
    source_env: str = "legacy"
    content_preview: str = ""

class StepResponse(BaseModel):
    step_name: str
    duration_ms: int
    input_summary: str
    output_summary: str
    hit_count: int = 0

class RunResponse(BaseModel):
    thread_id: str = "local"
    final_answer: str
    citations: List[CitationResponse]
    steps: List[StepResponse]
    graph: Dict[str, Any] = {"nodes": [], "edges": []}
    raw_state: Dict[str, Any]

@app.post("/api/run", response_model=RunResponse)
def run_query(req: RunRequest):
    """Execute a query using the Strands agent with multi-step reasoning."""
    
    start_time = time.time()
    
    try:
        # Initialize agent
        agent = AnswerAgent()
        
        # Execute the plan
        result_message = agent.run(plan, req.query)
        
        # Extract information from agent execution
        final_answer = result_message.content if result_message else "No answer generated"
        
        # Get metadata from final message
        metadata = result_message.metadata if hasattr(result_message, 'metadata') and result_message.metadata else {}
        
        # Build citations from evidence
        citations = build_citations(metadata)
        
        # Build step trace from agent memory
        steps = build_step_trace(agent)
        
        # Build raw state for compatibility
        raw_state = {
            "hits": metadata.get("hits", []),
            "db_results": metadata.get("db_results"),
            "sql_query": metadata.get("sql_query"),
            "evidence_sufficient": metadata.get("evidence_sufficient", True),
            "execution_time_ms": int((time.time() - start_time) * 1000)
        }
        
        return RunResponse(
            final_answer=final_answer,
            citations=citations,
            steps=steps,
            raw_state=raw_state
        )
        
    except Exception as e:
        # Log the full error for debugging
        error_trace = traceback.format_exc()
        print(f"Error executing query: {error_trace}")
        
        # Return error response
        return RunResponse(
            final_answer=f"Error processing query: {str(e)}",
            citations=[],
            steps=[],
            raw_state={"error": str(e), "trace": error_trace}
        )

def build_citations(metadata: Dict[str, Any]) -> List[CitationResponse]:
    """Build citation list from agent metadata."""
    citations = []
    
    # Add code citations
    hits = metadata.get("hits", [])
    for hit in hits[:10]:  # Limit to top 10
        path = hit.get("path") or hit.get("id", "")
        
        # Determine citation type
        if path.endswith((".java", ".jsp", ".jspf", ".xml")):
            citation_type = "code"
        elif path.endswith((".sql", ".ddl")):
            citation_type = "sql"
        else:
            citation_type = "doc"
        
        # Get content preview
        content = hit.get("text", "")
        preview = content[:150] + "..." if len(content) > 150 else content
        
        citations.append(CitationResponse(
            type=citation_type,
            path=path,
            repo=hit.get("repo", ""),
            sha=hit.get("sha", ""),
            content_preview=preview
        ))
    
    # Add database citation if SQL was executed
    if metadata.get("sql_query"):
        citations.append(CitationResponse(
            type="sql",
            path="Oracle Database Query",
            content_preview=metadata.get("sql_query", "")[:150]
        ))
    
    return citations

def build_step_trace(agent: AnswerAgent) -> List[StepResponse]:
    """Build execution step trace from agent memory."""
    steps = []
    
    if hasattr(agent, 'memory') and agent.memory:
        step_count = {}
        
        for message in agent.memory.messages:
            # Identify step based on content patterns
            content = message.content or ""
            
            if "Query analysis:" in content:
                step_name = "analyze_query"
            elif "CODE EVIDENCE" in content:
                step_name = "search_codebase"
            elif "DATABASE EVIDENCE" in content:
                step_name = "query_database"
            elif "SUPPORTING EVIDENCE" in content or message.metadata.get("final"):
                step_name = "synthesize_answer"
            else:
                continue
            
            # Count occurrences of each step
            step_count[step_name] = step_count.get(step_name, 0) + 1
            
            # Get hit count from metadata
            hit_count = 0
            if hasattr(message, 'metadata') and message.metadata:
                hits = message.metadata.get("code_hits", [])
                db_results = message.metadata.get("db_results", {})
                hit_count = len(hits) + (len(db_results.get("rows", [])) if db_results else 0)
            
            steps.append(StepResponse(
                step_name=step_name,
                duration_ms=500,  # Placeholder - real timing would need instrumentation
                input_summary=f"Processing {step_name}",
                output_summary=content[:100] + "..." if len(content) > 100 else content,
                hit_count=hit_count
            ))
    
    return steps

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "legacy-codebase-assistant"}

@app.get("/")
def root():
    """Root endpoint with service info."""
    return {
        "service": "Legacy Codebase Assistant",
        "version": "2.0",
        "description": "Strands-powered assistant for legacy codebase questions",
        "endpoints": ["/api/run", "/api/health"]
    }

# Enable CORS for development
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
