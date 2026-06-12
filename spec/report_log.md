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

### Interaction 13: `synth-small` first review-run specification

#### Request

Define the next immediate task after inspection implementation: run the
complete `synth-small` baseline-plus-inspection workflow end to end so the
user can perform the first manual inspection pass on real generated artifacts.

#### Actions completed

- Wrote `spec/synth_small_first_review_run.md`.
- Framed the next task as an execution-and-staging step rather than as new
  model development.
- Specified a canonical review-bundle target at
  `artifacts/synth_small_first_review`.
- Directed `spat` to use the existing repository CLI entrypoints for:
  environment sync,
  baseline artifact generation,
  and inspection of the generated bundle.
- Defined the required review outputs, including the nested inspection bundle
  with `verification.json`, `parameters.csv`, `surface_summary.csv`, and
  `report.md`.
- Added success conditions around a passing verification record and a clearly
  readable inspection report.
- Specified failure handling so failed verification is reported honestly rather
  than masked by speculative edits.
- Required the exact output path and run outcome to be recorded in
  `spec/report_log.md` after execution.

#### Outcome

`spatext` now has an explicit execution spec for producing the first canonical
`synth-small` review bundle, giving `spat` a clear next step before further
model expansion.

### Interaction 14: Canonical `synth-small` first review run

#### Request

Execute `spec/synth_small_first_review_run.md`: generate one canonical bundle
at `artifacts/synth_small_first_review`, run the existing inspection script
over it, require a passing `inspection/verification.json`, and record the
exact output path for the first manual review pass.

#### Actions completed

- Added the minimal artifact-hygiene rule `artifacts/` to `.gitignore` so the
  repo-local review bundle would not create avoidable worktree clutter.
- Executed the requested command sequence via the existing repository
  entrypoints:
  `uv sync --all-groups`
  `uv run python scripts/build_synth_small_baseline.py --output-dir artifacts/synth_small_first_review`
  `uv run python scripts/inspect_synth_small_baseline.py --artifact-dir artifacts/synth_small_first_review`
- Confirmed that the canonical output directory now exists at the repo-local
  path:
  `artifacts/synth_small_first_review`
- Confirmed that the inspection outputs now exist at:
  `artifacts/synth_small_first_review/inspection/verification.json`
  `artifacts/synth_small_first_review/inspection/report.md`
  `artifacts/synth_small_first_review/inspection/parameters.csv`
  `artifacts/synth_small_first_review/inspection/surface_summary.csv`
- Confirmed that the four baseline SVG figures exist:
  `suitability.svg`
  `carrying_capacity.svg`
  `equilibrium_abundance.svg`
  `equilibrium_occupancy.svg`
- Loaded the emitted `verification.json` and confirmed that it reports
  `"passed": true`.
- Confirmed that the two CSV inspection tables are non-empty and that the
  report file was written successfully.

#### Exact output paths

- Bundle directory:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_first_review`
- Inspection report:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_first_review/inspection/report.md`
- Verification record:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_first_review/inspection/verification.json`
- Suitability figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_first_review/suitability.svg`
- Carrying-capacity figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_first_review/carrying_capacity.svg`
- Equilibrium-abundance figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_first_review/equilibrium_abundance.svg`
- Equilibrium-occupancy figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_first_review/equilibrium_occupancy.svg`

#### Run outcome

- Verification passed: `true`
- Verification check count: `9`
- Blockers encountered: none
- Warnings encountered: none
- Hygiene adjustment made: added `artifacts/` to `.gitignore`

#### Outcome

The first canonical `synth-small` review bundle is now staged on disk and
ready for the user's first manual inspection pass, with a passing verification
record and direct paths recorded here for immediate access.

### Interaction 15: `synth-small` deterministic predator-truth specification

#### Request

Define the next modelling work package after the first successful baseline
review: introduce the predator onto the existing `synth-small` landscape and
build the first full deterministic driver-response truth module.

#### Actions completed

- Wrote `spec/synth_small_predator_truth.md`.
- Chose deterministic predator introduction as the next increment, explicitly
  postponing stochastic prey dynamics to a later robustness phase.
- Required the module to reuse the existing prey-only baseline as the initial
  state rather than forking baseline logic.
- Specified the predator as an exogenous generalist driver represented by:
  arrival surface `T_P(x)`,
  bounded time-varying pressure `P_t(x)`,
  and no numerical feedback from focal-prey decline onto predator spread.
- Chose a western-boundary source geometry and graph-distance arrival
  construction for the default synthetic invasion front.
- Set Type III predation mortality as the required default prey-response form,
  while keeping the broader design open to later alternatives.
- Required the module to generate the first latent true extirpation surface
  `T_X^{true}(x)` and the corresponding lag surface.
- Defined a self-contained artifact bundle including surface arrays,
  full trajectories, cell-level exports, summary diagnostics, and core SVG
  outputs.
- Added testing and acceptance criteria aimed at a deterministic, reproducible,
  non-degenerate synthetic benchmark with both extirpated and surviving cells.

#### Outcome

`spatext` now has a concrete specification for the first deterministic
predator-response truth module, giving `spat` a clear next target before any
stochasticity or observation-layer work is added.

### Interaction 16: Deterministic predator-truth implementation and run

#### Request

Implement the specification in `spec/synth_small_predator_truth.md` and
execute it so the generated artifacts can be examined directly.

#### Actions completed

- Implemented a new deterministic predator-response module under
  `spatext.synth.small.predator`.
- Reused the existing prey-only baseline programmatically as the initial
  condition rather than duplicating baseline logic.
- Implemented graph-native predator arrival from the western boundary to
  create the latent driver-arrival surface `T_P(x)`.
- Implemented deterministic post-arrival predator-pressure ramping to create
  the pressure trajectory `P_t(x)`.
- Implemented deterministic prey decline using the existing baseline
  demography kernel with an added Type III predation mortality term.
- Implemented latent true extirpation timing `T_X^{true}(x)` using the
  threshold rule based on local carrying capacity and baseline abundance.
- Implemented the extirpation-lag surface for extirpated cells.
- Implemented artifact emission for the predator-truth bundle, including:
  `domain.json`,
  `baseline_config.json`,
  `predator_config.json`,
  `diagnostics.json`,
  `summary.json`,
  `cells.csv`,
  `surfaces.npz`,
  `trajectories.npz`,
  and six SVG figures.
- Added the repository entrypoint
  `scripts/build_synth_small_predator_truth.py`.
- Exported the new predator-truth API through `spatext.synth.small`.
- Added tests covering:
  successful deterministic execution,
  reproducibility,
  artifact emission,
  missing-or-finite extirpation semantics,
  and failure on invalid configuration values.
- Tuned the default predator-response regime so the benchmark now yields a
  mixed outcome with both extirpated and surviving cells by the end of the
  run.
- Updated `README.md` and `AGENTS.md` so the repo front door and operating
  guide reflect the new module and its command-line entrypoint.

#### Implementation decisions

- Kept the predator exogenous in v1 by representing it through arrival time
  and pressure rather than as an endogenous predator population state.
- Used a Type III predation response as the default mortality form, as
  specified.
- Stored non-extirpated cells as missing values in `true_extirpation` and
  `extirpation_lag`, using `NaN` in the NPZ surfaces and blank fields in
  `cells.csv`.
- Stored the full deterministic prey and predator-pressure trajectories in
  `trajectories.npz` because the `25 x 25` benchmark is small and the audit
  value is high.

#### Deviations from spec

- No substantive spec change was required.
- The implementation only resolved tuning choices needed to reach the
  intended mixed default regime.

#### Verification completed

- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `uv run python scripts/build_synth_small_predator_truth.py --output-dir artifacts/synth_small_predator_truth`

All checks passed. The repo quality lane is green, all `23` tests passed,
coverage remained above the configured threshold, the package built
successfully, and the predator-truth artifact build completed without runtime
warnings or numerical failure.

#### Canonical output paths

- Bundle directory:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth`
- Summary:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/summary.json`
- Diagnostics:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/diagnostics.json`
- Surfaces archive:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/surfaces.npz`
- Trajectories archive:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/trajectories.npz`
- Suitability figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/suitability.svg`
- Initial-abundance figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/initial_abundance.svg`
- Driver-arrival figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/driver_arrival.svg`
- True-extirpation figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/true_extirpation.svg`
- Extirpation-lag figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/extirpation_lag.svg`
- Final-abundance figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/final_abundance.svg`

