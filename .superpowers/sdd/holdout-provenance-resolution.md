# Goal 023 Holdout-Provenance Resolution

Date: 2026-07-11

Status: `PROPOSED_PRE_HOLDOUT_BINDING_INTERPRETATION`

This ignored note is not itself authority. It proposes the exact operational
interpretation to append to Goal 023 `Log.md`, test, and independently accept
before Task 5. It does not authorize holdout exposure, alter authoritative
document bytes, or construct an RNG payload.

## Recommendation

Use an append-only `Log.md` interpretation plus executable tests. A tracked
Goal/Plan/Runbook/spec amendment is not currently required.

This is defensible because the accepted authority already:

- makes both receipts immutable;
- requires a later invalidating finding to be reported without modifying either
  receipt;
- excludes append-only `Log.md` from the analytical tracked-state digest;
- permits `Log.md` to record hashes while forbidding it from changing equations,
  thresholds, code, tests, schemas, or conclusions; and
- requires every later Log entry to preserve the exact full-file parent chain.

The interpretation below selects the only reading that satisfies those clauses
simultaneously. It adds no estimand, gate, schedule, RNG mapping, schema field,
or scientific conclusion.

If either the provenance/freeze reviewer or executor-readiness reviewer rejects
this reading as exceeding existing authority, stop before Task 4 freeze and make
a tracked, hash-resealed contract amendment. Do not expose holdout while that
question remains open.

## Current Authority And State

Accepted authority tuple:

```text
Goal     cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20
Plan     df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e
Runbook  78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed
spec     0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d
```

Current Log anchor at this review:

```text
parent_line_count: 2042
parent_sha256: 4f1773f513e35378a5126772d37c3f86c0cf69ea8560b81ebe4720ed622461e8
```

The future binding append must recompute its parent immediately before append;
it must not copy this anchor if intervening append-only work has occurred.

The preholdout receipt, holdout receipt, and Goal 023 artifact directory are
currently absent. Task 2a2 is implemented pending independent review. Nothing in
this resolution advances the scientific task gate.

## Exact Binding Interpretation

The following text is normative once appended to `Log.md` against the then-live
parent and independently accepted.

### 1. Immutable Receipt Fields Are Exposure-Time Assertions

`holdout_receipt.json` is an immutable exposure receipt, not a mutable terminal
disposition record.

- `exposed = true` means successful exclusive atomic receipt creation has
  irrevocably committed and burned the named holdout namespace. It does not
  assert that all scientific rows were subsequently emitted.
- `invalidated = false` means no invalidating event was known at the instant of
  atomic receipt creation.
- `no_contract_change = true` means the analytical tracked-state digest matched
  the frozen preholdout receipt and config at that instant.
- `receipt_sha256` authenticates those exposure-time assertions with that field
  omitted from its own canonical hash payload.

The same fields in `holdout_manifest.json` reproduce the receipt-time snapshot;
they are not a later mutable disposition channel.

A crash, partial failure, mutating post-holdout check, or later review finding
does not rewrite either object. It burns the namespace and is recorded as a
later provenance disposition. A finding requiring an analytical tracked change
sets publication disposition to `STOP_INVALIDATED_POST_EXPOSURE`; it does not
change the receipt's historical `invalidated = false` or
`no_contract_change = true` values.

### 2. Literal Analytical Tracked-Manifest Membership

"Every allowed tracked path" means the exact Runbook section 8 publication
allowlist. The analytical digest membership is that list minus only:

```text
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
```

Therefore the literal sorted 16-path analytical manifest is:

```text
AGENTS.md
README.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
pyproject.toml
scripts/run_synth_medium_latent_response_observation_recovery.py
spec/report_log.md
spec/synth_medium_latent_response_observation_recovery_gate.md
src/spatext/observe.py
src/spatext/synth/medium/__init__.py
src/spatext/synth/medium/latent_response_observation_recovery.py
tests/test_observe.py
tests/test_synth_medium_latent_response_observation_recovery.py
uv.lock
```

No glob, import walk, current `git ls-files` result, current dirty-path set, or
runtime discovery may add or omit a member. Every member must exist as a regular
file at freeze. The source receipt is included; the generated ignored config is
not a tracked path. Unchanged upstream dependencies are bound by the exact base
commit, clean-worktree guards, source APIs, and source digest receipt rather than
silently added to this Goal 023 publication manifest.

The canonical aggregate remains SHA-256 over lexically sorted UTF-8 lines:

```text
<file_sha256><two spaces><relative_path>\n
```

The preholdout receipt's `tracked_file_manifest` must equal this exact path set
and order. At final staging, Runbook section 8 requires all 19 allowlisted paths,
not merely a subset. The subset rule in `verify-staged-state` is an intermediate
safety guard and cannot weaken final exact-set acceptance.

### 3. Config And Digest Ordering

