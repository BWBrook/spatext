# Goal 023 Integrated Pre-Task-3 Contract Amendment Proposal

date: `2026-07-11`
status: `PATCH_READY_DEFERRED_UNTIL_TASK_2B_HANDOFF`
tracked_files_edited_by_this_proposal: `none`
holdout_authorized: `false`
calibration_authorized: `false`

## 1. Purpose And Authority Boundary

This proposal integrates every contract correction that must be sealed before
the first Task 3 RED test. It is the single patch authority for the corrections
previously developed in:

- `.superpowers/sdd/holdout-provenance-amendment-proposal.md`;
- `.superpowers/sdd/task-3-scenario-gate-preflight.md`;
- `.superpowers/sdd/task-3-latent-metric-proposal.md`;
- `.superpowers/sdd/task-3-decision-logic-proposal.md`;
- `.superpowers/sdd/task-3-schema-proposal.md`; and
- `.superpowers/sdd/task-3-artifact-cli-preflight.md`.

The tracked authority inspected for this proposal is:

```text
branch   codex/spatext-goal023-latent-response-observation-gate
HEAD     53462d0365babf2c8070714a930f69b4071af276
base     origin/main = 53462d0365babf2c8070714a930f69b4071af276
Goal     cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20
Plan     df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e
Runbook  78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed
spec     0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d
receipt  5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb
```

Task 2b owns the moving shared source, test, and `Log.md` parent. Therefore:

1. this proposal edits no tracked file and appends no live Log record;
2. the patch described here may be applied only after Task 2b has an accepted,
   hash-specific source/test/Log handoff;
3. every replacement document hash and Log parent must be computed from that
   accepted live state; and
4. Task 3, live runtime benchmarking, calibration, config emission, freeze,
   holdout, staging, commit, and publication remain blocked.

## 2. Integrated Decisions

The amendment shall encode these decisions exactly.

1. Keep all frozen model equations, estimands, supports, generating truth,
   optimizer/profile rules, scenario IDs, schedules, replication counts, seed
   mapping, current recovery/coverage/predictive thresholds, transportability
   statement, and publication authority unchanged.
2. Adopt the ordered 21-category latent-transition formulas, applicability,
   fixed frames, denominators, and missingness rules from the latent-metric
   proposal. The metrics are descriptive diagnostics only. They have no
   quantitative pass threshold, cannot alter any scenario reducer, and cannot
   alter the final recommendation. Every applicable row has
   `gate_result=diagnostic`; every inapplicable row has
   `gate_result=not_applicable`.
3. Preserve exactly the four existing recommendation classes. Use the total,
   fail-closed reducer in section 7. Every named control and stress is required
   for the top pass. Structured fit availability, convergence, coverage,
   predictive, and plug-in-design failures are `model_contract_failed`.
   Sparse-honesty contract failures are `model_contract_failed`. A valid,
   complete arrival-alignment discrimination failure is
   `process_observation_confounded`; invalid or unavailable alignment evidence
   is `model_contract_failed`. Dropout and frailty warnings are required only
   when `narrow_wrong=true`. A continuous-abundance warning is always required.
4. Add only the schema/evidence machinery needed to represent fit variants,
   shared equal-emission fits, literal truth access, descriptive stress rows,
   fixture-only Task 3 dispatch, and non-self-referential hashes.
5. Apply the complete provenance amendment: explicit post-exposure Log
   authority, complete byte envelopes around each command, pinned
   branch/HEAD/base and candidate-footprint guards at every irreversible
   checkpoint, and a nonmutating nonzero disposition with at most one
   independently approved exact retry.
6. Mark the prior Log-only interpretation
   `superseded_pending_amendment` by a future append-only record. Preserve every
   existing Log byte. Do not append that record until Task 2b releases the live
   parent.
7. Resolve the Task 3 calibration-smoke conflict by allowing only injected,
   deterministic fixture dispatch under `tmp_path`. Task 4 remains the first
   owner of a live runtime benchmark and any scientific calibration row.

The latent-metric proposal's quantitative thresholds and pass-count rules are
explicitly rejected. The schema proposal's alternative unscaled interval score,
zero expected values, continuous-abundance latent target, and warning-valued
latent rows are explicitly superseded by sections 6 and 9 below. Do not add the
schema draft's `truth_source` column: every applicable row uses the same Goal
023 simulated binary event/censor truth, while the only proposed alternative
truth source, Goal 018 quasi-extirpation, is now explicitly not applicable.

## 3. Scientific Invariants

The tracked amendment must contain an explicit no-change clause:

```markdown
This integrated pre-Task-3 amendment changes no Goal 023 biological or
statistical model equation, estimand, natural support, generating value,
transition or emission timing convention, optimizer/profile rule, scenario ID,
schedule, effort rule, replicate count, predictive-reference count, bootstrap
count, seed payload or substream mapping, existing numerical recovery/coverage/
predictive threshold, transportability statement, or publication authority.
It adds descriptive latent diagnostics, total decision handling, typed evidence
identity, nonrecursive artifact hashes, fixture-only Task 3 dispatch, and
fail-closed provenance execution mechanics only.
```

Insert that paragraph at the start of every new integrated-amendment section in
`Goal.md`, the authoritative spec, `Plan.md`, and `Runbook.md`.

## 4. Scenario Evidence Registry And Truth Access

### 4.1 Shared Normative Text

Insert the following complete section into both `Goal.md` and the authoritative
spec.

```markdown
### Scenario Evidence Registry And Fit Identity

The following 11-row registry is literal and ordered. It is the only authority
for truth access, fit scope, primary fit variant, comparator fit variant, and
latent-time applicability. Comparator fits remain visible in
`fit_execution_evidence.csv` but never silently enter primary recovery,
coverage, profile, latent-time, or predictive rows.

| # | Scenario | Truth access | Fit scope | Primary variant | Comparator | Parameter evidence | Latent-time evidence |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `process_oracle_observed_transition` | `oracle_only` | `replicate` | `canonical` | none | gated, 3 process parameters | diagnostic, all 5,225 passable cells |
| 2 | `observation_oracle_fixed_transition` | `oracle_only` | `replicate` | `canonical` | none | gated, 2 rates | not applicable |
| 3 | `dense_count_exact_model` | `analyst_firewalled` | `replicate` | `canonical` | none | gated, 5 parameters | diagnostic, all 5,225 passable cells |
| 4 | `structured_imperfect_effort` | `analyst_firewalled` | `replicate` | `canonical` | none | gated, 5 parameters | diagnostic, all 5,225 passable cells |
| 5 | `sparse_expected_failure` | `analyst_firewalled` | `replicate` | `canonical` | none | dedicated `beta_driver` gate; other rows descriptive | diagnostic, fixed 1,306-cell sparse frame |
| 6 | `zero_driver_effect_negative_control` | `analyst_firewalled` | `replicate` | `canonical` | none | control plus descriptive recovery | diagnostic, all 5,225 passable cells |
| 7 | `permuted_arrival_alignment_stress` | `stress_evaluator_only` | `replicate` | `permuted_alignment` | `correct_alignment` | primary variant descriptive; comparator score only | diagnostic, fixed 1,045 score cells |
| 8 | `no_emission_contrast_negative_control` | `analyst_firewalled` | `scenario_shared` | `equal_rate` | `ordered_emission` | shared fits and six fixed status rows; no recovery/profile rows | not applicable |
| 9 | `informative_dropout_misspecification_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | descriptive, 5 known parameters | diagnostic, all 5,225 passable cells |
| 10 | `goal018_continuous_abundance_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | estimates/interval widths only; no recovery truth | not applicable |
| 11 | `spatial_frailty_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | descriptive, 5 known parameters | diagnostic, all 5,225 passable cells |

Truth-access meanings are literal:

- `oracle_only`: true transition/state fields may enter only the physically
  separate named oracle likelihood. They never enter joint fitting.
- `analyst_firewalled`: generation truth remains in the controller/evaluator;
  the fitted interface receives only analyst-visible fields. Evaluation may
  compare a completed fit with generating truth.
- `stress_evaluator_only`: stress construction, hidden state, original
  alignment, dropout, frailty, continuous abundance, and correct/permuted
  comparison state remain in a physically separate evaluator and are consulted
  only after the required fit has completed.

For the arrival stress, the permitted permuted `TP(x)` is the primary analyst
covariate and true `TP(x)` is permitted only in the separate correct-alignment
comparator. Original alignment, permutation audit, paired-score evaluation, and
truth-based descriptive rows remain evaluator-only. For zero-driver and
equal-emission controls, the fitter is never told the generating zero/equal
label through starts, bounds, objectives, profiles, or tie-breaking.

Truth may generate data, compute a preregistered post-fit truth diagnostic, and
assign a frozen gate. It must never alter analyst schedules, starts, bounds,
objectives, profile starts, plug-in weights, predictive references, sorting, or
fit classification.
```

### 4.2 Exact Placement

- `Goal.md`: insert after the final paragraph of `### Expected failure and
  controls`, immediately before `## Replication And Holdout Lock`.
- authoritative spec: insert at the identical body anchor, immediately before
  `## Replication And Holdout Lock`.
- Do not alter any of the eleven existing scenario definitions.

## 5. Schema And Evidence Amendment

### 5.1 `scenario_definitions.csv`

Append these fields to the existing header:

```text
fit_scope,primary_fit_variant,comparator_fit_variant
```

Complete schema:

```text
scenario_id:str!
scenario_role:enum!
generation_model:enum!
fit_model:enum!
schedule_id:enum!
effort_rule:str!
development_replicates:int!
calibration_replicates:int!
holdout_replicates:int!
expected_behavior:enum!
truth_access_class:enum!
transportability_class:enum!
fit_scope:enum!
primary_fit_variant:enum!
comparator_fit_variant:enum?
```

Primary key: `scenario_id`.

Rows use the numbered scenario order in section 4, an explicit exception to
the general lexical primary-key sort rule.

### 5.2 `fit_execution_evidence.csv`

Add this root artifact with literal header:

```text
scenario_id,split_id,fit_scope,fit_variant,fit_index,source_replicate_first,source_replicate_last,source_replicate_count,fit_succeeded,converged_start_count,best_start_index,best_two_log_likelihoods_agree,at_boundary,boundary_parameter_ids,alpha_estimate,beta_driver_estimate,beta_quality_estimate,lambda_quasi_estimate,lambda_present_estimate,lambda_equal_estimate,log_likelihood,heldout_log_score,fit_failure_class,failure_code,evidence_row_type,design_kind,design_provenance,design_role,design_n_rows,design_n_columns,design_rank,design_condition_number,design_passed,design_failure_code,design_frame_cell_count,design_frame_sha256
```

Literal schema:

