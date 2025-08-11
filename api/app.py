from fastapi import FastAPI
from pydantic import BaseModel
import os
from typing import Any, Dict
from retrievers.pipeline import search
import json

app = FastAPI(title="Trace-It API", version="0.1.0")

class RunReq(BaseModel):
    query: str
    opts: Dict[str, Any] | None = None

@app.get("/healthz")
def health():
    return {"ok": True}

@app.post("/api/run")
def run(req: RunReq):
    q = req.query.strip()
    hits = search(q)
    # Build simple answer + citations as in verify_guard
    def mk_citations(hs):
        cits = []
        for h in hs[:5]:
            p = h.get("path") or h.get("id")
            kind = "code" if p and p.endswith((".java",".jsp",".jspf",".xml")) else ("sql" if p and not p.startswith("/") else "doc")
            cits.append({
                "type": kind,
                "path": p,
                "lines": [1,1],
                "repo": h.get("repo"),
                "sha": h.get("sha"),
                "source_env": h.get("source_env","legacy")
            })
        return cits

    if not hits:
        answer = "No evidence found. Try refining the query or indexing more repos/schemas."
        cits = []
    else:
        lines = [f"Query: {q}", "Evidence (top matches):"]
        for h in hits[:3]:
            lines.append(f"- {h.get('repo','repo')}:{h.get('path') or h.get('id')}")
        lines.append("")
        lines.append("Answer: Based on the cited files/objects above, see the evidence for implementation details.")
        answer = "\n".join(lines)
        cits = mk_citations(hits)

    return {
        "thread_id": "thr_local",
        "final_answer": answer,
        "citations": cits,
        "steps": [],
        "graph": {"nodes": [], "edges": []},
        "raw_state": {"hits": hits}
    }
