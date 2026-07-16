# Goal 023 Task 3 Scientific Scenario/Gate Preflight

status: `PREFLIGHT_COMPLETE_IMPLEMENTATION_BLOCKED`
date: `2026-07-11`
worktree: `/Users/bwbrook/.codex/worktrees/spatext/goal023`
branch: `codex/spatext-goal023-latent-response-observation-gate`
HEAD/base: `53462d0365babf2c8070714a930f69b4071af276`

## Scope And Evidence Boundary

This is a read-only scientific and test-design preflight for Plan Task 3. It
derives the exact scenario, denominator, diagnostic, classification, and stop
contracts from the frozen Goal/spec plus the accepted Task 2a handoff and the
Task 2b preflight. It does not implement Task 3.

No scenario, calibration, runtime benchmark, fit, profile, predictive ensemble,
RNG payload, holdout payload, future output, artifact writer, or CLI phase was
run or inspected. The only numerical calculation performed was independent
enumeration of the three frozen central-binomial acceptance sets from their
published `n`, `p`, and `alpha` values.

Inspected authority:

| Surface | SHA-256 / state |
| --- | --- |
| Goal | `cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20` |
| Plan | `df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e` |
| Runbook | `78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed` |
| authoritative spec | `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d` |
| accepted Task 2a source | `b61a3f7186a20748dc853f9f7fce8e3a04d008594ad2b64ce0139cebe1980486` |
| accepted Task 2a tests | `921775bf7c9516d7df0749e6e61a1c315c0b1aa7e80a9c05a364f26dc31bc286` |
| Task 2b preflight | `395d6cc9960d2c0a8f9f95a92b4b0e22e070b71c8a59910926aa7fae1b97bed9` |
| current progress ledger | Task 2b pending; Task 3 pending |

The current shared source/test files contain later Task 2b work and no longer
match the accepted Task 2a hashes. That work is evidence only until Task 2b is
independently accepted. Task 3 must bind to the future accepted Task 2b source,
tests, Log parent, and handoff hashes before its first RED test.

## Frozen Common Contract

### Model and estimands

- Canonical times are `0, 6, ..., 120`; event hazards use interval endpoints;
  endpoint emissions are post-transition; `t0` is always present.
- Generating truth is
  `alpha=-6`, `beta_driver=1.25`, `beta_quality=-0.60`,
  `lambda_quasi=0.15`, and `lambda_present=4`, except where a named control or
  stress overrides the generating process.
- Natural supports and full-width imputations are:

| Parameter | Support | Full width | Max median absolute error | Max median interval width |
| --- | ---: | ---: | ---: | ---: |
| `alpha` | `[-10,-2]` | `8` | `0.40` | `2.00` |
| `beta_driver` | `[-3,3]` | `6` | `0.20` | `1.00` |
| `beta_quality` | `[-2,2]` | `4` | `0.20` | `1.00` |
| `lambda_quasi` | `[0.01,1]` | `0.99` | `0.05` | `0.30` |
| `lambda_present` | `[0.25,10]` | `9.75` | `0.40` | `1.50` |

- Every process-oracle fit estimates and profiles exactly the three process
  parameters. Every observation-oracle fit estimates and profiles exactly the
  two ordered rates. Unless explicitly exempted below, every ordered joint fit
  estimates and profiles all five parameters.
- Every fit first requires the analyst-visible three-column `potential_design`
  rank/condition gate. The process oracle additionally requires the oracle-only
  truth-at-risk gate. Every successful joint fit requires the analyst-only
  plug-in smoothed-at-risk gate. Applicable rank must be full and condition must
  be `<1e8`; failed/nonfinite joint fits fail the plug-in gate without fallback.
- Before any estimation, all nine dense/structured/sparse A/B/C noncollision
  audits must reproduce recovery counts `16/15/2`, `16/14/3`, and `15/16/16`,
  respectively, with at least `12/16` successful searches and zero collisions.

### Canonical schedules and partitions

| Schedule | Cells | Times | Effort | Opportunity count |
| --- | ---: | --- | --- | ---: |
| `process_truth` | 5,225 passable | transitions only | not applicable | no counts |
| `dense_6` | 5,225 passable | `0,6,...,120` | `1` | `109,725` |
| `structured_12` | 5,225 passable | `0,12,...,120` | structured formula | `57,475` |
| `sparse_24` | fixed 1,306-cell frame | `0,24,...,120` | `0.6` | `7,836` |

Structured effort is exactly
`0.7 + 0.6 * min(max((Q_x + 2) / 4, 0), 1)`. The sparse frame is the first
1,306 cells under the frozen truth-independent SHA-256 ranking and is invariant
across split and replicate.

Split schedules are literal:

| Scenario class | Development | Calibration | Holdout |
| --- | ---: | ---: | ---: |
| four nested scenarios (1-4) | indices `0..11` (12) | `0..23` (24) | `0..47` (48) |
| sparse, controls, stresses (5-11) | indices `0..11` (12) | none | `0..23` (24) |
| equal-emission timing-only exception | base development indices `0..23` solely for one 24-replicate timing bundle | none | not scientific evidence |

Every scientific predictive ensemble has draws `0..198` (199). The equal-
emission scientific bootstrap has bundles `0..198`, each with pseudo-replicates
`0..23`. No holdout payload is legal during Task 3 implementation or tests.

## Eleven-Scenario Matrix

The `scenario_role`, `generation_model`, `fit_model`, `schedule_id`, and
`expected_behavior` values below use the frozen artifact enum vocabulary.
Rows marked **authority gap** require contract resolution before implementation;
they are not discretionary implementation choices.

| # | Scenario | Role | Generation | Fit surface | Schedule | Reps `D/C/H` | Expected |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `process_oracle_observed_transition` | `oracle` | `exact_binary` | `process_oracle` | `process_truth` | `12/24/48` | `recover` |
| 2 | `observation_oracle_fixed_transition` | `oracle` | `exact_binary` | `observation_oracle` | `structured_12` | `12/24/48` | `recover` |
| 3 | `dense_count_exact_model` | `exact_joint` | `exact_binary` | `ordered_joint` | `dense_6` | `12/24/48` | `recover` |
| 4 | `structured_imperfect_effort` | `exact_joint` | `exact_binary` | `ordered_joint` | `structured_12` | `12/24/48` | `recover` |
| 5 | `sparse_expected_failure` | `expected_failure` | `exact_binary` | `ordered_joint` | `sparse_24` | `12/0/24` | `weaken_honestly` |
| 6 | `zero_driver_effect_negative_control` | `negative_control` | `zero_driver` | `ordered_joint` | `dense_6` | `12/0/24` | `no_false_signal` |
| 7 | `permuted_arrival_alignment_stress` | `stress` | `exact_binary` | `ordered_joint` | `structured_12` | `12/0/24` | `predictive_warning` |
| 8 | `no_emission_contrast_negative_control` | `negative_control` | `equal_emission` | `equal_emission_joint` | `dense_6` | `12/0/24` | `unidentifiable` |
| 9 | `informative_dropout_misspecification_stress` | `stress` | `informative_dropout` | `ordered_joint` | `structured_12` | `12/0/24` | `predictive_warning` |
| 10 | `goal018_continuous_abundance_stress` | `stress` | `continuous_abundance` | `ordered_joint` | `structured_12` | `12/0/24` | `predictive_warning` |
| 11 | `spatial_frailty_stress` | `stress` | `spatial_frailty` | `ordered_joint` | `structured_12` | `12/0/24` | `predictive_warning` |

### 1. Process oracle

- Generate the canonical exact binary latent process; expose true event/censor
  outcomes only to the physically separate oracle fitter.
- Fit/profile `alpha`, `beta_driver`, and `beta_quality`; no count rates enter.
- Predictive applicability: none, because there are no counts.
- Holdout denominator: 48 attempts for each of the three parameter rows.
- Gate: convergence at least `46/48`; coverage count `36..48` for each parameter;
  parameter-specific median absolute error and median interval width limits;
  full 48-attempt imputation; process-oracle truth-at-risk rank/condition pass.
- Any failure is an oracle failure and has top recommendation precedence
  `model_contract_failed`; stop Goal 023.

### 2. Observation oracle

- Generate exact binary transitions and structured counts; fix true transitions
  in the oracle likelihood.
- Fit/profile `lambda_present` and `lambda_quasi` only.
- Predictive applicability: conditional oracle-only reporting with transitions
  held fixed. It is not a standard joint predictive gate and cannot satisfy one.
- Holdout denominator: 48 attempts for each of the two rate rows.
- Gate: convergence at least `46/48`; coverage `36..48` for each rate;
  parameter-specific median error/width limits; full 48-attempt imputation.
- Any oracle-layer failure is `model_contract_failed`; stop Goal 023.

### 3. Dense exact joint

- Generate and fit the same five-parameter exact binary/count model on every
  passable cell at every six-unit time with effort one.
- Fit/profile all five estimands. Standard 199-reference predictive diagnostics
  are required on the retained dense frame.
- Holdout denominator: 48 attempts for each of five parameter rows and each of
  the 27 predictive cells.
- Gate: convergence at least `46/48`; coverage `36..48` for every parameter;
  all median error/width limits; plug-in design pass; standard predictive gate.
- After both oracle layers pass, dense failure maps to
  `process_observation_confounded` unless a higher-precedence contract failure
  has already fired.

### 4. Structured exact joint

