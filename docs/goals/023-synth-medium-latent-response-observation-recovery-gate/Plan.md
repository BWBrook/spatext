# Goal 023 Implementation Plan

## Execution Model

One primary implementation worker writes sequentially across overlapping Goal
023 source/test files. Scientific, provenance, code, artifact, and final
reviewers are read-only. A different writer may take over only after an
explicit handoff and live status/diff review. Reviewers never repair their own
findings.

Every new behavior follows red-green TDD. `Log.md` records behavior/test IDs,
exact red command, test-file hash, failing assertion and exit status,
implementation paths, exact green command/output, and reviewer disposition.

## Task 0: Freeze The Authoritative Contract

Write scope:

- `spec/synth_medium_latent_response_observation_recovery_gate.md`
- Goal 023 `source_digest_receipt.json`
- Goal 023 `Log.md`

Steps:

1. Transcribe the exact equations, parameters, scenarios, analyst/truth
   firewall, estimator, profiles, seed partitions, gates, recommendation
   precedence, schemas, and boundaries from `Goal.md` into the authoritative
   spec without changing scientific content.
2. Add an algebraic/rank-based structural-identifiability argument for the
   process oracle, observation oracle, and exact joint likelihood, including
   emission ordering, right censoring, and the independent-cell assumption.
3. Add a separate practical-identifiability design audit for `G_xt` versus
   `Q_x`. Rank deficiency or condition number at least `1e8` stops execution
   and returns the packet for Barry-approved revision; it does not permit an
   estimand to be dropped during execution.
4. Compute the canonical source digests twice with independent implementations,
   reconcile them, and write the reviewed immutable source digest receipt.
5. Have independent scientific and executor-readiness reviewers approve the
   spec and receipt.
6. Record `shasum -a 256` for the approved spec and receipt in `Log.md`. No simulator,
   fitter, calibration, or holdout work may begin before this hash is frozen.

Deliverable: reviewed, hashed design authority with no unresolved ambiguity.

## Pre-Simulation Contract Amendment Gate

The original spec hash
`265a6144cc0575b7ff7b89bc1bfba4f603484aaac62352f95024d1d06c1f08dc`
is `superseded_pre_simulation`. Before any Task 2 work:

1. Amend Goal, authoritative spec, Plan, and Runbook with the exact timing,
   likelihood, design-diagnostic, computational-domain, identifiability,
   transform, start, optimizer, profile, and seed contracts.
2. Record and seal all four replacement document hashes while proving the
   source digest receipt remains
   `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`.
3. Repeat absence checks proving no Task 2 files, simulation, seed namespace,
   calibration, Goal 023 artifact, preholdout receipt, or holdout exposure.
4. Complete the Task 1 terminology/API red-green polish and verify frozen
   efforts and rate supports stay well inside the computational domain.
5. Obtain fresh Task 1 independent re-review plus independent
   scientific-identifiability, executor-readiness, and provenance/freeze
   `ACCEPT` decisions with no Critical or Important finding.

Task 2 remains stopped until every item passes. Task 1 subsequently received
hash-specific `ACCEPT`; scientific-identifiability, executor-readiness, and
provenance/freeze document reviews remain hash-dependent. No calibration or
holdout work is permitted.

## Amendment Iteration 2 Closure Gate

The amendment-1 Goal, Plan, Runbook, and spec hashes are
`reviewed_not_accepted_pre_simulation`. Iteration 2 must close every Important
review finding before Task 2:

1. Freeze the literal audit vector, SVD, inverse-search, collision, and three
   failing-fixture contracts.
2. Separate analyst potential, oracle-only truth-at-risk, and analyst plug-in
   design gates and prohibit truth-at-risk from joint acceptance.
3. Freeze `float64`, `ddof=0`, stable hazard/log-survival primitives, and
   `scipy.special.logsumexp` tests.
4. Freeze literal optimizer calls, conditional profile rate maps, projection,
   deduplication, sorting, stepping, bracket, and invalidation mechanics.
5. Freeze canonical cell/opportunity order, RNG array shapes and full
   consumption, sparse/alignment frames, schedules, quintiles, permutation,
   PIT, predictive, and bootstrap mapping without instantiating holdout.
6. Freeze attempted-replicate denominators, imputation rules, exact central
   binomial sets, equal-emission refitting, PIT/Holm/Stouffer warnings, and
   replicate/summary predictive schemas.
