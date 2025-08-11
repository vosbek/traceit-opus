#!/usr/bin/env python3
import argparse, json, os, sys, time, urllib.request

def _post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read()
        dt = (time.time() - t0) * 1000.0
        return json.loads(body.decode("utf-8")), int(dt)

def score(resp, expects):
    answer = (resp.get("final_answer","") or "").lower()
    req = (expects or {}).get("answer_contains", [])
    exact = (sum(1 for r in req if r.lower() in answer)/len(req)) if req else 1.0

    # citations check
    cits_ok = True
    pool = [resp.get("final_answer","").lower()] + [ (h.get("text","") or "").lower() for h in resp.get("raw_state",{}).get("hits",[]) ]
    for rule in (expects or {}).get("citations", []):
        want = rule.get("type","code")
        ok_type = any((c.get("type")==want) or (want=="sql_or_code" and c.get("type") in ("sql","code")) for c in resp.get("citations",[]))
        if not ok_type: cits_ok = False; break
        for s in rule.get("must_include",[]):
            if not any(s.lower() in t for t in pool): cits_ok = False; break
        if not cits_ok: break

    grounded = 1.0 if (resp.get("citations") and resp.get("final_answer")) else 0.0
    return exact, cits_ok, grounded

def main(file_path, api_url):
    total, fails = 0, 0
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            j = json.loads(line)
            resp, ms = _post(f"{api_url}/api/run", {"query": j["query"]})
            exact, cits_ok, grd = score(resp, j.get("expects",{}))
            ok = (exact>=0.8) and cits_ok and (grd>=0.9)
            rows.append((j["id"], exact, cits_ok, grd, ms, ok))
            total+=1; fails += (0 if ok else 1)

    header = ("ID","Exact","Citations","Grounded","ms","PASS")
    print("{:30}  {:>5}  {:>9}  {:>8}  {:>6}  {:>5}".format(*header))
    print("-"*72)
    for r in rows:
        print("{:30}  {:>5.2f}  {:>9}  {:>8.2f}  {:>6}  {:>5}".format(r[0], r[1], "ok" if r[2] else "fail", r[3], r[4], "true" if r[5] else "false"))
    print(f"Total: {total}  Fails: {fails}")
    return 0 if fails==0 else 1

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--api", default=os.getenv("EVAL_API_URL","http://localhost:8000"))
    args = ap.parse_args()
    raise SystemExit(main(args.file, args.api))