- Generate and fit the same exact five-parameter model on every passable cell at
  `0,12,...,120` using the known structured effort.
- Fit/profile all five. Standard 199-reference predictive diagnostics are
  required on the retained structured frame.
- Holdout denominator: 48 attempts for each parameter and predictive cell.
- Gate: convergence at least `44/48`; coverage `36..48` for every parameter;
  all median error/width limits; plug-in design pass; standard predictive gate.
- If dense passes and structured precision/recovery fails while coverage remains
  calibrated and false positives are controlled, classify
  `observation_limited_but_calibrated`.
- **Authority gap:** precedence does not classify structured coverage failure,
  structured predictive failure, or a failed plug-in design after dense passes.

### 5. Sparse expected failure

- Generate the exact model, then fit all five parameters on the fixed 1,306-cell,
  six-time, effort-0.6 frame. Profiles are required to evaluate honest weakness.
- Standard predictive diagnostics are required on the retained sparse frame.
- No general five-parameter recovery claim is made. The dedicated scientific
  claim is `beta_driver` honesty.
- Holdout denominator: all 24 attempts. For `beta_driver`, coverage must be
  `18..24`; failed/nonfinite fits and open/missing intervals count as uncovered.
- For the sparse `beta_driver` median width, use all 24 widths, impute `6` for a
  nonconverged/open/missing interval, sort, and average one-based values 12 and
  13. It must be at least the structured median computed from its 48 attempts.
- A required-fit failure also fails the sparse predictive gate and cannot be
  hidden by the honest-width result.
- A passing overall recommendation requires sparse to fail honestly.
- **Authority gap:** `weaken_honestly` is not reduced to one complete Boolean.
  The packet says coverage must calibrate and width must not beat structured,
  but does not say whether unexpectedly good sparse precision is itself a gate
  failure, a scientific surprise, or a pass of the larger model gate.

### 6. Zero-driver negative control

- Generate the exact model with `beta_driver=0`; retain the normal analyst
  `TP(x)` covariate. Fit/profile all five parameters under the ordered joint
  model. Standard predictive diagnostics are required.
- Holdout denominator: 24 attempts. Count profiles whose 90% interval excludes
  zero. The exact central-binomial acceptance set is `0..6` exclusions.
- A finite two-sided interval containing zero is no false signal. An interval
  excluding zero is a false signal. Every failed required fit also fails the
  predictive scenario gate.
- **Authority gap:** unlike nested and sparse coverage, the packet does not state
  whether a nonconverged fit or open/missing `beta_driver` profile contributes
  `false` to the exclusion indicator or invalidates the false-positive gate.
  It must not be silently dropped from the 24-attempt denominator.
- A negative-control false positive maps to
  `process_observation_confounded`, subject to higher precedence.

### 7. Permuted-arrival alignment stress

- Generate positive-effect exact data with true `TP(x)` and structured effort.
  Fit both correct- and permuted-arrival ordered joint models only on the fixed
  4,180-cell fit frame; score both marginal joint likelihoods only on the fixed
  1,045-cell score frame.
- The deterministic permutation rotates complete arrival vectors, including
  nonfinite values, within row-band by quality-quintile blocks. The absolute
  finite-pair Pearson correlation must be `<=0.25` or the stress contract is
  invalid.
- The primary inferential/predictive fit is the permuted model. The correctly
  aligned fit is a heldout-score comparator only. Standard predictive references
  use the fitted permuted model on fixed score opportunities; the correct model
  is never substituted as a reference.
- Holdout denominator: 24 paired attempts. Correct alignment must have the
  better heldout score in at least `22/24`, and at least one preregistered
  predictive warning must fire for the permuted model.
- A failed/nonfinite required fit produces no paired win and fails the predictive
  gate; it remains in both attempted denominators.
- **Authority gap:** the profile artifact has no fit-variant field. The most
  coherent reading is to profile/report the primary permuted fit only and retain
  the correct fit solely for heldout score, but this is not stated literally.
  Recommendation precedence also gives no class for an alignment gate failure.

### 8. Equal-emission negative control

- Generate all 24 holdout replicates with
  `lambda_present=lambda_quasi=lambda_equal=1` on the dense schedule.
- Fit one scenario-level equal-rate submodel and one shared ordered five-
  parameter alternative by summed log likelihood over all 24 replicates.
- The equal-rate MLE is
  `clip(sum(Y)/sum(E),0.01,10)` with a direct Poisson log likelihood. The ordered
  alternative uses the frozen eight-start optimizer.
- Profiles: none, for either model. No profile-based override is permitted.
- Bootstrap: 199 independent 24-replicate equal-submodel bundles. All 199
  ordered alternative refits must succeed. Set
  `D=2*(LL_ordered-LL_equal)` and
  `p=(1+count(D_b>=D_observed))/200`; pass only when `p>=0.05`.
