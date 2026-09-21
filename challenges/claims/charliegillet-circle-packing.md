# Claim: 03-hello-hills-v2/circle-packing

worker: charliegillet
started: 2026-09-20
status: done               # in-progress | done | stalled | abandoned
branch: main (committed directly)

## Approach

Literature/published optima first, then local search scored by the hill's own eval.py.

## Result

passed=true. sum_radii = 2.6359830849175787

```
grid example (floor)                              2.5414
AlphaEvolve 2025, recomputed from their coords    2.6358627564136983
OURS                                              2.6359830849175787
best known (Packomania / Friedman / Haowei Lin)   2.635983084919
```

## Limitations

- Essentially MATCHES the best-known record: 1.4e-12 below it, which is a tie for
  practical purposes, not a new record. It does exceed AlphaEvolve's published
  configuration (+1.2e-4) as recomputed with this hill's own evaluator.
- Not proven optimal; optimal packings for n=26 are unproven.
- Feasibility is exact, not floating point: eval.py parses numbers with
  parse_float=Fraction, and the finalizer snaps centres to exact 25-place decimals,
  re-solves the radii LP exactly, and repairs residual violations in exact arithmetic.
