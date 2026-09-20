#!/usr/bin/env python3
"""Exact minimum rule count via DP on the dyadic residue tree.

Rules live on nodes (k, r) of the binary tree of odd residues mod 2^k; a rule
covers exactly the target nodes in its subtree (levels 8..12).  Only the
best-margin rule at each node can matter.  For a requirement req(c) on every
target class c, f(node, carried) = min #rules in the subtree, where `carried`
is the best margin among chosen ancestors.  Exact Fractions throughout.

Usage: python3 tree_dp.py            # print the table of thresholds
       python3 tree_dp.py --write T  # write solution.json for threshold index T ('best' = pointwise best)
"""
import json, pathlib, sys
from fractions import Fraction
from functools import lru_cache
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_solution import all_rules, LEVELS, KMAX

sys.setrecursionlimit(10000)
HERE = pathlib.Path(__file__).resolve().parent
ZERO = Fraction(0)
node_rule = {}
for k, r, e, m in all_rules():
    if (k, r) not in node_rule or m > node_rule[(k, r)][3]:
        node_rule[(k, r)] = (k, r, e, m)

best = {}
def fill(k, r, carried):
    if (k, r) in node_rule:
        carried = max(carried, node_rule[(k, r)][3])
    if k >= 8 and carried > 0:
        best[(k, r)] = carried
    if k < KMAX:
        fill(k + 1, r, carried); fill(k + 1, r + (1 << k), carried)
fill(1, 1, ZERO)


def solve(req):
    """req: dict class -> required margin (only coverable classes). Returns list of rules."""
    INF = 10 ** 9
    @lru_cache(maxsize=None)
    def f(k, r, carried):
        options = []
        for pick in (False, True):
            c = carried
            cost = 0
            if pick:
                if (k, r) not in node_rule or node_rule[(k, r)][3] <= carried:
                    continue
                c = node_rule[(k, r)][3]; cost = 1
            if k >= 8 and (k, r) in req and c < req[(k, r)]:
                continue
            if k < KMAX:
                a = f(k + 1, r, c); b = f(k + 1, r + (1 << k), c)
                cost += a[0] + b[0]
            options.append((cost, pick))
        return min(options) if options else (INF, False)
    out = []
    def walk(k, r, carried):
        cost, pick = f(k, r, carried)
        assert cost < INF
        if pick:
            out.append(node_rule[(k, r)]); carried = node_rule[(k, r)][3]
        if k < KMAX:
            walk(k + 1, r, carried); walk(k + 1, r + (1 << k), carried)
    walk(1, 1, ZERO)
    return out


def main():
    taus = sorted(set(best.values()))
    table = []
    for i, tau in enumerate(taus):
        rules = solve({c: min(b, tau) for c, b in best.items()})
        table.append((i, tau, len(rules)))
        print("T=%2d tau=%-12s (%.6f)  min rules=%d" % (i, tau, float(tau), len(rules)))
    if "--write" in sys.argv:
        T = int(sys.argv[sys.argv.index("--write") + 1])
        rules = solve({c: min(b, taus[T]) for c, b in best.items()})
        rules.sort(key=lambda q: (q[0], q[1]))
        doc = {"rules": [{"modulus_power": k, "residue": r, "exponents": list(e)} for k, r, e, _ in rules]}
        p = HERE.parent / "solution.json"
        p.write_text(json.dumps(doc, separators=(",", ":")) + "\n")
        print("wrote", p, len(rules), "rules")


if __name__ == "__main__":
    main()
