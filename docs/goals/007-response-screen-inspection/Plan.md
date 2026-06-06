# Plan

## 1. Correct Branch State

- Report actual linked-worktree state.
- Fetch `origin`.
- Confirm `origin/main` is at `96e38bc` or newer.
- Create `codex/spatext-goal007-response-screen-inspection` from `origin/main`.
- Confirm branch state before editing.

## 2. Test First

- Add focused tests for:
  - disk-first inspection artifact writing,
  - missing required screen artifact failure,
  - decoy evaluation payload ignored,
  - CLI execution.
- Run the focused test and confirm it fails before implementation.

## 3. Implement Inspector

- Add `src/spatext/synth/small/response_screen_inspect.py`.
- Load the screen bundle from disk.
- Verify required files, columns, source verification, response-only boundary,
  and numeric coherence.
- Build review summary and group review flags.
- Render a compact inspection report.

## 4. Add CLI And Exports

- Add `scripts/inspect_synth_small_response_screen.py`.
- Export inspection types and functions from `spatext.synth.small`.

## 5. Add Spec And Docs

- Add `spec/synth_small_response_screen_inspection.md`.
- Update `README.md` only for the new user-facing inspection surface.
- Update `spec/report_log.md`.
- Update this goal log with validation evidence.

## 6. Validate

Run:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_response_screen_inspection.py --no-cov
uv run pytest tests/test_synth_small_response_screen.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the CLI against a local ignored screen bundle.

## 7. Report

- Report changed files.
- Report validation results.
- Confirm generated artifacts remain unstaged.
- Do not commit or push.
