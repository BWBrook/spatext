# spatext

`spatext` is a Python repository for response-only spatiotemporal extinction
inference.

The project is being built to support scientific workflows where:

- a putative ecological driver spreads through space and time,
- the biological response is local extinction or extirpation,
- direct observations of the driver are sparse, noisy, or missing, and
- the response is observed only through incomplete and biased records.

The initial scientific target is to determine what can be learned about a
spatially spreading extinction driver from response-only evidence, while making
recoverability limits and failure regimes explicit rather than hiding them.

## Scientific framing

The main scientific statement for the repository lives in
[`spec/problem_statement.md`](spec/problem_statement.md).

The mathematical modelling contract currently lives in
[`spec/theory.md`](spec/theory.md).

Two central latent quantities anchor the modelling vision:

- `TP(x)`: arrival time of the hypothesized driver at location `x`
- `TX(x)`: extirpation time at location `x`, inferred from observations

The first substantive case study is the mink-water-vole system in Great Britain
and Ireland, but the repository is being structured as a general framework
rather than a one-off case-study codebase.

## Current project stage

The repository is in early buildout, with the first synthetic baseline and
inspection workflow now in place. Current priorities are:

- keeping scientific specification separate from implementation,
- building a clean and testable Python package foundation,
- validating methods against synthetic truth before real-data interpretation,
- maintaining an auditable record of assumptions, gates, and outcomes.

## Repository map

```text
spatext/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── uv.lock
├── spec/
├── src/
├── tests/
└── scripts/
```

Key locations:

- [`AGENTS.md`](AGENTS.md): repo-local operating instructions
- [`spec/problem_statement.md`](spec/problem_statement.md): scientific mission
- [`spec/theory.md`](spec/theory.md): mathematical model and inference theory
- [`spec/synth_small_baseline.md`](spec/synth_small_baseline.md): Module 1
  baseline specification
- [`spec/synth_small_inspection.md`](spec/synth_small_inspection.md): Module 1
  inspection specification
- [`spec/synth_small_predator_truth.md`](spec/synth_small_predator_truth.md):
  deterministic predator-response truth specification
- [`spec/synth_small_predator_truth_inspection.md`](spec/synth_small_predator_truth_inspection.md):
  deterministic predator-response truth inspection specification
- [`spec/synth_small_predator_truth_sensitivity.md`](spec/synth_small_predator_truth_sensitivity.md):
  deterministic predator-response sensitivity and readiness specification
- [`spec/synth_small_observations.md`](spec/synth_small_observations.md):
  first response-only observation-layer specification
- [`spec/synth_small_extirpation_reconstruction.md`](spec/synth_small_extirpation_reconstruction.md):
  response-only observed-extirpation reconstruction specification
- [`spec/synth_small_response_screen.md`](spec/synth_small_response_screen.md):
  tiny response-only screen specification
- [`spec/synth_small_response_screen_inspection.md`](spec/synth_small_response_screen_inspection.md):
  disk-first response-screen inspection specification
- [`spec/synth_small_response_screen_evaluation.md`](spec/synth_small_response_screen_evaluation.md):
  synthetic-only response-screen evaluation-audit specification
- [`spec/synth_small_summary_vector.md`](spec/synth_small_summary_vector.md):
  synthetic-only summary-vector bridge specification
- [`spec/synth_small_compatibility_screen.md`](spec/synth_small_compatibility_screen.md):
  synthetic-only compatibility-screen specification
- [`spec/synth_small_compatibility_mismatch_audit.md`](spec/synth_small_compatibility_mismatch_audit.md):
  synthetic-only compatibility-mismatch audit specification
- [`spec/synth_small_false_negative_mechanism_audit.md`](spec/synth_small_false_negative_mechanism_audit.md):
  synthetic-only response-reconstruction false-negative mechanism audit
  specification
- [`spec/synth_small_observation_support_counterfactual_screen.md`](spec/synth_small_observation_support_counterfactual_screen.md):
  synthetic-only post-extirpation observation-support counterfactual screen
  specification
