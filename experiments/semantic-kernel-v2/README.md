# Semantic Kernel v2 Spike

Minimal, Kaggriculture-independent spike for the Rule Engine semantics in the v2 parent spec.

## Scope

This experiment fixes only the semantic boundary:

`StateSnapshot -> evaluate -> resolve -> plan -> apply -> next StateSnapshot`

It deliberately does **not** integrate with Kaggriculture, battle strategy, or Adoption Policy execution.

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

## Run

```bash
cd experiments/semantic-kernel-v2
python -m unittest -v test_semantic_kernel.py
```

## Boundary

Passing these tests is evidence of semantic consistency for the small pure-state model only. It is not yet evidence that Snapshot semantics improves Kaggriculture terminal score or should be adopted as the final production semantics.

Next gate after this spike:

`6 fixture tests -> Snapshot Adoption Gate -> Kaggriculture Adapter -> Battle Integration`
