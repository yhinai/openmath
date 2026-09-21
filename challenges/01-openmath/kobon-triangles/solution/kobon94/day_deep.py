#!/usr/bin/env python3
"""Deep portfolio re-attack on the DECISIVE band for N=18.

day_run.py swept K=0..48 once with a 1800 s cap and will never revisit a row,
so N=18 K=6 (=> >=94 triangles) is stuck at TIMEOUT.  This driver re-runs the
decisive band K=5..8 with a long per-job cap and several kissat seeds in
parallel on the idle cores.  Append-only log: deep_results.txt
(columns: N K seed verdict seconds).  Nothing here touches day_results.txt.
"""
import os
import signal
import subprocess
import time

WORK = "deep_work"
RES = "deep_results.txt"
TMO = int(os.environ.get("DEEP_TMO", "21600"))          # 6 h per job
PLAN = {6: [0, 1, 2, 3, 4, 5, 6, 7],                    # decisive row, widest portfolio
        5: [0, 1, 2],
        7: [0, 1, 2],
        8: [0, 1, 2]}
N = 18

os.makedirs(WORK, exist_ok=True)


def log(msg):
    line = "[{}] {}".format(time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open("deep_run.log", "a") as f:
        f.write(line + "\n")


def base_cnf():
    path = "tmp/in-kobon-{}.cnf".format(N)
    if not os.path.exists(path):
        subprocess.run(["python3", "-c",
                        "import koboncnf; koboncnf.generate({}, '{}', generate_table=False)".format(N, path)],
                       check=True, capture_output=True)
    return path


def cnf_for(K):
    path = "{}/m-{}-{}.cnf".format(WORK, N, K)
    if not os.path.exists(path):
        subprocess.run(["python3", "kobon_missing.py", base_cnf(), str(N), str(K), path],
                       check=True, capture_output=True)
    return path


def done(K, seed):
    if not os.path.exists(RES):
        return False
    for l in open(RES):
        p = l.split()
        if len(p) >= 4 and p[0] == str(N) and p[1] == str(K) and p[2] == str(seed) \
                and p[3] in ("SAT", "UNSAT", "TIMEOUT"):
            return True
    return False


def main():
    log("=== deep run starting; plan {} TMO={}s ===".format(PLAN, TMO))
    procs = []
    for K, seeds in sorted(PLAN.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        cnf = cnf_for(K)
        for seed in seeds:
            if done(K, seed):
                continue
            out = open("{}/deep-{}-{}-{}.log".format(WORK, N, K, seed), "w")
            p = subprocess.Popen(["kissat", "--seed={}".format(seed), cnf],
                                 stdout=out, stderr=subprocess.STDOUT,
                                 preexec_fn=os.setsid)
            procs.append((K, seed, p, out, time.time()))
            log("launched K={} seed={} pid={}".format(K, seed, p.pid))

    remaining = list(procs)
    while remaining:
        time.sleep(30)
        still = []
        for K, seed, p, out, t0 in remaining:
            rc = p.poll()
            if rc is None:
                if time.time() - t0 > TMO:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                    p.wait()
                    rc = -9
                else:
                    still.append((K, seed, p, out, t0))
                    continue
            out.close()
            txt = open("{}/deep-{}-{}-{}.log".format(WORK, N, K, seed)).read()
            dt = time.time() - t0
            if "s UNSATISFIABLE" in txt:
                v = "UNSAT"
            elif "s SATISFIABLE" in txt:
                v = "SAT"
            else:
                v = "TIMEOUT"
            with open(RES, "a") as f:
                f.write("{} {} {} {} {:.1f}\n".format(N, K, seed, v, dt))
            log("N={} K={} seed={} -> {} ({:.1f}s)".format(N, K, seed, v, dt))
            if v == "SAT":
                keep = "{}/SAT-DEEP-{}-{}-{}.cnf".format(WORK, N, K, seed)
                subprocess.run(["cp", cnf_for(K), keep])
                log("kept SAT instance at " + keep)
        remaining = still
    log("=== deep run finished ===")


if __name__ == "__main__":
    main()