```text
scenario_id:str!
split_id:enum!
fit_scope:enum!
fit_variant:enum!
fit_index:int!
source_replicate_first:int!
source_replicate_last:int!
source_replicate_count:int!
fit_succeeded:bool!
converged_start_count:int?
best_start_index:int?
best_two_log_likelihoods_agree:bool?
at_boundary:bool?
boundary_parameter_ids:str?
alpha_estimate:float?
beta_driver_estimate:float?
beta_quality_estimate:float?
lambda_quasi_estimate:float?
lambda_present_estimate:float?
lambda_equal_estimate:float?
log_likelihood:float?
heldout_log_score:float?
fit_failure_class:enum?
failure_code:str?
evidence_row_type:enum!
design_kind:enum?
design_provenance:str?
design_role:str?
design_n_rows:int?
design_n_columns:int?
design_rank:int?
design_condition_number:float?
design_passed:bool?
design_failure_code:str?
design_frame_cell_count:int?
design_frame_sha256:str?
```

Primary key and sort key:

```text
(scenario_id,split_id,fit_scope,fit_variant,fit_index,evidence_row_type,design_kind)
```

The fit identity sorts first, followed by `fit_result` before
`design_diagnostic` and then `potential,oracle,plugin`. Duplicate keys are
forbidden. Every fit identity has one fit-result row and exactly its applicable
design rows: process oracle `potential,oracle`; observation oracle and
`equal_rate` `potential`; every joint variant `potential,plugin`. The complete
frame is exactly 990 fit rows plus 1695 design rows. Fit/design nullability,
provenance, roles, row counts, canonical cell-frame count/digest, rank,
condition, pass, and typed failures are exactly the amended Goal/spec authority.
Row rules are exact:

- `fit_scope=replicate`: `fit_index`, `source_replicate_first`, and
  `source_replicate_last` all equal the scientific `replicate_id`; source count
  is `1`.
- `fit_scope=scenario_shared`: `fit_index=0`; equal-emission development uses
  source range `0..11`, count `12`; holdout uses `0..23`, count `24`.
- `fit_scope=bootstrap_shared`: only equal emission is legal;
  `fit_index=bundle_id` in `0..198`, source range `0..23`, count `24`.
- Timing-only equal-emission and timing-only bootstrap units emit no row because
  `scientific_row=false`.
- Every required attempt emits one fit-result row whether successful or failed.
  A failed row requires one applicable `fit_failure_class` and nonempty
  `failure_code`; accepted estimates, likelihood, and heldout score are null. A
  successful row has null failure class and code.
- Multistart `fit_succeeded=true` requires at least six successful starts,
  finite accepted output, and best-two agreement. `converged_start_count` is
  `0..8`; `best_start_index`, when present, is `1..8`.
- The closed-form equal-rate fit has null start fields. A clipped boundary MLE
  is visible but has `fit_succeeded=false` and
  `fit_failure_class=equal_rate_noninterior_failure` plus
  `failure_code=equal_rate_mle_noninterior`.
- `boundary_parameter_ids` is null when no accepted parameter is on a boundary;
  otherwise it is a no-space `|`-joined list in frozen parameter order.
- Process oracle populates three process estimates; observation oracle two rate
  estimates; ordinary ordered fits five estimates; equal-rate fits only
  `lambda_equal_estimate`.
- Arrival emits correct and permuted replicate rows. Both fit on 4,180 cells and
  both heldout scores use only the 1,045 score cells. A paired win requires two
  successful finite rows and strict `correct > permuted` score.
- Equal emission emits two observed shared rows and two bootstrap-shared rows
  for every bundle. The paired likelihoods must exactly reproduce observed
  `D`, every `D_b`, and add-one p. All 199 ordered bootstrap rows must succeed.

The joint fitter accepts only a module-issued canonical `AnalystFitFrame`,
checks exact history IDs before potential design or optimization, carries its
count/digest through `JointFitResult`, and derives persisted joint frame fields
only from that result. Design rank is bounded by
`min(n_rows,n_columns)` and pass requires `n_rows >= n_columns`. The literal
failure transition table is:

```text
potential_rank_gate_failure      -> potential rank failure; downstream not evaluated
potential_condition_gate_failure -> potential condition failure; downstream not evaluated
optimizer_or_nonfinite_failure   -> passing potential; rank-zero joint/process failure diagnostic
plugin_rank_gate_failure         -> matching evaluated plug-in rank failure
plugin_condition_gate_failure    -> matching evaluated plug-in condition failure
oracle_rank_gate_failure         -> matching evaluated oracle rank failure
oracle_condition_gate_failure    -> matching evaluated oracle condition failure
equal_rate_noninterior_failure   -> potential pass; no downstream diagnostic
```

Potential failure forbids optimizer-result fields. Plug-in failure requires a
successful optimizer result. Observation optimizer and equal-rate states retain
their potential-only applicability. Any contradiction fails before reduction.

This table is the sole fit-execution and convergence authority. Every fit-
derived science row must reconcile to exactly one permitted primary fit row.
`report.md` links this table directly. `control_comparison.svg` reads arrival
pair availability/scores and equal-emission observed/bootstrap fit evidence
back from this emitted table; live fit objects are not an alternative input.

### 5.3 Fit Variants In Existing Tables

Use these literal headers and primary keys:

```text
replicate_recovery.csv
scenario_id,split_id,replicate_id,fit_variant,parameter_id,truth_value,estimate,interval_lower,interval_upper,interval_width,converged,converged_start_count,at_boundary,profile_two_sided,truth_in_interval,log_likelihood,signed_error,absolute_error,gate_result
PK (scenario_id,split_id,replicate_id,fit_variant,parameter_id)

coverage_calibration.csv
scenario_id,split_id,fit_variant,parameter_id,replicate_count,converged_count,coverage_count,coverage_fraction,acceptance_lower_count,acceptance_upper_count,median_signed_error,median_absolute_error,median_interval_width,maximum_absolute_error,maximum_interval_width,gate_result
PK (scenario_id,split_id,fit_variant,parameter_id)

latent_time_calibration.csv
scenario_id,split_id,replicate_id,fit_variant,metric_id,sample_size,fit_succeeded,diagnostic_available,observed_value,expected_value,error,gate_result
PK (scenario_id,split_id,replicate_id,fit_variant,metric_id)

predictive_replicate_diagnostics.csv
scenario_id,split_id,replicate_id,fit_variant,stratum_type,stratum_value,metric_id,sample_size,fit_succeeded,diagnostic_available,observed_value,reference_mean,reference_sd,reference_mcse,standardized_residual,standardized_residual_nonfinite,randomized_pit
PK (scenario_id,split_id,replicate_id,fit_variant,stratum_type,stratum_value,metric_id)

predictive_check_summary.csv
scenario_id,split_id,fit_variant,stratum_type,stratum_value,metric_id,replicate_count,diagnostic_count,failed_fit_count,mean_standardized_residual,stouffer_z,ks_statistic,raw_p,holm_adjusted_p,warning,gate_result
PK (scenario_id,split_id,fit_variant,stratum_type,stratum_value,metric_id)

identifiability_profiles.csv
scenario_id,split_id,replicate_id,fit_variant,parameter_id,grid_index,parameter_value,profile_log_likelihood,likelihood_ratio_delta,nuisance_converged,inside_interval
PK (scenario_id,split_id,replicate_id,fit_variant,parameter_id,grid_index)
```

Existing types and nullability stay unchanged except:

```text
latent_time_calibration.fit_variant:enum!
latent_time_calibration.fit_succeeded:bool?
latent_time_calibration.diagnostic_available:bool!
```

General rows use `canonical`; arrival primary rows use
`permuted_alignment`; equal-emission predictive rows use `equal_rate`. Equal
emission has no recovery, coverage, latent-time, or profile rows. Arrival's
`correct_alignment` comparator has no recovery, coverage, latent-time,
profile, or predictive row.

### 5.4 Descriptive Stress Recovery

Arrival, informative dropout, continuous abundance, and spatial frailty retain
all attempted primary-fit parameter rows. They cannot silently become new
recovery gates.

For arrival, informative dropout, and spatial frailty:

- emit five `replicate_recovery` rows per attempted primary fit;
- retain generating values only in evaluator-side row construction;
- failed/nonfinite fits retain rows with null accepted estimate/interval fields;
- failed/open/missing intervals are uncovered in the full attempted
  denominator;
- descriptive median/maximum absolute error and interval width use the same
  full-support imputations as nested rows;
- median signed error uses finite converged estimates only and is nullable;
- coverage denominators are `12` development and `24` holdout;
  `acceptance_lower_count` and `acceptance_upper_count` are null; and
- recovery/coverage `gate_result` is `diagnostic` with complete fit evidence
  and `warning` when required fit/profile evidence is unavailable. This field
  never overrides the separate required-fit or predictive reducer.

For continuous abundance:

- emit five primary-fit recovery rows per attempt for estimates, intervals,
  convergence, boundaries, and likelihood;
- `truth_value`, `truth_in_interval`, `signed_error`, and `absolute_error` are
  null;
- emit one coverage row per parameter with attempted/converged counts and
  descriptively imputed interval-width summaries;
- coverage counts/fractions/bounds and signed/absolute-error summaries are
  null; and
- use the same diagnostic/warning availability convention.

### 5.5 Control Summary

Replace the `control_decision_summary.csv` header with:

```text
decision_row_id,decision_row_type,scenario_id,parameter_id,structural_status,practical_status,gate_family,gate_result,test_statistic,bootstrap_replicates,bootstrap_converged_count,bootstrap_failed_count,p_value,alignment_correlation,silent_misspecification_failure,attempted_replicates,evaluable_replicates,event_count,acceptance_lower_count,acceptance_upper_count,recommendation_rank,recommendation_class,transportability_class,interpretation
```

Primary key and row sort: `decision_row_id`, lexical.

```text
decision_row_type = scenario_gate|parameter_status|final_decision
scenario_gate ID = scenario_gate|<scenario_id>
parameter status ID = parameter_status|no_emission_contrast_negative_control|<parameter_id>
final ID = final_decision
```

Add nullable fields:

```text
attempted_replicates:int?
evaluable_replicates:int?
event_count:int?
acceptance_lower_count:int?
acceptance_upper_count:int?
bootstrap_converged_count:int?
bootstrap_failed_count:int?
```

The complete schema is:

```text
decision_row_id:str!
decision_row_type:enum!
scenario_id:str?
parameter_id:str?
structural_status:enum?
practical_status:enum?
gate_family:enum!
gate_result:enum!
test_statistic:float?
bootstrap_replicates:int?
bootstrap_converged_count:int?
bootstrap_failed_count:int?
p_value:float?
alignment_correlation:float?
silent_misspecification_failure:bool!
attempted_replicates:int?
evaluable_replicates:int?
event_count:int?
acceptance_lower_count:int?
acceptance_upper_count:int?
recommendation_rank:int?
recommendation_class:enum?
transportability_class:enum!
interpretation:str!
```

Equal emission records attempted `24`; evaluable `24` only when both observed
shared fits are valid, otherwise `0`; observed `D`; bootstrap count `199`;
successful ordered-refit count; failed count `199-successful`; and p only when
all required statistics are finite. All values must recompute from
`fit_execution_evidence.csv`.

