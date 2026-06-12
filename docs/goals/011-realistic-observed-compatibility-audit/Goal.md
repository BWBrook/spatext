# Goal 011: Realistic-Observed Compatibility Mismatch Audit

## Objective

Build a disk-first synthetic-only audit that explains why the Goal 010
`realistic_observed` compatibility screen rejects all current candidates.

This goal should diagnose the mismatch between the ideal synthetic target, the
realistic reconstructed target, and the compatibility-screen scores. It should
not change Goal 010 scoring, tune thresholds, add candidate sweeps, start ABC or
POM work, or make real-data claims.

## Context

Goal 009 created the reusable `S(T_X, T_P)` summary-vector layer.

Goal 010 created the first deterministic compatibility screen. Its headline
result is:

- `ideal_true`: default candidate is `compatible` with loss `0`.
- `realistic_observed`: default candidate is top-ranked but `incompatible`
  with loss `3.52263635737`.
- all three `realistic_observed` candidates are `incompatible`.

That is a useful pressure-test result. It says the summary and screen stack is
wired well enough to recover the default synthetic truth under `ideal_true`,
but the observation/reconstruction target has lost or shifted enough signal to
break compatibility under the current screen.

## Scientific Question

What explains the `realistic_observed` incompatibility: finite-target loss,
lag shifts, arrival-target coupling collapse, front-geometry change,
coverage-curve differences, response-screen false negatives, or some
combination of these?

## In Scope

- Add `spec/synth_small_compatibility_mismatch_audit.md`.
- Add a focused source module under `src/spatext/synth/small/`, probably
  `compatibility_mismatch_audit.py`.
- Add a CLI script, probably
  `scripts/audit_synth_small_compatibility_mismatch.py`.
- Read Goal 009 summary-vector artifacts from disk.
- Read Goal 010 compatibility-screen artifacts from disk, including
  `coverage_score_breakdown.csv`.
- Read the synthetic response-screen evaluation audit from disk, rebuilding
  ignored prerequisites through the runbook if local artifacts are absent.
- Decompose the `realistic_observed` mismatch by:
  - target-mode deltas between `ideal_true` and `realistic_observed`;
  - component-level weighted-loss contributions for the top
    `realistic_observed` candidate;
  - coverage-breakpoint gaps for the same comparison;
  - response-screen evaluation counts, especially false negatives;
  - correspondence between finite-target loss and missed true extirpations
    where the artifacts support it.
- Emit deterministic audit artifacts under
  `artifacts/synth_small_compatibility_screen/mismatch_audit/`.
- Add focused tests for artifact loading, decomposition arithmetic,
  evaluation-bridge logic, recommendation classification, CLI execution, and
  synthetic-only boundary labels.
- Update exports, README, `AGENTS.md` if the authoritative spec list changes,
  `spec/report_log.md`, and this goal log.

## Out Of Scope

- Changing Goal 010 compatibility scoring, thresholds, weights, ranks, or
  classes.
- Changing Goal 009 summary-vector semantics.
- Changing reconstruction, response-screen, inspection, or evaluation logic.
- Adding new candidate sweeps or expanding the candidate grid.
- ABC, POM, MCMC, likelihood fitting, posterior claims, parameter recovery, or
  real-data analysis.
- Remote compute.
- Reading Chief of Staff or Goal Composer.
- Commit or push.

## Required Inputs

The audit command should read these emitted artifacts:

Goal 009 summary vector:

- `artifacts/synth_small_summary_vector/summary_components.csv`
- `artifacts/synth_small_summary_vector/coverage_curve.csv`
- `artifacts/synth_small_summary_vector/mode_summary.json`
- `artifacts/synth_small_summary_vector/verification.json`

Goal 010 compatibility screen:

- `artifacts/synth_small_compatibility_screen/compatibility_screen_config.json`
- `artifacts/synth_small_compatibility_screen/target_summary.json`
- `artifacts/synth_small_compatibility_screen/candidate_scores.csv`
- `artifacts/synth_small_compatibility_screen/coverage_score_breakdown.csv`
- `artifacts/synth_small_compatibility_screen/mode_rankings.csv`
- `artifacts/synth_small_compatibility_screen/verification.json`

Goal 008 response-screen evaluation:

- `artifacts/synth_small_response_screen/evaluation/screen_evaluation_summary.json`
- `artifacts/synth_small_response_screen/evaluation/group_evaluation_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/site_evaluation_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/verification.json`

The audit command should fail loudly when required inputs are missing. The
runbook may rebuild the ignored local artifact chain first.

## Required Audit Components

Implement an audit with at least:

- target-mode summary deltas:
  - finite target count and fraction;
  - lag mean and standard deviation;
  - arrival-target squared correlation;
  - front-plane gradient magnitude;
  - coverage target times at each breakpoint;
- score contribution decomposition for the top `realistic_observed` candidate;
- coverage-breakpoint decomposition using `coverage_score_breakdown.csv`;
- response-screen evaluation bridge:
  - confusion matrix;
  - false-negative count and fraction;
  - weak-signal group count;
  - whether the ideal-to-realistic finite target drop equals, or nearly equals,
    the false-negative count;
- a machine-readable recommendation class.

The recommendation class should be conservative. Suggested initial classes:

- `diagnose_observation_reconstruction_before_abc`
- `screen_contract_bug_suspected`
- `candidate_expansion_may_be_warranted`
- `ready_for_next_inference_design`

For the current expected state, if `ideal_true` default is compatible but all
`realistic_observed` candidates are incompatible and false negatives explain a
large part of finite-target loss, the recommended class should be
`diagnose_observation_reconstruction_before_abc`.

## Required Outputs

Write a deterministic artifact bundle under:

```text
artifacts/synth_small_compatibility_screen/mismatch_audit/
```

Required files:

- `mismatch_audit_config.json`
- `target_delta_summary.csv`
- `score_contribution_summary.csv`
- `coverage_gap_summary.csv`
- `evaluation_bridge_summary.json`
- `recommendation.json`
- `verification.json`
- `report.md`

The JSON outputs must clearly label:

- `synthetic_only: true`
- `audit_only: true`
- `not_formal_inference: true`
- `no_scoring_change: true`
- source artifact directories and verification states.

## Acceptance Criteria

- The spec exists and is implemented.
- The CLI consumes the Goal 009, Goal 010, and Goal 008 artifacts from disk and
  writes the required mismatch-audit bundle.
- The audit explains which components dominate the top `realistic_observed`
  mismatch.
- Coverage-gap arithmetic is reconstructed from Goal 010
  `coverage_score_breakdown.csv`.
- The evaluation bridge reports the response-screen confusion matrix and
  false-negative relationship to the finite-target drop.
- The recommendation is conservative and does not authorize ABC/POM by itself.
- Focused tests pass.
- Proportionate full repository validation passes.
- Generated artifacts remain unstaged.
- No commit or push is performed.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.
