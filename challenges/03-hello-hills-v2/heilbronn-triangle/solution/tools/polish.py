"""High-precision polish of a locally optimal Heilbronn configuration.

At a maximin optimum the active set (tied minimal triples + points pinned to
the container's edges) gives a square nonlinear system in the 2n coordinates
and the common tied area t.  Newton (mpmath.findroot) solves it to hundreds
of digits.  Usage: polish.py <points.json in> <points.json out> [dps] [ndigits]
"""
import sys, json, itertools
from mpmath import mp, mpf, sqrt, matrix, findroot, nstr

IN, OUT = sys.argv[1], sys.argv[2]
DPS = int(sys.argv[3]) if len(sys.argv) > 3 else 140
NDIG = int(sys.argv[4]) if len(sys.argv) > 4 else 120
mp.dps = DPS
S3 = sqrt(3); AREA = S3 / 2
N = 11
P0 = [[mpf(str(a)), mpf(str(b))] for a, b in json.load(open(IN))]
TR = list(itertools.combinations(range(N), 3))

def det(P, t):
    (ax, ay), (bx, by), (cx, cy) = P[t[0]], P[t[1]], P[t[2]]
    return (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)

d = sorted(((abs(det(P0, t)), t) for t in TR))
tmin = d[0][0]
TIED = [t for v, t in d if v - tmin < tmin * mpf("1e-10")]
SGN = [1 if det(P0, t) > 0 else -1 for t in TIED]
# boundary: 0 = bottom (y=0), 1 = left (y=S3 x), 2 = right (y=S3(1-x))
EDGE = []
tol = mpf("1e-9")
for i, (x, y) in enumerate(P0):
    if y < tol: EDGE.append((i, 0))
    elif S3 * x - y < tol: EDGE.append((i, 1))
    elif S3 * (1 - x) - y < tol: EDGE.append((i, 2))
print("tied triples:", len(TIED), "edge constraints:", len(EDGE),
      "unknowns:", 2 * N + 1, file=sys.stderr)

def unpack(v):
    return [[v[2 * i], v[2 * i + 1]] for i in range(N)], v[2 * N]

def F(*v):
    P, t = unpack(list(v))
    r = [SGN[k] * det(P, TIED[k]) - t for k in range(len(TIED))]
    for i, e in EDGE:
        x, y = P[i]
        r.append(y if e == 0 else (y - S3 * x if e == 1 else y - S3 * (1 - x)))
    return r

x0 = [c for pt in P0 for c in pt] + [tmin]
need = 2 * N + 1
if len(F(*x0)) != need:
    print("system is not square (%d eqs, %d unknowns) - aborting" % (len(F(*x0)), need), file=sys.stderr)
    sys.exit(1)
sol = findroot(F, x0, tol=mpf(10) ** (-(DPS - 10)))
P, t = unpack([sol[i] for i in range(need)])
val = t / AREA
print("polished min_area =", nstr(val, 40), file=sys.stderr)

def fmt(z):
    s = nstr(z, NDIG, strip_zeros=False)
    if "e" in s or "E" in s:
        s = mp.nstr(z, NDIG)
    return s

out = []
for x, y in P:
    out.append([mp.nstr(x, NDIG, strip_zeros=False), mp.nstr(y, NDIG, strip_zeros=False)])
json.dump(out, open(OUT, "w"), indent=1)
