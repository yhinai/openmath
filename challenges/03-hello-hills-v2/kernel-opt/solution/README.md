# kernel-opt — solution

**Result: `passed=True` in both validation and test mode. Best observed `gflops` = 111.30 (test) / 108.34 (validation); median over 9 runs = 65.8 (test) / 70.9 (validation).**

Machine: **Apple M4 (arm64, Darwin 27.0.0)**, Apple clang 17.0.0. GFLOP/s is hardware-
dependent — these numbers are not comparable to any other host.

## What the submission is

`kernel.c` defines `void gemm(int n, const float *A, const float *B, float *C)`
(row-major, n x n, C = A @ B), exactly the signature `hill/eval.py` loads with
ctypes. `solution.json` mirrors the baseline example's file; eval.py does not
read it.

## How it works

A textbook BLIS-style blocked SGEMM, written from scratch:

- **Register blocking:** an 8x12 micro-kernel holding the whole C tile in NEON
  registers (24 accumulator vectors + 3 B vectors + 2 A vectors = 29 of the 32
  architectural `v` registers), using `vfmaq_laneq_f32` so each A element is
  lane-broadcast against three B vectors. 24 FMAs per k-step, zero C traffic in
  the inner loop.
- **Packing:** A and B blocks are copied into contiguous, micro-kernel-ordered
  buffers (`pack_a` gathers 8 rows of A k-major; `pack_b` copies 12 columns of B
  per k with three vector loads). The inner loop then walks both panels purely
  sequentially.
- **Cache blocking:** loops over `NC=512`, `KC=512`, `MC=256`. Edge tiles are
  handled by zero-padding the packed panels and writing back through a small
  8x12 scratch tile, so the kernel is correct for every `n`, not just multiples
  of 8 and 12.
- Accumulation across k-blocks is load-modify-store; for `n <= 512` `KC=512`
  means there is only one k-block, so C is written once.

**Not used:** no threads, no OpenMP, no BLAS / Accelerate / AMX, no assembly,
no inline `#pragma omp`, no special-casing of the evaluator's inputs or sizes.
The only library calls are `aligned_alloc`/`free`. A portable blocked scalar
path is compiled instead on non-AArch64 targets (dead code here).

## How it was found

1. Scored the hill's own `examples/baseline` first as the floor.
2. Wrote the 8x12 packed micro-kernel; it scored ~105 GFLOP/s on the first try.
3. Swept `MC x KC x NC` over 60 combinations with a standalone bench (same
   compiler flags eval.py uses, best-of-30 at n=512). All combinations landed
   between ~100 and ~116 GFLOP/s — at n=512 the working set is small enough
   that tile size barely matters on an M4 (128 KB L1D, 16 MB L2). Picked
   `MC=256, KC=512, NC=512`.
4. Tried software prefetch of the packed panels: consistently slightly *slower*
   (105-109 vs 110-113 in three paired runs). Dropped.

Roughly 110-116 GFLOP/s is about 80% of the M4 P-core's fp32 NEON FMA peak.
Reaching higher would likely need hand-written assembly or AMX/SME, which is
out of scope for a hand-written NEON kernel.

## Measurement variance — read this before trusting a single number

eval.py times **best-of-3** of a single n=512 multiply. At ~110 GFLOP/s that is
**~2.4 ms per rep**, so the measurement is extremely sensitive to scheduling
noise, and this machine was running other agents concurrently during the whole
session.

Nine consecutive evaluator runs of the *same* binary, `gflops`:

| run | validation | test |
|---|---|---|
| 1 | 61.56 | 54.67 |
| 2 | 70.81 | 65.77 |
| 3 | 70.85 | 84.78 |
| 4 | 66.17 | 111.69 |
| 5 | 107.42 | 111.42 |
| 6 | 69.79 | 42.82 |
| 7 | 90.03 | 70.90 |
| 8 | 103.26 | 57.28 |
| 9 | 108.34 | 42.15 |

median 70.85 (validation) / 65.77 (test); max 108.34 / 111.69; min 61.56 / 42.15.
That is a ~2.6x spread across identical runs. The isolated standalone bench
(best of 30 reps, no Python/ctypes/NumPy in the loop) is much steadier at
**110-116 GFLOP/s**, which is the honest estimate of the kernel's speed; the
evaluator number on an idle machine should land near the top of the table.
The hill declares `exclusive: cpu` for exactly this reason — the official
scoring run is not contended, this local machine was.

Baseline, same conditions, 5 validation runs: 0.660, 0.736, 0.720, 0.663, 0.807
GFLOP/s (median 0.720).

**Speedup over baseline:** ~98x on medians (70.85 / 0.720); ~150x on best-of
(108.34 / 0.720); ~155x comparing the steady standalone bench figure to the
baseline median.

## Reproduction

```bash
cd challenges/03-hello-hills-v2/kernel-opt/solution
PY=/private/tmp/claude-501/-Users-charlie-hackathons-openmath/eff8d621-7309-442b-9162-07db54bf13dc/scratchpad/hillenv/bin/python
$PY tools/verify_local.py            # validation mode
$PY tools/verify_local.py --final    # test mode
$PY tools/test_shapes.py             # correctness sweep over 26 sizes
```

