# Goal 023 Task 2b Numerical Preflight

## Status And Scope

This is a read-only numerical/TDD preflight for Plan Task 2b. It derives the
implementation and review obligations but does not implement them. No tests,
simulations, RNG payloads, audit searches, fits, profiles, calibration, runtime
benchmark, artifacts, or holdout work were run.

The inspected authority and accepted Task 2a1 state are:

| Surface | SHA-256 |
| --- | --- |
| authoritative spec | `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d` |
| Plan | `df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e` |
| Runbook | `78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed` |
| accepted Task 2a1 source | `78169d0114029287fd9a81bd5024b632a4060a8b27b8a14839d616a85d35bdb1` |
| accepted Task 2a1 tests | `5321062bfe52574ee34c39d028ff6b6e01f85dce696f7b66f99855204ba4a223` |

Task 2a1 is accepted. Task 2a2 and Task 2b are currently absent. A source/test
scan found no transform, Halton, optimizer, profile, inverse-audit, or design-
audit implementation. The execution model requires one writer across the
shared source/test files and an explicit handoff plus live diff review before a
different writer takes over (Plan lines 5-13). Task 2b must therefore wait for
Task 2a2 completion, review, and handoff.

## Exact Contract Index

The implementation must be checked against these literal clauses, not a
restatement from memory:

| Contract | Authority |
| --- | --- |
| supports, float64, `ddof=0`, stable process primitives | spec lines 64-76, 113-144 |
| ordered-rate transform and `1e-9` gap | spec lines 209-222 |
| eight Halton starts and oracle subsets | spec lines 224-243 |
| literal L-BFGS-B call and convergence | spec lines 245-277 |
| natural-space adaptive profiles | spec lines 279-331 |
| audit vector, finite differences, SVD | spec lines 333-401 |
| recovery/collision frontier and nine audit counts | spec lines 403-430 |
| three rank-failing fixtures | spec lines 432-446 |
| potential/oracle/plugin diagnostics and firewall | spec lines 448-494 |
| canonical scenarios and schedule definitions | spec lines 527-595, 648-713 |
| Task 2b TDD/review boundary | Plan lines 230-266; Runbook lines 169-219 |

No scenario replication, calibration, holdout, artifact, CLI, or documentation
export belongs to Task 2b (Plan lines 265-266).

## Required Task 2a Handoff

### Existing Task 2a1 APIs Task 2b should reuse

Task 2b should build additively on these accepted interfaces:

- natural support constants and `ProcessParameters`/`JointParameters`;
- `AnalystHistory`, `ProcessOracleOutcome`, and `ObservationOracleHistory` as
  physically separate analyst/oracle contracts;
- `process_oracle_log_likelihood`, `observation_oracle_log_likelihood`, and
  `joint_log_likelihood_enumeration` as scalar correctness oracles;
- `joint_log_likelihood_forward` as the independent likelihood cross-check;
- `joint_path_posterior_weights` for analyst-only plug-in at-risk weights;
- `ProcessLogPrimitives`, immutable float64 arrays, and explicit
  `LikelihoodEvaluationError` failures.

Task 2b must not weaken exact built-in type checks, immutable array storage,
post-transition endpoint timing, omitted-emission semantics, or the analyst/
truth firewall already covered by Task 2a1 tests.

### Task 2a2 outputs Task 2b needs

The Task 2a2 handoff should expose or make directly constructible:

1. A deterministic, count-free canonical schedule/design surface for dense,
   structured, and sparse audits, sorted by integer `cell_id` then time. The
   pre-estimation audit must not need simulated counts or an RNG payload.
2. A compact immutable analyst batch representation containing cell IDs,
   `Q`, `TP`, retained-opportunity masks/times, efforts, and counts in canonical
   order. The scalar `AnalystHistory` tuple remains the correctness oracle.
3. Canonical process-oracle and observation-oracle batch surfaces that are
   physically distinct from the analyst batch.
4. One generalized float64 SVD/rank helper and provenance-bearing diagnostic
   result used by all five-column and three-column branches. Task 2b must not
   create a second SVD convention.
5. Pure builders for `potential_design`, `process_oracle_truth_at_risk`, and
   `joint_plugin_smoothed_at_risk`, or an exact documented seam by which Task 2b
   supplies MLE posterior weights to the shared builder.

The handoff review must prove that truth-at-risk fields cannot be reached from
the joint objective, global starts, bounds, profiles, inverse audit, plug-in
gate, or acceptance logic. A generic object carrying both analyst and truth
fields is not an acceptable convenience boundary.

## Runtime Primitive Layer

