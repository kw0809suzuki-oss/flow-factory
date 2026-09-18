# Flow Factory

Cloud workspace for turning observed relations into executable experiments.

## Role

Drive is the factory floor for material, jobs, evidence, boundaries, and re-entry.
This repository is the 80 Mesh machine shop: code, tests, comparisons, and ablations.

## Flow

Drive material/job
→ 10 Mesh: keep junk and play branches
→ 50 Mesh: relation candidates
→ **80 Mesh here: build / test / compare / ablate**
→ 95 Mesh: return evidence to Drive

## Rules

- Generate freely; commit carefully.
- Assumptions may be used, but not promoted to observed facts.
- A component candidate needs an observable behavioral difference.
- One successful run is not enough for retention.
- Keep failed experiments when they improve the next observation.
- Prefer small experiments over framework growth.

## Working layout

- `experiments/` — disposable experiments and comparisons
- `components/` — only behavior that survived evidence
- `tests/` — reusable verification
- `docs/` — minimal contracts and handoff notes

The structure should grow from real work, not from planning.