- Predictive applicability: references come from the fitted equal submodel and
  are diagnostic only; they cannot replace the bootstrap classification.
- Fixed statuses independent of p:

| Parameter | Structural | Practical |
| --- | --- | --- |
| `alpha` | `unidentified` | `unidentified` |
| `beta_driver` | `unidentified` | `unidentified` |
| `beta_quality` | `unidentified` | `unidentified` |
| `lambda_quasi` | `unidentified` | `unidentified` |
| `lambda_present` | `identified` | `not_applicable` |
| `lambda_equal` | `identified` | `identified` only for a finite interior MLE, else `unidentified` |

- Any failed ordered bootstrap-bundle refit or `p<0.05` fails the control and
  maps explicitly to `model_contract_failed`; structural labels do not change.
- **Authority gap:** replicate/profile schemas contain `replicate_id` but no
  scenario-level fit identifier or fit variant. The packet specifies six
  control-status rows but no literal artifact row for the two shared MLEs and
  their convergence evidence.

### 9. Informative-dropout stress

- Generate the structured exact model, then independently remove each retained
  opportunity with probability `0.10` while present and `0.45` after transition.
  Fit the remaining fixed frame as if the schedule were ignorable.
- Fit/profile all five ordered-joint parameters. Standard predictive references
  keep the realized dropout mask, schedule, and effort fixed.
- Holdout denominator: 24 attempted fits and 24 rows per parameter for
  descriptive coverage/bias; 24 attempts per predictive cell.
- `narrow wrong` occurs when any known parameter's 90% interval excludes truth
  while width is no larger than its frozen maximum. Every such case requires a
  preregistered predictive warning; otherwise classify
  `silent_misspecification_failure`, then `model_contract_failed`.
- **Authority gap:** coverage and bias must be reported but have no standalone
  acceptance bounds. A failed fit fails prediction, but its recommendation
  consequence is not mapped unless it also reaches a named higher-level stop.

### 10. Goal 018 continuous-abundance stress

- Use the structured frame and Goal 018 continuous abundance interpolation.
  Set `q=4/mean(N_xt)` over finite positive structured opportunities and generate
  `Y_xt ~ Poisson(E_xt*q*N_xt)`.
- Fit/profile the misspecified five-parameter ordered binary model. There is no
  parameter-recovery claim.
- Standard predictive diagnostics are required on the same structured frame,
  and at least one warning must fire. No parameter truth is used for recovery.
- Holdout denominator: 24 attempted fits per predictive cell. A failed fit
  remains attempted, emits unavailable diagnostics, and fails the scenario.
- Absence of the required warning is a silent misspecification failure and maps
  to `model_contract_failed`.
- **Authority gap:** recommendation precedence does not explicitly classify a
  failed/nonfinite fit or other predictive-gate failure distinct from absence of
  the mandatory warning.

### 11. Spatial-frailty stress

- Generate the structured exact model, draw a `72x84` iid standard-normal field,
  smooth with `gaussian_filter(sigma=6,mode="reflect")`, standardize over
  passable cells with `ddof=0`, and multiply observation intensity only by
  `exp(0.5*U_x-0.125)`.
- Fit/profile all five parameters under the independent-cell ordered joint
  model. Standard predictive references use the fixed observed opportunity
  frame and do not regenerate frailty.
- Holdout denominator: 24 attempted fits and descriptive coverage/bias rows per
  known parameter; 24 attempts per predictive cell.
- Apply the same parameter-specific `narrow wrong` rule as informative dropout;
  any narrow-wrong result without a warning is
  `silent_misspecification_failure` then `model_contract_failed`.
- **Authority gap:** coverage/bias has no independent pass range, and failed-fit
  recommendation handling is not fully mapped.

## Denominator And Missingness Matrix

| Gate/output | Attempted denominator | Nonconverged/nonfinite fit | Open/missing profile | Nonfinite diagnostic |
| --- | ---: | --- | --- | --- |
| nested coverage | `48` per applicable parameter | uncovered | uncovered | not applicable |
| nested absolute error | `48` | impute full support width | estimate may exist; missing estimate gets full width | reject/failed row |
| nested interval width | `48` | impute full support width | impute full support width | reject/failed row |
| nested signed error | finite converged estimates only | omitted from descriptive median, which may be null | estimate can remain descriptive | nullable |
| nested convergence | `48` | failure in numerator | no effect on fit convergence numerator | not applicable |
| sparse `beta_driver` coverage | `24` | uncovered | uncovered | uncovered |
| sparse `beta_driver` width | `24` | impute `6` | impute `6` | impute `6` if interval unavailable |
| zero-driver exclusions | `24` | **authority gap; never remove attempt** | **authority gap; never remove attempt** | not applicable |
| alignment score wins | `24` paired attempts | no win and scenario fit failure | profile does not rescue | no win |
| equal-emission bootstrap | `199` bundles | any ordered refit failure fails entire gate | no profiles | any nonfinite statistic fails |
| predictive replicate rows | full scenario attempts x 27 cells | emit unavailable row; no reference; gate fail | fit may still predict if profile alone fails, unless scenario classification requires it | empty value plus nonfinite flag and mandatory warning |
| predictive summary | full attempts per cell | `diagnostic_count < replicate_count`, increment `failed_fit_count`, warning and fail | as above | null aggregate if undefined, warning and fail |
| stress coverage/bias | `24` per known parameter | retain attempted row; exact imputation/gate is **not frozen** | retain attempted row; exact imputation/gate is **not frozen** | never emit NaN/Inf |

