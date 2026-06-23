# AGENTS.md

This file is the repo-local operating guide for `spatext`. It should evolve as
the repository matures. Repo-local instructions here override the machine-wide
defaults where relevant.

## Purpose

`spatext` exists to support response-only spatiotemporal extinction inference.
The scientific framing lives first in [`spec/problem_statement.md`](spec/problem_statement.md).

The working proposition is:

> Spatial extinction dynamics can sometimes be inferred from response-only
> observations, but only if the workflow explicitly models observation
> limitations, validates recoverability under synthetic truth, and treats
> low-information failure as part of the scientific result.

## Current authoritative documents

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

During the current phase of the repo, `spec/` is the primary design authority.
Implementation should follow these documents rather than inventing parallel
plans.

## Working roles

- The user provides short task prompts and higher-level direction through spec
  documents and repo discussion.
- The code architect agent is referred to in repo docs as `spat`.

## Operating principles

- Keep scientific specification separate from implementation details.
- Prefer modular, auditable components over exploratory script piles.
- Treat synthetic validation as a hard gate before real-data interpretation.
- Make assumptions explicit when they affect inference, workflow, or
  conclusions.
- Bias toward reversible, low-sprawl decisions in the early repo phase.
- Treat negative or weak-information results as legitimate scientific outcomes,
  not hidden failures.

## Repo workflow

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

## Quality expectations

Before declaring substantial work complete, prefer to run the relevant subset
of:

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run pre-commit run --all-files
```

Run only what is proportionate to the change, but do not claim verification
that was not actually performed.

## Documentation maintenance

- Update [`spec/report_log.md`](spec/report_log.md) as meaningful interactions
  are completed so the repo keeps an auditable progress log.
- Treat `README.md` as the public orientation document for the current state of
  the repository.
- After substantial implementation work, review both `README.md` and
  `AGENTS.md` and update them if the repo's behavior, commands, workflow, or
  documented module state has changed.
- Add new spec files in `spec/` when decisions need durable rationale or
  explicit implementation contracts.

## Phase-0 status

The repo is currently in early bootstrap. Optimize for:

- clean package structure,
- explicit contracts,
- reproducible tooling,
- auditable workflow,
- low-friction evolution into simulation, inference, summaries, diagnostics,
  and case-study applications.
