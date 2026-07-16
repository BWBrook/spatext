# Goal 023 Integrated Amendment Final Rereview 2

Date: 2026-07-12  
Profile: `sol_max_auditor`  
Mode: fresh independent adversarial rereview, read-only except this ignored report

## Claim Audited

This rereview audits the exact current Goal 023 tuple and asks whether the
integrated amendment now implements the complete pre-Task-3 contract strongly
enough to authorize Task 3. Reports were treated as leads, not proof. The
current Goal, Plan, Runbook, authoritative spec, source receipt, source, tests,
and complete Log were read independently.

The binary decision rule is the one specified by Barry: Task 3 is authorized
only if no Critical or Important finding remains.

## Binary Verdict

**NOT SUPPORTED. Task 3 is NOT AUTHORIZED.**

One Critical and four Important findings remain. Task 3, RNG construction,
calibration, config emission, artifact generation, receipt creation, freeze,
and holdout remain **BLOCKED**.

The exact 98-test amendment matrix is green, and several prior defects are
genuinely repaired. That green result is not sufficient: fresh executable
counterexamples cross the post-receipt pre-RNG boundary on a disk-inconsistent
identity tuple and expose additional contract gaps while all 98 named tests
continue to pass.

| ID | Severity | Result |
| --- | --- | --- |
| C1 | Critical | Self-consistent config/receipt identities need not bind the captured analytical disk state; the post-receipt guard then calls the RNG factory. Malformed pre-receipt payloads also leave a newly created receipt on disk. |
| I1 | Important | All 98 names exist and pass, but several assigned behaviors remain absent from the named tests and production helpers. |
| I2 | Important | Split authority, complete fit frames, fit-to-control reconciliation, predictive row schema, and reducer contradiction handling remain incomplete. |
| I3 | Important | Latent row typing and recommendation neutrality are repaired, but the alleged canonical cell-ID frame is still supplied by the caller and can be forged. |
| I4 | Important | Artifact set checks and canonical reloads improved, but config literals, observed side effects, staging blobs, retries, publication transitions, and terminal exact-once state remain caller-asserted. |

## Findings

### Critical C1: A disk-inconsistent identity tuple crosses the post-receipt pre-RNG boundary

The current implementation now captures Git and disk state and revalidates it
(`latent_response_observation_recovery.py:7024-7090`). It also parses both
`--phase calibration` and `--phase=calibration` (`:6868-6890`), reloads typed
config and receipt identities from current bytes (`:6759-6865`), and uses an
exclusive receipt write (`:6783-6796`, `:7132-7149`). Those are real repairs.

The remaining boundary defect is narrower and more serious:

1. `require_phase_identities()` cross-binds config, preholdout receipt, and
   holdout receipt only to each other (`:6854-6865`).
2. `guard_holdout_post_receipt()` never compares their
   `tracked_state_sha256` or tracked-file manifest with
   `guard.analytical_sha256` and `guard.analytical_entries` captured from the
   live repository (`:7152-7167`).
3. Therefore a canonical, self-consistent, current-byte identity tuple that is
   inconsistent with the captured analytical disk state is accepted and the
   supplied RNG factory is called.
4. `guard_holdout_pre_receipt()` writes first and validates the resulting
   receipt second (`:7146-7148`). A malformed new payload raises, but the
   receipt remains on disk. The contract requires every pre-receipt failure to
   create neither receipt nor RNG object.

This bounded executable counterexample uses only temporary files and a list
append as an RNG-factory spy. It constructs no NumPy RNG, seed vector,
simulation, calibration, artifact, freeze, or holdout payload.