For all nested medians, use the ordinary even-sample median after imputation.
Maximum absolute error and maximum interval width are emitted descriptively;
the frozen parameter table sets limits only for the two medians.

Exact independently enumerated acceptance sets:

| Family | `n` | `p` | `alpha` | Inclusive accepted count |
| --- | ---: | ---: | ---: | ---: |
| 15 nested coverage rows | 48 | 0.90 | `0.05/15` | `36..48` |
| sparse `beta_driver` coverage | 24 | 0.90 | `0.05` | `18..24` |
| zero-driver exclusions | 24 | 0.10 | `0.05` | `0..6` |

The last range is an exact acceptance test under a 10% null rate; it permits an
observed exclusion fraction as high as `6/24=0.25`. Reports must not paraphrase
that result as a literal observed false-positive fraction of at most 10%.

## Predictive Gate Matrix

| Scenario | Applicability | Reference generator | Frame | Classification use |
| --- | --- | --- | --- | --- |
| process oracle | none | none | none | none |
| observation oracle | conditional diagnostic | fitted rates with fixed true transitions | structured retained frame | cannot satisfy joint gate |
| dense | standard | fitted ordered joint | dense retained frame | exact-model gate |
| structured | standard | fitted ordered joint | structured retained frame | exact-model gate |
| sparse | standard | fitted ordered joint | sparse retained frame | honest-failure evidence |
| zero driver | standard | fitted ordered joint | dense retained frame | control diagnostic plus required-fit gate |
| arrival permutation | standard | fitted permuted model | fixed score-cell opportunities | at least one warning required |
| equal emission | diagnostic | fitted equal submodel | dense retained frame | bootstrap remains decisive |
| informative dropout | standard | fitted ignorable model | fixed realized dropout frame | detects narrow-wrong bias |
| continuous abundance | standard | fitted binary model | fixed structured frame | warning mandatory |
| spatial frailty | standard | fitted independent-cell model | fixed structured frame | detects narrow-wrong bias |

Every applicable attempted replicate has exactly 27 stable cells: strata
`all,q1,q2,q3,q4,q5,early,middle,late`, each with metrics
`mean_count,zero_fraction,variance_to_mean`. A stratum with `n<2` fails. Each
successful fit uses one 199-dataset ensemble reused across all cells. References
hold opportunity membership, time, effort, and dropout fixed.

For each cell, use the exact randomized-rank PIT, exact KS test, stable Holm
adjustment across 27 cells at adjusted `p<0.01`, and Stouffer warning at
`abs(z)>3`. Zero reference SD yields residual zero only for exact observed-
reference equality; otherwise it is nonfinite and warns. MCSE is report-only.

## Recommendation Precedence Matrix

Apply the first matching class only:

1. `model_contract_failed`
   - source, schema, analytic likelihood, process oracle, observation oracle,
     holdout lock, or artifact contract fails;
   - equal-emission `p<0.05` or any ordered bootstrap refit fails;
   - any silent misspecification failure occurs;
   - numerical-domain, canonical design/noncollision, or other explicit global
     stop occurs.
2. `process_observation_confounded`
   - zero-driver negative control produces a false signal;
   - an accepted estimand is structurally or practically unidentified; or
   - dense exact joint recovery fails after both oracle layers pass.
3. `observation_limited_but_calibrated`
   - dense exact joint passes;
   - structured precision/recovery fails;
   - structured coverage remains calibrated; and
   - false positives remain controlled.
4. `latent_response_observation_gate_passed`
   - all four nested gates pass;
   - sparse weakens honestly; and
   - controls behave as specified.

Always emit
`transportability_class=scheduled_count_only_point_process_bridge_required`.

Unmapped outcomes must stop classification rather than fall through:

- structured coverage or predictive failure after dense passes;
- sparse dishonest coverage, unexpectedly narrow inference, or required-fit
  failure;
- arrival-alignment correlation, score, or warning failure;
- a stress required-fit/predictive failure that is not yet a named silent-
  misspecification event; and
