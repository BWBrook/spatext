# Runbook

## Working Directory

```bash
cd /Users/bwbrook/.codex/worktrees/b4ee/spatext
```

## Operating Rules

- Work on `codex/spatext-goal008-response-screen-evaluation-audit`.
- Keep evaluation outputs under `artifacts/synth_small_response_screen/evaluation/`.
- Hidden truth is allowed only inside this synthetic evaluation namespace.
- Do not change response-only reconstruction, screen, or inspection decisions.
- Do not run real data, formal inference, parameter sweeps, or remote compute.
- Do not commit or push.
- Do not stage generated artifacts, `dist/`, caches, or `.venv/`.

## Initial Checks

```bash
pwd
git rev-parse --show-toplevel
git rev-parse --git-dir
git rev-parse --git-common-dir
git branch --show-current
git rev-parse --short HEAD
git status --short --branch
git fetch --prune origin
git rev-parse --short origin/main
```

Expected base: `origin/main` at `db0517a` or newer.

## Prerequisite Artifacts

If local ignored artifacts are absent, rebuild the small chain:

```bash
uv run python scripts/build_synth_small_observations.py
uv run python scripts/reconstruct_synth_small_extirpation.py
uv run python scripts/run_synth_small_response_screen.py
uv run python scripts/inspect_synth_small_response_screen.py
```

## Evaluation Command

```bash
uv run python scripts/evaluate_synth_small_response_screen.py
```

Expected output directory:

```text
artifacts/synth_small_response_screen/evaluation/
```

Expected files:

```text
evaluation_config.json
screen_evaluation_summary.json
group_evaluation_summary.csv
site_evaluation_audit.csv
verification.json
report.md
```

## Focused Tests

```bash
uv run pytest tests/test_synth_small_response_screen_evaluation.py --no-cov
uv run pytest tests/test_synth_small_response_screen.py --no-cov
uv run pytest tests/test_synth_small_response_screen_inspection.py --no-cov
```

## Quality Lane

```bash
git diff --check
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

## Final Review

```bash
git status --short --branch
git diff --stat
git ls-files -o --exclude-standard
git status --ignored --short artifacts dist
```
