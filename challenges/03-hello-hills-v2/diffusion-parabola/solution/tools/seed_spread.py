"""Run the submission once, then score it with the hill's own chamfer_distance
against N independently seeded held-out draws, to quantify seed-to-seed spread.
"""
import importlib.util, sys
from pathlib import Path

import numpy as np

SOL = Path(__file__).resolve().parents[1]
HILL = SOL.parent / "hill"

spec = importlib.util.spec_from_file_location("ev", HILL / "eval.py")
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)

sys.path.insert(0, str(SOL))
import solution  # noqa: E402

n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 50
train = ev.generate_parabola(ev.N_TRAIN, seed=ev.TRAIN_SEED)
P = solution.train_and_sample(train, steps=10000, n_samples=2000, seed=0)
vals = []
for s in range(1, n_seeds + 1):
    t = ev.generate_parabola(ev.N_TEST, seed=s * 7919 + 13)
    vals.append(ev.chamfer_distance(P, t))
vals = np.array(vals)
print(f"n_seeds={n_seeds} mean={vals.mean():.9f} std={vals.std(ddof=1):.9f} "
      f"min={vals.min():.9f} max={vals.max():.9f}")
