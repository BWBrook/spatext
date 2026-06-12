# Goal 009: Synth-Small Summary-Vector Bridge

## Objective

Build a disk-first `synth-small` summary-vector bridge that computes reusable
`S(T_X, T_P)` summaries for the current synthetic benchmark.

This goal should turn the current response-only reconstruction, response screen,
and synthetic-only audit into the summary-vector layer needed before any formal
compatibility screen, ABC, POM, likelihood, posterior, parameter-sweep, or
real-data work is attempted.

## Context

Goals 005-008 built a coherent response-side ladder:

- Goal 005 reconstructed a conservative response-only `T_X^obs` proxy.
- Goal 006 emitted a cautious response-only screen over that reconstruction.
- Goal 007 made the screen reviewable from disk.
- Goal 008 used hidden truth only inside an evaluation namespace to audit screen
  failure modes.

The theory document says the next inference stack is:

```text
summaries -> compatibility screen -> ABC refinement
```

The repository does not yet have the reusable `summaries` layer. Goal 009 fills
that gap without fitting models or drawing inference.

## Scientific Question

Can the project compute a small, auditable summary vector for both ideal and
realistic synthetic targets, so that later screening and ABC work can compare
like with like and quantify information loss from observation/reconstruction?

## Modes

Implement two clearly labelled synthetic modes:

- `ideal_true`: uses synthetic `true_extirpation` as the target `T_X`.
- `realistic_observed`: uses reconstructed `observed_extirpation_time` as the
  target `T_X`.

Both modes may use synthetic `driver_arrival` as `T_P`, but this must be labelled
as synthetic method-development input. This goal is not a response-only decision
layer and not a real-data workflow.

## In Scope

- Add `spec/synth_small_summary_vector.md`.
- Add a focused source module under `src/spatext/synth/small/`, probably
  `summary_vector.py`.
- Add a CLI script, probably `scripts/build_synth_small_summary_vector.py`.
- Load existing emitted artifacts from disk.
- Join synthetic target, observed reconstruction, and driver-arrival fields by
  stable site/cell identifiers.
- Compute a modest first summary vector with explicit missing-value semantics.
- Emit deterministic summary-vector artifacts under
  `artifacts/synth_small_summary_vector/`.
- Add focused tests for summary computation, mode labelling, missing metric
  handling, CLI execution, and synthetic-only boundary protection.
- Update exports, README, `spec/report_log.md`, and this goal log.

## Out Of Scope

- ABC, POM, MCMC, likelihood fitting, posterior claims, parameter sweeps, or
  compatibility screening over parameter draws.
- Real-data analysis or interpretation.
- Changing Goal 005 reconstruction logic.
- Changing Goal 006 response-screen logic.
- Changing Goal 007 inspection logic.
- Changing Goal 008 evaluation logic.
- Reading Chief of Staff or Goal Composer.
- Remote compute.
- Commit or push.

## Required Inputs

The summary-vector command may read these emitted synthetic artifacts:

- `artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv`
- `artifacts/synth_small_extirpation_reconstruction/verification.json`
- `artifacts/synth_small_observations/evaluation_truth.csv`

It may also read configuration or verification files needed to label provenance.
The new summary-vector command itself must not rewrite any Goal 005-008
artifacts. A prerequisite rebuild of ignored local artifacts is allowed only when
those artifacts are absent or stale.

## Required Summary Components

Compute at least:

- finite target count and fraction over finite driver-arrival sites;
- lag count, mean, median, standard deviation, minimum, and maximum for
  finite `T_X - T_P` pairs;
- arrival-target squared correlation where defined;
- simple front-plane row/column slopes and gradient magnitude where enough
  finite target values exist;
- coverage-curve rows over deterministic breakpoints.

When a component is undefined, emit a machine-readable missing reason instead of
silently dropping it or inventing a value.

## Required Outputs

Write a deterministic artifact bundle under:

```text
artifacts/synth_small_summary_vector/
```

Required files:

- `summary_vector_config.json`
- `summary_components.csv`
- `mode_summary.json`
- `coverage_curve.csv`
- `verification.json`
- `report.md`

The JSON outputs must clearly label:

- `synthetic_only: true`
- mode names;
- which inputs came from observed reconstruction versus synthetic truth;
- that this is not formal inference.

## Acceptance Criteria

- The spec exists and is implemented.
- The CLI rebuilds or consumes the current local synthetic artifacts and writes
  the required summary-vector bundle.
- Both `ideal_true` and `realistic_observed` modes are present.
- Hidden truth remains confined to this clearly labelled synthetic
  method-development layer.
- The summary-vector command does not rewrite response-only reconstruction,
  screen, inspection, or evaluation artifacts.
- Focused tests pass.
- Proportionate full repository validation passes.
- Generated artifacts remain unstaged.
- No commit or push is performed.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.