Zero driver records attempted `24`; evaluable only for successful finite fits
with finite closed two-sided `beta_driver` intervals; event count as intervals
excluding zero; and bounds `0..6`. Any evaluable count below `24` is an
availability failure, not a non-exclusion or denominator reduction.

Arrival records attempted `24`; evaluable as complete finite fit pairs; event
count as strict correct-score wins; and bounds `22..24`. Any evaluable count
below `24` is an availability failure.

### 5.6 Enum Additions

Keep every existing enum and add:

```text
fit_scope = replicate|scenario_shared|bootstrap_shared
fit_variant = canonical|correct_alignment|permuted_alignment|equal_rate|ordered_emission
decision_row_type = scenario_gate|parameter_status|final_decision
```

`bootstrap_shared` occurs only in fit evidence. Do not add a latent threshold
enum, fifth recommendation, sentinel fit ID, nullable primary-key component,
or JSON hidden in an interpretation field.

## 6. Latent-Transition Diagnostic Contract

### 6.1 Normative Interpretation

Insert this complete section into both `Goal.md` and the authoritative spec:

```markdown
### Latent-Transition Diagnostics

Latent-time metrics are proper or interpretable censor-aware diagnostics, not
Goal 023 acceptance gates. They add no quantitative threshold, do not alter any
nested or scenario gate, and are excluded from recommendation inputs. An
available applicable row and an unavailable applicable row both use
`gate_result=diagnostic`; availability is carried separately. An inapplicable
row uses `gate_result=not_applicable`.

Index the 21 transition paths by `r=1,...,21` and define ordered evaluation
values `v_r=6*r`. Values `v_1,...,v_20` are event endpoints `6,...,120`.
`v_21=126` is an ordered label for `T>120`, not a biological claim that a
censored event occurred at 126.

For cell `x`, evaluator truth is

```text
R_x = transition_time / 6  for transition_time in {6,...,120}
R_x = 21                   for right censoring after 120
U_x = v_(R_x).
```

Let `p_xr` be the normalized analyst-side probability of path `r` at the
plug-in fit. These are conditional latent-path weights, not parameter-posterior
samples and not an MCMC/full-Bayesian posterior.

For process oracle, construct `p_xr` from fitted process path masses using only
analyst-visible `Q_x` and `TP(x)`. Complete that matrix before supplying true
event/censor outcomes to the evaluator. Never replace it with a one-hot oracle
truth vector. For ordinary joint fits, use normalized batched analyst path
weights at the fitted MLE. Evaluator truth enters only the pure scoring kernel.

Require exact sorted integer cell IDs on analyst and evaluator sides, exact
one-to-one ID equality, a `float64` matrix of shape `(N,21)`, finite nonnegative
entries, and every row sum within `1e-12` of one. Divide a within-tolerance row
by its finite positive sum once; do not clip or discard censor mass. Require
finite event truth on `6,12,...,120` or the accepted censor sentinel. A
missing/extra/duplicate cell, invalid probability, invalid truth, or nonfinite
score makes all three replicate diagnostics unavailable; no cell is dropped.

For endpoint `j=1,...,20`, define

```text
F_xj = sum(p_xr for r <= j)
I_xj = 1 if R_x <= j else 0.
```

The cumulative-incidence Brier diagnostic is

```text
transition_brier.observed_value =
  sum_x sum_j (F_xj - I_xj)^2 / (20*N)

transition_brier.expected_value =
  sum_x sum_j F_xj*(1-F_xj) / (20*N)

transition_brier.error = observed_value - expected_value.
```

It lies in `[0,1]` and is strictly proper for the complete ordered 21-category
distribution because the 20 cumulative probabilities identify all path masses.

Fix `alpha_interval=0.10`. Define the deterministic lower discrete quantile

```text
Q_x(q) = min(v_r such that sum(p_xs for s <= r) >= q).
```

Set `L_x=Q_x(0.05)` and `H_x=Q_x(0.95)`. Define the positively scaled central
interval score

```text
S_x(u) = 0.05*(H_x-L_x)
         + (L_x-u)*1(u<L_x)
         + (u-H_x)*1(u>H_x)

transition_interval_score.observed_value = sum_x S_x(U_x)/N
transition_interval_score.expected_value =
  sum_x sum_r p_xr*S_x(v_r)/N
transition_interval_score.error = observed_value - expected_value.
```

It lies in `[0,120]` time units and is proper for the 5th and 95th quantiles.
The positive `0.05` scale is part of the formula.

Set `M_x=Q_x(0.50)` and `A_x=abs(U_x-M_x)`. Then

```text
transition_median_absolute_error.observed_value = ordinary_median(A_1,...,A_N)
B_x = sum_r p_xr*abs(v_r-M_x)
transition_median_absolute_error.expected_value = ordinary_median(B_1,...,B_N)
transition_median_absolute_error.error = observed_value - expected_value.
```

For even `N`, the ordinary median is the arithmetic mean of the two central
sorted values. The median absolute error is an interpretable resolution
diagnostic, not a strictly proper full-distribution score, and its error is a
resolution contrast rather than a calibration residual with a claimed null
distribution.

Applicability and cell denominators are literal:

| Scenario | Status | `sample_size` | Frame/variant |
| --- | --- | ---: | --- |
| `process_oracle_observed_transition` | applicable | `5225` | all passable cells, canonical process fit |
| `observation_oracle_fixed_transition` | not applicable | `0` | none |
| `dense_count_exact_model` | applicable | `5225` | all passable cells, canonical fit |
| `structured_imperfect_effort` | applicable | `5225` | all passable cells, canonical fit |
| `sparse_expected_failure` | applicable | `1306` | frozen sparse frame, canonical fit |
| `zero_driver_effect_negative_control` | applicable | `5225` | all passable cells, canonical fit |
| `permuted_arrival_alignment_stress` | applicable | `1045` | score frame, primary permuted fit only |
| `no_emission_contrast_negative_control` | not applicable | `0` | none |
| `informative_dropout_misspecification_stress` | applicable | `5225` | all passable cells, canonical fit |
| `goal018_continuous_abundance_stress` | not applicable | `0` | no Goal 023 binary transition truth |
| `spatial_frailty_stress` | applicable | `5225` | all passable cells, canonical fit |

For every scientifically scheduled scenario/split/replicate, emit exactly
three rows in metric order `transition_brier`,
`transition_interval_score`, `transition_median_absolute_error`. Do not create
rows for a split the scenario does not instantiate. Inapplicable rows have
`sample_size=0`, `fit_succeeded=null`, `diagnostic_available=false`, null
numeric fields, and `gate_result=not_applicable`.

Applicable rows always retain the frozen cell denominator. All censored cells
remain in `N`. Missing count opportunities remove emissions only, never cells,
transition intervals, censor mass, or evaluator truth. Informative-dropout
cells with no retained counts receive an empty analyst history and fitted
process path probabilities.

A successful finite applicable fit with valid posterior/truth input has
`fit_succeeded=true`, `diagnostic_available=true`, finite values, and
`gate_result=diagnostic`. A failed/nonfinite required fit has
`fit_succeeded=false`, `diagnostic_available=false`, null numeric fields, the
fixed `sample_size`, and `gate_result=diagnostic`. A successful fit with an
invalid probability matrix, truth mismatch, or failed prerequisite design has
its literal fit status, `diagnostic_available=false`, null numeric fields, the
fixed `sample_size`, and `gate_result=diagnostic`. No complete-case fallback is
allowed.

A missing profile alone does not prevent plug-in path scoring when the MLE is
finite; the separate profile/recovery gate retains its own failure. A latent
row may not enter starts, fitting, profiles, plug-in design, predictive
references, scenario reducers, recommendation precedence, or result selection.
Missing, duplicate, malformed, or orphan latent rows are an artifact/schema
contract failure; their scientific values and availability are not.
```

### 6.2 Exact Placement

- `Goal.md`: insert immediately before
  `### Predictive applicability and fixed frames` in `## Deterministic Gates`.
- authoritative spec: insert at the identical body anchor.
- Do not add `latent_time_thresholds` to config and do not alter the existing
  numerical gate table.

## 7. Total Recommendation Contract

### 7.1 Common Evidence States

Insert these definitions before the scenario decision table:

```text
available       required evidence is converged, finite, schema-valid, and applicable
nonconverged    attempt exists but fails the frozen fit-success contract
nonfinite       a required value is nonfinite and serialized null with a typed flag
open_profile    valid profile reaches support without a closing crossing
missing_result  required row/variant/profile/diagnostic was not emitted
not_applicable  authority explicitly excludes the output
```

A missing/duplicate attempted row is `missing_result`, never an open profile.
Predictive completeness requires a successful finite required fit and all 27
valid diagnostic cells for every attempted replicate. A scientific warning
exists only when predictive evidence is complete and a finite preregistered
warning rule fires. Forced warning due to unavailability cannot satisfy a
stress warning requirement.

### 7.2 Frozen Denominators And Missingness

The following rules are patch text and do not alter existing numeric gates:

```markdown
For nested scenarios 1-4, use all 48 attempted holdout replicates for every
applicable parameter. Convergence denominators remain 48. Coverage is a
48-element Boolean vector; a nonconverged/nonfinite fit or open/missing interval
is uncovered. Missing estimates and interval widths receive the existing full-
support imputations `8`, `6`, `4`, `0.99`, or `9.75`. Median and maximum
absolute error and width use all 48 imputed values; the even median averages
positions 24 and 25. Signed-error medians use finite converged estimates only
and are null when none exist. Coverage remains inclusive `36..48`; convergence
minima remain `46/48`, `46/48`, `46/48`, and `44/48` in scenario order. A
missing or duplicate row is an artifact/schema failure and is never imputed.

Sparse honesty uses all 24 attempted `beta_driver` rows:

```text
sparse_coverage_pass = 18 <= coverage_count <= 24
sparse_width_pass = sparse_imputed_median_width >= structured_imputed_median_width
sparse_honesty_pass =
    sparse_predictive_pass and sparse_coverage_pass and sparse_width_pass.
```

Nonconverged/nonfinite/open/missing intervals are uncovered and contribute
width `6`; average sorted one-based positions 12 and 13. A failed required fit
also fails predictive completeness and cannot be rescued by imputation. Width
equal to structured passes; any smaller value is
`sparse_unexpectedly_narrow`. Other sparse recovery summaries are descriptive.

Zero-driver availability and false signal are separate:

```text
interval_decidable =
    fit is successful and finite
    and both interval endpoints are finite and closed
excludes_zero = interval_lower > 0 or interval_upper < 0
zero_driver_availability_pass = decidable_interval_count == 24
zero_driver_false_signal_pass =
    zero_driver_availability_pass and 0 <= exclusion_count <= 6.
