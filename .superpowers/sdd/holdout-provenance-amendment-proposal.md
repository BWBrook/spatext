# Goal 023 Narrow Tracked Provenance Contract Amendment Proposal

Date: 2026-07-11

Status: `PATCH_READY_PRE_EXPOSURE_ONLY`

## Scope And Stop Boundary

This proposal amends provenance execution mechanics only. It changes no
estimand, equation, parameter support, scenario, schedule, replicate count,
gate, denominator, recommendation precedence, RNG mapping, schema field, or
scientific conclusion. It authorizes no holdout construction, exposure,
calibration, artifact generation, scientific rerun, or publication.

The amendment fixes exactly four review findings:

1. explicitly authorize provenance-only `Log.md` appends after exposure;
2. define the disposition and retry rule for a non-mutating nonzero validation;
3. guard every immutable byte class around every post-exposure command; and
4. assert the pinned branch/HEAD/base and reject tracked or out-of-footprint
   changes at config emission, freeze, and immediately before receipt creation
   and RNG construction.

Holdout remains blocked until the tracked amendment is applied, all amendment
tests pass on temporary non-holdout fixtures, the amended authority tuple is
hash-resealed, and fresh scientific, executor-readiness, and provenance/freeze
reviewers return hash-specific `ACCEPT` with no Critical or Important finding.

## Independently Verified Authority

Current pre-amendment authority:

```text
branch   codex/spatext-goal023-latent-response-observation-gate
HEAD     53462d0365babf2c8070714a930f69b4071af276
base     origin/main = 53462d0365babf2c8070714a930f69b4071af276
Goal     cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20
Plan     df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e
Runbook  78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed
spec     0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d
Log      2222 lines; a531eb33d0afb1ffdb91efcf0cddc37bd0b8327269b074bb175b566a85039203
```

Verified clauses requiring amendment:

- Goal lines 714-719 and spec lines 729-734 protect only the analytical digest;
  neither defines the complete post-exposure byte envelope.
- Plan Task 5 lines 349-352 literally permits only the machine receipt, while
  Goal/spec already place append-only `Log.md` outside the analytical digest.
- Runbook section 7 lines 345-362 runs commands, including mutating hooks, with
  no complete byte-envelope guard and no nonzero/no-mutation branch.
- Runbook pins branch/HEAD at lines 6-9 and verifies branch/base late at lines
  421-424 and 435-454, but does not bind config emission, freeze, or the two
  pre-RNG checkpoints to that pin.
- The interpretation at Log lines 2069-2222 authorizes Log appends and guards
  the analytical digest, but does not specify a non-mutating nonzero retry,
  guard the Log prefix, both receipts, config, and every artifact byte around
  every command, or require the pinned branch/HEAD/base and footprint checks at
  all three irreversible checkpoints.

## Shared Normative Text

Use the following exact text wherever this proposal says to insert **Shared
Provenance Amendment Contract**. Goal and spec receive the complete text. Plan
and Runbook receive the task-specific text specified later, avoiding divergent
paraphrases.

