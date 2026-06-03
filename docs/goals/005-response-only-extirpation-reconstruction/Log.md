# Log

## Current Status

Executed by `mink` on 2026-06-03 as a response-only reconstruction baseline run.

## Why This Goal

The observation layer now has enough signal for a first reconstruction
baseline, but the project does not yet have an observed extirpation object.

Goal 005 should create a response-only `T_X^obs` reconstruction and evaluate it
against hidden truth before any ABC/POM machinery is considered.

## Checkpoints

- [x] Starting state audited
- [x] Reconstruction spec written
- [x] Response-only reconstruction implemented
- [x] Evaluation-only comparison implemented
- [x] CLI scripts added
- [x] Focused tests passed
- [x] Full quality lane passed
- [x] `spec/report_log.md` updated
- [x] Final status reported

## Implementation Notes

- 2026-06-03: Started from clean source state (`main...origin/main`), confirmed
  Goal 004 artifacts remain published, and added
  `spec/synth_small_extirpation_reconstruction.md`.

- 2026-06-03: Implemented reconstruction module and scripts:
  `src/spatext/synth/small/reconstruction.py`,
  `scripts/reconstruct_synth_small_extirpation.py`,
  and `scripts/inspect_synth_small_extirpation_reconstruction.py`.
  Updated exports in `src/spatext/synth/small/__init__.py`.
  Added tests at `tests/test_synth_small_extirpation_reconstruction.py`.

- 2026-06-03: Executed all required Goal 005 validation steps after minor
  initial formatting/inspection fix:
  - `uv sync --all-groups`
  - `uv run python scripts/build_synth_small_predator_truth.py`
  - `uv run python scripts/inspect_synth_small_predator_truth.py`
  - `uv run python scripts/build_synth_small_observations.py`
  - `uv run python scripts/inspect_synth_small_observations.py`
  - `uv run python scripts/reconstruct_synth_small_extirpation.py`
  - `uv run python scripts/inspect_synth_small_extirpation_reconstruction.py`
  - `uv run pytest tests/test_synth_small_extirpation_reconstruction.py --no-cov`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src tests`
  - `uv run pytest`
  - `uv run uv build`

  A temporary `AttributeError` in inspection (`__dict__` on slots dataclass)
  was fixed by switching to `dataclasses.asdict` in reconstruction loading checks.

- 2026-06-03: Final reconstruction artifacts now exist under
  `artifacts/synth_small_extirpation_reconstruction/` with expected required
  payload files. Evaluation summary:
  - TP / FP / TN / FN: `151 / 0 / 373 / 101`
  - sensitivity / specificity / precision: `0.5992 / 1.0 / 1.0`
  - temporal-error count: `151`
  - temporal mean / median / MAE: `7.0993 / 7.0 / 7.6424`
  - status counts: `151 observed-extirpated, 473 not-observed-extirpated, 1 insufficient, 0 no-survey`
  - interpretation: `ready_for_next_step = true`.

## Validation Summary

- Response-only output schema and rule remain separated from hidden truth:
  no forbidden columns in `site_reconstruction.csv`.
- Full repo quality lane passed on `/Users/bwbrook/papers/spatext` after formatting
  and lint cleanup.

## Final Status

- `Final status: complete`
- `recommended next step: response-only ABC/POM design with cautionary controls`
- No remaining in-scope blockers before next science goal.

## Supervisor Notes

Keep the scientific claim modest. This goal should answer whether a simple
observed-extirpation baseline is useful enough to support the next inference
design step.

Do not allow hidden truth to leak into `site_reconstruction.csv` or any
response-only reconstruction decisions.

Do not commit or push in this goal unless the supervisor explicitly authorizes
publication after review.
