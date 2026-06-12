# `synth-small` Compatibility Screen

## Purpose

This document specifies the first deterministic compatibility screen over the
`synth-small` summary-vector bridge.

Goal 009 created reusable `S(T_X, T_P)` summaries for the synthetic benchmark.
This layer asks a narrower follow-on question: whether a tiny, explicit
candidate set around the deterministic predator-truth default is compatible
with the already-emitted synthetic summary targets.

This screen is not ABC, POM, likelihood fitting, parameter recovery, posterior
inference, or real-data analysis. It is a synthetic-only ranking and audit
layer that can be reviewed before later inference machinery exists.

## Scope

In scope:

- read the Goal 009 summary-vector bundle from disk;
- evaluate both `ideal_true` and `realistic_observed` target modes;
- treat `realistic_observed` as the primary review mode;
- build candidate summaries using the same scalar and coverage semantics as
  the summary-vector bridge;
- rank a tiny deterministic candidate set within each target mode;
- emit explicit compatibility classes and invalid reasons;
- write a deterministic CSV, JSON, and Markdown artifact bundle.

Out of scope:

- ABC, POM, MCMC, likelihood fitting, posterior claims, or parameter recovery;
- broad parameter sweeps;
- changing deterministic predator-truth defaults;
- changing observation, reconstruction, response-screen, inspection, or
  evaluation artifacts;
- real-data analysis or interpretation;
- remote compute.

## Input Contract

The compatibility-screen command reads the Goal 009 target bundle:

```text
artifacts/synth_small_summary_vector/summary_vector_config.json
artifacts/synth_small_summary_vector/summary_components.csv
artifacts/synth_small_summary_vector/mode_summary.json
artifacts/synth_small_summary_vector/coverage_curve.csv
artifacts/synth_small_summary_vector/verification.json
```

The screen must fail loudly if required files are absent. It may reject a
target mode as `invalid` when required scalar components or coverage rows are
missing or explicitly undefined.

The command must not rewrite the summary-vector bundle or any upstream
observation, reconstruction, screen, inspection, or evaluation bundle.

## Target Modes

The screen evaluates both modes every run:

- `ideal_true`
- `realistic_observed`

`realistic_observed` is the primary target mode because it reflects the current
response-side synthetic target after observation and reconstruction. The
`ideal_true` mode is retained as a synthetic diagnostic. A correctly wired
default candidate should rank exact or near-exact against `ideal_true` because
both surfaces derive from the same deterministic default.

Both modes remain synthetic method-development targets. Neither mode implies
real-data recoverability.

## Candidate Set

The default candidate is explicitly labelled:

```text
label = default
predation_scale = 1.0
half_saturation = 6.0
ramp_duration = 8
```

The required compact candidate set is:

| Label | `predation_scale` | `half_saturation` | `ramp_duration` |
| --- | ---: | ---: | ---: |
| `weaker_predation` | `0.75` | `6.0` | `8` |
| `default` | `1.0` | `6.0` | `8` |
| `stronger_predation` | `1.25` | `6.0` | `8` |

The first implementation uses exactly these three candidates. It deliberately
does not run the existing 27-candidate predator-truth sensitivity grid.

## Summary Components

For each candidate, the screen builds the same summary-vector scalar
components and coverage curve over deterministic candidate truth:

- finite target count and fraction;
- lag mean and standard deviation;
- arrival-target squared correlation;
- front-plane gradient magnitude;
- coverage-curve target times at the Goal 009 breakpoints.

The same missing-value rule applies as in Goal 009: a defined value has an
empty `missing_reason`, while an undefined value has an empty value and an
explicit reason.

## Required Components and Gates

The initial required scalar components are:

- `finite_target_fraction`
- `lag_mean`
- `lag_std`
- `arrival_target_r2`
- `front_plane_gradient_magnitude`

The coverage curve is also required for the emitted breakpoints.

