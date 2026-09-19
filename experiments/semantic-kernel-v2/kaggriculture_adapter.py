from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from kernel import ActionIntent, Rule, StateSnapshot, StepTrace, apply, evaluate, plan, resolve


WHEAT_SEED_COST = 10
WHEAT3_COST = WHEAT_SEED_COST * 3
LAND_PRICES = (1000, 2000, 4000)


@dataclass(frozen=True)
class KaggricultureFixture:
    cash: int = 980
    wheat_trigger_below: int = 1000
    land_trigger_at_least: int = 970
    land_price_index: int = 0

    @property
    def land_cost(self) -> int:
        if not 0 <= self.land_price_index < len(LAND_PRICES):
            raise ValueError("land_price_index must identify an available LAND_PRICES entry")
        return LAND_PRICES[self.land_price_index]


def build_wheat3_land_fixture(
    fixture: KaggricultureFixture,
) -> tuple[StateSnapshot, tuple[Rule, Rule]]:
    snapshot = StateSnapshot({"cash": fixture.cash})
    land_cost = fixture.land_cost

    wheat_rule = Rule(
        id="A_WHEAT3",
        version="fixture-v2",
        trigger=lambda s: s.get("cash") < fixture.wheat_trigger_below,
        action=ActionIntent(
            id="act-buy-seed-wheat-3",
            kind="BUY_SEED_WHEAT_3",
            claims={"cash": WHEAT3_COST},
            requires=lambda s: s.get("cash") >= WHEAT3_COST,
            effects=(
                ("cash", "add", -WHEAT3_COST),
                ("fixture_wheat3_applied", "set", 1),
            ),
        ),
    )

    land_rule = Rule(
        id="B_LAND",
        version="fixture-v2",
        trigger=lambda s: s.get("cash") >= fixture.land_trigger_at_least,
        action=ActionIntent(
            id="act-buy-land",
            kind="BUY_LAND",
            claims={"cash": land_cost},
            requires=lambda s: s.get("cash") >= land_cost,
            effects=(
                ("cash", "add", -land_cost),
                ("fixture_land_applied", "set", 1),
            ),
        ),
    )

    return snapshot, (wheat_rule, land_rule)


def run_wheat3_land_fixture(
    fixture: KaggricultureFixture = KaggricultureFixture(),
    rule_order: Sequence[str] = ("A_WHEAT3", "B_LAND"),
) -> tuple[StateSnapshot, StepTrace, StateSnapshot | None]:
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
