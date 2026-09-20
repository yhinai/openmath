"""Enumerate all valid accelerated-Collatz descent certificates with k <= 12.

A rule is (k, r, exponents).  Validity is decided by the hill's own
evaluator (eval._verify_rule), so every emitted rule is provably accepted.

Key structural facts (all confirmed against the literature, see README.md):
  * a valuation word (e1..es) cuts out exactly ONE odd residue class mod
    2^(E+1), E = e1+...+es  (2-adic cylinder lemma), so k >= E+1 is exactly
    the condition that the word is stable on the class;
  * the affine iterate is C^s(n) = (3^s n + c)/2^E, hence it is contractive
    iff 3^s < 2^E (log-multiplier condition), and the descent margin is
    (2^E - 3^s)/2^E;
  * for a target class (j,t) with 8 <= j <= 12 to be covered, we need a rule
    with k <= j and r == t mod 2^k -- so only rules with k <= 12 can ever
    cover a target.
"""
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

SOL = Path(__file__).resolve().parent
HILL = next(
    p for p in (SOL.parent / "hill", SOL.parent, SOL.parent.parent)
    if (p / "eval.py").is_file()
)

spec = importlib.util.spec_from_file_location("hill_eval", HILL / "eval.py")
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)


def candidate_prefixes(k, r):
    """All exponent prefixes obtainable from the exact simulation of class r mod 2^k."""
    current = r
    exps = []
    total = 0
    out = []
    while len(exps) < ev.MAX_STEPS:
        numerator = 3 * current + 1
        e = ev._v2(numerator)
        if e > ev.MAX_EXPONENT:
            break
        exps.append(e)
        total += e
        current = numerator >> e
        if total > k - 1:          # k >= 1 + sum(e) can never hold again
            break
        out.append(tuple(exps))
    return out


def valid_rules(kmax=12):
    rules = []          # (k, r, exps, margin: Fraction)
    for k in range(2, kmax + 1):
        for r in range(1, 1 << k, 2):
            for exps in candidate_prefixes(k, r):
                try:
                    info = ev._verify_rule((k, r, exps))
                except ValueError:
                    continue
                rules.append((k, r, exps, info["margin"]))
    return rules


if __name__ == "__main__":
    rules = valid_rules()
    print(f"total valid rules (k<=12): {len(rules)}")
    best = {}   # (k, r) -> best-margin variant
    for k, r, exps, margin in rules:
        key = (k, r)
        if key not in best or margin > best[key][2]:
            best[key] = (exps, len(exps), margin)
    print(f"distinct (k, r) with at least one valid word: {len(best)}")
    for k in range(2, 13):
        ks = [v for (kk, _), v in best.items() if kk == k]
        if ks:
            print(f"  k={k}: {len(ks)} valid residues of {1 << (k - 1)} odd, "
                  f"best margin {max(v[2] for v in ks)} worst {min(v[2] for v in ks)}")
    payload = [
        {"k": k, "r": r, "exps": list(exps), "s": len(exps), "margin": [margin.numerator, margin.denominator]}
        for (k, r), (exps, n, margin) in sorted(best.items())
    ]
    (SOL / "candidates.json").write_text(json.dumps(payload))
    print("wrote candidates.json", len(payload))
