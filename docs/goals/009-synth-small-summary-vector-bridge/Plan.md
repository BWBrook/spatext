# Plan

## 1. Confirm State And Branch

- Report actual working directory and Git state.
- Fetch `origin`.
- Confirm `origin/main` is at `3ce6101` or newer.
- Create local branch `codex/spatext-goal009-summary-vector` from `origin/main`.
- If the branch already exists or checkout fails, stop and report the exact
  blocker. Do not force, delete, reset, or repair by improvisation.

## 2. Refresh Contracts

- Read `AGENTS.md`, `README.md`, `spec/problem_statement.md`,
  `spec/theory.md`, and `spec/report_log.md`.
- Read Goal 005-008 packets and active specs:
  - `docs/goals/005-response-only-extirpation-reconstruction/`
  - `docs/goals/006-response-only-inference-screen/`
  - `docs/goals/007-response-screen-inspection/`
  - `docs/goals/008-response-screen-evaluation-audit/`
  - `spec/synth_small_extirpation_reconstruction.md`
  - `spec/synth_small_response_screen.md`
  - `spec/synth_small_response_screen_evaluation.md`
- Read the current source/test surfaces for reconstruction, screen, inspection,
  and evaluation.

## 3. Write The Spec First

- Add `spec/synth_small_summary_vector.md`.
- Define:
  - purpose and scope;
  - input contract;
  - `ideal_true` and `realistic_observed` modes;
  - summary components;
  - missing metric semantics;
  - output artifact contract;
  - synthetic-only boundary rules;
  - acceptance criteria.

## 4. Test First

- Add `tests/test_synth_small_summary_vector.py`.
- Cover:
  - summary component computation for finite inputs;
  - undefined metric handling with explicit missing reasons;
  - both mode labels;
  - output artifact writing;
  - CLI execution;
  - no hidden-truth leakage into response-only artifact paths;
  - missing required artifact failure.
- Run the focused test and confirm it fails before implementation.

## 5. Implement Summary Vector Layer

- Add `src/spatext/synth/small/summary_vector.py`.
- Load artifacts from disk using the repository's existing CSV/JSON helper
  patterns.
- Build mode-specific target tables:
  - `ideal_true`: `true_extirpation` joined to `driver_arrival`;
  - `realistic_observed`: `observed_extirpation_time` joined to
    `driver_arrival`.
- Compute the required summary components and coverage curve rows.
- Emit verification checks and a compact Markdown report.
- Keep missing or undefined metrics explicit and machine-readable.

## 6. Add CLI And Exports

- Add `scripts/build_synth_small_summary_vector.py`.
- Export summary-vector types/functions from `src/spatext/synth/small/__init__.py`.

## 7. Update Docs And Log

- Update `README.md` with the new summary-vector surface and command.
- Update `spec/report_log.md`.
- Update `docs/goals/009-synth-small-summary-vector-bridge/Log.md` throughout
  the run with checkpoints and validation evidence.

## 8. Validate

Run a proportionate validation ladder:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_summary_vector.py --no-cov
uv run pytest tests/test_synth_small_extirpation_reconstruction.py --no-cov
uv run pytest tests/test_synth_small_response_screen.py --no-cov
uv run pytest tests/test_synth_small_response_screen_evaluation.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the summary-vector CLI against local ignored artifacts.

## 9. Report And Wake Up

- Report changed files.
- Report validation results.
- Confirm generated artifacts remain unstaged.
- Confirm no commit or push was performed.
- Send a short wake-up to the SpatExt orchestrator thread when complete or
  blocked, then wait for review.
