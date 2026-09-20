#!/usr/bin/env python3
"""Search for the cheapest (certificate_bits) exact CHSH certificate of the form
right vectors = e1,e2, left vectors u=(a,+-b,r)/c, a,b < CMAX, such that
(a1+b1)/c1 + (a2+b2)/c2 >= 2.828426  (i.e. gap_ppm = 1414213, the floor of
sqrt(2)*1e6, the maximum attainable on a 2x2 matrix).  Dimension 2 (r=0) and 3.
Restricted family, not a proof of global bit-minimality."""
import math
from fractions import Fraction
CMAX = 3000
bl = int.bit_length
def fb(x, c):
    g = math.gcd(x, c); return bl(x // g) + bl(c // g)
for d in (2, 3):
    cands = []
    for a in range(1, CMAX):
        for b in range(a, min(CMAX, a + 60)):
            for r in range(0, 45 if d == 3 else 1):
                s = a*a + b*b + r*r; c = math.isqrt(s)
                if c*c != s or (a+b)*1000 < 1414*c: continue
                bits = fb(a, c) + fb(b, c) + (fb(r, c) if d == 3 else 0)
                cands.append((Fraction(a+b, c), bits, (a, b, r, c)))
    out = None
    for v1, b1, t1 in cands:
        for v2, b2, t2 in cands:
            if v1 + v2 >= Fraction(2828426, 1000000):
                tot = b1 + b2 + 2*(2 + (d-1))
                if out is None or tot < out[0]: out = (tot, t1, t2)
    print("dim", d, "candidates", len(cands), "best total bits", out)