```markdown
### Provenance Amendment Contract

This provenance-only amendment changes no scientific contract or result. The
pinned repository identity is branch
`codex/spatext-goal023-latent-response-observation-gate`, HEAD
`53462d0365babf2c8070714a930f69b4071af276`, and base ref `origin/main` resolving
to the same commit. Config emission, `freeze-tracked-state`, and the holdout
phase immediately before exclusive `holdout_receipt.json` creation and again
immediately before any RNG object or payload construction must each fail closed
unless that identity is exact, the literal 16-file analytical manifest is
complete and reproduces its digest, every tracked change is inside the Runbook
section 8 allowlist, and no untracked non-ignored or other out-of-footprint path
exists. A failure at config emission writes no config; a freeze failure changes
no config byte and creates no preholdout receipt; a pre-receipt failure creates
no holdout receipt; a post-receipt/pre-RNG failure preserves the immutable
receipt, constructs no RNG object or payload, burns the namespace, and records
`STOP_INVALIDATED_POST_EXPOSURE`.

After exclusive atomic holdout-receipt creation, tracked writes are limited to
that machine-created immutable receipt and append-only provenance records at the
end of Goal 023 `Log.md`. The Log authorization is explicit and independent of
the scientific-command output restriction. A Log append must reproduce its
exact parent line count and SHA-256, preserve every parent byte as an exact
prefix, bind the authority tuple, config hash, analytical digest, both receipt
hashes, artifact-manifest hash and complete artifact-set hash, identify the
writer/reviewer role and immutable disposition, and change no analytical
contract or artifact result. One designated provenance writer may append only
an independently approved payload. No other tracked write is authorized.

Every command started after exposure, including inspection, hashing, validation,
review preparation, staging, a provenance append, and publication guards, must
run inside one fail-closed before/after envelope. Immediately before the command
capture: branch, HEAD and base; tracked and untracked non-ignored status; the
literal 16-file path/hash manifest and aggregate digest; the current Log byte
count, line count and SHA-256 as the immutable prefix; existence and SHA-256 of
both receipts; the frozen-config SHA-256; and the exact lexically sorted
artifact path/hash manifest, including the artifact-manifest file itself, plus
its aggregate artifact-set SHA-256. Also capture the cached path/blob manifest
so an index-only transition cannot conceal a byte change. Immediately after the
command reproduce all immutable bytes. Missing, added, replaced, reordered, or
changed artifact bytes are a mutation. For an authorized Log append only, the
captured Log must remain the exact prefix and the suffix must equal the
independently approved payload byte for byte. An exact staging command may
change only the index to the predeclared allowlisted path/blob set; it may not
change a working-tree byte. The authorized commit may change only HEAD from the
pinned parent to a commit whose parent and complete tree equal the approved
parent and cached candidate; subsequent fast-forward and push commands may make
only the exact repository-identity transitions already specified in Runbook
section 9. Every other command must leave the complete Log, index, identity,
status, and footprint unchanged. The envelope applies separately to each
command, not once around a command batch. The holdout command must internally
apply the same frozen-state guard immediately after receipt creation and before
RNG construction, then establish the immutable artifact snapshot after
successful emission for all later commands.

A zero exit with an unchanged envelope is `CONTINUE_FROZEN_CANDIDATE`. Any byte,
identity, status, or footprint mutation is `STOP_INVALIDATED_POST_EXPOSURE`,
whether the command exits zero or nonzero: preserve state, receipts, config and
artifacts; append the stop disposition if the Log prefix remains appendable; do
not restore, repair, amend, or retry under the namespace. A nonzero exit with an
otherwise unchanged envelope is
`STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION`; it is not scientific
invalidation, but it does not satisfy validation and publication must pause. A
single retry is permitted only for the exact same non-generative validation
command when an independent executor-readiness reviewer records that the first
failure was transient, confirms the complete envelope is unchanged, and
approves the exact retry command. No edit, dependency change, environment
mutation, cleanup, regeneration, calibration, holdout execution, RNG command,
or artifact-producing command may occur between attempts. The sole permitted
intervening command is one authorized exact Log append that records the
independent transient classification and approves the exact retry; it advances
only the guarded Log prefix. Holdout and any scientific or artifact-generating
command are never retryable. If the one retry exits zero with an unchanged
envelope, record `CONTINUE_FROZEN_CANDIDATE`; if it again exits nonzero without
mutation, record
`STOP_NONMUTATING_VALIDATION_FAILURE`, preserve the namespace and immutable
bytes, and stop publication without calling the scientific result invalid. No
second retry is permitted.
```

## Exact Tracked Document Modifications

### `Goal.md`

Placement: insert the complete **Shared Provenance Amendment Contract** after
the bullet ending at current lines 723-726 (atomic `holdout_receipt.json`
creation and pre-existing-receipt failure), before the eight-worker-process
bullet. Do not alter any surrounding scientific bullet.

Placement: in `## Acceptance And Stop Rules`, append this paragraph after the
existing acceptance paragraph and before `Stop on oracle failure...`:

```markdown
Provenance acceptance additionally requires the complete command envelope at
each post-exposure command, exact pinned branch/HEAD/base and footprint guards
at config emission, freeze, pre-receipt and pre-RNG, and a terminal disposition
for every nonzero validation under the one-retry rule. These are provenance
gates only and cannot alter a scientific gate or result.
```

### `Plan.md`

Placement: in Task 3, after current step 7, insert:

```markdown
8. Add red-green executable provenance-amendment tests using only temporary
   non-holdout fixtures. The tests must cover explicit post-exposure Log
   authorization, the complete immutable-byte envelope, nonzero/no-mutation
   disposition and one-retry rule, and fail-closed identity/footprint checks at
   config emission, freeze, pre-receipt, and pre-RNG. No test may construct,
   derive, preview, or inspect a Goal 023 holdout payload.
```

Placement: replace the Task 4 write-scope Log bullet with:

```markdown
- Goal 023 `Log.md` for append-only provenance records, including amendment
  supersession, reviewed hashes, freeze evidence, and immutable dispositions;
  no Log record may change science or analytical bytes.
```

Placement: replace Task 4 steps 4-8 with:

```markdown
4. Before emitting the candidate config, assert the pinned branch/HEAD/base,
   exact analytical manifest, accepted tracked footprint, and absence of every
   untracked non-ignored or out-of-footprint path. Fail without writing config.
5. Emit and inspect frozen config, source provenance, schemas, calibration
   tables, and visuals. Embed the reproduced analytical digest before computing
   and approving `config_sha256`.
6. Have independent scientific, provenance, validation, and contrarian
   reviewers inspect calibration behavior, exact candidate bytes, identity,
   footprint, and frozen hashes.
7. Record the approved config/source/spec hashes in append-only `Log.md`.
8. Rerun the complete pre-holdout validation ladder. Any analytical mutation
   returns to config emission and fresh review. No tracked analytical, test,
   spec, CLI, threshold, or documentation change is permitted after freeze.
9. Immediately before `freeze-tracked-state`, repeat the pinned identity,
   manifest, status, and footprint checks. Reproduce, never patch, the config
   digest; atomically create the immutable preholdout receipt; then verify the
   config is byte-identical and the receipt and disk manifests agree.
```

Placement: replace the Task 5 write scope with:

```markdown
Write scope:

- generated ignored holdout artifacts during the one authorized holdout
  execution;
- machine-created tracked immutable `holdout_receipt.json`; and
- append-only, provenance-only records at the end of Goal 023 `Log.md`, written
  by one designated provenance writer from independently approved exact bytes.

No other tracked write is permitted after exposure.
```

Placement: replace Task 5 steps 1-5 with:

```markdown
1. Immediately before exclusive receipt creation, assert the pinned
   branch/HEAD/base, exact analytical manifest/digest, exact accepted tracked
   footprint, no untracked non-ignored or out-of-footprint path, frozen config,
   and preholdout receipt. Fail before creating the holdout receipt on mismatch.
2. Atomically create the immutable holdout receipt. Immediately repeat the same
   checks plus receipt self-hash before constructing any RNG object or payload.
   A failure burns the namespace, constructs no RNG, and records
   `STOP_INVALIDATED_POST_EXPOSURE`.
3. Execute holdout once against the frozen config, produce the required ignored
   artifacts without changing tracked analytical bytes, and freeze the exact
   artifact path/hash manifest and aggregate artifact-set hash. Never retry the
   holdout or an artifact-generating command.
4. Run every later command in its own complete immutable-byte envelope. Apply
   the zero, mutation, and non-mutating-nonzero dispositions and the single
   independently approved retry rule exactly as defined in Goal/spec.
5. Obtain independent read-only scientific, contrarian, provenance, code, and
   artifact review. Record only approved append-only provenance payloads in
   `Log.md`.
6. If a finding requires a tracked analytical change, record
   `STOP_INVALIDATED_POST_EXPOSURE` without modifying either receipt and stop for
   Barry's approval of a fresh namespace. A terminal non-mutating validation
   failure stops publication but does not itself invalidate the scientific
   result or authorize a fresh namespace.
```

Placement: replace Task 6 steps 1-5 with:

