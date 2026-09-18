# LOTO6 Mesh Experiment

First disposable experiment for Flow Factory.

## Question

Can arbitrary observation rules applied to historical LOTO6 draws produce structures that survive comparison with matched random controls?

This is not a lottery prediction claim.

## Source

Historical draw material lives in Google Drive:
`MATERIAL｜ロト6 初期100回｜10 Mesh 構造遊び`

Drive remains the source for material/provenance. This repository holds executable transformations and tests.

## First rule families

1. gap signature
2. circular gap
3. mirror pairs `n ↔ 44-n`
4. residue weave: mod 2 / 3 / 5
5. carryover shadow: overlap and ±1 / ±2 neighborhood
6. empty-space center / largest hole
7. rank motion
8. pair-memory interval
9. shape flip / gap isomorphism
10. rule mutation by 10-draw blocks

## Control

Generate matched controls under the same condition:
- choose 6 unique integers from 1..43
- sort them
- 100 draws per control
- apply exactly the same rule families

A pattern seen in real data is not promoted if comparable structure appears in controls.

## Mesh behavior

### 10 Mesh
Keep odd patterns and weak relations. No prediction claim.

### 50 Mesh
Identify repeatable relation candidates and define measurable features.

### 80 Mesh
Implement metrics, controls, comparisons, and ablations here.

### 95 Mesh
Return only observed differences, boundary, and re-entry to Drive.

## Boundary

Post-hoc rules can manufacture patterns in random data.
Anything interesting remains a candidate until it survives controls and replication.
