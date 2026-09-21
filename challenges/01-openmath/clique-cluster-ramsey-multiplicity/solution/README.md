# clique-cluster-ramsey-multiplicity — solution

## Result

`solution.json` is a 768-block weighted two-colour template (schema
`weighted-two-color-blowup-v1`, all diagonals blue, integer weights in
3684..4249, weight sum 3071998).  The hill's own `hill/eval.py` returns, for
both `final=False` and `final=True`:

- `passed = True`
- `reference_beaten = 1`
- `density_ppt = 30142188577`
- `exact_density = 671117410537831388186309/22265052480462127079424004`
  (= 0.0301421885772... ; the frozen reference is McKay's
  10486266368/768^4 = 0.0301422734319...)
- `exact_reference_gap = 320934908917024358050415581/3782149146499994969038324915765248` (positive)

So by the hill's lifting lemma (hill/LIFTING.md) this certifies
c4 <= 0.03014218858 (rounded up), which is below the frozen reference
0.03014227343 by about 8.5e-8.  This is the best value **found**; it is not
claimed to be optimal, and by the hill's own wording it is a "candidate
improvement on the frozen reference; novelty and formal review required".
Whether a better bound exists in unpublished work (e.g. later experiments by
McKay) was not checked beyond arXiv:2206.04036v3's final note.

## How it was found

1. Seed: the published 768-vertex Cayley graph of Parczyk-Pokutta-Spiegel-Szabo
   (`hill/examples/published_cayley_768/solution.json`, density
   4551721/150994944 = 0.03014486, uniform weights).
2. Tabu edge-flip search on the template with uniform weights and blue
   diagonal (`tools/tabu.c`).  The objective T = red + blue ordered
   monochromatic 4-tuples (denominator 768^4) is maintained incrementally
   with exact 64-bit integers via per-pair common-neighbourhood edge counts;
   every 5000 moves it is re-checked against a from-scratch recount.  Runs
   used tabu tenure 400 (20 min), then 1000 (25 min), then 1000 (12 min),
   9 parallel seeds each round, keeping the best.  Result: T = 10486294298
   (uniform-weight density 0.03014224, still ABOVE the reference
   10486266368).  This is the same kind of move McKay used (switching
   edge/non-edge pairs); our pure-flip result did not reach his.
3. Block weights (`tools/wopt.c`): projected gradient descent on the quartic
   density P(w) over the simplex, in double precision, then rounded to
   integers with scale 4000 (weights 3684..4249).  40 iterations from the
   previous round's weights.  Floating point is used ONLY inside the
   heuristic; the submission is re-scored exactly by eval.py, which is the
   only number reported.
4. `tools/make_solution.py` writes `solution.json` from
   `tools/template.rows` + `tools/template.weights`.

Reproduce (heuristic; wall-clock-limited runs are not bit-reproducible):
`sh tools/run_search.sh`.  Re-score the committed file exactly:

```
cd challenges/01-openmath/clique-cluster-ramsey-multiplicity/solution
python3 tools/verify_local.py          # ~1 min per mode with non-uniform weights
```

## Verification and the private fixtures

`eval.py` reads `hill/private/validation.json` / `test.json`, which are not
distributed (private.lock: 310 and 337 bytes; not a brute-forceable
one-integer file, `scripts/crack_budget.py` finds nothing).  In eval.py those
files are used only by `_audit()`, which cross-checks the evaluator's fast
counter against its literal oracle on small fixtures and echoes the suite id;
they do not enter the score.  `tools/verify_local.py` copies `hill/` to a
temp dir, writes synthetic fixtures of the same schema there (never into
`hill/`), and runs the unmodified eval.py.  Consequently `audit_suite` in the
output below is our synthetic id, not the organiser's; the official audit
with the organiser's fixtures is unverified here but cannot change the
metrics.

Verbatim `python3 tools/verify_local.py` output (final=False then final=True):

