# Goal: First Response-Only Observation Layer

## Objective

Create the first synthetic response-only observation layer over the current
default `synth-small` predator-truth benchmark, with disk-first inspection and
a lightweight recoverability smoke test, so the project can move from latent
truth generation toward noisy-data parameter recovery.

## Why This Matters

Goals 001 and 002 established that the deterministic predator-truth benchmark
is structurally coherent and good enough for a first observation-layer target.
The next research step is to define what the data analyst actually sees:
noisy, effort-conditioned prey-response observations, not direct predator
arrival or predator-pressure truth.

This goal should create the first observable synthetic dataset and enough
diagnostics to decide whether it carries recoverable signal before ABC/POM
inference is attempted.

## Operating Mode

Scientific workflow plus implementation sprint.

## Scope

In scope:

- add a repo-local spec for the first response-only observation layer
- implement deterministic, seed-controlled observation generation
- add disk-first observation inspection
- add a lightweight recoverability smoke test using simple summaries
- produce CSV/JSON/Markdown review artefacts
- add focused tests for reproducibility, schema, inspection failures, and
  smoke-test metrics
- update project docs, report log, and this goal log

Out of scope:

- ABC, POM, MCMC, or full parameter fitting
- changing deterministic predator-truth defaults
- direct observation of predator arrival or predator pressure as analyst data
- large simulation ensembles or remote/HPC execution
- committing or pushing changes

## Read First

- `/Users/bwbrook/papers/spatext/AGENTS.md` - repo operating rules and quality lane
- `/Users/bwbrook/papers/spatext/README.md` - current entry points
- `/Users/bwbrook/papers/spatext/spec/problem_statement.md` - response-only inference problem
- `/Users/bwbrook/papers/spatext/spec/theory.md` - model notation
- `/Users/bwbrook/papers/spatext/spec/synth_small_predator_truth.md` - truth benchmark
- `/Users/bwbrook/papers/spatext/spec/synth_small_predator_truth_inspection.md` - truth inspection
- `/Users/bwbrook/papers/spatext/spec/synth_small_predator_truth_sensitivity.md` - readiness criteria
- `/Users/bwbrook/papers/spatext/docs/goals/001-predator-truth-inspection/Log.md` - inspection run log
- `/Users/bwbrook/papers/spatext/docs/goals/002-deterministic-benchmark-sensitivity/Log.md` - sensitivity run log
- `/Users/bwbrook/papers/spatext/artifacts/synth_small_predator_truth_sensitivity/decision_memo.md` - current readiness decision
- `/Users/bwbrook/papers/spatext/src/spatext/synth/small/predator.py` - latent truth generator
- `/Users/bwbrook/papers/spatext/src/spatext/synth/small/predator_inspect.py` - inspection pattern
- `/Users/bwbrook/papers/spatext/src/spatext/synth/small/sensitivity.py` - decision-package pattern

## Starting State Checks

- Confirm branch, remote, tracked modifications, and untracked files with
  `git status --short --branch`.
- Treat the existing dirty Goal 001 and Goal 002 work as project state to
  preserve.
- Confirm `uv sync --all-groups` succeeds before implementation.
- Regenerate or verify these upstream artefacts before building observations:
  - `artifacts/synth_small_predator_truth/`
  - `artifacts/synth_small_predator_truth/inspection/`
  - `artifacts/synth_small_predator_truth_sensitivity/`

## Required Work

- Write `spec/synth_small_observations.md` before implementation.
- Add an observation module under `src/spatext/synth/small/`.
- Add one or more scripts for building and inspecting the observation bundle.
  Suggested names:
  - `scripts/build_synth_small_observations.py`
  - `scripts/inspect_synth_small_observations.py`
- Use a fixed default random seed and record it in the emitted config.
- Define explicit effort and detection assumptions. A reasonable first design
  is repeated site visits over selected times, where detection probability is a
  monotone function of latent prey abundance and survey effort.
