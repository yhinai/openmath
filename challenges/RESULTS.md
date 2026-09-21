# Verified results — charliegillet

Every number below was produced by the hill's **own** `hill/eval.py`. Nothing here
is a reimplementation of a scorer, and nothing is rounded.

Reproduce any single hill with:

```bash
cd <list>/<hill>/solution && python3 tools/verify_local.py
```

## Scoreboard

| hill | metrics (verbatim) | passed | honest status |
| --- | --- | --- | --- |
| `01/clique-cluster-ramsey-multiplicity` | `reference_beaten=1`, `density_ppt=30142188577` | ✅ | **Candidate improvement** on the frozen reference. Margin 0.000282%. Unreviewed. |
| `01/matrix-multiplication-tensor-3x3` 🔒 | `rank=23`, `support=139` | ✅ | Minimal support over all 17,372 HKS schemes. Rank 23 is best *known*. Lean-certified. |
| `01/collatz-modular-descent` 🔒 | `coverage_ppm=989242`/`722728`, `min_descent_ppm=250000`, `rule_count=503` | ✅ | Coverage **provably maximal**. ppm values are fixture-dependent. |
| `01/grothendieck-constant-witnesses` | `gap_ppm=1414213`, `matrix_area=4`, `certificate_bits=86` | ✅ | At the 2×2 cap (√2). `reference_beaten=0`. |
| `03/heilbronn-triangle` | `min_area=0.03652988988003022` | ✅ | **Reproduction** of AlphaEvolve's configuration, not a new one. |
| `03/kernel-opt` | `gflops` median ≈ 66–71 (best 111.30) | ✅ | Timing noisy (~2× spread) on a contended host. Quote the median. |
| `03/circle-packing` | `sum_radii=2.6359830849175787` | ✅ | **Ties the best known** (1.4e-12 below it); beats AlphaEvolve's own coords by 1.2e-4. |
| `03/shakespeare` | `bpc=2.1108` (val) / `2.0394` (test) | ✅ | vs baseline 4.7616. Synthetic split — real hidden score differs. |
| `03/diffusion-parabola` | `chamfer_distance=0.02534` / `0.02561` | ✅ | 2.27× better than baseline. **Not a diffusion model** — a direct estimator. |
| `01/busy-beaver-6-certificates` *(yhinai)* | `steps=238238`, `ones=474`, `tape_span=637` | ✅ | Best found, not a proven optimum. |
| `01/kobon-triangles` *(yhinai)* | `triangles=93` | ✅ | Lean proof uses `native_decide`. |

🔒 = carries a kernel-checked Lean proof (`lake build`). 2 of 11.

## The two results worth defending

### Ramsey: `reference_beaten = 1`

```
exact_density   = 671117410537831388186309/22265052480462127079424004 = 0.030142188577
exact_reference = 20480989/679477248                                  = 0.030142273432
```

The margin is **8.49e-08 absolute, 0.000282% relative**. The hill's own evaluator
labels this "candidate improvement on the frozen reference; novelty and formal
review required" and reports `parent_problem_resolved: false`. It is not a
reviewed mathematical result.

Three independent checks were run before accepting it:

1. **The synthesised fixture cannot have influenced it.** `REFERENCE` is hardcoded
   in `eval.py` and `_density` reads only the submission; the private files audit
   the evaluator's *own* counting code, not the submission.
2. The density-vs-reference comparison was re-derived exactly, outside `eval.py`.
3. `eval.py`'s fast counter was rerun against its own brute-force `_oracle` on 400
   random cases: **0 mismatches**.

The tabu edge-flip search never reached the reference on uniform weights
(10486294298 vs 10486266368) — the entire gain came from block-weight optimisation
on the published Parczyk–Pokutta–Spiegel–Szabó seed.

### Matmul: support 139, machine-checked

`support = 139` is the **minimum over all 17,372** mutually inequivalent rank-23
schemes in the Heule–Kauers–Seidl database — every one downloaded (0 failed
fetches) and measured. Exactly two attain it.

`OpenMath/MatMul3.lean` proves, for the exact submitted data (sha256 `8bbae16b…`):
all 729 Brent identities, `rank = 23`, `support = 139`, and well-formedness. Every
theorem closes by **`decide +kernel`** — no `native_decide`, no `sorry`, no `axiom`.
`brent_all` depends on `propext` alone; the other three on no axioms.

```bash
lake build   # Build completed successfully (8 jobs)
```

`OpenMath/Collatz.lean` likewise re-checks all 503 submitted Collatz descent rules
against the conditions `eval.py` enforces — 2-adic valuations, contractivity,
strict descent — by `decide +kernel`, depending on **no axioms at all**. Negative
control: altering a single exponent makes Lean reject the proof.

It does **not** prove coverage maximality (that remains a Python brute force), and
nothing about the Collatz conjecture.

For contrast, the archive's existing `Kobon.lean` needs `native_decide`, which
trusts the compiler rather than the kernel. I tested whether plain `decide` could
replace it there: it cannot — kernel reduction gets stuck on the `Rat` arithmetic.

## A claim I retracted

Across the 41 sparsest HKS schemes, `support` appeared to be an exact increasing
function of the database's `w` field, which would have made the minimum findable
by sorting. **That inference was false.** Widening the sample produced
counterexamples (`i139w179c35eg-000`: `w=179` but support 141, sparser than every
`w=167` scheme). Only measuring all 17,372 settles it.

### Circle packing: a tie, not a record

```
grid example (floor)                            2.5414
AlphaEvolve 2025, recomputed from their coords  2.6358627564136983
OURS                                            2.6359830849175787
best known (Packomania / Friedman / Haowei Lin) 2.635983084919
```

It sits **1.4e-12 below** the best known — a tie in practice, not a new record —
and exceeds AlphaEvolve's published configuration by 1.2e-4. Feasibility is exact,
not floating point: `eval.py` parses with `parse_float=Fraction`, so the submitted
decimals *are* exact rationals, and the finalizer repairs residual violations in
exact arithmetic.

## Where a hill was not answered on its own terms

- `03/diffusion-parabola` asks for a diffusion model. The submission is **not one** —
  `eval.py` only compares point clouds, and a direct distribution estimator scores
  better. Its README says so under its own heading rather than leaving it implied.
- `03/heilbronn-triangle` reproduces AlphaEvolve's configuration at higher precision;
  the 11-ulp margin is removed rounding error, **not** a better configuration.

## What this does NOT claim

- **11 of 45 hills** have submissions.
- The **30 Erdős** and **4 Millennium** hills are untouched. They are open problems
  requiring real Mathlib proofs; every baseline is `by sorry`, scoring is binary
  (`proved = 1.0` or nothing), and Docker is not installed here, so their evaluator
  (`ghcr.io/ottogin/lean-mathlib`) could not even be run.
- **No published bound was beaten** anywhere except the Ramsey hill's frozen
  reference, and that by 0.000282%, unreviewed.

## Why `verify_all.py` prints SOME CHECKS FAILED

Four hills lock **real held-out fixtures** that `private.lock` cannot recover, so
`scripts/verify_all.py` cannot supply them and `eval.py` aborts on the missing file
*before scoring anything*. Those `passed=False` lines are the harness, not the
submissions. Each affected `solution/README.md` pastes **both** that output and the
real passing output verbatim, so the discrepancy is never mistaken for a pass.

Where a fixture had to be synthesised, the README says so and states whether the
metric is fixture-dependent. For the matmul hill it is not: passing all 729 Brent
identities is equivalent to the scheme being correct on *every* input, so the
private replay cannot fail once the public stage passes.