```

A touching interval contains zero. An undecidable attempt has
`excludes_zero=null`, remains in the denominator, and prevents the binomial
decision.

Arrival uses 24 paired attempts. A pair requires successful finite correct and
permuted fits plus finite fixed-frame heldout scores. A failed pair is no win
and fails availability. Correlation must be finite and absolute value at most
`0.25`. With complete availability, `22..24` strict correct-score wins pass and
`0..21` fail discrimination. The primary permuted fit supplies profiles and
predictive references; the correct fit is comparator evidence only. At least
one available scientific warning is mandatory.

Equal emission uses one shared equal and one shared ordered fit over all 24
replicates and exactly 199 complete 24-replicate bootstrap bundles. The add-one
denominator remains 200. Any failed/nonfinite shared fit, statistic, equal fit,
or ordered refit fails availability. With complete availability, `p>=0.05`
passes and `p<0.05` fails. No profile rows exist. The six fixed status rows are
independent of p and exempt from generic accepted-estimand confounding because
unidentifiability is the expected control result.

Every predictive-applicable attempted replicate emits exactly 27 stable rows.
A failed fit emits 27 unavailable rows, no reference ensemble, remains in the
full denominator, increments `failed_fit_count`, and fails predictive
completeness. Nonfinite diagnostics serialize null plus the existing flag.

For informative dropout and spatial frailty, retain all 24 descriptive rows per
known parameter. Coverage uses 24 attempts; failed/nonfinite/open/missing
intervals are uncovered; descriptive error/width uses existing full-support
imputation; signed error remains finite-only. `narrow_wrong` is true only for a
finite closed two-sided interval excluding truth with width no larger than the
existing parameter maximum. Open and broad wrong intervals are not
`narrow_wrong`. No new stress recovery threshold is added.

Continuous abundance has no parameter-recovery truth. Its fit/profile rows are
descriptive with null truth, coverage, error, and `narrow_wrong`; its decisive
scientific requirement is complete predictive evidence with at least one
warning.
```

### 7.3 Total Scenario Decision Table

Evaluate global contract gates first, then scenarios in canonical order. Within
one scenario, the first matching row has local precedence. Compute all local
reasons for reporting, then reduce by global rank.

| # | Scenario | First matching condition | Local impact and canonical reason |
| ---: | --- | --- | --- |
| 1 | process oracle | Any potential/oracle design, convergence, coverage, existing error/width, fit-domain, or required artifact gate fails | `contract_failure:process_oracle_failed` |
| 1 | process oracle | All applicable gates pass | `pass` |
| 2 | observation oracle | Any potential design, convergence, coverage, existing error/width, fit-domain, or required artifact gate fails | `contract_failure:observation_oracle_failed` |
| 2 | observation oracle | All gates pass; conditional prediction may warn diagnostically | `pass` |
| 3 | dense exact | Missing/duplicate/malformed evidence, numerical-domain failure, or predictive evidence unavailable for a reason other than a retained typed nonconvergence | `contract_failure:dense_evidence_invalid` |
| 3 | dense exact | With complete schema-valid finite evidence after both oracles pass, any dense convergence, coverage, existing accuracy/precision, finite plug-in design, accepted-estimand identification, or exact predictive scientific gate fails; typed nonconvergence-driven incompleteness is included | `confounding:dense_joint_failed` |
| 3 | dense exact | All dense gates pass | `pass` |
| 4 | structured exact | Missing/malformed evidence; required-fit unavailability; convergence failure; coverage outside `36..48`; predictive incompleteness/rejection; or plug-in design unavailable, rank below `3`, nonfinite, or condition `>=1e8` | `contract_failure:structured_not_calibrated` |
| 4 | structured exact | Complete valid evidence declares an accepted estimand structurally or practically unidentified, excluding expected equal-emission labels | `confounding:structured_estimand_unidentified` |
| 4 | structured exact | Coverage, fit availability, plug-in design, accepted-estimand identification, and prediction pass, but an existing median error or median width limit fails | `structured_limitation:structured_precision_recovery_failed` |
| 4 | structured exact | Every structured gate passes | `pass` |
| 5 | sparse | Missing/malformed rows, required-fit/predictive failure, coverage outside `18..24`, or median width below structured | `contract_failure:sparse_honesty_failed` |
| 5 | sparse | Coverage, width, and predictive completeness pass | `pass` |
| 6 | zero driver | Any interval undecidable, required fit/plug-in/predictive evidence fails, or rows are missing/malformed | `contract_failure:zero_driver_unavailable` |
| 6 | zero driver | All 24 intervals decidable and exclusions are `7..24` | `confounding:zero_driver_false_signal` |
| 6 | zero driver | All intervals decidable, exclusions `0..6`, and standard prediction passes | `pass` |
| 7 | arrival alignment | Invalid/nonfinite correlation; missing pair; required fit/plug-in/score/predictive unavailability; or malformed evidence | `contract_failure:alignment_contract_or_availability_failed` |
| 7 | arrival alignment | Complete valid evidence but no available scientific warning | `contract_failure:alignment_silent_misspecification` |
| 7 | arrival alignment | Complete evidence and warning, but correct alignment wins `0..21` | `confounding:arrival_alignment_not_discriminated` |
| 7 | arrival alignment | Correlation valid, all 24 pairs available, wins `22..24`, and warning present | `pass` |
| 8 | equal emission | Shared fit/statistic invalid; any of 199 ordered refits fails; p nonfinite or `<0.05`; fixed status differs; or evidence malformed | `contract_failure:equal_emission_control_failed` |
| 8 | equal emission | All refits succeed, p `>=0.05`, and fixed statuses are exact | `pass` |
| 9 | informative dropout | Required fit/plug-in/predictive evidence unavailable or malformed | `contract_failure:informative_dropout_unavailable` |
| 9 | informative dropout | `any_narrow_wrong=true` and no available scientific warning | `contract_failure:informative_dropout_silent_misspecification` |
| 9 | informative dropout | Prediction complete and either no narrow-wrong result exists or a warning detects it | `pass` |
| 10 | continuous abundance | Required fit/plug-in/predictive evidence unavailable or malformed | `contract_failure:continuous_abundance_unavailable` |
| 10 | continuous abundance | Complete evidence but no available scientific warning | `contract_failure:continuous_abundance_silent_misspecification` |
| 10 | continuous abundance | Complete evidence and at least one warning | `pass` |
| 11 | spatial frailty | Required fit/plug-in/predictive evidence unavailable or malformed | `contract_failure:spatial_frailty_unavailable` |
| 11 | spatial frailty | `any_narrow_wrong=true` and no available scientific warning | `contract_failure:spatial_frailty_silent_misspecification` |
| 11 | spatial frailty | Prediction complete and either no narrow-wrong result exists or a warning detects it | `pass` |

Latent diagnostic values, expected values, residuals, and availability never
appear in this table. A missing/duplicate/malformed latent artifact row may fail
the global artifact/schema contract, but a large, small, or unavailable
scientific latent diagnostic cannot change a local impact.

### 7.4 Global State Machine

Replace the current complete `## Recommendation Precedence` body in both Goal
and spec with the following:

```markdown
## Recommendation Precedence

Preserve exactly these four classes and ranks:

1. `model_contract_failed`
2. `process_observation_confounded`
3. `observation_limited_but_calibrated`
4. `latent_response_observation_gate_passed`

Compute every applicable local reducer so all reasons remain visible, then use:

```text
required_control_ids = {
    zero_driver_effect_negative_control,
    no_emission_contrast_negative_control,
}

required_stress_ids = {
    permuted_arrival_alignment_stress,
    informative_dropout_misspecification_stress,
    goal018_continuous_abundance_stress,
    spatial_frailty_stress,
}

contract_failure =
    any frozen source/schema/analytic/likelihood/holdout/artifact/provenance/
        numerical-domain/potential-design/noncollision gate fails
    or any required input is missing, unknown, duplicate, contradictory,
        malformed, or unevaluated
    or any scenario reducer returns contract_failure

confounding = any scenario reducer returns confounding

structured_limitation =
    scenario 3 returns pass
    and scenario 4 returns structured_limitation
    and every scenario other than 4 returns pass

all_required_pass =
    every global contract gate passes
    and scenarios 1..11 each return pass
    and every required control and stress ID is present exactly once

if contract_failure:
    recommendation_rank = 1
    recommendation_class = model_contract_failed
elif confounding:
    recommendation_rank = 2
    recommendation_class = process_observation_confounded
elif structured_limitation:
    recommendation_rank = 3
    recommendation_class = observation_limited_but_calibrated
elif all_required_pass:
    recommendation_rank = 4
    recommendation_class = latent_response_observation_gate_passed
else:
    recommendation_rank = 1
    recommendation_class = model_contract_failed
    reason = incomplete_or_contradictory_decision_vector
```

Rank 3 is reachable only when every non-structured global/scenario gate,
including sparse honesty, both controls, and all four stresses, passes. Rank 4
is unreachable when any control or stress is absent, unavailable, invalid, or
fails its local rule. A valid arrival-alignment discrimination failure is rank
2; invalid or unavailable alignment is rank 1. Dropout and frailty warnings are
conditional on `narrow_wrong`; continuous abundance and valid alignment always
require at least one available scientific warning.

When several reasons occur, emit all reason flags in canonical global-gate then
scenario order. Choose the smallest recommendation rank. Within that rank, the
first canonical reason is primary. Unknown or contradictory vectors never
default to pass.

Always emit:

```text
transportability_class = scheduled_count_only_point_process_bridge_required
```

Latent-transition diagnostics are recommendation-neutral and excluded from the
state machine.
```

## 8. Artifact Set And Hash Interfaces

### 8.1 Exact 22-File Bundle

Replace the current 21-file expected set with this literal 22-file order:

```text
recovery_gate_config.json
runtime_projection.json
source_provenance.json
holdout_manifest.json
model_parameter_contract.csv
scenario_definitions.csv
fit_execution_evidence.csv
replicate_recovery.csv
coverage_calibration.csv
latent_time_calibration.csv
predictive_replicate_diagnostics.csv
predictive_check_summary.csv
identifiability_profiles.csv
control_decision_summary.csv
verification.json
report.md
visuals/parameter_recovery.svg
visuals/coverage_calibration.svg
visuals/latent_time_calibration.svg
visuals/identifiability_profiles.svg
visuals/control_comparison.svg
visuals/review_montage.svg
```

The config `artifact_manifest` is an expected-set registry, not a final
integrity manifest. It has exactly 22 entries in that order. Every entry has
exactly `path`, `role`, `required`, and `sha256`; every `required=true`; every
`sha256=null`. The config is immutable after self-hashing.

The artifact-manifest document is `verification.json`. Freeze
`checks[name="artifact_manifest"].details` to exactly:

```text
schema_version:str
entries:list[{path:str,sha256:str}]
represented_artifact_set_sha256:str
```

Its `entries` list contains the other 21 files exactly once in the literal
bundle order, with `verification.json` omitted. Compute
`represented_artifact_set_sha256` over UTF-8 lines:

```text
<file_sha256><two spaces><relative_artifact_path>\n
```

