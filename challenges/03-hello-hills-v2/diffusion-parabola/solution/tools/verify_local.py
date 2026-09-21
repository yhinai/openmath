"""Run the hill's own eval.py against this submission, from a temp copy of hill/.

The hill ships no private/seeds.json (it is held out by AutoLab), so we
synthesise one matching the schema eval.py reads:
    {"validation": <int>, "test": <int>}
The absolute score below therefore comes from OUR seeds, not AutoLab's.
Because the generator is fixed and both splits are 2000 i.i.d. draws from the
same law, the real hidden score differs only by sampling noise (~3e-4 std,
measured over 40 seeds).

Usage:
  python3 tools/verify_local.py [--steps 10000] [--n-samples 2000]
                                [--val-seed 1234567] [--test-seed 7654321]
"""
import argparse, importlib.util, json, shutil, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOLUTION = HERE.parent
HILL = SOLUTION.parent / "hill"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=10000)
    ap.add_argument("--n-samples", type=int, default=2000)
    ap.add_argument("--val-seed", type=int, default=1234567)
    ap.add_argument("--test-seed", type=int, default=7654321)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        hc = Path(td) / "hill"
        shutil.copytree(HILL, hc)
        (hc / "private").mkdir(exist_ok=True)
        (hc / "private" / "seeds.json").write_text(
            json.dumps({"validation": args.val_seed, "test": args.test_seed}))
        spec = importlib.util.spec_from_file_location("ev", hc / "eval.py")
        ev = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ev)
        for final in (False, True):
            r = ev.eval(SOLUTION, final=final, steps=args.steps,
                        n_samples=args.n_samples)
            print(f"final={final}: {r}")


if __name__ == "__main__":
    main()
