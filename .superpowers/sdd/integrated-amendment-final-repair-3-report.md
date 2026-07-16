# Goal 023 Integrated Amendment Final Repair 3 Report

Date: `2026-07-12`
Profile: `sol_high_specialist`
Verdict: complete RED-GREEN repair of C1, I1-I5, M1, and the 15-step
correction sequence; all independent reviews and acceptance remain `PENDING`

Task 3, production RNG/vector construction, simulation, runtime benchmark,
calibration, canonical config/artifact/receipt production, freeze, holdout,
staging, commit, push, and publication remain `BLOCKED`.

## Exact Changed Files

Tracked write-scope files changed:

- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`
- `spec/synth_medium_latent_response_observation_recovery_gate.md`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`

Ignored evidence written:

- `.superpowers/sdd/integrated-amendment-final-repair-3-red-evidence.md`
- `.superpowers/sdd/integrated-amendment-final-repair-3-green-evidence.md`
- `.superpowers/sdd/integrated-amendment-final-repair-3-report.md`

`Plan.md`, `source_digest_receipt.json`, `pyproject.toml`, `uv.lock`,
`src/spatext/observe.py`, `tests/test_observe.py`, dependencies, lock state,
and every other tracked file were not edited by this repair. Existing user and
orchestrator changes were preserved.

## RED Evidence

Fourteen strengthened existing nodes from the exact 98-name manifest were run
before source/authority repair. Result: `14 failed in 1.08s`, exit `1`.

The failures were behavior-specific:

- out-of-support successful fit estimates were accepted;
- the required canonical zero-driver recovery interface did not exist;
- the required available/nonfinite predictive state was rejected;
- live spec/source reconstruction and exact source-receipt-file binding did
  not exist;
- false spec/source tuples passed freeze and pre-create validation;
- false spec/source config/preholdout/holdout tuples returned
  `CONTINUE_FROZEN_CANDIDATE` and called the list-append pre-RNG spy;
- post-create failures lacked explicit immutable stop dispositions;
- parsed complete-envelope Log payload, current-envelope retry, captured
  `git write-tree`, staged-tree publication identity, and module-issued fixture
  roots did not exist.

A direct current-API probe supplied 12 complete development arrival pairs plus
12 complete holdout pairs and was accepted as all 24 holdout pairs. A separate
Runbook probe found narrative prose in executable bash block 13. RED evidence
SHA-256 is
`e569ba89fd20c19d26c6641bde91d7c84e86223943e61585f57c561ca3e71ce8`.

## Repair Dispositions

### C1: live authority

`capture_live_authority()` now hashes the exact live authoritative spec,
requires source-receipt file SHA-256
`5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`,
parses and reconciles the accepted landscape/arrival identities, and derives
`source_sha256=6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`.

Config emission, freeze, pre-receipt, post-create, post-receipt, and
immediate-pre-RNG checks bind config and both receipts to that fresh authority,
the literal tracked manifest, and captured analytical digest. False authority
fails before new-file creation or returns the immutable post-exposure stop;
the RNG spy remains at zero. Exclusive writes validate complete payloads and
cross-bindings first. Post-create verification raises a typed immutable stop
while retaining bytes; pre-existing bytes are never overwritten.

### I1 and I2: executable science evidence

The exact 98-node manifest remains literal, unique, complete, and executable.
Affected T3A/T3D/T3S/T3P tests now exercise all rereview-3 counterexamples.

Successful fit evidence enforces every frozen natural support, exact boundary
identity, strict ordered rates, and a strictly interior `lambda_equal` MLE.
The exact accepted boundary outcome is a failed row with
`failure_code=equal_rate_mle_noninterior`.

Control reconciliation now consumes 24 sorted canonical emitted
`replicate_recovery.csv` beta-driver rows, reconciles them one-to-one to fit
evidence, and returns `zero_decision` from those rows. It invokes the complete
arrival-pair validator on exactly 24 holdout pairs with common split/source
identity and fixed 4180/1045 frames. Mixed development/holdout evidence fails.

Predictive evidence represents successful+available nonfinite residuals with
null residual, true nonfinite flag, and mandatory warning. It validates sample
size, metric domains, SD/MCSE algebra, standardized residual algebra, PIT, all
27 ordered cells, and typed failed-fit null rows.

### I3: complete external schemas

Goal/spec now provide complete self-contained header, type, nullability,
primary-key, sort-key, row-rule, and enum authority for:

- `model_parameter_contract.csv`
- `replicate_recovery.csv`
- `coverage_calibration.csv`
- `latent_time_calibration.csv`
- `predictive_replicate_diagnostics.csv`
- `predictive_check_summary.csv`
- `identifiability_profiles.csv`

Config parameter rows are explicitly the model-parameter schema without the
two status fields. The private zero-driver interval substitute was removed;
decisions bind canonical recovery evidence.

### I4: observed provenance

Ordinary post-exposure Log suffixes are canonical JSON with parsed/recomputed
bindings for every envelope member; no caller boolean remains. Retry requires
a fresh current capture and the sole module-validated reviewed Log-only
transition, which binds the exact failed command, exit, retry count, parent,
and complete envelope. Any other intervening state rejects.

