# Goal 023 Integrated Amendment Final Rereview 6

Date: 2026-07-12  
Role: independent `sol_max_auditor` scientific reproducibility and software-quality review  
Decision surface: exact pre-simulation contract only

## Verdict

**NOT SUPPORTED**  
**TASK 3 NOT AUTHORIZED**

The exact contract cannot yet authorize Task 3 fixture-only implementation.
There are no Critical findings, but there are four Important findings. The
complete science-bundle validator accepts two deterministic scientific
counterexamples, and it fabricates or omits the design-gate evidence needed to
exclude a third. The exact 98-node suite remains green because its integrated
fixture reaches only recommendation rank 1 and does not exercise these
acceptance paths.

No Task 3 production execution, stochastic vector, simulation, benchmark,
calibration, canonical artifact/config/receipt emission, freeze, holdout,
staging, commit, or push was run.

## Claim Audited

The claim under review was:

> This exact Goal/Plan/Runbook/spec/source/tests/Log/receipt tuple is complete,
> internally bound, scientifically decision-complete, deterministically
> testable, and safe enough to authorize only Task 3 fixture implementation,
> while retaining every source, phase, provenance, publication, terminal,
> fixture, and no-exposure boundary.

The tuple reproduced exactly:

| Surface | SHA-256 |
| --- | --- |
| Goal | `fcc948d50f95b55ea9cc545bd56c56a3190a03f28a00130b998a67c9966d492f` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb` |
| spec | `d034320882b2fd69076ec9539704369c35bae107c83f531b7c2bf649a8e2e112` |
| source | `8ad0c1ea96ea73686a677cc496c3ed1a63584a6787a238b09e0d4d5d1b45a231` |
| tests | `7013ccdece7d0ddc15354b8530d636e6b2a71e227d50d58dbb17e5eff528a04e` |
| Log | `d88afdf3c0bc7bad4e02023cba4c94e0458269e3daf3d85c314ac4997669c999` |
| source receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |

The Log is exactly 3,024 lines and 151,572 bytes. Goal and spec are byte
identical from `## Objective` onward.

## Findings

| ID | Severity | Finding |
| --- | --- | --- |
| I1 | Important | The complete reconciler can pass the zero-driver control while its standard predictive gate fails under finite Stouffer evidence. |
| I2 | Important | The reconciler treats forced nonfinite warnings as scientific warnings and can therefore pass a stress scenario on invalid warning evidence. |
| I3 | Important | Applicable potential/oracle/plug-in design gates are not persisted or reconstructed; the reconciler fabricates them, and a failed plug-in fit can remain `converged=True`. |
| I4 | Important | The exact 98-node suite does not exercise an integrated rank-4 science bundle or the three decisive negative paths above, so `98 passed` is not authorization evidence. |

### I1. Zero-driver prediction rejection is discarded

The authority is unambiguous:

- predictive completeness requires finite complete evidence, and a scientific
  warning is finite-rule evidence (Goal:802-806);
- any required predictive failure makes the zero-driver scenario unavailable
  (Goal:911);
- zero-driver passes only when all 24 intervals are decidable, exclusions are
  `0..6`, **and standard prediction passes** (Goal:913).

The implementation omits that gate:

- `SCENARIO_EVIDENCE_FIELDS["zero_driver_effect_negative_control"]` has no
  `predictive_pass` field (source:6172-6180);
- `reduce_scenario` checks only generic availability, 24 intervals, and the
  exclusion count (source:9041-9047);
- the complete-bundle reconciler computes `prediction_pass` but does not place
  it in zero-driver evidence (source:9540-9543, 9613-9621).

Independent deterministic counterexample:

1. Start from the exact complete science identity fixture.
2. Keep all 24 zero-driver fits and profile intervals successful, finite, and
   decidable, with zero exclusions.
3. Set every holdout predictive standardized residual to finite `1.0`.
4. Recompute all 27 summaries exactly. Every cell has
   `stouffer_z = 24 / sqrt(24) = 4.898979485566357`, `warning=true`, and
   `gate_result=fail`.
5. Recompute all 18 control rows and submit the result to
   `validate_science_bundle`.

Observed result:

```text
ZERO_COUNTEREXAMPLE_ACCEPTED pass pass 4.898979485566357 fail 1
```

