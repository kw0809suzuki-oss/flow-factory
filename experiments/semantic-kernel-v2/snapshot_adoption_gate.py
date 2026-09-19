from __future__ import annotations

import json

from kaggriculture_adapter import (
    KaggricultureFixture,
    UnresolvedDomainValue,
    run_wheat3_land_fixture,
)


def evaluate_snapshot_adoption_gate() -> dict[str, object]:
    observations: dict[str, object] = {}

    try:
        run_wheat3_land_fixture(KaggricultureFixture())
        observations["unknown_domain_value_preserved"] = False
    except UnresolvedDomainValue:
        observations["unknown_domain_value_preserved"] = True

    _, feasible_trace, feasible_state = run_wheat3_land_fixture(
        KaggricultureFixture(land_claim=950)
    )
    observations["feasible_fixture"] = {
        "eligible": list(feasible_trace.eligible_rule_ids),
        "selected": list(feasible_trace.selected_rule_ids),
        "plan_status": feasible_trace.plan_status,
        "executed": list(feasible_trace.executed_action_ids),
        "next_cash": feasible_state.get("cash") if feasible_state else None,
    }

    _, conflict_trace, conflict_state = run_wheat3_land_fixture(
        KaggricultureFixture(land_claim=960)
    )
    observations["conflict_fixture"] = {
        "eligible": list(conflict_trace.eligible_rule_ids),
        "selected": list(conflict_trace.selected_rule_ids),
        "plan_status": conflict_trace.plan_status,
        "plan_reason": conflict_trace.plan_reason,
        "executed": list(conflict_trace.executed_action_ids),
        "next_state": None if conflict_state is None else dict(conflict_state.values),
    }

    overall = "HOLD"
    reason = (
        "semantic adapter behavior is consistent, but production BUY_LAND resource claim "
        "is still unknown in the current factory evidence"
    )
    return {
        "snapshot_adoption_gate": overall,
        "reason": reason,
        "observations": observations,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_snapshot_adoption_gate(), indent=2, sort_keys=True))