- ambiguity about whether stress diagnostics are required for the top passing
  recommendation, whose text mentions controls but not all stresses.

## Task 3 TDD Matrix

### T3-01: literal scenario registry

- [ ] RED: require exactly 11 rows in canonical order and exact enum values from
  the matrix above; reject unknown, duplicate, missing, or reordered IDs.
- [ ] RED: assert exact schedule/effort mapping and exact `12/24/48` versus
  `12/0/24` split counts.
- [ ] RED: assert one explicit truth-access value per row. **Block this assertion
  until the authority maps `oracle_only`, `analyst_firewalled`, and
  `stress_evaluator_only` to all 11 scenarios.**
- [ ] GREEN must reuse accepted Task 2a schedule definitions, not duplicate
  schedule/frame logic.

### T3-02: fit dispatch and firewall

- [ ] RED: process oracle accepts only the process-oracle batch and three-
  parameter objective; observation oracle accepts only fixed-transition count
  histories and two-rate objective; ordinary scenarios accept analyst batches
  and five-parameter joint objective.
- [ ] RED: no scenario/split/replicate/generating parameter, transition truth,
  true state, dropout state, frailty field, or Goal 018 abundance enters starts,
  bounds, analyst objective, profile starts, or tie-breaking.
- [ ] RED: potential design runs before every fit; oracle truth-at-risk is
  callable only in scenario 1; plug-in design consumes only analyst posterior
  weights after a finite joint fit.
- [ ] RED: fewer than 6/8 starts, best-two disagreement, nonfinite objective,
  invalid support/order, or profile-above-LLmax invalidation propagates as a
  typed failed fit and is never converted to a sentinel estimate.

### T3-03: exact and sparse generators

- [ ] RED: scenarios 1-5 use the exact binary process with only the named
  schedule/observation differences.
- [ ] RED: process and observation RNGs consume their complete canonical arrays
  even after absorption and regardless of retained schedule.
- [ ] RED: sparse frame is exactly 1,306 truth-independent cells, fixed across
  all splits and replicates.
- [ ] RED: no holdout payload can be constructed by any Task 3 test; use injected
  deterministic arrays and temporary fixtures for behavior tests.

### T3-04: negative-control generators and decisions

- [ ] RED: zero-driver generation changes only `beta_driver` to zero and retains
  normal analyst `TP`; fit remains the unrestricted five-parameter model.
- [ ] RED: equal-emission generation uses equal rates one; shared equal and
  ordered fits sum exactly 24 replicate likelihoods.
- [ ] RED: equal MLE/support/direct Poisson LL, observed `D`, 199 bundle `D_b`,
  add-one p, all-refits-success rule, no-profile rule, and six fixed statuses.
- [ ] RED: bootstrap p cannot alter structural labels; failed bundle cannot be
  omitted; `p=0.05` passes and just below fails.
- [ ] RED: central-binomial zero-driver test yields literal bounds `0..6`, with
  boundary tests at six and seven.
- [ ] BLOCK zero-driver missing/open handling until authority resolves it.

### T3-05: misspecification generators

- [ ] RED: arrival permutation uses global quality quintiles, row-band crosses,
  cell-ID order, complete values including nonfinite, and exact cyclic shift.
- [ ] RED: correlation is finite-pair Pearson and `abs(correlation)<=0.25` is
  inclusive; just above invalidates before scientific classification.
- [ ] RED: alignment fit/score frames are disjoint 4,180/1,045 partitions; no
  score cell enters either fit; correct wins count uses all 24 attempts.
- [ ] RED: dropout uses one full structured-opportunity uniform vector and exact
  probabilities `0.10/0.45` before filtering.
- [ ] RED: continuous abundance uses the exact finite-positive opportunity mean
  in `q`, one Poisson model, and no binary parameter truth in recovery gates.
- [ ] RED: frailty consumes one full `72x84` field, exact Gaussian filter,
  passable-cell `ddof=0` standardization, and intensity multiplier only.
- [ ] RED: predictive references freeze realized frame/mask/effort and do not
  regenerate dropout or observational frailty.

### T3-06: profiles and recovery rows

- [ ] RED: profile subsets are 3/2/5 parameters for process oracle, observation
  oracle, and ordinary joint fits; equal emission emits no profile points.
- [ ] RED: nested `replicate_recovery` has exactly 15 parameter families per
  replicate across scenarios 1-4 (`3+2+5+5`).
- [ ] RED: nonconverged/nonfinite/open/missing nested results preserve all rows
  and apply exact coverage/error/width rules.
- [ ] RED: sparse beta rows apply 24-attempt coverage and width imputation.
- [ ] BLOCK alignment profile rows and shared equal-fit result rows until their
  artifact identity/multiplicity is frozen.

