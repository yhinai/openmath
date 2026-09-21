#!/bin/sh
# Reproduction of the search pipeline (heuristic, seeded but timing-dependent:
# the tabu runs stop on wall-clock, so exact re-runs are not bit-reproducible).
# 1. seed: hill/examples/published_cayley_768/solution.json  -> seed.rows
# 2. tabu edge-flip search (uniform weights):   ./tabu seed.rows out.rows SEED TENURE SECONDS
#    used: tenure 400 for 20 min, then tenure 1000 from that output for 25 min,
#    then tenure 1000 from that for 12 min  -> template.rows  (T = 10486294298)
# 3. weight descent:  ./wopt template.rows template.weights 40 4000 [init.weights]
# 4. python3 make_solution.py template.rows template.weights ../   -> solution.json
# 5. python3 verify_local.py
set -e
cd "$(dirname "$0")"
cc -O3 -march=native -o /tmp/tabu tabu.c
cc -O3 -march=native -o /tmp/wopt wopt.c -lm
python3 -c "import json;d=json.load(open('../../hill/examples/published_cayley_768/solution.json'));open('/tmp/seed.rows','w').write('\n'.join(d['red_rows'])+'\n')"
/tmp/tabu /tmp/seed.rows /tmp/s1.rows 9 400 1200
/tmp/tabu /tmp/s1.rows /tmp/s2.rows 12 1000 1500
/tmp/tabu /tmp/s2.rows /tmp/s3.rows 25 1000 720
/tmp/wopt /tmp/s3.rows /tmp/s3.w 40 4000
python3 make_solution.py /tmp/s3.rows /tmp/s3.w /tmp/cand
python3 verify_local.py /tmp/cand
