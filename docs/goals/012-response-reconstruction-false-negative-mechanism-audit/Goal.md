# Goal 012: Response-Reconstruction False-Negative Mechanism Audit

## Objective

Build a disk-first synthetic-only audit that explains the 101 response-screen
false negatives identified by Goal 011.

This goal should classify the site-level mechanisms behind missed true
extirpations before any reconstruction-rule change, observation-design change,
candidate expansion, ABC, POM, or real-data work is attempted.

## Context

Goal 011 established the current bottleneck:

- `ideal_true` finite targets: `252`
- `realistic_observed` finite targets: `151`
- finite-target drop: `101`
- response-screen false negatives: `101`
- bridge class: `finite_target_drop_matches_false_negatives`

The next question is no longer whether the compatibility screen is working. It
is why those 101 truly extirpated sites were not reconstructed as observed
extirpations.

## Scientific Question

Which observation/reconstruction mechanisms explain the 101 false negatives:
insufficient post-extirpation survey history, detections too late relative to
true extirpation, sparse visits, weak eastern signal, conservative sustained
absence rules, or some other auditable pattern?

## In Scope

- Add `spec/synth_small_false_negative_mechanism_audit.md`.
- Add a focused source module under `src/spatext/synth/small/`, probably
  `false_negative_mechanism_audit.py`.
- Add a CLI script, probably
  `scripts/audit_synth_small_false_negatives.py`.
- Read existing synthetic observation, reconstruction, response-screen
  evaluation, and mismatch-audit artifacts from disk.
- Join false-negative sites to:
  - `site_evaluation_audit.csv`;
  - `site_reconstruction.csv`;
  - `visits.csv`;
  - `observations.csv`;
  - `evaluation_truth.csv` where needed for hidden-truth timing labels;
  - Goal 011 `evaluation_bridge_summary.json` and `recommendation.json` for
    provenance.
- Classify every false-negative site into one primary mechanism and optional
  secondary flags.
- Emit deterministic audit artifacts under
  `artifacts/synth_small_response_screen/evaluation/false_negative_audit/`.
- Add focused tests for full false-negative coverage, mechanism arithmetic,
  group summaries, recommendation classification, CLI execution, and
  synthetic-only/audit-only labels.
- Update exports, README, `AGENTS.md` if the authoritative spec list changes,
  `spec/report_log.md`, and this goal log.

## Out Of Scope

- Changing reconstruction rules.
- Changing observation design or regenerating observations with new settings.
- Changing response-screen, compatibility-screen, or mismatch-audit logic.
- Tuning summary-vector or compatibility-screen weights, scales, thresholds,
  ranks, or classes.
- Adding candidate sweeps or parameter recovery.
- ABC, POM, MCMC, likelihood fitting, posterior claims, or real-data analysis.
- Remote compute.
- Reading Chief of Staff or Goal Composer.
- Commit or push.

## Required Inputs

The false-negative audit command should read these emitted artifacts:

Response-screen evaluation:

- `artifacts/synth_small_response_screen/evaluation/screen_evaluation_summary.json`
- `artifacts/synth_small_response_screen/evaluation/group_evaluation_summary.csv`
- `artifacts/synth_small_response_screen/evaluation/site_evaluation_audit.csv`
- `artifacts/synth_small_response_screen/evaluation/verification.json`

Extirpation reconstruction:

- `artifacts/synth_small_extirpation_reconstruction/site_reconstruction.csv`
- `artifacts/synth_small_extirpation_reconstruction/time_detection_summary.csv`
- `artifacts/synth_small_extirpation_reconstruction/verification.json`

Observation artifacts:

- `artifacts/synth_small_observations/visits.csv`
- `artifacts/synth_small_observations/observations.csv`
- `artifacts/synth_small_observations/evaluation_truth.csv`
- `artifacts/synth_small_observations/truth_reference.json`

Goal 011 mismatch audit:

- `artifacts/synth_small_compatibility_screen/mismatch_audit/evaluation_bridge_summary.json`
- `artifacts/synth_small_compatibility_screen/mismatch_audit/recommendation.json`
- `artifacts/synth_small_compatibility_screen/mismatch_audit/verification.json`

The command should fail loudly when required inputs are missing. The runbook may
rebuild the ignored local artifact chain first.

## Required Mechanism Features

For every false-negative site, compute at least:

- region and front band;
- true extirpation time;
- observed extirpation time, if any;
- reconstruction status;
- visit count and survey-time count;
- detection count;
- first and last detection time;
- final absence start time and final absence survey-time count;
- last survey time;
- first survey time after true extirpation;
- count of survey times after true extirpation;
- count of detections after true extirpation;
- lag from true extirpation to last detection;
- lag from true extirpation to first post-extirpation survey.

Use these to assign one primary mechanism. Suggested initial classes:

- `post_extirpation_detection_blocks_absence`
- `insufficient_post_extirpation_survey_history`
- `no_post_extirpation_surveys`
- `late_extirpation_near_survey_horizon`
- `sparse_or_low_effort_observation`
- `weak_east_or_edge_signal`
- `unclassified_false_negative`

The exact priority order can be pragmatic, but it must be documented in the
spec and emitted config. Every false negative must receive exactly one primary
mechanism.

## Required Outputs

Write a deterministic artifact bundle under:

```text
artifacts/synth_small_response_screen/evaluation/false_negative_audit/
```

Required files:

- `false_negative_audit_config.json`
- `false_negative_site_audit.csv`
- `mechanism_summary.csv`
- `group_mechanism_summary.csv`
- `observation_timing_summary.csv`
- `recommendation.json`
- `verification.json`
- `report.md`

The JSON outputs must clearly label:

- `synthetic_only: true`
- `audit_only: true`
- `evaluation_only: true`
- `not_formal_inference: true`
- `no_reconstruction_change: true`
- source artifact directories and verification states.

## Acceptance Criteria

- The spec exists and is implemented.
- The CLI consumes the required artifacts from disk and writes the required
  false-negative audit bundle.
- All 101 false negatives are represented exactly once in
  `false_negative_site_audit.csv`.
- Every false negative has one primary mechanism.
- Mechanism and group summary counts reconcile exactly to the false-negative
  count.
- The recommendation identifies the next intervention class without changing
  reconstruction or observation logic.
- Focused tests pass.
- Proportionate full repository validation passes.
- Generated artifacts remain unstaged.
- No commit or push is performed.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.
