# Goal 023 Integrated Amendment Final Rereview 7

Date: 2026-07-12  
Role: independent adversarial `sol_max_auditor` scientific reproducibility and
software-quality review  
Decision surface: exact current pre-simulation contract only

## Verdict

**NOT SUPPORTED**  
**TASK 3 NOT AUTHORIZED**

The audited claim is that the exact current Goal 023 pre-simulation contract
may authorize Task 3 fixture-only implementation. The authorization rule is
literal: authorization is permitted only with zero Critical and zero Important
findings.

This rereview finds **zero Critical, four Important, and one Minor** finding.
The exact assigned 98-node manifest passes, and the earlier zero-driver,
warning-provenance, persisted-design, rank-4-fixture, mutation-propagation, and
provenance/terminal repairs are present. Fresh counterexamples nevertheless
show that the contract still accepts scientifically contradictory design and
predictive evidence. A green manifest is therefore regression evidence, not
authorization evidence.

No Task 3 production execution, stochastic vector, simulation, benchmark,
calibration, canonical artifact/config/receipt, freeze, holdout, real-project
staging, commit, push, exposure, or publication was performed.

For concise citations below:

- `Goal.md` means
  `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`;
- `source.py` means
  `src/spatext/synth/medium/latent_response_observation_recovery.py`;
- `tests.py` means
  `tests/test_synth_medium_latent_response_observation_recovery.py`; and
- `proposal.md` means
  `.superpowers/sdd/integrated-contract-amendment-proposal.md`.

## Exact authority and identity

The supplied tuple reproduced byte for byte:

| Surface | SHA-256 |
| --- | --- |
| Goal | `03a59a5e0eae6aa8dfd74bf3e4e57550d4bbecef90544540033f1adc96ffe1cf` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb` |
| authoritative spec | `e48bf2a18282b2fb4d76429bb551613dcd3d988c137766a579500785b8134fd3` |
| source | `6108006d816e7fa5e54a005d1d5d98922b83225fb57578fd4699e79ba001c726` |
| tests | `a0d298e3ba885306d21e154e3085a76e5b7cbe08630f14e86cc7886dc358f78c` |
| Log | `a65439ece9b807e4186183a9996e9d967c213da86c618864ee2f997622a848a6` |
| source receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |

Inspected supplements also reproduced: current proposal
`ee367b6014bf823ffda2f406186179271a0f0e56ac955ea35ae6fb11c3bea15d`,
rereview 6
`fe8528caada0f314ea7430fe1542a8999bcf9fd0d3b5ba7018d4715636a99451`,
and repair-6 report
`a85e93a8177d5eefde09e3d8519e7cfe73e14c0ba1224b382b3f87cb74c20a20`.

Goal and spec are byte-identical from the `## Objective` header onward:
`147228` bytes, SHA-256
`bb97515b8a7769235c33a98abfd5aa6854cd62f2c5c84cabed9ed1e5a164e97a`.
The Log is exactly `3157` lines and `158768` bytes; all `19/19` parent hashes
and all `10/10` declared parent byte counts independently reproduce.

The source receipt's landscape and arrival hashes independently reproduce as
`53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a`
and
`5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba`;
their derived source identity is
`6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`.

## Strongest supporting evidence

The previous rereview-6 blockers are materially repaired:

1. Zero-driver evidence now includes persisted/reconstructed
   `predictive_pass`; complete finite evidence and open thresholds are literal
   in `Goal.md:2809-2836`, `source.py:9100-9140,9327-9337,9946-9955`, and
   `tests.py:6194-6277`. Exactly `p=0.01` and `abs(Z)=3` pass; the adjacent
   representable value beyond either boundary fails.
2. Forced versus finite warning provenance and precedence are reconstructed in
   `source.py:9100-9140,9825-9855,9956-9999`. Assigned test D-014 exercises
   forced-only and forced-plus-finite evidence for arrival, dropout,
   continuous-abundance, and frailty and obtains the exact local failure and
   rank-1 control result (`tests.py:7254-7341`).
3. The v2 fit/design table persists potential/oracle/plugin applicability,
   provenance, role, rank, condition, pass, and failure state
   (`Goal.md:1719-1802`; `source.py:6546-6658,9673-9689`).
