# Goal: Consolidate Three-Goal Synth-Small Pilot

## Objective

Consolidate the completed Goals 001-003 synth-small pilot into a clean,
validated, pushed `main` branch, without adding new science functionality.

## Why This Matters

The project now has a coherent early synthetic workflow: predator-truth
inspection, deterministic sensitivity/readiness, and a first response-only
observation layer with recoverability smoke diagnostics. That work is still
large uncommitted local state. Before adding the next science layer, the repo
needs a clean publication checkpoint that Barry and future agents can trust.

## Operating Mode

Evidence packaging validation and publication.

## Review Surface

The supervisor should review:

- final commit SHA and pushed branch state
- exact staged/committed path list
- validation command outcomes
- `docs/goals/004-consolidate-three-goal-pilot/Log.md`
- any residual untracked or ignored state

## Scope

In scope:

- inspect the full dirty worktree from Goals 001-003
- remove or ignore incidental `.DS_Store` host noise
- add `.DS_Store` to `.gitignore` if it is not already ignored
- re-run the current validation lane
- stage exact accepted paths only
- create one bundled commit after validation passes
- push `main` to `origin`
- update this goal log and `spec/report_log.md` with publication evidence

Out of scope:

- new science functionality
- extirpation reconstruction, ABC, POM, fitting, or inference
- changing scientific defaults, observation design, readiness criteria, or
  predator-truth parameters
- staging ignored artefacts under `artifacts/`, `dist/`, caches, or `.venv/`
- force-pushing, rebasing, amending pushed commits, or deleting prior work

## Read First

- `AGENTS.md` - repo-local authority and publication policy
- `README.md` - public orientation and implemented module list
- `spec/report_log.md` - operational history
- `docs/goals/001-predator-truth-inspection/Log.md` - Goal 001 evidence
- `docs/goals/002-deterministic-benchmark-sensitivity/Log.md` - Goal 002 evidence
- `docs/goals/003-first-response-observation-layer/Log.md` - Goal 003 evidence
- `artifacts/synth_small_predator_truth/inspection/report.md` - ignored review artefact
- `artifacts/synth_small_predator_truth_sensitivity/decision_memo.md` - ignored decision artefact
- `artifacts/synth_small_observations/inspection/report.md` - ignored observation review artefact

## Starting State Checks

Start from `/Users/bwbrook/papers/spatext`.

Confirm:

- `git status --short --branch` shows `main...origin/main`
- modified tracked files are expected Goal 001-003 documentation/API updates
- untracked files are expected Goal 001-003 goal docs, specs, scripts, modules,
  and tests, plus possible incidental `.DS_Store`
- ignored generated outputs remain ignored

Treat the existing dirty state as project state. Do not revert it.

## Git And Publication Policy

Barry has approved this consolidation goal to commit and push after validation
passes and exact staging is confirmed.

Use one bundled commit on `main` with this message unless a clear reason appears
to adjust it:

```text
feat: add synth-small observation readiness workflow
```

Push with a normal push:

```bash
git push origin main
```

Do not force-push. If push is rejected, fetch and inspect the incoming state,
then stop and report.

## Data, Compute, And Staging Policy

- This is local Mac mini validation and publication work.
- Do not stage generated artefacts from `artifacts/`.
- Do not stage `dist/`, `.coverage`, `.hypothesis/`, `.mypy_cache/`,
  `.pytest_cache/`, `.ruff_cache/`, `.venv/`, `__pycache__/`, or `.DS_Store`.
- It is acceptable to add `.DS_Store` to `.gitignore`.
- Natural parallelisation is not relevant for this packaging goal.

## Required Work

- Audit the dirty worktree and classify paths as:
  - accepted project source/docs/tests/goal logs
  - ignored generated artefacts
  - incidental host noise
  - unexpected or risky paths
- Add `.DS_Store` to `.gitignore` if missing, and remove the untracked local
  `.DS_Store` from the working tree.
- Re-run the validation lane from current files and ignored artefacts.
- Stage exact accepted paths only.
- Inspect the staged diff and staged path list before committing.
- Commit and push only after validation passes and the staged set is correct.
- Update this `Log.md` with commands, validation results, staged paths, commit
  SHA, push result, residual risks, and final git status.
- Update `spec/report_log.md` with a short Interaction 24 publication entry.

