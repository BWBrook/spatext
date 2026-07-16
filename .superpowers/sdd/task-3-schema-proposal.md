# Goal 023 Task 3 Schema And Evidence Amendment Proposal

status: `PATCH_READY_AUTHORITY_AMENDMENT_PROPOSAL`
date: `2026-07-11`
worktree: `/Users/bwbrook/.codex/worktrees/spatext/goal023`
branch: `codex/spatext-goal023-latent-response-observation-gate`
HEAD/base: `53462d0365babf2c8070714a930f69b4071af276`

## Scope And Non-Execution Boundary

This proposal closes the Task 3 schema and evidence-identity gaps identified in:

- `.superpowers/sdd/task-3-scenario-gate-preflight.md`; and
- `.superpowers/sdd/task-3-artifact-cli-preflight.md`.

It is a document-only, pre-simulation proposal. It does not edit authority or
production files, construct a scientific row, instantiate a calibration or
holdout payload, run an optimizer or profile, generate an artifact, create a
receipt, or alter the accepted Goal 023 hash chain.

The inspected authority tuple reproduces exactly:

```text
Goal     cda5595ee70bdb3e59658625fcd1724fda139ad6115903b2531f807b2b52de20
Plan     df98874e95a1ed910ae115097bdcbfdbd80dc5850328953cc4aa7ffa9416754e
Runbook  78698fc40fb106163225cf945c79f3fd00979d86625494d60b058882134bd5ed
spec     0ce393b7fdd3e80da242716408e9849601d3c2c1d0cc6abbbae4c6b2454ff48d
receipt  5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb
```

Task 2a is accepted. Task 2b remains pending. Task 3 remains blocked until the
future Task 2b handoff and the authority amendments proposed here and in the
holdout-provenance proposal are independently accepted against replacement
hashes.

## Recommendation

Use one additive, typed fit-level CSV and add one literal `fit_variant` key to
fit-derived tables. This is the smallest amendment that represents:

- both correct- and permuted-arrival fits without pretending that the correct
  comparator is a recovery/profile target;
- the equal-emission equal-rate and ordered shared fits at scenario and
  bootstrap-bundle scope without a fake `replicate_id`;
- convergence and failure evidence for every attempted fit; and
- direct recomputation of arrival wins and equal-emission likelihood-ratio
  statistics from emitted rows.

Do not encode shared fits with nullable primary-key components, negative
replicate sentinels, JSON hidden in `interpretation`, or a result-selected
profile policy.

Three approaches were considered:

1. **Recommended: add `fit_execution_evidence.csv` and explicit variants.**
   Existing recovery, coverage, profile, predictive, and control meanings stay
   intact. The exact bundle grows from 21 to 22 files.
2. **Overload `control_decision_summary.csv`.** This avoids one file but mixes
   per-fit parameter vectors, scenario gates, parameter statuses, and the final
   decision under one arbitrary string key. It is harder to validate and makes
   convergence evidence easy to hide.
3. **Broaden `replicate_recovery.csv` with nullable/sentinel replicate IDs.**
   This falsely labels shared equal-emission fits as replicate recovery and
   makes a literal non-null primary key impossible without an opaque sentinel.

Approach 1 is additive, auditable, and does not change any estimator, seed,
replicate count, scientific threshold, or existing parameter-recovery claim.

## Normative Amendment Text

The following sections are patch-ready normative text. Insert materially
identical text into both `Goal.md` and the authoritative spec. The schema
sections below replace the corresponding Source And Artifact Contracts text;
the Plan and Runbook changes are listed separately.

### 1. Scenario Evidence Registry

Freeze the following 11-row mapping. `primary_fit_variant` is the only variant
allowed in recovery, coverage, latent-time, profile, and predictive rows unless
an applicability rule below says no row exists. Comparator fits remain visible
in `fit_execution_evidence.csv` but cannot silently enter a primary diagnostic.

