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
  `codex/spatext-goal013-observation-support-counterfactual-screen`.
- Keep this goal synthetic-only, evaluation-only, counterfactual-only, and
  method-development only.
- Do not change default observation-design settings.
- Do not change emitted default observation or reconstruction artifacts outside
  the counterfactual output namespace.
- Do not change the production reconstruction rule.
- Do not change response-screen, summary-vector, compatibility-screen,
  mismatch-audit, or false-negative-audit scoring logic.
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

Expected base: `origin/main` at `91b5df7` or newer.

Create the branch:

```bash
git switch -c codex/spatext-goal013-observation-support-counterfactual-screen origin/main
```

If that fails, stop and report the exact error. Do not force, delete, reset,
rebase, or repair the branch state by improvisation.

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
uv run python scripts/audit_synth_small_false_negatives.py
```

The counterfactual screen should then read:

```text
artifacts/synth_small_observations/
artifacts/synth_small_extirpation_reconstruction/
artifacts/synth_small_response_screen/evaluation/
artifacts/synth_small_response_screen/evaluation/false_negative_audit/
artifacts/synth_small_summary_vector/
artifacts/synth_small_compatibility_screen/
```

## Counterfactual Command

Add and run:

```bash
uv run python scripts/run_synth_small_observation_support_counterfactual.py
```

Expected output directory:

```text
artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/
```

Expected files:

```text
counterfactual_config.json
scenario_definitions.csv
site_counterfactual_resolution.csv
scenario_reconstruction_summary.csv
scenario_summary_vectors.csv
scenario_compatibility_scores.csv
scenario_rankings.csv
recommendation.json
verification.json
report.md
```

## Focused Tests

```bash
uv run pytest tests/test_synth_small_observation_support_counterfactual_screen.py --no-cov
uv run pytest tests/test_synth_small_false_negative_mechanism_audit.py --no-cov
uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov
uv run pytest tests/test_synth_small_summary_vector.py --no-cov
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
