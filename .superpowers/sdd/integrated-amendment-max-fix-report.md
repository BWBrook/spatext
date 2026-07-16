# Goal 023 Integrated Amendment Max-Audit Fix Report

status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
task_3_authority: `BLOCKED`
date: `2026-07-11`
profile: `sol_high_specialist`
worktree: `/Users/bwbrook/.codex/worktrees/spatext/goal023`
branch: `codex/spatext-goal023-latent-response-observation-gate`
head: `53462d0365babf2c8070714a930f69b4071af276`

## Changed Paths

- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`
- `spec/synth_medium_latent_response_observation_recovery_gate.md`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `tests/test_synth_medium_latent_response_observation_recovery.py`
- this ignored report

Pre-existing `pyproject.toml`, `uv.lock`, `src/spatext/observe.py`, and
`tests/test_observe.py` changes were preserved and not edited by this repair.

## RED/GREEN

- Registry/firewall/fit identity: RED `11 failed`; GREEN `11 passed`.
- Latent diagnostics: RED `14 failed, 6 passed`; GREEN `20 passed`.
- Denominators/controls/stresses: RED `14 failed`; GREEN `14 passed`.
- Local/global reducers: RED `20 failed`; GREEN `20 passed`.
- Artifact/hash/fixture dispatch: RED `9 failed, 1 passed`; GREEN `10 passed`.
- Provenance/freeze: RED `22 failed` under the initial selector; GREEN
  `23 passed` including the never-retry behavior.
- Complete exact named matrix: `98 passed, 199 deselected in 0.26s`.

## Validation

- Complete Goal 023 test file: `297 passed in 731.04s`.
- Observation/upstream set: `69 passed in 46.95s`.
- Ruff format/check: passed.
- mypy: passed for 59 source files.
- Goal/spec body identity: passed.
- Exact proposal test inventory: `required=98 missing=0`.
- `git diff --check`: passed.
- Source receipt unchanged.
- Canonical artifact directory, config, preholdout receipt, and holdout receipt:
  absent.

## Exact Hashes

- Goal: `6883c0188be06c328f09a4e07a9872b366e414abac31bc5241b7d5c72f6b8e3f`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `fc74fae83c6e93701a06d342346ffe803360fb718f2ed34f69bcb610103a7e7b`
- authoritative spec: `af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e`
- source: `a862b269f85ae67b479e8df463582ea4019ce46abae7f20b0cacd6fa75d25458`
- tests: `e0b0ba396e48c02d51f4477260fd96790e167d8dadb94bce9e674faa2e490ae0`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- final Log: `a074ede50e6fd797537efdc245bd85be23ebe01e00b74d666aa54ad665840a8e`
- final Log shape: `2463` lines, `121774` bytes.

## Concerns

- Scientific, statistical, executor-readiness, artifact/schema, code,
  provenance/freeze, and independent max rereview remain `PENDING` for the
  replacement hashes.
- Task 3 remains blocked. No scientific scenario, live benchmark, calibration,
  canonical artifact/config/receipt, holdout payload, staging, commit, or push
  was run or created.
