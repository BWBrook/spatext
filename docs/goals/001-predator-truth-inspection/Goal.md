# Goal: Predator Truth Inspection Layer

## Objective

Create a disk-first inspection and review layer for the `synth-small`
deterministic predator-response truth bundle, so the project has auditable
evidence about the current generating model before adding noisy observation or
parameter recovery.

## Why This Matters

The project is moving from generating known synthetic truth toward recovering
model parameters from noisy response-only data. Before adding that next layer,
we need a compact, reproducible way to inspect whether the deterministic
predator-response truth bundle is scientifically coherent and internally
consistent.

## Operating Mode

Scientific workflow plus implementation sprint.

## Scope

In scope:

- add a repo-local spec for predator-truth inspection
- implement a disk-first predator-truth inspection library/API
- add a command-line script for the inspection workflow
- generate machine-readable summaries and a human-readable review report
- add tests for valid, missing, corrupted, and inconsistent bundles
- update project logs and docs needed for repeatability

Out of scope:

- noisy observation model
- parameter recovery or fitting
- stochastic predator/prey model changes
- broad redesign of the deterministic predator truth generator
- remote/HPC execution
- committing or pushing changes unless Barry explicitly authorises it

## Read First

- `/Users/bwbrook/papers/spatext/AGENTS.md` - repo operating rules and quality lane
- `/Users/bwbrook/papers/spatext/README.md` - current implemented entry points
- `/Users/bwbrook/papers/spatext/spec/problem_statement.md` - scientific problem
- `/Users/bwbrook/papers/spatext/spec/theory.md` - model layers and notation
- `/Users/bwbrook/papers/spatext/spec/synth_small_predator_truth.md` - current predator-truth contract
- `/Users/bwbrook/papers/spatext/spec/report_log.md` - current project history
- `/Users/bwbrook/papers/spatext/src/spatext/synth/small/predator.py` - truth generation
- `/Users/bwbrook/papers/spatext/src/spatext/synth/small/inspect.py` - baseline inspection pattern
- `/Users/bwbrook/papers/spatext/tests/test_synth_small_predator_truth.py` - existing truth tests
- `/Users/bwbrook/papers/spatext/tests/test_synth_small_inspection.py` - existing inspection tests

## Starting State Checks

- Confirm branch, remote, and dirty state with `git status --short --branch`.
- Treat the existing modified `spec/report_log.md`, if still present, as prior
  project state rather than something to revert.
- Confirm `uv sync --all-groups` succeeds before relying on the environment.
- Build or refresh the predator-truth artefact if the inspection target is
  missing or stale.

## Required Work

- Write `spec/synth_small_predator_truth_inspection.md` before implementation.
- Add an inspection module under `src/spatext/synth/small/`, following existing
  style and keeping the code disk-first and testable.
- Add `scripts/inspect_synth_small_predator_truth.py`.
- Write inspection outputs under
  `artifacts/synth_small_predator_truth/inspection/`.
- Include at least:
  - machine-readable verification status
  - parameter summary
  - surface/grid summary
  - trajectory and extirpation summary
  - human-readable `report.md`
- Verify or report scientifically relevant invariants, including:
  - expected inputs and metadata are present
  - `TP`/driver arrival values are finite and aligned to the baseline grid
  - predator-pressure and prey trajectories are internally consistent
  - `TX_true` and extirpation lags are finite where expected
  - no extirpation precedes predator arrival unless explicitly justified by
    the model/spec
  - vulnerability patterns are summarized clearly enough for Barry to review
- Add focused tests for successful inspection and important failure modes.
- Update `README.md` if a new user-facing command is added.
- Update `spec/report_log.md`.
- Update this goal's `Log.md`.

## Validation Gates

The goal is not complete until these pass or a blocker is clearly logged:

- `uv sync --all-groups`
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `uv run python scripts/build_synth_small_predator_truth.py`
- `uv run python scripts/inspect_synth_small_predator_truth.py`
- confirm the inspection `verification` output records a pass state
- confirm the inspection `report.md` exists and is non-empty

If formatting changes are required, run the formatter, then rerun the check.

## Deliverables

- `spec/synth_small_predator_truth_inspection.md`
- implementation module under `src/spatext/synth/small/`
- `scripts/inspect_synth_small_predator_truth.py`
- tests for the new inspection layer
- inspection outputs under
  `artifacts/synth_small_predator_truth/inspection/`
- updated `README.md` if needed
- updated `spec/report_log.md`
- updated `Log.md`
- final response with changed files, validation, artefact paths, residual
  risks, and recommended next goal

## Checkpoint Rules

Checkpoint in `Log.md` when:

- the spec is drafted
- the first inspection output bundle is generated
- tests pass for the inspection layer
- final validation is complete

## Pause Or Escalate

Pause and ask Barry before:

- changing scientific defaults or predator-truth model assumptions
- adding the noisy observation model
- starting parameter recovery/fitting
- launching remote or long-running compute
- deleting existing artefacts that are not clearly regenerated build outputs
- committing or pushing changes

## Stop Conditions

Stop when one of these is true:

- the inspection layer, tests, docs, and artefacts are produced and validation
  passes
- a real model/spec ambiguity blocks correct inspection design
- the task would require entering the out-of-scope observation or recovery
  layers

## Final Response Requirements

Report:

- what changed or was produced
- where the review artefacts live
- exact validation commands and outcomes
- any scientific warnings or interpretation limits
- dirty/clean Git status, without committing or pushing
- recommended next goal
