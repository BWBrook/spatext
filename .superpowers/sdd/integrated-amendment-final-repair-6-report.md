# Goal 023 Integrated Amendment Final Rereview 6 Repair Report

Date: 2026-07-12  
Role: coordinated `sol_high_specialist` deterministic fixture-validator repair owner  
Decision surface: exact pre-simulation contract only

## Result

I1-I4 and the Complete Repair Gate in
`integrated-amendment-final-rereview-6.md` are repaired on one authority tuple.
The literal 98-node amendment matrix, complete 297-node Goal file, 69 relevant
upstream regressions, two real temporary-worktree/terminal integrations, and
the complete authorized static/structural ladder are green.

This is a repair result, not acceptance. All reviews remain `PENDING`. Task 3
production execution, RNG construction, calibration, config emission, freeze,
holdout, real-project staging, commit, push, and publication remain `BLOCKED`.

## Changed Files

Tracked repair writes:

- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`
- `spec/synth_medium_latent_response_observation_recovery_gate.md`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`

Ignored evidence write:

- `.superpowers/sdd/integrated-amendment-final-repair-6-report.md`
- `.superpowers/sdd/integrated-amendment-final-repair-6-red-a.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-6-red-predictive.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-6-red-design-schema.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-6-green-exact-98-final.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-6-green-full-goal-final.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-6-green-upstream-final.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-6-green-git-terminal-final.xml`

Runbook, Plan, source receipt, `pyproject.toml`, lockfile, observation kernel,
and all unrelated tracked files were not changed by this repair. The existing
dirty candidate footprint was preserved.

## RED Evidence

RED was captured before implementation against working validation surfaces.
The raw and adjudicated counts are intentionally separated:

| Evidence | Raw result | Behavior disposition |
| --- | --- | --- |
| `integrated-amendment-final-repair-6-red-a.xml` | 3 tests, 3 failures, 0 errors, 703.676 s | T3A-011 is genuine: a converged `JointFitResult` accepted a failed plug-in design. The two predictive failures were test-setup mixed-summary algebra errors and are not counted as counterexample RED. |
| `integrated-amendment-final-repair-6-red-predictive.xml` | 2 tests, 2 failures, 0 errors, 6.080 s | Both genuine: zero-driver discarded finite open-boundary Stouffer/Holm failures; arrival accepted forced-only and forced-plus-finite warning states. |
| `integrated-amendment-final-repair-6-red-design-schema.xml` | 1 test, 1 failure, 0 errors, 0.534 s | Genuine: the declared fit artifact lacked all ten normalized design-evidence fields. |

Adjudicated behavior-specific RED is therefore four failing assigned nodes:
JointFit/design invariants, persisted design schema, zero-driver predictive
binding, and forced/scientific warning precedence. I4's missing integrated
rank-4 path was independently observed in rereview 6 as a complete bundle that
stopped at rank 1; the strengthened T3R-020 and T3S-001 nodes now traverse the
real complete bundle rather than a hand-built reducer vector.

Evidence hashes:

| Evidence | SHA-256 |
| --- | --- |
| RED A | `ffc80de15f57ec1f1759de62ff1a40f620edd7a74f5ed1289590e995cc8008a5` |
| RED predictive | `eb03780acab46a62e0f62788360fbd83adc0e0dbdcb4766604f7e33a642a9eee` |
| RED design schema | `afcee32b571c66f714419e0291622d538b2a1b27e49cfe489562e53bc116f208` |

## Finding Dispositions

### I1: zero-driver predictive pass

- Added literal `predictive_pass` to zero-driver evidence in Goal/spec/source.
- Reconstructed it from the exact validated holdout replicate and 27-cell
  summary frame.
- Required it before the `0..6` exclusion decision.
- Full-bundle Stouffer exactly `3` and Holm exactly `0.01` pass; the next value
  across either open boundary produces
  `contract_failure:zero_driver_unavailable`, a failed control row, rank 1,
  `model_contract_failed`, and verification `passed=false`.

### I2: forced versus scientific warnings

- Added the complete `PredictiveScenarioState`:
  `predictive_complete_finite`, `predictive_pass`, `finite_rule_fired`,
  `scientific_warning_available`, and `forced_warning`.
