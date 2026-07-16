# Goal 023 Task 3 Current Gap Inventory

Read-only inventory made from the live worktree. No production CLI, RNG,
payload, artifact, calibration, or holdout path was run.

## Dependency-ordered checklist

1. **Registry and fit evidence: implemented.**
   `SCENARIO_EVIDENCE_REGISTRY` has 11 entries at
   `src/spatext/synth/medium/latent_response_observation_recovery.py:6115`;
   `SCENARIO_DEFINITIONS` and its validators are at `:6389` and `:6459`.
   Fit-row schema, sorting, completeness, arrival-pair, primary-variant, and
   equal-emission recomputation surfaces are at `:6546-6991`.
2. **Scenario execution: partial.** Scenario split/frame and latent/gate
   helpers exist at `:7122-7768`, but there is no production scenario runner
   or CLI script. Only injected fixture dispatch exists at `:12071`.
3. **Latent diagnostics and reducers: implemented.** Typed diagnostic helpers
   and validation are at `:7321-7569`; recovery, predictive, control, stress,
   and total reduction surfaces are at `:7575-10035`.
4. **Exact artifact contract: implemented as schemas/writers/verification
   surfaces.** `ARTIFACT_PATHS` contains 22 paths at `:5325`; schema/version
   declarations are at `:5350`; manifest, verification, disk-first snapshot,
   config, and receipt writers/validators are at `:10096-10830`.
   Tests `test_lro_3s_001` through `test_lro_3s_004` are at
   `tests/test_synth_medium_latent_response_observation_recovery.py:7951-8500`.
5. **Typed config/receipt/phase/provenance guards: implemented.** Identity
   loading and phase checks are at `:10562-10871`; command envelopes,
   provenance, phase capture/validation, config/freeze/receipt guards, and
   staging/publication checks are at `:10986-12070`. Relevant tests are
   `test_lro_3s_005` and the later guard tests at `:8500-9737`.
6. **Fixture-only CLI dispatch: implemented at API level, production entry
   point missing.** `FixtureTaskService`, `fixture_task_service`, and
   `dispatch_fixture_calibration` are at `:5030-5040` and `:12071-12100`;
   fixture tests are `test_lro_3s_006`, `test_lro_3s_007`, and
   `test_lro_3s_010` at `:8513-8787`. The required script is absent.
7. **Exports: missing.** `src/spatext/synth/medium/__init__.py` exports older
   medium surfaces only; it does not import or list the Goal 023 module
   symbols. The file is present, but the Task 3 API export requirement is not
   satisfied.
8. **Documentation: partial/missing.** `AGENTS.md`, `README.md`, and
   `spec/report_log.md` exist, but live searches show no Goal 023 Task 3 CLI,
   registry, artifact, or guard documentation in those files. Goal `Log.md`
   exists and contains prior Goal 023 records, but no Task 3 completion record
   was inferred or added.
9. **Write scope and allowed commands: documented, not executed.** The
   checklist permits only injected fixture tests and non-generative checks;
   it explicitly forbids `uv sync`, `uv build`, benchmarks, calibration,
   canonical writers, RNG-vector tests, simulation, and holdout. Task 4 owns
   the first live benchmark/calibration (`.superpowers/sdd/task3-executor-checklist.md:152-170`,
   `Plan.md:355-399`). No command from that forbidden set was run.

## Current git evidence

Branch: `codex/spatext-goal023-latent-response-observation-gate`, tracking
`origin/main`. Existing dirty footprint was not changed:

```text
M  pyproject.toml
M  uv.lock
?? docs/goals/023-synth-medium-latent-response-observation-recovery-gate/
?? spec/synth_medium_latent_response_observation_recovery_gate.md
?? src/spatext/observe.py
?? src/spatext/synth/medium/latent_response_observation_recovery.py
?? tests/test_observe.py
?? tests/test_synth_medium_latent_response_observation_recovery.py
```

## Literal conflicts

1. `.superpowers/sdd/task3-executor-checklist.md:3-18` says Task 3 is blocked
   pending a separate Task 2b repair/integrated amendment seal, while
   `docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md:301-353`
   presents Task 3 as the implementation task and its source/test footprint is
   already present. This is a status/authority conflict, not a scientific
   judgement.
2. The checklist points its fixture assertions to test lines `4695-4825`
   (`:66-74`), but the live `test_lro_3s_001`-`010` block is at
   `tests/test_synth_medium_latent_response_observation_recovery.py:7951-8787`.

## Counts

- Implemented surfaces: **7**
- Missing surfaces: **3**
- Conflicts: **2**
