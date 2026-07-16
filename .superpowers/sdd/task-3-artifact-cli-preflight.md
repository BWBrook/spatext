# Goal 023 Task 3 Artifact, CLI, And Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete pre-holdout Goal 023 scenario, artifact, CLI,
runtime-projection, provenance-guard, and review-visual surface without
constructing a Goal 023 holdout payload.

**Architecture:** Keep the required source footprint literal. Extend the one
Goal 023 core module with typed immutable task/result records and pure builders;
keep the script a thin phase dispatcher; serialize only compact, canonically
sorted rows. Run scientific work as independent scenario/replicate tasks whose
RNG identity is entirely payload-derived, then merge compact results in frozen
key order so worker completion order cannot affect bytes.

**Tech Stack:** Python 3.14, NumPy 2.3+, SciPy 1.17-1.x, stdlib
`concurrent.futures`, `csv`, `json`, `hashlib`, `pathlib`, and the existing
hand-written SVG conventions.

## Status And Authority Snapshot

This is a read-only Task 3 preflight. No calibration, optimizer/profile run,
runtime benchmark, artifact generation, holdout payload, receipt, or future
output was created or inspected.

Snapshot on 2026-07-11:

| Surface | State |
| --- | --- |
| branch | `codex/spatext-goal023-latent-response-observation-gate` |
| HEAD/base | `53462d0365babf2c8070714a930f69b4071af276` |
| authoritative spec | `0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d` |
| Goal | `cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20` |
| Plan | `df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e` |
| Runbook | `78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed` |
| Log | 2222 lines; `a531eb33d0afb1ffdb91efcf0cddc37bd0b8327269b074bb175b566a85039203` |
| current core source | `eef58af9aa809bd7d0c055a368a3eb2f2975b4056043420edbd571a82fe93b92` |
| current core tests | `10c0f460bd26088a85d3edd56752cf5f592cc716d3e9835e48ce1779325008bb` |
| provenance amendment proposal | `957c138936e269b4fb252141aac1103d4d84f169db23a8497fbb3d043062846f` |

The core source and tests are moving Task 2b state, not an accepted Task 3
handoff. Recompute all hashes at handoff; do not treat this table as authority
after another append or edit.

## Global Constraints

- Synthetic scheduled counts only; fixed Goal 017 landscape and Goal 018
  `balanced_corridor_detour_v2` arrival surface.
- No Goal 019-022 fit, reconstructed target fit, spread fit, ABC, MCMC,
  posterior claim, real data, remote compute, or production adoption.
- Do not construct, derive, preview, inspect, or hash any Goal 023 holdout RNG
  payload before the one authorized holdout command.
- Every stochastic draw uses the frozen canonical JSON payload and its own
  `PCG64DXSM(SeedSequence(...))` substream.
- Every worker result must be invariant to worker count and completion order.
- All emitted CSV is UTF-8 with an explicit header, LF endings, `.` decimal,
  empty string only for structurally nullable values, and no NaN or infinity.
- All emitted JSON uses sorted keys, finite numbers, and no undeclared top-level
  fields.
- Generated artifacts remain under the ignored
  `artifacts/synth_medium_latent_response_observation_recovery/` directory.
- Tracked writes remain inside the Goal 023 publication allowlist. Do not add a
  convenience module, data store, dependency, or artifact outside the frozen
  footprint.
- The Goal packet's bundled publication rule overrides the generic frequent-
  commit plan pattern: no Task 3 commit, staging, or push.

## Blocking Preconditions

Task 3 implementation must not start until both gates below are satisfied.

1. **Task 2b handoff:** accepted implementations exist for process,
   observation, joint, and equal-rate fitting; adaptive profiles; practical
   identifiability; typed failures; and the complete nine-audit pre-estimation
   gate. Current progress marks Task 2b pending, and current tests contain no
   adaptive profile suite.
2. **Provenance amendment:** apply the exact patch-ready proposal in
   `.superpowers/sdd/holdout-provenance-amendment-proposal.md`, append its
   supersession and v2 records against live Log parents, add its 14 temporary-
   fixture tests, reseal Goal/Plan/Runbook/spec hashes, and obtain fresh
   scientific, executor-readiness, and provenance/freeze acceptance. The
   existing Log-only interpretation is preserved but superseded for holdout
   authority.

Stop rather than adapting Task 3 around either missing handoff.

## Design Decision

Three architectures were considered:

