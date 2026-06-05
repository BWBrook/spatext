# `synth-small` Response-Only Screen

## Purpose

This document specifies a tiny response-only screen over the Goal 005
`T_X^obs` reconstruction artifacts.

The screen is a summary and diagnostic layer. It is not ABC, POM, likelihood
fitting, posterior inference, driver-arrival inference, or real-data analysis.

## Scope

In scope:

- consume existing response-side reconstruction artifacts from disk;
- compute compact site, group, and time summaries;
- report weak-information and failure-mode diagnostics;
- emit deterministic screen artifacts for human review;
- keep screen inputs and outputs response-only.

Out of scope:

- reading evaluation-only diagnostics;
- using latent process fields;
- changing the Goal 005 reconstruction rule;
- parameter sweeps or fitted models;
- real-data workflows;
- remote compute.

## Input Contract

The screen reads only:

- `reconstruction_config.json`
- `site_reconstruction.csv`
- `time_detection_summary.csv`
- `verification.json`

The screen must not read `evaluation_metrics.json`.

The primary input table is `site_reconstruction.csv`, with fields such as:

- `site_id`
- `cell_id`
- `row`
- `col`
- `region`
- `front_band`
- `survey_time_count`
- `detection_count`
- `observed_extirpated_by_end`
- `observed_extirpation_time`
- `reconstruction_status`

## Screen Summaries

The screen should compute:

- total sites;
- surveyed sites;
- sufficient-history sites;
- observed-extirpated sites;
- not-observed-extirpated sites;
- insufficient-history sites;
- no-survey sites;
- observed-extirpated fraction;
- sufficient-history fraction.

It should also emit group summaries by:

- `region`;
- `front_band`.

Each group summary should include:

- site count;
- observed-extirpated count and fraction;
- not-observed-extirpated count;
- insufficient-history count and fraction;
- no-survey count;
- observed-extirpation timing range where available;
- a compact screen note such as `informative`, `no_observed_extirpation`,
  `weak_observed_extirpation_signal`, or `low_information`.

Time summaries should carry forward response-only detection summaries and add a
cumulative detection fraction.

## Failure-Mode Diagnostics

The screen must make weak information explicit. At minimum, report:

- fraction not observed extirpated by the reconstruction rule;
- fraction with insufficient history;
- fraction with no surveys;
- count of low-information groups;
- a cautionary screen decision.

Low-information output is a valid scientific result, not an implementation
failure.

## Output Artifacts

The screen command writes:

- `artifacts/synth_small_response_screen/response_screen_config.json`
- `artifacts/synth_small_response_screen/screen_summary.json`
- `artifacts/synth_small_response_screen/group_screen_summary.csv`
- `artifacts/synth_small_response_screen/time_screen_summary.csv`
- `artifacts/synth_small_response_screen/verification.json`
- `artifacts/synth_small_response_screen/report.md`

## Interpretation

The expected default interpretation is `screen_with_caution`: enough observed
response signal exists for a later bounded synthetic-comparison layer, but the
screen must not be treated as fitted inference.

The screen is allowed to say `do_not_screen` when sufficient response-side
information is absent.

## Acceptance Criteria

- The spec exists and is implemented.
- The screen reads only the response-side reconstruction artifacts listed
  above.
- Screen artifacts are deterministic under deterministic inputs.
- Screen artifacts do not include evaluation-only payloads or latent process
  fields.
- Focused tests cover artifact emission, CLI execution, and response-only
  boundary checks.
- Generated artifacts remain unstaged.
