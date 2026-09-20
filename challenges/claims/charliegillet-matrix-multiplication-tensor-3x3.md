# Claim: 01-openmath/matrix-multiplication-tensor-3x3

worker: charliegillet
started: 2026-09-20
status: done               # in-progress | done | stalled | abandoned
branch: main (committed directly)

## Approach

Reproduce a published rank-23 exact decomposition of the 3x3 matrix-multiplication
tensor over Q and minimise the secondary metric `support` (nonzero coefficients in
u, v, w). Measured published rank-23 schemes directly on this metric and submitted the
sparsest found: i41w163c235e-000 from the Heule-Kauers-Seidl database of 17,372
inequivalent schemes. A flip-graph search annealed on `support` found no
improvement on any published scheme.

## Result

rank = 23, support = 139, passed = true.

```
command: cd 01-openmath/matrix-multiplication-tensor-3x3/solution/tools && python3 verify_local.py
output:  [validation] {"config": [{"name": "tensor", "primary": true, "value": "3x3-general-matrix-multiplication"}, {"name": "coefficient_domain", "primary": true, "value": "exact-rationals"}, {"name": "verification", "primary": true, "value": "729-brent-identities"}, {"name": "mode", "primary": false, "value": "validation"}], "details": {"brent_identities_checked": 729, "coefficient_domain": "Q", "private_replays_checked": 16}, "metrics": [{"direction": "min", "name": "rank", "value": 23}, {"direction": "min", "name": "support", "value": 139}], "passed": true}
         [final] {"config": [{"name": "tensor", "primary": true, "value": "3x3-general-matrix-multiplication"}, {"name": "coefficient_domain", "primary": true, "value": "exact-rationals"}, {"name": "verification", "primary": true, "value": "729-brent-identities"}, {"name": "mode", "primary": false, "value": "test"}], "details": {"brent_identities_checked": 729, "coefficient_domain": "Q", "private_replays_checked": 16}, "metrics": [{"direction": "min", "name": "rank", "value": 23}, {"direction": "min", "name": "support", "value": 139}], "passed": true}
```

Note: `scripts/verify_all.py --hill matrix-multiplication-tensor-3x3` reports
passed=False for this hill. That is the harness being unable to synthesise the
held-out replay fixture, not a failing submission; both outputs are pasted
verbatim in solution/README.md.

## Limitations

- rank 23 is BEST KNOWN, not proven optimal (open gap 19-23; Blaser lower bound 19).
- support 139 is BEST FOUND, not proven minimal. No lower bound claimed.
- 139 IS the minimum over the full HKS database: all 17,372 schemes downloaded and
  measured (0 failures), attained by exactly 2 of them. That settles the database,
  not the question - HKS show the rank-23 schemes form a manifold of dimension >=17,
  so sparser schemes may exist outside the catalogue.
- reference_beaten = 0. No published bound was beaten. The submitted scheme is a
  published one (HKS i41w163c235e-000), selected by measuring it on this hill's
  metric; selecting the sparsest member of a published database is not a new
  construction. My own flip-graph and symmetry-orbit searches found nothing better
  than the published schemes.
- Not verified against the real held-out fixture (unavailable). The replay stage is
  implied by the 729 Brent identities, which are checked from public data.
- The HKS database was reached over its http endpoint (the https endpoint serves an
  expired/self-signed certificate). Every scheme is validated against all 729 Brent
  identities before use, so a tampered download cannot yield a wrong result.