The current scalar likelihood is a strong analytic oracle but is not a viable
optimizer kernel by itself. A dense evaluation through nested Python calls is
approximately `5225 cells * 21 paths * 21 opportunities`, before finite-
difference multiplication, eight starts, and profiles. Task 2b should introduce
one vectorized/batched likelihood layer and prove exact agreement with the
accepted scalar APIs before using it in optimization.

Minimum runtime primitives:

1. **Coordinate maps**: forward/inverse global rate transform; process-only,
   observation-only, and joint subset maps; conditional profile maps.
2. **Frozen starts**: radical inverse and deterministic start tables for 8 and
   16 positive Halton indices, returned as immutable float64 data.
3. **Batched objectives**: process oracle, observation oracle, and analyst joint
   negative log likelihood, with fixed canonical summation order and no truth
   access.
4. **Vectorized joint kernel**: construct process path masses for all cells;
   compute present/quasi emission terms once per opportunity; use cumulative
   present-to-quasi emission differences to form all event/censor paths; call
   `scipy.special.logsumexp` over the path axis. Test against scalar enumeration
   and forward recursion for one, two, and 20 intervals, including irregular
   masks and no observations.
5. **Posterior path kernel**: normalized 21-path weights in canonical cell order
   for the plug-in design, equal to `joint_path_posterior_weights` cell by cell.
6. **Optimizer adapter**: one literal `minimize` call, one result validator, and
   typed immutable start/fit results. It must isolate one failed start without
   aborting later starts.
7. **Audit primitives**: stable audit-vector builder, central-difference scaled
   Jacobian, generalized SVD diagnostic, scaled natural distance, RMSE inverse
   objective, and typed audit result.
8. **Profile primitives**: conditional nuisance maps, projection, deterministic
   deduplication, point scheduler/cache, nuisance optimizer, bracket/root
   adapter, and final classification.

The scalar and batched paths should remain separate implementations so their
agreement is meaningful. Replacing the scalar oracle with a wrapper around the
batched kernel would erase the independent check.

## Ordered-Rate Transform Checklist

### RED tests

1. Assert the exact forward map for `p_frac,q_frac` corners and interior points:
   `lambda_present = 0.25 + 9.75*p_frac`,
   `q_upper = min(1, lambda_present-1e-9)`, and
   `lambda_quasi = 0.01 + (q_upper-0.01)*q_frac`.
2. Assert exact natural supports and strict `lambda_present > lambda_quasi` at
   all corners, especially `q_frac=1` while `lambda_present < 1+1e-9`.
3. Assert the inverse map round-trips interior and boundary points, using
   `p_frac=(lambda_present-0.25)/9.75` and
   `q_frac=(lambda_quasi-0.01)/(q_upper-0.01)`.
4. Reject NaN, infinity, bool, subclasses, coordinates outside `[0,1]`, natural
   rates outside support, equal/reversed rates, and values beyond the permitted
   projection tolerance.
5. Assert the exact `1e-9` gap is a config/runtime constant and is not enlarged,
   made relative, or used as a scientific support change.
6. Exercise the kink at `lambda_present=1+1e-9` from both sides. The map is
   continuous but its derivative changes when `q_upper` reaches `1`.

### Review traps

- `q_frac` is coupled to `p_frac` whenever `lambda_present < 1+1e-9`; treating
  the two rate coordinates as independent natural rates changes the objective.
- Do not clip invalid natural rates into the transform. Only profile projection
  may clip coordinate roundoff within `1e-12` of a box.
- Preserve the strict `<0.01` target-recovery boundary versus the `>=0.01`
  collision boundary; equality is a collision, not recovery.

## Halton Start Checklist

### RED tests

1. Generate positive Halton indices `1..8`, never index zero, with bases
   `2,3,5,7,11` in coordinate order
   `alpha,beta_driver,beta_quality,p_frac,q_frac`.
2. Map each radical inverse as `0.05+0.90*u`, then map the first three columns
   to their natural boxes while retaining rate fractions for columns four/five.
3. Assert all 40 values against the literal table in spec lines 231-240. Use a
   tolerance tight enough to catch a wrong index/base/map, while accounting for
   the table's displayed decimal precision.
4. Assert process-oracle starts are columns `0:3`, observation-oracle starts are
   columns `3:5`, and joint starts are all five columns from the same row IDs.
5. Generate inverse-audit starts from indices `1..16`; assert rows `1..8` are
   bit-for-bit the same internal values as the global-start generator.
6. Prove starts depend on no data, truth, scenario, split, replicate, or RNG.

### Review traps

- A quasi-random library default often starts at Halton index zero and may
  scramble by default. Either behavior violates the frozen table.
