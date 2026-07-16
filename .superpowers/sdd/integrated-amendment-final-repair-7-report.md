# Goal 023 Integrated Amendment Final Rereview 7 Repair Report

Date: 2026-07-12  
Role: coordinated `sol_high_specialist` fail-closed contract repair owner  
Decision surface: exact pre-simulation contract only

## Result

**DONE**

I1-I4 and M1 from the SHA-256-specific rereview 7 are repaired on one
authority tuple. The exact 98-node manifest, complete 297-node Goal file, 69
relevant upstream regressions, two real temporary-worktree/terminal
integrations, static/structural ladder, Log chain, source receipt, state guards,
and no-exposure checks are green.

This is a repair result, not acceptance. Every review remains `PENDING`.
Task 3 and all stochastic, artifact, config, receipt, freeze, holdout, staging,
commit, push, and publication authorities remain `BLOCKED`.

## Changed Files

Tracked repair writes:

- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`
- `spec/synth_medium_latent_response_observation_recovery_gate.md`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`

Ignored repair/evidence writes:

- `.superpowers/sdd/integrated-contract-amendment-proposal.md`
- `.superpowers/sdd/integrated-amendment-final-repair-7-report.md`
- `.superpowers/sdd/integrated-amendment-final-repair-7-red.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-7-green-targeted.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-7-green-98.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-7-green-full.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-7-green-upstream.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-7-green-gitterminal.xml`

Plan, Runbook, source receipt, dependency files, observation kernel, artifact
count, and unrelated existing changes were not changed by this repair.

## RED Evidence

Behavior-specific RED ran against the working current code before source or
authority edits:

```text
T3A-007: expected arrival design rows 83600, observed 104500
T3A-011: successful fit plus failed decisive design did not raise
T3D-014: predictive sample_size=999999 did not raise
3 failed in 714.04s; exit 1
```

JUnit SHA-256:
`56aec63d65b70dc44058faa4b7cdabb3f5854ab81488e98b839c1c52c5c32f5b`.
These were missing-behavior failures, not import, collection, fixture-root, or
artifact setup errors.

## Finding Dispositions

### I1: arrival fit-frame design authority

- Potential and plug-in diagnostics use exactly 4180 fit cells and 83600 rows.
- Persisted diagnostics bind exact cell count and sorted-cell identity SHA-256.
- Score cells remain limited to heldout score and predictive comparison.
- One-cell fit/score swaps, wrong digests/counts, and 104500-row arrival
  mutations fail before reduction.

### I2: authoritative design invariants

- `DesignDiagnostic` validates exact builtin types, positive dimensions,
  `0 <= rank <= n_columns`, the rank/condition convention, derived pass, and
  failure nullability.
- Joint and process-oracle result constructors invoke the validator.
- Forged rank/pass, condition/pass, NaN/nonfinite, invalid-dimension, and
  contradictory failure states are rejected for potential, plug-in, and
  oracle diagnostics.

### I3: persisted fit/design state machine

- The complete fit/design table is identity-partitioned before state checks.
- Failed potential forces a failed parameter-null fit and downstream
  `not_evaluated_potential_failed` diagnostics.
- Failed/nonfinite joint and process-oracle fits require their exact rank-zero
  downstream failure states.
- Plug-in/oracle rank or condition failure forces the fit to failed and
  parameter-null while retaining diagnostic evidence.
- Successful fits require every applicable design to pass; observation-oracle
  and equal-rate potential-only exceptions are explicit.
- Contradictions stop before scenario, control, recommendation, or verification
  reduction.

### I4: predictive retained-frame binding

- Predictive rows now persist opportunity-frame count/SHA-256 and nullable
  fixed dropout-mask SHA-256 inside the existing predictive artifact.
- Sample sizes derive from retained canonical `(cell_id,time)` opportunities;
  all three metrics share the same exact `n` per stratum.
- Arrival uses score cells. Informative dropout binds its deterministic
  fixture-only fixed mask without production RNG or payload construction.
- Size, digest, metric-disagreement, fit/score-frame, and mask mutations fail
  before summary, recommendation, and verification.
- The complete rank-4 fixture no longer uses `n=2` and retains every exact
  science-frame count and all eleven local passes.

### M1: proposal behavior

T3A-005 now describes the exact 35-column normalized fit/design schema,
seven-part key, explicit row/design ordering, frame binding, and retained
failed rows. Its assigned name and manifest position are unchanged.

## Validation

