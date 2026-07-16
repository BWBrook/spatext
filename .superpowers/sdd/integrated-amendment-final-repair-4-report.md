# Goal 023 Integrated Amendment Final Repair 4 Report

Date: `2026-07-12`
Profile: `sol_high_specialist`
State: repair complete; every review and acceptance disposition remains
`PENDING`; Task 3 and every stochastic or irreversible production phase remain
`BLOCKED`

## Scope And Verdict

This repair owns I1-I5 and all 11 correction steps in
`integrated-amendment-final-rereview-4.md`. The bounded repair is complete and
green. It does not authorize Task 3. Fresh independent max-tier rereview is
still required on the exact tuple below.

Tracked files changed by this repair:

1. `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`
2. `spec/synth_medium_latent_response_observation_recovery_gate.md`
3. `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md`
4. `src/spatext/synth/medium/latent_response_observation_recovery.py`
5. `tests/test_synth_medium_latent_response_observation_recovery.py`
6. `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`

Ignored evidence written under `.superpowers/sdd/`:

- `integrated-amendment-final-repair-4-report.md`
- `integrated-amendment-final-repair-4-goal-tests.xml`
- `integrated-amendment-final-repair-4-goal-tests-final.xml`
- `integrated-amendment-final-repair-4-upstream-tests.xml`

Plan, source receipt, dependencies, lockfile, observation kernel, and every
other tracked file were not edited by this repair. The pre-existing
`pyproject.toml`, `uv.lock`, observation-kernel, and unrelated worktree state
were preserved.

## Behavior-Specific RED

Before implementation, eight individually executed existing manifest nodes
failed on the fresh review behaviors:

| Finding | Existing node | Observed RED |
| --- | --- | --- |
| I1 frozen truth | `test_lro_3a_011_every_primary_science_row_reconciles_to_one_fit_row` | forged dense `beta_driver` truth was accepted; `pytest.raises` reported `DID NOT RAISE` |
| I1 summary validity | `test_lro_3d_001_nested_denominators_imputations_and_even_median_are_literal` | negative/nonfinite summary evidence was accepted; `DID NOT RAISE` |
| I2 fixed statuses | `test_lro_3r_010_equal_p_boundary_refit_completeness_and_status_independence` | caller Boolean status evidence passed; `DID NOT RAISE` |
| I3 config version | `test_lro_3s_004_config_and_receipt_self_hashes_are_not_file_hashes` | `schema_version=anything-nonempty` produced a canonical config; `DID NOT RAISE` |
| I4 retry | `test_post_exposure_nonzero_without_mutation_allows_one_approved_exact_retry` | opaque mutating Python argv was authorized; `DID NOT RAISE` |
| I4 Task 6 | `test_task6_validation_dispatch_is_postholdout_only` | the same opaque argv was accepted for dispatch; `DID NOT RAISE` |
| I5 publication | `test_authorized_commit_merge_and_push_transitions_are_literal` | a valid distinct canonical-checkout merge was rejected because checkout roots differed |
| I5 terminal | `test_terminal_attestation_is_exactly_reviewed_appended_and_staged_once` | a newly parented second terminal record was accepted; `DID NOT RAISE` |

These failures exercised existing behavior and APIs. They were not missing
imports, unavailable future artifacts, live optimizer failures, or fixture
setup errors. The strengthened final nodes additionally cover the full 48-row
forged dense frame, 24 null-truth zero-driver rows, arbitrary Log paths,
realistic cached/index changes, and immutable terminal failure.

## Repair Dispositions

### I1: truth, fit evidence, and summaries

- Added one literal ordered `SCENARIO_PARAMETER_TRUTH_ROWS` authority matching
  Goal/spec. Truth-bearing rows retain truth on failed/open fits. Only the five
  continuous-abundance rows are truth-free; equal emission has no recovery
  rows.
- `validate_replicate_recovery_row()` now rejects caller-selected truth,
  nonfinite values, impossible/out-of-support intervals, negative width,
  contradictory boundaries/profiles, and incorrect error/coverage algebra.
- Primary recovery, latent, predictive, and profile rows resolve to exactly one
  fit row and reconcile fit status, variant, source identity, parameter subset,
  estimate, likelihood, starts, boundaries, and profile likelihood-ratio
  algebra.
