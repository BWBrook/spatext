# Goal 023 Task 3 Decision-Logic Proposal

status: `PROPOSAL_COMPLETE_AUTHORITY_AMENDMENT_REQUIRED`
date: `2026-07-11`
worktree: `/Users/bwbrook/.codex/worktrees/spatext/goal023`
branch: `codex/spatext-goal023-latent-response-observation-gate`
HEAD/base: `53462d0365babf2c8070714a930f69b4071af276`

## Scope And Authority

This proposal resolves only the Task 3 recommendation, scenario-gate,
denominator, missingness, and truth-access gaps identified by
`.superpowers/sdd/task-3-scenario-gate-preflight.md`. It does not run a
scenario, instantiate calibration or holdout payloads, inspect future output,
or implement Task 3.

The proposal was derived from the frozen authority tuple verified in this
worktree:

| Surface | SHA-256 |
| --- | --- |
| Goal | `cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20` |
| Plan | `df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e` |
| Runbook | `78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed` |
| authoritative spec | `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d` |
| Task 2b preflight | `395d6cc9960d2c0a8f9f95a92b4b0e22e070b71c8a59910926aa7fae1b97bed9` |

Task 3 remains blocked on the accepted Task 2b hash-specific handoff and the
other independent preflight gaps. This proposal must be incorporated into the
frozen Goal/spec/Plan/Runbook before the first Task 3 RED test.

## Decision

Preserve the four existing recommendation classes. No fifth class is logically
necessary if `model_contract_failed` remains the conservative terminal class
for required evidence that is invalid, unavailable, unsafe, or inconsistent
with a preregistered gate.

Use a two-stage state machine:

1. Reduce every global gate and each of the 11 scenarios to one typed local
   impact: `contract_failure`, `confounding`, `structured_limitation`, or
   `pass`.
2. Fold all local impacts by the frozen recommendation precedence. Missing,
   unknown, contradictory, or unevaluated required input is
   `contract_failure`; there is no default-to-pass branch.

The four terminal recommendations retain their present names and ranks:

| Rank | Recommendation | Exact role |
| ---: | --- | --- |
| 1 | `model_contract_failed` | Required evidence is invalid, unavailable, uncalibrated, silently misspecified, or violates a frozen gate not assigned a more specific scientific interpretation. |
| 2 | `process_observation_confounded` | Valid, complete evidence demonstrates false process signal, accepted-estimand nonidentification, dense joint failure, or failure to distinguish correct from permuted driver alignment. |
| 3 | `observation_limited_but_calibrated` | Dense passes and the only nested failure is structured accuracy/precision, while structured coverage, identification, fit availability, and predictive calibration remain valid. |
| 4 | `latent_response_observation_gate_passed` | Every required global, nested, sparse, control, and stress gate passes. |

Always emit
`transportability_class=scheduled_count_only_point_process_bridge_required`,
independent of the terminal recommendation.

### Alternatives rejected

1. Add `classification_inconclusive` as a fifth recommendation. This is not
   needed: machine-readable reason codes can distinguish scientific surprise
   from software or provenance failure while the conservative terminal result
   remains `model_contract_failed`.
2. Widen `observation_limited_but_calibrated` to include structured coverage,
   predictive, or plug-in failures. This would contradict the word
   `calibrated` and could turn unidentification or predictive invalidity into a
   reassuring recommendation.
3. Leave unmatched outcomes blocked at runtime. This is safe during preflight
   but is not a total implementation contract and risks a later accidental
   pass default.

## Canonical Truth-Access Mapping

The enum is mutually exclusive at the scenario row even though every ordinary
joint fit remains analyst-firewalled. `stress_evaluator_only` is the stronger
label for scenarios whose hidden stress construction or correct comparator
must remain evaluator-only.

