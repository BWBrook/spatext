# Synth-Small Target-Timing Residual Decomposition

Goal 014 adds a synthetic-only, evaluation-only residual-decomposition
diagnostic for the current synth-small compatibility bridge.

The diagnostic asks why the Goal 013 finite-target-restored scenario remains
incompatible under the unchanged Goal 009 summary-vector and Goal 010
compatibility-screen contracts. It compares a small deterministic set of target
time transforms, scores them against the existing candidate set, and decomposes
loss by summary-vector component.

## Scope

This is a diagnostic table bundle only.

- It does not change default observation-design settings.
- It does not rewrite default observation or reconstruction artifacts.
- It does not change the production final-absence reconstruction rule or
  `min_final_absence_run`.
- It does not change response-screen, summary-vector, compatibility-screen,
  mismatch-audit, false-negative-audit, counterfactual-screen, threshold,
  scale, weight, rank, class, or candidate logic.
- It does not start ABC, POM, likelihood fitting, posterior interpretation,
  parameter recovery, real-data analysis, broad sweeps, or remote compute.

Hidden synthetic truth may be used only inside explicitly labelled
synthetic-only, evaluation-only, target-transform diagnostic outputs.

## Inputs

The builder reads existing emitted artifacts from disk:

- `artifacts/synth_small_observations/`
- `artifacts/synth_small_extirpation_reconstruction/`
- `artifacts/synth_small_response_screen/evaluation/`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/`
- `artifacts/synth_small_summary_vector/`
- `artifacts/synth_small_compatibility_screen/`

The published Goal 009 summary-vector artifact contract emits
`summary_vector_config.json`, `summary_components.csv`, `mode_summary.json`,
`coverage_curve.csv`, and `verification.json`. Goal 014 treats those files as
the source-of-truth summary-vector bridge and records that the packet-listed
`summary_vector/target_summary.json` name is not part of the existing Goal 009
contract. The Goal 010 compatibility-screen `target_summary.json` remains a
required bridge artifact.

All prerequisite verification payloads must be present and passing before the
Goal 014 verification can pass.

## Target Transforms

The transform set is intentionally small and ordered:

`status_quo_observed`
: Current `realistic_observed` reconstructed target from
  `site_reconstruction.csv:observed_extirpation_time`.

`goal013_support_floor`
: The emitted Goal 013 `truth_guided_absence_floor_all` target, using
  counterfactual support times for resolved false negatives and status quo
  times elsewhere.

`false_negative_true_time`
: Status quo with every Goal 012 false-negative site made finite at its
  synthetic true extirpation time.

`false_negative_true_time_detection_respecting`
: Status quo with only false-negative sites that have no post-extirpation
  detections made finite at their synthetic true extirpation time. Sites with
  post-extirpation detections remain unresolved.

`all_extirpated_true_time`
: Every truly extirpated finite target site is set to its synthetic true
  extirpation time. This transform must reconcile with the established Goal
  010 `ideal_true` compatibility expectation.

These transforms are diagnostic targets, not analyst-facing reconstruction
rules.

## Outputs

The CLI writes:

`artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/`

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

All JSON outputs include:

- `synthetic_only: true`
- `evaluation_only: true`
- `target_transform_diagnostic_only: true`
- `not_formal_inference: true`
- `no_default_observation_change: true`
- `no_reconstruction_rule_change: true`
- `no_scoring_change: true`
- `no_candidate_change: true`

## Table Contracts

`target_transform_definitions.csv`
: One row per transform with stable ID, boundary labels, target site rule,
  target time rule, and scientific contrast.

`site_target_transform_resolution.csv`
: One row per site per transform with site ID, location, false-negative status,
  Goal 012 primary mechanism where applicable, status-quo target time,
  transformed target time, true extirpation time, Goal 013 counterfactual time
  where applicable, and resolution class.

`target_transform_summary_vectors.csv`
: Long-form scalar summary-component and coverage-curve rows for every
  transform, using the Goal 009 summary-vector helper semantics.

`target_transform_component_losses.csv`
: One row per transform, candidate, and scored component. The table includes
  target value, candidate value, absolute gap, normalized gap, weight, scale,
  weighted gap, and missing reason.

`target_transform_rankings.csv`
: One row per transform and candidate with deterministic rank, total weighted
  loss, and compatibility class from the unchanged Goal 010 contract.

`component_delta_table.csv`
: One row per transform, candidate, and component with residual weighted gap,
  the corresponding `status_quo_observed` and `goal013_support_floor` weighted
  gaps, signed deltas from both baselines, absolute deltas from both
  baselines, residual contribution rank, absolute-delta-from-status-quo rank,
  and absolute-delta-from-Goal-013-support-floor rank within each
  transform/candidate. Ranks are deterministic: descending contribution or
  absolute delta, with component-name tie breaks.

## Reconciliation Checks

Goal 014 must verify:

- `status_quo_observed` reconciles with Goal 010/013 `realistic_observed`:
  finite target count `151`, top candidate `default`, class `incompatible`,
  and loss `3.52263635737` within numerical tolerance.
- `goal013_support_floor` reconciles with the emitted Goal 013
  `truth_guided_absence_floor_all` scenario: finite target count `252`, top
  candidate `default`, class `incompatible`, and loss `1.88500331398` within
  numerical tolerance.
- `all_extirpated_true_time` reconciles with the Goal 010 `ideal_true`
  expectation: finite target count `252`, top candidate `default`, class
  `compatible`, and loss `0`.
- Component losses sum to ranking totals for valid rows, and the scored
  component table has the expected row count.

If these checks fail, the recommendation must be `residual_contract_failed` or
`compatibility_contract_review_needed` rather than hiding the mismatch.

## Recommendation

The recommendation class identifies the next discussion target without starting
it. Current classes are:

- `timing_bias_drives_residual`
- `coverage_shape_drives_residual`
- `spatial_alignment_drives_residual`
- `compatibility_contract_review_needed`
- `ready_for_inference_design_discussion`
- `residual_contract_failed`

The expected current result is that `all_extirpated_true_time` restores the
Goal 010 ideal-truth bridge, while `goal013_support_floor` remains
incompatible with dominant residual losses in coverage/timing/shape
components. Any follow-on reconstruction-rule, observation-design, candidate,
ABC, POM, or real-data work requires a later bounded goal.
