import os, re
from pathlib import Path
from typing import Dict, Any, List
from retrievers.pipeline import upsert

EL_RX = re.compile(r"\$\{([^}]+)\}")

def extract_el(text: str) -> List[str]:
    toks = set()
    for m in EL_RX.finditer(text):
        toks.add(m.group(1).strip())
    return sorted(toks)

def index_repo_jsp(root: str):
    rootp = Path(root)
    repo_name = rootp.name
    for ext in ("*.jsp","*.jspf"):
        for path in rootp.rglob(ext):
            try:
                rel = str(path.relative_to(rootp)).replace("\\","/")
                text = path.read_text(errors="ignore")
                anchors = extract_el(text)
                doc = {
                    "id": f"jsp:{repo_name}:{rel}",
                    "kind": "JSPView",
                    "repo": repo_name,
                    "path": "/" + rel if not rel.startswith("/") else rel,
                    "sha": "<fs>",
                    "source_env": os.getenv("SOURCE_ENV","legacy"),
                    "text": text[:16000],
                    "anchors": anchors,
                }
                upsert(doc)
            except Exception as e:
                print(f"[jsp_el] error {path}: {e}")
