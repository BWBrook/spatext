# Runbook

## Start

```bash
cd /Users/bwbrook/papers/spatext
pwd
git status --short --branch
git fetch --prune origin
git switch -c codex/spatext-goal016-response-observable-timing-rule-screen origin/main
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
  spec/synth_small_summary_vector.md \
  spec/synth_small_compatibility_screen.md \
  spec/synth_small_observation_support_counterfactual_screen.md \
  spec/synth_small_target_timing_residual_decomposition.md \
  spec/synth_small_target_time_error_anatomy_audit.md \
  docs/goals/013-post-extirpation-observation-support-counterfactual-screen/Goal.md \
  docs/goals/014-synth-small-target-timing-residual-decomposition/Goal.md \
  docs/goals/015-synth-small-target-time-error-anatomy-audit/Goal.md \
  docs/goals/016-synth-small-response-observable-timing-rule-screen/Goal.md
do
  printf '\n=== %s ===\n' "$path"
  sed -n '1,300p' "$path"
done
```

## Prerequisite Artifact Chain

The rule-screen CLI should read prerequisite artifacts from disk. If they are
missing locally, rebuild the existing ignored synthetic chain using repo-local
commands. A typical local sequence is:

```bash
uv run python scripts/run_synth_small_observations.py
uv run python scripts/run_synth_small_extirpation_reconstruction.py
uv run python scripts/run_synth_small_summary_vector.py
uv run python scripts/run_synth_small_compatibility_screen.py
uv run python scripts/evaluate_synth_small_response_screen.py
uv run python scripts/run_synth_small_observation_support_counterfactual.py
uv run python scripts/analyze_synth_small_target_timing_residuals.py
uv run python scripts/audit_synth_small_target_time_errors.py
```

If a prerequisite command requires an earlier bridge artifact, use the current
repo-local runbook sequence and record the substitution in `Log.md`.

## Focused Development Loop

Write the spec and tests before implementation:

```bash
uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov
```

Implement until the focused test passes:

```bash
uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov
```

Run the new CLI:

```bash
uv run python scripts/screen_synth_small_response_observable_timing_rules.py
```

Expected output directory:

```text
artifacts/synth_small_response_screen/evaluation/response_observable_timing_rule_screen/
```

Required files:

```text
timing_rule_screen_config.json
rule_definitions.csv
site_rule_resolution.csv
rule_summary_vectors.csv
rule_component_losses.csv
rule_rankings.csv
proxy_rule_performance.csv
grid_simplicity_risk_audit.csv
recommendation.json
verification.json
report.md
```

## Validation

Run:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov
uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov
uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov
uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run python scripts/screen_synth_small_response_observable_timing_rules.py
git status --ignored --short artifacts dist
```

Generated artifacts and build outputs must remain ignored and unstaged.

## Stop Conditions

Stop and report rather than improvising if:

- required disk inputs cannot be found or rebuilt from existing repo commands;
- site-level joins cannot reconcile synth-small site count;
- status-quo, Goal 013 support-floor, Goal 014 all-true, or Goal 015 anatomy
  accounting cannot be reconciled;
- summary-vector or compatibility-loss reuse would require changing existing
  scoring contracts;
- a proposed candidate rule needs hidden truth but is not labelled as a
  truth-guided or truth-only reference;
- implementation would require changing observation design, production
  reconstruction rules, scoring, candidates, a richer landscape generator, or
  inference machinery.

## Wake-Up

When complete or blocked, send a short wake-up to the SpatExt orchestrator
thread and wait for review. Include branch/status, changed files, validation
results, generated artifact path, candidate rule summary, best eligible rule,
proxy-stratified performance, grid/front-band overfit-risk assessment,
recommendation class, generated-artifact handling, and boundary confirmation.
