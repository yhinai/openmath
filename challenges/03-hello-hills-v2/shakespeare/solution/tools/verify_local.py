#!/usr/bin/env python3
"""Score solution/ with the hill's OWN eval.py.

The hill's real held-out text (`hill/private/val.txt`, 111540 bytes) is NOT
distributed, so this script builds a *synthetic* stand-in: it splits the hill's
train.txt into a 892314-char training part and a 111540-char pseudo-held-out
part, stages a copy of the submission whose train.txt is the truncated training
part, and runs the hill's unmodified eval.py against that.

The numbers it prints are therefore NOT the hill's real score -- they are
against a self-made split. Nothing under hill/ is modified.

Usage:  python3 tools/verify_local.py [--final] [--chars N] [--workdir DIR]
"""
import argparse, importlib.util, json, shutil, sys, tempfile
from pathlib import Path

SOL = Path(__file__).resolve().parents[1]
HILL = SOL.parent / "hill"
VAL_LEN = 111540


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--chars", type=int, default=8000)
    ap.add_argument("--workdir")
    a = ap.parse_args()
    work = Path(a.workdir) if a.workdir else Path(tempfile.mkdtemp(prefix="shakespeare-verify-"))
    hc, stage = work / "hill", work / "submission"
    for p in (hc, stage):
        if p.exists():
            shutil.rmtree(p)
    shutil.copytree(HILL, hc)
    full = (HILL / "train.txt").read_text()
    (hc / "private").mkdir(exist_ok=True)
    (hc / "private" / "val.txt").write_text(full[-VAL_LEN:])   # synthetic stand-in
    stage.mkdir()
    for f in SOL.glob("*.py"):
        shutil.copy(f, stage / f.name)
    (stage / "train.txt").write_text(full[:-VAL_LEN])          # train without pseudo-val
    spec = importlib.util.spec_from_file_location("hill_eval", hc / "eval.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(json.dumps(mod.eval(stage, final=a.final, eval_chars=a.chars)))


if __name__ == "__main__":
    sys.exit(main())
