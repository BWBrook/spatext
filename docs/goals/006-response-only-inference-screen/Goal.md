# Goal 006: Response-Only Inference Screen

## Objective

Build a tiny, cautious response-only screen over the existing `synth-small`
`T_X^obs` reconstruction artifacts.

The goal is to summarize the reconstructed response surface and its
low-information failure modes before any ABC, POM, likelihood, or real-data
work is considered.

## Context

Goal 005 produced a conservative observed-extirpation proxy from response-only
observation artifacts. That baseline is useful enough for a next step, but its
false-negative and spatial-bias limits are part of the scientific result.

Goal 006 should therefore add a small screen package, not a formal inference
engine.

## Scientific Question

Using only `T_X^obs` reconstruction outputs, can the project produce a compact
screening summary that identifies where the response signal is strong enough to
support later synthetic comparison and where it remains weak or absent?

## In Scope

- Add a response-only screen specification.
- Add a small source module under `src/spatext/synth/small/`.
- Add a CLI script that consumes Goal 005 reconstruction artifacts from disk.
- Emit a small deterministic screen artifact bundle under `artifacts/`.
- Add focused tests for screen outputs and response-only boundary protection.
- Update public docs and the report log.

## Out Of Scope

- ABC, POM, MCMC, likelihood fitting, posterior inference, or parameter sweeps.
- Driver-arrival, predator-pressure, or process-parameter inference.
- Real-data analysis.
- Changing the Goal 005 reconstruction rule.
- Using hidden-truth diagnostics as screen inputs.
- Emitting hidden-truth or evaluation payloads from the screen bundle.
- Remote compute.
- Commit or push unless explicitly authorized later.

## Required Inputs

The screen may read only these Goal 005 reconstruction artifacts:

- `reconstruction_config.json`
- `site_reconstruction.csv`
- `time_detection_summary.csv`
- `verification.json`

It must not read `evaluation_metrics.json`.

## Required Outputs

The screen command writes:

- `response_screen_config.json`
- `screen_summary.json`
- `group_screen_summary.csv`
- `time_screen_summary.csv`
- `verification.json`
- `report.md`

## Acceptance Criteria

- Screen outputs are deterministic for deterministic reconstruction inputs.
- Screen artifacts omit hidden-truth and evaluation fields.
- Summary includes site-level coverage, observed-extirpation fractions, group
  failure notes, and cautionary screen decision.
- Focused tests pass.
- Proportionate repository validation passes.
- No generated artifacts are staged.
