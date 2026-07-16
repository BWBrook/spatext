# Goal 023 Runbook

## 1. Preflight

```bash
cd /Users/bwbrook/.codex/worktrees/spatext/goal023
test "$(git branch --show-current)" = "codex/spatext-goal023-latent-response-observation-gate"
test "$(git rev-parse HEAD)" = "53462d0365babf2c8070714a930f69b4071af276"
git status --short --branch --untracked-files=all
uv sync --all-groups
```

Stop on changes outside the accepted footprint.

## 2. Task 0 Contract Freeze

```bash
shasum -a 256 spec/synth_medium_latent_response_observation_recovery_gate.md
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
```

Record the independently approved hashes in `Log.md`. No simulator, fitter,
calibration seed, or holdout seed may be materialised before this gate.

## 2A. Pre-Simulation Contract Amendment Seal

The original authoritative spec hash
`265a6144cc0575b7ff7b89bc1bfba4f603484aaac62352f95024d1d06c1f08dc`
is `superseded_pre_simulation`. Before Task 2, hash the replacement documents
and prove the approved source digest receipt is unchanged:

```bash
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
shasum -a 256 spec/synth_medium_latent_response_observation_recovery_gate.md
test "$(shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json | awk '{print $1}')" = "5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb"
```

Repeat the no-exposure boundary checks:

```bash
test ! -e tests/test_synth_medium_latent_response_observation_recovery.py
test ! -e src/spatext/synth/medium/latent_response_observation_recovery.py
test ! -d artifacts/synth_medium_latent_response_observation_recovery
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json
test ! -e docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
git status --short --branch --untracked-files=all
```

No seed-construction or holdout-payload command is permitted in this amendment
gate. The only RNG evidence allowed here is recomputation of the two frozen
development/calibration vectors from their literal payloads.

Task 1 must then receive a fresh red-green terminology/API polish and re-review:

```bash
uv run pytest tests/test_observe.py --no-cov
uv run ruff format --check tests/test_observe.py src/spatext/observe.py
uv run ruff check tests/test_observe.py src/spatext/observe.py
uv run mypy src tests
git diff --check
```

Record the replacement hashes and fresh Task 1 evidence in `Log.md`. Task 1
subsequently received hash-specific `ACCEPT`; it remains valid only while its
accepted source and test hashes are unchanged. Task 2 remains stopped until
independent scientific-identifiability, executor-readiness, and
provenance/freeze reviewers all return `ACCEPT` with no Critical or Important
finding. Until then label those three document reviews `PENDING`; do not create
Task 2 files, calibration, holdout, or artifacts.

## 2B. Amendment Iteration 2 Seal

The amendment-1 contract hashes are
`reviewed_not_accepted_pre_simulation`. Its provenance `ACCEPT` is
non-transferable. After iteration-2 edits, rerun the section 2A hash, receipt,
absence, status, and Task 1 commands, then record new hashes. Task 2 remains
stopped until fresh scientific-identifiability, executor-readiness, and
provenance/freeze reviews all return `ACCEPT` with no Critical or Important
finding; the separate Task 1 `ACCEPT` remains hash-specific.

The iteration-2 document audit must explicitly verify:

```bash
rg -n "log1p\(mu|numpy\.linalg\.svd|equal_emission_fixture|ORACLE-BENCHMARK-ONLY|sqrt\(W\)X" docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "log_survival|log_hazard|scipy\.special\.logsumexp|finite_diff_rel_step|joint_plugin_smoothed_at_risk" docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "PCG64DXSM|pit_randomization|1306|1045|22 of 24|Stouffer|holm_adjusted|predictive_replicate_diagnostics" docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md spec/synth_medium_latent_response_observation_recovery_gate.md
if rg -n "three Monte Carlo standard errors|three MCSE|exceeds three" docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md spec/synth_medium_latent_response_observation_recovery_gate.md; then exit 1; fi
```

Do not instantiate a seed, simulation, calibration, runtime benchmark, artifact,
or holdout payload while sealing the amendment. Label all fresh document
reviews `PENDING` until their independent dispositions are appended.

## 2C. Narrow Orchestrator Contract Correction Seal

