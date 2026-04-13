# Report Log

This file is a running operational log maintained by `spat`. It records what
was done in each interaction, what was achieved, and any notable decisions or
verification outcomes that matter for the build history of `spatext`.

## 2026-04-13

### Interaction 1: Repository initialization

#### Request

Create a new Git commit in the empty folder, create a private GitHub
repository called `spatext`, and push the initial state.

#### Actions completed

- Confirmed the working directory was an empty non-Git folder.
- Verified `gh` authentication state before attempting remote operations.
- Initialized a new Git repository on `main`.
- Created an intentional empty root commit with message `Initial commit`.
- Created the private GitHub repository `BWBrook/spatext`.
- Added `origin` and pushed `main` to GitHub.
- Verified that the remote repository existed and that visibility was
  `PRIVATE`.

#### Outcome

The repository was established locally and remotely, with `main` tracking
`origin/main` and the private GitHub repo ready for project buildout.

### Interaction 2: Scientific orientation

#### Request

Read `spec/problem_statement.md` and use it as the foundational grounding for
the mission of the repository.

#### Actions completed

- Read the full problem statement.
- Extracted and internalized the scientific spine of the project:
  response-only spatiotemporal inference for extinction/extirpation dynamics.
- Identified the two central latent surfaces:
  `TP(x)` for driver arrival and `TX(x)` for inferred extirpation timing.
- Recognized synthetic validation as a hard gate before real-data
  interpretation.
- Interpreted the mink-water-vole case study as the first substantive
  application, not the sole purpose of the repository.
- Adopted auditability, modularity, and synthetic-first validation as the key
  architectural guardrails for future implementation work.

#### Outcome

`spat` was oriented to the scientific purpose of `spatext` and aligned future
architecture decisions with the core proposition laid out in the problem
statement.

### Interaction 3: Tooling bootstrap

#### Request

Read `spec/tooling_bootstrap.md` and follow its directives to set up the
repository tooling.

#### Actions completed

- Read the full bootstrap specification and treated it as the tooling contract.
- Verified `uv` availability in the environment.
- Updated `uv` from `0.8.19` to `0.11.6` so the requested Python `3.14.4`
  interpreter channel was available.
- Installed and pinned CPython `3.14.4` in `.python-version`.
- Created the phase-0 package scaffold:
  `.gitignore`, `LICENSE`, `README.md`, `pyproject.toml`,
  `.pre-commit-config.yaml`, `src/spatext/`, `tests/`, and `scripts/`.
- Configured `uv_build`, `src/` layout, strict `mypy`, `pytest` with coverage,
  `ruff`, dependency groups, and committed lockfile authority via `uv.lock`.
- Added the minimal typed package skeleton under `src/spatext/`.
- Added a smoke test under `tests/test_smoke.py`.
- Generated `uv.lock`.
- Installed pre-commit hooks locally.
- Ran the canonical verification commands:
  `uv sync --all-groups`,
  `uv run ruff format --check .`,
  `uv run ruff check .`,
  `uv run mypy src tests`,
  `uv run pytest`,
  `uv build`,
  `uv run pre-commit run --all-files`.

#### Issue encountered and resolved

- The first pre-commit `ruff` hook revision selected was too old to accept
  `target-version = "py314"` in `pyproject.toml`.
- Resolved this by aligning both the dependency pin and the pre-commit hook to
  `ruff 0.15.10`.
- Re-ran the verification lane successfully after that adjustment.

#### Outcome

The repository now has a reproducible, single-authority Python bootstrap
aligned with the specification, and the full initial quality gate passes
cleanly under the pinned Python `3.14.4` environment.

### Interaction 4: Initial repo governance documents

#### Request

Create an initial repo-root `AGENTS.md` that can mature over time, and expand
the root `README.md` into an evolving project-orientation document.

#### Actions completed

- Created the first repo-local `AGENTS.md`.
- Established the current repo operating contract around:
  scientific authority in `spec/`,
  `uv` and `pyproject.toml` as tooling authorities,
  synthetic-first validation,
  modular design,
  auditable workflow,
  and explicit Git hygiene.