1. **Recommended: compact task-result pipeline in the required core module.**
   Workers receive small `ReplicateTask` identities, reconstruct immutable
   worker context once, and return only fit/profile/predictive rows. It obeys
   the exact source footprint and keeps deterministic merge points explicit.
2. **One giant review-pack result mirroring Goals 017-022.** This matches older
   modules but would retain raw 199-reference ensembles and all histories in
   memory, making eight-process execution and holdout projection fragile.
3. **SQLite/Arrow intermediate store or extra private modules.** This would
   simplify streaming and code size but violates the approved dependency and
   tracked-footprint boundary unless the authority is amended.

Use approach 1. The prior review-pack API remains a style reference only.

## File And Interface Boundaries

### `src/spatext/observe.py`

Remain unchanged in Task 3. It owns only reusable effective-count rates,
effort-scaled means, scalar Poisson log probabilities, and numerical-domain
errors. No scenario, seed, artifact, receipt, or CLI policy may enter it.

### `src/spatext/synth/medium/latent_response_observation_recovery.py`

Own all scientific and provenance behavior, grouped in this order inside the
required single module:

1. frozen constants, enum domains, file/schema tuples, and scenario registry;
2. accepted Task 2a/2b model, simulation, likelihood, fit, and profile APIs;
3. source-context reconciliation and analyst/evaluator firewall adapters;
4. task graph and deterministic worker entry points;
5. compact replicate, profile, predictive, and control result records;
6. aggregate gates and recommendation precedence;
7. canonical CSV/JSON/report/SVG builders and validators;
8. runtime measurement, task expansion, and deterministic LPT projection;
9. tracked-state, receipt, artifact-snapshot, and command-envelope guards;
10. high-level phase functions called by the CLI.

Add these Task 3 boundary records and entry points. Exact dataclass field order
must be tested because it feeds deterministic serialization:

```python
@dataclass(frozen=True, slots=True)
class ScenarioDefinition:
    scenario_id: str
    scenario_role: str
    generation_model: str
    fit_model: str
    schedule_id: str
    effort_rule: str
    development_replicates: int
    calibration_replicates: int
    holdout_replicates: int
    expected_behavior: str
    truth_access_class: str
    transportability_class: str

@dataclass(frozen=True, slots=True)
class ReplicateTask:
    scenario_id: str
    split_id: str
    replicate_id: int

    @property
    def task_id(self) -> str: ...

@dataclass(frozen=True, slots=True)
class ScenarioReplicateResult:
    task: ReplicateTask
    recovery_rows: tuple[dict[str, object], ...]
    latent_time_rows: tuple[dict[str, object], ...]
    profile_rows: tuple[dict[str, object], ...]
    predictive_rows: tuple[dict[str, object], ...]
    control_rows: tuple[dict[str, object], ...]
    fit_succeeded: bool
    failure_reason: str | None

@dataclass(frozen=True, slots=True)
class RuntimeTaskUnit:
    task_id: str
    scenario_id: str
    benchmark_split: str
    benchmark_replicate_first: int
    benchmark_replicate_last: int
    measured_duration_seconds: float
    calibration_repeat_count: int
    holdout_repeat_count: int
    includes_profiles: bool
    predictive_reference_count: int
    scientific_row: bool

@dataclass(frozen=True, slots=True)
class TrackedStateManifest:
    entries: tuple[tuple[str, str], ...]
    tracked_state_sha256: str

@dataclass(frozen=True, slots=True)
class ArtifactSnapshot:
    entries: tuple[tuple[str, str], ...]
    artifact_set_sha256: str

@dataclass(frozen=True, slots=True)
class ProvenanceEnvelope:
    branch: str
    head: str
    base: str
    status: tuple[str, ...]
    cached_entries: tuple[tuple[str, str], ...]
    tracked_state: TrackedStateManifest
    log_bytes: int
    log_lines: int
    log_sha256: str
    preholdout_receipt_sha256: str
    holdout_receipt_sha256: str
    frozen_config_sha256: str
    artifacts: ArtifactSnapshot

def run_scenario_replicate(task: ReplicateTask) -> ScenarioReplicateResult: ...
def run_runtime_benchmark(*, workers: int, output_dir: Path) -> dict[str, object]: ...
def run_calibration(*, workers: int, output_dir: Path) -> tuple[Path, ...]: ...
def freeze_tracked_state(*, frozen_config: Path, repo_root: Path) -> Path: ...
def run_holdout(*, workers: int, frozen_config: Path, output_dir: Path) -> tuple[Path, ...]: ...
def verify_bundle(*, frozen_config: Path, output_dir: Path) -> dict[str, object]: ...
def verify_tracked_state(*, frozen_config: Path, repo_root: Path) -> None: ...
def verify_staged_state(*, frozen_config: Path, repo_root: Path) -> None: ...
```