Before resubmitting amendment iteration 2 for review, verify the generalized
SVD, dedicated sparse coverage, and predictive failed-fit rules in both Goal
and authoritative spec:

```bash
rg -n "max\(n_rows, n_columns\)|rank == n_columns|n_columns = 5|n_columns = 3" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
if rg -n "rank == 5 else infinity|max\(n_rows, 5\).*s_max" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md; then exit 1; fi
rg -n "24.*attempted holdout|Binomial\(24, 0.90\)|n = 24.*p = 0.90|dedicated exact binomial" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "failed or nonfinite fit prevents predictive|never silently omitted|failed_fit_count" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Rerun the section 2A document hashes, source-receipt equality, absence checks,
Goal/spec body diff, document hooks, and `git diff --check`. Append the new
hashes and correction disposition to `Log.md`. All fresh reviews remain
`PENDING` except the unchanged hash-specific Task 1 `ACCEPT`; Task 2 remains
stopped.

## 2D. Final Contract Review-Fix Seal

The hash-specific Task 1 `ACCEPT` remains valid only while
`tests/test_observe.py` and `src/spatext/observe.py` retain their accepted
hashes. Prior scientific and provenance `ACCEPT` decisions do not transfer to
the final replacement document hashes. Before re-review, verify:

```bash
test "$(rg -c 'RMSE <= 5e-5' \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md)" = "2"
test "$(rg -c 'RMSE <= 5e-5' \
  spec/synth_medium_latent_response_observation_recovery_gate.md)" = "2"
if rg -n "RMSE <= (1e-5|1e-8)" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md; then exit 1; fi
rg -n "5e-5, 1e-4, 2e-4|0.0025, 0.005, 0.01|16 / 15 / 2|16 / 14 / 3|15 / 16 / 16|no collision|before any estimation" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "never by bootstrap p|lambda_present.*baseline level|ordered.*contrast|cannot change.*structural labels" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n '\| `lambda_present` \| `identified` \| `not_applicable` \||\| `lambda_equal` \| `identified` \| `identified` subject|\| `lambda_quasi` \| `unidentified` \| `unidentified` \|' \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "development.*0, \.\.\., 11|calibration.*0, \.\.\., 23|holdout.*0, \.\.\., 47|before RNG construction" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "excluded from predictive|oracle-only conditional|permuted fitted model|sample_variance|n < 2|no substitute reference" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n 'ordinary even-sample median|12th and 13th|support width, `6`|48-attempt' \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "runtime_projection.json|longest-processing-time|least-loaded worker|1.20 \* max\(worker_loads\)|199 copies" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Then rerun Goal/spec body diff, document hooks, `git diff --check`, exact
document and source-receipt hashes, hash-specific nonmutating Task 1 checks,
and all Task 2/artifact/receipt/holdout absence checks. Append final hashes and
dispositions to `Log.md`. Set scientific-identifiability,
executor-readiness, and provenance/freeze re-reviews to `PENDING`; Task 2
remains stopped until all three return `ACCEPT` with no Critical or Important
finding.

## 2E. Integrated Pre-Task-3 Contract Amendment Seal

This integrated pre-Task-3 amendment changes no Goal 023 biological or
statistical model equation, estimand, natural support, generating value,
transition or emission timing convention, optimizer/profile rule, scenario ID,
schedule, effort rule, replicate count, predictive-reference count, bootstrap
count, seed payload or substream mapping, existing numerical recovery/coverage/
predictive threshold, transportability statement, or publication authority.

Do not begin this seal until Task 2b has a hash-specific independent acceptance
and releases the shared source/test/Log parent. Reproduce that parent before an
append. Append the supersession disposition from this amendment without
changing prior bytes, then apply the coordinated Goal/Plan/Runbook/spec patch.

Verify the literal correction surfaces:

```bash
rg -n "Scenario Evidence Registry And Fit Identity|fit_execution_evidence.csv|permuted_alignment|bootstrap_shared" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "transition_brier.expected_value|0.05\*\(H_x-L_x\)|ordinary_median\(B_1|recommendation-neutral" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
if rg -n "latent_time_thresholds|23/24|46/48.*latent|44/48.*latent" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md; then exit 1; fi
rg -n "structured_not_calibrated|sparse_honesty_failed|arrival_alignment_not_discriminated|continuous_abundance_silent_misspecification" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "represented_artifact_set_sha256|artifact_set_sha256|config_file_sha256|holdout_receipt_file_sha256" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
rg -n "STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION|complete.*envelope|before RNG" \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/{Goal,Plan,Runbook}.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md
```

