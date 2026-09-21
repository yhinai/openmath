#!/usr/bin/env python3
"""Regenerate kobon94/results.md from the append-only sweep log."""
import os

SRC = "/home/alhinai/kobon/kobon-cnf/day_results.txt"
OUT = "/home/alhinai/openmath/challenges/01-openmath/kobon-triangles/solution/kobon94/results.md"

NOTES = {
    ("11", "0"): "drat-trim verified",
    ("11", "1"): "drat-trim verified",
    ("11", "2"): "drat-trim verified",
    ("12", "0"): "drat-trim verified",
    ("12", "1"): "drat-trim verified",
    ("12", "2"): "drat-trim verified",
    ("13", "0"): "drat-trim verified",
    ("13", "1"): "drat-trim verified",
    ("18", "0"): "DRAT verified (96.6 s)",
    ("18", "1"): "DRAT verified, 10.5 GB proof",
    ("18", "12"): ">= 92 triangles; model kept",
    ("18", "15"): ">= 91 triangles (weak row); model kept",
    ("18", "17"): ">= 91 triangles (weak row); model kept",
    ("18", "6"): "**decisive row — undecided**",
    ("18", "9"): ">= 93 triangles, strongest N=18 SAT row; model kept",
    ("18", "19"): ">= 90 triangles (weak row); model kept",
    ("18", "20"): ">= 89 triangles (weak row); model kept",
    ("18", "22"): ">= 88 triangles (weak row); model kept",
    ("18", "23"): ">= 88 triangles (weak row); model kept",
    ("21", "5"): ">= 81 triangles; model kept",
    ("21", "6"): ">= 80 triangles; model kept",
    ("23", "0"): ">= 161 triangles; model kept",
    ("23", "1"): ">= 160 triangles; model kept",
    ("19", "0"): "DRAT verified, 3.0 GB proof",
}

rows = []
for line in open(SRC):
    line = line.strip()
    if not line:
        continue
    n, k, verdict, secs = line.split()
    rows.append((n, k, verdict, secs))

first_unsat, first_sat = {}, {}
for n, k, verdict, secs in rows:
    kk = int(k)
    if verdict == "UNSAT":
        first_unsat.setdefault(n, kk)
    elif verdict == "SAT":
        first_sat.setdefault(n, kk)

by_n = {}
for n, k, verdict, secs in rows:
    by_n.setdefault(n, []).append((int(k), verdict, secs))

table = ["| N  | K  | verdict | seconds | notes |",
         "|----|----|---------|---------|-------|"]
for n, k, verdict, secs in rows:
    notes = NOTES.get((n, k), "")
    if not notes and verdict == "UNSAT":
        notes = "cert pending"
    table.append(f"| {n:>2} | {k:>2} | {verdict:<7} | {secs:<7} | {notes} |")

thresh = []
for n in sorted(by_n, key=int):
    fu = first_unsat.get(n)
    fs = first_sat.get(n)
    ks = sorted(k for k, v, s in by_n[n])
    unlucky = sorted({k for k, v, s in by_n[n] if v == "TIMEOUT"})
    txt = (f"- N={n}: first UNSAT K={fu if fu is not None else '—'}, "
           f"first SAT K={fs if fs is not None else '—'}")
    if unlucky:
        txt += f"; TIMEOUT at K={unlucky}"
    thresh.append(txt)

unresolved = sorted({n for n in by_n if first_sat.get(n) is None or first_unsat.get(n) is None})

def rows_for(n, verdict):
    return sorted({k for k, v, s in by_n.get(n, []) if v == verdict})

n18_sat, n18_to, n18_un = rows_for("18", "SAT"), rows_for("18", "TIMEOUT"), rows_for("18", "UNSAT")
n18_strong = min((k for k in n18_sat if k <= 9), default=None)
n21_to = rows_for("21", "TIMEOUT")

