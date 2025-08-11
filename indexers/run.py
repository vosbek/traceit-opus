import csv, os, sys
from .jsp_el import index_repo_jsp
from .struts_xml import index_repo_struts
from .java_parser import index_repo_java
from retrievers.pipeline import ensure_index

USAGE = "Usage: python -m indexers.run --repos config/repos.csv"

def run(csv_path: str):
    ensure_index()
    with open(csv_path, newline="") as f:
        rdr = csv.DictReader(f)
        if "repo" not in rdr.fieldnames:
            print("repos.csv must have a 'repo' column with local paths", file=sys.stderr)
            sys.exit(1)
        for row in rdr:
            repo_path = row["repo"].strip()
            if not os.path.isdir(repo_path):
                print(f"[skip] not a directory: {repo_path}")
                continue
            print(f"[index] {repo_path}")
            index_repo_java(repo_path)
            index_repo_jsp(repo_path)
            index_repo_struts(repo_path)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--repos", required=True)
    a = p.parse_args()
    run(a.repos)
