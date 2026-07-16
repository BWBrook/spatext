# Goal 023 Integrated Amendment Final Rereview 5

Date: `2026-07-12`
Profile: `sol_max_auditor`
Mode: fresh independent adversarial rereview, read-only except this ignored report

## Claim Audited

This review asks whether the exact supplied Goal 023 authority and current
pre-simulation implementation are complete and fail-closed enough to begin Task
3 fixture-only implementation. Authorization requires the frozen ecological and
statistical contract, all artifact schemas, every fit/science reconciliation,
the 98 assigned behaviors, command authority, source identities, and later
repository transitions to reject contradictory evidence before it can support a
gate or recommendation.

The prior rereview and repair reports were treated as leads, not proof. I read
the current Goal, Plan, Runbook, authoritative spec, source receipt, source,
tests, complete Log, integrated amendment proposal,
`integrated-amendment-final-rereview-4.md`, and
`integrated-amendment-final-repair-4-report.md` against live disk and Git state.

Reference labels below are:

- `Goal`: `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`
- `source`: `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `tests`: `tests/test_synth_medium_latent_response_observation_recovery.py`
- `proposal`: `.superpowers/sdd/integrated-contract-amendment-proposal.md`

## Binary Verdict

**NOT SUPPORTED. TASK 3 IS NOT AUTHORIZED.**

No Critical finding was established, but four Important findings remain. Task 3
fixture implementation, Goal 023 RNG/vector construction, production
simulation, runtime benchmarking, calibration, canonical config/artifact or
receipt production, freeze, holdout, real-project staging, commit, push, and
publication remain **BLOCKED**.

| ID | Severity | Result |
| --- | --- | --- |
| I1 | Important | The frozen finite Stouffer warning rule is not implemented; systematic predictive bias with `abs(stouffer_z) > 3` can pass. |
| I2 | Important | Full fit/science reconciliation remains open across recovery intervals, profile evidence, scenario gates, control statistics, and the final recommendation. |
| I3 | Important | Runtime and verification JSON validators accept internally impossible documents, so the 22-artifact authority is not fail-closed in implementation. |
| I4 | Important | The 98-name manifest is exact and green, but several assigned behaviors are only partially or vacuously exercised, including the new counterexamples. |

## Findings

### Important I1: the Stouffer warning threshold is omitted

The Goal is explicit: each predictive cell warns when the Holm-adjusted PIT p
is below `0.01` **or** `abs(stouffer_z) > 3` (Goal:1508-1526). The implementation
computes Stouffer Z at source:8356-8357, but its warning expression at
source:8371-8378 checks only completeness, fit status, nonfinite residuals, and
null aggregates. The later gate at source:8405-8412 checks the incomplete
warning and Holm p-value, but never the finite Stouffer threshold.

A deterministic in-memory probe supplied complete successful dense-development
fit and predictive evidence for all 12 attempted replicates and all 27 cells.
Every standardized residual was finite and equal to `1.0`; PIT values were the
12 uniform midpoints, giving exact finite and non-warning PIT evidence. The
current summary validator accepted:

```text
accepted=True
stouffer_z=3.464101615138
frozen_warning_threshold=3
raw_p=1
warning=False
gate_result=pass
```

The frozen contract requires `warning=true` and `gate_result=fail`. This is a
direct scientific false pass: a coherent signed predictive bias can support a
higher recommendation even though the declared diagnostic is over threshold.

### Important I2: fit/science and final-decision reconciliation is incomplete

The repair correctly froze scenario/parameter truth and now rejects caller-
selected truth. It also recomputes several row-local and summary quantities.
The complete evidence graph is still validated as disconnected tables:

1. Recovery-to-fit reconciliation checks estimate, fit status, starts,
   boundary, and likelihood, but receives no profile rows
   (source:6677-6736).
2. The profile validator checks only groups that the caller supplied. It does
   not require one complete profile group for every required successful
   fit/parameter, derive the recovery interval from those points, or compare
   `interval_lower`, `interval_upper`, and `profile_two_sided` to the recovery
   row (source:7468-7584).
3. Control reconciliation recomputes selected zero, arrival, and equal counts
   and statistics, but does not bind `gate_result`, arrival correlation,
   `silent_misspecification_failure`, scenario reasons, or the final
   recommendation to the evidence (source:7867-8110).

This conflicts with the authority that all interval/error fields are
recomputed, profiles reconcile to the same fit, summaries consume complete
source rows, and caller values are not authority (Goal:2421-2451). It also
conflicts with the requirement that all control values recompute from fit
evidence and no caller boolean stand in for decision rows (Goal:2107-2120,
2598-2615).

Two deterministic in-memory probes were accepted:

```text
contradictory_recovery_profile_accepted=True
recovery_interval=[-3,3]
profile_at_both_bounds_delta=4>2.705543
profile_inside=False
```

The complete 12-row dense development recovery frame declared the full
`beta_driver` support as its interval, while the profile group for the same
fit/parameter placed both support bounds outside the LR interval. Each table
validated separately; no complete-bundle validator rejected the contradiction
or the absent profile groups for the remaining successful fits.

```text
contradictory_control_gates_accepted=True
zero_decision=pass
arrival_wins=24
equal_p=1.0
all_scenario_gate_result=fail
final_recommendation_rank=4
```

The underlying complete control evidence recomputed a passing zero-driver
control, 24/24 correct-alignment wins, and equal-emission `p=1.0`. Replacing all
scenario `gate_result` values with `fail` while retaining a rank-4 final row was
still accepted. The emitted science tables therefore need not describe one
coherent analysis or one reproducible recommendation.

### Important I3: runtime and verification artifacts can self-certify contradictions

The Goal freezes a complete repeated-task frame, deterministic eight-worker LPT
loads, `safety_factor=1.20`, `projected_seconds=1.20*max(worker_loads)`, and a
`1500` second bound (Goal:1280-1305, 2280-2329). It also freezes the
artifact-manifest details represented by `verification.json`
(Goal:2167-2190).

`validate_runtime_projection_document()` instead accepts any safety factor at
least `1`, arbitrary Boolean `includes_profiles`, any integer predictive count,
any integer equal-bootstrap calibration repeat count, merely nonempty duration
arrays, arbitrary nonnegative load/projection vectors, and an unrelated Boolean
`passed` (source:8792-8907). It does not reconstruct task IDs, exact expansion,
LPT assignment, projections, or the pass condition.

`validate_verification_document()` checks the top-level key set, hash shapes,
boundary labels, ordered check names, and basic types. It does not validate the
literal artifact-manifest detail object, bind check outcomes to evidence,
recompute top-level `passed`, or bind the recommendation to the final decision
(source:8914-8948).

The following intentionally impossible documents were accepted in memory:

```text
runtime_accepted=True
safety_factor=9.0
duration_rows=1/1
worker_loads=all_zero
projected_seconds=0/0
passed=True
predictive_reference_count=-999
equal_calibration_repeat_count=999