- Complete finite evidence is reconstructed from exact validated replicate and
  summary rows, including failed/missing fits, unavailable diagnostics, null
  required aggregates, and nonfinite residual flags.
- Scientific warning exists only for complete finite evidence with Holm
  adjusted `p < 0.01` or `abs(Stouffer Z) > 3`.
- Forced warning takes precedence if forced and finite-rule evidence coexist;
  the finite rule remains visible but cannot satisfy a stress warning gate.
- Arrival, informative dropout, continuous abundance, and spatial frailty are
  each tested under forced-only and forced-plus-finite-rule mutations. Every
  mutation reaches the scenario reducer and produces the exact local contract
  reason, failed control row, rank 1, and model-contract class.

### I3: JointFit and persisted design evidence

- `JointFitResult` now rejects convergence unless parameters, converged joint
  multistart, potential pass, plug-in pass, and null failure all agree.
- A failed result rejects parameters and requires a nonempty typed reason.
- `fit_joint_analyst_histories` now returns `converged=false`, null parameters,
  the retained converged multistart, retained failed plug-in diagnostic, and
  `joint_plugin_design_gate_failed`.
- `fit_execution_evidence.csv` is normalized `v2`, retaining the exact
  22-artifact contract. Its literal 33-column header adds row kind, design kind,
  provenance, role, row/column counts, rank, condition, pass, and typed failure.
- Exact applicability is persisted: process oracle has potential+oracle;
  observation oracle and equal-rate have potential; every other registered
  variant has potential+plug-in.
- The complete frame is exactly 990 fit-result rows plus 1,695 design rows.
- Missing, duplicate, foreign, inapplicable, wrong provenance/role, nonfinite,
  rank-deficient, and condition-boundary states fail closed.
- Scenario design pass, plug-in availability, rank, condition, and oracle state
  are derived only from persisted rows. No fit-success inference or reducer
  constant remains.

### I4: integrated acceptance path

- The deterministic COMPLETE fixture traverses exactly:
  990 fit identities, 1,695 design rows, 2,340 recovery rows, 11,700 profile
  points, 105 coverage rows, 552 latent groups, 504 predictive groups, 23
  predictive-summary groups, and 18 controls.
- Every successful required fit has a complete ordered profile group; recovery,
  intervals, errors, coverage, controls, and verification are recomputed.
- All eleven scenarios produce local `pass`; final rank is 4 and class is
  `latent_response_observation_gate_passed`; recommendation and verification
  top-level pass are true.
- One-fact predictive and design mutations propagate through local reason,
  control row, final rank/class, verification detail, and top-level pass.
- Exactly 98 manifest names and their order were preserved.

## Authority Additions

Goal and spec remain byte-identical from `## Objective`. They now literally
define:

- normalized fit/design artifact schema version `v2`, exact 33-column header,
  types, row-specific nullability, seven-part primary/sort key, row kinds,
  design kinds, applicability, provenance, role, dimensions, rank, condition,
  pass, and typed failures;
- exact design condition boundaries: finite `>=1`, strict `<1e8`, rank 3;
- fail-closed `JointFitResult` consistency and exact plug-in failure state;
- the five predictive provenance states, finite scientific rule, open
  boundaries, and forced-warning precedence;
- zero-driver's required predictive pass;
- the complete rank-4 fixture frame and verification detail bindings;
- unchanged report links, updated control visual dependency, and unchanged
  exact 22-file artifact count.

No biological/model/threshold/seed/scenario invariant changed.

## GREEN Evidence

Final executable evidence on the bound source/test tuple:

| Validation | Result | JUnit SHA-256 |
| --- | --- | --- |
| Exact literal 98-name manifest | `98 passed in 738.60s` | `808ccbf205f451d44345cd2fb38ba18cb2ccf0cf28cee2935e59da030936653a` |
| Complete Goal 023 file | `297 passed in 741.68s` | `056479d3425e648e77aba9807197451add762e719162f74b46c8f84d94b0869e` |
| Relevant upstream regressions | `69 passed in 46.65s` | `8c6cca1ec72a7e8acd9eaec0c790dfe661478ae5d64df91e06b489b188e91de6` |
| Real temporary two-worktree/terminal integration | `2 passed in 1.12s` | `9c8c8be5eac5305def8c9bbd0b2531065f846055d0e26fabf9b1f9c83894b073` |

