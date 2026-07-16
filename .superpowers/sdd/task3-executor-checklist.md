# Goal 023 Task 3 Executor Checklist

Read-only extraction for the executor. Task 3 is blocked pending the separate
Task 2b repair. Do not edit tracked files, instantiate Goal 023 RNG/payloads,
simulate, calibrate, produce scientific artifacts, benchmark, or hold out.

## Authority and order

1. Release only after the hash-specific Task 2b source/test/Log handoff and
   integrated amendment seal. The proposal says Task 3, runtime benchmarking,
   calibration, config emission, freeze, holdout, staging, commit, and
   publication remain blocked until that handoff ([integrated amendment
   proposal](/Users/bwbrook/.codex/worktrees/spatext/goal023/.superpowers/sdd/integrated-contract-amendment-proposal.md:1-43);
   [Runbook](/Users/bwbrook/.codex/worktrees/spatext/goal023/docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md:169-210)).
2. Implement/verify the registry and typed evidence; then latent diagnostics;
   then existing gates and reducer; then writers, disk-first verification,
   hashes, provenance guards, documentation, and fixture dispatch. This is the
   exact Plan order ([Plan](/Users/bwbrook/.codex/worktrees/spatext/goal023/docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md:301-345)).
3. Preserve every biological/statistical invariant and existing threshold; the
   amendment adds only diagnostics, decision handling, typed evidence, hashes,
   fixture dispatch, and provenance mechanics ([proposal](/Users/bwbrook/.codex/worktrees/spatext/goal023/.superpowers/sdd/integrated-contract-amendment-proposal.md:49-111)).

## 1. Literal scenario matrix

The following order and values are literal ([spec](/Users/bwbrook/.codex/worktrees/spatext/goal023/spec/synth_medium_latent_response_observation_recovery_gate.md:609-649)).

| # | scenario | truth access | fit scope | primary | comparator | replicates / evidence |
|---:|---|---|---|---|---|---|
| 1 | `process_oracle_observed_transition` | `oracle_only` | `replicate` | `canonical` | none | 3 process parameters; diagnostic latent rows, 5,225 cells |
| 2 | `observation_oracle_fixed_transition` | `oracle_only` | `replicate` | `canonical` | none | 2 rates; latent not applicable |
| 3 | `dense_count_exact_model` | `analyst_firewalled` | `replicate` | `canonical` | none | 5 parameters; diagnostic, 5,225 cells |
| 4 | `structured_imperfect_effort` | `analyst_firewalled` | `replicate` | `canonical` | none | 5 parameters; diagnostic, 5,225 cells |
| 5 | `sparse_expected_failure` | `analyst_firewalled` | `replicate` | `canonical` | none | dedicated `beta_driver` gate; fixed 1,306-cell frame; diagnostic |
| 6 | `zero_driver_effect_negative_control` | `analyst_firewalled` | `replicate` | `canonical` | none | control plus descriptive recovery; diagnostic, 5,225 cells |
| 7 | `permuted_arrival_alignment_stress` | `stress_evaluator_only` | `replicate` | `permuted_alignment` | `correct_alignment` | descriptive primary; comparator score; fixed 1,045 score cells |
| 8 | `no_emission_contrast_negative_control` | `analyst_firewalled` | `scenario_shared` | `equal_rate` | `ordered_emission` | shared fits and six fixed status rows; no recovery/profile/latent rows |
| 9 | `informative_dropout_misspecification_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | descriptive, 5 known parameters; diagnostic, 5,225 cells |
| 10 | `goal018_continuous_abundance_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | estimates/widths only; no recovery truth; latent not applicable |
| 11 | `spatial_frailty_stress` | `stress_evaluator_only` | `replicate` | `canonical` | none | descriptive, 5 known parameters; diagnostic, 5,225 cells |

Truth classes are literal: oracle truth only enters the named physically
separate oracle likelihood; analyst-firewalled truth stays controller/evaluator
side; stress-evaluator truth is consulted only after fitting ([spec](/Users/bwbrook/.codex/worktrees/spatext/goal023/spec/synth_medium_latent_response_observation_recovery_gate.md:635-650)).

