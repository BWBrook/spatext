# Goal 023 Integrated Amendment Final Rereview 3

Date: `2026-07-12`
Profile: `sol_max_auditor`
Mode: fresh independent adversarial rereview, read-only except this ignored report

## Claim Audited

This review asks whether the exact current Goal 023 pre-simulation contract is
complete and fail-closed enough to begin Task 3 fixture-only implementation.
Operationally, authorization requires all frozen scientific identities,
schemas, denominators, cell frames, recommendation rules, side-effect
boundaries, and repository-state transitions to agree with current disk/Git
state, and every invalid state to fail before receipt or RNG construction.

The supplied prior reports were treated as leads, not proof. The current Goal,
Plan, Runbook, authoritative spec, source receipt, source, tests, complete Log,
amendment proposal, both prior final rereviews, and the final repair-2 report
were read and checked against the live worktree.

## Binary Verdict

**NOT SUPPORTED. Task 3 is NOT AUTHORIZED.**

One Critical and five Important findings remain. Task 3 fixture implementation,
Goal 023 RNG construction, runtime benchmarking, calibration, config emission,
artifact/config/receipt production, freeze, holdout, staging, commit, and push
remain **BLOCKED**.

The exact 98-node manifest is genuine and green, but it does not exercise the
counterexamples below. Most seriously, a config/preholdout/holdout identity
tuple with a correct live analytical digest but false spec and source identities
crosses the post-receipt pre-RNG boundary and calls the supplied RNG factory.

| ID | Severity | Result |
| --- | --- | --- |
| C1 | Critical | Live spec/source authority is not bound to config or receipts; a false canonical tuple creates a new receipt and crosses the pre-RNG boundary. |
| I1 | Important | All 98 names exist and pass, but several named behaviors remain weaker than their assigned contract. |
| I2 | Important | Fit-domain, arrival-denominator, and predictive typed-state contracts accept or reject scientifically wrong states. |
| I3 | Important | The current Goal/spec do not contain complete literal schemas for all artifacts they call authoritative. |
| I4 | Important | Retry, ordinary Log append, and publication-tree authorization remain partly caller-asserted rather than bound to current captured state. |
| I5 | Important | Fixture bundle writing is deterministic but is not constrained away from the canonical production artifact path. |
| M1 | Minor | The Runbook includes narrative prose inside an executable `bash` block. |

## Findings

### Critical C1: False spec/source identities create a receipt and cross the pre-RNG boundary

The repaired phase machinery now captures branch, HEAD, base, status, the
literal analytical manifest, disk hashes, presence vectors, and the aggregate
`tracked_state_sha256`. It also reloads canonical config and receipt bytes and
rechecks the live state immediately before RNG entry. Those are substantial
repairs.

The remaining gap is at the authority-to-disk binding:

1. `_validate_config_schema()` checks only that `spec_sha256` and
   `source_sha256` look like lowercase SHA-256 values
   (`latent_response_observation_recovery.py:7363-7369`).
2. `_validate_live_phase_bindings()` binds only the aggregate tracked-state
   digest and cross-binds config/receipt values to one another
   (`:7847-7884`). It never checks `spec_sha256` against the actual spec file
   hash or derives `source_sha256` from the live source receipt.
3. The test fixture labels arbitrary `"a" * 64` and `"b" * 64` as valid
   spec/source identities (`tests/...recovery.py:3919-3928`).
4. `guard_holdout_pre_receipt()` therefore validates and creates a new receipt
   carrying false authority (`source:7943-7976`).
5. `guard_holdout_post_receipt()` repeats the same incomplete checks and then
   calls `rng_factory()` (`source:7979-8019`).

The current live authority values are:

```text
authoritative spec SHA-256  af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e
derived source_sha256       6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0
source receipt SHA-256      5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb
```

A deterministic temporary-directory probe used the exact current spec and
source-receipt bytes, a correct aggregate analytical digest, canonical config
and receipt serialization, and a list append as the RNG spy. It created no
NumPy RNG or Goal 023 payload:

```text
disk_spec_sha256=   af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e
config_spec_sha256= aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
derived_source_sha256= 6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0
config_source_sha256= bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
post_receipt_result= CONTINUE_FROZEN_CANDIDATE
rng_factory_calls= 1
```

The corresponding pre-receipt probe reported:

```text
spec_identity_matches= False
new_receipt_created= True
receipt_bound_false_spec= aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

This directly falsifies both the complete-validation-before-create claim and
the reject-invalid-input-before-stochastic-execution claim. C1 is Critical.

### Important I1: The exact 98-node manifest overstates behavioral coverage

AST and proposal inventory checks found exactly 98 unique required names, 98
manifest entries in the same order, 98 unique top-level definitions, no
missing name, and no duplicate definition. The exact node-ID command passed:

```text
98 passed in 0.60s
```

The names are real, but several tests certify weaker behavior:

- T3S-004 and T3P-011/T3P-012 build their supposedly valid identities from
  arbitrary spec/source hashes, masking C1.
- T3D-013 checks all-holdout rows and one missing row, but never supplies mixed
  development/holdout arrival evidence (`tests:4838-4895`).
- T3A-005 does not test natural-support enforcement or the mandatory failed
  status of a boundary equal-rate MLE.
- T3D-014 covers failed-fit rows, but not the required nullable serialization
  of a nonfinite standardized residual.
- T3P-004 proves exact command equality against the first failure record, but
  supplies no current envelope at retry authorization (`tests:5656-5673`).
- T3P-001 treats a caller boolean as proof that an arbitrary suffix binds the
  complete envelope.

The green matrix is useful regression evidence, but not evidence that all 98
assigned behaviors are implemented.

### Important I2: Fit, control, and predictive evidence is not fail-closed

#### Fit-domain evidence

`validate_fit_execution_row()` requires finite estimates and strict rate
ordering, but does not check estimates against the frozen natural supports
(`source:5951-5993`; Goal lines 98-108). It also accepts a successful
equal-rate fit at its support boundary even though the literal rule requires
`fit_succeeded=false` and
`failure_code=equal_rate_mle_noninterior` (Goal lines 1693-1698).

Observed deterministic probes:

```text
out_of_support_alpha_accepted= 999.0
boundary_equal_rate_success_accepted= True
```

#### Arrival holdout denominator

`reconcile_control_summary()` groups arrival rows only by `fit_index` and
variant (`source:6768-6781`). It does not require `split_id=holdout` or require
both rows in a pair to share that split. A mixed frame of 12 complete
development pairs plus 12 complete holdout pairs was accepted as the full
24-pair holdout control:

```text
arrival_split_counts= {'development': 12, 'holdout': 12}
accepted_summary= {'zero_attempted': 24, 'zero_evaluable': 24,
 'arrival_attempted': 24, 'arrival_evaluable': 24, 'arrival_wins': 24,
 'bootstrap_converged_count': 199, 'bootstrap_failed_count': 0}
```

This permits development evidence to satisfy an untouched-holdout decision.

#### Predictive nonfinite state

The frozen contract requires a nonfinite standardized residual to serialize as
an empty value with `standardized_residual_nonfinite=true` and to force a
warning (Goal lines 1443-1494). The validator instead requires every numeric
field to be finite whenever `diagnostic_available=true` and requires the flag
to be false (`source:6929-6938`). The required state is therefore
unrepresentable:

```text
required_nonfinite_predictive_state_rejected=
  ValueError available predictive row requires a successful finite state
