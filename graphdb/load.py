import os
from typing import Dict, Any, Iterable
from opensearchpy import OpenSearch, RequestsHttpConnection
from neo4j import GraphDatabase

OS_INDEX = os.getenv("OS_INDEX","traceit_docs")
OS_URL = os.getenv("OPENSEARCH_URL","http://opensearch:9200")
N4J_URL = os.getenv("NEO4J_URL","bolt://neo4j:7687")
N4J_USER = os.getenv("NEO4J_USER","neo4j")
N4J_PASS = os.getenv("NEO4J_PASS","test")

client = OpenSearch(hosts=[OS_URL], use_ssl=False, verify_certs=False, connection_class=RequestsHttpConnection)
driver = GraphDatabase.driver(N4J_URL, auth=(N4J_USER,N4J_PASS))

def _scroll(index: str):
    page = client.search(index=index, size=500, query={"match_all": {}}, scroll="2m")
    sid = page.get("_scroll_id")
    hits = page["hits"]["hits"]
    while hits:
        for h in hits:
            yield h
        page = client.scroll(scroll_id=sid, scroll="2m")
        sid = page.get("_scroll_id"); hits = page["hits"]["hits"]

def load():
    with driver.session() as sess:
        for h in _scroll(OS_INDEX):
            src = h.get("_source",{})
            kind = src.get("kind")
            doc_id = src.get("id")
            path = src.get("path")
            if kind == "Code":
                sess.run("MERGE (f:File {id:$id}) SET f.path=$path, f.repo=$repo",
                         id=f"file:{path}", path=path, repo=src.get("repo"))
            if kind == "StrutsAction":
                sess.run("MERGE (s:StrutsAction {id:$id}) SET s.name=$name, s.path=$path",
                         id=doc_id, name=src.get("action_name") or path, path=path)
            if kind == "JSPView":
                sess.run("MERGE (v:JSPView {id:$id}) SET v.path=$path",
                         id=doc_id, path=path)
    print("[graphdb.load] Neo4j load complete")

if __name__ == "__main__":
    load()
