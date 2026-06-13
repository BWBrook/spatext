# Synth-Small Target-Time Error Anatomy Audit

Goal 015 adds a synthetic-only, evaluation-only target-time error anatomy audit
for the current synth-small diagnostic ladder.

The audit localizes the timing errors exposed by Goal 014 at the site level.
It compares the status-quo reconstructed target and the Goal 013
`truth_guided_absence_floor_all` support-floor target against synthetic true
extirpation times, then separates response-observable proxy signals from
truth-only diagnostics before any reconstruction-rule screen is attempted.

## Scope

This is a diagnostic table bundle only.

- It does not change default observation-design settings.
- It does not rewrite default observation or reconstruction artifacts.
- It does not change the production final-absence reconstruction rule or
  `min_final_absence_run`.
- It does not change response-screen, summary-vector, compatibility-screen,
  mismatch-audit, false-negative-audit, observation-support counterfactual, or
  target-timing residual scoring logic.
- It does not add candidates, parameter sweeps, ABC, POM, likelihood fitting,
  posterior interpretation, real-data analysis, or remote compute.

Hidden synthetic truth is used only inside clearly labelled synthetic-only and
evaluation-only outputs.

## Inputs

The command reads existing emitted artifacts from disk:

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
- `artifacts/synth_small_response_screen/evaluation/screen_evaluation_summary.json`
- `artifacts/synth_small_response_screen/evaluation/site_evaluation_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/verification.json`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/false_negative_site_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/mechanism_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/observation_timing_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/recommendation.json`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/verification.json`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/counterfactual_config.json`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/site_counterfactual_resolution.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/scenario_reconstruction_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/scenario_rankings.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/verification.json`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/residual_decomposition_config.json`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/site_target_transform_resolution.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/target_transform_rankings.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/component_delta_table.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/recommendation.json`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/verification.json`

Missing inputs fail loudly. The runbook may rebuild the ignored prerequisite
chain before running the audit.

## Outputs

The CLI writes:

`artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/`

Required files:

- `target_time_error_anatomy_config.json`
- `site_target_time_error_audit.csv`
- `target_time_error_group_summary.csv`
- `error_mechanism_summary.csv`
- `observable_proxy_summary.csv`
- `transform_error_contrast.csv`
- `bias_classification_summary.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

All JSON outputs include:

- `synthetic_only: true`
- `evaluation_only: true`
- `error_anatomy_diagnostic_only: true`
- `not_formal_inference: true`
- `no_default_observation_change: true`
- `no_reconstruction_rule_change: true`
- `no_scoring_change: true`
- `no_candidate_change: true`

## Site-Level Error Definitions

`site_target_time_error_audit.csv` has one row per synth-small site.

For sites with finite synthetic true extirpation time:

```text
status_quo_signed_error = status_quo_target_time - true_extirpation_time
support_floor_signed_error = support_floor_target_time - true_extirpation_time
```

Positive error is late reconstruction, negative error is early reconstruction,
zero is exact, and blank target time on a true-extirpated site is nonfinite.
Absolute error is the absolute value of the signed error where finite.

Error magnitude classes are:

- `not_comparable`: no finite synthetic true extirpation time;
- `nonfinite`: true extirpated but no target time;
- `exact`: absolute error is `0`;
- `small_abs_1_to_3`: absolute error is greater than `0` and less than `4`;
- `moderate_abs_4_to_7`: absolute error is at least `4` and less than `8`;
- `large_abs_ge_8`: absolute error is at least `8`.

The site table includes region, front band, true extirpation time, status-quo
target time, support-floor target time, false-negative status, Goal 012 primary
mechanism, post-extirpation detection counts, survey and effort features,
near-horizon classes, finite/nonfinite classes, support-floor resolution status,
and semicolon-delimited proxy flag fields.

## Group Summaries

`target_time_error_group_summary.csv` includes grouped summaries for:

- `overall`;
- `false_negative_status`;
- `primary_mechanism`;
- `region`;
- `front_band`;
- `post_extirpation_detection_class`;
- `near_horizon_class`;
- `survey_gap_class`;
- `status_quo_finite_class`;
- `support_floor_resolution_status`.