#### Run outcome

- Extirpated fraction: `0.3328`
- Surviving fraction: `0.6672`
- Driver-arrival range: `4` to `28`
- Finite lag range: `6` to `14`
- Stayed finite: `true`
- Stayed nonnegative: `true`
- Additional artifact-hygiene adjustment needed for this run: none

#### Outcome

`spatext` now has the first full deterministic driver-response truth object in
place for `synth-small`, and one canonical predator-truth bundle is staged on
disk for direct scientific inspection of arrival, lag, extirpation, and final
abundance structure.

### Interaction 17: Predator-truth visualisation scale and legend refresh

#### Request

Adjust the generated predator-truth visualisations so that directly
comparable surfaces use locked colour scales across time and add a visible
colour scale bar to each image, then regenerate the relevant figures.

#### Actions completed

- Updated the predator-truth SVG writer so it now supports fixed
  `color_min` and `color_max` values instead of always rescaling to each
  surface independently.
- Added a coloured scale bar with explicit minimum and maximum labels to each
  predator-truth numeric SVG figure.
- Added a missing-value key to figures that contain `NaN` surfaces, such as
  true extirpation and extirpation lag.
- Locked the abundance comparison figures to a shared scale spanning the full
  range across:
  `initial_abundance.svg`
  `final_abundance.svg`
- Locked the absolute-time figures to a shared scale spanning the full range
  across:
  `driver_arrival.svg`
  `true_extirpation.svg`
- Kept `extirpation_lag.svg` on its own shared lag scale with a matching
  colour bar.
- Added test coverage to verify that the emitted SVGs now include the common
  scale text and scale-bar elements for these comparisons.
- Regenerated the canonical predator-truth artifact bundle so the figures on
  disk reflect the updated visualisation contract.

#### Verification completed

- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `uv run python scripts/build_synth_small_predator_truth.py --output-dir artifacts/synth_small_predator_truth`

All checks passed. The repo quality lane remained green, and the regenerated
SVGs now advertise the intended shared scales and visible colour legends.

#### Refreshed figure paths