- Expanded `README.md` from a bootstrap stub into a fuller orientation
  document.
- Documented the project purpose, scientific framing, current stage, repo map,
  tooling baseline, core commands, and current operating stance.
- Recorded the user's Git preference to avoid commits and pushes unless
  explicitly requested, with bundled commits preferred over atomic ones.

#### Outcome

The repository now has an initial local governance document and a more durable
front-door README, giving future work a clearer operating context and an
explicit workflow baseline.

### Interaction 5: Bundle and publish current repo state

#### Request

Create a Git commit and push the changes completed so far.

#### Actions completed

- Prepared the current repository state for a bundled checkpoint commit.
- Included the accumulated bootstrap, specification, governance, and README
  work in one publishable snapshot.
- Created a bundled commit to lock in the current repo baseline.
- Pushed the current `main` branch to `origin`.

#### Outcome

The repository state up to this point was checkpointed in Git and published to
the remote repository as the current shared baseline.

### Interaction 6: Theory specification

#### Request

Create `spec/theory.md` as a clean mathematical statement of the modelling
theory underpinning `spatext`, using `exdyn-sandbox` as the source of the
current scientific and algorithmic structure.

#### Actions completed

- Mined `exdyn-sandbox` for the core theoretical structure across:
  process dynamics,
  driver-arrival construction,
  predation-field ramping,
  latent extirpation definitions,
  observation models,
  TX estimation,
  response-side summaries,
  screening loss,
  ABC distance,
  and synthetic validation logic.
- Wrote `spec/theory.md` as a clean theory note rather than a direct lift from
  sandbox prose.
- Made the notation explicit around:
  `T_P(x)`,
  `T_X^{true}(x)`,
  `T_X^{obs}(x)`,
  latent abundance `N_t(x)`,
  predation pressure `P_t(x)`,
  and parameter vector `theta`.
- Formalised the main mathematical layers using LaTeX:
  arrival surface and delta offsets,
  logistic predation ramp,
  local prey dynamics with Allee effects and predation mortality,
  dispersal operator,
  latent first-passage extirpation,
  observation models,
  hold-rule TX estimator,
  response-side summary vector,
  screening objective,
  unit-consistent real-data loss,
  ABC distance,
  and synthetic twin validation logic.
- Closed the document by stating the implied module decomposition for future
  `spatext` implementation work.

#### Outcome

`spatext` now has a dedicated mathematical theory document that can serve as
the scientific anchor for simulation and inference implementation, separate
from both tooling specs and the more narrative problem statement.

### Interaction 7: `synth-small` baseline-module specification

#### Request

Define the first substantive synthetic module for `spatext` as a small,
tractable baseline example whose initial goal is to construct the prey
landscape at equilibrium before predator introduction.

#### Actions completed

- Wrote `spec/synth_small_baseline.md`.
- Agreed with the suitability-first design:
  create habitat/suitability before populating the prey landscape.
- Scoped the first module to the prey-only baseline phase:
  no predator,
  no observation model,
  no TX estimation,
  no parameter recovery yet.
- Specified `synth-small` as a `25 x 25` island benchmark with a fully known
  static suitability surface and deterministic prey dynamics run to
  equilibrium.
- Recommended a square lattice for the first concrete implementation, while
  requiring the spatial backend to be graph-based and tessellation-agnostic so
  that hexes can be added later without redesigning the module stack.
- Specified the preferred boundary treatment for v1:
  no external source population,
  no wrap-around,
  and dispersal defined over valid in-domain neighbors only.
- Defined the required baseline outputs:
  domain metadata,
  suitability,
  carrying capacity,
  equilibrium abundance,
  optional occupancy,
  and convergence diagnostics.
- Added structural, dynamical, reproducibility, and visual acceptance
  criteria.

#### Outcome

`spatext` now has a concrete first-module specification that gives `spat` a
clear implementation target: build a small, auditable, equilibrium prey
baseline as the foundation for all later synthetic predator, observation, and
recovery work.

