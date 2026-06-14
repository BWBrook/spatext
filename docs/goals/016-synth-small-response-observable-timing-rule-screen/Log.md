# Log

## 2026-06-14 - Orchestrator Packet

Barry approved a response-observable timing-rule screen after Goal 015 showed
that the current synth-small timing residual is late-biased, spatially
structured, and partly visible through response-observable proxies. Barry also
raised a strategic concern that the constrained synth-small grid may be too
simple and too sparse to identify anything subtler than a linear wave, and
suggested that a later synthetic landscape might need larger extent,
impassable water bodies, low-quality matrix, higher-quality patches,
corridors, spatial contagion, and multiple colonisation points.

The orchestrator's judgement is that this Goal 016 should remain narrow:
perform one last response-only rule screen on the current toy system before
moving to a larger synthetic-world redesign or an explicit observation/process
model. A positive rule-screen result should be treated as diagnostic, and any
spatial/front-band gain must be audited for simple-grid overfit risk. A
negative result should help justify moving beyond deterministic response-only
rules.

The orchestrator created this Goal 016 packet for `mink`. The goal asks for a
synthetic-only, evaluation-only screen of deterministic response-observable
target-time rules, with truth-guided and truth-only targets retained only as
references.

No implementation, validation run, commit, push, or project/science work was
performed by the orchestrator.

## 2026-06-14 - Action Implementation

Starting state:

- repository: `/Users/bwbrook/papers/spatext`;
- branch: `main...origin/main` at Goal 015 commit `018bc8d`;
- only untracked starting work: this Goal 016 packet.

Action setup:

- read `Goal.md`, `Plan.md`, `Runbook.md`, and this `Log.md`;
- fetched `origin`;
- created branch
  `codex/spatext-goal016-response-observable-timing-rule-screen` from
  `origin/main`, preserving the untracked Goal 016 packet;
- refreshed repo-local `AGENTS.md`, README, problem/theory specs, report-log
  headings, and the Goal 009/010/013/014/015 specs/source/test surfaces;
- confirmed prerequisite ignored artifacts were already present locally, so no
  prerequisite rebuild was needed before implementation.

Test-first checkpoint:

- added focused tests in
  `tests/test_synth_small_response_observable_timing_rule_screen.py`;
- RED run:
  `uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov`
  failed during collection because
  `build_synth_small_response_observable_timing_rule_screen` was not yet
  exported.

Implementation added:

- spec:
  `spec/synth_small_response_observable_timing_rule_screen.md`;
- module:
  `src/spatext/synth/small/response_observable_timing_rule_screen.py`;
- CLI:
  `scripts/screen_synth_small_response_observable_timing_rules.py`;
- package exports in `src/spatext/synth/small/__init__.py`;
- README and `AGENTS.md` updates.

Rule set:

- `status_quo_observed` baseline;
- eligible response-observable rules:
  - `long_detection_gap_shift_minus4`;
  - `west_band_shift_minus4`;
  - `long_gap_or_west_band_shift_minus4`;
  - `nonfinite_last_survey_expansion`;
- references:
  - `goal013_support_floor`;
  - `all_extirpated_true_time`.

Focused GREEN run:

- `uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov`
  passed (`3` tests).

Interim interpretation:

- best eligible response-observable rule:
  `long_detection_gap_shift_minus4`;
- best eligible rule remains incompatible under the unchanged Goal 010
  compatibility thresholds;
- `all_extirpated_true_time` remains the only restoring reference;
- spatial/front-band rule gains are emitted with explicit
  simple-grid-overfit-risk labels.

Full validation:

- `git diff --check` passed.
- `uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov`
  passed (`3` tests).
- `uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov`
  passed (`3` tests).
- `uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov`
  passed (`3` tests).
- `uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov`
  passed (`6` tests).
- `uv run pytest tests/test_synth_small_summary_vector.py --no-cov`
  passed (`5` tests).
- `uv run ruff format --check .` passed (`62` files already formatted).
- `uv run ruff check .` passed.
- `uv run mypy src tests` passed (`42` source files).
- `uv run pytest` passed (`92` tests, `93.03%` coverage).
- `uv build` passed.
- `uv run python scripts/screen_synth_small_response_observable_timing_rules.py`
  passed and wrote `11` files.
