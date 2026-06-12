# Synth-Small False-Negative Mechanism Audit

## Purpose

The synth-small false-negative mechanism audit explains the `101`
response-screen false negatives identified by the Goal 011 compatibility
mismatch audit.

This layer is synthetic-only, evaluation-only, audit-only, and disk-first. It
classifies why truly extirpated sites were not reconstructed as observed
extirpations. It does not change reconstruction rules, observation settings,
response-screen logic, compatibility scoring, mismatch-audit logic, or any
inference machinery.

## Input Contract

The audit reads existing emitted artifacts from disk:

Response-screen evaluation:

- `artifacts/synth_small_response_screen/evaluation/screen_evaluation_summary.json`
- `artifacts/synth_small_response_screen/evaluation/group_evaluation_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/site_evaluation_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/verification.json`

Extirpation reconstruction:

- `artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv`
- `artifacts/synth_small_extirpation_reconstruction/time_detection_summary.csv`
- `artifacts/synth_small_extirpation_reconstruction/verification.json`

Observation bundle:

- `artifacts/synth_small_observations/visits.csv`
- `artifacts/synth_small_observations/observations.csv`
- `artifacts/synth_small_observations/evaluation_truth.csv`
- `artifacts/synth_small_observations/truth_reference.json`

Goal 011 mismatch audit:

- `artifacts/synth_small_compatibility_screen/mismatch_audit/evaluation_bridge_summary.json`
- `artifacts/synth_small_compatibility_screen/mismatch_audit/recommendation.json`
- `artifacts/synth_small_compatibility_screen/mismatch_audit/verification.json`

All prerequisite verification payloads must be present and passing before the
false-negative audit can pass. Missing prerequisites should be rebuilt through
the Goal 012 runbook rather than silently skipped.

## Output Contract

The audit writes:

`artifacts/synth_small_response_screen/evaluation/false_negative_audit/`

Required files:

