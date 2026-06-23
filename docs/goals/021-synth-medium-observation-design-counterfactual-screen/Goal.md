# Goal 021: Synth-Medium Observation-Design Recoverability Counterfactual Screen

Build a deterministic, synthetic-only counterfactual observation-design screen
over the fixed Goal 017 landscape and Goal 018 spread-impact truth, using the
published Goal 019 observation design and Goal 020 response-reconstruction
benchmark as baseline evidence.

## Objective

Determine what kind of additional response-observation support would make
`synth-medium` response-time reconstruction credible enough for later fitting
work. The output compares a small, interpretable set of alternative observation
regimes against the published baseline, then recommends whether plausible
field-like observation improvements can recover enough timing signal or whether
only an unrealistic diagnostic ceiling works.

## Boundaries

- Synthetic-only and review-only.
- Preserve the Goal 017 landscape exactly.
- Preserve the Goal 018 spread-impact truth exactly.
- Preserve the Goal 019 published baseline observation design exactly.
- Preserve the Goal 020 published response-reconstruction benchmark outcome.
- Do not adopt a production observation design or reconstruction rule.
- Do not fit parameters or run ABC, POM, likelihood, MCMC, posterior,
  parameter recovery, optimization, broad sweeps, remote compute, or real-data
  work.
- Do not stage generated artifacts, build outputs, caches, virtual
  environments, or unrelated files.
- Do not commit, push, or start Goal 022.

## Expected Footprint

- `spec/synth_medium_observation_design_counterfactual_screen.md`
- `src/spatext/synth/medium/observation_design_counterfactual_screen.py`
- `scripts/screen_synth_medium_observation_design_counterfactuals.py`
- `tests/test_synth_medium_observation_design_counterfactual_screen.py`
- exports in `src/spatext/synth/medium/__init__.py`
- README, AGENTS, report-log, and this goal packet

## Required Artifact Bundle

Generated artifacts are written under:

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

## Completion Signal

Wake the orchestrator with branch/status, changed files, validation evidence,
artifact and visual paths, headline regime/rule results, decision
recommendation, generated/build artifact handling, and boundary confirmation.