- Initial abundance:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/initial_abundance.svg`
- Final abundance:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/final_abundance.svg`
- Driver arrival:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/driver_arrival.svg`
- True extirpation:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/true_extirpation.svg`
- Extirpation lag:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/extirpation_lag.svg`

#### Outcome

The predator-truth figures are now better suited for direct visual
comparison: abundance surfaces no longer hide decline through independent
rescaling, time-valued surfaces share a common temporal legend, and each SVG
now includes an explicit colour bar for viewer interpretation.

### Interaction 18: Predator-truth vulnerability revision after first artifact review

#### Request

Review the predator-truth artifact interpretation after the first scientific
inspection discussion, then revise the module so it no longer encodes naturally
low-density prey cells as systematically safer by default. The agreed direction
was:

- replace the current Type III default with a Type II default more consistent
  with an exogenous generalist predator,
- replace the locally scaled extirpation threshold with an absolute
  quasi-extinction threshold for deterministic runs,
- regenerate the canonical predator-truth bundle,
- log the scientific reasoning and implementation choices for traceability.

#### Scientific diagnosis from the review discussion

The first predator-truth run revealed an undesirable default property:

- low-density prey cells were protected twice,
- Type III mortality reduced per-capita impact at low focal-prey abundance,
- the cell-wise extirpation threshold also became lower in low-density cells,
- together these choices made sparse cells less likely to extirpate than denser
  cells.

That behaviour was coherent mathematically but misaligned with the intended
scientific story for this module: an exogenous generalist predator wave whose
pressure is not numerically coupled to the focal prey and therefore should not
hand the focal prey an automatic low-density refuge.

#### Actions completed

- Replaced the predator-response default from Type III to Type II in
  `src/spatext/synth/small/predator.py`, using a per-capita mortality form that
  remains strong when focal prey are scarce rather than attenuating sharply at
  low abundance.
- Replaced the previous cell-wise threshold rule
  `min(phi K(x), rho N0(x))` with an absolute quasi-extinction threshold for the
  deterministic v1 predator-truth module.
- Tuned the revised deterministic default to a mixed regime with:
  `predation_scale = 1.0`,
  `half_saturation = 6.0`,
  `quasi_extirpation_abundance = 3.0`.
- Kept the current no-Allee default in place for this module, treating explicit
  low-density collapse amplification as a later realism layer rather than a
  required component of deterministic v1.
- Expanded the predator-truth artifact export so the extirpation threshold is
  now auditable in both:
  `surfaces.npz`
  `cells.csv`
- Added diagnostics fields recording both the response form and the threshold
  form/value.
- Added summary fields for the extirpation-threshold surface.
- Strengthened the predator-truth tests so they now check the revised
  vulnerability pattern and the constant-threshold export.
- Updated `spec/synth_small_predator_truth.md` so the authoritative module spec
  now matches the revised implementation rather than preserving an outdated Type
  III / locally scaled threshold contract.
- Reviewed `README.md` after implementation and updated the predator-truth
  section to describe the current Type II plus absolute quasi-extinction
  interpretation.
- Reviewed `AGENTS.md`; no repo-local operating-guide change was needed because
  the workflow rules did not change.

#### Explicit spec revision

This interaction deliberately revised the earlier predator-truth default
specification.

Previous default:

- Type III predation response,
- cell-wise extirpation threshold based on local carrying capacity and initial
  abundance.

Revised default:

- Type II predation response,
- absolute quasi-extinction threshold.

Reason for the revision:

- the first review run showed that the previous defaults hard-coded a scarcity
  refuge that was at odds with the intended ecological story for an exogenous
  generalist predator,
- the revised defaults better align the synthetic truth object with the
  scientific expectation that naturally sparse cells should not automatically be
  safer under arrival of a generalist predator wave.

#### Verification completed

- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `uv run python scripts/build_synth_small_predator_truth.py --output-dir artifacts/synth_small_predator_truth`

All checks passed. The repo quality lane remained green, all `24` tests passed,
coverage remained above the configured threshold at `94.48%`, the package built
successfully, and the refreshed predator-truth bundle was regenerated without
numerical failure.

#### Refreshed canonical output paths

- Bundle directory:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth`
- Summary:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/summary.json`
- Diagnostics:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/diagnostics.json`
- Surfaces archive:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/surfaces.npz`
- Trajectories archive:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/trajectories.npz`
- Driver-arrival figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/driver_arrival.svg`
- True-extirpation figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/true_extirpation.svg`
- Extirpation-lag figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/extirpation_lag.svg`
- Final-abundance figure:
  `/home/bwbrook/papers/spatext/artifacts/synth_small_predator_truth/final_abundance.svg`

#### Refreshed run outcome

- Predation response form: `type_ii`
- Extirpation-threshold form: `absolute_quasi_extinction`
- Quasi-extinction abundance: `3.0`
- Extirpated fraction: `0.4032`
- Surviving fraction: `0.5968`
- Driver-arrival range: `4` to `28`
- True-extirpation range: `15` to `52`
- Finite lag range: `11` to `41`
- Stayed finite: `true`
- Stayed nonnegative: `true`
- Additional clipping used: `false`

#### Interpreted pattern after revision

The regenerated run now expresses the intended vulnerability direction much more
clearly:

- extirpation is concentrated toward the western side where predator arrival is
  earliest,
- lower-initial-abundance cells are now more prone to extirpation than higher
  ones under the default deterministic truth settings,
- quartile-level extirpation rates across increasing initial-abundance bins are:
  `0.994`, `0.538`, `0.077`, `0.0`,
- the first five columns contain `112` extirpated cells, while the last five
  contain only `12`.

That revised pattern is not the final ecological truth model, but it is a much
better deterministic benchmark for the next rounds of inspection and synthetic
observation work.

### Interaction 19: Mac Mini dev-box handover preparation

#### Request

Prepare for moving `spatext` work from the current WSL environment to Barry's
Mac Mini development box by creating a detailed handover document for the
counterpart agent there. Include current repo state, continuation guidance, and
artifact-transfer considerations.

#### Actions completed

- Refreshed `origin` and confirmed that local `main` still matches
  `origin/main` at:
  `f639afd9fd5a2eaf7fd767218749df9e9ee13d96`
- Confirmed the working tree was clean before creating the handover document.
- Checked the current SSH configuration and identified the Mac Mini aliases:
  `dev-box-ts`
  `barrys-mac-mini`
- Ran a bounded non-interactive SSH probe to `dev-box-ts`, confirming access to
  the Mac Mini host `Mac-mini.lan` with home directory `/Users/bwbrook`.
- Searched common Mac-side checkout locations and did not find an existing
  `spatext` repository there.
- Checked the locally generated ignored artifact directories and recorded their
  approximate sizes:
  `artifacts/synth_small_first_review` at about `360K`
  `artifacts/synth_small_predator_truth` at about `700K`
- Created `spec/devbox_handover.md`.

#### Handover contents

The new handover document records:

- the canonical GitHub repository and latest verified commit,
- clone or fast-forward instructions for the Mac Mini,
- `uv` setup and verification commands,
- repo operating rules from `AGENTS.md`,
- implemented module state for baseline, inspection, first review run, and
  predator truth,
- the scientific rationale for the Type II plus absolute quasi-extinction
  predator-truth revision,
- artifact regeneration commands,
- optional WSL-to-Mac `rsync` commands if exact local artifacts need to be
  copied after the dev-box checkout exists,
- likely next work packages and watch points for the next agent.

#### Outcome

The Mac Mini counterpart agent now has a durable repo-local handover document at
`spec/devbox_handover.md`. The document favors regenerating ignored artifacts on
the dev box after clone or fast-forward, while also preserving exact copy
commands for the current WSL artifact bundles if continuity of SVG/NPZ/CSV files
is desired.

### Interaction 20: Mac Mini dev-box clone and verification

#### Request

Clone `BWBrook/spatext` into the empty Mac-side folder and review the repository
using the handover document as the orientation guide.

#### Actions completed

- Confirmed the working directory was the empty target folder:
  `/Users/bwbrook/papers/spatext`.
- Cloned `BWBrook/spatext` directly into that folder.
- Confirmed the live host was the intended Mac Mini target:
  `Barry's Mac mini` / `Mac-mini.lan`, macOS `26.5`, `arm64`.
- Read the repo-local operating guide, README, tooling contract, problem
  statement, report log, and `spec/devbox_handover.md`.
