# Plan

## 1. Confirm State And Branch

- Report actual working directory and Git state.
- Fetch `origin`.
- Confirm `origin/main` is at `7e4e6f7` or newer.
- Create local branch
  `codex/spatext-goal012-false-negative-mechanism-audit` from `origin/main`.
- If the branch already exists or checkout fails, stop and report the exact
  blocker. Do not force, delete, reset, or repair by improvisation.

## 2. Refresh Contracts

- Read `AGENTS.md`, `README.md`, `spec/problem_statement.md`,
  `spec/theory.md`, `spec/report_log.md`,
  `spec/synth_small_extirpation_reconstruction.md`,
  `spec/synth_small_response_screen_evaluation.md`, and
  `spec/synth_small_compatibility_mismatch_audit.md`.
- Read Goal 005, Goal 008, Goal 011, and this Goal 012 packet.
- Read current source/test surfaces for:
  - observations;
  - extirpation reconstruction;
  - response-screen evaluation;
  - compatibility mismatch audit.

## 3. Write The Spec First

- Add `spec/synth_small_false_negative_mechanism_audit.md`.
- Define:
  - purpose and scope;
  - disk input contract;
  - false-negative site feature definitions;
  - mechanism classes and priority order;
  - group and timing summaries;
  - recommendation classes;
  - output artifact contract;
  - synthetic-only, evaluation-only, audit-only, and non-inference boundary
    rules;
  - acceptance criteria.

## 4. Test First

- Add `tests/test_synth_small_false_negative_mechanism_audit.py`.
- Cover:
  - disk-first loading of response-screen evaluation, reconstruction,
    observation, and Goal 011 artifacts;
  - exactly 101 false-negative site rows;
  - one primary mechanism per false negative;
  - mechanism and group counts reconciling to the false-negative count;
  - timing feature arithmetic;
  - recommendation classification;
  - output artifact writing;
  - CLI execution;
  - synthetic-only/audit-only/evaluation-only labels.
- Run the focused test and confirm it fails before implementation.

## 5. Implement False-Negative Audit Layer

- Add `src/spatext/synth/small/false_negative_mechanism_audit.py`.
- Load required CSV/JSON artifacts from disk.
- Join rows by `site_id` and verify row alignment.
- Compute site-level timing and detection features from emitted visits and
  observations.
- Assign primary mechanisms using the documented priority order.
- Build mechanism summaries, group summaries, observation timing summaries,
  recommendation payload, verification checks, and a compact report.
- Do not mutate reconstruction, response-screen, evaluation, summary-vector,
  compatibility-screen, or mismatch-audit artifacts.

## 6. Add CLI And Exports

- Add `scripts/audit_synth_small_false_negatives.py`.
- Export the audit API from `src/spatext/synth/small/__init__.py`.

## 7. Update Docs And Log

- Update `README.md` with the false-negative audit surface and command.
- Update `AGENTS.md` if the authoritative spec list needs the new spec.
- Update `spec/report_log.md`.
- Update
  `docs/goals/012-response-reconstruction-false-negative-mechanism-audit/Log.md`
  throughout the run with checkpoints and validation evidence.

## 8. Validate

Run a proportionate validation ladder:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_false_negative_mechanism_audit.py --no-cov
uv run pytest tests/test_synth_small_compatibility_mismatch_audit.py --no-cov
uv run pytest tests/test_synth_small_response_screen_evaluation.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the false-negative audit CLI against local ignored artifacts.

## 9. Report And Wake Up

- Report changed files.
- Report validation results.
- Report false-negative count, dominant mechanism classes, strongest group
  signals, and recommendation class.
- Confirm generated artifacts remain unstaged.
- Confirm no commit or push was performed.
- Send a short wake-up to the SpatExt orchestrator thread when complete or
  blocked, then wait for review.