```bash
uv run python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from runpy import run_path

ns = run_path('tests/test_synth_medium_latent_response_observation_recovery.py')
core = ns['_core']()

with TemporaryDirectory() as td:
    tmp = Path(td)
    root = tmp / 'post'
    _, _ = ns['_phase_tree'](core, root, 'post_receipt')
    config_path = tmp / 'forged-config.json'
    core.write_canonical_config(config_path, ns['_valid_config_payload'](core))
    config = core.load_frozen_config_identity(config_path)
    pre_path = root / core.PUBLICATION_PATHS[-2]
    pre_path.write_bytes(core.canonical_json_bytes(ns['_preholdout_payload'](core, config)))
    pre = core.load_receipt_file_identity(pre_path)
    holdout_path = root / core.PUBLICATION_PATHS[-1]
    core.write_canonical_receipt(holdout_path, ns['_holdout_receipt_payload'](core, config))
    git_runner = ns['_phase_tree'](core, root, 'post_receipt')[0].git_runner
    guard = core.capture_phase_guard(root, 'post_receipt', git_runner=git_runner)
    calls = []
    result = core.guard_holdout_post_receipt(
        guard, holdout_path, config=config, preholdout_receipt=pre,
        rng_factory=lambda: calls.append('rng'))
    print('post_receipt_disk_digest_matches_config=',
          guard.analytical_sha256 == config.payload['tracked_state_sha256'])
    print('post_receipt_result=', result)
    print('rng_factory_calls=', len(calls))

with TemporaryDirectory() as td:
    tmp = Path(td)
    root = tmp / 'pre'
    initial, _ = ns['_phase_tree'](core, root, 'pre_receipt')
    config_path = tmp / 'config.json'
    core.write_canonical_config(
        config_path,
        ns['_valid_config_payload'](
            core, tracked_state_sha256=initial.analytical_sha256))
    config = core.load_frozen_config_identity(config_path)
    pre_path = root / core.PUBLICATION_PATHS[-2]
    pre_path.write_bytes(core.canonical_json_bytes(
        ns['_preholdout_payload_for_guard'](config, initial)))
    guard = core.capture_phase_guard(
        root, 'pre_receipt', git_runner=initial.git_runner)
    pre = core.load_receipt_file_identity(pre_path)
    receipt = root / core.PUBLICATION_PATHS[-1]
    calls = []
    try:
        core.guard_holdout_pre_receipt(
            guard, receipt, config=config, preholdout_receipt=pre,
            receipt_payload={'exposed': True},
            rng_factory=lambda: calls.append('rng'))
    except Exception as error:
        print('pre_receipt_exception=', type(error).__name__)
    print('malformed_receipt_left_on_disk=', receipt.exists())
    print('pre_receipt_rng_factory_calls=', len(calls))
PY
```

Observed on the audited tuple:

```text
post_receipt_disk_digest_matches_config= False
post_receipt_result= CONTINUE_FROZEN_CANDIDATE
rng_factory_calls= 1
pre_receipt_exception= ValueError
malformed_receipt_left_on_disk= True
pre_receipt_rng_factory_calls= 0
```

This directly falsifies the no-RNG-on-every-malformed-state claim. C1 remains
Critical even though no real Goal 023 RNG has yet been constructed.

### Important I1: The exact 98 names pass, but assigned behavior coverage remains incomplete

The proposal assigns 98 behaviors in six groups: T3A 11, T3L 20, T3D 14, T3R
20, T3S 10, and T3P 23. AST inventory confirms 98 unique required names, 98
definitions, no missing name, and no duplicate name. The exact matrix passes.

The proposal's printed suggested selector is not the exact matrix: it selects
only 88 tests. T3P-014 through T3P-023 are omitted by name. The expanded exact
selector below selects all 98.

Fresh review of every assigned group found behavior-name mismatches that remain
observable in production:

- T3A-005/007/010 do not reject nonnested calibration fits, incomplete arrival
  split frames, or mixed-split observed equal-emission pairs.
- T3L-011/014/017 nominate `range(n)` as both the claimed canonical frame and
  the tested analyst/evaluator frame. They never compare against the actual
  landscape, sparse, or alignment-score authority IDs.
- T3D-013 does not require the 24 zero-driver intervals to reconcile to 24
  zero-driver fit/profile rows. T3D-014 asserts a 10-field substitute mapping,
  not the literal 17-column predictive artifact row.
- T3R-010/011/012/017/019 do not reject all contradictory availability and
  forced-warning combinations; the equal-emission reducer ignores fit
  availability, and dropout/frailty reducers ignore `warning_forced` when
  `narrow_wrong=false`.
