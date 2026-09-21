#!/usr/bin/env python3
"""Second (breadth) day-long experiment driver for the Kobon "is 94 attainable?" question.

Companion to day_run.py: same contract, same result-file format (`N K verdict seconds`
appended to day_results.txt), but a disjoint queue of N values so the day covers more
breadth.  Runs concurrently with day_run.py; the two never share an (N, K) pair in
practice, and already_done() skips anything the other driver has already recorded.

For each (N, K) it builds the global-missing CNF (kobon_missing.py), runs
`timeout $KOBON_TMO kissat <cnf>`, parses the verdict from the solver output
('s SATISFIABLE' / 's UNSATISFIABLE'), and appends the row to day_results.txt.

With S = N(N-2) segments and three distinct, never-shared sides per triangle,
triangles >= (S-K)/3, so K <= 6 for N=18 <=> "there exists an arrangement with >= 94
triangles".

SAT instances are preserved as day_work/SAT-2-<N>-<K>.cnf plus a copy of the solver
output as day_work/SAT-2-<N>-<K>.sat; UNSAT bulk is deleted.
"""
import os
import subprocess
import time

TMP = "tmp"
WORK = "day_work"
os.makedirs(WORK, exist_ok=True)
RES = "day_results.txt"
LOG = "day_run2.log"
TMO = os.environ.get("KOBON_TMO", "1800")

# (N, Kmax): sweep K = 0..Kmax for these N.  N values disjoint from day_run.py's queue.
QUEUE = [
    (12, 9),     # breadth: bound 36, best known 33
    (13, 9),     # breadth: bound 44, best known 40
    (15, 12),    # breadth: bound 62, best known 59
    (17, 6),     # calibration neighbour: bound 80, best known 76/77
    (19, 6),     # breadth: bound 106, best known 102
    (21, 6),     # breadth
    (23, 6),     # breadth
    (25, 6),     # breadth
    (27, 6),     # breadth
    (29, 6),     # breadth
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
    with open(LOG, "a") as f:
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
    cnf = "{}/m2-{}-{}.cnf".format(WORK, N, K)
    subprocess.run(["python3", "kobon_missing.py", base, str(N), str(K), cnf],
                   check=True, capture_output=True)
    t0 = time.time()
    verdict = "TIMEOUT"
    out = ""
    try:
        p = subprocess.run(["timeout", str(TMO), "kissat", cnf],
                           capture_output=True, text=True, timeout=int(TMO) + 120)
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
    return verdict, cnf, out


def main():
    log("=== day run 2 starting; queue: {}".format(QUEUE))
    for N, kmax in QUEUE:
        for K in range(0, kmax + 1):
            if already_done(N, K):
                continue
            v, cnf, out = run_one(N, K)
            # keep SAT instances (they may yield a real arrangement); drop UNSAT bulk
            if v == "SAT":
                keep = "{}/SAT-2-{}-{}.cnf".format(WORK, N, K)
                subprocess.run(["cp", cnf, keep])
                with open("{}/SAT-2-{}-{}.sat".format(WORK, N, K), "w") as f:
                    f.write(out)
                log("kept SAT instance at " + keep)
            else:
                try:
                    os.remove(cnf)
                except OSError:
                    pass
    log("=== day run 2 finished")


if __name__ == "__main__":
    main()