in represented-entry order. Missing, extra, duplicate, zero-byte, nonregular,
or changed files fail verification.

After canonical `verification.json` bytes exist, an external
`ArtifactSnapshot` hashes all 22 files, including `verification.json`; sorts the
complete path/hash manifest lexically by path; and computes
`artifact_set_sha256` with the same line format. That complete digest is held by
the post-exposure envelope and append-only Log records. It is never embedded in
an included artifact.

Use the phrase `artifact-manifest document (verification.json)` throughout the
authority and tests. Do not use `artifact-manifest file`, add a second manifest,
or modify `source_digest_receipt.json`.

### 8.2 Unambiguous Hash Names

Freeze these meanings:

```text
config_sha256
  Embedded config self-hash over the canonical config payload with only
  config_sha256 omitted.

config_file_sha256
  SHA-256 over complete canonical recovery_gate_config.json bytes, including
  the embedded config_sha256 field.

receipt_sha256
  Embedded holdout-receipt self-hash over canonical receipt payload with only
  receipt_sha256 omitted.

holdout_receipt_file_sha256
  SHA-256 over complete holdout_receipt.json bytes.

preholdout_receipt_file_sha256
  SHA-256 over complete preholdout_state_receipt.json bytes. That receipt has
  no embedded self-hash.

represented_artifact_set_sha256
  verification.json's digest over the 21 represented files.

artifact_set_sha256
  External complete 22-file snapshot digest including verification.json.
```

`holdout_manifest.json.receipt_sha256` equals the embedded holdout-receipt
`receipt_sha256`, never the file-byte hash. Config bindings in verification and
both receipts use embedded `config_sha256`. Before/after envelopes use complete
file-byte hashes as well as the self-hash identities.

Typed internal identities must be equivalent to:

```python
@dataclass(frozen=True, slots=True)
class FrozenConfigIdentity:
    path: Path
    payload: Mapping[str, object]
    config_sha256: str
    config_file_sha256: str
    canonical_bytes: bytes

@dataclass(frozen=True, slots=True)
class HoldoutReceiptIdentity:
    path: Path
    payload: Mapping[str, object]
    receipt_sha256: str
    holdout_receipt_file_sha256: str
    canonical_bytes: bytes

@dataclass(frozen=True, slots=True)
class ReceiptFileIdentity:
    path: Path
    file_sha256: str
    canonical_bytes: bytes
```

Freeze these `ProvenanceEnvelope` members:

```text
config_sha256
config_file_sha256
preholdout_receipt_file_sha256
receipt_sha256
holdout_receipt_file_sha256
represented_artifact_set_sha256
artifact_set_sha256
```

Raw dicts, unchecked paths, ambiguous `sha256` strings, and swapped self/file
hashes are rejected at every phase boundary.

### 8.3 Exact Placement

- In Goal/spec `## Source And Artifact Contracts`, add
  `fit_execution_evidence.csv` immediately after `scenario_definitions.csv` in
  the root-file grain list and replace all affected row grains, schemas, keys,
  and enums with sections 5 and 8.
- Replace the current bundle tuple wherever it appears in Goal/spec, config
  contract, Runbook checks, report requirements, or ignored implementation
  guidance.
- Immediately after the canonical tracked-state digest paragraph, insert the
  hash-name and two-level artifact text above.
- Preserve all existing JSON top-level keys. Expand only the nested scenario,
  artifact-manifest, and verification details needed by these amendments. Do
  not add a latent-threshold config object.

## 9. Provenance Amendment Contract

### 9.1 Shared Normative Text

Insert the following complete section into both Goal and spec immediately after
the existing bullet that requires exclusive atomic `holdout_receipt.json`
creation and before the eight-worker bullet.

```markdown
### Provenance Amendment Contract

This provenance amendment changes no scientific contract or result. The pinned
repository identity is branch
`codex/spatext-goal023-latent-response-observation-gate`, HEAD
`53462d0365babf2c8070714a930f69b4071af276`, and base ref `origin/main`
resolving to the same commit.

Config emission, `freeze-tracked-state`, and the holdout phase immediately
before exclusive receipt creation and again immediately before any RNG object
or payload construction must fail closed unless all of the following hold:

1. branch, HEAD, and base are exact;
2. the literal 16-file analytical manifest is complete and reproduces its
   digest;
3. every changed candidate path is inside the literal Runbook section 8
   19-path publication-path universe;
4. every path required in the current phase is present with its exact disk hash
   and every receipt required to be absent in that phase is absent;
5. no untracked non-ignored path exists outside that allowlist and no other
   out-of-footprint path exists; and
6. the phase-specific config and receipt conditions hold.

The phase-specific presence vector is literal:

```text
config emission and pre-freeze:
  present = 16 analytical files + Log.md
  absent  = preholdout_state_receipt.json + holdout_receipt.json

post-freeze and holdout pre-receipt:
  present = 16 analytical files + Log.md + preholdout_state_receipt.json
  absent  = holdout_receipt.json

holdout post-receipt and publication:
  present = all 19 publication paths
  absent  = none
```

The accepted candidate-footprint rule permits required new publication paths
to remain unstaged before the existing section 8 exact-staging step; it does not
permit an unknown path. The guard records each candidate path's exact status,
presence/absence, and disk hash so a new, removed, staged, unstaged, or
untracked state change cannot be hidden.

A config-emission failure writes no config. A freeze failure changes no config
byte and creates no preholdout receipt. A pre-receipt failure creates no
holdout receipt. A post-receipt/pre-RNG failure preserves the immutable
receipt, constructs no RNG object or payload, burns the namespace, and records
`STOP_INVALIDATED_POST_EXPOSURE`.

Before freeze, every potentially mutating validation command, including
`pre-commit run --all-files`, must be proven a working-tree and index no-op on
the exact candidate. Any pre-freeze mutation returns to RED-GREEN work, config
re-emission, hash resealing, and fresh review.

After exclusive atomic holdout-receipt creation, working-tree writes to tracked
publication paths are limited to that machine-created immutable receipt and
append-only provenance records at the end of Goal 023 `Log.md`. The Log
authorization is explicit and independent of the scientific-command output
restriction. One designated provenance writer may append only an independently
approved exact payload. No other tracked working-tree write is authorized.

A Log append must reproduce its parent line count, byte count, and SHA-256;
preserve every parent byte as an exact prefix; bind branch/HEAD/base, authority
tuple, embedded and file config hashes, analytical digest, both receipt file
hashes and embedded receipt self-hash, represented artifact-set hash, complete
artifact-set hash, and current candidate/index manifests; identify writer and
reviewer roles plus immutable disposition; and change no analytical contract or
artifact result.

Every command started after exposure, including inspection, hashing,
validation, review preparation, staging, provenance append, commit, merge,
fetch, push, and publication guards, runs inside its own fail-closed
before/after envelope. Immediately before each command capture:

- branch, HEAD, and base;
- complete tracked, staged, unstaged, and untracked non-ignored status;
- the cached path/blob manifest;
- the literal 16-file path/hash manifest and aggregate digest;
- current Log byte count, line count, SHA-256, and exact prefix bytes;
- existence and full-file SHA-256 of both receipts;
- embedded `receipt_sha256` for the holdout receipt;
- embedded `config_sha256` and complete `config_file_sha256`;
- the represented 21-file artifact manifest and
  `represented_artifact_set_sha256`; and
- the exact lexical 22-file path/hash snapshot, including
  `verification.json`, plus `artifact_set_sha256`.

Immediately after the command reproduce every immutable member. A missing,
added, replaced, reordered, zero-byte, nonregular, or changed artifact is a
mutation. Apply the envelope separately to each command, never once around a
batch.

For an authorized Log append, the old Log bytes must remain the exact prefix
and the suffix must equal the independently approved payload byte for byte.
Every other envelope member and every non-Log index blob remains unchanged.
For an authorized exact staging command, only the index may change, and only to
the predeclared allowlisted path/blob set; no working-tree byte may change. The
authorized commit may change only HEAD from the pinned parent to a commit whose
parent and complete tree equal the approved parent and cached candidate.
Subsequent fast-forward and push commands may make only the exact identity
transitions in Runbook section 9. All other commands leave Log, index,
identity, status, footprint, receipts, config, and artifacts unchanged.

All ordinary post-holdout review records are appended and staged before final
review. The final reviewer inspects the exact cached candidate and an exact
proposed terminal-attestation payload containing its live Log parent. On
acceptance, that returned payload is the approved append. The provenance writer
appends it once, stages `Log.md`, proves exact prefix and suffix plus unchanged
non-Log blobs and envelope, and permits no further Log append before commit. No
second attestation about that append is permitted. Rejection appends no
acceptance record.

The holdout command internally repeats the complete frozen-state guard after
receipt creation and before RNG construction. After successful emission it
establishes the immutable 22-file artifact snapshot used by every later
envelope.

A zero exit with an unchanged envelope is
`CONTINUE_FROZEN_CANDIDATE`. Any byte, identity, status, or footprint mutation
is `STOP_INVALIDATED_POST_EXPOSURE`, whether the command exits zero or nonzero:
preserve state, receipts, config, and artifacts; append the stop disposition if
the Log prefix remains safely appendable; do not restore, repair, amend, or
retry under the namespace.

A nonzero exit with an otherwise unchanged envelope is
`STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION`. It does not
scientifically invalidate the frozen result, but validation is unsatisfied and
publication pauses. One retry is permitted only for the exact same
non-generative validation command after an independent executor-readiness
reviewer records that the first failure was transient, confirms the complete
envelope remained unchanged, and approves the exact retry command.

No edit, dependency change, environment mutation, cleanup, regeneration,
calibration, holdout execution, RNG command, or artifact-producing command may
occur between attempts. The sole permitted intervening command is one
authorized exact Log append recording the independent transient classification
and exact retry. That append advances only the guarded Log prefix. Holdout and
all scientific or artifact-generating commands are never retryable.

If the one retry exits zero with an unchanged envelope, record
`CONTINUE_FROZEN_CANDIDATE`. If it again exits nonzero without mutation,
record `STOP_NONMUTATING_VALIDATION_FAILURE`, preserve the namespace and all
immutable bytes, and stop publication without calling the scientific result
invalid. No second retry is permitted.
```

### 9.2 Literal Analytical Manifest

The 16-path analytical manifest remains exactly:

```text
AGENTS.md
README.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
pyproject.toml
scripts/run_synth_medium_latent_response_observation_recovery.py
spec/report_log.md
spec/synth_medium_latent_response_observation_recovery_gate.md
src/spatext/observe.py
src/spatext/synth/medium/__init__.py
src/spatext/synth/medium/latent_response_observation_recovery.py
tests/test_observe.py
tests/test_synth_medium_latent_response_observation_recovery.py
uv.lock
```

Do not discover membership by glob, import, `git ls-files`, current dirtiness,
or runtime scanning. The source digest receipt remains outside amendment and
byte-identical.

### 9.3 Acceptance Text

