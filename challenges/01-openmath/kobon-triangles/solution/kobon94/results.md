# Kobon triangles — is 94 attainable? (SAT sweep, host spark)

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

| N  | K  | verdict | seconds | notes |
|----|----|---------|---------|-------|
| 11 |  0 | UNSAT   | 0.5     | drat-trim verified |
| 11 |  1 | UNSAT   | 9.3     | drat-trim verified |
| 11 |  2 | UNSAT   | 97.3    | drat-trim verified |
| 11 |  3 | SAT     | 34.0    |  |
| 11 |  4 | SAT     | 50.5    |  |
| 11 |  5 | SAT     | 272.2   |  |
| 11 |  6 | SAT     | 37.4    |  |
| 11 |  7 | SAT     | 82.4    |  |
| 12 |  0 | UNSAT   | 1.1     | drat-trim verified |
| 12 |  1 | UNSAT   | 19.7    | drat-trim verified |
| 18 |  9 | SAT     | 6m      | >= 93 triangles, strongest N=18 SAT row; model kept |
| 12 |  2 | UNSAT   | 261.2   | drat-trim verified |
| 11 |  8 | SAT     | 907.4   |  |
| 11 |  9 | SAT     | 13.1    |  |
| 18 |  0 | UNSAT   | 30.3    | DRAT verified (96.6 s) |
| 12 |  3 | TIMEOUT | 1800.0  |  |
| 18 |  1 | UNSAT   | 1648.7  | DRAT verified, 10.5 GB proof |
| 12 |  4 | TIMEOUT | 1800.0  |  |
| 18 |  2 | TIMEOUT | 1800.0  |  |
| 18 | 12 | SAT     | 1h      | >= 92 triangles; model kept |
| 18 |  3 | TIMEOUT | 1h      |  |
| 18 |  6 | TIMEOUT | 1h      | **decisive row — undecided** |
| 12 |  5 | TIMEOUT | 1873.7  |  |
| 18 |  3 | TIMEOUT | 1803.3  |  |
| 12 |  6 | TIMEOUT | 1800.0  |  |
| 18 |  4 | TIMEOUT | 1800.0  |  |
| 12 |  7 | TIMEOUT | 1800.0  |  |
| 18 |  5 | TIMEOUT | 1800.0  |  |
| 12 |  8 | TIMEOUT | 1800.0  |  |
| 18 |  7 | TIMEOUT | 1800.0  |  |
| 12 |  9 | SAT     | 54.4    |  |
| 13 |  0 | UNSAT   | 2.3     | drat-trim verified |
| 13 |  1 | UNSAT   | 72.8    | drat-trim verified |
| 13 |  2 | SAT     | 7.9     |  |
| 13 |  3 | SAT     | 7.8     |  |
| 13 |  4 | SAT     | 28.4    |  |
| 13 |  5 | SAT     | 32.6    |  |
| 13 |  6 | SAT     | 87.7    |  |
| 13 |  7 | SAT     | 21.7    |  |
| 13 |  8 | SAT     | 43.0    |  |
| 13 |  9 | SAT     | 25.1    |  |
| 15 |  0 | SAT     | 3.9     |  |
| 15 |  1 | SAT     | 1.5     |  |
| 15 |  2 | SAT     | 166.9   |  |
| 15 |  3 | SAT     | 20.0    |  |
| 15 |  4 | SAT     | 50.5    |  |
| 15 |  5 | SAT     | 3.7     |  |
| 15 |  6 | SAT     | 11.9    |  |
| 15 |  7 | SAT     | 12.1    |  |
| 15 |  8 | SAT     | 6.1     |  |
| 15 |  9 | SAT     | 49.3    |  |
| 15 | 10 | SAT     | 91.9    |  |
| 15 | 11 | SAT     | 41.1    |  |
| 15 | 12 | SAT     | 13.6    |  |
| 17 |  0 | SAT     | 12.9    |  |
| 17 |  1 | SAT     | 96.2    |  |
| 17 |  2 | SAT     | 82.6    |  |
| 17 |  3 | SAT     | 193.9   |  |
| 17 |  4 | SAT     | 398.1   |  |
| 17 |  5 | SAT     | 30.7    |  |
| 17 |  6 | SAT     | 81.7    |  |
| 18 |  8 | TIMEOUT | 1800.0  |  |
| 19 |  0 | UNSAT   | 407.4   | DRAT verified, 3.0 GB proof |
| 18 | 10 | TIMEOUT | 1800.0  |  |
| 19 |  1 | TIMEOUT | 1800.0  |  |
| 19 |  2 | SAT     | 89.1    |  |
| 19 |  3 | SAT     | 186.2   |  |
| 19 |  4 | SAT     | 635.9   |  |
| 19 |  5 | SAT     | 329.4   |  |
| 18 | 11 | TIMEOUT | 1800.0  |  |
| 19 |  6 | TIMEOUT | 1800.0  |  |
| 21 |  0 | SAT     | 87.6    |  |
| 18 | 13 | TIMEOUT | 1800.0  |  |
| 21 |  1 | SAT     | 162.1   |  |
| 18 | 14 | TIMEOUT | 1800.0  |  |
| 21 |  2 | TIMEOUT | 1800.0  |  |
| 18 | 15 | SAT     | 570.2   | >= 91 triangles (weak row); model kept |
| 21 |  3 | TIMEOUT | 1800.0  |  |
| 18 | 16 | TIMEOUT | 1800.0  |  |
| 18 | 17 | SAT     | 1117.7  | >= 91 triangles (weak row); model kept |
| 21 |  4 | TIMEOUT | 1800.0  |  |
| 21 |  5 | SAT     | 1581.5  |  |
| 18 | 18 | TIMEOUT | 1800.0  |  |
| 18 | 19 | SAT     | 875.3   |  |

