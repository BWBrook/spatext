# Runbook

## Start

```bash
cd /Users/bwbrook/papers/spatext
pwd
git status --short --branch
git fetch --prune origin
git switch -c codex/spatext-goal015-target-time-error-anatomy-audit origin/main
git status --short --branch
```

If branch creation fails because the branch already exists, stop and report the
exact status. Do not force, delete, reset, rebase, or repair by improvisation.

## Required Reading

```bash
sed -n '1,220p' AGENTS.md
sed -n '1,220p' README.md
sed -n '1,220p' spec/problem_statement.md
sed -n '1,260p' spec/theory.md
rg '^## Interaction|^# Interaction|^### Interaction' spec/report_log.md
```

Read the relevant specs and goal packets before implementing:

```bash
for path in \
  spec/synth_small_observations.md \
  spec/synth_small_extirpation_reconstruction.md \
  spec/synth_small_response_screen_evaluation.md \
  spec/synth_small_false_negative_mechanism_audit.md \
  spec/synth_small_observation_support_counterfactual_screen.md \
  spec/synth_small_target_timing_residual_decomposition.md \
  docs/goals/012-response-reconstruction-false-negative-mechanism-audit/Goal.md \
  docs/goals/013-post-extirpation-observation-support-counterfactual-screen/Goal.md \
  docs/goals/014-synth-small-target-timing-residual-decomposition/Goal.md \
  docs/goals/015-synth-small-target-time-error-anatomy-audit/Goal.md
do
  printf '\n=== %s ===\n' "$path"
  sed -n '1,280p' "$path"
done
```

## Prerequisite Artifact Chain

The error-anatomy CLI should read prerequisite artifacts from disk. If they are
missing locally, rebuild the existing ignored synthetic chain using repo-local
commands. A typical local sequence is:

```bash
uv run python scripts/run_synth_small_observations.py
uv run python scripts/run_synth_small_extirpation_reconstruction.py
uv run python scripts/evaluate_synth_small_response_screen.py
uv run python scripts/audit_synth_small_false_negatives.py
uv run python scripts/run_synth_small_observation_support_counterfactual.py
uv run python scripts/analyze_synth_small_target_timing_residuals.py
```

If a prerequisite command requires an earlier bridge artifact, use the current
repo-local runbook sequence and record the substitution in `Log.md`.

## Focused Development Loop

Write the spec and tests before implementation:

```bash
uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov
```

Implement until the focused test passes:

```bash
uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov
```

Run the new CLI:

```bash
uv run python scripts/audit_synth_small_target_time_errors.py
```

Expected output directory:

```text
artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/
```

Required files:

```text
target_time_error_anatomy_config.json
site_target_time_error_audit.csv
target_time_error_group_summary.csv
error_mechanism_summary.csv
observable_proxy_summary.csv
transform_error_contrast.csv
bias_classification_summary.csv
recommendation.json
verification.json
report.md
```

## Validation

Run:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov
uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov
uv run pytest tests/test_synth_small_false_negative_mechanism_audit.py --no-cov
uv run pytest tests/test_synth_small_observation_support_counterfactual_screen.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run python scripts/audit_synth_small_target_time_errors.py
git status --ignored --short artifacts dist
```

Generated artifacts and build outputs must remain ignored and unstaged.

## Stop Conditions

Stop and report rather than improvising if:

- required disk inputs cannot be found or rebuilt from existing repo commands;
- site-level joins cannot reconcile synth-small site count;
- status-quo finite count, false-negative count, Goal 013 support-floor finite
  count, or Goal 014 compatibility restoration cannot be reconciled;
- grouped summaries do not reconcile with the site-level table;
- the implementation would require changing observation design, reconstruction
  rules, scoring, candidates, or inference machinery.

## Wake-Up

When complete or blocked, send a short wake-up to the SpatExt orchestrator
thread and wait for review. Include branch/status, changed files, validation
results, generated artifact path, target-time error anatomy outcomes,
observable-proxy inventory, recommendation class, and boundary confirmation.
