# Goal 018: Synth-Medium Spread-Impact Review Pack

## Objective

Build a deterministic `synth-medium` predator-spread and prey-impact
simulation review pack over the accepted Goal 017 landscape, then stop for
human visual and audit-table review.

The output should let Barry inspect whether the spatio-temporal predator
progression is ecologically plausible and whether the resulting latent truth
has enough timing and spread signal to justify later back-fitting work.

This goal is synthetic-only and review-only. It may tune a small number of
named parameter candidates to find a plausible default scenario, but it must
not start fitting, inference, observations, reconstruction, ABC, POM,
likelihood, posterior, parameter recovery, real-data analysis, broad sweeps,
remote compute, Goal 019, commit, or push work.

## Context

Goal 017 created and published an accepted `synth-medium` landscape review
pack:

- a `72 x 84` grid;
- coherent impassable water components;
- low-quality matrix;
- medium-quality transition zones;
- high-quality patches;
- corridors; and
- three western source zones.

Barry approved that landscape after visual and scientific sanity checking.
Goal 018 is the next bounded step: simulate predator spread and prey impact
across that fixed substrate, while keeping the result as a review artifact
rather than an inference result.

## In Scope

- Add `spec/synth_medium_spread_impact_review_pack.md`.
- Add a focused implementation under `src/spatext/synth/medium/`.
- Add a CLI script, expected as
  `scripts/simulate_synth_medium_spread_impact.py`.
- Use the accepted Goal 017 landscape exactly as the substrate.
- Build a deterministic graph-based spread process with:
  - multiple western source zones;
  - water excluded from spread and prey dynamics;
  - habitat-quality and corridor/source conductance effects;
  - source-specific contribution labels;
  - spatially variable spread timing;
  - prey baseline abundance tied to habitat quality; and
  - prey decline/impact/extirpation timing with nonzero lag after predator
    arrival.
- Emit audit tables, verification JSON, Markdown report, and deterministic SVG
  review visuals.
- Record a small bounded parameter-candidate log and selected default scenario.
- Add tests, docs, report-log entry, and this goal log.

## Out Of Scope

- Modifying the accepted Goal 017 landscape design or contract.
- Observation models.
- Extirpation reconstruction from observations.
- Synth-small scoring, classes, candidates, compatibility, response-rule,
  mismatch, false-negative, Goal 013, Goal 014, Goal 015, or Goal 016 changes.
- ABC, POM, MCMC, likelihood fitting, posterior claims, parameter recovery, or
  other back-fitting.
- Real-data analysis or the Britain mink-vole case study.
- Broad parameter sweeps.
- Remote compute.
- Commit or push.
- Goal 019.

## Required Outputs

Write generated outputs under:

```text
artifacts/synth_medium_spread_impact/
```

Required root files:

- `simulation_config.json`
- `parameter_candidate_log.csv`
- `cell_truth.csv`
- `time_series_summary.csv`
- `source_contribution_summary.csv`
- `habitat_class_timing_summary.csv`
- `corridor_barrier_effect_summary.csv`
- `prey_impact_summary.csv`
- `recoverability_proxy_summary.csv`
- `verification.json`
- `report.md`

Required visual review files under:

```text
artifacts/synth_medium_spread_impact/visuals/
```

- `predator_arrival_time.svg`
- `predator_occupancy_snapshots.svg`
- `prey_abundance_snapshots.svg`
- `prey_impact_time.svg`
- `source_contribution_map.svg`
- `arrival_impact_lag.svg`
- `review_montage.svg`

## Review Gates

Verification should evaluate deterministic gates for:

- Goal 017 landscape source verification;
- required file and visual contract;
- cell-count reconciliation with Goal 017;
- water never colonized and excluded from prey dynamics;
- source zones seeding spread;
- nontrivial but not instantaneously saturated final spread;
- broad predator-arrival distribution;
- informative prey impact/extirpation count and timing distribution;
- nonzero arrival-impact lag distribution;
- at least two material source-zone contributions, or explicit dominance
  reporting;
- habitat conductance gradient between low-quality matrix and corridor/source
  habitat;
- barrier/water detour signal; and
- recoverability proxy readiness for later review.

## Boundary Labels

JSON outputs should include:

- `synthetic_only: true`
- `synth_medium_landscape_source_verified: true`
- `spread_impact_review_only: true`
- `visual_review_required: true`
- `parameter_tuning_bounded: true`
- `no_observation_model: true`
- `no_reconstruction_or_inference: true`
- `no_abc_pom_likelihood_or_posterior: true`
- `no_real_data: true`

## Acceptance Criteria

- The spec exists and is implemented.
- Focused tests pass.
- The CLI writes the required table and visual bundle.
- The selected default is recorded in the candidate log.
- Review gates pass or are explicitly reported if blocked.
- Generated artifacts remain ignored and unstaged.
- No commit or push is performed.
- A completion/blockage wake-up is sent to the SpatExt orchestrator thread.
