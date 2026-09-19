from __future__ import annotations

import json

from kaggriculture_adapter import LAND_PRICES, WHEAT3_COST, run_wheat3_land_fixture


def evaluate_snapshot_adoption_gate() -> dict[str, object]:
    _, trace, next_state = run_wheat3_land_fixture()

    checks = {
        "official_wheat3_cost_is_30": WHEAT3_COST == 30,
        "official_land_prices_known": LAND_PRICES == (1000, 2000, 4000),
        "both_rules_eligible_from_same_snapshot": trace.eligible_rule_ids == ("A_WHEAT3", "B_LAND"),
        "both_rules_remain_selected": trace.selected_rule_ids == ("A_WHEAT3", "B_LAND"),
        "action_requirement_failure_is_explicit": trace.plan_reason == "requirement_failed:act-buy-land",
        "no_action_executed_after_invalid_plan": trace.executed_action_ids == (),
        "no_next_state_committed_after_invalid_plan": next_state is None,
    }

    passed = all(checks.values())
    return {
        "snapshot_adoption_gate": "PASS" if passed else "HOLD",
        "scope": "semantic default only",
        "checks": checks,
        "wheat3_land_trace": {
            "eligible": list(trace.eligible_rule_ids),
            "selected": list(trace.selected_rule_ids),
            "plan_status": trace.plan_status,
            "plan_reason": trace.plan_reason,
            "executed": list(trace.executed_action_ids),
            "next_state": None if next_state is None else dict(next_state.values),
        },
        "boundary": (
            "PASS does not imply terminal-score improvement or Battle integration correctness. "
            "It means the Snapshot candidate satisfies the current semantic adoption gate."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_snapshot_adoption_gate(), indent=2, sort_keys=True))
