# Synth-Medium Recoverability-Target Observation-Design Review Pack

Goal 022 adds a deterministic, synthetic-only observation-design review pack
over the accepted Goal 017 landscape and Goal 018 spread-impact truth. It asks
whether a more serious but still field-plausible response-observation regime
can make response-time reconstruction credible enough for later fitting review.

## Scope

This module is a review/diagnostic layer only.

- It preserves the published Goal 017 landscape exactly.
- It preserves the published Goal 018 spread-impact truth exactly.
- It preserves the published Goal 019 default observation design as the
  baseline reference.
- It preserves the published Goal 020 response-reconstruction benchmark and
  reuses its response-only benchmark rules.
- It preserves the published Goal 021 counterfactual result as baseline
  context, including the unrealistic diagnostic ceiling.
- It does not adopt a production observation design or reconstruction rule.
- It does not fit parameters, run ABC/POM/likelihood/MCMC/posterior workflows,
  perform parameter recovery, analyze real data, run remote compute, or start a
  follow-on goal.

## Candidate Regimes

The deterministic regime set is deliberately small:

- `structured_response_observed_default`: the published Goal 019/020 baseline.
- `stratified_scheduled_panel`: field-plausible scheduled panel support across
  habitat, region, and front-band strata.
- `weak_strata_targeted_panel`: field-plausible support for weak observable
  landscape strata such as low-quality matrix, eastern bands, and water edges.
- `post_detection_confirmation_panel`: response-observable revisits after
  detected occupancy.
- `final_absence_revisit_panel`: response-observable revisits for cells with
  occupancy history but weak final-absence support.
- `high_cadence_rotating_panel`: a broad rotating panel with higher temporal
  cadence.
- `integrated_recoverability_target_panel`: the most serious field-plausible
  candidate, combining stratified scheduled support, weak-strata targeting, and
  confirmation revisits.
- `near_perfect_response_observation_ceiling`: unrealistic diagnostic ceiling
  retained as a reference only.

No field-plausible candidate uses hidden prey-extirpation truth to decide where
or when to survey. Hidden truth enters only in synthetic audit summaries after
observations and response-only reconstructions are built.

## Output Contract

The CLI writes to:

```text
artifacts/synth_medium_recoverability_target_observation_design/
```

Required root files:

- `recoverability_target_config.json`
- `regime_definitions.csv`
- `observation_effort_summary.csv`
- `strata_effort_summary.csv`
- `reconstruction_benchmark_summary.csv`
- `support_gap_summary.csv`
- `baseline_to_candidate_delta.csv`
- `readiness_decision_summary.csv`
- `verification.json`
- `report.md`

Required visual files:

- `visuals/effort_support_surfaces.svg`
- `visuals/support_gap_maps.svg`
- `visuals/residual_maps.svg`
- `visuals/recoverability_decision_montage.svg`
- `visuals/ceiling_reference_panel.svg`

Visuals must be self-decoding SVGs with legends/decode keys on map panels and a
bounded decision-table layout that avoids clipped or overlapping text.

## Table Contracts

`regime_definitions.csv`
: One row per regime with role, plausibility class, counterfactual class,
  response-observable trigger, additional support semantics, hidden-truth-use
  flag, and interpretation.

`observation_effort_summary.csv`
: One row per regime with survey records, surveyed cells, post-impact support,
  detection-history support, post-detection support, final-absence support,
  false negatives, effort, and deltas versus baseline.

`strata_effort_summary.csv`
: Regime-level effort and support summaries by all passable cells, habitat
  class, column/front band, and row band.

`reconstruction_benchmark_summary.csv`
: One row per regime/rule with Goal 020 benchmark metrics, baseline deltas,
  loss, rank, and regime recommendation class.

`support_gap_summary.csv`
: Response-only support-gap summaries for each regime/rule and group.

`baseline_to_candidate_delta.csv`
: One best-rule row per regime comparing recall, false negatives, false
  positives, specificity, precision, timing errors, large errors, loss, and
  effort/support deltas against the published baseline.

`readiness_decision_summary.csv`
: Final deterministic decision row separating baseline, best field-plausible
  candidate, lowest-effort ready field-plausible candidate, and diagnostic
  ceiling. The best field-plausible candidate is selected by explicit criteria,
  not by regime ID: readiness class first, then lower loss, lower false
  negatives, lower large errors, higher finite recall, lower false positives,
  and stable regime ID as the final tie-breaker. The decision row also carries
  observation-effort burden fields for the baseline, best field-plausible
  candidate, lowest-effort ready candidate, and ceiling reference: survey record
  count, deltas and ratios versus baseline and ceiling, surveyed-cell count, and
  final-absence support count.

The decision layer deliberately separates the best-performing ready candidate
from the lowest-effort ready candidate. If both exist and differ, the final
recommendation should be read as a recoverability/logistics review gate: the
scientific signal can be made recoverable under high-intensity field-plausible
designs, but Barry still needs to judge whether the effort burden is acceptable
before any fitting work is considered.

## Baseline Reconciliation

Verification requires exact reconciliation to the published Goal 020 baseline:

- baseline regime: `structured_response_observed_default`
- baseline primary rule: `final_absence_run_1`
- finite recall: `0.524364653765`
- false negatives: `2040`
- false positives: `304`
- large timing errors: `809`

Verification also records Goal 017/018/019/021 source reconciliation.

## Recommendation Labels

The final recommendation is one of:

- `recoverability_review_ready`
- `plausible_design_improves_but_process_model_needed`
- `only_unrealistic_observation_ceiling_recovers_signal`
- `recoverability_target_design_blocked`

`recoverability_review_ready` is allowed only when a field-plausible candidate,
not the diagnostic ceiling, meets the deterministic reconstruction-review gates.
It is not an authorization to fit; it indicates that at least one
field-plausible observation design is worth human recoverability and logistics
review.

## Verification Labels

JSON outputs include:

- `synthetic_only: true`
- `recoverability_target_observation_design_review_only: true`
- `synth_medium_landscape_source_verified: true`
- `synth_medium_spread_impact_source_verified: true`
- `synth_medium_observation_design_source_verified: true`
- `synth_medium_response_reconstruction_source_verified: true`
- `synth_medium_observation_design_counterfactual_source_verified: true`
- `response_only_observation_designs: true`
- `response_only_reconstruction_benchmark_reused: true`
- `published_baseline_preserved: true`
- `ceiling_regime_is_diagnostic_only: true`
- `visual_review_required: true`
- `no_production_observation_design_adoption: true`
- `no_production_reconstruction_rule_adoption: true`
- `no_abc_pom_likelihood_or_posterior: true`
- `no_real_data: true`