7. Freeze the eight-worker runtime benchmark/projection/calibration stop gate.
8. Record replacement hashes and repeat Task 1, scientific-identifiability,
   executor-readiness, and provenance/freeze reviews. The amendment-1
   provenance `ACCEPT` is non-transferable and must be repeated. Task 1 later
   received hash-specific `ACCEPT` for its unchanged source/test hashes.

Scientific-identifiability, executor-readiness, and provenance/freeze reviews
for each replacement document tuple remain `PENDING` until recorded as
`ACCEPT` with no Critical or Important finding. Task 2, calibration, artifacts,
seeds, and holdout remain stopped.

## Narrow Orchestrator Contract Correction Gate

Before amendment iteration 2 is resubmitted for review:

1. Generalize the SVD convention to `n_columns`, then require rank `5` for the
   five-column noncollision Jacobian and rank `3` for each three-column
   potential, oracle, and plug-in design diagnostic.
2. Freeze sparse `beta_driver` honest coverage over all 24 attempted holdout
   replicates, with failed/open/missing intervals counted false and the exact
   dedicated `Binomial(24, 0.90)` acceptance set at `alpha = 0.05`.
3. Make every failed or nonfinite fit fail its scenario gate, prevent
   predictive diagnostics, and remain explicit in attempted predictive
   denominators and literal schemas.
4. Reseal Goal, spec, Plan, Runbook, and Log hashes; prove the source receipt
   and no-exposure boundaries remain unchanged; retain every fresh review as
   `PENDING`.

This correction is documents only. It does not authorize Task 2, artifacts,
seed construction, calibration, or holdout exposure.

## Final Contract Review-Fix Gate

Before final document re-review and any Task 2 work:

1. Use `RMSE <= 5e-5` with scaled distance `< 0.01` for target recovery and
   distance `>= 0.01` for collision. Before estimation, reproduce all nine dry
   audits and exact recovery counts: dense `16/15/2`, structured `16/14/3`,
   sparse `15/16/16`, with no collision. This is the unique passing pair in the
   frozen tolerance frontier and remains supporting evidence only.
2. Separate equal-emission structural labels from bootstrap p. Preserve
   structural identification of the `lambda_present` baseline and
   `lambda_equal`, mark the ordered contrast and four specified latent/process
   parameters unidentified, use `not_applicable` for the unprofiled
   `lambda_present` practical status, and retain p/all-refits only as the
   control gate.
3. Freeze every zero-based scenario/split/replicate/draw range and reject
   unknown or out-of-range combinations before RNG construction.
4. Freeze predictive applicability, retained opportunity frames, the permuted
   primary reference, exact count metrics, `n < 2` failure, and required-fit
   failure propagation without substitute ensembles or denominator reduction.
5. Freeze sparse `beta_driver` median width over all 24 attempts with width `6`
   imputation and the ordinary even-sample median, compared with the frozen
   structured 48-attempt median.
6. Replace component-level runtime projection with complete measured task
   units, exact repeated-duration lists, deterministic eight-worker LPT, and
   the literal `runtime_projection.json` audit contract.
7. Preserve Task 1 `ACCEPT` only for its unchanged source/test hashes. Treat
   prior scientific and provenance `ACCEPT` decisions as hash-specific and
   non-transferable; set scientific-identifiability, executor-readiness, and
   provenance/freeze re-reviews to `PENDING` for replacement document hashes.

Task 2 remains stopped until all three document re-reviews return `ACCEPT`
with no Critical or Important finding. This gate creates no source, tests,
artifacts, seed payloads, calibration, or holdout material.

## Task 1: Probability And Observation Kernel

Write scope:

- `tests/test_observe.py`
- `src/spatext/observe.py`
- `pyproject.toml`
- `uv.lock`
- Goal 023 `Log.md`

Steps:

1. Write and run failing tests for Poisson log probability, effort scaling,
   effective-rate ordering, zero counts, invalid parameters, and stable
   boundaries.
2. Add the bounded SciPy dependency and implement the smallest typed, pure
   observation kernel that passes. It must not import synth-medium code.
3. Rerun focused tests, formatting, lint, mypy, and dependency-lock checks.
4. Add a fresh red-green terminology/API cycle distinguishing
   `numerical_domain_failure` from scientific likelihood outcomes and prove
   frozen effort/rate combinations remain comfortably below the
   `1_000_000_000` computational mean limit without changing the unbounded
   Poisson statistical support.
