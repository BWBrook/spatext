# Plan

## 1. Confirm State And Branch

- Fetch `origin`.
- Confirm `origin/main` is Goal 018 commit `187b387` or newer.
- Confirm the worktree is clean.
- Create branch
  `codex/spatext-goal019-synth-medium-observation-design-review` from
  `origin/main`.
- If the branch exists or state differs materially, stop and report exact
  status without force/reset/rebase/delete/repair.

## 2. Refresh Contracts

- Read repo-local instructions, README, scientific specs, Goal 017/018
  packets, and the current medium landscape/spread-impact modules.
- Read synth-small observation/reconstruction modules for artifact and
  response-only caution patterns.
- Search report-log headings before adding a new interaction.

## 3. Write Spec And Tests First

- Add `spec/synth_medium_observation_design_review_pack.md`.
- Add `tests/test_synth_medium_observation_design.py`.
- Cover:
  - required output and visual files;
  - deterministic rebuild;
  - boundary labels;
  - reconciliation to Goal 018 truth;
  - no water surveys;
  - benchmark/default/stress regimes and selected default;
  - default imperfect coverage, false negatives, post-impact support, timing
    signal, and spatial signal;
  - sparse stress lower information than default;
  - CLI writes the bundle.
- Run focused tests and confirm RED before implementation.

## 4. Implement Observation-Design Module

- Add `src/spatext/synth/medium/observations.py`.
- Build from `build_synth_medium_spread_impact_review_pack()` without mutating
  Goal 017 or Goal 018.
- Implement deterministic regimes with response-only observation records.
- Keep predator truth out of analyst-facing observation records.
- Build audit summaries, verification checks, report, and deterministic SVGs.

## 5. Add CLI And Exports

- Add `scripts/build_synth_medium_observation_design.py`.
- Export public API from `src/spatext/synth/medium/__init__.py`.

## 6. Update Docs And Logs

- Update `README.md`.
- Update `AGENTS.md` with the new authoritative spec.
- Add Interaction 39 to `spec/report_log.md`.
- Update this goal `Log.md`.

## 7. Validate

Run:

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

## 8. Wake Up

Report branch/status, changed files, validation, generated artifact and visual
paths, regime IDs, selected default, benchmark/default/stress comparison, key
default outcomes, review-gate summary, artifact handling, and boundary
confirmation.