`run_scenario_replicate` is the only worker-callable science entry point. It
wraps Task 2b APIs through one `run_required_fit(...)` adapter and never accepts
an evaluator/truth object. Evaluator truth remains in a separate local result
used only after fit completion to build recovery/coverage rows.

### `scripts/run_synth_medium_latent_response_observation_recovery.py`

Own argument parsing, phase dispatch, concise summaries, and exit status only.
It must not define equations, scenario branches, schemas, receipt bytes, or
artifact logic. Set BLAS thread defaults before importing NumPy/SciPy-backed
package code so eight worker processes do not each create a full BLAS pool.

Literal phase interface:

```text
--phase runtime-benchmark [--workers 8] [--output-dir PATH]
--phase calibration [--workers 8] [--output-dir PATH]
--phase freeze-tracked-state --frozen-config PATH
--phase verify-tracked-state --frozen-config PATH
--phase holdout --frozen-config PATH [--workers 8] [--output-dir PATH]
--phase verify --frozen-config PATH [--output-dir PATH]
--phase verify-staged-state --frozen-config PATH
```

`--workers` must be a built-in integer from 1 through 8; default is 8. Reject
unknown phases/arguments before importing or constructing any RNG payload.
Only `runtime-benchmark`, `calibration`, and the one authorized `holdout` phase
may invoke scientific task runners. Verification and freeze phases are
non-generative by construction.

### `src/spatext/synth/medium/__init__.py`

Export only the default output directory, exact root/visual file tuples,
`ScenarioDefinition`, the top-level build/phase functions, and report renderer.
Do not export receipt mutation helpers, command runners, worker globals, or
truth/evaluator records.

### `tests/test_synth_medium_latent_response_observation_recovery.py`

Continue the existing behavior-ID convention. Test public contracts through
the core module, inject clocks/executors/command runners/RNG factories, and use
`tmp_path` for every writer/receipt/guard test. No test may call a Goal 023
holdout payload constructor.

### Documentation files

- `AGENTS.md`: document phase separation, disk-first verification, and the
  post-exposure no-regeneration rule.
- `README.md`: add scheduled-count-only Goal 023 orientation and commands only
  after their behavior exists.
- `spec/report_log.md`: append a concise Task 3 implementation record without
  rewriting Goal 017-022 history.
- Goal 023 `Log.md`: append exact parent-bound RED/GREEN/review evidence only.

## Exact Scenario And Task Graph

Keep `SCENARIO_DEFINITIONS` in the numbered contract order:

1. `process_oracle_observed_transition`
2. `observation_oracle_fixed_transition`
3. `dense_count_exact_model`
4. `structured_imperfect_effort`
5. `sparse_expected_failure`
6. `zero_driver_effect_negative_control`
7. `permuted_arrival_alignment_stress`
8. `no_emission_contrast_negative_control`
9. `informative_dropout_misspecification_stress`
10. `goal018_continuous_abundance_stress`
11. `spatial_frailty_stress`

Scientific task IDs are:

```text
scenario=<scenario_id>|split=<split_id>|replicate=<zero-padded-4-digit-id>
```

The calibration command executes all non-holdout evidence: 12 development
replicates for every scenario plus 24 calibration replicates for each of the
four nested scenarios. The holdout graph remains a metadata-only description
until the authorized holdout phase: 48 replicates for each nested scenario and
24 for each nonnested scenario. The equal-emission holdout classification is
one shared 24-replicate observed bundle plus 199 independently seeded
24-replicate bootstrap bundles.

Before Task 3 code is written, add one authority test that locks the exact
runtime-repeat interpretation:

- nested measured units: `calibration_repeat_count = 36`,
  `holdout_repeat_count = 48`;
- sparse and each non-equal control/stress: `12` and `24`;
- equal-emission measured 24-replicate timing bundle: `1` and `1`;
- equal-bootstrap measured unit: `0` and `199`.