5. Obtain fresh independent spec-compliance and numerical-quality re-review.
   Resolve all critical and important findings through a new red-green cycle.

Deliverable: reusable effective-count likelihood, independent of benchmark
policy.

## Task 2a: Latent Transition, Simulation, And Exact Likelihood

Write scope:

- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- Goal 023 `Log.md`

Steps:

1. Write failing analytic tests for the exact endpoint timing convention,
   cloglog hazard, no-driver null, pre-arrival/background risk, absorbing
   transition, right censoring, transition-time probability normalisation,
   `float64` arrays, population-standardised `Q`, support-extreme stable
   process primitives, and actual canonical `Q` range.
2. Add one-, two-, and 20-interval tests proving direct enumeration, an
   independent forward recursion, and brute-force tiny-history calculation are
   equal, including no observations, zero counts, irregular retained
   opportunities, baseline-present and post-transition emissions, and
   coarsened schedules.
3. Implement typed frozen parameter/support, analyst-observation, and separate
   truth/evaluator contracts. Add firewall tests proving truth-at-risk rows and
   forbidden truth fields cannot enter or alter the analyst joint likelihood.
4. Implement deterministic component-separated seeded process/count
   simulation, transition event/censoring probabilities, process-oracle
   survival likelihood, fixed-transition observation-oracle likelihood, and
   analyst-only joint `scipy.special.logsumexp` likelihood. Test canonical
   order, exact RNG shapes, full consumption after absorption, and integer
   product numerical-domain failure.
5. Test `potential_design`, `process_oracle_truth_at_risk`, and
   `joint_plugin_smoothed_at_risk` provenance labels and plug-in weights. Prove
   truth-at-risk values do not enter joint starts, bounds, objective, profiles,
   or gates.
6. Test invalid schemas, times, efforts, counts, parameters, RNG payload keys,
   exact zero-based scenario/split/replicate/draw ranges, rejection of every
   unknown or out-of-range combination before RNG construction, the two frozen
   non-holdout RNG vectors, canonical schedules, sparse frame, quality
   quintiles, arrival permutation, and alignment frame. Instantiate no holdout
   payload.
7. Run focused/static/regression checks and obtain independent likelihood,
   firewall, provenance, and code review.

Deliverable: analytically tested simulator and exact nested oracle/joint
likelihood, with no optimiser or profile implementation.

## Task 2b: Identifiability Diagnostics, Optimizer, And Profiles

Write scope:

- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- Goal 023 `Log.md`

Steps:

1. Write failing tests for the ordered natural-rate transform, strict
   computational gap, exact eight Halton starts and oracle subsets, optimizer
   literal call/options, convergence classification, deterministic sorting,
   and injected failed/nonfinite starts.
2. Write failing tests for potential/oracle/plugin design gates and the
   dense/structured/sparse numerical noncollision audit at frozen points A, B,
   and C, including canonical `log1p(mu)|log(p0)` vectors, the generalized
   float64 `n_columns` SVD tolerance, explicit five-column audit and
   three-column design rank branches, Jacobian scaling, exactly 16 inverse
   starts, both `RMSE <= 5e-5` recovery/collision rules with the `0.01` distance
   frontier, all nine exact dry-audit recovery counts and no-collision result,
   and the three literal rank-failing controls. The complete nine-audit test
   runs before estimation.
3. Implement bounded L-BFGS-B fitting with the frozen finite-difference
   settings and no truth/data-dependent starts.
4. Write failing tests for natural-space adaptive profiles, nuisance-start
   conditional rate maps, projection tolerance, ordering/deduplication,
   unique-point stepping, open sides, sign-changing brackets, Brent start/tie
   rules, and injected global-fit invalidation when a profile exceeds `LLmax`
   tolerance.
5. Implement the frozen profile procedure and practical-identifiability
   classification without changing supports, estimands, schedules, or gates.
6. Run focused/static/regression checks and obtain independent numerical,
   identifiability, provenance, and code review.

Deliverable: reviewed fitting and profile layer. No scenario replication,
calibration, holdout, artifact, CLI, or documentation-export work begins.

## Integrated Pre-Task-3 Contract Amendment Gate

This integrated pre-Task-3 amendment changes no Goal 023 biological or
statistical model equation, estimand, natural support, generating value,
transition or emission timing convention, optimizer/profile rule, scenario ID,
schedule, effort rule, replicate count, predictive-reference count, bootstrap
count, seed payload or substream mapping, existing numerical recovery/coverage/
predictive threshold, transportability statement, or publication authority.