In Goal/spec `## Acceptance And Stop Rules`, append after the existing
acceptance paragraph and before the stop paragraph:

```markdown
Provenance acceptance additionally requires the complete per-command envelope,
exact pinned branch/HEAD/base and candidate-footprint guards at config emission,
freeze, pre-receipt, and pre-RNG, and a terminal disposition for every nonzero
validation under the one-retry rule. These are provenance gates only and
cannot alter a scientific gate or result.
```

## 10. Exact Tracked-Document Patch Map

### 10.1 Goal And Authoritative Spec

Apply one coordinated edit to both files after Task 2b handoff:

1. Insert the no-change clause from section 3 as the opening paragraph of a new
   `## Integrated Pre-Task-3 Contract Amendment` section immediately before
   `## Scenario Contract`.
2. Insert the scenario evidence registry at the section 4 anchor.
3. Insert latent diagnostics at the section 6 anchor.
4. Replace the complete `## Recommendation Precedence` body with section 7.4.
5. In `## Source And Artifact Contracts`, apply every schema and artifact
   replacement from sections 5 and 8; retain every unaffected field and rule.
6. Insert the provenance contract at the section 9 anchor.
7. Append the provenance acceptance paragraph at the section 9.3 anchor.
8. Preserve the Goal/spec body identity: apart from the spec's existing
   authority preamble and Goal's title, their amended bodies must remain
   byte-equivalent.

No current scientific paragraph is deleted except the complete obsolete
recommendation body and the literal schema/file-list text that the replacement
sections supersede.

### 10.2 Plan

Insert a new `## Integrated Pre-Task-3 Contract Amendment Gate` immediately
before `## Task 3: Pre-Holdout Scenarios, Artifacts, And Documentation`:

```markdown
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
```

Replace Task 3 steps 1-7 with:

```markdown
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
```

Replace Task 4's Log write-scope bullet with:

```markdown
- Goal 023 `Log.md` for append-only provenance records, including amendment
  supersession, reviewed hashes, freeze evidence, and immutable dispositions;
  no Log record may change science or analytical bytes.
```

Replace Task 4 steps 4-8 with:

```markdown
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
```

Replace Task 5 write scope and steps with:

```markdown
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
```

Replace Task 6 steps 1-5; keep step 6 unchanged:

```markdown
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
```

### 10.3 Runbook

Insert `## 2E. Integrated Pre-Task-3 Contract Amendment Seal` immediately
before `## 3. TDD Evidence`:

````markdown
## 2E. Integrated Pre-Task-3 Contract Amendment Seal

This integrated pre-Task-3 amendment changes no Goal 023 biological or
statistical model equation, estimand, natural support, generating value,
transition or emission timing convention, optimizer/profile rule, scenario ID,
schedule, effort rule, replicate count, predictive-reference count, bootstrap
count, seed payload or substream mapping, existing numerical recovery/coverage/
predictive threshold, transportability statement, or publication authority.

Do not begin this seal until Task 2b has a hash-specific independent acceptance
and releases the shared source/test/Log parent. Reproduce that parent before an
append. Append the supersession disposition from this amendment without
changing prior bytes, then apply the coordinated Goal/Plan/Runbook/spec patch.

Verify the literal correction surfaces:

```bash
rg -n "Scenario Evidence Registry And Fit Identity|fit_execution_evidence.csv|permuted_alignment|bootstrap_shared" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "transition_brier.expected_value|0.05\*\(H_x-L_x\)|ordinary_median\(B_1|recommendation-neutral" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
if rg -n "latent_time_thresholds|23/24|46/48.*latent|44/48.*latent" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md; then exit 1; fi
rg -n "structured_not_calibrated|sparse_honesty_failed|arrival_alignment_not_discriminated|continuous_abundance_silent_misspecification" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "represented_artifact_set_sha256|artifact_set_sha256|config_file_sha256|holdout_receipt_file_sha256" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION|complete.*envelope|before RNG" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/{Goal,Plan,Runbook}.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Run Goal/spec body equivalence, document hooks, `git diff --check`, exact
document/source/test hashes, source-receipt equality, and all no-exposure
checks. Append the integrated amendment record only with live hashes. Obtain
fresh scientific, statistical, executor-readiness, artifact/schema, code, and
provenance/freeze acceptance. Task 3 remains blocked until all are clean.
````

In `## 3. TDD Evidence`, append:

```markdown
Integrated-amendment RED/GREEN evidence must cover the complete matrix in the
accepted amendment proposal. Task 3 calibration dispatch tests are in-process,
injected, deterministic fixtures under `tmp_path`. They must assert
`holdout_payload_instantiated=false`, `scientific_rows_emitted=false`,
`rng_factory_call_count=0`, and `canonical_output_write_count=0`. They must not
call the live calibration runner or launch a production calibration subprocess.
Task 4 section 4 is the first live runtime benchmark and calibration owner.
```

In section 4, immediately before candidate config emission, insert:

```markdown
Before candidate config emission, run the implementation identity-and-footprint
guard. It must assert pinned branch, HEAD, and `origin/main`; reproduce the
literal 16-file manifest; require the exact phase-specific state within the
19-path publication-path universe; reject every out-of-allowlist untracked
non-ignored or other out-of-footprint path; and write no config on failure. The
emitted config must already contain the reproduced analytical digest before
`config_sha256` and `config_file_sha256` are computed.
```

Immediately before `freeze-tracked-state`, invoke the same guard. It must exit
nonzero on identity, manifest, status, or footprint mismatch while changing no
config byte and creating no preholdout receipt.

Replace section 5 through its final prose before section 6 with:

````markdown
## 5. Execute Holdout Once

Immediately before exclusive receipt creation, assert branch
`codex/spatext-goal023-latent-response-observation-gate`, HEAD and
`origin/main` commit
`53462d0365babf2c8070714a930f69b4071af276`; reproduce the 16-file manifest and
digest; require the exact holdout-pre-receipt presence state within the 19-path
publication-path universe; reject every out-of-allowlist untracked non-ignored
or other path; verify frozen config and preholdout receipt; and require the
holdout receipt to be absent. Fail before receipt creation on mismatch.

```bash
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase holdout \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
```

The command atomically creates the immutable tracked receipt before exposure.
After receipt creation and immediately before constructing any RNG object or
payload, it internally repeats identity, footprint, analytical digest, embedded
and file config hashes, preholdout-receipt file hash, and holdout-receipt
self/file hashes. Failure preserves the receipt, constructs no RNG, records
`STOP_INVALIDATED_POST_EXPOSURE`, and burns the namespace. On success, capture
the represented 21-file digest and external complete 22-file artifact snapshot.

Never delete the Goal 023 bundle, rerun holdout, or rerun an artifact-producing
command. A required analytical change invalidates publication and requires
Barry's approval plus a fresh seed namespace.
````

In section 6, add `fit_execution_evidence.csv` to the inspected tables and
require the exact 22-file set, represented 21-file verification manifest, and
complete external 22-file snapshot.

Replace the opening prose and command block of section 7 with:

````markdown
Do not regenerate data or change tracked analytical files. Before and after
each individual command below, capture and compare the complete provenance
envelope defined in Goal/spec. Do not guard the command block as one unit.

```bash
git diff --check
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run pre-commit run --all-files
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase verify \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase verify-tracked-state \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
git status --ignored --short artifacts dist
git status --short --branch --untracked-files=all
```

Accept only zero exit plus an unchanged envelope. Mutation is
`STOP_INVALIDATED_POST_EXPOSURE`. An unchanged nonzero is
`STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION` and pauses
publication. Retry the exact same non-generative command at most once, only
after independent transient classification, unchanged-envelope proof, and an
approved exact retry recorded by one guarded Log append. A successful retry is
`CONTINUE_FROZEN_CANDIDATE`; a second unchanged nonzero is
`STOP_NONMUTATING_VALIDATION_FAILURE` and stops publication without scientific
invalidation. Holdout and artifact-generating commands are never retryable.
````

After the section 8 `verify-staged-state` description, insert:

```markdown
Post-exposure `Log.md` appends are explicitly authorized provenance writes.
Guard each append as one command: the captured Log remains the exact prefix,
the suffix equals independently approved bytes, and every other envelope member
and non-Log staged blob remains unchanged. Exact staging may change only the
index to the predeclared allowlisted path/blob set and no working-tree byte.
```

At the start of section 9's final guard block, require the complete per-command
envelope and nonzero disposition rule. Preserve the existing branch/HEAD/base,
fast-forward, push, and stop rules unchanged.

### 10.4 Log

Do not edit or append `Log.md` while Task 2b owns the parent.

After Task 2b's accepted child is final, append one exact administrative record
at EOF. Compute the live parent line count, byte count, and SHA-256 immediately
before writing. The following is a generation template; angle-bracket tokens
must be replaced with live values before any byte is appended, and no token may
enter tracked Log text:

```markdown

## 2026-07-11 - Holdout-Provenance Interpretation Supersession

record_type: `holdout_provenance_binding_interpretation_v1_disposition`
parent_line_count: `<live decimal parent line count>`
parent_byte_count: `<live decimal parent byte count>`
parent_sha256: `<live lowercase SHA-256>`
target_record_type: `holdout_provenance_binding_interpretation_v1`
target_record_start_line: `2069`
target_record_end_line: `2222`
status: `superseded_pending_amendment`

The target interpretation remains preserved byte for byte but is not authority
for holdout exposure. Independent review found unresolved provenance execution
gaps: explicit post-exposure Log authorization in tracked authority, complete
immutable-byte guards around every post-exposure command, pinned identity and
candidate-footprint guards at config emission/freeze/pre-receipt/pre-RNG, and a
terminal disposition plus controlled one-retry rule for unchanged nonzero
validation. This disposition changes no science and authorizes no holdout
construction or exposure. Holdout remains blocked pending the integrated
tracked amendment, executable non-holdout tests, hash resealing, and fresh
hash-specific acceptance.
```

Before append, reproduce all three parent values and verify lines `2069..2222`
remain byte-identical. If the parent differs, regenerate only the administrative
record against the live parent. Never insert, delete, rewrite, reorder, or
backfill an earlier byte.

After the coordinated tracked amendment, tests, validation, and reviews are
final, append a separate
`integrated_pre_task3_contract_amendment_v1` record. It must bind the then-live
Log parent; amended Goal/Plan/Runbook/spec hashes; accepted Task 2b source/test
hashes; pinned branch/HEAD/base; unchanged source-receipt hash; exact RED/GREEN
and validation commands/results; reviewer roles and hash-specific dispositions;
and one of:

```text
BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION
BINDING_ACCEPTED_PRE_TASK3
```

Do not put guessed hashes, mutable status, or placeholders in tracked Log text.

## 11. Ordered RED Test Matrix

All tests use deterministic injected arrays, typed result fixtures, fake files,
fake git/status providers, injected command runners, RNG-factory spies, and
`tmp_path`. No test constructs, derives, previews, hashes, or inspects a Goal
023 holdout payload. A RED failure must identify the missing behavior, not a
missing import, unavailable future artifact, live optimizer run, or fixture
setup error.

