# Synth-Medium Spread-Impact Review Pack

Goal 018 adds a deterministic predator-spread and prey-impact review pack over
the accepted Goal 017 `synth-medium` landscape. The result is a synthetic truth
object for human visual and audit-table review only. It is not a fitted model
and it is not evidence for a real-data claim.

## Scope

This module simulates latent predator spread and prey impact over the fixed
Goal 017 landscape.

- It uses the accepted landscape exactly as the substrate.
- It may compare a small bounded set of named parameter candidates.
- It selects one deterministic default scenario for review.
- It does not create observations or reconstruct extirpation from
  observations.
- It does not change synth-small or synth-medium landscape contracts, response
  rules, summary vectors, compatibility screens, candidates, classes, ABC, POM,
  likelihood, posterior, or real-data workflows.

## Default Model

The default spread process is graph based. Source-zone cells on the western
frontier seed predator pressure at time zero. Water cells are excluded from
the passable graph and are never colonized.

Each passable habitat class has a deterministic conductance:

- source zones and corridors are high-conductance support/movement habitat;
- high-quality patches are relatively permeable;
- medium-quality cells are intermediate;
- low-quality matrix cells are passable but slow.

Predator arrival time is the minimum weighted graph travel time from any
source-zone cell. The selected source-zone contribution is the source that
achieves the lowest travel cost for each cell.

Prey baseline abundance is tied to the Goal 017 habitat quality surface.
After predator arrival, prey impact/extirpation timing is deterministic and
lags arrival by a habitat-, pressure-, and distance-conditioned amount. The
lag distribution is nonzero and intentionally not constant, so prey impact is
related to predator arrival without being identical to it.

## Bounded Candidate Tuning

The default candidate set is small and deterministic. Each row in
`parameter_candidate_log.csv` records:

- candidate ID;
- movement scale;
- matrix friction;
- corridor/source/high-quality conductance multipliers;
- predator horizon;
- prey-impact strength;
- quasi-extirpation fraction;
- key diagnostic counts; and
- whether the candidate was selected or rejected with rationale.

Candidate tuning is not optimization and does not use any posterior,
likelihood, fitting criterion, or real-data target.

## Output Contract

The CLI writes to:

```text
artifacts/synth_medium_spread_impact/
```

Required files:

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

Required visual files:

- `visuals/predator_arrival_time.svg`
- `visuals/predator_occupancy_snapshots.svg`
- `visuals/prey_abundance_snapshots.svg`
- `visuals/prey_impact_time.svg`
- `visuals/source_contribution_map.svg`
- `visuals/arrival_impact_lag.svg`
- `visuals/review_montage.svg`

## Table Contracts

`cell_truth.csv`
: One row per Goal 017 landscape cell. Includes landscape fields, water and
  habitat labels, predator arrival, selected source, final occupancy, prey
  baseline, final abundance, impact/extirpation timing, lag, and review bands.

`time_series_summary.csv`
: One row per review time with predator occupancy counts, impact/extirpation
  counts, and mean prey abundance over passable cells.

`source_contribution_summary.csv`
: One `source_contribution` row per contributing source zone plus one
  `uncolonized_passable_accounting` row. Source rows report
  `source_contribution_fraction_of_colonized_passable`, whose denominator is
  `final_colonized_passable_count` and whose threshold drives the material
  source count. The uncolonized accounting row separately reports
  `uncolonized_passable_count` and
  `uncolonized_passable_fraction_of_all_passable`, whose denominator is
  `all_passable_count`. This keeps source-contribution shares distinct from
  uncolonized-passable accounting.

`habitat_class_timing_summary.csv`
: Timing and abundance summaries by habitat class, including conductance.

`corridor_barrier_effect_summary.csv`
: Descriptive summaries for corridor cells, low-quality matrix,
  water-adjacent passable cells, non-water-adjacent passable cells, and the
  narrower water-adjacent/non-water-adjacent low-quality-matrix contrast used
  to audit water detours without confounding the signal with corridor or patch
  cells.

`prey_impact_summary.csv`
: Impact/extirpation timing, lag, and abundance summaries at landscape and
  habitat-review levels.

`recoverability_proxy_summary.csv`
: Deterministic proxy indicators for whether the truth object has enough
  finite targets, timing variation, lag variation, source contribution, and
  barrier/corridor signal to be worth later review. Timing proxy IDs are
  `arrival_time_range` and `impact_lag_range`; their observed values are
  full ranges (`max - min`), not interquartile ranges.

## Verification Labels

JSON outputs include:

- `synthetic_only: true`
- `synth_medium_landscape_source_verified: true`
- `spread_impact_review_only: true`
- `visual_review_required: true`
- `parameter_tuning_bounded: true`
- `no_observation_model: true`
- `no_reconstruction_or_inference: true`
- `no_abc_pom_likelihood_or_posterior: true`
- `no_real_data: true`

## Review Gates

`verification.json` evaluates:

- required artifact and visual files;
- Goal 017 cell-count reconciliation;
- water never colonized and no prey dynamics assigned to water;
- source-zone seeding and contribution;
- nontrivial spread that is not instantaneous saturation;
- broad predator-arrival distribution;
- informative prey impact/extirpation count and timing distribution;
- nonzero lag distribution;
- at least two material source-zone contributions;
- habitat conductance gradient;
- water/barrier detour signal, evaluated as a low-quality-matrix
  water-adjacent contrast;
- recoverability proxy readiness.

If a gate fails, the recommendation is `spread_impact_review_blocked`. If
gates pass, the recommendation is `ready_for_human_spread_impact_review`.
