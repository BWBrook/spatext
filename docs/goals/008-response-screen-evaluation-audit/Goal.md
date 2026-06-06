# Goal 008: Response-Screen Evaluation Audit

## Objective

Build a clearly labelled synthetic-only evaluation audit for the Goal 006/007
response-screen output.

The audit may use hidden-truth and evaluation artifacts only inside an
evaluation namespace after the response-only screen and inspection artifacts
already exist.

## Context

Goal 006 produced a cautious response-only screen with decision
`screen_with_caution`. Goal 007 added disk-first inspection of that screen. The
next bounded package is a synthetic evaluation audit that explains where the
screen succeeds or fails under known truth without changing the response-only
decision.

## Scientific Question

Using synthetic truth only after the response-only screen has been emitted, how
well do the screen calls identify true extirpation, and which groups explain
false-negative or weak-signal failure modes?

## In Scope

- Add an evaluation-only spec.
- Add a disk-first evaluation module under `src/spatext/synth/small/`.
- Add a CLI script that writes under
  `artifacts/synth_small_response_screen/evaluation/`.
- Use emitted screen artifacts plus clearly labelled Goal 005 evaluation/truth
  diagnostics.
- Add focused tests for evaluation namespace labelling, response-output
  immutability, failure-mode summaries, CLI execution, and missing-truth
  failure.
- Update exports, README, and report log.

## Out Of Scope

- Changing Goal 005 reconstruction, Goal 006 screen, or Goal 007 inspection
  decisions.
- Using hidden truth inside response-only decision outputs.
- Real-data analysis or interpretation.
- ABC, POM, MCMC, likelihood fitting, parameter sweeps, posterior claims, or
  driver-arrival inference.
- Remote compute.
- Commit or push unless SRF-A explicitly authorizes publication later.

## Required Inputs

The evaluation audit reads:

- emitted response-screen artifacts;
- emitted response-screen inspection artifacts where present;
- `site_reconstruction.csv`;
- `evaluation_metrics.json`;
- `evaluation_truth.csv`.

These inputs are permitted only because this goal is a synthetic evaluation
audit.

## Required Outputs

The evaluation command writes:

- `evaluation/evaluation_config.json`
- `evaluation/screen_evaluation_summary.json`
- `evaluation/group_evaluation_summary.csv`
- `evaluation/site_evaluation_audit.csv`
- `evaluation/verification.json`
- `evaluation/report.md`

## Acceptance Criteria

- Evaluation outputs are clearly labelled `evaluation_only`.
- Response-only screen and inspection artifacts are not modified.
- Hidden-truth fields do not leak into response-only output contracts.
- Failure-mode summaries identify weak-information/eastern groups.
- Focused and proportionate repository validation pass.
- Generated artifacts remain unstaged.