| Scenario | Truth access | Fit scope | Primary variant | Comparator variant | Parameter recovery | Latent-time rows |
| --- | --- | --- | --- | --- | --- | --- |
| `process_oracle_observed_transition` | `oracle_only` | `replicate` | `canonical` | none | gated, 3 parameters | not applicable |
| `observation_oracle_fixed_transition` | `oracle_only` | `replicate` | `canonical` | none | gated, 2 rates | not applicable |
| `dense_count_exact_model` | `analyst_firewalled` | `replicate` | `canonical` | none | gated, 5 parameters | descriptive, simulated binary truth |
| `structured_imperfect_effort` | `analyst_firewalled` | `replicate` | `canonical` | none | gated, 5 parameters | descriptive, simulated binary truth |
| `sparse_expected_failure` | `analyst_firewalled` | `replicate` | `canonical` | none | dedicated `beta_driver` gate; other rows descriptive | descriptive, simulated binary truth |
| `zero_driver_effect_negative_control` | `analyst_firewalled` | `replicate` | `canonical` | none | control/descriptive | descriptive, simulated binary truth |
| `permuted_arrival_alignment_stress` | `stress_evaluator_only` | `replicate` | `permuted_alignment` | `correct_alignment` | primary variant descriptive only | descriptive on score cells |
| `no_emission_contrast_negative_control` | `analyst_firewalled` | `scenario_shared` | `equal_rate` | `ordered_emission` | no recovery/profile rows; fixed status rows only | not applicable |
| `informative_dropout_misspecification_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | descriptive, 5 known parameters | descriptive, simulated binary truth |
| `goal018_continuous_abundance_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | estimates/interval widths only; truth/error/coverage null | descriptive against Goal 018 quasi-extirpation |
| `spatial_frailty_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | descriptive, 5 known parameters | descriptive, simulated binary truth |

Truth-access meanings are literal:

- `oracle_only`: true transition/state fields may enter only the physically
  separate named oracle likelihood. They never enter joint fitting.
- `analyst_firewalled`: generation truth remains in the controller/evaluator;
  the fitted interface receives only analyst-visible fields. Evaluation may
  compare completed fits with generating truth.
- `stress_evaluator_only`: misspecification truth, frame membership, dropout,
  frailty, continuous abundance, and correct/permuted comparison state remain
  in a physically separate evaluator and are consulted only after the required
  fit has completed.

For the arrival stress, fixed true `TP(x)` is still an approved analyst
covariate for the correct comparator. The `stress_evaluator_only` label governs
variant pairing, score-frame evaluation, and truth-based descriptive rows; it
does not reclassify `TP(x)` as hidden biological truth.

Amend `scenario_definitions.csv` by appending three fields to the existing
header:

```text
fit_scope,primary_fit_variant,comparator_fit_variant
```

The complete schema is:

```text
scenario_id:str!
scenario_role:enum!
generation_model:enum!
fit_model:enum!
schedule_id:enum!
effort_rule:str!
development_replicates:int!
calibration_replicates:int!
holdout_replicates:int!
expected_behavior:enum!
truth_access_class:enum!
transportability_class:enum!
fit_scope:enum!
primary_fit_variant:enum!
comparator_fit_variant:enum?
```

Primary key: `scenario_id`.

Row order is the numbered 11-scenario contract order, not lexical scenario ID
order. This is an explicit exception to the general primary-key sort rule and
removes the existing preflight/schema-order contradiction.

Additional enum domains are:

```text
fit_scope = replicate|scenario_shared|bootstrap_shared
fit_variant = canonical|correct_alignment|permuted_alignment|equal_rate|ordered_emission
```

`bootstrap_shared` is not a scenario-definition row value. It is used only by
equal-emission bootstrap fit evidence.

### 2. Additive Fit-Execution Evidence

Add root artifact `fit_execution_evidence.csv` with literal header:

```text
scenario_id,split_id,fit_scope,fit_variant,fit_index,source_replicate_first,source_replicate_last,source_replicate_count,fit_succeeded,converged_start_count,best_start_index,best_two_log_likelihoods_agree,at_boundary,boundary_parameter_ids,alpha_estimate,beta_driver_estimate,beta_quality_estimate,lambda_quasi_estimate,lambda_present_estimate,lambda_equal_estimate,log_likelihood,heldout_log_score,failure_code
```

Literal schema:

```text
scenario_id:str!
split_id:enum!
fit_scope:enum!
fit_variant:enum!
fit_index:int!
source_replicate_first:int!
source_replicate_last:int!
source_replicate_count:int!
fit_succeeded:bool!
converged_start_count:int?
best_start_index:int?
best_two_log_likelihoods_agree:bool?
at_boundary:bool?
boundary_parameter_ids:str?
alpha_estimate:float?
beta_driver_estimate:float?
beta_quality_estimate:float?
lambda_quasi_estimate:float?
lambda_present_estimate:float?
lambda_equal_estimate:float?
log_likelihood:float?
heldout_log_score:float?
failure_code:str?
```

Primary key and row order:

```text
(scenario_id,split_id,fit_scope,fit_variant,fit_index)
```

String components sort lexically and `fit_index` sorts numerically. Duplicate
keys are forbidden.

Row constraints are literal:

- `fit_scope=replicate`: `fit_index=source_replicate_first=
  source_replicate_last=replicate_id` and `source_replicate_count=1`.
- `fit_scope=scenario_shared`: `fit_index=0`; equal-emission development uses
  source range `0..11` and count `12`; holdout uses `0..23` and count `24`.
- `fit_scope=bootstrap_shared`: only equal emission is legal;
  `fit_index=bundle_id` in `0..198`, source range `0..23`, and count `24`.
- The runtime timing-only equal bundle and timing-only bootstrap bundle emit no
  row because `scientific_row=false`.
- Every required multistart attempt emits exactly one row, whether successful
  or failed. `converged_start_count` is `0..8` and
  `best_start_index` is nullable `1..8`. `fit_succeeded=true` requires at least
  six successful starts, finite accepted output, and
  `best_two_log_likelihoods_agree=true`.
- The closed-form equal-rate fit has null start fields. A finite interior MLE
  has `fit_succeeded=true`. A clipped boundary MLE remains visible with its
  estimate, likelihood, `at_boundary=true`,
  `fit_succeeded=false`, and `failure_code=equal_rate_mle_noninterior`.
- `boundary_parameter_ids` is null when no accepted parameter is on a boundary;
  otherwise it is a `|`-delimited list in fixed parameter order with no spaces.
- A failed multistart fit may retain its start count, best-start index, and
  agreement flag, but accepted parameter estimates, fit likelihood, and
  heldout score are null. `failure_code` is required on every failed row and
  null on every successful row.
- Parameter estimate fields are populated only when that parameter belongs to
  the named fit. Process oracle populates three process fields; observation
  oracle populates two rate fields; ordinary ordered fits populate five fields;
  equal-rate fits populate only `lambda_equal_estimate`.
- Arrival emits two replicate-scope rows per attempted replicate, one for
  `correct_alignment` and one for `permuted_alignment`. Both are fit only on
  the fixed 4,180-cell fit frame and both `heldout_log_score` values are scored
  only on the fixed 1,045-cell score frame.
- An arrival paired win exists only when both required rows succeed and both
  heldout scores are finite, with the correct score strictly greater than the
  permuted score. A failed/missing pair is no win and separately fails the
  fit-availability gate; it cannot be dropped from 24 attempts.
- Equal emission emits two `scenario_shared` rows for the observed bundle and
  two `bootstrap_shared` rows per bundle. The two log likelihoods in each key
  pair must reproduce observed `D` and every `D_b` exactly. All 199 ordered
  bootstrap rows must have `fit_succeeded=true`.

This table is the sole fit-execution/convergence authority. Recovery and
profile tables remain scientific-parameter evidence and must reconcile to it;
they cannot invent or suppress a fit.

`report.md` must link this table directly. `control_comparison.svg` must read it
back from disk for arrival pair availability/scores and equal-emission observed
and bootstrap fit availability; live fit objects are not an alternative input.

### 3. Explicit Variant Keys In Fit-Derived Tables

Add required `fit_variant:enum!` immediately after the replicate or split key
in every fit-derived table below. The amended literal headers and primary keys
are:

```text
replicate_recovery.csv
scenario_id,split_id,replicate_id,fit_variant,parameter_id,truth_value,estimate,interval_lower,interval_upper,interval_width,converged,converged_start_count,at_boundary,profile_two_sided,truth_in_interval,log_likelihood,signed_error,absolute_error,gate_result
PK (scenario_id,split_id,replicate_id,fit_variant,parameter_id)

