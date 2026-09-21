"""Maximin search for the Heilbronn triangle problem in a unit equilateral triangle.

Sequential linear programming (SLP) with a trust region on point moves:
at each step the triple determinants are linearised around the current
configuration and an LP maximises the worst-case |det| subject to the
containment half-planes and a box trust region. Many random restarts.
"""
import sys, json, itertools, numpy as np
from scipy.optimize import linprog

N = int(sys.argv[1]) if len(sys.argv) > 1 else 11
SEED0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
RESTARTS = int(sys.argv[3]) if len(sys.argv) > 3 else 200
OUT = sys.argv[4] if len(sys.argv) > 4 else "best.json"
S3 = np.sqrt(3.0)
TRIPLES = np.array(list(itertools.combinations(range(N), 3)))
AREA = S3 / 2.0  # twice the container area


def dets(P):
    a, b, c = P[TRIPLES[:, 0]], P[TRIPLES[:, 1]], P[TRIPLES[:, 2]]
    return (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])


def score(P):
    return np.abs(dets(P)).min() / AREA


def grads(P):
    """d(det)/d(each coord), shape (T, N, 2) sparse-ish -> dense small."""
    G = np.zeros((len(TRIPLES), N, 2))
    a, b, c = P[TRIPLES[:, 0]], P[TRIPLES[:, 1]], P[TRIPLES[:, 2]]
    idx = np.arange(len(TRIPLES))
    # det = (bx-ax)(cy-ay) - (cx-ax)(by-ay)
    G[idx, TRIPLES[:, 0], 0] = -(c[:, 1] - a[:, 1]) + (b[:, 1] - a[:, 1])
    G[idx, TRIPLES[:, 0], 1] = -(b[:, 0] - a[:, 0]) + (c[:, 0] - a[:, 0])
    G[idx, TRIPLES[:, 1], 0] = (c[:, 1] - a[:, 1])
    G[idx, TRIPLES[:, 1], 1] = -(c[:, 0] - a[:, 0])
    G[idx, TRIPLES[:, 2], 0] = -(b[:, 1] - a[:, 1])
    G[idx, TRIPLES[:, 2], 1] = (b[:, 0] - a[:, 0])
    return G


def rand_point(rng):
    while True:
        x, y = rng.random(), rng.random() * (S3 / 2)
        if y <= S3 * x and y <= S3 * (1 - x):
            return x, y


def slp(P, iters=300, tr0=0.05):
    T = len(TRIPLES)
    tr = tr0
    best = score(P)
    bestP = P.copy()
    for it in range(iters):
        d = dets(P)
        s = np.sign(d)
        s[s == 0] = 1.0
        G = grads(P) * s[:, None, None]
        # vars: dx (2N), t ; maximise t  ->  minimise -t
        # constraints: -(g.dx) + t <= |d|   i.e.  t - g.dx <= s*d
        A = np.zeros((T + 3 * N, 2 * N + 1))
        b = np.zeros(T + 3 * N)
        A[:T, :2 * N] = -G.reshape(T, 2 * N)
        A[:T, 2 * N] = 1.0
        b[:T] = s * d
        # containment: y>=0 ; y <= S3 x ; y <= S3(1-x)
        for i in range(N):
            x, y = P[i]
            r = T + 3 * i
            A[r, 2 * i + 1] = -1.0; b[r] = y
            A[r + 1, 2 * i + 1] = 1.0; A[r + 1, 2 * i] = -S3; b[r + 1] = S3 * x - y
            A[r + 2, 2 * i + 1] = 1.0; A[r + 2, 2 * i] = S3; b[r + 2] = S3 * (1 - x) - y
        cvec = np.zeros(2 * N + 1); cvec[2 * N] = -1.0
        bounds = [(-tr, tr)] * (2 * N) + [(None, None)]
        res = linprog(cvec, A_ub=A, b_ub=b, bounds=bounds, method="highs")
        if not res.success:
            tr *= 0.5
            if tr < 1e-15: break
            continue
        step = res.x[:2 * N].reshape(N, 2)
        Pn = P + step
        sc = score(Pn)
        if sc > best + 1e-18:
            best, bestP, P = sc, Pn.copy(), Pn
            tr = min(tr * 1.3, 0.1)
        else:
            tr *= 0.5
            if tr < 1e-16:
                break
            P = bestP.copy()
    return best, bestP


def main():
    rng = np.random.default_rng(SEED0)
    gbest, gP = -1, None
    try:
        cur = json.load(open(OUT))
        gP = np.array([[float(a), float(b)] for a, b in cur["points"]])
        gbest = score(gP)
    except Exception:
        pass
    for r in range(RESTARTS):
        P = np.array([rand_point(rng) for _ in range(N)])
        sc, P = slp(P)
        # perturbation restarts from the best
        if sc > gbest:
            gbest, gP = sc, P.copy()
            json.dump({"score": gbest, "points": gP.tolist()}, open(OUT, "w"))
        if gP is not None:
            Q = gP + rng.normal(0, 0.01, gP.shape)
            sc2, Q = slp(Q)
            if sc2 > gbest:
                gbest, gP = sc2, Q.copy()
                json.dump({"score": gbest, "points": gP.tolist()}, open(OUT, "w"))
        print(f"restart {r} best {gbest:.12f}", flush=True)


if __name__ == "__main__":
    main()