verification_accepted=True
all_15_checks_passed=False
artifact_manifest_details={}
recommendation_class=latent_response_observation_gate_passed
passed=True
```

Thus exact top-level schemas and enums are not enough to make all 22 artifacts
literal and reproducible. A canonical-looking runtime or verification artifact
can attest to calculations and a recommendation that its own contents refute.

### Important I4: exact node inventory is not meaningful 98-behavior coverage

The proposal, manifest, and AST inventories are exactly 98/98/98, unique, and in
the same order. Every definition contains an executable assertion or
`pytest.raises`, and the exact manifest passes. That is useful inventory and
regression evidence, but inspection establishes material semantic gaps:

- T3A-011 validates recovery and profile inputs independently and never tests a
  recovery interval contradicted by its profile evidence (tests:4629-4768;
  proposal:1647).
- T3L-020 labels one case an invalid posterior, but omits
  `evaluator_cell_ids`; the builder therefore short-circuits before calling the
  posterior evaluator (tests:5139-5164; source:7019-7041; proposal:1672).
- T3D-013 mutates count evidence but never mutates scenario gates,
  `silent_misspecification_failure`, correlation, or final recommendation
  against the recomputed controls (tests:5470-5590; proposal:1690).
- T3D-014 tests failed/unavailable and one nonfinite predictive row, but no
  complete finite cell with `abs(stouffer_z)>3` or a finite Holm rejection
  (tests:5593-5715; proposal:1691).
- T3R-017 checks one local field set to `None`, one local reason at a time, and
  five contradictions. It does not cover interacting finite scenario vectors
  or establish the assigned total local/global mapping for those vectors
  (tests:6180-6202; proposal:1713).
- T3S-001 positively asserts acceptance of the impossible one-row runtime
  expansion and empty verification details described in I3
  (tests:6253-6394). No exact-manifest node rejects the corresponding
  cross-field contradictions.

Consequently, `98 passed` cannot establish that all 98 assigned scientific and
reproducibility behaviors are implemented. Several strengthened examples test
the repaired local case while leaving the higher-order contradiction open.

## Supported Surfaces

The following surfaces survived independent reconstruction and adversarial
inspection:

- The supplied Goal, Plan, Runbook, spec, source, tests, Log, and source-receipt
  file hashes match exactly.
- Goal and spec are byte-identical from `## Objective`: `133582` bytes, SHA-256
  `5daae64f6464f529d31f41523efd01da05ab5f2aa17eb8c9a8d546749e412007`.