The full bundle and reconstructed controls were accepted. The final fixture
rank remains 1 because other fixture scenarios intentionally fail; that does
not alter the false local `pass`.

Required correction:

1. Add `predictive_pass` to the literal zero-driver evidence schema.
2. Populate it from the exact holdout summary frame and require it to be true
   before the exclusion decision.
3. Ensure zero-driver plug-in evidence is real as required by I3.
4. Strengthen an assigned exact-manifest node with full-bundle finite
   Stouffer and Holm counterexamples. Test the open boundaries explicitly:
   `abs(stouffer_z) == 3` and adjusted `p == 0.01` do not warn; the next value
   beyond either boundary fails the zero-driver gate.

### I2. Forced warnings are relabelled scientific

The authority distinguishes two warning classes:

- a scientific warning exists only with complete finite evidence and a finite
  preregistered rule (Goal:802-805);
- a forced warning caused by unavailable evidence cannot satisfy a stress
  warning requirement (Goal:805-806);
- nonfinite residuals are warning-producing typed failures, while finite Holm
  and Stouffer thresholds are the scientific rules (Goal:1556-1562).

The summary validator itself correctly detects nonfinite evidence
(source:8802-8844). The complete reconciler then loses that provenance:

- `predictive_states` calls a scenario available when diagnostic counts equal
  replicate counts and failed-fit counts are zero; it does not inspect
  `standardized_residual_nonfinite` (source:9515-9527);
- it collapses every warning to `any(summary.warning)`;
- it hardcodes `warning_forced=False` for arrival (source:9622-9633) and all
  remaining stress scenarios (source:9643-9665).

Independent deterministic counterexample:

1. Start from the exact complete science identity fixture.
2. Preserve all 24 successful arrival fits, scores, paired wins, and finite
   alignment correlation.
3. In one predictive cell, set `reference_sd=0`, make observed unequal to the
   reference mean, serialize the residual null, and set
   `standardized_residual_nonfinite=true`.
4. Recompute the exact summary. The cell has finite aggregate
   `stouffer_z=0.0`, but `warning=true` solely because one residual is
   nonfinite.
5. Recompute and validate all controls.

Observed result:

```text
FORCED_WARNING_COUNTEREXAMPLE_ACCEPTED pass pass 0.0 True 1
```

The arrival stress was accepted as `pass` even though its only warning is
forbidden forced evidence.

Required correction:

1. Reconstruct separate `predictive_complete_finite`,
   `scientific_warning_available`, and `forced_warning` states from the exact
   replicate and summary rows.
2. Define scientific warning only when every required fit/cell is available,
   every required diagnostic is finite, and at least one finite Holm or
   Stouffer rule fires.
3. Treat failed fits, missing cells, null required aggregates, and nonfinite
   residual flags as incomplete/forced evidence. They cannot satisfy arrival,
   continuous-abundance, dropout, or frailty warning requirements.
4. Add integrated exact-manifest counterexamples for each stress class,
   including a case where forced and scientific warnings coexist so the
   precedence is explicit.

### I3. Design-gate evidence is fabricated or internally contradictory

The authority requires distinct design diagnostics with provenance and role
(Goal:433-458). Every applicable matrix must have rank 3 and condition below
`1e8`; a failed or nonfinite joint fit makes the plug-in gate fail
(Goal:450-457). These are decisive scenario inputs (Goal:898-928).

The implementation does not carry that evidence through the science bundle:

- `fit_execution_evidence.csv` has no potential, oracle, or plug-in design
  provenance/rank/condition/pass fields (source:5329-5353);
- `validate_science_bundle` accepts only fit, recovery, profile, coverage,
  latent, predictive, predictive-summary, and control rows
  (source:9367-9376);
- the reconciler sets `plugin_available = fit_available`, hardcodes oracle
  `design_pass=True`, and invents structured plug-in rank 3 and condition 1.0
  (source:9563-9569, 9586-9599);
- all other applicable joint scenarios receive only the same synthetic
  availability Boolean (source:9574-9585, 9600-9665).