4. The deterministic full fixture contains `990` fit identities, `1695` design
   identities, `2340` recovery rows, `11700` profile points, `105` coverage
   rows, `552` latent groups, `504` predictive groups, `23` predictive-summary
   rows, and `18` controls. It reports all 11 scenario gates `pass`, final rank
   `4`, class `latent_response_observation_gate_passed`, and verification
   `passed=true` (`tests.py:6626-7065,7912-7941,8153-8176`).
5. The assigned integrated mutations propagate the exact local reason, local
   control, final rank/class, and `verification=false`
   (`tests.py:8187-8276`). Runtime, artifact, source, phase, provenance,
   publication, terminal, fixture, and no-exposure behavior remains represented
   by the exact manifest nodes through `tests.py:9742`.

These are genuine strengths. They do not cover the fresh counterexamples below.

## Findings

### Critical

None.

### Important I1 - The arrival design gate is not computed on the fitted frame

The contract freezes `4180` arrival fit cells and `1045` score cells and says
that both alignment models are fit only on fit cells (`Goal.md:1046-1051`). It
also requires every non-sparse potential and plugin diagnostic to report
`104500 = 5225 * 20` rows (`Goal.md:1791-1793`). The implementation encodes the
full-landscape count for arrival (`source.py:5492-5495`) even though it
independently reconstructs the exact `4180/1045` split
(`source.py:7240-7254`). The fixture hard-codes the same full-landscape count
(`tests.py:4048-4088`).

Fresh deterministic output, exit `0`:

```text
alignment_fit_score=[4180,1045]
arrival_declared_potential_rows=104500
arrival_fit_only_rows=83600
```

A practical-identifiability gate over cells not used by the fit does not prove
identifiability of that fit. For the plugin gate it also requires posterior
weights from score-cell analyst histories, so a decisive fit-acceptance input
consumes the score frame. The current authority cannot simultaneously preserve
the literal fit-only split and implement the stated row count.

Complete correction:

1. Define the decisive arrival potential and plugin matrices on the exact
   `4180` fit-cell IDs only, hence `83600` rows; keep any full-landscape
   diagnostic separate and explicitly nondecisive.
2. Bind the fit-cell identity/digest to both persisted diagnostics, and prohibit
   score-cell histories from plugin-fit acceptance. Score cells remain limited
   to the declared score/predictive comparisons.
3. Amend Goal/spec row-count authority, `expected_potential_design_rows`, the
   fixture builders, and assigned T3A-005/T3A-007/T3A-011 tests. Require a
   one-cell fit/score swap or `104500` arrival row mutation to fail before
   reduction and verification.
4. Reseal Goal/spec/source/tests/Log hashes and rerun a fresh independent audit.

### Important I2 - Typed design-result invariants trust a forged `passed` flag

`DesignDiagnostic` has no invariant validator (`source.py:335-344`).
`JointFitResult` checks labels and then trusts `diagnostic.passed`
(`source.py:700-747`); `ProcessOracleFitResult` does the same with even fewer
rank/condition checks (`source.py:771-794`). This is weaker than the literal
rank/condition/pass algebra in `Goal.md:1791-1802` and the fail-closed result
contract in `Goal.md:2801-2807`. T3A-011 rejects an honestly encoded failed
plugin but never supplies `rank=2, passed=true` (`tests.py:5168-5238`).

Fresh constructor probes, exit `0`:

```text
bad_potential: JointFitResult accepted converged=true, potential_rank=2
bad_plugin:    JointFitResult accepted converged=true, plugin_rank=2
bad_oracle:    ProcessOracleFitResult accepted converged=true, rank=2, passed=true
```

Complete correction:

1. Add one authoritative in-memory `DesignDiagnostic` validator: exact builtin
   types; positive dimensions; `0 <= rank <= n_columns`; the frozen
   rank/condition convention; `passed` derived exactly from full rank, finite
   condition `>=1`, and condition `<1e8`; and failure null if and only if pass.
2. Make all joint/process result constructors invoke that validator and derive,
   rather than trust, acceptance. Preserve a failed diagnostic for audit but
   reject convergence and accepted parameters.