- T3S-004 validates a test helper whose parameter objects are incomplete and
  whose frozen gate literals are wrong. T3S-006 observes only injected callbacks
  plus a caller-supplied external sequence, leaving an uninstrumented service
  closure invisible.
- T3P-004/016/017/022 do not bind a retry to the failed command, derive staging
  blobs from live Git state, validate real ref forms and transition semantics,
  or maintain exact-once terminal state outside a caller boolean.

The executable counterexamples in C1 and I2-I4 all pass through current
production helpers while the exact 98 matrix is green. The matrix therefore
does not establish the assigned behavioral claim.

### Important I2: Fit, denominator, predictive, and reducer contracts accept contradictory evidence

Several earlier fit defects are repaired: the registry fit scope and permitted
variants are now enforced (`:5528-5539`); successful fit parameter subsets,
boundary states, best-two agreement, and arrival scores are typed
(`:5540-5621`); duplicate fit keys are rejected (`:5648-5666`); arrival pair
duplicates are rejected (`:5669-5705`); and observed plus all 199 bootstrap
pairs are recomputed (`:5716-5762`).

The remaining gaps are independently executable:

- The literal scenario registry assigns 24 calibration replicates to all seven
  nonnested scenarios (`:5433-5435`), contrary to Goal lines 949-960 and
  1056-1061. `_split_replicate_count()` likewise authorizes calibration for
  every scenario (`:5818-5825`).
- `validate_arrival_fit_pairs()` accepts any nonempty set of complete pairs. It
  does not require the complete 12-development or 24-holdout pair frame.
- Equal-emission recomputation groups bootstrap rows only by bundle index and
  does not require the two observed fits, or each pair, to share one split.
- `reconcile_control_summary()` receives zero-driver intervals separately and
  never resolves them to zero-driver fit/profile evidence (`:6224-6281`).
- A failed fit row leaves `best_two_log_likelihoods_agree` untyped
  (`:5622-5644`).
- `failed_predictive_rows()` emits 27 rows, but not the literal 17-column
  artifact schema; it substitutes `warning`, omits eight required fields, and
  labels strata `1..5` and `1..3` rather than `q1..q5` and
  `early|middle|late` (`:6284-6310`; Goal lines 1411-1420 and 1734-1736).
- The equal-emission reducer ignores required fit/predictive/plugin
  availability (`:6428-6439`). Dropout and frailty accept a caller-forced
  warning whenever `narrow_wrong=false` (`:6440-6455`).

Executable counterexample:

```bash
uv run python - <<'PY'
from runpy import run_path
ns = run_path('tests/test_synth_medium_latent_response_observation_recovery.py')
core = ns['_core']()
success = ns['_successful_fit_row']

print('nonnested_calibration_counts=', {
    row.scenario_id: row.calibration_replicates
    for row in core.SCENARIO_DEFINITIONS
    if row.scenario_id not in core.NESTED_SCENARIOS})
sparse_cal = success(
    core, scenario_id='sparse_expected_failure', split_id='calibration')
print('sparse_calibration_fit_accepted=',
      core.validate_fit_execution_row(sparse_cal)['split_id'])

fit_ids, score_ids = tuple(range(4180)), tuple(range(4180, 5225))
arrival_pair = tuple(success(
    core, scenario_id='permuted_arrival_alignment_stress',
    fit_variant=variant, heldout_log_score=-1.0)
    for variant in ('correct_alignment', 'permuted_alignment'))
print('one_of_24_arrival_pair_count_accepted=',
      core.validate_arrival_fit_pairs(
          arrival_pair, fit_cell_ids=fit_ids, score_cell_ids=score_ids,
          canonical_fit_cell_ids=fit_ids,
          canonical_score_cell_ids=score_ids))

equal = list(ns['_equal_fit_rows'](core))
equal[0] = equal[0] | {
    'split_id': 'development',
    'source_replicate_last': 11,
    'source_replicate_count': 12}
recomputed = core.recompute_equal_emission_bootstrap(equal)
print('mixed_observed_splits=', tuple(row['split_id'] for row in equal[:2]))
print('mixed_split_equal_bootstrap_p=', recomputed['p_value'])

arrival_rows = tuple(success(
    core, scenario_id='permuted_arrival_alignment_stress', split_id='holdout',
    fit_variant=variant, fit_index=index,
    source_replicate_first=index, source_replicate_last=index,
    heldout_log_score=-1.0 if variant == 'correct_alignment' else -2.0)
    for index in range(24)
    for variant in ('correct_alignment', 'permuted_alignment'))
fit_rows = (*arrival_rows, *ns['_equal_fit_rows'](core))
summary = core.reconcile_control_summary(
    zero_intervals=tuple([(-1.0, 1.0)] * 24), fit_rows=fit_rows)
zero_rows = [row for row in fit_rows
             if row['scenario_id'] == 'zero_driver_effect_negative_control']
print('zero_driver_fit_rows_supplied=', len(zero_rows),
      'zero_evaluable_returned=', summary['zero_evaluable'])

failed = ns['_fit_row'](
    core, best_two_log_likelihoods_agree='not-a-bool')
print('malformed_failed_fit_state_accepted=',
      core.validate_fit_execution_row(failed)['best_two_log_likelihoods_agree'])

rows = core.failed_predictive_rows(
    scenario_id='dense_count_exact_model', split_id='holdout', replicate_id=0)
header = {
    'scenario_id', 'split_id', 'replicate_id', 'fit_variant', 'stratum_type',
    'stratum_value', 'metric_id', 'sample_size', 'fit_succeeded',
    'diagnostic_available', 'observed_value', 'reference_mean', 'reference_sd',
    'reference_mcse', 'standardized_residual',
    'standardized_residual_nonfinite', 'randomized_pit'}
print('failed_predictive_missing_fields=', sorted(header - set(rows[0])))
print('failed_predictive_extra_fields=', sorted(set(rows[0]) - header))
print('failed_predictive_strata=', sorted({
    (row['stratum_type'], row['stratum_value']) for row in rows}))

passing = ns['_passing_evidence']()
print('forced_dropout_warning_result=', core.reduce_scenario(
    'informative_dropout_misspecification_stress',
    passing | {'warning_forced': True}))
print('unavailable_equal_fit_result=', core.reduce_scenario(
    'no_emission_contrast_negative_control',
    passing | {'fit_available': False}))
PY
```

Observed:

```text
nonnested_calibration_counts= {'sparse_expected_failure': 24, 'zero_driver_effect_negative_control': 24, 'permuted_arrival_alignment_stress': 24, 'no_emission_contrast_negative_control': 24, 'informative_dropout_misspecification_stress': 24, 'goal018_continuous_abundance_stress': 24, 'spatial_frailty_stress': 24}
sparse_calibration_fit_accepted= calibration
one_of_24_arrival_pair_count_accepted= 1
mixed_observed_splits= ('development', 'holdout')
mixed_split_equal_bootstrap_p= 1.0
zero_driver_fit_rows_supplied= 0 zero_evaluable_returned= 24
malformed_failed_fit_state_accepted= not-a-bool
failed_predictive_missing_fields= ['observed_value', 'randomized_pit', 'reference_mcse', 'reference_mean', 'reference_sd', 'sample_size', 'standardized_residual', 'standardized_residual_nonfinite']
failed_predictive_extra_fields= ['warning']
failed_predictive_strata= [('all', 'all'), ('habitat_quality_quintile', '1'), ('habitat_quality_quintile', '2'), ('habitat_quality_quintile', '3'), ('habitat_quality_quintile', '4'), ('habitat_quality_quintile', '5'), ('time_band', '1'), ('time_band', '2'), ('time_band', '3')]
forced_dropout_warning_result= pass
unavailable_equal_fit_result= pass
```

These are contract failures, not merely missing optional test cases. I2 remains
Important.

### Important I3: Latent diagnostics accept a caller-forged canonical cell-ID frame

The latent numeric kernel remains correct. The fixed event/censor categories,
Brier score, scaled interval score, median absolute error, expected-value
calculations, and complete typed diagnostic row state are now validated
(`:5836-6094`). Recommendation neutrality is explicit because
`reduce_recommendation()` discards `latent_rows` (`:6458-6465`), as required.

