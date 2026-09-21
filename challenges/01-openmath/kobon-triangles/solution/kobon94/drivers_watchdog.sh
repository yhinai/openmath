#!/bin/sh
# Kobon sweep driver babysitter -- mirror of certifier_watchdog.sh for the
# day_run.py / day_run2.py / day_deep.py sweep drivers.
#
# Why this exists: spark reboots on a ~6 h cycle (observed boots 14:37, 20:38,
# 02:38, 08:39, 14:39), and drivers launched by hand from a hermes/cron session
# also died inside a minute of that session ending (their process group went
# with it).  launch_all.py double-forks each driver into its own os.setsid()
# session and skips any driver already alive, so running it every 5 min and at
# @reboot is idempotent and keeps the sweep going unattended.
#
# Remove with:  crontab -l | grep -v drivers_watchdog | crontab -
# Stop the drivers with:  pkill -f 'python3 -u day_run'
cd /home/alhinai/kobon/kobon-cnf || exit 1
exec python3 launch_all.py >> driver_watchdog.log 2>&1
