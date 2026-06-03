# Plan

## Milestone 1: Establish Authority

Acceptance criteria:

- repo state is known
- prior dirty files are noted and not reverted
- authoritative specs and existing inspection patterns have been read
- target artefact location is known

Validation:

- `git status --short --branch`
- `uv sync --all-groups`
- confirm predator-truth artefact path exists or can be regenerated

## Milestone 2: Specify Inspection Contract

Acceptance criteria:

- `spec/synth_small_predator_truth_inspection.md` defines inputs, outputs,
  invariants, and review questions
- the spec distinguishes hard verification failures from scientific warnings
- output filenames and schemas are stable enough for later recovery workflows

Validation:

- spec references the existing predator-truth terminology consistently
- planned outputs map to the files the script will write

## Milestone 3: Implement And Test Inspection

Acceptance criteria:

- inspection code reads artefacts from disk rather than in-memory generator
  state
- command-line script is repeatable from a fresh repo environment
- tests cover successful inspection and at least missing/corrupted/inconsistent
  input cases

Validation:

- targeted tests for the inspection layer pass
- full `uv run pytest` passes

## Milestone 4: Produce Review Bundle

Acceptance criteria:

- inspection outputs are written under
  `artifacts/synth_small_predator_truth/inspection/`
- `report.md` summarizes parameters, grid/surface state, trajectories,
  extirpation timing, lags, and warnings
- machine-readable verification output records pass/fail/warning state

Validation:

- `uv run python scripts/build_synth_small_predator_truth.py`
- `uv run python scripts/inspect_synth_small_predator_truth.py`
- output files exist and are non-empty

## Milestone 5: Final Quality Lane And Handoff

Acceptance criteria:

- full quality lane passes
- `spec/report_log.md` and this goal's `Log.md` are updated
- final report gives supervisor enough evidence for a post-run review

Validation:

- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `git status --short --branch`