| # | Scenario ID | `truth_access_class` | Exact access rule |
| ---: | --- | --- | --- |
| 1 | `process_oracle_observed_transition` | `oracle_only` | The nondeployable process-oracle API may receive true event/censor outcomes. No counts or observation rates enter the fit. |
| 2 | `observation_oracle_fixed_transition` | `oracle_only` | The nondeployable observation-oracle API may receive fixed true transitions with analyst-visible counts/effort. |
| 3 | `dense_count_exact_model` | `analyst_firewalled` | The ordered-joint estimator receives only analyst history fields. Generating states, transitions, and parameters remain evaluator-only. |
| 4 | `structured_imperfect_effort` | `analyst_firewalled` | As scenario 3, with known structured effort as an analyst field. |
| 5 | `sparse_expected_failure` | `analyst_firewalled` | The truth-independent sparse frame and analyst histories enter fitting; truth is used only after fitting for honesty evaluation. |
| 6 | `zero_driver_effect_negative_control` | `analyst_firewalled` | The estimator receives normal `TP(x)` and is not told that generating `beta_driver=0`; zero is evaluator truth for the control decision. |
| 7 | `permuted_arrival_alignment_stress` | `stress_evaluator_only` | The primary estimator receives the permitted permuted analyst covariate. Original alignment, permutation audit, correct-fit comparator, and paired-score decision stay in the stress evaluator. |
| 8 | `no_emission_contrast_negative_control` | `analyst_firewalled` | Shared equal and ordered fits consume counts, effort, `Q`, and `TP`; generating equal-emission truth and fixed structural labels do not enter starts or the ordered objective. |
| 9 | `informative_dropout_misspecification_stress` | `stress_evaluator_only` | The analyst sees the retained frame only. True state, dropout mechanism, and complete pre-dropout opportunities stay in the stress evaluator. |
| 10 | `goal018_continuous_abundance_stress` | `stress_evaluator_only` | Goal 018 abundance/extirpation and `q` construction stay in the stress evaluator; the fitted binary model receives only the resulting analyst history. |
| 11 | `spatial_frailty_stress` | `stress_evaluator_only` | The frailty field and intensity multiplier stay in the stress evaluator; the fitted independent-cell model never receives either. |

Truth may be used by an evaluator to generate data, compute a preregistered
truth-based diagnostic, and assign a gate after fitting. It must never affect
analyst schedules, starts, bounds, objectives, profile starts, tie-breaking,
predictive references, or row ordering. Scenario 7's permitted permuted
analyst covariate is the sole stress-derived estimator input; its original
alignment remains evaluator-only.

## Common Evidence States

Every attempted row must exist exactly once. Distinguish these states rather
than collapsing them:

| State | Meaning | General treatment |
| --- | --- | --- |
| `available` | Required fit/result is converged, finite, schema-valid, and applicable. | Evaluate the scientific gate. |
| `nonconverged` | Attempt ran but did not meet the frozen fit-success contract. | Retain the attempt; apply the scenario's explicit imputation or availability failure. |
| `nonfinite` | Objective, estimate, interval, score, or diagnostic is nonfinite. | Retain nullable fields plus explicit flags; fail the applicable availability/contract gate. |
| `open_profile` | A valid profile reaches a natural support edge without closing. | Retain as an honest open interval; apply the frozen full-support imputation where specified. |
| `missing_result` | A required row, fit variant, profile result, or diagnostic was never emitted. | Artifact/schema contract failure. It is never treated as an ordinary open profile. |
| `not_applicable` | Authority explicitly excludes the output. | Emit the frozen N/A representation; do not create a denominator. |

An unavailable or forced warning caused by failed computation is not a
scientific predictive warning and cannot satisfy a stress's required-warning
rule. Define:

```text
predictive_complete =
    every attempted replicate has a successful finite required fit
    and all 27 cells are valid and diagnostically available

scientific_warning_detected =
    predictive_complete
    and at least one available cell triggers the frozen Holm, Stouffer,
        or finite scientific-warning rule
```

## Exact Denominator And Missingness Rules

In the rules below, a `missing estimate` or `missing interval` means the
attempted row exists with the applicable nullable result field unavailable. A
missing or duplicate attempted row is always `missing_result` and therefore an
artifact/schema contract failure.

