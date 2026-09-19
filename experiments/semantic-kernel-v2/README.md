# Semantic Kernel v2 Spike

Minimal semantic-kernel spike for the Rule Engine contract in the Kaggriculture v2 parent spec.

## Scope

The semantic boundary remains:

`StateSnapshot -> evaluate -> resolve -> plan -> apply -> next StateSnapshot`

The kernel itself is Kaggriculture-independent. A thin fixture adapter now maps the WHEAT3 / LAND boundary into this model without connecting to Battle runtime.

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
- `plan()` validates the selected Action bundle. Resource insufficiency or ambiguous non-commutative writes invalidate the **bundle**; they do not erase selected Rules.
- `apply()` applies an already-valid bundle. It never re-evaluates triggers or resolves Rules.

This preserves:

`eligible != selected != executed`

## Important spike decision

Resource over-claim is treated as a **planning failure** in this spike.

Example trace shape:

```text
eligible: [A, B]
selected: [A, B]
planned: invalid
reason: resource_claim_conflict:cash
executed: []
```

That choice directly tests the parent contract that `plan()` must not silently rewrite Rule selection.

## Six semantic conformance cases

1. Two compatible eligible Rules compose.
2. A mutates state so B's trigger would become false; B remains eligible in the current step.
3. Reverse declaration order produces the same outcome.
4. Two selected Actions over-claim the same resource; plan is invalid and neither Rule disappears.
5. A opens C; C waits until the next step.
6. Non-commutative Actions with no dependency/phase are rejected; explicit phase makes the plan deterministic.

Local result: **6 / 6 PASS**.

## Kaggriculture fixture adapter

`kaggriculture_adapter.py` maps the current WHEAT3 / LAND semantic fixture into the kernel.

The adapter deliberately requires `land_claim` as an explicit input. It does not infer or invent the production BUY_LAND resource claim.

Adapter gate cases verify:

- unknown `land_claim` remains Unknown and is rejected at the adapter boundary;
- a jointly feasible WHEAT3 / LAND fixture preserves both eligibility and selection;
- an over-claiming fixture stops at `plan()` without erasing either selected Rule;
- reversing Rule declaration order does not change the result.

Local result: **4 / 4 PASS**.

## Snapshot Adoption Gate

Run:

```bash
cd experiments/semantic-kernel-v2
python -m unittest -v test_semantic_kernel.py test_kaggriculture_adapter.py
python snapshot_adoption_gate.py
```

Current gate result: **HOLD**.

Reason: semantic adapter behavior is consistent, but the production BUY_LAND resource claim is still Unknown in current factory evidence. The gate refuses to upgrade Snapshot to production semantics by guessing that domain value.

The recorded output is in:

`snapshot-adoption-gate-result.json`

## Boundary

The current evidence proves only:

- the pure semantic kernel passes its six conformance fixtures;
- the thin WHEAT3 / LAND adapter preserves the kernel responsibility split;
- Unknown domain data can remain Unknown without collapsing the pipeline.

It does **not** yet prove:

- the production BUY_LAND claim or operational requirements;
- that Snapshot semantics should be the final Kaggriculture runtime default;
- terminal-score or win-rate improvement;
- Battle integration correctness.

Current route:

`Parent Spec -> Pure Semantic Kernel -> 6/6 -> Fixture Adapter -> 4/4 -> Snapshot Adoption Gate: HOLD -> resolve domain evidence -> Kaggriculture Adapter -> Battle Integration`
