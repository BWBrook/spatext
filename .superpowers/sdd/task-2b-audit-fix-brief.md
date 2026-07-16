# Goal 023 Task 2b Max-Audit Fix Brief

Work in `/Users/bwbrook/.codex/worktrees/spatext/goal023`.

Read first:

- repo `AGENTS.md`;
- Goal 023 Goal/Plan/Runbook and authoritative spec;
- `.superpowers/sdd/task-2b-brief.md`;
- `.superpowers/sdd/task-2b-max-audit.md`;
- current Task 2b source and tests;
- Goal 023 `Log.md`.

Bound input state:

- source SHA-256 `d732977d6bb6ae966d4e8575e4ad242d0054d826414ba00846d2e1e0b827bfa3`;
- tests SHA-256 `3d92ab723aed2a14b27aaebb6080917999ed9a0bf7a2de60aed65e90222b2ef9`;
- Log `2254` lines, SHA-256
  `a59540d9bcbca47b8277499a596d16d8e3e7be2f592ce1ab848c0070f4d19094`;
- authoritative spec SHA-256
  `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`.

## Ownership

Own only:

- `src/spatext/synth/medium/latent_response_observation_recovery.py`;
- `tests/test_synth_medium_latent_response_observation_recovery.py`;
- one append-only child at the end of Goal 023 `Log.md`;
- ignored `.superpowers/sdd/task-2b-audit-fix-report.md`.

Do not edit authority documents yet. Do not revert accepted prior work. You are
not alone in the codebase.

## Required Repairs

Use strict TDD and close the two implementation findings from the max audit.

1. Close every deployable estimator/profile route behind a canonical typed
   `NineAuditPreflightResult` and the analyst/truth firewall.
   - Provide preflight-gated production fit/profile adapters for process oracle,
     observation oracle, and joint variants.
   - Construct joint objectives internally from `AnalystHistory`/`AnalystBatch`.
   - Keep process- and observation-oracle inputs in physically distinct typed
     entrypoints.
   - Make raw callback-based optimizer/profile primitives private implementation
     details, not deployable public fitting surfaces.
   - Reject fabricated/incomplete preflight records.
   - Add adversarial tests proving evaluator objects, truth-bearing closures or
     callables, oracle-at-risk data, and fabricated preflights cannot authorize
     deployable fitting or profiling.
   - Preserve the literal optimizer, start, likelihood, profile, failure, and
     nine-audit rules.

2. Preserve every finite canonical predator-arrival time, including all `620`
   finite values above `120` and the observed maximum near `205.910318`.
   - Do not recode finite post-horizon values to `None`, NaN, or infinity.
   - The within-horizon driver remains zero until arrival by the existing
     formula, so Task 2b audit vectors/counts must remain unchanged.
   - Add a source-bound regression proving the 620 values remain finite and a
     permutation/correlation-facing regression proving complete values survive.

3. Preserve Task 2b's numerical evidence: exact nine recovery counts, zero
   collisions, scalar/batched agreement, profiles, controls, and all accepted
   Task 2a behavior.

## Boundaries

No Task 3 scenario suite, authority amendment, artifact, CLI, calibration,
receipt, holdout payload, staging, commit, or push. Do not tune any contract
value. If a repair requires changing a frozen estimand, support, schedule,
threshold, or numerical result, stop and report `BLOCKED`.

## Validation And Ledger

Record behavior-specific RED evidence before source changes. Run focused tests,
observation regressions, targeted Ruff, `mypy src tests`, and `git diff --check`.
The full 194+ test file includes a roughly 12-minute canonical audit; run it once
on final bytes. Append one Log child against the exact live 2254-line parent,
with RED/GREEN evidence, exact hashes, audit counts/runtime, and independent
re-review status `PENDING`. Never insert or rewrite prior Log bytes.

Write the full report to `.superpowers/sdd/task-2b-audit-fix-report.md` and
return only status, changed paths, test/audit summary, final hashes, and concerns.