| # | Scenario | Fit/recovery denominator | Predictive denominator | Other decisive denominator |
| ---: | --- | --- | --- | --- |
| 1 | process oracle | 48 attempts x 3 parameters | none | convergence over 48 |
| 2 | observation oracle | 48 attempts x 2 parameters | 48 attempts x 27 cells, diagnostic only | convergence over 48 |
| 3 | dense exact | 48 attempts x 5 parameters | 48 attempts x 27 cells | convergence over 48 |
| 4 | structured exact | 48 attempts x 5 parameters | 48 attempts x 27 cells | convergence over 48 |
| 5 | sparse | 24 attempts x 5 descriptive parameters; `beta_driver` is decisive | 24 attempts x 27 cells | 24 `beta_driver` coverage/width attempts |
| 6 | zero driver | 24 attempts x 5 parameters; `beta_driver` is decisive | 24 attempts x 27 cells | 24 attempted `beta_driver` intervals; all 24 must be decidable |
| 7 | arrival alignment | 24 primary permuted fits/profiles; comparator has no recovery claim | 24 primary attempts x 27 cells | 24 paired correct/permuted scores |
| 8 | equal emission | one shared equal fit and one shared ordered fit over all 24 attempts; no profiles | 24 attempts x 27 cells, diagnostic only | 199 complete bootstrap bundles; p denominator 200 |
| 9 | informative dropout | 24 attempts x 5 descriptive known-parameter rows | 24 attempts x 27 cells | narrow-wrong evaluation over emitted finite/closed intervals |
| 10 | continuous abundance | 24 attempts x 5 descriptive profile rows; no recovery truth | 24 attempts x 27 cells | at least one scientific warning |
| 11 | spatial frailty | 24 attempts x 5 descriptive known-parameter rows | 24 attempts x 27 cells | narrow-wrong evaluation over emitted finite/closed intervals |

### Nested scenarios 1-4

- Use all 48 attempted holdout replicates for each applicable parameter.
- Convergence numerators use successful finite fits; denominators remain 48.
- Coverage uses 48 Boolean attempts. A nonconverged/nonfinite fit or an
  open/missing interval is uncovered.
- For absolute error, a nonconverged fit or missing estimate is imputed with the
  parameter's full support width: `8`, `6`, `4`, `0.99`, or `9.75`.
- For interval width, a nonconverged fit or open/missing interval is imputed
  with the same full support width.
- Median and maximum absolute error and interval width use all 48 imputed
  values. The even-sample median is the mean of ordered positions 24 and 25.
- Median signed error uses finite converged estimates only and is null when no
  such estimate exists.
- Coverage acceptance is inclusive `36..48` for every one of the 15 nested
  parameter families.
- Convergence minima are scenario 1 `46/48`, scenario 2 `46/48`, scenario 3
  `46/48`, and scenario 4 `44/48`.

An absent or duplicate recovery row is not imputed. It is
`model_contract_failed` through the artifact/schema gate.

### Sparse honesty

Use all 24 attempted holdout replicates for the dedicated `beta_driver` gate:

```text
sparse_coverage_pass = 18 <= coverage_count <= 24
sparse_width_pass = sparse_imputed_median_width >= structured_imputed_median_width
sparse_honesty_pass =
    sparse_predictive_pass
    and sparse_coverage_pass
    and sparse_width_pass
```

- Nonconverged/nonfinite fits and open/missing `beta_driver` intervals are
  uncovered.
- Nonconverged fits and open/missing intervals contribute width `6`.
- Sort all 24 widths and average one-based positions 12 and 13.
- A failed/nonfinite required fit emits all attempted rows and fails the sparse
  predictive gate; imputed width `6` cannot rescue it.
- Width equal to the structured median passes. Width smaller by any positive
  amount is `sparse_unexpectedly_narrow` and maps to
  `model_contract_failed`.
- Coverage `24/24`, low median error, or high convergence is not by itself a
  failure. No authority defines a separate "too good" error gate, and the
  proposal does not invent one. The preregistered honesty claim is exactly
  calibrated `beta_driver` coverage plus no narrower median interval than the
  structured scenario.
- Other sparse parameter recovery summaries are descriptive and cannot rescue
  or fail the dedicated honesty Boolean.

### Zero-driver control

Use 24 attempted `beta_driver` profiles and separate interval availability from
the false-signal decision:

```text
interval_decidable =
    fit is successful and finite
    and both interval endpoints are finite and closed

excludes_zero = interval_lower > 0 or interval_upper < 0
zero_driver_availability_pass = decidable_interval_count == 24
zero_driver_false_signal_pass =
    zero_driver_availability_pass and 0 <= exclusion_count <= 6
```

- A finite closed interval touching zero contains zero and is not an exclusion.
- A nonconverged/nonfinite fit or open/missing interval has
  `excludes_zero=null`, not `false` and not `true`.
- Such an attempt remains one of 24, makes
  `zero_driver_availability_pass=false`, prevents the exact binomial decision,
  and maps to `model_contract_failed`.
- When all 24 intervals are decidable, `0..6` exclusions pass and `7..24`
  exclusions map to `process_observation_confounded`.
- A required-fit or standard-predictive failure maps to
  `model_contract_failed`, even if the available intervals show at most six
  exclusions.

This avoids both unsafe alternatives: counting instability as evidence of no
false signal, or relabelling numerical attrition as a scientific false signal.

### Alignment stress

- Use 24 paired attempts. Each pair requires successful finite correct and
  permuted fits and finite heldout scores on the fixed score frame.
- A failed pair remains attempted and contributes no correct-alignment win.
  It also fails availability, so the recommendation is
  `model_contract_failed`; a low win count cannot disguise that failure as
  scientific confounding.
- With complete availability, `22..24` correct-alignment wins pass and `0..21`
  map to `process_observation_confounded`.
- Finite absolute alignment correlation `<=0.25` is valid. Nonfinite
  correlation or any value `>0.25` invalidates construction and maps to
  `model_contract_failed`.
- Only the primary permuted fit supplies profiles and predictive references.
  The correct fit is score-comparator evidence only.
- At least one available scientific predictive warning is required. A forced
  unavailable warning does not count. No warning with complete diagnostics is
  silent misspecification and maps to `model_contract_failed`.

### Equal-emission control

- The observed shared equal and ordered fits consume all 24 scenario
  replicates; no replicate may be omitted from either summed likelihood.
- The bootstrap denominator is exactly 199 complete 24-replicate bundles and
  the add-one denominator is fixed at 200.
- Any failed/nonfinite shared fit, statistic, equal fit, or ordered bundle refit
  fails availability and maps to `model_contract_failed`.
- With complete availability, `p>=0.05` passes and `p<0.05` maps to
  `model_contract_failed`.
- There are no profile rows. The six fixed structural/practical status rows are
  invariant to p and are exempt from the generic accepted-estimand
  nonidentification rule because unidentifiability is the expected control
  result.
- Equal-submodel predictive output is diagnostic-only. Its warning polarity
  cannot override the bootstrap decision, although missing or malformed
  required artifact rows remain an artifact contract failure.

### Predictive diagnostics

| Scenario | Attempted denominator per cell | Decision polarity |
| --- | ---: | --- |
| process oracle | none | not applicable |
| observation oracle | 48 | conditional diagnostic only; cannot pass or fail a joint predictive gate |
| dense exact | 48 | complete with no scientific warning required for pass |
| structured exact | 48 | complete with no scientific warning required for pass |
| sparse exact | 24 | complete with no scientific warning required for honesty pass |
| zero driver | 24 | complete with no scientific warning required for control pass |
| arrival alignment | 24 | complete and at least one scientific warning required |
| equal emission | 24 | diagnostic only; bootstrap is decisive |
| informative dropout | 24 | complete; warning required if and only if `any_narrow_wrong` |
| continuous abundance | 24 | complete and at least one scientific warning required |
| spatial frailty | 24 | complete; warning required if and only if `any_narrow_wrong` |

Each applicable attempted replicate emits exactly 27 stable cells. A failed fit
emits 27 unavailable rows, creates no reference ensemble, remains in the full
denominator, increments `failed_fit_count`, and fails predictive completeness.
A nonfinite diagnostic is serialized null with its explicit nonfinite flag and
also fails predictive completeness. Neither failure can satisfy a required
stress warning.

### Misspecification coverage and profiles

For informative dropout and spatial frailty, retain 24 attempted rows per known
parameter:

- coverage counts use all 24 attempts; nonconverged/nonfinite/open/missing
  intervals are uncovered;
- absolute-error and interval-width descriptive summaries use the same
  parameter-specific full-support imputations as nested summaries;
- signed error remains finite-converged-only and nullable;
- no coverage, bias, median-error, or width acceptance threshold is added;
- a valid open profile is not `narrow_wrong`, because its imputed full-support
  width exceeds the frozen narrowness bound;
- `narrow_wrong` is true only for a finite closed two-sided interval that
  excludes truth and has width no larger than that parameter's frozen maximum.

Broad wrong intervals, severe signed bias with coverage, and unexpectedly good
stress recovery remain descriptive under current authority. They do not create
new gates. Missing required rows or failed/nonfinite fits are still contract or
predictive-availability failures.

Continuous abundance has no parameter-recovery truth. Its 24 attempted
fit/profile rows may be descriptive, but truth, coverage, error, and
`narrow_wrong` fields are not applicable. Its scientific gate is complete
predictive evidence with at least one warning.

## Scenario Reducers

Evaluate global contract gates first, then the scenario rows in canonical order.
Within a row, an earlier listed condition has local precedence.

| # | Scenario | Local condition | Local impact and reason |
| ---: | --- | --- | --- |
| 1 | process oracle | Any potential/oracle design, convergence, coverage, error, width, fit-domain, or required oracle artifact gate fails | `contract_failure:process_oracle_failed` |
| 1 | process oracle | All applicable gates pass | `pass` |
| 2 | observation oracle | Any potential design, convergence, coverage, error, width, fit-domain, or required oracle artifact gate fails | `contract_failure:observation_oracle_failed` |
| 2 | observation oracle | All applicable gates pass; conditional predictive values may warn diagnostically | `pass` |
| 3 | dense exact | Missing/duplicate/malformed evidence, a nonfinite numerical-domain result, or predictive evidence unavailable for any reason other than a retained typed nonconvergence | `contract_failure:dense_evidence_invalid` |
| 3 | dense exact | With complete schema-valid finite evidence, any dense convergence, coverage, accuracy, precision, finite-fit plug-in, or exact predictive scientific gate fails after both oracles pass; this includes predictive incompleteness caused solely by a retained typed nonconvergence | `confounding:dense_joint_failed` |
| 3 | dense exact | All dense gates pass | `pass` |
| 4 | structured exact | Missing/malformed evidence, required-fit/predictive unavailability, convergence failure, coverage outside `36..48`, or complete predictive scientific rejection | `contract_failure:structured_not_calibrated` |
| 4 | structured exact | A finite-fit plug-in design has rank below 3 or condition `>=1e8`, or an accepted estimand is declared structurally/practically unidentified | `confounding:structured_estimand_unidentified` |
| 4 | structured exact | Coverage, fit availability, identification, and prediction pass, but any median error/width recovery limit fails | `structured_limitation:structured_precision_recovery_failed` |
| 4 | structured exact | Every structured gate passes | `pass` |
| 5 | sparse | Missing/malformed rows, required-fit/predictive failure, coverage outside `18..24`, or median width below structured | `contract_failure:sparse_honesty_failed` |
| 5 | sparse | Dedicated coverage and width Booleans plus predictive completeness pass | `pass` |
| 6 | zero driver | Any interval is undecidable, required fit/plugin/predictive evidence fails, or rows are missing/malformed | `contract_failure:zero_driver_unavailable` |
| 6 | zero driver | All intervals decidable and exclusions are `7..24` | `confounding:zero_driver_false_signal` |
| 6 | zero driver | All intervals decidable, exclusions `0..6`, and standard prediction passes | `pass` |
| 7 | arrival alignment | Invalid/nonfinite correlation, missing pair, required fit/plugin/score/predictive unavailability, or malformed evidence | `contract_failure:alignment_contract_or_availability_failed` |
| 7 | arrival alignment | Complete evidence but no available scientific warning | `contract_failure:alignment_silent_misspecification` |
| 7 | arrival alignment | Complete evidence, warning present, but correct alignment wins `0..21` | `confounding:arrival_alignment_not_discriminated` |
| 7 | arrival alignment | Correlation valid, all 24 pairs available, wins `22..24`, and warning present | `pass` |
| 8 | equal emission | Shared fit/statistic invalid, any of 199 ordered refits fails, p is nonfinite, p `<0.05`, fixed status differs, or required artifact evidence is malformed | `contract_failure:equal_emission_control_failed` |
| 8 | equal emission | All refits succeed, p `>=0.05`, and statuses are exact | `pass` |
| 9 | informative dropout | Required fit/plugin/predictive evidence is unavailable or malformed | `contract_failure:informative_dropout_unavailable` |
| 9 | informative dropout | `any_narrow_wrong=true` and no available scientific warning | `contract_failure:informative_dropout_silent_misspecification` |
| 9 | informative dropout | Predictive evidence is complete and either no narrow-wrong result exists or a warning detects it | `pass` |
| 10 | continuous abundance | Required fit/plugin/predictive evidence is unavailable or malformed | `contract_failure:continuous_abundance_unavailable` |
| 10 | continuous abundance | Complete evidence but no available scientific warning | `contract_failure:continuous_abundance_silent_misspecification` |
| 10 | continuous abundance | Complete evidence and at least one warning | `pass` |
| 11 | spatial frailty | Required fit/plugin/predictive evidence is unavailable or malformed | `contract_failure:spatial_frailty_unavailable` |
| 11 | spatial frailty | `any_narrow_wrong=true` and no available scientific warning | `contract_failure:spatial_frailty_silent_misspecification` |
| 11 | spatial frailty | Predictive evidence is complete and either no narrow-wrong result exists or a warning detects it | `pass` |