Run Goal/spec body equivalence, document hooks, `git diff --check`, exact
document/source/test hashes, source-receipt equality, and all no-exposure
checks. Append the integrated amendment record only with live hashes. Obtain
fresh scientific, statistical, executor-readiness, artifact/schema, code, and
provenance/freeze acceptance. Task 3 remains blocked until all are clean.

## 3. TDD Evidence

For every red-green behavior, append to `Log.md`:

- behavior and test IDs;
- test-file SHA-256 before implementation;
- exact red command, failing assertion, and nonzero exit status;
- implementation paths;
- exact green command and pass count; and
- independent reviewer disposition.

Focused commands:

```bash
uv run pytest tests/test_observe.py --no-cov
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov
uv run pytest tests/test_synth_medium_landscape.py --no-cov
uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
uv run pytest tests/test_synth_medium_observation_design.py --no-cov
uv run pytest tests/test_synth_medium_recoverability_target_observation_design.py --no-cov
```

Task 2a analytic evidence must include enumeration/forward/brute-force equality
for one, two, and 20 intervals; baseline-present and post-transition timing;
coarsened and irregular schedules; firewall separation; plug-in at-risk
weights; invalid schemas; and frozen non-holdout RNG vectors. Task 2b evidence
must separately cover transforms, exact Halton starts, optimizer options,
profiles, noncollision/design audits, and injected failures. Never combine the
Task 2a RED with Task 2b implementation.

Iteration-2 tests additionally require float64/ddof0 support-extreme process
primitives, literal optimizer calls, exact SVD/rank/collision controls,
normalized plugin path weights, full RNG consumption order, fixed sparse and
alignment frames, denominator/imputation/binomial rules, equal-emission failed
bundle behavior, and predictive PIT/Holm/Stouffer schemas.

The orchestrator correction additionally requires one generalized SVD helper
test with explicit five- and three-column branches, sparse `beta_driver`
coverage tests over all 24 attempts with failed/open/missing intervals counted
false, and predictive tests proving a failed/nonfinite fit emits unavailable
rows, remains in attempted denominators, and fails the scenario gate.

The final review-fix tests must reproduce all nine dry audits before estimation
with exact target-recovery counts dense `16/15/2`, structured `16/14/3`, and
sparse `15/16/16`, no collision, and both `RMSE <= 5e-5` rules at distance
`0.01`. They must also prove equal-emission structural labels are independent
of p, preserve the identified `lambda_present` baseline, and distinguish the
unidentifiable ordered contrast. Continue to cover no profiles, all zero-based
index ranges and pre-RNG rejection, predictive applicability/fixed
frames/metric boundaries, sparse 24-width median imputation, and deterministic
runtime task expansion plus eight-worker LPT.

Integrated-amendment RED/GREEN evidence must cover the complete matrix in the
accepted amendment proposal. Task 3 calibration dispatch tests are in-process,
injected, deterministic fixtures under `tmp_path`. They must assert
`holdout_payload_instantiated=false`, `scientific_rows_emitted=false`,
`rng_factory_call_count=0`, and `canonical_output_write_count=0`. They must not
call the live calibration runner or launch a production calibration subprocess.
Task 4 section 4 is the first live runtime benchmark and calibration owner.

## 4. Complete Pre-Holdout Validation

All tracked source, tests, specs, artifact writers, CLI phases, and
documentation must be complete before this section.

Before candidate config emission, run the implementation identity-and-footprint
guard. It must assert pinned branch, HEAD, and `origin/main`; reproduce the
literal 16-file manifest; require the exact phase-specific state within the
19-path publication-path universe; reject every out-of-allowlist untracked
non-ignored or other out-of-footprint path; and write no config on failure. The
emitted config must already contain the reproduced analytical digest before
`config_sha256` and `config_file_sha256` are computed.

