# Plan

## Milestone 1: State Audit

Expected result:

- current branch and dirty state are recorded
- accepted source/docs/tests/goal files are separated from ignored artefacts
- incidental `.DS_Store` is identified
- no unexpected project files are hidden in the dirty state

Validation:

- `git status --short --branch`
- `git ls-files -m -o --exclude-standard`
- `git status --short --ignored`

## Milestone 2: Packaging Hygiene

Expected result:

- `.DS_Store` is not stageable host noise
- `.gitignore` includes `.DS_Store` if needed
- ignored artefact policy is still intact

Validation:

- `.DS_Store` no longer appears in `git status --short`
- ignored generated outputs still appear only as ignored paths

## Milestone 3: Rebuild And Validate Evidence

Expected result:

- predator-truth, inspection, sensitivity, observation, and observation
  inspection artefacts regenerate successfully under ignored `artifacts/`
- verification JSONs and smoke metrics pass
- full Python quality gates pass

Validation:

- run every command listed in `Runbook.md`
- record key outputs in `Log.md`

## Milestone 4: Exact Staging Review

Expected result:

- only accepted source/docs/tests/goal files are staged
- generated artefacts, build products, caches, and host noise are not staged
- staged diff is understandable as one bundled pilot checkpoint

Validation:

- `git diff --cached --name-only`
- `git diff --cached --stat`
- `git status --short`

## Milestone 5: Commit And Push

Expected result:

- one bundled commit exists on `main`
- `origin/main` is updated by normal push
- final repo status is clean except ignored local artefacts/caches

Validation:

- `git commit -m "feat: add synth-small observation readiness workflow"`
- `git push origin main`
- `git rev-parse HEAD`
- `git status --short --branch`

## Milestone 6: Final Handoff

Expected result:

- this goal log records final validation, commit, push, and residual risks
- final response tells the supervisor exactly what changed and what remains
- next science goal recommendation is clear but not started

Validation:

- `Log.md` is updated
- final response includes commit SHA, validation results, git status, and next
  recommended science goal
