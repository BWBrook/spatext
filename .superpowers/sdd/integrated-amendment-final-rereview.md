# Goal 023 Integrated Amendment Final Rereview

date: `2026-07-12`
auditor_profile: `sol_max_auditor`
mode: `independent final rereview, read-only except this report`
verdict: `NOT SUPPORTED`
task_3_authority: `BLOCKED`
calibration_authority: `BLOCKED`
holdout_authority: `BLOCKED`

## Claim Audited

The audited claim is that the repaired Goal 023 integrated amendment now forms
one exact, executable, fail-closed pre-Task-3 contract: all prior Critical and
Important findings are closed; all 98 named tests implement their assigned
behaviors; Goal/spec authority is identical; reducer, schema, latent,
artifact, and provenance counterexamples fail closed; the Log remains an exact
append-only chain; no calibration or holdout exposure has occurred; and Task 3
can safely open.

For this claim to hold, passing test names are not enough. The test bodies and
implementation must enforce the literal proposal behavior, especially the
fixed frames, canonical evidence domains, complete schemas, disk-derived typed
identities, exclusive receipts, and pre-RNG provenance guards required by the
accepted fix brief.

## Verdict

`NOT SUPPORTED`.

One Critical and four Important findings remain. The document repair is exact,
but the executable repair is not the accepted complete fail-closed contract.
Task 3 must not open on this tuple.

## Findings

### Critical C1: The provenance phase state machine can cross the pre-RNG boundary on invalid state

The accepted repair required a complete provenance phase state machine and
identity/footprint/envelope/retry/staging/commit guards, with every prior
provenance counterexample failing closed
(`integrated-amendment-max-fix-brief.md:43-51`). The current implementation is
still a caller-asserted fixture surface rather than a disk-derived state
machine:

- `phase_guard_fixture()` manufactures expected branch, commit, manifest, and
  presence values; `validate_phase_guard()` compares those supplied values to
  constants but captures no Git state, path hashes, status, or filesystem
  presence (`latent_response_observation_recovery.py:6323-6360`).
- `guard_holdout_pre_receipt()` uses a replacing write and does not require the
  receipt to be absent. An independent temporary-path counterexample proved it
  overwrites an existing receipt (`:6376-6384`).
- `guard_holdout_post_receipt()` checks only `receipt.is_file()`. It does not
  parse or validate the receipt, config, preholdout receipt, analytical digest,
  self/file hashes, or cross-bindings before calling `rng_factory()`
  (`:6387-6400`). With arbitrary bytes `b"not a receipt\n"`, a canonical
  caller-supplied guard returned `CONTINUE_FROZEN_CANDIDATE` and called the RNG
  spy once.
- `validate_task3_command()` rejects only the space-separated strings
  `--phase calibration` and `--phase holdout`; it accepted
  `--phase=calibration` (`:6217-6220`).

The current source therefore cannot establish the required no-RNG boundary.
The fact that no real Goal 023 RNG or holdout payload has yet been constructed
does not make this guard safe. It means exposure has not happened yet.

Required correction: replace supplied-state mappings with injected but real
state capture; make receipt creation exclusive and non-overwriting; load and
cross-validate complete canonical config/preholdout/holdout identities before
RNG construction; prove all mismatch classes create zero RNG objects; and
validate parsed phase values rather than selected command spellings.

### Important I1: The 98 names exist and pass, but the matrix does not implement all assigned behaviors

The proposal inventory and test definitions match exactly: 98 required names,
98 unique names, no missing name. A fresh bounded run passed `98`, deselected
`199`, and took `0.25s`. However, review of every group found named tests that
exercise only a weaker happy path while their assigned behavior remains
unimplemented:

- `T3A-005/007/010/011` do not cover registry-consistent scope, complete
  successful-fit fields, duplicate arrival variants, observed `D` and add-one
  p reconstruction, parameter subsets, or all six foreign-key forms
  (`tests/test_synth_medium_latent_response_observation_recovery.py:3769-3914`).
- `T3L-011` supplies two cells for a fixed 5,225-cell scenario and accepts the
  emitted `sample_size=5225`; `T3L-017` similarly uses one cell as an available
  diagnostic
  (`tests/test_synth_medium_latent_response_observation_recovery.py:4051-4063`,
  `:4140-4163`).
- `T3D-013` checks only the ideal `24/24/199` case and does not test invalid
  denominators
  (`tests/test_synth_medium_latent_response_observation_recovery.py:4345-4361`).
- `T3R-016/017` do not test scenario-impossible but prefix-valid reasons or all
  canonical finite evidence vectors
  (`tests/test_synth_medium_latent_response_observation_recovery.py:4628-4645`).
- `T3S-002/006/007` neither rejects an extra represented artifact nor proves
  zero side effects independently of service-reported counters
  (`tests/test_synth_medium_latent_response_observation_recovery.py:4711-4719`,
  `:4764-4796`).
