# Plan

## 1. Correct Worktree State

- Report the actual linked Codex worktree state before editing.
- Fetch `origin`.
- Create `codex/spatext-goal006-response-screen` from `origin/main`.
- Confirm branch state again before implementation.

## 2. Define The Screen Contract

- Add `spec/synth_small_response_screen.md`.
- Specify response-only inputs and forbidden outputs.
- Define compact site, group, time, and failure-mode summaries.
- State that the screen is not ABC/POM or parameter inference.

## 3. Test First

- Add focused tests for:
  - artifact writing,
  - default summary values,
  - hidden-truth boundary,
  - CLI execution.
- Run the focused test and confirm it fails before production code exists.

## 4. Implement Minimal Screen

- Add `src/spatext/synth/small/response_screen.py`.
- Read only reconstruction response artifacts from disk.
- Compute:
  - site-count and status summaries,
  - group summaries by region and front band,
  - time detection summaries,
  - low-information and cautionary failure notes.
- Export the public API from `spatext.synth.small`.

## 5. Add CLI

- Add `scripts/run_synth_small_response_screen.py`.
- Default input:
  `artifacts/synth_small_extirpation_reconstruction/`.
- Default output:
  `artifacts/synth_small_response_screen/`.

## 6. Update Docs

- Add the Goal 006 spec.
- Update `README.md` with the new response-screen surface.
- Update `spec/report_log.md`.
- Keep `AGENTS.md` unchanged unless workflow rules change.

## 7. Validate

Run:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_response_screen.py --no-cov
uv run pytest tests/test_synth_small_extirpation_reconstruction.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

Run the screen CLI when local reconstruction artifacts are available or rebuild
small prerequisites as needed.

## 8. Report

- Report files changed.
- Report validation commands and results.
- Confirm generated artifacts remain unstaged.
- Do not commit or push.
