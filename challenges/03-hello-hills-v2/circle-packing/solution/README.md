# circle-packing (n = 26) — solution

## Result

| | `sum_radii` |
|---|---|
| Grid example (`hill/examples/grid`) — the floor | 2.5414 |
| AlphaEvolve (2025), recomputed from their own coordinates | 2.6358627564136983 |
| **This submission** | **2.6359830849175787** |
| Best known (Packomania / Erich Friedman, Haowei Lin) | 2.635983084919 |

`passed = True` in both `final=False` (validation) and `final=True` (test) modes.

This beats the grid floor by +0.0945830849175787 and beats the published
AlphaEvolve figure by +0.0001203285038804. It sits 1.4e-12 below the current
best-known value. **Not proven optimal** — no optimality proof exists for n=26;
every published figure, including this one, is a numerical lower bound.

## How it was found

Independent search — no published coordinates were copied. The search converged
on its own to the same configuration as the best-known packing, agreeing with it
to 11 decimal places.

1. **Global search** (`tools/optimize.py`): SLSQP over all 3n = 78 variables
   (x, y, r) maximising `sum r`, with analytic Jacobians for the 4n wall
   constraints and the 325 pairwise non-overlap constraints. Run from many
   random restarts plus perturbation restarts around the incumbent, 10 workers
   in parallel. Between SLSQP passes the radii are re-solved exactly for the
   fixed centres by a linear program (`radii_lp`), which is the exact optimum of
   the radii subproblem and is what lifts the local optima.
2. **Exact rationalisation** (`tools/finalize.py`). `eval.py` parses every number
   with `parse_float=Fraction`, so the JSON decimals *are* exact rationals. The
   finalizer snaps the centres to exact 25-place decimals, re-solves the radii LP
   against those exact centres, then repairs any residual violation in exact
   `Fraction` arithmetic (bisecting a rational lower bound for each needed square
   root), floors every radius down to 25 places, and re-checks every constraint
   with **tolerance 0**. The submission is therefore feasible exactly, not merely
   within the hill's 1e-9 slack — it would still pass if `tolerance` were set to 0.

The structure found matches the literature description: all four corners occupied
by circles tangent to two walls, most circles edge-tangent, a few large interior
circles, and 26 distinct radii (min 0.0691806763572364, max 0.13701043012374214).

## Reproduction

```bash
PY=/path/to/python            # needs numpy + scipy
HILL=challenges/03-hello-hills-v2/circle-packing

# 1. search (stochastic; ~15 min across 10 parallel workers reaches 2.63598)
$PY $HILL/solution/tools/optimize.py /tmp/best.json 900 4001

# 2. exact rationalisation of the float result into the submission
$PY $HILL/solution/tools/finalize.py $HILL/solution/tools/champion_float.json \
                                     $HILL/solution/solution.json

# 3. score with the hill's OWN eval.py, from a temp copy of hill/
$PY $HILL/solution/tools/verify_local.py $HILL/solution
```

`tools/champion_float.json` is the raw float output of step 1 that step 2 was run
on, so step 2 and step 3 reproduce the submitted numbers deterministically.
Step 1 is stochastic and seed 4001 is the seed that found this configuration.

## Verbatim evaluator output

`python3 solution/tools/verify_local.py solution` (runs `hill/eval.py` unmodified
from a temporary copy of `hill/`):

```
--- final=False ---
{
  "config": [
    {
      "name": "n",
      "primary": true,
      "value": 26
    },
    {
      "name": "mode",
      "primary": true,
      "value": "validation"
    },
    {
      "name": "tolerance",
      "primary": true,
      "value": 1e-09
    }
  ],
  "details": {
    "max_radius": 0.13701043012374214,
    "min_radius": 0.0691806763572364
  },
  "metrics": [
    {
      "direction": "max",
      "name": "sum_radii",
      "value": 2.6359830849175787
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
      "value": 26
    },
    {
      "name": "mode",
      "primary": true,
      "value": "test"
    },
    {
      "name": "tolerance",
      "primary": true,
      "value": 1e-09
    }
  ],
  "details": {
    "max_radius": 0.13701043012374214,
    "min_radius": 0.0691806763572364
  },
  "metrics": [
    {
      "direction": "max",
      "name": "sum_radii",
      "value": 2.6359830849175787
    }
  ],
  "passed": true
}
```

`python3 scripts/verify_all.py --hill circle-packing`, run from
`/Users/charlie/hackathons/openmath/challenges`:

```
========================================================================
HILL: 03-hello-hills-v2/circle-packing
  [validation] passed=True {'sum_radii': 2.6359830849175787}
        details: {'min_radius': 0.0691806763572364, 'max_radius': 0.13701043012374214}
  [final] passed=True {'sum_radii': 2.6359830849175787}
        details: {'min_radius': 0.0691806763572364, 'max_radius': 0.13701043012374214}
========================================================================
VERDICT: all checked solutions passed
```

## Limitations and what was not done

- **Not proven optimal.** n=26 has no optimality proof. This is a numerical
  lower bound from local optimisation, nothing more.
- 1.4e-12 short of the best-known 2.635983084919. A higher-precision Newton
  solve on the tangency system (identify the contact graph, then solve the
  active-constraint system in `mpmath`) would likely close that gap; it was not
  done for time.
- The hill has **no** `private/` directory — `eval.py` says so explicitly and
  reads no fixture — so no fixture had to be synthesised and `crack_budget.py`
  was not needed. Scoring is against the hill's genuine, unmodified `eval.py`.
- A bug was found and fixed mid-run: an earlier version of the greedy feasibility
  repair in `optimize.py` could exhaust its iteration cap and silently return an
  infeasible point, reporting impossible sums above 3.0. It now hard-rejects any
  unconverged repair. Those bogus candidates were discarded and never submitted;
  every number above comes from the hill's own evaluator.

## Sources

- AlphaEvolve results notebook (section B.12, "Packing circles inside a unit
  square to maximize sum of radii"; n=26, 2.634 → 2.635):
  https://github.com/google-deepmind/alphaevolve_results —
  https://colab.research.google.com/github/google-deepmind/alphaevolve_results/blob/master/mathematical_results.ipynb
- AlphaEvolve paper: https://arxiv.org/abs/2506.13131
- Packomania, "circles in a square, maximise sum of radii" (csqv), n=26 =
  2.635983084919: https://www.packomania.com/csqv/csqv.html
  (Note: this csqv table is a *different* objective from the classic Packomania
  equal-circles problem, and is the one this hill uses.)
- Erich Friedman, "Circles in Squares":
  https://erich-friedman.github.io/packing/cirRsqu/
- ShinkaEvolve (2.63597770931127): https://arxiv.org/pdf/2509.19349
- OpenEvolve issue #156 (2.6359773947566274):
  https://github.com/algorithmicsuperintelligence/openevolve/issues/156

Literature values were used only as a *bar to compare against*. No third-party
coordinates were downloaded into, or used to build, this submission, and no
third-party code was executed.