```

These are scientific evidence-contract failures, not matters of taste.

### Important I3: Several canonical artifact schemas are not self-contained

The Goal/spec contain complete schemas for `scenario_definitions.csv`,
`fit_execution_evidence.csv`, and `control_decision_summary.csv`. For six other
fit-derived tables they provide headers and keys, then say that existing types
and nullability remain unchanged (Goal lines 1717-1753). No current earlier
section defines those types and nullability.

More seriously, config parameters are defined as every field in
`model_parameter_contract.csv` except two status fields (Goal lines
2084-2085), but the current Goal/spec contain no literal header, type schema,
primary key, sort rule, enum domains, or definition of those two status fields
for `model_parameter_contract.csv`. Source code fills the ambiguity with an
internal nine-field tuple, which is not a substitute for frozen external
authority.

The zero-driver reconciler adds another internal eight-column
`ZERO_DRIVER_INTERVAL_EVIDENCE_HEADER`, rather than reconciling against a
fully defined canonical profile/interval artifact. Task 3 cannot implement or
validate exact emitted schemas from an authority that depends on absent
"existing" definitions.

### Important I4: Operational provenance remains partly caller-asserted

The captured staging implementation now checks the literal 19-path allowlist,
worktree blobs, index blobs, and index-only status. Terminal attestation also
checks the real Log path, exact reviewed payload, observed append, and newly
staged Log blob. Those repairs are supported.

Three remaining interfaces are not fully observed:

1. `authorize_retry()` checks the original failure's before/after envelopes
   but accepts no current envelope or authorized Log-only transition
   (`source:7694-7722`). After an independently visible current-state mutation,
   the same failure record still authorized the retry:

   ```text
   intervening_envelope_changes= ('config_file_sha256',)
   retry_authorized_without_current_state= ('pytest', '-q')
   ```

2. `validate_post_exposure_log_append()` accepts
   `binds_complete_envelope: bool` rather than parsing/recomputing the suffix
   bindings (`source:7646-7663`). An arbitrary suffix was accepted when the
   caller supplied `True`.
3. `validate_publication_transition()` checks captured refs, parents, and the
   post-commit tree, but receives `approved_tree` as a raw caller string and
   has no binding to the validated captured staging/index state or a captured
   `git write-tree` result (`source:8111-8208`). It therefore cannot prove that
   the committed tree is the exact cached candidate.

Retry authorization, ordinary provenance appends, and commit transition need a
single observed state chain, not separately self-consistent caller claims.

### Important I5: Fixture bundle output is not protected from the canonical path

The exact review execution remained temporary-only and side-effect-free. The
owned fixture dispatch service is also a genuine no-op boundary. However,
`emit_fixture_bundle()` accepts any `Path` and writes the 22 canonical artifact
names without checking that the resolved destination is a verified temporary
fixture root or differs from
`artifacts/synth_medium_latent_response_observation_recovery`
(`source:7604-7619`). T3S-010 always passes `tmp_path`, so it does not prove the
production namespace is unreachable.

No canonical-path counterexample was executed because this review was
explicitly forbidden from producing artifacts. Static control flow is
unambiguous: the path boundary is absent. A Task 3 fixture helper must fail
before writing when given the production artifact directory or any alias of it.

### Minor M1: One Runbook command block is not executable

Runbook line 359 places the prose sentence beginning `Immediately before`
inside a fenced `bash` block. Copying that exact block attempts to execute the
prose before `freeze-tracked-state`. Move the sentence above the fence.

## Strongest Supporting Evidence

The current tuple and frozen authorities reproduce exactly:

| Object | SHA-256 / size |
| --- | --- |
| source | `fe2628800bd0db521a8649285ab0679ce81655877f1b0154c1e5d1b9dd69b180` |
| tests | `d3f6cc1920f20c994e8f65ecefca637a5d3e13f46f0b8a0a905030c3231e3069` |
| Log | `f3bc360138e3ce33abf25b741150a7c59dc2daf5dabd9b8c9360a0b9d95df843`; 2666 lines; 132318 bytes |
| Goal | `6883c0188be06c328f09a4e07a9872b366e414abac31bc5241b7d5c72f6b8e3f` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `fc74fae83c6e93701a06d342346ffe803360fb718f2ed34f69bcb610103a7e7b` |
| authoritative spec | `af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e` |
| source receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |
| amendment proposal | `ee367b6014bf823ffda2f406186179271a0f0e56ac955ea35ae6fb11c3bea15d` |
| final rereview 2 | `1c9a374b18e33bc95bc7424aced6595197e356d3ab30aa32cd5d840a7f4e0906` |

Goal and spec bodies from `## Objective` are byte-identical: `106597`
bytes, SHA-256
`855a3c3291dedf473fc1879601987f6126924e71123e4aa515b86805a3bb93eb`.

Independent source reconstruction reproduced:

```text
landscape_sha256=53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a
arrival_sha256=5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba
counts=(6048 landscape, 5225 passable, 823 water,
        4605 final colonised passable, 4289 finite prey extirpations)
```

The current implementation's passable frame equals the accepted landscape;
the independently recomputed SHA-ranked sparse frame is exactly 1306 cells;
the independently recomputed alignment partition is exactly 4180 fit plus
1045 score cells with zero overlap.

The literal scenario registry has 11 rows. Nested scenarios use `12/24/48`
development/calibration/holdout replicates; all seven nonnested scenarios use
`12/0/24`. The config constants contain five ordered parameter rows, 10 seed
partition fields, 13 gate fields, and the exact 22-path artifact registry.
The checked gate literals include `15`, `0.10`, `0.05`, and `0.01`.

The current Log was read and parsed in full. All 15 parent SHA-256 bindings
reproduce; all six declared parent byte counts reproduce. The historical
legacy break is explicitly quarantined, and the current append-only root and
every later child are intact.

## Bounded Validation

Fresh exact manifest command:

```bash
uv run python -c 'import runpy,pytest; p="tests/test_synth_medium_latent_response_observation_recovery.py"; n=runpy.run_path(p)["AMENDMENT_TEST_NAMES"]; raise SystemExit(pytest.main([*(f"{p}::{x}" for x in n), "--no-cov", "-q"]))'
```

Observed: `98 passed in 0.60s`, exit `0`.

Static and structural checks:

```text
proposal/AST/manifest: required=98, unique=98, manifest_matches=true,
                       defined=98, missing=[], duplicate_defs=[]
Ruff format check:     2 files already formatted
Ruff check:            All checks passed!
mypy src tests:        Success: no issues found in 59 source files
git diff --check:      pass
Goal/spec body hash:   identical
```

