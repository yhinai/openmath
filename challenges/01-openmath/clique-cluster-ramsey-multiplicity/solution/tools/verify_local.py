#!/usr/bin/env python3
"""Run the hill's OWN, unmodified eval.py against solution/solution.json.

eval.py reads hill/private/{validation,test}.json, which are not distributed.
private.lock locks 310/337-byte fixture suites (not a one-integer budget), so
they cannot be brute-forced.  In eval.py those suites are used ONLY by _audit():
each fixture is a small template on which the evaluator cross-checks its own
fast counter (_density) against its literal oracle (_oracle); the suite's "id"
is echoed as details.audit_suite.  They never touch the submission's score.
We therefore synthesise fixtures of the same schema and place them ONLY in a
temporary copy of hill/.  Consequence: details.audit_suite below is OUR id, not
the organiser's; every other field is computed by the real evaluator.

Usage: python3 verify_local.py [solution_dir]
"""
import importlib.util, json, pathlib, shutil, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
HILL = HERE.parent.parent / "hill"
SOL = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent
S = "weighted-two-color-blowup-v1"


def suite(name, fx):
    return {"id": name, "fixtures": [{"schema": S, "weights": w, "red_rows": r} for w, r in fx]}


VAL = suite("synthetic-local-validation", [
    ([1, 1], ["01", "10"]),
    ([2, 3, 5], ["110", "100", "001"]),
    ([1, 2, 4, 1], ["1110", "1010", "1101", "0011"]),
])
TEST = suite("synthetic-local-test", [
    ([1, 1], ["00", "00"]),
    ([3, 1, 2], ["010", "101", "010"]),
    ([6, 6, 1, 1, 9], ["11010", "11011", "00101", "11001", "01110"]),
])


def main():
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        shutil.copytree(HILL, td / "hill")
        (td / "hill" / "private").mkdir(exist_ok=True)
        (td / "hill" / "private" / "validation.json").write_text(json.dumps(VAL))
        (td / "hill" / "private" / "test.json").write_text(json.dumps(TEST))
        spec = importlib.util.spec_from_file_location("ev", td / "hill" / "eval.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rc = 0
        for label, final in (("validation", False), ("final", True)):
            r = mod.eval(SOL, final=final)
            print("[%s] %s" % (label, json.dumps(r, sort_keys=True)))
            if r.get("passed") is not True:
                rc = 1
        return rc


if __name__ == "__main__":
    sys.exit(main())
