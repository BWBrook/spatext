# Goal 014: Synth-Small Target-Timing Residual Decomposition

## Objective

Build a synthetic-only, evaluation-only residual-decomposition diagnostic that
explains why the finite-target-restored Goal 013 target remains incompatible
under the existing summary-vector and compatibility-screen bridge.

The primary deliverable is a compact, auditable set of tables that decomposes
compatibility loss across target-time transformations and summary-vector
components. This goal should make the next scientific decision clearer without
changing reconstruction rules, observation design, scoring, candidates, or
inference machinery.

## Context

Goals 009-013 established the current diagnostic ladder:

- Goal 009 added the `S(T_X, T_P)` summary-vector bridge.
- Goal 010 showed the default candidate is compatible under `ideal_true` but
  incompatible under `realistic_observed`.
- Goal 011 showed that the finite-target drop from `ideal_true` to
  `realistic_observed` exactly matches the `101` response-screen false
  negatives.
- Goal 012 diagnosed the false-negative mechanisms.
- Goal 013 tested post-extirpation observation-support counterfactuals.

Goal 013 produced the important result that
`truth_guided_absence_floor_all` restores the finite-target count to `252` and
resolves all `101` false negatives, but still leaves the default candidate
`incompatible` with loss about `1.88500331398`. The dominant residual
components appear to be timing and target-shape terms, especially
`coverage_curve_rmse`, `lag_mean`, `front_plane_gradient_magnitude`, and
`arrival_target_r2`.

The next question is therefore no longer only "can missing finite targets be
restored?" It is "which target-time distortions remain after finite-target
support is restored, and do truth-guided target-time replacements restore the
compatibility bridge?"

## Scientific Question

For the synth-small system, which finite-site target-time transformation first
restores compatibility with the default process candidate under the unchanged
Goal 009/010 bridge, and which summary-vector components dominate the residual
loss when compatibility is not restored?

## In Scope

- Add `spec/synth_small_target_timing_residual_decomposition.md`.
- Add a focused module under `src/spatext/synth/small/`, probably
  `target_timing_residual_decomposition.py`.
- Add a CLI script, probably
  `scripts/analyze_synth_small_target_timing_residuals.py`.
- Read existing emitted synthetic artifacts from disk.
- Define a small deterministic target-time transformation set with stable
  transform IDs.
- Reuse the existing summary-vector and compatibility-screen contracts without
  changing their scoring weights, thresholds, candidates, or classes.
- Emit per-transform summary vectors, component losses, rankings, and delta
  tables.
- Emit per-site resolution rows that explain which sites changed target status
  or target time under each transformation.
- Report whether each transform reconciles with the Goal 010 `ideal_true`
  bridge, Goal 010/013 `realistic_observed` baseline, and Goal 013
  `truth_guided_absence_floor_all` scenario.
- Emit deterministic audit artifacts under:
  `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/`.
- Add focused tests for transform definitions, reconciliation, component-loss
  accounting, delta-table ranking, recommendation classification, CLI
  execution, and boundary labels.
- Update exports, README, `AGENTS.md` if the authoritative spec list changes,
  `spec/report_log.md`, and this goal log.

## Out Of Scope

- Changing default observation-design settings.
- Changing emitted default observation artifacts.
- Changing the production reconstruction rule or `min_final_absence_run`.
- Changing response-screen, summary-vector, compatibility-screen,
  mismatch-audit, false-negative-audit, or counterfactual-screen scoring logic.
- Adding new process candidates or broad parameter sweeps.
- ABC, POM, MCMC, likelihood fitting, posterior claims, or parameter recovery.
- Real-data analysis.
- Remote compute.
- Commit or push.

## Target-Time Transform Principles

This diagnostic may use hidden synthetic truth only because it is explicitly
synthetic-only and evaluation-only. Any truth-guided replacement must be
labelled as a diagnostic target transformation, not as an analyst-facing
reconstruction method.

Keep the transform set small and interpretable. It should include at least:

- `status_quo_observed`: the current `realistic_observed` reconstructed target.
- `goal013_support_floor`: the Goal 013
  `truth_guided_absence_floor_all` target, reconciled from the emitted
  counterfactual bundle.
- `false_negative_true_time`: the status-quo target with Goal 012
  false-negative sites made finite at their synthetic true extirpation time.
- `false_negative_true_time_detection_respecting`: like the previous transform,
  but only for false negatives not blocked by post-extirpation detections.
- `all_extirpated_true_time`: every truly extirpated finite target site is set
  to its synthetic true extirpation time.

If the existing artifact contracts make one of these names awkward, adapt the
implementation while preserving the scientific contrasts. Do not grow this into
a broad transform sweep.