### Interaction 8: `synth-small` baseline implementation

#### Request

Implement the specification in `spec/synth_small_baseline.md`, with permission
to adjust the spec only if implementation exposed a real conflict or roadblock.

#### Actions completed

- Implemented a reusable cell-graph spatial backend in `spatext.spatial`.
- Built the `synth-small` baseline module under `spatext.synth.small` with:
  deterministic suitability generation,
  suitability-driven carrying capacity,
  prey-only equilibrium dynamics,
  graph-based dispersal on a `25 x 25` square lattice,
  convergence diagnostics,
  occupancy derivation,
  and an auditable result object.
- Added repository utility script
  `scripts/build_synth_small_baseline.py` to emit a baseline artifact bundle.
- Added artifact export for:
  domain/config/diagnostic JSON,
  cell and edge CSV files,
  compressed surface arrays,
  and SVG plots for suitability, carrying capacity, equilibrium abundance, and
  occupancy.
- Added tests covering:
  structural checks,
  dynamical acceptance checks,
  reproducibility,
  artifact emission,
  failure-on-nonconvergence,
  helper utilities,
  and graph-domain invariants.
- Added `numpy` as the first runtime dependency to support the first real
  numerical modelling kernel.

#### Implementation decisions

- Used a symmetric rook-neighbor square graph as the concrete v1 adjacency
  choice for the `25 x 25` lattice.
- Kept the spatial API graph-based so that a hex-domain variant can be added
  later without redesigning the high-level module interface.
- Emitted plots as SVG via package helpers instead of introducing a plotting
  dependency such as `matplotlib`, to keep the phase-0 runtime tool surface
  minimal while still satisfying the visual-output requirement.

#### Deviations from spec

- No substantive spec deviation was required.
- The implementation resolved unspecified details rather than changing the
  scientific contract.

#### Verification completed

- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `uv run python scripts/build_synth_small_baseline.py --output-dir /tmp/spatext-synth-small-baseline`

All checks passed, tests reached `100%` coverage for the package, and the
artifact-emission utility wrote the expected baseline bundle successfully.

#### Outcome

`spatext` now has a working Module 1 baseline implementation that produces one
clean synthetic truth object `(\mathcal{X}, S, K, N*)` for the prey-only
equilibrium state, ready to support later predator, observation, TX, and
recovery modules.

### Interaction 9: `synth-small` inspection and verification specification

#### Request

Define the next work package after baseline implementation: the first
verification and visualisation tooling for inspecting the emitted `synth-small`
artifacts.

#### Actions completed

- Wrote `spec/synth_small_inspection.md`.
- Framed the next module as an inspection layer that sits on top of the
  existing baseline artifact bundle rather than duplicating baseline
  generation.
- Required the tooling to verify artifacts by reloading them from disk, not by
  reusing a live in-memory result object.
- Specified the first mandatory human-facing outputs:
  suitability-led base map inspection,
  parameter table,
  diagnostics,
  surface summaries,
  and an overall pass/fail verification record.
- Defined the required inspection outputs under an `inspection/` subdirectory:
  `verification.json`,
  `parameters.csv`,
  `surface_summary.csv`,
  and `report.md`.
- Specified the required structural, numerical, and scientific-sanity checks
  for the baseline bundle.
- Recommended a simple scriptable Markdown-report workflow with static assets,
  rather than introducing notebooks or dashboard tooling at this stage.
- Added testing and acceptance criteria for both valid and corrupted artifact
  bundles.

#### Outcome

`spatext` now has a concrete specification for the first inspection layer on
top of the `synth-small` baseline artifacts, giving `spat` a clear next target
for human-auditable verification and visual review.

### Interaction 10: Post-implementation doc refresh and checkpoint publish

#### Request

Review and update `README.md` and/or `AGENTS.md` as needed after the
implementation run, then create a Git commit and push it.

#### Actions completed

- Updated `README.md` so the repo front door now reflects the implemented
  Module 1 baseline, its main entrypoints, and the baseline artifact command.
