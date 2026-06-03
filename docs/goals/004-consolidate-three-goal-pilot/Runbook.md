# Runbook

## Working Directory

```bash
cd /Users/bwbrook/papers/spatext
```

## Operating Rules

- Read `Goal.md`, `Plan.md`, `Runbook.md`, and `Log.md` before changing files.
- Follow repo-local `AGENTS.md`.
- Treat the existing dirty Goals 001-003 work as project state.
- Do not stage ignored artefacts, caches, build outputs, or host noise.
- Commit and push only after validation passes and exact staging is confirmed.
- Do not start the next science goal.

## Initial Checks

```bash
git status --short --branch
git ls-files -m -o --exclude-standard
git status --short --ignored
```

## Packaging Hygiene

If `.DS_Store` is not already ignored:

1. Add `.DS_Store` as its own line in `.gitignore`.
2. Remove the local untracked `.DS_Store` file from the working tree.
3. Confirm it no longer appears as an untracked path.

```bash
git status --short
```

## Validation Lane

Run:

```bash
uv sync --all-groups
uv run python scripts/build_synth_small_predator_truth.py
uv run python scripts/inspect_synth_small_predator_truth.py
uv run python scripts/run_synth_small_predator_truth_sensitivity.py
uv run python scripts/build_synth_small_observations.py
uv run python scripts/inspect_synth_small_observations.py
jq '{passed}' artifacts/synth_small_predator_truth/inspection/verification.json
jq '{recommendation: .recommendation, default_classification: .default_candidate.readiness_classification}' artifacts/synth_small_predator_truth_sensitivity/readiness.json
jq '{passed}' artifacts/synth_small_observations/inspection/verification.json
jq '{passed, finite_metrics: ([.metrics[] | type == "number"] | all)}' artifacts/synth_small_observations/inspection/recoverability_smoke.json
test -s artifacts/synth_small_observations/inspection/report.md
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run pre-commit after staging the accepted files so new files are included in
the hook surface.

## Exact Staging

Stage only these paths:

```bash
git add \
  .gitignore \
  AGENTS.md \
  README.md \
  spec/report_log.md \
  spec/synth_small_predator_truth_inspection.md \
  spec/synth_small_predator_truth_sensitivity.md \
  spec/synth_small_observations.md \
  src/spatext/synth/small/__init__.py \
  src/spatext/synth/small/predator_inspect.py \
  src/spatext/synth/small/sensitivity.py \
  src/spatext/synth/small/observations.py \
  scripts/inspect_synth_small_predator_truth.py \
  scripts/run_synth_small_predator_truth_sensitivity.py \
  scripts/build_synth_small_observations.py \
  scripts/inspect_synth_small_observations.py \
  tests/test_synth_small_predator_truth_inspection.py \
  tests/test_synth_small_predator_truth_sensitivity.py \
  tests/test_synth_small_observations.py \
  docs/goals/001-predator-truth-inspection \
  docs/goals/002-deterministic-benchmark-sensitivity \
  docs/goals/003-first-response-observation-layer \
  docs/goals/004-consolidate-three-goal-pilot
```

Then inspect:

```bash
git diff --cached --name-only
git diff --cached --stat
git status --short
uv run pre-commit run --all-files
```

If pre-commit changes files, inspect and stage the relevant accepted files
again, then rerun the affected checks.

## Commit And Push

After validation and staged-diff review:

```bash
git commit -m "feat: add synth-small observation readiness workflow"
git rev-parse HEAD
git push origin main
git status --short --branch
```

If the push is rejected, do not force-push. Run:

```bash
git fetch --prune origin
git status --short --branch
git log --oneline --decorate --graph --max-count=12 --all
```

Then stop and report.

## Reporting Rules

Update `Log.md` at each checkpoint. The final response should include:

- commit SHA
- push result
- validation summary
- staged/committed path categories
- final `git status --short --branch`
- residual risks
- recommended next science goal