(The default `python3` on this machine has no NumPy, which `eval.py` imports.)

`tools/verify_local.py` copies `hill/` to a temp directory, drops in a
**synthesised** `private/seeds.json`, and calls the hill's own unmodified
`eval.py`. Nothing under `hill/` is touched.

### About the synthesised fixture — stated plainly

`hill/private/seeds.json` is **not** distributed. `private.lock` gives only its
size (91 bytes) and sha256; `scripts/crack_budget.py` only enumerates
single-integer parameter files and cannot recover a two-list seed file, so the
real seeds were **not** recovered. `tools/verify_local.py` substitutes
`{"validation": [11, 22, 33], "test": [101, 202, 303]}`, the schema eval.py
requires (`seeds["test" if final else "validation"]`, iterated, with
`seeds[0] + 1` as the timing RNG seed). Seeds only choose which random matrices
are drawn; they affect neither correctness (verified across 26 sizes and many
seeds) nor timing. The `checksum` values below therefore will not match the
official run's.

## Verbatim evaluator output

### `final=False` (validation)

```json
{
  "passed": true,
  "metrics": [
    {
      "name": "gflops",
      "value": 106.60310093582808,
      "direction": "max"
    }
  ],
  "config": [
    {
      "name": "mode",
      "value": "validation",
      "primary": true
    },
    {
      "name": "n",
      "value": 512,
      "primary": true
    },
    {
      "name": "tolerance",
      "value": 0.002,
      "primary": true
    },
    {
      "name": "machine",
      "value": "Charlies-MacBook-Pro.local",
      "primary": true
    }
  ],
  "details": {
    "seconds_best_of_3": 0.0025180829979944974,
    "timings_seconds": [
      0.0025180829979944974,
      0.0044299589935690165,
      0.006683792002149858
    ],
    "compiler": "Apple clang version 17.0.0 (clang-1700.0.13.5)",
    "compiler_flags": [
      "-O3",
      "-march=native",
      "-ffast-math",
      "-shared",
      "-fPIC",
      "-lm"
    ],
    "architecture": "arm64",
    "platform": "Darwin",
    "checksum": 9297.318359375
  }
}
```

### `final=True` (test)

```json
{
  "passed": true,
  "metrics": [
    {
      "name": "gflops",
      "value": 111.30129236615164,
      "direction": "max"
    }
  ],
  "config": [
    {
      "name": "mode",
      "value": "test",
      "primary": true
    },
    {
      "name": "n",
      "value": 512,
      "primary": true
    },
    {
      "name": "tolerance",
      "value": 0.002,
      "primary": true
    },
    {
      "name": "machine",
      "value": "Charlies-MacBook-Pro.local",
      "primary": true
    }
  ],
  "details": {
    "seconds_best_of_3": 0.0024117910070344806,
    "timings_seconds": [
      0.0025085829984163865,
      0.0024117910070344806,
      0.002644499996677041
    ],
    "compiler": "Apple clang version 17.0.0 (clang-1700.0.13.5)",
    "compiler_flags": [
      "-O3",
      "-march=native",
      "-ffast-math",
      "-shared",
      "-fPIC",
      "-lm"
    ],
    "architecture": "arm64",
    "platform": "Darwin",
    "checksum": 9601.744140625
  }
}
```

These two are single runs, taken back-to-back; see the variance table above for
the full spread.

## Verbatim `python3 scripts/verify_all.py --hill kernel-opt`

Run from `/Users/charlie/hackathons/openmath/challenges` with the NumPy-enabled
interpreter:

```
HILL: 03-hello-hills-v2/kernel-opt
  NOT recovered: private/seeds.json (real held-out data; fixture must be supplied)
  [validation] passed=None FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpsg7f4rsm/hill/private/seeds.json'
  [final] passed=None FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/t4/3kjjx5vj47d2hs8zcbkm61sr0000gn/T/tmpsg7f4rsm/hill/private/seeds.json'
========================================================================
VERDICT: SOME CHECKS FAILED
```

`verify_all.py` cannot score this hill: it tries to recover `private/seeds.json`
from `private.lock` and fails (as explained above), and it offers no way to
supply a fixture. The `FileNotFoundError` is that missing file, not a defect in
the submission — `tools/verify_local.py` runs the identical `eval.py` with a
fixture in place and reports `passed: true`.

## Correctness

`tools/test_shapes.py` checks C = A @ B against NumPy for
n = 1, 2, 3, 7, 8, 11, 12, 13, 17, 31, 64, 96, 97, 127, 128, 129, 200, 256, 257,
383, 384, 511, 512, 513, 640, 1024 — all pass, max relative error 9.9e-8 (the
evaluator's tolerance is 2e-3). eval.py itself re-verifies every timed
repetition against NumPy with fresh random data, so the timing cannot be gamed
by caching, and no such trick is attempted here.

## Limitations

- Timing on this host is heavily contended; treat the median, not the peak, as
  what was actually observed here.
- The real held-out seeds were not recovered; the fixture is synthesised.
- Tile sizes were tuned only at n=512 (the scored size) on an M4. Other sizes
  and other Apple cores may prefer different `MC/KC/NC`.
- Not attempted: hand-written assembly, AMX/SME, `fmla` scheduling by hand,
  larger micro-kernels via register spill analysis.
