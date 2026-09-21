# Machine-checkable DRAT certificates (Kobon CNF)

Verifier: `/home/alhinai/kobon/drat-trim/drat-trim` (built from github.com/marijnheule/drat-trim)
Solver: `kissat 4.0.4`. Note: kissat 4.0.4 has **no `--proof=` option** — the proof
file is a *positional* second argument. ASCII DRAT was requested with `--no-binary`.

    kissat --no-binary <cnf> <proof.drat>

## 1. Base N=18 model (96 triangles impossible for 18 lines)

- CNF: `tmp/in-kobon-18.cnf` (14994 vars, 554778 clauses, 10149133 bytes)
- Command: `kissat --no-binary tmp/in-kobon-18.cnf tmp/proof18.drat > tmp/kissat18_proof.log`
- Verdict line: `s UNSATISFIABLE` (kissat exit 20, process-time 30s)
- Proof: `tmp/proof18.drat`, 247888825 bytes, sha256 `03029d5d830adab2205a2ef1164803b4bf4adafe77f3d1dc912c8f50260a950b`
- Verify command: `drat-trim tmp/in-kobon-18.cnf tmp/proof18.drat`
- drat-trim output (verbatim):

```
c parsing input formula with 14994 variables and 554778 clauses
c finished parsing
c detected empty clause; start verification via backward checking
c 94965 of 554778 clauses in core
c 265544 of 1149277 lemmas in core using 9253757 resolution steps
c 23559 RAT lemmas in core; 117221 redundant literals in core lemmas
s VERIFIED
c verification time: 110.035 seconds
```

## 2. N=11, K=2 (no 33-triangle arrangement) — smallest interesting UNSAT with missing entries

- CNF: `day_work/m-11-2.cnf` — did **not** exist, rebuilt with
  `python3 kobon_missing.py tmp/in-kobon-11.cnf 11 2 day_work/m-11-2.cnf`
  (7038 vars, 78754 clauses, relaxed 5940 clauses, 1424452 bytes)
- Command: `kissat --no-binary day_work/m-11-2.cnf day_work/m-11-2.drat`
- Verdict line: `s UNSATISFIABLE` (kissat exit 20, ~1m40s)
- Proof: `day_work/m-11-2.drat`, 633860584 bytes, sha256 `645497ef8e8e87a048e17aea62470bc10e587a041449512b3a835bb98e1d553d`
- Verify command: `drat-trim day_work/m-11-2.cnf day_work/m-11-2.drat`
- drat-trim output (verbatim):

```
c parsing input formula with 7038 variables and 78754 clauses
c finished parsing
c detected empty clause; start verification via backward checking
c 46265 of 78754 clauses in core
c 1035090 of 2146008 lemmas in core using 139997368 resolution steps
c 6146 RAT lemmas in core; 2418480 redundant literals in core lemmas
s VERIFIED
c verification time: 118.286 seconds
```

## 3. N=18, K=6 (>= 94 triangles, the decisive instance)

- CNF exists: `day_work/p-18-6.cnf` (73740 vars, 672264 clauses, relaxed 29376 clauses)
- `day_results.txt` contains **no row for N=18 K=6**. The only N=18 row present is
  `18 9 SAT 6m` (i.e. 93 triangles are reachable). The pre-existing
  `day_work/p-18-6.sat` log is truncated at ~448 s with **no verdict line** (an
  interrupted run), likewise `p-18-3.sat` and `p-18-12.sat`.
- `kissat --no-binary day_work/p-18-6.cnf day_work/p-18-6.drat` was started to produce
  a proof; at ~21 min it had not terminated. **No certificate for this instance —
  verdict neither UNSAT nor SAT established here.**
