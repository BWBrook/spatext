# Goal 019: Synth-Medium Observation-Design Review Pack

## Objective

Build a deterministic `synth-medium` observation-design review pack over the
published Goal 018 latent spread-impact truth, then stop for human visual and
audit-table review.

This goal creates response-only prey observation regimes. It does not
reconstruct extirpation times, fit parameters, infer posteriors, analyse real
data, or change the accepted Goal 017/018 truth contracts.

## Context

Goal 017 published the accepted `synth-medium` landscape. Goal 018 published a
deterministic predator-spread and prey-impact truth over that fixed landscape,
with selected default `balanced_corridor_detour_v2`.

Goal 019 overlays observation designs onto that latent truth. The default
regime should be a plausible imperfect response-only observation process, not
perfect observability. A full-observability regime is included only as an
upper-bound benchmark.

## In Scope

- Add `spec/synth_medium_observation_design_review_pack.md`.
- Add a focused observation-design implementation under
  `src/spatext/synth/medium/`.
- Add a CLI script for writing the review bundle.
- Add at least three deterministic regimes:
  - `truth_reference_full_observability`;
  - `structured_response_observed_default`;
  - `sparse_response_observed_stress`.
- Emit audit tables, verification JSON, Markdown report, and deterministic SVG
  visual-review files.
- Add tests, docs, report-log entry, exports, and this goal log.

## Out Of Scope

- Changing the accepted Goal 017 landscape.
- Changing the accepted Goal 018 spread-impact truth, selected default, source
  map, or visual contract.
- Observing predators as analyst-facing data.
- Reconstructing extirpation times from observations.
- Building or selecting a reconstruction rule.
- Changing synth-small scoring/classes/candidates or prior synth-medium
  artifacts.
- ABC, POM, MCMC, likelihood fitting, posterior claims, parameter recovery, or
  any back-fitting.
- Real-data analysis or the Britain mink-vole case study.
- Broad sweeps.
- Remote compute.
- Commit or push.
- Goal 020.

## Required Outputs

Generated outputs are written under:

```text
artifacts/synth_medium_observation_design/
```

Required root files:

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

Required visual review files under:

```text
artifacts/synth_medium_observation_design/visuals/
```

- `survey_effort_surface_default.svg`
- `observed_final_response_default.svg`
- `truth_observed_mismatch_default.svg`
- `post_impact_support_default.svg`
- `regime_comparison_montage.svg`
- `review_montage.svg`

## Review Gates

Verification should evaluate deterministic gates for:

- Goal 018 truth source verification and headline reconciliation;
- water cells receiving no survey records;
- full-observability benchmark coverage and no designed detection gaps;
- default-regime broad but uneven coverage;
- default-regime imperfect detection and nonzero false negatives;
- default-regime post-impact support sufficient for later review;
- default-regime timing signal not collapsing to one survey wave;
- default-regime spatial signal across habitat classes and regions;
- sparse stress regime lower information than the default;
- generated records and summaries reconciling deterministically.

## Boundary Labels

JSON outputs should include:

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

## Acceptance Criteria

- The spec exists and is implemented.
- Focused tests pass.
- The CLI writes the required table and visual bundle.
- `structured_response_observed_default` is the selected default.
- The full-observability benchmark and sparse stress regime are clearly
  labelled.
- Generated artifacts remain ignored and unstaged.
- No commit or push is performed.
- A completion/blockage wake-up is sent to the SpatExt orchestrator thread.
