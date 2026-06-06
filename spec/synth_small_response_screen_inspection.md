# `synth-small` Response-Screen Inspection

## Purpose

This document specifies a disk-first inspection layer for the Goal 006
response-only screen bundle.

The inspection layer exists to make screen outputs easier and safer to review.
It reloads emitted artifacts from disk, verifies their contract, and writes a
compact inspection bundle. It does not rebuild the screen from live objects and
does not perform formal inference.

## Scope

In scope:

- load an existing response-screen artifact directory;
- verify required files and table columns;
- verify that emitted screen artifacts remain response-only;
- summarize the source screen decision and review flags;
- write human-readable and machine-readable inspection outputs.

Out of scope:

- rebuilding the response screen inside the inspector;
- reading `evaluation_metrics.json` or hidden-truth artifacts;
- latent process, generated truth, or real-data inputs;
- ABC, POM, MCMC, likelihood fitting, parameter sweeps, posterior claims, or
  driver-arrival inference;
- changing the Goal 006 screen logic.

## Input Contract

The inspector reads only:

- `response_screen_config.json`
- `screen_summary.json`
- `group_screen_summary.csv`
- `time_screen_summary.csv`
- `verification.json`
- `report.md`

Any missing required file is a loud failure.

## Output Artifacts

The inspector writes under:

```text
artifacts/synth_small_response_screen/inspection/
```

Required outputs:

- `verification.json`
- `review_summary.json`
- `group_review_summary.csv`
- `report.md`

## Review Summary

The review summary should include:

- source screen decision;
- site count;
- observed-extirpated count;
- not-observed-extirpated count;
- insufficient-history count;
- observed-extirpated fraction;
- late-screen-bias warning;
- not-observed-extirpated fraction;
- low-information or weak-signal groups.

## Response-Only Boundary

Inspection outputs must not include hidden-truth or evaluation-only fields such
as:

- `driver_arrival`
- `predator_pressure`
- `true_extirpation`
- `extirpation_lag`
- `extirpated_by_end`
- `initial_abundance`
- `final_abundance`
- `evaluation_truth`
- `evaluation_metrics`

The inspector may ignore decoy or unrelated files in the artifact directory,
including any evaluation-looking payload that is not part of the screen contract.

## Interpretation

The inspector is a review aid. It may report a source decision such as
`screen_with_caution`, but this remains a response-side screen decision only.
Weak-information output is a valid scientific result.

## Acceptance Criteria

- The spec exists and is implemented.
- The inspector is disk-first and does not call the screen builder.
- Missing required screen artifacts fail loudly.
- Inspection outputs omit hidden-truth and evaluation fields.
- Focused tests cover artifact emission, CLI execution, missing-file behavior,
  and response-only boundary checks.
- Generated artifacts remain unstaged.