- `T3P-012/016/017/019/022` use self-consistent synthetic values but do not
  validate receipt bytes, the literal staging allowlist, Git transition
  semantics, the live Log target, or a complete terminal envelope
  (`tests/test_synth_medium_latent_response_observation_recovery.py:4999-5114`).

This is not merely missing test strength. The independent counterexamples in
I2-I4 pass through the production helpers while all 98 named tests remain
green. The claimed behavior-specific repair and RED/GREEN evidence are
therefore not established.

Required correction: rewrite the affected named tests to exercise every clause
assigned by proposal sections 11.1-11.6, obtain genuine behavior-specific RED
evidence, then implement to GREEN. Do not count a test name as coverage when
the assigned failure mode is absent from its assertions.

### Important I2: Fit schemas, denominators, and the total reducer still accept contradictory evidence

The previous impossible replicate-index counterexample is now rejected and the
canonical dense confounding reason now reaches rank 2. The broader literal
contracts remain incomplete:

- `validate_fit_execution_row()` checks a valid scope enum but never requires
  `fit_scope == registry.fit_scope`. It accepted the equal-emission scenario as
  a replicate-scoped fit. It also accepted a successful ordinary fit with all
  five required parameter estimates and boundary fields null
  (`latent_response_observation_recovery.py:5283-5373`).
- `validate_arrival_fit_pairs()` reduces variants to a set and accepted a
  duplicate correct-alignment row plus one permuted row as one complete pair;
  it enforces neither the fixed disjoint fit/score frames nor duplicate-free
  evidence (`:5397-5408`).
- `recompute_equal_emission_bootstrap()` returns only bootstrap statistics. It
  does not validate observed shared fits or reconstruct observed `D`, every
  `D_b`, and the add-one p as assigned (`:5419-5440`).
- `reconcile_control_summary()` validates no frozen denominator. It accepted
  one zero row, one arrival row, and `equal_bootstrap_succeeded=200`, returning
  `bootstrap_failed_count=-1` (`:5800-5834`).
- `reduce_recommendation()` accepts arbitrary reason strings by prefix. A
  vector with the process oracle set to the impossible local reason
  `confounding:not_a_canonical_oracle_reason` returned rank 2 instead of
  failing the contradictory vector at rank 1 (`:6011-6053`).

Required correction: enforce the literal registry scope/variant mapping,
complete typed successful and failed rows, parameter subsets, boundary and
score fields, duplicate-free paired evidence, observed/bootstrap equal-emission
reconstruction, frozen control denominators, and scenario-specific canonical
local-reason domains before global reduction.

### Important I3: The latent numeric kernel is correct, but fixed frames and row validation remain fail-open

The 21-category event/censor mapping and the three numeric formulas reproduce
the required fixtures: one-category displacement gives `0.05/6/6`, and event
at 6 versus censor gives `1/120/120`. The diagnostic-row layer is still not the
required fixed-frame contract:

- `build_latent_diagnostic_rows()` never requires the supplied cell frame to
  contain the registry's exact `5225`, `1306`, or `1045` IDs. It computes on
  any nonempty frame but writes the registry sample size (`:5586-5651`). A
  one-cell dense fixture was accepted as `diagnostic_available=true` with
  `sample_size=5225`.
- The row builder does not pass evaluator cell IDs into the evaluator, so its
  own path cannot prove analyst/evaluator ID identity (`:5620-5625`).
- `validate_latent_diagnostic_rows()` checks only three metric names, column
  order, and shared identity. It does not validate applicability, sample size,
  fit state, availability/nullability, finite values, error identity, or
  `diagnostic|not_applicable` gate state (`:5654-5670`). Rows with
  `sample_size=1`, `diagnostic_available=false`, `observed_value=999`, and
  `gate_result=pass` were accepted.

Required correction: require exact scenario-specific analyst/evaluator ID
frames and cardinalities before a diagnostic can be available, and validate
the complete typed row state machine. Preserve recommendation neutrality for
valid finite and valid unavailable diagnostics.

### Important I4: Artifact, identity, fixture-dispatch, and staging interfaces are not fail-closed

Several narrow prior examples are fixed: the complete 22-file snapshot rejects
extras and zero-byte files, and the config loader rejects noncanonical bytes.
Other required interfaces remain open:

- `build_artifact_manifest_document()` hashes the 21 represented paths but
  never compares disk contents to the expected set. It accepted all 22 files
  plus `extra.txt` (`:6108-6121`).
- The config and receipt loaders validate canonical bytes and self-hashes but
  no required top-level or nested schema. A config containing only
  `config_sha256` and a holdout receipt containing only `exposed` plus its
  self-hash were accepted (`:6147-6202`).
- `require_phase_identities()` is only a runtime type check. A publicly
  constructed `FrozenConfigIdentity` with unchecked path, arbitrary hashes,
  and noncanonical bytes passed (`:6205-6214`).