Thresholds per N (first UNSAT K / first SAT K):

- N=11: first UNSAT K=0, first SAT K=3
- N=12: first UNSAT K=0, first SAT K=9; TIMEOUT at K=[3, 4, 5, 6, 7, 8]
- N=13: first UNSAT K=0, first SAT K=2
- N=15: first UNSAT K=—, first SAT K=0
- N=17: first UNSAT K=—, first SAT K=0
- N=18: first UNSAT K=0, first SAT K=9; TIMEOUT at K=[2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 16, 18]
- N=19: first UNSAT K=0, first SAT K=2; TIMEOUT at K=[1, 6]
- N=21: first UNSAT K=—, first SAT K=0; TIMEOUT at K=[2, 3, 4]

## Decisive row (N=18, K=6)

**Not decided — TIMEOUT, twice** (1800 s in the sweep; 1 h in the parallel probe).
The dedicated proof attempt (`kissat --no-binary` on `p-18-6.cnf`) was SIGTERM'd at
1 h 50 m with no `s` line; the leftover `day_work/p-18-6.drat` (36 GB) contains no
conclusion. The sweep drivers skip rows already in `results.txt`, so the timeout is
recorded and not retried automatically.

Genuine N=18 models (`s SATISFIABLE`) on record: K=9, 12, 15, 17, 19
(K=9 is the strongest, >= 93 triangles;
the rest only give >= 92 or the weak >= 91 bound). They are kept under `day_work/`.
N=18 rows on record: K=0, 1 UNSAT;
K=2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 16, 18 TIMEOUT; K=9, 12, 15, 17, 19 SAT.
So: no headline result, no 94-triangle discovery, and no basis for an UNSAT claim at K=6.
N=21 rows TIMEOUT at K=2, 3, 4 (no verdict yet).

Rows still unresolved (no verdict on both sides of the boundary): N=15, 17, 21.

## Machine-checked certificates (`day_work/certifier_state.json`)

Certifier babysitter (cron `*/5`, `certifier_watchdog.sh` -> `certifier.py`)
re-solves every UNSAT row with a DRAT trace and checks it with drat-trim.
Verified: 11:0, 11:1, 11:2, 12:0, 12:1, 12:2, 13:0, 13:1, 18:0, 18:1 (10.5 GB
proof, `s VERIFIED`, rc=0), 19:0 (3.0 GB proof) — 11 rows, all `s VERIFIED`.
Every UNSAT row on record is now machine-checked; everything else is TIMEOUT/SAT.

Disk: 464 GB of 3.7 TB used on `/`; `day_work` 50 GB.

Status text is regenerated by the supervisor cron job; `results.txt` is the raw
append-only log from the sweep drivers (`day_run.py`, `day_run2.py`).
