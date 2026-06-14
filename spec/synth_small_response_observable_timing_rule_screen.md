# Synth-Small Response-Observable Timing-Rule Screen

Goal 016 adds a synthetic-only, evaluation-only screen of deterministic
target-time rules that use only response-observable inputs. The screen asks
whether the Goal 015 residual timing signal is strong enough to justify a later
bounded reconstruction-rule design goal, without changing the production
reconstruction rule or the Goal 009/010 summary-vector and compatibility
contracts.

## Scope

This is a diagnostic rule screen only.

- It does not change default observation-design settings.
- It does not rewrite emitted observation, reconstruction, response-screen, or
  bridge artifacts.
- It does not change the production final-absence reconstruction rule or
  `min_final_absence_run`.
- It does not change summary-vector, compatibility-screen, mismatch-audit,
  false-negative-audit, observation-support counterfactual, residual
  decomposition, or target-time anatomy scoring logic.
- It does not adopt a reconstruction rule.
- It does not add candidates, parameter sweeps, ABC, POM, likelihood fitting,
  posterior interpretation, real-data analysis, remote compute, or richer
  landscape-generator work.

Truth-guided and truth-only rules may appear only as labelled synthetic
references.

## Inputs

The command reads existing emitted artifacts from disk and fails loudly if
required files are missing.

Observation and reconstruction artifacts:

- `artifacts/synth_small_observations/observation_config.json`
- `artifacts/synth_small_observations/sites.csv`
- `artifacts/synth_small_observations/visits.csv`
- `artifacts/synth_small_observations/observations.csv`
- `artifacts/synth_small_observations/evaluation_truth.csv`
- `artifacts/synth_small_observations/truth_reference.json`
- `artifacts/synth_small_extirpation_reconstruction/reconstruction_config.json`
- `artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv`
- `artifacts/synth_small_extirpation_reconstruction/time_detection_summary.csv`
- `artifacts/synth_small_extirpation_reconstruction/verification.json`

Evaluation and bridge artifacts:

- `artifacts/synth_small_response_screen/evaluation/screen_evaluation_summary.json`
- `artifacts/synth_small_response_screen/evaluation/site_evaluation_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/verification.json`
- `artifacts/synth_small_summary_vector/summary_vector_config.json`
- `artifacts/synth_small_summary_vector/mode_summary.json`
- `artifacts/synth_small_summary_vector/summary_components.csv`
- `artifacts/synth_small_summary_vector/coverage_curve.csv`
- `artifacts/synth_small_summary_vector/verification.json`
- `artifacts/synth_small_compatibility_screen/target_summary.json`
- `artifacts/synth_small_compatibility_screen/candidate_scores.csv`
- `artifacts/synth_small_compatibility_screen/mode_rankings.csv`
- `artifacts/synth_small_compatibility_screen/coverage_score_breakdown.csv`
- `artifacts/synth_small_compatibility_screen/verification.json`

Diagnostic artifacts:

- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/site_counterfactual_resolution.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/scenario_rankings.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/verification.json`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/site_target_transform_resolution.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/target_transform_rankings.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/component_delta_table.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/verification.json`
- `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/site_target_time_error_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/observable_proxy_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/recommendation.json`
- `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/verification.json`

## Rule Set

The rule set is intentionally small and deterministic.

`status_quo_observed`
: Baseline using the current reconstructed observed extirpation time.

`long_detection_gap_shift_minus4`
: Eligible response-observable rule. For finite status-quo targets with
  `observed_extirpation_time - last_detection_time >= 8`, move the target four
  time steps earlier. Other sites retain the status-quo target.

`west_band_shift_minus4`
: Eligible response-observable, spatially keyed rule. For finite status-quo
  targets in `front_band == west_band`, move the target four time steps earlier.

`long_gap_or_west_band_shift_minus4`
: Eligible response-observable combination rule. Move finite targets four
  time steps earlier when either the long detection-to-target gap or west-band
  condition is met.

`nonfinite_supported_final_survey_gap_expansion`
: Eligible response-observable finite-target expansion rule. Status-quo finite
  targets are retained. Status-quo nonfinite sites receive their last observed
  survey time only when the production final-absence run is still below the
  current threshold, the site has at least eight observed survey times, the site
  has at least one detection, and the final observed survey is at least eight
  time steps after the last detection. This is the conservative finite-support
  candidate.

`nonfinite_last_survey_expansion`
: Eligible response-observable finite-target expansion rule. Status-quo finite
  targets are retained; status-quo nonfinite sites receive their last observed
  survey time as a diagnostic target. This rule is a broad all-nonfinite stress
  test, not the conservative finite-support candidate, because it can create
  finite targets for non-extirpated sites.

`goal013_support_floor`
: Truth-guided reference using the Goal 013
  `truth_guided_absence_floor_all` support-floor target.

`all_extirpated_true_time`
: Truth-only reference using synthetic true extirpation time for all truly
  extirpated sites. This reference must reconcile with the Goal 010
  `ideal_true` compatibility expectation.

## Outputs

The CLI writes to:

