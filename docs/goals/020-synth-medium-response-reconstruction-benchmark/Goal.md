# Goal 020: Synth-Medium Response Reconstruction Benchmark

## Objective

Build a deterministic, synthetic-only response-time reconstruction benchmark
over the accepted Goal 019 `synth-medium` observations and fixed Goal 018
latent truth, then stop for orchestrator review.

The benchmark should determine whether the accepted
`structured_response_observed_default` observation regime contains enough
response-only signal to support later back-fitting work. It must also include
the Goal 019 full-observability benchmark as a positive control and the sparse
regime as a low-information stress contrast.

## Required Outputs

Write generated review artifacts under:

```text
artifacts/synth_medium_response_reconstruction_benchmark/
```

Required root files:

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

## Acceptance Gates

- Reconcile against the published Goal 017/018/019 headline counts and
  selected IDs.
- Reconstruct response times from response observations and observation support
  only.
- Keep hidden truth out of analyst-facing reconstructed-time tables.
- Use hidden truth only in clearly labelled synthetic audit bridge/summaries.
- Verify the full-observability benchmark as a positive control.
- Quantify default-regime finite/nonfinite reconstruction, classification
  counts, timing errors, spatial/group error patterns, and support gaps.
- Show that the sparse stress regime is lower information than the default.
- Emit self-decoding SVGs with testable layout bounds.
- Choose a skeptical deterministic recommendation class.

## Hard Boundaries

- Do not change Goal 017 landscape design.
- Do not change Goal 018 spread-impact truth or selected default.
- Do not change Goal 019 observation regimes, survey probabilities, selected
  default, schemas, or scientific outcomes.
- Do not adopt a production reconstruction rule.
- Do not fit parameters or run ABC, POM, likelihood, MCMC, posterior,
  parameter-recovery, optimization, broad-sweep, remote-compute, or real-data
  work.
- Do not stage generated artifacts, build outputs, caches, `.venv/`, or
  unrelated files.
- Do not commit or push.
- Do not start Goal 021.
