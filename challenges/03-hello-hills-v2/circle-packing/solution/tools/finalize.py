#!/usr/bin/env python3
"""Turn a float solution into an EXACT-rational submission.

eval.py parses every number with `parse_float=Fraction`, so a decimal literal in
the JSON is an exact rational. This script:
  1. snaps centres x,y to exact decimals (DIGITS places),
  2. recomputes radii by LP against those exact centres,
  3. repairs any residual violation in exact Fraction arithmetic,
  4. floors every radius DOWN to DIGITS decimal places and subtracts EPS,
  5. re-checks every constraint with exact Fractions, strictly (tolerance 0).
So the submission is feasible even at tolerance=0, not merely within 1e-9.
"""
import json, sys
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog

N = 26
DIGITS = 25
SCALE = 10**DIGITS
EPS = Fraction(1, 10**20)

def floor_frac(f, scale=SCALE):
    return Fraction((f * scale).__floor__(), scale)

def round_frac(f, scale=SCALE):
    return Fraction(round(f * scale), scale)

def lp_radii(x, y):
    iu, ju = np.triu_indices(N, 1)
    A, b = [], []
    for i in range(N):
        for v in (x[i], 1-x[i], y[i], 1-y[i]):
            row = np.zeros(N); row[i] = 1.0
            A.append(row); b.append(max(v, 0.0))
    for i, j in zip(iu, ju):
        row = np.zeros(N); row[i] = 1.0; row[j] = 1.0
        A.append(row); b.append(float(np.hypot(x[i]-x[j], y[i]-y[j])))
    res = linprog(-np.ones(N), A_ub=np.array(A), b_ub=np.array(b),
                  bounds=[(0, 0.5)]*N, method="highs")
    return res.x

def exact_repair(X, Y, R):
    """Shrink radii until every constraint holds STRICTLY in exact arithmetic."""
    for i in range(N):
        cap = min(X[i], 1 - X[i], Y[i], 1 - Y[i]) - EPS
        if R[i] > cap:
            R[i] = cap
    for _ in range(500):
        bad = False
        for i in range(N):
            for j in range(i+1, N):
                d2 = (X[i]-X[j])**2 + (Y[i]-Y[j])**2
                s = R[i] + R[j]
                if s*s >= d2:
                    bad = True
                    # shrink the larger radius until s^2 < d2 with margin
                    k = i if R[i] >= R[j] else j
                    o = j if k == i else i
                    # need R[k] < sqrt(d2) - R[o]; use a rational lower bound on sqrt
                    lo = Fraction(0); hi = max(s, Fraction(2))
                    for _ in range(80):  # bisect a rational sqrt lower bound
                        mid = (lo + hi) / 2
                        if mid*mid <= d2: lo = mid
                        else: hi = mid
                    R[k] = max(lo - R[o] - EPS, Fraction(0))
        if not bad:
            break
    return R

def check(X, Y, R):
    probs = []
    for i in range(N):
        if R[i] <= 0: probs.append(f"r[{i}]<=0")
        if X[i] - R[i] < 0 or X[i] + R[i] > 1: probs.append(f"x[{i}] wall")
        if Y[i] - R[i] < 0 or Y[i] + R[i] > 1: probs.append(f"y[{i}] wall")
    for i in range(N):
        for j in range(i+1, N):
            if (X[i]-X[j])**2 + (Y[i]-Y[j])**2 - (R[i]+R[j])**2 < 0:
                probs.append(f"overlap {i},{j}")
    return probs

def dec(f, digits=DIGITS):
    neg = f < 0
    f = abs(f)
    whole = f.numerator // f.denominator
    frac = f - whole
    s = str((frac * 10**digits).__floor__()).rjust(digits, "0")
    return ("-" if neg else "") + f"{whole}.{s}"

def main():
    src, dst = sys.argv[1], sys.argv[2]
    d = json.load(open(src))
    x = np.array([c["x"] for c in d["circles"]])
    y = np.array([c["y"] for c in d["circles"]])
    X = [round_frac(Fraction(v)) for v in x]
    Y = [round_frac(Fraction(v)) for v in y]
    xf = np.array([float(v) for v in X]); yf = np.array([float(v) for v in Y])
    r = lp_radii(xf, yf)
    R = [floor_frac(Fraction(v)) for v in r]
    R = exact_repair(X, Y, R)
    R = [floor_frac(v) for v in R]
    R = exact_repair(X, Y, R)
    probs = check(X, Y, R)
    if probs:
        print("EXACT CHECK FAILED:", probs[:5]); sys.exit(1)
    total = sum(R, Fraction(0))
    body = ",\n".join(
        f'    {{"x": {dec(X[i])}, "y": {dec(Y[i])}, "r": {dec(R[i])}}}'
        for i in range(N))
    open(dst, "w").write('{\n  "circles": [\n' + body + "\n  ]\n}\n")
    print(f"exact-feasible at tolerance 0; sum_radii = {float(total)!r}")

if __name__ == "__main__":
    main()
