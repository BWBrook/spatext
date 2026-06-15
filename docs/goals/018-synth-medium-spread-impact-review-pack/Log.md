# Log

## 2026-06-14 - Orchestrator Packet

Barry approved Goal 018 after human visual/scientific sanity review of the
published Goal 017 `synth-medium` landscape. The approved next step is a
deterministic synthetic-only predator-spread and prey-impact review pack over
that fixed landscape.

The goal permits bounded tuning of a small number of named parameter
candidates to identify a default scenario that is ecologically plausible and
information-rich enough for later back-fitting review. It explicitly forbids
fitting, inference, observations, reconstruction, real-data analysis, broad
sweeps, remote compute, commits, pushes, Goal 019, or changes to the accepted
Goal 017 landscape contract.

No implementation, validation, generated-artifact staging, commit, push,
fitting, inference, real-data work, or follow-on goal work was performed by
the orchestrator.

## 2026-06-14 - Action-Agent Implementation

Action agent `mink` confirmed the action repo at
`/Users/bwbrook/papers/spatext`, fetched `origin`, confirmed canonical
`origin/main` at Goal 017 commit `ce42cced`, and created branch
`codex/spatext-goal018-synth-medium-spread-impact-review` from `origin/main`.

Read before implementation:

- repo-local `AGENTS.md`
- `README.md`
- `spec/problem_statement.md`
- `spec/theory.md`
- `spec/synth_medium_landscape.md`
- Goal 017 packet files
- `src/spatext/synth/medium/landscape.py`
- relevant synth-small predator truth and inspection patterns

Implemented the Goal 018 review pack:

- added `spec/synth_medium_spread_impact_review_pack.md`;
- added `src/spatext/synth/medium/spread_impact.py`;
- added `scripts/simulate_synth_medium_spread_impact.py`;
- added `tests/test_synth_medium_spread_impact.py`;
- exported the spread-impact surface from `src/spatext/synth/medium/__init__.py`;
- updated `README.md`, `AGENTS.md`, and `spec/report_log.md`.

Contract-first RED check:

```bash
uv run pytest tests/test_synth_medium_spread_impact.py --no-cov
```

The first focused run failed because the new `spatext.synth.medium`
spread-impact API did not yet exist. After implementation, the focused Goal
018 tests passed.

Bounded candidate tuning remained within the packet scope. Five named
candidate parameter sets were recorded in `parameter_candidate_log.csv`.
`balanced_corridor_detour_v2` was selected as the default because it produced
conservative finite spread, low-matrix detours, three material source
contributions, broad arrival timing, and non-synchronous prey lags without
instantaneous saturation.

One auditability adjustment was made during implementation: the water/barrier
detour gate is evaluated using the explicit
`water_adjacent_low_quality_matrix` versus
`non_water_adjacent_low_quality_matrix` contrast. The broader
`water_adjacent_passable` group is still emitted, but it mixes corridors and
patches with low-quality matrix and is therefore not the verification contrast.

## 2026-06-14 - Review Iteration: Recoverability and Source Accounting Polish

Orchestrator review found the visual dynamics and headline counts promising,
but requested two auditability fixes before acceptance:

- rename recoverability proxy IDs `arrival_time_iqr` and `impact_lag_iqr`
  because the observed values are full ranges, not interquartile ranges;
- clarify `source_contribution_summary.csv` denominator semantics so source
  contribution fractions are not conflated with the uncolonized-passable
  accounting row.

Implemented the narrow polish without retuning or changing the selected
default:

- recoverability proxy IDs are now `arrival_time_range` and
  `impact_lag_range`;
- `source_contribution_summary.csv` now includes `row_role`, explicit source
  contribution count/fraction/denominator fields, an explicit
  `uncolonized_passable_accounting` row with all-passable denominator fields,
  and material-source threshold/status columns;
- the generated report lists the source-denominator semantics and the renamed
  recoverability proxies;
- spec, README, report log, and focused tests were updated to lock the schema.

CLI smoke:

```bash
uv run python scripts/simulate_synth_medium_spread_impact.py
```

Selected output:

- selected parameter set: `balanced_corridor_detour_v2`
- final colonized passable cells: `4605`
- finite prey quasi-extirpations: `4289`
- material source count: `3`
- recommendation: `ready_for_human_spread_impact_review`
- written files: `18`

Generated review bundle:

```text
artifacts/synth_medium_spread_impact/
```

Visual review files:

- `artifacts/synth_medium_spread_impact/visuals/predator_arrival_time.svg`
- `artifacts/synth_medium_spread_impact/visuals/predator_occupancy_snapshots.svg`
- `artifacts/synth_medium_spread_impact/visuals/prey_abundance_snapshots.svg`
- `artifacts/synth_medium_spread_impact/visuals/prey_impact_time.svg`
- `artifacts/synth_medium_spread_impact/visuals/source_contribution_map.svg`
- `artifacts/synth_medium_spread_impact/visuals/arrival_impact_lag.svg`
- `artifacts/synth_medium_spread_impact/visuals/review_montage.svg`

Boundaries preserved: no Goal 017 landscape redesign, observation model,
extirpation reconstruction, synth-small scoring/candidate/class change,
ABC/POM/likelihood/MCMC/posterior/parameter recovery/fitting, real-data
analysis, broad sweep, remote compute, commit, push, generated-artifact
staging, or Goal 019 work was started.
