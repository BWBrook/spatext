# Log

## 2026-06-15 - Orchestrator Packet

Barry approved Goal 020 after accepting and publishing the Goal 019
observation-design review pack. The approved next step is a deterministic,
synthetic-only response-time reconstruction benchmark over the accepted Goal
019 observations and fixed Goal 018 latent truth.

The goal asks whether the `structured_response_observed_default` observation
regime retains enough response-only signal to justify later back-fitting work.
It includes the full-observability benchmark as a positive control and the
sparse regime as a low-information stress contrast.

Hard boundaries: no Goal 017 landscape change, Goal 018 truth change, Goal 019
observation-design change, production reconstruction-rule adoption, fitting,
ABC/POM/likelihood/MCMC/posterior work, parameter recovery, real-data analysis,
broad sweep, remote compute, commit, push, generated-artifact staging, or Goal
021.

## 2026-06-15 - Action Implementation

Created branch
`codex/spatext-goal020-synth-medium-response-reconstruction-benchmark` from
`origin/main` after confirming the action repo was clean at the accepted Goal
019 commit `93df97569b4810b8a1b100feaedc332a2534a40d`.

Read repo-local `AGENTS.md`, README, Goal 017/018/019 specs and logs, and the
current synth-medium landscape, spread-impact, and observation modules before
implementation.

Added focused tests first in
`tests/test_synth_medium_response_reconstruction_benchmark.py`. The RED check:

```bash
uv run pytest tests/test_synth_medium_response_reconstruction_benchmark.py --no-cov
```

failed because the new response-reconstruction API did not yet exist.

Implemented the Goal 020 review-pack footprint:

- `spec/synth_medium_response_reconstruction_benchmark.md`
- `src/spatext/synth/medium/response_reconstruction.py`
- `scripts/benchmark_synth_medium_response_reconstruction.py`
- `tests/test_synth_medium_response_reconstruction_benchmark.py`
- exports in `src/spatext/synth/medium/__init__.py`
- README, AGENTS, and report-log updates

After implementation, the focused Goal 020 tests passed:

```bash
uv run pytest tests/test_synth_medium_response_reconstruction_benchmark.py --no-cov
```

with `5` tests passing.

Generated review bundle:

```text
artifacts/synth_medium_response_reconstruction_benchmark/
```

CLI smoke:

```bash
uv run python scripts/benchmark_synth_medium_response_reconstruction.py
```

Output:

- selected default regime `structured_response_observed_default`
- rule count `3`
- primary default rule `final_absence_run_1`
- default finite recall `0.524364653765`
- default median absolute error `16.186166872186`
- recommendation `observation_design_not_recoverable_enough_for_backfitting`
- `16` files written

Headline benchmark outcomes:

- Full-observability positive control passed. Best benchmark rule
  `midpoint_after_last_detection` reconstructed all `4289` true positives with
  `0` false negatives and median absolute error `2.929258094361`.
- Default regime best rule `final_absence_run_1`: `2553` finite
  reconstructions, `2249` true positives, `304` false positives, `2040` false
  negatives, finite recall `0.524364653765`, specificity `0.675213675214`,
  precision `0.880924402664`, median absolute error `16.186166872186`, p90
  absolute error `56.5705868251`, and `809` large errors.
- Sparse stress best rule `final_absence_run_2`: `59` finite reconstructions,
  `52` true positives, finite recall `0.012124038237`, median absolute error
  `25.2808847092`, and worse loss than the default.
- Default support-gap accounting for `final_absence_run_1`: `5225` passable
  cells, `4411` surveyed cells, `814` never surveyed cells, `1216` cells with
  no detection history, `642` cells with no post-detection survey, and `2553`
  cells with finite reconstruction support.

Final validation completed:

- `git status --short --branch --untracked-files=all`
- `git diff --check`
- `uv run pytest tests/test_synth_medium_response_reconstruction_benchmark.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_spread_impact.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_landscape.py --no-cov`
  (`5` passed)
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest` (`113` passed, coverage `93.66%`)
- `uv build`
- `uv run python scripts/benchmark_synth_medium_response_reconstruction.py`
  (`16` files written)
- `git status --ignored --short artifacts dist`
  (`!! artifacts/`, `!! dist/`)

No Goal 017 landscape change, Goal 018 truth change, Goal 019
observation-design change, production reconstruction-rule adoption, fitting,
ABC/POM/likelihood/MCMC/posterior work, parameter recovery, real-data analysis,
broad sweep, remote compute, commit, push, generated-artifact staging, or Goal
021 work was performed.
