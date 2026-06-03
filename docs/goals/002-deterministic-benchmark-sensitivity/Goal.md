# Goal: Deterministic Benchmark Sensitivity And Observation Readiness

## Objective

Produce a deterministic sensitivity and readiness package for the
`synth-small` predator-truth benchmark, so Barry can decide whether the current
default generating model is good enough for the first noisy observation layer
or needs modest parameter tuning first.

## Why This Matters

Goal 001 verified that the current predator-truth artefact is structurally
coherent. That is necessary but not sufficient. Before adding noisy
response-only observations, the project needs evidence that the deterministic
truth benchmark has a useful extinction/survival balance, lag structure, and
vulnerability gradient over a small neighbourhood of plausible predator
parameters.

## Operating Mode

Scientific workflow plus implementation sprint.

## Scope

In scope:

- add a repo-local spec for deterministic benchmark sensitivity/readiness
- implement a small, deterministic local sensitivity sweep
- reuse the existing predator-truth and inspection APIs where practical
- produce CSV/JSON/Markdown review artefacts
- rank or classify candidate parameter sets using explicit readiness criteria
- recommend whether to keep the current default for the observation layer
- add focused tests for metric extraction, candidate classification, and report
  generation
- update project logs and goal logs

Out of scope:

- noisy observation model
- parameter recovery or fitting
- broad predator/prey model redesign
- changing default predator-truth parameters without Barry's approval
- remote/HPC execution
- committing or pushing changes

## Read First

- `/Users/bwbrook/papers/spatext/AGENTS.md` - repo operating rules and quality lane
- `/Users/bwbrook/papers/spatext/README.md` - current entry points
- `/Users/bwbrook/papers/spatext/spec/problem_statement.md` - scientific problem
- `/Users/bwbrook/papers/spatext/spec/theory.md` - model notation
- `/Users/bwbrook/papers/spatext/spec/synth_small_predator_truth.md` - deterministic truth contract
- `/Users/bwbrook/papers/spatext/spec/synth_small_predator_truth_inspection.md` - inspection contract
- `/Users/bwbrook/papers/spatext/docs/goals/001-predator-truth-inspection/Log.md` - previous action-goal log
- `/Users/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/inspection/report.md` - current default review report
- `/Users/bwbrook/papers/spatext/src/spatext/synth/small/predator.py` - truth generator
- `/Users/bwbrook/papers/spatext/src/spatext/synth/small/predator_inspect.py` - inspection implementation

## Starting State Checks

- Confirm branch, remote, tracked modifications, and untracked files with
  `git status --short --branch`.
- Treat the existing dirty state from Goal 001 as project state to preserve.
- Confirm `uv sync --all-groups` succeeds before implementation.
- Confirm the Goal 001 inspection report exists, or regenerate the default
  predator-truth bundle and inspection report.

## Required Work

- Write `spec/synth_small_predator_truth_sensitivity.md` before implementation.
- Add a sensitivity module under `src/spatext/synth/small/`.
- Add `scripts/run_synth_small_predator_truth_sensitivity.py`.
- Keep the default sweep small enough for local execution. A useful initial
  grid is roughly 12-30 candidate parameter sets around the current default,
  varying at least:
  - `predation_scale`
  - `half_saturation`
  - `ramp_duration`
- Include the current default configuration as an explicitly labelled baseline
  candidate.
- For each candidate, compute at least:
  - verification pass/fail
  - extirpated and surviving fractions
  - lag min/max/mean/std
  - low- and high-initial-abundance extirpation rates
  - west- and east-band extirpated counts
  - final-abundance mean
  - whether numerical clipping occurred
  - a compact readiness classification
- Define explicit readiness criteria in the spec and code. Suggested initial
  criteria:
  - verification passes
  - extirpated fraction is neither near-zero nor near-total
  - finite lag variation is non-trivial
  - low-initial-abundance cells are more vulnerable than high-initial-abundance
    cells
  - west-band extirpation exceeds east-band extirpation for the western-arrival
    benchmark
- Write outputs under
  `artifacts/synth_small_predator_truth_sensitivity/`, including at least:
  - `sweep_results.csv`
  - `candidate_rankings.csv`
  - `readiness.json`
  - `decision_memo.md`
- The decision memo should state whether the current default appears
  observation-ready, which candidate looks best under the stated criteria, and
  what remains a scientific judgement for Barry.
- Update `README.md` if a new user-facing command is added.
- Update `spec/report_log.md`.
- Update this goal's `Log.md`.

## Validation Gates

The goal is not complete until these pass or a blocker is clearly logged:

- `uv sync --all-groups`
- `uv run python scripts/build_synth_small_predator_truth.py`
- `uv run python scripts/inspect_synth_small_predator_truth.py`
- `uv run python scripts/run_synth_small_predator_truth_sensitivity.py`
- confirm `readiness.json` exists and includes the default-candidate
  classification
- confirm `decision_memo.md` exists and is non-empty
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`

If formatting changes are required, run the formatter, then rerun the check.

## Deliverables

- `spec/synth_small_predator_truth_sensitivity.md`
- implementation module under `src/spatext/synth/small/`
- `scripts/run_synth_small_predator_truth_sensitivity.py`
- tests for the sensitivity/readiness layer
- outputs under `artifacts/synth_small_predator_truth_sensitivity/`
- updated `README.md` if needed
- updated `spec/report_log.md`
- updated `Log.md`
- final response with changed files, validation, artefact paths, readiness
  conclusion, residual risks, and recommended Goal 003

## Checkpoint Rules

Checkpoint in `Log.md` when:

- the spec is drafted
- the first sweep output is generated
- tests pass for the sensitivity layer
- the decision memo is written
- final validation is complete

## Pause Or Escalate

Pause and ask Barry before:

- changing the default predator-truth parameters
- adding noisy observations
- implementing parameter recovery/fitting
- expanding to a large sweep that would need remote compute
- deleting existing Goal 001 outputs or goal-management files
- committing or pushing changes

## Stop Conditions

Stop when one of these is true:

- the sensitivity package, tests, docs, logs, and artefacts are produced and
  validation passes
- the current code does not expose enough configuration to run a meaningful
  local sweep without broader refactoring
- the task would require entering the out-of-scope observation or recovery
  layers

## Final Response Requirements

Report:

- what changed or was produced
- where the review artefacts live
- exact validation commands and outcomes
- current default readiness classification
- best-ranked candidate and why, if there is one
- scientific warnings or interpretation limits
- tracked/untracked Git status, without committing or pushing
- recommended Goal 003
