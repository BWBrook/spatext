# Goal 023 Integrated Amendment Final Repair 2 Report

date: `2026-07-12`
profile: `sol_high_specialist`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
acceptance_status: `PENDING`
task_3_authority: `BLOCKED`
stochastic_and_irreversible_phases: `BLOCKED`

## Scope

Tracked project files changed by this repair:

- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`

Ignored evidence written under the authorized evidence directory:

- `.superpowers/sdd/integrated-amendment-final-repair-2-report.md`
- `.superpowers/sdd/integrated-amendment-final-repair-2-98-pytest.txt`
- `.superpowers/sdd/integrated-amendment-final-repair-2-full-pytest.txt`
- `.superpowers/sdd/integrated-amendment-final-repair-2-upstream-pytest.txt`

No Goal, Plan, Runbook, authoritative spec, dependency, lockfile, observation
kernel, source receipt, or other tracked file was modified by this repair.
Pre-existing `pyproject.toml`, `uv.lock`, `src/spatext/observe.py`,
`tests/test_observe.py`, Goal/spec packet, and orchestrator changes were
preserved.

## RED Evidence

Behavior-specific tests were written before the production repair. Exact RED
selector:

```bash
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py \
  -k 'lro_3a_005 or lro_3a_007 or lro_3a_010 or lro_3l_014 or lro_3d_013 or lro_3d_014 or lro_3r_010 or lro_3r_011 or lro_3r_012 or lro_3r_017 or lro_3s_004 or lro_3s_006 or post_exposure_nonzero_without_mutation or holdout_pre_receipt or holdout_post_receipt or exact_staging or authorized_commit_merge_and_push or terminal_attestation' \
  --no-cov