The ignored config is emitted only after the final 16 analytical files exist.
The required order is:

1. Finish all permitted analytical edits and pre-holdout review fixes.
2. Compute the exact 16-file manifest and `tracked_state_sha256` from disk.
3. Emit the candidate config containing that digest.
4. Compute `config_sha256` from canonical config bytes with only
   `config_sha256` omitted; `tracked_state_sha256` remains in the hash payload.
5. Independently review the exact config bytes, config hash, 16-file manifest,
   tracked digest, source hash, and spec hash together.
6. Append the approved hashes and review dispositions to `Log.md`; the Log is
   outside the analytical digest.
7. Rerun the complete pre-holdout ladder. Any analytical mutation returns to
   step 1 and requires a newly emitted and reviewed config before freeze.
8. `freeze-tracked-state` only reproduces the config's digest and atomically
   creates `preholdout_state_receipt.json`. It must never patch or regenerate
   the reviewed config.
9. `verify-tracked-state` independently reproduces the same digest from disk.

Thus Plan Task 4's later "compute" step is an independent freeze-time
reproduction of a digest already present in the reviewed config, not permission
to insert a digest after config approval.

### 4. Post-Holdout Review Evidence Write Scope

After atomic holdout receipt creation, the only permitted tracked writes are:

1. the machine-created immutable `holdout_receipt.json`; and
2. append-only, provenance-only records at the end of Goal 023 `Log.md`.

The Plan's "machine-created tracked receipt only" limits scientific command
output and analytical tracked state. It does not revoke the spec's separately
defined append-only provenance plane. No other tracked path may change.

Each post-holdout Log append must:

- name and reproduce the exact full-file parent line count and SHA-256;
- bind the authority tuple, config hash, tracked-state digest, both receipt
  hashes, artifact-manifest hash, and reviewed artifact-set hash;
- identify reviewer role and immutable reviewer disposition;
- record findings and publication disposition without changing any artifact
  recommendation, gate result, schema, threshold, or scientific conclusion;
- use `CONTINUE_FROZEN_CANDIDATE` only when no finding requires an analytical
  change; otherwise use `STOP_INVALIDATED_POST_EXPOSURE`; and
- leave every prior Log byte unchanged.

Reviewers remain read-only. One designated provenance writer performs exact
appends after independently checking the returned disposition. No review report
may be improvised into another tracked file.

### 5. Potentially Mutating Hooks Are Check-Only Gates

`pre-commit run --all-files` contains `trailing-whitespace`,
`end-of-file-fixer`, `ruff-format`, and `ruff --fix`, all of which can mutate
tracked bytes. Its post-holdout meaning is:

- qualify the exact command as a no-op on the final analytical bytes before
  freeze;
- immediately before the post-holdout command, capture the 16-file manifest,
  aggregate digest, and tracked status;
- run the command once as a check-only gate;
- immediately reproduce the same manifest, digest, and status; and
- accept the command only if it exited zero and changed no tracked byte.

No post-holdout formatter or fixer output is an authorized repair. Any tracked
mutation, even one made automatically by a successful hook, is an invalidating
event: preserve the mutated state and receipts, record
`STOP_INVALIDATED_POST_EXPOSURE`, and stop. Do not restore, rerun, amend, or
continue under the namespace.

Apply the same before/after guard to every command capable of modifying tracked
bytes. `uv build` may replace ignored `dist/`; it may not change the 16-file
manifest or the immutable holdout bundle. Verification may inspect the holdout
bundle but may not regenerate scientific rows.

### 6. Task 6 Validation Ladder

Task 6 "full validation ladder" means, in order:

1. Runbook section 7 post-holdout read-only verification on the frozen bytes,
   with the check-only guards above.
2. Artifact, receipt, manifest, tracked-digest, branch/base, ignored-output, and
   status checks.
3. Exact 19-path staging from Runbook section 8.
4. `git diff --cached --check` and `verify-staged-state`.
5. Fresh final review of the exact cached candidate plus the proposed terminal
   Log-attestation bytes.
6. Exact terminal-append verification, restaging of `Log.md`, and repetition of
   the nonmutating staged-state, digest, receipt, artifact, branch/base, and
   status guards immediately before commit.

It does not mean Runbook section 4. After exposure, never delete the bundle,
rerun runtime benchmarking or calibration, rerun holdout, or regenerate any
scientific artifact. The section 4 ladder remains exclusively pre-holdout.

### 7. Final Review And Log Recursion

All ordinary post-holdout review records must already be appended and staged
before final review. The fresh final reviewer inspects:

- the exact cached candidate;
- the immutable config, artifacts, receipts, and validation evidence;
- the live 16-file digest and exact 19-path staged set; and
- the exact proposed terminal-attestation payload as bytes, including its
  live Log parent line count and parent SHA-256.

