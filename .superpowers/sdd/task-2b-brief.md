# Goal 023 Task 2b Brief

## Context And Authority

Complete Plan Task 2b in the isolated worktree
`/Users/bwbrook/.codex/worktrees/spatext/goal023`.

Read first:

1. `AGENTS.md`
2. Goal 023 `Goal.md`, `Plan.md`, and `Runbook.md`
3. `spec/synth_medium_latent_response_observation_recovery_gate.md`
4. current `src/spatext/synth/medium/latent_response_observation_recovery.py`
5. current `tests/test_synth_medium_latent_response_observation_recovery.py`
6. ignored numerical preflight `.superpowers/sdd/task-2b-preflight.md`

The authoritative spec SHA-256 is
`0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`.
Do not modify any Goal/Plan/Runbook/spec authority file.

Accepted Task 2a state:

- source `b61a3f7186a20748dc853f9f7fce8e3a04d008594ad2b64ce0139cebe1980486`
- tests `921775bf7c9516d7df0749e6e61a1c315c0b1aa7e80a9c05a364f26dc31bc286`
- Log parent `2222` lines,
  `a531eb33d0afb1ffdb91efcf0cddc37bd0b8327269b074bb175b566a85039203`

The Log parent includes a binding holdout-provenance interpretation. Preserve
it byte-for-byte. Independent review of that prefix may run concurrently, but
no other writer will edit the shared source/test/Log while you work.

## Ownership

You own only:

- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- one append-only child at the end of Goal 023 `Log.md`
- ignored report `.superpowers/sdd/task-2b-report.md`

You are not alone in the codebase. Do not revert or rewrite existing work;
extend the accepted Task 2a interfaces and preserve every existing test.

## Required Outcome

Use strict red-green-refactor TDD, with separate recorded RED cycles for the
major behavior groups. Implement all and only Plan Task 2b:

1. Exact ordered natural-rate forward/inverse and conditional profile maps,
   strict `1e-9` gap, projection/dedup thresholds, and invalid-input handling.
2. Exact positive-index 8-row and 16-row Halton starts, oracle subsets, literal
   values, and no data/truth/RNG dependency.
3. A vectorized/batched analyst likelihood and posterior path kernel that is
   independently tested against the accepted scalar enumeration and forward
   recursion. Keep scalar and batch implementations genuinely separate.
4. One literal L-BFGS-B adapter/options/result validator used for global,
   inverse-audit, and profile nuisance fits; deterministic start sorting,
   6-of-8 convergence and best-two agreement; per-start injected failures.
5. Stable canonical audit vector `log1p(mu)` block followed by `log(p0)` block,
   scaled central-difference Jacobian, generalized SVD, all nine frozen A/B/C
   dense/structured/sparse inverse audits with exact recovery counts and zero
   collisions, and the three literal rank-failing fixtures. The complete
   nine-audit preflight must structurally precede estimation.
6. Frozen natural-space adaptive profile procedure: conditional maps,
   projection, deterministic start ordering/dedup, unique stepping, open sides,
   sign-changing brackets, literal Brent settings, LLmax invalidation, and
   practical-identifiability classification.
7. Typed immutable result records and explicit failure propagation. Preserve
   the analyst/truth firewall: generating truth and oracle at-risk rows must not
   reach joint starts, bounds, objectives, batch kernels, profiles, sorting,
   practical gates, or acceptance logic.

Treat `.superpowers/sdd/task-2b-preflight.md` as the implementation/review
checklist, but the authoritative spec controls every exact value. Do not change
supports, estimands, schedules, thresholds, optimizer settings, or gate logic.

## Performance Requirement

The scalar likelihood remains the correctness oracle but is not the fitting
kernel. Build an equivalence-tested vectorized/batched implementation suitable
for the frozen optimizer/audit/profile workload. Do not duplicate schedule,
SVD, or design logic already accepted in Task 2a.

## Hard Boundaries

Do not implement or run scenario replication, calibration, holdout, predictive
ensembles, artifacts, CLI, documentation export, receipts, staging, commit, or
push. Do not construct any holdout payload. Task 2b tests may use deterministic
count-free audits and temporary analyst histories only.

If the nine exact recovery counts, zero-collision result, a literal optimizer/
profile rule, or accepted Task 2a behavior cannot be reproduced without
changing the contract, stop and report `BLOCKED`; do not tune or repair the
contract.

## Ledger

Immediately before appending, verify the first 2222 lines remain byte-identical
to the parent hash above. Append one child at EOF only, naming the live parent
line count/hash, each RED/GREEN cycle, exact audit results, validation, hashes,
independent-review status `PENDING`, self-review, and boundary confirmation.
Never insert, reorder, or backfill.

## Minimum Validation

- focused latent-recovery tests without coverage
- observation-kernel regressions without coverage
- relevant upstream synth-medium regressions
- targeted Ruff format/lint
- `uv run mypy src tests`
- `git diff --check`
- exact source/test/Log/report hashes and final Log line count

Write the full report to `.superpowers/sdd/task-2b-report.md`. Return only
status, changed paths, hashes, one-line test/audit summary, runtime, and concerns.
