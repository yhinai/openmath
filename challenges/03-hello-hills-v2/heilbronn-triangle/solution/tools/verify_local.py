"""Score a submission directory with the hill's OWN eval.py (imported from a copy)."""
import importlib.util, pathlib, shutil, sys, tempfile, json

HILL = pathlib.Path(__file__).resolve().parents[2] / "hill"
SUB = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1]

tmp = pathlib.Path(tempfile.mkdtemp())
shutil.copytree(HILL, tmp / "hill")
spec = importlib.util.spec_from_file_location("ev", tmp / "hill" / "eval.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for final in (False, True):
    print(f"--- final={final} ---")
    print(json.dumps(m.eval(SUB, final=final), indent=2, sort_keys=True))
