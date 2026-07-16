# Goal 023 Task 2b Max-Audit Repair Report

## Status

`REPAIRED_GREEN_PENDING_INDEPENDENT_REREVIEW`

Both Important implementation findings in
`.superpowers/sdd/task-2b-max-audit.md` were repaired under the exact authority
of `.superpowers/sdd/task-2b-audit-fix-brief.md`. Self-review found no remaining
Critical or Important repair finding. Task 2b is not accepted by this report:
the required independent rereview remains `PENDING`.

Bound authority and input state were verified before editing:

- authoritative spec SHA-256:
  `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d`;
- repair brief SHA-256:
  `0f3746da086237bc2e423e012f3493caf3bbb1671758d2263ba151deac8507bf`;
- max-audit SHA-256:
  `e9117f1286ef378f95bed056afd3dd4c11487d79c6b2637196e3c38974bd5309`;
- input source SHA-256:
  `d732977d6bb6ae966d4e8575e4ad242d0054d826414ba00846d2e1e0b827bfa3`;
- input tests SHA-256:
  `3d92ab723aed2a14b27aaebb6080917999ed9a0bf7a2de60aed65e90222b2ef9`;
- Log parent: `2254` lines, SHA-256
  `a59540d9bcbca47b8277499a596d16d8e3e7be2f592ce1ab848c0070f4d19094`.

## Repairs

### 1. Preflight and analyst/truth firewall closure

- `NineAuditPreflightResult` is now factory-issued only by
  `run_nine_audit_preflight`. Direct construction is rejected, and every
  deployable adapter revalidates both issuance and the complete immutable
  nine-audit frontier. Canonical diagnostic row counts are also exact:
  dense `219450`, structured `114950`, and sparse `15672`.
- Added preflight-gated, exact-typed production fits:
  `fit_process_oracle_outcomes`, `fit_observation_oracle_histories`, and
  `fit_joint_analyst_histories`.
- Added corresponding typed profile adapters:
  `profile_process_oracle_outcomes`,
  `profile_observation_oracle_histories`, and
  `profile_joint_analyst_histories`.
- Process-oracle fitting derives and gates its distinct
  `process_oracle_truth_at_risk` design from exact
  `ProcessOracleOutcome` values. Observation-oracle fitting accepts only exact
  `ObservationOracleHistory` values. Joint fitting and profiling accept only
  exact `AnalystHistory` tuples and construct their objectives internally from
  `AnalystBatch` with `batched_joint_log_likelihood`.
- The callback-taking optimizer and profile engines were renamed private:
  `_run_optimizer_start`, `_run_multistart_optimization`, and
  `_profile_parameter`. No deployable public route accepts an objective,
  callback, evaluator, truth object, scenario, seed, split, or replicate field.
- Adversarial tests cover evaluator objects, tuple subclasses/invalid typed
  values, truth-bearing closures, process-oracle data presented to the joint
  route, unexpected objective callbacks, and fabricated exact preflight
  instances. All fail closed before input iteration or optimization.

### 2. Canonical finite predator arrivals

- `_canonical_arrival_time` now preserves every nonnegative finite arrival;
  it no longer treats the model horizon as the arrival-value domain.
- The canonical audit fixture now passes Goal 018 source values literally,
  without converting post-horizon arrivals to `None`.
- Source-bound tests establish `5225/5225` finite values, exactly `620` above
  `120`, and maximum `205.910318172679`. The latest arrival produces an exactly
  zero 20-interval driver inside the `0..120` horizon.
- The permutation/correlation-facing regression retains all `5225` finite
  pairs and the complete arrival multiset.

## TDD evidence

### Firewall/preflight cycle

With source still byte-identical to the audited input, the focused command for
factory-only construction, typed production surfaces, and fabricated-preflight
blocking failed `3/3` in `0.48s`. Failures were the expected old behaviors:
public construction remained possible, oracle adapters were absent, and the
callback primitives were still public. The identical command passed `3/3` in
`0.32s` after the minimal source change. The private optimizer/profile
mechanics then passed `18` focused regressions in `0.56s`.

### Arrival cycle

Before changing arrival validation, the two source-bound tests errored `2/2`
in `0.80s` at the first source value above the old cap,
`120.576984839346`. After removing only the upper-horizon rejection, the
identical command passed `2/2` in `0.61s`.

## Numerical and validation evidence

- Broad fast latent-recovery run on final formatted bytes:
  `194 passed, 5 deselected in 2.45s`.
- Observation plus relevant upstream synth-medium regressions: `79` tests,
  exit `0`, approximately `26.3s`.
- Full final latent-recovery file, including the module-scoped canonical
  9-by-16 inverse preflight and genuine-preflight adapter tests:
  `199 passed in 772.21s` (`real 772.46s`).
- Exact recovery counts remained dense `A/B/C = 16/15/2`, structured
  `16/14/3`, and sparse `15/16/16`; every collision count remained zero.
- Independent raw-arrival versus prior-recode comparison across all three
  schedules and all three targets found maximum absolute differences exactly
  `0.0` for both canonical audit vectors and scaled Jacobians.
- Scalar/batched likelihood and posterior equivalence, Halton starts, literal
  L-BFGS-B behavior, adaptive profile boundaries, injected failure propagation,
  rank-failing controls, and accepted Task 2a behavior all passed in the full
  file.
- `uv run ruff format --check` and targeted `ruff check`: pass.
- `uv run mypy src tests`: pass, no issues in `59` source files.
- `git diff --check`: pass.

## Changed paths and final hashes

- `src/spatext/synth/medium/latent_response_observation_recovery.py`
  (`701dd468219737d8885a2f52ef9e4cbb8965397277f6b9d1a4f3ebbfe72bc673`)
- `tests/test_synth_medium_latent_response_observation_recovery.py`
  (`cb18204c6c78e9a0a1f049198f563b131cd3ee8d84793d1dfa94a87d6f68b6aa`)
- `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`
  (`2305` lines;
  `7a95d0ce27fb7ffa9e9ec77308659a68b243f79f986b85ecdb518d7365ebd5b6`)
- `.superpowers/sdd/task-2b-audit-fix-report.md` (ignored; this report)

The first `2254` Log lines remain byte-identical to the bound parent SHA.

## Concerns and boundary confirmation

- Independent rereview is still required; this implementation report does not
  accept Task 2b or authorize Task 3.
- Preflight authorization is intentionally an in-process capability. A copied,
  reconstructed, or deserialized record fails closed; a controller must run
  the canonical preflight in the same process before fitting/profiling.
- The pre-existing authority/provenance amendment question recorded in the
  prior checkpoint was not changed or adjudicated here.
- No Task 3 code, scenario/calibration execution, holdout payload, artifact,
  receipt, authority amendment, staging, commit, or push was created or run.
