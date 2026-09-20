#!/usr/bin/env python3
"""Run the hill's OWN eval.py (from a temp COPY of hill/) against solution.json.

hill/private/{validation,test}.json are not distributed (205 / 229 bytes, a
witness plus expected values; not brute-forceable).  eval.py uses them only as
an arithmetic self-test of _sign_optimum/_vector_objective, independent of the
submission.  We synthesise a fixture of the same schema (the public baseline
witness with its correct expected values) inside the temp copy only.

Usage: python3 verify_local.py [solution_dir]
"""
import importlib.util, json, pathlib, shutil, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
HILL = HERE.parent.parent / "hill"
SOL = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent


def main():
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        shutil.copytree(HILL, td / "hill")
        fx = json.loads((HILL / "examples" / "baseline" / "solution.json").read_text())
        fx["expected"] = {"sign_optimum": 2, "objective": [14, 5]}
        (td / "hill" / "private").mkdir(exist_ok=True)
        for f in ("validation.json", "test.json"):
            (td / "hill" / "private" / f).write_text(json.dumps(fx))
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
