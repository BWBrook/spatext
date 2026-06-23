# Goal 022: Synth-Medium Recoverability-Target Observation-Design Review Pack

## Objective

Build a bounded, deterministic, synthetic-only `synth-medium`
observation-design review pack that tests whether a more serious but still
field-plausible response-observation regime can make the published Goal 018
truth recoverable enough for later fitting review.

This is diagnostic only. It identifies whether a candidate observation design
looks recoverable; it does not fit anything, adopt a production observation
design, or adopt a production reconstruction rule.

## Context

- Goal 017 published the synth-medium landscape.
- Goal 018 published the synth-medium spread-impact truth.
- Goal 019 published the default observation-design review pack.
- Goal 020 showed the default regime is not recoverable enough for back-fitting.
- Goal 021 showed modest response-only counterfactuals still fail, while only
  the unrealistic diagnostic ceiling recovers the signal.

## Required Product

Add:

- `spec/synth_medium_recoverability_target_observation_design.md`
- `src/spatext/synth/medium/recoverability_target_observation_design.py`
- `scripts/build_synth_medium_recoverability_target_observation_design.py`
- `tests/test_synth_medium_recoverability_target_observation_design.py`
- exports, README, AGENTS, report-log, and this goal packet.

Generated review artifacts go under:

```text
artifacts/synth_medium_recoverability_target_observation_design/
```

Generated artifacts remain ignored and unstaged.

## Hard Boundaries

- No fitting, ABC, POM, likelihood fitting, MCMC, posterior claim, parameter
  recovery, broad optimization, or broad sweep.
- No real-data analysis.
- No remote compute.
- No production observation-design adoption.
- No production reconstruction-rule adoption.
- No changes to published Goal 017 landscape, Goal 018 spread-impact truth,
  Goal 019 default observation design, Goal 020 benchmark, or Goal 021
  counterfactual screen.
- No commit or push.
- Do not start Goal 023.
