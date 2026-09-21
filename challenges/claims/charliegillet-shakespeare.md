# Claim: 03-hello-hills-v2/shakespeare

worker: charliegillet
started: 2026-09-20
status: done               # in-progress | done | stalled | abandoned
branch: main (committed directly)

## Approach

Literature/published optima first, then local search scored by the hill's own eval.py.

## Result

passed=true. bpc 2.1108186099892166 (validation) / 2.0394005959307 (test),
AGAINST A SYNTHETIC SPLIT, not the hill's real held-out text.

```
command: cd 03-hello-hills-v2/shakespeare/solution && python3 tools/verify_local.py
ours      validation 2.1108186099892166   test 2.0394005959307
baseline  (same harness)                  4.7616055352264794
```

## Limitations

- THE REAL HIDDEN SCORE WILL DIFFER. hill/private/val.txt (111540 bytes) is real
  held-out text, not recoverable. tools/verify_local.py carves a synthetic stand-in
  from the END of train.txt and stages a submission whose train.txt EXCLUDES that
  slice, so there is no train/test contamination - but it is still not the real text.
- Slice-to-slice spread is ~0.06 bpc across four disjoint 8-10k slices; treat any
  difference below ~0.05 bpc as noise.
- Training data provenance verified by the coordinator: solution/train.txt is
  byte-identical (sha256) to the hill's shipped hill/train.txt. No held-out text
  was obtained, reconstructed, or memorised.
- Character-level n-gram/PPM mixture, not a neural model. Best found, not optimal;
  the README lists PPM update exclusion as untried and likely worth 0.1-0.2 bpc.