On acceptance, the reviewer's returned terminal-attestation payload is itself
the approved append. The provenance writer appends those exact bytes once,
stages `Log.md`, and proves:

- the previous Log is a byte-for-byte prefix;
- the appended suffix equals the reviewer-approved payload byte-for-byte;
- the parent line count/hash reproduces;
- the 16-file digest, receipts, config, artifacts, and every non-Log staged blob
  are unchanged; and
- no further Log append will occur before commit.

Do not append a second statement saying that the terminal append was reviewed.
The exact-suffix proof closes the recursion. If the final reviewer does not
accept, append no acceptance record. A required analytical change invalidates
the exposed holdout and stops publication.

## Required Tests Before Freeze

- Exact receipt-schema test with exposure-time values and self-hash omission.
- Receipt-before-RNG test and pre-existing-receipt rejection before RNG
  construction.
- Receipt-created-then-failure test proving the namespace is burned and the
  receipt is never rewritten.
- Post-review invalidation test proving receipt bytes remain unchanged while a
  separate provenance disposition records the stop.
- Exact sorted 16-path manifest equality test, including the source receipt and
  excluding only Log plus the two self-referential receipts.
- Missing member, extra member, substituted member, duplicate member, and path
  reordering rejection tests.
- Config test proving `tracked_state_sha256` exists before `config_sha256` is
  approved and participates in the canonical config hash.
- Freeze test proving a digest mismatch fails without changing config bytes or
  creating the preholdout receipt.
- Atomic preholdout-receipt creation and independent disk-reproduction tests.
- Log append test proving exact parent count/hash, unchanged prefix, and
  provenance-only record type.
- Hook qualification check proving the configured mutating hooks are a no-op on
  the exact pre-freeze candidate.
- Guard test proving any post-command tracked-byte change returns invalidation,
  not an auto-fix success.
- Task 6 dispatch test proving the post-holdout ladder cannot call cleanup,
  runtime benchmark, calibration, holdout, or scientific artifact generation.
- Final-attestation test proving exact approved-suffix append, one terminal
  attestation only, and no review-append-review recursion.

All tests use temporary synthetic fixtures and non-holdout namespaces. They
must not instantiate, derive, preview, or inspect a Goal 023 holdout payload or
vector.

## Independent Review Checklist

### Provenance/Freeze Reviewer

- Confirm the authority tuple and then-live Log parent reproduce.
- Confirm this interpretation changes no authoritative bytes or scientific
  contract.
- Confirm the literal 16-path manifest is exactly Runbook section 8 minus only
  Log and the two named self-referential receipts.
- Confirm upstream unchanged dependencies remain protected by base/status and
  source-receipt guards.
- Confirm config review occurs only after the digest is embedded and before the
  excluded preholdout receipt is created.
- Confirm post-holdout Log records are append-only provenance, not analytical
  changes.
- Confirm receipt fields remain immutable historical assertions after any later
  invalidation.

### Executor-Readiness Reviewer

- Confirm every ambiguity has one executable branch and one stop path.
- Confirm receipt and hash mismatches fail before RNG construction.
- Confirm all potentially mutating validation is prequalified and guarded.
- Confirm Task 6 invokes section 7 plus staged-state guards, never section 4.
- Confirm the terminal-attestation protocol has no self-reference or recursive
  review requirement.

### Scientific Reviewer

- Confirm no estimand, equation, parameter, support, scenario, schedule,
  replicate count, gate, denominator, recommendation precedence, or RNG mapping
  changes.
- Confirm later invalidation is a publication/provenance disposition and does
  not rewrite the immutable scientific result or receipt.

### Final Pre-Exposure Acceptance

- All tests above pass on the final candidate.
- Scientific, executor-readiness, and provenance/freeze reviewers return
  hash-specific `ACCEPT` with no Critical or Important finding.
- The exact interpretation and dispositions are appended to `Log.md` using the
  live parent chain.
- A fresh full pre-holdout validation cycle passes after the append; analytical
  bytes remain unchanged and the config/digest pair is regenerated and
  re-reviewed if any analytical byte changed.
- The preholdout receipt is absent until the final freeze operation.
- The holdout receipt and every holdout payload, vector, row, and artifact are
  absent until all gates pass.

## Amendment Threshold And Remaining Hold

An authoritative tracked amendment is required only if a reviewer concludes
that any resolution above changes field semantics rather than clarifying their
forced exposure-time meaning, that "allowed tracked path" cannot refer to the
Runbook allowlist, or that Task 5's write scope absolutely forbids the spec's
append-only Log provenance channel. Such a finding is a pre-exposure contract
blocker and must be resolved and resealed before any holdout construction.

Until the interpretation, tests, and independent acceptances are present in the
tracked Log chain, status remains:

```text
HOLDOUT_BLOCKED_PENDING_BINDING_INTERPRETATION_AND_TESTS
```
