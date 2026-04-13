# Tooling Bootstrap Directive for `spat`

## Purpose

This document tells `spat` how to bootstrap the initial development tooling for
`spatext`. It is a tooling and workflow contract, not a scientific-methods
document. The aim is to give the new repository a clean, durable, low-friction
Python foundation that supports:

- modular scientific software design,
- strong tests and validation from the start,
- transparent reproducibility,
- maintainable growth into case studies and later papers,
- minimal tooling sprawl.

## Executive decision

`spatext` should start with the following baseline:

- language: CPython `3.14`
- project/environment manager: `uv`
- build backend: `uv_build`
- package layout: `src/` layout
- metadata authority: one `pyproject.toml`
- lockfile authority: one committed `uv.lock`
- initial repo shape: one package, not a workspace
- initial docs authority: Markdown files in `spec/`
- initial workflow policy: no `pixi`

The important constraint is this:

> In phase 0, `spatext` should have exactly one Python environment authority and
> one packaging authority. That authority is `uv` plus `pyproject.toml`.

## Decision rationale

This choice is meant to optimize for long-term clarity, not novelty.

- Python is the right implementation language for a modular scientific software
  project that will support simulation, inference, geospatial preprocessing,
  testing, reporting, and future case-study work.
- Python `3.14` is now stable. `spatext` should target the `3.14.x` line and
  pin an exact patch release in local development.
- `uv` gives us fast environment creation, Python installation, a
  cross-platform lockfile, dependency groups, and a clean `pyproject.toml`
  workflow without splitting the project across multiple package-management
  systems.
- `uv_build` is a good fit because the initial package should be pure Python,
  and the build backend defaults align well with a clean `src/`-layout package.
- `src/` layout prevents accidental imports from the repo root and forces the
  package to behave like an installed package during tests.

## Exact Python version policy

Use the Python `3.14` series for the package contract, but pin a concrete patch
release for local development.

- In `pyproject.toml`, set `requires-python = ">=3.14,<3.15"`.
- In `.python-version`, pin the exact interpreter used for local development.
- As of `2026-04-13`, the expected development interpreter is `3.14.4`.
- If `3.14.4` is unavailable for some reason, install and pin the latest stable
  `3.14.x` release available at bootstrap time and record that change plainly in
  the commit or implementation note.

This gives us semantic stability for the package and exact reproducibility for
the local development environment.

## Role for `pixi`

`pixi` does have a potential role, but not in the initial bootstrap.

### Decision

Do not add `pixi.toml`, do not create a pixi environment, and do not make
`pixi` part of the phase-0 developer workflow.

### Why not now

- `uv` already covers the core Python package-management needs well.
- Adding `pixi` immediately would create two overlapping environment concepts
  before we have any evidence that the second one is needed.
- The initial work is package scaffolding, testing, typing, linting, and basic
  scientific-kernel development. That does not justify a dual-tooling setup.
- A clean repo should begin with the minimum viable tool surface.

### When `pixi` may become justified later

Revisit `pixi` only if one or more of these become true:

- the project develops hard binary/runtime dependencies that are awkward to
  install reproducibly with wheels alone,
- the repo needs a single reproducible environment spanning Python plus R,
  Julia, Quarto, or system CLI tools,
- geospatial dependencies create repeated onboarding pain around GDAL, GEOS,
  PROJ, or related compiled libraries,
- cross-platform environment parity becomes a persistent problem in contributor
  setup or CI.

### Rule if `pixi` is added later

If `pixi` is introduced in a later phase:

- `pyproject.toml` must remain the authoritative source for Python package
  metadata,
- `uv` remains the authoritative Python dependency resolver and lockfile owner
  unless explicitly superseded by a separate approved spec,
- `pixi` should be treated as an environment/system-package layer, not as a
  second competing project-definition layer,
- the addition must be justified in its own spec document.

## Bootstrap architecture

### Package shape

Start as a single importable package, not a monorepo and not a workspace.

Recommended initial structure:

```text
spatext/
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── LICENSE
├── README.md
├── pyproject.toml
├── uv.lock
├── spec/
│   ├── problem_statement.md
│   └── tooling_bootstrap.md
├── src/
│   └── spatext/
│       ├── __init__.py
│       └── py.typed
├── tests/
│   └── test_smoke.py
└── scripts/
```

