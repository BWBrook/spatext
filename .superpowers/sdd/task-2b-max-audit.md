# Goal 023 Task 2b Independent Final Audit

Date: 2026-07-11  
Mode: read-only scientific/code audit; this report is the only workspace write  
Bound candidate: spec `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`; source `d732977d6bb6ae966d4e8575e4ad242d0054d826414ba00846d2e1e0b827bfa3`; tests `3d92ab723aed2a14b27aaebb6080917999ed9a0bf7a2de60aed65e90222b2ef9`; 2254-line Log `a59540d9bcbca47b8277499a596d16d8e3e7be2f592ce1ab848c0070f4d19094`.

## Claim audited

Operationally, the claim is that these exact bytes (1) implement every frozen Task 2b numerical rule without changing the estimands, supports, schedules, tolerances, or likelihood; (2) reproduce the canonical nine-audit noncollision frontier before estimation; (3) expose only deterministic, failure-explicit, analyst-safe fitting/profile paths; and therefore (4) may be accepted and handed to Task 3 with no Critical or Important defect.

For that claim to hold, the exact numerical maps and inequalities must be correct; the scalar and batched likelihoods must represent the same 21-path model by independent code paths; the optimizer/profile engines must use the literal calls and fail closed; all canonical source covariates must retain their frozen meaning; and no production fit/profile route may bypass the nine-audit gate or carry evaluator truth.

## Audit verdict: CONDITIONALLY_SUPPORTED — TASK 2b NOT ACCEPTED

The numerical core is strongly supported: all requested exact mechanics and the complete nine-audit result reproduced. The full handoff claim is not yet supported because three Important issues remain. There are no Critical findings. Under the explicit acceptance rule, Task 2b cannot be accepted or handed to Task 3 until the Important findings are closed and independently rechecked.

## Findings ranked by scientific consequence

### Critical

None detected.

### Important 1 — The analyst/truth firewall and preflight gate are not closed across all estimator/profile surfaces

The safe high-level joint fit does consume a `NineAuditPreflightResult` and constructs its likelihood internally from `AnalystHistory`/`AnalystBatch` (`src/spatext/synth/medium/latent_response_observation_recovery.py:2744-2817`). However, the public `run_multistart_optimization` accepts an arbitrary objective and no preflight (same file, lines 2205-2222), while `profile_parameter` accepts and invokes an opaque callback (lines 2029-2067 and 3753-3760). A direct probe made the ungated multistart path converge 8/8 and showed a profile callback reading external evaluator-like state on every one of 13,104 objective calls. There are no corresponding preflight-gated process-oracle or observation-oracle production fit entrypoints.

The tests prove the high-level joint-fit signature is truth-free, but profile tests use a hand-constructed “authorized” preflight whose diagnostic has only 10 rows (`tests/test_synth_medium_latent_response_observation_recovery.py:2952-3007`), rather than binding profile execution to the actual canonical preflight. Thus the tests do not establish the brief's stronger requirement that generating truth and oracle-at-risk data cannot reach objectives or profiles. No actual truth leak was observed—Task 3 does not yet exist—but the structural guarantee claimed for handoff is absent.

Required correction: before any Task 3 fit/profile use, provide one preflight-gated production fit/profile adapter for process, observation, and joint variants; construct joint objectives internally from analyst-only batches; keep oracle inputs in distinct typed entrypoints; make raw callback-based optimizer/profile primitives private; and add adversarial tests proving evaluator objects, truth-bearing closures/callables, and fabricated preflight records cannot authorize deployable fitting or profiling.

### Important 2 — Canonical finite arrival times beyond 120 are rejected and silently recoded

The frozen source contains 5225 passable-cell `TP(x)` values, including 620 finite values above 120 (maximum 205.910318). The specification defines `A_x = TP(x)` and assigns zero driver only by the formula within the 0–120 horizon (and explicitly for nonfinite arrivals); it does not authorize replacing finite post-horizon values with missing values. The implementation rejects every finite arrival above 120 (`src/spatext/synth/medium/latent_response_observation_recovery.py:4223-4236`), and the canonical audit fixture explicitly converts such values to `None` (`tests/test_synth_medium_latent_response_observation_recovery.py:2520-2529`).

This does not change the Task 2b audit numerics: an independent comparison preserving the raw finite values produced exactly zero difference in all tested audit vectors and Jacobians because `G_xt = 0` through time 120. It nevertheless breaks literal source provenance and can change Task 3's required finite-pair arrival-correlation audit and complete-value permutation semantics. It also prevents direct construction of analyst/design records from the frozen source without an undocumented transformation.

