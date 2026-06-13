# Plan

## 1. Confirm State And Branch

- Report actual working directory and Git state.
- Fetch `origin`.
- Confirm `origin/main` is at `5b181c9` or newer.
- Create local branch
  `codex/spatext-goal014-target-timing-residual-decomposition` from
  `origin/main`.
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
  - `spec/synth_small_summary_vector.md`;
  - `spec/synth_small_compatibility_screen.md`;
  - `spec/synth_small_compatibility_mismatch_audit.md`;
  - `spec/synth_small_false_negative_mechanism_audit.md`;
  - `spec/synth_small_observation_support_counterfactual_screen.md`.
- Read Goal 009 through Goal 013 packets and this Goal 014 packet.
- Read current source/test surfaces for observations, reconstruction,
  response-screen evaluation, summary vectors, compatibility screening,
  mismatch auditing, false-negative auditing, and observation-support
  counterfactuals.

## 3. Rebuild Or Verify Local Prerequisite Artifacts

- Inspect whether all required disk inputs exist.
- If missing, rebuild only the local ignored synthetic artifact chain needed by
  the runbook.
- Do not stage generated artifacts.
- Record which prerequisite artifacts were found or rebuilt in `Log.md`.

## 4. Write The Spec First

- Add `spec/synth_small_target_timing_residual_decomposition.md`.
- Define:
  - purpose and scope;
  - disk input contract;
  - target-transform IDs and semantics;
  - per-site target-resolution schema;
  - transform summary-vector schema;
  - component-loss schema;
  - component-delta schema;
  - ranking and recommendation semantics;
  - output artifact contract;
  - bridge-reconciliation checks against Goals 009, 010, and 013;
  - synthetic-only, evaluation-only, diagnostic-only, and non-inference
    boundary rules;
  - acceptance criteria.

## 5. Test First

- Add `tests/test_synth_small_target_timing_residual_decomposition.py`.
- Cover:
  - disk-first loading of prerequisite artifacts;
  - transform definitions emitted with stable IDs and boundary labels;
  - `status_quo_observed` reconciliation with Goal 010/013 counts, top
    candidate, class, and loss;
  - `goal013_support_floor` reconciliation with the emitted Goal 013
    `truth_guided_absence_floor_all` scenario;
  - `all_extirpated_true_time` reconciliation with the Goal 010 `ideal_true`
    finite-target and compatibility expectation;
  - one or more per-site resolution rows for transformed false-negative sites;
  - component-loss rows that sum to total ranking loss within tolerance;
  - component-delta table ordering and signs;
  - recommendation classification;
  - output artifact writing;
  - CLI execution.
- Run the focused test and confirm it fails before implementation.

## 6. Implement The Residual Decomposition

- Add `src/spatext/synth/small/target_timing_residual_decomposition.py`.
- Load required artifacts from disk and verify provenance.
- Build a small documented transform set.
- Produce site-level target-resolution rows without mutating default
  observation or reconstruction artifacts.
- Reuse existing summary-vector and compatibility-screen contracts where
  practical.
- Emit transform summary vectors, component losses, rankings, component deltas,
  recommendation, verification, and a compact report.
- Do not mutate observations, reconstruction, response-screen evaluation,
  summary-vector, compatibility-screen, mismatch-audit, false-negative-audit,
  or Goal 013 artifacts.

## 7. Add CLI And Exports

- Add `scripts/analyze_synth_small_target_timing_residuals.py`.
- Export the public API from `src/spatext/synth/small/__init__.py`.

## 8. Update Docs And Log

- Update `README.md` with the residual-decomposition surface and command.
- Update `AGENTS.md` if the authoritative spec list needs the new spec.
- Update `spec/report_log.md`.
- Update this goal `Log.md` throughout the run with checkpoints and validation
  evidence.

## 9. Validate

Run a proportionate validation ladder:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov
uv run pytest tests/test_synth_small_observation_support_counterfactual_screen.py --no-cov
uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov
uv run pytest tests/test_synth_small_summary_vector.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the residual-decomposition CLI against local ignored artifacts:

```bash
uv run python scripts/analyze_synth_small_target_timing_residuals.py
```

Check generated/build artifact handling:

```bash
git status --ignored --short artifacts dist
```

## 10. Report And Wake Up

- Report changed files.
- Report validation results.
- Report transform IDs and semantics.
- Report status-quo reconciliation.
- Report Goal 013 support-floor reconciliation.
- Report whether `all_extirpated_true_time` restores the Goal 010 `ideal_true`
  compatibility expectation.
- Report the dominant residual components and component deltas.
- Report recommendation class.
- Confirm generated artifacts remain unstaged.
- Confirm no commit or push was performed.
- Send a short wake-up to the SpatExt orchestrator thread when complete or
  blocked, then wait for review.