Complete staging capture records the literal worktree/index blob maps and real
`git write-tree` result. Validation returns a module-issued staged identity;
commit/merge/push transitions must use its tree and the same repo root while
retaining exact ref/parent semantics.

### I5 and M1: fixture and Runbook boundaries

Fixture bundle emission accepts only a module-issued, new temporary root.
Resolved canonical production path, aliases, descendants, raw paths, forged
tokens, moved roots, and existing paths fail before any write. The production
artifact path remains absent.

The sentence formerly inside Runbook bash block 13 is outside the fence. All
18 executable bash blocks pass `bash -n`.

## GREEN Evidence

- strengthened counterexample nodes: `14 passed in 0.77s`, exit `0`;
- exact executable 98-name manifest: `98 passed in 0.96s`, exit `0`;
- complete Goal 023 file: `297 passed in 710.36s (0:11:50)`, exit `0`;
- observation/upstream synth-medium set: `69 passed in 46.79s`, exit `0`;
- Ruff format check: `2 files already formatted`;
- Ruff check: `All checks passed!`;
- mypy: `Success: no issues found in 59 source files`;
- tracked `git diff --check`: pass;
- owned-untracked `git diff --no-index --check`: no whitespace diagnostics;
- exact manifest still contains 98 unique names and definitions.

An intermediate full-file run exposed one old assertion that prohibited every
`artifacts/` literal. It was correctly narrowed to permit exactly the inert
canonical path required for pre-write rejection while still prohibiting live
artifact/scenario/calibration/holdout functions. The final complete run above
is on the exact reported source/test hashes.

GREEN evidence SHA-256 is
`8992233634e517b0e47d7714172be24141147b6089c46716314b1ec722e4867d`.

## Authority And File Hashes

- Goal: `c20981e0062a03453f99f066cce460e0bcbb2717b803ee009b7e36eb2a9c6af6`
- Plan unchanged: `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84`
- Runbook: `ffae51c58789fd721032ce734c0ef0250bc2a2727bfbc99530ecd2f16dd20804`
- authoritative spec/live spec identity:
  `ccd3f601224f36782d44ee43e325214e8ba66928b8e97fc531fe41419341c7d2`
- source module: `f18ea913632b07de9f5108bdd23e5ef2a799d20b1a710c6ce5418776e1441e1a`
- tests: `37dee62067c03b8a5e4b47430c1b347f160d5c2580c966644abba66d4cdf2575`
- accepted source receipt unchanged:
  `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb`
- final rereview 3:
  `71fd0e0d242ba4488bc0e8a5fdb54f6290d9b6a77a012cc415fc6fe7f2c05e29`
- final Log:
  `0bbd23f592a57c875e9b12a109c06cedf5912f8eb8697e14ba156bc50966d030`

Goal and spec bodies from `## Objective` are byte-identical: `117226` bytes,
SHA-256
`416890f17cd4ac3ab785dad190b165b05b7a76ae8425e7ab1f51277feccb4282`.

Source/frame reconciliation reproduced 5225 unique Goal 017 passable IDs, the
deterministic 1306-cell sparse frame, and disjoint 4180 fit plus 1045 score
frames with union 5225.

## Log Parent And New Shape

Live parent immediately before append:

- lines: `2666`
- bytes: `132318`
- SHA-256: `f3bc360138e3ce33abf25b741150a7c59dc2daf5dabd9b8c9360a0b9d95df843`
- reproduced bindings: `15/15` parent hashes and `6/6` byte counts

New Log after the one child:

- lines: `2784`
- bytes: `138517`
- SHA-256: `0bbd23f592a57c875e9b12a109c06cedf5912f8eb8697e14ba156bc50966d030`
- record type: `integrated_amendment_final_rereview_3_authority_repair_v1`
- reproduced bindings: `16/16` parent hashes and `7/7` byte counts
- scientific/statistical/executor/artifact/code/provenance/max reviews:
  all `PENDING`
- acceptance: `PENDING`

No acceptance record was appended.

## Git And No Exposure

Branch remains `codex/spatext-goal023-latent-response-observation-gate`.
HEAD and `origin/main` both remain
`53462d0365babf2c8070714a930f69b4071af276`. Git index is empty. Existing
`pyproject.toml`/`uv.lock` modifications and untracked orchestrator files are
preserved. No stage, commit, push, reset, restore, cleanup, or deletion was
performed.

The canonical artifact directory, recovery config,
`preholdout_state_receipt.json`, `holdout_receipt.json`, and production Goal
023 CLI are absent. No Task 3 command, production RNG/vector, simulation,
runtime benchmark, calibration, canonical artifact/config/receipt, production
freeze, holdout, staging, commit, push, or publication occurred. Tests used
only deterministic test objects, list-append spies, fake Git runners, and
temporary-directory serializers/receipts.

Fresh independent max-tier rereview is required on this exact tuple. Until it
reports no Critical or Important finding, Task 3 and every stochastic or
irreversible phase remain blocked.
