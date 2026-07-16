# AGENTS.md

This file is the repo-local archive guide for `spatext`. Repo-local
instructions here override machine-wide defaults where relevant.

## Archive mode

Goal 022 at commit `53462d0365babf2c8070714a930f69b4071af276` is the last
accepted scientific checkpoint. After the single documentation-only archival
administration commit, treat `main` as read-only. The blocked Goal 023 work is
preserved separately on
`archive/goal023-latent-response-observation-gate`; it is not accepted or
published. Active development continues in the private successor programme,
`BWBrook/latent-landscapes`.

Permitted work in this repository is limited to:

- read-only inspection; and
- explicitly authorized, bounded provenance extraction that preserves source
  identity and reports the exact material extracted.

Do not:

- add or change scientific implementation, specifications, tests, or
  dependencies;
- create new goal packets or extend an unfinished goal;
- run workflows that create generated outputs, artifacts, caches, builds, or
  environments; or
- commit, push, tag, publish, or otherwise expose repository content without
  separate explicit authorization.

The historical sections below describe the archived repository. They do not
authorize renewed implementation.

## Historical purpose

`spatext` exists to support response-only spatiotemporal extinction inference.
The scientific framing lives first in [`spec/problem_statement.md`](spec/problem_statement.md).

The working proposition is:

> Spatial extinction dynamics can sometimes be inferred from response-only
> observations, but only if the workflow explicitly models observation
> limitations, validates recoverability under synthetic truth, and treats
> low-information failure as part of the scientific result.

## Historical authoritative documents

- Scientific framing: [`spec/problem_statement.md`](spec/problem_statement.md)
- Mathematical theory: [`spec/theory.md`](spec/theory.md)
- Tooling contract: [`spec/tooling_bootstrap.md`](spec/tooling_bootstrap.md)
- Module specs under `spec/`, including
  [`spec/synth_small_baseline.md`](spec/synth_small_baseline.md) and
  [`spec/synth_small_inspection.md`](spec/synth_small_inspection.md) and
  [`spec/synth_small_predator_truth.md`](spec/synth_small_predator_truth.md)
  and
  [`spec/synth_small_predator_truth_inspection.md`](spec/synth_small_predator_truth_inspection.md)
  and
  [`spec/synth_small_predator_truth_sensitivity.md`](spec/synth_small_predator_truth_sensitivity.md)
  and
  [`spec/synth_small_observations.md`](spec/synth_small_observations.md)
  and
  [`spec/synth_small_summary_vector.md`](spec/synth_small_summary_vector.md)
  and
  [`spec/synth_small_compatibility_screen.md`](spec/synth_small_compatibility_screen.md)
  and
  [`spec/synth_small_compatibility_mismatch_audit.md`](spec/synth_small_compatibility_mismatch_audit.md)
  and
  [`spec/synth_small_false_negative_mechanism_audit.md`](spec/synth_small_false_negative_mechanism_audit.md)
  and
  [`spec/synth_small_observation_support_counterfactual_screen.md`](spec/synth_small_observation_support_counterfactual_screen.md)
  and
  [`spec/synth_small_target_timing_residual_decomposition.md`](spec/synth_small_target_timing_residual_decomposition.md)
  and
  [`spec/synth_small_target_time_error_anatomy_audit.md`](spec/synth_small_target_time_error_anatomy_audit.md)
  and
  [`spec/synth_small_response_observable_timing_rule_screen.md`](spec/synth_small_response_observable_timing_rule_screen.md)
  and
  [`spec/synth_medium_landscape.md`](spec/synth_medium_landscape.md)
  and
  [`spec/synth_medium_spread_impact_review_pack.md`](spec/synth_medium_spread_impact_review_pack.md)
  and
  [`spec/synth_medium_observation_design_review_pack.md`](spec/synth_medium_observation_design_review_pack.md)
  and
  [`spec/synth_medium_response_reconstruction_benchmark.md`](spec/synth_medium_response_reconstruction_benchmark.md)
  and
  [`spec/synth_medium_observation_design_counterfactual_screen.md`](spec/synth_medium_observation_design_counterfactual_screen.md)
  and
  [`spec/synth_medium_recoverability_target_observation_design.md`](spec/synth_medium_recoverability_target_observation_design.md)
- Operational build history: [`spec/report_log.md`](spec/report_log.md)

During active development, `spec/` was the primary design authority. These
documents now remain historical contracts, not instructions to resume
implementation.

## Historical working roles

- The user provides short task prompts and higher-level direction through spec
  documents and repo discussion.
- The code architect agent is referred to in repo docs as `spat`.

## Historical operating principles

- Keep scientific specification separate from implementation details.
- Prefer modular, auditable components over exploratory script piles.
- Treat synthetic validation as a hard gate before real-data interpretation.
- Make assumptions explicit when they affect inference, workflow, or
  conclusions.
- Bias toward reversible, low-sprawl decisions in the early repo phase.
- Treat negative or weak-information results as legitimate scientific outcomes,
  not hidden failures.

## Historical repository workflow

- Use `uv` as the single Python environment and dependency authority.
- Use `pyproject.toml` as the single packaging and metadata authority.
- Keep the package in `src/spatext/`.
- Keep tests in `tests/`.
- Keep small repo utilities in `scripts/`, but do not place core library logic
  there.
- When verifying artifact contracts, prefer disk-first inspection layers that
  consume emitted bundles rather than silently reusing live in-memory objects.
- Do not introduce `pixi`, notebooks, or alternative dependency manifests
  unless a later approved spec justifies them.

## Git hygiene

- Do not create commits unless the user explicitly asks.
- Do not push to a remote unless the user explicitly asks.
- Prefer bundled commits over highly atomic commits unless the user asks
  otherwise.
- Do not revert user changes unless explicitly instructed.

## Archive verification

Do not rerun scientific tests, builds, artifact generation, or environment
setup as routine archive work. For an explicitly authorized provenance
extraction or archive-administration change, use only the read-only or
documentation checks named in that authorization and report exactly what was
run.

## Archive records

- [`README.md`](README.md) is the public archive orientation.
- [`docs/archive_status.md`](docs/archive_status.md) records the transition,
  accepted endpoint, archival branch, planned tag, and successor programme.
- Existing goal packets and [`spec/report_log.md`](spec/report_log.md) remain
  historical provenance and must not be extended.
