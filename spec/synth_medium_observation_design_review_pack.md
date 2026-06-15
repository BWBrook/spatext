# Synth-Medium Observation-Design Review Pack

Goal 019 adds a deterministic observation-design review pack over the
published Goal 018 `synth-medium` spread-impact truth. It creates response-only
prey observation records and audit tables for human review before any
reconstruction, fitting, inference, or real-data work begins.

## Scope

This module overlays observations onto the accepted Goal 018 latent truth.

- It uses the accepted Goal 018 selected default exactly as the source truth.
- It emits prey response observations, not predator observations.
- It includes a full-observability benchmark, an imperfect default regime, and
  a sparse low-information stress regime.
- It does not reconstruct extirpation times from observations.
- It does not change Goal 017 landscape or Goal 018 spread-impact contracts.
- It does not run ABC, POM, likelihood, MCMC, posterior, parameter recovery,
  fitting, real-data, broad-sweep, or remote-compute workflows.

## Observation Regimes

`truth_reference_full_observability`
: Benchmark only. It records complete passable-cell coverage at review times
  with perfect response visibility. It is not the selected default and is not a
  plausible field survey design.

`structured_response_observed_default`
: Selected default. It is a deterministic but imperfect response-only
  observation process with uneven spatial and temporal effort, habitat and
  region effects, imperfect detection, post-impact survey gaps, and nonzero
  false negatives.

`sparse_response_observed_stress`
: Low-information stress test. It is intentionally weaker than the default and
  should expose where response-only recovery would become fragile or fail.

## Output Contract

The CLI writes to:

```text
artifacts/synth_medium_observation_design/
```

Required files:

- `observation_design_config.json`
- `regime_summary.csv`
- `survey_schedule.csv`
- `observation_records.csv`
- `cell_observation_summary.csv`
- `truth_observation_bridge.csv`
- `false_negative_summary.csv`
- `coverage_gap_summary.csv`
- `effort_by_habitat_region_summary.csv`
- `recoverability_signal_summary.csv`
- `verification.json`
- `report.md`

Required visual files:

- `visuals/survey_effort_surface_default.svg`
- `visuals/observed_final_response_default.svg`
- `visuals/truth_observed_mismatch_default.svg`
- `visuals/post_impact_support_default.svg`
- `visuals/regime_comparison_montage.svg`
- `visuals/review_montage.svg`

The visual review contract is intentionally human-facing:

- `regime_comparison_montage.svg` must use a readable table-like or otherwise
  non-overlapping layout with short metric labels, visible metric values, and
  bars for coverage, post-impact support, false negatives, and detection rate.
  Its content must fit inside the SVG width/viewBox with explicit right margin
  so normal preview tools do not clip the rightmost metric column.
- The map SVGs and review montage must include embedded legends or decode keys
  for survey effort, final observed status, truth/observed mismatch, and
  post-impact support.
- `review_montage.svg` must reserve non-overlapping panel boxes for title,
  map, and legend regions. The generated SVG should expose deterministic panel
  layout bounds so tests can verify lower-panel titles do not collide with
  upper-panel legends.
- Legends must explicitly distinguish water/not-passable background,
  no-survey or no-support cells, true observed response, false negatives, and
  not-extirpated/uninformative cells where those semantics appear.

## Table Contracts

`regime_summary.csv`
: One row per regime with role, selected-default flag, coverage, survey record
  counts, false negatives, post-impact support, detected timing range,
  recoverability signal, and recommendation-relevant interpretation.

`survey_schedule.csv`
: One row per conducted response-only survey visit. It includes regime, cell,
  survey time, effort, habitat/region metadata, and deterministic design
  weights. Water cells must not appear.

`observation_records.csv`
: Analyst-facing response-only prey observations. It includes regime, visit,
  cell, time, effort, passability, observed count, and detected flag. It must
  not include predator arrival, predator occupancy, source contribution, true
  extirpation, or latent prey-abundance columns.

`cell_observation_summary.csv`
: One row per passable cell and regime with coverage, detection, pre-impact
  and post-impact support, last detection, first post-impact non-detection,
  and observed response-change status.

`truth_observation_bridge.csv`
: Synthetic-only audit bridge joining the latent Goal 018 truth to
  observation outcomes. This table may include truth fields because it is
  explicitly not analyst-facing.

`false_negative_summary.csv`
: Regime-level and grouped counts for true finite prey extirpations that are
  not observed as response changes under the regime.

`coverage_gap_summary.csv`
: Regime-level and grouped coverage gaps, including no-survey, no-pre-impact
  support, no-post-impact support, and long-gap diagnostics.

`effort_by_habitat_region_summary.csv`
: Effort and detection summaries by habitat class and coarse region/source
  bands.

`recoverability_signal_summary.csv`
: Deterministic review proxies for whether each regime retains enough
  response-only signal for later reconstruction/back-fitting review.

## Verification Labels

JSON outputs include:

- `synthetic_only: true`
- `synth_medium_spread_impact_source_verified: true`
- `observation_design_review_only: true`
- `response_only_observations: true`
- `full_observability_is_benchmark_only: true`
- `selected_default_is_imperfect_observation: true`
- `visual_review_required: true`
- `no_reconstruction_or_inference: true`
- `no_abc_pom_likelihood_or_posterior: true`
- `no_real_data: true`

## Review Gates

`verification.json` evaluates:

- required artifact and visual files;
- Goal 018 source truth reconciliation;
- water cells receiving no survey records;
- full-observability benchmark coverage and designed lack of detection gaps;
- default-regime broad but incomplete and uneven coverage;
- default-regime imperfect detection and nonzero false negatives;
- default-regime post-impact support;
- default-regime timing and spatial signal retention;
- sparse stress regime lower information than the default;
- record/table reconciliation.

If a gate fails, the recommendation is `observation_design_review_blocked`.
If gates pass, the recommendation is `ready_for_human_observation_design_review`.