```bash
git diff --check
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
rm -rf dist
uv build
uv run pre-commit run --all-files
rm -rf artifacts/synth_medium_latent_response_observation_recovery
/usr/bin/time -p uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase runtime-benchmark \
  --workers 8
jq -e \
  '.workers == 8 and
   .safety_factor == 1.2 and
   (.measured_task_units | length) == 11 and
   all(.measured_task_units[];
       (.task_id | type) == "string" and
       .measured_duration_seconds >= 0 and
       .calibration_repeat_count >= 0 and
       .holdout_repeat_count >= 0) and
   (.calibration_task_durations | type) == "array" and
   (.holdout_task_durations | type) == "array" and
   (.calibration_worker_loads | length) == 8 and
   (.holdout_worker_loads | length) == 8 and
   all(.calibration_worker_loads[]; . >= 0) and
   all(.holdout_worker_loads[]; . >= 0) and
   .equal_bootstrap_task_unit.bundle_index == 0 and
   .equal_bootstrap_task_unit.pseudo_replicate_first == 0 and
   .equal_bootstrap_task_unit.pseudo_replicate_last == 23 and
   .equal_bootstrap_task_unit.holdout_repeat_count == 199 and
   .equal_bootstrap_task_unit.scientific_row == false and
   .projected_calibration_seconds <= 1500 and
   .projected_holdout_seconds <= 1500 and
   .holdout_payload_instantiated == false and
   .scientific_rows_emitted == false and
   .passed == true' \
  artifacts/synth_medium_latent_response_observation_recovery/runtime_projection.json
CALIBRATION_START=$(date +%s)
/usr/bin/time -p uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase calibration \
  --workers 8
CALIBRATION_SECONDS=$(($(date +%s) - CALIBRATION_START))
test "$CALIBRATION_SECONDS" -le 1800
printf 'calibration_wall_seconds=%s\n' "$CALIBRATION_SECONDS"
```

The runtime benchmark uses nested calibration replicate `0`, each non-equal
development replicate `0`, and only the timing-specific equal-emission
development bundle and development bootstrap bundle `0`. It times one complete
unit per scenario, including profiles and 199 references where applicable,
plus one complete equal-bootstrap refit. `runtime_projection.json` expands the
frozen calibration/holdout duration lists, includes 199 equal holdout bootstrap
durations, and records deterministic LPT worker loads and 20% safety-factor
makespans. Any benchmark, projection, or calibration timing failure stops
before freeze and returns to Barry. Do not reduce evidence, change thresholds,
use remote compute, or expose holdout.

Inspect calibration and source provenance:

```bash
sed -n '1,300p' artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
sed -n '1,260p' artifacts/synth_medium_latent_response_observation_recovery/source_provenance.json
sed -n '1,320p' artifacts/synth_medium_latent_response_observation_recovery/runtime_projection.json
shasum -a 256 spec/synth_medium_latent_response_observation_recovery_gate.md
shasum -a 256 artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
```

After independent calibration approval, append final hashes to `Log.md`, then
freeze and verify the complete analytical tracked state:

Immediately before `freeze-tracked-state`, invoke the same guard. It must exit nonzero on identity, manifest, status, or footprint mismatch while changing no config byte and creating no preholdout receipt.

```bash
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase freeze-tracked-state \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase verify-tracked-state \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json
```

No tracked analytical, code, test, spec, threshold, CLI, or documentation edit
is permitted after this point.

## 5. Execute Holdout Once

Immediately before exclusive receipt creation, assert branch
`codex/spatext-goal023-latent-response-observation-gate`, HEAD and
`origin/main` commit
`53462d0365babf2c8070714a930f69b4071af276`; reproduce the 16-file manifest and
digest; require the exact holdout-pre-receipt presence state within the 19-path
publication-path universe; reject every out-of-allowlist untracked non-ignored
or other path; verify frozen config and preholdout receipt; and require the
holdout receipt to be absent. Fail before receipt creation on mismatch.

```bash
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase holdout \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
```

The command atomically creates the immutable tracked receipt before exposure.
After receipt creation and immediately before constructing any RNG object or
payload, it internally repeats identity, footprint, analytical digest, embedded
and file config hashes, preholdout-receipt file hash, and holdout-receipt
self/file hashes. Failure preserves the receipt, constructs no RNG, records
`STOP_INVALIDATED_POST_EXPOSURE`, and burns the namespace. On success, capture
the represented 21-file digest and external complete 22-file artifact snapshot.

