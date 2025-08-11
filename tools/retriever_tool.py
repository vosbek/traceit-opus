from strands import Tool, tool
from retrievers.pipeline import search

@tool(name="code_search", desc="Search legacy code/DB index for evidence with BM25 and anchors.")
def code_search(query: str) -> dict:
    hits = search(query)
    return {"hits": hits}
