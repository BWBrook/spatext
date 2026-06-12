# Goal 010: Synth-Small Compatibility Screen

## Objective

Build the first synthetic-only `synth-small` compatibility screen over the
Goal 009 summary-vector layer.

This goal should compare a tiny deterministic set of candidate synthetic
driver-response mechanisms against the existing `S(T_X, T_P)` targets and emit
a ranked, auditable compatibility bundle. It is a screen and ranking device,
not ABC, POM, likelihood fitting, posterior inference, parameter recovery, or
real-data analysis.

## Context

Goal 009 added a disk-first summary-vector bridge with two target modes:

- `ideal_true`: synthetic true extirpation target.
- `realistic_observed`: reconstructed response-side extirpation target.

The theory document names the next stack as:

```text
summaries -> compatibility screen -> ABC refinement
```

Goal 010 fills the `compatibility screen` layer while deliberately staying
short of ABC or formal inference. The key scientific pressure test is whether
the summary vector can rank simple candidate mechanisms in a transparent way,
and whether the observed reconstruction target behaves differently from the
ideal synthetic target.

## Scientific Question

Can the current `synth-small` summary vector support a deterministic,
synthetic-only compatibility screen that ranks a small candidate set while
making gates, weighted losses, missingness, and non-inference boundaries
explicit?

## Target Modes

The screen must compare candidate synthetic summaries against both Goal 009
target modes:

- `ideal_true` for a sanity check against the synthetic truth target.
- `realistic_observed` as the primary review target for information-loss
  behaviour after observation and reconstruction.

The output must clearly label `realistic_observed` as the primary mode, but it
must not hide the `ideal_true` comparison.

## Candidate Set

Use a tiny deterministic candidate set derived from the existing
`SensitivityCandidate` / predator-truth configuration machinery. The default
set should include at least:

- `weaker_predation`: `predation_scale = 0.75`, `half_saturation = 6.0`,
  `ramp_duration = 8`
- `default`: `predation_scale = 1.0`, `half_saturation = 6.0`,
  `ramp_duration = 8`, labelled as the default candidate
- `stronger_predation`: `predation_scale = 1.25`, `half_saturation = 6.0`,
  `ramp_duration = 8`

The implementation may include up to four additional nearby deterministic
candidates if this improves ranking diagnostics without turning the goal into a
broad sweep. Do not run the full 27-candidate sensitivity grid unless the code
already makes it essentially free and the output remains compact.

Each candidate summary should use the same `S(T_X, T_P)` component semantics as
Goal 009. Candidate `T_X` is the candidate synthetic true extirpation surface.
Candidate `T_P` is that candidate's synthetic driver-arrival surface. Candidate
summaries are method-development inputs and must be labelled synthetic-only.

## In Scope

- Add `spec/synth_small_compatibility_screen.md`.
- Add a focused source module under `src/spatext/synth/small/`, probably
  `compatibility_screen.py`.
- Add a CLI script, probably
  `scripts/run_synth_small_compatibility_screen.py`.
- Load the Goal 009 summary-vector target bundle from disk.
- Generate or compute a tiny deterministic candidate summary table.
- Compare candidates against both `ideal_true` and `realistic_observed` target
  summaries.
- Implement explicit admissibility gates and a documented weighted-gap loss.
- Emit deterministic compatibility-screen artifacts under
  `artifacts/synth_small_compatibility_screen/`.
- Add focused tests for scoring, ranking, missingness, invalid-candidate
  handling, CLI execution, and synthetic-only boundary protection.
- Update exports, README, `AGENTS.md` if the authoritative spec list changes,
  `spec/report_log.md`, and this goal log.

## Out Of Scope

- ABC, POM, MCMC, likelihood fitting, posterior claims, parameter recovery, or
  real-data analysis.
- Broad parameter sweeps or remote compute.
- Changing Goal 005 reconstruction logic.
- Changing Goal 006 response-screen logic.
- Changing Goal 007 inspection logic.
- Changing Goal 008 evaluation logic.
- Changing Goal 009 summary-vector target semantics except to fix a narrow
  integration bug that blocks this goal. If that happens, pause and report.
- Reading Chief of Staff or Goal Composer.
- Commit or push.

## Required Inputs

The compatibility-screen command should read the Goal 009 target bundle:

- `artifacts/synth_small_summary_vector/summary_vector_config.json`
- `artifacts/synth_small_summary_vector/summary_components.csv`
- `artifacts/synth_small_summary_vector/mode_summary.json`
- `artifacts/synth_small_summary_vector/coverage_curve.csv`
- `artifacts/synth_small_summary_vector/verification.json`

If prerequisite ignored artifacts are absent or stale, the runbook may rebuild
the small local chain. The compatibility-screen command itself must not rewrite
Goal 005-009 artifacts except when explicitly rebuilding prerequisites before
the screen run.

## Required Screen Components

Implement a transparent screen with at least:

- a target summary parser for Goal 009 scalar components and coverage rows;
- candidate summary computation using the same component names and missingness
  semantics as the summary-vector layer;
- required-component checks for finite target and candidate values;
- admissibility gates for basic plausibility, including finite target fraction,
  finite lag mean, finite lag variation, and finite arrival-target coupling;
- weighted-gap loss over:
  - `finite_target_fraction`
  - `lag_mean`
  - `lag_std`
  - `arrival_target_r2`
  - `front_plane_gradient_magnitude`
  - coverage-curve target-time RMSE at matching breakpoints
- deterministic ranks within each target mode;
- a coarse compatibility class such as `compatible`, `borderline`,
  `incompatible`, or `invalid`.

Weights, scale factors, gate thresholds, required components, optional
components, and missingness penalties must be emitted in a machine-readable
config artifact. The exact initial values can be pragmatic, but they must be
documented and not tuned silently to make the default candidate win.

## Required Outputs

Write a deterministic artifact bundle under:

```text
artifacts/synth_small_compatibility_screen/
```

Required files:

- `compatibility_screen_config.json`
- `target_summary.json`
- `candidate_summaries.csv`
- `candidate_scores.csv`
- `mode_rankings.csv`
- `verification.json`
- `report.md`

The JSON outputs must clearly label:

- `synthetic_only: true`
- `primary_target_mode: realistic_observed`
- both target modes evaluated;
- candidate parameter values;
- that the screen is not formal inference.

## Acceptance Criteria

- The spec exists and is implemented.
- The CLI consumes the Goal 009 summary-vector target bundle and writes the
  required compatibility-screen bundle.
- Both `ideal_true` and `realistic_observed` target modes are evaluated.
- The default candidate is present and explicitly labelled.
- In `ideal_true` mode, the default candidate should rank as an exact or
  near-exact match to the default synthetic truth unless there is a documented
  reason it cannot.
- `realistic_observed` mode is treated as the primary review target and reports
  the observation/reconstruction information-loss effect without overclaiming.
- Required-component missingness or gate failure produces an `invalid` class
  with explicit reasons rather than silent omission.
- Focused tests pass.
- Proportionate full repository validation passes.
- Generated artifacts remain unstaged.
- No commit or push is performed.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.
