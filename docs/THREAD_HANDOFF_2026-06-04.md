# SpatExt Thread Handoff

Date: 2026-06-04

Prepared by: `mink`

This note is for the next agent taking over this repository after the current
thread is closed and archived. It is intentionally a handoff note only, not a
new work plan or science goal.

## Current Repository State

Repository:

```text
/Users/bwbrook/papers/spatext
https://github.com/BWBrook/spatext.git
```

Current published checkpoint:

```text
4b9f6f6 feat: add synth-small extirpation reconstruction baseline
```

At the time this handoff was written, `main` was aligned with `origin/main`
before this note was added. The only expected local change after this handoff is
this file.

The repo is in early synthetic-methods buildout. The active scientific spine is
response-only spatiotemporal extinction inference, with synthetic validation as
a hard gate before real mink-water-vole work.

Read first:

```text
AGENTS.md
README.md
spec/problem_statement.md
spec/theory.md
spec/report_log.md
docs/goals/005-response-only-extirpation-reconstruction/Log.md
```

The older `spec/devbox_handover.md` is useful historical context for the WSL to
Mac mini move, but it is stale with respect to current repository state. Prefer
the live Git history, `spec/report_log.md`, and the goal logs.

## Completed Goal Checkpoints

Goals 001-003 built the first synth-small pilot:

- deterministic predator-response hidden truth,
- predator-truth inspection,
- deterministic sensitivity/readiness diagnostics,
- first response-only observation bundle,
- observation inspection and recoverability smoke diagnostics.

Goal 004 consolidated that three-goal pilot and published it on `main`.

Goal 005 added the first response-only observed-extirpation reconstruction
baseline. It is now published at commit `4b9f6f6`.

Goal 005 outputs and implementation:

```text
spec/synth_small_extirpation_reconstruction.md
src/spatext/synth/small/reconstruction.py
scripts/reconstruct_synth_small_extirpation.py
scripts/inspect_synth_small_extirpation_reconstruction.py
tests/test_synth_small_extirpation_reconstruction.py
docs/goals/005-response-only-extirpation-reconstruction/
```

Generated artifacts are not committed. Rebuild them locally when needed under:

```text
artifacts/synth_small_extirpation_reconstruction/
```

## Goal 005 Scientific Summary

Goal 005 estimates a response-only `T_X^obs` proxy from analyst-facing
observation tables:

```text
artifacts/synth_small_observations/sites.csv
artifacts/synth_small_observations/visits.csv
artifacts/synth_small_observations/observations.csv
artifacts/synth_small_observations/observation_config.json
```

The reconstruction rule is intentionally conservative:

1. Aggregate observations by site and survey time.
2. Find the last observed detection time.
3. Look for a final sustained zero-detection tail after that detection.
4. If at least two surveyed times with positive effort and zero detections
   occur in that final tail, classify the site as observed-extirpated by end
   and set `observed_extirpation_time` to the first time in the tail.
5. Use hidden truth only after reconstruction, and only for evaluation metrics.

The response-only CSV boundary was explicitly checked. `site_reconstruction.csv`
must not contain hidden-truth fields such as:

```text
driver_arrival
predator_pressure
true_extirpation
extirpation_lag
extirpated_by_end
initial_abundance
final_abundance
```

Final default Goal 005 metrics:

```text
TP / FP / TN / FN: 151 / 0 / 373 / 101
sensitivity: 0.5992063492063492
specificity: 1.0
precision: 1.0
temporal error count: 151
temporal error mean / median / MAE: 7.099337748344371 / 7.0 / 7.642384105960265
```

The Goal 005 report classified the baseline as ready for the next step, but only
with cautionary controls. Spatial heterogeneity remains important: sensitivity
is strong in west/front-band areas and weak in eastern areas, so the next layer
must not overstate recoverability.

## Validation Baseline

The repo uses `uv` as the Python authority. Prefer `uv run python` over bare
`python`; a plain `python` command may not exist on this host.

For substantial work, the expected validation lane is:

```bash
uv sync --all-groups
uv run python scripts/build_synth_small_predator_truth.py
uv run python scripts/inspect_synth_small_predator_truth.py
uv run python scripts/build_synth_small_observations.py
uv run python scripts/inspect_synth_small_observations.py
uv run python scripts/reconstruct_synth_small_extirpation.py
uv run python scripts/inspect_synth_small_extirpation_reconstruction.py
uv run pytest tests/test_synth_small_extirpation_reconstruction.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Publication checkpoint for Goal 005 also passed:

```bash
uv run pre-commit run --all-files
git push origin main
```

The full suite at publication time had 48 passing tests and coverage above the
configured 90% gate.

## Thread And Project Relationships

This repository is the action repo. It is not the orchestration/control-plane
repo.

Relevant locations:

```text
/Users/bwbrook/papers/spatext          # action repo
/Users/bwbrook/work/goal_composer      # supervisor/orchestration filing system
/Users/bwbrook/work/nectar             # remote-compute control-plane repo
```

During the previous lane, the practical hierarchy was:

```text
Barry -> Research Project Manager -> orchestrator -> mink/action agent
```

The user has now flagged a wholesale migration and re-organisation of
orchestration locations and management. Treat any older orchestration paths,
thread ids, or project-hierarchy notes as potentially in transition. Before
acting on new multi-agent or remote-compute instructions, re-orient from the
current live files and the new instructions.

For remote compute, use `/Users/bwbrook/work/nectar` as the source of truth.
No Goal 005 work used remote compute, and there is no current reason to move
this repo off the Mac mini for ordinary validation.

## Risks And Caveats

- Do not start ABC, POM, fitting, parameter inference, real-data analysis, or
  remote compute without a new explicit goal packet or supervisor instruction.
- Keep hidden truth out of response-only reconstruction outputs and decisions.
  Hidden truth belongs only in clearly labelled evaluation diagnostics.
- Generated artifacts and caches should remain unstaged:
  `artifacts/`, `dist/`, `.coverage`, `.hypothesis/`, `.mypy_cache/`,
  `.pytest_cache/`, `.ruff_cache/`, `.venv/`, and `__pycache__/`.
- `spec/devbox_handover.md` contains old WSL-to-Mac context. It should not be
  treated as the current head-state document.
- `README.md` may lag the newest Goal 005 module state. The authoritative
  current record is `spec/report_log.md` plus the Goal 005 packet.
- The current `T_X^obs` rule is deliberately simple. Its high precision is not
  proof of identifiability; the false-negative rate and spatial bias are part
  of the scientific result.

## Recommended Next Actions

For the next thread:

1. Start with `git status --short --branch` and `git log --oneline --decorate
   --max-count=6`.
2. Read `AGENTS.md`, `spec/report_log.md`, and the latest goal packet.
3. Confirm the new orchestration-management location before relying on old
   `goal_composer` assumptions.
4. If asked for science work, insist on a bounded repo-local goal packet under
   `docs/goals/`.
5. The next science layer should remain cautious: design the response-only
   ABC/POM or inference-screening layer around the existing `T_X^obs` baseline,
   with explicit uncertainty, failure-mode, and low-information controls.