Each row records site count, true-extirpated count, status-quo/support-floor
finite target counts, mean/median signed and absolute errors, late/early/exact
and nonfinite counts, and support-floor improvement/worsening/unchanged counts.

## Observable Proxy Inventory

`observable_proxy_summary.csv` classifies candidate explanatory signals as:

- `response_observable`: computable from analyst-facing observation or
  reconstruction artifacts without hidden truth;
- `truth_only`: requires synthetic truth and cannot be used as an
  analyst-facing rule signal;
- `mixed`: combines response artifacts with synthetic truth for evaluation, but
  may have a response-only proxy that would need a later bounded screen.

The inventory records the source artifact/columns, affected site count, and
whether the signal is suitable for a later response-observable rule-screen
goal. Suitability does not authorize that screen inside Goal 015.

The table also records how each proxy connects to the residual timing problem
after Goal 013 support-floor finite-target restoration:

- `true_extirpated_affected_site_count`: affected sites with finite synthetic
  true extirpation time;
- `support_floor_large_abs_error_site_count`: affected true-extirpated sites
  whose support-floor absolute timing error is at least the configured
  `large_error_min`;
- `support_floor_large_abs_error_fraction`: the corresponding fraction among
  affected true-extirpated sites;
- `rule_screen_role`: one of `finite_target_support_context`,
  `residual_timing_candidate`, `truth_only_reference`, or
  `mixed_evaluation_context`.

Finite-target support context, such as status-quo nonfinite state or short
final-absence runs, is distinguished from residual-timing candidates. The
current response-observable residual-timing candidates include a
data-derived spatial/front-band signal sourced from `sites.csv:region,front_band`
and response-side reconstruction-history signals such as long detection-to-
target gaps.

## Transform Contrast And Bias Classification

`transform_error_contrast.csv` summarizes timing-error consequences for the
Goal 014 target transforms, including finite true-extirpated target count,
nonfinite true-extirpated count, mean/median error, late/early/exact counts,
default-candidate loss, compatibility class, and whether the transform restores
the established Goal 010 ideal-truth bridge.

`bias_classification_summary.csv` deterministically classifies evidence for
late bias, early bias, end-window compression, spatial structure,
survey-gap association, detection-persistence association, and truth-only
dependence.

## Reconciliation Checks

Verification must reconcile:

- one site-audit row per synth-small site (`625`);
- ideal true finite target count (`252`);
- status-quo finite target count (`151`);
- response-screen false-negative count (`101`);
- Goal 013 support-floor finite target count (`252`);
- Goal 014 `all_extirpated_true_time` finite target count (`252`), default
  candidate `default`, compatibility class `compatible`, and loss `0`;
- group summaries against the site-level table.

If these checks fail, the recommendation class must be
`target_time_error_contract_failed`.

## Recommendation

The recommendation class identifies the next project move without starting it.
Classes are:

- `response_observable_rule_screen_ready`
- `timing_bias_truth_only_not_observable`
- `survey_design_gap_dominates`
- `detection_persistence_rule_review_needed`
- `end_window_compression_dominates`
- `target_time_error_contract_failed`

The expected current diagnostic is that Goal 013 support-floor finite-target
restoration resolves the false negatives, but the remaining timing error is
late-biased, spatially structured, and concentrated in already finite
status-quo targets. That pattern supports a later bounded
response-observable rule-screen discussion, not a rule change in this goal.
The recommendation may be `response_observable_rule_screen_ready` only when at
least one response-observable proxy with role `residual_timing_candidate` has
nonzero large-error coverage under the support-floor target.

## Acceptance Criteria

- The CLI consumes required disk artifacts and writes the required bundle.
- The site audit has one row per synth-small site.
- Prior-goal counts and Goal 014 ideal-truth restoration reconcile.
- Error summaries reconcile numerically with the site table.
- The proxy inventory separates response-observable, truth-only, and mixed
  signals.
- The recommendation is deterministic and diagnostic-only.
- Focused tests pass.
- Generated artifacts remain ignored and unstaged.
