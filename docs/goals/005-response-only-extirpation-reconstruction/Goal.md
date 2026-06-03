# Goal 005: Response-Only Extirpation Reconstruction

## Objective

Build the first `synth-small` response-only extirpation reconstruction layer.

The goal is to estimate an observed extirpation proxy, `T_X^obs`, from the
analyst-facing observation tables only, then evaluate that reconstruction
against hidden truth in a clearly separated diagnostic step.

This is the bridge between noisy observations and later ABC/POM machinery. It
must remain a transparent reconstruction baseline, not an inference engine.

## Context

Goals 001-004 established and published a clean synthetic pilot checkpoint:

- deterministic predator-response hidden truth,
- predator-truth inspection,
- deterministic sensitivity/readiness diagnostics,
- first response-only observation bundle,
- observation inspection and recoverability smoke diagnostics,
- pushed publication checkpoint on `main`.

The Goal 003 smoke diagnostic showed that noisy observations retain basic
signal about true extirpation, but it did not reconstruct a per-site observed
extirpation surface. Goal 005 should create that missing object.

## Scientific Question

Using only response-side survey data, can a simple, auditable rule reconstruct
enough of the latent extirpation pattern to justify moving toward formal
inference later?

For this goal, "enough" means:

- every reconstructed value has a clear response-only provenance,
- reconstruction failures are explicit,
- hidden truth is used only for evaluation diagnostics,
- the evaluation report shows spatial, temporal, and classification failure
  modes.

## In Scope

- Add a spec for response-only extirpation reconstruction.
- Add a small reconstruction module under `src/spatext/synth/small/`.
- Add CLI script(s) that load existing observation artifacts from disk.
- Produce deterministic reconstruction artifacts under:

```text
artifacts/synth_small_extirpation_reconstruction/
```

- Produce an evaluation-only comparison against hidden truth.
- Add tests for reconstruction rules, output schemas, truth separation, and
  evaluation metrics.
- Update package exports and `spec/report_log.md`.
- Update this goal log as work proceeds.

## Out Of Scope

- ABC, POM, MCMC, likelihood fitting, or parameter inference.
- Estimating predator arrival, predator pressure, or process parameters.
- Changing the deterministic truth benchmark.
- Changing the observation-generation design.
- Using hidden truth inside the response-only reconstruction algorithm.
- Real mink-water-vole case-study data.
- Remote compute or large sweeps.
- Commit or push unless the supervisor explicitly sends a publication
  follow-up.

## Required Response-Only Inputs

The reconstruction step may use only:

- `artifacts/synth_small_observations/sites.csv`
- `artifacts/synth_small_observations/visits.csv`
- `artifacts/synth_small_observations/observations.csv`
- `artifacts/synth_small_observations/observation_config.json`

The reconstruction step must not use:

- `evaluation_truth.csv`
- `truth_reference.json` truth summaries
- predator-truth surfaces or trajectories
- latent abundance arrays
- driver-arrival arrays

Hidden truth may be loaded only after response-only reconstruction artifacts
exist, and only to create evaluation diagnostics.

## Suggested Reconstruction Rule

Keep the first implementation deliberately simple and explainable.

For each site:

1. Aggregate observations by `site_id` and `time_index`.
2. Record visit count, total effort, total observed count, and whether any
   detection occurred at each surveyed time.
3. Identify the last observed detection time.
4. Search for a final sustained absence run after the last detection:
   consecutive surveyed times with visits, positive effort, and zero detections.
5. If the final absence run has at least two surveyed time points, classify the
   site as observed-extirpated by end and set `T_X^obs` to the first time in
   that final absence run.
6. If the site has late detections or no adequate final absence run, classify
   it as not observed-extirpated by end.
7. If the site has no usable observation history, mark it as insufficient data.

This rule is intentionally a baseline. If a better simple rule emerges during
implementation, use it only if the report explains the decision and preserves
the response-only boundary.

## Required Outputs

At minimum, write:

```text
artifacts/synth_small_extirpation_reconstruction/reconstruction_config.json
artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv
artifacts/synth_small_extirpation_reconstruction/time_detection_summary.csv
artifacts/synth_small_extirpation_reconstruction/verification.json
artifacts/synth_small_extirpation_reconstruction/evaluation_metrics.json
artifacts/synth_small_extirpation_reconstruction/report.md
```

### `site_reconstruction.csv`

This is the primary response-only output. It should include fields such as:

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

It must not contain hidden-truth columns such as `driver_arrival`,
`true_extirpation`, `extirpation_lag`, `extirpated_by_end`,
`initial_abundance`, `final_abundance`, or predator-pressure columns.

### `time_detection_summary.csv`

This should summarize response-only detection patterns by survey time, including
visit counts, site counts, detection rates, and mean observed counts.

### `verification.json`

This should verify output schema and response-only truth separation.

### `evaluation_metrics.json`

This is evaluation-only. It may use `evaluation_truth.csv` and should report at
least:

- site coverage,
- confusion matrix for observed vs true extirpated-by-end,
- sensitivity / specificity or equivalent,
- precision or positive predictive value when defined,
- temporal error for sites with both observed and true extirpation times,
- bias summaries by `region` and/or `front_band`,
- a short interpretation and limits block.

### `report.md`

The report should be readable without opening JSON:

- inputs used,
- reconstruction rule,
- response-only schema boundary,
- aggregate reconstruction results,
- hidden-truth evaluation results,
- spatial/temporal failure modes,
- recommendation on whether to proceed toward ABC/POM next or refine the
  reconstruction baseline first.

## Acceptance Criteria

This goal is complete when:

- the spec exists,
- reconstruction artifacts are written deterministically,
- response-only outputs exclude hidden truth,
- evaluation metrics are separated and clearly labelled,
- focused tests pass,
- the full repo quality lane passes,
- `spec/report_log.md` records the interaction,
- `Log.md` records the final status and next recommendation.