3. Strengthen an assigned node with rank-2/`passed=true`, condition
   `>=1e8`/`passed=true`, NaN/nonfinite, invalid dimensions, and contradictory
   failure-reason probes for potential, plugin, and oracle results.
4. Reseal source/tests/Log and obtain fresh hash-specific review.

### Important I3 - Persisted fit and design rows lack cross-row state invariants

The row validator checks each fit or design row independently and then merely
partitions the table (`source.py:6546-6781,6810-6816`). Complete-frame checking
verifies identities, not state coherence (`source.py:9673-9689`). The reducer
then turns a contradictory design into a local gate failure
(`source.py:9876-9888`) instead of rejecting an impossible bundle. Indeed, the
assigned mutation deliberately leaves a successful fit row in place while
changing a potential/plugin row to failed, and the bundle is accepted for
reduction (`tests.py:5099-5166`). This contradicts `Goal.md:2801-2807`.

Fresh row-level probes, exit `0`, were both accepted:

```text
successful_fit + failed_potential + passing_plugin
successful_fit + passing_potential + failed_plugin
```

Complete correction:

1. After identity partitioning, enforce a state machine per fit identity. A
   failed potential implies `fit_succeeded=false`, no accepted estimates, and
   each downstream diagnostic failed/not evaluated with
   `not_evaluated_potential_failed`.
2. With potential passing, a failed/nonfinite joint fit requires a failed
   plugin with `joint_fit_failed_or_nonfinite`; a failed process-oracle fit
   requires the oracle code `process_oracle_fit_failed_or_nonfinite`.
3. A successful fit requires every applicable decisive design to pass. A
   plugin/oracle rank or condition failure must make the persisted fit failed
   and parameter-null, while retaining the diagnostic. Encode the existing
   equal-rate/observation-oracle applicability exceptions explicitly.
4. Add assigned full-bundle one-fact tests for every transition above; each
   contradiction must be rejected before local reason/control/final
   rank/class/verification are constructed. Reseal and rereview.

### Important I4 - Predictive sample size is unbound and the rank-4 fixture is impossible

Predictive metrics must use exactly the retained opportunity frame
(`Goal.md:1485-1503`). The constructor instead accepts caller-provided stratum
sizes (`source.py:8767-8808`), and validation checks only integer `>=2`
(`source.py:8840-8847`). It does not bind sizes to scenario/split/replicate,
require the three metrics in a stratum to share the same `n`, or reproduce
sizes from the fixed schedule/dropout/score frame.

The complete rank-4 fixture assigns sample size `2` to every `all`, quintile,
and time-band stratum (`tests.py:6931-6936`) and is nevertheless accepted as all
11 pass/rank 4/verified true (`tests.py:7912-7941,8153-8176`). A fresh probe
also accepted `sample_size=999999` in every cell, exit `0`.

Complete correction:

1. Freeze and reconstruct exact sample sizes from the same retained analyst
   opportunity frame used for each scenario/split/replicate; arrival uses score
   cells and stochastic-dropout scenarios use their realized fixed masks.
2. Require the three metrics within each stratum to carry one identical exact
   `n`. Persist and bind an opportunity-frame digest/count ledger in the
   existing predictive artifact or explicitly amend the artifact contract.
3. Replace the impossible rank-4 fixture sizes with authoritative counts. Add
   one-fact size, digest, metric-disagreement, score/fit-frame, and dropout-mask
   mutations that fail before summary, recommendation, and verification.
4. Amend Goal/spec/source/tests/Log, reseal all hashes, and rereview.

### Minor M1 - One proposal behavior description is stale

`proposal.md:1641` still assigns T3A-005 an exact 23-column schema, while the
binding Goal requires 33 columns (`Goal.md:1721-1725`) and the test asserts the
33-column header (`tests.py:4431-4436`). The proposal/manifest/AST names remain
exact, so this does not add a blocking finding under the tracked-authority
hierarchy. Mark the proposal behavior text superseded or update and rebind its
hash so “98 assigned behaviors” is semantically as well as nominally exact.

## Independent execution and bounded structural checks

The successful exact-manifest command was:

```bash
TMPDIR=/private/tmp \
UV_CACHE_DIR=/private/tmp/spatext-rereview7-uv-cache \
PYTHONDONTWRITEBYTECODE=1 \
PYTEST_ADDOPTS='-p no:cacheprovider' \
uv run --no-sync python - <<'PY'
import runpy
import tempfile
from pathlib import Path
import pytest
p = Path('tests/test_synth_medium_latent_response_observation_recovery.py')
n = runpy.run_path(str(p))['AMENDMENT_TEST_NAMES']
assert len(n) == len(set(n)) == 98
with tempfile.TemporaryDirectory(prefix='spatext-rereview7-', dir='/private/tmp') as root:
    code = pytest.main([
        *(f'{p}::{name}' for name in n),
        '--no-cov', '-q', '--basetemp', f'{root}/pytest',
    ])
raise SystemExit(code)
PY
```

Result: **exit `0`; `98 passed in 774.62s (0:12:54)`; no pytest warnings.**
No broad test suite was run.

Harness diagnostics are retained rather than hidden:

- An initial invocation before redirecting the uv cache exited `2` before
  collection because `/Users/bwbrook/.cache/uv` was not writable.
- The first complete 98-selector run used `/private/tmp` for `--basetemp` but
  did not set `TMPDIR`. It exited `1` with `96 passed, 2 failed in 757.94s`.
  Both failures were fixture-root guard mismatches because Python's
  `gettempdir()` authority and pytest's forced base differed; the failing nodes
  were `test_lro_3s_010_two_fixture_bundles_are_byte_identical` and
  `test_holdout_success_freezes_represented_and_complete_artifact_snapshots`.
  No production state was reached. Setting `TMPDIR=/private/tmp` produced the
  clean exact rerun above.

Additional bounded checks:

| Check | Outcome |
| --- | --- |
| proposal / manifest / AST inventory | `98/98/98`, unique, exact, ordered; `98/98` nodes contain an assertion/raise; exit `0` |
| science frames | fit `990`, design `1695`, recovery `2340`, coverage `105`, latent `552`, predictive `504`, predictive summary `23`; exit `0` |
| deterministic counterexample probe | reproduced all four Important findings; exit `0` |
| Runbook shell structure | all `18/18` Bash blocks pass `bash -n`; exit `0` |
| Runbook/source command registry | `12/12`, exact and ordered; exit `0` |
| Ruff format check on source/tests | `2 files already formatted`; exit `0` |
| Ruff check on source/tests | `All checks passed!`; exit `0` |
| mypy on source/tests, no incremental cache | `Success: no issues found in 2 source files`; exit `0` |
| `git diff --check` | no output; exit `0` |

## Git, index, Log, production state, and exposure

The audited branch, HEAD, and upstream are
`codex/spatext-goal023-latent-response-observation-gate`,
`53462d0365babf2c8070714a930f69b4071af276`, and the same `origin/main`
commit (`+0/-0`). The pre-existing worktree modifications/untracked Goal 023
packet remain exactly as found. The Git index is empty and its index-file hash
is `bf54e224e227ca6c2a33be68ec287431a202ac4ffd589a36d11740685c9a3564`.
The Log hash/line/byte identity above is unchanged.

The canonical artifact directory, recovery config, preholdout receipt, holdout
receipt, production Goal 023 CLI, and remote Goal 023 branch are absent. All
deterministic examples and pytest bases were outside the repository and were
removed; the path-guarded cleanup exited `0` with no
`/private/tmp/spatext-rereview7*` paths remaining. A direct shell removal was
rejected by execution policy before running; it changed nothing.

This report is the only repository file written by this audit. It is ignored by
Git; no tracked file, authority document, source, test, Log byte, or index entry
was changed.

## Residual uncertainty and strict Task 3 boundary

The exact manifest proves deterministic behavior for its assigned examples,
not completeness against unassigned contradictions. No production numerical
fit, stochastic generator, reference simulation, or disk-first canonical
bundle was executed, so no scientific result is inferred from this audit.

After all four Important corrections are sealed, a fresh hash-specific audit
must rerun the exact assigned manifest plus the new counterexamples. Even a
future `SUPPORTED / TASK 3 AUTHORIZED` disposition would authorize only the
Task 3 fixture implementation boundary. It would not authorize live production
execution, RNG construction, simulation, benchmark, calibration, canonical
artifact/config/receipt creation, freeze, holdout, real-project staging,
commit, push, exposure, or publication.
