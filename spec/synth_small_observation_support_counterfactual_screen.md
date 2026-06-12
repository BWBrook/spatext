# Synth-Small Observation-Support Counterfactual Screen

Goal 013 adds a synthetic-only, evaluation-only counterfactual screen for the
observed-extirpation signal gap diagnosed in Goals 010-012.

The screen asks whether bounded post-extirpation observation support, applied
only as a labelled counterfactual to the existing false negatives, can restore
enough finite target support for the unchanged summary-vector and compatibility
bridge to become useful under the current final-absence reconstruction rule.

## Scope

The screen is diagnostic only.

- It does not change default observation-design settings.
- It does not rewrite emitted default observation or reconstruction artifacts.
- It does not change the production final-absence reconstruction rule or
  `min_final_absence_run`.
- It does not change summary-vector, compatibility-screen, mismatch-audit,
  false-negative-audit, threshold, scale, weight, rank, class, or candidate
  logic.
- It does not start ABC, POM, likelihood fitting, posterior interpretation,
  parameter recovery, real-data analysis, or remote compute.

Hidden synthetic truth is used only to define labelled counterfactual support
times for already identified response-screen false negatives. These outputs are
not analyst-facing observation-design recommendations.

## Inputs

The builder reads the disk artifacts from the small synthetic chain:

- `artifacts/synth_small_observations/`
- `artifacts/synth_small_extirpation_reconstruction/`
- `artifacts/synth_small_response_screen/evaluation/`
- `artifacts/synth_small_response_screen/evaluation/false_negative_audit/`
- `artifacts/synth_small_summary_vector/`
- `artifacts/synth_small_compatibility_screen/`

The status-quo scenario must reconcile the current observed-target count and
false-negative count from those artifacts: 151 finite observed targets and 101
response-screen false negatives.

The screen also verifies and records the existing bridge artifacts that define
the current summary-vector/compatibility context:

- `artifacts/synth_small_summary_vector/verification.json`
- `artifacts/synth_small_summary_vector/mode_summary.json`
- `artifacts/synth_small_compatibility_screen/target_summary.json`
- `artifacts/synth_small_compatibility_screen/candidate_scores.csv`
- `artifacts/synth_small_compatibility_screen/mode_rankings.csv`
- `artifacts/synth_small_compatibility_screen/verification.json`

`counterfactual_config.json` and `verification.json` include source-verification
fields for these bridge bundles. The status-quo scenario is reconciled against
the existing Goal 010 `realistic_observed` top ranking: finite target count
`151`, top candidate `default`, top class `incompatible`, and top loss
`3.52263635737`. The ideal-true finite target count is reconciled to `252`.

## Scenarios

The scenario set is intentionally small and deterministic.

`status_quo`
: Uses the existing observed extirpation target without adding support.

`truth_guided_absence_floor_all`
: A diagnostic upper bound that gives every false-negative site enough
  synthetic post-extirpation zero-detection support to satisfy the current
  final-absence rule. This scenario does not respect post-extirpation detections
  as blockers; it is labelled as an upper bound.

`detection_blocker_respecting_floor`
: Adds the same bounded support only to false-negative sites with no
  post-extirpation detections in the emitted observations. Sites with
  post-extirpation detections remain unresolved so detection persistence is not
  confused with survey timing.

`late_followup_detection_blocker_respecting`
: Adds late follow-up support for timing-gap false negatives with no
  post-extirpation detections. The counterfactual target time is no earlier than
  both one step after true extirpation and one interval after the last observed
  survey.

For support-floor scenarios, the synthetic counterfactual support count equals
the current reconstruction rule's `min_final_absence_run`. The target time is
the first synthetic support time, matching the current final-absence-run
semantics.

## Outputs

The CLI writes to
`artifacts/synth_small_response_screen/evaluation/observation_support_counterfactual/`.

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

`site_counterfactual_resolution.csv` contains one row per false-negative site
per scenario. It records the status-quo observed target, true extirpation time,
counterfactual target time when resolved, post-extirpation detection count,
support count, and unresolved reason.

`scenario_summary_vectors.csv` is a long-form summary-vector artifact. It
contains scalar summary components and coverage-curve target rows for each
scenario, using the existing Goal 009 summary-vector helpers.

`scenario_compatibility_scores.csv` and `scenario_rankings.csv` reuse the Goal
010 candidate set, required components, weights, scales, compatibility classes,
and ranking rules. Scenario IDs are target modes for this diagnostic screen.

## Interpretation

The screen distinguishes finite-target recovery from compatibility recovery.
A scenario can restore the finite-target count while remaining incompatible if
the unchanged weighted-gap loss still exceeds the Goal 010 thresholds.

The recommendation remains pre-inference and diagnostic. A later bounded goal is
required before any reconstruction-rule change, observation-design change,
candidate expansion, ABC, POM, or real-data work.
