# Goal 023 Task 2a2 Brief

## Context

Complete the second half of Plan Task 2a in the existing isolated worktree
`/Users/bwbrook/.codex/worktrees/spatext/goal023`.

Read these files first. They are authoritative and contain the exact values to
use verbatim:

1. `AGENTS.md`
2. `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`
3. `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md`, especially Task 2a
4. `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md`
5. `spec/synth_medium_latent_response_observation_recovery_gate.md`, especially Replication And Holdout Lock, Canonical stochastic realisation and schedules, Structural-identifiability proposition and audits, and Analyst/Truth Firewall
6. accepted source and tests already present in `src/spatext/synth/medium/latent_response_observation_recovery.py` and `tests/test_synth_medium_latent_response_observation_recovery.py`

The frozen authoritative spec SHA-256 is
`0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`.
Do not change any frozen goal/spec/runbook contract file.

The accepted Task 2a1 source SHA-256 before this task is
`78169d0114029287fd9a81bd5024b632a4060a8b27b8a14839d616a85d35bdb1`.
The accepted Task 2a1 test SHA-256 before this task is
`5321062bfe52574ee34c39d028ff6b6e01f85dce696f7b66f99855204ba4a223`.

## Ownership

You own only:

- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- append-only updates at the end of `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`
- the ignored report `.superpowers/sdd/task-2a2-report.md`

You are not alone in the codebase. Do not revert or rewrite existing work. Work
with the current accepted code and preserve all existing semantics/tests.

## Required Outcomes

Use strict red-green-refactor TDD. Add failing tests first and record the exact
RED command/output before production changes.

Implement and test exactly the Task 2a simulation/design layer:

1. Canonical payload validation, canonical compact sorted-key ASCII JSON,
   SHA-256 entropy-word conversion, `SeedSequence`, and `PCG64DXSM` generator.
   Reproduce both frozen non-holdout raw-uint64 vectors exactly.
2. Reject missing/extra/unknown payload keys, component combinations, split
   combinations, and every out-of-range scenario/replicate/draw index before
   RNG construction. Do not construct or inspect any holdout payload.
3. Deterministic process simulation using one full `(n_passable, 20)` uniform
   array in C order and full consumption after absorption.
4. Deterministic observation simulation using exactly one Poisson call over the
   complete canonical mean vector in opportunity order, without state-dependent
   skipping. Preserve the analyst/truth firewall.
5. Canonical schedules, opportunity ordering, structured effort formula, fixed
   sparse frame, quality quintiles, arrival permutation, and alignment frame,
   exactly as frozen in the spec.
6. Provenance-distinct `potential_design`,
   `process_oracle_truth_at_risk`, and
   `joint_plugin_smoothed_at_risk` diagnostics with exact SVD rank/condition
   convention. Truth-at-risk values must not enter joint starts, bounds,
   objective, profiles, gates, or analyst likelihood.
7. Invalid schema/domain tests, exact shapes/dtypes/immutability, deterministic
   order, and source-scope checks proving no optimizer/profile/scenario-suite/
   artifact/calibration/holdout work has begun.

The deliverable is still Task 2a only: analytically tested simulator and exact
nested oracle/joint likelihood plus deterministic design primitives. Do not
implement transforms, Halton starts, optimizers, inverse audits, profiles,
scenario suites, CLI, artifacts, calibration, or holdout.

## Ledger Contract

Before appending, verify the current Log parent is exactly:

- line count `1962`
- SHA-256 `b047ab616b7292661b311c3ad227543df3556ad2dbcd9c9117257a60f92f4aad`

Append one new child at the end only. Name the exact parent line count/hash,
the RED and GREEN evidence, changed-file hashes, static/regression checks,
self-review, and boundary confirmation. Never insert, reorder, or backfill.

## Validation

At minimum run and report:

- focused latent-recovery tests without coverage
- observation-kernel regression tests without coverage
- Ruff format check and lint on touched source/test
- `uv run mypy src tests`
- `git diff --check`
- exact final hashes and Log line count/root hash

## Stop Rules

Stop and report rather than improvising if any frozen vector, payload rule,
schedule/frame count, prior accepted likelihood/firewall behavior, or append-only
ledger parent cannot be reproduced exactly. Do not alter thresholds or the
contract to make tests pass.