- Confirmed the checkout was clean and aligned with `origin/main` at:
  `a332c4fd749b5f853e4c85d114952bad496e6a16`
- Noted that this is one commit newer than the handover's last verified
  implementation commit because it includes the dev-box handover document.
- Created a fresh `uv` environment using the pinned CPython `3.14.4`.
- Ran the full local quality lane:
  `uv run ruff format --check .`
  `uv run ruff check .`
  `uv run mypy src tests`
  `uv run pytest`
  `uv build`
  `uv run pre-commit run --all-files`
- Regenerated the ignored baseline review bundle and inspection report at:
  `artifacts/synth_small_first_review`
- Regenerated the ignored predator-truth bundle at:
  `artifacts/synth_small_predator_truth`

#### Verification completed

- `uv sync --all-groups` completed successfully and created `.venv` with
  CPython `3.14.4`.
- Ruff formatting and lint checks passed.
- Mypy passed with no issues in `12` source files.
- Pytest collected and passed all `24` tests.
- Coverage remained above the configured `90%` gate at `94.48%`.
- `uv build` created both the source distribution and wheel.
- Pre-commit hooks passed.
- Baseline inspection verification passed all checks.
- Predator-truth regeneration reproduced the expected handover values:
  extirpated fraction `0.4032`,
  surviving fraction `0.5968`,
  driver-arrival range `4` to `28`,
  true-extirpation range `15` to `52`,
  finite lag range `11` to `41`,
  stayed finite `true`,
  stayed nonnegative `true`,
  and additional clipping `false`.

#### Review outcome

The Mac Mini checkout is now usable as the active development copy. The
repository remains in early, spec-led synthetic-validation buildout with three
implemented pieces: prey-only baseline generation, disk-first baseline
inspection, and deterministic predator-response truth generation. The most
natural next work package remains the one identified in the handover: inspect
the regenerated predator-truth artifacts with Barry, then either tune the
deterministic truth benchmark or build the predator-truth inspection layer
before adding the observation model.

### Interaction 21: Predator-truth inspection layer

#### Request

Execute the local project goal under
`docs/goals/001-predator-truth-inspection/`: create a disk-first inspection and
review layer for the `synth-small` deterministic predator-response truth
bundle, update the goal log, produce review artifacts, and verify the result
without committing or pushing.

#### Actions completed

- Read the goal `Goal.md`, `Plan.md`, `Runbook.md`, and `Log.md`.
- Confirmed the working state: `main` was tracking `origin/main`,
  `spec/report_log.md` was already modified from the Mac Mini handover work,
  and the local goal docs were untracked project state.
- Ran `uv sync --all-groups` successfully before implementation.
- Wrote `spec/synth_small_predator_truth_inspection.md`.
- Added the disk-first predator-truth inspection implementation in
  `src/spatext/synth/small/predator_inspect.py`.
- Added the command-line entry point
  `scripts/inspect_synth_small_predator_truth.py`.
- Exported the new inspection API from `spatext.synth.small`.
- Added focused tests in
  `tests/test_synth_small_predator_truth_inspection.py` covering:
  valid bundles, missing files, corrupted NPZ inputs, extirpation-before-arrival
  inconsistency, trajectory endpoint mismatch, and inconsistent summary values.
- Updated `README.md` and `AGENTS.md` to include the new inspection spec and
  user-facing command.
- Updated the local goal log at
  `docs/goals/001-predator-truth-inspection/Log.md`.
- Rebuilt the predator-truth artifact bundle and generated the inspection
  outputs under `artifacts/synth_small_predator_truth/inspection/`.

#### Inspection outputs

The inspection command writes:

- `artifacts/synth_small_predator_truth/inspection/verification.json`
- `artifacts/synth_small_predator_truth/inspection/parameters.csv`
- `artifacts/synth_small_predator_truth/inspection/surface_summary.csv`
- `artifacts/synth_small_predator_truth/inspection/trajectory_summary.csv`
- `artifacts/synth_small_predator_truth/inspection/extirpation_summary.csv`
- `artifacts/synth_small_predator_truth/inspection/report.md`

For the current regenerated predator-truth bundle, `verification.json` records
`passed: true` and `warning_count: 0`.

Key review metrics in the generated report include:

- extirpated fraction: `0.4032`
- surviving fraction: `0.5968`
- driver-arrival range: `4` to `28`
- true-extirpation range: `15` to `52`
- finite lag range: `11` to `41`
- low-initial-abundance extirpation rate: `0.993630573248`
- high-initial-abundance extirpation rate: `0`
- west-band extirpated count: `112`
- east-band extirpated count: `12`

#### Verification completed

