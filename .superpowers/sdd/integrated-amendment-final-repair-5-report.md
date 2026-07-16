# Goal 023 Integrated Amendment Final Rereview 5 Repair Report

Date: `2026-07-12`
Profile: `sol_high_specialist`
Status: `REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW`
Acceptance: `PENDING`
Task 3 and every stochastic or irreversible phase: `BLOCKED`

## Scope And Boundary

This repair resolves Important I1-I4 and all ten correction steps in
`integrated-amendment-final-rereview-5.md`. It is deterministic
fixture-validator and authority work only.

Tracked-path content changed:

1. `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md`
2. `spec/synth_medium_latent_response_observation_recovery_gate.md`
3. `src/spatext/synth/medium/latent_response_observation_recovery.py`
4. `tests/test_synth_medium_latent_response_observation_recovery.py`
5. `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md`

Ignored evidence written under `.superpowers/sdd/`:

- `integrated-amendment-final-repair-5-red.xml`
- `integrated-amendment-final-repair-5-red-2.xml`
- `integrated-amendment-final-repair-5-red-predictive.xml`
- `integrated-amendment-final-repair-5-green-98.xml`
- `integrated-amendment-final-repair-5-green-98-final.xml`
- `integrated-amendment-final-repair-5-green-full-goal.xml`
- `integrated-amendment-final-repair-5-green-full-goal-final.xml`
- `integrated-amendment-final-repair-5-green-upstream.xml`
- `integrated-amendment-final-repair-5-green-upstream-final.xml`
- `integrated-amendment-final-repair-5-green-git-terminal.xml`
- `integrated-amendment-final-repair-5-report.md`

`Runbook.md`, `Plan.md`, the accepted source receipt, `pyproject.toml`,
`uv.lock`, `src/spatext/observe.py`, `tests/test_observe.py`, dependencies,
lock state, and all other tracked paths were not edited by this repair.
Pre-existing user/orchestrator changes in those paths were preserved.

## Genuine RED Evidence

The assigned existing manifest nodes were strengthened before production
repair. The first exploratory XML contained a test-data arithmetic defect and
is retained for audit but is not claimed as behavioral RED.

The corrected six-node run in
`integrated-amendment-final-repair-5-red-2.xml` reported `6 failed`, exit 1.
Five failures directly reached their target counterexamples:

| Node | Observed RED |
| --- | --- |
| T3A-011 | `contradictory recovery and profile evidence was accepted` |
| T3L-020 | `invalid posterior never reached the owned evaluator` |
| T3D-013 | caller-selected control/scenario/final evidence did not raise |
| T3R-017 | availability and forced-warning precedence returned the wrong canonical reason |
| T3S-001 | impossible runtime evidence did not raise |

The T3D-014 row in that run stopped on a fixture-algebra precondition and is
not counted as predictive RED. After correcting only that test fixture, the
isolated run in `integrated-amendment-final-repair-5-red-predictive.xml`
reported `1 failed`: complete finite evidence with `abs(Stouffer Z) > 3` was
accepted without a warning or failed gate.

Two direct deterministic probes completed the remaining behavior-specific RED:

```text
AssertionError: finite Holm-adjusted p below 0.01 was accepted without warning
AssertionError: verification self-certified false checks, empty manifest details, and a top recommendation
```

Thus the genuine RED set covers profile/recovery contradiction, fixture
side-effect hiding, caller-selected controls/final recommendation, finite high
Stouffer, finite low Holm, reducer precedence, impossible runtime, and
self-certified verification. No RED depended on a missing import, future
artifact, production payload, or stochastic execution.

## Finding Dispositions

### I1: Predictive Warning

`predictive_warning_required()` now implements the exact union:

```text
incomplete/nonfinite/failed fit
OR Holm-adjusted p < 0.01
OR abs(Stouffer Z) > 3
```

The predictive gate is derived only from that recomputed warning. Tests cover
finite high-Stouffer and low-Holm evidence, exact non-warning boundaries at
`3.0` and `0.01`, and the immediately adjacent open-boundary values.

Disposition: `REPAIRED_PENDING_INDEPENDENT_MAX_REREVIEW`.

### I2: Complete Science Reconciliation

One typed `validate_science_bundle()` path now consumes fit, recovery, profile,
coverage, latent, predictive-replicate, predictive-summary, and control tables.
It derives the complete scenario/split/variant frames and rejects every
missing, extra, duplicate, orphan, or foreign identity group before a gate is
computed.

Every required successful fit/parameter has a complete ordered profile group.
The frozen LR crossing algorithm derives interval endpoints, support-side
openness, and `profile_two_sided`; recovery estimate error, interval width,
coverage, row gate, and coverage summary are recomputed from the reconciled
fit/profile/truth evidence. Failed fit states remain explicitly typed and do
not masquerade as successful profile evidence.

