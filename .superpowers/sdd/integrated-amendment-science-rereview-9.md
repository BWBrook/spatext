# Goal 023 Integrated Amendment Science Rereview 9

Date: 2026-07-12  
Role: independent `sol_high_specialist` scientific/statistical architecture review  
Decision surface: exact current pre-Task-3 tuple and Task 3 fixture-only authorization

## Verdict

**NOT SUPPORTED**  
**TASK 3 FIXTURE-ONLY NOT AUTHORIZED**

This review finds **zero Critical, three Important, and zero Minor** findings.
The module-issued analyst fit frame now closes the original fit/score-frame
substitution, and the nominal predictive serialization contains the required
semantic fields. However, one impossible fit transition remains accepted, the
predictive authority can be changed after issuance without changing its accepted
digest, and the complete rank-4 fixture does not consume either the production
schedule adapter or the actual predictive metric calculator.

No production CLI, RNG, vector, payload, scenario run, benchmark, calibration,
canonical artifact/config/receipt, freeze, holdout, staging, commit, push, or
publication was performed. Probes were deterministic and in-process only. This
report is the only file written and is ignored by Git.

The assigned tuple reproduced exactly:

| Surface | SHA-256 |
| --- | --- |
| Goal | `076ad8cc29dc08837a985eb169be3ee0113ef1d66ebdcf250b766bb20f98089b` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb` |
| Spec | `153658d517b589f9e8e9ea3e04f97c2c6b8c6576baf44a081b98562f9fabd67c` |
| Source | `40246f46a5fcd80ddae55b0739dde8104b10dc7e2508400f7ee4793c62bea8b7` |
| Tests | `44eaab1b5be36f9743ae397f0dd13915cd1c12c11107135b4b9f0f145b539062` |
| Proposal | `89a90783c33d1c571537876fa8d5263d3d8fc61cc0c3b22c407f3a9c4a772e4f` |
| Receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |
| Log | `4a1c74c48180ce3f91075297373131e27941da5c2f9508a401da1e178f334075` |

For citations below, `source.py` is
`src/spatext/synth/medium/latent_response_observation_recovery.py` and
`tests.py` is `tests/test_synth_medium_latent_response_observation_recovery.py`.

## Findings

### Critical

None.

### Important I1 - The persisted transition algebra accepts a logically successful optimizer as an optimizer failure

**Evidence.** A failed persisted fit may use
`optimizer_or_nonfinite_failure` with any `converged_start_count` in `0..8`.
When the count is positive, only a best-start index is required; best-two
agreement is allowed whenever at least two starts succeeded
(`source.py:7171-7213`). The fit/design state machine then checks only that the
potential design passes and the downstream diagnostic is rank zero with the
fit-failed code (`source.py:7352-7384`). It does not reconcile the optimizer
fields with the typed multistart success rule used for accepted fits: at least
six converged starts, a valid best start, and best-two agreement
(`source.py:7071-7082`).

**Fresh counterexample.** A canonical joint fit row with all eight starts
converged, best start 1, and best-two agreement true was changed to
`fit_succeeded=false`, `fit_failure_class=optimizer_or_nonfinite_failure`, with
a passing potential diagnostic and rank-zero
`joint_fit_failed_or_nonfinite` plug-in diagnostic. The exact row validator and
fit/design state machine accepted it:

```text
impossible_optimizer_transition_accepted=true
converged_start_count=8
best_start_index=1
best_two_log_likelihoods_agree=true
failure_class=optimizer_or_nonfinite_failure
```

This state cannot arise from `fit_joint_analyst_histories`: those optimizer
fields describe a converged multistart, which proceeds to a real plug-in
diagnostic rather than the rank-zero optimizer-failure sentinel
(`source.py:3383-3417`). The explicit table therefore remains wider than the
production typed state machine.

**Consequence.** Persisted evidence can claim both complete optimizer success
and optimizer/nonfinite failure. The contradiction reaches the complete
fit/design authority instead of stopping before reduction, so failure cause and
applicability remain unauthenticated.

**Required closure.** Define optimizer/nonfinite persisted substates that are
exactly image-equivalent to `MultiStartFitResult`, or require the literal failed
multistart predicates. At minimum, reject `count >= 6` with a valid best start
and best-two agreement true as optimizer failure. Exercise every permitted
optimizer-field combination against both the typed fit constructor and the
persisted complete-bundle transition.

### Important I2 - Predictive frame validation is revocable by object mutation but cached as permanent

**Evidence.** Predictive frames and their nested opportunities are frozen
dataclasses, but Python's `object.__setattr__` can still change them. The frame
validator returns immediately for any previously validated object identity
(`source.py:8161-8170`), and every issued frame is inserted into that identity
cache before it is consumed (`source.py:8277-8317`). Consequently, later calls
skip canonical schedule comparison, stratum-count reconstruction, semantic
digest reconstruction, and keyed mask reconstruction
(`source.py:8181-8228`). The metric calculator calls this cached validator and
then consumes the current nested opportunity labels (`source.py:8348-8378`).

**Fresh counterexample.** On one issued dense holdout frame, counts were keyed
so original q1 opportunities had value 1 and all others value 0. After first
validation, every nested q1/q2 label was swapped in place. The accepted digest
did not change, but the actual metric calculation consumed the changed labels:

```text
digest_unchanged=true
q1_mean_before=1.0
q1_mean_after=0.0
q2_mean_before=0.0
q2_mean_after=1.0
mutated_frame_accepted=true
```

This directly violates the Goal claim that equal-cardinality quality/time
swaps are invalid before summary and that the digest binds all 27 metric cells
(`Goal.md:2941-2945`). It also applies to effort, time band, keep identity, and
keep/drop state because all are nested mutable attributes and all semantic
rechecks are bypassed by the identity cache.

**Consequence.** A registered digest can authenticate one opportunity frame
while metrics and persisted rows consume another. The SHA-256 serialization is
complete, but it is no longer authority once validation is cached independently
of the bytes being consumed.

**Required closure.** Remove identity-only validation caching from this
scientific authority or cache an immutable canonical byte representation and
reconcile current objects to it on every consumption. A stronger design is for
the frame to retain only canonical bytes plus private immutable primitive
tuples, with metrics reconstructed from those authenticated values. Add a
post-issuance nested-field mutation matrix covering effort, both strata,
keep-key, and keep/drop state; every mutation must stop before metrics, row
emission, summary, or recommendation.

### Important I3 - The complete rank-4 fixture bypasses the production adapter and actual metric calculation

**Evidence.** The complete fixture obtains a fixture-issued opportunity frame
only to seed `failed_predictive_rows`, then overwrites all scientific predictive
values directly (`tests.py:7594-7637`). It sets observed/reference values,
standardized residuals, and PIT values algebraically; it never supplies keyed
observed counts to `predictive_metrics_from_opportunity_frame`. Across the
entire test file, the metric calculator and production schedule adapter are
called only in the isolated T3D-014 unit test (`tests.py:7792-7823`), not in the
complete rank-4 path.

The fixture is also an idealized reducer construction rather than a plausible
synthetic result: replicate estimates are overwritten to exact generating
truth (`tests.py:7307-7329`), profiles use the same fixed five-point likelihood
shape for every parameter and replicate (`tests.py:7382-7475`), and predictive
cells receive fixed residuals of zero or one with deterministic evenly spaced
PIT values (`tests.py:7611-7637`). Those choices are acceptable for a local
algebra fixture only if they are not represented as production architecture
evidence.

**Fresh counterexample.** Both production predictive functions were replaced
in-process by functions that raise immediately. The complete fixture still
constructed 13,608 predictive rows, validated, and reached rank 4:

```text
rank4_fixture_bypasses_production_adapter=true
rank4_fixture_bypasses_metric_calculation=true
recommendation_rank=4
predictive_rows=13608
```

**Consequence.** The complete acceptance fixture cannot detect a missing,
broken, or scientifically divergent fixture-to-production adapter, nor a metric
implementation that does not consume the authenticated retained opportunities.
It proves reducer reachability, not end-to-end scientific plausibility or Task 3
readiness. This contradicts the repair claim that all observed metric cells in
the complete path derive from the retained typed opportunities.

**Required closure.** Split the claims explicitly: retain the current fixture
as a reducer-totality fixture, and add a complete deterministic integration
fixture whose predictive rows are produced through the schedule adapter and
`predictive_metrics_from_opportunity_frame` from keyed counts. Reference
summaries may remain deterministic, but observed metrics, sample sizes, and
frame evidence must share that one production-shaped object path. Prove the
complete fixture fails when either adapter or metric calculator is disabled.

### Minor

None.

## Supported Architecture

The following requested surfaces survived inspection and bounded challenge:

- `fit_joint_analyst_histories` requires an exact module-issued
  `AnalystFitFrame`, canonicalizes histories, and checks the complete ordered ID
  tuple before potential design construction, batching, objective evaluation,
  or optimization (`source.py:3329-3383`, `source.py:7881-7920`).
- `JointFitResult` carries the issued frame, count, and digest and revalidates
  row count against `cell_count * 20`; persistence obtains joint design identity
  from a revalidated result (`source.py:796-930`, `source.py:7923-7950`).
- Arrival fit authority is 4,180 cells while predictive scoring uses the 1,045
  score cells; the score-frame substitution therefore stops before the
  objective on the nominal typed path.
- The mathematical design algebra now enforces
  `rank <= min(n_rows,n_columns)`, requires `n_rows >= n_columns` for pass, and
  rejects the prior 1x3/rank-3 and 2x3/rank-3 impossible diagnostics
  (`source.py:372-409`).
- Canonical predictive serialization nominally includes cell, time,
  `float.hex(effort)`, quality stratum, time band, keyed keep identity, and
  keep/drop state (`source.py:8013-8059`, `source.py:8101-8117`). The production
  adapter compares the complete canonical schedule before issuance
  (`source.py:8321-8345`). I2 concerns authority after issuance, not field
  omission or a serialization collision.

## Verification And Stop Rule

Performed only:

1. exact SHA-256 reproduction for the ten assigned tuple surfaces;
2. source/spec/test/Goal/Log/receipt and prior rereview/repair inspection;
3. one deterministic in-process optimizer-transition probe;
4. one deterministic in-process post-issuance predictive-frame mutation probe;
5. one deterministic complete-fixture dependency-substitution probe.

The 98-node manifest and full Goal/upstream suites were not rerun. Existing
repair-8 green evidence was treated as regression evidence, not independently
reproduced authorization evidence.

Task 3 fixture-only implementation remains blocked. Close I1-I3 on one resealed
tuple and repeat a fresh scientific/statistical architecture review. A future
SUPPORTED verdict would authorize only the explicitly requested next fixture
phase; it would not authorize production RNG, simulation, benchmark,
calibration, canonical artifacts/config/receipts, freeze, holdout, staging,
commit, push, exposure, or publication.
