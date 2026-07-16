# Goal 023 Integrated Amendment Final Rereview 8

Date: 2026-07-12  
Role: fresh independent adversarial `sol_max_auditor` review  
Decision surface: exact current pre-simulation tuple and Task 3 fixture-only
authorization

## Verdict

**NOT SUPPORTED**  
**TASK 3 FIXTURE-ONLY NOT AUTHORIZED**

The operational claim is that the exact current Goal 023 tuple has no Critical
or Important gap and may therefore authorize Task 3 fixture-only
implementation. That claim requires all decisive design and predictive evidence
to be bound to the data frame that produced it, all typed design states to be
mathematically possible, and every persisted fit/design contradiction to stop
before reduction.

The assigned 98-node manifest is green and the complete deterministic fixture
reaches all eleven local passes, rank 4, and verification true. Fresh
counterexamples nevertheless bypass four claimed invariants. This review finds
**zero Critical, four Important, and zero Minor** findings. A green assigned
manifest is therefore regression evidence, not authorization evidence.

No production CLI, RNG, vector, payload, scenario run, benchmark, calibration,
canonical artifact/config/receipt, freeze, holdout, staging, commit, push, or
publication was performed.

For concise citations below:

- `Goal.md` is
  `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`;
- `source.py` is
  `src/spatext/synth/medium/latent_response_observation_recovery.py`; and
- `tests.py` is
  `tests/test_synth_medium_latent_response_observation_recovery.py`.

## Findings

### Critical

None.

### Important I1 - Arrival fit-frame authority is disconnected from estimator acceptance

**Evidence.** `fit_joint_analyst_histories` accepts only a tuple of generic
histories and has no scenario, frame role, expected cell identity, or
module-issued frame token (`source.py:3127-3206`). Its canonicalization checks
only exact history type and increasing cell IDs (`source.py:3878-3890`). The
later arrival validator compares caller-supplied canonical fit/score ID tuples
separately from fit rows (`source.py:7067-7108`), while persisted design
validation compares caller-populated count/digest fields to constants
(`source.py:6725-6743`). No value binds the histories used by the objective and
plug-in diagnostic to those persisted fields.

**Fresh counterexample.** I supplied analyst histories for exactly the 1,045
score cells, with a deterministic injected successful optimizer only. The real
potential and real plug-in calculations both returned rank 3 over 20,900 rows,
and `fit_joint_analyst_histories` returned `converged=true`:

```text
score_cell_count=1045
potential_rows=20900
plugin_rows=20900
plugin_rank=3
plugin_passed=true
converged=true
```

This is the frame explicitly prohibited from fit acceptance by
`Goal.md:1046-1051,1797-1802`. The assigned test supplies the expected ID tuples
to a separate validator and mutates declared row/digest fields
(`tests.py:4686-4750`); it does not connect those IDs to estimator histories.

**Consequence.** Task 3 can accidentally fit arrival on score histories. Honest
persistence of 20,900 rows would later fail, but the current fixture pattern
populates expected count/digest constants independently of any fit object
(`tests.py:4052-4097`). The claimed end-to-end guarantee that score histories
cannot enter fit acceptance is therefore false.

**Required closure.** Introduce a module-issued typed analyst fit frame derived
from the exact canonical cell IDs. Require it in the joint fitter before the
objective, carry its count and digest through `JointFitResult`, and derive
persisted design fields only from that issued result. Add a one-fact test that
passes the 1,045 score histories to the arrival fitter and proves rejection
before optimization. Reseal Goal/spec/source/tests/Log and rereview.

### Important I2 - The typed design algebra accepts an impossible 1x3 rank-3 matrix

**Evidence.** The new validator requires positive dimensions but limits rank
only by `n_columns` (`source.py:351-381`; mirrored in `Goal.md:2843-2852`). It
does not enforce the mathematical invariant
`rank <= min(n_rows,n_columns)`. Joint constructors then treat the resulting
`passed=true` diagnostic as decisive (`source.py:734-790`). Assigned forged
states include `n_rows=0` but not a positive row dimension smaller than rank
(`tests.py:5275-5347`).

