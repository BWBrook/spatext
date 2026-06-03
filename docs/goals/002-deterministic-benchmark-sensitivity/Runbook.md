# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/spatext
```

## Operating Rules

- Follow `/Users/bwbrook/papers/spatext/AGENTS.md`.
- Preserve all Goal 001 work and pre-existing dirty files.
- Use `uv` for environment and command execution.
- Keep generated sensitivity outputs under `artifacts/`.
- Do not commit or push.
- Do not change predator-truth defaults unless Barry explicitly approves.

## Suggested Commands

Orient:

```bash
git status --short --branch
uv sync --all-groups
```

Refresh default truth and inspection artefacts:

```bash
uv run python scripts/build_synth_small_predator_truth.py
uv run python scripts/inspect_synth_small_predator_truth.py
```

Run sensitivity package:

```bash
uv run python scripts/run_synth_small_predator_truth_sensitivity.py
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
- default readiness classification
- best candidate, if one is clearly identified
- scientific warnings or interpretation limits
- tracked and untracked Git status
- recommended Goal 003

## Decision Authority

The executor may autonomously:

- choose a small local parameter grid near the current default
- implement practical readiness scoring/classification
- add tests and docs for the sensitivity workflow
- regenerate ignored artefacts

The executor must pause before:

- changing default generating parameters
- adding observation-noise machinery
- implementing fitting/recovery
- expanding to large remote sweeps
- committing or pushing