## Required Inputs

The command should read these existing artifacts from disk.

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
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/recommendation.json`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/verification.json`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/counterfactual_config.json`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/site_counterfactual_resolution.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/scenario_summary_vectors.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/scenario_compatibility_scores.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/scenario_rankings.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/verification.json`

Bridge artifacts:

- `artifacts/synth_small_summary_vector/target_summary.json`
- `artifacts/synth_small_summary_vector/mode_summary.json`
- `artifacts/synth_small_summary_vector/verification.json`
- `artifacts/synth_small_compatibility_screen/target_summary.json`
- `artifacts/synth_small_compatibility_screen/candidate_scores.csv`
- `artifacts/synth_small_compatibility_screen/mode_rankings.csv`
- `artifacts/synth_small_compatibility_screen/coverage_score_breakdown.csv`
- `artifacts/synth_small_compatibility_screen/verification.json`

The command should fail loudly when required inputs are missing. The runbook may
rebuild the local ignored artifact chain first.

## Required Outputs

Write a deterministic artifact bundle under:

```text
artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/
```

Required files:

- `residual_decomposition_config.json`
- `target_transform_definitions.csv`
- `site_target_transform_resolution.csv`
- `target_transform_summary_vectors.csv`
- `target_transform_component_losses.csv`
- `target_transform_rankings.csv`
- `component_delta_table.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

The JSON outputs must clearly label:

- `synthetic_only: true`
- `evaluation_only: true`
- `target_transform_diagnostic_only: true`
- `not_formal_inference: true`
- `no_default_observation_change: true`
- `no_reconstruction_rule_change: true`
- `no_scoring_change: true`
- `no_candidate_change: true`

## Table Requirements

The emitted tables should be useful for scientific diagnosis, not just
machine-readable compliance.

- `target_transform_definitions.csv` should identify each transform, whether it
  uses hidden truth, and the intended scientific contrast.
- `site_target_transform_resolution.csv` should include at least one row per
  transformed site per transform, including site ID, false-negative status,
  primary Goal 012 mechanism if available, original target state/time,
  transformed target state/time, true extirpation time, and resolution class.
- `target_transform_summary_vectors.csv` should expose the summary-vector
  components for every transform.
- `target_transform_component_losses.csv` should include one row per transform,
  candidate, and scored component, with target value, candidate value,
  absolute gap, normalized gap, weight, and weighted gap.
- `target_transform_rankings.csv` should show the top candidate, class, and
  total loss for each transform.
- `component_delta_table.csv` should rank component contributions and deltas
  from both `status_quo_observed` and `goal013_support_floor`.

## Recommendation Classes

The recommendation should classify the next project move without starting it.
Suggested classes:

- `timing_bias_drives_residual`: truth-guided target times restore
  compatibility, and timing/lag components explain most of the loss delta.
- `coverage_shape_drives_residual`: finite targets and true-time replacement
  improve timing but coverage-shape components remain dominant.
- `spatial_alignment_drives_residual`: front-plane or spatial alignment
  components remain dominant after target-time replacement.
- `compatibility_contract_review_needed`: even `all_extirpated_true_time` does
  not reconcile with the established `ideal_true` compatibility bridge.
- `ready_for_inference_design_discussion`: only if compatibility is restored
  and residual diagnostics no longer point to observation or reconstruction
  artifacts as the primary blocker.
- `residual_contract_failed`: prerequisite verification, transform accounting,
  or bridge reconciliation fails.

The last two classes are discussion recommendations only. Do not start ABC/POM
work inside this goal.

## Acceptance Criteria

- The spec exists and is implemented.
- The CLI consumes required artifacts from disk and writes the required bundle.
- Transform definitions are documented and emitted with stable IDs.
- The `status_quo_observed` transform reconciles with current Goal 010/013
  `realistic_observed` counts, top candidate, class, and loss.
- The `goal013_support_floor` transform reconciles with the emitted Goal 013
  `truth_guided_absence_floor_all` scenario counts, top candidate, class, and
  loss.
- The `all_extirpated_true_time` transform reconciles with the Goal 010
  `ideal_true` finite-target count and compatibility expectation; if it does
  not, the bundle must classify this as a contract failure rather than hiding
  it.
- Component losses and total losses are numerically reconcilable from the
  emitted tables.
- At least one emitted table ranks residual components by contribution and
  delta from both status quo and the Goal 013 support floor.
- The recommendation identifies the next intervention class without changing
  production observation, reconstruction, scoring, candidates, or inference
  logic.
- Focused tests pass.
- Proportionate full repository validation passes.
- Generated artifacts remain unstaged.
- No commit or push is performed.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.