Never delete the Goal 023 bundle, rerun holdout, or rerun an artifact-producing
command. A required analytical change invalidates publication and requires
Barry's approval plus a fresh seed namespace.

## 6. Inspect Immutable Holdout Artifacts

```bash
find artifacts/synth_medium_latent_response_observation_recovery -maxdepth 2 -type f -print | sort
sed -n '1,300p' artifacts/synth_medium_latent_response_observation_recovery/report.md
sed -n '1,340p' artifacts/synth_medium_latent_response_observation_recovery/verification.json
sed -n '1,120p' artifacts/synth_medium_latent_response_observation_recovery/control_decision_summary.csv
sed -n '1,120p' artifacts/synth_medium_latent_response_observation_recovery/fit_execution_evidence.csv
sed -n '1,120p' artifacts/synth_medium_latent_response_observation_recovery/model_parameter_contract.csv
```

Compare the emitted exact 22-file set, represented 21-file verification manifest, and complete external 22-file snapshot with the frozen identities. Reject missing files,
stale extras, zero-byte outputs, NaN/infinity, unstable sorting, clipped SVGs,
or unreferenced visuals.

## 7. Post-Holdout Read-Only Verification

Do not regenerate data or change tracked analytical files. Before and after
each individual command below, capture and compare the complete provenance
envelope defined in Goal/spec. Do not guard the command block as one unit.

The following ordered registry is closed. Retry and Task 6 dispatch require an
exact argv match before execution; each entry binds its class, parsed phase,
and the sole reviewed retry disposition
`TRANSIENT_VALIDATION_FAILURE_RETRY_APPROVED`:

| # | Command class | Parsed phase | Exact argv |
| ---: | --- | --- | --- |
| 1 | `static_diff` | null | `git diff --check` |
| 2 | `format_check` | null | `uv run ruff format --check .` |
| 3 | `lint_check` | null | `uv run ruff check .` |
| 4 | `type_check` | null | `uv run mypy src tests` |
| 5 | `test_check` | null | `uv run pytest` |
| 6 | `build_check` | null | `uv build` |
| 7 | `hook_check` | null | `uv run pre-commit run --all-files` |
| 8 | `frozen_verify` | `verify` | `uv run python scripts/run_synth_medium_latent_response_observation_recovery.py --phase verify --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json` |
| 9 | `tracked_state_verify` | `verify-tracked-state` | `uv run python scripts/run_synth_medium_latent_response_observation_recovery.py --phase verify-tracked-state --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json` |
| 10 | `receipt_hash_read` | null | `shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json` |
| 11 | `ignored_status_read` | null | `git status --ignored --short artifacts dist` |
| 12 | `repository_status_read` | null | `git status --short --branch --untracked-files=all` |

```bash
git diff --check
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
uv run pre-commit run --all-files
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase verify \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase verify-tracked-state \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
shasum -a 256 docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
git status --ignored --short artifacts dist
git status --short --branch --untracked-files=all
```

Accept only zero exit plus an unchanged envelope. Mutation is
`STOP_INVALIDATED_POST_EXPOSURE`. An unchanged nonzero is
`STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION` and pauses
publication. Retry the exact same non-generative command at most once, only
after independent transient classification, unchanged-envelope proof, and an
approved exact retry recorded by one guarded Log append. A successful retry is
`CONTINUE_FROZEN_CANDIDATE`; a second unchanged nonzero is
`STOP_NONMUTATING_VALIDATION_FAILURE` and stops publication without scientific
invalidation. Holdout and artifact-generating commands are never retryable.

Expected ignored output:

```text
!! artifacts/
!! dist/
```

## 8. Exact Staging And Final Review

Stage only:

```text
AGENTS.md
README.md
pyproject.toml
uv.lock
spec/report_log.md
spec/synth_medium_latent_response_observation_recovery_gate.md
src/spatext/observe.py
src/spatext/synth/medium/__init__.py
src/spatext/synth/medium/latent_response_observation_recovery.py
scripts/run_synth_medium_latent_response_observation_recovery.py
tests/test_observe.py
tests/test_synth_medium_latent_response_observation_recovery.py
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json
docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
```