```
[validation] {"config": [{"name": "protocol", "primary": true, "value": "k4-weighted-blowup-v1"}, {"name": "reference", "primary": true, "value": "10486266368/768^4"}, {"name": "mode", "primary": false, "value": "validation"}], "details": {"asymptotic_bound": "c4 <= exact_density by the weighted blow-up lemma", "audit_suite": "synthetic-local-validation", "blue_numerator": "1350342031249919741797988", "exact_density": "671117410537831388186309/22265052480462127079424004", "exact_reference": "20480989/679477248", "exact_reference_gap": "320934908917024358050415581/3782149146499994969038324915765248", "parent_problem_resolved": false, "raw_denominator": "89060209921848508317696016", "red_numerator": "1334127610901405810947248", "research_status": "candidate improvement on the frozen reference; novelty and formal review required", "target_achieved": true, "template_blocks": 768, "trust_boundary": "Python integer certificate check plus mathematical lifting lemma; no approved proof-assistant acceptance is asserted", "weight_sum": 3071998}, "metrics": [{"direction": "max", "name": "reference_beaten", "value": 1}, {"direction": "min", "name": "density_ppt", "value": 30142188577}], "passed": true}
[final] {"config": [{"name": "protocol", "primary": true, "value": "k4-weighted-blowup-v1"}, {"name": "reference", "primary": true, "value": "10486266368/768^4"}, {"name": "mode", "primary": false, "value": "test"}], "details": {"asymptotic_bound": "c4 <= exact_density by the weighted blow-up lemma", "audit_suite": "synthetic-local-test", "blue_numerator": "1350342031249919741797988", "exact_density": "671117410537831388186309/22265052480462127079424004", "exact_reference": "20480989/679477248", "exact_reference_gap": "320934908917024358050415581/3782149146499994969038324915765248", "parent_problem_resolved": false, "raw_denominator": "89060209921848508317696016", "red_numerator": "1334127610901405810947248", "research_status": "candidate improvement on the frozen reference; novelty and formal review required", "target_achieved": true, "template_blocks": 768, "trust_boundary": "Python integer certificate check plus mathematical lifting lemma; no approved proof-assistant acceptance is asserted", "weight_sum": 3071998}, "metrics": [{"direction": "max", "name": "reference_beaten", "value": 1}, {"direction": "min", "name": "density_ppt", "value": 30142188577}], "passed": true}
```

Verbatim `python3 scripts/verify_all.py --hill clique-cluster-ramsey-multiplicity`
(run from `challenges/`).  It fails as expected because that generic script
does not supply the private fixtures (FileNotFoundError is caught by eval.py
as OSError); it is not a failure of the submission:

```
========================================================================
HILL: 01-openmath/clique-cluster-ramsey-multiplicity
  NOT recovered: private/test.json (real held-out data; fixture must be supplied)
  NOT recovered: private/validation.json (real held-out data; fixture must be supplied)
  [validation] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmplsl5jnjn/hill/private/validation.json'"}
  [final] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmplsl5jnjn/hill/private/test.json'"}
========================================================================
VERDICT: SOME CHECKS FAILED
```

## Limitations / what was not done

- Not proven optimal; the search was ~1 hour of tabu + gradient descent.
  Further tabu/weight alternation (flips evaluated under non-uniform
  weights, diagonal colour changes, more blocks) was not tried.
- Evaluation time with non-uniform weights is about 30-60 s per mode on this
  machine (limit 480 s).
- Novelty relative to unpublished work is not established.

## Sources

- O. Parczyk, S. Pokutta, C. Spiegel, T. Szabo, New Ramsey Multiplicity
  Bounds and Search Heuristics, arXiv:2206.04036v3 (final Note records
  McKay's 10486266368/768^4): https://arxiv.org/abs/2206.04036 ,
  https://arxiv.org/html/2206.04036v3
- Their construction data (seed graph c4.graph6.txt):
  https://doi.org/10.5281/zenodo.6364588
- Hill statement and lifting lemma: `../hill/README.md`, `../hill/LIFTING.md`,
  `../hill/SOURCES.md`.
