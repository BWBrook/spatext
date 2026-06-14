# Plan

## 1. Confirm State And Branch

- Report actual working directory and Git state.
- Fetch `origin`.
- Confirm `origin/main` includes Goal 015 commit `018bc8d` or newer.
- Create local branch
  `codex/spatext-goal016-response-observable-timing-rule-screen` from
  `origin/main`, preserving this untracked Goal 016 packet.
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
  - `spec/synth_small_summary_vector.md`;
  - `spec/synth_small_compatibility_screen.md`;
  - `spec/synth_small_observation_support_counterfactual_screen.md`;
  - `spec/synth_small_target_timing_residual_decomposition.md`;
  - `spec/synth_small_target_time_error_anatomy_audit.md`.
- Read Goal 013 through Goal 015 packets and this Goal 016 packet.
- Read current source/test surfaces for observations, reconstruction,
  summary-vector, compatibility-screen, observation-support counterfactuals,
  target-timing residual decomposition, and target-time error anatomy.

## 3. Rebuild Or Verify Local Prerequisite Artifacts

- Inspect whether all required disk inputs exist.
- If missing, rebuild only the local ignored synthetic artifact chain needed by
  the runbook.
- Do not stage generated artifacts.
- Record which prerequisite artifacts were found or rebuilt in `Log.md`.

## 4. Write The Spec First

- Add `spec/synth_small_response_observable_timing_rule_screen.md`.
- Define:
  - purpose and scope;
  - disk input contract;
  - rule eligibility classes;
  - candidate and reference rule-definition schema;
  - site-rule resolution schema;
  - summary-vector and compatibility-loss reuse contract;
  - proxy-stratified performance schema;
  - grid-simplicity and spatial-overfit risk audit;
  - recommendation classes;
  - output artifact contract;
  - reconciliation checks against Goals 010, 013, 014, and 015;
  - synthetic-only, evaluation-only, rule-screen-only, and non-inference
    boundary rules;
  - acceptance criteria.

## 5. Test First

- Add `tests/test_synth_small_response_observable_timing_rule_screen.py`.
- Cover:
  - disk-first loading of prerequisite artifacts;
  - rule definitions separating response-observable rules from truth-guided and
    truth-only references;
  - one row per synth-small site per rule in the site-rule table;
  - reconciliation with Goal 010 compatibility expectations, Goal 013 support
    floor, Goal 014 all-true restoration, and Goal 015 proxy/anatomy counts;
  - deterministic summary-vector and component-loss accounting;
  - proxy-stratified performance for the Goal 015 residual-timing candidates;
  - grid/front-band overfit-risk audit;
  - recommendation classification;
  - output artifact writing;
  - CLI execution;
  - synthetic-only/evaluation-only/rule-screen-only labels.
- Run the focused test and confirm it fails before implementation.

## 6. Implement The Rule Screen

- Add `src/spatext/synth/small/response_observable_timing_rule_screen.py`.
- Load required artifacts from disk and verify provenance.
- Define a compact, deterministic rule set. Include status quo as baseline,
  eligible response-observable rules, and truth-guided/truth-only references.
- Keep candidate rules simple and auditable. Prefer transparent threshold,
  cap, lag, and proxy-combination rules over opaque fitting.
- Use existing summary-vector and compatibility-screen calculations rather
  than duplicating scoring semantics.
- Emit rule definitions, site-level rule resolution, summary-vector rows,
  component losses, rankings, proxy performance, spatial/front-band risk
  audit, recommendation, verification, and a compact report.
- Do not mutate observations, reconstruction, response-screen evaluation,
  summary-vector, compatibility-screen, Goal 013, Goal 014, or Goal 015
  artifacts.

## 7. Add CLI And Exports

- Add `scripts/screen_synth_small_response_observable_timing_rules.py`.
- Export the public API from `src/spatext/synth/small/__init__.py`.

## 8. Update Docs And Log

- Update `README.md` with the response-observable timing-rule screen surface
  and command.
- Update `AGENTS.md` if the authoritative spec list needs the new spec.
- Update `spec/report_log.md`.
- Update this goal `Log.md` throughout the run with checkpoints and validation
  evidence.

## 9. Validate

Run a proportionate validation ladder:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov
uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov
uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov
uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the new CLI against local ignored artifacts:

```bash
uv run python scripts/screen_synth_small_response_observable_timing_rules.py
```

Check generated/build artifact handling:

```bash
git status --ignored --short artifacts dist
```

## 10. Report And Wake Up

- Report changed files.
- Report validation results.
- Report generated artifact path and required files.
- Report candidate rule count and eligibility-class counts.
- Report the top eligible response-observable rule and whether it improves
  compatibility.
- Report the status-quo, Goal 013 support-floor, Goal 014 all-true, and best
  eligible-rule reconciliation.
- Report proxy-stratified performance, especially for
  `long_detection_to_target_gap`,
  `spatial_front_band_west_band_signal`, and `sparse_survey_history`.
- Report grid/front-band overfit-risk assessment.
- Report recommendation class.
- Confirm generated artifacts remain unstaged.
- Confirm no commit or push was performed.
- Send a short wake-up to the SpatExt orchestrator thread when complete or
  blocked, then wait for review.