The frame authority is still circular. `build_latent_diagnostic_rows()` checks
that analyst IDs and evaluator IDs equal the caller's `canonical_cell_ids` and
that its length equals the registry cardinality (`:5980-6004`). It never derives
or verifies those IDs against the actual passable landscape, the deterministic
sparse frame, or the deterministic alignment-score frame.

Executable counterexample, using only deterministic landscape construction and
fixed one-hot arrays:

```bash
uv run python - <<'PY'
from importlib import import_module
from runpy import run_path
import numpy as np

ns = run_path('tests/test_synth_medium_latent_response_observation_recovery.py')
core = ns['_core']()
landscape = import_module(
    'spatext.synth.medium.landscape').build_synth_medium_landscape()
actual = tuple(sorted(
    cell.cell_id for cell in landscape.cells if cell.passability != 'water'))
forged = tuple(range(5225))
rows = core.build_latent_diagnostic_rows(
    scenario_id='dense_count_exact_model', split_id='holdout', replicate_id=0,
    fit_succeeded=True, cell_ids=forged,
    path_probabilities=np.tile(ns['_one_hot'](0), (5225, 1)),
    truth_transition_times=tuple([6] * 5225),
    evaluator_cell_ids=forged, canonical_cell_ids=forged,
    prerequisite_valid=True)
core.validate_latent_diagnostic_rows(rows)
print('forged_frame_equals_actual_passable_frame=', forged == actual)
print('forged_frame_available=',
      all(row['diagnostic_available'] for row in rows))
print('forged_min_max=', (min(forged), max(forged)),
      'actual_min_max=', (min(actual), max(actual)))
vector = {scenario_id: 'pass' for scenario_id in core.SCENARIO_IDS}
print('recommendation_neutral=',
      core.reduce_recommendation(vector, latent_rows=rows)
      == core.reduce_recommendation(vector))
PY
```

Observed:

```text
forged_frame_equals_actual_passable_frame= False
forged_frame_available= True
forged_min_max= (0, 5224) actual_min_max= (0, 6047)
recommendation_neutral= True
```

The cardinalities and typed row states are correct, and recommendation
neutrality is correct. Exact cell-ID authority is not. I3 remains Important.

### Important I4: Config, fixture, staging, retry, transition, and terminal guards remain caller-asserted

The artifact set itself is substantially repaired:

- represented artifact validation requires the literal 21 represented paths;
- the complete external snapshot requires the literal 22-file set and rejects
  extras, symlinks, missing files, and zero-byte files;
- config and receipt loaders require canonical bytes, self-hashes, exact
  top-level key sets, and current-byte reloads;
- phase presence vectors require exactly 17, 18, and 19 paths at the three
  boundaries.

The following interfaces still fail the full contract:

1. `_validate_config_schema()` requires only a nonempty list of mapping objects
   for `parameters` (`:6668-6674`), not every typed
   `model_parameter_contract.csv` field required by Goal lines 2084-2085. Gate
   values are checked only by broad type (`:6684-6696`), not against the frozen
   literals. The test helper itself uses coverage gate count 5 rather than 15,
   negative false-positive rate 0.05 rather than 0.10, sparse alpha 0.10 rather
   than 0.05, and PIT familywise alpha 0.05 rather than 0.01 (Goal lines
   1288-1299 and 1337-1338).
2. `dispatch_fixture_calibration()` observes only callbacks supplied in the
   `side_effects` mapping and a caller-supplied `observed_rng_calls` sequence
   (`:7296-7343`). A service can call an external closure and report no side
   effects.
3. `validate_exact_staging()` derives the literal path set from
   `STAGING_PATHS`, but trusts all blob digests in the caller-constructed
   `before.candidate_entries` (`:7176-7188`). It does not capture or compare the
   actual Git index/worktree blobs.
4. `authorize_retry()` has no prior failed-command argument and therefore
   cannot prove the retry command is exact (`:6961-6978`).
5. `validate_publication_transition()` accepts arbitrary strings as refs and a
   caller boolean for tree equality; it does not prove commit/merge/push-specific
   Git semantics (`:7191-7209`).
