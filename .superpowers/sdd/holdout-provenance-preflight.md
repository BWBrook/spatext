# Goal 023 Holdout And Provenance Preflight

Date: 2026-07-11

Mode: read-only contract audit. This preflight did not construct a holdout
payload, generate artifacts, run calibration, inspect future outputs, or edit a
tracked file.

## Conclusion

The intended Task 3 -> Task 4 -> Task 5 -> Task 6 progression is coherent only
if the tracked analytical state becomes byte-immutable before the one-shot
holdout, `Log.md` remains append-only and outside the analytical digest, and all
post-exposure activity is inspection or validation against frozen bytes.

The holdout must not be exposed yet. One Critical contract ambiguity requires a
binding interpretation before Task 5: the immutable receipt is created before
results exist but contains `invalidated` and `no_contract_change`, whose truth
can change during later review. Several Important execution ambiguities should
also be resolved before the freeze.

## Audited Authority And Current Provenance Anchor

Audited files:

- `AGENTS.md`
- Goal 023 `Goal.md`, `Plan.md`, `Runbook.md`, and `Log.md`
- `spec/synth_medium_latent_response_observation_recovery_gate.md`

Observed authority tuple:

```text
Goal     cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20
Plan     df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e
Runbook  78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed
spec     0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d
```

The reconciled append-only chain is internally reproducible from its new root:

- `1-1807` reproduces
  `0e07d664e3a1e2be58b7930cf3a23ffc123456bcbba9f7654cc8335fe15100ad`.
- The later parents at lines `1844`, `1889`, and `1937` reproduce the hashes
  declared by their child records.
- The current file has `1962` lines and SHA-256
  `b047ab616b7292661b311c3ad227543df3556ad2dbcd9c9117257a60f92f4aad`.
- Therefore, the next append must declare
  `parent_line_count: 1962` and
  `parent_sha256: b047ab616b7292661b311c3ad227543df3556ad2dbcd9c9117257a60f92f4aad`.

The earlier `994-1758` narrative remains quarantined and cannot be used as
current gate evidence. Current post-root records show Task 2a1 accepted and no
Task 2a2/2b, scenario, calibration, artifact, or holdout work yet begun.

## Non-Negotiable Invariants

1. Holdout bytes are never instantiated, read, previewed, summarized, or used
   for a decision before the freeze gates pass.
2. The frozen seed namespace is used exactly once. A receipt creation followed
   by a crash burns that namespace; it does not authorize retry.
3. After freeze, only the two excluded receipts and append-only `Log.md` may
   change in tracked state. `Log.md` entries may record evidence and hashes but
   may not change equations, thresholds, code, tests, schemas, or conclusions.
4. Every `Log.md` append declares and reproduces the exact full-file parent line
   count and SHA-256. No insertion, deletion, reordering, or backfill is allowed.
5. The analytical tracked-state digest is reproduced before holdout, after
   post-holdout checks, before final review, and before commit.
6. Generated artifacts are ignored and immutable after holdout. Inspection and
   verification must not regenerate scientific rows.
7. A post-exposure finding that requires any analytical tracked change ends the
   Goal 023 namespace. It is reported as invalid and cannot be repaired or rerun.

## Exact Task 3 -> Task 4 -> Task 5 -> Task 6 Sequence

### Task 3: Complete The Entire Pre-Holdout Surface

1. Finish red-green TDD for all eleven scenarios, schedules, stochastic
   consumption rules, seed-range rejection, fitting/profiling, gates,
   denominator/imputation rules, predictive diagnostics, schemas, manifests,
   visuals, and phase-separated CLI behavior.
2. Prove in tests that holdout rejects changed hashes, a pre-existing receipt,
   a wrong namespace, unknown scenarios, out-of-range indices, and missing
   provenance before RNG construction.
3. Implement artifact and documentation surfaces using development/calibration
   data only. Holdout task counts may be represented as inert integers for
   runtime projection; no holdout RNG payload or vector may be constructed.
4. Complete transportability language: scheduled-count only, point-process
   bridge required, no spread fit, no ABC/MCMC/posterior, no real data, no
   remote compute, and no production adoption.
5. Run focused and full checks, static checks, non-holdout CLI checks, schema
   checks, visual checks, and the complete validation ladder except holdout.
6. Obtain independent scientific, code, artifact, documentation, and provenance
   reviews. Resolve every Critical and Important finding while changes are
   still permitted.
