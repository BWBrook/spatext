# Plan

1. Confirm the repo is on the Goal 021 branch from the published Goal 020 base.
2. Read repo-local instructions, current synth-medium specs, and Goal 017-020
   contracts.
3. Add focused tests first for the Goal 021 artifact contract, baseline
   reconciliation, counterfactual regime semantics, decision separation, visual
   layout, determinism, and CLI smoke.
4. Implement the counterfactual screen as package code that reuses the published
   observation-design and response-reconstruction contracts without changing
   them.
5. Add the CLI, exports, spec, README/AGENTS/report-log updates, and goal log.
6. Generate the ignored artifact bundle with the CLI.
7. Run the validation ladder and wake the orchestrator.

## Implementation Notes

- Use the published Goal 019 default observation records as the exact baseline.
- Reuse Goal 020 benchmark rules for all regimes.
- Treat the near-perfect regime as an unrealistic diagnostic ceiling.
- Select the cross-regime best plausible design by recoverability
  (finite-recall and false-negative reduction) rather than by loss alone.
- Keep all generated outputs under the ignored artifact namespace.
