# Goal 023 Integrated Amendment Final Repair Report

date: `2026-07-12`
profile: `sol_high_specialist`
status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
task_3_authority: `BLOCKED`
calibration_authority: `BLOCKED`
config_emission_authority: `BLOCKED`
freeze_authority: `BLOCKED`
holdout_authority: `BLOCKED`

## Scope

Tracked files changed by this repair:

- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`

Ignored evidence file added:

- `.superpowers/sdd/integrated-amendment-final-repair-report.md`

No Goal, Plan, Runbook, authoritative spec, dependency, lockfile, observation
kernel, source receipt, or other tracked file was modified by this repair.

## RED Evidence

Exact command:

```bash
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py \
  -k 'lro_3a_005 or lro_3a_007 or lro_3a_010 or lro_3l_011 or lro_3l_017 or lro_3d_013 or lro_3r_016 or lro_3s_002 or lro_3s_004 or lro_3s_005 or lro_3s_006 or lro_3s_008 or holdout_pre_receipt or holdout_post_receipt or exact_staging' \
  --no-cov
```

Observed result: `15 failed, 282 deselected in 0.74s`, exit `1`.

The failures reproduced all final-rereview counterexample families:

- registry-inconsistent fit scope and incomplete successful-fit fields;
- duplicate arrival variants and missing observed equal-emission reconstruction;
- short latent frames and malformed typed latent rows;
- invalid frozen control denominators and scenario-impossible local reasons;
- extra represented artifacts, incomplete config/receipt schemas, and forged identities;
- fixture service side effects hidden behind reported zero counters;
- `--phase=calibration` parsing bypass;
- replacing receipt creation and malformed post-receipt RNG entry;
- caller-approved out-of-allowlist staging.

## Repair Outcome

The repair implements one complete pre-RNG provenance state machine using
injected Git command output and real disk hashing. It parses porcelain status
and command phases, revalidates captured state at each boundary, enforces the
literal publication footprint and phase presence vectors, creates receipts
exclusively, loads complete canonical config/preholdout/holdout schemas,
cross-binds their self/file identities, and constructs zero RNG objects on
every tested mismatch.

Fit evidence now enforces registry scope and variants, split frames, complete
successful/failed parameter and boundary states, duplicate-free fixed
`4180/1045` arrival pairs, observed `D`, every one of 199 `D_b`, add-one p,
all six primary-science foreign-key forms, parameter subsets, and frozen
control denominators. The global reducer accepts only scenario-specific
canonical reason domains.

Latent diagnostics require exact authority/analyst/evaluator cell-ID equality
and cardinalities `5225`, `1306`, or `1045`, and validate the complete
applicable/available/unavailable/not-applicable typed row state machine.
Valid finite and valid unavailable rows remain recommendation-neutral.

Artifact representation rejects extras. Config and receipts require complete
nested schemas and canonical bytes. Typed identities are reloaded at phase
boundaries. Fixture dispatch observes injected RNG/output/scientific/payload
services and filesystem changes rather than trusting returned counters. Exact
staging derives the literal 19-path allowlist and blobs from the frozen
candidate; parsed command, retry, publication transition, live supersession,
and complete terminal-envelope guards fail closed.

## GREEN Evidence

- Exact proposal inventory: `98` unique names, `98 passed in 0.63s`.
- Complete Goal 023 test file: `297 passed in 700.66s`.
- Relevant upstream regression set: `69 passed in 46.39s`.
- `uv run ruff format --check` on source/test: pass.
- `uv run ruff check` on source/test: pass.
- `uv run mypy src tests`: `Success: no issues found in 59 source files`.
- `git diff --check`: pass.
- Goal/spec body equivalence: `106597` bytes, SHA-256
  `855a3c3291dedf473fc1879601987f6126924e71123e4aa515b86805a3bb93eb`.
- Existing parent-bound Log records before append: `13/13` reproduced.
- Exact proposal-name inventory: `required=98`, `missing=0`.

## Bound Hashes

- Goal: `6883c0188be06c328f09a4e07a9872b366e414abac31bc5241b7d5c72f6b8e3f`
- Plan: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `fc74fae83c6e93701a06d342346ffe803360fb718f2ed34f69bcb610103a7e7b`
- authoritative spec: `af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e`
- source: `421f0a9b9082c3c66002ce446a2444510b10a0205645e716de048ccda54bc116`
- tests: `dede165ea37c7fc2fb8709b00c72c45001bba2e7a42d5419b4d36696e2774f05`
- source receipt: `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- proposal: `ee367b6014bf823ffda2f406186179271a0f0e56ac955ea35ae6fb11c3bea15d`

## Log Chain

Live parent immediately before append:

- lines: `2463`
- bytes: `121774`
- SHA-256: `a074ede50e6fd797537efdc245bd85be23ebe01e00b74d666aa54ad665840a8e`

New Log shape after the single repair child:

- lines: `2555`
- bytes: `126506`
- SHA-256: `9d6d8b0265720e7eef6102bdc6e8271517b030bdd1c29018c995d7b7d6d8e768`

The child records every independent review as `PENDING` and appends no
acceptance.

## Final State

Branch and identity remain:

- branch: `codex/spatext-goal023-latent-response-observation-gate`
- HEAD: `53462d0365babf2c8070714a930f69b4071af276`
- `origin/main`: `53462d0365babf2c8070714a930f69b4071af276`

The Git index is empty. Existing orchestrator changes in `pyproject.toml`,
`uv.lock`, Goal 023 authority files, observation files, and other untracked
Goal 023 paths were preserved and not reverted.

No artifact directory, recovery config, preholdout receipt, or holdout receipt
exists. No Task 3 scenario, RNG construction, runtime benchmark, calibration,
scientific row, canonical output write, artifact, config, receipt, holdout
payload, exposure, staging, commit, push, publication, deletion, reset,
restore, or broad cleanup occurred.

Recommendation: keep Task 3 and every irreversible phase blocked and request a
fresh hash-specific independent Sol Max rereview of the bound source/test/Log
tuple.
