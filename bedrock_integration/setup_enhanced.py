directory(doc_path)
        print(f"    Indexed {doc_results['indexed']} documents")
    
    # Index CORBA IDLs
    idl_path = os.getenv("IDL_PATH")
    if idl_path and Path(idl_path).exists():
        print(f"\n  🔌 Indexing CORBA IDLs at {idl_path}...")
        for idl_file in Path(idl_path).rglob("*.idl"):
            print(f"    Analyzing {idl_file.name}...")
            corba_analyzer.analyze_idl_file(idl_file)
    
    print("\n✅ Indexing complete!")

def create_api_wrapper():
    """Create enhanced API wrapper for the orchestrator."""
    print("\n🌐 Creating enhanced API wrapper...")
    
    api_file = Path("api/enhanced_strands_app.py")
    api_file.parent.mkdir(exist_ok=True)
    
    api_content = '''#!/usr/bin/env python3
"""
Enhanced Strands API with Bedrock integration.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from bedrock_integration.enhanced_orchestrator import MasterOrchestrator
from bedrock_integration.codebase_training_system import CodebasePatternLearner
from strands.types import Message
from opensearchpy import OpenSearch
from neo4j import GraphDatabase

app = FastAPI(title="Legacy Codebase Assistant - Enhanced with Bedrock")

# Initialize connections
os_client = OpenSearch(
    hosts=[os.getenv("OPENSEARCH_URL", "http://localhost:9200")],
    http_compress=True
)

neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URL", "bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASS", "password"))
)

# Initialize orchestrator
orchestrator = MasterOrchestrator(os_client, neo4j_driver)

class Query(BaseModel):
    query: str

class FeedbackRequest(BaseModel):
    query_id: str
    helpful: bool
    comments: str = ""

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "enhanced": True, "bedrock": True}

@app.post("/api/run")
async def run_query(request: Query):
    """
    Execute enhanced query with Bedrock integration.
    """
    try:
        # Create initial message
        initial_message = Message(role="user", content=request.query)
        
        # Execute through orchestrator steps
        orchestrator.memory = []  # Reset memory for new query
        
        # Run each step
        steps = [
            "analyze_and_optimize_query",
            "search_codebase_enhanced",
            "search_jars_if_needed",
            "query_database_smart",
            "search_documentation",
            "check_corba_interfaces",
            "synthesize_comprehensive_answer"
        ]
        
        current_message = initial_message
        step_results = []
        
        for step_name in steps:
            step_method = getattr(orchestrator, step_name)
            result = step_method(current_message)
            
            step_results.append({
                "step_name": step_name,
                "duration_ms": result.metadata.get("execution_time", 0) * 1000,
                "hit_count": len(result.metadata.get("code_hits", []))
            })
            
            current_message = result
            orchestrator.memory.append(result)
        
        # Extract final answer
        final_metadata = current_message.metadata
        
        return {
            "final_answer": final_metadata.get("final_answer", "No answer generated"),
            "citations": final_metadata.get("citations", []),
            "confidence": final_metadata.get("confidence", 0),
            "query_id": final_metadata.get("query_id", ""),
            "execution_time": final_metadata.get("execution_time", 0),
            "steps": step_results,
            "evidence_sources": final_metadata.get("evidence_sources", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for continuous improvement.
    """
    try:
        # Record feedback
        orchestrator.pattern_learner.record_feedback(
            request.query_id,
            "",  # Query will be looked up from history
            "",  # Answer will be looked up from history
            request.helpful,
            request.comments
        )
        
        return {"status": "feedback_recorded", "query_id": request.query_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """
    Get system metrics and performance data.
    """
    return {
        "orchestrator_metrics": orchestrator.metrics,
        "feedback_summary": orchestrator.pattern_learner.get_feedback_summary()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open(api_file, 'w') as f:
        f.write(api_content)
    
    print(f"  ✅ Created {api_file}")

def create_test_suite():
    """Create comprehensive test suite."""
    print("\n🧪 Creating test suite...")
    
    test_file = Path("test_enhanced_mvp.py")
    
    test_content = '''#!/usr/bin/env python3
