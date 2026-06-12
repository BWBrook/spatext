# Goal 013: Post-Extirpation Observation-Support Counterfactual Screen

## Objective

Build a synthetic-only, evaluation-only counterfactual screen that asks whether
the current `realistic_observed` incompatibility can be resolved by improving
post-extirpation observation support under the existing reconstruction rule.

This goal is a decision-support layer. It should not change the default
observation generator, the reconstruction rule, the response screen, the
summary-vector contract, compatibility scoring, candidate definitions, or any
inference machinery.

## Context

Goals 009-012 established the current diagnostic ladder:

- Goal 009 added the `S(T_X, T_P)` summary-vector bridge.
- Goal 010 showed that the default candidate is compatible under `ideal_true`
  but incompatible under `realistic_observed`.
- Goal 011 showed that the `101` finite-target drop from `ideal_true` to
  `realistic_observed` exactly matches the response-screen false-negative
  count.
- Goal 012 explained those `101` false negatives, with dominant mechanisms:
  - `no_post_extirpation_surveys`: `39`;
  - `late_extirpation_near_survey_horizon`: `30`;
  - `post_extirpation_detection_blocks_absence`: `28`;
  - `insufficient_post_extirpation_survey_history`: `4`.

The next question is whether bounded post-extirpation observation-support
counterfactuals can restore enough observed extirpation signal to make the
existing compatibility bridge useful, before any rule change or ABC/POM design
is attempted.

## Scientific Question

If synthetic false negatives are given explicit, auditable post-extirpation
survey support in a clearly labelled evaluation-only namespace, does the
`realistic_observed` target become compatible with the default process
candidate under the existing final-absence reconstruction rule and current
summary-vector/compatibility scoring?

## In Scope

- Add `spec/synth_small_observation_support_counterfactual_screen.md`.
- Add a focused module under `src/spatext/synth/small/`, probably
  `observation_support_counterfactual_screen.py`.
- Add a CLI script, probably
  `scripts/run_synth_small_observation_support_counterfactual.py`.
- Read existing emitted synthetic artifacts from disk.
- Define a small deterministic scenario set with stable scenario IDs.
- Create clearly labelled counterfactual reconstruction/target summaries in a
  separate evaluation-only output namespace.
- Reuse the existing summary-vector and compatibility-screen contracts where
  possible.
- Report whether each scenario resolves:
  - false-negative count;
  - finite-target count;
  - compatibility-screen loss/class;
  - dominant remaining blocker class.
- Emit deterministic audit artifacts under:
  `artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/`.
- Add focused tests for scenario definitions, per-site resolution accounting,
  summary-vector/compatibility bridge outputs, recommendation classification,
  CLI execution, and boundary labels.
- Update exports, README, `AGENTS.md` if the authoritative spec list changes,
  `spec/report_log.md`, and this goal log.

## Out Of Scope

- Changing default observation-design settings.
- Changing emitted default observation artifacts outside the counterfactual
  output namespace.
- Changing the production reconstruction rule or `min_final_absence_run`.
- Changing response-screen, summary-vector, compatibility-screen,
  mismatch-audit, or false-negative-audit scoring logic.
- Adding new process candidates or broad parameter sweeps.
- ABC, POM, MCMC, likelihood fitting, posterior claims, or parameter recovery.
- Real-data analysis.
- Remote compute.
- Commit or push.

## Counterfactual Principles

This screen may use hidden synthetic truth only because it is explicitly
evaluation-only and synthetic-only. Any truth-guided support must be labelled as
diagnostic counterfactual support, not as an analyst-facing observation design.

The scenarios should be conservative and reviewable. They should distinguish at
least:

- `status_quo`: the current emitted artifacts, reproduced as the baseline.
- a post-extirpation survey-support floor that asks whether inadequate survey
  opportunity is the dominant problem.
- a scenario that respects post-extirpation detections as blockers, so survey
  timing is not confused with detection persistence.
- a late-follow-up support scenario that asks whether end-window support is
  enough under the current final-absence rule.

Exact scenario definitions may be adapted to the existing repo contracts, but
they must be documented in the spec and emitted configuration. The scenario
set should remain small; this is not a broad sweep.

## Required Inputs

The command should read these existing artifacts from disk:

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

Evaluation and bridge artifacts:

- `artifacts/synth_small_response_screen/evaluation/screen_evaluation_summary.json`
- `artifacts/synth_small_response_screen/evaluation/site_evaluation_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/verification.json`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/false_negative_site_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/mechanism_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/recommendation.json`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/verification.json`
- `artifacts/synth_small_summary_vector/target_summary.json`
- `artifacts/synth_small_compatibility_screen/candidate_scores.csv`
- `artifacts/synth_small_compatibility_screen/mode_rankings.csv`
- `artifacts/synth_small_compatibility_screen/verification.json`

The command should fail loudly when required inputs are missing. The runbook may
rebuild the local ignored artifact chain first.

## Required Outputs

Write a deterministic artifact bundle under:

```text
artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/
```

Required files:

- `counterfactual_config.json`
- `scenario_definitions.csv`
- `site_counterfactual_resolution.csv`
- `scenario_reconstruction_summary.csv`
- `scenario_summary_vectors.csv`
- `scenario_compatibility_scores.csv`
- `scenario_rankings.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

The JSON outputs must clearly label:

- `synthetic_only: true`
- `evaluation_only: true`
- `counterfactual_only: true`
- `not_formal_inference: true`
- `no_default_observation_change: true`
- `no_reconstruction_rule_change: true`
- `no_scoring_change: true`

## Recommendation Classes

The recommendation should classify the next project move without starting it.
Suggested classes:

- `observation_support_sufficient_before_rule_change`: bounded support
  scenarios restore compatibility under the current rule.
- `detection_persistence_blocks_observation_support`: survey timing alone is
  insufficient because post-extirpation detections dominate unresolved sites.
- `reconstruction_rule_review_needed_before_inference`: even generous bounded
  support does not restore compatibility under the current final-absence rule.
- `counterfactual_contract_failed`: prerequisite verification or scenario
  accounting fails.
- `ready_for_inference_design_discussion`: only if compatibility is restored
  and residual diagnostics do not point to observation or reconstruction
  artifacts.

The last class is a discussion recommendation only; do not start ABC/POM work
inside this goal.

## Acceptance Criteria

- The spec exists and is implemented.
- The CLI consumes required artifacts from disk and writes the required bundle.
- Scenario definitions are documented and emitted.
- The status-quo scenario exactly reconciles with current Goal 010-012 counts.
- Every Goal 012 false-negative site has one per-scenario resolution row.
- Scenario summaries reconcile finite-target counts and false-negative counts.
- Scenario compatibility scores/rankings are emitted and traceable to the
  existing summary-vector/compatibility contracts.
- The recommendation identifies the next intervention class without changing
  production observation, reconstruction, scoring, or inference logic.
- Focused tests pass.
- Proportionate full repository validation passes.
- Generated artifacts remain unstaged.
- No commit or push is performed.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.