Replicate lock: scenarios 1-4 use development 12 (`0..11`), calibration 24
(`0..23`), holdout 48 (`0..47`); scenarios 5-11 use development 12 and
holdout 24 with no calibration rows. Predictive references and equal-emission
bootstrap use draws `0..198`; bootstrap pseudo-replicates are `0..23`
([spec](/Users/bwbrook/.codex/worktrees/spatext/goal023/spec/synth_medium_latent_response_observation_recovery_gate.md:950-976)).

## 2. Required implementation surface and dispatch

Required Task 3 source/API/CLI surface: `observe.py`; the Goal 023 medium
module; `scripts/run_synth_medium_latent_response_observation_recovery.py`;
the two listed tests; medium `__init__.py`; `AGENTS.md`, `README.md`,
`spec/report_log.md`, and Goal 023 `Log.md`. The complete source footprint and
receipt paths are enumerated in Goal ([Goal](/Users/bwbrook/.codex/worktrees/spatext/goal023/docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md:2160-2178)).

The module must expose typed scenario/fit evidence, latent diagnostics,
recommendation reduction, deterministic writers, disk-first verification,
artifact snapshots, config/receipt identities, phase guards, provenance
envelopes, and fixture dispatch. Current source anchors include
`SCENARIO_EVIDENCE_REGISTRY`, `SCENARIO_DEFINITIONS`, `ARTIFACT_PATHS`, fit-row
validators, latent helpers, and artifact/receipt classes ([source](/Users/bwbrook/.codex/worktrees/spatext/goal023/src/spatext/synth/medium/latent_response_observation_recovery.py:4762-5250)).

Task 3 CLI smoke is injected and deterministic under `tmp_path`: it may test
parser, dispatch, worker/output forwarding, summary, and exit behavior, but
must not call the live calibration runner, instantiate any Goal 023 RNG object
or payload, emit scientific rows, write the canonical artifact directory, or
launch production `--phase calibration` ([Plan](/Users/bwbrook/.codex/worktrees/spatext/goal023/docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md:337-345)).
Required assertions: `holdout_payload_instantiated=false`,
`scientific_rows_emitted=false`, `rng_factory_call_count=0`, and
`canonical_output_write_count=0` ([Runbook](/Users/bwbrook/.codex/worktrees/spatext/goal023/docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md:260-270);
[tests](/Users/bwbrook/.codex/worktrees/spatext/goal023/tests/test_synth_medium_latent_response_observation_recovery.py:4764-4804)).

## 3. Exact artifact contract

The 22 paths, in required order, are:

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

Config manifest entries are exactly `{path,role,required,sha256}`, all required
and null-hashed. `verification.json` represents the other 21 exactly once with
`{schema_version,entries,represented_artifact_set_sha256}`. The external
snapshot hashes all 22, including `verification.json`, lexical-sorts paths,
and stores `artifact_set_sha256`; neither digest is recursively embedded
([Goal](/Users/bwbrook/.codex/worktrees/spatext/goal023/docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md:1884-1980)).

Schemas that must be exact:

- `scenario_definitions.csv`: existing fields plus
  `fit_scope,primary_fit_variant,comparator_fit_variant`; primary key
  `scenario_id`, but rows are numbered scenario order ([spec](/Users/bwbrook/.codex/worktrees/spatext/goal023/spec/synth_medium_latent_response_observation_recovery_gate.md:1618-1650)).
- `fit_execution_evidence.csv`: the literal 23-column header and typed nullable
  fields at [spec](/Users/bwbrook/.codex/worktrees/spatext/goal023/spec/synth_medium_latent_response_observation_recovery_gate.md:1651-1731);
  sort key `(scenario_id,split_id,fit_scope,fit_variant,fit_index)`. Replicate
  rows are one source replicate; shared rows use index 0 and ranges 0..11 or
  0..23; bootstrap-shared is equal-emission only, bundle 0..198, source count
  24. Failed attempts still emit one row with `failure_code`.
