# Log

## Current Status

Drafted by supervisor on 2026-05-30.

Execution started by `spatext_agent` on 2026-05-30. Existing Goal 001 and
Goal 002 dirty work is being preserved; no commit or push will be made.

## Why This Goal

Goal 002 supports moving forward with the current default deterministic
predator-truth benchmark. The next useful research artefact is therefore the
first response-only observation layer: what an analyst would actually observe,
with predator truth held back for evaluation.

This final pilot goal should stress the orchestrator workflow more seriously:
it spans scientific design, data generation, disk-first inspection, and a small
recoverability smoke test, while still keeping full inference out of scope.

## Checkpoints

- [x] Observation spec drafted
- [x] First observation bundle generated
- [x] Inspection report generated
- [x] Recoverability smoke metrics produced
- [x] Observation-layer tests passing
- [x] Final validation complete

## Work Log

### 2026-05-30

- Read `Goal.md`, `Plan.md`, `Runbook.md`, and this `Log.md` in the requested
  order.
- Read repo-local `AGENTS.md`, README, problem/theory specs, predator-truth
  and inspection specs, predator-truth sensitivity spec, Goal 001/002 logs,
  and the current sensitivity decision memo.
- Confirmed starting state with `git status --short --branch`: `main` tracks
  `origin/main`; existing Goal 001/002 tracked modifications and untracked
  files remain present and must be preserved.
- Ran `uv sync --all-groups`; it completed successfully.
- Refreshed upstream artifacts with
  `uv run python scripts/build_synth_small_predator_truth.py`,
  `uv run python scripts/inspect_synth_small_predator_truth.py`, and
  `uv run python scripts/run_synth_small_predator_truth_sensitivity.py`.
  All completed successfully, with the sensitivity run still reporting the
  default candidate as `observation_ready`.
- Drafted `spec/synth_small_observations.md`, defining the first response-only
  observation design, analyst-facing column boundaries, evaluation-truth
  separation, output contract, inspection checks, and recoverability smoke
  metrics.
- Added focused observation-layer tests and confirmed the initial red state:
  `uv run pytest tests/test_synth_small_observations.py --no-cov` failed
  because the observation API did not yet exist.
- Implemented the observation generator, disk-first inspection layer, build
  script, and inspection script.
- Ran focused observation-layer tests with
  `uv run pytest tests/test_synth_small_observations.py --no-cov`; all `6`
  tests passed.
- Ran `uv run python scripts/build_synth_small_observations.py`; it wrote the
  root observation bundle under `artifacts/synth_small_observations/` with
  `10,288` visits/observations using seed `20260530`.
- Ran `uv run python scripts/inspect_synth_small_observations.py`; it wrote
  the inspection bundle under `artifacts/synth_small_observations/inspection/`
  and reported both verification and smoke-test status as passed.
- Current recoverability smoke result:
  pre-driver detection rate `0.8576294277929155`,
  post-driver detection rate `0.6599564744287268`,
  late extirpated detection rate `0.227`,
  late surviving detection rate `0.7910974499089254`, and
  late-detection AUC `0.8939508196721312`.
- Ran the final validation lane:
  `uv sync --all-groups`,
  `uv run python scripts/build_synth_small_predator_truth.py`,
  `uv run python scripts/inspect_synth_small_predator_truth.py`,
  `uv run python scripts/run_synth_small_predator_truth_sensitivity.py`,
  `uv run python scripts/build_synth_small_observations.py`,
  `uv run python scripts/inspect_synth_small_observations.py`,
  observation verification/smoke/report existence checks,
  `uv run ruff format --check .`, `uv run ruff check .`,
  `uv run mypy src tests`, `uv run pytest`, `uv build`, and
  `uv run pre-commit run --files $(git ls-files -m -o --exclude-standard)`.
- Final full test result: `42` tests passed with total coverage `92.47%`.
- Build outputs were created at `dist/spatext-0.1.0.tar.gz` and
  `dist/spatext-0.1.0-py3-none-any.whl`.