Notes:

- `scripts/` is for small repository utilities, never for core library logic.
- `notebooks/` should not exist in phase 0.
- `data/` should not be introduced until there is a separate data policy.
- `docs/` may be added later, but `spec/` remains the design authority during
  early buildout.

### Workspace policy

Do not use a `uv` workspace initially.

Only move to a workspace if the repo later splits into genuinely distinct
packages, for example:

- a core `spatext` library,
- a separate case-study package,
- a dedicated CLI or report package that must version independently.

Until that point, one package is simpler and better.

## Packaging directives

### Build backend

Use `uv_build` as the initial build backend.

Recommended `build-system` block:

```toml
[build-system]
requires = ["uv_build>=0.11.6,<0.12"]
build-backend = "uv_build"
```

This follows the `uv` recommendation to include an upper bound on `uv_build`.

### Project metadata

Use a standard `pyproject.toml` with explicit metadata from day one.

Minimum project metadata should include:

- name
- version
- description
- readme
- requires-python
- license
- authors
- urls

Use a static version initially, for example `0.1.0`. Do not introduce dynamic
version tooling on day one.

### Source layout

Use a `src/` layout and keep the import package under `src/spatext/`.

This is not optional. The package should be tested as installed code, not as
repo-root-imported code.

## Dependency strategy

### Guiding rule

Keep runtime dependencies minimal at bootstrap.

Do not preload half the scientific Python ecosystem before the first real module
contracts exist. The bootstrap should set up the package and the quality system,
not prematurely freeze the eventual modelling stack.

### Dependency categories

Use these categories consistently:

- `project.dependencies`: only true runtime dependencies of the shipped package
- `[dependency-groups]`: local development and test tooling
- `project.optional-dependencies`: future published extras such as `geo`,
  `bayes`, `viz`, or `notebooks` if those become part of the package interface

### Initial dependency groups

Create the following groups immediately:

- `lint`
- `test`
- `type`
- `dev`

Recommended pattern:

```toml
[dependency-groups]
lint = ["ruff"]
test = [
  "pytest",
  "pytest-cov",
  "hypothesis",
]
type = ["mypy"]
dev = [
  { include-group = "lint" },
  { include-group = "test" },
  { include-group = "type" },
  "pre-commit",
]

[tool.uv]
default-groups = ["dev"]
```

Rules:

- `dev` should aggregate the other local groups.
- `uv.lock` must be committed.
- CI should use `uv sync --all-groups --frozen`.
- Local development may use `uv sync` with default groups.

### What not to do

Do not add any of the following in phase 0:

- `requirements.txt`
- `requirements-dev.txt`
- `environment.yml`
- `pixi.toml`
- `poetry.lock`
- `Pipfile`
- `setup.py`
- `setup.cfg`

`pyproject.toml` and `uv.lock` are sufficient.

## Quality-tooling directives

### Test runner: `pytest`

`pytest` should be the primary test runner from day one.

Configuration expectations:

- use `--import-mode=importlib`
- test the installed package under `src/`
- keep tests in `tests/`
- prefer simple unit tests around pure functions and contracts
- add property-based tests for invariants, not just example-by-example tests