Rows are labelled `invalid` when required target or candidate values are
missing, non-finite, or fail the structural gates. Initial structural gates are
deliberately simple:

- finite target fraction must be finite and greater than zero;
- lag mean must be finite;
- lag standard deviation must be finite and greater than zero;
- arrival-target squared correlation must be finite;
- front-plane gradient magnitude must be finite;
- every required coverage breakpoint must have a finite target time.

Invalid rows keep their candidate metadata, receive no inferential rank claim,
and emit machine-readable invalid reasons.

## Weighted-Gap Loss

Valid rows are ranked using a transparent weighted-gap loss. For each required
scalar component:

```text
weighted_gap = weight * abs(candidate_value - target_value) / scale
```

The coverage term is the root-mean-square difference between candidate and
target coverage target times, divided by a documented coverage scale and then
weighted. The per-breakpoint target time, candidate time, absolute gap, and
squared gap must be emitted so the collapsed RMSE row can be reconstructed from
the artifact bundle.

The initial weights and scales are practical deterministic-screen settings,
not statistical likelihoods:

| Component | Weight | Scale |
| --- | ---: | ---: |
| `finite_target_fraction` | `2.0` | `0.25` |
| `lag_mean` | `1.0` | `10.0` |
| `lag_std` | `1.0` | `5.0` |
| `arrival_target_r2` | `1.0` | `0.5` |
| `front_plane_gradient_magnitude` | `1.0` | `1.0` |
| `coverage_curve_rmse` | `1.0` | `10.0` |

Ranks are deterministic within each mode: valid candidates sort by total loss,
then default candidates before non-default candidates on exact ties, then label.
Invalid candidates sort after valid candidates and retain `invalid` class.

## Compatibility Classes

Compatibility classes are screen labels only:

- `compatible`: total weighted loss is at most `0.25`;
- `borderline`: total weighted loss is greater than `0.25` and at most `1.0`;
- `incompatible`: total weighted loss is greater than `1.0`;
- `invalid`: required values or gates failed.

These classes are not posterior probabilities, confidence levels, or parameter
claims.

## Output Contract

The command writes under:

```text
artifacts/synth_small_compatibility_screen/
```

Required files:

- `compatibility_screen_config.json`
- `target_summary.json`
- `candidate_summaries.csv`
- `candidate_scores.csv`
- `coverage_score_breakdown.csv`
- `mode_rankings.csv`
- `verification.json`
- `report.md`

### `coverage_score_breakdown.csv`

One row per target mode, candidate, and coverage breakpoint. Required columns
include:

- `target_mode`
- `candidate_label`
- `is_default`
- `coverage_fraction`
- `target_time`
- `candidate_time`
- `absolute_gap`
- `squared_gap`
- `scale`
- `weight`
- `missing_reason`

For valid rows, the corresponding `coverage_curve_rmse` row in
`candidate_scores.csv` is:

```text
sqrt(mean(squared_gap)) / scale * weight
```

with `absolute_gap` in `candidate_scores.csv` equal to
`sqrt(mean(squared_gap))`.

JSON outputs must clearly state:

- `synthetic_only: true`;
- `primary_target_mode: realistic_observed`;
- all target modes evaluated;
- all candidates and candidate parameters;
- weights, scales, gates, required components, and missingness rules;
- `not_formal_inference: true`.

## Acceptance Criteria

This goal is complete when:

- this spec exists and is implemented;
- the CLI reads the Goal 009 bundle and writes the required bundle;
- both target modes are evaluated;
- the default candidate is present and explicitly labelled;
- the default candidate ranks exact or near-exact under `ideal_true`;
- `realistic_observed` is reported as the primary review target;
- invalid rows carry explicit reasons;
- coverage-curve RMSE contributions are auditable by breakpoint;
- focused compatibility-screen tests pass;
- proportionate repository validation passes;
- generated artifacts remain unstaged;
- no commit or push is performed.
