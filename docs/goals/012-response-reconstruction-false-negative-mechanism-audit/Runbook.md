# Runbook

## Working Directory

```bash
cd /Users/bwbrook/papers/spatext
```

## Operating Rules

- Work only in `/Users/bwbrook/papers/spatext`.
- Do not read `/Users/bwbrook/chief_of_staff`.
- Do not read `/Users/bwbrook/work/goal_composer`.
- Work on local branch
  `codex/spatext-goal012-false-negative-mechanism-audit`.
- Keep this goal synthetic-only, evaluation-only, audit-only, and
  method-development only.
- Do not change reconstruction rules or observation settings.
- Do not change response-screen, compatibility-screen, or mismatch-audit
  logic.
- Do not start ABC, POM, fitting, posterior claims, parameter recovery, broad
  parameter sweeps, real-data analysis, or remote compute.
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

Expected base: `origin/main` at `7e4e6f7` or newer.

Create the branch:

```bash
git switch -c codex/spatext-goal012-false-negative-mechanism-audit origin/main
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
uv run python scripts/audit_synth_small_compatibility_mismatch.py
```

The false-negative audit should then read:

```text
artifacts/synth_small_response_screen/evaluation/
artifacts/synth_small_extirpation_reconstruction/
artifacts/synth_small_observations/
artifacts/synth_small_compatibility_screen/mismatch_audit/
```

## False-Negative Audit Command

Add and run:

```bash
uv run python scripts/audit_synth_small_false_negatives.py
```

Expected output directory:

```text
artifacts/synth_small_response_screen/evaluation/false_negative_audit/
```

Expected files:

```text
false_negative_audit_config.json
false_negative_site_audit.csv
mechanism_summary.csv
group_mechanism_summary.csv
observation_timing_summary.csv
recommendation.json
verification.json
report.md
```

## Focused Tests

```bash
uv run pytest tests/test_synth_small_false_negative_mechanism_audit.py --no-cov
uv run pytest tests/test_synth_small_compatibility_mismatch_audit.py --no-cov
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