Recommended `pytest` block:

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
  "--import-mode=importlib",
  "--strict-config",
  "--strict-markers",
  "--cov=spatext",
  "--cov-branch",
  "--cov-report=term-missing",
]
```

### Coverage: `coverage.py` via `pytest-cov`

Use branch coverage, not line coverage alone.

Rules:

- coverage should target `spatext`
- branch coverage must be enabled
- the package should start with a hard quality floor

Recommended starting policy:

- fail under `90%` total coverage for the core package in phase 0
- if a lower threshold becomes temporarily necessary, it must be justified in a
  short note or issue and then raised again quickly

### Property-based testing: `hypothesis`

`spatext` is a scientific modelling package. That makes invariant testing more
important than in many ordinary application repos.

Use `hypothesis` early for:

- monotonicity or order constraints,
- boundary conditions,
- idempotence or conservation properties,
- valid domain restrictions,
- agreement between alternative implementations of the same kernel.

This is especially important for simulation kernels, summary-statistic
functions, and extirpation-time estimators.

### Linting and formatting: `ruff`

Use `ruff` as both the linter and formatter.

Rules:

- formatting is done with `ruff format`
- linting is done with `ruff check`
- use an explicit rule selection, not `ALL`
- allow safe auto-fixes, avoid blanket unsafe fixes

Recommended starting configuration:

```toml
[tool.ruff]
target-version = "py314"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "RUF"]
```

The intent is to catch real issues and keep the codebase tidy without turning
the linter into a style-tax engine.

### Type checking: `mypy`

Use `mypy` in strict mode from the beginning.

This repo is being built from scratch. That is exactly when strict typing is
most affordable and most valuable.

Rules:

- `mypy` should run in strict mode
- avoid global `ignore_missing_imports = true`
- if a library lacks usable typing, use targeted local workarounds rather than a
  repo-wide type-checking escape hatch
- keep public interfaces and scientific kernels typed, even if some peripheral
  scripts remain lighter

Recommended starting configuration:

```toml
[tool.mypy]
python_version = "3.14"
strict = true
packages = ["spatext"]
```

### Git hooks: `pre-commit`

Use `pre-commit` from phase 0.

At minimum, the hook stack should run:

- `ruff format`
- `ruff check --fix`
- basic file hygiene hooks such as trailing-whitespace, end-of-file-fixer, and
  check-yaml where relevant

The hook layer should be fast and predictable. It exists to reduce noise and
prevent obvious errors from reaching CI.

## Documentation and notebook policy

### Documentation

During early buildout:

- `spec/` is the authoritative design/documentation layer
- project docs should remain Markdown-first
- do not build a full docs site yet unless there is enough real API surface to
  justify it

When a docs site becomes worthwhile, prefer:

- `mkdocs-material`
- `mkdocstrings[python]`

But this is phase 1 or later, not phase 0.

### Notebooks

Do not make notebooks part of the initial package workflow.

If notebooks are introduced later:

- they belong in an optional environment group,
- they are for exploration, exposition, or demos,
- they are never the canonical home of core modelling logic.

## CI policy for the initial repo

The initial CI lane should be intentionally lean and deterministic.

When CI is added, it should:

- install the pinned Python `3.14.x` interpreter,
- run `uv sync --all-groups --frozen`,
- run formatting check,
- run lint,
- run type checking,
- run tests with coverage,
- run `uv build`.

Do not put heavy scientific runs, case-study pipelines, notebooks, or large
data-dependent jobs in the default CI lane.

Those can become separate scheduled or manually triggered workflows later.

## Immediate bootstrap tasks for `spat`

The next implementation task should do the following, in roughly this order:

1. Check that `uv` is available.
2. Check whether the requested Python `3.14.4` interpreter is available via
   `uv`; install it if needed.
3. Pin that interpreter in `.python-version`.
4. Initialize `spatext` as a package repo using `pyproject.toml`, `src/`
   layout, and `uv_build`.
5. Add the local dependency groups for linting, testing, typing, and
   pre-commit.
6. Generate and commit `uv.lock`.
7. Create the minimal package skeleton under `src/spatext/`.
8. Create a smoke test in `tests/`.
9. Configure `ruff`, `pytest`, `coverage`, and `mypy` in `pyproject.toml`.
10. Add `.pre-commit-config.yaml` and install hooks locally.
11. Verify the canonical bootstrap commands below.

## Canonical commands

The repo should treat these as the primary local commands:

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run pre-commit run --all-files
```

CI should use:

```bash
uv sync --all-groups --frozen
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

## Acceptance criteria for the next task

The next task is done only when a fresh clone can perform the following without
manual environment improvisation:

- install or select the pinned Python `3.14.x` interpreter,
- create the project environment with `uv`,
- sync all dependency groups,
- run formatting, linting, typing, tests, and build successfully,
- reproduce that state from the committed `uv.lock`.

## Final rule

Bias toward clarity and reversibility.

If `spat` must choose between:

- adding another tool now, or
- keeping the bootstrap simpler and postponing that decision,

the default choice should be to keep the bootstrap simpler.