```markdown
1. Run only the Runbook section 7 post-holdout ladder. Wrap each individual
   command in the complete immutable-byte envelope; never dispatch section 4.
2. Resolve every nonzero through the provenance disposition and one-retry rule.
   Do not continue merely because no byte changed.
3. Stage the exact 19-path allowlist. Reject every extra staged, tracked,
   unstaged, or untracked non-ignored path and confirm generated/build outputs
   are ignored.
4. Dispatch a fresh final reviewer against the exact cached candidate, complete
   immutable envelope, validation output, and exact proposed terminal Log
   payload. Append only the exact approved bytes and re-run every envelope and
   staged-state guard immediately before commit.
5. Any mutation or required analytical change records
   `STOP_INVALIDATED_POST_EXPOSURE` and stops publication. A terminal
   non-mutating validation failure records
   `STOP_NONMUTATING_VALIDATION_FAILURE` and stops publication without rewriting
   scientific disposition. Otherwise commit, fast-forward canonical `main`,
   push, and prove post-push equality.
```

Keep existing Task 6 step 6 (`Do not start Goal 024.`) unchanged.

### `Runbook.md`

Placement: after current line 294, before `After independent calibration
approval...`, insert:

```markdown
Before candidate config emission, run the implementation's identity-and-footprint
guard. It must assert the pinned branch, HEAD and `origin/main` commit; reproduce
the literal 16-file manifest; reject every tracked change outside the section 8
allowlist and every untracked non-ignored or other out-of-footprint path; and
write no config on failure. The emitted config must already contain the
reproduced analytical digest before `config_sha256` is computed.
```

Placement: immediately before the `freeze-tracked-state` command at current
lines 299-302, insert the same identity-and-footprint guard invocation. The
implementation command name may follow the existing CLI pattern, but its
observable contract is exact: nonzero on any identity, manifest, status, or
footprint mismatch; no config-byte change; no preholdout receipt creation.

Placement: replace sections `## 5. Execute Holdout Once` through the prose
immediately before `## 6. Inspect Immutable Holdout Artifacts` with:

````markdown
## 5. Execute Holdout Once

Immediately before the holdout command's exclusive receipt creation, assert
the pinned branch
`codex/spatext-goal023-latent-response-observation-gate`, HEAD and
`origin/main` commit
`53462d0365babf2c8070714a930f69b4071af276`; reproduce the 16-file manifest and
digest; reject tracked changes outside section 8 and every untracked non-ignored
or other out-of-footprint path; verify the frozen config and preholdout receipt;
and require the holdout receipt to be absent. Fail before receipt creation on
any mismatch.

```bash
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase holdout \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
```

The command atomically creates the immutable tracked receipt before exposure.
After receipt creation and immediately before constructing any RNG object or
payload, it must internally repeat the identity, footprint, analytical digest,
config, preholdout-receipt, and holdout-receipt self-hash checks. Failure at this
checkpoint preserves the receipt, constructs no RNG, records
`STOP_INVALIDATED_POST_EXPOSURE`, and burns the namespace. On successful
emission, capture and freeze the exact artifact path/hash manifest, including
the artifact-manifest file, and its aggregate artifact-set hash.

Never delete the Goal 023 bundle, rerun holdout, or rerun any artifact-producing
command. A finding requiring a tracked analytical change invalidates publication
and requires Barry's approval plus a fresh seed namespace.
````

Placement: replace the opening sentence and command block of section 7 (current
lines 343-362) with:

````markdown
Do not regenerate data or change tracked analytical files. Before and after
**each individual command below**, capture and compare the complete provenance
envelope: pinned branch/HEAD/base; tracked and untracked non-ignored status;
16-file manifest and digest; current Log byte count, line count and SHA-256 as
an immutable prefix; both receipt hashes; frozen-config hash; exact artifact
path/hash manifest including its manifest file; and aggregate artifact-set hash.
Do not use one guard around the block.

```bash
git diff --check
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run pre-commit run --all-files
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase verify \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase verify-tracked-state \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
git status --ignored --short artifacts dist
git status --short --branch --untracked-files=all
```

