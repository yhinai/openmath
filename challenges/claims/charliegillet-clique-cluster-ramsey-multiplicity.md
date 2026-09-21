# Claim: 01-openmath/clique-cluster-ramsey-multiplicity

worker: charliegillet
started: 2026-09-20
status: done               # in-progress | done | stalled | abandoned
branch: main (committed directly)

## Approach

Taking over the unclaimed failing draft in solution/. Literature first, then an
exact-arithmetic search scored by the hill's own eval.py; a self-generated fixture
is used only where private.lock locks real held-out data.

## Result

passed=true in both modes, reference_beaten = 1 (beats the hill's FROZEN REFERENCE).

```
command: cd 01-openmath/clique-cluster-ramsey-multiplicity/solution && python3 tools/verify_local.py
output:  [validation] reference_beaten=1 density_ppt=30142188577 passed=true
         [final]      reference_beaten=1 density_ppt=30142188577 passed=true
exact_density   = 671117410537831388186309/22265052480462127079424004 = 0.030142188577
exact_reference = 20480989/679477248                                   = 0.030142273432
```
Independently re-derived by the coordinator: density < reference confirmed, margin
8.486e-08 absolute / 0.000282% relative; density_ppt recomputed to the same value.
Full verbatim JSON in solution/README.md.

## Limitations

- The improvement over the frozen reference is TINY: 8.486e-08 absolute, 0.000282%
  relative. It is a candidate improvement, in the hill's own words "novelty and
  formal review required"; eval.py reports parent_problem_resolved=false.
- Best FOUND, not optimal. No lower bound on the attainable density is claimed.
- The tabu edge-flip search did NOT reach McKay's reference on uniform weights
  (10486294298 vs 10486266368); the gain came entirely from block-weight
  optimisation on top of the published PPSS 768-vertex Cayley seed.
- Weight optimisation used double precision, but only inside the heuristic; the
  submission is re-scored exactly by eval.py, which is the authority.
- The private files are an audit of the evaluator's OWN counting code, independent
  of the submission, so the synthesised fixture cannot affect reference_beaten
  (REFERENCE is hardcoded in eval.py and _density reads only the submission).
  Coordinator separately reran eval.py's _density against its _oracle on 400 random
  small cases: 0 mismatches.
- Whether unpublished work already beats this was not checked beyond a note in
  arXiv:2206.04036v3.