- `uv sync --all-groups`
- `uv run pytest tests/test_synth_small_predator_truth_inspection.py --no-cov`
- `uv run python scripts/build_synth_small_predator_truth.py`
- `uv run python scripts/inspect_synth_small_predator_truth.py`
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`

All required checks passed. The full test suite collected `30` tests, all
passed, and total coverage was `92.82%`, above the configured `90%` gate.

#### Outcome

The predator-truth inspection layer is now implemented, documented, tested, and
executable as a local artifact review step. The next recommended scientific
goal is to review the generated predator-truth report with Barry and decide
whether the deterministic truth benchmark needs parameter tuning before adding
the first synthetic observation layer.

### Interaction 22: Deterministic benchmark sensitivity and readiness

#### Request

Execute the local project goal under
`docs/goals/002-deterministic-benchmark-sensitivity/`: produce a small
deterministic sensitivity and readiness package around the current
`synth-small` predator-truth default, preserve the existing Goal 001 dirty
work, update local logs, and verify without committing or pushing.

#### Actions completed

- Read the goal `Goal.md`, `Plan.md`, `Runbook.md`, and `Log.md`.
- Confirmed the working state: `main` was tracking `origin/main`, Goal 001
  changes were dirty and preserved, and the Goal 002 docs were local untracked
  project state.
- Ran `uv sync --all-groups` successfully before implementation.
- Confirmed the Goal 001 inspection report existed at
  `artifacts/synth_small_predator_truth/inspection/report.md`.
- Wrote `spec/synth_small_predator_truth_sensitivity.md`.
- Added the local deterministic sensitivity implementation in
  `src/spatext/synth/small/sensitivity.py`.
- Added the command-line entry point
  `scripts/run_synth_small_predator_truth_sensitivity.py`.
- Exported the sensitivity API from `spatext.synth.small`.
- Added focused tests in
  `tests/test_synth_small_predator_truth_sensitivity.py` covering:
  candidate construction, metric extraction, readiness classification, output
  writing, memo rendering, and finite scores over the default grid.
- Updated `README.md` and `AGENTS.md` to include the sensitivity spec and
  user-facing command.
- Updated the local goal log at
  `docs/goals/002-deterministic-benchmark-sensitivity/Log.md`.
- Ran the default 27-candidate local grid over:
  `predation_scale in {0.75, 1.0, 1.25}`,
  `half_saturation in {4.0, 6.0, 8.0}`, and
  `ramp_duration in {6, 8, 10}`.

#### Sensitivity outputs

The sensitivity command writes:

- `artifacts/synth_small_predator_truth_sensitivity/sweep_results.csv`
- `artifacts/synth_small_predator_truth_sensitivity/candidate_rankings.csv`
- `artifacts/synth_small_predator_truth_sensitivity/readiness.json`
- `artifacts/synth_small_predator_truth_sensitivity/decision_memo.md`

For the current local sweep:

- candidate count: `27`
- observation-ready candidates: `9`
- review candidates: `13`
- not-ready candidates: `5`
- default candidate classification: `observation_ready`
- best-ranked candidate: `default`
- recommendation: `keep_default_for_first_observation_layer`

Default-candidate review metrics:

- predation scale: `1.0`
- half-saturation: `6.0`
- ramp duration: `8`
- extirpated fraction: `0.4032`
- surviving fraction: `0.5968`
- finite lag range: `11` to `41`
- finite lag standard deviation: `7.5891142734`
- low-initial-abundance extirpation rate: `0.993630573248`
- high-initial-abundance extirpation rate: `0`
- west-band extirpated count: `112`
- east-band extirpated count: `12`
- non-negative clipping used: `false`

#### Verification completed

- `uv sync --all-groups`
- `uv run python scripts/build_synth_small_predator_truth.py`
- `uv run python scripts/inspect_synth_small_predator_truth.py`
- `uv run python scripts/run_synth_small_predator_truth_sensitivity.py`
- `uv run pytest tests/test_synth_small_predator_truth_sensitivity.py --no-cov`
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `uv run pre-commit run --files $(git ls-files -m -o --exclude-standard)`

All required checks passed. The full test suite collected `36` tests, all
passed, and total coverage was `92.76%`, above the configured `90%` gate.

#### Outcome

The deterministic sensitivity package is now implemented, documented, tested,
and executable as a local readiness decision step. Under the current explicit
criteria, the existing default predator-truth benchmark is classified as
`observation_ready` and is also the top-ranked candidate in the local sweep.
The next recommended goal is to add the first synthetic observation layer over
the approved deterministic truth object.

### Interaction 23: First response-only observation layer

#### Request

Execute the local project goal under
`docs/goals/003-first-response-observation-layer/`: add the first
seed-controlled response-only observation layer over the approved
`synth-small` predator-truth default, preserve the existing Goal 001 and Goal
002 dirty work, write disk-first inspection and recoverability-smoke artifacts,
and verify without committing or pushing.

#### Actions completed

- Read `Goal.md`, `Plan.md`, `Runbook.md`, and `Log.md`.
- Confirmed the working state: `main` was tracking `origin/main`, Goal 001 and
  Goal 002 changes remained dirty and preserved, and the Goal 003 docs were
  local untracked project state.
- Ran `uv sync --all-groups` successfully before implementation.
- Refreshed upstream predator-truth, predator-truth inspection, and
  predator-truth sensitivity artifacts.
- Confirmed the sensitivity decision still classifies the default candidate as
  `observation_ready` and recommends
  `keep_default_for_first_observation_layer`.
- Wrote `spec/synth_small_observations.md`.
- Added the first observation implementation in
  `src/spatext/synth/small/observations.py`.
- Added command-line entry points:
  `scripts/build_synth_small_observations.py` and
  `scripts/inspect_synth_small_observations.py`.
- Exported the observation API from `spatext.synth.small`.
- Added focused tests in `tests/test_synth_small_observations.py` covering:
  default-seed reproducibility, required schemas, analyst-facing truth-column
  exclusion, missing-file inspection failure, malformed detection indicators,
  and finite recoverability-smoke metrics.
- Updated `README.md` and `AGENTS.md` to include the new observation spec and
  user-facing commands.
- Updated the local goal log at
  `docs/goals/003-first-response-observation-layer/Log.md`.

#### Observation design

The first observation layer uses the approved default predator-truth object and
fixed seed `20260530`. All `25 x 25` cells are candidate sites. Survey times
are every four time steps through the predator-truth simulation horizon, with
two replicate visits for each sampled site-time. Visit inclusion is incomplete
and biased by broad west/central/east region plus suitability. Effort is
positive and varies by region, time, and seed-controlled random noise.

Observed counts are generated from a monotone effort/abundance response:

```text
Y_v ~ Poisson(lambda_v)
lambda_v = effort_v * count_scale * N_t(x) /
  (detection_half_saturation + N_t(x))
