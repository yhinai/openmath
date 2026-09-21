# shakespeare — solution

Character-level next-character prediction, metric `bpc` (minimise).

## Result

**Scored against a synthetic held-out split, NOT the hill's real held-out text.**
`hill/private/val.txt` (111540 bytes) is not distributed and is not recoverable
(`scripts/crack_budget.py` only cracks tiny integer parameter files; this is
111 KB of real text). The numbers below come from the hill's **own, unmodified
`eval.py`** run against a stand-in `private/val.txt` that `tools/verify_local.py`
builds from the hill's `train.txt`. **The real hidden score will differ.**

| mode | eval_chars | bpc |
|---|---|---|
| `final=False` (validation) | 8000 | `2.1108186099892166` |
| `final=True` (test) | 8000 | `2.0394005959307` |
| baseline (`hill/examples/baseline`, same harness) | 8000 | `4.7616055352264794` |

Tuning was done on a *different* slice of the pseudo-held-out text
(chars 20000–30000) from the two slices reported above, so those two numbers are
not the ones the hyper-parameters were fitted on. Validation-vs-test gap on the
synthetic split: 2.1108 vs 2.0394 (0.071 bpc); the "test" half of the synthetic
val simply happens to be easier text. Tuning slice: 2.0805; second holdout slice
(40000–50000): 2.1395. Spread across four disjoint 8–10k slices is ~0.06 bpc, so
treat any difference below ~0.05 bpc as noise.

### Verbatim evaluator output

```
### verify_local validation
{"passed": true, "metrics": [{"name": "bpc", "value": 2.1108186099892166, "direction": "min"}], "config": [{"name": "mode", "value": "validation", "primary": true}, {"name": "eval_chars", "value": 8000, "primary": true}], "details": {"chars_scored": 8000}}
### verify_local final
{"passed": true, "metrics": [{"name": "bpc", "value": 2.0394005959307, "direction": "min"}], "config": [{"name": "mode", "value": "test", "primary": true}, {"name": "eval_chars", "value": 8000, "primary": true}], "details": {"chars_scored": 8000}}
```

### `python3 scripts/verify_all.py --hill shakespeare` (from `challenges/`)

```
========================================================================
HILL: 03-hello-hills-v2/shakespeare
  NOT recovered: private/val.txt (real held-out data; fixture must be supplied)
  [validation] passed=None FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpiudxzgpg/hill/private/val.txt'
  [final] passed=None FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpiudxzgpg/hill/private/val.txt'
========================================================================
VERDICT: SOME CHECKS FAILED
```

That failure is the missing hidden fixture, not a failure of the submission:
`verify_all.py` has no `private/val.txt` to score against. Use
`tools/verify_local.py`, which supplies a synthetic one.

## Reproduction

```bash
cd /Users/charlie/hackathons/openmath/challenges/03-hello-hills-v2/shakespeare
python3 solution/tools/verify_local.py            # final=False
python3 solution/tools/verify_local.py --final    # final=True
```
Stdlib only — no numpy, no torch (torch is not installed here and eval.py
imports nothing beyond `importlib.util`, `math`, `sys`, `pathlib`).

## Model

Linear mixture of six variable-order **PPM** (prediction by partial matching)
character models, orders K ∈ {2, 3, 4, 5, 6, 8}.

Each component is a back-off cascade from order K down to order 0 with PPM-C
escape probabilities and **full exclusion**: at each order, over the characters
not already claimed by a higher order, with total count `n` and `t` distinct
characters, `denom = n + ESC*t`, each seen char gets `rem * count/denom`, and
`rem *= ESC*t/denom` is carried to the next lower order. Leftover mass is spread
uniformly over the characters no order proposed, so nothing gets zero
probability (an unsmoothed zero would cost the evaluator's floor, 26.6 bits).
`ESC = 0.8`.

Mixture weights `(0.0088, 0.0667, 0.4236, 0.2381, 0.1805, 0.0823)` were fitted
by EM on the tuning slice. The mixture beats the best single order by ~0.047 bpc
consistently on every holdout slice (e.g. 2.1108 vs 2.1580 on the validation
slice, 2.0394 vs 2.0784 on the test slice for the best single model, K=5).

Counts are built at import time from `train.txt` (a verbatim copy of the hill's
own 1003854-byte training file, shipped beside `model.py` so the module works
from any working directory). Import ≈ 11 s; scoring 8000 chars ≈ 7 s; the
worst case allowed by the hill (`eval_chars=55000`) is ≈ 60 s against a
900 s watchdog. Memory ≈ 0.5 GB (1.6 M contexts). Files: `model.py` 3.4 KB,
`train.txt` 1.0 MB.

## What was tried and rejected

- Interpolated absolute discounting (Kneser-Ney style, no continuation counts),
  orders 5–8, D ∈ {0.5, 0.7, 0.85, 0.95}: best 2.193 on the tuning slice, worse
  than PPM back-off with exclusion (2.145). Rejected.
- Per-order escape weights tuned by coordinate descent at K=7: converged to
  ~2.227, still worse than a plain K=5 model. Deep orders genuinely hurt here.
- Larger single K (9, 11): monotonically worse (2.33, 2.37).

## Limitations / not done

- **The reported bpc is against a self-made split, not the hill's held-out
  text.** The shipped model trains on the *full* `train.txt`; the numbers above
  come from a model trained on `train.txt` minus its last 111540 chars, so the
  real submission has ~12% more training data than what was measured.
- Not done, and likely worth another ~0.1–0.2 bpc: PPM update exclusion
  (incremental counting), secondary symbol estimation (SSE), and a neural
  character model (torch is not installed).
- "Best found", not optimal: the hyper-parameter search was a coarse grid plus
  EM on the mixture weights, on ~10k characters of tuning text.

## Note for the coordinator

The hill's `train.txt` is exactly the first 1003854 characters of the standard
`tinyshakespeare` corpus (1115394 chars) and `private/val.txt` is 111540 bytes —
exactly the remaining 10%. The held-out passage is therefore the tail of a
well-known public-domain corpus and could in principle be obtained. It was
**not** obtained, downloaded, reconstructed, or written from memory, and nothing
in this solution is fitted to it.
