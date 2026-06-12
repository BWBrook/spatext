# Plan

## 1. Confirm State And Branch

- Report actual working directory and Git state.
- Fetch `origin`.
- Confirm `origin/main` is at `0fd5ee5` or newer.
- Create local branch `codex/spatext-goal010-compatibility-screen` from
  `origin/main`.
- If the branch already exists or checkout fails, stop and report the exact
  blocker. Do not force, delete, reset, or repair by improvisation.

## 2. Refresh Contracts

- Read `AGENTS.md`, `README.md`, `spec/problem_statement.md`,
  `spec/theory.md`, `spec/report_log.md`, and
  `spec/synth_small_summary_vector.md`.
- Read Goal 009:
  - `docs/goals/009-synth-small-summary-vector-bridge/`
- Read current source/test surfaces for:
  - summary vectors;
  - predator truth sensitivity candidates;
  - observation and reconstruction only as needed for prerequisite artifacts.

## 3. Write The Spec First

- Add `spec/synth_small_compatibility_screen.md`.
- Define:
  - purpose and scope;
  - target-mode contract;
  - candidate-set contract;
  - target summary input contract;
  - candidate summary semantics;
  - admissibility gates;
  - weighted-gap loss;
  - missingness and invalid-candidate semantics;
  - output artifact contract;
  - synthetic-only and non-inference boundary rules;
  - acceptance criteria.

## 4. Test First

- Add `tests/test_synth_small_compatibility_screen.py`.
- Cover:
  - target summary parsing from Goal 009 style artifacts;
  - candidate summary generation for the tiny deterministic candidate set;
  - default candidate near-exact match in `ideal_true` mode;
  - ranking output for both modes;
  - invalid-candidate or missing-component handling with explicit reasons;
  - output artifact writing;
  - CLI execution;
  - synthetic-only and non-inference labels.
- Run the focused test and confirm it fails before implementation.

## 5. Implement Compatibility Screen Layer

- Add `src/spatext/synth/small/compatibility_screen.py`.
- Reuse existing summary-vector helpers where practical rather than duplicating
  summary math.
- Use existing `SensitivityCandidate` and predator-truth configuration helpers
  where practical for deterministic candidates.
- Build candidate target rows from candidate synthetic truth:
  - `T_X = candidate true_extirpation`
  - `T_P = candidate driver_arrival`
- Compare candidate summaries against both Goal 009 target modes.
- Emit:
  - scalar gap rows;
  - coverage RMSE rows;
  - gate decisions;
  - total weighted loss;
  - compatibility class;
  - deterministic rank within each mode.
- Keep all hidden-truth use confined to this synthetic method-development
  namespace.

## 6. Add CLI And Exports

- Add `scripts/run_synth_small_compatibility_screen.py`.
- Export the compatibility-screen API from
  `src/spatext/synth/small/__init__.py`.

## 7. Update Docs And Log

- Update `README.md` with the new compatibility-screen surface and command.
- Update `AGENTS.md` if the authoritative spec list needs the new spec.
- Update `spec/report_log.md`.
- Update `docs/goals/010-synth-small-compatibility-screen/Log.md` throughout
  the run with checkpoints and validation evidence.

## 8. Validate

Run a proportionate validation ladder:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov
uv run pytest tests/test_synth_small_summary_vector.py --no-cov
uv run pytest tests/test_synth_small_predator_truth_sensitivity.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the compatibility-screen CLI against local ignored artifacts.

## 9. Report And Wake Up

- Report changed files.
- Report validation results.
- Report candidate counts, top-ranked candidates by mode, and compatibility
  classes.
- Confirm generated artifacts remain unstaged.
- Confirm no commit or push was performed.
- Send a short wake-up to the SpatExt orchestrator thread when complete or
  blocked, then wait for review.