```

The analyst-facing files are `sites.csv`, `visits.csv`, and
`observations.csv`. They exclude predator arrival, predator pressure, true
extirpation, extirpation lag, initial abundance, and final abundance. Hidden
truth is available only in the clearly labelled evaluation file
`evaluation_truth.csv` plus `truth_reference.json`.

#### Observation outputs

The observation build command writes:

- `artifacts/synth_small_observations/observation_config.json`
- `artifacts/synth_small_observations/truth_reference.json`
- `artifacts/synth_small_observations/sites.csv`
- `artifacts/synth_small_observations/visits.csv`
- `artifacts/synth_small_observations/observations.csv`
- `artifacts/synth_small_observations/evaluation_truth.csv`

The inspection command writes:

- `artifacts/synth_small_observations/inspection/verification.json`
- `artifacts/synth_small_observations/inspection/observation_summary.csv`
- `artifacts/synth_small_observations/inspection/recoverability_smoke.json`
- `artifacts/synth_small_observations/inspection/report.md`

For the current local run, the build wrote `10,288` visits/observations.

#### Recoverability smoke result

The disk-first observation inspection passed, and
`recoverability_smoke.json` reported:

- pre-driver detection rate: `0.8576294277929155`
- post-driver detection rate: `0.6599564744287268`
- pre/post detection drop: `0.19767295336418866`
- late extirpated detection rate: `0.227`
- late surviving detection rate: `0.7910974499089254`
- late surviving-minus-extirpated detection-rate difference:
  `0.5640974499089254`
- late-detection AUC for extirpated versus surviving sites:
  `0.8939508196721312`

The smoke test therefore indicates that the noisy response observations retain
basic signal about latent extirpation. It is not a fitted model and does not
prove parameter identifiability.

#### Verification completed

- `uv sync --all-groups`
- `uv run python scripts/build_synth_small_predator_truth.py`
- `uv run python scripts/inspect_synth_small_predator_truth.py`
- `uv run python scripts/run_synth_small_predator_truth_sensitivity.py`
- `uv run python scripts/build_synth_small_observations.py`
- `uv run python scripts/inspect_synth_small_observations.py`
- `jq '{passed}' artifacts/synth_small_observations/inspection/verification.json`
- `jq '{passed, finite_metrics: ([.metrics[] | type == "number"] | all), metrics}' artifacts/synth_small_observations/inspection/recoverability_smoke.json`
- `test -s artifacts/synth_small_observations/inspection/report.md`
- `uv run pytest tests/test_synth_small_observations.py --no-cov`
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`
- `uv build`
- `uv run pre-commit run --files $(git ls-files -m -o --exclude-standard)`

All required checks passed. The full test suite collected `42` tests, all
passed, and total coverage was `92.47%`, above the configured `90%` gate.

#### Outcome

The three-goal pilot now has a coherent deterministic truth object, a
readiness decision package, and a first response-only observation layer with
disk-first inspection and a simple recoverability smoke test. The recommended
next step is to consolidate this pilot into a small end-to-end synthetic
pipeline that reconstructs an observed extirpation surface from the
response-only observations, then compares that reconstructed surface against
the hidden truth before any ABC/POM machinery is added.

### Interaction 24: Consolidate three-goal synth-small pilot

#### Request

Consolidate Goals 001-003 into a clean pushed publication checkpoint on
`main` without adding new science functionality; preserve existing work and
avoid staging generated/cached artifacts.

#### Actions completed

- Read `docs/goals/004-consolidate-three-goal-pilot/Goal.md`,
  `Plan.md`, `Runbook.md`, and `Log.md`.
- Confirmed baseline state in `/Users/bwbrook/papers/spatext`:
  - `git status --short --branch` showed `main...origin/main`.
  - Dirty state included only expected Goal 001-003 documentation, specs,
    scripts, modules, tests and existing modified docs, plus incidental
    host `.DS_Store`.
- Added `.DS_Store` to `.gitignore` and removed local `.DS_Store`.
- Re-ran the goal’s validation lane (`uv sync`, truth/observation build + inspect,
  sensitivity run, JSON smoke checks, format, lint, type-check, test, and build):
  - `42` tests passed, `92.47%` coverage.
  - All artifact verification checks passed (`passed: true` plus finite metrics).
  - Distribution build succeeded (`dist/spatext-0.1.0.tar.gz`, wheel).
- Staged exactly the accepted path set and confirmed by:
  - `git diff --cached --name-only`
  - `git diff --cached --stat`.
- Ran `uv run pre-commit run --all-files` on staged files; all hooks passed.

#### Commit and publication

- Committed on `main`:
  - message: `feat: add synth-small observation readiness workflow`
  - scope: all accepted Goal 001-003 consolidation artifacts plus `.gitignore`.
- Pushed with `git push origin main`.

#### Outcome

The three-goal synthetic pilot is now in a pushed publication checkpoint state,
with no generated artifacts, caches, or host noise staged. The next science-step
recommendation remains: build a response-only extirpation reconstruction check
against hidden truth before introducing ABC/POM inference.

### Interaction 25: Build response-only extirpation reconstruction baseline

#### Request

Build a first response-only `T_X^obs` reconstruction from the synth-small
response observations, then evaluate it against hidden truth using separate
diagnostics only.

#### Actions completed

- Reviewed and followed the active goal packet:
  `docs/goals/005-response-only-extirpation-reconstruction/`.
- Rebuilt prerequisites and smoke-verified the synthetic truth and observation
  layer:
  `scripts/build_synth_small_predator_truth.py`,
  `scripts/inspect_synth_small_predator_truth.py`,
  `scripts/build_synth_small_observations.py`,
  `scripts/inspect_synth_small_observations.py`.
- Implemented `spec/synth_small_extirpation_reconstruction.md`.
- Added response-only reconstruction logic in:
  `src/spatext/synth/small/reconstruction.py`.
- Added CLI entrypoints:
  `scripts/reconstruct_synth_small_extirpation.py` and
  `scripts/inspect_synth_small_extirpation_reconstruction.py`.
- Exported reconstruction symbols in `src/spatext/synth/small/__init__.py`.
- Added focused tests in
  `tests/test_synth_small_extirpation_reconstruction.py`.
- Ran and passed all requested quality checks:
  - `uv sync --all-groups`
  - `uv run python scripts/reconstruct_synth_small_extirpation.py`
  - `uv run python scripts/inspect_synth_small_extirpation_reconstruction.py`
  - `uv run pytest tests/test_synth_small_extirpation_reconstruction.py --no-cov`
  - `uv run ruff format .`
  - `uv run ruff check .`
  - `uv run mypy src tests`
  - `uv run pytest`
  - `uv run uv build`
- Artifact outputs written and validated under:
  `artifacts/synth_small_extirpation_reconstruction/`.

#### Outcomes

- Required files:
  - `reconstruction_config.json`
  - `site_reconstruction.csv`
  - `time_detection_summary.csv`
  - `verification.json`
  - `evaluation_metrics.json`
  - `report.md`
- Response-only boundary held (no hidden-truth fields in `site_reconstruction.csv`).
- Reconstruction diagnostics at default settings:
  - TP / FP / TN / FN confusion: `151 / 0 / 373 / 101`
  - sensitivity / specificity / precision: `0.5992 / 1.0 / 1.0`
  - temporal-error count: `151`, MAE: `7.6424`
  - interpreted status counts: 151 observed-extirpated, 473 not-observed-extirpated,
    1 insufficient, 0 unsurveyed.