- `false_negative_audit_config.json`
- `false_negative_site_audit.csv`
- `mechanism_summary.csv`
- `group_mechanism_summary.csv`
- `observation_timing_summary.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

All JSON outputs must include:

- `synthetic_only: true`
- `audit_only: true`
- `evaluation_only: true`
- `not_formal_inference: true`
- `no_reconstruction_change: true`
- `no_observation_design_change: true`
- `no_scoring_change: true`

## Site-Level Feature Contract

`false_negative_site_audit.csv` contains exactly one row for every site whose
response-screen evaluation classification is `fn`.

Required columns:

- `site_id`
- `cell_id`
- `row`
- `col`
- `region`
- `front_band`
- `primary_mechanism`
- `secondary_flags`
- `true_extirpation_time`
- `observed_extirpation_time`
- `reconstruction_status`
- `visit_count`
- `survey_time_count`
- `detection_count`
- `first_detection_time`
- `last_detection_time`
- `final_absence_start_time`
- `final_absence_survey_time_count`
- `first_survey_time`
- `last_survey_time`
- `first_post_extirpation_survey_time`
- `post_extirpation_survey_time_count`
- `post_extirpation_detection_count`
- `post_extirpation_detection_time_count`
- `mean_effort`
- `min_effort`
- `max_effort`
- `post_extirpation_mean_effort`
- `last_detection_minus_true_extirpation`
- `first_post_survey_minus_true_extirpation`
- `last_survey_minus_true_extirpation`

Post-extirpation survey and detection counts use strict timing:
`time_index > true_extirpation_time`.

## Mechanism Priority

Every false negative receives exactly one primary mechanism using this priority
order:

1. `no_post_extirpation_surveys`: no surveyed time occurs after true
   extirpation.
2. `late_extirpation_near_survey_horizon`: fewer than two post-extirpation
   surveyed times and the last surveyed time is within `8` time units of true
   extirpation.
3. `post_extirpation_detection_blocks_absence`: at least one detection occurs
   after true extirpation, preventing a final sustained-absence call.
4. `insufficient_post_extirpation_survey_history`: post-extirpation survey
   history exists but cannot satisfy the two-survey final absence rule.
5. `sparse_or_low_effort_observation`: sparse visit, survey-time, or
   detection counts, or low emitted effort diagnostics, remain after
   higher-priority timing mechanisms are excluded. The default low-effort
   checks are `mean_effort <= 0.9` or `min_effort <= 0.65`; those effort
   values are emitted at site level so the label is auditable from disk.
6. `weak_east_or_edge_signal`: the false negative belongs to the eastern
   region or east front band after higher-priority mechanisms are excluded.
7. `unclassified_false_negative`: a catch-all that should remain empty under
   the current default artifacts.

Secondary flags may include overlapping diagnostics such as
`weak_east_or_edge_signal`, `sparse_or_low_effort_observation`,
`post_extirpation_detection_seen`, `limited_post_extirpation_surveys`, and
`near_survey_horizon`.

The expected current primary mechanism counts are:

- `no_post_extirpation_surveys`: `39`
- `late_extirpation_near_survey_horizon`: `30`
- `post_extirpation_detection_blocks_absence`: `28`
- `insufficient_post_extirpation_survey_history`: `4`

## Summary Outputs

### `mechanism_summary.csv`

One row per primary mechanism.

Columns:

- `primary_mechanism`
- `false_negative_count`
- `false_negative_fraction`
- `mean_post_extirpation_survey_time_count`
- `mean_post_extirpation_detection_count`
- `mean_last_survey_minus_true_extirpation`

### `group_mechanism_summary.csv`

One row per group and primary mechanism for `region` and `front_band`.

Columns:

- `group_type`
- `group`
- `primary_mechanism`
- `false_negative_count`
- `group_false_negative_count`
- `group_share`
- `total_false_negative_share`

### `observation_timing_summary.csv`

One row for the overall audit and one row per primary mechanism, region, and
front band.

Columns:

- `summary_type`
- `label`
- `false_negative_count`
- `mean_post_extirpation_survey_time_count`
- `median_post_extirpation_survey_time_count`
- `mean_post_extirpation_detection_count`
- `mean_true_extirpation_time`
- `mean_last_survey_minus_true_extirpation`
- `mean_last_detection_minus_true_extirpation`
- `mean_first_post_survey_minus_true_extirpation`
- `mean_effort`
- `mean_min_effort`
- `mean_max_effort`
- `mean_post_extirpation_mean_effort`
- `low_mean_effort_count`
- `low_min_effort_count`
- `near_horizon_count`
- `no_post_extirpation_survey_count`

## Recommendation Classes

The audit emits one recommendation class:

- `diagnose_post_extirpation_observation_gap_before_rule_change`: no or late
  post-extirpation survey coverage explains most false negatives.
- `diagnose_post_extirpation_detection_persistence_before_rule_change`:
  post-extirpation detections are the dominant mechanism.
- `review_group_specific_observation_support`: one group explains a dominant
  share after timing mechanisms are not dominant.
- `screen_contract_bug_suspected`: prerequisite verification, count
  reconciliation, or Goal 011 bridge checks fail.
- `ready_for_reconstruction_rule_review`: no dominant observation/timing
  mechanism remains after audit reconciliation.

The expected current recommendation is
`diagnose_post_extirpation_observation_gap_before_rule_change`.

## Acceptance Criteria

- The CLI consumes the required artifacts from disk.
- All `101` false negatives appear exactly once in
  `false_negative_site_audit.csv`.
- Every false negative has exactly one primary mechanism.
- Mechanism, group, and timing summaries reconcile to the false-negative
  count.
- Recommendation JSON identifies the next diagnostic intervention class but
  does not authorize a reconstruction-rule, observation-design, scoring, ABC,
  POM, or real-data change.
- Generated artifacts remain ignored and unstaged.
