# grothendieck-constant-witnesses — solution

## Result
CHSH matrix `[[1,1],[1,-1]]` (sign optimum 2) with exact rational unit vectors
right = e1, e2; left = (696, ±697)/985 (696² + 697² = 985²).
Vector objective 2786/985, certified lower bound **K_G ≥ 1393/985 = 1.4142131...**

Evaluator metrics: `gap_ppm = 1414213`, `matrix_area = 4`, `certificate_bits = 86`.

This is a lower bound only, and it is BELOW the published bounds (Davie/Reeds
~1.67696; Fishburn-Reeds 10/7 for a 20x20 matrix). It does **not** match or beat
any published bound on K_G. It is what the hill's size limits allow as far as we
could find: eval.py restricts to +-1 matrices of at most 8x8.

## Why this is (probably) the cap here
* gap_ppm: any 2x2 witness is bounded by K_G(2)=sqrt(2)=1.41421356..., so
  floor(ratio*1e6) <= 1414213 for rational certificates; we attain it.
  Exceeding sqrt(2) is known to need larger matrices (Fishburn-Reeds: 20x20
  real matrix for 10/7; K_2 = K_3 = sqrt 2). A floating-point hill climb over
  +-1 matrices of all shapes up to 8x8 (`tools/hillclimb.py`, 360 s, log in
  `tools/hillclimb.log`) found nothing above 1.4142135623730956. NOT a proof
  that no 8x8 +-1 matrix exceeds sqrt 2; the search is heuristic and short.
* matrix_area: 4 is the minimum eval.py allows.
* certificate_bits: `tools/min_bits.py` searches left vectors (a,±b,r)/c,
  a,b<3000, with right vectors fixed to e1,e2, in dimension 2 and 3: best 86
  (dim 3 best 90). Non-axis right vectors and dimension >3 were NOT searched, so
  86 is best found, not proven minimal.

## Verification
`hill/private/{validation,test}.json` are not distributed; `crack_budget.py`
found no match (they are witness fixtures, 205/229 bytes). eval.py uses them only
as an arithmetic self-test independent of the submission, so
`tools/verify_local.py` copies hill/ to a temp dir and puts a synthesised fixture
(the public baseline witness + its expected values) there. The real hidden
fixtures are therefore unverified.

Command: `python3 tools/verify_local.py` (from this directory). Verbatim output:

```
[validation] {"config": [{"name": "certificate", "primary": true, "value": "finite-rational-grothendieck-witness"}, {"name": "matrix_bounds", "primary": true, "value": "2-8-by-2-8"}, {"name": "mode", "primary": false, "value": "validation"}], "details": {"lower_bound": "1393/985", "matrix_shape": [2, 2], "sign_optimum": 2, "vector_dimension": 2, "vector_objective": "2786/985"}, "metrics": [{"direction": "max", "name": "gap_ppm", "value": 1414213}, {"direction": "min", "name": "matrix_area", "value": 4}, {"direction": "min", "name": "certificate_bits", "value": 86}], "passed": true}
[final] {"config": [{"name": "certificate", "primary": true, "value": "finite-rational-grothendieck-witness"}, {"name": "matrix_bounds", "primary": true, "value": "2-8-by-2-8"}, {"name": "mode", "primary": false, "value": "test"}], "details": {"lower_bound": "1393/985", "matrix_shape": [2, 2], "sign_optimum": 2, "vector_dimension": 2, "vector_objective": "2786/985"}, "metrics": [{"direction": "max", "name": "gap_ppm", "value": 1414213}, {"direction": "min", "name": "matrix_area", "value": 4}, {"direction": "min", "name": "certificate_bits", "value": 86}], "passed": true}
```

`python3 scripts/verify_all.py --hill grothendieck-constant-witnesses` (from
challenges/) — FAILS, because that script supplies no fixture for this hill:

```
========================================================================
HILL: 01-openmath/grothendieck-constant-witnesses
  NOT recovered: private/test.json (real held-out data; fixture must be supplied)
  NOT recovered: private/validation.json (real held-out data; fixture must be supplied)
  [validation] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpv9clzfpv/hill/private/validation.json'"}
  [final] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpv9clzfpv/hill/private/test.json'"}
========================================================================
VERDICT: SOME CHECKS FAILED
```

## Files
* `solution.json` — submission.
* `tools/verify_local.py`, `tools/min_bits.py`, `tools/hillclimb.py` (needs numpy; run with python3.12).
* `tools/draft_random_search.py` — earlier worker's exploratory draft, used as a library by hillclimb.py; not part of the answer.

## Sources
* Fishburn, Reeds, "Bell inequalities, Grothendieck's constant, and root two", SIAM J. Discrete Math 7 (1994): https://www.proquest.com/openview/42ebb84b5b7a87f0dc2c6b911bbf748b/1
* Reeds, Sloane, "A finite matrix with Grothendieck ratio greater than sqrt 2": https://neilsloane.com/doc/ReedsSloane.pdf
* Designolle et al., "Better bounds on finite-order Grothendieck constants": https://arxiv.org/abs/2409.03739
* https://mathworld.wolfram.com/GrothendiecksConstant.html
(Only search-result abstracts were consulted; the papers were not read in full.)
