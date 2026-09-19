#!/usr/bin/env python3
import csv, json, sys
from collections import defaultdict

REQ=["run_id","variant","seed","turn","self_action","opponent_action","wheat_inventory","wheat_price","self_money","opponent_money"]

def main(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    missing_cols=[c for c in REQ if c not in (rows[0].keys() if rows else [])]
    if missing_cols:
        print(json.dumps({"reentry_ready":False,"reason":"missing_columns","missing_columns":missing_cols},ensure_ascii=False,indent=2))
        return 2
    by=defaultdict(lambda:defaultdict(set))
    bad=[]
    for i,r in enumerate(rows, start=2):
        try:
            t=int(r["turn"]); float(r["wheat_inventory"]); float(r["wheat_price"])
        except Exception:
            bad.append(i); continue
        by[r["seed"]][r["variant"]].add(t)
        if not r["self_action"].strip() or not r["opponent_action"].strip():
            bad.append(i)
    ready=[]
    need=set(range(2,121))
    for seed,v in by.items():
        if need.issubset(v.get("baseline",set())) and need.issubset(v.get("full_v1",set())):
            ready.append(seed)
    out={
      "reentry_ready": bool(ready) and not bad,
      "paired_complete_seeds": ready,
      "bad_rows": bad,
      "boundary":"Sufficiency check only; no causality inference."
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0 if out["reentry_ready"] else 1

if __name__=="__main__":
    raise SystemExit(main(sys.argv[1]))