```

Observed: `18 failed, 279 deselected in 1.05s`, exit `1`.

All 18 failures were behavior-specific. They reproduced every fresh
final-rereview-2 counterexample family: nonnested calibration, partial arrival
pairs, mixed equal-emission sources, forged latent IDs, absent zero-driver
fit/profile evidence, incomplete predictive rows, unavailable and forced-
warning reducer contradictions, incomplete config literals, hidden fixture
side effects, retry command substitution, create-before-validate receipt
behavior, live-state-unbound pre-RNG entry, forged staging blobs, non-object
publication refs, and repeatable incomplete terminal attestation.

## Finding Dispositions

### C1 - Live pre-RNG provenance

`REPAIRED`

- Config, preholdout, and holdout `tracked_state_sha256` values are compared to
  freshly recaptured `PhaseGuardState.analytical_sha256` at every boundary.
- The preholdout literal tracked manifest must equal the live captured ordered
  analytical entries, not merely reproduce a caller-provided digest.
- Config/receipt files are reloaded from current bytes and all spec, config,
  source, tracked-state, self-hash, file-hash, and manifest bindings are checked.
- Holdout payload validation and all live/cross bindings occur before exclusive
  creation. Malformed or forged payloads leave no receipt; pre-existing bytes
  are preserved.
- The complete state is recaptured, identities are reloaded, and bindings are
  repeated immediately before the injected RNG factory. Every mismatch returns
  `STOP_INVALIDATED_POST_EXPOSURE` or raises before creation with zero RNG calls.

### I1 - Exact assigned behavior matrix

`REPAIRED`

- The test file contains `AMENDMENT_TEST_NAMES`, a literal ordered executable
  manifest of exactly 98 unique test names.
- `test_lro_3s_009...` proves that the manifest equals the complete intended
  amendment selection with no missing or extra name.
- The matrix is executed directly by node ID from that manifest, not by the
  former 88-test selector.

### I2 - Fit, denominator, predictive, and reducer contracts

`REPAIRED`

- Nonnested scenarios have development 12 and holdout 24 only. Every
  calibration fit and RNG payload is rejected, including shared-fit scopes.
- Complete split-frame validation is explicit. Arrival requires every
  correct/permuted pair exactly once over development 12 or holdout 24 and uses
  the fixed 4,180/1,045 cell frame.
- Equal-emission observed and all 199 bootstrap pairs share holdout, source
  range 0..23, scope, fit identity, and both variants before reconstruction.
- Every failed fit field is typed. Zero-driver intervals reconcile one-to-one
  with 24 primary fit rows and 24 typed profile interval rows.
- Failed predictive fits emit and validate the literal 17-column schema over
  all 27 ordered cells using `q1..q5` and `early|middle|late`.
- Each local reducer accepts only its exact scenario-specific typed evidence
  schema, rejects missing/extra/contradictory availability, rejects forced
  warnings, and returns only its canonical local reason domain.

### I3 - Authoritative latent frames

`REPAIRED`

- Canonical latent IDs are derived internally from the actual Goal 017
  passable landscape.
- Sparse IDs use the frozen Goal 023 SHA-256 ranking and exact 1,306-cell frame.
- Arrival latent IDs use the frozen alignment-score ranking and exact
  1,045-cell score frame; the complement is the exact 4,180-cell fit frame.
- Caller-nominated `canonical_cell_ids` authority is removed. Analyst and
  evaluator IDs must equal the internally derived frame.
- Applicable, unavailable, failed, and not-applicable latent rows retain the
  complete typed state machine and remain recommendation-neutral.

### I4 - Config, fixture, staging, publication, and terminal guards

`REPAIRED`

- Config validation requires exact model, estimator, five parameter rows in
  order with supports/values, all scenario rows, seed partitions, artifact
  registry, boundary labels, and gate objects. Direct assertions cover gate
  literals `15`, `0.10`, `0.05`, and `0.01`.
- Fixture dispatch accepts only its module-owned side-effect-free service; an
  external closure is rejected before invocation, and extra live/RNG/output
  services are rejected.
- Staging state is captured from injected Git status, worktree `hash-object`,
  cached-path, and index object queries. Validation requires an empty initial
  index, the literal 19-path allowlist, unchanged worktree blobs, exact frozen
  index blobs, and index-only post-staging status.
- A retry uses a typed nonzero failure record, unchanged full envelope, exact
  failed command, retry count zero, and independent approval. Holdout,
  calibration, benchmark, and artifact commands remain nonretryable.
- Commit, merge, and push transitions consume captured Git state and validate
  lowercase object IDs, branch/ref movement, commit parent, tree, local main,
  and remote main semantics for each transition.
- Terminal attestation contains tracked, staged, unstaged, untracked, cached,
  analytical, and candidate state plus every bound hash. Append/stage exact-once
  is enforced by recapturing the live Log/index envelope; no caller
  `already_appended` assertion remains.

## Fourteen-Step Correction Sequence

1. Task 3 and all stochastic/irreversible phases remained blocked: complete.
2. Live state/config/receipt binding at every boundary and before RNG: complete.
3. Validate before exclusive receipt creation and preserve bytes: complete.
4. Literal complete config schema and values: complete.
5. Scenario-specific split authority and exact frames: complete.
6. Complete arrival and same-source equal-emission reconstruction: complete.
7. Zero fit/profile, failed fit, and 27-cell predictive reconciliation: complete.
8. Exact typed scenario evidence and contradiction rejection: complete.
9. Internally authoritative latent cell frames: complete.
10. Owned fixture service boundary with no hidden closure path: complete.
11. Captured staging, exact retry, and transition-specific Git semantics: complete.
12. Complete observed terminal envelope and exact-once append/stage: complete.
13. Behavior RED, rewritten named tests, and literal 98-node manifest: complete.
14. Full validation, hash reseal, one parent-bound pending-review Log child, and
   this report: complete. Fresh independent max rereview remains pending.

## GREEN Evidence

Exact executable 98-node manifest command:

```bash
uv run python -c 'import runpy,pytest; p="tests/test_synth_medium_latent_response_observation_recovery.py"; n=runpy.run_path(p)["AMENDMENT_TEST_NAMES"]; raise SystemExit(pytest.main([*(f"{p}::{x}" for x in n), "--no-cov", "-q"]))'
```

Final observed result: `98 passed in 0.61s`, exit `0`.

Complete Goal file:

```text
297 passed in 703.59s (0:11:43)
```

Observation and relevant upstream synth-medium regressions:

```text
69 passed in 69.92s (0:01:09)
```

Static and structural checks:

- `uv run ruff format --check <source> <tests>`: `2 files already formatted`.
- `uv run ruff check <source> <tests>`: `All checks passed!`.
- `uv run mypy src tests`: `Success: no issues found in 59 source files`.
- tracked and owned-untracked `git diff --check`: `PASS`.
- Goal/spec bodies from `## Objective`: byte-identical, `106597` bytes,
  SHA-256 `855a3c3291dedf473fc1879601987f6126924e71123e4aa515b86805a3bb93eb`.
