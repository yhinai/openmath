#!/usr/bin/env python3
"""Day-long experiment driver for the Kobon "is 94 attainable?" question.

For each (N, K) it builds the global-missing CNF (kobon_missing.py), runs Kissat,
and appends `N K verdict seconds` to day_results.txt.

Semantics: the model requires every finite segment to be a triangle side unless
one of K global "missing" entries sits on it; with S = N(N-2) segments and three
distinct, never-shared sides per triangle, triangles >= (S-K)/3.  So
  K <= 6 for N=18  <=>  "there exists an arrangement with >= 94 triangles".

Two-sided calibration on N=11 (known: no 33, but 32 exists):
  K=2 -> UNSAT, K=3 -> SAT.  A sweep that reproduces that boundary is trustworthy.
"""
import os
import subprocess
import sys
import time

TMP = "tmp"
WORK = "day_work"
os.makedirs(WORK, exist_ok=True)
RES = "day_results.txt"
TMO = int(os.environ.get("KOBON_TMO", "1800"))

# (N, Kmax): sweep K = 0..Kmax for these N
QUEUE = [
    (11, 9),     # calibration: known no-33, yes-32
    (18, 48),    # THE question: threshold between 94 (K=6) and the SAT threshold
    (16, 12),    # breadth: bound 74, best known 72
    (14, 12),    # breadth: bound 56, best known 53
    (10, 9),     # breadth: bound 26, best known 25
    (20, 12),    # breadth: bound 120, best known 116
    (22, 12),    # breadth
    (24, 12),    # breadth
    (26, 12),    # breadth
    (28, 12),    # breadth
]


def base_cnf(N):
    path = "{}/in-kobon-{}.cnf".format(TMP, N)
    if not os.path.exists(path):
        subprocess.run(["python3", "-c",
                        "import koboncnf; koboncnf.generate({}, '{}', generate_table=False)".format(N, path)],
                       check=True, capture_output=True)
    return path


def log(msg):
    line = "[{}] {}".format(time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open("day_run.log", "a") as f:
        f.write(line + "\n")


def already_done(N, K):
    if not os.path.exists(RES):
        return False
    for l in open(RES):
        p = l.split()
        if len(p) >= 4 and p[0] == str(N) and p[1] == str(K) and p[2] in ("SAT", "UNSAT", "TIMEOUT"):
            return True
    return False


def run_one(N, K):
    base = base_cnf(N)
    cnf = "{}/m-{}-{}.cnf".format(WORK, N, K)
    subprocess.run(["python3", "kobon_missing.py", base, str(N), str(K), cnf],
                   check=True, capture_output=True)
    t0 = time.time()
    verdict = "TIMEOUT"
    try:
        p = subprocess.run(["kissat", cnf], capture_output=True, text=True, timeout=TMO)
        out = p.stdout
        if "s UNSATISFIABLE" in out:
            verdict = "UNSAT"
        elif "s SATISFIABLE" in out:
            verdict = "SAT"
    except subprocess.TimeoutExpired:
        verdict = "TIMEOUT"
    dt = time.time() - t0
    with open(RES, "a") as f:
        f.write("{} {} {} {:.1f}\n".format(N, K, verdict, dt))
    log("N={} K={} -> {} ({:.1f}s)".format(N, K, verdict, dt))
    return verdict, cnf


def main():
    log("=== day run starting; queue: {}".format(QUEUE))
    for N, kmax in QUEUE:
        for K in range(0, kmax + 1):
            if already_done(N, K):
                continue
            v, cnf = run_one(N, K)
            # keep SAT instances (they may yield a real arrangement); drop UNSAT bulk
            if v == "SAT":
                keep = "day_work/SAT-{}-{}.cnf".format(N, K)
                subprocess.run(["cp", cnf, keep])
                log("kept SAT instance at " + keep)
            else:
                try:
                    os.remove(cnf)
                except OSError:
                    pass
    log("=== day run finished")


if __name__ == "__main__":
    main()
