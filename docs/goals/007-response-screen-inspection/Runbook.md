# Runbook

## Working Directory

```bash
cd /Users/bwbrook/.codex/worktrees/b4ee/spatext
```

## Operating Rules

- Work on `codex/spatext-goal007-response-screen-inspection`.
- Inspect existing response-screen artifacts from disk.
- Do not rebuild the screen inside the inspector.
- Do not read `evaluation_metrics.json`, hidden-truth artifacts, generated truth
  bundles, or real data.
- Do not run ABC, POM, likelihood fitting, parameter sweeps, or driver-arrival
  inference.
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

Expected base: `origin/main` at `96e38bc` or newer.

## Prerequisite Screen Bundle

If local ignored artifacts are absent, rebuild the small chain:

```bash
uv run python scripts/build_synth_small_observations.py
uv run python scripts/reconstruct_synth_small_extirpation.py
uv run python scripts/run_synth_small_response_screen.py
```

## Inspection Command

```bash
uv run python scripts/inspect_synth_small_response_screen.py
```

Expected output directory:

```text
artifacts/synth_small_response_screen/inspection/
```

Expected files:

```text
verification.json
review_summary.json
group_review_summary.csv
report.md
```

## Focused Tests

```bash
uv run pytest tests/test_synth_small_response_screen_inspection.py --no-cov
uv run pytest tests/test_synth_small_response_screen.py --no-cov
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