7. Append the Task 3 evidence to `Log.md` using the exact parent line/hash
   protocol. Recompute the new full-file anchor after every append.
8. Enter Task 4 only when the tracked implementation and documentation are
   complete and no review finding remains open.

### Task 4: Calibrate, Review, Then Freeze

1. Confirm the holdout receipt and preholdout receipt do not yet exist and that
   no holdout artifacts, payloads, or vectors exist.
2. Run the eight-worker runtime benchmark using only the frozen development and
   calibration exceptions. Confirm `holdout_payload_instantiated == false` and
   `scientific_rows_emitted == false`.
3. Verify eleven complete scenario timing units, one equal-emission bootstrap
   timing unit, exact expanded calibration/holdout duration lists, 199 equal
   holdout bootstrap copies, eight deterministic LPT loads, safety factor
   `1.20`, and both projected makespans `<= 1500` seconds.
4. Run full calibration once with eight local workers. Stop if wall time exceeds
   `1800` seconds. Do not reduce evidence, alter thresholds, use remote compute,
   or expose holdout to rescue a failure.
5. Inspect the config, source provenance, schemas, calibration tables, and
   visuals. Confirm source/spec/config hashes and exact artifact manifest.
6. Obtain independent scientific, provenance, validation, and contrarian
   approval of calibration behavior and the exact candidate frozen bytes.
7. Append approved spec/config/source hashes and reviewer dispositions to
   `Log.md`, preserving the full-file parent chain.
8. Rerun the complete pre-holdout validation ladder. Any modification produced
   by a supposedly validating command must be treated as a finding, resolved,
   reviewed, and followed by a fresh validation cycle before freeze.
9. Compute the analytical tracked-file manifest and digest from the final bytes.
   The config must already contain that exact digest when its `config_sha256` is
   approved; the freeze phase may reproduce but must not patch the config.
10. Atomically create `preholdout_state_receipt.json`, then verify its spec,
    config, source, tracked-state digest, sorted per-file manifest, and own file
    hash. Reproduce the same digest from disk and from the frozen config.
11. Append a provenance-only `Log.md` record for the preholdout receipt and final
    freeze anchor if such an append is authorized by the clarified write scope.
    This append is outside the analytical digest but still obeys the chain.
12. From this point, no analytical tracked file, test, spec, CLI, threshold, or
    documentation file may change.

### Task 5: Expose Once, Then Read Only

1. Run every pre-holdout check listed below immediately before invocation.
2. The holdout command must use exclusive atomic receipt creation. It must fail
   before RNG construction if `holdout_receipt.json` already exists.
3. The receipt must bind the exact spec, config, source, tracked-state digest,
   and seed namespace before any holdout result is emitted or made readable.
4. Execute the frozen holdout exactly once. Never delete the bundle or receipt,
   and never retry under the same namespace, including after partial failure.
5. Emit only ignored holdout artifacts plus the machine-created tracked receipt.
   Do not alter source, tests, specs, thresholds, docs, or the frozen config.
6. Inspect the exact file set, report, verification, control decision, parameter
   contract, CSV schemas/order, JSON finiteness, zero-byte/stale extras, SVG
   clipping, and report links without regeneration.
7. Run the post-holdout checks listed below. Reproduce all hashes before and
   after every potentially mutating tool.
8. Obtain independent read-only scientific, contrarian, provenance, code, and
   artifact reviews against the same immutable bytes.
9. If a finding requires an analytical tracked change, stop. Preserve both
   receipts and all exposed artifacts, report scientific invalidation upward,
   and request Barry's approval for a fresh namespace. Do not amend or rerun.
10. Record review evidence only through the pre-agreed provenance mechanism;
    do not improvise a tracked post-holdout file outside the exclusions.

### Task 6: Stage And Publish Without Reopening Science

1. Interpret Task 6's "full validation ladder" as the Runbook section 7
   post-holdout read-only ladder, not section 4. Do not delete artifacts, rerun
   runtime benchmarking/calibration, or regenerate holdout output.
2. Verify receipt, spec/config/source/tracked hashes, artifact manifest, and
   review evidence. Reproduce the analytical digest again.
3. Stage only the exact Runbook allowlist. Reject every extra staged path,
   unstaged tracked path, and non-ignored untracked path. Confirm `artifacts/`
   and `dist/` remain ignored.