### 11.1 Registry, Truth Firewall, And Fit Identity

| ID | Test | Required RED behavior |
| --- | --- | --- |
| `T3A-001` | `test_lro_3a_001_scenario_registry_truth_access_scope_and_variants_are_literal` | Require the exact 11-row section 4 mapping and canonical order. |
| `T3A-002` | `test_lro_3a_002_truth_access_rejects_missing_extra_reordered_or_unknown` | Reject every incomplete, duplicate, reordered, or invalid enum mapping. |
| `T3A-003` | `test_lro_3a_003_stress_truth_cannot_enter_analyst_fit` | Reject original alignment, dropout state, Goal 018 abundance, and frailty from analyst APIs. |
| `T3A-004` | `test_lro_3a_004_control_truth_cannot_enter_starts_objective_or_profiles` | Prove zero/equal generating labels cannot influence fitting. |
| `T3A-005` | `test_lro_3a_005_fit_execution_schema_key_sort_and_failure_rows_are_literal` | Require the exact v3 36-column normalized fit/design schema, seven-part key, typed failure class, explicit row-kind/design-kind sort, result-derived cell-frame binding, and retained failed rows. This fully supersedes the proposal's original 23-column/five-part and later 35-column behavior while preserving the assigned node name and manifest position. |
| `T3A-006` | `test_lro_3a_006_fit_variant_is_in_every_fit_derived_primary_key` | Require all six amended table keys and registry-consistent variants. |
| `T3A-007` | `test_lro_3a_007_arrival_emits_complete_correct_permuted_pairs` | Require two fit rows per attempt, fixed disjoint frames, and no dropped failed pair. |
| `T3A-008` | `test_lro_3a_008_arrival_primary_tables_use_permuted_only` | Reject comparator recovery/profile/latent/predictive rows. |
| `T3A-009` | `test_lro_3a_009_equal_shared_fits_have_no_fake_replicate_id` | Require two scenario-shared rows, exact source ranges, and typed closed-form/multistart evidence. |
| `T3A-010` | `test_lro_3a_010_equal_bootstrap_pairs_are_complete_and_recomputable` | Require 199 equal/ordered row pairs and exact `D`, `D_b`, p reconstruction. |
| `T3A-011` | `test_lro_3a_011_every_primary_science_row_reconciles_to_one_fit_row` | Enforce cross-table foreign keys, issued 4180-cell arrival fit frames before optimization, mathematical 1x3/2x3 rejection, typed result constructors, every explicit fit/design transition on the complete 990/1695 bundle, and no orphan/duplicate/contradictory row before reduction. |

### 11.2 Latent Diagnostics

| ID | Test | Required RED behavior |
| --- | --- | --- |
| `T3L-001` | `test_lro_3l_001_event_censor_indices_and_126_label_are_literal` | Require exact 21-category mapping and nonbiological censor-label semantics. |
| `T3L-002` | `test_lro_3l_002_one_hot_event_and_censor_score_zero` | All observed and expected values are exactly zero. |
| `T3L-003` | `test_lro_3l_003_one_category_displacement_scores_point_zero_five_six_six` | Require Brier `0.05`, interval `6`, median error `6`. |
| `T3L-004` | `test_lro_3l_004_event_six_vs_censor_scores_one_one_twenty_one_twenty` | Require extreme ordered penalties. |
| `T3L-005` | `test_lro_3l_005_brier_and_expected_value_match_hand_calculation` | Verify cumulative score and `F*(1-F)` expected value. |
| `T3L-006` | `test_lro_3l_006_discrete_quantiles_use_first_crossing` | Cover 5th/50th/95th ties and censor endpoint. |
| `T3L-007` | `test_lro_3l_007_scaled_interval_expected_value_matches_21_path_enumeration` | Verify the `0.05`-scaled formula and exact expected value. |
| `T3L-008` | `test_lro_3l_008_odd_even_medians_and_bayes_risk_are_literal` | Verify ordinary median and median of cellwise Bayes risks. |
| `T3L-009` | `test_lro_3l_009_process_oracle_probabilities_precede_truth` | Oracle truth changes scores only, never path probabilities or fit. |
| `T3L-010` | `test_lro_3l_010_batched_and_scalar_weights_score_identically` | Cover dense, structured, sparse, and irregular fixtures. |
| `T3L-011` | `test_lro_3l_011_empty_histories_retain_process_paths_and_cells` | No-count cells remain in the fixed frame. |
| `T3L-012` | `test_lro_3l_012_censored_truth_remains_in_every_denominator` | No censor/event complete-case filtering. |
| `T3L-013` | `test_lro_3l_013_invalid_probability_or_truth_fails_complete_diagnostic` | Reject shuffled/missing/extra/duplicate/nonfinite/negative/bad-sum rows without dropping cells. |
| `T3L-014` | `test_lro_3l_014_applicability_and_frame_sizes_are_literal` | Require the exact section 6 scenario statuses and `5225/1306/1045/0` sizes. |
| `T3L-015` | `test_lro_3l_015_failed_fit_retains_three_diagnostic_unavailable_rows` | Fixed sample size, null values, diagnostic result, no fallback. |
| `T3L-016` | `test_lro_3l_016_inapplicable_attempts_emit_three_not_applicable_rows` | Observation oracle, equal emission, and continuous abundance emit N/A rows, not zeros. |
| `T3L-017` | `test_lro_3l_017_metric_values_and_availability_never_change_recommendation` | Parameterize different finite in-range values and valid unavailable rows; prove identical local/global class. |
| `T3L-018` | `test_lro_3l_018_missing_or_malformed_row_is_schema_failure_only` | Distinguish artifact contract from scientific metric neutrality. |
| `T3L-019` | `test_lro_3l_019_no_latent_threshold_object_or_pass_count_exists` | Reject threshold config, pass/fail latent results, and aggregate pass counts. |
| `T3L-020` | `test_lro_3l_020_valid_fit_with_failed_prerequisite_or_invalid_posterior_is_unavailable_diagnostic` | Retain fixed rows/sample size, literal fit status, null values, and recommendation neutrality. |

### 11.3 Denominators, Controls, And Stress Rows

| ID | Test | Required RED behavior |
| --- | --- | --- |
| `T3D-001` | `test_lro_3d_001_nested_denominators_imputations_and_even_median_are_literal` | Require all 48 rows, full widths, uncovered states, and finite-only signed median. |
| `T3D-002` | `test_lro_3d_002_nested_coverage_and_convergence_boundaries_are_unchanged` | Require `36/35`, `46/45`, and `44/43` boundaries. |
| `T3D-003` | `test_lro_3d_003_missing_recovery_row_is_contract_failure_not_imputation` | Missing artifact row reaches rank 1. |
| `T3D-004` | `test_lro_3d_004_sparse_coverage_and_width_use_all_24` | Require `18..24`, width `6`, and positions 12/13. |
| `T3D-005` | `test_lro_3d_005_sparse_equal_width_passes_next_value_below_fails` | Preserve inclusive honest-width boundary. |
| `T3D-006` | `test_lro_3d_006_sparse_failed_fit_cannot_be_rescued_by_imputation` | Predictive/availability failure remains rank 1. |
| `T3D-007` | `test_lro_3d_007_sparse_low_error_or_24_coverage_adds_no_gate` | Descriptive strength cannot fail or rescue honesty. |
| `T3D-008` | `test_lro_3d_008_zero_driver_touching_zero_is_not_exclusion` | Lower/upper zero and straddling intervals contain zero. |
| `T3D-009` | `test_lro_3d_009_zero_driver_six_passes_seven_confounds` | Require 24 decidable intervals and exact rank outcomes. |
| `T3D-010` | `test_lro_3d_010_zero_driver_failed_open_missing_are_undecidable` | Null event, attempted 24, no binomial decision, rank 1. |
| `T3D-011` | `test_lro_3d_011_known_truth_stress_recovery_is_descriptive_full_denominator` | Verify imputation, null bounds, and no new recovery threshold. |
| `T3D-012` | `test_lro_3d_012_continuous_abundance_has_no_parameter_truth_claim` | Require null truth/coverage/error and retained estimate/width evidence. |
| `T3D-013` | `test_lro_3d_013_control_summary_denominators_reconcile_to_fit_evidence` | Recompute zero, arrival, and equal attempted/evaluable/event/bootstrap counts. |
| `T3D-014` | `test_lro_3d_014_failed_predictive_fit_emits_27_unavailable_rows` | Require a module-issued production/fixture opportunity adapter and canonical cell/time/exact-effort/quality/time-band/keyed-keep serialization; derive all three same-n metrics from retained objects; reject equal-cardinality quality/time swaps, effort, size/digest/metric/frame, and keyed-mask mutations before summary; retain failed-fit 27-row denominator behavior. |

### 11.4 Scenario Reducers And Totality

| ID | Test | Required RED behavior |
| --- | --- | --- |
| `T3R-001` | `test_lro_3r_001_each_oracle_failure_maps_to_model_contract_failed` | Parameterize every oracle/design/recovery/artifact failure. |
| `T3R-002` | `test_lro_3r_002_dense_complete_scientific_failure_maps_to_confounding` | Both oracles pass; valid dense scientific failures reach rank 2. |
| `T3R-003` | `test_lro_3r_003_structured_recovery_only_failure_maps_to_observation_limited` | Only existing median error/width fails; rank 3. |
| `T3R-004` | `test_lro_3r_004_structured_coverage_predictive_fit_or_plugin_failure_is_rank_one` | Include 35/48, failed fit, unavailable cell, scientific predictive rejection, plug-in design rank `2`, condition `1e8`, and unavailable plug-in. |
| `T3R-005` | `test_lro_3r_005_structured_accepted_estimand_unidentified_is_rank_two` | Complete valid evidence with non-control unidentification maps to confounding. |
| `T3R-006` | `test_lro_3r_006_sparse_honesty_failure_is_rank_one` | Parameterize coverage, width, fit, predictive, and row failures. |
| `T3R-007` | `test_lro_3r_007_alignment_correlation_boundary_and_availability_are_rank_one` | `abs=0.25` valid; next/nonfinite/missing pair unavailable rank 1. |
| `T3R-008` | `test_lro_3r_008_alignment_22_wins_passes_21_confounds` | Complete valid evidence and warning; exact rank 4 vs rank 2 vector. |
| `T3R-009` | `test_lro_3r_009_alignment_warning_is_mandatory_and_scientific` | No/forced warning rank 1; one available warning satisfies. |
| `T3R-010` | `test_lro_3r_010_equal_p_boundary_refit_completeness_and_status_independence` | `p=0.05`, just below, failed refit, fixed six statuses. |
| `T3R-011` | `test_lro_3r_011_dropout_and_frailty_warning_is_conditional_on_narrow_wrong` | No narrow wrong/no warning passes; narrow wrong/no warning rank 1; broad wrong remains descriptive. |
| `T3R-012` | `test_lro_3r_012_continuous_abundance_warning_is_mandatory` | Complete with warning passes; complete without warning rank 1. |
| `T3R-013` | `test_lro_3r_013_each_control_and_stress_is_required_for_top_pass` | Remove/fail scenarios 6-11 individually and make rank 4 unreachable. |
| `T3R-014` | `test_lro_3r_014_rank_three_requires_every_nonstructured_gate` | Fail sparse, either control, or any stress from rank-3 vector and lose rank 3. |
| `T3R-015` | `test_lro_3r_015_rank_precedence_and_canonical_reasons_are_stable` | Rank 1 beats 2/3; rank 2 beats 3; retain all reasons in order. |
| `T3R-016` | `test_lro_3r_016_unknown_missing_duplicate_or_contradictory_never_passes` | Fail closed with specific or catch-all rank-1 reason. |
| `T3R-017` | `test_lro_3r_017_local_and_global_reducers_are_total` | Every finite enum vector yields exactly one local impact and one rank. |
| `T3R-018` | `test_lro_3r_018_transportability_class_is_invariant` | All four terminal ranks retain the bridge class. |
| `T3R-019` | `test_lro_3r_019_every_stress_fit_plugin_or_predictive_unavailability_is_rank_one` | Parameterize scenarios 7 and 9-11 over every required availability failure. |
| `T3R-020` | `test_lro_3r_020_all_required_global_and_scenario_gates_pass_reaches_rank_four` | Prove the top class is reachable only from one complete valid vector. |