### T3-07: gate arithmetic

- [ ] RED: independently enumerate exact central-binomial sets and assert
  nested `36..48`, sparse `18..24`, and zero-driver `0..6`.
- [ ] RED: nested convergence minima are `46/48`, `46/48`, `46/48`, and
  `44/48` in scenario order.
- [ ] RED: impute supports `8,6,4,0.99,9.75`; assert ordinary even-sample median
  after imputation and nullable finite-only median signed error.
- [ ] RED: parameter thresholds apply to median absolute error and median
  interval width, not the emitted maxima.
- [ ] RED: sparse median is the mean of ordered positions 12 and 13 and compares
  against the structured 48-attempt imputed median.
- [ ] RED: alignment wins at `22/24` and fails at `21/24`; warning count at least
  one; equal p at `0.05` passes.

### T3-08: predictive diagnostics

- [ ] RED: exact scenario applicability and reference model from the predictive
  matrix; process oracle emits none; observation oracle is conditional only.
- [ ] RED: exactly 27 rows per attempted replicate in frozen stratum/metric
  order; exact metric formulas including `ddof=1`, all-zero variance ratio, and
  `n<2` failure.
- [ ] RED: one 199-reference ensemble is reused across all 27 cells; exact PIT
  consumes 27 uniforms in frozen order.
- [ ] RED: exact KS, stable Holm tie key, adjusted-p formula, Stouffer finite-only
  pooling, nonfinite warning, and no MCSE threshold.
- [ ] RED: failed/nonfinite fit emits all unavailable replicate rows, creates no
  references, remains in summary denominator, increments failed-fit count, and
  forces warning/fail.
- [ ] RED: NaN/Inf is serialized only through nullable field plus explicit flag.
- [ ] RED: continuous abundance must warn; narrow-wrong dropout/frailty without
  warning sets the silent-failure flag.

### T3-09: recommendation state machine

- [ ] RED: encode ranks 1-4 and prove higher precedence wins under simultaneous
  conditions, especially equal-emission failure over generic negative-control
  wording.
- [ ] RED: every possible named gate-result vector maps to exactly one terminal
  recommendation or an explicit `classification_blocked_unmapped_outcome` stop.
- [ ] RED: no false default to the passing class; all unmapped authority gaps
  stop until the frozen contract is amended.
- [ ] RED: transportability class is always the scheduled-count-only bridge
  requirement regardless of recommendation.

### T3-10: artifacts and schemas

- [ ] RED: exact file manifest, exact CSV headers/types/nullability/primary keys,
  canonical ordering, sorted-key JSON, UTF-8/LF, no NaN/Inf, and deterministic
  repeated-byte output.
- [ ] RED: `scenario_definitions.csv` contains exactly 11 rows and no inferred
  or duplicate scenario.
- [ ] RED: failed fits still produce attempted recovery/predictive rows.
- [ ] RED: equal-emission produces one scenario summary plus six fixed parameter
  status rows; bootstrap refit failures are visible.
- [ ] RED: required visuals decode their own labels and source rows.
- [ ] BLOCK `latent_time_calibration.csv` and its visual until metric formulas,
  applicability, expected values, and gate thresholds are frozen.

### T3-11: phase, seed, and runtime separation

- [ ] RED: benchmark, calibration, holdout, verify, freeze, and tracked-state
  checks are distinct dispatches; unknown phase fails before RNG construction.
- [ ] RED: Task 3 tests may validate phase refusal and payload schemas using
  fakes, but may not instantiate any holdout payload or scientific calibration
  row.
- [ ] RED: exact scenario/split/component/draw partitions are disjoint and every
  out-of-range combination fails before `SeedSequence`/RNG construction.
- [ ] RED: runtime projection expands exact task counts, includes 199 equal
  bootstrap refits, applies deterministic eight-worker LPT and factor `1.20`,
  and asserts no holdout payload/scientific rows.
- [ ] BLOCK any literal `--phase calibration` smoke execution in Task 3. Plan
  Task 3 step 6 conflicts with Task 4 ownership of calibration and with the
  present no-calibration instruction; use injected CLI tests until resolved.

### T3-12: review and provenance

- [ ] Bind Task 3 RED evidence to accepted Task 2b source/test/Log hashes.
- [ ] Require scientific review of every scenario row and gate denominator;
  statistical review of binomial/PIT/Holm/Stouffer/bootstrap logic; provenance
  review of analyst/truth boundaries; code review of deterministic dispatch;
  artifact review of exact schemas; and final independent staged-diff review.
- [ ] Any Critical or Important finding returns to RED before calibration.
- [ ] No Task 3 result authorizes calibration freeze or holdout exposure.

## Contradictions And High-Risk Ambiguities

### Critical: latent-response gate is not specified

