# `synth-small` Inspection and Verification

## Purpose

This document specifies the next work package after the successful baseline
implementation of `synth-small`.

The baseline builder already creates the synthetic truth object and emits a
clean artifact bundle. The next step is to build the first human-facing
inspection layer on top of those artifacts so that we can:

- verify that the emitted bundle is internally consistent,
- visualise the baseline synthetic landscape in a compact and readable form,
- inspect the exact parameterisation used to generate that landscape,
- establish the first reusable pattern for artifact review in `spatext`.

This module is still deliberately simple. It is not a dashboard, and it is not
yet about noisy observations, inference, or recovery. Its job is to make the
existing baseline artifacts auditable by both machines and humans.

## Executive decisions

### 1. Verify from disk, not from the live object

The inspection tooling should consume an already written `synth-small`
artifact directory rather than working directly from an in-memory
`SynthSmallBaselineResult`.

This matters because we want to validate the artifact contract itself, not just
the producing code path.

So the intended workflow is:

1. build the baseline artifact bundle,
2. load that bundle back from disk,
3. run consistency checks,
4. render a compact inspection report.

### 2. Keep the first report static and file-based

Do **not** introduce a notebook, web app, or dashboard framework for this
first inspection tool.

The first version should be:

- deterministic,
- scriptable,
- easy to diff,
- easy to archive,
- easy to run in CI later.

The preferred first output is a Markdown report with linked or embedded static
SVG assets and adjacent machine-readable verification outputs.

### 3. Start with the essentials

The first inspection tool must at minimum expose:

- the base map,
- the core parameter table,
- core diagnostics,
- a pass/fail verification summary.

For `synth-small`, the canonical base map is the **suitability surface** over
the island domain. Carrying capacity, equilibrium abundance, and occupancy
should also be shown, but suitability is the primary anchor map.

### 4. Treat visualisation as part of verification

The visual layer is not just cosmetic. It is part of the audit trail.

The inspection outputs should help us quickly catch:

- malformed spatial patterns,
- degenerate or overly flat landscapes,
- unexpected edge effects,
- bizarre carrying-capacity mappings,
- implausible equilibrium structure,
- accidental changes in configuration.

### 5. Do not duplicate the baseline generator

The new tooling should sit **on top of** the existing baseline artifact bundle.
It should not create a second, partially overlapping baseline-generation path.

If a visualization needs the suitability map, it should load the existing
artifact, not re-simulate the system independently.

## Scope

This work package covers the first inspection and verification tooling for the
existing `synth-small` baseline artifacts.

It includes:

- artifact loading,
- structural and numerical verification,
- parameter-table generation,
- compact report rendering,
- a simple command-line entrypoint,
- tests for valid and invalid bundles.

It does **not** include:

- predator introduction,
- observation models,
- TX estimation,
- posterior recovery,
- interactive dashboards,
- notebook-driven exploratory workflows,
- publication-grade figure styling.

## Input contract

The tool should assume an existing baseline artifact directory produced by the
current baseline builder. At present that bundle includes:

- `domain.json`
- `config.json`
- `diagnostics.json`
- `summary.json`
- `cells.csv`
- `edges.csv`
- `surfaces.npz`
- `suitability.svg`
- `carrying_capacity.svg`
- `equilibrium_abundance.svg`
- `equilibrium_occupancy.svg`

The inspection tooling should treat these files as the source material to be
validated and summarized.

## Output contract

Given a valid baseline artifact directory, the inspection tooling should create
an `inspection/` subdirectory containing at least:

- `verification.json`
- `parameters.csv`
- `surface_summary.csv`
- `report.md`

Optional additional outputs are allowed if they remain deterministic and
useful, but these four are the required minimum.

### `verification.json`

This should be the machine-readable pass/fail record for the artifact bundle.

It should contain:

- an overall `passed` field,
- a list of named checks,
- per-check status,
- a short message for each check,
- enough detail to diagnose a failure without opening Python.

### `parameters.csv`

This should be a flat, human-readable table of the generating configuration.

Recommended columns:

- `group`
- `name`
- `value`

The table should preserve logical grouping, for example:

- domain,
- suitability,
- demography,
- dispersal,
- convergence,
- occupancy.

Nested configuration fields should be flattened into stable names such as:

- `suitability.baseline`
- `suitability.primary_bump.center_row`
- `suitability.primary_bump.sigma`

### `surface_summary.csv`

This should provide a concise numeric summary of the main spatial surfaces.

Required rows:

- suitability,
- carrying_capacity,
- equilibrium_abundance,
- occupancy.

Recommended columns:

- `surface`
- `min`
- `max`
- `mean`
- `std`
- `sum`

For occupancy, the interpretation may be binary, but it should still be
reported consistently.

### `report.md`

This is the primary human-facing inspection artifact.

It should be a compact, readable report that can be opened directly in the
repo or rendered elsewhere later.

The report should include:

- title and short purpose statement,
- artifact-directory reference,
- verification status summary,
- domain summary,
- parameter table preview,
- diagnostics table,
- surface summary table,
- embedded or linked figures for:
  - suitability,
  - carrying capacity,
  - equilibrium abundance,
  - equilibrium occupancy.

The report should prefer relative links to the existing SVGs and generated CSV
files so the bundle stays portable.

## Verification requirements

The first verification pass should check the baseline artifact bundle for both
structural validity and scientific sanity.

### Required structural checks

At minimum:

- all required files exist,
- JSON files are readable,
- CSV files are readable,
- `surfaces.npz` loads successfully,
- shapes agree across metadata, CSVs, and surface arrays,
- the domain cell count matches the expected number of cell records,
- the edge list is non-empty and consistent with the domain graph.

### Required numerical checks

At minimum:

- suitability is finite and bounded in `[0, 1]`,
- carrying capacity is finite and strictly positive,
- equilibrium abundance is finite and non-negative,
- occupancy is binary-valued after load,
- diagnostics are present and indicate convergence,
- summary values are consistent with recomputation from the loaded surfaces.

### Required scientific-sanity checks

At minimum:

- suitability is not spatially constant,
- equilibrium abundance is not spatially constant,
- occupancy is neither all false nor all true,
- equilibrium abundance does not exceed carrying capacity by an unreasonable
  numerical margin,
- the bundle reflects the intended `25 x 25` square benchmark unless the
  caller explicitly points to a different valid future variant.

These are not deep scientific claims. They are first-line smoke alarms against
broken or degenerate outputs.

## Report design guidance

The first report should optimise for legibility and auditability, not visual
flair.

### General style

Use:

- plain Markdown,
- stable table formatting,
- concise prose,
- explicit file references,
- section order that mirrors how a modeller would inspect the system.

Avoid:

- long narrative text,
- decorative styling systems,
- hidden metadata,
- JavaScript or browser-dependent interactivity.

### Suggested report order

1. Overview
2. Verification status
3. Domain and graph summary
4. Parameter table
5. Diagnostics
6. Surface summary
7. Figures

This order makes it easy to answer:

1. Did the bundle load?
2. Did the checks pass?
3. What exact system was built?
4. What did it look like?

### Base map treatment

The first figure in the report should be the suitability map.

That figure is the baseline spatial cause in the synthetic system, so it
should appear before carrying capacity and abundance.

The other figures should follow in causal order:

1. suitability,
2. carrying capacity,
3. equilibrium abundance,
4. equilibrium occupancy.

## Recommended implementation structure

The new tooling should be implemented as a distinct inspection layer, not
bolted awkwardly into the baseline generator.

Suggested structure:

- a small artifact-loading layer,
- a verification layer,
- a report-rendering layer,
- a repository script entrypoint.

Possible module locations:

- `spatext.synth.small.inspect`
- `spatext.synth.small.io`

Exact filenames are up to `spat`, but the separation of concerns should remain
clear.

## Command-line interface

Provide a repository script for building the inspection outputs from an
existing artifact directory.

Suggested command shape:

```bash
uv run python scripts/inspect_synth_small_baseline.py \
  --artifact-dir artifacts/synth_small_baseline
```

Recommended behavior:

- default output directory is `<artifact-dir>/inspection`,
- fail loudly on missing or malformed required inputs,
- write all required outputs on success,
- print a short success summary including the output location and overall
  verification result.

## Testing requirements

This work package should come with tests that exercise both happy-path and
failure-path behavior.

At minimum, cover:

- successful load and inspection of a valid baseline bundle,
- creation of all required inspection outputs,
- deterministic parameter-table rendering,
- detection of missing required files,
- detection of shape mismatches,
- detection of out-of-bounds suitability values,
- detection of non-binary occupancy values,
- detection of inconsistent summary statistics.

The tests should continue to support the repo's strict quality posture:

- `ruff`
- `mypy`
- `pytest`
- `uv build`

## Acceptance criteria

This work package is complete when all of the following are true:

- a user can build the baseline artifact bundle and then run one inspection
  command against it,
- the command emits `inspection/verification.json`,
  `inspection/parameters.csv`, `inspection/surface_summary.csv`, and
  `inspection/report.md`,
- the report clearly shows the base map and the main downstream surfaces,
- the parameter table makes the generating configuration easy to inspect,
- the verification record gives a clear overall pass/fail status,
- corrupted or incomplete bundles fail clearly and are covered by tests,
- the implementation uses the existing artifact bundle rather than silently
  re-running the model.

## Why this comes next

This is the right next step because it strengthens the synthetic workflow at
exactly the right level.

We already know how to generate the baseline truth object. Now we need to make
that object inspectable, checkable, and easy to reason about before adding
predator dynamics or noisy observation layers.

That gives us a clean sequence:

1. build baseline truth,
2. inspect and verify baseline truth,
3. add perturbation and observation layers,
4. test recovery against known truth.
