# Goal 023 Integrated Amendment Max Audit

date: `2026-07-11`
auditor_profile: `sol_max_auditor`
mode: `independent final audit, read-only except this report`
verdict: `NOT SUPPORTED`
task_3_authority: `BLOCKED`
calibration_authority: `BLOCKED`
holdout_authority: `BLOCKED`

## Claim Audited

The audited claim is that the amended Goal, Plan, Runbook, authoritative spec,
source, tests, and append-only Log form one coherent, executable, fail-closed
contract that preserves the accepted Goal 023 science, closes the prior
provenance and Task 3 authority gaps, and safely authorizes Task 3 without
constructing calibration or holdout material.

For that claim to hold, the accepted proposal's exact tracked-document patch
map must be present; Goal and spec bodies must agree; the literal 11-scenario
registry, schemas, reducers, artifact identities, phase guards, provenance
envelopes, and retry state machine must be executable; all 98 named pre-Task-3
RED behaviors must have behavior-specific coverage; the Log chain must remain
append-only; and no calibration or holdout exposure may have occurred.

## Verdict

`NOT SUPPORTED`.

One Critical and four Important findings remain. The current tuple is not a
safe Task 3 authority. This is also the tuple's own recorded state: the final
Log record is `BINDING_PENDING_FINAL_PRE_TASK3_VALIDATION`, all six fresh review
fields are `PENDING`, and Task 3 is explicitly still blocked
(`Log.md:2347-2386`).

## Findings

### Critical C1: The accepted authority and provenance patch was not applied

The proposal requires replacement of the complete recommendation body and all
affected schemas, insertion of the complete provenance contract, Goal/spec
body identity, replacement of downstream Plan steps, and replacement of the
Runbook's holdout and post-holdout procedures
(`integrated-contract-amendment-proposal.md:1213-1235`, `1237-1401`,
`1403-1568`). The current files contain only abbreviated amendment summaries.

Evidence:

- Goal/spec body equivalence fails. Their integrated-amendment sections differ,
  even though byte-equivalent bodies were mandatory.
- The obsolete recommendation body remains in Goal at `Goal.md:1187-1207` and
  spec at `spec/synth_medium_latent_response_observation_recovery_gate.md:1148-1168`.
- The old scenario, recovery, coverage, latent, predictive, profile, and control
  schemas remain at `Goal.md:1298-1359` and spec `:1259-1320`; required fit
  variants, new fields, and keys were not coordinated into authority.
- No `### Provenance Amendment Contract` exists in Goal or spec. The complete
  phase presence vectors, per-command byte envelopes, Log-append mechanics,
  mutation dispositions, and one-retry state machine are absent.
- Plan Task 3-6 remains the pre-amendment version at `Plan.md:300-420`, despite
  the proposal requiring exact replacements.
- Runbook section 2E is abbreviated at `Runbook.md:169-194`; section 4 still
  deletes outputs and launches live benchmark/calibration without the required
  pre-config and pre-freeze footprint guards (`Runbook.md:248-334`); section 5
  lacks both pre-receipt and post-receipt/pre-RNG guards (`Runbook.md:339-352`);
  section 7 runs commands without per-command envelopes or retry dispositions
  (`Runbook.md:368-389`).
- Source defines a passive `ProvenanceEnvelope` record at
  `latent_response_observation_recovery.py:4813-4830`, but implements no
  envelope capture/comparison, phase guard, Log suffix validator, retry
  dispatcher, receipt transition, staging transition, or commit/push
  transition before the module ends at line 5384.
- No provenance/freeze test from proposal section 11.6 exists.

Consequence: the prior provenance gap remains open in tracked authority and in
executable code. Following the current Plan/Runbook after Task 3 could reach
freeze and holdout without the accepted identity, footprint, receipt, envelope,
and nonzero-disposition protections. Task 3 cannot be authorized on this tuple.

Required correction: apply proposal sections 4-10.3 literally to Goal, spec,
Plan, and Runbook; restore Goal/spec body equivalence; implement the complete
typed phase/provenance state machine; and keep Task 3 blocked until all section
11.6 tests and fresh hash-specific reviews pass.

### Important I1: Required executable coverage is largely absent