```text
artifacts/synth_small_response_screen/evaluation/response_observable_timing_rule_screen/
```

Required files:

- `timing_rule_screen_config.json`
- `rule_definitions.csv`
- `site_rule_resolution.csv`
- `rule_summary_vectors.csv`
- `rule_component_losses.csv`
- `rule_rankings.csv`
- `proxy_rule_performance.csv`
- `grid_simplicity_risk_audit.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

All JSON outputs include:

- `synthetic_only: true`
- `evaluation_only: true`
- `response_observable_rule_screen_only: true`
- `not_formal_inference: true`
- `no_default_observation_change: true`
- `no_reconstruction_rule_change: true`
- `no_scoring_change: true`
- `no_candidate_change: true`
- `no_richer_landscape_change: true`
- `no_pom_or_likelihood_change: true`

## Table Contracts

`rule_definitions.csv`
: One row per rule with stable ID, family, eligibility class, source columns,
  finite-target-expansion flag, spatially keyed flag, hidden-truth flag, and
  interpretation.

`site_rule_resolution.csv`
: One row per site per rule with site ID, group labels, truth status, status-quo
  target, Goal 013 support-floor target, rule target, finite status, signed and
  absolute timing error where synthetic truth permits audit, target deltas from
  status quo and support floor, response-observable proxy flags, and whether a
  status-quo nonfinite target was made finite.

`rule_summary_vectors.csv`
: Long-form summary-vector components and coverage-curve target rows for every
  rule, using the Goal 009 summary-vector helper semantics.

`rule_component_losses.csv`
: One row per rule, candidate, and scored component under the unchanged Goal 010
  compatibility contract. The table includes target value, candidate value,
  absolute gap, normalized gap, weight, weighted gap, missing reason, and a
  deterministic component contribution rank.

`rule_rankings.csv`
: One row per rule and candidate with deterministic rank, compatibility class,
  total weighted loss, finite-target count, timing-error summaries, eligibility
  class, nonfinite-to-finite conversion counts split by synthetic truth status,
  deltas from the status-quo baseline and Goal 013 support-floor reference,
  the loss-gap fraction closed toward Goal 013, and a finite-support role label.

`proxy_rule_performance.csv`
: Proxy-stratified timing performance for the Goal 015 response-observable
  residual-timing candidates: `long_detection_to_target_gap`,
  `spatial_front_band_west_band_signal`, and `sparse_survey_history`.

`grid_simplicity_risk_audit.csv`
: Rule-level audit of spatial/front-band dependence. Spatially keyed gains are
  labelled as simple-grid overfit-prone diagnostic evidence, not robust method
  evidence.

## Reconciliation Checks

Verification must reconcile:

- one site-rule row per synth-small site per rule;
- status quo finite targets `151`, default candidate `default`, class
  `incompatible`, and loss `3.52263635737`;
- Goal 013 support-floor finite targets `252`, default candidate `default`,
  class `incompatible`, and loss `1.88500331398`;
- Goal 014 all-true finite targets `252`, default candidate `default`, class
  `compatible`, and loss `0`;
- Goal 015 recommendation `response_observable_rule_screen_ready` and
  `residual_timing_candidate_count = 3`;
- component-loss row cardinality and summability against rankings.
- conservative finite-support accounting, including the count of status-quo
  nonfinite sites made finite and the truth-audit split of those converted
  sites.

If these checks fail, the recommendation class must be
`timing_rule_screen_contract_failed`.

## Recommendation

Recommendation classes are:

- `response_observable_timing_rule_promising`
- `spatial_proxy_overfit_risk`
- `response_only_signal_insufficient`
- `observation_process_model_needed`
- `richer_synthetic_landscape_needed`
- `timing_rule_screen_contract_failed`

The current expected diagnostic is that the best eligible response-observable
rule, whether it is a timing shift or the conservative finite-support
candidate, may reduce total loss but remains incompatible and does not
materially approach the Goal 013 support-floor reference. The broad
`nonfinite_last_survey_expansion` rule is retained only as a stress test.
Spatial/front-band gains must be reported as simple-grid overfit-prone unless a
later richer synthetic landscape supports the same pattern.

## Acceptance Criteria

- The CLI consumes required disk artifacts and writes the required bundle.
- Candidate definitions separate eligible response-observable rules from
  status-quo, truth-guided, and truth-only references.
- Site-rule rows reconcile one row per synth-small site per rule.
- Status-quo, Goal 013 support-floor, Goal 014 all-true, and Goal 015 anatomy
  counts reconcile.
- Summary-vector and compatibility-screen scoring reuse the existing contracts.
- Proxy-stratified performance exposes whether residual-timing proxies explain
  rule gains.
- Finite-support accounting distinguishes the conservative supported
  nonfinite-expansion candidate from the broad all-nonfinite stress test.
- Grid/front-band overfit risk is explicit.
- The recommendation is deterministic and does not start a rule change,
  landscape redesign, scoring change, candidate change, or inference workflow.
- Focused tests pass.
- Generated artifacts remain ignored and unstaged.
