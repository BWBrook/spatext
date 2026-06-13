# Goal 015: Synth-Small Target-Time Error Anatomy Audit

## Objective

Build a synthetic-only, evaluation-only target-time error anatomy audit that
explains where the Goal 014 timing bias comes from at the site level, and
which parts of that bias are visible from response-only artifacts rather than
only from hidden synthetic truth.

This goal should make the next intervention decision sharper. It should not
change the default reconstruction rule, observation design, summary-vector
contract, compatibility scoring, candidates, or inference machinery.

## Context

Goals 009-014 established a response-side diagnostic ladder:

- Goal 009 added the `S(T_X, T_P)` summary-vector bridge.
- Goal 010 showed the default candidate is compatible under `ideal_true` but
  incompatible under `realistic_observed`.
- Goal 011 showed that the finite-target drop from `ideal_true` to
  `realistic_observed` exactly matches the `101` response-screen false
  negatives.
- Goal 012 diagnosed those false negatives.
- Goal 013 showed that post-extirpation support can restore finite target
  count, but not compatibility.
- Goal 014 showed that the bridge itself is not broken: the
  `all_extirpated_true_time` target restores the Goal 010 `ideal_true`
  compatibility expectation, while the Goal 013 support floor remains
  incompatible with dominant residuals in timing and target-shape components.

The next question is therefore not "can truth fix the target?" The answer is
yes. The next question is "what target-time errors are being made, where do
they occur, and which error signals are response-observable enough to justify
a later bounded reconstruction-rule screen?"

## Scientific Question

For the synth-small system, how do status-quo and Goal 013 support-floor target
times differ from synthetic true extirpation times across sites, mechanisms,
regions, front bands, survey histories, and detection-persistence classes; and
which diagnostic signals are visible without using hidden truth?

## In Scope

- Add `spec/synth_small_target_time_error_anatomy_audit.md`.
- Add a focused module under `src/spatext/synth/small/`, probably
  `target_time_error_anatomy_audit.py`.
- Add a CLI script, probably `scripts/audit_synth_small_target_time_errors.py`.
- Read existing emitted synthetic artifacts from disk.
- Build a site-level audit comparing:
  - synthetic true extirpation time;
  - status-quo reconstructed observed target time;
  - Goal 013 support-floor target time;
  - Goal 014 target-transform classification where useful.
- Summarize target-time error by:
  - false-negative status and Goal 012 primary mechanism;
  - post-extirpation detection count;
  - no-post-extirpation-survey and near-horizon classes;
  - region and front band;
  - survey effort and survey-gap features;
  - status-quo finite versus status-quo nonfinite sites;
  - Goal 013 support-floor resolved versus unresolved sites.
- Emit an observable-proxy inventory separating:
  - signals available from response-only artifacts;
  - signals requiring synthetic truth;
  - mixed signals that can be audited under truth but only approximated in
    response-only use.
- Emit deterministic artifacts under:
  `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/`.
- Add focused tests for site-level accounting, grouped summaries, observable
  proxy classification, recommendation classification, CLI execution, and
  boundary labels.
- Update exports, README, `AGENTS.md` if the authoritative spec list changes,
  `spec/report_log.md`, and this goal log.

## Out Of Scope

- Changing default observation-design settings.
- Changing emitted default observation or reconstruction artifacts.
- Changing the production reconstruction rule or `min_final_absence_run`.
- Changing response-screen, summary-vector, compatibility-screen,
  mismatch-audit, false-negative-audit, Goal 013, or Goal 014 scoring logic.
- Adding a new response-observable reconstruction rule.
- Adding process candidates or broad parameter sweeps.
- ABC, POM, MCMC, likelihood fitting, posterior claims, or parameter recovery.
- Real-data analysis.
- Remote compute.
- Commit or push.

## Required Inputs

The command should read existing artifacts from disk.

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

