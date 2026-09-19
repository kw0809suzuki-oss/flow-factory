import unittest

from kaggriculture_adapter import (
    KaggricultureFixture,
    UnresolvedDomainValue,
    run_wheat3_land_fixture,
)


class KaggricultureAdapterGateTests(unittest.TestCase):
    def test_adapter_refuses_to_invent_unknown_land_claim(self):
        with self.assertRaises(UnresolvedDomainValue):
            run_wheat3_land_fixture(KaggricultureFixture())

    def test_jointly_feasible_fixture_preserves_snapshot_eligibility(self):
        _, trace, next_state = run_wheat3_land_fixture(
            KaggricultureFixture(land_claim=950)
        )
        self.assertEqual(trace.eligible_rule_ids, ("A_WHEAT3", "B_LAND"))
        self.assertEqual(trace.selected_rule_ids, ("A_WHEAT3", "B_LAND"))
        self.assertEqual(trace.plan_status, "valid")
        self.assertIsNotNone(next_state)
        self.assertEqual(next_state.get("cash"), 0)
        self.assertEqual(next_state.get("fixture_wheat3_applied"), 1)
        self.assertEqual(next_state.get("fixture_land_applied"), 1)

    def test_resource_overclaim_stops_at_plan_without_erasing_rules(self):
        _, trace, next_state = run_wheat3_land_fixture(
            KaggricultureFixture(land_claim=960)
        )
        self.assertIsNone(next_state)
        self.assertEqual(trace.eligible_rule_ids, ("A_WHEAT3", "B_LAND"))
        self.assertEqual(trace.selected_rule_ids, ("A_WHEAT3", "B_LAND"))
        self.assertEqual(trace.plan_status, "invalid")
        self.assertEqual(trace.plan_reason, "resource_claim_conflict:cash")
        self.assertEqual(trace.executed_action_ids, ())

    def test_adapter_does_not_reintroduce_rule_declaration_order(self):
        fixture = KaggricultureFixture(land_claim=950)
        _, left, left_state = run_wheat3_land_fixture(
            fixture, ("A_WHEAT3", "B_LAND")
        )
        _, right, right_state = run_wheat3_land_fixture(
            fixture, ("B_LAND", "A_WHEAT3")
        )

        self.assertEqual(left.eligible_rule_ids, right.eligible_rule_ids)
        self.assertEqual(left.selected_rule_ids, right.selected_rule_ids)
        self.assertEqual(left.planned_action_ids, right.planned_action_ids)
        self.assertEqual(dict(left_state.values), dict(right_state.values))


if __name__ == "__main__":
    unittest.main()
