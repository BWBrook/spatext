# Goal 016: Synth-Small Response-Observable Timing-Rule Screen

## Objective

Build a synthetic-only, evaluation-only screen of deterministic target-time
rules that use only response-observable inputs, then test whether any such
rule can reduce the Goal 015 residual timing error and improve Goal 010
compatibility without changing production reconstruction, scoring, candidates,
or inference machinery.

This is a rule-screening diagnostic, not a rule adoption. Its purpose is to
decide whether the current synth-small response artifacts contain enough
observable signal to justify a later bounded reconstruction-rule design goal,
or whether the project should instead move toward a richer synthetic landscape
and/or explicit observation/process modelling.

## Context

Goals 009-015 have narrowed the current synth-small failure mode:

- Goal 010 showed that the default candidate is compatible under `ideal_true`
  but incompatible under `realistic_observed`.
- Goal 011 showed the finite-target drop from `ideal_true` to
  `realistic_observed` matches the `101` response-screen false negatives.
- Goal 013 showed truth-guided post-extirpation support restores finite target
  count to `252` but does not restore compatibility.
- Goal 014 showed that all true target times restore the Goal 010 ideal-truth
  compatibility expectation.
- Goal 015 showed that remaining support-floor timing error is late-biased,
  spatially structured, concentrated in already finite status-quo targets, and
  partly visible through response-observable residual-timing candidate proxies:
  `long_detection_to_target_gap`,
  `spatial_front_band_west_band_signal`, and
  `sparse_survey_history`.

Barry also raised a strategic concern: the constrained synth-small grid may be
too simple and too sparse to identify anything more nuanced than a linear wave.
This goal should therefore treat spatially keyed rule gains with caution. A
rule that works mainly because the current grid has a simple west/middle/east
front is diagnostic evidence, not a robust method claim.

## Scientific Question

Can response-observable target-time adjustment rules, built from the current
synth-small observation/reconstruction/site metadata rather than hidden truth,
recover enough target timing structure to improve compatibility; or does the
screen show that response-only diagnostics are insufficient on the current
toy system?

## In Scope

- Add `spec/synth_small_response_observable_timing_rule_screen.md`.
- Add a focused module under `src/spatext/synth/small/`, probably
  `response_observable_timing_rule_screen.py`.
- Add a CLI script, probably
  `scripts/screen_synth_small_response_observable_timing_rules.py`.
- Read existing emitted synthetic artifacts from disk.
- Define a small deterministic candidate rule set using only response-
  observable/site metadata, such as:
  - status-quo reconstructed target times;
  - last-detection to reconstructed-target gap;
  - final absence support;
  - survey sparsity and detection support;
  - site/front-band metadata;
  - simple combinations of the Goal 015 residual-timing proxy signals.
- Include truth-only and truth-guided references as benchmarks only, not
  eligible response-observable rules:
  - Goal 013 support-floor reference;
  - all-extirpated true-time reference;
  - any direct true-time transform needed to reconcile prior goals.
- Score candidate target-rule outputs through the existing summary-vector and
  compatibility-screen contract.
- Emit per-site, per-rule, per-component, and per-proxy performance artifacts.
- Classify whether candidate improvements are:
  - compatible or still incompatible;
  - driven by finite-target recovery versus timing-shape correction;
  - response-observable versus truth-guided;
  - potentially overfit to the simple grid/front-band structure.
- Update exports, README, `AGENTS.md` if the authoritative spec list changes,
  `spec/report_log.md`, and this goal log.

## Out Of Scope

- Changing default observation-design settings.
- Changing emitted default observation or reconstruction artifacts.
- Changing the production reconstruction rule or `min_final_absence_run`.
- Changing response-screen, summary-vector, compatibility-screen,
  mismatch-audit, false-negative-audit, Goal 013, Goal 014, or Goal 015 scoring
  logic.
- Adopting a new reconstruction rule as default.
- Claiming parameter recovery.
- Adding a richer landscape generator.
- Adding a POM, likelihood, MCMC, ABC, or posterior workflow.
- Real-data analysis.
- Broad parameter sweeps.
- Remote compute.
- Commit or push.

## Required Inputs

The command should read existing artifacts from disk and fail loudly if
required inputs are missing. The runbook may rebuild ignored local artifacts
using existing repo commands.

Observation and reconstruction artifacts:

- `artifacts/synth_small_observations/observation_config.json`
- `artifacts/synth_small_observations/sites.csv`
- `artifacts/synth_small_observations/visits.csv`
- `artifacts/synth_small_observations/observations.csv`
- `artifacts/synth_small_observations/evaluation_truth.csv`
- `artifacts/synth_small_observations/truth_reference.json`
- `artifacts/synth_small_extirpation_reconstruction/reconstruction_config.json`
- `artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv`
- `artifacts/synth_small_extirpation_reconstruction/time_detection_summary.csv`
- `artifacts/synth_small_extirpation_reconstruction/verification.json`

Evaluation and diagnostic artifacts:

- `artifacts/synth_small_response_screen/evaluation/screen_evaluation_summary.json`
- `artifacts/synth_small_response_screen/evaluation/site_evaluation_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/verification.json`
- `artifacts/synth_small_summary_vector/summary_vector_config.json`
- `artifacts/synth_small_summary_vector/mode_summary.json`
- `artifacts/synth_small_summary_vector/summary_components.csv`
- `artifacts/synth_small_summary_vector/coverage_curve.csv`
- `artifacts/synth_small_summary_vector/verification.json`
- `artifacts/synth_small_compatibility_screen/target_summary.json`
- `artifacts/synth_small_compatibility_screen/candidate_scores.csv`
- `artifacts/synth_small_compatibility_screen/mode_rankings.csv`
- `artifacts/synth_small_compatibility_screen/verification.json`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/site_counterfactual_resolution.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/scenario_rankings.csv`
- `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/verification.json`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/site_target_transform_resolution.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/target_transform_rankings.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/component_delta_table.csv`
- `artifacts/synth_small_response_screen/evaluation/target_timing_residual_decomposition/verification.json`
- `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/site_target_time_error_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/observable_proxy_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/recommendation.json`
- `artifacts/synth_small_response_screen/evaluation/target_time_error_anatomy/verification.json`

## Required Outputs

Write a deterministic artifact bundle under:

```text
artifacts/synth_small_response_screen/evaluation/response_observable_timing_rule_screen/
```

Required files:

- `timing_rule_screen_config.json`
- `rule_definitions.csv`
- `site_rule_resolution.csv`
- `rule_summary_vectors.csv`
- `rule_component_losses.csv`
- `rule_rankings.csv`
- `proxy_rule_performance.csv`
- `grid_simplicity_risk_audit.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

The JSON outputs must clearly label:

- `synthetic_only: true`
- `evaluation_only: true`
- `response_observable_rule_screen_only: true`
- `not_formal_inference: true`
- `no_default_observation_change: true`
- `no_reconstruction_rule_change: true`
- `no_scoring_change: true`
- `no_candidate_change: true`
- `no_richer_landscape_change: true`
- `no_pom_or_likelihood_change: true`

## Table Requirements

`rule_definitions.csv`
: One row per candidate or reference rule. Include rule ID, rule family,
  eligibility class (`response_observable`, `truth_guided_reference`,
  `truth_only_reference`, `status_quo_baseline`), response-observable source
  columns, whether the rule may assign finite targets to status-quo nonfinite
  sites, whether the rule is spatially keyed, and the interpretation.

`site_rule_resolution.csv`
: One row per site per rule. Include site ID, truth status, status-quo target,
  rule target, finite status, signed/absolute error where truth permits audit,
  rule delta from status quo, rule delta from Goal 013 support-floor reference,
  response-observable proxy flags, and whether the rule changes a nonfinite
  target to finite.

`rule_summary_vectors.csv`
: Summary-vector components for each rule target mode, using the existing
  summary-vector definitions and component names.

`rule_component_losses.csv`
: Compatibility component losses for each rule target mode against the
  existing default candidate and any existing candidate rows needed for
  reconciliation. Include absolute gaps, normalized gaps, weights, weighted
  gaps, and component ranks.

`rule_rankings.csv`
: Deterministic ranking of rules by compatibility loss, compatibility class,
  finite-target count, target-time error metrics, and eligibility class.

`proxy_rule_performance.csv`
: Stratified performance by the Goal 015 response-observable proxy roles,
  especially `long_detection_to_target_gap`,
  `spatial_front_band_west_band_signal`, and `sparse_survey_history`. Include
  affected-site counts, large-error counts, mean/median error, and whether the
  rule improves or worsens those strata.

`grid_simplicity_risk_audit.csv`
: A compact audit of whether apparent gains depend strongly on spatial/front-
  band metadata. Include at least a rule-level spatial-keyed flag, performance
  with and without spatially keyed rules where possible, and an interpretation
  of whether the current simple-grid result should be treated as overfit-prone.

## Recommendation Classes

The recommendation should classify the next project move without starting it.
Suggested classes:

- `response_observable_timing_rule_promising`: at least one eligible response-
  observable rule materially improves compatibility without being dominated by
  simple-grid spatial overfit.
- `spatial_proxy_overfit_risk`: improvement is mostly carried by front-band or
  site-position metadata and should motivate richer synthetic-landscape work
  before adopting a rule.
- `response_only_signal_insufficient`: eligible response-observable rules do
  not materially improve compatibility on the current synth-small system.
- `observation_process_model_needed`: failures point mainly to sampling noise,
  unobservability, or detection persistence rather than a deterministic
  response-side timing correction.
- `richer_synthetic_landscape_needed`: the current grid/front structure is too
  simple to adjudicate the next modelling choice.
- `timing_rule_screen_contract_failed`: prerequisite verification, accounting,
  scoring, or artifact reconciliation fails.

Do not start the recommended follow-on inside this goal.

## Acceptance Criteria

- The spec exists and is implemented.
- The CLI consumes required artifacts from disk and writes the required bundle.
- Candidate rule definitions clearly separate eligible response-observable
  rules from truth-guided and truth-only references.
- Site-rule rows reconcile one row per synth-small site per rule.
- Status-quo, Goal 013 support-floor, Goal 014 all-true, and Goal 015
  anatomy counts reconcile with prior artifacts.
- Summary-vector and compatibility-screen calculations use the existing
  contracts and component definitions.
- Rule rankings are deterministic and include compatibility class, loss,
  finite-target count, and timing-error summaries.
- Proxy-stratified performance makes clear whether Goal 015 residual-timing
  candidate proxies actually explain rule improvements.
- Spatial/front-band gains are explicitly audited as potential simple-grid
  overfit, not treated as robust method evidence.
- Recommendation classification is deterministic and does not start a rule
  change, landscape redesign, scoring change, candidate change, or inference
  workflow.
- Focused tests pass.
- Proportionate full repository validation passes.
- Generated artifacts remain unstaged.
- No commit or push is performed.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.
