# heilbronn-triangle — solution (n = 11)

## Result

`min_area = 0.03652988988003022` (evaluator float), 30 digits
`0.0365298898800302164248471279616`.

This is the AlphaEvolve n=11 configuration, **re-solved exactly** at 140-digit
precision and submitted with 120 significant digits per coordinate. The
`hill/examples/alphaevolve/points.json` example, whose coordinates are plain
doubles, scores `0.03652988988003013` /
`0.0365298898800301230967422996169`. The baseline example scores
`0.0317227922374209557424134398892`.

So this submission **beats both bundled examples**, but only in the last digits:
the configuration is the same one AlphaEvolve found; the gain (~9.3e-17,
about 11 ulps of the float metric) comes entirely from removing the rounding
error in the published double-precision coordinates.

| submission | min_area (float) | min_area (30 digits) |
|---|---|---|
| `hill/examples/baseline` | 0.031722792237420956 | 0.0317227922374209557424134398892 |
| `hill/examples/alphaevolve` | 0.03652988988003013 | 0.0365298898800301230967422996169 |
| **this solution** | **0.03652988988003022** | **0.0365298898800302164248471279616** |

Not proven optimal. Heilbronn optima are unproven for n = 11; this is the best
*known* configuration, and independent random-restart search here never found a
better basin (best from scratch in ~30 min of 8-way parallel search: 0.03358).

## How it was found

1. **Literature first.** Best known value for n=11 in a unit-area triangle is
   AlphaEvolve's (2025) construction, ≈ 0.0365298898800302; the previous record
   was Cantrell's 0.0360+ (2006, Erich Friedman's page). See Sources.
2. **Independent search** (`tools/optimize2.py`): basin hopping over random
   restarts, each polished by sequential linear programming — the 165 triple
   determinants are linearised and an LP maximises the worst case subject to
   the three containment half-planes and a trust region. 8 parallel workers.
   From scratch this reached 0.0335766506; seeded from the AlphaEvolve point it
   never escaped that basin. It did **not** beat the literature.
3. **Exact polish** (`tools/polish.py`). At the optimum 17 triples are tied at
   the minimum and 6 points sit on the container's edges (2 on the bottom, 2 on
   the left, 2 on the right). That is 17 + 6 = 23 equations in 23 unknowns
   (22 coordinates + the common tied area t) — a square system, solved with
   `mpmath.findroot` at `mp.dps = 140` starting from the AlphaEvolve doubles.
   The resulting value,
   `0.03652988988003021642484712796158011223847`, agrees to every printed digit
   with the independent high-precision value published on the community
   heilbronn-site (`0.0365298898800302164248471279615801122384728660`).

Container convention (from `hill/eval.py`): vertices (0,0), (1,0), (1/2, √3/2);
the metric is min over the 165 triples of |twice-signed-area| divided by √3/2.

## Reproduction

```bash
PY=/private/tmp/claude-501/-Users-charlie-hackathons-openmath/eff8d621-7309-442b-9162-07db54bf13dc/scratchpad/hillenv/bin/python  # needs numpy, mpmath, scipy
cd /Users/charlie/hackathons/openmath/challenges/03-hello-hills-v2/heilbronn-triangle

# exact re-derivation of the submitted points (writes solution/points.json)
$PY solution/tools/polish.py hill/examples/alphaevolve/points.json solution/points.json 140 120

# score it with the hill's own eval.py (imported from a temp copy of hill/)
$PY solution/tools/verify_local.py solution

# independent search (optional, long): basin hopping, seed 1, 1800 s
$PY solution/tools/optimize2.py 1 /tmp/best.json 1800
```

## Verbatim evaluator output

`solution/tools/verify_local.py` imports `eval.py` from a temporary copy of
`hill/` (nothing under `hill/` is touched). No `hill/private/*` is read by this
hill's evaluator — it states "There is no held-out data" — so no fixture was
needed.

```
--- final=False ---
{
  "config": [
    {
      "name": "n",
      "primary": true,
      "value": 11
    },
    {
      "name": "region",
      "primary": false,
      "value": "unit equilateral triangle"
    }
  ],
  "details": {
    "min_area_30_digits": "0.0365298898800302164248471279616",
    "smallest_triangle": [
      3,
      6,
      7
    ]
  },
  "metrics": [
    {
      "direction": "max",
      "name": "min_area",
      "value": 0.03652988988003022
    }
  ],
  "passed": true
}
--- final=True ---
{
  "config": [
    {
      "name": "n",
      "primary": true,
      "value": 11
    },
    {
      "name": "region",
      "primary": false,
      "value": "unit equilateral triangle"
    }
  ],
  "details": {
    "min_area_30_digits": "0.0365298898800302164248471279616",
    "smallest_triangle": [
      3,
      6,
      7
    ]
  },
  "metrics": [
    {
      "direction": "max",
      "name": "min_area",
      "value": 0.03652988988003022
    }
  ],
  "passed": true
}
```

`python3 scripts/verify_all.py --hill heilbronn-triangle` run from
`/Users/charlie/hackathons/openmath/challenges` — note the repo's `python3` has
no `mpmath`, so the same script was run with the venv interpreter:

```
========================================================================
HILL: 03-hello-hills-v2/heilbronn-triangle
  [validation] passed=True {'min_area': 0.03652988988003022}
        details: {'min_area_30_digits': '0.0365298898800302164248471279616', 'smallest_triangle': [3, 6, 7]}
  [final] passed=True {'min_area': 0.03652988988003022}
        details: {'min_area_30_digits': '0.0365298898800302164248471279616', 'smallest_triangle': [3, 6, 7]}
========================================================================
VERDICT: all checked solutions passed
```

With the system `python3` the same command prints:

```
========================================================================
HILL: heilbronn-triangle
  ERROR: eval.py import failed: No module named 'mpmath'
========================================================================
VERDICT: SOME CHECKS FAILED
```

## Limitations

- **Not a new construction.** The configuration is AlphaEvolve's; only its
  coordinates are new (exact critical point instead of doubles).
- **Not proven optimal** for n = 11, and no global optimality certificate was
  attempted. Certified optima in the triangle are published only up to n = 8.
- The search in step 2 was float64 only and modest (about 30 CPU-minutes);
  absence of a better basin is weak evidence, not proof.
- The exact minimal polynomial claimed by the community site (degree 16) was
  **not** verified here; only the decimal value was reproduced independently.

## Sources

- AlphaEvolve results notebook (n=11 triangle construction and its coordinates):
  https://github.com/google-deepmind/alphaevolve_results —
  https://raw.githubusercontent.com/google-deepmind/alphaevolve_results/main/mathematical_results.ipynb
- "Mathematical exploration and discovery at scale", arXiv:2511.02864
  (Problem 6.48; reports the n=11 improvement over the previous record):
  https://arxiv.org/abs/2511.02864
- Erich Friedman, "The Heilbronn Problem for Triangles" (n=11: "A = .0360+",
  David Cantrell, July 2006) — page currently 404, read via the Wayback
  Machine: https://erich-friedman.github.io/packing/heiltri/ ,
  https://web.archive.org/web/2024/https://erich-friedman.github.io/packing/heiltri/
- Community record site, high-precision n=11 value used as a cross-check:
  https://raw.githubusercontent.com/tejstead/heilbronn-site/HEAD/data/canonical/triangle/n11.json
- Certified optima for n ≤ 8 in the unit triangle: https://arxiv.org/html/2607.15021v1
