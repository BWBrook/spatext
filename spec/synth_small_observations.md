# `synth-small` First Response-Only Observation Layer

## Purpose

This document specifies the first synthetic observation layer over the current
default `synth-small` deterministic predator-response truth benchmark.

The layer converts latent prey abundance trajectories into noisy,
effort-conditioned response observations. It deliberately does not expose
predator arrival, predator pressure, or true extirpation in analyst-facing
tables. Those latent quantities are retained only in clearly labelled
evaluation artifacts used by inspection and smoke diagnostics.

## Scope

In scope:

- deterministic, seed-controlled observation generation,
- repeated visits at selected survey times,
- an explicit effort and detection/count model,
- disk-first inspection of emitted observation bundles,
- a lightweight recoverability smoke test using simple summaries,
- CSV, JSON, and Markdown review artifacts.

Out of scope:

- ABC, POM, MCMC, likelihood fitting, or parameter recovery,
- changing the deterministic predator-truth default,
- direct observation of predator arrival or predator pressure,
- remote compute or large simulation ensembles.

## Default Observation Design

The default observation bundle targets the current default predator-truth
benchmark approved by the deterministic sensitivity package.

The default random seed is:

```text
20260530
```

The default survey design is:

- spatial frame: all `25 x 25` `synth-small` cells are candidate sites,
- survey times: every four time steps from `0` through the predator-truth
  simulation horizon,
- repeated visits: two replicate visits for each sampled site-time,
- visit inclusion: incomplete and spatially biased, with higher visit
  probability in western and central bands and moderate suitability-related
  sampling bias,
- effort: positive continuous effort per realized visit, varying by region,
  time, and seed-controlled random noise.

This first design is intentionally compact. It is not meant to be a realistic
Great Britain water-vole survey design. Its purpose is to create a noisy,
auditable response-only layer that contains enough signal to test the next
stage of synthetic recovery machinery.

## Detection And Count Model

The latent abundance at a site and time is `N_t(x)`. For realized visit `v`,
effort is `E_v > 0`. The emitted count is a response observation:

```text
Y_v ~ Poisson(lambda_v)
lambda_v = E_v * count_scale * N_t(x) / (detection_half_saturation + N_t(x))
detected_v = 1[Y_v > 0]
```

The default values are:

```text
count_scale = 2.5
detection_half_saturation = 8.0
```

This makes detection probability monotone in both latent prey abundance and
survey effort, while retaining count noise and imperfect detection.

## Analyst-Facing Tables

The analyst-facing observation files are:

- `sites.csv`
- `visits.csv`
- `observations.csv`

These files may contain site identifiers, grid coordinates, broad observation
regions, visit times, replicate identifiers, effort, observed counts, and
detection indicators.

They must not contain:

- `driver_arrival`,
- `predator_pressure`,
- `true_extirpation`,
- `extirpation_lag`,
- `extirpated_by_end`,
- `initial_abundance`,
- `final_abundance`,
- any other direct predator-truth or latent-abundance column.

## Truth And Evaluation Tables

Truth is retained only for evaluation and inspection.

The observation bundle writes:

- `truth_reference.json`, a metadata file describing the upstream truth source
  and evaluation boundary,
- `evaluation_truth.csv`, a clearly labelled evaluation table containing
  hidden truth columns needed for recoverability smoke diagnostics.

These files are not analyst-facing observations.

## Output Contract

The build command writes under:

```text
artifacts/synth_small_observations/
```

Required root outputs:

- `observation_config.json`
- `truth_reference.json`
- `sites.csv`
- `visits.csv`
- `observations.csv`
- `evaluation_truth.csv`

Required inspection outputs:

- `inspection/verification.json`
- `inspection/observation_summary.csv`
- `inspection/recoverability_smoke.json`
- `inspection/report.md`

## Inspection Contract

Inspection must load an existing observation bundle from disk. It must not
silently regenerate observations in memory.

Hard verification checks should include at least:

- all required bundle files are present,
- JSON files are valid objects,
- CSV files have required schemas,
- analyst-facing tables exclude forbidden truth columns,
- visits and observations have a one-to-one `visit_id` relationship,
- observed counts are non-negative integers,
- detection indicators are binary and match `observed_count > 0`,
- effort values are finite and positive,
- visit times are within the declared simulation horizon,
- evaluation truth rows align with the site frame,
- at least one observation exists in early and late survey windows.

The inspection report should summarize:

- sampling design,
- effort and detection/count assumptions,
- spatial and temporal coverage,
- observed response patterns by time and region,
- temporal coverage relative to driver arrival and extirpation using
  evaluation-only truth,
- whether analyst-facing tables exclude predator-truth columns.

## Recoverability Smoke Test

The smoke test is not inference. It is a quick check for basic information
content in the noisy observations.

The default smoke metrics are:

- detection rate before driver arrival,
- detection rate after driver arrival,
- the drop from pre-arrival to post-arrival detection,
- late-window detection rate for truly extirpated sites,
- late-window detection rate for surviving sites,
- the difference between surviving and extirpated late detection rates,
- a simple AUC ranking diagnostic that uses low late detection as a score for
  true extirpation.

The smoke test passes when the metrics are finite and point in the expected
direction:

- post-arrival detection is lower than pre-arrival detection,
- truly extirpated sites have lower late-window detection than surviving sites,
- the late-detection AUC is above `0.60`.

These thresholds are deliberately weak. They only indicate that the first noisy
observation layer contains basic response signal. They do not prove parameter
identifiability or justify real-data interpretation.

## Acceptance Criteria

This work package is complete when:

- this spec exists,
- the observation build command writes the required bundle,
- the inspection command writes the required inspection artifacts,
- the analyst-facing tables exclude predator truth,
- recoverability smoke metrics are finite and documented,
- focused observation tests pass,
- the full repo quality lane passes.