- Do not reconstruct expected tests from the production helper. Tests need an
  independent radical-inverse calculation or the literal table.

## L-BFGS-B And Fit Checklist

### RED tests

1. Capture the call and assert literal `method`, `jac`, bounds, and every option:
   `ftol=1e-12`, `gtol=1e-6`, `maxiter=1000`, `maxfun=20000`, `maxls=50`, and
   `finite_diff_rel_step=1e-5`.
2. Apply the same adapter to global, inverse-audit, and profile nuisance fits.
   No branch may silently use a different finite-difference or tolerance policy.
3. Prove the process oracle fits exactly three parameters, the observation
   oracle exactly two ordered-rate coordinates, and the joint fit all five.
4. Classify a start successful only when all are true: `result.success`,
   `status == 0`, finite objective, finite coordinate vector, valid natural
   supports, and strict rate ordering.
5. Inject, one at a time: raised objective exception, `success=False`, nonzero
   status, NaN/inf objective, NaN/inf coordinate, wrong result shape, out-of-box
   coordinate, and invalid natural transform. Each is one failed start, never a
   clipped or sentinel success, and later starts are still attempted.
6. Require at least six of eight successful starts. Sort successes by log
   likelihood descending then start index ascending.
7. Apply the best-two agreement rule exactly:
   `abs(LL1-LL2) <= 1e-6*(1+abs(LL1))`. Test equality, just below, and just above.
8. Assert deterministic selection under injected optimizer-return permutations.
9. Prove objective evaluation and fit records contain no evaluator truth fields.

### Review traps

- The literal optimizer minimizes; all convergence and tie rules are stated in
  log-likelihood space. Centralize the sign conversion.
- A finite final result does not rescue an earlier invalid/nonfinite evaluation
  if the adapter observed it. Record the start as failed.
- SciPy `nfev` accounting with `jac="3-point"` can approach `maxfun` quickly;
  tests should assert options, not brittle exact call counts.
- Catch optimizer failures at the per-start boundary. Do not catch all errors
  around the entire eight-start fit.

## Design And Noncollision Audit Checklist

### Shared SVD diagnostic

1. Require exact float64 2-D input and reject empty/nonfinite matrices.
2. Compute `s = numpy.linalg.svd(matrix, compute_uv=False)` and literal
   `tol=max(n_rows,n_columns)*eps*s_max`.
3. Set `rank=count(s>tol)` and
   `condition=s_max/s_min` only at full column rank; otherwise infinity.
4. Test explicit five-column and three-column branches. Never hard-code five in
   the generalized helper.
5. Potential/oracle/plugin matrices pass only at rank 3 and condition `<1e8`;
   canonical audit Jacobians pass only at rank 5 and condition `<1e8`.

### Stable audit vector

For each scheduled opportunity in canonical order, construct `log1p(mu)` then
`log(p0)` in two contiguous blocks. Use stable log-space quantities:

- `logS = cumulative sum(log_survival)`;
- stable `log(1-S)` (including exact `S=1` at `t0`);
- `log(p0) = logsumexp(logS-E*lambda_present,
  log(1-S)-E*lambda_quasi)`;
- a stable/vectorized mixture for `mu`, followed by `log1p`.

RED tests must catch interleaving the two metrics, sorting by string cell ID,
omitting `t0`, using retained data order, or deriving `log(p0)` from an unstable
probability-space sum.

### Scaled Jacobian and inverse search

1. Use central differences with steps `1e-5*support_width`: `8e-5`, `6e-5`,
   `4e-5`, `9.9e-6`, and `9.75e-5` in natural parameter order.
2. Scale each Jacobian column by the corresponding support width after
   differencing. Do not scale the parameter before choosing the step.
3. At A, B, and C for dense, structured, and sparse schedules, assert rank 5
   and condition `<1e8` before inverse search.
4. Define inverse objective as audit-vector RMSE. Use exactly 16 frozen starts
   and the literal optimizer adapter.
5. Count success only for normal optimizer success plus finite RMSE. Require at
   least 12/16 successes.
6. Target recovery requires both `RMSE <= 5e-5` and scaled maximum natural
   distance `<0.01`.
7. Collision requires both `RMSE <= 5e-5` and distance `>=0.01`.
8. Reproduce before any estimation all nine exact recovery counts:
   dense `16/15/2`, structured `16/14/3`, sparse `15/16/16`, ordered A/B/C.
   Assert zero collisions in every audit.
9. Cache deterministic schedule arrays and target vectors, but do not cache or
   substitute optimizer outcomes across targets/schedules.

### Literal failure fixtures