**Fresh counterexample.** Two exact `DesignDiagnostic` objects with
`n_rows=1,n_columns=3,rank=3,condition_number=1,passed=true` were accepted, and
they authorized a converged `JointFitResult`.

**Consequence.** A mathematically impossible diagnostic can become accepted
typed fit evidence. This is a defect in the amended authority algebra itself,
not only an implementation mismatch, and defeats the stated forged-state
defence.

**Required closure.** Amend Goal/spec and code so rank is an exact integer in
`0..min(n_rows,n_columns)` and pass additionally requires
`n_rows >= n_columns`. Add potential, plug-in, and oracle constructor probes for
`1x3/rank3`, `2x3/rank3`, and valid `3x3/rank3`. Reseal and rereview.

### Important I3 - Optimizer-failure and design-failure transitions are not distinguished

**Evidence.** A failed fit accepts any nonempty `failure_code`
(`source.py:6881-6911`). Once potential passes, the state machine permits any
failed joint fit to carry either `joint_fit_failed_or_nonfinite` rank zero or an
evaluated `rank_deficient`/`condition_limit_failed` plug-in
(`source.py:7012-7029`). It never reconciles the fit failure code to the
downstream transition required by `Goal.md:1812-1823,2854-2859`.

**Fresh counterexample.** In the complete 990-fit/1,695-design fixture, I
changed one ordered bootstrap fit to
`failure_code=ordered_bootstrap_fit_failed` while retaining an evaluated plug-in
with `rank=2,failure_code=rank_deficient`. The complete science-bundle validator
accepted the contradiction, constructed the equal-emission control, and reduced
it to final rank 1:

```text
contradictory_bundle_accepted=true
fit_failure_code=ordered_bootstrap_fit_failed
plugin_rank=2
plugin_failure_code=rank_deficient
equal_gate=fail
final_rank=1
```

The conservative rank does not cure the provenance contradiction: the contract
requires rejection before any control or recommendation reduction.

**Consequence.** Persisted evidence can claim that optimization failed and that
a post-fit plug-in matrix was evaluated. Failure cause, applicability, and audit
provenance are not trustworthy even though this example reduces conservatively.

**Required closure.** Freeze typed fit failure classes and an explicit
transition table. Optimizer/nonfinite failure must require rank-zero
`joint_fit_failed_or_nonfinite` or
`process_oracle_fit_failed_or_nonfinite`; a rank/condition diagnostic may occur
only with the matching design-gate fit failure. Potential failure must also
forbid optimizer-result fields. Exercise every transition through the complete
bundle, not only the row-level helper. Reseal and rereview.

### Important I4 - Predictive digests do not authenticate effort or stratum membership

**Evidence.** The retained predictive records carry
`(cell_id,time,quintile,time_band)` (`source.py:7510-7537`), but the digest loop
hashes only `cell_id` and `time` and explicitly discards quintile/time-band
labels (`source.py:7552-7593`). Effort is absent from both those records and the
20-column predictive artifact schema (`source.py:5939-5960`). Validation then
compares rows only with this parallel fixture ledger (`source.py:9169-9187`).
This is weaker than the exact cell/time/effort/dropout frame required by
`Goal.md:1485-1503,2014-2051`.

**Fresh counterexamples.** Swapping every canonical `q1` and `q2` membership in
the dense holdout frame changed all memberships but produced an exactly equal
`PredictiveOpportunityFrameEvidence`: same SHA-256 and the same counts
`21945/21945`. Baseline rows still validated after the swap.

```text
all_q1_q2_memberships_swapped=true
frame_evidence_identical=true
digest_equal=true
stratum_counts_equal=true
baseline_rows_accepted_after_swap=true
```

Separately, source inspection and execution confirmed `effort_in_schema=false`
and `effort_hashed=false`; a 27-row structured frame validates without carrying
any effort identity. These are semantic serialization collisions, not attacks
on SHA-256.

**Consequence.** Predictive metrics may be computed under swapped quality
strata or altered effort while retaining the exact accepted sample sizes,
digest, summaries, and recommendation path. The fixture-to-production handoff
also has no way to prove that the realized production opportunity frame is the
one summarized.