- Final Log chain: `15/15` parent hashes and `6/6` declared byte counts reproduce.
- Final Git index: empty.

Evidence file hashes:

- 98-node pytest: `c2315393701413425bc37aa22ce6f611957e32eb9579561167d2b035482c0424`
- full Goal pytest: `35c45f8e6e835e89632ef0c49ef51592dc48a34602eb0844e3b245342b08a14e`
- upstream pytest: `b761a19e823f5ea67a58fd04cbf1343e0b0f02b94c27bda14cafc4735b51890b`

## Hashes And Log Shape

Authority and repair tuple:

- Goal: `6883c0188be06c328f09a4e07a9872b366e414abac31bc5241b7d5c72f6b8e3f`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `fc74fae83c6e93701a06d342346ffe803360fb718f2ed34f69bcb610103a7e7b`
- authoritative spec: `af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- amendment proposal: `ee367b6014bf823ffda2f406186179271a0f0e56ac955ea35ae6fb11c3bea15d`
- final rereview 2: `1c9a374b18e33bc95bc7424aced6595197e356d3ab30aa32cd5d840a7f4e0906`
- repaired source: `fe2628800bd0db521a8649285ab0679ce81655877f1b0154c1e5d1b9dd69b180`
- repaired tests: `d3f6cc1920f20c994e8f65ecefca637a5d3e13f46f0b8a0a905030c3231e3069`

Live Log parent immediately before append:

- lines: `2555`
- bytes: `126506`
- SHA-256: `9d6d8b0265720e7eef6102bdc6e8271517b030bdd1c29018c995d7b7d6d8e768`

Final Log after the one child append:

- lines: `2666`
- bytes: `132318`
- SHA-256: `f3bc360138e3ce33abf25b741150a7c59dc2daf5dabd9b8c9360a0b9d95df843`
- record type: `integrated_amendment_final_rereview_2_repair_v1`
- acceptance: `PENDING`
- all scientific/statistical/readiness/schema/code/provenance/max reviews:
  `PENDING`

## Git And Exposure State

```text
branch=codex/spatext-goal023-latent-response-observation-gate
head=53462d0365babf2c8070714a930f69b4071af276
base=53462d0365babf2c8070714a930f69b4071af276
index_entries=0
```

`git status --short` at report time:

```text
 M pyproject.toml
 M uv.lock
?? docs/goals/023-synth-medium-latent-response-observation-recovery-gate/
?? spec/synth_medium_latent_response_observation_recovery_gate.md
?? src/spatext/observe.py
?? src/spatext/synth/medium/latent_response_observation_recovery.py
?? tests/test_observe.py
?? tests/test_synth_medium_latent_response_observation_recovery.py
```

The status includes preserved pre-existing user/orchestrator files outside this
repair's write scope. Nothing was staged.

No Task 3 scenario, live/production RNG construction, simulation, benchmark,
calibration, canonical artifact/config/receipt, freeze, holdout, staging,
commit, push, publication, cleanup, deletion, reset, or restore occurred.
Required validation invoked only deterministic fixture/test RNG objects and
temporary-directory serializers; no Goal 023 production namespace or
canonical output path was exposed. The canonical artifact directory,
`recovery_gate_config.json`, `preholdout_state_receipt.json`, and
`holdout_receipt.json` are absent.

This report records repair completion only. It is not acceptance. Task 3 and
every stochastic or irreversible phase remain blocked until a fresh
hash-specific independent max rereview returns no Critical or Important
finding and all required reviews are accepted.
