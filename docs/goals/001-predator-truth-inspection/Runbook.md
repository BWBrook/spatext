# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/spatext
```

## Operating Rules

- Follow `/Users/bwbrook/papers/spatext/AGENTS.md`.
- Use `uv` for environment and command execution.
- Keep generated outputs under `artifacts/` unless an existing spec says
  otherwise.
- Do not revert pre-existing dirty changes.
- Do not commit or push.
- Keep the inspection layer disk-first so it can validate artefacts produced by
  earlier or external runs.

## Suggested Commands

Orient:

```bash
git status --short --branch
uv sync --all-groups
```

Build target artefact:

```bash
uv run python scripts/build_synth_small_predator_truth.py
```

Run inspection:

```bash
uv run python scripts/inspect_synth_small_predator_truth.py
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
- scientific warnings or interpretation limits
- whether the worktree is dirty or clean
- recommended next goal

## Decision Authority

The executor may autonomously:

- add inspection specs, code, scripts, and tests
- regenerate ignored synthetic-small artefacts
- update user-facing docs for the new inspection command
- define practical machine-readable summary schemas when the existing specs do
  not yet specify them

The executor must pause before:

- changing the deterministic predator-truth generating model
- adding noisy observations
- implementing parameter recovery
- launching remote compute
- committing or pushing
