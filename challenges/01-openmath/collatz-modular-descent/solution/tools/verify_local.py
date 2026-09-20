#!/usr/bin/env python3
"""Run the hill's OWN eval.py (from a temp COPY of hill/) against solution.json.

hill/private/{validation,test}.json are held-out target lists (941 / 1142 bytes
of {"modulus_power","residue","weight"} records) and cannot be recovered from
private.lock.  We synthesise fixtures matching the schema eval.py parses: random
odd residue classes mod 2^8..2^12 with random weights 1..1000.  THE REAL HIDDEN
SCORE WILL DIFFER, because coverage_ppm depends on which classes are hidden.

Besides the fixture scores, this script checks the fixture-independent claim:
for EVERY one of the 3968 possible target classes, the submission covers it iff
any valid rule could, and (up to the cap 55/64) with the best possible margin.

Usage: python3 verify_local.py [solution_dir]
"""
import importlib.util, json, pathlib, random, shutil, sys, tempfile
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
HILL = HERE.parent.parent / "hill"
SOL = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent
sys.path.insert(0, str(HERE))


def fixture(seed, n):
    rng = random.Random(seed)
    seen, out = set(), []
    while len(out) < n:
        k = rng.randint(8, 12); r = rng.randrange(1, 1 << k, 2)
        if (k, r) in seen:
            continue
        seen.add((k, r))
        out.append({"modulus_power": k, "residue": r, "weight": rng.randint(1, 1000)})
    return {"targets": out}


def main():
    rc = 0
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        shutil.copytree(HILL, td / "hill")
        (td / "hill" / "private").mkdir(exist_ok=True)
        (td / "hill" / "private" / "validation.json").write_text(json.dumps(fixture(1, 18)))
        (td / "hill" / "private" / "test.json").write_text(json.dumps(fixture(2, 22)))
        spec = importlib.util.spec_from_file_location("ev", td / "hill" / "eval.py")
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        for label, final in (("validation", False), ("final", True)):
            r = mod.eval(SOL, final=final)
            print("[%s] %s" % (label, json.dumps(r, sort_keys=True)))
            if r.get("passed") is not True:
                rc = 1
        # fixture-independent check, using eval.py's own verifier and _covers
        from build_solution import all_rules
        verified = [mod._verify_rule(q) for q in mod._load_rules(SOL)]
        allv = [mod._verify_rule((k, r, e)) for k, r, e, _ in all_rules()]
        CAP = Fraction(55, 64)
        bad_cov = bad_margin = coverable = 0
        for K in range(8, 13):
            for t in range(1, 1 << K, 2):
                tgt = (K, t, 1)
                opt = [q["margin"] for q in allv if mod._covers(q, tgt)]
                got = [q["margin"] for q in verified if mod._covers(q, tgt)]
                coverable += bool(opt)
                if bool(opt) != bool(got):
                    bad_cov += 1
                elif opt and max(got) < min(max(opt), CAP):
                    bad_margin += 1
        print("[universe] classes=3968 coverable=%d coverage_mismatches=%d margin_below_min(best,55/64)=%d"
              % (coverable, bad_cov, bad_margin))
        if bad_cov or bad_margin:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
