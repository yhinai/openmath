"""Exploratory numeric search for a sign matrix with a large vector/sign ratio."""
import numpy as np
import math
import itertools
import json

def sign_opt(A):
    A = np.asarray(A, dtype=float)
    m, n = A.shape
    masks = np.arange(1 << m)
    X = np.empty((1 << m, m))
    for i in range(m):
        X[:, i] = np.where((masks >> i) & 1, 1.0, -1.0)
    Z = X @ A
    return int(round(np.abs(Z).sum(axis=1).max()))


def optimize(A, d=8, restarts=24, iters=250, rng=None):
    A = np.asarray(A, dtype=float)
    m, n = A.shape
    if rng is None:
        rng = np.random.default_rng()
    best = -1.0
    bU = bV = None
    for r in range(restarts):
        V = rng.standard_normal((n, d))
        V /= np.linalg.norm(V, axis=1, keepdims=True)
        U = rng.standard_normal((m, d))
        U /= np.linalg.norm(U, axis=1, keepdims=True)
        for it in range(iters):
            W = A @ V
            nw = np.linalg.norm(W, axis=1, keepdims=True)
            nw[nw < 1e-13] = 1.0
            U = W / nw
            W2 = A.T @ U
            nw2 = np.linalg.norm(W2, axis=1, keepdims=True)
            nw2[nw2 < 1e-13] = 1.0
            V = W2 / nw2
        obj = float(np.sum(A * (U @ V.T)))
        if obj > best:
            best = obj
            bU = U.copy()
            bV = V.copy()
    return best, bU, bV


def matrix_from_circle(alpha, beta):
    m, n = len(alpha), len(beta)
    A = np.zeros((m, n))
    for i, a in enumerate(alpha):
        for j, b in enumerate(beta):
            A[i, j] = 1.0 if math.cos(a - b) >= 0 else -1.0
    return A


def report(A, rng):
    s = sign_opt(A)
    obj, U, V = optimize(A, restarts=40, iters=400, rng=rng)
    return s, obj, obj / s, U, V


if __name__ == "__main__":
    rng = np.random.default_rng(12345)
    # sanity: CHSH
    A = np.array([[1.0, 1.0], [1.0, -1.0]])
    print("CHSH sign", sign_opt(A), "ratio", report(A, rng)[2])

    results = []
    for (m, n) in [(2, 2), (3, 3), (3, 4), (4, 4), (4, 5), (5, 5), (6, 6), (7, 7), (8, 8)]:
        best = (0, None)
        trials = {2: 5, 3: 60, 4: 60, 5: 60, 6: 40, 7: 30, 8: 30}[m]
        for t in range(trials):
            M = rng.integers(0, 2, size=(m, n)) * 2 - 1
            s, obj, r, U, V = report(M, rng)
            if r > best[0]:
                best = (r, M.copy())
        print(f"{m}x{n} best ratio {best[0]:.6f} sign={sign_opt(best[1])} matrix={best[1].astype(int).tolist()}")
        results.append((m, n, best[0], best[1].astype(int).tolist()))

    # circle family
    print("--- circle family ---")
    for (m, n) in [(3, 3), (4, 4), (5, 5), (6, 6), (8, 8)]:
        best = (0, None)
        for t in range(400):
            alpha = rng.uniform(0, 2 * math.pi, m)
            beta = rng.uniform(0, 2 * math.pi, n)
            M = matrix_from_circle(alpha, beta)
            s, obj, r, U, V = report(M, rng)
            if r > best[0]:
                best = (r, M.copy())
        print(f"circle {m}x{n} best ratio {best[0]:.6f} matrix={best[1].astype(int).tolist()}")
