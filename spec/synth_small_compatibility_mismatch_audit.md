# Synth-Small Compatibility Mismatch Audit

## Purpose

The synth-small compatibility mismatch audit explains why the Goal 010
compatibility screen accepts the deterministic default candidate under
`ideal_true` but rejects all candidates under `realistic_observed`.

This layer is synthetic-only and disk-first. It consumes already-emitted Goal
008, Goal 009, and Goal 010 artifacts, writes an audit bundle, and does not
change compatibility-screen scoring, candidate ranks, thresholds, classes, or
candidate definitions.

## Input Contract

The audit reads these prerequisite bundles:

- `artifacts/synth_small_summary_vector/`
  - `summary_components.csv`
  - `coverage_curve.csv`
  - `mode_summary.json`
  - `verification.json`
- `artifacts/synth_small_compatibility_screen/`
  - `compatibility_screen_config.json`
  - `target_summary.json`
  - `candidate_scores.csv`
  - `coverage_score_breakdown.csv`
  - `mode_rankings.csv`
  - `verification.json`
- `artifacts/synth_small_response_screen/evaluation/`
  - `screen_evaluation_summary.json`
  - `group_evaluation_summary.csv`
  - `site_evaluation_audit.csv`
  - `verification.json`

All input verification payloads must be present and pass before the audit can
pass. Missing prerequisites should be rebuilt through the Goal 011 runbook, not
silently skipped.

## Output Contract

The audit writes to:

`artifacts/synth_small_compatibility_screen/mismatch_audit/`

Required files:

- `mismatch_audit_config.json`
- `target_delta_summary.csv`
- `score_contribution_summary.csv`
- `coverage_gap_summary.csv`
- `evaluation_bridge_summary.json`
- `recommendation.json`
- `verification.json`
- `report.md`

All JSON outputs must label the bundle as `synthetic_only`, `audit_only`,
`not_formal_inference`, and `no_scoring_change`.

## CSV Schemas

### `target_delta_summary.csv`

One row per scalar summary component and coverage breakpoint comparing
`realistic_observed` to `ideal_true`.

Columns:

- `summary_type`: `component` or `coverage_curve`
- `metric`: component name or `coverage_target_time:<coverage_fraction>`
- `ideal_true_value`
- `realistic_observed_value`
- `delta`: `realistic_observed_value - ideal_true_value`
- `absolute_delta`
- `missing_reason`

### `score_contribution_summary.csv`

One row per Goal 010 score component for the top-ranked
`realistic_observed` candidate.

Columns:

- `target_mode`
- `candidate_label`
- `rank`
- `component`
- `target_value`
- `candidate_value`
- `absolute_gap`
- `scale`
- `weight`
- `normalized_abs_gap`
- `weighted_gap`
- `loss_share`
- `missing_reason`

Rows are sorted by descending `weighted_gap`, then component name. This makes
the dominant mismatch components directly auditable from the emitted CSV.

### `coverage_gap_summary.csv`

One row per coverage breakpoint for the top-ranked `realistic_observed`
candidate.

Columns:

- `target_mode`
- `candidate_label`
- `coverage_fraction`
- `target_time`
- `candidate_time`
- `signed_gap`: `candidate_time - target_time`
- `absolute_gap`
- `squared_gap`
- `rmse`
- `scale`
- `weight`
- `missing_reason`

The `rmse` column is repeated for each row so a reviewer can reconstruct the
`coverage_curve_rmse` score contribution from the per-breakpoint `squared_gap`
values.

## Bridge Summary

`evaluation_bridge_summary.json` reports:

- ideal and realistic finite-target counts from `summary_components.csv`
- `finite_target_drop = ideal_true_finite_target_count -
  realistic_observed_finite_target_count`
- response-screen confusion matrix and false-negative count from
  `screen_evaluation_summary.json`
- `false_negative_bridge_difference = finite_target_drop -
  false_negative_count`
- `false_negative_bridge_fraction = false_negative_count /
  finite_target_drop` when the drop is positive
- false-negative and weak-signal group summaries copied from the evaluation
  artifact

The expected current bridge class is
`finite_target_drop_matches_false_negatives` because the finite-target drop is
`101` and the response-screen false-negative count is `101`.

## Recommendation Classes

The audit emits exactly one recommendation class:

- `diagnose_observation_reconstruction_before_abc`: ideal default is
  compatible, all `realistic_observed` candidates are incompatible, and the
  finite-target drop is largely explained by response-screen false negatives.
- `screen_contract_bug_suspected`: prerequisite verification fails or the
  screen artifacts contradict required ranking/class invariants.
- `candidate_expansion_may_be_warranted`: ideal default is compatible and the
  false-negative bridge does not explain most realistic-observed mismatch.
- `ready_for_next_inference_design`: ideal and realistic modes are both
  compatible without the above warnings.

The Goal 011 expected current recommendation is
`diagnose_observation_reconstruction_before_abc`.

