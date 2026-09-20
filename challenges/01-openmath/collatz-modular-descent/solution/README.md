# collatz-modular-descent — solution

## Result

`solution.json`: 503 exact descent rules, all with `modulus_power <= 12`, 29280 bytes.

The hidden target lists (`private/validation.json` 941 B, `private/test.json` 1142 B) are real
held-out data and were NOT recovered, so **the real scores are unknown**. What is proven
(exhaustively, by `tools/verify_local.py`, using eval.py's own `_verify_rule` and `_covers`)
holds for every possible hidden target list:

1. **coverage_ppm is the maximum attainable**, whatever the hidden targets are. Targets are odd
   classes mod 2^K, 8<=K<=12; a rule covers a target only if its modulus_power <= K <= 12, and
   eval.py forces sum(exponents) <= modulus_power-1 <= 11. All 10641 valid rules with k<=12 were
   enumerated; 3352 of the 3968 possible target classes are coverable by some rule
   (94/128, 203/256, 421/512, 869/1024, 1765/2048 per level) and this submission covers every
   one of them. The other 616 classes cannot be covered by ANY valid submission.
2. **min_descent_ppm is the maximum attainable whenever that maximum is <= 55/64 (859375 ppm)**:
   every coverable class receives margin >= min(its best possible margin, 55/64). Giving every
   class its pointwise best margin needs at least 649 rules (exact tree DP), over the 512 cap, so a
   cap is unavoidable; 55/64 is the largest threshold whose exact minimum (503) fits in 512.
   If the hidden list happens to contain only classes whose best margin exceeds 55/64 (1074 of 3352 coverable classes, about 32%,
   are such; for ~15+ targets all being such is very unlikely but possible),
   a differently tuned submission could score a higher min_descent_ppm. Not proven optimal there.
3. **rule_count = 503 is NOT minimal for the actual hidden list.** Someone who knew the ~20 hidden
   targets could use ~20 rules. 503 is the exact minimum for the target-independent guarantee
   in (1)+(2) (tree DP, `tools/tree_dp.py`). This is a deliberate trade: metrics 1 and 2
   dominate metric 3 lexicographically. Cheaper alternatives (exact minima), via
   `python3 tools/tree_dp.py --write T`:

```
T= 0 tau=13/256       (0.050781)  min rules=107
T= 1 tau=5/32         (0.156250)  min rules=121
T= 2 tau=1/4          (0.250000)  min rules=145
T= 3 tau=295/1024     (0.288086)  min rules=191
T= 4 tau=47/128       (0.367188)  min rules=191
T= 5 tau=7/16         (0.437500)  min rules=219
T= 6 tau=269/512      (0.525391)  min rules=256
T= 7 tau=37/64        (0.578125)  min rules=279
T= 8 tau=5/8          (0.625000)  min rules=318
T= 9 tau=1319/2048    (0.644043)  min rules=351
T=10 tau=175/256      (0.683594)  min rules=351
T=11 tau=23/32        (0.718750)  min rules=382
T=12 tau=781/1024     (0.762695)  min rules=418
T=13 tau=101/128      (0.789062)  min rules=418
T=14 tau=13/16        (0.812500)  min rules=454
T=15 tau=431/512      (0.841797)  min rules=473
T=16 tau=55/64        (0.859375)  min rules=503
T=17 tau=1805/2048    (0.881348)  min rules=535
T=18 tau=229/256      (0.894531)  min rules=535
T=19 tau=29/32        (0.906250)  min rules=563
T=20 tau=943/1024     (0.920898)  min rules=575
T=21 tau=119/128      (0.929688)  min rules=575
T=22 tau=485/512      (0.947266)  min rules=595
T=23 tau=61/64        (0.953125)  min rules=615
T=24 tau=1967/2048    (0.960449)  min rules=623
T=25 tau=247/256      (0.964844)  min rules=623
T=26 tau=997/1024     (0.973633)  min rules=635
T=27 tau=125/128      (0.976562)  min rules=635
T=28 tau=503/512      (0.982422)  min rules=639
T=29 tau=2021/2048    (0.986816)  min rules=646
T=30 tau=253/256      (0.988281)  min rules=646
T=31 tau=1015/1024    (0.991211)  min rules=648
T=32 tau=509/512      (0.994141)  min rules=648
T=33 tau=2039/2048    (0.995605)  min rules=649
T=34 tau=1021/1024    (0.997070)  min rules=649
T=35 tau=2045/2048    (0.998535)  min rules=649
```
   (T=0, 107 rules, is the exact minimum for maximal coverage alone.)

## How found

Rules sit on nodes (k, r) of the binary tree of odd residues mod 2^k; a rule covers the target
nodes in its subtree. `tools/build_solution.py` enumerates every valid rule (all prefixes of the
accelerated trajectory that eval.py accepts: valuation pattern, k >= sum+1, 3^m < 2^s, strict
descent of the least representative; note r=1 never descends, so e.g. 1 mod 2^k is uncoverable
while 17 mod 32 is). `tools/tree_dp.py` keeps the best-margin rule per node and solves the
minimum rule count exactly by DP over (node, best margin among chosen ancestors), for each margin
threshold. Exact ints/Fractions throughout.

## Verification (self-generated fixture — real hidden score may differ)

Fixtures: random odd classes mod 2^8..2^12, weights 1..1000 (18 and 22 targets, seeds 1 and 2),
written only into a temp copy of hill/. Coverage on the real list depends on how many hidden
targets fall in the 616 uncoverable classes (uniformly ~15.5% of classes).

Command: `python3 tools/verify_local.py`  (from this directory). Verbatim output:

```
[validation] {"config": [{"name": "certificate", "primary": true, "value": "accelerated-collatz-residue-descent"}, {"name": "target_family", "primary": true, "value": "private-odd-dyadic-residues"}, {"name": "mode", "primary": false, "value": "validation"}], "details": {"covered_weight": 11035, "private_targets_scored": 18, "rules_verified": 503, "total_weight": 11155}, "metrics": [{"direction": "max", "name": "coverage_ppm", "value": 989242}, {"direction": "max", "name": "min_descent_ppm", "value": 250000}, {"direction": "min", "name": "rule_count", "value": 503}], "passed": true}
[final] {"config": [{"name": "certificate", "primary": true, "value": "accelerated-collatz-residue-descent"}, {"name": "target_family", "primary": true, "value": "private-odd-dyadic-residues"}, {"name": "mode", "primary": false, "value": "test"}], "details": {"covered_weight": 9832, "private_targets_scored": 22, "rules_verified": 503, "total_weight": 13604}, "metrics": [{"direction": "max", "name": "coverage_ppm", "value": 722728}, {"direction": "max", "name": "min_descent_ppm", "value": 250000}, {"direction": "min", "name": "rule_count", "value": 503}], "passed": true}
[universe] classes=3968 coverable=3352 coverage_mismatches=0 margin_below_min(best,55/64)=0
```

`python3 scripts/verify_all.py --hill collatz-modular-descent` (from challenges/), verbatim.
It reports failure only because it has no fixture for this hill (the evaluator cannot open the
missing private files); it does not test the rules:

```
========================================================================
HILL: 01-openmath/collatz-modular-descent
  NOT recovered: private/test.json (real held-out data; fixture must be supplied)
  NOT recovered: private/validation.json (real held-out data; fixture must be supplied)
  [validation] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpm06lcrll/hill/private/validation.json'"}
  [final] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpm06lcrll/hill/private/test.json'"}
========================================================================
VERDICT: SOME CHECKS FAILED
```

## Limitations / skipped

- Hidden files not recovered; `scripts/crack_budget.py` was not run since the schema is a list
  of ~20 (modulus_power, residue, weight) records, far outside brute-force range.
- hill/tests not run (needs the `hills` package).
- `drafts_previous_worker/` holds an earlier worker's unfinished scripts; not part of the answer
  (its 240 KB candidates.json was deleted; build_solution.py regenerates the enumeration).

## Sources

- Terras, stopping time density; Everett; Garner — background as summarised in
  Winkler, "New results on the stopping time behaviour of the Collatz 3x+1 function", https://arxiv.org/pdf/1504.00212v2
- Winkler, "On the structure and the behavior of Collatz 3n+1 sequences", https://arxiv.org/pdf/1412.0519
- Tao, blog on Collatz and powers of 2 and 3, https://terrytao.wordpress.com/2011/08/25/the-collatz-conjecture-littlewood-offord-theory-and-powers-of-2-and-3/
- OEIS A100982 (number of residue classes mod 2^s with given stopping time), https://oeis.org/A100982