4. Run `verify-staged-state`; require exact branch/base anchors, allowed cached
   paths, no residual non-ignored work, and equality with the preholdout digest.
5. Have a fresh final reviewer inspect the exact cached diff, immutable
   artifacts, receipts, validation evidence, and live status.
6. Do not append an unreviewed final-review record after that review. Either
   keep the acceptance as external immutable evidence, or have the reviewer
   approve the exact proposed append bytes and then verify that only those
   bytes were appended. Otherwise the final review creates an infinite
   review-then-append loop.
7. Repeat branch/base, staged-diff, receipt, tracked-state, and artifact guards
   immediately before commit.
8. Commit only after no Critical or Important finding remains. Fast-forward the
   clean canonical `main`, push, and prove local/remote equality. Stop on any
   failed guard; do not force, reset, rebase, stash, or clean.
9. Do not start Goal 024.

## Exact Pre-Holdout Checks

These checks must all pass in one uninterrupted final pre-exposure gate:

- Branch is `codex/spatext-goal023-latent-response-observation-gate`.
- `HEAD` and `origin/main` are the frozen base
  `53462d0365babf2c8070714a930f69b4071af276`, unless an explicitly amended and
  independently reviewed contract replaces both anchors before freeze.
- Authority hashes equal the accepted Goal/Plan/Runbook/spec tuple.
- Source receipt is present, immutable, independently reproduced, and passed.
- No open Critical or Important Task 3 or calibration review finding exists.
- Full check-only validation passes on the final tracked bytes.
- Runtime benchmark contains no holdout payload/scientific row and both
  projections are `<= 1500` seconds.
- Calibration wall time is `<= 1800` seconds and calibration passed without
  accessing the holdout namespace.
- Frozen config hash is canonical with `config_sha256` omitted from its own
  hash payload; spec/source hashes match authority.
- Config contains the already-computed final `tracked_state_sha256`; freeze does
  not modify config bytes after config approval.
- `preholdout_state_receipt.json` contains the exact sorted path/hash manifest
  and matching spec/config/source/tracked hashes.
- The tracked-state digest independently reproduces from final files using
  `<file_sha256><two spaces><relative_path>\n`, lexical path order, and only the
  contractually excluded `Log.md`, preholdout receipt, and holdout receipt.
- The exact manifest membership has been agreed and tested; no path can be
  silently omitted or added.
- Latest `Log.md` entry reproduces its parent line count/hash; current chain has
  no insertion, deletion, reordering, or backfill.
- `holdout_receipt.json` is absent.
- No holdout row, payload, seed object, RNG vector, result, or stale holdout
  artifact exists.
- Holdout phase fails before RNG construction for receipt existence, hash
  mismatch, wrong namespace, extra scenario, bad index, or missing provenance.
- Artifact directory contains only the reviewed calibration surface expected by
  the frozen phase sequence; exact manifest and stale-extra policy pass.
- No unstaged analytical change or non-ignored untracked source path exists.
- Eight local workers are used; no remote compute path is active.
- A failed atomic receipt creation or any post-creation process failure is
  explicitly understood to burn the namespace.

## Exact Post-Holdout Checks

Perform inspection first, then check-only validation, without regeneration:

- `holdout_receipt.json` exists exactly once and its self-hash reproduces with
  `receipt_sha256` omitted.
- Receipt spec/config/source/tracked hashes and seed namespace match the frozen
  config and preholdout receipt.
- The receipt was created before any holdout output; no second execution was
  attempted.
- The analytical tracked-state digest equals the preholdout value immediately
  after execution, after all read-only checks, before final review, and before
  commit.
- `Log.md` changes, if authorized, are append-only and each child reproduces
  its full parent; no append contains analytical contract changes.
- Exact emitted artifact set equals the frozen manifest; there are no missing,
  extra, stale, or zero-byte files.
- All CSV headers, types, primary keys, ordering, nullability, and denominators
  match the spec; no failed replicate is silently dropped.
- JSON has sorted keys, exact declared top-level fields, finite numeric values,
  and matching hashes/boundary labels.
- All six SVGs are present, self-decoding, unclipped, and referenced by the
  report.
- Verification has the exact gate-family checks plus `artifact_manifest` and
  `tracked_state`; recommendation precedence is unchanged.
- Source, schema, analytic, process-oracle, observation-oracle, holdout-lock,
  artifact, and silent-misspecification failures map to
  `model_contract_failed` before lower-precedence outcomes.