The first full-file invocation also had all 297 tests pass, but the command's
repo-wide coverage plugin returned nonzero because an isolated single-file run
covered only 40% of unrelated modules against the global 90% threshold. The
same 297 nodes were rerun with `--no-cov`; the final zero-exit result above is
the authoritative full-file evidence. No assertion failed in either run.

Static and structural evidence:

```text
Ruff format: 85 files already formatted
Ruff check: All checks passed!
mypy --no-incremental src tests: Success, 59 source files
git diff --check: pass
proposal/manifest/AST: 98/98/98 exact, unique, ordered, executable 98/98
Runbook Bash parser: 18 blocks, 0 failures
Runbook/source command registry: 12/12 exact and ordered
Goal/spec Objective identity: 147228 bytes, exact
source hashes: exact receipt landscape/arrival/derived identity
science frames: 990/2340/105/552/504/23
cell frames: 5225/1306/4180/1045, fit/score intersection 0, union 5225
post-append Log chain: 19/19 parent hashes, 10/10 byte counts
```

Independent source reconstruction:

```text
landscape_sha256=53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a
arrival_sha256=5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba
source_sha256=6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0
counts=6048/5225/823/5225
```

## Authority Hashes

| Surface | SHA-256 |
| --- | --- |
| Goal | `03a59a5e0eae6aa8dfd74bf3e4e57550d4bbecef90544540033f1adc96ffe1cf` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb` |
| authoritative spec | `e48bf2a18282b2fb4d76429bb551613dcd3d988c137766a579500785b8134fd3` |
| Goal/spec Objective body | `bb97515b8a7769235c33a98abfd5aa6854cd62f2c5c84cabed9ed1e5a164e97a` |
| source | `6108006d816e7fa5e54a005d1d5d98922b83225fb57578fd4699e79ba001c726` |
| tests | `a0d298e3ba885306d21e154e3085a76e5b7cbe08630f14e86cc7886dc358f78c` |
| source receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |
| rereview 6 | `fe8528caada0f314ea7430fe1542a8999bcf9fd0d3b5ba7018d4715636a99451` |
| final Log | `a65439ece9b807e4186183a9996e9d967c213da86c618864ee2f997622a848a6` |

## Log Binding

Live parent immediately before append:

```text
lines=3024
bytes=151572
sha256=d88afdf3c0bc7bad4e02023cba4c94e0458269e3daf3d85c314ac4997669c999
```

New Log shape:

```text
lines=3157
bytes=158768
sha256=a65439ece9b807e4186183a9996e9d967c213da86c618864ee2f997622a848a6
chain=19/19 parent hashes, 10/10 declared byte counts
```

The one appended record is
`integrated_amendment_final_rereview_6_repair_v1`. All review dispositions and
acceptance are `PENDING`; Task 3 and every stochastic/irreversible authority
remain `BLOCKED`. No acceptance record was appended.

## Git And No Exposure

```text
branch=codex/spatext-goal023-latent-response-observation-gate
HEAD=53462d0365babf2c8070714a930f69b4071af276
origin/main=53462d0365babf2c8070714a930f69b4071af276
index=empty
remote Goal 023 branch=absent
canonical artifact directory=absent
recovery config=absent
preholdout receipt=absent
holdout receipt=absent
production Goal 023 CLI=absent
```

Pre-existing status was preserved: `pyproject.toml` and `uv.lock` remain
modified; the untracked Goal packet, spec, observation files, source, and tests
remain untracked. Nothing was staged.

No Task 3 production CLI or live scenario ran. No production RNG object,
vector, or payload was constructed. No simulation, runtime benchmark,
calibration, canonical artifact/config/receipt, production freeze, holdout,
real-project staging, commit, push, publication, cleanup, reset, restore,
deletion, or external exposure occurred. Test-side deterministic fixtures,
spies, fake runners, temporary serializers, and pytest-cleaned temporary Git
repositories were the only execution surfaces.