- [`spec/synth_small_target_timing_residual_decomposition.md`](spec/synth_small_target_timing_residual_decomposition.md):
  synthetic-only target-timing residual-decomposition diagnostic specification
- [`spec/tooling_bootstrap.md`](spec/tooling_bootstrap.md): tooling contract
- [`spec/report_log.md`](spec/report_log.md): running operational log
- [`src/spatext/`](src/spatext): installable package source
- [`tests/`](tests): test suite

## Tooling baseline

The bootstrap environment currently uses:

- CPython `3.14.4`
- [`uv`](https://github.com/astral-sh/uv) for environment and dependency
  management
- `uv_build` as the build backend
- `ruff` for formatting and linting
- `mypy` for strict type checking
- `pytest` and `pytest-cov` for tests and coverage
- `pre-commit` for fast local hygiene checks

The authoritative Python packaging and dependency definitions live in
[`pyproject.toml`](pyproject.toml) and [`uv.lock`](uv.lock).

## Core local commands

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run pre-commit run --all-files
```

## Implemented baseline module

Module 1 is now implemented as a small synthetic prey-only baseline benchmark.
It constructs:

- a `25 x 25` square-lattice island domain,
- a deterministic suitability surface,
- a suitability-driven carrying-capacity surface,
- a prey-only equilibrium abundance surface,
- convergence diagnostics and occupancy summaries,
- an auditable artifact bundle for inspection.

The main implementation entrypoints are:

- [`src/spatext/spatial.py`](src/spatext/spatial.py): graph-based spatial domain
  primitives
- [`src/spatext/synth/small/baseline.py`](src/spatext/synth/small/baseline.py):
  `synth-small` baseline configuration, simulation, and artifact export
- [`scripts/build_synth_small_baseline.py`](scripts/build_synth_small_baseline.py):
  command-line utility for emitting a baseline bundle

To generate the baseline artifact bundle locally:

```bash
uv run python scripts/build_synth_small_baseline.py \
  --output-dir artifacts/synth_small_baseline
```

That command writes JSON, CSV, NPZ, and SVG artifacts for downstream
inspection and later synthetic modules.

## Implemented inspection module

Module 1 now also includes a disk-first inspection layer for auditing an
existing baseline artifact bundle. It:

- reloads the baseline bundle from disk,
- verifies structural, numerical, and scientific-sanity checks,
- flattens the generating configuration into a readable parameter table,
- summarizes the core spatial surfaces,
- renders a compact Markdown inspection report that links back to the emitted
  SVG artifacts.

The main inspection entrypoints are:

- [`src/spatext/synth/small/inspect.py`](src/spatext/synth/small/inspect.py):
  artifact loading, verification, summary-table generation, and Markdown
  report rendering
- [`scripts/inspect_synth_small_baseline.py`](scripts/inspect_synth_small_baseline.py):
  command-line utility for inspecting an existing baseline bundle

To inspect an existing baseline artifact bundle locally:

```bash
uv run python scripts/inspect_synth_small_baseline.py \
  --artifact-dir artifacts/synth_small_baseline
```

That command writes an `inspection/` subdirectory containing:

- `verification.json`
- `parameters.csv`
- `surface_summary.csv`
- `report.md`

## Implemented predator-truth module

Module 1 now also includes the first deterministic predator-response truth
module built on top of the prey-only baseline. It produces:

- a west-to-east driver-arrival surface `T_P(x)`,
- a deterministic predator-pressure trajectory `P_t(x)`,
- a prey abundance trajectory `N_t(x)` after predator introduction,
- a latent true extirpation surface `T_X^true(x)`,
- an extirpation-lag surface for extirpated cells,
- a self-contained artifact bundle for downstream inspection tooling.

The current default interpretation is an exogenous generalist-predator wave:

- west-to-east arrival with a bounded pressure ramp,
- a Type II per-capita prey mortality response,
- an absolute quasi-extinction threshold for `T_X^true(x)`,
- no default Allee effect in this deterministic v1 benchmark.

The main predator-truth entrypoints are:

- [`src/spatext/synth/small/predator.py`](src/spatext/synth/small/predator.py):
  deterministic predator arrival, pressure ramping, prey response,
  extirpation timing, and artifact export
- [`scripts/build_synth_small_predator_truth.py`](scripts/build_synth_small_predator_truth.py):
  command-line utility for emitting a predator-truth bundle

To generate the predator-truth artifact bundle locally:

```bash
uv run python scripts/build_synth_small_predator_truth.py \
  --output-dir artifacts/synth_small_predator_truth
```

That command writes JSON, CSV, NPZ, and SVG artifacts for the full latent
driver-response truth object, including surfaces and full deterministic
trajectories.

## Implemented predator-truth inspection module

Module 1 now also includes a disk-first inspection layer for auditing an
existing deterministic predator-truth artifact bundle. It:

- reloads the predator-truth bundle from disk,
- verifies structural, numerical, trajectory, extirpation, and diagnostic
  contracts,
- separates hard verification failures from scientific warnings,
- writes parameter, surface, trajectory, and extirpation-summary tables,
- renders a Markdown review report that links back to the emitted SVG figures.

The main predator-truth inspection entrypoints are:

- [`src/spatext/synth/small/predator_inspect.py`](src/spatext/synth/small/predator_inspect.py):
  artifact loading, verification, warning generation, summary-table generation,
  and Markdown report rendering
- [`scripts/inspect_synth_small_predator_truth.py`](scripts/inspect_synth_small_predator_truth.py):
  command-line utility for inspecting an existing predator-truth bundle

To inspect an existing predator-truth artifact bundle locally:

```bash
uv run python scripts/inspect_synth_small_predator_truth.py
```

That command writes an `inspection/` subdirectory containing:

- `verification.json`
- `parameters.csv`
- `surface_summary.csv`
- `trajectory_summary.csv`
- `extirpation_summary.csv`
- `report.md`

## Implemented predator-truth sensitivity module

Module 1 now also includes a small deterministic sensitivity/readiness sweep
around the current predator-truth defaults. It:

- runs the current default plus a local grid over `predation_scale`,
  `half_saturation`, and `ramp_duration`,
- computes extirpation, lag, vulnerability, west/east-band, final-abundance,
  and numerical-stability metrics for each candidate,
- classifies candidates with explicit readiness criteria,
- ranks candidates with a documented deterministic score,
- writes a compact decision package for deciding whether the current default
  is ready for the first observation layer.

The main sensitivity entrypoints are:

- [`src/spatext/synth/small/sensitivity.py`](src/spatext/synth/small/sensitivity.py):
  candidate construction, metric extraction, readiness classification, ranking,
  and report rendering
- [`scripts/run_synth_small_predator_truth_sensitivity.py`](scripts/run_synth_small_predator_truth_sensitivity.py):
  command-line utility for emitting the sensitivity decision package

To run the local deterministic sensitivity sweep:

```bash
uv run python scripts/run_synth_small_predator_truth_sensitivity.py
```

That command writes `artifacts/synth_small_predator_truth_sensitivity/`
containing:

- `sweep_results.csv`
- `candidate_rankings.csv`
- `readiness.json`
- `decision_memo.md`

## Implemented first observation module

Module 1 now also includes the first seed-controlled response-only observation
layer over the approved default predator-truth benchmark. It:

- samples repeated site visits at selected times,
- emits effort-conditioned prey-response detections/counts,
- keeps predator arrival, predator pressure, true extirpation, and latent
  abundance out of analyst-facing tables,
- writes a clearly labelled evaluation-truth table for diagnostics,
- inspects observation bundles from disk,
- runs a lightweight recoverability smoke test without fitting the model.

The main observation entrypoints are:

- [`src/spatext/synth/small/observations.py`](src/spatext/synth/small/observations.py):
  observation generation, artifact emission, disk-first inspection, and smoke
  metrics
- [`scripts/build_synth_small_observations.py`](scripts/build_synth_small_observations.py):
  command-line utility for emitting the observation bundle
- [`scripts/inspect_synth_small_observations.py`](scripts/inspect_synth_small_observations.py):
  command-line utility for inspecting an existing observation bundle

To build and inspect the first observation bundle:

```bash
uv run python scripts/build_synth_small_observations.py
uv run python scripts/inspect_synth_small_observations.py
```

The build command writes `artifacts/synth_small_observations/` containing:

- `observation_config.json`
- `truth_reference.json`
- `sites.csv`
- `visits.csv`
- `observations.csv`
- `evaluation_truth.csv`

The inspection command writes `inspection/` outputs:

- `verification.json`
- `observation_summary.csv`
- `recoverability_smoke.json`
- `report.md`

## Implemented extirpation reconstruction module

Module 1 now also includes the first conservative response-only
observed-extirpation reconstruction layer. It:

- reads the analyst-facing observation tables from disk,
- estimates a response-side `T_X^obs` proxy using a final sustained-absence
  rule,
- keeps hidden truth out of reconstruction decisions and primary outputs,
- writes separate evaluation diagnostics for synthetic validation only.

The main reconstruction entrypoints are:

- [`src/spatext/synth/small/reconstruction.py`](src/spatext/synth/small/reconstruction.py):
  reconstruction rules, artifact writing, evaluation-only diagnostics, and
  bundle inspection
- [`scripts/reconstruct_synth_small_extirpation.py`](scripts/reconstruct_synth_small_extirpation.py):
  command-line utility for emitting reconstruction artifacts
- [`scripts/inspect_synth_small_extirpation_reconstruction.py`](scripts/inspect_synth_small_extirpation_reconstruction.py):
  command-line utility for inspecting an existing reconstruction bundle

To build and inspect the reconstruction bundle:

```bash
uv run python scripts/reconstruct_synth_small_extirpation.py
uv run python scripts/inspect_synth_small_extirpation_reconstruction.py
```

The reconstruction command writes
`artifacts/synth_small_extirpation_reconstruction/` containing:

- `reconstruction_config.json`
- `site_reconstruction.csv`
- `time_detection_summary.csv`
- `verification.json`
- `evaluation_metrics.json`
- `report.md`

## Implemented response-only screen module

Module 1 now also includes a tiny response-only screen over the reconstructed
`T_X^obs` surface. It:

- reads only response-side reconstruction artifacts,
- computes compact site, group, and time summaries,
- flags weak-information groups and late-screen bias risks,
- emits a cautionary screen decision without fitting a model.

The main screen entrypoints are:

- [`src/spatext/synth/small/response_screen.py`](src/spatext/synth/small/response_screen.py):
  response-only screen summaries, verification, and report rendering
- [`src/spatext/synth/small/response_screen_inspect.py`](src/spatext/synth/small/response_screen_inspect.py):
  disk-first response-screen artifact inspection and review summaries
- [`src/spatext/synth/small/response_screen_evaluate.py`](src/spatext/synth/small/response_screen_evaluate.py):
  synthetic-only evaluation audit for screen failure modes
- [`scripts/run_synth_small_response_screen.py`](scripts/run_synth_small_response_screen.py):
  command-line utility for emitting screen artifacts
- [`scripts/inspect_synth_small_response_screen.py`](scripts/inspect_synth_small_response_screen.py):
  command-line utility for inspecting an existing screen bundle
- [`scripts/evaluate_synth_small_response_screen.py`](scripts/evaluate_synth_small_response_screen.py):
  command-line utility for synthetic-only screen evaluation

To build, inspect, and evaluate the screen bundle after the reconstruction and
observation bundles exist:

```bash
uv run python scripts/run_synth_small_response_screen.py
uv run python scripts/inspect_synth_small_response_screen.py
uv run python scripts/evaluate_synth_small_response_screen.py
```

That command writes `artifacts/synth_small_response_screen/` containing:

- `response_screen_config.json`
- `screen_summary.json`
- `group_screen_summary.csv`
- `time_screen_summary.csv`
- `verification.json`
- `report.md`

The inspection command writes `inspection/` outputs:

- `verification.json`
- `review_summary.json`
- `group_review_summary.csv`
- `report.md`

The evaluation command writes `evaluation/` outputs:

- `evaluation_config.json`
- `screen_evaluation_summary.json`
- `group_evaluation_summary.csv`
- `site_evaluation_audit.csv`
- `verification.json`
- `report.md`

## Implemented summary-vector bridge

Module 1 now also includes a synthetic-only `S(T_X, T_P)` summary-vector bridge
for later compatibility-screen or ABC design work. It:

- reads emitted reconstruction and observation evaluation artifacts from disk,
- computes matching summaries for `ideal_true` and `realistic_observed` modes,
- emits explicit missing reasons for undefined metrics,
- writes deterministic summary components, coverage curves, verification, and
  a compact report.

The main summary-vector entrypoints are:

- [`src/spatext/synth/small/summary_vector.py`](src/spatext/synth/small/summary_vector.py):
  disk-first loading, mode construction, summary computation, missing-metric
  handling, verification, and report rendering
- [`scripts/build_synth_small_summary_vector.py`](scripts/build_synth_small_summary_vector.py):
  command-line utility for emitting the summary-vector bundle

To build the summary-vector bundle after the observation and reconstruction
bundles exist:

```bash
uv run python scripts/build_synth_small_summary_vector.py
```

That command writes `artifacts/synth_small_summary_vector/` containing:

- `summary_vector_config.json`
- `summary_components.csv`
- `mode_summary.json`
- `coverage_curve.csv`
- `verification.json`
- `report.md`

This is a synthetic method-development layer. The bundle itself does not
perform ABC, likelihood fitting, posterior inference, parameter sweeps, or
real-data analysis.

## Implemented compatibility screen

Module 1 now also includes a synthetic-only compatibility screen over the
summary-vector bundle. It:

- reads the Goal 009 summary-vector target bundle from disk,
- evaluates both `ideal_true` and `realistic_observed` target modes,
- treats `realistic_observed` as the primary review mode,
- builds matching summaries for a tiny deterministic candidate set,
- applies documented gates and weighted-gap losses,
- exposes per-breakpoint coverage gaps behind the coverage RMSE term, and
- emits deterministic rankings, compatibility classes, invalid reasons,
  verification, and a compact report.

The main compatibility-screen entrypoints are:

- [`src/spatext/synth/small/compatibility_screen.py`](src/spatext/synth/small/compatibility_screen.py):
  target-bundle loading, candidate summary generation, gate/loss scoring,
  ranking, verification, and report rendering
- [`scripts/run_synth_small_compatibility_screen.py`](scripts/run_synth_small_compatibility_screen.py):
  command-line utility for emitting the compatibility-screen bundle

To build the compatibility-screen bundle after the summary-vector bundle
exists:

```bash
uv run python scripts/run_synth_small_compatibility_screen.py
```

That command writes `artifacts/synth_small_compatibility_screen/` containing:

- `compatibility_screen_config.json`
- `target_summary.json`
- `candidate_summaries.csv`
- `candidate_scores.csv`
- `coverage_score_breakdown.csv`
- `mode_rankings.csv`
- `verification.json`
- `report.md`

`coverage_score_breakdown.csv` contains one row per target mode, candidate, and
coverage breakpoint, with target time, candidate time, absolute gap, and
squared gap. It provides the audit trail for reconstructing the
`coverage_curve_rmse` contribution in `candidate_scores.csv`.

The default candidate is expected to rank exact or near-exact under
`ideal_true`. `realistic_observed` is the primary review target and may show
information loss from observation and reconstruction. Compatibility classes are
screen labels only; they are not likelihoods, posterior probabilities,
parameter-recovery claims, or real-data interpretation.

## Implemented compatibility mismatch audit

Module 1 now also includes a synthetic-only, disk-first audit explaining the
current `realistic_observed` compatibility mismatch. It:

- reads the emitted summary-vector, compatibility-screen, and response-screen
  evaluation bundles from disk,
- compares `ideal_true` and `realistic_observed` target summaries,
- ranks score-component contributions for the top realistic candidate,
- exposes per-breakpoint coverage gaps that reconstruct the coverage RMSE term,
- bridges the finite-target drop to response-screen false negatives, and
- emits a non-inference recommendation before any ABC, POM, fitting, posterior
  claim, parameter recovery, broad sweep, or real-data analysis.

The main mismatch-audit entrypoints are:

- [`src/spatext/synth/small/compatibility_mismatch_audit.py`](src/spatext/synth/small/compatibility_mismatch_audit.py):
  artifact loading, target-delta summaries, score-contribution summaries,
  coverage-gap summaries, bridge diagnostics, recommendation, verification,
  and report rendering
- [`scripts/audit_synth_small_compatibility_mismatch.py`](scripts/audit_synth_small_compatibility_mismatch.py):
  command-line utility for emitting the mismatch-audit bundle

To build the mismatch-audit bundle after the prerequisite summary-vector,
compatibility-screen, and response-screen evaluation bundles exist:

```bash
uv run python scripts/audit_synth_small_compatibility_mismatch.py
```

That command writes
`artifacts/synth_small_compatibility_screen/mismatch_audit/` containing:

- `mismatch_audit_config.json`
- `target_delta_summary.csv`
- `score_contribution_summary.csv`
- `coverage_gap_summary.csv`
- `evaluation_bridge_summary.json`
- `recommendation.json`
- `verification.json`
- `report.md`

The default audit currently recommends
`diagnose_observation_reconstruction_before_abc`: the `ideal_true` default
candidate is compatible, all `realistic_observed` candidates are incompatible,
and the finite-target drop of `101` matches the response-screen false-negative
count of `101`.

## Implemented false-negative mechanism audit

Module 1 now also includes a synthetic-only, disk-first audit explaining the
response-screen false negatives behind the Goal 011 finite-target bridge. It:

- reads emitted response-screen evaluation, extirpation reconstruction,
  observation, and mismatch-audit bundles from disk,
- classifies every false-negative site into one primary diagnostic mechanism,
- exposes post-extirpation survey timing, detection, and effort features per
  site,
- summarizes mechanism counts by region and front-band groups, and
- emits a non-inference recommendation before any reconstruction-rule,
  observation-design, scoring, ABC, POM, fitting, posterior, broad-sweep, or
  real-data work.

The main false-negative audit entrypoints are:

- [`src/spatext/synth/small/false_negative_mechanism_audit.py`](src/spatext/synth/small/false_negative_mechanism_audit.py):
  artifact loading, site-level timing features, primary mechanism
  classification, mechanism/group/timing summaries, recommendation,
  verification, and report rendering
- [`scripts/audit_synth_small_false_negatives.py`](scripts/audit_synth_small_false_negatives.py):
  command-line utility for emitting the false-negative audit bundle

To build the false-negative audit bundle after the response-screen evaluation,
reconstruction, observation, and mismatch-audit bundles exist:

```bash
uv run python scripts/audit_synth_small_false_negatives.py
```

That command writes
`artifacts/synth_small_response_screen/evaluation/false_negative_audit/`
containing:

- `false_negative_audit_config.json`
- `false_negative_site_audit.csv`
- `mechanism_summary.csv`
- `group_mechanism_summary.csv`
- `observation_timing_summary.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

The default audit currently classifies all `101` response-screen false
negatives as post-extirpation observation support problems:
`no_post_extirpation_surveys` (`39`),
`late_extirpation_near_survey_horizon` (`30`),
`post_extirpation_detection_blocks_absence` (`28`), and
`insufficient_post_extirpation_survey_history` (`4`). The recommendation is
`diagnose_post_extirpation_observation_gap_before_rule_change`.
The `sparse_or_low_effort_observation` diagnostic remains available after
higher-priority timing mechanisms and is now auditable through emitted
`mean_effort`, `min_effort`, `max_effort`, and post-extirpation effort
summaries.

## Implemented observation-support counterfactual screen

Module 1 now also includes a synthetic-only, evaluation-only counterfactual
screen over the Goal 012 false negatives. It:

- reads emitted response-screen evaluation, reconstruction, observation,
  false-negative audit, summary-vector, and compatibility-screen bundles from
  disk,
- keeps the production observation design and final-absence reconstruction rule
  unchanged,
- defines a small deterministic scenario set including `status_quo`,
  `truth_guided_absence_floor_all`,
  `detection_blocker_respecting_floor`, and
  `late_followup_detection_blocker_respecting`,
- verifies the existing Goal 009/010 bridge artifacts and reconciles status quo
  to the Goal 010 `realistic_observed` top ranking, and
- emits a non-inference recommendation before any reconstruction-rule,
  observation-design, scoring, ABC, POM, fitting, posterior, broad-sweep, or
  real-data work.

The main counterfactual-screen entrypoints are:

- [`src/spatext/synth/small/observation_support_counterfactual_screen.py`](src/spatext/synth/small/observation_support_counterfactual_screen.py):
  artifact loading, scenario resolution, summary-vector construction,
  compatibility scoring, recommendation, verification, and report rendering
- [`scripts/run_synth_small_observation_support_counterfactual.py`](scripts/run_synth_small_observation_support_counterfactual.py):
  command-line utility for emitting the counterfactual-screen bundle

To build the counterfactual-screen bundle after the response-screen evaluation,
reconstruction, observation, false-negative audit, summary-vector, and
compatibility-screen bundles exist:

```bash
uv run python scripts/run_synth_small_observation_support_counterfactual.py
```

That command writes
`artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/`
containing:

- `counterfactual_config.json`
- `scenario_definitions.csv`
- `site_counterfactual_resolution.csv`
- `scenario_reconstruction_summary.csv`
- `scenario_summary_vectors.csv`
- `scenario_compatibility_scores.csv`
- `scenario_rankings.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

The default counterfactual screen currently verifies the existing Goal 009/010
bridge artifacts, reconciles status quo to `151` finite targets, top candidate
`default`, class `incompatible`, and loss `3.52263635737`, and shows that the
truth-guided all-false-negative support floor restores the finite-target count
to `252` but remains incompatible. The recommendation is
`finite_target_support_improves_but_compatibility_not_restored`.

## Implemented target-timing residual decomposition

Module 1 now also includes a synthetic-only, evaluation-only target-timing
residual-decomposition diagnostic over the Goal 013 compatibility residual. It:

- reads emitted observation, reconstruction, response-screen evaluation,
  false-negative audit, observation-support counterfactual, summary-vector, and
  compatibility-screen bundles from disk,
- verifies the published Goal 009 summary-vector bridge files and the Goal 010
  compatibility-screen bridge artifacts,
- compares a small deterministic target-transform set:
  `status_quo_observed`, `goal013_support_floor`,
  `false_negative_true_time`,
  `false_negative_true_time_detection_respecting`, and
  `all_extirpated_true_time`,
- reuses the unchanged Goal 009 summary-vector helpers and Goal 010 candidate
  scoring contract, and
- emits per-transform site resolutions, summary vectors, component losses,
  rankings, and component deltas before any reconstruction-rule,
  observation-design, scoring, candidate, ABC, POM, or real-data work.
  The component-delta table includes residual contribution ranks and
  absolute-delta ranks from both `status_quo_observed` and
  `goal013_support_floor` within each transform/candidate group.

The main residual-decomposition entrypoints are:

- [`src/spatext/synth/small/target_timing_residual_decomposition.py`](src/spatext/synth/small/target_timing_residual_decomposition.py):
  artifact loading, target-transform resolution, summary-vector construction,
  compatibility scoring, component-delta accounting, recommendation,
  verification, and report rendering
- [`scripts/analyze_synth_small_target_timing_residuals.py`](scripts/analyze_synth_small_target_timing_residuals.py):
  command-line utility for emitting the residual-decomposition bundle

To build the residual-decomposition bundle after the Goal 009-013 prerequisite
bundles exist:

```bash
uv run python scripts/analyze_synth_small_target_timing_residuals.py
```

That command writes
`artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/`
containing:

- `residual_decomposition_config.json`
- `target_transform_definitions.csv`
- `site_target_transform_resolution.csv`
- `target_transform_summary_vectors.csv`
- `target_transform_component_losses.csv`
- `target_transform_rankings.csv`
- `component_delta_table.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

The default diagnostic currently shows that only
`all_extirpated_true_time` restores the Goal 010 `ideal_true` expectation for
the default candidate (`compatible`, loss `0`). The Goal 013
`goal013_support_floor` remains incompatible with default loss
`1.88500331398`; its dominant residual components are
`coverage_curve_rmse`, `lag_mean`, `front_plane_gradient_magnitude`, and
`arrival_target_r2`. The recommendation is `timing_bias_drives_residual`.

## Operating stance

The repo is intentionally being built around a few early constraints:

- one Python environment authority,
- one packaging authority,
- synthetic-first validation,
- modular design,
- auditable scientific interpretation.

That means the repository should resist avoidable tooling sprawl and should not
inherit legacy exploratory structure just because it existed elsewhere.

## Status notes

- The initial package and quality-tooling scaffold is in place.
- Module 1 `synth-small` baseline generation is implemented and verified.
- Module 1 `synth-small` inspection and verification is implemented and
  verified.
- Module 1 `synth-small` deterministic predator-response truth is implemented,
  verified, and executable as a repo-local artifact build.
- Module 1 `synth-small` deterministic predator-response truth inspection is
  implemented, verified, and executable as a repo-local artifact review step.
- Module 1 `synth-small` deterministic predator-response sensitivity/readiness
  is implemented, verified, and executable as a local decision package.
- Module 1 `synth-small` first response-only observation layer is implemented,
  verified, and executable as a local observation/recoverability-smoke package.
- Module 1 `synth-small` response-only extirpation reconstruction is
  implemented, verified, and executable as a local reconstruction package.
- Module 1 `synth-small` response-only screen is implemented as a cautious
  summary layer over the reconstructed response surface.
- Module 1 `synth-small` response-only screen inspection is implemented as a
  disk-first review layer over emitted screen artifacts.
- Module 1 `synth-small` response-screen evaluation is implemented as a
  synthetic-only diagnostic layer under an explicit evaluation namespace.
- Module 1 `synth-small` summary-vector bridge is implemented as a
  synthetic-only `S(T_X, T_P)` layer before compatibility-screen or ABC work.
- Module 1 `synth-small` compatibility screen is implemented as a
  synthetic-only deterministic ranking layer before ABC or POM work.
- Module 1 `synth-small` compatibility mismatch audit is implemented as a
  synthetic-only diagnostic layer explaining the current realistic-observed
  incompatibility before ABC or POM work.
- Module 1 `synth-small` false-negative mechanism audit is implemented as a
  synthetic-only diagnostic layer explaining response-screen false negatives
  before reconstruction-rule, observation-design, ABC, or POM work.
- Module 1 `synth-small` observation-support counterfactual screen is
  implemented as a synthetic-only, evaluation-only diagnostic layer before any
  default observation-design, reconstruction-rule, scoring, ABC, or POM change.
- Module 1 `synth-small` target-timing residual decomposition is implemented
  as a synthetic-only, evaluation-only diagnostic layer explaining the Goal 013
  residual before any reconstruction-rule, observation-design, scoring,
  candidate, ABC, or POM change.
- The report log in [`spec/report_log.md`](spec/report_log.md) tracks completed
  interactions and implementation milestones.
- Commits and remote pushes are performed only when explicitly requested.