The accepted proposal contains 98 named RED behaviors: 11 registry/fit, 20
latent, 14 denominator/control, 20 reducer, 10 artifact/CLI, and 23
provenance/freeze tests (`integrated-contract-amendment-proposal.md:1624-1759`).

The current test file contains only 11 amendment tests at
`tests/test_synth_medium_latent_response_observation_recovery.py:3692-3911`.
Only 3 of the 98 required test names exist exactly. Several IDs were repurposed
for weaker tests: current `T3A-002`, `T3L-003/004`, `T3R-001/002`, and
`T3S-001/002/003` do not implement the behaviors assigned those IDs by the
proposal. There are no `T3D` or `T3P` tests.

The 11 current tests pass, but that does not establish the required contract.
The execution report's `11/11` RED and `12/12` GREEN claim therefore describes
a small substitute suite, not the accepted complete matrix
(`integrated-amendment-execution-report.md:43-53`).

Required correction: add every named test in proposal sections 11.1-11.6 with
the exact assigned behavior, preserve the IDs, run behavior-specific RED before
implementation, then GREEN. Record the exact commands, failures, final hashes,
and results in an append-only Log child. Passing broad pre-existing Task 2 tests
cannot substitute for these tests.

### Important I2: Registry, schemas, fit evidence, and recommendation reduction are not contract-correct

The source's `ScenarioDefinition` has 12 fields while
`SCENARIO_DEFINITIONS_HEADER` has 15, omitting fit scope and variants from the
typed row (`latent_response_observation_recovery.py:4734-4746`, `4942-4958`).
The generated definitions also use values outside the frozen enum domains:
`scenario`, `goal023_binary_transition`, `joint`, `diagnostic_only`, and
`scheduled_count_only` (`:5092-5128`). These conflict with the authority's
literal enums and transportability class.

`validate_fit_execution_row()` checks only a small subset of the 23-column
contract (`:5133-5163`). An independent counterexample showed it accepts a
successful `fit_scope=replicate` row with `fit_index=7`, source range `0..99`,
and source count `100`, although replicate rows require all indices to equal
the scientific replicate and count `1`. It does not enforce split, registry
variant, shared/bootstrap ranges, successful-fit completeness, start counts,
parameter subsets, boundary fields, primary keys, sorting, or cross-table
foreign keys.

`reduce_recommendation()` is not the frozen total reducer (`:5258-5283`). It
has no local scenario reducers or evidence-state validation and tests exact
membership of `"confounding"` rather than canonical `confounding:<reason>`
values. The independent vector with every scenario passing except
`dense_count_exact_model="confounding:dense_joint_failed"` returned rank 1
`model_contract_failed`; the contract requires rank 2
`process_observation_confounded`.

Required correction: implement the literal 11-row registry including parameter
evidence and truth-access enforcement; emit valid scenario definitions in
numbered order; implement all amended headers, types, enums, PKs, sort rules,
fit-variant foreign keys, attempted denominators, shared-fit reconstruction,
and descriptive stress rows; then implement every local reducer and the total
global state machine with canonical reasons and invariant transportability.

### Important I3: The latent formula kernel is correct, but the required diagnostic row contract is missing

The numeric kernel at `latent_response_observation_recovery.py:5166-5255`
implements the 21-category censor mapping, cumulative Brier score, positively
scaled interval score, deterministic first-crossing quantiles, and ordinary
median calculation correctly. Independent hand fixtures reproduced
`0.05/6/6` for a one-category displacement and `1/120/120` for event-at-6
versus censor.

However, no executable layer implements scenario applicability, analyst/evaluator
cell-ID equality, fixed `5225/1306/1045/0` frames, exactly three ordered rows per
scheduled attempt, unavailable-fit rows, inapplicable rows, literal
`fit_succeeded` and `diagnostic_available` states, or schema-only failure of a
missing/malformed row. Invalid input simply raises from the numeric kernel.
There is no test proving latent values and valid unavailability are
recommendation-neutral. Only `T3L-001` and `T3L-002` exist under their required
names; 18 required latent tests are absent.

Required correction: retain the current formulas, add the complete typed row
builder/validator and fixed-frame applicability contract, and implement all
`T3L-003` through `T3L-020` behaviors without adding a latent threshold or
recommendation input.

