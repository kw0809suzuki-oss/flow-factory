from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from kernel import ActionIntent, Rule, StateSnapshot, StepTrace, apply, evaluate, plan, resolve


class UnresolvedDomainValue(ValueError):
    pass


@dataclass(frozen=True)
class KaggricultureFixture:
    cash: int = 980
    wheat3_cost: int = 30
    land_claim: Optional[int] = None
    wheat_trigger_below: int = 1000
    land_trigger_at_least: int = 970


def build_wheat3_land_fixture(
    fixture: KaggricultureFixture,
) -> tuple[StateSnapshot, tuple[Rule, Rule]]:
    if fixture.land_claim is None:
        raise UnresolvedDomainValue(
            "land_claim is unknown; adapter refuses to invent a BUY_LAND resource claim"
        )

    snapshot = StateSnapshot({"cash": fixture.cash})

    wheat_rule = Rule(
        id="A_WHEAT3",
        version="fixture-v1",
        trigger=lambda s: s.get("cash") < fixture.wheat_trigger_below,
        action=ActionIntent(
            id="act-buy-seed-wheat-3",
            kind="BUY_SEED_WHEAT_3",
            claims={"cash": fixture.wheat3_cost},
            effects=(
                ("cash", "add", -fixture.wheat3_cost),
                ("fixture_wheat3_applied", "set", 1),
            ),
        ),
    )

    land_rule = Rule(
        id="B_LAND",
        version="fixture-v1",
        trigger=lambda s: s.get("cash") >= fixture.land_trigger_at_least,
        action=ActionIntent(
            id="act-buy-land",
            kind="BUY_LAND",
            claims={"cash": fixture.land_claim},
            effects=(
                ("cash", "add", -fixture.land_claim),
                ("fixture_land_applied", "set", 1),
            ),
        ),
    )

    return snapshot, (wheat_rule, land_rule)


def run_wheat3_land_fixture(
    fixture: KaggricultureFixture,
    rule_order: Sequence[str] = ("A_WHEAT3", "B_LAND"),
) -> tuple[StateSnapshot, StepTrace, Optional[StateSnapshot]]:
    snapshot, rules = build_wheat3_land_fixture(fixture)
    by_id = {rule.id: rule for rule in rules}
    ordered_rules = tuple(by_id[rule_id] for rule_id in rule_order)

    eligible, trace = evaluate(snapshot, ordered_rules)
    selected, trace = resolve(snapshot, eligible, trace)
    bundle, trace = plan(snapshot, selected, trace)

    if bundle is None:
        return snapshot, trace, None

    next_state, trace = apply(snapshot, bundle, trace)
    return snapshot, trace, next_state
