# Plan

1. Confirm the action repo is clean at the accepted Goal 019 base and create
   `codex/spatext-goal020-synth-medium-response-reconstruction-benchmark`.
2. Read repo-local instructions, README, Goal 017/018/019 specs/logs, and the
   synth-medium landscape, spread-impact, and observation modules.
3. Write focused Goal 020 tests first for artifact contract, source
   reconciliation, response-only schema boundaries, positive-control behavior,
   default/stress contrast, visual layout, determinism, and CLI smoke.
4. Implement `src/spatext/synth/medium/response_reconstruction.py` with a
   small deterministic rule set and package-level artifact writer.
5. Add CLI `scripts/benchmark_synth_medium_response_reconstruction.py`.
6. Add durable spec and public/repo documentation entries.
7. Generate the ignored artifact bundle and inspect headline outcomes.
8. Run the validation ladder and wake the orchestrator with results.

## Rule Set

Use transparent response-observable benchmark rules:

- `final_absence_run_2`
- `final_absence_run_1`
- `midpoint_after_last_detection`

The rules are benchmark diagnostics only. They are not production adoption.

## Recommendation Labels

Choose one deterministic label:

- `response_reconstruction_ready_for_human_review`
- `default_observation_design_recoverability_marginal`
- `observation_design_not_recoverable_enough_for_backfitting`

The recommendation should be skeptical and evidence-led.
