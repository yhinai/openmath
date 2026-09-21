"""Character-level model for the `shakespeare` hill.

Contract (hill/eval.py): expose `predict_next(prefix) -> {char: natural-log-prob}`
with sum_c P(c | prefix) <= 1.  The evaluator passes only text[:i], one char at
a time, and scores bits/char from the probability given to the true next char.

Model
-----
A linear mixture of six variable-order PPM models.  Each component is a
back-off cascade over context orders K, K-1, ..., 0 using PPM-C style escape
probabilities with full exclusion:

    denom = n + ESC * t        (n = total count of non-excluded chars in the
    P(c)  += rem * count(c)/denom    context, t = number of distinct such chars)
    rem   *= ESC * t / denom

and a final uniform spread of the leftover mass over the characters no order
proposed.  Components use K = 2, 3, 4, 5, 6, 8; their outputs are averaged with
weights fitted by EM on a validation slice held out from train.txt.  The
mixture is strictly better than any single order (see README.md).

All counts come from `train.txt`, a verbatim copy of the hill's own training
text shipped next to this file.  No held-out text is used anywhere.
"""

import math
from pathlib import Path

# ---- hyper-parameters, tuned on a split held out from train.txt only --------
ORDERS = (2, 3, 4, 5, 6, 8)
WEIGHTS = (0.0088, 0.0667, 0.4236, 0.2381, 0.1805, 0.0823)
ESC = 0.8
# -----------------------------------------------------------------------------

_KMAX = max(ORDERS)
_W = [w / sum(WEIGHTS) for w in WEIGHTS]

_TEXT = Path(__file__).with_name("train.txt").read_text()
_ALPHABET = tuple(sorted(set(_TEXT)))


def _build(text, k_max):
    cnt = {}
    g = cnt.get
    for i in range(len(text)):
        c = text[i]
        lo = i - k_max
        if lo < 0:
            lo = 0
        for j in range(lo, i + 1):
            key = text[j:i]
            d = g(key)
            if d is None:
                cnt[key] = d = {}
            d[c] = d.get(c, 0) + 1
    return cnt


_CNT = _build(_TEXT, _KMAX)
_get = _CNT.get


def _component(prefix, lp, K):
    """PPM-C back-off distribution (as a plain dict char -> prob) for order K."""
    excl = set()
    rem = 1.0
    out = {}
    kk = K if K <= lp else lp
    for k in range(kk, -1, -1):
        d = _get(prefix[lp - k:] if k else "")
        if not d:
            continue
        items = [(c, v) for c, v in d.items() if c not in excl] if excl else list(d.items())
        if not items:
            continue
        n = 0
        for _, v in items:
            n += v
        e = ESC * len(items)
        denom = n + e
        r = rem
        for c, v in items:
            out[c] = out.get(c, 0.0) + r * v / denom
        rem = r * e / denom
        excl.update(c for c, _ in items)
        if rem < 1e-12:
            break
    left = [c for c in _ALPHABET if c not in excl]
    if left:
        u = rem / len(left)
        for c in left:
            out[c] = out.get(c, 0.0) + u
    return out


def predict_next(prefix):
    lp = len(prefix)
    mix = {}
    for K, w in zip(ORDERS, _W):
        for c, p in _component(prefix, lp, K).items():
            mix[c] = mix.get(c, 0.0) + w * p
    s = 0.0
    for p in mix.values():
        s += p
    if s > 1.0:                      # guard: the evaluator requires sum <= 1
        inv = 1.0 / s
        mix = {c: p * inv for c, p in mix.items()}
    return {c: math.log(p) for c, p in mix.items() if p > 0.0}
