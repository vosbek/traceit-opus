import os
import oracledb
from retrievers.pipeline import upsert

def run():
    dsn = os.getenv("ORACLE_DSN")
    user = os.getenv("ORACLE_USER")
    pw = os.getenv("ORACLE_PASS")
    if not (dsn and user and pw):
        print("[db_oracle] ORACLE_DSN/USER/PASS not set; skipping")
        return

    conn = oracledb.connect(user=user, password=pw, dsn=dsn)  # thin mode
    cur = conn.cursor()

    # Tables & columns
    cur.execute("""
      SELECT atc.OWNER, atc.TABLE_NAME, atc.COLUMN_NAME, atc.DATA_TYPE
      FROM ALL_TAB_COLUMNS atc WHERE OWNER NOT IN ('SYS','SYSTEM') FETCH FIRST 5000 ROWS ONLY
    """)
    for owner, t, c, dt in cur:
        doc = {
            "id": f"dbcol:{owner}.{t}.{c}",
            "kind": "Column",
            "repo": "oracle",
            "path": f"{owner}.{t}.{c}",
            "sha": "<db>",
            "source_env": "legacy",
            "text": f"{owner}.{t}.{c} {dt}",
            "anchors": [owner, t, c, dt]
        }
        upsert(doc)

    # Views
    cur.execute("""
      SELECT OWNER, VIEW_NAME, TEXT FROM ALL_VIEWS WHERE OWNER NOT IN ('SYS','SYSTEM') FETCH FIRST 500 ROWS ONLY
    """)
    for owner, v, txt in cur:
        upsert({
            "id": f"view:{owner}.{v}",
            "kind": "View",
            "repo": "oracle",
            "path": f"{owner}.{v}",
            "sha": "<db>",
            "source_env": "legacy",
            "text": (txt or "")[:16000],
            "anchors": [owner, v]
        })

    # Procedures
    cur.execute("""
      SELECT OWNER, OBJECT_NAME, OBJECT_TYPE FROM ALL_OBJECTS 
      WHERE OBJECT_TYPE IN ('PROCEDURE','FUNCTION','TRIGGER') AND OWNER NOT IN ('SYS','SYSTEM') FETCH FIRST 1000 ROWS ONLY
    """)
    for owner, name, typ in cur:
        upsert({
            "id": f"proc:{owner}.{name}",
            "kind": "Procedure" if typ in ('PROCEDURE','FUNCTION') else "Trigger",
            "repo": "oracle",
            "path": f"{owner}.{name}",
            "sha": "<db>",
            "source_env": "legacy",
            "text": f"{typ} {owner}.{name}",
            "anchors": [owner, name, typ]
        })

    cur.close(); conn.close()
    print("[db_oracle] metadata load complete")
