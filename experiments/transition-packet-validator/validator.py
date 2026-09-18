#!/usr/bin/env python3
import json

B_TO_C_REQUIRED = [
    "parent_world","parent_source_id","parent_source_title","objective",
    "requirements","constraints","expected_artifact","boundary","reentry_target"
]
C_TO_B_REQUIRED = [
    "task_id","source_id","parent_source_id","artifact_id","build_status",
    "execution_environment","evidence","boundary","reentry"
]
OLD_REQUIRED = ["task_id","objective","route","payload"]

def present(v):
    return v is not None and (not isinstance(v,str) or v.strip() != "")

def validate(packet, required):
    obj = packet if isinstance(packet,dict) else {}
    missing=[k for k in required if k not in obj or not present(obj[k])]
    return {"ok": not missing, "missing": missing}

def classify(cases, mode):
    fp=fn=0
    rows=[]
    for c in cases:
        if mode=="off":
            ok=True; missing=[]
        elif mode=="old":
            r=validate(c["packet"], OLD_REQUIRED); ok=r["ok"]; missing=r["missing"]
        else:
            req=B_TO_C_REQUIRED if c["direction"]=="B_TO_C" else C_TO_B_REQUIRED
            r=validate(c["packet"], req); ok=r["ok"]; missing=r["missing"]
        expected=c["expected_valid"]
        if ok and not expected: fp+=1
        if (not ok) and expected: fn+=1
        rows.append({"name":c["name"],"expected_valid":expected,"accepted":ok,"missing":missing})
    return {"false_positive":fp,"false_negative":fn,"cases":rows}

def main():
    with open("cases.json",encoding="utf-8") as f:
        cases=json.load(f)
    result={
        "old":classify(cases,"old"),
        "aligned":classify(cases,"aligned"),
        "off":classify(cases,"off"),
        "boundary":"Presence/non-empty validation only. Type/enum/version negotiation and production downstream cost are not tested."
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