- Coverage and predictive summaries consume complete validated source frames,
  recompute counts, fractions, exact even medians, full-support imputations,
  PIT/KS/Holm values, warnings, and gates, and reject wrong split counts or
  caller-derived values.
- Control decisions reconcile to 24 zero-driver rows, 24 complete same-source
  arrival pairs, 199 equal/ordered bootstrap pairs, observed/refit likelihood
  statistics, and the six fixed equal-emission status rows.

Counterexample outcomes:

- 48 dense `beta_driver` rows with truth `0.0` versus authority `1.25`:
  rejected before summary/gate.
- 24 successful zero-driver rows with null truth/errors: rejected before
  control reconciliation.
- Negative/nonfinite width or error, partial row, out-of-support estimate,
  mismatched fit estimate/likelihood/status, profile-delta mismatch, or wrong
  summary count: rejected.
- Complete valid recovery/predictive/control frames: accepted and recomputed.

### I2: exact 98 behavior matrix

- Preserved exactly 98 names, order, unique top-level definitions, and exact
  executable manifest.
- Proposal/manifest/AST audit reports `98/98/98`, exact order equality, and all
  98 nodes containing executable assertions or `pytest.raises` checks.
- T3A-005 asserts the independent literal 23-column fit header and complete
  failed-row status.
- T3A-011 exercises full row/fit/profile reconciliation and forged truth.
- T3L-010 covers dense, structured, sparse, and irregular fixtures over every
  observed, expected, and error metric.
- T3D-001 and T3D-004 use distinct 24th/25th and 12th/13th values to prove
  exact ordinary even medians.
- T3R-008 proves global rank 4 versus rank 2; T3R-010 validates six emitted
  status rows rather than a Boolean.
- T3S-004 independently reconstructs config/receipt self hashes and complete
  file hashes.
- T3P-007 mutates every `ProvenanceEnvelope` field.
- T3P-017 uses a real temporary repository with two worktrees and a bare local
  origin through commit, fast-forward merge, and push-state transitions.
- T3P-022 covers canonical path, realistic cached/index state, recursive
  second record, and immutable post-append stop.

### I3: complete external artifact authority

Goal/spec and source now freeze:

- all 22 artifact contract versions as `v1`;
- exact generated JSON `schema_version=v1`, source-receipt `1.0`, receipt
  versions, and `seed_namespace=goal023-holdout-v1`;
- complete scenario role, generation, fit, schedule, effort, expected,
  truth-access, transportability, recommendation, and 13-value gate-family
  domains;
- all 11 literal scenario rows and the complete scenario/parameter truth map;
- exact config model, estimator, parameter, seed, gate, manifest, and boundary
  values;
- complete headers, types, row-specific nullability, primary keys, sort keys,
  enums, and reconciliation rules for all ten CSVs;
- runtime, source, holdout-manifest, verification, report-link, and visual-source
  nested/literal authority.

`Goal.md` and the authoritative spec remain byte-identical from
`## Objective`: `133582` bytes, SHA-256
`5daae64f6464f529d31f41523efd01da05ab5f2aa17eb8c9a8d546749e412007`.

### I4: closed command registry

Runbook section 7 and source contain the same ordered twelve exact argv
vectors. Every entry binds command class, parsed phase, and reviewed transient
disposition. Failure records, retry payloads, authorization, and Task 6 all
resolve through this closed registry before execution. Unregistered opaque,
holdout, calibration, benchmark, regeneration, and artifact commands fail
closed.

### I5: publication and terminal state

- Staging captures branch, HEAD, worktree blobs, index blobs, live
  `git write-tree`, resolved checkout root, and resolved Git common object
  store.
- Commit must occur in the Goal worktree. Merge and push must occur in one
  distinct canonical checkout sharing the same common store, approved tree,
  parent, and local/remote ref semantics.
- The real temporary two-worktree test completed commit, fast-forward merge,
  and local bare-origin push. Pytest cleanup removed the temporary repository;
  no real-project Git mutation occurred.