There is also a typed fit inconsistency. `JointFitResult` has no invariant
validator (source:691-698). After optimization, `fit_joint_analyst_histories`
returns `converged=True` even when the plug-in diagnostic fails, merely adding
`failure_reason="joint_plugin_design_gate_failed"` (source:3071-3078).
Process-oracle results, by contrast, enforce consistent converged/diagnostic/
failure state in `__post_init__` (source:709-734).

Independent deterministic probe replaced only the optimizer and plug-in
diagnostic with typed in-memory fixtures:

```text
PLUGIN_FAILURE_RESULT True False joint_plugin_design_gate_failed
SCIENCE_BUNDLE_ARGUMENTS fit_rows recovery_rows profile_rows coverage_rows latent_rows predictive_rows predictive_summary_rows control_rows
FIT_EVIDENCE_HAS_DESIGN_FIELDS ()
```

Required correction:

1. Give `JointFitResult` a fail-closed invariant equivalent to the oracle
   result invariants. A failed potential or plug-in design gate cannot coexist
   with `converged=True`, accepted parameters, or null failure reason.
2. Make `fit_joint_analyst_histories` return a failed result when the plug-in
   gate fails, preserving the diagnostic for audit but rejecting the fit.
3. Persist exact applicable design evidence. Amend the fit-evidence schema, or
   add a separately declared artifact, with provenance, role, row/column count,
   rank, condition, pass, and typed failure. Define exact scenario/variant
   applicability and nullability.
4. Reconstruct every `design_pass`, `plugin_available`, `plugin_rank`, and
   `plugin_condition` from those persisted rows. Do not infer them from
   `fit_succeeded` and do not insert constants.
5. Update Goal/spec, headers, schema versions, report links, artifact
   dependencies, verification checks, and authority hashes consistently.
6. Add integrated tests that mutate each applicable potential/oracle/plug-in
   rank, condition boundary, provenance, role, missing row, duplicate row, and
   nonfinite condition. Every mutation must deterministically alter the local
   reason and reconstructed final rank/class as specified.

### I4. The exact 98 tests do not prove the integrated acceptance path

The proposal, literal manifest, and AST inventories are exactly 98/98/98,
unique, and ordered. All 98 nodes pass. The behavior coverage is nevertheless
incomplete at the authorization boundary:

- the complete science fixture makes only zero-driver and arrival replicate
  fits successful (tests:5956-5967);
- the reconstructed fixture reaches rank 1, class `model_contract_failed`,
  with both oracles, dense, structured, sparse, dropout, continuous abundance,
  and frailty failing;
- the rank-4 test uses `_passing_vector`, a hand-built reducer input detached
  from fit/profile/coverage/predictive/design artifact reconciliation
  (tests:7136-7143);
- the full-bundle tests therefore never prove an integrated rank-4 path and do
  not reject I1, I2, or I3. The two accepted full-bundle counterexamples and
  the inconsistent plug-in result all coexist with `98 passed`.

Required correction:

1. Strengthen the assigned exact 98 nodes rather than relying on unmanifested
   tests.
2. Build one deterministic complete science fixture that traverses the entire
   identity frame, derives successful recovery from exact profile groups,
   derives coverage from recovery, carries real design diagnostics, supplies
   finite scientific warnings where required, reconstructs exactly 18 control
   rows, and reaches rank 4/class
   `latent_response_observation_gate_passed`.
3. From that fixture, mutate one decisive artifact fact at a time and assert
   the exact local reason, control row, final rank, final class, and
   verification recommendation/pass result.
4. Include the I1-I3 counterexamples as assigned-node behaviors and prove the
   target full-bundle functions are reached.

## Strong Support Retained

The following surfaces were independently inspected and are not findings in
this rereview:

1. **Finite predictive arithmetic.** The per-cell validator reproduces exact
   finite Stouffer statistics, exact KS p-values, 27-family Holm adjustment,
   open warning thresholds, and typed nonfinite flags. I1 and I2 concern the
   downstream scenario reconciliation, not this arithmetic.
2. **Complete identity frames.** The reconstructed frames are exact:
   fit 990, recovery 2,340, coverage 105, latent 552 groups, predictive 504
   groups, and predictive-summary 23 groups. Successful profile groups are
   bound to fits, recovery endpoints are profile-derived, and coverage is
   recovery-derived.
