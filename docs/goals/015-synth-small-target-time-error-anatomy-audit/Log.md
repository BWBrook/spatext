# Log

## 2026-06-13 - Orchestrator Packet

Barry approved a careful follow-on diagnostic after Goal 014 showed that the
Goal 010 bridge is recoverable under true target times, while the Goal 013
support floor remains incompatible because timing and target-shape errors
remain.

The orchestrator created this Goal 015 packet for `mink`. The goal asks for a
synthetic-only, evaluation-only target-time error anatomy audit that localizes
site-level timing error, summarizes error by mechanism and observation context,
and separates response-observable proxies from hidden-truth-only diagnostics.

No implementation, validation run, commit, push, or project/science work was
performed by the orchestrator.

## 2026-06-13 - Action Implementation

`mink` started from `/Users/bwbrook/papers/spatext`, confirmed
`main...origin/main` at Goal 014 commit `b58901a`, and created branch
`codex/spatext-goal015-target-time-error-anatomy-audit` from `origin/main`,
preserving the untracked Goal 015 packet.

Read before implementation:

- repo-local `AGENTS.md`;
- `README.md`;
- `spec/problem_statement.md`;
- `spec/theory.md`;
- `spec/report_log.md`;
- Goal 012-014 specs and goal packets;
- Goal 015 `Goal.md`, `Plan.md`, `Runbook.md`, and `Log.md`;
- current Goal 012 false-negative, Goal 013 counterfactual, and Goal 014
  residual-decomposition source/test surfaces.

Prerequisite ignored artifacts for observations, reconstruction,
response-screen evaluation, false-negative audit, Goal 013 counterfactuals,
and Goal 014 residual decomposition were present locally, so no prerequisite
rebuild was needed before implementation.

Implementation added:

- `spec/synth_small_target_time_error_anatomy_audit.md`
- `tests/test_synth_small_target_time_error_anatomy_audit.py`
- `src/spatext/synth/small/target_time_error_anatomy_audit.py`
- `scripts/audit_synth_small_target_time_errors.py`
- exports in `src/spatext/synth/small/__init__.py`
- README, AGENTS, and report-log updates for the new diagnostic surface

TDD checkpoint:

- RED check:
  `uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov`
  failed initially because
  `build_synth_small_target_time_error_anatomy_audit` was not exported.
- Focused Goal 015 tests then passed:
  `uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov`
  (`3` passed).

Current diagnostic outcomes:

- site audit reconciles `625` synth-small sites;
- true extirpated sites: `252`;
- status-quo finite targets: `151`;
- response-screen false negatives: `101`;
- Goal 013 support-floor finite targets: `252`;
- Goal 014 `all_extirpated_true_time` still restores the Goal 010 ideal-truth
  bridge (`default`, `compatible`, loss `0`);
- Goal 013 support floor resolves the finite-target gap but leaves late-biased,
  spatially structured timing error concentrated in already finite status-quo
  targets;
- recommendation: `response_observable_rule_screen_ready`.

Full validation completed:

- `git status --short --branch` showed the expected Goal 015 source/docs/test
  footprint on
  `codex/spatext-goal015-target-time-error-anatomy-audit...origin/main`.
- `git diff --check` passed.
- `uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov`
  passed (`3` tests).
- `uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov`
  passed (`3` tests).
- `uv run pytest tests/test_synth_small_false_negative_mechanism_audit.py --no-cov`
  passed (`4` tests).
- `uv run pytest tests/test_synth_small_observation_support_counterfactual_screen.py --no-cov`
  passed (`4` tests).
- `uv run ruff format --check .` passed (`59` files already formatted).
- `uv run ruff check .` passed.
- `uv run mypy src tests` passed (`40` source files checked).
- `uv run pytest` passed (`89` tests, coverage `92.87%`).
- `uv build` passed.
- `uv run python scripts/audit_synth_small_target_time_errors.py` passed and
  wrote `10` files under
  `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/`.
- `git status --ignored --short artifacts dist` confirmed generated artifacts
  and build outputs remain ignored (`!! artifacts/`, `!! dist/`).

