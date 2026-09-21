# Claim: 03-hello-hills-v2/heilbronn-triangle

worker: charliegillet
started: 2026-09-20
status: done               # in-progress | done | stalled | abandoned
branch: main (committed directly)

## Approach

Literature/published optima first, then local search scored by the hill's own eval.py.

## Result

passed=true in both modes. min_area = 0.03652988988003022
(30 digits: 0.0365298898800302164248471279616)

```
command: cd 03-hello-hills-v2/heilbronn-triangle/solution && python3 tools/verify_local.py
coordinator scored all three with the hill's eval.py (final=True):
  baseline     0.0317227922374209557424134398892
  alphaevolve  0.0365298898800301230967422996169
  OURS         0.0365298898800302164248471279616
```

## Limitations

- This is NOT a new configuration. It is AlphaEvolve's own n=11 configuration,
  re-solved at 140-digit precision. The margin over the bundled alphaevolve example
  is 9.33e-17 absolute / 2.55e-15 relative (about 11 ulps of the float metric), and
  comes ENTIRELY from removing rounding error in that example's double-precision
  coordinates. Do not present this as beating AlphaEvolve.
- Independent search from scratch never found this basin: best was 0.03358 after
  ~30 min of 8-way parallel basin hopping. The result is a reproduction.
- Not proven optimal - Heilbronn optima are unproven for n=11.
