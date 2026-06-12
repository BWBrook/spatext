# Plan

## 1. Confirm State And Branch

- Report actual working directory and Git state.
- Fetch `origin`.
- Confirm `origin/main` is at `0ee8f59` or newer.
- Create local branch `codex/spatext-goal011-compatibility-mismatch-audit`
  from `origin/main`.
- If the branch already exists or checkout fails, stop and report the exact
  blocker. Do not force, delete, reset, or repair by improvisation.

## 2. Refresh Contracts

- Read `AGENTS.md`, `README.md`, `spec/problem_statement.md`,
  `spec/theory.md`, `spec/report_log.md`,
  `spec/synth_small_summary_vector.md`, and
  `spec/synth_small_compatibility_screen.md`.
- Read Goal 008, Goal 009, and Goal 010 packets.
- Read current source/test surfaces for:
  - response-screen evaluation;
  - summary vectors;
  - compatibility screen.

## 3. Write The Spec First

- Add `spec/synth_small_compatibility_mismatch_audit.md`.
- Define:
  - purpose and scope;
  - input artifact contract;
  - target-delta summaries;
  - score-contribution summaries;
  - coverage-gap summaries;
  - response-screen evaluation bridge;
  - recommendation classes;
  - output artifact contract;
  - synthetic-only, audit-only, and non-inference boundary rules;
  - acceptance criteria.

## 4. Test First

- Add `tests/test_synth_small_compatibility_mismatch_audit.py`.
- Cover:
  - disk-first loading of Goal 009/010/008-style artifacts;
  - finite-target drop and false-negative bridge arithmetic;
  - component-loss contribution ranking for the top `realistic_observed`
    candidate;
  - coverage-gap reconstruction from `coverage_score_breakdown.csv`;
  - conservative recommendation classification;
  - output artifact writing;
  - CLI execution;
  - synthetic-only and audit-only labels.
- Run the focused test and confirm it fails before implementation.

## 5. Implement Mismatch Audit Layer

- Add `src/spatext/synth/small/compatibility_mismatch_audit.py`.
- Load required CSV/JSON artifacts from disk.
- Keep parsing and arithmetic small, explicit, and testable.
- Do not recompute compatibility scores from live model objects when the
  emitted Goal 010 artifacts already contain the score rows.
- Build target-mode deltas from Goal 009 artifacts.
- Build score-contribution summaries from Goal 10 `candidate_scores.csv`.
- Build coverage-gap summaries from Goal 10 `coverage_score_breakdown.csv`.
- Build evaluation bridge summaries from Goal 008 evaluation artifacts.
- Emit verification checks and a compact Markdown report.

## 6. Add CLI And Exports

- Add `scripts/audit_synth_small_compatibility_mismatch.py`.
- Export the audit API from `src/spatext/synth/small/__init__.py`.

## 7. Update Docs And Log

- Update `README.md` with the new mismatch-audit surface and command.
- Update `AGENTS.md` if the authoritative spec list needs the new spec.
- Update `spec/report_log.md`.
- Update `docs/goals/011-realistic-observed-compatibility-audit/Log.md`
  throughout the run with checkpoints and validation evidence.

## 8. Validate

Run a proportionate validation ladder:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_compatibility_mismatch_audit.py --no-cov
uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov
uv run pytest tests/test_synth_small_response_screen_evaluation.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the mismatch-audit CLI against local ignored artifacts.

## 9. Report And Wake Up

- Report changed files.
- Report validation results.
- Report the recommendation class and the dominant mismatch components.
- Confirm generated artifacts remain unstaged.
- Confirm no commit or push was performed.
- Send a short wake-up to the SpatExt orchestrator thread when complete or
  blocked, then wait for review.
