# Log

## 2026-06-13 - Orchestrator Packet

Barry approved the next diagnostic table-first goal after Goal 013 showed that
finite-target support alone improves but does not restore compatibility.

The orchestrator created this Goal 014 packet for `mink`. The goal asks for a
synthetic-only, evaluation-only residual-decomposition bundle that compares a
small set of target-time transformations, reconciles against Goals 009, 010,
and 013, and emits component-loss and component-delta tables that identify the
remaining incompatibility driver.

No implementation, validation run, commit, push, or project/science work was
performed by the orchestrator.

## 2026-06-13 - Action Implementation

`mink` restarted Goal 014 on branch
`codex/spatext-goal014-target-timing-residual-decomposition` from
`origin/main` at `5b181c9`, preserving the untracked Goal 014 packet.

Initial state matched the corrective restart gate:

```text
pwd: /Users/bwbrook/papers/spatext
branch: main
status: only the four untracked Goal 014 packet files
```

Read the Goal 014 packet and refreshed the Goal 009-013 contracts, current
summary-vector, compatibility-screen, false-negative audit, and Goal 013
counterfactual source/test surfaces.

Prerequisite artifacts were already present locally except for the
packet-listed `artifacts/synth_small_summary_vector/target_summary.json`.
That file is not part of the accepted Goal 009 artifact contract, which emits
`summary_vector_config.json`, `summary_components.csv`, `mode_summary.json`,
`coverage_curve.csv`, and `verification.json`. The Goal 014 implementation
therefore verifies those published Goal 009 files and the Goal 010
`compatibility_screen/target_summary.json`, records this interpretation in
`residual_decomposition_config.json` and `verification.json`, and does not
create or mutate an upstream Goal 009 artifact.

Added:

- `spec/synth_small_target_timing_residual_decomposition.md`
- `src/spatext/synth/small/target_timing_residual_decomposition.py`
- `scripts/analyze_synth_small_target_timing_residuals.py`
- `tests/test_synth_small_target_timing_residual_decomposition.py`

Updated:

- `AGENTS.md`
- `README.md`
- `src/spatext/synth/small/__init__.py`

Test-first checkpoint:

- RED:
  `uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov`
  failed because `build_synth_small_target_timing_residual_decomposition` was
  not exported.
- GREEN:
  `uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov`
  passed (`3` tests).

CLI smoke:

```text
uv run python scripts/analyze_synth_small_target_timing_residuals.py
```

wrote the required 10-file bundle under
`artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/`.

Transform outcomes for the default candidate:

- `status_quo_observed`: loss `3.52263635737`, `incompatible`
- `goal013_support_floor`: loss `1.88500331398`, `incompatible`
- `false_negative_true_time`: loss `1.95601478734`, `incompatible`
- `false_negative_true_time_detection_respecting`: loss `2.34353714396`,
  `incompatible`
- `all_extirpated_true_time`: loss `0`, `compatible`

The `all_extirpated_true_time` transform restores the Goal 010 `ideal_true`
compatibility expectation. The dominant `goal013_support_floor` residual
components for the default candidate are `coverage_curve_rmse`, `lag_mean`,
`front_plane_gradient_magnitude`, and `arrival_target_r2`. The recommendation
class is `timing_bias_drives_residual`.

Final validation completed:

- `git status --short --branch`
- `git diff --check`
- `uv run pytest tests/test_synth_small_target_timing_residual_decomposition.py --no-cov`
  (`3` tests)
- `uv run pytest tests/test_synth_small_observation_support_counterfactual_screen.py --no-cov`
  (`4` tests)
- `uv run pytest tests/test_synth_small_compatibility_screen.py --no-cov`
  (`6` tests)
- `uv run pytest tests/test_synth_small_summary_vector.py --no-cov`
  (`5` tests)
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest` (`86` tests, coverage `92.37%`)
- `uv build`
- `uv run python scripts/analyze_synth_small_target_timing_residuals.py`
- `git status --ignored --short artifacts dist`

Generated artifacts and build outputs remained ignored:

```text
!! artifacts/
!! dist/
```

No observation-design, production reconstruction-rule, response/summary/
compatibility/mismatch/false-negative/Goal 013 scoring, candidate, ABC, POM,
likelihood, posterior, parameter-recovery, real-data, remote-compute, commit,
or push boundary was crossed.

## 2026-06-13 - Review Polish

The Goal 014 review requested narrow auditability polish for
`component_delta_table.csv` and stricter component-loss verification.

Changed the residual-decomposition artifact contract so
`component_delta_table.csv` now includes:

- `absolute_delta_from_status_quo_rank_within_transform_candidate`
- `absolute_delta_from_goal013_support_floor_rank_within_transform_candidate`

Ranks are deterministic within each `(target_transform_id, candidate_label)`
group, sorted by descending absolute delta with component-name tie breaks. The
existing `residual_rank_within_transform_candidate` column remains unchanged.

Tightened `component_loss_accounting` verification to require both:

- component weighted gaps sum to ranking losses; and
- `score_row_count == expected_score_row_count`.

Updated focused tests, spec, README, generated report text, and this log. The
ignored Goal 014 artifact bundle was regenerated with:

```text
uv run python scripts/analyze_synth_small_target_timing_residuals.py
```

The regenerated `all_extirpated_true_time` / `default` absolute-delta ranks
from `goal013_support_floor` are:

1. `coverage_curve_rmse` (`0.676110198119`)
2. `lag_mean` (`0.46547619047`)
3. `front_plane_gradient_magnitude` (`0.36179212734`)
4. `arrival_target_r2` (`0.329361891376`)

Scientific outcomes remained unchanged:

- `all_extirpated_true_time` restores the Goal 010 `ideal_true` bridge.
- `goal013_support_floor` remains incompatible with default loss
  `1.88500331398`.
- Recommendation remains `timing_bias_drives_residual`.

No observation-design, production reconstruction-rule, response/summary/
compatibility/mismatch/false-negative/Goal 013 scoring, candidate, ABC, POM,
likelihood, posterior, parameter-recovery, real-data, remote-compute, commit,
or push boundary was crossed.
