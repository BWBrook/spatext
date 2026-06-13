# Plan

## 1. Confirm State And Branch

- Report actual working directory and Git state.
- Fetch `origin`.
- Confirm `origin/main` is at `b58901a` or newer.
- Create local branch
  `codex/spatext-goal015-target-time-error-anatomy-audit` from `origin/main`.
- If branch creation or checkout fails, stop and report the exact blocker. Do
  not force, delete, reset, rebase, or repair by improvisation.

## 2. Refresh Contracts

- Read `AGENTS.md`, `README.md`, `spec/problem_statement.md`,
  `spec/theory.md`, and `spec/report_log.md`.
- Before editing `spec/report_log.md`, search current interaction headings so
  the new entry does not duplicate an earlier number.
- Read these specs:
  - `spec/synth_small_observations.md`;
  - `spec/synth_small_extirpation_reconstruction.md`;
  - `spec/synth_small_response_screen_evaluation.md`;
  - `spec/synth_small_false_negative_mechanism_audit.md`;
  - `spec/synth_small_observation_support_counterfactual_screen.md`;
  - `spec/synth_small_target_timing_residual_decomposition.md`.
- Read Goal 012 through Goal 014 packets and this Goal 015 packet.
- Read current source/test surfaces for observations, reconstruction,
  response-screen evaluation, false-negative auditing, observation-support
  counterfactuals, and target-timing residual decomposition.

## 3. Rebuild Or Verify Local Prerequisite Artifacts

- Inspect whether all required disk inputs exist.
- If missing, rebuild only the local ignored synthetic artifact chain needed by
  the runbook.
- Do not stage generated artifacts.
- Record which prerequisite artifacts were found or rebuilt in `Log.md`.

## 4. Write The Spec First

- Add `spec/synth_small_target_time_error_anatomy_audit.md`.
- Define:
  - purpose and scope;
  - disk input contract;
  - site audit schema;
  - target-time error definitions;
  - grouping dimensions and group-summary schema;
  - observable-proxy classification rules;
  - transform-error contrast schema;
  - bias-classification summary schema;
  - recommendation classes;
  - output artifact contract;
  - reconciliation checks against Goals 012, 013, and 014;
  - synthetic-only, evaluation-only, diagnostic-only, and non-inference
    boundary rules;
  - acceptance criteria.

## 5. Test First

- Add `tests/test_synth_small_target_time_error_anatomy_audit.py`.
- Cover:
  - disk-first loading of prerequisite artifacts;
  - one site-audit row per synth-small site;
  - status-quo finite count, false-negative count, Goal 013 support-floor
    finite count, and Goal 014 compatibility restoration reconciliation;
  - signed and absolute target-time error calculations;
  - grouped summaries reconciling with site-level rows;
  - observable-proxy summary separating response-observable, truth-only, and
    mixed signals;
  - recommendation classification;
  - output artifact writing;
  - CLI execution;
  - synthetic-only/evaluation-only/diagnostic-only labels.
- Run the focused test and confirm it fails before implementation.

## 6. Implement The Error Anatomy Audit

- Add `src/spatext/synth/small/target_time_error_anatomy_audit.py`.
- Load required artifacts from disk and verify provenance.
- Join site-level truth, reconstruction, response-evaluation,
  false-negative-audit, Goal 013, and Goal 014 rows by site ID.
- Compute status-quo and support-floor signed/absolute timing errors relative
  to synthetic true extirpation time.
- Classify error direction and magnitude.
- Derive response-observable survey/detection proxy fields from observation
  and reconstruction artifacts.
- Emit site audit rows, grouped summaries, mechanism summary, proxy inventory,
  transform contrast, bias classification, recommendation, verification, and a
  compact report.
- Do not mutate observations, reconstruction, response-screen evaluation,
  false-negative-audit, Goal 013, Goal 014, summary-vector, or compatibility
  artifacts.

## 7. Add CLI And Exports

- Add `scripts/audit_synth_small_target_time_errors.py`.
- Export the public API from `src/spatext/synth/small/__init__.py`.

## 8. Update Docs And Log

- Update `README.md` with the target-time error anatomy surface and command.
- Update `AGENTS.md` if the authoritative spec list needs the new spec.
- Update `spec/report_log.md`.
- Update this goal `Log.md` throughout the run with checkpoints and validation
  evidence.

## 9. Validate

Run a proportionate validation ladder:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov
uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov
uv run pytest tests/test_synth_small_false_negative_mechanism_audit.py --no-cov
uv run pytest tests/test_synth_small_observation_support_counterfactual_screen.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the error-anatomy CLI against local ignored artifacts:

```bash
uv run python scripts/audit_synth_small_target_time_errors.py
```

Check generated/build artifact handling:

```bash
git status --ignored --short artifacts dist
```

## 10. Report And Wake Up

- Report changed files.
- Report validation results.
- Report target-time error anatomy outcomes.
- Report status-quo and support-floor error summaries.
- Report strongest mechanism, region/front-band, survey-gap, and detection-
  persistence signals.
- Report observable versus truth-only proxy inventory.
- Report recommendation class.
- Confirm generated artifacts remain unstaged.
- Confirm no commit or push was performed.
- Send a short wake-up to the SpatExt orchestrator thread when complete or
  blocked, then wait for review.
