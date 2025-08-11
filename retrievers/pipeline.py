import os
from typing import List, Dict, Any
from opensearchpy import OpenSearch, RequestsHttpConnection

OS_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
OS_INDEX = os.getenv("OS_INDEX", "traceit_docs")

_client = OpenSearch(
    hosts=[OS_URL],
    use_ssl=False,
    verify_certs=False,
    connection_class=RequestsHttpConnection,
    timeout=30,
)

def ensure_index():
    if _client.indices.exists(index=OS_INDEX):
        return
    body = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "kind": {"type": "keyword"},
                "repo": {"type": "keyword"},
                "path": {"type": "keyword"},
                "sha": {"type": "keyword"},
                "source_env": {"type": "keyword"},
                "anchors": {"type": "keyword"},
                "text": {"type": "text"}
            }
        }
    }
    _client.indices.create(index=OS_INDEX, body=body)

def search(query: str) -> List[Dict[str, Any]]:
    ensure_index()
    q = {
        "size": 20,
        "query": {
            "bool": {
                "should": [
                    {"match": {"text": {"query": query}}},
                    {"terms": {"anchors": [a for a in query.split() if len(a) > 2]}},
                ]
            }
        },
        "_source": ["id","kind","repo","path","sha","source_env","text"]
    }
    res = _client.search(index=OS_INDEX, body=q)
    out = []
    for hit in res.get("hits",{}).get("hits",[]):
        src = hit.get("_source",{})
        out.append(src)
    return out

def upsert(doc: Dict[str, Any]):
    ensure_index()
    _client.index(index=OS_INDEX, id=doc["id"], body=doc, refresh=True)