Accept a command only on zero exit and an unchanged envelope. Any mutation is
`STOP_INVALIDATED_POST_EXPOSURE`. A nonzero with an unchanged envelope is
`STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION`; pause publication.
Retry the exact same non-generative command at most once, only after independent
executor-readiness approval that the failure was transient and the complete
envelope remained unchanged. No intervening change or generative command is
allowed. Success records `CONTINUE_FROZEN_CANDIDATE`; a second unchanged nonzero
records `STOP_NONMUTATING_VALIDATION_FAILURE` and stops publication without
scientific invalidation. Holdout and artifact-producing commands are never
retryable.
````

Placement: after the section 8 paragraph ending at current line 428, insert:

```markdown
Post-exposure `Log.md` appends are explicitly authorized provenance writes, not
analytical changes. Guard each append as one command: the captured Log must
remain an exact prefix, the suffix must equal independently approved bytes, and
every other envelope member and every non-Log staged blob must remain unchanged.
```

Placement: at the start of section 9's final guard block, require the same
complete per-command envelope and the nonzero disposition rule before commit.
The existing branch/HEAD/base assertions remain and are not weakened.

### `spec/synth_medium_latent_response_observation_recovery_gate.md`

Placement: insert the complete **Shared Provenance Amendment Contract** after
the bullet ending at current lines 738-741 (atomic `holdout_receipt.json`
creation), before the eight-worker-process bullet.

Placement: after current lines 1340-1346 defining the canonical tracked-state
digest, append:

```markdown
The analytical digest is only one member of the post-exposure provenance
envelope. The immutable Log prefix, both receipts, frozen config, artifact
manifest, every artifact file, repository identity, and accepted footprint are
guarded with it around each post-exposure command under the Provenance Amendment
Contract. Append-only provenance records are explicitly authorized after
exposure and remain outside the analytical digest.
```

Placement: in `## Acceptance And Stop Rules`, append the same provenance
acceptance paragraph specified for `Goal.md` after the existing acceptance
paragraph and before the stop paragraph.

### `Log.md`

Do not edit or delete any byte of the interpretation at lines 2069-2222. On the
current exact parent only, append this record before applying or accepting the
tracked amendment:

```markdown

## 2026-07-11 - Holdout-Provenance Interpretation Supersession

record_type: `holdout_provenance_binding_interpretation_v1_disposition`
parent_line_count: `2222`
parent_sha256: `a531eb33d0afb1ffdb91efcf0cddc37bd0b8327269b074bb175b566a85039203`
target_record_type: `holdout_provenance_binding_interpretation_v1`
target_record_start_line: `2069`
target_record_end_line: `2222`
status: `superseded_pending_amendment`

The target interpretation remains preserved byte for byte but is not authority
for holdout exposure. Independent review found four unresolved provenance
execution gaps: explicit post-exposure Log authorization in tracked authority,
non-mutating nonzero validation disposition and retry, complete immutable-byte
guards around every post-exposure command, and pinned identity/footprint guards
at config emission, freeze, pre-receipt, and pre-RNG. This disposition changes
no science and authorizes no holdout construction or exposure. Holdout remains
blocked pending a tracked, hash-resealed amendment, executable non-holdout
tests, and fresh hash-specific acceptance.
```

Before appending, reproduce the declared parent. If either parent value differs,
stop and regenerate this administrative record against the then-live parent;
never alter prior Log bytes.

After all tracked amendment files and tests are final, append a separate
`holdout_provenance_contract_amendment_v2` record. It must bind the then-live Log
parent, amended Goal/Plan/Runbook/spec SHA-256 values, pinned branch/HEAD/base,
test commands and results, reviewer roles and hash-specific dispositions, and
status `BINDING_PENDING_FINAL_PRE_EXPOSURE_VALIDATION` or
`BINDING_ACCEPTED_PRE_EXPOSURE` as the evidence warrants. Do not place guessed
hashes or placeholders in tracked Log text.

## Later Executable Test Contract

Add these tests to
`tests/test_synth_medium_latent_response_observation_recovery.py` before freeze.
They must use `tmp_path`, fake tracked files, fake receipts/artifacts, injected
command runners, and RNG-factory spies. They must never construct, derive,
preview, or inspect a Goal 023 holdout payload.