The full 297-test Goal file was not rerun. The user requested the exact 98-node
manifest and bounded static checks, and the direct counterexamples already
resolve the authorization claim. Prior full-suite reports were not used as
current proof.

## Repository And Exposure State

```text
branch: codex/spatext-goal023-latent-response-observation-gate
HEAD:   53462d0365babf2c8070714a930f69b4071af276
base:   origin/main = 53462d0365babf2c8070714a930f69b4071af276
index:  empty
```

The canonical artifact directory, `recovery_gate_config.json`,
`preholdout_state_receipt.json`, `holdout_receipt.json`, and the production
Goal 023 CLI script are absent. The exact pre-review dirty footprint is
unchanged. No Task 3 scenario, production RNG, seed vector, simulation,
runtime benchmark, calibration, config emission, canonical artifact or
receipt, freeze, holdout, staging, commit, push, cleanup, reset, or restore was
run.

The 98 tests and independent probes used only deterministic arrays, temporary
directories, canonical serializers under those directories, fake Git runners,
and list-append RNG spies. No NumPy RNG was constructed by the amendment
manifest or this rereview.

## Complete Correction Sequence

1. Keep Task 3 and every stochastic or irreversible phase blocked. Do not
   append acceptance to `Log.md`.
2. Derive the expected spec identity from the live analytical spec file and
   derive `source_sha256` by parsing the exact accepted source receipt. Require
   the receipt file itself to match
   `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`.
3. At config emission, freeze, pre-receipt, post-receipt, and immediately
   before RNG, require config and both receipts to match those independently
   derived live identities, not merely one another. Add direct false-spec and
   false-source counterexamples for both receipt creation and RNG entry.
4. Preserve validate-before-exclusive-create semantics. Any invalid authority
   must leave no new config or receipt; every post-create verification failure
   must have an explicit immutable stop disposition without replacing prior
   bytes.
5. Enforce every successful estimate's natural support, strict rate ordering,
   and boundary consistency. A boundary `lambda_equal` MLE must emit the exact
   failed row and failure code required by the Goal.
6. Make control reconciliation require all 24 arrival pairs to be holdout rows,
   require both variants in each pair to share split/source identity, and call
   the complete arrival-frame validator rather than rebuilding a weaker group.
7. Implement the required predictive nonfinite state: successful fit and
   available diagnostic, nullable standardized residual, nonfinite flag true,
   and mandatory downstream warning. Validate metric domains and algebraic
   relationships as part of the literal row schema.
8. Restore complete, self-contained headers, types, nullability, keys, sort
   rules, and enum domains for `model_parameter_contract.csv` and every table
   currently relying on unspecified "existing" schemas. Remove or formally
   authorize the substitute zero-profile interval schema and bind decisions to
   canonical emitted profile/recovery evidence.
9. Bind retry authorization to a freshly captured current envelope plus the
   sole permitted reviewed Log-only transition. Reject any intervening byte,
   status, identity, config, receipt, artifact, or index change.
10. Replace `binds_complete_envelope: bool` with parsed/recomputed suffix
    bindings. Bind the publication `approved_tree` to the validated captured
    index, for example through a module-issued captured `git write-tree`
    identity linked to `CapturedStagingState`.
11. Make fixture output accept only a module-issued temporary fixture root, or
    explicitly reject the resolved canonical artifact directory and aliases
    before the first write. Add a no-write canonical-path counterexample.
12. Rewrite affected T3A/T3D/T3S/T3P tests to include every counterexample
    above. Capture behavior-specific RED, implement to GREEN, and retain the
    literal 98-node manifest with no missing or extra node.
13. Move Runbook line 359 outside the `bash` fence and statically validate all
    executable Runbook blocks.
14. Rerun the exact 98-node manifest, bounded static ladder, complete
    non-generative regression suite, source/frame reconciliation, authority
    hashes, Log-chain verifier, empty-index check, and no-exposure checks.
15. Append one new exact parent-bound repair child only after those checks,
    leave all review dispositions pending, and obtain a fresh independent
    max-tier rereview of the new source/test/Log tuple.

## Residual Uncertainty

The accepted Task 1/2 numerical likelihood and spatial-source work was not
falsified by this review, and the current repository shows no holdout or
production exposure. The unresolved risk is the pre-simulation contract
itself: false authority can cross RNG entry, development evidence can satisfy
a holdout denominator, and required artifact states are not all representable
or self-contained. Until those counterexamples fail closed on a newly sealed
tuple, Task 3 authorization would be scientifically and procedurally unsafe.

## Stop Rule

The binary gate is failed. The next legitimate action is bounded RED-GREEN
contract repair and another hash-specific independent rereview, not Task 3.
