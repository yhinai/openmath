#!/usr/bin/env python3
"""Floating-point hill climb over +-1 matrices up to 8x8 looking for
vector/sign ratio > sqrt(2). Exploratory only (alternating maximisation gives a
LOWER estimate of the SDP value). Writes best-so-far to hillclimb_best.json."""
import json, sys, time, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from draft_random_search import sign_opt, optimize
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
T = float(sys.argv[1]) if len(sys.argv) > 1 else 300
out = pathlib.Path(__file__).parent / "hillclimb_best.json"
best = (0, None); t0 = time.time()
def ratio(M): return optimize(M, restarts=6, iters=120, rng=rng)[0] / sign_opt(M)
while time.time() - t0 < T:
    m, n = rng.integers(2, 9), rng.integers(2, 9)
    M = rng.integers(0, 2, size=(m, n)) * 2 - 1
    r = ratio(M)
    for _ in range(150):
        i, j = rng.integers(m), rng.integers(n)
        M[i, j] *= -1; r2 = ratio(M)
        if r2 >= r: r = r2
        else: M[i, j] *= -1
    if r > best[0]:
        best = (r, M.tolist()); out.write_text(json.dumps({"ratio": r, "matrix": best[1]}))
        print(m, n, r, flush=True)
