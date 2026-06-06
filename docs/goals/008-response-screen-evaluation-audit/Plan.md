# Plan

## 1. Correct Branch State

- Report actual linked-worktree state.
- Fetch `origin`.
- Confirm `origin/main` is at `db0517a` or newer.
- Create `codex/spatext-goal008-response-screen-evaluation-audit` from
  `origin/main`.
- Confirm branch state before editing.

## 2. Refresh Contracts

- Read repo guide, README, report log, Goal 005-007 packets, and active specs.
- Read reconstruction, screen, inspection source and tests.
- Keep the Goal 008 boundary: synthetic-only evaluation, not response-only
  decision-making.

## 3. Test First

- Add focused tests for:
  - synthetic-only audit artifact writing,
  - response-only artifact immutability,
  - evaluation namespace labelling,
  - no hidden-truth leakage into response contracts,
  - missing truth artifact failure,
  - CLI execution.
- Run the focused test and confirm it fails before implementation.

## 4. Implement Evaluation Audit

- Add `src/spatext/synth/small/response_screen_evaluate.py`.
- Read emitted screen artifacts from disk.
- Read reconstruction evaluation metrics and observation evaluation truth from
  clearly labelled artifacts.
- Join site reconstruction rows to truth rows.
- Compute site, group, and summary audit diagnostics.
- Write evaluation-only artifacts.

## 5. Add CLI And Exports

- Add `scripts/evaluate_synth_small_response_screen.py`.
- Export evaluation types and functions from `spatext.synth.small`.

## 6. Add Spec And Docs

- Add `spec/synth_small_response_screen_evaluation.md`.
- Update README with the evaluation-audit command.
- Update `spec/report_log.md`.
- Update this log with validation evidence.

## 7. Validate

Run:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_response_screen_evaluation.py --no-cov
uv run pytest tests/test_synth_small_response_screen.py --no-cov
uv run pytest tests/test_synth_small_response_screen_inspection.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the evaluation CLI against local ignored artifacts.

## 8. Report

- Report changed files.
- Report validation results.
- Confirm generated artifacts remain unstaged.
- Do not commit or push.
