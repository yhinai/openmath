#!/usr/bin/env python3
"""Detach the Kobon sweep drivers into their own sessions so they survive
gateway/cron-session teardown.

Plain `nohup ... &` was NOT enough: the drivers shared the launching cron
session's process group and were SIGKILLed when that session ended (observed
2026-09-21 14:43:5x: day_run.py, day_run2.py and all 17 deep kissat jobs died
mid-run).  Each child here gets its own session via os.setsid(), exactly like
launch_deep.py, which did survive.

Skips any driver whose process is already alive (matched by script name in the
full command line), so this is safe to call on every supervisor run.
"""
import os
import subprocess
import sys

DRIVERS = [
    ("day_run.py", "day_console.log"),
    ("day_run2.py", "day_run2.console.log"),
    ("day_deep.py", "day_deep.console.log"),
]


def alive(script):
    out = subprocess.run(["pgrep", "-f", "python3 -u " + script],
                         capture_output=True, text=True).stdout.strip()
    return bool(out)


def spawn(script, logname):
    pid = os.fork()
    if pid > 0:
        return pid
    os.setsid()                      # own session => immune to pgid kills
    pid2 = os.fork()
    if pid2 > 0:
        os._exit(0)
    os.chdir("/home/alhinai/kobon/kobon-cnf")
    out = os.open(logname, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    os.dup2(out, 1)
    os.dup2(out, 2)
    devnull = os.open(os.devnull, os.O_RDONLY)
    os.dup2(devnull, 0)
    os.execvp("python3", ["python3", "-u", script])
    os._exit(127)


def main():
    for script, logname in DRIVERS:
        if not os.path.exists(script):
            print("skip (absent): " + script)
            continue
        if alive(script):
            print("already running: " + script)
            continue
        pid = spawn(script, logname)
        print("spawned {} as pid {}".format(script, pid))
        sys.stdout.flush()
        os.waitpid(pid, 0)           # reap the short-lived intermediate


if __name__ == "__main__":
    main()