- Post-holdout Ruff format-check, Ruff check, mypy, pytest, build, and verify
  complete successfully. Any command that changes tracked bytes is an
  invalidating event, not an automatic repair.
- Independent scientific, contrarian, provenance, code, and artifact reviewers
  inspect the same immutable artifact and tracked-state hashes.
- Staging is the exact allowlist; generated artifacts/build outputs remain
  ignored; no unstaged tracked or non-ignored untracked path remains.
- Final staged-state verification and final reviewer acceptance refer to the
  exact commit candidate bytes.
- Immediately pre-commit branch/base and all digest guards reproduce; after
  publication canonical `main`, local commit, and `origin/main` are equal.

## Contract Risks

### Critical 1: Immutable Receipt Contains Future-Dependent State

The holdout receipt must be created atomically before results are emitted and
must never be modified. Its required fields nevertheless include `invalidated`
and `no_contract_change`. Later read-only review can discover a defect requiring
an analytical change, at which point the Plan says the holdout is invalid, but
also says not to modify the receipt. Therefore the fields cannot simultaneously
be immutable terminal truth and accurately represent later invalidation.

Required binding interpretation before exposure: define both fields explicitly
as exposure-time assertions, with later invalidation recorded in a separate
append-only/external disposition; or change the pre-exposure receipt schema and
independently reseal the contract before any holdout payload exists. This cannot
be resolved after Task 5 starts.

### Important 1: Tracked Manifest Membership Is Not Literal

The spec says to hash every "allowed tracked path" and elsewhere every
"analytical tracked file", but it never gives one literal manifest list. The
Runbook staging allowlist is the strongest candidate, while the repository has
many other tracked files and imported source dependencies. Independent digest
reproduction requires a single normative membership rule. Bind it before Task
4 freeze and test exact inclusion/exclusion, rather than inferring it during the
one-shot command.

### Important 2: Config/Digest Ordering Can Mutate A Reviewed Config

Task 4 reviews and records the frozen config hash before the later numbered step
that says to compute the tracked-state digest, while the config must contain
that digest. The only non-invalidating interpretation is that config emission
already computes the final digest and the freeze step merely reproduces it and
writes the excluded preholdout receipt. Any freeze-time insertion into config
changes `config_sha256` after approval and must stop the holdout.

### Important 3: Post-Holdout Review Evidence Has No Clear Tracked Write Scope

Task 5's write scope permits ignored artifacts and `holdout_receipt.json` only,
yet requires five independent reviews and an immutable review record. The spec
excludes append-only `Log.md` from the analytical digest, suggesting that
provenance-only appends are intended, but Task 5 does not authorize them.
Pre-agree whether review evidence is appended to `Log.md` or retained as an
external immutable record, and define its hash linkage before holdout.

### Important 4: The Post-Holdout "Read-Only" Ladder Includes Mutating Hooks

`pre-commit run --all-files` invokes `trailing-whitespace`,
`end-of-file-fixer`, `ruff-format`, and `ruff --fix`; these hooks can edit
tracked files. Running them after holdout conflicts with the literal read-only
rule. They should be proven no-op before freeze and guarded by immediate
before/after tracked-state hashes. Any mutation after exposure invalidates the
holdout; it must not be silently accepted as validation.

### Important 5: Task 6's "Full Validation Ladder" Is Ambiguous

The pre-holdout ladder deletes the artifact bundle and reruns runtime benchmark
and calibration, while the post-holdout contract forbids deleting the bundle or
regenerating data. Task 6 must bind "full validation" to Runbook section 7 plus
staged-state guards, not rerun Runbook section 4.

### Important 6: Final Review Versus Final Log Append Can Recurse

If final-review acceptance is appended to tracked `Log.md` after the reviewer
approves `git diff --cached`, the reviewed bytes have changed. Re-reviewing and
then appending the next acceptance repeats indefinitely. Resolve this by using
external immutable final-review evidence or by having the reviewer approve the
exact proposed append bytes and verifying that exact append before commit.

## Stop Decision

Status: `HOLDOUT_BLOCKED_PENDING_CONTRACT_CLARIFICATION`.

Task 3 and Task 4 work may continue only within their non-holdout boundaries.
Task 5 must not begin until Critical 1 has a binding, independently reviewed
resolution and the Important freeze/provenance interpretations are made
literal. No holdout payload should be used to choose among those resolutions.