### 11.5 Artifact, Hash, CLI, And Determinism

| ID | Test | Required RED behavior |
| --- | --- | --- |
| `T3S-001` | `test_lro_3s_001_exact_22_file_manifest_and_null_config_hashes` | Reject 21/23, missing/extra/duplicate/reordered entries and non-null pre-emission hashes. |
| `T3S-002` | `test_lro_3s_002_verification_represents_other_21_files` | Exclude itself and reproduce represented digest. |
| `T3S-003` | `test_lro_3s_003_external_snapshot_includes_all_22_files` | Detect any represented/verification/missing/extra/zero-byte mutation. |
| `T3S-004` | `test_lro_3s_004_config_and_receipt_self_hashes_are_not_file_hashes` | Reproduce each exact identity and reject swaps. |
| `T3S-005` | `test_lro_3s_005_phase_guards_require_typed_hash_identities` | Reject raw dicts, unchecked paths, and ambiguous hashes. |
| `T3S-006` | `test_lro_3s_006_task3_calibration_dispatch_smoke_is_fixture_only` | Exercise parser/dispatch/forwarding with all four zero counters. |
| `T3S-007` | `test_lro_3s_007_task3_smoke_cannot_reach_live_calibration_runner` | A live-runner bomb is never called. |
| `T3S-008` | `test_lro_3s_008_task4_is_first_live_benchmark_and_calibration_owner` | No Task 3 production subprocess or scientific row. |
| `T3S-009` | `test_lro_3s_009_scenario_definitions_use_contract_order` | Preserve numbered order and repeated bytes. |
| `T3S-010` | `test_lro_3s_010_two_fixture_bundles_are_byte_identical` | Permuted task input and fake 1/8-worker completion produce identical 22 files. |

### 11.6 Provenance And Freeze

| ID | Test | Required RED behavior |
| --- | --- | --- |
| `T3P-001` | `test_post_exposure_log_append_accepts_exact_provenance_suffix_and_parent` | Prove explicit authority, exact prefix/suffix, bindings, and no other mutation. |
| `T3P-002` | `test_post_exposure_log_append_rejects_prefix_change_or_analytical_payload` | Reject insertion/deletion/rewrite/wrong parent/unapproved or scientific suffix. |
| `T3P-003` | `test_post_exposure_zero_exit_requires_complete_unchanged_envelope` | Zero exit alone is insufficient. |
| `T3P-004` | `test_post_exposure_nonzero_without_mutation_allows_one_approved_exact_retry` | Require pending disposition, independent approval, exact command, and no intervening change. |
| `T3P-005` | `test_post_exposure_second_nonmutating_nonzero_stops_without_invalidation` | Terminal stop, immutable state, no second retry, scientific disposition unchanged. |
| `T3P-006` | `test_post_exposure_mutation_invalidates_for_zero_or_nonzero_exit` | Any mutation invalidates and forbids retry/restore. |
| `T3P-007` | `test_post_exposure_guard_detects_each_immutable_byte_class` | Parameterize analytical file, Log prefix, both receipts, config, represented/complete artifacts, identity, index, status, and footprint. |
| `T3P-008` | `test_post_exposure_guard_wraps_each_command_not_batch` | Mutation between successful commands cannot escape. |
| `T3P-009` | `test_config_emission_fails_closed_on_identity_or_footprint_mismatch` | Wrong branch/HEAD/base/manifest/status or out-of-allowlist path writes no config. |
| `T3P-010` | `test_freeze_fails_closed_on_identity_or_footprint_mismatch` | Config bytes remain exact and no preholdout receipt exists. |
| `T3P-011` | `test_holdout_pre_receipt_guard_fails_before_receipt_and_rng` | Every mismatch creates neither receipt nor RNG/payload. |
| `T3P-012` | `test_holdout_post_receipt_guard_failure_burns_namespace_before_rng` | Receipt remains; RNG factory count zero; invalidated disposition. |
| `T3P-013` | `test_holdout_success_freezes_represented_and_complete_artifact_snapshots` | Require 21-file represented and 22-file complete hashes. |
| `T3P-014` | `test_holdout_and_artifact_generating_commands_are_never_retryable` | Retry dispatcher rejects both classes. |
| `T3P-015` | `test_allowed_new_candidate_paths_are_hashed_but_extra_untracked_path_fails` | Preserve unstaged pre-freeze workflow while rejecting unknown footprint. |
| `T3P-016` | `test_exact_staging_changes_only_predeclared_index_blobs` | No working byte or unexpected index member changes. |
| `T3P-017` | `test_authorized_commit_merge_and_push_transitions_are_literal` | Permit only approved parent/tree/fast-forward/ref transitions. |
| `T3P-018` | `test_candidate_footprint_presence_vector_is_phase_specific` | Require 17 present before freeze, 18 before holdout receipt, and all 19 after receipt, with the exact receipt absences. |
| `T3P-019` | `test_supersession_record_preserves_log_target_and_binds_live_parent` | Require target lines 2069-2222 unchanged, exact live parent values, and status `superseded_pending_amendment`. |
| `T3P-020` | `test_holdout_receipt_exposure_fields_self_hash_and_later_invalidation_are_immutable` | Freeze receipt-time meanings and reject every attempted rewrite after exposure. |
| `T3P-021` | `test_task6_validation_dispatch_is_postholdout_only` | Prohibit benchmark, calibration, regeneration, and section 4 dispatch after exposure. |
| `T3P-022` | `test_terminal_attestation_is_exactly_reviewed_appended_and_staged_once` | Prove no recursive second attestation or post-approval append. |
| `T3P-023` | `test_potentially_mutating_hooks_are_noops_before_freeze` | Any formatter/hook byte or index mutation returns to pre-freeze RED-GREEN work. |

Suggested focused command after Task 2b acceptance and amendment RED creation:

```bash
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py \
  -k 'lro_3a or lro_3l or lro_3d or lro_3r or lro_3s or post_exposure or config_emission or freeze_fails or holdout_pre_receipt or holdout_post_receipt or holdout_success' \
  --no-cov
```

## 12. Validation, Review, And Application Order

Apply only after the accepted Task 2b handoff:

1. Reproduce the live Log parent and append the exact supersession disposition.
2. Apply the coordinated Goal/Plan/Runbook/spec, implementation, and test patch.
3. Run each strict RED group and record behavior-specific failure evidence.
4. Implement minimum GREEN behavior without changing any frozen science.
5. Generate two complete fixture-only 22-file bundles under separate temporary
   directories and compare them byte for byte.
6. Run focused Task 2a/2b/3 tests and the complete non-generative pre-Task-3
   validation ladder. Do not run live benchmark, calibration, or holdout.
7. Compute live document/source/test hashes and append the integrated amendment
   record against the then-live Log parent.
8. Obtain independent reviews:
   - scientific: latent formulas, censor category, scenario interpretation;
   - statistical: denominators, proper-score expected values, controls, total
     reducer;
   - artifact/schema: every field, key, enum, sort, foreign key, and hash;
   - executor-readiness/code: fixture boundary, typed failures, totality;
   - provenance/freeze: every checkpoint, byte class, disposition, retry;
   - final: exact candidate and no unapproved scope.
9. Resolve every Critical or Important finding through a new RED-GREEN cycle,
   reseal hashes, and repeat affected reviews.
10. Mark Task 3 ready only when every review returns hash-specific `ACCEPT` and
    all non-generative validation is clean.

Stop if implementation would require a new estimator, parameter, profile,
support, schedule, replicate/reference/bootstrap count, seed mapping, existing
numeric threshold, latent pass threshold, truth-bearing analyst field, fifth
recommendation class, extra artifact, dependency, real data, remote compute, or
holdout payload.

## 13. Contradiction Audit And Barry-Level Decision

Under the fixed orchestrator choices, the six pre-Task-3 analyses have no
remaining scientific or strategic contradiction:

- latent formulas and missingness are exact, while their recommendation effect
  is explicitly null;
- the four-class reducer is total and fail-closed;
- structured plugin failures are explicitly rank 1, removing the one ambiguity
  left in the draft decision proposal;
- every control and stress has a required top-pass role;
- fit variants and shared fits have non-null identities;
- Task 3 calibration smoke is fixture-only and Task 4 owns first live science;
- verification and the external artifact snapshot close self-reference;
- post-exposure Log appends, complete envelopes, identity/footprint guards, and
  unchanged-nonzero retry have literal mechanics; and
- the accepted candidate-footprint rule reconciles required new unstaged files
  with fail-closed rejection of unknown untracked paths before section 8 exact
  staging.

No Barry-level scientific or strategic decision is unavoidable to apply this
amendment. Barry remains required only under the already frozen authority if a
future live runtime/resource gate fails, an exposed namespace is invalidated
and a fresh namespace is requested, or implementation discovers a genuinely
new material scientific assumption or strategic trade-off.

## 14. Proposal Self-Review

- No tracked file, live Log parent, scientific row, RNG object, calibration,
  artifact, receipt, holdout payload, staging state, commit, or publication was
  changed by this proposal.
- No quantitative latent threshold or fifth recommendation was introduced.
- All existing numeric scientific gates remain literal.
- Every requested schema field, primary key, enum, truth map, total decision
  branch, formula, denominator, missingness state, artifact hash, provenance
  checkpoint, and RED behavior is explicit.
- All future Log hashes are deliberately live-bound; no placeholder is allowed
  to enter tracked Log text.
- Task 2b retains sole ownership of the current source/test/Log parent until its
  accepted handoff.
