# Goal 023 Integrated Amendment Final Repair 8 Report

Date: 2026-07-12  
Role: `sol_high_specialist`  
Disposition: **DONE - REPAIR COMPLETE, ALL REVIEWS PENDING**  
Authority source: `integrated-amendment-final-rereview-8.md`, SHA-256
`c85fe1cca10f3dd31145bbd4354484ad3e5e933a3b9fe2df8736c792c770a367`

## Executive Result

All four Important findings I1-I4 are repaired as one coordinated fail-closed
amendment. The exact assigned 98-node manifest, complete 297-node Goal file,
69-node relevant upstream set, and two real terminal/worktree integration nodes
are green. Goal and authoritative spec are byte-identical from `## Objective`.
The artifact registry remains exactly 22 paths, and the complete fixture
retains all eleven local passes, rank 4,
`latent_response_observation_gate_passed`, and true recommendation and
verification.

Exactly one parent-prefix-bound Log child was appended. Every review remains
`PENDING`; Task 3 and every stochastic or irreversible authority remain
`BLOCKED`. No production or publication authority is granted by this repair.

## Initial State And Boundaries

Branch, HEAD, and base remained:

```text
branch=codex/spatext-goal023-latent-response-observation-gate
HEAD=53462d0365babf2c8070714a930f69b4071af276
origin/main=53462d0365babf2c8070714a930f69b4071af276
```

The worktree was already dirty and the Goal 023 packet was untracked. Those
pre-existing edits were preserved. No clean, reset, restore, delete, stage,
commit, push, production CLI, RNG, vector, payload, simulation, benchmark,
calibration, canonical artifact/config/receipt, freeze, holdout, or publication
operation was performed.

Plan and Runbook did not require amendment and retain their incoming hashes.
The source receipt and every frozen biological/model/estimand/support/
generating-value/schedule/seed/threshold/scenario/publication invariant are
unchanged.

## RED Evidence

Behavior-specific tests were added to the assigned T3A-011 and T3D-014 nodes
before source implementation. The current code then failed both nodes:

```text
2 failed in 772.46s
exit=1
JUnit SHA-256=b2834e2b3aa84a08ee2e4512857688952187322529a6be213914e5d72057b81b
```

T3A-011 showed that 1,045 arrival score-cell histories reached the injected
optimizer and returned a converged joint fit. T3D-014 showed that predictive
records lacked effort, equal-cardinality quality and time-band swaps retained
the same digest, and no production schedule adapter existed. The assigned
T3A-011 node also contains the 1x3/2x3 impossible-rank probes and the complete
bundle optimizer/design contradiction required by the rereview.

Evidence file:

- `.superpowers/sdd/integrated-amendment-final-repair-8-red.xml`

## I1 - Issued Analyst Fit Frame

Added module-issued immutable `AnalystFitFrame` authority derived only from
exact registered canonical cell IDs. The joint fitter now requires this frame
and checks the complete ordered history ID tuple before potential-design
construction, batching, objective evaluation, or optimization.

`JointFitResult` carries the issued frame, exact cell count, and cell digest.
Typed result validation ties potential and plug-in row counts to
`frame.cell_count * 20`. Persisted joint design frame fields are obtained only
through a validated `JointFitResult`; oracle-only and closed-form applicability
use the same module issuer directly.

For arrival this fixes the accepted surface at exactly:

```text
fit cells=4180
score cells=1045
fit design rows=83600
fit/score intersection=0
fit/score union=5225
```

Score histories, a 5,225-cell substitution, fit/score swaps, wrong count or
digest, and 104,500-row arrival evidence stop before optimization or reduction.
Other scenarios continue to use their authoritative 5,225- or 1,306-cell
frames without changing model or schedule authority.

## I2 - Mathematical Design Algebra

The authoritative in-memory and persisted rule is now:

```text
0 <= rank <= min(n_rows,n_columns)
pass requires n_rows >= n_columns
pass requires rank == n_columns
pass requires finite 1 <= condition < 1e8
```

Potential, plug-in, and oracle constructors reject 1x3/rank3 and 2x3/rank3.
Each 3x3/rank3 control remains valid. Joint and process result constructors
revalidate typed diagnostics, so forged dimensions, rank/pass, condition/pass,
NaN, nonfinite, or failure-nullability states cannot authorize a result.

## I3 - Typed Failure Transitions

Added nine frozen fit failure classes and one explicit transition table:

```text
preflight_or_input_failure        -> in-memory only; not persistable
potential_rank_gate_failure       -> potential rank failure; downstream N/A
potential_condition_gate_failure  -> potential condition failure; downstream N/A
optimizer_or_nonfinite_failure    -> passing potential; rank-zero joint/process failure
plugin_rank_gate_failure          -> matching evaluated plug-in rank failure
plugin_condition_gate_failure     -> matching evaluated plug-in condition failure
oracle_rank_gate_failure          -> matching evaluated oracle rank failure
oracle_condition_gate_failure     -> matching evaluated oracle condition failure
equal_rate_noninterior_failure    -> potential pass; no downstream design
```

Potential failure forbids optimizer-result fields. Plug-in gate failure
requires a successful optimizer result. Optimizer/nonfinite failure requires
the exact rank-zero `joint_fit_failed_or_nonfinite` or
`process_oracle_fit_failed_or_nonfinite` diagnostic. Evaluated rank/condition
diagnostics require their matching gate class. Observation optimizer and
equal-rate potential-only applicability are explicit.

The normalized fit/design artifact is now v3 with an exact 36-column header
including `fit_failure_class`. Every persistable transition is exercised using
the complete 990-fit/1,695-design bundle before reduction. The rereview's
optimizer-failure plus evaluated plug-in-rank contradiction is rejected before
control or recommendation construction.

## I4 - Canonical Predictive Opportunity Object

Added a module-issued `PredictiveOpportunityFrameEvidence` and production
adapter from the exact canonical `ScheduledOpportunity` tuple. The adapter
rejects schedule size, identity, time, effort, or covariate differences.

One canonical ASCII serialization covers every opportunity in cell/time order:

```text
cell_id
time
float.hex(effort)
quality-stratum label
time-band label
keyed keep identity
keep/drop state
```

The opportunity digest covers all semantic fields, including dropped rows.
Informative dropout additionally hashes keyed keep states in canonical order,
not positional bits. Sample sizes and all 27 observed metric cells are derived
from the same retained typed opportunities consumed by metric calculation. The
three metrics in each stratum therefore share exactly one reconstructed `n`.

Tests reject, before summary or recommendation:

- equal-cardinality q1/q2 membership swaps;
- equal-cardinality early/late membership swaps;
- exact effort mutation in the production schedule adapter;
- missing or metric-specific sample sizes;
- opportunity count/digest and fit/score-frame mutations; and
- equal-cardinality keyed keep/drop swaps and mask-digest mutation.

Immutable non-dropout opportunity tuples and canonical serialization bodies are
shared across replicates. This preserves the exact semantic contract without
inflating the complete fixture. The exact 22-artifact registry and existing
20-column predictive artifact are retained; count/digest/mask evidence remains
inside that existing artifact.

## Proposal And Authority Text

Goal and authoritative spec were amended identically from `## Objective`.
They now state the issued fit-frame lifecycle, mathematical rank bound, v3
36-column fit-failure schema, explicit transition table, production predictive
adapter, complete semantic serialization, and retained-object metric algebra.

The proposal now fully supersedes both its original 23-column/five-part and
intermediate 35-column behavior. T3A-005 retains its assigned name and exact
manifest position while binding the v3 36-column behavior. T3A-011 and T3D-014
describe their expanded repair-8 duties.

## Changed Files

Authoritative and implementation files changed by this repair:

- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`
- `spec/synth_medium_latent_response_observation_recovery_gate.md`
- `src/spatext/synth/medium/latent_response_observation_recovery.py`
- `tests/test_synth_medium_latent_response_observation_recovery.py`
- `.superpowers/sdd/integrated-contract-amendment-proposal.md`
- `.superpowers/sdd/integrated-amendment-final-repair-8-report.md`

Ignored validation evidence created:

- `.superpowers/sdd/integrated-amendment-final-repair-8-red.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-8-green-98.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-8-green-full.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-8-green-upstream.xml`
- `.superpowers/sdd/integrated-amendment-final-repair-8-green-gitterminal.xml`

Plan, Runbook, source receipt, dependency files, observation kernel, and all
other pre-existing files were not changed by this repair.

## Validation

Focused and complete Goal runs used `--no-cov`, because the repository-wide
coverage threshold is not meaningful for isolated selectors and would make an
otherwise green focused run nonzero.

| Validation | Result | Evidence SHA-256 |
| --- | --- | --- |
| Behavior-specific RED | `2 failed in 772.46s` | `b2834e2b3aa84a08ee2e4512857688952187322529a6be213914e5d72057b81b` |
| Exact literal 98-name manifest | `98 passed in 817.48s` | `7a877b3bb1cc0c6ee5607e4e8da452e04161638c3d0d3c22db511609cbc699f7` |
| Complete Goal 023 test file | `297 passed in 818.38s` | `07c2e2a6f170542f9877974dc0bf3b30caf3f94708a9b1bca21f680768166100` |
| Relevant upstream regressions | `69 passed in 49.89s` | `cd244c3cb11c82fa7d3000069ef7ac271ced05339afb4c39343d5bf7a1e826c6` |
| Real worktree/terminal integration | `2 passed in 1.59s` | `72b3e11634601d45b7fe40924c7e91999915c53923a28ffc6a454dd7489e9168` |

Static and structural evidence:

```text
Ruff format: 85 files already formatted
Ruff check: All checks passed!
mypy --no-incremental src tests: Success, 59 source files
git diff --check: pass
proposal/manifest/AST: 98/98/98 exact, unique, ordered
Runbook Bash parser: 18 blocks, 0 failures
Runbook/source command registry: 12/12 exact and ordered
Goal/spec Objective identity: 156188 bytes, exact
Goal/spec Objective SHA-256: 756b9edc86b1bded55714a891c0ab4669624fb22415685b01c3894610c3bec52
artifact registry: exactly 22 unique ordered paths
fit evidence header/failure classes: 36/9
alignment frames: 4180/1045, intersection 0, union 5225
source receipt and derived source identity: exact
post-append Log chain: 21/21 hashes, 12/12 byte bindings, 21/21 line bindings
branch/HEAD/base: pinned and equal
Git index: empty
canonical artifacts/config/receipts/production CLI: absent
```

Complete fixture evidence:

```text
fit results/design rows = 990/1695
recovery/profile/coverage = 2340/11700/105
latent/predictive/predictive-summary groups = 552/504/23
control rows = 18
local gates = 11 pass
recommendation rank/class = 4 / latent_response_observation_gate_passed
recommendation/verification passed = true/true
```

## Log Child

Exactly one repair child was appended:

```text
record_type=integrated_amendment_final_rereview_8_repair_v1
parent_line_count=3282
parent_byte_count=165543
parent_sha256=02f94a646d75557afe92f944fc82eb8869d452c28a7a42d94fdc044c820cc6a3
final_line_count=3423
final_byte_count=173175
final_sha256=4a1c74c48180ce3f91075297373131e27941da5c2f9508a401da1e178f334075
```

All review fields are `PENDING`. Task 3, RNG, vector/payload, simulation,
benchmark, calibration, artifact/config/receipt, freeze, holdout, staging,
commit, push, and publication authorities are `BLOCKED`.

## Final Tuple Hashes

| Surface | SHA-256 |
| --- | --- |
| Goal | `076ad8cc29dc08837a985eb169be3ee0113ef1d66ebdcf250b766bb20f98089b` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb` |
| authoritative spec | `153658d517b589f9e8e9ea3e04f97c2c6b8c6576baf44a081b98562f9fabd67c` |
| source | `40246f46a5fcd80ddae55b0739dde8104b10dc7e2508400f7ee4793c62bea8b7` |
| tests | `44eaab1b5be36f9743ae397f0dd13915cd1c12c11107135b4b9f0f145b539062` |
| proposal | `89a90783c33d1c571537876fa8d5263d3d8fc61cc0c3b22c407f3a9c4a772e4f` |
| source receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |
| derived source identity | `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0` |
| rereview 8 | `c85fe1cca10f3dd31145bbd4354484ad3e5e933a3b9fe2df8736c792c770a367` |
| final Log | `4a1c74c48180ce3f91075297373131e27941da5c2f9508a401da1e178f334075` |

Goal/spec Objective body:

```text
bytes=156188
sha256=756b9edc86b1bded55714a891c0ab4669624fb22415685b01c3894610c3bec52
identical=true
```

## Concerns And Stop Rule

No implementation or validation concern remains in this repair scope.
Independent scientific, statistical, executor-readiness, artifact/schema,
code, provenance/freeze, and max rereview dispositions are intentionally still
pending. This report and the green fixture are repair evidence, not acceptance.

Stop here. Do not authorize Task 3 or any stochastic/irreversible phase until a
fresh hash-specific independent max rereview of this exact tuple returns zero
Critical and zero Important findings.