- Terminal payloads are canonical complete-envelope records bound to the exact
  Goal 023 Log path. A durable existing terminal record blocks every second
  record, including a newly parented one.
- Successful append permits only the exact Log staged/cached blob and status
  transition while preserving all non-Log state. Post-append observation
  failure raises
  `STOP_INVALIDATED_TERMINAL_ATTESTATION_IMMUTABLE` and cannot become
  acceptance.

## GREEN Evidence

Exact executable amendment manifest:

```text
98 passed in 1.63s
```

Complete Goal 023 test file on the final source/test tuple:

```text
297 passed in 707.02s (0:11:47)
```

Relevant upstream observation, landscape, spread-impact, observation-design,
and recoverability-design regressions:

```text
69 passed in 46.69s
```

Static and structural ladder:

```text
Ruff format: 85 files already formatted
Ruff check: All checks passed!
mypy --no-incremental src tests: Success, 59 source files
git diff --check: pass
owned-untracked diff check: 6 files, 0 whitespace failures
Runbook bash: 18 blocks, 0 failures
Runbook/source command registry: 12/12 exact
proposal/manifest/AST: 98/98/98 exact, unique, ordered
Goal/spec Objective body: identical
pre-append Log chain: 16/16 hashes, 7/7 byte counts
post-append Log chain: 17/17 hashes, 8/8 byte counts
```

Independent source reconstruction:

```text
landscape_sha256=53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a
arrival_sha256=5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba
source_sha256=6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0
counts=6048,5225,823,4605,4289
passable/sparse/fit/score=5225/1306/4180/1045
fit-score disjoint=true; union=5225
```

## Authority Hashes

- Goal:
  `292172dbcdf14d4d44384c630097443a249526fe920a373f741775806f40d5e3`
- Plan unchanged:
  `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook:
  `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb`
- authoritative spec:
  `d5e5b4ca088478fe6c0a95a35aad12698cfc54e949cac001ec6d9b1e3ce21c5f`
- source:
  `00d4871d7de0447293bd86fcafd960aa3ffe7dbabd15fd45e44600a11656e860`
- tests:
  `a8ae7c5202d9e4462785a9a62d3a1fade0425a8b28bf8d4e008430283c0c8919`
- source receipt unchanged:
  `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- final rereview 4:
  `b70bf4b331b59ef62fdc73348fb3888e84ec96c554fab67e07ba1c4f9e944749`
- final Log:
  `9b7e9843f0c67cb445b6b90d158fabbf6ce3005f6c487d96e09e9321bbc5d381`

## Log Parent And New Shape

Live parent captured immediately before append:

```text
lines=2784
bytes=138517
sha256=0bbd23f592a57c875e9b12a109c06cedf5912f8eb8697e14ba156bc50966d030
```

New Log after the one repair child:

```text
lines=2902
bytes=144896
sha256=9b7e9843f0c67cb445b6b90d158fabbf6ce3005f6c487d96e09e9321bbc5d381
record_type=integrated_amendment_final_rereview_4_repair_v1
parent_prefix_exact=true
acceptance=PENDING
all seven review dispositions=PENDING
```

No acceptance child was appended.

## Git And No Exposure

```text
branch=codex/spatext-goal023-latent-response-observation-gate
HEAD=53462d0365babf2c8070714a930f69b4071af276
origin/main=53462d0365babf2c8070714a930f69b4071af276
index=empty
remote Goal 023 branch=absent
```

The canonical artifact directory, recovery config, preholdout receipt, holdout
receipt, and production Goal 023 CLI are absent. No Task 3 command, production
RNG object/vector/payload, simulation, runtime benchmark, calibration,
canonical artifact/config/receipt, production freeze, holdout, real-project
staging, commit, push, publication, reset, restore, cleanup, or deletion
occurred.

The only Git commit/merge/push operations were inside a pytest-owned temporary
repository explicitly authorized by rereview step 8. The only generated
evidence files are ignored JUnit/report files under `.superpowers/sdd/`; none
is a canonical Goal 023 artifact, config, or receipt.

## Required Next Gate

Task 3 remains blocked. The next legitimate action is a fresh independent
max-tier rereview of the exact Goal/spec/Runbook/source/test/Log tuple above.