"""
Enhanced test suite for Bedrock-integrated system.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

# Enhanced golden questions that test all components
TEST_CASES = [
    {
        "query": "What query against IWDB will retrieve all the static Items associated with a given username from users table?",
        "expected_keywords": ["SELECT", "users", "ssc_group_users", "items", "contextual_rules"],
        "expected_sources": ["database", "code"]
    },
    {
        "query": "Where does the 'Specified Amount' field get its data from in the database?",
        "expected_keywords": ["agreement_values", "DEATH BENEFIT AMOUNT", "cppf"],
        "expected_sources": ["database", "documentation"]
    },
    {
        "query": "What business validation rules exist for calculating premium amounts?",
        "expected_keywords": ["validation", "premium", "calculate", "rule"],
        "expected_sources": ["jar", "business_rules", "code"]
    },
    {
        "query": "Show me the CORBA interfaces for policy management services",
        "expected_keywords": ["interface", "policy", "operation", "CORBA"],
        "expected_sources": ["corba", "code"]
    },
    {
        "query": "What JSP files handle the display of Universal Life contract options?",
        "expected_keywords": ["jsp", "contractOptions", "Universal Life", "display"],
        "expected_sources": ["code", "documentation"]
    }
]

def test_enhanced_query(test_case):
    """Test a single enhanced query."""
    print(f"\\n{'='*60}")
    print(f"Testing: {test_case['query'][:80]}...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE}/api/run",
            json={"query": test_case["query"]},
            timeout=60  # Longer timeout for Bedrock
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
        
        result = response.json()
        duration = time.time() - start_time
        
        # Check response quality
        answer = result.get("final_answer", "")
        citations = result.get("citations", [])
        confidence = result.get("confidence", 0)
        sources = result.get("evidence_sources", [])
        
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📊 Confidence: {confidence:.1%}")
        print(f"📚 Citations: {len(citations)}")
        print(f"🔍 Sources: {', '.join(sources)}")
        
        # Check for expected keywords
        found_keywords = []
        missing_keywords = []
        
        for keyword in test_case["expected_keywords"]:
            if keyword.lower() in answer.lower():
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Check for expected sources
        expected_sources = set(test_case.get("expected_sources", []))
        actual_sources = set(sources)
        matching_sources = expected_sources & actual_sources
        
        print(f"\\n✅ Found keywords: {found_keywords}")
        if missing_keywords:
            print(f"⚠️  Missing keywords: {missing_keywords}")
        print(f"✅ Matching sources: {matching_sources}")
        
        # Success criteria
        success = (
            len(found_keywords) >= len(test_case["expected_keywords"]) * 0.5 and
            len(matching_sources) >= 1 and
            confidence > 0.5
        )
        
        if success:
            print("\\n✅ TEST PASSED")
        else:
            print("\\n❌ TEST FAILED")
        
        # Print answer preview
        print(f"\\nAnswer preview: {answer[:300]}...")
        
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all enhanced tests."""
    print("🚀 Testing Enhanced Legacy Codebase Assistant with Bedrock")
    
    # Test health
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("bedrock"):
                print("✅ Enhanced API with Bedrock is running")
            else:
                print("⚠️  API running but Bedrock not detected")
        else:
            print("❌ API not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # Run test cases
    passed = 0
    total = len(TEST_CASES)
    
    for test_case in TEST_CASES:
        if test_enhanced_query(test_case):
            passed += 1
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print(f"\\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed >= total * 0.8:
        print("\\n🎉 Enhanced system is working excellently!")
    elif passed >= total * 0.6:
        print("\\n✅ System is functional but needs tuning")
    else:
        print("\\n⚠️  System needs attention")
    
    # Test metrics endpoint
    try:
        response = requests.get(f"{API_BASE}/api/metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            print(f"\\n📈 System Metrics:")
            print(f"  Queries processed: {metrics['orchestrator_metrics']['queries_processed']}")
            print(f"  Avg response time: {metrics['orchestrator_metrics']['avg_response_time']:.2f}s")
            if metrics['feedback_summary']['total'] > 0:
                print(f"  Feedback success rate: {metrics['feedback_summary']['success_rate']:.1%}")
    except:
        pass

if __name__ == "__main__":
    main()
'''
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"  ✅ Created {test_file}")

def main():
    """Main setup process."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   Enhanced Legacy Codebase Assistant Setup - With Bedrock   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check requirements
    check_requirements()
    
    # Setup environment
    if not setup_environment():
        print("\n⚠️  Please configure your .env file and run again!")
        return
    
    # Test Bedrock connection
    if not test_bedrock_connection():
        print("\n⚠️  Bedrock connection required for enhanced features!")
        print("Please check your AWS credentials and try again.")
        return
    
    # Initialize databases
    os_client = initialize_opensearch()
    neo4j_driver = initialize_neo4j()
    
    if not os_client or not neo4j_driver:
        print("\n⚠️  Database initialization failed!")
        print("Make sure OpenSearch and Neo4j are running.")
        return
    
    # Create API wrapper
    create_api_wrapper()
    
    # Create test suite
    create_test_suite()
    
    # Start indexing
    print("\n📚 Ready to index your codebase!")
    print("Would you like to start indexing now? This may take a while.")
    response = input("Start indexing? (y/n): ")
    
    if response.lower() == 'y':
        start_indexing(os_client, neo4j_driver)
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    Setup Complete! 🎉                        ║
╠══════════════════════════════════════════════════════════════╣
║  Next steps:                                                 ║
║  1. Start the API:                                          ║
║     python api/enhanced_strands_app.py                      ║
║                                                              ║
║  2. Test the system:                                        ║
║     python test_enhanced_mvp.py                             ║
║                                                              ║
║  3. Access the UI:                                          ║
║     http://localhost:4200                                   ║
║                                                              ║
║  4. View metrics:                                           ║
║     http://localhost:8000/api/metrics                       ║
╚══════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()
