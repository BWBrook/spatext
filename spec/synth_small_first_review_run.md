# `synth-small` First Review Run

## Purpose

This document specifies the next immediate task for `spat` after completion of
the `synth-small` baseline and inspection implementations.

The goal is no longer to build new machinery. The goal is to execute the
current machinery end to end and produce the first canonical review bundle for
human inspection.

In practical terms, this means:

1. generate a fresh `synth-small` baseline artifact bundle,
2. run the disk-first inspection tooling on that bundle,
3. stage the resulting artifacts in a stable location,
4. report back the exact path so the user can perform the first manual
   inspection pass.

## Why this comes next

This is the right next step because the code path is now mature enough for a
first real audit by eye.

We already have:

- a baseline generator,
- a disk-first inspection workflow,
- static figures,
- verification checks,
- a Markdown inspection report.

Before adding more scientific complexity, we should now produce one canonical
reviewable bundle and inspect what the current implementation actually makes.

## Scope

This task is an execution-and-staging task, not a modelling-extension task.

It includes:

- one fresh baseline build,
- one fresh inspection pass,
- stable placement of the resulting artifacts,
- reporting the run outcome and location.

It does **not** include:

- changes to the scientific model,
- new features,
- parameter retuning,
- new plots beyond what already exists,
- speculative refactoring.

Code changes should only be made if the run exposes a real blocker.

## Canonical run target

The first review bundle should be written to a stable, repo-local path:

`artifacts/synth_small_first_review`

Within that directory, the existing build and inspection tooling should create
the baseline bundle and the nested inspection outputs.

Expected structure after a successful run:

```text
artifacts/synth_small_first_review/
├── domain.json
├── config.json
├── diagnostics.json
├── summary.json
├── cells.csv
├── edges.csv
├── surfaces.npz
├── suitability.svg
├── carrying_capacity.svg
├── equilibrium_abundance.svg
├── equilibrium_occupancy.svg
└── inspection/
    ├── verification.json
    ├── parameters.csv
    ├── surface_summary.csv
    └── report.md
```

## Run protocol

`spat` should use the existing repository entrypoints rather than calling
package internals directly.

Recommended command sequence:

```bash
uv sync --all-groups
uv run python scripts/build_synth_small_baseline.py \
  --output-dir artifacts/synth_small_first_review
uv run python scripts/inspect_synth_small_baseline.py \
  --artifact-dir artifacts/synth_small_first_review
```

If the target output directory already exists, `spat` should avoid mixing old
and new outputs. The preferred behavior is:

- remove only the previously generated review directory if it is clearly a
  generated artifact directory for this task, then
- rebuild it from scratch.

If `spat` judges that removal is risky or ambiguous, it should instead choose a
clean equivalent path and record that exact path in `spec/report_log.md`.

## Output hygiene

The generated review bundle is a runtime artifact, not source code.

So:

- the run outputs should **not** be committed,
- the worktree should remain interpretable after the run,
- if writing into repo-local `artifacts/` exposes an obvious ignore-gap,
  `spat` may make the smallest reasonable hygiene adjustment to avoid clutter.

That adjustment should be minimal and directly justified by the execution task,
not treated as a chance for general repo cleanup.

## Required success conditions

The first review run is successful only if all of the following are true:

- the baseline build command completes successfully,
- the inspection command completes successfully,
- `artifacts/synth_small_first_review/inspection/verification.json` exists,
- that verification payload reports `"passed": true`,
- `artifacts/synth_small_first_review/inspection/report.md` exists,
- the four baseline SVG figures exist and are linked from the inspection
  report,
- `parameters.csv` and `surface_summary.csv` exist and are non-empty.

## Failure handling

If the inspection verification fails, `spat` should **not** silently paper over
the problem.

In that case:

- preserve the failed bundle,
- record the failure clearly in `spec/report_log.md`,
- summarize which checks failed,
- stop before making speculative scientific or implementation changes unless a
  clearly justified blocker fix is required.

The point of this run is to expose the current state honestly.

## What `spat` should report back

After the run, `spat` should add a new entry to `spec/report_log.md` that
records:

- the exact commands executed,
- the exact output path,
- whether the verification passed,
- any hygiene adjustment made for generated artifacts,
- whether any blocker or warning was encountered.

The report-log entry should make it easy for the user to locate the bundle
without searching the filesystem.

## Acceptance criteria

This task is complete when:

- a single canonical `synth-small` review bundle exists on disk,
- its inspection report is ready for human reading,
- its verification record passes,
- its location is explicitly recorded in `spec/report_log.md`,
- no unnecessary model changes were made just to "improve" the output.

## Immediate next use

Once this run is complete, the next conversation can focus on the substance of
the artifacts themselves:

- whether the suitability surface looks sensible,
- whether the carrying-capacity mapping is doing what we expect,
- whether the equilibrium abundance pattern looks biologically and numerically
  plausible,
- whether the occupancy threshold is sensible for later observation work,
- and what should be changed before adding predator dynamics.
