# matrix-multiplication-tensor-3x3 — rank 23, support 139

An exact rank-23 decomposition of the 3×3 matrix-multiplication tensor over ℚ,
with 139 nonzero coefficients across `u`, `v`, `w`, all in {−1, 0, +1}.

**Result: `rank = 23`, `support = 139`, `passed: true`.**

23 is the **best known** rank, *not* a proven optimum, and 139 is the **best
found** support, not a proven minimum. See *Limitations*.

## Result

```
rank    = 23      (metric direction: min)
support = 139     (metric direction: min)   nonzeros: u 45, v 45, w 49
passed  = true    (729/729 Brent identities, exact arithmetic over Q)
```

## How it was found

The submitted scheme is `i41w163c235e-000` from the Heule–Kauers–Seidl database
of 17,372 mutually inequivalent rank-23 schemes for 3×3 matrix multiplication,
published alongside *New ways to multiply 3×3-matrices*.

**All 17,372 schemes were downloaded and measured** (0 failed fetches, 0 malformed
files). Support 139 is the **minimum over the entire database**, attained by exactly
two schemes — `i41w163c235e-000` and `i41w163c367g-000`. The distribution at the
sparse end is 139:2, 140:3, 141:5, 142:7, 143:13, 144:35. Reproduce the scan with
`tools/scan_hks_database.py`.

The hill's secondary metric `support` counts nonzero coefficients. The recent
literature on rank-23 3×3 schemes instead minimises **additions after
common-subexpression elimination**, which is a different objective — so the
published addition records (56, 52) do not bound this metric, and a scheme with
few additions is not automatically sparse. Measuring schemes directly on
`support` is what produced the result here.

Every candidate was parsed, re-oriented into the hill's index convention, and
checked against all 729 Brent identities before being measured.

| scheme | source | support |
| --- | --- | --- |
| **`i41w163c235e-000` — submitted** | Heule–Kauers–Seidl database | **139** |
| `i44w165c235e-000` (next best) | Heule–Kauers–Seidl database | 140 |
| Laderman 1976 | HKS `classic/laderman.tab`, and Sedoglavic's database at λ=1 | 153 |
| flip-graph `gg-333-rank23` | `khoruzhii/flip-cpd` | 155 |
| 56-addition ternary scheme | arXiv:2604.27645 | 175 |

Two independent sources — the HKS `classic/laderman.tab` file and Sedoglavic's
Maple tensor file specialised at λ=1 — both give Laderman at support **153**,
which is a useful cross-check that the parsing and orientation logic is right.

### The database's own `w` is not this metric

HKS scheme names encode a weight, e.g. `i41w163c235e-000` has `w=163`, but that
is **not** `support`: the same scheme measures 139, and the database's page for
Laderman reports "Weight: 219" where `support` is 153. Over the 41 lowest-`w`
schemes `support` looked like an exact increasing function of `w`, which would
have made `w=163` the database-wide minimum — **but that inference is false.**
Widening the sample found schemes whose support falls *below* that line (e.g.
`i139w179c35eg-000` has `w=179` but support 141, sparser than every `w=167`
scheme). So `support` is **not** monotone in `w`: sorting on `w` is unsound, which
is why the whole database had to be measured rather than just its low-`w` head.

### Searches that did **not** improve on the published schemes

`tools/search_support.py` implements a flip-graph local search (Kauers–Moosbauer
transitions) annealed directly on `support`, with factors matched up to
*proportionality* over ℚ — each rank-one term is defined only up to scalars, so
proportional matching is exact and admits strictly more moves than exact equality.
A sandwich-symmetry orbit search over `u → P u Q⁻¹`, `v → Q v R⁻¹`, `w → R w P⁻¹`
was also run, allowing rational coefficients.

**Neither found anything better than the published schemes**, from any starting
point tried. The flip graph around these schemes is move-poor: the Laderman scheme
has only three proportional factor pairs, giving roughly six available moves, so
the walk explores a small neighbourhood. The entire improvement from 153 to 139
came from measuring published schemes, not from my search.

## Reproducing the verification

`hill/private/{validation,test}.json` are real held-out replay fixtures. Unlike
the busy-beaver hill, `private.lock` here locks genuine data rather than a tiny
parameter file, so `scripts/crack_budget.py` cannot recover it. A fixture matching
the schema in `eval.py` is synthesised instead.

**This does not weaken the check.** `eval.py` verifies all 729 Brent identities
first, from public data alone. Passing them is equivalent to the scheme computing
`A·B` correctly for **every** input, so the private replay stage is mathematically
implied and cannot fail once the Brent stage passes, whatever the hidden matrices
contain. The fixture only supplies well-formed input so that stage can run.

```bash
cd 01-openmath/matrix-multiplication-tensor-3x3/solution/tools
python3 verify_local.py
```

Verbatim output:

```
[validation] {"config": [{"name": "tensor", "primary": true, "value": "3x3-general-matrix-multiplication"}, {"name": "coefficient_domain", "primary": true, "value": "exact-rationals"}, {"name": "verification", "primary": true, "value": "729-brent-identities"}, {"name": "mode", "primary": false, "value": "validation"}], "details": {"brent_identities_checked": 729, "coefficient_domain": "Q", "private_replays_checked": 16}, "metrics": [{"direction": "min", "name": "rank", "value": 23}, {"direction": "min", "name": "support", "value": 139}], "passed": true}
[final] {"config": [{"name": "tensor", "primary": true, "value": "3x3-general-matrix-multiplication"}, {"name": "coefficient_domain", "primary": true, "value": "exact-rationals"}, {"name": "verification", "primary": true, "value": "729-brent-identities"}, {"name": "mode", "primary": false, "value": "test"}], "details": {"brent_identities_checked": 729, "coefficient_domain": "Q", "private_replays_checked": 16}, "metrics": [{"direction": "min", "name": "rank", "value": 23}, {"direction": "min", "name": "support", "value": 139}], "passed": true}
```

An independent cross-check, not using `eval.py` at all — multiplying 300 random
integer matrix pairs through the scheme and comparing against ordinary 3×3
multiplication — gives **0 mismatches**.

### The archive-wide verifier reports FAILED for this hill

```bash
python3 scripts/verify_all.py --hill matrix-multiplication-tensor-3x3
```

```
========================================================================
HILL: 01-openmath/matrix-multiplication-tensor-3x3
  NOT recovered: private/test.json (real held-out data; fixture must be supplied)
  NOT recovered: private/validation.json (real held-out data; fixture must be supplied)
  [validation] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpo99j15hi/hill/private/validation.json'"}
  [final] passed=False 
        details: {'error': "[Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpo99j15hi/hill/private/test.json'"}
========================================================================
VERDICT: SOME CHECKS FAILED
```

That `passed=False` is **not** a failure of the submission. `verify_all.py` only
reconstructs hidden files that are tiny parameter files; it cannot synthesise a
replay fixture, so `eval.py` aborts on the missing file before scoring anything.
The `passed: true` above comes from the same `eval.py` with the fixture supplied.
Both outputs are reported so the discrepancy is not mistaken for a passing run.

## Limitations — what this does NOT prove

- **Rank 23 is best known, not proven optimal.** Whether 3×3 matrix multiplication
  is possible with 22 multiplications is open; the best published lower bound on
  the tensor's rank is 19 (Bläser). Nothing here narrows that gap.
- **Support 139 is best found, not proven minimal.** No lower bound on `support`
  is established or claimed.
- **139 is the minimum of the HKS database, but that database is not exhaustive.**
  All 17,372 schemes were measured and none is sparser. That settles the database,
  not the question: HKS show the rank-23 schemes form a manifold of dimension at
  least 17, so infinitely many schemes lie outside their catalogue and a sparser
  one may be among them.
- **`reference_beaten = 0`.** No published bound was beaten. The submitted scheme
  is a published one, selected by measuring it on this hill's metric. Selecting the
  sparsest member of a published database is not a new construction, and my own
  searches found nothing better than what was published.
- **Not verified against the real held-out fixture**, which is unavailable. The
  argument that the replay is implied by the Brent identities is mathematical,
  given above; it was not executed against the hill author's actual data.

## Sources

- M. J. H. Heule, M. Kauers, M. Seidl, *New ways to multiply 3×3-matrices*,
  J. Symbolic Computation 104 (2021). https://arxiv.org/abs/1905.10192
  Scheme database: http://www.algebra.uni-linz.ac.at/research/matrix-multiplication/
  (the https endpoint serves an expired/self-signed certificate; the http endpoint
  serves the same files. Every downloaded scheme is validated against all 729
  Brent identities before use, so a corrupted or tampered download cannot yield a
  wrong result — it simply fails verification.)
- J. D. Laderman, *A noncommutative algorithm for multiplying 3×3 matrices using
  23 multiplications*, Bull. AMS 82 (1976) 126–128.
  https://doi.org/10.1090/S0002-9904-1976-13988-2
- A. Sedoglavic, *Fast Matrix Multiplication Algorithms Database*.
  https://fmm.univ-lille.fr/3x3x3.html
- M. Kauers, J. Moosbauer, *Flip graphs for matrix multiplication*.
  https://arxiv.org/abs/2212.01175
- *An Exact 56-Addition, Rank-23 Scheme for General 3×3 Matrix Multiplication*.
  https://arxiv.org/abs/2604.27645
- flip-graph scheme dataset: https://github.com/khoruzhii/flip-cpd

## Files

- `solution.json` — the submission: `u`, `v`, `w`, each 23×9, integer coefficients.
- `tools/verify_local.py` — runs the hill's own `eval.py` with a synthesised fixture.
- `tools/parse_tab.py` — parses an HKS `.tab` scheme, finds the Brent-valid
  orientation in the hill's convention, and measures `support`.
- `tools/build_solution.py` — rebuilds Laderman (support 153) from Sedoglavic's
  Maple file; kept as the independent cross-check of the parsing logic.
- `tools/search_support.py` — flip-graph / symmetry support search (no improvement).
- `tools/scan_hks_database.py` — measures `support` for every scheme in a directory
  of HKS `.tab` files; reproduces the database-wide minimum of 139.
