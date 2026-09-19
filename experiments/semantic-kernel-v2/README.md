# Semantic Kernel v2 Spike

Minimal semantic-kernel spike for the Rule Engine contract in the Kaggriculture v2 parent spec.

## Scope

The semantic boundary remains:

`StateSnapshot -> evaluate -> resolve -> plan -> apply -> next StateSnapshot`

The kernel itself is Kaggriculture-independent. A thin fixture adapter maps the WHEAT3 / LAND boundary into this model without connecting to Battle runtime.

## Runtime types

Only five domain types are introduced:

- `StateSnapshot`
- `Rule`
- `ActionIntent`
- `StepTrace`
- `ExperimentResult`

`ActionBundle` is only a tuple alias, not a new domain object.

## Responsibility split

- `evaluate()` evaluates all Rule triggers against one immutable snapshot.
- `resolve()` handles only Rule-level semantics such as `supersedes`, `exclusive`, and explicit Rule conflicts.
- `plan()` validates the selected Action bundle. Resource insufficiency, failed operational requirements, or ambiguous non-commutative writes invalidate the **bundle**; they do not erase selected Rules.
- `apply()` applies an already-valid bundle. It never re-evaluates triggers or resolves Rules.

This preserves:

`eligible != selected != executed`

## Six semantic conformance cases

1. Two compatible eligible Rules compose.
2. A mutates state so B's trigger would become false; B remains eligible in the current step.
3. Reverse declaration order produces the same outcome.
4. Two selected Actions over-claim the same resource; plan is invalid and neither Rule disappears.
5. A opens C; C waits until the next step.
6. Non-commutative Actions with no dependency/phase are rejected; explicit phase makes the plan deterministic.

Local result: **6 / 6 PASS**.

## Kaggriculture fixture adapter

`kaggriculture_adapter.py` maps the WHEAT3 / LAND semantic fixture into the kernel using current official Kaggriculture mechanics from `Kaggle/kaggle-environments`.

Grounded constants:

- WHEAT seed cost = 10, therefore `BUY_SEED WHEAT 3` claims 30 cash.
- LAND prices = 1000 / 2000 / 4000.
- A LAND purchase is operationally infeasible when current cash is below the applicable LAND price.

At `cash=980`:

- Rule A trigger `cash < 1000` is true.
- Rule B trigger `cash >= 970` is true.
- Both Rules remain eligible and selected from the same snapshot.
- BUY_LAND is already operationally infeasible at the cheapest LAND price.
- `plan()` reports `requirement_failed:act-buy-land`.
- No Action executes and no next State is committed.

This is useful because it demonstrates that trigger eligibility and Action feasibility are separate facts in the real game mechanics, not only in an abstract fixture.

Adapter result: **5 / 5 PASS**.

## Snapshot Adoption Gate

Run:

```bash
cd experiments/semantic-kernel-v2
python -m unittest -v test_semantic_kernel.py test_kaggriculture_adapter.py
python snapshot_adoption_gate.py
```

Current gate result: **PASS — semantic default scope**.

The recorded output is in:

`snapshot-adoption-gate-result.json`

This PASS means the Snapshot candidate satisfies the current semantic adoption gate:

- one immutable snapshot per step;
- frozen eligibility;
- declaration-order independence;
- newly-open Rules deferred to the next step;
- resource and operational feasibility handled after eligibility;
- invalid plans execute nothing and commit no next State.

## Boundary

The PASS does **not** establish:

- terminal-score or win-rate improvement;
- Battle integration correctness;
- that every future Kaggriculture Action can be represented without extending Action metadata;
- that Snapshot can never need revision after real Battle evidence.

It establishes only that Snapshot is now coherent enough to become the default semantic mode for the next adapter/integration stage.

Current route:

`Parent Spec -> Pure Semantic Kernel -> 6/6 -> Kaggriculture Fixture Adapter -> 5/5 -> Snapshot Adoption Gate: PASS -> Kaggriculture Adapter -> Battle Integration`