If independent executor review concludes the timing-only equal bundle cannot
conservatively represent its 12 scientific development replicates, stop for a
narrow pre-exposure contract clarification. Do not silently change repeat
counts or divide the measured duration by 24.

## Predictive Bundle Architecture

For every count-applicable fitted replicate:

1. freeze the retained opportunity frame once;
2. compute the 27 observed stratum/metric values once;
3. generate exactly 199 reference datasets in draw-index order;
4. for each draw, consume the complete process array and complete Poisson
   vector, then reduce immediately to the 27 metrics;
5. retain a `float64` matrix of shape `(199, 27)`, not 199 histories or count
   vectors;
6. consume exactly 27 PIT uniforms in frozen stratum/metric order;
7. emit 27 replicate diagnostic rows, then discard the matrix.

The 27 cells are ordered `all`, `q1`-`q5`, `early`, `middle`, `late`, with
metric order `mean_count`, `zero_fraction`, `variance_to_mean`. A failed fit
creates 27 unavailable rows with the attempted denominator preserved and does
not construct a predictive-reference RNG.

`process_oracle_observed_transition` emits no predictive rows.
`observation_oracle_fixed_transition` is explicitly oracle-conditional.
`no_emission_contrast_negative_control` uses its equal-submodel references and
marks predictive warning as diagnostic only. The permuted-arrival stress uses
the permuted fitted model as its primary reference and the correctly aligned
fit only for heldout score comparison.

Aggregate by `(scenario_id, split_id, stratum_type, stratum_value, metric_id)`
in lexical/numeric key order. Calculate exact KS and Holm only when all required
PIT values are valid; otherwise serialize nullable inferential fields, set
`warning = true`, and fail the gate. Stouffer uses only finite residuals but
never changes `replicate_count`.

## Exact Artifact Bundle

The final expected set has 21 files. Define one literal tuple in this order;
never discover it from disk:

```text
recovery_gate_config.json
runtime_projection.json
source_provenance.json
holdout_manifest.json
model_parameter_contract.csv
scenario_definitions.csv
replicate_recovery.csv
coverage_calibration.csv
latent_time_calibration.csv
predictive_replicate_diagnostics.csv
predictive_check_summary.csv
identifiability_profiles.csv
control_decision_summary.csv
verification.json
report.md
visuals/parameter_recovery.svg
visuals/coverage_calibration.svg
visuals/latent_time_calibration.svg
visuals/identifiability_profiles.svg
visuals/control_comparison.svg
visuals/review_montage.svg
```

The config's `artifact_manifest` uses the same order and contains exactly
`path`, `role`, `required`, and nullable `sha256`. The immutable config cannot
acquire post-holdout hashes later.

To close the provenance proposal's artifact-manifest self-reference without a
new schema or file, make `verification.json`'s existing
`checks[name="artifact_manifest"].details` the final manifest-bearing object.
It records path/hash pairs for the other 20 files in the literal order and a
hash over those lines. The external `ArtifactSnapshot` then adds the hash of
`verification.json` itself and hashes the complete 21-entry lexical manifest.
Tests must prove this two-level rule is non-self-referential, complete, and
detects missing, extra, or replaced files. Require provenance reviewers to
accept this reading in the tracked amendment before freeze.

### CSV columns and row order

Headers are literal and rows sort by the declared primary key, with string
components lexically ascending and integers numerically ascending:

- `model_parameter_contract.csv`:
  `parameter_id,role,units,transform,lower_bound,upper_bound,generating_value,fitted_scenarios,structural_status,practical_status,interpretation`.
- `scenario_definitions.csv`:
  `scenario_id,scenario_role,generation_model,fit_model,schedule_id,effort_rule,development_replicates,calibration_replicates,holdout_replicates,expected_behavior,truth_access_class,transportability_class`.
- `replicate_recovery.csv`:
  `scenario_id,split_id,replicate_id,parameter_id,truth_value,estimate,interval_lower,interval_upper,interval_width,converged,converged_start_count,at_boundary,profile_two_sided,truth_in_interval,log_likelihood,signed_error,absolute_error,gate_result`.
- `coverage_calibration.csv`:
  `scenario_id,split_id,parameter_id,replicate_count,converged_count,coverage_count,coverage_fraction,acceptance_lower_count,acceptance_upper_count,median_signed_error,median_absolute_error,median_interval_width,maximum_absolute_error,maximum_interval_width,gate_result`.