1. `test_post_exposure_log_append_accepts_exact_provenance_suffix_and_parent`
   proves explicit authorization, parent reproduction, unchanged prefix, exact
   approved suffix, required hash bindings, and no other changed byte.
2. `test_post_exposure_log_append_rejects_prefix_change_or_analytical_payload`
   rejects insertion, deletion, rewrite, wrong parent, unapproved suffix, and
   any scientific/analytical field change.
3. `test_post_exposure_zero_exit_requires_complete_unchanged_envelope`
   proves zero alone is insufficient and compares every envelope member.
4. `test_post_exposure_nonzero_without_mutation_allows_one_approved_exact_retry`
   proves the pending disposition, independent transient classification, exact
   command equality, no intervening change, and one successful retry.
5. `test_post_exposure_second_nonmutating_nonzero_stops_without_invalidation`
   proves terminal stop, preserved receipts/config/artifacts, unchanged
   scientific disposition, and rejection of a second retry.
6. `test_post_exposure_mutation_invalidates_for_zero_or_nonzero_exit`
   parameterizes exit status and proves mutation always invalidates and forbids
   retry or restoration.
7. `test_post_exposure_guard_detects_each_immutable_byte_class`
   parameterizes analytical file, Log prefix, preholdout receipt, holdout
   receipt, frozen config, artifact-manifest file, represented artifact file,
   missing/extra artifact, branch, HEAD, base, tracked status, and untracked
   non-ignored footprint changes.
8. `test_post_exposure_guard_wraps_each_command_not_the_command_batch` proves a
   mutation between two individually successful commands cannot escape.
9. `test_config_emission_fails_closed_on_identity_or_footprint_mismatch`
   parameterizes wrong branch/HEAD/base, analytical manifest mismatch, tracked
   out-of-allowlist path, and untracked non-ignored path; no config is written.
10. `test_freeze_fails_closed_on_identity_or_footprint_mismatch` proves the
    config is byte-identical and no preholdout receipt is created.
11. `test_holdout_pre_receipt_guard_fails_before_receipt_and_rng` proves each
    mismatch creates neither receipt nor RNG object/payload.
12. `test_holdout_post_receipt_guard_failure_burns_namespace_before_rng` injects
    each mismatch between atomic receipt creation and RNG construction, proves
    the immutable receipt remains, RNG factory call count is zero, and the stop
    disposition is `STOP_INVALIDATED_POST_EXPOSURE`.
13. `test_holdout_success_freezes_complete_artifact_snapshot` proves the
    artifact-manifest file and every represented file are included in the exact
    path/hash aggregate used by all later command envelopes.
14. `test_holdout_and_artifact_generating_commands_are_never_retryable` proves
    the non-mutating retry rule cannot dispatch either command class.

Red evidence must show the missing behavior, not an import or fixture failure.
Green evidence must include focused tests plus the complete pre-holdout
validation ladder. Any formatter/fixer mutation returns to red-green work,
config re-emission, hash resealing, and fresh review before freeze.

## Application Order

1. Reproduce the current Log parent and append the exact supersession record.
2. Apply only the Goal, Plan, Runbook, spec, Log, implementation, and test
   changes required by this four-problem amendment; make no scientific change.
3. Run the amendment tests on temporary non-holdout fixtures and the full
   pre-holdout validation ladder. No holdout phase is permitted.
4. Compute the amended Goal/Plan/Runbook/spec hashes and append the v2 amendment
   record against the then-live Log parent.
5. Obtain fresh hash-specific scientific, executor-readiness, and
   provenance/freeze acceptance with no Critical or Important finding.
6. Rerun the full pre-holdout ladder. Only then may config emission and freeze
   proceed under the amended guards. Holdout remains separately gated.

## Barry-Level Decision

No Barry-level scientific or strategic decision is required to apply this
amendment. It preserves all science and closes deterministic provenance
execution gaps. Barry is required only under the existing contract if an
exposed namespace is scientifically invalidated and a fresh namespace is
requested, or if implementation reveals a material scientific assumption or
genuine strategic trade-off.
