import unittest

from kernel import ActionIntent, Rule, StateSnapshot, apply, evaluate, plan, resolve


def ge(key, value):
    return lambda s: s.get(key) >= value


def lt(key, value):
    return lambda s: s.get(key) < value


def eq(key, value):
    return lambda s: s.get(key) == value


def run_until_plan(snapshot, rules):
    eligible, trace = evaluate(snapshot, rules)
    selected, trace = resolve(snapshot, eligible, trace)
    bundle, trace = plan(snapshot, selected, trace)
    return eligible, selected, bundle, trace


class SemanticConformanceTests(unittest.TestCase):
    def test_case_1_both_actions_compose(self):
        snapshot = StateSnapshot({"cash": 100})
        a = Rule(
            "A", "1", ge("cash", 0),
            ActionIntent("act-A", "SPEND_A", claims={"cash": 20}, effects=(("cash", "add", -20),)),
        )
        b = Rule(
            "B", "1", ge("cash", 0),
            ActionIntent("act-B", "SPEND_B", claims={"cash": 30}, effects=(("cash", "add", -30),)),
        )

        eligible, selected, bundle, trace = run_until_plan(snapshot, [a, b])
        self.assertEqual([r.id for r in eligible], ["A", "B"])
        self.assertEqual([r.id for r in selected], ["A", "B"])
        self.assertEqual(trace.plan_status, "valid")
        next_state, trace = apply(snapshot, bundle, trace)
        self.assertEqual(next_state.get("cash"), 50)
        self.assertEqual(trace.executed_action_ids, ("act-A", "act-B"))

    def test_case_2_a_does_not_erase_b_eligibility(self):
        snapshot = StateSnapshot({"cash": 980})
        a = Rule(
            "A", "1", lt("cash", 1000),
            ActionIntent("act-A", "BUY_SEED_WHEAT_3", effects=(("cash", "add", -30),)),
        )
        b = Rule(
            "B", "1", ge("cash", 970),
            ActionIntent("act-B", "MARK_B", effects=(("b_executed", "set", 1),)),
        )

        eligible, selected, bundle, trace = run_until_plan(snapshot, [a, b])
        self.assertEqual(trace.eligible_rule_ids, ("A", "B"))
        self.assertEqual(trace.selected_rule_ids, ("A", "B"))
        next_state, trace = apply(snapshot, bundle, trace)
        self.assertEqual(next_state.get("cash"), 950)
        self.assertEqual(next_state.get("b_executed"), 1)

    def test_case_3_rule_declaration_order_does_not_leak(self):
        snapshot = StateSnapshot({"cash": 980})
        a = Rule(
            "A", "1", lt("cash", 1000),
            ActionIntent("act-A", "MARK_A", effects=(("a_executed", "set", 1),)),
        )
        b = Rule(
            "B", "1", ge("cash", 970),
            ActionIntent("act-B", "CASH_RAISE", effects=(("cash", "add", 100),)),
        )

        outcomes = []
        for rules in ([a, b], [b, a]):
            eligible, selected, bundle, trace = run_until_plan(snapshot, rules)
            next_state, trace = apply(snapshot, bundle, trace)
            outcomes.append(
                (
                    trace.eligible_rule_ids,
                    trace.selected_rule_ids,
                    trace.planned_action_ids,
                    dict(next_state.values),
                )
            )
        self.assertEqual(outcomes[0], outcomes[1])
        self.assertEqual(outcomes[0][3]["cash"], 1080)
        self.assertEqual(outcomes[0][3]["a_executed"], 1)

    def test_case_4_resource_conflict_is_plan_failure_not_rule_erasure(self):
        snapshot = StateSnapshot({"cash": 50})
        a = Rule(
            "A", "1", ge("cash", 0),
            ActionIntent("act-A", "SPEND_A", claims={"cash": 30}, effects=(("cash", "add", -30),)),
        )
        b = Rule(
            "B", "1", ge("cash", 0),
            ActionIntent("act-B", "SPEND_B", claims={"cash": 30}, effects=(("cash", "add", -30),)),
        )

        _, _, bundle, trace = run_until_plan(snapshot, [a, b])
        self.assertIsNone(bundle)
        self.assertEqual(trace.eligible_rule_ids, ("A", "B"))
        self.assertEqual(trace.selected_rule_ids, ("A", "B"))
        self.assertEqual(trace.plan_status, "invalid")
        self.assertEqual(trace.plan_reason, "resource_claim_conflict:cash")
        self.assertEqual(trace.executed_action_ids, ())

    def test_case_5_newly_open_rule_waits_until_next_step(self):
        snapshot = StateSnapshot({"gate": 0})
        a = Rule(
            "A", "1", eq("gate", 0),
            ActionIntent("act-A", "OPEN_GATE", effects=(("gate", "set", 1),)),
        )
        c = Rule(
            "C", "1", eq("gate", 1),
            ActionIntent("act-C", "AFTER_GATE", effects=(("c_executed", "set", 1),)),
        )

        eligible, selected, bundle, trace = run_until_plan(snapshot, [a, c])
        self.assertEqual([r.id for r in eligible], ["A"])
        next_state, trace = apply(snapshot, bundle, trace)
        self.assertEqual(next_state.get("gate"), 1)
        self.assertEqual(next_state.get("c_executed"), 0)

        next_eligible, _ = evaluate(next_state, [a, c])
        self.assertEqual([r.id for r in next_eligible], ["C"])

    def test_case_6_non_commutative_bundle_requires_ordering_semantics(self):
        snapshot = StateSnapshot({"x": 0})
        a = Rule(
            "A", "1", ge("x", 0),
            ActionIntent("act-A", "SET_X_1", effects=(("x", "set", 1),), conflict_keys=frozenset({"x"})),
        )
        b = Rule(
            "B", "1", ge("x", 0),
            ActionIntent("act-B", "SET_X_2", effects=(("x", "set", 2),), conflict_keys=frozenset({"x"})),
        )

        _, _, bundle, trace = run_until_plan(snapshot, [a, b])
        self.assertIsNone(bundle)
        self.assertEqual(trace.plan_status, "invalid")
        self.assertEqual(trace.plan_reason, "non_commutative_conflict:act-A:act-B:x")

        a_ordered = Rule(
            "A", "1", ge("x", 0),
            ActionIntent(
                "act-A", "SET_X_1", effects=(("x", "set", 1),),
                conflict_keys=frozenset({"x"}), phase=10,
            ),
        )
        b_ordered = Rule(
            "B", "1", ge("x", 0),
            ActionIntent(
                "act-B", "SET_X_2", effects=(("x", "set", 2),),
                conflict_keys=frozenset({"x"}), phase=20,
            ),
        )

        _, _, bundle, trace = run_until_plan(snapshot, [b_ordered, a_ordered])
        self.assertIsNotNone(bundle)
        self.assertEqual(trace.planned_action_ids, ("act-A", "act-B"))
        next_state, _ = apply(snapshot, bundle, trace)
        self.assertEqual(next_state.get("x"), 2)


if __name__ == "__main__":
    unittest.main()