- `latent_time_calibration.csv`:
  `scenario_id,split_id,replicate_id,metric_id,sample_size,observed_value,expected_value,error,gate_result`.
- `predictive_replicate_diagnostics.csv`:
  `scenario_id,split_id,replicate_id,stratum_type,stratum_value,metric_id,sample_size,fit_succeeded,diagnostic_available,observed_value,reference_mean,reference_sd,reference_mcse,standardized_residual,standardized_residual_nonfinite,randomized_pit`.
- `predictive_check_summary.csv`:
  `scenario_id,split_id,stratum_type,stratum_value,metric_id,replicate_count,diagnostic_count,failed_fit_count,mean_standardized_residual,stouffer_z,ks_statistic,raw_p,holm_adjusted_p,warning,gate_result`.
- `identifiability_profiles.csv`:
  `scenario_id,split_id,replicate_id,parameter_id,grid_index,parameter_value,profile_log_likelihood,likelihood_ratio_delta,nuisance_converged,inside_interval`.
- `control_decision_summary.csv`:
  `decision_row_id,scenario_id,parameter_id,structural_status,practical_status,gate_family,gate_result,test_statistic,bootstrap_replicates,p_value,alignment_correlation,silent_misspecification_failure,recommendation_rank,recommendation_class,transportability_class,interpretation`.

`fitted_scenarios` is the sole exception to lexical order: join IDs in frozen
scenario-contract order with `|` and no spaces. Equal-emission status rows are
fixed by degeneracy, not bootstrap p.

### JSON contracts

Use explicit validators that reject extra top-level fields and type confusion
such as bool-as-int. Implement one canonical JSON function:

```python
def canonical_json_bytes(payload: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")
```

Config hash omits only `config_sha256`; holdout receipt hash omits only
`receipt_sha256`. `source_sha256` uses the literal two-line source digest rule.
Do not reuse receipt hashing for config hashing.

### Atomic writer rule

Calibration artifacts write to a sibling temporary directory, fsync files,
validate exact set/schema/order, then replace the pre-holdout candidate bundle.
The holdout phase never deletes or replaces the bundle wholesale. It writes
each final artifact through same-directory temporary files and `os.replace`
only after successful validation, preserving the frozen config and runtime
projection bytes.

Tracked receipts use exclusive creation with `os.open(..., O_CREAT | O_EXCL |
O_WRONLY, 0o644)`, canonical bytes, `fsync`, and close. Never use a replaceable
temporary rename for a receipt.

## Deterministic Parallel Scheduling

Use `ProcessPoolExecutor(max_workers=workers, initializer=...)` under the
platform default spawn behavior. The initializer builds the immutable
landscape/design context once per worker. Do not pickle the 5,225-cell context
with every task.

Submit tasks in canonical task-ID order. Store each future with its input index;
collect compact results into that index, then flatten and sort rows by artifact
primary key. Never append rows in `as_completed` order.

Set parent environment defaults before package import:

```text
OPENBLAS_NUM_THREADS=1
OMP_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1
NUMEXPR_NUM_THREADS=1
```

Do not override an explicit user value. Record effective values in runtime
benchmark diagnostic details, not as new top-level JSON fields.

Task failure is data, not pool cancellation: return a typed failed result with
nullable scientific fields and the attempted denominator preserved. Pool,
schema, provenance, or numerical-domain failures remain hard command failures.

## Runtime Benchmark And Projection

Benchmark exactly 11 scenario units plus one separate equal-bootstrap unit:

- nested scenarios: calibration replicate 0;
- sparse and every non-equal control/stress: development replicate 0;
- equal emission: timing-only development pseudo-replicates 0-23;
- equal bootstrap: development bundle 0 over pseudo-replicates 0-23.

Only the benchmark exception may validate the development bootstrap mapping.
It must use a dedicated `BenchmarkPayload`/factory that cannot accept
`split="holdout"`; it emits no scientific row and never calls the holdout
payload constructor.

Stable duration IDs are:

```text
calibration|scenario=<id>|split=<id>|replicate=<0000>
holdout|scenario=<id>|split=holdout|replicate=<0000>
holdout|scenario=no_emission_contrast_negative_control|bootstrap=<000>
```

Expand all duration objects before scheduling. Deterministic LPT is pure:

```python
def lpt_worker_loads(tasks: tuple[DurationTask, ...], workers: int) -> tuple[float, ...]:
    ordered = sorted(tasks, key=lambda task: (-task.duration_seconds, task.task_id))
    loads = [0.0] * workers
    for task in ordered:
        worker = min(range(workers), key=lambda index: (loads[index], index))
        loads[worker] += task.duration_seconds
    return tuple(loads)
```

Projection is `1.20 * max(loads)` and must be at most 1,500 seconds for both
graphs. Record raw `perf_counter_ns()` deltas converted once to seconds. Tests
inject integer nanosecond durations; never assert live timing equality.

The actual calibration wall gate remains 1,800 seconds. A miss stops before
freeze; it cannot reduce replicates/references/profiles, change thresholds, use
remote compute, or expose holdout.

## Receipt, Hash, And Phase Guards

The literal analytical manifest is the 16-path list in the current Log and
provenance proposal. Encode it as a tuple constant; never use globs,
`git ls-files`, imports, or current dirtiness to define membership.

Phase state machine:

```text
runtime-benchmark -> calibration -> freeze-tracked-state
-> holdout (once) -> verify -> verify-staged-state
```

`verify-tracked-state` is legal after freeze and after holdout. Other backward
or repeated transitions fail closed.

At config emission, freeze, holdout pre-receipt, and holdout post-receipt/pre-
RNG, require exact branch/HEAD/base, the 16-path digest, accepted tracked
footprint, no untracked non-ignored path, source receipt/hash, config hash, and
the phase-specific receipt conditions. Guard functions accept injected git and
RNG factories in tests.

Holdout ordering is literal:

1. complete pre-receipt guard;
2. exclusive immutable receipt creation with exposure-time values;
3. complete post-receipt guard and receipt self-hash;
4. only then instantiate the first holdout payload/RNG;
5. run tasks once;
6. validate and freeze the complete artifact snapshot;
7. never retry or regenerate.

Post-exposure command envelopes capture and compare identity, status, index,
16 analytical bytes, exact Log prefix, both receipts, frozen config, and all 21
artifact bytes around each individual command. Implement the amendment's three
dispositions verbatim:

```text
CONTINUE_FROZEN_CANDIDATE
STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION
STOP_NONMUTATING_VALIDATION_FAILURE
STOP_INVALIDATED_POST_EXPOSURE
```

The one retry is available only for the exact same non-generative command after
an independently approved exact Log append. Holdout and artifact-generating
commands are never retryable.

## Review Visuals

Render the six required SVGs from emitted rows, never live fit objects:

- `parameter_recovery.svg`: all attempted estimates and 90% intervals by
  parameter/scenario, truth lines, and explicit failed/open markers.
- `coverage_calibration.svg`: coverage counts against exact inclusive binomial
  bounds, with full attempted denominators.
- `latent_time_calibration.svg`: Brier, interval score, and median absolute
  transition-time error by scenario/split.
- `identifiability_profiles.svg`: fixed replicate 0 panels for each applicable
  scenario/parameter plus support and LR cutoff; no result-selected replicate.
- `control_comparison.svg`: all negative controls/stresses, warnings, alignment
  score, equal-emission p, and silent-misspecification state.
- `review_montage.svg`: compact gate/recommendation summary, runtime projections,
  source/config/receipt status, and scheduled-count transportability label.

Every SVG needs an XML title, visible title, axis/legend labels, attempted
denominator, failure encoding, and the literal transportability footer where
scientific interpretation appears. Test exact canvas/viewBox, nonempty marks,
legend presence, text bounds, no `NaN`/`inf`, and report linkage.

## Ordered TDD And Implementation Tasks

### Task 0: Seal Preconditions And Task 2b Handoff

**Files:** Goal 023 authority, Log, current core source/test, and ignored SDD
notes; no Task 3 implementation yet.

- [ ] Apply and independently accept the provenance amendment in its specified
  order using the live Log parent.
- [ ] Finish Task 2b and obtain accepted source/test/Log hashes.
- [ ] Record an interface inventory for Task 2b fit/profile records and map
  them to `run_required_fit` without changing Task 2b internals.
- [ ] Run the accepted focused Task 2b suite and confirm profiles and the nine-
  audit gate exist before adding a Task 3 test.

Expected stop: no Task 3 RED until both hash-specific accepts are present.

### Task 1: Freeze Registries, Schemas, And Task Graphs

**Files:** modify core source/test only; append Log evidence after GREEN.