- `uv build` produced:
  - `dist/spatext-0.1.0.tar.gz`
  - `dist/spatext-0.1.0-py3-none-any.whl`
- Next recommendation logged for the packet:
  proceed to response-only ABC/POM with cautionary controls.

### Interaction 26: Build tiny response-only inference screen

#### Request

Create and implement Goal 006 on a named branch: a tiny response-only screen
over the existing `synth-small` `T_X^obs` reconstruction outputs, keeping the
work cautious, bounded, and free of real-data or formal-inference claims.

#### Actions completed

- Corrected the live worktree interpretation before editing:
  the thread workspace is the linked Codex worktree
  `/Users/bwbrook/.codex/worktrees/b4ee/spatext`, not the primary checkout.
- Fetched `origin`, confirmed `origin/main` at `f9a0ed0` or newer, and created
  branch `codex/spatext-goal006-response-screen` from `origin/main`.
- Added Goal 006 packet:
  `docs/goals/006-response-only-inference-screen/`.
- Added `spec/synth_small_response_screen.md`.
- Added response-only screen implementation in:
  `src/spatext/synth/small/response_screen.py`.
- Added CLI entrypoint:
  `scripts/run_synth_small_response_screen.py`.
- Exported screen symbols in `src/spatext/synth/small/__init__.py`.
- Added focused tests in `tests/test_synth_small_response_screen.py`.
- Updated `README.md` with the Goal 005 reconstruction and Goal 006 screen
  surfaces.

#### Screen design

The screen reads only response-side reconstruction artifacts:

- `reconstruction_config.json`
- `site_reconstruction.csv`
- `time_detection_summary.csv`
- `verification.json`

It does not read the Goal 005 evaluation-only metrics file. The output bundle
summarizes site counts, observed-extirpated fractions, group-level weak-signal
notes, time detection summaries, and a cautionary screen decision.

#### Validation completed

- RED check:
  `uv run pytest tests/test_synth_small_response_screen.py --no-cov`
  initially failed because the new screen API did not exist.
- Focused checks passed:
  - `uv run pytest tests/test_synth_small_response_screen.py --no-cov`
    (`4` tests).
  - `uv run pytest tests/test_synth_small_extirpation_reconstruction.py --no-cov`
    (`6` tests).
- Quality checks passed:
  - `git diff --check`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src tests`
  - `uv run pytest` (`52` tests, coverage `92.68%`)
  - `uv build`
- CLI smoke passed:
  `uv run python scripts/build_synth_small_observations.py`
  `uv run python scripts/reconstruct_synth_small_extirpation.py`
  `uv run python scripts/run_synth_small_response_screen.py`

#### Outcomes

- Screen artifact outputs written under:
  `artifacts/synth_small_response_screen/`.
- Default response-screen summary:
  - site count: `625`
  - observed-extirpated sites: `151`
  - not-observed-extirpated sites: `473`
  - insufficient-history sites: `1`
  - observed-extirpated fraction: `0.2416`
  - screen decision: `screen_with_caution`
  - not-observed-extirpated fraction: `0.7568`
  - late-screen bias warning: `true`
- Generated artifacts and distribution outputs were not staged.
- No real-data, formal inference, remote-compute, commit, or push boundary was
  crossed.

### Interaction 29: Build synth-small summary-vector bridge

#### Request

Execute Goal 009: build a synthetic-only `S(T_X, T_P)` summary-vector bridge
before any compatibility-screen, ABC, POM, likelihood, posterior, parameter
sweep, real-data, or remote-compute work.

#### Actions completed

- Confirmed the primary action repo checkout:
  `/Users/bwbrook/papers/spatext`.
- Fetched `origin`, confirmed `origin/main` at `3ce6101`, and created branch
  `codex/spatext-goal009-summary-vector` from `origin/main`.
- Refreshed repo contracts, Goal 005-008 packets, active specs, and current
  reconstruction/screen/evaluation source and tests.
- Added `spec/synth_small_summary_vector.md`.
- Added focused tests in `tests/test_synth_small_summary_vector.py`.
- Added disk-first summary-vector implementation in:
  `src/spatext/synth/small/summary_vector.py`.
- Added CLI entrypoint:
  `scripts/build_synth_small_summary_vector.py`.
- Exported summary-vector symbols in `src/spatext/synth/small/__init__.py`.
- Updated `README.md` and `AGENTS.md` with the summary-vector surface.

#### Summary-vector design

The bridge reads emitted synthetic artifacts from disk:

- `artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv`
- `artifacts/synth_small_extirpation_reconstruction/verification.json`
- `artifacts/synth_small_observations/evaluation_truth.csv`

It emits both required modes:

- `ideal_true`: `T_X = true_extirpation`, `T_P = driver_arrival`;
- `realistic_observed`: `T_X = observed_extirpation_time`,
  `T_P = driver_arrival`.

Undefined scalar or coverage metrics are retained with explicit
`missing_reason` values rather than dropped.

#### Validation completed

- RED check:
  `uv run pytest tests/test_synth_small_summary_vector.py --no-cov`
  initially failed because `build_synth_small_summary_vector` did not exist.
- Focused checks passed:
  - `uv run pytest tests/test_synth_small_summary_vector.py --no-cov`
    (`5` tests).
  - `uv run pytest tests/test_synth_small_extirpation_reconstruction.py --no-cov`
    (`6` tests).
  - `uv run pytest tests/test_synth_small_response_screen.py --no-cov`
    (`4` tests).
  - `uv run pytest tests/test_synth_small_response_screen_evaluation.py --no-cov`
    (`4` tests).
- Quality checks passed after a narrow optional-float typing fix:
  - `git diff --check`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src tests`
  - `uv run pytest` (`65` tests, coverage `93.12%`)
  - `uv build`
- CLI smoke passed:
  `uv run python scripts/build_synth_small_summary_vector.py`

#### Outcomes

- Summary-vector artifact outputs written under:
  `artifacts/synth_small_summary_vector/`.
- Required files:
  - `summary_vector_config.json`
  - `summary_components.csv`
  - `mode_summary.json`
  - `coverage_curve.csv`
  - `verification.json`
  - `report.md`
