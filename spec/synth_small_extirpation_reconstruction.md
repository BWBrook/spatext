# `synth-small` Response-Only Extirpation Reconstruction

## Purpose

This document specifies a first-pass, auditable, response-only reconstruction layer
for the `synth-small` observation tables. The layer estimates an observed
extirpation proxy `T_X^obs(x)` from `sites.csv`, `visits.csv`, and
`observations.csv`, then evaluates that reconstruction against hidden truth only in
separate diagnostics.

The goal is not inference or fitting. It is a conservative baseline that makes
reconstruction logic explicit, reproducible, and separated from hidden-truth
inputs.

## Scope

In scope:

- response-only reconstruction from analyst-facing observation tables.
- per-site reconstruction records using a transparent final-sustained-absence rule.
- deterministic artifact emission for reconstruction, verification, and human-readable
  reporting.
- deterministic hidden-truth evaluation metrics written after reconstruction.

Out of scope:

- ABC, POM, likelihood fitting, parameter inference.
- estimating predator arrival, predator pressure, or latent process parameters.
- real data workflows.
- changing deterministic truth design or observation-design defaults.
- remote/distributed compute.

## Response-Only Input Contract

The reconstruction step reads only the existing observation bundle:

- `artifacts/synth_small_observations/sites.csv`
- `artifacts/synth_small_observations/visits.csv`
- `artifacts/synth_small_observations/observations.csv`
- `artifacts/synth_small_observations/observation_config.json`

Optional evaluation only:

- `artifacts/synth_small_observations/evaluation_truth.csv`

The following columns must not be used in reconstruction logic:

- `driver_arrival`
- `true_extirpation`
- `extirpation_lag`
- `extirpated_by_end`
- `initial_abundance`
- `final_abundance`

## Reconstruction Rule

For each site `x`, aggregate by survey time:

1. Count surveyed times, realized visits, observed counts, and detections.
2. Find the last observed detection time.
3. Inspect the final run of surveyed times after the last detection where
   - visit effort is positive,
   - and detections are zero.
4. If that final zero-detection run has length at least 2, set:
   - `observed_extirpated_by_end = 1`
   - `observed_extirpation_time =` first time in that final run
   Else set:
   - `observed_extirpated_by_end = 0`
5. If a site has no detection history or no surveyed times, classify it as
   `insufficient_history`.

All logic is intentionally conservative and auditable. The rule does not estimate
driver arrival or abundance and does not claim certainty.

## Output Artifacts

The reconstruction command writes:

- `artifacts/synth_small_extirpation_reconstruction/reconstruction_config.json`
- `artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv`
- `artifacts/synth_small_extirpation_reconstruction/time_detection_summary.csv`
- `artifacts/synth_small_extirpation_reconstruction/verification.json`
- `artifacts/synth_small_extirpation_reconstruction/evaluation_metrics.json`
- `artifacts/synth_small_extirpation_reconstruction/report.md`

### `site_reconstruction.csv`

Required columns:

- `site_id`
- `cell_id`
- `row`
- `col`
- `region`
- `front_band`
- `visit_count`
- `survey_time_count`
- `detection_count`
- `first_detection_time`
- `last_detection_time`
- `final_absence_start_time`
- `final_absence_survey_time_count`
- `observed_extirpated_by_end`
- `observed_extirpation_time`
- `reconstruction_status`

Forbidden in this file:

- `driver_arrival`
- `predator_pressure`
- `true_extirpation`
- `extirpation_lag`
- `extirpated_by_end`
- `initial_abundance`
- `final_abundance`
- any additional hidden-truth latent columns.

### `time_detection_summary.csv`

Required columns:

- `time_index`
- `visit_count`
- `site_count`
- `observation_count`
- `detection_count`
- `detection_rate`
- `mean_observed_count`
- `mean_effort`

### `verification.json`

Machine-readable validation and contract checks, including response-only boundary
checks and schema checks on required output columns.

### `evaluation_metrics.json`

Evaluation-only diagnostics that compare reconstruction against `evaluation_truth.csv`.

Minimum fields:

- `site_coverage`
- `confusion_matrix`
- `sensitivity`
- `specificity`
- `precision`
- `temporal_error`
- `bias_by_region`
- `bias_by_front_band`
- `interpretation`
- `limits`

### `report.md`

Human-readable report that summarizes:

- command inputs and reconstruction rule,
- response-only output schema boundary,
- reconstruction status counts,
- coverage summary,
- hidden-truth classification and error summaries,
- spatial-temporal failure notes and next-step recommendation.

## Acceptance Criteria

- this spec exists and is implemented;
- deterministic reconstruction artifacts are emitted;
- `site_reconstruction.csv` omits hidden-truth columns;
- response-only reconstruction is performed without hidden truth;
- separate evaluation payload quantifies agreement with hidden truth;
- focused tests pass:
  - schema integrity,
  - forbidden-column exclusion,
  - reconstruction handling of never-detected and no-survey sites,
  - evaluation finite metrics where defined,
  - scripts execute successfully.
