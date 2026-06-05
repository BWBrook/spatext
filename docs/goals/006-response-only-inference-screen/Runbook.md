# Runbook

## Working Directory

```bash
cd /Users/bwbrook/.codex/worktrees/b4ee/spatext
```

## Operating Rules

- Work on `codex/spatext-goal006-response-screen`.
- Keep the screen response-only.
- Do not read `evaluation_metrics.json` inside the screen implementation.
- Do not start ABC, POM, fitting, broad sweeps, real-data analysis, or remote
  compute.
- Do not commit or push.
- Do not stage generated artifacts or caches.

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

Expected base: `origin/main` at `f9a0ed0` or newer.

## Build Screen Artifacts

If prerequisite artifacts are absent, rebuild the small local chain:

```bash
uv run python scripts/build_synth_small_observations.py
uv run python scripts/reconstruct_synth_small_extirpation.py
```

Then run:

```bash
uv run python scripts/run_synth_small_response_screen.py
```

Expected output directory:

```text
artifacts/synth_small_response_screen/
```

Expected files:

```text
response_screen_config.json
screen_summary.json
group_screen_summary.csv
time_screen_summary.csv
verification.json
report.md
```

## Boundary Check

The screen must not read or emit hidden-truth or evaluation-only payloads. It
should consume only:

```text
reconstruction_config.json
site_reconstruction.csv
time_detection_summary.csv
verification.json
```

## Focused Tests

```bash
uv run pytest tests/test_synth_small_response_screen.py --no-cov
uv run pytest tests/test_synth_small_extirpation_reconstruction.py --no-cov
```

## Quality Lane

```bash
git diff --check
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

## Final Review

```bash
git status --short --branch
git diff --stat
git ls-files -o --exclude-standard
```

Report generated artifact paths, but do not stage them.
