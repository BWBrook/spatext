# Plan

## Milestone 1: Establish State And Prior Evidence

Acceptance criteria:

- dirty state from Goal 001 is understood and preserved
- Goal 001 report is present or regenerated
- current default metrics are extracted from the existing inspection report or
  recomputed from artefacts

Validation:

- `git status --short --branch`
- `uv sync --all-groups`
- default build and inspection commands pass

## Milestone 2: Specify Sensitivity Contract

Acceptance criteria:

- `spec/synth_small_predator_truth_sensitivity.md` defines the sweep inputs,
  metrics, readiness criteria, and output files
- the spec distinguishes deterministic readiness from biological finality
- candidate labels and default-candidate handling are stable

Validation:

- spec maps directly to planned CSV/JSON/Markdown outputs
- default candidate is explicitly represented

## Milestone 3: Implement Local Sweep

Acceptance criteria:

- sweep implementation can build and summarize candidate configurations
- command-line script writes the expected artefact bundle
- full sweep remains appropriate for local Mac Mini execution
- tests cover metric extraction, readiness classification, and report rendering

Validation:

- targeted tests pass
- `uv run python scripts/run_synth_small_predator_truth_sensitivity.py` passes

## Milestone 4: Produce Decision Package

Acceptance criteria:

- `sweep_results.csv` contains one row per candidate
- `candidate_rankings.csv` orders candidates by documented criteria
- `readiness.json` records the default candidate, best candidate, and criteria
- `decision_memo.md` gives a concise scientific decision surface for Barry

Validation:

- output files exist and are non-empty
- default candidate classification is present
- memo states whether to keep or revisit the current default before observation

## Milestone 5: Final Quality Lane And Handoff

Acceptance criteria:

- full quality lane passes
- README/report log/action-goal log are updated
- final response includes exact tracked/untracked Git status

Validation:

- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `git status --short --branch`
