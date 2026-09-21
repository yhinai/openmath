# Claim: 03-hello-hills-v2/kernel-opt

worker: charliegillet
started: 2026-09-20
status: done               # in-progress | done | stalled | abandoned
branch: main (committed directly)

## Approach

Literature/published optima first, then local search scored by the hill's own eval.py.

## Result

passed=true in both modes. gflops is HIGHLY VARIABLE on this contended host.

```
command: cd 03-hello-hills-v2/kernel-opt/solution && python3 tools/verify_local.py
agent-reported: best 111.30 (test) / 108.34 (validation); median over 9 runs 65.8 / 70.9
coordinator re-ran 5x: 54.99, 101.69, 105.63, 98.08, 77.27  (passed=true every run)
```
Report the MEDIAN, not the peak. Machine: Apple M4 arm64, Apple clang 17.0.0.

## Limitations

- gflops is hardware-dependent and NOT comparable across machines.
- Run-to-run variance on this host is close to 2x (54.99 to 105.63 in 5 coordinator
  runs) because 5 agents were running concurrently. The peak figure is not a stable
  measurement; the median is the honest number.
- Single-threaded hand-written NEON kernel: no threads, OpenMP, BLAS/Accelerate/AMX,
  assembly, or special-casing of evaluator inputs. Verified by inspection.
- The real held-out seeds were not recovered; the fixture is synthesised.
- Speedup over baseline (~98x on medians) inherits the same timing noise.