- Descriptive stress recovery retains attempted rows, full denominators, and
  nullable finite-only summaries; continuous abundance has null truth/error/
  coverage fields and requires predictive evidence plus a warning ([spec](/Users/bwbrook/.codex/worktrees/spatext/goal023/spec/synth_medium_latent_response_observation_recovery_gate.md:1770-1840)).
- `control_decision_summary.csv` uses the replacement 24-column header and
  typed nullable denominator/bootstrap fields; values recompute from fit
  evidence ([spec](/Users/bwbrook/.codex/worktrees/spatext/goal023/spec/synth_medium_latent_response_observation_recovery_gate.md:1795-1880)).
- Visuals are exactly the six SVG paths above; self-decoding/schema checks and
  montage membership are required ([tests](/Users/bwbrook/.codex/worktrees/spatext/goal023/tests/test_synth_medium_latent_response_observation_recovery.py:4695-4753)).

## 4. Guards and manifests

At config emission, freeze, pre-receipt, and pre-RNG, fail closed unless
pinned branch/HEAD/base, status, exact analytical manifest, phase-specific
candidate footprint, and receipt presence/absence vector all match. Never write
config or a receipt on a failed guard. The exact publication universe and
phase vectors are defined in [spec](/Users/bwbrook/.codex/worktrees/spatext/goal023/spec/synth_medium_latent_response_observation_recovery_gate.md:1080-1140)
and [Runbook](/Users/bwbrook/.codex/worktrees/spatext/goal023/docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md:272-370).

The analytical manifest is the literal 16-file tracked analytical set; the
publication-path universe is 19 paths; candidate changes must be inside the
Runbook section 8 allowlist. Pre-freeze has the analytical files, Log, and no
receipts; post-freeze/pre-holdout has those plus
`preholdout_state_receipt.json` and no `holdout_receipt.json` ([spec](/Users/bwbrook/.codex/worktrees/spatext/goal023/spec/synth_medium_latent_response_observation_recovery_gate.md:1108-1135)).
Every command has a complete byte envelope. A nonmutating nonzero result gets
one independently approved exact retry; a second failure stops. Any mutation
invalidates the immutable state ([proposal](/Users/bwbrook/.codex/worktrees/spatext/goal023/.superpowers/sdd/integrated-contract-amendment-proposal.md:120-170)).

## 5. Allowed non-generative validation

These are the Task 3 focused commands from the Runbook, with `--no-cov`:

```bash
uv run pytest tests/test_observe.py --no-cov
uv run pytest tests/test_synth_medium_latent_response_observation_recovery.py --no-cov
uv run pytest tests/test_synth_medium_landscape.py --no-cov
uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
uv run pytest tests/test_synth_medium_observation_design.py --no-cov
uv run pytest tests/test_synth_medium_recoverability_target_observation_design.py --no-cov
git diff --check
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv run pre-commit run --all-files
```

Run only injected fixture tests for dispatch/artifacts/guards, especially
`test_lro_3s_001` through `test_lro_3s_010` ([tests](/Users/bwbrook/.codex/worktrees/spatext/goal023/tests/test_synth_medium_latent_response_observation_recovery.py:4695-4825)). Do not run `uv sync`, `uv build`, any runtime benchmark, calibration, canonical artifact writer, RNG-vector test, simulation, calibration, or holdout command while this checklist is being executed. Task 4 owns the first live runtime benchmark and calibration ([Plan](/Users/bwbrook/.codex/worktrees/spatext/goal023/docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md:355-399)).

## Authority inconsistency

The requested `/Users/bwbrook/.codex/agents/luna_low_scout.toml` does not exist
on this host (no matching file was found under `/Users/bwbrook/.codex`). The
available scout skill says dispatched subagents should ignore its workflow
section ([using-superpowers](/Users/bwbrook/.codex/plugins/cache/openai-curated-remote/superpowers/6.1.1/skills/using-superpowers/SKILL.md:1-8)); no substitute profile was treated as authoritative. The target worktree also had pre-existing tracked modifications/untracked Goal 023 implementation files; none were edited.