- `git status --ignored --short artifacts dist` showed only ignored
  `artifacts/` and `dist/`.

Final CLI outcome:

- rules evaluated: `7`;
- eligible response-observable rules: `4`;
- compatible eligible response-observable rules: `0`;
- best eligible response-observable rule:
  `long_detection_gap_shift_minus4`;
- best eligible class: `incompatible`;
- recommendation: `response_only_signal_insufficient`.

Generated artifacts were regenerated under
`artifacts/synth_small_response_screen/evaluation/response_observable_timing_rule_screen/`
and remain ignored/unstaged.

## 2026-06-14 - Review Iteration: Finite-Support Auditability Polish

Orchestrator review found that the timing-residual side of the screen was
auditable, but the finite-target-support conclusion leaned too heavily on the
broad `nonfinite_last_survey_expansion` stress test, which assigns last survey
time to every status-quo nonfinite site. The requested narrow polish was to add
at least one conservative response-observable finite-support candidate and make
its nonfinite-to-finite accounting visible in artifacts, tests, spec, report,
recommendation, and verification.

Test-first checkpoint:

- added focused assertions that require
  `nonfinite_supported_final_survey_gap_expansion`, explicit
  nonfinite-to-finite conversion columns in `rule_rankings.csv`, and a
  `finite_support_screen` recommendation payload;
- RED run:
  `uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov`
  failed because the rule count/component rows still reflected the original
  `7`-rule screen and no conservative finite-support rows existed.

Implementation polish:

- added `nonfinite_supported_final_survey_gap_expansion`, a conservative
  response-observable finite-support candidate that assigns `last_survey_time`
  only to status-quo nonfinite sites with below-threshold final absence,
  at least `8` observed survey times, at least one detection, and a final
  survey at least `8` time steps after the last detection;
- kept `nonfinite_last_survey_expansion` as a broad all-nonfinite stress test;
- extended `rule_rankings.csv` and `recommendation.json` with:
  - status-quo nonfinite sites converted to finite;
  - converted sites that are true extirpated under synthetic audit;
  - converted sites that are not true extirpated under synthetic audit;
  - finite-support role;
  - loss delta from the Goal 013 support-floor reference;
  - fraction of the status-quo-to-Goal 013 loss gap closed;
- added a `finite_support_accounting` verification check;
- added a finite-support table to `report.md`.

Focused GREEN run:

- `uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov`
  passed (`4` tests).

Updated interim interpretation:

- rules evaluated: `8`;
- eligible response-observable rules: `5`;
- compatible eligible response-observable rules: `0`;
- best eligible response-observable rule changed to
  `nonfinite_supported_final_survey_gap_expansion`;
- conservative finite-support candidate converts `12` status-quo nonfinite
  sites, of which `8` are true extirpated and `4` are not true extirpated under
  synthetic audit;
- conservative finite-support candidate yields `163` finite targets, default
  loss `3.17643512355`, class `incompatible`, and large-error count `79`;
- it improves loss versus status quo but closes only `0.211403424727` of the
  status-quo-to-Goal 013 loss gap, below the deterministic `0.5` materiality
  threshold;
- recommendation remains `response_only_signal_insufficient`.

Review-iteration validation:

- `git diff --check` passed.
- `uv run pytest tests/test_synth_small_response_observable_timing_rule_screen.py --no-cov`
  passed (`4` tests).
- `uv run pytest tests/test_synth_small_target_time_error_anatomy_audit.py --no-cov`
  passed (`3` tests).
- `uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov`
  passed (`3` tests).
- `uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov`
  passed (`6` tests).
- `uv run pytest tests/test_synth_small_summary_vector.py --no-cov`
  passed (`5` tests).
- `uv run ruff format --check .` passed (`62` files already formatted).
- `uv run ruff check .` passed.
- `uv run mypy src tests` passed (`42` source files).
- `uv run pytest` passed (`93` tests, `93.07%` coverage).
- `uv build` passed.
- `uv run python scripts/screen_synth_small_response_observable_timing_rules.py`
  passed and wrote `11` files.
- `git status --ignored --short artifacts dist` showed only ignored
  `artifacts/` and `dist/`.

Generated artifacts were regenerated under
`artifacts/synth_small_response_screen/evaluation/response_observable_timing_rule_screen/`
and remain ignored/unstaged.