coverage_calibration.csv
scenario_id,split_id,fit_variant,parameter_id,replicate_count,converged_count,coverage_count,coverage_fraction,acceptance_lower_count,acceptance_upper_count,median_signed_error,median_absolute_error,median_interval_width,maximum_absolute_error,maximum_interval_width,gate_result
PK (scenario_id,split_id,fit_variant,parameter_id)

latent_time_calibration.csv
scenario_id,split_id,replicate_id,fit_variant,metric_id,truth_source,sample_size,fit_succeeded,diagnostic_available,observed_value,expected_value,error,gate_result
PK (scenario_id,split_id,replicate_id,fit_variant,metric_id)

predictive_replicate_diagnostics.csv
scenario_id,split_id,replicate_id,fit_variant,stratum_type,stratum_value,metric_id,sample_size,fit_succeeded,diagnostic_available,observed_value,reference_mean,reference_sd,reference_mcse,standardized_residual,standardized_residual_nonfinite,randomized_pit
PK (scenario_id,split_id,replicate_id,fit_variant,stratum_type,stratum_value,metric_id)

predictive_check_summary.csv
scenario_id,split_id,fit_variant,stratum_type,stratum_value,metric_id,replicate_count,diagnostic_count,failed_fit_count,mean_standardized_residual,stouffer_z,ks_statistic,raw_p,holm_adjusted_p,warning,gate_result
PK (scenario_id,split_id,fit_variant,stratum_type,stratum_value,metric_id)

identifiability_profiles.csv
scenario_id,split_id,replicate_id,fit_variant,parameter_id,grid_index,parameter_value,profile_log_likelihood,likelihood_ratio_delta,nuisance_converged,inside_interval
PK (scenario_id,split_id,replicate_id,fit_variant,parameter_id,grid_index)
```

The existing types and nullability remain unchanged except for the expanded
latent-time schema in section 4. General rows use `fit_variant=canonical`.
Arrival primary rows use `permuted_alignment`. Equal-emission predictive rows
use `equal_rate`. No recovery, coverage, latent-time, or profile row exists for
equal emission. No recovery or profile row exists for the arrival
`correct_alignment` comparator.

The arrival `permuted_alignment` fit alone is profiled and used for recovery,
latent-time, and predictive rows. The correct fit remains a heldout-score
comparator represented in `fit_execution_evidence.csv`. This makes the
authority's "comparator only" language literal and prevents comparator
profiles from becoming a second inferential analysis.

Except for `scenario_definitions.csv`, CSV rows retain the existing stable
lexical/numeric sort over their amended primary keys. Enum spelling, not enum
declaration order, controls lexical components.

### 4. Latent-Time Evidence Contract

Latent-time rows are descriptive, recommendation-neutral diagnostics. They do
not add a sixth recovery threshold or alter any of the four nested gates. This
is the only scientifically conservative resolution available without inventing
an unapproved quantitative threshold.

Add enum:

```text
truth_source = simulated_binary_transition|goal018_quasi_extirpation
```

Rows are required for every attempted replicate of:

```text
dense_count_exact_model
structured_imperfect_effort
sparse_expected_failure
zero_driver_effect_negative_control
permuted_arrival_alignment_stress
informative_dropout_misspecification_stress
goal018_continuous_abundance_stress
spatial_frailty_stress
```

Rows are not applicable and must not be emitted for either oracle or for the
equal-emission control. Oracle transitions are supplied rather than inferred;
the equal-rate likelihood contains no information about latent paths and has no
identified fitted process vector.

Use the augmented transition-time support:

```text
tau = (6,12,...,120,126)
```

The terminal value `126` means "no transition by 120" and is an evaluation
category only; it is never reported as a biological event time. For a fitted
cell, let `w_xj` be the normalized analyst-only posterior weight for each of
the 20 event endpoints plus the final censor path. Let
`F_x(t_k)=sum_{j:tau_j<=t_k} w_xj` for endpoints `t_k=6,...,120`. The evaluator
maps a censored truth to `126`. A finite Goal 018 quasi-extirpation remains at
its evaluator time; a Goal 018 value absent or later than 120 maps to `126`.

Metrics are literal:

```text
transition_brier =
  mean over cells x and endpoints k of
  (F_x(t_k) - I(T_x <= t_k))^2