- [ ] Write RED tests for all 11 definitions, enum domains, exact root/visual
  tuples, 21-file order, CSV headers, JSON top-level keys, exact row sort keys,
  analytical 16-path manifest, and calibration/holdout task counts.
- [ ] Implement immutable constants and validators only.
- [ ] GREEN focused tests; add mutation tests proving returned arrays/tuples and
  registries cannot be changed.

Run:

```bash
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py -k 'registry or schema or task_graph' --no-cov
```

### Task 2: Scenario Generators And Fit Adapter

**Files:** modify core source/test only; append Log evidence after review.

- [ ] Write separate RED groups for nested scenarios, sparse/zero-driver/
  permuted/equal controls, and dropout/continuous/frailty stresses.
- [ ] Test every scenario's generation covariates, fitting covariates, schedule,
  effort, RNG components, complete stochastic consumption, and truth firewall.
- [ ] Implement `run_required_fit` and `run_scenario_replicate`; keep evaluator
  truth physically separate until row construction.
- [ ] Inject failed/nonfinite fits and prove complete attempted rows with no
  denominator loss.
- [ ] Prove task execution byte-equivalent under input permutations and 1 vs 8
  fake workers.

### Task 3: Profiles, Recovery, Coverage, And Latent-Time Rows

**Files:** modify core source/test only.

- [ ] RED tests for adaptive profile row ordering, open sides, LLmax
  invalidation, boundary status, support-width imputations, 48-attempt nested
  coverage, dedicated 24-attempt sparse coverage, ordinary even median, and
  exact central-binomial bounds.
- [ ] Implement pure row builders and aggregate gates over compact fit/profile
  results.
- [ ] Prove failures count false for coverage, full support for error/width,
  and remain in convergence denominators.

### Task 4: Predictive Diagnostics

**Files:** modify core source/test only.

- [ ] RED tests for applicability, fixed frames, 199 draw IDs, complete draw
  consumption, 27-cell order, metric boundaries, zero SD, PIT ties, exact KS,
  Holm tie order, Stouffer, failed-fit unavailable rows, and warning rules.
- [ ] Implement the `(199, 27)` reduction buffer and discard raw references.
- [ ] Prove a failed fit constructs zero reference RNGs and cannot be rescued
  by other replicates.

### Task 5: Equal-Emission, Controls, And Recommendation

**Files:** modify core source/test only.

- [ ] RED tests for the shared observed bundle, 199 bootstrap bundle task IDs,
  direct equal-rate MLE, ordered refits, p formula, failed-bundle hard failure,
  no profiles, fixed six parameter-status rows, alignment 22/24 gate, stress
  warnings, and silent misspecification.
- [ ] Implement control summaries and recommendation precedence as pure
  functions.
- [ ] Prove bootstrap p cannot alter structural labels and every contract/
  artifact/provenance failure wins recommendation precedence.

### Task 6: Stable Artifact Writers And Disk-First Verification

**Files:** modify core source/test only.

- [ ] RED tests for every CSV/JSON schema, lexical/numeric order, nullability,
  bool serialization, duplicate keys, finite values, exact set, stale extras,
  zero-byte files, config/source hashes, and two-level artifact snapshot.
- [ ] Implement canonical JSON/CSV writers, temporary-directory calibration
  publication, holdout per-file atomic publication, and disk-first readers.
- [ ] Build verification and report only from re-read emitted bytes.
- [ ] Compare two independently generated non-holdout fixture bundles byte for
  byte.

### Task 7: Runtime Projection And Multiprocessing

**Files:** modify core source/test and create the CLI script.

- [ ] RED tests for 11 measured units, equal bootstrap unit, exact repeats,
  stable task IDs, nanosecond timing conversion, LPT tie breaks, eight loads,
  1.20 factor, 1,500-second gates, no scientific rows, and no holdout factory
  calls.
- [ ] Implement worker initializer, compact worker return values, deterministic
  merge, benchmark clock injection, duration expansion, and LPT.
- [ ] Prove 1-worker and 8-worker fake execution emit identical rows and
  ordering.

Do not run the live benchmark in Task 3; Task 4 owns that execution.

### Task 8: Provenance Guards, Receipts, And Phase CLI

**Files:** modify core source/test and CLI script; authority amendment already
sealed in Task 0.

- [ ] Implement the proposal's 14 named tests exactly, using temporary
  non-holdout fixtures, injected command runners, and RNG-factory spies.
- [ ] Add RED tests for phase parser legality, illegal transitions, frozen-
  config requirements, exact exit codes, and non-generative verification.