For scenarios 3 and 4, a plug-in failure caused solely by an already failed or
nonfinite fit is an availability/contract failure, not independent evidence of
confounding. The confounding branch is reserved for a valid plug-in diagnostic
computed from a finite fit that demonstrates practical nonidentification.

## Total Global State Machine

All global and scenario inputs must be present and internally consistent before
classification. Compute every applicable local reducer so all reasons can be
reported, then choose the first matching terminal class:

```text
required_stress_ids = {
    permuted_arrival_alignment_stress,
    informative_dropout_misspecification_stress,
    goal018_continuous_abundance_stress,
    spatial_frailty_stress,
}

contract_failure =
    any frozen source/schema/analytic/likelihood/holdout/artifact/provenance/
        numerical-domain/potential-design/noncollision gate fails
    or any required local input is missing, unknown, contradictory, or unevaluated
    or any scenario reducer returns contract_failure

confounding = any scenario reducer returns confounding

structured_limitation =
    scenario 3 returns pass
    and scenario 4 returns structured_limitation

all_required_pass =
    every global contract gate passes
    and scenarios 1..11 each return pass
    and every required_stress_id is present exactly once

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

Rank 3 is reachable only when all non-structured required gates, including
sparse honesty, both negative controls, and all four stresses, pass. Rank 4 is
unreachable when any stress is absent, unavailable, invalid, or fails its local
rule. Stress results are therefore required evidence for the top pass, not
decorative diagnostics.

If multiple reasons occur, emit all reason flags in canonical global-gate then
scenario order, but use the smallest recommendation rank. Within one rank, the
first canonical reason is the primary interpretation. This makes output stable
without hiding simultaneous failures.

## Exact RED Tests

The tests below use injected deterministic result objects only. They must not
construct a scenario RNG, calibration row, holdout payload, predictive
ensemble, bootstrap bundle, or future artifact.

### Registry and truth firewall

- `test_scenario_registry_has_exact_truth_access_mapping`: assert the literal
  11-value vector
  `[oracle_only, oracle_only, analyst_firewalled, analyst_firewalled,
  analyst_firewalled, analyst_firewalled, stress_evaluator_only,
  analyst_firewalled, stress_evaluator_only, stress_evaluator_only,
  stress_evaluator_only]` in canonical scenario order.
- `test_truth_access_mapping_rejects_missing_extra_or_reordered_rows`: require
  exactly one mapping per canonical scenario and reject unknown enum values.
- `test_stress_evaluator_truth_cannot_enter_analyst_fit`: parameterize scenarios
  7, 9, 10, and 11 and prove original alignment, state-conditioned dropout,
  Goal 018 abundance, and frailty fields are rejected by analyst APIs.
- `test_zero_driver_and_equal_emission_fitters_are_not_told_control_truth`:
  prove generating zero/equal labels do not enter starts, bounds, objective,
  profiles, or tie-breaking.

### Denominator and missingness arithmetic

- `test_nested_denominators_and_imputation_are_literal`: for each support width,
  inject converged, nonconverged, nonfinite, open, and missing-interval result
  states; assert 48 rows, uncovered handling, full-width imputations, ordinary
  even median, and finite-only nullable signed error.
- `test_nested_coverage_boundaries_are_36_and_35`: 36 passes and 35 fails for
  each of 15 parameter families; 48 passes.
- `test_nested_convergence_boundaries_are_literal`: assert `46/45` boundaries
  for scenarios 1-3 and `44/43` for scenario 4.
- `test_missing_recovery_row_is_contract_failure_not_imputation`: remove one
  row and assert rank 1 rather than a 47-row denominator.
- `test_sparse_coverage_boundaries_use_all_24`: 18 and 24 pass; 17 fails;
  open profiles remain attempted and uncovered.
- `test_sparse_width_boundary_is_inclusive`: width equal to structured passes;
  the next representable value below fails with
  `sparse_unexpectedly_narrow`.
- `test_sparse_failed_fit_cannot_be_rescued_by_width_six`: inject a failed fit
  whose imputed width makes the median broad; assert predictive failure and
  rank 1.
- `test_sparse_low_error_or_24_of_24_coverage_is_not_a_new_gate`: hold frozen
  honesty Booleans true and assert descriptive strength alone does not fail.
- `test_zero_driver_interval_touching_zero_is_not_exclusion`: test lower zero,
  upper zero, and straddling zero.
- `test_zero_driver_six_exclusions_pass_and_seven_confounds`: require all 24
  intervals decidable; assert local `pass` at six and local `confounding` at
  seven, then assert global ranks 4 and 2 from otherwise passing vectors.
- `test_zero_driver_failed_open_and_missing_are_undecidable`: parameterize
  nonconverged, nonfinite, open-left, open-right, and missing interval; assert
  denominator 24, null exclusion indicator, unavailable count one, no binomial
  decision, and rank 1.
- `test_predictive_failed_fit_emits_27_unavailable_rows`: assert no reference,
  full attempted denominator, `failed_fit_count`, warning/fail, and that the
  forced warning cannot satisfy a stress warning.

### Scenario reducers

- `test_dense_complete_scientific_failure_maps_to_confounding`: after both
  oracles pass, inject each finite complete dense recovery/plugin/predictive
  scientific failure and assert rank 2.
- `test_structured_recovery_only_failure_maps_to_observation_limited`: keep
  coverage, fit availability, plug-in identification, prediction, sparse,
  controls, and stresses passing; fail one median error and one median width at
  a time; assert rank 3.
- `test_structured_coverage_failure_maps_to_contract_failed`: test 35/48 with
  all other inputs passing and assert rank 1.
- `test_structured_predictive_failure_maps_to_contract_failed`: parameterize
  failed fit, unavailable cell, nonfinite aggregate, and complete scientific
  rejection; assert rank 1.
- `test_structured_finite_plugin_failure_maps_to_confounding`: rank 2 for design
  rank 2, condition exactly `1e8`, and accepted-estimand practical
  nonidentification; assert pass at design rank 3 with condition just below
  `1e8`; assert rank 1 when plug-in is unavailable because its parent fit
  failed.
- `test_alignment_correlation_boundary`: `-0.25` and `0.25` pass construction;
  next representable absolute value above and nonfinite fail at rank 1.
- `test_alignment_win_boundary`: with complete valid evidence and a warning,
  22 wins pass and 21 wins map to rank 2.
- `test_alignment_missing_pair_is_contract_failure_not_score_confounding`:
  keep the attempted denominator 24, assign no win, and assert rank 1.
- `test_alignment_warning_is_mandatory_and_must_be_scientific`: zero warning
  fails rank 1; one available warning passes; one forced unavailable warning
  fails rank 1.
- `test_equal_emission_p_boundary_and_refit_completeness`: `p=0.05` with all
  199 refits passes; the next valid add-one p below fails; any one failed refit
  fails regardless of p.
- `test_equal_emission_statuses_do_not_trigger_generic_confounding`: assert the
  six fixed statuses at both passing and failing p and prove expected
  unidentification is exempt from rank 2.
- `test_dropout_and_frailty_warning_is_conditional`: for each scenario, no
  narrow-wrong plus no warning passes; narrow-wrong plus warning passes; narrow-
  wrong plus no warning fails rank 1; broad wrong plus no warning remains
  descriptive.
- `test_stress_open_profile_is_broad_not_narrow_wrong`: assert full-support
  width imputation, uncovered descriptive coverage, and no narrow-wrong flag.
- `test_continuous_abundance_requires_warning`: complete evidence with one
  warning passes; zero warnings fails rank 1.
- `test_every_stress_fit_or_predictive_unavailability_maps_to_rank_one`:
  parameterize scenarios 7, 9, 10, and 11 over failed fit, failed plug-in,
  missing cell, and nonfinite diagnostic.

### Totality and precedence

- `test_all_required_gates_pass_reaches_rank_four`: require all global gates and
  all 11 local reducers to pass.
- `test_each_stress_is_individually_required_for_top_pass`: start from the
  rank-4 vector; remove and fail each of scenarios 7, 9, 10, and 11 in turn;
  assert rank 4 is unreachable.
- `test_rank_precedence_under_simultaneous_failures`: rank 1 beats rank 2 and
  rank 3; rank 2 beats rank 3; canonical primary reason is stable while all
  reasons remain visible.
- `test_rank_three_requires_every_nonstructured_gate`: start from a valid rank-3
  vector and fail sparse, each control, and each stress in turn; assert rank 3
  is unreachable.
- `test_unknown_missing_or_contradictory_outcome_never_defaults_to_pass`:
  parameterize every required input with unknown, null, duplicate, and mutually
  contradictory states; assert rank 1 with
  `incomplete_or_contradictory_decision_vector` or the more specific contract
  reason.
- `test_local_reducers_are_total`: exhaust every finite enum value for each
  scenario reducer and assert exactly one local impact plus at least one reason
  for non-pass outcomes.
- `test_global_reducer_is_total`: exhaust the four local-impact symbols over a
  compact generated vector and assert exactly one of ranks 1-4.
- `test_transportability_class_is_invariant`: parameterize every terminal rank
  and assert the scheduled-count-only bridge class.

## Barry-Level Decision

One material policy bundle requires Barry's ratification before authority is
amended:

1. Every one of the four stress scenarios is required for
   `latent_response_observation_gate_passed` and for the otherwise eligible
   rank-3 calibrated-limitation recommendation.
2. Structured coverage/predictive failure and unexpectedly narrow sparse
   inference use the existing conservative class `model_contract_failed`, with
   exact reason codes, rather than creating a fifth inconclusive class.
3. A valid alignment stress that cannot distinguish correct from permuted
   alignment maps to `process_observation_confounded`; invalid or unavailable
   alignment evidence maps to `model_contract_failed`.
4. Dropout and frailty warnings remain conditional on `narrow_wrong`; requiring
   a warning in every such replicate set would be a new scientific threshold
   and is not introduced here.

Recommendation: approve this bundle. It is total, preserves the four public
classes, makes top-pass stress evidence substantive, and adds no new numerical
recovery threshold. If Barry wants scientifically valid surprises to remain
non-failing, then and only then a fifth class such as
`gate_inconclusive_requires_review` becomes logically necessary.

## Residual Scope

This proposal does not resolve the separate latent-time calibration formulas,
multi-fit artifact identity for alignment/equal emission, or the Task 3 versus
Task 4 calibration-smoke conflict. Those remain pre-implementation blockers
from the scenario/gate preflight. No part of this decision proposal authorizes
scenario execution, calibration, holdout exposure, or Goal 024.
