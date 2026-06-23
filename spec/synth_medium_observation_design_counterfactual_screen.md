# Synth-Medium Observation-Design Recoverability Counterfactual Screen

Goal 021 adds a deterministic, synthetic-only counterfactual screen over the
accepted `synth-medium` landscape, spread-impact truth, observation design, and
response-reconstruction benchmark. The screen asks what kind of additional
response-observation support would be needed before later fitting work could be
credible.

## Scope

This module is a design-recovery screen only.

- It preserves the accepted Goal 017 landscape exactly.
- It preserves the accepted Goal 018 spread-impact truth exactly.
- It preserves the accepted Goal 019 `structured_response_observed_default`
  observation design as the published baseline.
- It preserves the accepted Goal 020 `final_absence_run_1` default benchmark
  outcome as the baseline reconstruction evidence.
- It compares a small deterministic set of counterfactual observation regimes.
- It reuses the Goal 020 benchmark reconstruction rules as diagnostics.
- It does not adopt a production observation design or reconstruction rule.
- It does not fit parameters, run ABC/POM/likelihood/MCMC/posterior workflows,
  perform parameter recovery, analyze real data, run remote compute, or start a
  follow-on goal.

## Output Contract

The CLI writes to:

```text
artifacts/synth_medium_observation_design_counterfactual_screen/
```

Required root files:

- `counterfactual_screen_config.json`
- `counterfactual_regime_definitions.csv`
- `counterfactual_observation_summary.csv`
- `counterfactual_reconstruction_rankings.csv`
- `counterfactual_support_gap_summary.csv`
- `counterfactual_error_summary.csv`
- `baseline_to_counterfactual_delta.csv`
- `recoverability_decision_summary.csv`
- `verification.json`
- `report.md`

Required visual files:

- `visuals/recoverability_decision_montage.svg`
- `visuals/support_gap_comparison_montage.svg`
- `visuals/residual_comparison_baseline_best.svg`
- `visuals/baseline_to_best_plausible_delta.svg`
- `visuals/ceiling_comparison_panel.svg`

The visual files must be self-decoding, nonempty SVGs with readable labels and
testable layout bounds for nontrivial panels. The decision-table SVG must keep
long display labels inside their assigned columns. Long rule IDs may be
shortened for display in `recoverability_decision_montage.svg`, but the full
rule IDs remain in `counterfactual_reconstruction_rankings.csv` and related
machine-readable tables.

## Regimes

The deterministic regime set is intentionally small:

- `structured_response_observed_default`: the published Goal 019 baseline,
  reconciled exactly to the Goal 020 default benchmark result.
- `post_impact_followup_boost`: plausible field-like late follow-up for cells
  with response-observable detection history.
- `final_absence_confirmation_support`: plausible field-like confirmation
  visits for cells with detection history but insufficient final-absence
  support.
- `weak_area_targeted_support`: plausible field-like extra support in
  low-quality matrix and weakly recovered west/east bands exposed by prior
  diagnostics.
- `balanced_habitat_region_support`: plausible field-like stratified support
  across habitat and region bands.
- `near_perfect_response_observation_ceiling`: unrealistic diagnostic ceiling
  based on full response visibility. It is separated from plausible regimes and
  must not support a field-like readiness claim.

## Table Contracts

`counterfactual_regime_definitions.csv`
: One row per regime with role, plausibility class, counterfactual class,
  source regime, response-observable trigger, added support semantics, and
  interpretation.

`counterfactual_observation_summary.csv`
: One row per regime with record count, surveyed cells, post-impact support,
  detection-history support, final-absence support, false negatives, mean survey
  count, mean effort, and deltas versus the published baseline.

`counterfactual_reconstruction_rankings.csv`
: One row per regime/rule with the Goal 020 ranking metrics plus baseline
  deltas and a regime-level recommendation class. Ranking within a regime uses
  the existing Goal 020 weighted loss. The cross-regime "best plausible" choice
  is a recoverability screen choice: it prioritizes finite recall and
  false-negative reduction before loss.

`counterfactual_support_gap_summary.csv`
: Support-gap summaries by regime, rule, and group, including all-passable,
  habitat, and column-band rows.

`counterfactual_error_summary.csv`
: Synthetic truth error summaries by regime, rule, and group, including finite
  recall, false positives, false negatives, median and p90 absolute error, and
  large-error counts.

`baseline_to_counterfactual_delta.csv`
: One best-rule row per regime comparing record/support effort and
  reconstruction metrics against the published baseline.

`recoverability_decision_summary.csv`
: Final deterministic decision row separating the published baseline, best
  plausible field-like counterfactual, and diagnostic ceiling.

## Baseline Reconciliation

Verification requires exact reconciliation to the published Goal 019/020
headline values:

- baseline regime: `structured_response_observed_default`
- baseline primary rule: `final_absence_run_1`
- baseline finite recall: `0.524364653765`
- false negatives: `2040`
- false positives: `304`
- large timing errors: `809`
- baseline recommendation:
  `observation_design_not_recoverable_enough_for_backfitting`

If these values drift, the Goal 021 screen must fail verification rather than
silently redefining the baseline.

## Verification Labels

JSON outputs include:

- `synthetic_only: true`
- `synth_medium_landscape_source_verified: true`
- `synth_medium_spread_impact_source_verified: true`
- `synth_medium_observation_design_source_verified: true`
- `synth_medium_response_reconstruction_source_verified: true`
- `observation_design_counterfactual_screen_only: true`
- `response_only_observation_counterfactuals: true`
- `response_only_reconstruction_benchmark_reused: true`
- `published_baseline_preserved: true`
- `ceiling_regime_is_diagnostic_only: true`
- `visual_review_required: true`
- `no_production_observation_design_adoption: true`
- `no_production_reconstruction_rule_adoption: true`
- `no_abc_pom_likelihood_or_posterior: true`
- `no_real_data: true`

## Decision Boundary

The decision must distinguish plausible field-like improvements from an
unrealistic diagnostic ceiling. A ceiling-only recovery can support the label
`only_unrealistic_observation_ceiling_recovers_signal`, but it cannot support a
claim that the published default or plausible field-like support is ready for
fitting.
