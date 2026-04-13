# spatext

`spatext` is a Python repository for response-only spatiotemporal extinction
inference.

The project is being built to support scientific workflows where:

- a putative ecological driver spreads through space and time,
- the biological response is local extinction or extirpation,
- direct observations of the driver are sparse, noisy, or missing, and
- the response is observed only through incomplete and biased records.

The initial scientific target is to determine what can be learned about a
spatially spreading extinction driver from response-only evidence, while making
recoverability limits and failure regimes explicit rather than hiding them.

## Scientific framing

The main scientific statement for the repository lives in
[`spec/problem_statement.md`](spec/problem_statement.md).

The mathematical modelling contract currently lives in
[`spec/theory.md`](spec/theory.md).

Two central latent quantities anchor the modelling vision:

- `TP(x)`: arrival time of the hypothesized driver at location `x`
- `TX(x)`: extirpation time at location `x`, inferred from observations

The first substantive case study is the mink-water-vole system in Great Britain
and Ireland, but the repository is being structured as a general framework
rather than a one-off case-study codebase.

## Current project stage

The repository is in early buildout, with the first synthetic baseline and
inspection workflow now in place. Current priorities are:

- keeping scientific specification separate from implementation,
- building a clean and testable Python package foundation,
- validating methods against synthetic truth before real-data interpretation,
- maintaining an auditable record of assumptions, gates, and outcomes.

## Repository map

```text
spatext/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── uv.lock
├── spec/
├── src/
├── tests/
└── scripts/
```

Key locations:

- [`AGENTS.md`](AGENTS.md): repo-local operating instructions
- [`spec/problem_statement.md`](spec/problem_statement.md): scientific mission
- [`spec/theory.md`](spec/theory.md): mathematical model and inference theory
- [`spec/synth_small_baseline.md`](spec/synth_small_baseline.md): Module 1
  baseline specification
- [`spec/synth_small_inspection.md`](spec/synth_small_inspection.md): Module 1
  inspection specification
- [`spec/tooling_bootstrap.md`](spec/tooling_bootstrap.md): tooling contract
- [`spec/report_log.md`](spec/report_log.md): running operational log
- [`src/spatext/`](src/spatext): installable package source
- [`tests/`](tests): test suite

## Tooling baseline

The bootstrap environment currently uses:

- CPython `3.14.4`
- [`uv`](https://github.com/astral-sh/uv) for environment and dependency
  management
- `uv_build` as the build backend
- `ruff` for formatting and linting
- `mypy` for strict type checking
- `pytest` and `pytest-cov` for tests and coverage
- `pre-commit` for fast local hygiene checks

The authoritative Python packaging and dependency definitions live in
[`pyproject.toml`](pyproject.toml) and [`uv.lock`](uv.lock).

## Core local commands

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run pre-commit run --all-files
```

## Implemented baseline module

Module 1 is now implemented as a small synthetic prey-only baseline benchmark.
It constructs:

- a `25 x 25` square-lattice island domain,
- a deterministic suitability surface,
- a suitability-driven carrying-capacity surface,
- a prey-only equilibrium abundance surface,
- convergence diagnostics and occupancy summaries,
- an auditable artifact bundle for inspection.

The main implementation entrypoints are:

- [`src/spatext/spatial.py`](src/spatext/spatial.py): graph-based spatial domain
  primitives
- [`src/spatext/synth/small/baseline.py`](src/spatext/synth/small/baseline.py):
  `synth-small` baseline configuration, simulation, and artifact export
- [`scripts/build_synth_small_baseline.py`](scripts/build_synth_small_baseline.py):
  command-line utility for emitting a baseline bundle

To generate the baseline artifact bundle locally:

```bash
uv run python scripts/build_synth_small_baseline.py \
  --output-dir artifacts/synth_small_baseline
```

That command writes JSON, CSV, NPZ, and SVG artifacts for downstream
inspection and later synthetic modules.

## Implemented inspection module

Module 1 now also includes a disk-first inspection layer for auditing an
existing baseline artifact bundle. It:

- reloads the baseline bundle from disk,
- verifies structural, numerical, and scientific-sanity checks,
- flattens the generating configuration into a readable parameter table,
- summarizes the core spatial surfaces,
- renders a compact Markdown inspection report that links back to the emitted
  SVG artifacts.

The main inspection entrypoints are:

- [`src/spatext/synth/small/inspect.py`](src/spatext/synth/small/inspect.py):
  artifact loading, verification, summary-table generation, and Markdown
  report rendering
- [`scripts/inspect_synth_small_baseline.py`](scripts/inspect_synth_small_baseline.py):
  command-line utility for inspecting an existing baseline bundle

To inspect an existing baseline artifact bundle locally:

```bash
uv run python scripts/inspect_synth_small_baseline.py \
  --artifact-dir artifacts/synth_small_baseline
```

That command writes an `inspection/` subdirectory containing:

- `verification.json`
- `parameters.csv`
- `surface_summary.csv`
- `report.md`

## Operating stance

The repo is intentionally being built around a few early constraints:

- one Python environment authority,
- one packaging authority,
- synthetic-first validation,
- modular design,
- auditable scientific interpretation.

That means the repository should resist avoidable tooling sprawl and should not
inherit legacy exploratory structure just because it existed elsewhere.

## Status notes

- The initial package and quality-tooling scaffold is in place.
- Module 1 `synth-small` baseline generation is implemented and verified.
- Module 1 `synth-small` inspection and verification is implemented and
  verified.
- The report log in [`spec/report_log.md`](spec/report_log.md) tracks completed
  interactions and implementation milestones.
- Commits and remote pushes are performed only when explicitly requested.
