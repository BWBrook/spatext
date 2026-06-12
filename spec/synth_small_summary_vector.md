# `synth-small` Summary-Vector Bridge

## Purpose

This document specifies the first reusable summary-vector layer for the
`synth-small` synthetic benchmark.

The layer computes compact `S(T_X, T_P)` summaries from emitted disk artifacts.
It is a bridge between the existing reconstruction/screen/evaluation ladder and
later compatibility-screen or ABC work. It is not itself formal inference.

## Scope

In scope:

- disk-first loading of existing `synth-small` artifacts;
- a reusable summary vector for synthetic method development;
- clearly labelled `ideal_true` and `realistic_observed` modes;
- explicit missing-value semantics for undefined metrics;
- deterministic CSV, JSON, and Markdown artifacts;
- synthetic-only provenance labels.

Out of scope:

- ABC, POM, MCMC, likelihood fitting, posterior claims, or parameter sweeps;
- real-data analysis or interpretation;
- changing reconstruction, response-screen, inspection, or evaluation logic;
- rewriting any Goal 005-008 artifacts;
- remote compute.

## Input Contract

The summary-vector command reads existing emitted artifacts from disk.

Required inputs:

- `artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv`
- `artifacts/synth_small_extirpation_reconstruction/verification.json`
- `artifacts/synth_small_observations/evaluation_truth.csv`

The reconstruction table supplies the response-side observed target and stable
site/cell identifiers. The evaluation-truth table supplies synthetic
method-development truth, including driver arrival and true extirpation.

The command may read configuration or verification files needed for provenance,
but it must not rewrite the reconstruction, screen, inspection, or evaluation
bundles.

## Modes

The command must emit both modes every run.

### `ideal_true`

`ideal_true` uses synthetic `true_extirpation` as `T_X` and synthetic
`driver_arrival` as `T_P`.

This mode represents ideal synthetic access to the true extirpation surface and
is only valid inside method-development diagnostics.

### `realistic_observed`

`realistic_observed` uses response-side
`observed_extirpation_time` as `T_X` and synthetic `driver_arrival` as `T_P`.

This mode represents the current realistic synthetic target after observation
and reconstruction. The use of `driver_arrival` remains synthetic
method-development input, not a response-only real-data claim.

## Summary Components

For each mode, compute at least:

- finite target count and fraction over finite driver-arrival sites;
- lag count, mean, median, standard deviation, minimum, and maximum for finite
  `T_X - T_P` pairs;
- arrival-target squared correlation where defined;
- simple front-plane row and column slopes for `T_X ~ row + col`;
- front-plane gradient magnitude from those slopes;
- deterministic coverage-curve rows over fixed breakpoints.

The default coverage breakpoints are:

```text
0.0, 0.25, 0.5, 0.75, 1.0
```

Each coverage row reports the time threshold at the requested cumulative
coverage fraction among finite target values.

## Missing Metric Semantics

Undefined metrics must be emitted explicitly rather than dropped.

Each scalar summary component has:

- `mode`
- `component`
- `value`
- `missing_reason`

If a component is defined, `value` is finite and `missing_reason` is empty. If
it is undefined, `value` is empty and `missing_reason` is one of:

- `no_finite_target`
- `no_finite_driver_arrival`
- `no_finite_lag_pairs`
- `insufficient_finite_pairs`
- `constant_arrival_or_target`
- `singular_front_plane`

Coverage rows use the same rule with an empty threshold value and an explicit
missing reason when no finite target values exist.

## Output Contract

The command writes a deterministic artifact bundle under:

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

JSON outputs must clearly state:

- `synthetic_only: true`;
- the emitted mode names;
- which input fields came from observed reconstruction and synthetic truth;
- that the bundle is not formal inference.

## Boundary Rules

Hidden truth may appear only inside this synthetic summary-vector bundle and
only under explicit synthetic-only labelling.

The command must not:

- mutate Goal 005 reconstruction artifacts;
- mutate Goal 006 response-screen artifacts;
- mutate Goal 007 inspection artifacts;
- mutate Goal 008 evaluation artifacts;
- write hidden-truth fields into response-only artifact locations;
- produce compatibility-screen, ABC, POM, likelihood, posterior, parameter
  sweep, or real-data outputs.

## Acceptance Criteria

This goal is complete when:

- this spec exists and is implemented;
- both `ideal_true` and `realistic_observed` modes are emitted;
- summary components and coverage curves use explicit missing reasons;
- the CLI writes the required bundle;
- focused tests pass;
- proportionate repository validation passes;
- generated artifacts remain unstaged;
- no commit or push is performed.