1. `equal_emission_fixture`: real dense canonical design, unrestricted
   `lambda_present=lambda_quasi=1`; process derivative columns vanish and rank
   is below 5. No ordered transform and no inverse search is allowed.
2. `deficient_design_fixture`: 32 cells, `Q=0`, nonfinite `TP`, dense times
   `0..120`, effort 1; rank is below 5.
3. `absent_state_support_fixture`: 32 cells, `t0` only, effort 1; rank is below 5.
4. Each fixture passes only by failing rank 5. A fixture must not be made to
   satisfy the canonical inverse-audit path.
5. Inject canonical rank deficiency, condition `==1e8`, fewer than 12 inverse
   successes, no recovery, and one collision. Every case stops the audit.

### Design-gate integration

- `potential_design`: unweighted analyst-visible `[1,G,Q]` over all potential
  intervals; required before every fit.
- `process_oracle_truth_at_risk`: oracle-only true at-risk rows, required only
  for the process-oracle layer, never joint acceptance.
- `joint_plugin_smoothed_at_risk`: after a finite joint MLE, normalize all 21
  path weights per cell and use
  `w_xj=sum(paths k>=j plus censoring)` on every interval. Diagnose
  `sqrt(w)*[1,G_endpoint,Q]`.
- A failed/nonfinite joint fit automatically fails the plug-in gate. Do not run
  it with fallback parameters.
- Test the indexing edge explicitly: the event-at-`j` path is included in
  at-risk weight for the start of interval `j`.

## Profile Checklist

### Conditional maps and projections

1. Target and reported interval endpoints are always natural-space values.
2. For process targets, retain the global rate transform unchanged.
3. With fixed `lambda_present=p*`, map nuisance `q_frac` using
   `min(1,p*-1e-9)` exactly.
4. With fixed `lambda_quasi=q*`, map nuisance `p_frac` from
   `max(0.25,q*+1e-9)` to `10` exactly.
5. Reject invalid fixed targets/maps. Natural-to-coordinate projection clips
   only roundoff within `1e-12`; farther values fail.
6. Deduplicate when maximum coordinate difference is `<=1e-10`, retaining the
   first source in frozen order. Test equality and both sides of the threshold.

### Adaptive point search

1. For side index `m=0,1,...`, use
   `min(distance_to_bound,0.02*support_width*1.6**m)` from the MLE.
2. Evaluate each unique natural target once. Stop producing duplicate bound
   points after clipping.
3. At each point, order nuisance starts as: projected global MLE; nearest prior
   successful point on the same side; projected frozen global starts.
4. Deduplicate in that order and attempt at most eight starts total.
5. Select by log likelihood descending then start-source order. If every start
   fails, the point fails and the side remains open.
6. Test deterministic nearest-point and tie behavior with symmetric injected
   successful points.

### Brackets, roots, and classification

1. Root value is exactly
   `2*(LLmax-LLprofile)-2.705543454095404`.
2. Only a sign-changing bracket may be passed to `scipy.optimize.brentq`.
3. Assert literal `xtol=1e-5*natural_support_width` and `maxiter=100`.
4. Brent nuisance starts use the nearest successful bracket/profile optimum as
   adjacent start, then the same deterministic projected starts and tie rules.
5. A support bound closes an interval only when it participates in a sign-
   changing bracket. Reaching a bound without a sign change is open/
   unidentified, not a bound endpoint.
6. Inject a successful profile value above `LLmax` by exactly, just below, and
   just above `1e-6*(1+abs(LLmax))`; only the last invalidates the global fit and
   stops classification.
7. Practical identification requires a finite two-sided interval, cutoff
   crossing on both sides, and MLE farther than 1% of support width from both
   bounds. Test exact 1% as not identifiable.
8. A process-oracle fit profiles only its three estimands; an observation oracle
   only its two rate estimands; joint fits profile all five. Equal-emission
   control profiles none.

## Ordered TDD Sequence

Do not combine these RED cycles. Each behavior group needs the Runbook evidence:
behavior/test IDs, pre-implementation test hash, exact RED command and expected
failure, implementation paths, exact GREEN result, and reviewer disposition.

1. **2B-01 coordinate contract**: support metadata, forward/inverse ordered-rate
   maps, invalid inputs, conditional maps, and projection/dedup boundaries.
2. **2B-02 deterministic starts**: independent radical inverse, exact eight
   rows, oracle subsets, exact 16 inverse rows, no data/truth/RNG dependence.
3. **2B-03 batched runtime kernel**: scalar/vectorized equality and immutable
   analyst/oracle batch boundaries.
4. **2B-04 optimizer adapter**: literal call/options, subset objectives, result
   validation, sorting, 6/8 and best-two rules, injected failures.