- [ ] Implement immutable manifests, exclusive receipts, provenance envelopes,
  one-retry disposition, and phase dispatch.
- [ ] Prove pre-receipt mismatch creates no receipt/RNG and post-receipt
  mismatch preserves receipt, burns namespace, and creates no RNG.
- [ ] Prove verification cannot dispatch cleanup, benchmark, calibration,
  holdout, or artifact generation.

### Task 9: Visuals, Report, Exports, And Orientation

**Files:** core source/test, `__init__.py`, `AGENTS.md`, `README.md`,
`spec/report_log.md`, Goal 023 `Log.md`.

- [ ] RED tests for six exact visual names, disk-first inputs, fixed content,
  self-decoding labels, report links, and scheduled-count transportability.
- [ ] Implement SVG/report builders and high-level exports.
- [ ] Update docs only after CLI behavior is GREEN; preserve Goal 017-022
  prose/history.
- [ ] Append parent-bound Task 3 evidence and independent review dispositions.

### Task 10: Pre-Holdout Validation And Independent Review

No holdout, runtime benchmark, or full calibration is run in this preflight.
At implementation completion, run the pre-holdout validation ladder through
non-holdout fixture/smoke behavior only, leaving live runtime benchmark and
calibration execution to Task 4 as the Goal packet specifies.

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
```

Then obtain independent scientific, numerical/performance, artifact/schema,
documentation/visual, code, and provenance/freeze reviews. Resolve every
Critical or Important finding before Task 4. Re-run the complete ladder after
the final analytical edit and prove the provenance hooks are byte no-ops.

## Performance Traps And Required Mitigations

1. **Profile/reference multiplication:** finite-difference L-BFGS-B times eight
   starts, adaptive nuisance profiles, and 199 references can multiply one
   replicate into thousands of likelihood calls. Cache each unique profile
   point, reuse adjacent successful nuisance starts exactly as frozen, and
   compute reference metrics without fitting references.
2. **Process spawning and pickling:** macOS spawn plus 5,225-cell schedules can
   dominate runtime if context is sent per future. Build context once per
   worker and return only compact rows, never histories or 199 datasets.
3. **BLAS oversubscription:** eight worker processes with multithreaded BLAS can
   make runtime slower and noisier than one process. Set thread defaults before
   scientific imports and record them in diagnostics.
4. **Order-dependent floating reductions:** completion-order accumulation can
   change low bits and hashes. Sum likelihoods inside a task in canonical array
   order; merge task rows only after index restoration and primary-key sort.
5. **Equal-emission bootstrap load:** 199 bundles x 24 pseudo-replicates x two
   shared fits is likely the holdout bottleneck. Keep each bundle one coarse
   task, benchmark one complete bundle, and do not parallelize its inner 24
   replicates as nested pools.
6. **Artifact memory:** retaining all profiles and predictive histories in a
   giant result object can exceed the Mac mini's useful working set. Retain
   compact rows only and stream finalized CSV sections in task order.
7. **Atomicity/self-reference:** config, verification, receipts, and artifact
   manifests have different hashing rules. Keep separate canonical builders
   and test crash points; never use one generic `hash_and_write` shortcut.

## Stop Rules

Stop Task 3 on any of the following:

- Task 2b handoff lacks accepted profiles or nine-audit authorization.
- The provenance amendment or two-level artifact-snapshot interpretation is
  not independently accepted.
- Runtime task repeat counts cannot be made literal without authority change.
- A test needs a real holdout scenario/split payload or future artifact.
- The 21-file set requires an extra artifact/schema/dependency.
- Truth enters analyst fit/profile/task scheduling or predictive references.
- One-worker and eight-worker fixture outputs differ after canonical sorting.
- Receipt creation can occur after RNG construction or can overwrite an
  existing receipt.
- Projected or actual runtime misses its Task 4 gate; do not tune evidence.

## Definition Of Ready For Task 4

Task 3 is ready only when all tracked analytical files are complete, all Task 3
tests and the amended provenance tests pass without a Goal 023 holdout payload,
the CLI phase graph is exact, the runtime benchmark is implemented but not yet
used to expose science, two fixture bundles are byte-identical, visuals/report
pass disk-first review, and all independent reviews have no open Critical or
Important finding. Task 4 then owns the live benchmark, full calibration,
config emission, review, and immutable tracked-state freeze.
