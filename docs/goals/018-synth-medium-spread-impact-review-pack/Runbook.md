# Runbook

## Start

```bash
cd /Users/bwbrook/papers/spatext
pwd
git fetch --prune origin
git status --short --branch --untracked-files=all
git rev-parse origin/main
git log -1 --oneline origin/main
git switch -c codex/spatext-goal018-synth-medium-spread-impact-review origin/main
git status --short --branch --untracked-files=all
```

Stop if branch creation fails, the branch already exists, `origin/main` is not
cleanly the Goal 017 base, or the worktree has unexpected changes.

## Required Reading

```bash
sed -n '1,220p' AGENTS.md
sed -n '1,260p' README.md
sed -n '1,240p' spec/problem_statement.md
sed -n '1,360p' spec/theory.md
sed -n '1,260p' spec/synth_medium_landscape.md
for path in docs/goals/017-synth-medium-landscape-design-review-pack/{Goal.md,Plan.md,Runbook.md,Log.md}; do
  sed -n '1,320p' "$path"
done
sed -n '1,760p' src/spatext/synth/medium/landscape.py
sed -n '1,760p' src/spatext/synth/small/predator.py
rg '^## Interaction|^# Interaction|^### Interaction' spec/report_log.md
```

## Focused Development Loop

```bash
uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
```

The first run should fail before implementation because the Goal 018 API does
not yet exist.

After implementation:

```bash
uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
uv run python scripts/simulate_synth_medium_spread_impact.py
```

Expected output directory:

```text
artifacts/synth_medium_spread_impact/
```

## Validation

```bash
git status --short --branch --untracked-files=all
git diff --check
uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
uv run pytest tests/test_synth_medium_landscape.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run python scripts/simulate_synth_medium_spread_impact.py
git status --ignored --short artifacts dist
```

Generated artifacts and build outputs must remain ignored and unstaged.

## Stop Conditions

Stop and report rather than improvising if:

- the accepted Goal 017 landscape cannot be used without changing its contract;
- water cells would need to be colonized or assigned prey dynamics;
- no bounded candidate produces a plausible information-rich scenario;
- visual artifacts cannot be emitted without adding a new plotting dependency;
- audit tables cannot reconcile;
- implementation would require observations, reconstruction, scoring changes,
  inference, real data, broad sweeps, remote compute, commit, or push.

## Wake-Up

When complete or blocked, wake the SpatExt orchestrator with branch/status,
changed files, validation results, generated artifact and visual paths,
selected default parameter set, candidate tuning summary, key outcomes,
review-gate pass/fail summary, recoverability proxy summary, artifact handling,
and boundary confirmation.