6. `terminal_attestation_payload()` omits several complete-envelope members,
   and `apply_terminal_attestation()` delegates exact-once state to the caller's
   `already_appended` boolean (`:7252-7288`). The same operation is accepted
   twice when the caller repeats `False`.

Executable counterexample:

```bash
uv run python - <<'PY'
from json import loads
from pathlib import Path
from runpy import run_path
from tempfile import TemporaryDirectory

ns = run_path('tests/test_synth_medium_latent_response_observation_recovery.py')
core = ns['_core']()

with TemporaryDirectory() as td:
    path = Path(td) / 'config.json'
    core.write_canonical_config(path, ns['_valid_config_payload'](core))
    config = core.load_frozen_config_identity(path)
    print('incomplete_parameter_objects_accepted=',
          config.payload['parameters'][0])
    print('wrong_frozen_gate_values_accepted=', {
        key: config.payload['gates'][key]
        for key in ('coverage_gate_count', 'negative_false_positive_rate',
                    'sparse_coverage_alpha', 'pit_familywise_alpha')})

calls = []
def external_rng():
    calls.append('rng')
def service(**_):
    external_rng()
    return dict(core.FIXTURE_ZERO_COUNTERS)
with TemporaryDirectory() as td:
    result = core.dispatch_fixture_calibration(
        workers=1, output_dir=Path(td),
        services={'run_fixture_tasks': service})
print('unobserved_external_side_effect_calls=', len(calls),
      'dispatcher_result=', result)

blobs = tuple((path, '0' * 64) for path in core.STAGING_PATHS)
before = ns['_envelope'](core, candidate_entries=blobs)
after = ns['_envelope'](core, candidate_entries=blobs, staged=blobs)
core.validate_exact_staging(before, after)
print('caller_forged_staging_blobs_accepted=', len(blobs))

print('different_retry_commands_each_authorized=', (
    core.authorize_retry(
        command=('pytest', 'A'), command_class='validation', retry_count=0,
        independent_approval=True, unchanged_envelope=True),
    core.authorize_retry(
        command=('pytest', 'B'), command_class='validation', retry_count=0,
        independent_approval=True, unchanged_envelope=True)))

print('non_sha_publication_ref_accepted=',
      core.validate_publication_transition(
          'commit', parent=core.PINNED_COMMIT,
          before_ref=core.PINNED_COMMIT, after_ref='not-a-sha',
          approved_ref='not-a-sha', tree_matches=True))

payload = core.terminal_attestation_payload(before)
document = loads(payload)
complete_state = {
    'analytical_entries', 'cached_entries', 'staged',
    'tracked', 'unstaged', 'untracked'}
print('terminal_attestation_missing_state=',
      sorted(complete_state - set(document)))
first = core.apply_terminal_attestation(
    before, payload, reviewed_payload=payload, already_appended=False)
second = core.apply_terminal_attestation(
    before, payload, reviewed_payload=payload, already_appended=False)
print('same_attestation_call_accepted_twice=', first == second)
PY
```

Observed:

```text
incomplete_parameter_objects_accepted= {'parameter_id': 'alpha'}
wrong_frozen_gate_values_accepted= {'coverage_gate_count': 5, 'negative_false_positive_rate': 0.05, 'sparse_coverage_alpha': 0.1, 'pit_familywise_alpha': 0.05}
unobserved_external_side_effect_calls= 1 dispatcher_result= {'holdout_payload_instantiated': False, 'scientific_rows_emitted': False, 'rng_factory_call_count': 0, 'canonical_output_write_count': 0}
caller_forged_staging_blobs_accepted= 19
different_retry_commands_each_authorized= (('pytest', 'A'), ('pytest', 'B'))
non_sha_publication_ref_accepted= True
terminal_attestation_missing_state= ['analytical_entries', 'cached_entries', 'staged', 'tracked', 'unstaged', 'untracked']
same_attestation_call_accepted_twice= True
```

I4 remains Important.

## Prior Finding Rereview