All 18 control rows are reconstructed rather than trusted. The reconstruction
uses complete zero-driver and arrival denominators/events, canonical alignment
correlation, equal-emission observed D and bootstrap p, availability,
scenario-specific reasons, silent-failure state, six fixed statuses, and the
declared reducer for final rank/class. The retained-observed/failed-bootstrap
state is explicit and fail-closed. No caller-selected final row is authority.

Disposition: `REPAIRED_PENDING_INDEPENDENT_MAX_REREVIEW`.

### I3: Runtime And Verification

Goal/spec and source now freeze exact benchmark task IDs, benchmark splits and
ranges, profile inclusion, predictive-reference counts, calibration and
holdout repeat counts, and the equal-bootstrap task authority. Runtime
validation reconstructs the exact 96 calibration and 536 holdout task arrays,
stable IDs/order, deterministic eight-worker LPT loads, `1.20` projections,
`1500`-second limits, and derived `passed`. Caller contradictions in any of
those fields are rejected.

Verification now validates the exact artifact-manifest detail schema and each
live represented digest. Its 15 checks are derived from validated config,
runtime, source, receipt, science, control, and artifact evidence.
Recommendation and transportability are bound to the reconstructed control
decision, and top-level `passed` is derived. A represented-file mutation after
document construction is detected from disk.

Disposition: `REPAIRED_PENDING_INDEPENDENT_MAX_REREVIEW`.

### I4: Exact 98 Behavior Matrix

The proposal inventory, `AMENDMENT_TEST_NAMES`, and top-level test AST remain
exactly 98/98/98, unique and in the same order. All 98 definitions contain an
executable assertion or rejection check. The assigned nodes T3A-011, T3L-020,
T3D-013, T3D-014, T3R-017, and T3S-001 now exercise every rereview-5
counterexample rather than shape-only or short-circuited cases.

Disposition: `REPAIRED_PENDING_INDEPENDENT_MAX_REREVIEW`.

## Ten Corrections

1. Task 3 remains blocked; no acceptance or terminal Log record was appended.
2. Predictive warning and exact open boundaries are recomputed and tested.
3. One complete science-bundle reconciler validates every table and identity frame.
4. Profile roots and recovery/coverage outputs derive from ordered profile evidence.
5. All 18 control rows and the final recommendation derive from validated evidence.
6. Runtime arrays, LPT loads, projections, limits, and pass state are executable authority.
7. Verification is a live cross-artifact validator with derived checks and recommendation.
8. Exactly 98 names/order are preserved and the under-covered nodes are strengthened.
9. The complete authorized non-generative validation ladder is green.
10. One parent-bound repair child was appended with all reviews and acceptance pending.

## GREEN Evidence

Final exact-manifest selector, built directly from the literal AST tuple:

```text
98 passed in 5.13s
JUnit: tests=98 failures=0 errors=0 time=5.093
```

Complete Goal 023 test file on the final source/test tuple:

```text
297 passed in 708.84s (0:11:48)
JUnit: tests=297 failures=0 errors=0 time=708.799
```

Relevant observation, landscape, spread-impact, observation-design, and
recoverability-design upstream regressions:

```text
69 passed in 45.49s
JUnit: tests=69 failures=0 errors=0 time=45.445
```

Real temporary Git repository integration for distinct worktrees,
write-tree/commit/fast-forward/push-state, and exact-once terminal handling:

```text
2 passed in 1.01s
JUnit: tests=2 failures=0 errors=0 time=0.964
```

Static and structural ladder:

```text
Ruff format: 85 files already formatted
Ruff check: All checks passed!
mypy --no-incremental src tests: Success, 59 source files
git diff --check: pass
owned-untracked diff check: 5 files, 0 whitespace failures
Runbook Bash: 18 blocks, 0 failures
Runbook/source command registry: 12/12 exact
proposal/manifest/AST: 98/98/98 exact, unique, ordered
executable assertion nodes: 98/98
Goal/spec Objective body: 140530 bytes, byte-identical
pre-append Log chain: 17/17 parent hashes, 8/8 byte counts
post-append Log chain: 18/18 parent hashes, 9/9 byte counts
```

Independent source and frame reconstruction:

```text
landscape_sha256=53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a
arrival_sha256=5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba
source_sha256=6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0
counts=6048,5225,823,4605,4289
passable/sparse/fit/score=5225/1306/4180/1045
fit-score disjoint=true; union=5225; passable_exact=true
```

## Authority Hashes

Final authority and implementation tuple:

| Surface | SHA-256 |
| --- | --- |
| Goal | `fcc948d50f95b55ea9cc545bd56c56a3190a03f28a00130b998a67c9966d492f` |
| Plan, unchanged | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook, unchanged | `580502f69bbecf0d416722db7e22ae71c6cc7251725fcb1b7b799ee4f7085cbb` |
| authoritative spec | `d034320882b2fd69076ec9539704369c35bae107c83f531b7c2bf649a8e2e112` |
| source | `8ad0c1ea96ea73686a677cc496c3ed1a63584a6787a238b09e0d4d5d1b45a231` |
| tests | `7013ccdece7d0ddc15354b8530d636e6b2a71e227d50d58dbb17e5eff528a04e` |
| source receipt, unchanged | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |
| rereview 5 | `e8b647a66354efb321ef281302a69f8e6bb52a98a5ac1928995fc8bd8fcbb34f` |
| final Log | `d88afdf3c0bc7bad4e02023cba4c94e0458269e3daf3d85c314ac4997669c999` |

Final and RED evidence hashes:

| Evidence | SHA-256 |
| --- | --- |
| RED corrected six-node | `df24305f5d86788e42677ac7a1d489f98a3ebf6afbf3fb6f72ba57bfb5225e5b` |
| RED isolated predictive | `8ac8ba7335c5f1e7012f6c3e572136534ddd954ce46625ce0634aad09f31a004` |
| GREEN exact 98 final | `28085723561439afd62cbd7f0737239ebef57302705a025b1cedfbc8acdc8075` |
| GREEN full Goal final | `df91be8683c2aab6b23ca3777317b7ed305d754f45b1d608e02177a43eaa5c95` |
| GREEN upstream final | `86918ea694526a88a13006a833f30bcbb434b92d8182957b673ac0d43957c3e4` |
| GREEN Git/terminal | `bb26d0b4bcedc3a3b0cce447c0fd9d0d6da8b5908e163ff60998b3a5ebbd03ca` |

Intermediate retained XML hashes are:

```text
red exploratory       ea3385dac7c66ff5eeb2b1023d4d5b528274a83cbb6e376b8991096e3743f23e
green 98 pre-final     500cab9445e42cfa787959d6994b0009e98cf7f4fdd3bc0723c0040d649f7e88
green full pre-final   7059877c0e9a89ea52dc02bcd710b15b987b585d292a4eaea38086065fb18c3c
green upstream pre-final 015262077d63706c37b850d3f695acc573c1685d0c09219fd41f2d1c6491707d
```

## Log Parent And Child

Live parent captured immediately before append:

```text
lines=2902
bytes=144896
sha256=9b7e9843f0c67cb445b6b90d158fabbf6ce3005f6c487d96e09e9321bbc5d381
```

Appended child:

```text
record_type=integrated_amendment_final_rereview_5_repair_v1
status=REPAIR_COMPLETE_PENDING_INDEPENDENT_MAX_REREVIEW
acceptance=PENDING
all seven review dispositions=PENDING
Task 3 and all stochastic/irreversible authorities=BLOCKED
```

New Log shape:

```text
lines=3024
bytes=151572
sha256=d88afdf3c0bc7bad4e02023cba4c94e0458269e3daf3d85c314ac4997669c999
chain=18/18 parent hashes, 9/9 declared byte counts
parent prefix SHA-256 reproduced exactly
```

No acceptance, terminal attestation, or Task 3 authorization was appended.

## Git And No Exposure

Final live repository identity before report creation:

```text
branch=codex/spatext-goal023-latent-response-observation-gate
HEAD=53462d0365babf2c8070714a930f69b4071af276
origin/main=53462d0365babf2c8070714a930f69b4071af276
git_common_dir=/Users/bwbrook/papers/spatext/.git
index=empty
remote Goal 023 branch=absent
```

The worktree remains intentionally dirty with the supplied Goal 023 packet and
pre-existing user/orchestrator changes:

```text
 M pyproject.toml
 M uv.lock
?? docs/goals/023-synth-medium-latent-response-observation-recovery-gate/
?? spec/synth_medium_latent_response_observation_recovery_gate.md
?? src/spatext/observe.py
?? src/spatext/synth/medium/latent_response_observation_recovery.py
?? tests/test_observe.py
?? tests/test_synth_medium_latent_response_observation_recovery.py
```

No file is staged. No real-project commit or push occurred. The canonical
artifact directory, recovery config, preholdout receipt, holdout receipt,
production Goal 023 CLI, and remote Goal branch are absent. Temporary Git
repository actions occurred only in pytest-owned temporary repositories and
were removed by test cleanup.

No Task 3 production CLI or live scenario execution, production RNG object,
vector, or payload, simulation, benchmark, calibration, canonical artifact,
config, or receipt, freeze, holdout, real-project staging, commit, push,
publication, cleanup, reset, restore, or deletion occurred. A fresh
hash-specific independent `sol_max_auditor` rereview with no Critical or
Important finding remains mandatory before Task 3 can be authorized.
