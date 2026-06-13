# Runbook

## Start

```bash
cd /Users/bwbrook/papers/spatext
pwd
git status --short --branch
git fetch --prune origin
git switch -c codex/spatext-goal014-target-timing-residual-decomposition origin/main
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
rg '^## Interaction|^# Interaction' spec/report_log.md
```

Read the relevant specs and goal packets before implementing:

```bash
for path in \
  spec/synth_small_observations.md \
  spec/synth_small_extirpation_reconstruction.md \
  spec/synth_small_response_screen_evaluation.md \
  spec/synth_small_summary_vector.md \
  spec/synth_small_compatibility_screen.md \
  spec/synth_small_compatibility_mismatch_audit.md \
  spec/synth_small_false_negative_mechanism_audit.md \
  spec/synth_small_observation_support_counterfactual_screen.md \
  docs/goals/009-synth-small-summary-vector-bridge/Goal.md \
  docs/goals/010-synth-small-compatibility-screen/Goal.md \
  docs/goals/011-realistic-observed-compatibility-audit/Goal.md \
  docs/goals/012-response-reconstruction-false-negative-mechanism-audit/Goal.md \
  docs/goals/013-post-extirpation-observation-support-counterfactual-screen/Goal.md \
  docs/goals/014-synth-small-target-timing-residual-decomposition/Goal.md
do
  printf '\n=== %s ===\n' "$path"
  sed -n '1,260p' "$path"
done
```

## Prerequisite Artifact Chain

The residual-decomposition CLI should read prerequisite artifacts from disk. If
they are missing locally, rebuild the existing ignored synthetic chain using
repo-local commands. A typical local sequence is:

```bash
uv run python scripts/run_synth_small_observations.py
uv run python scripts/run_synth_small_extirpation_reconstruction.py
uv run python scripts/evaluate_synth_small_response_screen.py
uv run python scripts/run_synth_small_summary_vector.py
uv run python scripts/run_synth_small_compatibility_screen.py
uv run python scripts/audit_synth_small_compatibility_mismatch.py
uv run python scripts/audit_synth_small_false_negatives.py
uv run python scripts/run_synth_small_observation_support_counterfactual.py
```

If any command name has changed, use the current repo-local equivalent and
record the substitution in `Log.md`.

## Focused Development Loop

Write the spec and tests before implementation:

```bash
uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov
```

Implement until the focused test passes:

```bash
uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov
```

Run the new CLI:

```bash
uv run python scripts/analyze_synth_small_target_timing_residuals.py
```

Expected output directory:

```text
artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/
```

Required files:

```text
residual_decomposition_config.json
target_transform_definitions.csv
site_target_transform_resolution.csv
target_transform_summary_vectors.csv
target_transform_component_losses.csv
target_transform_rankings.csv
component_delta_table.csv
recommendation.json
verification.json
report.md
```

## Validation

Run:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov
uv run pytest tests/test_synth_small_observation_support_counterfactual_screen.py --no-cov
uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov
uv run pytest tests/test_synth_small_summary_vector.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run python scripts/analyze_synth_small_target_timing_residuals.py
git status --ignored --short artifacts dist
```

Generated artifacts and build outputs must remain ignored and unstaged.

## Stop Conditions

Stop and report rather than improvising if:

- required disk inputs cannot be found or rebuilt from existing repo commands;
- the `status_quo_observed` transform cannot reconcile with Goal 010/013;
- the `goal013_support_floor` transform cannot reconcile with Goal 013;
- the `all_extirpated_true_time` transform cannot reconcile with the Goal 010
  `ideal_true` compatibility expectation;
- the implementation would require changing observation design, reconstruction
  rules, summary-vector scoring, compatibility-screen scoring, process
  candidates, or inference machinery.

## Wake-Up

When complete or blocked, send a short wake-up to the SpatExt orchestrator
thread and wait for review. Include branch/status, changed files, validation
results, generated artifact path, transform outcomes, dominant residual
components, recommendation class, and boundary confirmation.