| Prior finding | Fresh disposition on the exact current tuple |
| --- | --- |
| C1 captured Git/disk phase state, parser, exclusive receipt, complete identities, zero RNG | Git/disk capture, revalidation, phase parser, typed canonical reload, and exclusive nonreplacement are repaired. Live analytical-state cross-binding and validate-before-create are not; C1 remains Critical. |
| I1 all 98 assigned behaviors | All 98 names and a green exact matrix are confirmed. Multiple assigned counterexamples are still absent and executable; I1 remains Important. |
| I2 fit scope/variants, complete rows, pairs, bootstrap, denominators, local reasons | Registry scope/variants, successful row typing, duplicate rejection, bootstrap count, and canonical local-reason domains improved. Split legality, complete pair frames, same-split pairing, failed/predictive row typing, cross-table denominators, and contradiction rejection remain open; I2 remains Important. |
| I3 exact latent frames/cardinalities, typed states, recommendation neutrality | Cardinalities, typed row state, numeric formulas, and neutrality are repaired. Exact cell-ID authority remains caller-forged; I3 remains Important. |
| I4 artifact sets, canonical identities, observed side effects, staging, retry/transition/terminal guards | Literal represented/complete sets and canonical current-byte reloads are repaired. Full config literals and the operational provenance guards remain open; I4 remains Important. |

## Exact Tuple And Chain

The current tuple reproduced exactly:

| Object | SHA-256 / size |
| --- | --- |
| source | `421f0a9b9082c3c66002ce446a2444510b10a0205645e716de048ccda54bc116` |
| tests | `dede165ea37c7fc2fb8709b00c72c45001bba2e7a42d5419b4d36696e2774f05` |
| Log | `9d6d8b0265720e7eef6102bdc6e8271517b030bdd1c29018c995d7b7d6d8e768`; 2555 lines; 126506 bytes |
| Goal | `6883c0188be06c328f09a4e07a9872b366e414abac31bc5241b7d5c72f6b8e3f` |
| Plan | `65e90dc237225d1f26e28064af2947738d1bb24ddfee742b720b425172a9bf84` |
| Runbook | `fc74fae83c6e93701a06d342346ffe803360fb718f2ed34f69bcb610103a7e7b` |
| authoritative spec | `af04446473b60af8280fcc4533c0550c60ad8605ea88802720d3d80558d1ac8e` |
| source receipt | `5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb` |
| amendment proposal | `ee367b6014bf823ffda2f406186179271a0f0e56ac955ea35ae6fb11c3bea15d` |

Goal and authoritative-spec bodies from `Objective` onward are byte-identical:
106597 bytes, SHA-256
`855a3c3291dedf473fc1879601987f6126924e71123e4aa515b86805a3bb93eb`.

The full Log was read. All 14 parent-bound records reproduce both their parent
byte counts and SHA-256 values: `records=14 hash_ok=14 byte_ok=14`. The live
parent chain ends at the exact 2555-line, 126506-byte Log tuple above.

Repository identity reproduced as:

```text
branch: codex/spatext-goal023-latent-response-observation-gate
HEAD:   53462d0365babf2c8070714a930f69b4071af276
base:   53462d0365babf2c8070714a930f69b4071af276 (origin/main)
index:  empty
```

No exposure state was found. The Goal 023 artifact directory,
`recovery_gate_config.json`, `preholdout_state_receipt.json`, and
`holdout_receipt.json` are absent. No production RNG, RNG vector, Task 3,
benchmark, calibration, config emission, artifact writer, receipt phase,
freeze, or holdout command was run by this rereview. The required exact tests
and bounded counterexamples did invoke fixture-only canonical serializers,
loaders, and bundle helpers under automatically removed OS temporary
directories; none wrote a Goal 023 production path.

## Bounded Validation

The proposal's suggested selector was run first and proved incomplete:

```text
88 passed, 209 deselected in 0.47s
```

The exact expanded amendment selector was then run:

```bash
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py \
  -k 'lro_3a or lro_3l or lro_3d or lro_3r or lro_3s or post_exposure or config_emission or freeze_fails or holdout_pre_receipt or holdout_post_receipt or holdout_success or holdout_and_artifact_generating or allowed_new_candidate_paths or exact_staging or authorized_commit_merge_and_push or candidate_footprint_presence_vector or supersession_record or holdout_receipt_exposure_fields or task6_validation_dispatch or terminal_attestation or potentially_mutating_hooks' \
  --no-cov
```

