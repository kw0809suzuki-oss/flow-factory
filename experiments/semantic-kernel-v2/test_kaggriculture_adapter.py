import unittest

from kaggriculture_adapter import (
    LAND_PRICES,
    WHEAT3_COST,
    KaggricultureFixture,
    run_wheat3_land_fixture,
)


class KaggricultureAdapterGateTests(unittest.TestCase):
    def test_official_cost_mapping(self):
        self.assertEqual(WHEAT3_COST, 30)
        self.assertEqual(LAND_PRICES, (1000, 2000, 4000))

    def test_cash_980_keeps_b_eligible_but_fails_action_requirement(self):
        _, trace, next_state = run_wheat3_land_fixture()
        self.assertIsNone(next_state)
        self.assertEqual(trace.eligible_rule_ids, ("A_WHEAT3", "B_LAND"))
        self.assertEqual(trace.selected_rule_ids, ("A_WHEAT3", "B_LAND"))
        self.assertEqual(trace.plan_status, "invalid")
        self.assertEqual(trace.plan_reason, "requirement_failed:act-buy-land")
        self.assertEqual(trace.executed_action_ids, ())

    def test_b_trigger_would_turn_false_after_a_but_eligibility_is_frozen(self):
        snapshot, trace, _ = run_wheat3_land_fixture()
        self.assertEqual(snapshot.get("cash"), 980)
        self.assertEqual(trace.eligible_rule_ids, ("A_WHEAT3", "B_LAND"))
        # If A alone were applied, cash would become 950 and B.trigger would be false.
        # Snapshot semantics preserves the already-recorded eligibility fact.
        self.assertEqual(snapshot.get("cash") - WHEAT3_COST, 950)

    def test_later_land_prices_are_also_infeasible_at_cash_980(self):
        for price_index in (0, 1, 2):
            _, trace, next_state = run_wheat3_land_fixture(
                KaggricultureFixture(land_price_index=price_index)
            )
            self.assertIsNone(next_state)
            self.assertEqual(trace.eligible_rule_ids, ("A_WHEAT3", "B_LAND"))
            self.assertEqual(trace.selected_rule_ids, ("A_WHEAT3", "B_LAND"))
            self.assertEqual(trace.plan_reason, "requirement_failed:act-buy-land")

    def test_adapter_does_not_reintroduce_rule_declaration_order(self):
        fixture = KaggricultureFixture()
        _, left, left_state = run_wheat3_land_fixture(
            fixture, ("A_WHEAT3", "B_LAND")
        )
        _, right, right_state = run_wheat3_land_fixture(
            fixture, ("B_LAND", "A_WHEAT3")
        )

        self.assertIsNone(left_state)
        self.assertIsNone(right_state)
        self.assertEqual(left.eligible_rule_ids, right.eligible_rule_ids)
        self.assertEqual(left.selected_rule_ids, right.selected_rule_ids)
        self.assertEqual(left.plan_status, right.plan_status)
        self.assertEqual(left.plan_reason, right.plan_reason)


if __name__ == "__main__":
    unittest.main()