| Validation | Result | Evidence SHA-256 |
| --- | --- | --- |
| Exact literal 98-name manifest | `98 passed in 745.50s` | `2b7c5217067af1d04f8d4b64a85750b28ca6771badbe12bed7e51fc31a555f8f` |
| Complete Goal 023 test file | `297 passed in 750.21s` | `bb747792a0d9a6381794b44d2c11e72f93a3d0a89d498f3193f71d6a8e1f676e` |
| Relevant upstream regressions | `69 passed in 46.74s` | `1dba3e539e4de7710f13e4176c435536becd1cdad5d425f8aeb755d2200b7a63` |
| Real worktree/terminal integration | `2 passed in 1.38s` | `ab8b184ec5493373e247199c90ed073c00032cb2fe81bb5f23080f548e56024a` |

Focused and full Goal runs used `--no-cov` because the repo-wide 90% coverage
threshold is not meaningful for isolated selectors. No assertion failed.

Static and structural evidence:

```text
Ruff format: 85 files already formatted
Ruff check: All checks passed!
mypy --no-incremental src tests: Success, 59 source files
git diff --check: pass
proposal/manifest/AST: 98/98/98 exact, unique, ordered
Runbook Bash parser: 18 blocks, 0 failures
Runbook/source command registry: 12/12
Goal/spec Objective identity: 151187 bytes, exact
Goal/spec Objective SHA-256: 815c0109f13b846b5a66cb00184384559ba7299e6c91af70d90a4d09248e065c
artifact registry: exactly 22 paths
alignment frames: 4180/1045, intersection 0, union 5225
source receipt: exact accepted file, landscape, arrival, and derived identities
post-append Log chain: 20/20 parent hashes, 11/11 declared byte counts
```

Complete fixture evidence remains:

```text
fit/design/recovery/profile/coverage = 990/1695/2340/11700/105
latent/predictive/predictive-summary/control = 552/504/23/18
local gates = 11 pass
recommendation = rank 4, latent_response_observation_gate_passed
recommendation and verification passed = true/true
```

## Final Tuple Hashes

| Surface | SHA-256 |
| --- | --- |
| Goal | `a99909b344cbf8f342a443112d06b38e30ec10e514f6d9e4966cb4c0ab5cf759` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb` |
| authoritative spec | `b22d796375ce507317a35a7e6156dcdb138c182f4cb9a35f7dfc3e103ef6dffc` |
| Goal/spec Objective body | `815c0109f13b846b5a66cb00184384559ba7299e6c91af70d90a4d09248e065c` |
| source | `973ed93a7165e78ba267f0d3a87b24065a7448b70aed713b22bf1558efd81b0b` |
| tests | `bc6827f5fce8ef73d7776771d0eeaf6abf4d82ef3c1aa5f70d023c1020cfc2b4` |
| proposal | `7a2fea9874f69aeef07d074c9e217b62aabc7507a8e9ad728e5d707963716b97` |
| source receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |
| derived source identity | `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0` |
| rereview 7 | `6439d8235ce469e1a103df9560b217109ec5fb16db40062471cad9f4e26042e3` |
| final Log | `02f94a646d75557afe92f944fc82eb8869d452c28a7a42d94fdc044c820cc6a3` |

## Log Binding

Live parent immediately before append:

```text
lines=3157
bytes=158768
sha256=a65439ece9b807e4186183a9996e9d967c213da86c618864ee2f997622a848a6
```

Final Log:

```text
lines=3282
bytes=165543
sha256=02f94a646d75557afe92f944fc82eb8869d452c28a7a42d94fdc044c820cc6a3
chain=20/20 parent hashes, 11/11 declared byte counts
```

Exactly one record was appended:
`integrated_amendment_final_rereview_7_repair_v1`. All reviews and acceptance
remain `PENDING`; Task 3 and all stochastic/irreversible authorities remain
`BLOCKED`.

## Git And No Exposure

```text
branch=codex/spatext-goal023-latent-response-observation-gate
HEAD=53462d0365babf2c8070714a930f69b4071af276
origin/main=53462d0365babf2c8070714a930f69b4071af276
index=empty
index_sha256=bf54e224e227ca6c2a33be68ec287431a202ac4ffd589a36d11740685c9a3564
remote Goal 023 branch=absent
canonical artifact directory=absent
recovery config=absent
preholdout receipt=absent
holdout receipt=absent
production Goal 023 CLI=absent
```

No production CLI, RNG object, vector, payload, simulation, benchmark,
calibration, canonical artifact/config/receipt, freeze, holdout, staging,
commit, push, cleanup, reset, restore, deletion, or publication occurred.
Nothing was staged. Pre-existing `pyproject.toml`, `uv.lock`, observation, and
Goal 023 candidate worktree changes were preserved.

## Concerns

The deterministic dropout ledger is fixture-only. A future production row must
bind the actually realized fixed dropout mask under the same count/digest
contract. That future boundary is not authorized here.

Fresh independent hash-specific rereview is still required. Until it returns
zero Critical and zero Important findings, Task 3 remains blocked.
