# Log

## 2026-06-23 - Implementation

- Confirmed the action repo was clean on `main...origin/main`.
- Created branch
  `codex/spatext-goal022-recoverability-target-observation-design` from
  `origin/main`.
- Read repo-local `AGENTS.md`, README, Goal 019-021 specs, and synth-medium
  observation/reconstruction/counterfactual modules.
- Wrote the focused Goal 022 test contract first; the RED check failed because
  the new Goal 022 exports did not exist.
- Implemented the Goal 022 module, CLI, spec, exports, and review-pack docs.
- Focused Goal 022 tests pass locally:
  `uv run pytest tests/test_synth_medium_recoverability_target_observation_design.py --no-cov`
  (`5` tests).

Preliminary deterministic outcome:

- candidate regime count: `8`
- field-plausible candidate count: `6`
- best field-plausible candidate:
  `integrated_recoverability_target_panel`
- best field-plausible rule: `final_absence_run_2`
- best field-plausible finite recall: `0.881557472604`
- best field-plausible false negatives: `508`
- diagnostic ceiling false negatives: `0`
- recommendation: `recoverability_review_ready`

No published Goal 017-021 source contract was changed. No fitting, inference,
real-data analysis, remote compute, commit, push, generated-artifact staging,
or Goal 023 work was started.

## 2026-06-23 - Validation Complete

Full validation passed:

- `git status --short --branch --untracked-files=all`
- `git diff --check`
- `uv run pytest tests/test_synth_medium_recoverability_target_observation_design.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_observation_design_counterfactual_screen.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_response_reconstruction_benchmark.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_spread_impact.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_landscape.py --no-cov`
  (`5` passed)
- `uv run ruff format --check .` (`81` files already formatted)
- `uv run ruff check .`
- `uv run mypy src tests` (`55` source files)
- `uv run pytest` (`123` passed, coverage `93.83%`)
- `uv build`
- `uv run python scripts/build_synth_medium_recoverability_target_observation_design.py`
  (`15` files written)
- `git status --ignored --short artifacts dist` showed only
  `!! artifacts/` and `!! dist/`

Final CLI outcome:

- baseline regime: `structured_response_observed_default`
- baseline primary rule: `final_absence_run_1`
- candidate regime count: `8`
- rule count: `3`
- best field-plausible regime: `integrated_recoverability_target_panel`
- best field-plausible rule: `final_absence_run_2`
- best field-plausible finite recall: `0.881557472604`
- best field-plausible false negatives: `508`
- ceiling finite recall: `1.0`
- ceiling false negatives: `0`
- decision recommendation: `recoverability_review_ready`

Generated artifacts were written under
`artifacts/synth_medium_recoverability_target_observation_design/` and remained
ignored/unstaged.

## 2026-06-23 - Review Iteration: Effort-Aware Decision Layer

Orchestrator review accepted the core candidate-regime outputs but requested a
narrow decision-layer polish before publication.

Implemented changes:

- Removed the ID-first preference for
  `integrated_recoverability_target_panel` in best field-plausible candidate
  selection.
- Documented and implemented criterion-driven best selection: readiness class,
  lower loss, lower false negatives, lower large errors, higher finite recall,
  lower false positives, then stable regime ID.
- Added decision-summary effort accounting for baseline, best field-plausible
  candidate, lowest-effort ready candidate, and diagnostic ceiling:
  survey-record count, deltas/ratios versus baseline and ceiling, surveyed-cell
  count, and final-absence support count.
- Separated best-performing ready candidate from lowest-effort ready candidate
  in `readiness_decision_summary.csv`, report text, and the decision montage.
- Added a `Records` column to the decision montage so the high survey burden is
  visible in the visual review artifact.

The candidate regimes, generated observations, reconstruction rules, thresholds,
and headline numerical outcomes were not changed.
