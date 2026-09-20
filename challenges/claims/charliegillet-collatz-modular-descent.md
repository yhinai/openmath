# Claim: 01-openmath/collatz-modular-descent

worker: charliegillet
started: 2026-09-20
status: done               # in-progress | done | stalled | abandoned
branch: main (committed directly)

## Approach

Taking over the unclaimed failing draft in solution/. Literature first, then an
exact-arithmetic search scored by the hill's own eval.py; a self-generated fixture
is used only where private.lock locks real held-out data.

## Result

passed=true in both modes, against a SELF-GENERATED fixture (hidden targets not recoverable).

```
command: cd 01-openmath/collatz-modular-descent/solution && python3 tools/verify_local.py
output:  [validation] coverage_ppm=989242 min_descent_ppm=250000 rule_count=503 passed=true
         [final]      coverage_ppm=722728 min_descent_ppm=250000 rule_count=503 passed=true
         [universe] classes=3968 coverable=3352 coverage_mismatches=0
```
Full verbatim JSON is in solution/README.md.

## Limitations

- coverage_ppm above is on my fixture; the real hidden score is unknown and will differ.
- What IS proven: eval.py restricts targets to odd classes mod 2^8..2^12 (3968 classes).
  Exactly 3352 admit any valid rule; the submission covers all 3352. So coverage is the
  maximum attainable for ANY hidden target list. Re-derived independently by the
  coordinator from eval.py's rule conditions alone: same 3352, 0 missing.
- min_descent_ppm=250000 is NOT proven optimal; giving every class its best margin
  needs >= 649 rules, over the 512 cap.
- rule_count=503 is minimal for the target-independent guarantee, not for the hidden list.
- scripts/verify_all.py reports FAILED for this hill: it has no fixture to supply.