L_x = smallest tau with posterior CDF >= 0.05
U_x = smallest tau with posterior CDF >= 0.95
interval_score_x =
  (U_x - L_x)
  + 20 * max(L_x - T_x, 0)
  + 20 * max(T_x - U_x, 0)
transition_interval_score = mean_x(interval_score_x)

M_x = smallest tau with posterior CDF >= 0.50
transition_median_absolute_error = median_x(abs(M_x - T_x))
```

These definitions are censoring-aware because the posterior and truth both
retain a distinct no-transition-by-horizon category. No inverse-probability
censoring weight is needed because synthetic evaluator truth is complete.

Frame and row rules are:

- dense, structured, zero-driver, dropout, continuous-abundance, and frailty
  use all 5,225 passable evaluator cells;
- sparse uses the fixed 1,306-cell sparse frame;
- arrival uses only the fixed 1,045 score cells under the primary permuted fit;
- `truth_source=simulated_binary_transition` except continuous abundance,
  which uses `goal018_quasi_extirpation`;
- each applicable attempted replicate emits exactly three rows in lexical
  metric order, which is also
  `transition_brier`, `transition_interval_score`, then
  `transition_median_absolute_error`;
- on an available fit, `observed_value` is the metric above,
  `expected_value=0`, `error=observed_value`, and
  `gate_result=diagnostic`;
- on a failed/nonfinite fit or invalid posterior, all three rows remain,
  `fit_succeeded=false`, `diagnostic_available=false`, the three numerical
  value fields are null, and `gate_result=warning`;
- a successful row has `fit_succeeded=true`,
  `diagnostic_available=true`, finite numerical fields, and the sample size of
  the fixed evaluator frame; and
- the latent-time visual must label these values "descriptive; no frozen
  recommendation threshold" and show explicit unavailable-fit markers.

No latent-time row may be used in starts, fitting, profile choice, predictive
reference construction, recommendation precedence, or result selection.

### 5. Stress Descriptive Recovery

Arrival, informative dropout, continuous abundance, and spatial frailty retain
all attempted fit and parameter rows. Their recovery tables are descriptive and
cannot silently become exact-model gates.

For arrival, informative dropout, and spatial frailty:

- emit five `replicate_recovery` rows per attempted primary fit;
- retain the known generating values in evaluator-only row construction;
- failed/nonfinite fits have null accepted estimate and interval fields;
- failed/open/missing intervals count as uncovered in the full attempted
  denominator;
- missing estimates and interval widths use the same full-support imputation as
  nested rows for descriptive median/maximum absolute error and width;
- median signed error uses finite converged estimates only and is nullable;
- `coverage_calibration` has the full `12` development or `24` holdout
  denominator, but `acceptance_lower_count` and `acceptance_upper_count` are
  null because no stress coverage acceptance set exists; and
- recovery and coverage `gate_result` is `diagnostic` when all required fit
  evidence is available and `warning` when any fit/profile evidence is
  unavailable. Neither value changes the recommendation by itself.

For continuous abundance:

- emit five primary-fit `replicate_recovery` rows per attempt so estimates,
  intervals, convergence, boundaries, and likelihood remain visible;
- `truth_value`, `truth_in_interval`, `signed_error`, and `absolute_error` are
  null because there is no binary-model parameter-recovery truth;
- emit one `coverage_calibration` row per parameter with attempted and
  converged counts plus descriptively imputed interval-width summaries;
- coverage counts/fractions/bounds and signed/absolute-error summaries are
  null; and
- `gate_result` follows the same diagnostic/warning availability rule.

The required-fit and predictive scenario gates remain separate. A descriptive
recovery row cannot rescue a failed fit or missing required warning.

### 6. Control Summary Denominators And Equal-Emission Convergence

Amend `control_decision_summary.csv` to make heterogeneous rows and gate
denominators literal. Use header:

```text
decision_row_id,decision_row_type,scenario_id,parameter_id,structural_status,practical_status,gate_family,gate_result,test_statistic,bootstrap_replicates,bootstrap_converged_count,bootstrap_failed_count,p_value,alignment_correlation,silent_misspecification_failure,attempted_replicates,evaluable_replicates,event_count,acceptance_lower_count,acceptance_upper_count,recommendation_rank,recommendation_class,transportability_class,interpretation
```

New types/domains are:

```text
decision_row_type = scenario_gate|parameter_status|final_decision
attempted_replicates:int?
evaluable_replicates:int?
event_count:int?
acceptance_lower_count:int?
acceptance_upper_count:int?
bootstrap_converged_count:int?
bootstrap_failed_count:int?
```

Primary key remains `decision_row_id`; rows sort lexically by that key. Freeze
IDs:

```text
scenario_gate|<scenario_id>
parameter_status|no_emission_contrast_negative_control|<parameter_id>
final_decision
```

Equal-emission scenario summary must contain:

```text
attempted_replicates = 24
evaluable_replicates = 24 when both observed shared fits are valid, otherwise 0
test_statistic = D_observed
bootstrap_replicates = 199
bootstrap_converged_count = count of successful ordered bootstrap rows
bootstrap_failed_count = 199 - bootstrap_converged_count
p_value = frozen add-one p when all required statistics are finite
```

The p-value, observed statistic, and all 199 bootstrap statistics must be
recomputable from `fit_execution_evidence.csv`. Any mismatch is an artifact
contract failure. The six parameter-status rows remain fixed independently of
p and link to the explicit shared fit estimates without duplicating them.

For zero driver, define one complete availability rule:

- `attempted_replicates=24` always;
- a replicate is evaluable only when the required fit succeeds and the
  `beta_driver` profile has a finite two-sided interval;
- `event_count` counts evaluable intervals that exclude zero;
- `acceptance_lower_count=0` and `acceptance_upper_count=6`;
- the false-signal binomial gate is evaluated only when
  `evaluable_replicates=24`; and
- fewer than 24 evaluable attempts fails the fit/evidence contract rather than
  being counted as a conservative non-exclusion or dropped. With 24 evaluable
  attempts, `event_count>6` is the negative-control false-signal outcome.

For arrival, `attempted_replicates=24`, `evaluable_replicates` counts complete
finite fit pairs, `event_count` counts strict correct-score wins, and bounds are
`22..24`. Fewer than 24 evaluable pairs fails availability; it does not shrink
the win denominator.

All other scenario-gate rows populate attempted/evaluable counts when a fixed
replicate denominator exists. Null means structurally inapplicable, never
"not computed".

### 7. Exact Artifact Set And Self-Reference Closure

The final bundle has 22 files. Replace the 21-file tuple with this literal
order:

```text
recovery_gate_config.json
runtime_projection.json
source_provenance.json
holdout_manifest.json
model_parameter_contract.csv
scenario_definitions.csv
fit_execution_evidence.csv
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