Required correction: preserve every finite canonical `TP(x)` value (including values above 120), let the driver formula yield zero inside the horizon, add a source-bound regression asserting the actual 620 post-horizon finite values remain finite, and rerun the Task 2a/2b checks and nine-audit hash binding. The alternative is an explicit reviewed authority amendment authorising the recode; an implicit test-fixture transformation is insufficient.

### Important 3 — The current ledger explicitly blocks Task 3 pending a tracked contract amendment

The bound Log status is `IMPLEMENTED_GREEN_PENDING_INDEPENDENT_REVIEW_AND_CONTRACT_AMENDMENT` and states that the rejected Log-only provenance interpretation “must be replaced by the prepared tracked contract amendment before Task 3” (`Log.md:2224-2254`). The ignored amendment proposal is not current authority. Therefore the literal “safe to hand off to Task 3” part of the claim is false even if the numerical implementation is accepted after repair.

Required correction: after resolving the findings above, apply the coordinated tracked pre-Task-3 amendment, append the parent-bound supersession/amendment records, reseal Goal/Plan/Runbook/spec and source/test hashes, and obtain all required hash-specific reviews with no Critical or Important finding before the first Task 3 RED test.

### Minor

None requiring correction beyond the residual uncertainties below.

## Strongest supporting evidence and independent checks

- Provenance: branch `codex/spatext-goal023-latent-response-observation-gate`, HEAD `53462d0365babf2c8070714a930f69b4071af276`; all four bound hashes matched. The first 2222 Log lines reproduced parent SHA `a531eb33d0afb1ffdb91efcf0cddc37bd0b8327269b074bb175b566a85039203`.
- Transforms/starts: independently coded radical inverses reproduced all 16 Halton rows bit-for-bit (maximum error 0). Ordered-rate forward/inverse corners, interior, kink, conditional maps, projection, deduplication, `1e-9`, `1e-12`, and `1e-10` boundaries agreed with the frozen formulas.
- Likelihood/posterior: an independently coded irregular/no-observation 21-path enumeration agreed with the batched cell likelihood to `8.88e-16`, the forward recursion to `1.39e-17`, and batched posterior weights to `8.33e-17`. Static and monkeypatch checks confirmed the batched path does not call scalar likelihood/posterior helpers.
- Audit vector/Jacobian: an independent stable implementation reproduced every canonical vector and scaled central-difference Jacobian exactly. All nine SVDs had rank 5; conditions were 66.72–1090.43, far below `1e8`.
- Full canonical inverse preflight: rerun directly on the bound source under Python 3.14.4, NumPy 2.4.4, SciPy 1.18.0; 773.52 s. All 144 searches succeeded. Recovery counts were exactly dense `16/15/2`, structured `16/14/3`, sparse `15/16/16`; all nine collision counts were zero and the preflight authorized estimation.
- Negative controls: equal-emission, deficient-design, and absent-state-support fixtures had ranks 2, 3, and 1; all had infinite condition, attempted no inverse search, and passed only by failing rank 5. The equal-emission process derivative was exactly zero.
- Optimizer/profile/failure rules: source contains one `minimize` call and one `brentq` call with the literal settings. Injected exception/nonfinite starts did not stop later starts; six successes were ranked deterministically and passed the inclusive best-two rule. A quadratic profile recovered endpoints 1.0173847 and 1.4826153, used `xtol=6e-5`, `maxiter=100`, and obeyed the strict LLmax and 1%-interior boundaries.
- Boundary/firewall state: no Goal 023 artifact directory, CLI, preholdout receipt, holdout receipt, calibration, scenario execution, RNG payload, staging, commit, or push was created or run. A static call-graph trace from the high-level joint fit found no truth, simulation, RNG, seed, or scenario function in its executable path.
- Bound checkpoint evidence (not rerun wholesale here): 194 focused tests passed in 737.23 s, targeted Ruff format/lint passed, mypy reported no issues in 59 source files, and `git diff --check` passed.

## Residual uncertainty after correction

Even after the three issues are closed, the inverse-search reproduction is not a second optimizer implementation: it independently verifies formulas, Jacobians, ranks, thresholds, and classifications but executes the production SciPy L-BFGS-B adapter. Exact recovery counts are therefore confirmed for the locked macOS arm64 environment, not proven invariant across future NumPy/SciPy/platform changes. No scenario, calibration, predictive, or holdout inference was assessed, by design. Finally, clean adversarial tests can reduce but cannot prove the absence of all future controller-level truth leakage; Task 3 must preserve the typed separation and fail-closed fit adapter.
