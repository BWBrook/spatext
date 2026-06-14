# Runbook

## Start

```bash
cd /Users/bwbrook/papers/spatext
pwd
git status --short --branch
git fetch --prune origin
git switch -c codex/spatext-goal017-synth-medium-landscape-review origin/main
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
  spec/synth_small_baseline.md \
  spec/synth_small_predator_truth.md \
  spec/synth_small_observations.md \
  spec/synth_small_response_observable_timing_rule_screen.md \
  docs/goals/016-synth-small-response-observable-timing-rule-screen/Goal.md \
  docs/goals/017-synth-medium-landscape-design-review-pack/Goal.md
do
  printf '\n=== %s ===\n' "$path"
  sed -n '1,320p' "$path"
done
```

Read the source surfaces that are likely to matter:

```bash
sed -n '1,260p' src/spatext/spatial.py
sed -n '1,320p' src/spatext/synth/small/baseline.py
sed -n '1,320p' src/spatext/synth/small/predator.py
```

## Focused Development Loop

Write the spec and tests before implementation:

```bash
uv run pytest tests/test_synth_medium_landscape.py --no-cov
```

Implement until the focused test passes:

```bash
uv run pytest tests/test_synth_medium_landscape.py --no-cov
```

Run the new CLI:

```bash
uv run python scripts/build_synth_medium_landscape.py
```

Expected output directory:

```text
artifacts/synth_medium_landscape/
```

Required root files:

```text
landscape_config.json
cells.csv
adjacency.csv
patch_summary.csv
corridor_summary.csv
water_component_summary.csv
source_zone_summary.csv
connectivity_summary.csv
quality_summary.csv
verification.json
report.md
```

Required visual files:

```text
visuals/habitat_classes.svg
visuals/quality_surface.svg
visuals/water_barriers.svg
visuals/corridors_and_sources.svg
visuals/source_distance.svg
visuals/review_montage.svg
```

## Validation

Run:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_medium_landscape.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run python scripts/build_synth_medium_landscape.py
git status --ignored --short artifacts dist
```

Generated artifacts and build outputs must remain ignored and unstaged.

## Stop Conditions

Stop and report rather than improvising if:

- the design cannot produce coherent water/barrier components without
  fragmenting all passable land;
- source zones cannot reach a substantial passable component;
- visual artifacts cannot be emitted without adding a new plotting dependency;
- audit tables cannot reconcile with `cells.csv`;
- implementation would require predator spread, prey dynamics, observations,
  reconstruction, summary-vector/compatibility changes, fitting, inference, or
  real data.

## Wake-Up

When complete or blocked, send a short wake-up to the SpatExt orchestrator
thread and wait for review. Include branch/status, changed files, validation
results, generated artifact path, visual review paths, landscape dimensions,
habitat/source/connectivity summaries, verification result, generated-artifact
handling, and boundary confirmation.