CLI outcome:

- sites audited: `625`;
- true extirpated sites: `252`;
- recommendation: `response_observable_rule_screen_ready`;
- dominant remaining error group: `not_false_negative`;
- strongest spatial signal: `west_band`;
- observable proxy inventory: `4` response-observable, `3` mixed, and `2`
  truth-only signals.

No generated artifact, `dist/`, cache, or virtual-environment file was staged.
No commit or push was performed.

## 2026-06-13 - Review Polish: Observable-Proxy Auditability

Review requested a narrow tightening of `observable_proxy_summary.csv` before
acceptance. The issue was that the proxy table identified response-observable
signals but did not show whether those signals covered the remaining large
support-floor timing errors, and it still carried a fixed east/edge spatial
flag even though the generated evidence identified `west_band` as the strongest
spatial signal.

Polish implemented:

- extended `observable_proxy_summary.csv` with:
  - `true_extirpated_affected_site_count`;
  - `support_floor_large_abs_error_site_count`;
  - `support_floor_large_abs_error_fraction`;
  - `rule_screen_role`;
- added role labels:
  - `finite_target_support_context`;
  - `residual_timing_candidate`;
  - `truth_only_reference`;
  - `mixed_evaluation_context`;
- added a data-derived response-observable spatial proxy,
  `spatial_front_band_west_band_signal`, sourced from
  `sites.csv:region,front_band`;
- removed the fixed `weak_east_or_edge_signal` site-level proxy flag;
- tightened the recommendation so `response_observable_rule_screen_ready`
  requires at least one response-observable `residual_timing_candidate` with
  nonzero large-error coverage.

Deterministic large-error proxy coverage after the polish:

- `status_quo_nonfinite`: role `finite_target_support_context`, large-error
  coverage `0`;
- `short_final_absence_run`: role `finite_target_support_context`,
  large-error coverage `0`;
- `long_detection_to_target_gap`: role `residual_timing_candidate`, `79`
  true-extirpated affected sites, `49` large support-floor timing errors,
  fraction `49/79`;
- `spatial_front_band_west_band_signal`: role `residual_timing_candidate`,
  `112` true-extirpated affected sites, `49` large support-floor timing
  errors, fraction `49/112`.

Scientific reconciliation counts and recommendation class remain unchanged:

- sites audited: `625`;
- true extirpated sites: `252`;
- status-quo finite targets: `151`;
- false negatives: `101`;
- support-floor finite targets: `252`;
- recommendation: `response_observable_rule_screen_ready`.

Review-polish validation completed:

- `git diff --check` passed.
- `uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov`
  passed (`3` tests).
- `uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov`
  passed (`3` tests).
- `uv run pytest tests/test_synth_small_false_negative_mechanism_audit.py --no-cov`
  passed (`4` tests).
- `uv run pytest tests/test_synth_small_observation_support_counterfactual_screen.py --no-cov`
  passed (`4` tests).
- `uv run ruff format --check .` passed (`59` files already formatted).
- `uv run ruff check .` passed.
- `uv run mypy src tests` passed (`40` source files checked).
- `uv run pytest` passed (`89` tests, coverage `92.74%`).
- `uv build` passed.
- `uv run python scripts/audit_synth_small_target_time_errors.py` passed and
  wrote `10` files under
  `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/`.
- `git status --ignored --short artifacts dist` confirmed generated artifacts
  and build outputs remain ignored (`!! artifacts/`, `!! dist/`).

Regenerated proxy-table contract:

- required columns are present:
  `true_extirpated_affected_site_count`,
  `support_floor_large_abs_error_site_count`,
  `support_floor_large_abs_error_fraction`, and `rule_screen_role`;
- `observable_proxy_summary.csv` now contains `5` response-observable, `3`
  mixed, and `2` truth-only rows;
- `recommendation.json` records `residual_timing_candidate_count = 3` with
  top residual-timing candidate proxies
  `long_detection_to_target_gap`,
  `spatial_front_band_west_band_signal`, and `sparse_survey_history`;
- `verification.json` passed all checks.
