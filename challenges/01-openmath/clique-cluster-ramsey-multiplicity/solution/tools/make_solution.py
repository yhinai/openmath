#!/usr/bin/env python3
"""rows file (+ optional integer weights file) -> solution.json.  usage: make_solution.py rows [weights] outdir"""
import json, sys, pathlib
a = sys.argv[1:]
rows = pathlib.Path(a[0]).read_text().split()
w = [int(x) for x in pathlib.Path(a[1]).read_text().split()] if len(a) == 3 else [1] * len(rows)
out = pathlib.Path(a[-1]); out.mkdir(parents=True, exist_ok=True)
(out / "solution.json").write_text(json.dumps({"schema": "weighted-two-color-blowup-v1", "weights": w, "red_rows": rows}, separators=(",", ":")))
print(min(w), max(w), sum(w))
