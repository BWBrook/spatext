# Plan

## 1. Confirm State And Branch

- Fetch `origin`.
- Confirm `origin/main` includes Goal 017 commit `ce42cce` or newer.
- Confirm the worktree is clean.
- Create branch
  `codex/spatext-goal018-synth-medium-spread-impact-review` from
  `origin/main`.
- If the branch exists or state differs materially, stop and report exact
  status without force/reset/rebase/delete/repair.

## 2. Refresh Contracts

- Read `AGENTS.md`, `README.md`, `spec/problem_statement.md`,
  `spec/theory.md`, `spec/synth_medium_landscape.md`, Goal 017 packet files,
  `src/spatext/synth/medium/landscape.py`, and relevant synth-small predator
  truth/visual patterns.
- Search `spec/report_log.md` interaction headings before adding the new
  entry.

## 3. Write Spec And Tests First

- Add `spec/synth_medium_spread_impact_review_pack.md`.
- Add `tests/test_synth_medium_spread_impact.py`.
- Cover:
  - required output and visual files;
  - deterministic rebuild;
  - boundary labels;
  - reconciliation to the Goal 017 landscape;
  - water never colonized;
  - source zones seed and contribute;
  - candidate log has bounded attempts and one selected default;
  - cell truth, summaries, and time-series reconcile;
  - review gates pass;
  - CLI writes the bundle.
- Run focused tests and confirm RED before implementation.

## 4. Implement Spread-Impact Module

- Add `src/spatext/synth/medium/spread_impact.py`.
- Build from `build_synth_medium_landscape()` without mutating Goal 017.
- Represent passable adjacency from Goal 017 edge/cell records.
- Compute weighted graph spread from all source-zone cells using habitat
  conductance and deterministic edge costs.
- Record source-zone contribution by lowest-cost source path.
- Build prey baseline abundance from habitat quality.
- Compute predator pressure/occupancy and prey abundance decline summaries.
- Derive prey impact/extirpation timing with nonzero lag after predator
  arrival.
- Evaluate a bounded set of named parameter candidates and select one default.
- Emit audit tables, verification checks, report, and deterministic SVG
  visuals.

## 5. Add CLI And Exports

- Add `scripts/simulate_synth_medium_spread_impact.py`.
- Export public API from `src/spatext/synth/medium/__init__.py`.

## 6. Update Docs And Logs

- Update `README.md`.
- Update `AGENTS.md` with the new authoritative spec.
- Add Interaction 38 to `spec/report_log.md`.
- Update this goal `Log.md`.

## 7. Validate

Run:

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

## 8. Wake Up

Report branch/status, changed files, validation, generated artifact path,
visual paths, selected parameter set, candidate tuning summary, key spread and
prey-impact outcomes, review-gate summary, recoverability proxy summary,
generated-artifact handling, and boundary confirmation.
