"""Scan every downloaded HKS .tab and report the sparsest by nonzero count.

`support` is invariant under the slot permutation / transposition needed to put a
scheme into the hill's index convention (relabelling positions cannot change how
many are nonzero), so it is read straight off the file.  Only the winner is then
put through the full Brent verification.
"""
import glob, re, sys, collections

def raw_nnz(path):
    n = 0; rows = 0
    for line in open(path):
        line = line.strip()
        if not line or set(line) <= set("-+"): continue
        parts = line.split("|")
        if len(parts) != 3: continue
        rows += 1
        for p in parts:
            for x in p.split():
                if int(x) != 0: n += 1
    return n, rows

best = []
bad = 0
for p in glob.glob("lit/tabs/*.tab"):
    name = p.split("/")[-1][:-4]
    try:
        n, rows = raw_nnz(p)
    except Exception:
        bad += 1; continue
    if rows != 69:          # 23 terms x 3 rows
        bad += 1; continue
    best.append((n, name))
best.sort()
print("scanned:", len(best), "malformed/skipped:", bad)
print("sparsest 10:")
for n, name in best[:10]: print("   support %d  %s" % (n, name))
c = collections.Counter(n for n, _ in best)
print("support histogram (lowest 6):", sorted(c.items())[:6])
