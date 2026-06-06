# Goal 007: Response-Screen Inspection

## Objective

Build a disk-first inspection layer for the Goal 006 `synth-small`
response-screen artifact bundle.

The goal is to make the screen output safer and easier for CoS and Barry to
review without rebuilding from live in-memory objects and without moving into
formal inference.

## Context

Goal 006 produced a cautious response-only screen with decision
`screen_with_caution`. The next bounded increment is a review layer that reloads
that emitted bundle from disk, checks the artifact contract, and writes compact
inspection outputs.

## Scientific Question

Can the emitted response-only screen bundle be reviewed from disk in a way that
makes weak-information and cautionary diagnostics explicit while preserving the
no-hidden-truth boundary?

## In Scope

- Add a disk-first inspection spec.
- Add a small inspection module under `src/spatext/synth/small/`.
- Add a CLI script that inspects an existing screen bundle.
- Emit inspection artifacts under the screen bundle's `inspection/` directory.
- Add focused tests for artifact contract, CLI execution, and hidden-truth /
  evaluation boundary protection.
- Update exports, README, and report log.

## Out Of Scope

- Rebuilding the response screen from live objects inside the inspector.
- Reading `evaluation_metrics.json`, hidden-truth artifacts, latent process
  fields, generated truth bundles, or real data.
- ABC, POM, MCMC, likelihood fitting, parameter sweeps, posterior claims, or
  driver-arrival inference.
- Changing Goal 006 screen logic unless an unavoidable integration bug appears.
- Commit or push unless CoS explicitly authorizes publication later.

## Required Inputs

The inspector reads only the existing screen artifacts:

- `response_screen_config.json`
- `screen_summary.json`
- `group_screen_summary.csv`
- `time_screen_summary.csv`
- `verification.json`
- `report.md`

## Required Outputs

The inspection command writes:

- `inspection/verification.json`
- `inspection/review_summary.json`
- `inspection/group_review_summary.csv`
- `inspection/report.md`

## Acceptance Criteria

- Inspector reloads emitted screen artifacts from disk.
- Missing required screen artifacts fail loudly.
- Inspection outputs omit hidden-truth and evaluation fields.
- Focused tests pass.
- Proportionate repository validation passes.
- Generated artifacts remain unstaged.
