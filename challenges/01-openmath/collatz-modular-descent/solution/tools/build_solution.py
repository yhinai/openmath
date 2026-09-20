#!/usr/bin/env python3
"""Exhaustively enumerate every rule eval.py can accept that can cover a hidden
target (modulus_power <= 12), then build a pointwise-optimal rule set.

Exact integers / Fractions only.
Usage: python3 build_solution.py [--write]
"""
import json, pathlib, sys
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
KMAX = 12          # targets have 8 <= modulus_power <= 12; a rule with k > 12 covers nothing
LEVELS = range(8, 13)


def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2; c += 1
    return c


def all_rules():
    """Every valid (k, r, exps) with k <= 12, mirroring eval._verify_rule."""
    out = []
    for k in range(2, KMAX + 1):
        for r in range(1, 1 << k, 2):
            cur, exps, s = r, [], 0
            while len(exps) < 24:
                num = 3 * cur + 1
                e = v2(num)
                if s + e + 1 > k or e > 32:
                    break
                s += e; exps.append(e); cur = num >> e
                if 3 ** len(exps) < (1 << s) and cur < r:
                    out.append((k, r, tuple(exps), Fraction((1 << s) - 3 ** len(exps), 1 << s)))
    return out


def main():
    rules = all_rules()
    # best margin available to every possible target class (K, t)
    best = {}
    for K in LEVELS:
        for t in range(1, 1 << K, 2):
            for rule in rules:
                k, r, _, m = rule
                if k <= K and t % (1 << k) == r and ((K, t) not in best or m > best[(K, t)][3]):
                    best[(K, t)] = rule
    total = sum(1 << (K - 1) for K in LEVELS)
    print("valid rules with k<=12:", len(rules))
    print("coverable target classes: %d of %d" % (len(best), total))
    for K in LEVELS:
        n = sum(1 for (j, _) in best if j == K)
        print("  level 2^%d: %d of %d odd residues coverable" % (K, n, 1 << (K - 1)))
    # Greedy minimal set that gives EVERY coverable class its best margin.
    need = dict((c, best[c][3]) for c in best)
    def gives(rule):
        k, r, _, m = rule
        return {(K, t) for K in LEVELS if K >= k for t in range(r, 1 << K, 1 << k)
                if need.get((K, t)) == m}
    cover = {rule: gives(rule) for rule in rules}
    chosen, left = [], set(need)
    while left:
        rule = max(rules, key=lambda q: (len(cover[q] & left), -q[0], -q[1]))
        chosen.append(rule); left -= cover[rule]
    chosen.sort(key=lambda q: (q[0], q[1], q[2]))
    print("rules chosen:", len(chosen))
    print("min best-margin over coverable classes:", min(need.values()))
    if "--write" in sys.argv:
        doc = {"rules": [{"modulus_power": k, "residue": r, "exponents": list(e)} for k, r, e, _ in chosen]}
        p = HERE.parent / "solution.json"
        p.write_text(json.dumps(doc, separators=(",", ":")) + "\n")
        print("wrote", p, p.stat().st_size, "bytes")
    unc = [(K, t) for K in LEVELS for t in range(1, 1 << K, 2) if (K, t) not in best]
    (HERE / "uncoverable.json").write_text(json.dumps(unc))


if __name__ == "__main__":
    main()