- Default summary-vector mode counts:
  - `ideal_true`: finite targets `252`, finite target fraction `0.4032`,
    lag count `252`, lag mean `22.5674603175`;
  - `realistic_observed`: finite targets `151`, finite target fraction
    `0.2416`, lag count `151`, lag mean `25.0264900662`.
- Summary-vector verification passed with `synthetic_only: true`.
- Generated artifacts and distribution outputs were not staged.
- No ABC, POM, formal inference, parameter sweep, posterior claim, real-data,
  remote-compute, commit, or push boundary was crossed.

### Interaction 27: Build response-screen inspection layer

#### Request

Create and implement Goal 007 on a named branch: a disk-first inspection layer
for the accepted Goal 006 response-screen artifact bundle.

#### Actions completed

- Confirmed the thread workspace is the linked Codex worktree
  `/Users/bwbrook/.codex/worktrees/b4ee/spatext`.
- Fetched `origin`, confirmed `origin/main` at `96e38bc` or newer, and created
  branch `codex/spatext-goal007-response-screen-inspection` from `origin/main`.
- Added Goal 007 packet:
  `docs/goals/007-response-screen-inspection/`.
- Added `spec/synth_small_response_screen_inspection.md`.
- Added disk-first inspection implementation in:
  `src/spatext/synth/small/response_screen_inspect.py`.
- Added CLI entrypoint:
  `scripts/inspect_synth_small_response_screen.py`.
- Exported inspection symbols in `src/spatext/synth/small/__init__.py`.
- Added focused tests in
  `tests/test_synth_small_response_screen_inspection.py`.
- Updated `README.md` with the response-screen inspection surface.

#### Inspection design

The inspector reads only the emitted screen artifact bundle:

- `response_screen_config.json`
- `screen_summary.json`
- `group_screen_summary.csv`
- `time_screen_summary.csv`
- `verification.json`
- `report.md`

It does not rebuild the screen from live objects, and it ignores evaluation-like
decoy files that are outside the screen contract.

#### Validation completed

- RED check:
  `uv run pytest tests/test_synth_small_response_screen_inspection.py --no-cov`
  initially failed because the new inspection API did not exist.
- Focused checks passed:
  - `uv run pytest tests/test_synth_small_response_screen_inspection.py --no-cov`
    (`4` tests).
  - `uv run pytest tests/test_synth_small_response_screen.py --no-cov`
    (`4` tests).
- Quality checks passed:
  - `git diff --check`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src tests`
  - `uv run pytest` (`56` tests, coverage `92.81%`)
  - `uv build`
- CLI smoke passed:
  `uv run python scripts/inspect_synth_small_response_screen.py`

#### Outcomes

- Inspection artifact outputs written under:
  `artifacts/synth_small_response_screen/inspection/`.
- Default inspection review summary:
  - screen decision: `screen_with_caution`
  - site count: `625`
  - observed-extirpated sites: `151`
  - not-observed-extirpated sites: `473`
  - insufficient-history sites: `1`
  - observed-extirpated fraction: `0.2416`
  - late-screen bias warning: `true`
  - not-observed-extirpated fraction: `0.7568`
  - weak-signal review groups: `front_band/east_band`, `region/east`
- Generated artifacts and distribution outputs were not staged.
- No real-data, hidden-truth/evaluation-input, formal inference, remote-compute,
  commit, or push boundary was crossed.

### Interaction 28: Build response-screen evaluation audit

#### Request

Create and implement Goal 008 on a named branch: a synthetic-only evaluation
audit for the Goal 006/007 response-screen output.

#### Actions completed

- Confirmed the thread workspace is the linked Codex worktree
  `/Users/bwbrook/.codex/worktrees/b4ee/spatext`.
- Fetched `origin`, confirmed `origin/main` at `db0517a` or newer, and created
  branch `codex/spatext-goal008-response-screen-evaluation-audit` from
  `origin/main`.
- Refreshed Goal 005-007 packets, specs, and source/test surfaces.
- Added Goal 008 packet:
  `docs/goals/008-response-screen-evaluation-audit/`.
- Added `spec/synth_small_response_screen_evaluation.md`.
- Added synthetic-only evaluation implementation in:
  `src/spatext/synth/small/response_screen_evaluate.py`.
- Added CLI entrypoint:
  `scripts/evaluate_synth_small_response_screen.py`.
- Exported evaluation symbols in `src/spatext/synth/small/__init__.py`.
- Added focused tests in
  `tests/test_synth_small_response_screen_evaluation.py`.
- Updated `README.md` with the response-screen evaluation surface.

#### Evaluation design

The audit reads emitted response-screen artifacts plus clearly labelled
synthetic evaluation artifacts:

- `site_reconstruction.csv`
- `evaluation_metrics.json`
- `evaluation_truth.csv`

It writes only under:

```text
artifacts/synth_small_response_screen/evaluation/
```

and all JSON outputs are explicitly labelled `evaluation_only`.

#### Validation completed

- RED check:
  `uv run pytest tests/test_synth_small_response_screen_evaluation.py --no-cov`
  initially failed because the new evaluation API did not exist.
- Focused checks passed:
  - `uv run pytest tests/test_synth_small_response_screen_evaluation.py --no-cov`
    (`4` tests).
  - `uv run pytest tests/test_synth_small_response_screen.py --no-cov`
    (`4` tests).
  - `uv run pytest tests/test_synth_small_response_screen_inspection.py --no-cov`
    (`4` tests).
- Quality checks passed:
  - `git diff --check`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src tests`
  - `uv run pytest` (`60` tests, coverage `93.05%`)
  - `uv build`
- CLI smoke passed:
  `uv run python scripts/evaluate_synth_small_response_screen.py`

#### Outcomes

- Evaluation artifact outputs written under:
  `artifacts/synth_small_response_screen/evaluation/`.
- Default synthetic-only audit summary:
  - evaluation-only: `true`
  - screen decision: `screen_with_caution`
  - TP / FP / TN / FN: `151 / 0 / 373 / 101`
  - sensitivity / specificity / precision: `0.5992063492063492 / 1.0 / 1.0`
  - false-negative groups: `front_band/east_band`,
    `front_band/middle_band`, `region/central`, `region/east`
  - weak-signal groups: `front_band/east_band`, `region/east`
- Generated artifacts and distribution outputs were not staged.
- No real-data, formal inference, remote-compute, commit, or push boundary was
  crossed.