- All 17 Log parent hashes and all 8 declared byte counts reproduce. The live
  Log is exactly 2902 lines and 144896 bytes.
- The source receipt and live source APIs independently reconstruct landscape,
  arrival, and combined source identities, frozen counts, and the disjoint
  fit/score frame.
- Scenario/parameter truth is now literal and caller-selected truth is rejected.
  Row-local recovery algebra, complete coverage-source frames, and the tested
  predictive-source frame are materially stronger than rereview 4.
- The Runbook and source contain the same closed ordered registry of 12 exact
  validation argv vectors. All 18 Runbook Bash blocks parse.
- The exact temporary Git integration uses a bare local origin, a canonical
  checkout, a distinct Goal linked worktree, one shared common store, live
  `git write-tree`, commit, fast-forward merge, and pushed ref transition. It
  passed without touching the real repository (tests:7512-7671).
- Canonical terminal path binding, complete exact-once terminal record,
  realistic staged/cached Log transition, non-Log preservation, and immutable
  post-append stop are implemented and pass the current temporary test
  (tests:7673 onward; Goal:2638-2654).
- Live phase/spec/source identities and authoritative spatial frames reproduce.
  Fixture output paths remain isolated from canonical output roots.
- The real index is empty. The canonical artifact directory, config, receipts,
  holdout material, and production Goal 023 CLI are absent. The remote Goal 023
  branch is absent. No real exposure or publication occurred.

These supported surfaces do not cure I1-I4 because a scientifically
contradictory fixture bundle can still pass its validators and tests.

## Exact Authority Tuple

| Surface | Observed SHA-256 | Match |
| --- | --- | --- |
| Goal | `292172dbcdf14d4d44384c630097443a249526fe920a373f741775806f40d5e3` | yes |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` | yes |
| Runbook | `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb` | yes |
| spec | `d5e5b4ca088478fe6c0a95a35aad12698cfc54e949cac001ec6d9b1e3ce21c5f` | yes |
| source file | `00d4871d7de0447293bd86fcafd960aa3ffe7dbabd15fd45e44600a11656e860` | yes |
| tests | `a8ae7c5202d9e4462785a9a62d3a1fade0425a8b28bf8d4e008430283c0c8919` | yes |
| Log | `9b7e9843f0c67cb445b6b90d158fabbf6ce3005f6c487d96e09e9321bbc5d381` | yes |
| source receipt file | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` | yes |

Additional reviewed surfaces:

```text
integrated-amendment-final-rereview-4.md
  b70bf4b331b59ef62fdc73348fb3888e84ec96c554fab67e07ba1c4f9e944749
integrated-amendment-final-repair-4-report.md
  c7b6190581185e40f2227246649d13db5bd76ce5d3b68120fbf7fb8db8ec6d82
integrated-contract-amendment-proposal.md
  ee367be2ce95084d16f051ac9d9b9633786e03343df6616e1faf0ecb010f515d
```

## Independent Source Reconstruction

```text
landscape_sha256=53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a
arrival_sha256=5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba
source_sha256=6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0
counts=6048,5225,823,4605,4289
passable/sparse/fit/score=5225/1306/4180/1045
fit-score disjoint=true
fit-score union=5225
```

The live authority object contains the expected spec hash, this reconstructed
source hash, and the supplied source-receipt file hash.

## Bounded Validation Evidence

Exact executable amendment manifest:

```text
uv run python -c 'import runpy,pytest; p="tests/test_synth_medium_latent_response_observation_recovery.py"; n=runpy.run_path(p)["AMENDMENT_TEST_NAMES"]; raise SystemExit(pytest.main([*(f"{p}::{x}" for x in n), "--no-cov", "-q"]))'
98 passed in 1.65s
exit=0
```

Bounded non-generative Task 2 regression selection, excluding the two expensive
nine-audit executions:

```text
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov -q -k '(lro_2a1 or lro_2a2 or lro_2b) and not all_nine_canonical_local_audits and not all_nine_inverse_audits'
exit=0
```

Static and structural checks:

```text
ruff format --check source/test: 2 files already formatted
ruff check source/test: All checks passed
mypy --no-incremental src tests: Success, 59 source files
git diff --check: pass
owned-file trailing whitespace: none
Runbook Bash parser: 18 blocks, 0 failures
Runbook/source command registry: 12/12 exact and ordered
proposal/manifest/AST: 98/98/98 exact, unique, and ordered
Goal/spec Objective body: identical
Log chain: 17/17 parent hashes, 8/8 declared byte counts
```

