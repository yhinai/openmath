"""Coverage / margin analysis + rule-set optimisation for the hill.

Universe: every odd residue class (j, t) with 8 <= j <= 12 that is *coverable*
at all (i.e. some rule with k <= j has r == t mod 2^k).  The hidden target
collections are subsets of these classes, so covering all coverable classes is
the maximal-coverage strategy for any hidden split.
"""
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

SOL = Path(__file__).resolve().parent
HILL = next(p for p in (SOL.parent / "hill", SOL.parent, SOL.parent.parent) if (p / "eval.py").is_file())
spec = importlib.util.spec_from_file_location("hill_eval", HILL / "eval.py")
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)

LEVELS = range(8, 13)
cand = json.loads((SOL / "candidates.json").read_text())
# pool: (k, r) -> (margin Fraction, exps)
pool = {}
for c in cand:
    m = Fraction(c["margin"][0], c["margin"][1])
    key = (c["k"], c["r"])
    if key not in pool or m > pool[key][0]:
        pool[key] = (m, tuple(c["exps"]))

# ---------------------------------------------------------------- coverage
def rule_covers(k, r, j, t):
    return j >= k and t % (1 << k) == r

# for each level, which targets are coverable and by which rules
cover_by = {}        # (j,t) -> list of (k,r)   (k <= j)
for j in LEVELS:
    for t in range(1, 1 << j, 2):
        ms = [(k, r) for (k, r) in pool if k <= j and t % (1 << k) == r]
        cover_by[(j, t)] = ms

universe = [key for key, ms in cover_by.items() if ms]
uncoverable = [key for key, ms in cover_by.items() if not ms]
print(f"targets (j,t) for j=8..12: {sum(1 << (j-1) for j in LEVELS)}")
print(f"coverable: {len(universe)}   uncoverable: {len(uncoverable)}")
for j in LEVELS:
    tot = 1 << (j - 1)
    cov = sum(1 for (jj, t) in cover_by if jj == j and cover_by[(jj, t)])
    print(f"  level {j}: {cov}/{tot} coverable")
print("uncoverable samples:", uncoverable[:12])

# what rules are needed at minimum?  every coverable (j,t) must use k<=j
# best margin available for each target with the FULL pool
best_full = {key: max(pool[(k, r)][0] for (k, r) in ms) for key, ms in cover_by.items() if ms}
print("min over targets of best-margin (full pool):", float(min(best_full.values())), min(best_full.values()))
worst = min(best_full, key=lambda k: best_full[k])
print("  worst target:", worst, best_full[worst])

# ---------------------------------------------------------- greedy set cover
# weight each target equally (our self-generated split); rule pool = all (k,r)
rem = set(universe)
chosen = []
# candidate rule coverage count at any time
def gain(k, r, rem):
    return sum(1 for (j, t) in rem if j >= k and t % (1 << k) == r)

while rem:
    best = None
    for (k, r) in pool:
        if k > 12:
            continue
        g = gain(k, r, rem)
        if g and (best is None or g > best[0]):
            best = (g, k, r)
    if not best:
        print("STUCK with", len(rem), "left")
        break
    g, k, r = best
    chosen.append((k, r))
    rem -= {(j, t) for (j, t) in rem if j >= k and t % (1 << k) == r}
print(f"greedy cover: {len(chosen)} rules, remaining {len(rem)}")

# margin quality of the greedy set
sel = set(chosen)
def margins_of(sel):
    out = {}
    for (j, t) in universe:
        ms = [pool[(k, r)][0] for (k, r) in cover_by[(j, t)] if (k, r) in sel]
        out[(j, t)] = max(ms) if ms else Fraction(0)
    return out

mg = margins_of(sel)
print("greedy min-margin:", float(min(mg.values())))
print("greedy k histogram:", {k: sum(1 for kk, _ in chosen if kk == k) for k in range(4, 13)})
json.dump(sorted(chosen), open(SOL / "_greedy.json", "w"))