- Keep analyst-facing observations response-only:
  - observed prey detections/counts or detection/non-detection summaries are in
    the main observation table
  - predator arrival, predator pressure, and true extirpation may appear only
    in clearly labelled truth/evaluation tables, not as observed analyst data
- Emit outputs under `artifacts/synth_small_observations/`, including at least:
  - `observation_config.json`
  - `truth_reference.json`
  - `sites.csv`
  - `visits.csv`
  - `observations.csv`
  - `inspection/verification.json`
  - `inspection/observation_summary.csv`
  - `inspection/recoverability_smoke.json`
  - `inspection/report.md`
- The inspection report should summarize:
  - sampling design
  - detection/effort assumptions
  - temporal coverage relative to driver arrival and extirpation
  - missingness or sampling coverage
  - observed response patterns by time and region
  - whether analyst-facing data excludes predator truth
- The recoverability smoke test should be deliberately simple. It should not
  fit the model. It should show whether the noisy observations contain basic
  signal about the latent truth, for example by:
  - comparing observed response summaries before and after driver arrival
  - checking whether cells that truly extirpate have lower late detections than
    survivors
  - computing a simple classification or ranking diagnostic for extirpated
    versus surviving cells
  - reporting limitations clearly
- Add focused tests for:
  - reproducible observation generation under the default seed
  - required output files and schemas
  - inspection failure on malformed/missing observation bundles
  - analyst-facing tables excluding predator truth columns
  - recoverability smoke metrics being finite and present
- Update `README.md` if user-facing commands are added.
- Update `AGENTS.md` if a new spec becomes authoritative.
- Update `spec/report_log.md`.
- Update this goal's `Log.md`.

## Validation Gates

The goal is not complete until these pass or a blocker is clearly logged:

- `uv sync --all-groups`
- `uv run python scripts/build_synth_small_predator_truth.py`
- `uv run python scripts/inspect_synth_small_predator_truth.py`
- `uv run python scripts/run_synth_small_predator_truth_sensitivity.py`
- `uv run python scripts/build_synth_small_observations.py`
- `uv run python scripts/inspect_synth_small_observations.py`
- confirm observation inspection `verification.json` records a pass state
- confirm `recoverability_smoke.json` exists and contains finite smoke metrics
- confirm `inspection/report.md` exists and is non-empty
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`

If formatting changes are required, run the formatter, then rerun the check.

## Deliverables

- `spec/synth_small_observations.md`
- observation and inspection implementation under `src/spatext/synth/small/`
- scripts for building and inspecting observations
- tests for observation generation and inspection
- observation outputs under `artifacts/synth_small_observations/`
- updated `README.md` and `AGENTS.md` if needed
- updated `spec/report_log.md`
- updated `Log.md`
- final response with changed files, validation, artefact paths,
  recoverability-smoke result, residual risks, and recommended post-pilot
  integration step

## Checkpoint Rules

Checkpoint in `Log.md` when:

- the observation spec is drafted
- the first observation bundle is generated
- the inspection report is generated
- recoverability smoke metrics are produced
- tests pass for the observation layer
- final validation is complete

## Pause Or Escalate

Pause and ask Barry before:

- changing deterministic predator-truth defaults
- exposing predator arrival or pressure as analyst-observed data
- introducing full inference or fitting
- adding heavy dependencies
- expanding to large simulation ensembles or remote compute
- deleting existing Goal 001 or Goal 002 outputs or goal-management files
- committing or pushing changes

## Stop Conditions

Stop when one of these is true:

- the observation layer, inspection, smoke test, docs, logs, and artefacts are
  produced and validation passes
- the observation design exposes a scientific ambiguity that cannot be resolved
  without Barry's judgement
- the task would require entering out-of-scope inference or recovery machinery

## Final Response Requirements

Report:

- what changed or was produced
- where the observation and inspection artefacts live
- exact validation commands and outcomes
- observation design summary
- recoverability smoke-test result and limits
- tracked/untracked Git status, without committing or pushing
- recommended next step after this three-goal pilot