```bash
git add \
  AGENTS.md README.md pyproject.toml uv.lock spec/report_log.md \
  spec/synth_medium_latent_response_observation_recovery_gate.md \
  src/spatext/observe.py \
  src/spatext/synth/medium/__init__.py \
  src/spatext/synth/medium/latent_response_observation_recovery.py \
  scripts/run_synth_medium_latent_response_observation_recovery.py \
  tests/test_observe.py \
  tests/test_synth_medium_latent_response_observation_recovery.py \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/preholdout_state_receipt.json \
  docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json
git diff --cached --check
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase verify-staged-state \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
git status --ignored --short artifacts dist
```

The `verify-staged-state` phase must fail unless branch and base are exact, the
cached path set is a subset of the frozen allowlist, no unstaged tracked or
untracked non-ignored path remains, and the analytical tracked-state digest
matches the pre-holdout receipt.

A fresh final reviewer inspects `git diff --cached`, immutable artifacts,
receipts, validation evidence, and live status. Any required analytical change
invalidates holdout and stops publication.

Post-exposure `Log.md` appends are explicitly authorized provenance writes.
Guard each append as one command: the captured Log remains the exact prefix,
the suffix equals independently approved bytes, and every other envelope member
and non-Log staged blob remains unchanged. Exact staging may change only the
index to the predeclared allowlisted path/blob set and no working-tree byte.

Terminal attestation uses only the canonical Goal 023 `Log.md` path and one
canonical JSON line with `record_type=terminal_attestation`. Recompute the
complete envelope and reject any existing terminal record before append. After
append, `git add` may update only the Log worktree bytes, Log cached/index blob,
and their exact porcelain status; every non-Log blob remains identical. Any
post-append observation mismatch is the immutable terminal disposition
`STOP_INVALIDATED_TERMINAL_ATTESTATION_IMMUTABLE`, never acceptance, and no
second terminal line is permitted under a new parent.

## 9. Publication

Every publication command is individually wrapped in the complete per-command envelope and must satisfy the nonzero disposition rule before any identity transition.


Immediately after final-review acceptance, repeat all state guards:

```bash
git fetch --prune origin
test "$(git branch --show-current)" = "codex/spatext-goal023-latent-response-observation-gate"
test "$(git rev-parse HEAD)" = "53462d0365babf2c8070714a930f69b4071af276"
test "$(git rev-parse origin/main)" = "53462d0365babf2c8070714a930f69b4071af276"
GOAL_COMMON=$(git rev-parse --path-format=absolute --git-common-dir)
git diff --cached --check
uv run python scripts/run_synth_medium_latent_response_observation_recovery.py \
  --phase verify-staged-state \
  --frozen-config artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json
APPROVED_TREE=$(git write-tree)
git commit -m "feat: add synth-medium latent-response observation recovery gate"
GOAL_SHA=$(git rev-parse HEAD)
test "$(git rev-parse HEAD^{tree})" = "$APPROVED_TREE"

cd /Users/bwbrook/papers/spatext
test "$(git branch --show-current)" = "main"
test -z "$(git status --porcelain)"
CANONICAL_COMMON=$(git rev-parse --path-format=absolute --git-common-dir)
test "$CANONICAL_COMMON" = "$GOAL_COMMON"
git fetch --prune origin
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
git merge --ff-only codex/spatext-goal023-latent-response-observation-gate
test "$(git rev-parse HEAD)" = "$GOAL_SHA"
git push origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
git status --short --branch
```

Stop on any failure. Do not force, reset, rebase, stash, clean, delete branches,
or broaden the footprint. Do not start Goal 024.

## Scientific Stop Rules

Stop on oracle failure, false-positive controls, unresolved accepted estimand
ridge, confidently wrong sparse inference, hidden truth leakage, unreported
missingness bias, numerical-domain failure, canonical noncollision/design-audit
failure, silent misspecification, holdout-lock breach, false case-study
transportability, need for full spread fitting, real data, remote compute, or a
new material biological assumption. No schedule or estimand repair is allowed
under the Goal 023 namespace after a canonical audit failure.
