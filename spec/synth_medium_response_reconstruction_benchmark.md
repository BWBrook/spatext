# Synth-Medium Response Reconstruction Benchmark Review Pack

Goal 020 adds a deterministic response-time reconstruction benchmark over the
published Goal 019 `synth-medium` observation design and the fixed Goal 018
latent spread-impact truth. It asks whether the accepted default observation
regime contains enough response-only signal to justify later back-fitting
work.

## Scope

This module reconstructs response/extirpation proxy times from response-only
observation records.

- It uses the accepted Goal 017 landscape, Goal 018 spread-impact truth, and
  Goal 019 observation regimes exactly as source inputs.
- It evaluates the Goal 019 full-observability benchmark, structured default,
  and sparse stress regimes.
- It emits response-only reconstructed times first, then joins hidden truth
  only in synthetic audit bridge tables.
- It does not adopt a production reconstruction rule.
- It does not change observation design, spread-impact truth, landscape,
  synth-small scoring/classes/candidates, ABC, POM, likelihood, posterior,
  fitting, parameter recovery, broad-sweep, remote-compute, or real-data
  workflows.

## Reconstruction Rules

The benchmark uses a small deterministic set of response-observable rules:

`final_absence_run_2`
: Conservative final-absence rule. A cell needs detection history plus at
  least two final surveyed non-detection times after the last detection. The
  reconstructed response time is the first time in that final absence run.

`final_absence_run_1`
: Timing-sensitive final-absence rule. A cell needs detection history plus at
  least one final surveyed non-detection after the last detection. The
  reconstructed response time is the first time in that final absence run.

`midpoint_after_last_detection`
: Interval-censored timing rule. A cell needs the same support as
  `final_absence_run_1`, but the reconstructed response time is the midpoint
  between the last detection and first final absence.

All rules are benchmark-only. Rule definitions record `uses_hidden_truth =
false`; hidden truth enters only after reconstruction in the audit bridge and
summary tables.

## Output Contract

The CLI writes to:

```text
artifacts/synth_medium_response_reconstruction_benchmark/
```

Required files:

- `response_reconstruction_config.json`
- `reconstruction_rule_definitions.csv`
- `reconstructed_cell_times.csv`
- `truth_reconstruction_bridge.csv`
- `reconstruction_error_summary.csv`
- `rule_regime_rankings.csv`
- `support_gap_summary.csv`
- `recoverability_signal_summary.csv`
- `verification.json`
- `report.md`

Required visual files:

- `visuals/truth_response_time.svg`
- `visuals/default_primary_reconstructed_time.svg`
- `visuals/default_primary_residual_error.svg`
- `visuals/default_primary_support_gap.svg`
- `visuals/regime_rule_comparison_montage.svg`
- `visuals/review_montage.svg`

The visual contract is human-facing and testable. Map SVGs include embedded
legends for water/not-passable cells, finite/nonfinite timing, residual-error
direction, and support gaps. The regime/rule comparison SVG uses a bounded
table layout with visible labels, bars, and values for recall, median error,
large errors, and loss. The review montage exposes deterministic panel layout
bounds so tests can catch clipping or legend/title overlap.

## Table Contracts

`reconstruction_rule_definitions.csv`
: One row per benchmark rule with rule ID, support threshold, time estimator,
  source columns, and hidden-truth-use flag.

`reconstructed_cell_times.csv`
: Analyst-facing reconstructed response times. It includes regime, rule, cell,
  habitat/region bands, survey/detection counts, final absence support,
  reconstructed time/status, and support class. It must not include predator
  arrival, prey impact/extirpation truth, signed error, absolute error, or
  true finite labels.

`truth_reconstruction_bridge.csv`
: Synthetic-only audit bridge joining reconstructed response times to Goal 018
  true prey quasi-extirpation times. This table may include truth fields and
  error classifications because it is explicitly not analyst-facing.

`reconstruction_error_summary.csv`
: Regime/rule summaries by all passable cells, habitat class, row band, and
  column band. It reports finite reconstruction counts, TP/FP/FN/TN counts,
  recall, specificity, precision, signed/absolute timing errors, and large
  error counts.

`rule_regime_rankings.csv`
: One row per regime/rule with deterministic loss and rank. Lower loss is
  better. The loss combines finite-recall failure, false positives, large
  errors, median absolute error, and p90 absolute error. It is a review
  diagnostic, not a fitting objective.

`support_gap_summary.csv`
: Response-only support accounting for never-surveyed cells, no-detection
  history, missing post-detection surveys, final absence support, and finite
  reconstruction support.

`recoverability_signal_summary.csv`
: Deterministic review proxies for the full-observability positive control,
  default nontrivial reconstruction, default error distribution, default
  support gaps, and sparse-stress lower-information contrast.

## Verification Labels

JSON outputs include:

- `synthetic_only: true`
- `synth_medium_landscape_source_verified: true`
- `synth_medium_spread_impact_source_verified: true`
- `synth_medium_observation_design_source_verified: true`
- `response_reconstruction_benchmark_only: true`
- `response_only_reconstruction_rules: true`
- `full_observability_is_benchmark_only: true`
- `selected_default_is_imperfect_observation: true`
- `visual_review_required: true`
- `no_production_reconstruction_rule_adoption: true`
- `no_abc_pom_likelihood_or_posterior: true`
- `no_real_data: true`

## Review Gates

`verification.json` evaluates:

- required artifact and visual files;
- source reconciliation against Goal 017/018/019 headline counts;
- response-only schema boundaries for `reconstructed_cell_times.csv`;
- full-observability positive-control behavior;
- nontrivial default-regime finite reconstruction;
- default-regime error distribution and spatial audit tables;
- sparse stress lower-information contrast;
- deterministic row-count reconciliation; and
- visual contract presence.

The recommendation is one of:

- `response_reconstruction_ready_for_human_review`
- `default_observation_design_recoverability_marginal`
- `observation_design_not_recoverable_enough_for_backfitting`

The recommendation is deliberately skeptical. A pretty default map is not
enough; the default regime must retain finite support and auditable timing
accuracy beyond the sparse stress contrast.
