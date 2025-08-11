import os, re
from pathlib import Path
from retrievers.pipeline import upsert

CLASS_RX = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)")
IDENT_RX = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")

def index_repo_java(root: str):
    rootp = Path(root)
    repo = rootp.name
    for path in rootp.rglob("*.java"):
        try:
            rel = str(path.relative_to(rootp)).replace("\\","/")
            text = path.read_text(errors="ignore")
            classes = CLASS_RX.findall(text)
            methods = []
            for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
                # skip constructor calls (preceded by 'new')
                if text[max(0,m.start()-10):m.start()].strip().startswith("new"):
                    continue
                methods.append(m.group(1))
            idents = set(IDENT_RX.findall(text))
            anchors = sorted(set(list(classes)+methods+list(idents)))[:500]
            doc = {
                "id": f"code:{repo}:{rel}",
                "kind": "Code",
                "repo": repo,
                "path": "/" + rel if not rel.startswith("/") else rel,
                "sha": "<fs>",
                "source_env": os.getenv("SOURCE_ENV","legacy"),
                "text": text[:16000],
                "anchors": anchors,
            }
            upsert(doc)
        except Exception as e:
            print(f"[java_parser] error {path}: {e}")