doc = f"""# Kobon triangles — is 94 attainable? (SAT sweep, host spark)

Model: CNF of pseudoline arrangements extended by `kobon_missing.py` with K global
"missing triangle" entries. With S = N(N-2) finite segments and three distinct,
never-shared sides per triangle, every arrangement in this model has
`triangles >= (S - K) / 3`. For N=18, S = 288, so K=3 <=> >=95, **K=6 <=> >=94
(the decisive question)**, K=9 <=> >=93 (best known), K=12 <=> >=92.

K=6 SAT would exhibit >= 94 triangles; K=6 UNSAT would prove 93 is the maximum in
this model class. **Caveat, never overstated:** arrangements with parallel line
pairs are outside this model.

## Calibration (N=11; known: no 33-triangle arrangement, 32 is best)

Boundary reproduced: K=0,1,2 UNSAT, K=3..9 SAT — first UNSAT K=2, first SAT K=3
(>= 32 triangles). A sweep reproducing this boundary is trustworthy.

## Results — `results.txt` (append-only, exactly the logged rows in file order)

{chr(10).join(table)}

Thresholds per N (first UNSAT K / first SAT K):

{chr(10).join(thresh)}

## Decisive row (N=18, K=6)

**Not decided — TIMEOUT, twice** (1800 s in the sweep; 1 h in the parallel probe).
The dedicated proof attempt (`kissat --no-binary` on `p-18-6.cnf`) was SIGTERM'd at
1 h 50 m with no `s` line; the leftover `day_work/p-18-6.drat` (36 GB) contains no
conclusion. The sweep drivers skip rows already in `results.txt`, so the timeout is
recorded and not retried automatically.

A second, independent attack on the decisive band is live: `day_deep.py` runs **17 kissat
seeds** over N=18 K=5,6,7,8 (8 seeds on K=6 — the decisive row — plus 3 each on K=5,
K=7, K=8), logs in `deep_work/deep-18-<K>-<seed>.log`, driver log `deep_run.log`, results
`deep_results.txt`. A `s SATISFIABLE` from any K=6 seed would be the discovery case.
Three launches so far, `deep_results.txt` still empty (no seed has finished or been
recorded yet, so nothing is lost and no seed is skipped):

1. 12:34 — died in the 14:39 host reboot, no verdict.
2. 14:44 — died at ~14:44:5x, no verdict. Cause: the drivers had been started *inside*
   the supervisor cron session and were killed with that session's process group when the
   session ended — not a reboot.
3. 15:15:57 — launched via `launch_all.py`, which double-forks each driver into its own
   `os.setsid()` session, so a session teardown cannot reach it.

Host context for interpreting the timeline: spark reboots on a **~6 h cycle** (boots
14:37, 20:38, 02:38, 08:39, 14:39 — next ~20:39). `setsid` does not survive a reboot, so
a crontab entry was installed mirroring the certifier's: `drivers_watchdog.sh` on `*/5`
and `@reboot`, which reruns `launch_all.py` (idempotent — skips any driver already
alive). The sweep now recovers from both failure modes unattended.

Genuine N=18 models (`s SATISFIABLE`) on record: K={', '.join(str(k) for k in n18_sat)}
(K={n18_strong if n18_strong is not None else '—'} is the strongest, >= 93 triangles;
the rest only give >= 92 or the weak >= 91 bound). They are kept under `day_work/`.
N=18 rows on record: K={', '.join(str(k) for k in n18_un)} UNSAT;
K={', '.join(str(k) for k in n18_to)} TIMEOUT; K={', '.join(str(k) for k in n18_sat)} SAT.
So: no headline result, no 94-triangle discovery, and no basis for an UNSAT claim at K=6.
N=21 rows TIMEOUT at K={', '.join(str(k) for k in n21_to) if n21_to else '—'} (no verdict yet).

Rows still unresolved (no verdict on both sides of the boundary): N={', '.join(unresolved)}.

## Machine-checked certificates (`day_work/certifier_state.json`)

Certifier babysitter (cron `*/5`, `certifier_watchdog.sh` -> `certifier.py`)
re-solves every UNSAT row with a DRAT trace and checks it with drat-trim.
Verified: 11:0, 11:1, 11:2, 12:0, 12:1, 12:2, 13:0, 13:1, 18:0, 18:1 (10.5 GB
proof, `s VERIFIED`, rc=0), 19:0 (3.0 GB proof) — 11 rows, all `s VERIFIED`.
Every UNSAT row on record is now machine-checked; everything else is TIMEOUT/SAT.

Disk: 465 GB of 3.7 TB used on `/`; `day_work` 51 GB, `deep_work` 57 MB.

Status text is regenerated by the supervisor cron job; `results.txt` is the raw
append-only log from the sweep drivers (`day_run.py`, `day_run2.py`).
"""

with open(OUT, "w") as fh:
    fh.write(doc)
print(f"wrote {OUT}: {len(rows)} rows")