### Important I4: Artifact and typed hash interfaces do not fail closed

The 22-path tuple and represented-21 versus complete-22 split are present, but
the validators are incomplete (`latent_response_observation_recovery.py:4893-4916`,
`:5305-5355`). Independent temporary-fixture checks found:

- `build_artifact_manifest_document()` and `artifact_snapshot()` accepted all
  22 expected files plus an unexpected extra file;
- `load_frozen_config_identity()` accepted pretty-printed noncanonical bytes
  whose embedded self-hash matched the canonical payload;
- no loader validates `HoldoutReceiptIdentity` or `ReceiptFileIdentity`;
- no phase boundary validates expected paths, full schemas, receipt self/file
  hash separation, or swaps among typed identities; and
- fixture calibration dispatch trusts service-reported zero counters and has
  no injected RNG-factory/live-runner bomb or canonical-output guard
  (`:5364-5384`).

Required correction: reject extra, duplicate, reordered, zero-byte,
nonregular/symlink, or changed artifacts; require canonical bytes and complete
schemas for config and both receipts; implement typed path-bound identities and
phase guards; make fixture dispatch prove rather than trust the four zero
counters; and add all `T3S-001` through `T3S-010` tests.

## Strongest Supporting Evidence

- The supplied bound tuple reproduces exactly: Goal, Plan, Runbook, spec,
  source, tests, and the 2,386-line Log all match their supplied SHA-256 values.
- The append-only children are internally consistent. Prefixes through lines
  2305, 2323, and 2345 reproduce both recorded SHA-256 and byte counts
  `113393`, `114393`, and `115553`.
- The accepted pre-amendment model core remains well covered. A fresh safe
  selection of 15 model/timing/likelihood/firewall/transform tests passed in
  `0.28s`.
- All 11 current amendment tests passed in `0.25s`; their limitation is scope,
  not immediate test failure.
- No Goal 023 artifact directory, config, preholdout receipt, or holdout receipt
  exists. The current RNG payload validator still rejects `split="holdout"`.
  No Task 3, calibration, or holdout command was run by this audit.

## Independent Checks Performed

1. Recomputed all supplied hashes and the Log line count: exact match.
2. Recomputed three successive Log parent hashes and byte counts: exact match.
3. Ran Goal/spec body equivalence: failed, as described in C1.
4. Ran the proposal's canonical-reason presence check: failed; the required
   reducer reason strings are absent from Goal and spec.
5. Counted proposal tests versus current tests: 98 required, 11 current
   amendment tests, 3 exact-name matches.
6. Ran the 11 current amendment tests: `11 passed, 199 deselected`.
7. Ran 15 safe core scientific tests: `15 passed`.
8. Reproduced latent score fixtures independently: exact expected values.
9. Reproduced reducer, fit-row, extra-artifact, and noncanonical-config
   counterexamples: all four exposed the defects above.
10. Verified artifact and receipt absence on disk: all absence checks passed.

## Required Correction Sequence

1. Keep Task 3, calibration, config emission, freeze, and holdout blocked.
2. Apply the proposal's exact document patch map, including Goal/spec body
   identity and complete Plan/Runbook replacements.
3. Add all 98 named tests with strict behavior-specific RED evidence.
4. Implement the complete registry/schema/reducer/artifact/provenance surfaces
   until those tests pass, without changing frozen science.
5. Run the complete non-generative pre-Task-3 validation ladder, reseal every
   bound hash, and append exact parent-bound Log records.
6. Obtain fresh scientific, statistical, executor-readiness, artifact/schema,
   code, and provenance/freeze `ACCEPT` decisions with no Critical or Important
   finding.
7. Repeat this independent max audit on the replacement tuple. Only a clean
   result may authorize the first Task 3 RED test.

## Residual Uncertainty

The prior execution report records a hash-matched full `210 passed` run, but
this audit did not repeat the approximately 13-minute canonical inverse-audit
suite because that cannot remedy the missing amendment behaviors. No generated
Task 3 bundle or CLI exists to inspect end to end. Disk absence and the current
pre-holdout lock provide strong evidence against persistent calibration or
holdout exposure, but cannot prove that no earlier external process ever
created and discarded an in-memory object.
