# Runbook

## Start

```bash
cd /Users/bwbrook/papers/spatext
pwd
git fetch --prune origin
git status --short --branch --untracked-files=all
git rev-parse origin/main
git log -1 --oneline origin/main
git switch -c codex/spatext-goal019-synth-medium-observation-design-review origin/main
git status --short --branch --untracked-files=all
```

Stop if branch creation fails, the branch already exists, `origin/main` is not
cleanly the Goal 018 base, or the worktree has unexpected changes.

## Required Reading

```bash
sed -n '1,220p' AGENTS.md
sed -n '1,320p' README.md
sed -n '1,260p' spec/problem_statement.md
sed -n '1,360p' spec/theory.md
sed -n '1,280p' spec/synth_medium_landscape.md
sed -n '1,320p' spec/synth_medium_spread_impact_review_pack.md
for path in docs/goals/017-synth-medium-landscape-design-review-pack/{Goal.md,Plan.md,Runbook.md,Log.md}; do
  sed -n '1,320p' "$path"
done
for path in docs/goals/018-synth-medium-spread-impact-review-pack/{Goal.md,Plan.md,Runbook.md,Log.md}; do
  sed -n '1,320p' "$path"
done
sed -n '1,760p' src/spatext/synth/medium/landscape.py
sed -n '1,900p' src/spatext/synth/medium/spread_impact.py
sed -n '1,760p' src/spatext/synth/small/observations.py
sed -n '1,520p' src/spatext/synth/small/reconstruction.py
rg '^## Interaction|^# Interaction|^### Interaction' spec/report_log.md
```

## Focused Development Loop

```bash
uv run pytest tests/test_synth_medium_observation_design.py --no-cov
```

The first run should fail before implementation because the Goal 019 API does
not yet exist.

After implementation:

```bash
uv run pytest tests/test_synth_medium_observation_design.py --no-cov
uv run python scripts/build_synth_medium_observation_design.py
```

Expected output directory:

```text
artifacts/synth_medium_observation_design/
```

## Validation

```bash
git status --short --branch --untracked-files=all
git diff --check
uv run pytest tests/test_synth_medium_observation_design.py --no-cov
uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
uv run pytest tests/test_synth_medium_landscape.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run python scripts/build_synth_medium_observation_design.py
git status --ignored --short artifacts dist
```

Generated artifacts and build outputs must remain ignored and unstaged.

## Stop Conditions

Stop and report rather than improvising if:

- the accepted Goal 018 truth cannot be used without changing its contract;
- water cells would need survey records;
- the default imperfect regime cannot preserve a usable signal without turning
  into perfect observability;
- visual artifacts cannot be emitted without adding a new plotting dependency;
- audit tables cannot reconcile;
- implementation would require reconstruction, fitting, inference, real data,
  broad sweeps, remote compute, commit, push, or Goal 020.

## Wake-Up

When complete or blocked, wake the SpatExt orchestrator with branch/status,
changed files, validation results, generated artifact and visual paths, regime
IDs, selected default, benchmark/default/stress comparison, key default
outcomes, review-gate pass/fail summary, artifact handling, and boundary
confirmation.