- Updated `AGENTS.md` so post-implementation review of `README.md` and
  `AGENTS.md` becomes an explicit part of the repo workflow.
- Preserved the user's new `report_log.md` addition and kept the interaction
  ordering chronological.
- Bundled the current implemented module, supporting specs, tests, and
  documentation into a checkpoint commit.
- Pushed the checkpoint to `origin/main`.

#### Outcome

The repository documentation now matches the implemented baseline module, and
the current state was published as the next shared checkpoint on GitHub.

### Interaction 11: `synth-small` inspection implementation

#### Request

Implement the specification in `spec/synth_small_inspection.md`.

#### Actions completed

- Implemented a new inspection layer under `spatext.synth.small.inspect`.
- Added disk-first artifact loading for the existing baseline bundle:
  required-file checks,
  JSON/CSV loading,
  NPZ surface loading,
  and typed bundle assembly.
- Implemented structural, numerical, and scientific-sanity verification for:
  shape consistency,
  graph consistency,
  suitability bounds,
  positive carrying capacity,
  valid equilibrium abundance,
  binary occupancy,
  convergence diagnostics,
  summary consistency,
  and non-degenerate benchmark structure.
- Added deterministic generation of:
  `inspection/verification.json`,
  `inspection/parameters.csv`,
  `inspection/surface_summary.csv`,
  and `inspection/report.md`.
- Rendered the Markdown inspection report with:
  overview,
  verification table,
  domain summary,
  flattened parameter table,
  diagnostics table,
  surface summary table,
  and relative links to the existing SVG figures.
- Added repository utility script
  `scripts/inspect_synth_small_baseline.py` as the CLI entrypoint for
  inspecting an on-disk baseline bundle.
- Exported the new inspection types and functions through
  `spatext.synth.small`.
- Added tests covering:
  successful inspection output generation,
  deterministic parameter-table rendering,
  missing-file failure,
  shape mismatch detection,
  out-of-bounds suitability detection,
  non-binary occupancy detection,
  and inconsistent summary detection.
- Reviewed and updated `README.md` and `AGENTS.md` so the repo front door and
  workflow guide reflect the new inspection module.

#### Implementation decisions

- Kept the inspection workflow strictly disk-first so it validates the artifact
  contract rather than a live in-memory result object.
- Interpreted "fail loudly" in a two-tier way:
  missing or unreadable required inputs raise immediately,
  while readable-but-inconsistent bundles still emit inspection outputs with a
  clear failed verification record.
- Hardened the verification path so malformed but loadable bundles do not
  crash the checker during arithmetic; instead they surface as explicit failed
  checks.

#### Deviations from spec

- No substantive spec change was required.
- The implementation clarified ambiguous failure semantics rather than
  changing the inspection contract itself.

#### Verification completed

- `uv run ruff format .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `uv run python scripts/build_synth_small_baseline.py --output-dir /tmp/...`
- `uv run python scripts/inspect_synth_small_baseline.py --artifact-dir /tmp/...`

All checks passed. The package quality lane is green, all `18` tests passed,
coverage remained above the configured threshold, the package built
successfully, and the inspection CLI successfully verified a freshly emitted
baseline bundle from disk.

#### Outcome

`spatext` now has the first reusable artifact-inspection workflow in place:
Module 1 baseline bundles can be reloaded, audited, summarized, and rendered
into a compact human-readable report without rerunning the model itself.

### Interaction 12: Publish `synth-small` inspection checkpoint

#### Request

Create a bundled Git commit for the completed inspection work and push it to
the remote repository.

#### Actions completed

- Reviewed the current worktree to confirm the pending changes were the
  expected `synth-small` inspection implementation, tests, and doc updates.
- Added the new inspection module, CLI entrypoint, test coverage, README and
  AGENTS updates, and the corresponding report-log entries to the Git index.
- Created a bundled checkpoint commit for the completed inspection milestone.
- Pushed the updated `main` branch to `origin`.

#### Outcome

The `synth-small` inspection layer and its documentation are now checkpointed
in Git and published to the remote repository as the next shared project
baseline.
