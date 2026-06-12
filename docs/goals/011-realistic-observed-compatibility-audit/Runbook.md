# Runbook

## Working Directory

```bash
cd /Users/bwbrook/papers/spatext
```

## Operating Rules

- Work only in `/Users/bwbrook/papers/spatext`.
- Do not read `/Users/bwbrook/chief_of_staff`.
- Do not read `/Users/bwbrook/work/goal_composer`.
- Work on local branch `codex/spatext-goal011-compatibility-mismatch-audit`.
- Keep this goal synthetic-only, audit-only, and method-development only.
- Do not start ABC, POM, fitting, posterior claims, parameter recovery, broad
  parameter sweeps, real-data analysis, or remote compute.
- Do not modify Goals 005-010 logic unless a narrow integration bug blocks
  this goal; if that happens, pause and report.
- Do not tune Goal 010 scoring thresholds or weights.
- Do not commit or push.
- Do not stage generated artifacts, `dist/`, caches, or `.venv/`.
- Update this goal `Log.md` as work proceeds.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.

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

Expected base: `origin/main` at `0ee8f59` or newer.

Create the branch:

```bash
git switch -c codex/spatext-goal011-compatibility-mismatch-audit origin/main
```

If that fails, stop and report the exact error. Do not force, delete, reset, or
repair the branch state by improvisation.

## Prerequisite Artifacts

If local ignored artifacts are absent or stale, rebuild the small chain:

```bash
uv run python scripts/build_synth_small_predator_truth.py
uv run python scripts/build_synth_small_observations.py
uv run python scripts/reconstruct_synth_small_extirpation.py
uv run python scripts/run_synth_small_response_screen.py
uv run python scripts/inspect_synth_small_response_screen.py
uv run python scripts/evaluate_synth_small_response_screen.py
uv run python scripts/build_synth_small_summary_vector.py
uv run python scripts/run_synth_small_compatibility_screen.py
```

The mismatch audit should then read:

```text
artifacts/synth_small_summary_vector/
artifacts/synth_small_compatibility_screen/
artifacts/synth_small_response_screen/evaluation/
```

## Mismatch-Audit Command

Add and run:

```bash
uv run python scripts/audit_synth_small_compatibility_mismatch.py
```

Expected output directory:

```text
artifacts/synth_small_compatibility_screen/mismatch_audit/
```

Expected files:

```text
mismatch_audit_config.json
target_delta_summary.csv
score_contribution_summary.csv
coverage_gap_summary.csv
evaluation_bridge_summary.json
recommendation.json
verification.json
report.md
```

## Focused Tests

```bash
uv run pytest tests/test_synth_small_compatibility_mismatch_audit.py --no-cov
uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov
uv run pytest tests/test_synth_small_response_screen_evaluation.py --no-cov
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

Report generated artifact paths, but do not stage them.