The config `artifact_manifest` is an immutable expected-set registry, not the
post-emission integrity manifest. It has exactly 22 entries in the order above;
each entry has exactly `path`, `role`, `required`, and `sha256`; `required=true`;
and every `sha256` is null. This makes the config self-hash finite and prevents
pre-holdout hashes from masquerading as final artifact hashes.

`verification.json` is the artifact-manifest document referred to by the
provenance amendment. Freeze
`checks[name="artifact_manifest"].details` to contain exactly:

```text
schema_version:str
entries:list[{path:str,sha256:str}]
represented_artifact_set_sha256:str
```

Its `entries` list contains the other 21 files in the literal bundle order with
`verification.json` omitted. The represented-set digest is SHA-256 over UTF-8
lines:

```text
<file_sha256><two spaces><relative_artifact_path>\n
```

in that same represented-entry order. No path appears twice. Missing, extra,
zero-byte, nonregular, or changed files fail before verification is accepted.

After canonical `verification.json` bytes are written, the external
`ArtifactSnapshot` hashes all 22 files, including `verification.json`, sorts
the complete path/hash manifest lexically by path, and computes
`artifact_set_sha256` over the same line format. This second-level complete hash
is held by post-exposure command envelopes and bound into append-only Log
attestations. It cannot be written into an included artifact without recursion.

In all provenance text and tests, replace the ambiguous phrase
"artifact-manifest file" with:

```text
artifact-manifest document (`verification.json`)
```

This solution adds no second manifest file and has no self-reference:

- config freezes expected paths only;
- verification hashes every other artifact;
- the external snapshot hashes verification plus every represented artifact.

This is a pre-emission schema amendment. No Goal 023 scientific artifact bundle
exists to migrate, and every pre-existing field keeps its prior type and
meaning. The immutable tracked `source_digest_receipt.json` remains byte-for-byte
unchanged; do not bump or reinterpret its independent `schema_version` while
versioning future generated bundle objects.

### 8. Config And Receipt Hash Interfaces

Freeze the following names and never use bare `config hash`, `receipt hash`, or
`manifest hash` where two meanings exist:

```text
config_sha256
  Embedded config self-hash over canonical config payload with only the
  config_sha256 field omitted.

config_file_sha256
  SHA-256 over the complete canonical recovery_gate_config.json file bytes,
  including the embedded config_sha256 field.

receipt_sha256
  Embedded holdout-receipt self-hash over canonical receipt payload with only
  receipt_sha256 omitted.

holdout_receipt_file_sha256
  SHA-256 over the complete holdout_receipt.json file bytes.

preholdout_receipt_file_sha256
  SHA-256 over the complete preholdout_state_receipt.json bytes. That schema
  has no embedded receipt self-hash.

represented_artifact_set_sha256
  The verification document's digest over the 21 represented files.

artifact_set_sha256
  The external complete 22-file snapshot digest including verification.json.
```

