#!/usr/bin/env python3
"""Run the hill's OWN eval.py against ../ (the solution dir) using a temp copy
of hill/ with a SYNTHESISED private/seeds.json (the real one is not distributed).

Schema: {"validation": [ints], "test": [ints]} -- inferred from eval.py, which
does  seeds = json.loads(...)["test" if final else "validation"]  and then
iterates seeds, using seeds[0] + 1 as the timing RNG seed. The recovered file is
91 bytes per private.lock; we cannot recover its exact seeds, so the numbers
below are OUR OWN seeds. Correctness is seed-independent; timing is too.

Usage: verify_local.py [--final] [--n 512]
"""
import argparse, importlib.util, json, pathlib, shutil, tempfile

HERE = pathlib.Path(__file__).resolve().parent
SOL = HERE.parent
HILL = SOL.parent / "hill"
SEEDS = {"validation": [11, 22, 33], "test": [101, 202, 303]}


def run(sol: pathlib.Path, final: bool, n: int = 512):
    with tempfile.TemporaryDirectory() as td:
        h = pathlib.Path(td) / "hill"
        shutil.copytree(HILL, h)
        (h / "private").mkdir(exist_ok=True)
        (h / "private" / "seeds.json").write_text(json.dumps(SEEDS))
        spec = importlib.util.spec_from_file_location("ev", h / "eval.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m.eval(sol, final=final, n=n)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--sol", default=str(SOL))
    a = ap.parse_args()
    print(json.dumps(run(pathlib.Path(a.sol), a.final, a.n), indent=2))
