# Goal 023 Task 2b Repair Rereview

Date: 2026-07-11  
Mode: independent read-only scientific/code rereview; this report is the only
workspace write  
Verdict: `SUPPORTED`

## Claim Audited

The claim is that the two Important implementation findings in
`.superpowers/sdd/task-2b-max-audit.md` are fully closed on the exact repaired
bytes: every deployable process-oracle, observation-oracle, and joint fit and
profile route is typed, factory-preflight-gated, and callback-free at its public
boundary; evaluator truth cannot reach joint objectives or profiles; all finite
canonical predator arrivals remain literal; and the repair leaves the frozen
Task 2b likelihood, audit, optimizer, recovery, and profile behavior unchanged.

For that claim to hold, fabricated preflight values must fail before data access
or optimization, raw callback engines must be private implementation details,
each public objective must be constructed internally from the exact typed data,
the joint path must remain analyst-only and batched, all 5,225 finite arrivals
including the 620 above 120 must survive every relevant source surface, and the
frozen nine-audit/profile evidence must remain valid.

## Audit Verdict

`SUPPORTED`. No Critical or Important finding remains in either repaired
implementation issue. The analyst/truth firewall is closed at all six
deployable fit/profile boundaries, and preserving post-horizon finite arrivals
causes no in-horizon numerical change.

This verdict closes only the two implementation findings. It does not resolve
the pre-existing tracked-contract amendment recorded before Task 3 and does not
authorize Task 3, scenarios, calibration, holdout work, staging, commit, or
push.

## Findings

### Critical

None detected.

### Important

None detected.

## Strongest Supporting Evidence

- Bound identity matched exactly: source
  `701dd468219737d8885a2f52ef9e4cbb8965397277f6b9d1a4f3ebbfe72bc673`,
  tests `cb18204c6c78e9a0a1f049198f563b131cd3ee8d84793d1dfa94a87d6f68b6aa`,
  and 2,305-line Log
  `7a95d0ce27fb7ffa9e9ec77308659a68b243f79f986b85ecdb518d7365ebd5b6`.
  The first 2,254 Log lines independently reproduced parent SHA-256
  `a59540d9bcbca47b8277499a596d16d8e3e7be2f592ce1ab848c0070f4d19094`.
- `NineAuditPreflightResult` rejects public construction, authorization requires
  same-process factory issuance, and every use revalidates the ordered nine
  schedule/target records, exact diagnostic row counts, rank/condition gates,
  16 indexed searches per audit, frozen recovery counts, zero collisions, and
  pass state (`src/spatext/synth/medium/latent_response_observation_recovery.py:439-545`).
- The six public adapters accept only exact typed process outcomes,
  fixed-state observation histories, or analyst histories plus the typed
  preflight. Their objectives are constructed internally; the joint fit and
  profile both build `AnalystBatch` and call `batched_joint_log_likelihood`
  (`src/spatext/synth/medium/latent_response_observation_recovery.py:2846-3120`).
- The only callback-taking optimizer/profile engines are
  `_run_optimizer_start`, `_run_multistart_optimization`, and
  `_profile_parameter`. No unprefixed raw counterpart exists, no public
  function accepts a `Callable`, and the package initializer exports none of
  them. There remains exactly one production `scipy.optimize.minimize` call and
  one `scipy.optimize.brentq` call with the frozen settings.
- Exact built-in and tuple-element type checks reject evaluator objects,
  truth-bearing callables, tuple subclasses, oracle data on the joint route,
  and unexpected objective keywords before optimization. An unissued
  `object.__new__` preflight fails before data iteration or any fit/profile
  primitive.
- Independent source reconstruction found all `5,225/5,225` arrivals finite,
  exactly `620` above `120`, maximum `205.910318172679`, exact retention in
  dense/structured/sparse audit designs, `5,225` finite permutation pairs, and
  exact preservation of the complete arrival multiset.
- Across all three schedules and all A/B/C targets, an independent comparison
  of preserved raw arrivals against the prior post-120-to-NaN recode produced
  maximum absolute differences of exactly `0.0` for both canonical audit
  vectors and scaled Jacobians. The driver formula therefore preserves the
  frozen in-horizon estimand while restoring literal provenance.

## Independent Checks

1. Read the repo contract, Goal/Plan/Runbook, authoritative spec, Task 2b brief
   and numerical preflight, max audit, repair brief/report, full current source
   and repair-relevant tests, and Log lines 2255-2305.
2. Verified the authoritative spec SHA-256
   `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`
   and unchanged accepted Task 1 source/test hashes.
3. Ran six focused repair tests covering blocked/fabricated preflights, public
   surface privacy, and both source-bound arrival regressions: `6 passed in
   0.62s`.
4. Ran 15 focused optimizer/profile tests covering the literal L-BFGS-B
   adapter, per-start failure propagation, six-of-eight and best-two rules,
   conditional profile maps, stepping, brackets, Brent settings, open sides,
   LLmax invalidation, and practical classification: `15 passed in 0.55s`.
5. Ran targeted Ruff format and lint checks: pass. Ran `uv run mypy src tests`:
   no issues in 59 source files. Ran `git diff --check`: pass.
6. Reviewed, but did not repeat, the bound final full run reported by the repair
   worker: `199 passed in 772.21s`, with dense `16/15/2`, structured
   `16/14/3`, sparse `15/16/16`, and zero collisions. The exact source/test
   hashes of that run are the bytes audited here.

## Required Corrections

None for the two repaired implementation findings.

## Residual Uncertainty And Boundary

The preflight is deliberately an in-process capability, not a security barrier
against arbitrary mutation or monkeypatching by code already executing inside
the module process. Normal public construction, copying, deserialization, or
unissued reconstruction cannot authorize estimation; controllers must execute
the canonical preflight in the same process.

The 144 inverse searches were not rerun in this rereview because the exact
199-test run on these bytes was already supplied and took 772.21 seconds. This
rereview independently rechecked the repaired provenance-sensitive numerical
maps, source values, public call graph, failure boundaries, and fast
optimizer/profile behavior. Platform-level optimizer invariance beyond the
locked macOS arm64 NumPy/SciPy environment remains unproved, as in the original
audit.

No Task 3 path, scenario replication, RNG payload, calibration, holdout,
artifact, receipt, staging, commit, or push was run or created.