`holdout_manifest.json.receipt_sha256` must equal the embedded
`holdout_receipt.json.receipt_sha256`, not the holdout receipt's file-byte hash.
`verification.json.config_sha256`, both receipts' `config_sha256`, and every
config binding use the embedded config self-hash. Artifact snapshots and
before/after command envelopes always use full file-byte hashes.

Use typed validated interfaces internally, equivalent to:

```python
@dataclass(frozen=True, slots=True)
class FrozenConfigIdentity:
    path: Path
    payload: Mapping[str, object]
    config_sha256: str
    config_file_sha256: str
    canonical_bytes: bytes

@dataclass(frozen=True, slots=True)
class HoldoutReceiptIdentity:
    path: Path
    payload: Mapping[str, object]
    receipt_sha256: str
    holdout_receipt_file_sha256: str
    canonical_bytes: bytes

@dataclass(frozen=True, slots=True)
class ReceiptFileIdentity:
    path: Path
    file_sha256: str
    canonical_bytes: bytes
```

Every phase boundary loads and validates one of these identities before using
its fields. A raw dict, unchecked path, or ambiguous single `sha256` string is
not accepted by freeze, holdout, verify, staged-state, or provenance-envelope
helpers.

Amend the planned `ProvenanceEnvelope` fields to include the exact names:

```text
config_sha256
config_file_sha256
preholdout_receipt_file_sha256
receipt_sha256
holdout_receipt_file_sha256
represented_artifact_set_sha256
artifact_set_sha256
```

The existing config/receipt canonical hash rules remain unchanged. This is an
interface clarification, not a schema-value change.

### 9. Task 3 Fixture-Only Calibration Smoke

Replace Plan Task 3 step 6 with:

```markdown
6. Run all focused/full tests, static checks, fixture-only CLI dispatch smoke,
   artifact schema/visual fixture checks, and the full non-generative
   validation ladder. The Task 3 calibration smoke must inject deterministic
   fixture task results and writers under `tmp_path`; it may exercise parser,
   dispatch, worker-count forwarding, output-path forwarding, summary, and exit
   behavior, but it must not call the live calibration runner, instantiate any
   Goal 023 RNG object or payload, emit a scientific row, write the canonical
   artifact directory, or run a production `--phase calibration` subprocess.
   Task 4 owns the first live runtime benchmark and calibration execution.
```

Add the same boundary to Runbook section 3. Runbook section 4 remains the first
and only live pre-holdout benchmark/calibration procedure.

The CLI may expose a test injection seam such as a phase-services protocol or
callable map, but no production `--fixture-only` flag is added. Production
argument vocabulary remains literal. Task 3 tests invoke the dispatcher in
process with fake services and spies. A fake success receipt must assert:

```text
holdout_payload_instantiated = false
scientific_rows_emitted = false
rng_factory_call_count = 0
canonical_output_write_count = 0
```

### 10. Recommendation Safety

The new evidence rows do not alter recommendation precedence. They make
availability and named gate outcomes explicit so the state machine cannot
default to pass.

Until the separate recommendation-totality gap is amended, every otherwise
unmapped named gate vector must stop with the internal disposition
`classification_blocked_unmapped_outcome`; it must not emit one of the four
final recommendation classes. This proposal must not hide that separate
scientific decision inside schema code.

At minimum, missing/duplicate fit evidence, variant mismatch, failed required
fit availability, irreproducible equal-emission statistics, or artifact/hash
inconsistency is already covered by the current higher-precedence
`model_contract_failed` class. A valid but scientifically surprising outcome
whose class is not frozen remains blocked rather than being relabelled as a
schema failure.

## Patch Map

Apply the amendment only after Task 2b's accepted handoff is known.

1. **Goal and authoritative spec**
   - Insert sections 1, 4, 5, 6, 7, 8, and 10 into the matching scenario,
     deterministic-gate, recommendation, and Source And Artifact Contracts
     surfaces.
   - Add the new file/schema and fit-variant enum material from sections 2 and
     3.
   - Keep model equations, supports, starts, profiles, seed payloads,
     replication counts, thresholds, and transportability wording unchanged.
2. **Plan**
   - Task 3 steps 1-2: name fit-execution rows, variants, latent descriptive
     formulas, stress denominator rules, exact 22-file set, and two-level
     manifest tests.
   - Replace Task 3 step 6 with section 9.
   - Task 4 remains the first live benchmark/calibration owner.
3. **Runbook**
   - Section 3: add the exact RED/GREEN evidence below and fixture-only smoke
     boundary.
   - Sections 4, 6, and 7: update 21 to 22 files, name
     `verification.json` as the manifest document, and use unambiguous hash
     names.
4. **Artifact/CLI preflight**
   - Supersede its 21-file statement, ambiguous ArtifactSnapshot fields, and
     Task 3 profile/recovery TODOs with this proposal.
5. **Log**
   - Append only after live replacement document hashes and the current parent
     are known. Record this as a pre-simulation schema/evidence amendment, then
     obtain fresh scientific, executor-readiness, artifact/schema, and
     provenance/freeze acceptance. Earlier accepts remain hash-specific and
     non-transferable.

