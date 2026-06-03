# Plan

## 1. Orient To The Clean Checkpoint

- Read `Goal.md`, `Plan.md`, `Runbook.md`, and `Log.md`.
- Read repo-local `AGENTS.md`.
- Confirm branch and worktree state.
- Confirm the Goal 004 publication commits are present.
- Do not commit or push in this goal.

## 2. Specify The Reconstruction Contract

- Add `spec/synth_small_extirpation_reconstruction.md`.
- Define:
  - response-only input files,
  - forbidden truth columns,
  - reconstruction rule,
  - output schemas,
  - evaluation-only metrics,
  - scientific limits.

## 3. Implement Response-Only Reconstruction

- Add `src/spatext/synth/small/reconstruction.py`.
- Keep response-only reconstruction separate from evaluation.
- Load `sites.csv`, `visits.csv`, and `observations.csv` from disk.
- Build per-site survey histories.
- Estimate `T_X^obs` using a simple final sustained-absence rule.
- Write deterministic reconstruction artifacts.

Implementation structure should make it hard to accidentally use hidden truth:

- response-only loader/function for analyst-facing tables,
- response-only reconstruction result,
- separate evaluation function that accepts reconstruction output plus
  `evaluation_truth.csv`.

## 4. Add CLI Entrypoints

Add scripts with conservative defaults:

- `scripts/reconstruct_synth_small_extirpation.py`
- `scripts/inspect_synth_small_extirpation_reconstruction.py`

The reconstruction command should load existing observations from disk. It may
fail loudly if the observation bundle is missing; the runbook will rebuild the
bundle first.

## 5. Add Tests

Add focused tests under:

- `tests/test_synth_small_extirpation_reconstruction.py`

Test at least:

- deterministic output under default inputs,
- required files and schemas,
- response-only output excludes forbidden truth columns,
- reconstruction handles never-detected or insufficient-history sites,
- evaluation metrics are finite where defined,
- inspection/report artifacts exist.

## 6. Update Public Surfaces

- Export the new reconstruction APIs in `src/spatext/synth/small/__init__.py`.
- Update `README.md` only if a concise command or workflow note is useful.
- Update `spec/report_log.md` with the completed interaction.

## 7. Validate

Run the full validation lane in `Runbook.md`.

If a validation failure appears, diagnose and fix only within Goal 005 scope.
Do not broaden into ABC/POM, fitting, or real-data work.

## 8. Report

Update `Log.md` with:

- files changed,
- validation results,
- key reconstruction/evaluation metrics,
- residual risks,
- recommended next step.

Stop with the worktree dirty and report to the supervisor. Do not commit or
push unless a separate supervisor instruction authorizes publication.
