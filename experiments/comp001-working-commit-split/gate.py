#!/usr/bin/env python3
import json

def decide(*, can_progress, evidence_ok, commit_requested, split_enabled=True):
    if not split_enabled:
        return {
            "progress_allowed": bool(can_progress),
            "commit_allowed": bool(commit_requested and can_progress),
            "state": "committed" if (commit_requested and can_progress) else ("working" if can_progress else "blocked"),
            "reason": "split_disabled"
        }

    progress_allowed = bool(can_progress)
    commit_allowed = bool(commit_requested and evidence_ok)
    if commit_allowed:
        state = "committed"
        reason = "evidence_present"
    elif progress_allowed:
        state = "working"
        reason = "evidence_missing_commit_refused" if commit_requested else "working_progress"
    else:
        state = "blocked"
        reason = "progress_not_allowed"
    return {
        "progress_allowed": progress_allowed,
        "commit_allowed": commit_allowed,
        "state": state,
        "reason": reason
    }

def main():
    with open("cases.json", encoding="utf-8") as f:
        cases=json.load(f)
    out=[]
    for c in cases:
        on=decide(**c["input"], split_enabled=True)
        off=decide(**c["input"], split_enabled=False)
        out.append({"name":c["name"],"expected":c["expected"],"component_on":on,"component_off":off})
    print(json.dumps({"cases":out}, ensure_ascii=False, indent=2))

if __name__=="__main__":
    main()
