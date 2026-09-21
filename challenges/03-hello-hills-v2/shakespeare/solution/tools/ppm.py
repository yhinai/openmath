import math

def build(text, K):
    cnt = {}
    g = cnt.get
    for i in range(len(text)):
        c = text[i]
        lo = i - K
        if lo < 0: lo = 0
        for j in range(lo, i + 1):
            k = text[j:i]
            d = g(k)
            if d is None: cnt[k] = d = {}
            d[c] = d.get(c, 0) + 1
    return cnt

def make_predict(cnt, alphabet, K, esc=1.0, alpha=0.0, floor=1e-9):
    V = len(alphabet)
    A = tuple(alphabet)
    get = cnt.get
    def predict(prefix):
        excl = set()
        rem = 1.0
        out = {}
        lp = len(prefix)
        kk = K if K <= lp else lp
        for k in range(kk, -1, -1):
            d = get(prefix[lp - k:] if k else "")
            if not d: continue
            if excl:
                items = [(c, v) for c, v in d.items() if c not in excl]
            else:
                items = list(d.items())
            if not items: continue
            n = 0
            for _, v in items: n += v
            t = len(items)
            e = esc * t
            denom = n + e - alpha * t
            if denom <= 0: continue
            r = rem
            for c, v in items:
                out[c] = out.get(c, 0.0) + r * (v - alpha) / denom
            rem = r * e / denom
            excl.update(c for c, _ in items)
            if rem < 1e-12: break
        left = [c for c in A if c not in excl]
        if left:
            u = rem / len(left)
            for c in left: out[c] = out.get(c, 0.0) + u
        s = sum(out.values())
        if s > 1.0: 
            inv = 1.0 / s
            out = {c: p * inv for c, p in out.items()}
        return {c: math.log(p) for c, p in out.items() if p > 0.0}
    return predict

def bpc(predict, text):
    tot = 0.0
    FL = math.log(1e-8)
    for i in range(len(text)):
        d = predict(text[:i])
        p = math.exp(d.get(text[i], -800)) if text[i] in d else 0.0
        tot += max(math.log(p) if p > 0 else FL, FL)
    return -tot / (len(text) * math.log(2))