The complete 297-test Goal file and its two expensive nine-audit executions
were not rerun in this bounded rereview. The repair-4 report's prior full run was
read but was not used as independent proof. No forbidden production phase was
executed.

## Git And No Exposure

```text
branch=codex/spatext-goal023-latent-response-observation-gate
HEAD=53462d0365babf2c8070714a930f69b4071af276
origin/main=53462d0365babf2c8070714a930f69b4071af276
git_common_dir=/Users/bwbrook/papers/spatext/.git
index=empty
remote Goal 023 branch=absent
```

The pre-existing working tree remains dirty with the supplied Goal 023
authority/implementation. This rereview did not edit any tracked file or Log.
It did not run Task 3, construct production stochastic vectors, benchmark,
calibrate, create canonical artifacts/config/receipts, freeze, expose holdout,
stage the real project, commit, or push. Temporary Git commit/merge/push actions
occurred only inside the pytest-owned integration repository and were removed
by pytest cleanup.

## Complete Corrections Required

1. Keep Task 3 blocked and append no acceptance or terminal Log record.
2. Implement the exact predictive warning rule from Goal:1508-1541. Recompute
   `warning` from source evidence as incomplete/nonfinite/failed fit **or**
   `holm_adjusted_p < 0.01` **or** `abs(stouffer_z) > 3`, then derive
   `gate_result` only from that result. Add complete finite high-Stouffer and
   finite low-Holm counterexamples, including boundary cases at exactly `3`
   and `0.01`.
3. Add one complete science-bundle reconciler over fit, recovery, profile,
   coverage, latent, predictive, and control tables. Derive the exact required
   identity frame from scenario/split/variant authority; reject every missing,
   extra, duplicate, or foreign group before computing a gate.
4. In that reconciler, derive profile interval endpoints, openness, and
   `profile_two_sided` from the validated ordered profile points and the frozen
   LR crossing algorithm. Bind those values to each recovery row and then
   recompute width, coverage, errors, recovery gate, and coverage summary. A
   successful required fit with no complete profile group must fail.
5. Recompute all 18 control rows from validated evidence. This includes zero
   and arrival denominators/events, alignment correlation from the canonical
   source/permutation frame, equal-emission statistic/bootstrap p-value,
   `gate_result`, availability, `silent_misspecification_failure`, the six fixed
   statuses, scenario reasons, and the final rank/class through the declared
   reducer. Reject any caller-selected final row.
6. Make runtime authority executable. Freeze any still implicit per-scenario
   task ID, profile-inclusion, predictive-reference, repeat-count, and equal-
   bootstrap calibration-count literals in Goal/spec. Reconstruct the exact
   calibration/holdout task arrays, stable IDs/order, deterministic LPT loads,
   `1.20` projections, `1500`-second limits, and `passed`; reject every caller
   contradiction.
7. Make verification a cross-artifact validator. Enforce the exact
   artifact-manifest detail schema and represented digest; bind every check to
   its validated artifact/gate evidence; bind recommendation and
   transportability to `control_decision_summary.csv`; and derive top-level
   `passed` rather than accepting it.
8. Preserve exactly 98 test names and order, but strengthen the existing nodes
   rather than adding an unregistered side suite. At minimum close T3A-011,
   T3L-020, T3D-013, T3D-014, T3R-017, and the runtime/verification coverage in
   T3S-001 or another already assigned exact node. Include every counterexample
   printed in this report as an observed RED before repair.
9. Rerun the exact 98-node command, the complete bounded non-generative Goal
   test surface appropriate to the repair, Ruff, mypy, Runbook Bash parsing,
   12-command registry comparison, proposal/manifest/AST audit, Goal/spec body
   identity, source/spatial reconstruction, Log-chain verification, index and
   no-exposure checks, and the real temporary two-worktree/terminal integration.
10. Only after all corrected evidence is green may a repair child with every
    acceptance disposition still `PENDING` be appended to Log. A fresh
    independent `sol_max_auditor` rereview of the new exact tuple remains
    mandatory before Task 3 can be authorized.

## Final Disposition

**NOT SUPPORTED. TASK 3 IS NOT AUTHORIZED.**

The repository-state, source-identity, command-registry, publication, and
terminal repairs are credible. The remaining failures sit directly on the
scientific gate and canonical evidence path: finite predictive bias can pass,
profile and final-decision contradictions can coexist, and runtime/verification
documents can self-certify impossible states. Those are Important
reproducibility defects, so the stop rule is mandatory.