5. **2B-05 generalized diagnostics**: integrate the accepted Task 2a2 SVD/design
   helpers; five- versus three-column branches and provenance firewall.
6. **2B-06 audit vector/Jacobian**: stable canonical vector, central differences,
   column scaling, A/B/C rank and condition.
7. **2B-07 inverse audits**: 16 starts, success/recovery/collision rules, all nine
   exact counts and no collisions, run before any estimation.
8. **2B-08 failure controls**: three literal fixtures plus injected rank,
   condition, success-count, recovery, and collision failures.
9. **2B-09 profile engine**: target maps, unique stepping, start order,
   deduplication, failed/open sides, sign-changing brackets, literal Brent call.
10. **2B-10 invalidation/classification**: above-LLmax injection, MLE boundary,
    two-sided crossing, oracle subsets, and no-profile equal-emission boundary.
11. **2B-11 regression/static review**: focused latent tests and observation
    regression, format, Ruff, mypy, `git diff --check`, scope scan, hashes, and
    independent numerical/identifiability/provenance/code review.

The complete nine-audit test must execute and pass before any global estimation
test invokes the fitter. Enforce this structurally with a separate preflight
entry point/result consumed by fitting, not only pytest file order.

## Independent Review Checklist

### Numerical reviewer

- Independently regenerate the 8/16 Halton tables and conditional rate maps.
- Inspect every inequality at exact boundaries: `1e-9`, `1e-12`, `1e-10`,
  `5e-5`, `0.01`, `1e8`, 6/8, 12/16, and LL tolerances.
- Verify stable `log(p0)`, `log1p(mu)`, cloglog primitives, float64, and no
  probability-space cancellation.
- Confirm scalar/batched likelihood equality and deterministic summation.
- Reproduce all nine counts and all three rank failures independently.

### Identifiability reviewer

- Distinguish supporting local noncollision evidence from proof.
- Confirm schedule-specific audit vectors use analyst-visible count-free
  opportunities and frozen efforts.
- Verify potential, oracle-only, and plug-in design roles and provenance.
- Confirm no schedule, support, estimand, or threshold repair occurs after a
  canonical failure.
- Confirm practical profile status is not substituted for structural status.

### Provenance/firewall reviewer

- Trace every estimator input from public API to objective and profile calls.
- Prove truth-at-risk and generating parameters cannot influence starts,
  bounds, objective, audit target, profiles, gates, or sorting.
- Confirm no RNG payload, holdout index, simulation, or calibration artifact was
  materialized by Task 2b tests.
- Verify only the shared source/test files and append-only Log child changed.

### Code reviewer

- Check one optimizer/SVD/profile implementation, not parallel near-duplicates.
- Check typed immutable result records and explicit failed-state propagation.
- Check caches are keyed by all schedule/target/parameter inputs and cannot
  leak one fit or profile point into another.
- Check deterministic tie-breaking is encoded and tested, not inherited from
  incidental list/dict/process completion order.
- Check Task 2a1 regression semantics remain intact after vectorization.

## Stop Rules

Stop Task 2b and return to Barry without threshold or estimand repair if:

- Task 2a2 is not accepted or its shared-file handoff is ambiguous;
- any authority hash differs from the accepted tuple;
- the vectorized kernel disagrees with scalar enumeration/forward recursion;
- any canonical audit has rank below 5, condition at least `1e8`, fewer than
  12/16 successful searches, no target recovery, or any collision;
- any literal failure fixture reaches rank 5;
- fewer than 6/8 global starts succeed or the best two disagree;
- a profile optimum exceeds the global LL tolerance;
- truth/evaluator data enter any joint fitting surface; or
- implementation would require scenario replication, RNG construction,
  calibration, holdout, artifact, CLI, remote compute, or contract changes.

## Top Numerical Risks

1. **Optimizer-scale runtime**: the accepted scalar likelihood is analytically
   excellent but computationally explosive under 3-point finite differences,
   eight starts, inverse audits, and profiles. A tested vectorized batch kernel
   is a prerequisite, not an optional optimization.
2. **Rate-map/profile boundary errors**: the piecewise ordered transform, strict
   `1e-9` gap, conditional nuisance maps, and asymmetric `<0.01`/`>=0.01`
   frontier create several one-bit classification boundaries where generic
   clipping or independent-rate parameterization would silently change the
   estimand.
3. **Task 2a2 seam/provenance leakage**: canonical count-free schedules,
   analyst batches, three-column diagnostics, and plug-in weights are shared
   dependencies. Duplicating them in Task 2b or carrying oracle truth through a
   convenience batch would undermine both determinism and the analyst/truth
   firewall.