The expected accepted path set is:

- `.gitignore`
- `AGENTS.md`
- `README.md`
- `spec/report_log.md`
- `spec/synth_small_predator_truth_inspection.md`
- `spec/synth_small_predator_truth_sensitivity.md`
- `spec/synth_small_observations.md`
- `src/spatext/synth/small/__init__.py`
- `src/spatext/synth/small/predator_inspect.py`
- `src/spatext/synth/small/sensitivity.py`
- `src/spatext/synth/small/observations.py`
- `scripts/inspect_synth_small_predator_truth.py`
- `scripts/run_synth_small_predator_truth_sensitivity.py`
- `scripts/build_synth_small_observations.py`
- `scripts/inspect_synth_small_observations.py`
- `tests/test_synth_small_predator_truth_inspection.py`
- `tests/test_synth_small_predator_truth_sensitivity.py`
- `tests/test_synth_small_observations.py`
- `docs/goals/001-predator-truth-inspection/`
- `docs/goals/002-deterministic-benchmark-sensitivity/`
- `docs/goals/003-first-response-observation-layer/`
- `docs/goals/004-consolidate-three-goal-pilot/`

## Validation Gates

The goal is not complete until all of these pass:

```bash
uv sync --all-groups
uv run python scripts/build_synth_small_predator_truth.py
uv run python scripts/inspect_synth_small_predator_truth.py
uv run python scripts/run_synth_small_predator_truth_sensitivity.py
uv run python scripts/build_synth_small_observations.py
uv run python scripts/inspect_synth_small_observations.py
jq '{passed}' artifacts/synth_small_predator_truth/inspection/verification.json
jq '{recommendation: .recommendation, default_classification: .default_candidate.readiness_classification}' artifacts/synth_small_predator_truth_sensitivity/readiness.json
jq '{passed}' artifacts/synth_small_observations/inspection/verification.json
jq '{passed, finite_metrics: ([.metrics[] | type == "number"] | all)}' artifacts/synth_small_observations/inspection/recoverability_smoke.json
test -s artifacts/synth_small_observations/inspection/report.md
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run pre-commit run --all-files
```

After staging, also run:

```bash
git diff --cached --name-only
git diff --cached --stat
```

This is evidence-packaging validation plus publication validation.

## Deliverables

- updated `docs/goals/004-consolidate-three-goal-pilot/Log.md`
- updated `spec/report_log.md`
- `.gitignore` updated for `.DS_Store` if needed
- one pushed commit on `main`
- final response with:
  - validation summary
  - exact staged/committed path categories
  - commit SHA and push result
  - final tracked/untracked/ignored git status
  - residual risks
  - recommended next science goal

## Decision Authority

You may decide:

- how to phrase the short `spec/report_log.md` publication entry
- whether `.DS_Store` needs a `.gitignore` entry
- how to fix narrow packaging, formatting, lint, or test failures caused by the
  accepted Goals 001-003 work

You must pause before:

- changing scientific defaults or generated-data design
- adding any new science layer
- changing public APIs beyond packaging fixes needed for validation
- staging any ignored generated artefact
- committing if validation fails
- pushing if the staged path list includes unexpected files
- resolving a push race with merge/rebase/force-push

## Checkpoint Rules

Update `Log.md` after:

- initial dirty-state audit
- validation completes
- `.DS_Store` handling is complete
- exact staging is complete
- commit is created
- push succeeds or blocks

## Pause Or Escalate

Pause and report if:

- validation fails for a reason that is not a narrow packaging/hygiene issue
- unexpected dirty files appear outside the accepted path set
- staged diff includes generated artefacts or host noise
- the push is rejected
- committing would require changing scientific assumptions

## Stop Conditions

Stop when one of these is true:

- validation passes, exact accepted paths are committed, `main` is pushed, and
  final status is reported
- validation or push blocks and the blocker is recorded
- the task would require new science or out-of-scope inference work

## Final Response Requirements

Report:

- what was committed and pushed
- commit SHA and branch/remote state
- validation commands and outcomes
- staged/committed path categories
- remaining untracked or ignored files
- whether generated artefacts remain ignored
- residual risks
- recommended next science goal: response-only `T_X^obs` reconstruction and
  hidden-truth comparison before ABC/POM