- `dispatch_fixture_calibration()` trusts four counters returned by the
  injected service. A service that actually called an RNG spy once and then
  reported zero was accepted (`:6497-6511`).
- `validate_exact_staging()` accepts any `approved_index` supplied by its
  caller. An out-of-allowlist path was accepted when the same tuple was passed
  as `approved_index` (`:6409-6419`).

Required correction: reject extra represented artifacts; validate complete
config and receipt schemas and cross-bindings; make typed identities obtainable
only from validated canonical loaders or revalidate them at the boundary;
instrument fixture dispatch around injected RNG/live-runner/output services so
zero side effects are observed rather than reported; and derive the exact
staging allowlist and blob set from frozen authority, not caller approval.

## Prior Finding Rereview

| Prior finding | Rereview status |
| --- | --- |
| C1 authority/provenance patch absent | Document patch fixed; executable provenance remains Critical and fail-open. |
| I1 98 behaviors absent | All 98 names exist; assigned behavior coverage remains Important and incomplete. |
| I2 registry/schema/reducer incorrect | Original reducer and replicate-index examples fixed; new literal-schema and contradictory-vector counterexamples remain. |
| I3 latent row contract absent | Numeric formulas fixed; fixed-frame and typed-row contract remain Important. |
| I4 artifact/hash interfaces fail open | Complete snapshot and canonical-byte check fixed; represented set, complete schemas, identity proof, dispatch bombs, and staging remain Important. |

## Strongest Supporting Evidence

- The complete bound tuple reproduces exactly:
  - Goal `6883c0188be06c328f09a4e07a9872b366e414abac31bc5241b7d5c72f6b8e3f`;
  - Plan `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`;
  - Runbook `fc74fae83c6e93701a06d342346ffe803360fb718f2ed34f69bcb610103a7e7b`;
  - spec `af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e`;
  - source `a862b269f85ae67b479e8df463582ea4019ce46abae7f20b0cacd6fa75d25458`;
  - tests `e0b0ba396e48c02d51f4477260fd96790e167d8dadb94bce9e674faa2e490ae0`;
  - Log `a074ede50e6fd797537efdc245bd85be23ebe01e00b74d666aa54ad665840a8e`;
  - source receipt `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`.
- Goal and spec bodies from `## Objective` onward are byte-identical:
  `106597` bytes each, SHA-256
  `855a3c3291dedf473fc1879601987f6126924e71123e4aa515b86805a3bb93eb`.
- Every proposal markdown replacement block for Goal/spec/Plan/Runbook is
  present exactly. Normalized schema and artifact patch bodies also match
  exactly.
- All 13 parent-bound Log records reproduce their declared prefix hash; every
  available byte count also matches. Final Log shape is `2463` lines and
  `121774` bytes.
- The exact 98-name inventory is complete and a fresh bounded run passed
  `98 passed, 199 deselected in 0.25s`.
- Fresh bounded static checks passed: Ruff format, Ruff check, mypy over 59
  source files, and `git diff --check`.
- The supplied repair evidence records `297 passed in 731.04s` for the full
  Goal 023 file and `69 passed in 46.95s` upstream. This rereview did not repeat
  the 12-minute full file because executable counterexamples already falsified
  the amendment claim.

## Append-Only And No-Exposure State

- The append-only Log chain is intact through the repair child.
- The canonical artifact directory, recovery config, preholdout receipt, and
  holdout receipt are absent.
- The Git index is empty; HEAD remains
  `53462d0365babf2c8070714a930f69b4071af276`.
- This rereview ran only the 98 deterministic fixture/validator tests, static
  checks, hash/chain checks, and temporary-directory counterexamples. It did
  not run Task 3, a live benchmark, calibration, a Goal 023 RNG/payload,
  holdout, staging, commit, or push.

## Required Correction Sequence

1. Keep Task 3, calibration, config emission, freeze, and holdout blocked.
2. Repair C1 first with a real captured-state and typed-identity pre-RNG phase
   machine; add exclusive receipt semantics and command/phase parsing.
3. Complete registry, fit-row, fit-pair, equal-bootstrap, denominator, and
   scenario-specific reducer validation.
4. Enforce exact latent cell-ID frames and the complete latent row schema.
5. Complete represented-artifact, config/receipt schema, typed identity,
   fixture-side-effect, and literal staging guards.
6. Rewrite the affected named tests to their exact assigned behaviors, obtain
   behavior-specific RED evidence, then GREEN.
7. Run the full non-generative validation ladder, reseal all hashes, append one
   exact parent-bound repair child with reviews pending, and repeat independent
   max rereview.

## Residual Uncertainty

The accepted Task 1/2 numerical science was not challenged by the amendment
counterexamples, and no exposure evidence was found. The principal uncertainty
is implementation completeness: the passing suite currently proves selected
examples and type shapes, not the complete fail-closed state transitions it
names. Until the counterexamples above are rejected by behavior-specific
tests, a green suite cannot support Task 3 authority.
