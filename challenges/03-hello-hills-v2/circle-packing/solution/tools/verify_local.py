#!/usr/bin/env python3
"""Score a submission dir with the hill's OWN eval.py (from a temp copy of hill/)."""
import importlib.util, json, pathlib, shutil, sys, tempfile

HILL = pathlib.Path(__file__).resolve().parents[2] / "hill"

def load_eval():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="hillcopy_"))
    dst = tmp / "hill"
    shutil.copytree(HILL, dst)
    spec = importlib.util.spec_from_file_location("ev", dst / "eval.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    sub = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                       pathlib.Path(__file__).resolve().parents[1])
    ev = load_eval()
    for final in (False, True):
        res = ev.eval(sub, final=final)
        print(f"--- final={final} ---")
        print(json.dumps(res, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