Before the first Task 3 RED test:

1. Accept the Task 2b source/test/Log handoff against exact hashes.
2. Append the parent-bound
   `holdout_provenance_binding_interpretation_v1_disposition` record with status
   `superseded_pending_amendment`, preserving all prior Log bytes.
3. Amend Goal, authoritative spec, Plan, and Runbook in one coordinated patch
   with the literal scenario registry, diagnostic-only latent formulas, total
   recommendation reducer, fit/shared evidence schemas, 22-file nonrecursive
   artifact contract, fixture-only Task 3 dispatch, and complete provenance
   contract.
4. Add RED-GREEN executable tests using temporary non-holdout fixtures only.
5. Run the complete non-generative pre-Task-3 validation ladder and reseal the
   four document hashes plus source/test hashes.
6. Append a parent-bound integrated-amendment record containing only live
   hashes and exact review dispositions.
7. Obtain fresh scientific, statistical, executor-readiness, artifact/schema,
   code, and provenance/freeze `ACCEPT` decisions with no Critical or Important
   finding.

No live runtime benchmark, scientific calibration row, Goal 023 RNG object or
payload, holdout payload, artifact bundle, preholdout receipt, or holdout
receipt is permitted in this gate.

## Task 3: Pre-Holdout Scenarios, Artifacts, And Documentation

Write scope:

- `spec/synth_medium_latent_response_observation_recovery_gate.md`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `scripts/run_synth_medium_latent_response_observation_recovery.py`
- `src/spatext/synth/medium/__init__.py`
- `AGENTS.md`
- `README.md`
- `spec/report_log.md`
- Goal 023 `Log.md`

Steps:

1. Write RED tests for the literal 11-row truth-access/fit-variant registry,
   exact schedules and existing gates, full attempted denominators and
   missingness, fit-execution evidence, shared equal-emission recomputation,
   descriptive stress rows, diagnostic-only latent formulas, total four-class
   reducer, exact 22-file schemas, two-level artifact hashes, typed config/
   receipt identities, fixture-only phase dispatch, and complete provenance
   guards.
2. Implement all eleven scenarios and typed fit evidence. Keep the arrival
   correct fit comparator-only; keep equal-emission shared fits free of fake
   replicate IDs; reconcile every primary science row to one fit row.
3. Implement the three proper/interpretable latent diagnostics exactly, with
   fixed frames, censoring, expected values, nullable availability, and no
   threshold or recommendation input.
4. Implement existing recovery, predictive, control, stress, and total
   recommendation gates without changing any existing numeric threshold.
5. Implement deterministic 22-file writers, disk-first verification, the
   represented 21-file verification manifest, complete external 22-file
   snapshot, unambiguous self/file hash identities, reports, and self-decoding
   visuals.
6. Implement phase, receipt, identity/footprint, per-command envelope, Log
   append, mutation, nonmutating-nonzero, and one-retry guards using injected
   runners and RNG factories.
7. Run focused/full tests, static checks, fixture-only CLI dispatch smoke,
   artifact schema/visual fixture checks, and the full non-generative
   validation ladder. The Task 3 smoke injects deterministic fixture task
   results and writers under `tmp_path`; it may exercise parser, dispatch,
   worker/output forwarding, summary, and exit behavior, but must not call the
   live calibration runner, instantiate any Goal 023 RNG object or payload,
   emit a scientific row, write the canonical artifact directory, or run a
   production `--phase calibration` subprocess. Task 4 owns the first live
   runtime benchmark and calibration execution.
8. Obtain independent scientific, statistical, code, artifact/schema,
   documentation/visual, executor-readiness, and provenance/freeze review.
   Resolve every Critical or Important finding before Task 4.

Deliverable: reviewed pre-holdout implementation contract. Task 4 owns the
first live benchmark and calibration.

## Task 4: Calibration And Immutable Freeze

Write scope:

- generated ignored calibration artifacts;
- Goal 023 `preholdout_state_receipt.json`;
- Goal 023 `Log.md` for append-only provenance records, including amendment
  supersession, reviewed hashes, freeze evidence, and immutable dispositions;
  no Log record may change science or analytical bytes.

Steps:

1. Run the development/calibration-only eight-worker runtime benchmark using
   nested calibration replicate `0`, non-equal development replicate `0`, and
   the timing-only equal-emission development 24-replicate bundle plus
   development bootstrap bundle `0`. Emit no scientific row or holdout payload.