Observed:

```text
98 passed, 199 deselected in 0.49s
```

Bounded static checks:

```text
AST required-name inventory: required=98 unique_required=98 defined_required=98 missing=[] duplicates=[]
uv run ruff format --check <source> <tests>: 2 files already formatted
uv run ruff check <source> <tests>: All checks passed!
uv run mypy src tests: Success: no issues found in 59 source files
git diff --check: pass
```

Broader tests were not rerun. They were unnecessary to resolve the authorization
claim after the direct C1 counterexample and the independent I2-I4
counterexamples falsified it. Prior reported broader-test results were not used
as proof.

## Complete Correction Sequence

1. Keep Task 3, RNG, calibration, config emission, artifacts, receipts, freeze,
   and holdout blocked. Do not append acceptance to the Log.
2. Repair C1 first. At every config/freeze/pre-receipt/post-receipt boundary,
   compare config and receipt `tracked_state_sha256` and the literal tracked
   manifest against the current captured `PhaseGuardState`, not merely against
   one another. Revalidate immediately before any RNG factory call.
3. Validate the complete holdout receipt payload and all config/preholdout/live
   disk cross-bindings before the exclusive create. A malformed new payload
   must leave no receipt. Preserve pre-existing bytes on every failure.
4. Make config validation literal: require every typed parameter-contract field,
   exact parameter order/values/supports, exact seed partitions, exact gate
   objects and thresholds, and exact model/estimator/scenario values. Add direct
   tests for 15, 0.10, 0.05, and 0.01 at their frozen keys.
5. Make split authority scenario-specific. Nonnested scenarios have development
   12 and holdout 24 only; reject every calibration row and RNG payload for
   them. Require exact complete split frames, not merely in-range individual
   rows.
6. Require arrival pairs for the complete applicable split and require both
   variants for each replicate exactly once. Require observed equal-emission
   fits and every bootstrap pair to share scenario, split, source range, and
   fit identity before recomputation.
7. Reconcile every zero-driver interval to exactly one zero-driver primary fit
   and profile row. Validate every failed fit field, and emit/validate the
   literal 17-column predictive row with `q1..q5`,
   `early|middle|late`, typed nulls, and all 27 stable cells.
8. Make each local reducer validate a complete scenario-specific evidence
   schema and reject contradictory fields. Equal emission must require fit and
   bootstrap availability. Forced warnings must never satisfy dropout,
   continuous-abundance, or frailty warning requirements. Preserve the now
   correct scenario-specific canonical reason domains and rank precedence.
9. Replace caller-supplied `canonical_cell_ids` authority with an internally
   derived or separately validated typed frame identity bound to the actual
   passable landscape, deterministic sparse frame, or deterministic alignment
   score frame. Keep the repaired row typing and recommendation neutrality.
10. Observe fixture side effects at the service boundary that owns all callable
    paths; do not accept caller-supplied external counters as proof. A service
    closure that reaches any RNG/live runner/output writer must fail.
11. Capture staging blobs from live Git/worktree state and compare the resulting
    index to the literal allowlist and frozen blob map. Bind a retry to the exact
    failed command and unchanged captured envelope. Implement transition-specific
    Git checks with valid object IDs, parent/tree/ref semantics, and live state.
12. Include the complete terminal envelope in the reviewed attestation and
    enforce exact-once append/stage through observed Log/index state, not an
    `already_appended` argument.
13. Rewrite every affected T3A/T3L/T3D/T3R/T3S/T3P named test to contain the
    counterexample assigned by the proposal. Obtain genuine behavior-specific
    RED results, implement to GREEN, and replace the proposal's 88-test selector
    with an exact 98-test command or node-ID manifest.
14. Rerun the complete non-generative validation ladder, reseal every current
    hash, append a new parent-bound repair child only after review, and obtain a
    fresh independent max-tier rereview of the exact new tuple.

## Stop Rule

The authorization gate is binary and currently failed. No Critical or Important
finding may be waived by the green 98-test matrix, by prior broader test runs,
or by the fact that holdout has not yet been exposed. The next legitimate state
is a bounded RED-GREEN repair and another hash-specific independent rereview,
not Task 3.