`latent_time_calibration.csv`, three transition metrics, per-row `gate_result`,
and `visuals/latent_time_calibration.svg` are required, but the authority gives
no metric formulas, applicability by scenario, expected values, aggregation,
missing/nonconverged treatment, or acceptance thresholds. An implementation
cannot truthfully claim a latent-response recovery gate from the current packet.

Resolution required: freeze exact censoring-aware definitions, scenario/split
applicability, denominators, imputation/null rules, thresholds, and relation to
the four nested gates before Task 3 writes those outputs.

### Critical: recommendation precedence is not total

Several named scenario failures have no terminal class: structured coverage or
predictive failure after dense success, dishonest sparse behavior, arrival-
alignment gate failure, and non-silent required-fit failures in stresses. The
passing clause also says controls must behave but does not explicitly require
all stress gates. Defaulting unmatched cases to pass would be scientifically
unsafe.

Resolution required: add a complete truth table or explicit catch-all class for
every named gate and state whether every stress is required for the top pass.

### Critical: multi-fit scenario evidence does not fit the schemas

Arrival alignment has correct and permuted fits but recovery/profile schemas
have no `fit_variant`. Equal emission has two shared scenario-level fits but the
same schemas require `replicate_id` and provide no shared-fit record. This risks
profiling the wrong alignment, treating comparator output as primary inference,
or losing convergence evidence behind the equal-emission p-value.

Resolution required: freeze primary/comparator profile policy and add a fit-
variant/shared-fit artifact identity, or explicitly prohibit those rows and
define a complete replacement evidence schema.

### Important: zero-driver attrition handling is incomplete

The 24-attempt denominator is fixed, but failed/nonfinite fits and open/missing
profiles are not assigned an exclusion indicator. Counting them as non-
exclusions can make an unstable fitter appear conservative; dropping them
violates the denominator contract.

Resolution required: define the false-signal indicator and separate fit-
availability gate for every attempted row.

### Important: stress coverage is descriptive but gate wording is broader

Informative dropout and spatial frailty must report coverage/bias, but only the
`narrow wrong` plus no-warning combination has an acceptance consequence. There
is no treatment for broad wrong intervals, severe bias with coverage, or missing
profiles beyond generic predictive fit failure.

Resolution required: state explicitly that these are descriptive except for
the silent-failure rule, or freeze additional stress thresholds.

### Important: Task 3 calibration-smoke boundary conflicts with Task 4

Plan Task 3 step 6 asks for a CLI calibration smoke, while Task 4 owns runtime
benchmarking and full calibration and the current task forbids calibration.
Early scientific calibration output could weaken the frozen pre-holdout
separation even without constructing holdout.

Resolution required: make Task 3 calibration tests fixture-only, or define a
non-scientific no-row smoke phase distinct from `--phase calibration`.

### Important: truth-access enum mapping is absent

The schema freezes `oracle_only|analyst_firewalled|stress_evaluator_only` but
does not map those values to the 11 rows. This is provenance-sensitive for
negative controls and stress scoring.

Resolution required: add the literal 11-row mapping to authority and test it.

## Stop Rules

Stop before Task 3 implementation if:

- Task 2b lacks hash-specific independent acceptance and an explicit shared-file
  handoff;
- Goal/spec/Plan/Runbook or accepted parent hashes differ;
- any of the three Critical authority gaps above remains unresolved;
- canonical nine-audit, optimizer, profile, vectorized/scalar equality, or
  analyst/truth firewall evidence is not accepted;
- implementation requires changing a frozen model, estimand, schedule, support,
  threshold, seed partition, denominator, or recommendation to make a test pass.

Stop Task 3 execution immediately if:

- any test constructs a holdout payload or reads a future holdout output;
- any scenario test emits scientific calibration rows rather than temporary
  deterministic fixtures;
- an unknown/missing/out-of-range scenario, split, component, replicate, or draw
  reaches RNG construction;
- oracle/evaluator truth enters analyst starts, bounds, objectives, profiles,
  diagnostics, sorting, or recommendation logic;
- a failed/nonfinite fit or missing profile is dropped from an attempted
  denominator;
- any predictive reference changes the retained frame, effort, or dropout mask;
- NaN/Inf, duplicate keys, unstable sorting, or an unregistered artifact is
  emitted;
- a named gate outcome has no frozen recommendation mapping;
- a numerical-domain, canonical design/noncollision, oracle, negative-control,
  silent-misspecification, or provenance gate fails; or
- completing the task would require full spread fitting, real data, remote
  compute, case-study exposure/zero fields, or a new biological assumption.

After Task 3 implementation, stop before calibration unless all focused/full
validation and independent scientific, statistical, code, artifact,
documentation, provenance, and final review gates are clean. Do not proceed to
Goal 024.
