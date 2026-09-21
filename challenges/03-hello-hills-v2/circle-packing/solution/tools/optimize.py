#!/usr/bin/env python3
"""Maximise sum of radii of n non-overlapping circles in the unit square.

Method: SLSQP on all 3n variables (x, y, r) with analytic Jacobians, from many
random restarts, plus perturbation restarts around the incumbent best.
Best-so-far is written to disk (raw float JSON) after every improvement.
"""
import json, os, sys, time
import numpy as np
from scipy.optimize import minimize, linprog

N = 26

def unpack(z):
    return z[:N], z[N:2*N], z[2*N:]

IU, JU = np.triu_indices(N, 1)

def neg_sum(z):
    return -z[2*N:].sum()

def neg_sum_jac(z):
    g = np.zeros(3*N); g[2*N:] = -1.0
    return g

def cons_f(z):
    x, y, r = unpack(z)
    wall = np.concatenate([x - r, 1 - x - r, y - r, 1 - y - r])
    dx = x[IU] - x[JU]; dy = y[IU] - y[JU]; rs = r[IU] + r[JU]
    pair = dx*dx + dy*dy - rs*rs
    return np.concatenate([wall, pair])

def cons_jac(z):
    x, y, r = unpack(z)
    m = 4*N + len(IU)
    J = np.zeros((m, 3*N))
    idx = np.arange(N)
    J[idx,        idx]       =  1; J[idx,        2*N+idx] = -1   # x - r
    J[N+idx,      idx]       = -1; J[N+idx,      2*N+idx] = -1   # 1-x-r
    J[2*N+idx,    N+idx]     =  1; J[2*N+idx,    2*N+idx] = -1   # y - r
    J[3*N+idx,    N+idx]     = -1; J[3*N+idx,    2*N+idx] = -1   # 1-y-r
    dx = x[IU] - x[JU]; dy = y[IU] - y[JU]; rs = r[IU] + r[JU]
    k = 4*N + np.arange(len(IU))
    J[k, IU]       =  2*dx; J[k, JU]       = -2*dx
    J[k, N+IU]     =  2*dy; J[k, N+JU]     = -2*dy
    J[k, 2*N+IU]   = -2*rs; J[k, 2*N+JU]   = -2*rs
    return J

CONS = [{"type": "ineq", "fun": cons_f, "jac": cons_jac}]
BND = [(0.0, 1.0)]*(2*N) + [(0.0, 0.5)]*N

def radii_lp(x, y):
    """Given centres, exactly maximise sum r by LP."""
    A, b = [], []
    for i in range(N):
        for v in (x[i], 1-x[i], y[i], 1-y[i]):
            row = np.zeros(N); row[i] = 1.0
            A.append(row); b.append(max(v, 0.0))
    for i, j in zip(IU, JU):
        row = np.zeros(N); row[i] = 1.0; row[j] = 1.0
        A.append(row); b.append(np.hypot(x[i]-x[j], y[i]-y[j]))
    res = linprog(-np.ones(N), A_ub=np.array(A), b_ub=np.array(b),
                  bounds=[(0, 0.5)]*N, method="highs")
    return res.x if res.success else None

def polish(z0):
    res = minimize(neg_sum, z0, jac=neg_sum_jac, bounds=BND, constraints=CONS,
                   method="SLSQP", options={"maxiter": 400, "ftol": 1e-12})
    return res.x

def feasible_value(z, margin=1e-12):
    """Shrink radii so all constraints hold with slack, return (z, sum)."""
    x, y, r = z[:N].copy(), z[N:2*N].copy(), z[2*N:].copy()
    x = np.clip(x, 0, 1); y = np.clip(y, 0, 1)
    r = np.minimum(r, np.minimum.reduce([x, 1-x, y, 1-y]))
    r = np.maximum(r, 0.0)
    # iteratively fix pair overlaps by shrinking the larger radius
    for _ in range(200):
        d = np.hypot(x[IU]-x[JU], y[IU]-y[JU])
        over = r[IU] + r[JU] - d
        bad = over > -margin
        if not bad.any():
            break
        for k in np.where(bad)[0]:
            i, j = IU[k], JU[k]
            exc = r[i] + r[j] - d[k] + margin
            if r[i] >= r[j]:
                r[i] = max(r[i] - exc, 0.0)
            else:
                r[j] = max(r[j] - exc, 0.0)
    r = np.minimum(r, np.minimum.reduce([x, 1-x, y, 1-y]) - margin)
    r = np.maximum(r, 0.0)
    # HARD final check: if the greedy repair did not converge, reject outright.
    d = np.hypot(x[IU]-x[JU], y[IU]-y[JU])
    if (r[IU] + r[JU] - d > 0).any() or (r <= 0).any():
        return np.concatenate([x, y, r]), -1.0
    if (r - np.minimum.reduce([x, 1-x, y, 1-y]) > 0).any():
        return np.concatenate([x, y, r]), -1.0
    return np.concatenate([x, y, r]), r.sum()

def random_start(rng):
    x = rng.uniform(0.05, 0.95, N); y = rng.uniform(0.05, 0.95, N)
    r = radii_lp(x, y)
    if r is None:
        r = np.full(N, 0.02)
    return np.concatenate([x, y, r])

def perturb(z, rng, scale):
    x, y, r = z[:N].copy(), z[N:2*N].copy(), z[2*N:].copy()
    k = rng.integers(1, 6)
    for _ in range(k):
        i = rng.integers(N)
        x[i] = rng.uniform(0.02, 0.98); y[i] = rng.uniform(0.02, 0.98)
    x += rng.normal(0, scale, N); y += rng.normal(0, scale, N)
    x = np.clip(x, 0.001, 0.999); y = np.clip(y, 0.001, 0.999)
    rr = radii_lp(x, y)
    if rr is None:
        rr = r
    return np.concatenate([x, y, rr])

def write(path, z, val):
    x, y, r = z[:N], z[N:2*N], z[2*N:]
    obj = {"circles": [{"x": float(x[i]), "y": float(y[i]), "r": float(r[i])}
                       for i in range(N)]}
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)
    print(f"[write] sum_radii={val!r}", flush=True)

def main():
    out = sys.argv[1]
    seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rng = np.random.default_rng(seed)
    t0 = time.time()
    best_z, best = None, -1.0
    if os.path.exists(out):
        d = json.load(open(out))
        z = np.array([c["x"] for c in d["circles"]] + [c["y"] for c in d["circles"]]
                     + [c["r"] for c in d["circles"]])
        best_z, best = feasible_value(z)
        print(f"[seed-in] {best!r}", flush=True)
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        if best_z is None or rng.random() < 0.35:
            z0 = random_start(rng)
        else:
            z0 = perturb(best_z, rng, rng.choice([0.005, 0.02, 0.06]))
        try:
            z = polish(z0)
            # re-solve radii exactly then polish once more
            r = radii_lp(z[:N], z[N:2*N])
            if r is not None:
                z = polish(np.concatenate([z[:N], z[N:2*N], r]))
            zf, val = feasible_value(z)
        except Exception:
            continue
        if val > best:
            best, best_z = val, zf
            write(out, best_z, best)
    print(f"[done] iters={it} best={best!r}", flush=True)

if __name__ == "__main__":
    main()
