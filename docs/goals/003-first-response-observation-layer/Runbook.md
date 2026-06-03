# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/spatext
```

## Operating Rules

- Follow `/Users/bwbrook/papers/spatext/AGENTS.md`.
- Preserve all Goal 001 and Goal 002 work and pre-existing dirty files.
- Use `uv` for environment and command execution.
- Keep generated observation outputs under `artifacts/`.
- Keep analyst-facing observations response-only.
- Do not commit or push.

## Suggested Commands

Orient:

```bash
git status --short --branch
uv sync --all-groups
```

Refresh upstream artefacts:

```bash
uv run python scripts/build_synth_small_predator_truth.py
uv run python scripts/inspect_synth_small_predator_truth.py
uv run python scripts/run_synth_small_predator_truth_sensitivity.py
```

Build and inspect observations:

```bash
uv run python scripts/build_synth_small_observations.py
uv run python scripts/inspect_synth_small_observations.py
```

Quality lane:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

## Reporting Rules

Update:

- `spec/report_log.md`
- `Log.md`

The final response should include:

- changed files
- generated artefact paths
- exact validation results
- observation design summary
- recoverability smoke-test result and limits
- tracked and untracked Git status
- recommended next step after the three-goal pilot

## Decision Authority

The executor may autonomously:

- choose a compact first survey design suitable for `synth-small`
- define practical detection/effort defaults and a fixed seed
- add inspection and smoke-test metrics
- regenerate ignored artefacts
- add focused tests and docs

The executor must pause before:

- changing deterministic predator-truth defaults
- exposing predator truth as observed analyst data
- implementing ABC/POM/fitting machinery
- adding heavy dependencies
- running remote or large ensemble jobs
- committing or pushing
