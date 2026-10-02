#!/usr/bin/env python3
import json

def decide(case):
    created = case["handoff_created_at"]
    premise = {x["key"]: x["value"] for x in case["premise_claims"]}
    newer_seen = False
    comparable = False

    for ev in case.get("newer_evidence", []):
        # Only evidence observed after handoff creation can affect freshness.
        if ev["observed_at"] <= created:
            continue

        newer_seen = True
        for k, v in ev.get("claims", {}).items():
            if k not in premise:
                continue

            comparable = True
            if v != premise[k]:
                return "stale"

    if not newer_seen:
        return "fresh"
    if comparable:
        return "fresh"
    return "unknown"

with open("cases.json", encoding="utf-8") as f:
    data = json.load(f)

out = []
for c in data["cases"]:
    got = decide(c)
    out.append(
        {
            "id": c["id"],
            "expected": c["expected"],
            "got": got,
            "pass": got == c["expected"],
        }
    )

print(
    json.dumps(
        {
            "results": out,
            "all_pass": all(x["pass"] for x in out),
        },
        ensure_ascii=False,
        indent=2,
    )
)
