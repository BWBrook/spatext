# Plan

## Milestone 1: Establish State And Upstream Artefacts

Acceptance criteria:

- dirty state from Goals 001 and 002 is understood and preserved
- upstream truth, inspection, and sensitivity artefacts are present or
  regenerated
- current recommendation to use the default truth benchmark is confirmed from
  `readiness.json` or the decision memo

Validation:

- `git status --short --branch`
- `uv sync --all-groups`
- upstream build, inspection, and sensitivity commands pass

## Milestone 2: Specify Observation Contract

Acceptance criteria:

- `spec/synth_small_observations.md` defines observation design, detection,
  effort, files, schemas, and analyst-facing versus truth/evaluation columns
- the spec explicitly says predator arrival and pressure are not observed
  analyst data
- recoverability smoke-test outputs and interpretation limits are specified

Validation:

- planned files map to implementation outputs
- seed and reproducibility contract are clear

## Milestone 3: Implement Observation Generation

Acceptance criteria:

- observation generator reads or builds the default predator-truth benchmark
- outputs are deterministic under the default seed
- main observation table contains only response-side observations plus allowed
  site/time/effort fields
- truth reference/evaluation files are clearly separated

Validation:

- build script writes required files
- targeted tests for reproducibility and schema pass

## Milestone 4: Implement Inspection And Smoke Test

Acceptance criteria:

- inspection loads an existing observation bundle from disk
- verification fails clearly for missing or malformed required files
- smoke metrics are finite and documented
- report gives Barry a compact review surface for the observation layer

Validation:

- inspect script writes verification, summary, smoke JSON, and report
- targeted tests for inspection and smoke metrics pass

## Milestone 5: Final Quality Lane And Handoff

Acceptance criteria:

- full quality lane passes
- README/AGENTS/report log/action-goal log are updated
- final response includes exact tracked/untracked Git status and a post-pilot
  integration recommendation

Validation:

- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `git status --short --branch`