**Required closure.** Define one canonical opportunity serialization containing
at least cell ID, time, exact effort representation, quality-stratum label,
time-band label, and keyed keep/dropout state in canonical order. Derive both
sample sizes and digest from the actual retained opportunity object consumed by
metric calculation, not a parallel fixture ledger. Add equal-cardinality
`q1/q2` and `early/late` swaps, one effort mutation, one keyed mask mutation,
and a production-adapter test; each must fail before summary/recommendation.
Reseal and rereview.

### Minor

None.

## Strongest Supporting Evidence

The supplied tuple reproduced exactly:

| Surface | SHA-256 |
| --- | --- |
| Goal | `a99909b344cbf8f342a443112d06b38e30ec10e514f6d9e4966cb4c0ab5cf759` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb` |
| authoritative spec | `b22d796375ce507317a35a7e6156dcdb138c182f4cb9a35f7dfc3e103ef6dffc` |
| source | `973ed93a7165e78ba267f0d3a87b24065a7448b70aed713b22bf1558efd81b0b` |
| tests | `bc6827f5fce8ef73d7776771d0eeaf6abf4d82ef3c1aa5f70d023c1020cfc2b4` |
| proposal | `7a2fea9874f69aeef07d074c9e217b62aabc7507a8e9ad728e5d707963716b97` |
| source receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |
| Log | `02f94a646d75557afe92f944fc82eb8869d452c28a7a42d94fdc044c820cc6a3` |

Goal and spec are byte-identical from `## Objective`: `151187` bytes, SHA-256
`815c0109f13b846b5a66cb00184384559ba7299e6c91af70d90a4d09248e065c`.

The exact literal manifest completed with **98 passed in 793.04s**. Independent
proposal/manifest/AST extraction was `98/98/98`, unique and ordered. The complete
fixture independently reconstructed:

```text
fit results/design rows = 990/1695
recovery/profile/coverage = 2340/11700/105
latent/predictive/predictive-summary groups = 552/504/23
control rows = 18
local gates = 11 pass
rank/class = 4 / latent_response_observation_gate_passed
verification passed = true (covered by the exact manifest)
```

Additional independent checks passed:

- source receipt landscape and arrival digests reproduced from canonical source
  APIs, with derived source identity
  `6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0`;
- arrival authority is exactly 4,180 fit cells, 1,045 score cells, intersection
  zero, union 5,225, and 83,600 declared decisive rows;
- artifact registry is exactly 22 unique ordered paths;
- all 18 Runbook Bash blocks pass `bash -n`;
- Runbook/source closed command registry is exactly `12/12` and ordered;
- Log chain reproduces `20/20` parent SHA-256 values and `11/11` declared parent
  byte counts;
- Ruff format/check passed for source and tests;
- mypy `--no-incremental` passed for source and tests;
- `git diff --check` passed and the Git index is empty.

An initial independent source serializer aborted before digesting because 823
water rows use `None` arrival rather than a numeric nonfinite value. A direct
type inventory identified `5225 float / 823 NoneType`; the corrected
contract-faithful serializer then reproduced both receipt digests. This was an
audit-harness error, not a repository finding.

No broad 297-node or upstream suite was rerun. The exact assigned 98 plus the
bounded static checks are sufficient regression evidence, and the fresh
deterministic counterexamples already decide authorization.

## Git And Exposure State

Branch, HEAD, and base remain
`codex/spatext-goal023-latent-response-observation-gate`,
`53462d0365babf2c8070714a930f69b4071af276`, and the same `origin/main`.
The index is empty. The remote Goal 023 branch is absent. The canonical artifact
directory, production CLI, preholdout receipt, and holdout receipt are absent.
All tests and probes used deterministic in-process objects or disposable paths
under `/private/tmp`; no tracked authority byte was changed.

This report is the only file written by this rereview. It is ignored by Git.

## Residual Uncertainty And Stop Rule

The four findings are demonstrated acceptance counterexamples, not hypothetical
coverage preferences. Close all four on one resealed authority tuple and repeat
a fresh hash-specific audit. Until that audit returns zero Critical and zero
Important findings, Task 3 fixture-only implementation remains blocked. Even a
future supported disposition would not authorize production RNG, simulation,
benchmark, calibration, canonical artifacts/config/receipts, freeze, holdout,
staging, commit, push, exposure, or publication.