The holdout-provenance amendment and this amendment should be applied in one
controlled document reseal so they do not repeatedly supersede each other's
Goal/Plan/Runbook/spec hashes.

## Ordered RED Tests

Use temporary deterministic fixtures only. The names below are patch-ready;
their final numeric prefix may be adjusted to the accepted Task 2b test ledger,
but behavior text must remain literal.

### Registry, schemas, and order

1. `test_lro_3s_001_scenario_truth_access_fit_scope_and_variants_are_literal`
   asserts the exact 11-row table, canonical row order, and the exact truth
   mapping `oracle_only` for rows 1-2, `analyst_firewalled` for rows 3-6 and 8,
   and `stress_evaluator_only` for rows 7 and 9-11.
2. `test_lro_3s_002_fit_execution_schema_primary_key_and_sort_are_literal`
   asserts the exact 23-column header, non-null five-part key, lexical/numeric
   order, and rejection of duplicate/reordered rows.
3. `test_lro_3s_003_fit_variant_is_part_of_every_fit_derived_primary_key`
   asserts all six amended headers and rejects a row whose variant does not
   match the scenario registry.
4. `test_lro_3s_004_scenario_definitions_use_contract_order_not_lexical_order`
   demonstrates the explicit scenario-order exception and repeated-byte output.

### Arrival variants

5. `test_lro_3s_005_arrival_emits_complete_correct_and_permuted_fit_pairs`
   creates injected development fixtures and asserts two fit rows per attempt,
   identical replicate identity, disjoint fit/score frames, finite score fields
   only on success, and no dropped failed pair.
6. `test_lro_3s_006_arrival_primary_tables_use_permuted_variant_only`
   asserts recovery, coverage, latent-time, profile, and predictive rows use
   `permuted_alignment`; correct-comparator recovery/profile rows are rejected.
7. `test_lro_3s_007_arrival_win_gate_retains_all_24_attempts`
   checks strict score comparison, boundaries at 22 and 21 wins, and a failed
   pair producing no win plus availability failure rather than denominator
   loss.

### Equal-emission shared fits

8. `test_lro_3s_008_equal_emission_shared_fit_rows_have_no_fake_replicate_id`
   asserts two observed scenario-shared rows, fit index 0, exact source ranges,
   the equal closed-form start-field nulls, and the ordered eight-start
   convergence fields.
9. `test_lro_3s_009_equal_emission_bootstrap_rows_are_complete_and_recomputable`
   requires exactly 199 equal/ordered bootstrap pairs, indices `0..198`, source
   range `0..23`, no missing failure row, and exact recomputation of every
   `D_b`, observed `D`, and add-one p.
10. `test_lro_3s_010_equal_emission_convergence_and_statuses_are_independent`
    proves a failed ordered bootstrap row fails the scenario summary, boundary
    equal MLE is explicit, and p never changes the six structural/practical
    status rows.
11. `test_lro_3s_011_equal_emission_has_no_recovery_latent_or_profile_rows`
    rejects hidden per-replicate/shared recovery, latent-time, and profile rows;
    equal-rate predictive rows remain diagnostic and explicit.

### Latent-time definitions

12. `test_lro_3s_012_latent_metrics_are_exact_for_event_and_censor_fixture`
    uses two cells with posterior mass `0.5` at time 6 and `0.5` at censor 126,
    one true event at 6 and one censored truth. It requires Brier `0.25`, mean
    interval score `120`, median absolute error `60`, expected value `0`, and
    error equal to observed value.
13. `test_lro_3s_013_perfect_latent_posterior_has_zero_metrics`
    covers both a finite event and censor category with exact one-hot weights.
14. `test_lro_3s_014_latent_applicability_frames_and_truth_sources_are_literal`
    asserts exactly the eight applicable scenarios, frame sizes
    `5225/1306/1045`, continuous-abundance truth source, and no oracle/equal rows.
15. `test_lro_3s_015_failed_fit_retains_three_unavailable_latent_rows`
    asserts null values, fixed sample size, warning result, and no evaluator or
    posterior fallback.

### Stress recovery and control denominators

16. `test_lro_3s_016_known_truth_stress_recovery_uses_full_attempted_denominator`
    injects failed/open/missing rows and verifies uncovered treatment,
    full-support imputation, finite-only signed median, null acceptance bounds,
    and diagnostic/warning result without a recovery threshold.
17. `test_lro_3s_017_continuous_abundance_recovery_has_no_parameter_truth_claim`
    requires estimates/intervals/convergence rows but null truth, coverage, and
    error fields, with interval-width summaries retained.
18. `test_lro_3s_018_zero_driver_requires_24_evaluable_profiles`
    tests six versus seven exclusions and separately proves any failed/open
    attempt fails availability instead of counting as a non-exclusion.
19. `test_lro_3s_019_control_summary_denominators_reconcile_to_fit_evidence`
    checks attempted/evaluable/event/bootstrap counts against the detailed fit
    and profile rows for zero-driver, arrival, and equal emission.

### Artifact self-reference and hash interfaces

20. `test_lro_3s_020_exact_22_file_manifest_and_config_null_hash_registry`
    asserts the literal order, roles, required flags, all-null config manifest
    hashes, and rejection of 21, 23, missing, extra, duplicate, or reordered
    entries.