2. Time one complete unit per scenario and one complete equal-bootstrap refit;
   expand exact calibration/holdout task-duration lists, including 199 equal
   holdout bootstrap copies, and project deterministic eight-worker LPT with
   safety factor `1.20`. Emit and inspect `runtime_projection.json`; stop unless
   both projected makespans are at most `1500` seconds.
3. Run full calibration within 30 minutes without materialising holdout rows;
   equivalently at most `1800` seconds. Otherwise stop and return to Barry
   without reducing evidence, changing thresholds, using remote compute, or
   exposing holdout.
4. Before emitting the candidate config, assert pinned branch/HEAD/base, exact
   analytical manifest, exact phase-specific candidate footprint, and absence of
   every out-of-allowlist untracked non-ignored or other out-of-footprint path.
   Fail without writing config.
5. Emit and inspect frozen config, source provenance, schemas, calibration
   tables, and visuals. Embed the reproduced analytical digest before computing
   and approving `config_sha256` and `config_file_sha256`.
6. Have independent scientific, statistical, provenance, validation, artifact,
   and contrarian reviewers inspect calibration behavior, candidate bytes,
   identity, footprint, and frozen hashes.
7. Record approved config/source/spec and candidate hashes in append-only Log.
8. Rerun the complete pre-holdout validation ladder. Any analytical mutation
   returns to config emission and fresh review. No analytical/test/spec/CLI/
   threshold/documentation change is permitted after freeze.
9. Immediately before `freeze-tracked-state`, repeat identity, manifest,
   status, and footprint guards. Reproduce, never patch, config digest;
   atomically create the immutable preholdout receipt; verify config bytes and
   disk manifests remain exact.

Deliverable: reviewed immutable config and untouched holdout namespace.

## Task 5: Single Holdout Execution And Read-Only Review

Write scope:

- generated ignored holdout artifacts during the one authorized execution;
- machine-created tracked immutable `holdout_receipt.json`; and
- append-only provenance records at the end of Goal 023 `Log.md`, written by
  one designated writer from independently approved exact bytes.

No other tracked working-tree write is permitted after exposure.

Steps:

1. Immediately before exclusive receipt creation, assert pinned
   branch/HEAD/base, exact analytical manifest/digest, exact phase-specific
   candidate footprint, no out-of-allowlist untracked non-ignored path, frozen
   config, and preholdout receipt. Fail before receipt creation on mismatch.
2. Atomically create the immutable holdout receipt. Immediately repeat all
   checks plus receipt self/file hashes before constructing any RNG object or
   payload. A failure burns the namespace, creates no RNG, and records
   `STOP_INVALIDATED_POST_EXPOSURE`.
3. Execute holdout once, emit the exact 22-file bundle, and freeze represented
   and complete artifact-set hashes. Never retry holdout or any artifact-
   generating command.
4. Run every later command in its own complete immutable-byte envelope. Apply
   zero, mutation, and nonmutating-nonzero dispositions plus the single
   independently approved retry exactly as Goal/spec define.
5. Obtain independent read-only scientific, contrarian, provenance, code, and
   artifact review. Append only approved exact provenance payloads.
6. A required analytical change records `STOP_INVALIDATED_POST_EXPOSURE` and
   stops for Barry's fresh-namespace approval. A terminal nonmutating
   validation failure stops publication but does not itself invalidate the
   scientific result or authorize a fresh namespace.

## Task 6: Final Review, Staging, And Publication

1. Run only Runbook section 7 post-holdout commands. Wrap each command in its
   complete envelope; never dispatch section 4.
2. Resolve every nonzero through the provenance disposition and one-retry rule.
3. Stage the exact 19-path allowlist. Reject every extra staged, tracked,
   unstaged, or out-of-allowlist untracked non-ignored path and confirm generated
   outputs are ignored.
4. Dispatch a fresh final reviewer against the cached candidate, complete
   envelope, validation output, and exact proposed terminal Log payload. Append
   only approved bytes and rerun every guard before commit.
5. Mutation or required analytical change records
   `STOP_INVALIDATED_POST_EXPOSURE`. A terminal unchanged nonzero records
   `STOP_NONMUTATING_VALIDATION_FAILURE`. Otherwise commit, fast-forward
   canonical `main`, push, and prove post-push equality.
6. Do not start Goal 024.