Evaluation and diagnostic artifacts:

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
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/scenario_rankings.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/verification.json`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/residual_decomposition_config.json`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/site_target_transform_resolution.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/target_transform_rankings.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/component_delta_table.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/recommendation.json`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/verification.json`

The command should fail loudly when required inputs are missing. The runbook
may rebuild the local ignored artifact chain first.

## Required Outputs

Write a deterministic artifact bundle under:

```text
artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/
```

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

The JSON outputs must clearly label:

- `synthetic_only: true`
- `evaluation_only: true`
- `error_anatomy_diagnostic_only: true`
- `not_formal_inference: true`
- `no_default_observation_change: true`
- `no_reconstruction_rule_change: true`
- `no_scoring_change: true`
- `no_candidate_change: true`

## Table Requirements

`site_target_time_error_audit.csv`
: One row per site with location, region, front band, truth/reconstruction/
  support-floor target times, signed and absolute status-quo error, signed and
  absolute support-floor error, error direction, error-magnitude class,
  false-negative status, Goal 012 primary mechanism where available,
  post-extirpation detection count, survey effort/gap features, near-horizon
  flags, and response-observable proxy flags.

`target_time_error_group_summary.csv`
: Grouped error summaries by deterministic grouping dimensions, including at
  least false-negative status, primary mechanism, region, front band,
  post-extirpation detection class, near-horizon class, survey-gap class, and
  status-quo finite class. Include counts, finite counts, mean/median signed
  error, mean/median absolute error, late/early/nonfinite counts, and support-
  floor improvement counts.

`error_mechanism_summary.csv`
: A compact mechanism-level table linking Goal 012 mechanism labels to target-
  time error direction, magnitude, support-floor change, and observability.

`observable_proxy_summary.csv`
: A table of candidate explanatory/proxy signals with columns identifying
  whether each signal is response-observable, truth-only, or mixed; the source
  artifact/columns; the affected site count; and whether it is suitable for a
  later response-observable rule-screen goal.

`transform_error_contrast.csv`
: A small table connecting Goal 014 transforms to site-level timing-error
  consequences, especially the difference between `goal013_support_floor` and
  `all_extirpated_true_time`.

`bias_classification_summary.csv`
: Deterministic classification of whether timing error is predominantly late,
  early, end-window compressed, spatially structured, survey-gap associated,
  detection-persistence associated, or truth-only.

## Recommendation Classes

The recommendation should classify the next project move without starting it.
Suggested classes:

- `response_observable_rule_screen_ready`: a small response-observable proxy
  set explains enough timing bias to justify a later bounded rule-screen goal.
- `timing_bias_truth_only_not_observable`: timing bias is clear under truth but
  not recoverable from response-only proxies.
- `survey_design_gap_dominates`: survey opportunity or end-window support
  dominates timing error and should be discussed before rule changes.
- `detection_persistence_rule_review_needed`: post-extirpation detections
  dominate timing error enough to motivate a later bounded rule-screen.
- `end_window_compression_dominates`: timing error is concentrated near the
  survey horizon, making late-window treatment the next likely target.
- `target_time_error_contract_failed`: prerequisite verification, site
  accounting, or group-summary reconciliation fails.

Do not start the recommended follow-on inside this goal.

## Acceptance Criteria

- The spec exists and is implemented.
- The CLI consumes required artifacts from disk and writes the required bundle.
- The site audit has one row per synth-small site and reconciles site count
  with the observation/truth artifacts.
- Status-quo finite count, false-negative count, Goal 013 support-floor finite
  count, and Goal 014 `all_extirpated_true_time` compatibility restoration
  reconcile with prior artifacts.
- Error summaries reconcile numerically with the site-level table.
- The observable-proxy inventory clearly separates response-observable,
  truth-only, and mixed signals.
- Recommendation classification is deterministic and does not start a rule
  change, scoring change, candidate change, or inference workflow.
- Focused tests pass.
- Proportionate full repository validation passes.
- Generated artifacts remain unstaged.
- No commit or push is performed.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.
