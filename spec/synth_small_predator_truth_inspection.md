# `synth-small` Predator-Truth Inspection and Review

## Purpose

This document specifies the disk-first inspection layer for the
`synth-small` deterministic predator-response truth bundle.

The predator-truth generator now creates a complete latent driver-response
object: baseline prey state, driver arrival, predator pressure, prey response,
latent true extirpation, and lag. Before adding noisy observations or
parameter recovery, the project needs a compact review bundle that can verify
the emitted artifacts from disk and summarize whether the current deterministic
truth object is scientifically coherent.

This inspection layer is not a model-fitting tool. It is an audit and review
tool for the generated truth bundle.

## Executive Decisions

### 1. Inspect from disk

The inspection tool must consume an existing
`artifacts/synth_small_predator_truth` directory. It must not silently rebuild
the truth object in memory and then inspect that live object.

This preserves the established project pattern:

1. build a deterministic artifact bundle,
2. reload that bundle from disk,
3. verify structural and numerical contracts,
4. render machine-readable summaries and a human-facing report.

### 2. Separate hard failures from scientific warnings

The inspection output should distinguish two kinds of review signal:

- hard verification checks, where failure means the artifact contract is broken
  or internally inconsistent,
- scientific warnings, where the bundle is structurally valid but a pattern
  deserves review before downstream observation or recovery work.

For example, a lag surface that disagrees with `T_X^true(x) - T_P(x)` is a
hard failure. A weak or unexpected vulnerability pattern is a scientific
warning that Barry should review, but it need not mean the files are malformed.

### 3. Keep the first report static and portable

The first predator-truth inspection output should be deterministic, file-based,
and easy to archive. It should not introduce notebooks, dashboards, web apps,
or new plotting dependencies.

The primary human-facing artifact is a Markdown report with relative links to
the existing SVG figures and adjacent CSV/JSON summaries.

## Input Contract

The input artifact directory is expected to contain:

- `domain.json`
- `baseline_config.json`
- `predator_config.json`
- `diagnostics.json`
- `summary.json`
- `cells.csv`
- `surfaces.npz`
- `trajectories.npz`
- `suitability.svg`
- `initial_abundance.svg`
- `driver_arrival.svg`
- `true_extirpation.svg`
- `extirpation_lag.svg`
- `final_abundance.svg`

The required surface arrays are:

- `suitability`
- `carrying_capacity`
- `initial_abundance`
- `driver_arrival`
- `extirpation_threshold`
- `true_extirpation`
- `extirpation_lag`
- `final_abundance`

The required trajectory arrays are:

- `prey_abundance`
- `predator_pressure`

## Output Contract

Given a valid input directory, the inspection tool writes an `inspection/`
subdirectory containing:

- `verification.json`
- `parameters.csv`
- `surface_summary.csv`
- `trajectory_summary.csv`
- `extirpation_summary.csv`
- `report.md`

### `verification.json`

The verification record is the machine-readable status output. It should
include:

- input and output paths,
- overall pass/fail status,
- named hard verification checks,
- per-check messages and details,
- scientific warnings.

### `parameters.csv`

The parameter table flattens the domain metadata, baseline configuration,
predator configuration, and core diagnostics into stable rows:

- `group`
- `name`
- `value`

### `surface_summary.csv`

The surface table summarizes grid-shaped arrays with missing-value awareness:

- `surface`
- `finite_count`
- `missing_count`
- `min`
- `max`
- `mean`
- `std`
- `sum`

### `trajectory_summary.csv`

The trajectory table summarizes time-by-grid arrays:

- `trajectory`
- `time_steps`
- `rows`
- `cols`
- `finite_count`
- `missing_count`
- `min`
- `max`
- `mean`
- `std`
- `initial_mean`
- `final_mean`

### `extirpation_summary.csv`

The extirpation summary records review metrics that are central to deciding
whether the deterministic truth object is a useful benchmark:

- extirpated and surviving counts/fractions,
- finite `T_X^true(x)` range,
- finite lag range,
- mean and standard deviation of finite lags,
- driver-arrival range,
- extirpation rates in low- and high-initial-abundance quartiles,
- west- and east-band extirpated counts.

### `report.md`

The Markdown report should include:

- verification pass/fail status,
- scientific warnings,
- domain and parameter summaries,
- surface and trajectory summaries,
- extirpation and vulnerability summaries,
- relative links to existing SVG figures:
  - suitability,
  - initial abundance,
  - driver arrival,
  - true extirpation,
  - extirpation lag,
  - final abundance.

## Hard Verification Checks

The first implementation should verify at least:

- all required input files are present,
- required NPZ arrays are present and loadable,
- all grid surfaces match the domain shape,
- trajectory arrays have shape `(simulation_horizon + 1, rows, cols)`,
- `cells.csv` has one row per cell,
- `driver_arrival` values are finite and align to the baseline grid,
- western-boundary driver arrival equals the configured introduction time,
- predator pressure is finite and lies within configured bounds,
- prey abundance trajectories are finite and non-negative,
- the first prey-abundance frame matches `initial_abundance`,
- the final prey-abundance frame matches `final_abundance`,
- finite `T_X^true(x)` values have finite lags,
- non-extirpated cells have missing lags,
- finite lags equal `T_X^true(x) - T_P(x)`,
- no extirpation precedes predator arrival,
- summary statistics match recomputation from the loaded arrays,
- `cells.csv` is consistent with the loaded arrays,
- diagnostics are consistent with loaded trajectory and surface state.

## Scientific Warnings

The inspection should report, but not necessarily fail on:

- near-total or near-zero extirpation fractions,
- use of numerical clipping,
- weak or reversed low-density vulnerability patterns,
- very low lag variation,
- non-Type-II or non-absolute-threshold defaults if those appear in a future
  bundle.

## Acceptance Criteria

This inspection work package is complete when:

- the spec exists and documents the input/output contract,
- the implementation reads an existing predator-truth artifact directory from
  disk,
- the CLI command writes all required inspection outputs,
- tests cover valid, missing, corrupted, and inconsistent bundles,
- generated inspection outputs exist under
  `artifacts/synth_small_predator_truth/inspection/`,
- the repo quality lane passes.

## Next Use

After this inspection layer exists, the next scientific conversation can focus
on the generated predator-truth report:

- whether the west-to-east arrival and extirpation pattern is qualitatively
  appropriate,
- whether the vulnerability pattern is acceptable for the intended
  generalist-predator benchmark,
- whether deterministic parameters need gentle tuning,
- and whether the project is ready to add the first synthetic observation
  layer.