21. `test_lro_3s_021_verification_manifest_represents_other_21_files`
    proves verification excludes itself, includes every other file once in
    literal order, and reproduces `represented_artifact_set_sha256`.
22. `test_lro_3s_022_external_snapshot_includes_verification_and_all_22_files`
    proves lexical complete ordering, exact `artifact_set_sha256`, and detection
    of mutation to verification, a represented artifact, missing/extra files,
    and zero-byte files.
23. `test_lro_3s_023_config_and_receipt_self_hashes_are_not_file_hashes`
    independently reproduces embedded and full-file hashes, proves the named
    fields are not interchangeable, and checks holdout-manifest receipt binding.
24. `test_lro_3s_024_phase_guards_require_typed_validated_hash_identities`
    rejects raw dicts, unchecked paths, swapped self/file hashes, and a
    preholdout receipt treated as if it had an embedded self-hash.

### Fixture-only Task 3 CLI smoke

25. `test_lro_3s_025_task3_calibration_dispatch_smoke_is_fixture_only`
    exercises parser/dispatcher behavior with injected fake services under
    `tmp_path`, workers/output forwarding, fixed summary, and zero RNG/payload/
    canonical-write counts.
26. `test_lro_3s_026_task3_smoke_cannot_reach_live_calibration_runner`
    installs a live-runner bomb and proves the fixture path never calls it.
27. `test_lro_3s_027_task4_is_first_live_benchmark_and_calibration_owner`
    asserts Task 3 validation metadata contains no production benchmark or
    calibration subprocess and Task 4 retains the literal live commands.

### Cross-table and recommendation safety

28. `test_lro_3s_028_every_primary_science_row_reconciles_to_one_fit_row`
    enforces scenario/split/replicate/variant foreign-key relationships,
    parameter subsets, fit status, and no orphan/duplicate science row.
29. `test_lro_3s_029_unmapped_named_gate_vector_blocks_instead_of_passing`
    proves an unresolved valid scientific outcome produces
    `classification_blocked_unmapped_outcome`, never the passing class.
30. `test_lro_3s_030_two_independent_fixture_bundles_are_byte_identical`
    covers the full 22-file non-holdout fixture set under permuted task input
    and fake one-worker/eight-worker completion order.

Suggested focused RED/GREEN command after Task 2b acceptance:

```bash
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py \
  -k 'lro_3s' --no-cov
```

No RED test may fail because a fixture imports a missing future artifact or
because it calls a prohibited live payload. It must fail on the specific absent
schema, evidence, formula, guard, or dispatch behavior.

## Validation And Review Gate

After tracked implementation, but before Task 4 live execution:

1. Run all focused Task 2a/2b/3 tests and the complete pre-holdout validation
   ladder without a production runtime benchmark or calibration run.
2. Generate two fixture-only bundles under temporary directories and compare
   all 22 files byte for byte.
3. Obtain independent scientific review of latent metric definitions,
   descriptive-only stress semantics, and no-profile comparator policy.
4. Obtain independent statistical review of full denominators, zero-driver
   availability, equal-emission recomputation, and censor-category scoring.
5. Obtain independent artifact/schema review of every header, key, enum, row
   order, cross-table constraint, and the two-level manifest.
6. Obtain independent provenance/freeze review of config/receipt self-hash
   versus file-hash interfaces and the coordinated provenance amendment.
7. Reseal Goal, Plan, Runbook, spec, and Log hashes. No Task 4 live execution
   is legal until all reviews return `ACCEPT` with no Critical or Important
   finding.

Stop immediately if implementation requires a new estimator, parameter,
profile, seed mapping, replicate count, quantitative latent-time threshold,
extra truth in an analyst interface, or a hidden/sentinel evidence identity.

## Barry-Level Decision

No Barry-level decision is required **if** latent-time evidence is adopted as
the explicit descriptive, recommendation-neutral contract above. That choice
preserves all frozen scientific thresholds and recommendation classes.

A request to make any latent-time metric a quantitative pass/fail gate would
be a new scientific assumption. The authority currently provides no defensible
threshold, denominator-level sampling model, or multiplicity rule for such a
gate. That change must return to Barry before implementation.

The separate recommendation-totality question for valid but scientifically
surprising outcomes also remains Barry-level if the orchestrator wants a new
terminal scientific class rather than the fail-closed
`classification_blocked_unmapped_outcome` disposition.

## Proposal Self-Review

- No placeholder, sentinel primary key, nullable primary-key component, or
  hidden JSON/text evidence is proposed.
- Every multi-fit/shared-fit attempt has one literal fit identity and retains
  failure/convergence evidence.
- Comparator output cannot enter primary profiles or predictive references.
- Stress parameter rows are explicitly descriptive and retain attempted
  denominators.
- Latent metrics have formulas, applicability, frames, truth source,
  missingness behavior, and interpretation, without an invented threshold.
- Truth-access enums map all 11 scenarios.
- Config, verification, external artifact snapshot, and receipts have distinct
  nonrecursive hash interfaces.
- Task 3 exercises only injected fixture calibration dispatch; Task 4 remains
  the first live benchmark/calibration owner.
- The proposal changes no tracked file and constructs no scientific payload or
  artifact.