3. **Control reconstruction.** The validator requires exactly 18 sorted rows
   and reconstructs scenario/status/final rows. The rank-1 fixture result is
   internally reproduced. I4 is the absence of an integrated rank-4 proof.
4. **Runtime contract.** A deterministic temporary example reconstructed
   exactly 11 measured units, 96 calibration tasks, 536 holdout tasks, eight
   LPT worker loads per phase, 1.20 safety scaling, projections 16.56 and
   92.64000000000001 seconds, false payload/scientific counters, and
   `passed=true` under the 1,500-second limit.
5. **Artifact and verification contract.** The manifest is exactly 22 files;
   `verification.json` represents the other 21 live files. The temporary
   represented digest was
   `722dbc7ac40a7b81ca9d32907273f43db502f933fa92fb5f429211ecc64744a0`.
   Verification rebuilt exactly 15 checks and derived recommendation and pass
   from the supplied science bundle. The rank-1 fixture correctly produced
   `model_contract_failed` and `passed=false`.
6. **Source identity.** Independent in-memory CSV reconstruction reproduced:

```text
landscape_sha256=53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a
arrival_sha256=5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba
source_sha256=6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0
counts=6048,5225,823,4605,4289
passable/sparse/fit/score=5225/1306/4180/1045
```

7. **Phase and no-side-effect boundaries.** Exact phase presence vectors,
   source authority, typed config/receipt hashes, temporary fixture ownership,
   canonical-path alias rejection, fixture zero counters, post-exposure
   envelopes, retry registry, exact staging, commit/merge/push transition
   validation, and one-time terminal attestation are materially implemented
   and exercised by assigned tests.
8. **Goal/spec/Runbook/Log authority.** Goal/spec bodies match; all 18 Runbook
   Bash blocks parse; the scoped Runbook/source command registries are 12/12
   exact and ordered; the Log chain verifies 18/18 parent hashes and 9/9
   declared byte counts.

## Bounded Verification Run

Exact executable manifest:

```text
uv run python - <<'PY'
import runpy, pytest
from pathlib import Path
p = Path('tests/test_synth_medium_latent_response_observation_recovery.py')
n = runpy.run_path(str(p))['AMENDMENT_TEST_NAMES']
assert len(n) == len(set(n)) == 98
raise SystemExit(pytest.main([*(f'{p}::{x}' for x in n), '--no-cov', '-q']))
PY

98 passed in 4.98s
exit=0
```

Static and structural checks:

```text
ruff format --check source/test: 2 files already formatted
ruff check source/test: All checks passed
mypy --no-incremental src tests: Success, 59 source files
git diff --check: pass
Runbook Bash parser: 18 blocks, 0 failures
Runbook/source command registry: 12/12 exact and ordered
proposal/manifest/AST: 98/98/98 exact, unique, and ordered
Goal/spec Objective body: identical
Log chain: 18/18 parent hashes, 9/9 declared byte counts
```

The two counterexamples and plug-in probe were deterministic, in-memory, and
accepted by the current public validation surfaces. Temporary artifact and
verification examples used an automatically removed temporary directory.

The full Goal test file and the two expensive nine-audit executions were not
run. They are unnecessary to establish the deterministic blockers above and
were outside the requested exact-98 bounded rereview.

## Git And No Exposure

```text
branch=codex/spatext-goal023-latent-response-observation-gate
HEAD=53462d0365babf2c8070714a930f69b4071af276
origin/main=53462d0365babf2c8070714a930f69b4071af276
git_common_dir=/Users/bwbrook/papers/spatext/.git
index=empty
remote Goal 023 branch=absent
canonical artifact directory=absent
preholdout receipt=absent
holdout receipt=absent
```

The pre-existing dirty candidate footprint was not staged or edited. This
rereview writes only this ignored report and does not edit tracked files or
Log.

## Complete Repair Gate

Task 3 remains blocked until all four Important findings are corrected in the
same authority tuple. The next independent rereview must receive fresh hashes,
reproduce Goal/spec body identity and the Log chain, rerun the exact 98-node
manifest plus bounded static/structural checks, and rerun all three
counterexamples against the repaired full-bundle validator.

Authorization requires zero Critical and zero Important findings. This review
does not meet that threshold.
