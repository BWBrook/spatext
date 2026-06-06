# `synth-small` Response-Screen Evaluation Audit

## Purpose

This document specifies a synthetic-only evaluation audit for the Goal 006
response-screen output and Goal 007 inspection output.

The audit may use hidden truth only after response-only artifacts already
exist, and only under an explicitly labelled evaluation namespace. It is a
method-development diagnostic, not a response-only decision layer and not
formal inference.

## Scope

In scope:

- load emitted response-screen artifacts from disk;
- load emitted reconstruction evaluation diagnostics and observation evaluation
  truth;
- join screen calls to synthetic truth by site;
- compute site-level and group-level audit diagnostics;
- identify weak-information and false-negative failure modes;
- write evaluation-only artifacts under the screen bundle.

Out of scope:

- changing reconstruction, screen, or inspection decisions;
- using hidden truth inside response-only outputs;
- real-data analysis;
- ABC, POM, MCMC, likelihood fitting, parameter sweeps, posterior claims, or
  driver-arrival inference;
- remote compute.

## Input Contract

The evaluation audit reads:

- `artifacts/synth_small_response_screen/` screen artifacts;
- `artifacts/synth_small_response_screen/inspection/` inspection artifacts
  where present;
- `artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv`;
- `artifacts/synth_small_extirpation_reconstruction/evaluation_metrics.json`;
- `artifacts/synth_small_observations/evaluation_truth.csv`.

The final three inputs are evaluation/truth inputs and must not be used by the
response-only screen or inspection layers.

## Output Artifacts

The evaluation command writes:

- `artifacts/synth_small_response_screen/evaluation/evaluation_config.json`
- `artifacts/synth_small_response_screen/evaluation/screen_evaluation_summary.json`
- `artifacts/synth_small_response_screen/evaluation/group_evaluation_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/site_evaluation_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/verification.json`
- `artifacts/synth_small_response_screen/evaluation/report.md`

All JSON outputs must include `evaluation_only: true`.

## Audit Summaries

The audit should compute:

- confusion matrix for screen calls against synthetic truth;
- sensitivity, specificity, and precision;
- false-negative count and false-positive count;
- group-level metrics by `region` and `front_band`;
- weak-signal and false-negative groups;
- a concise report explaining that the audit does not change the screen
  decision.

## Boundary Checks

The audit must preserve these boundaries:

- response-only screen artifacts are not rewritten;
- response-only inspection artifacts are not rewritten;
- hidden truth remains confined to evaluation outputs;
- evaluation outputs are clearly labelled;
- failure modes are reported as method-development diagnostics.

## Interpretation

The expected default result is a useful but limited screen: high precision and
specificity, with substantial false negatives and weak eastern signal. Those
weaknesses are scientific diagnostics, not implementation failures.

## Acceptance Criteria

- The spec exists and is implemented.
- The evaluation is disk-first.
- Missing evaluation-truth input fails loudly.
- Evaluation outputs are labelled `evaluation_only`.
- Response-only artifacts remain unchanged after evaluation.
- Focused tests cover artifact writing, CLI execution, boundary protection,
  and failure-mode summaries.
- Generated artifacts remain unstaged.
