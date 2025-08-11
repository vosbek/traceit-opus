import os
from pathlib import Path
import xml.etree.ElementTree as ET
from retrievers.pipeline import upsert

def _norm_jsp(p: str) -> str:
    p = (p or "").strip()
    if not p:
        return p
    if not p.startswith("/"):
        p = "/" + p
    return p.replace("\\","/")

def _action_to_id(repo: str, name_or_path: str) -> str:
    return f"struts:{repo}:{name_or_path}"

def index_repo_struts(root: str):
    rootp = Path(root)
    repo = rootp.name
    for xml in list(rootp.rglob("struts*.xml")) + list(rootp.rglob("struts-config*.xml")):
        try:
            tree = ET.parse(xml)
            x = tree.getroot()
            txt = xml.read_text(errors="ignore")

            # Struts 2: <action name="x"><result>/a.jsp</result></action>
            for act in x.findall(".//action"):
                name = act.get("name") or act.get("path") or act.get("value") or ""
                action_path = name
                if name and not name.startswith("/"):
                    action_path = f"/{name}.action"
                results = [ (r.text or "").strip() for r in act.findall("result") if r.text ]
                upsert({ 
                    "id": _action_to_id(repo, action_path),
                    "kind": "StrutsAction",
                    "repo": repo,
                    "path": action_path,
                    "action_name": name,
                    "sha": "<fs>",
                    "source_env": os.getenv("SOURCE_ENV","legacy"),
                    "text": txt[:8000],
                    "anchors": [name or action_path],
                })
            # Struts 1: <action path="/foo" forward="/bar.jsp"><forward .../></action>
            for act in x.findall(".//action-mappings/action") + x.findall(".//action"):
                path = act.get("path")
                if not path: 
                    continue
                upsert({
                    "id": _action_to_id(repo, path),
                    "kind": "StrutsAction",
                    "repo": repo,
                    "path": path,
                    "action_name": path,
                    "sha": "<fs>",
                    "source_env": os.getenv("SOURCE_ENV","legacy"),
                    "text": txt[:8000],
                    "anchors": [path],
                })
        except Exception as e:
            print(f"[struts_xml] error {xml}: {e}")
