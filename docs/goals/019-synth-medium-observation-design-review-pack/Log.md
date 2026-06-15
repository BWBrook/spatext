# Log

## 2026-06-15 - Orchestrator Packet

Barry approved Goal 019 after accepting and publishing the Goal 018
`synth-medium` spread-impact review pack. The approved next step is a
deterministic synthetic-only observation-design review pack over the fixed
Goal 018 latent truth.

The default observation regime must be a plausible imperfect response-only
process with uneven effort, imperfect detection, false negatives, and some
post-impact gaps. A full-observability regime is included only as a labelled
benchmark. A sparse regime is included as a low-information stress test.

The goal explicitly forbids changing Goal 017/018 truth contracts,
reconstructing extirpation times, building a reconstruction rule, fitting,
inference, real-data analysis, broad sweeps, remote compute, commits, pushes,
and Goal 020.

No implementation, validation, generated-artifact staging, commit, push,
fitting, inference, real-data work, or follow-on goal work was performed by
the orchestrator.

## 2026-06-15 - Action Implementation

Created branch
`codex/spatext-goal019-synth-medium-observation-design-review` from
`origin/main` after confirming the action repo was clean at the published
Goal 018 base.

Read the Goal 019 delegation, repo-local instructions, README, problem
statement, theory, Goal 017/018 specs and packets, the synth-medium landscape
and spread-impact source, and relevant synth-small observation/reconstruction
patterns for style and boundary context.

Added the Goal 019 implementation footprint:

- `spec/synth_medium_observation_design_review_pack.md`
- `src/spatext/synth/medium/observations.py`
- `scripts/build_synth_medium_observation_design.py`
- `tests/test_synth_medium_observation_design.py`
- exports in `src/spatext/synth/medium/__init__.py`
- README, AGENTS, and report-log updates

The focused RED check
`uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
initially failed because the new observation-design API did not exist. After
implementation, the same focused test passed with `4` tests.

The regenerated review bundle is written under:

```text
artifacts/synth_medium_observation_design/
```

It contains the required `12` root audit/report files plus `6` SVG visual
review files.

Current CLI smoke:

```bash
uv run python scripts/build_synth_medium_observation_design.py
```

wrote `18` files with selected default regime
`structured_response_observed_default`.

Headline regenerated outcomes:

- Source truth reconciliation passed for Goal 018
  `balanced_corridor_detour_v2`: `6048` cells, `5225` passable, `823` water,
  `4605` final colonized passable cells, and `4289` finite prey
  quasi-extirpations.
- Benchmark `truth_reference_full_observability`: surveyed passable fraction
  `1.0`, false negatives `0`.
- Default `structured_response_observed_default`: `21258` records, `4411`
  surveyed passable cells (`0.844210526316`), `1976` observed response
  changes, `2313` false negatives, post-impact support `3014`
  (`0.702727908603`), and detected response-time range `108`.
- Stress `sparse_response_observed_stress`: `3614` records, `4175` false
  negatives, post-impact support fraction `0.155280951271`.
- Verification passed and recommendation is
  `ready_for_human_observation_design_review`.

Targeted hygiene completed before the full final validation ladder:

- `uv run ruff format src/spatext/synth/medium/observations.py scripts/build_synth_medium_observation_design.py tests/test_synth_medium_observation_design.py`
- `uv run ruff check src/spatext/synth/medium/observations.py scripts/build_synth_medium_observation_design.py tests/test_synth_medium_observation_design.py`
- `uv run mypy src/spatext/synth/medium/observations.py tests/test_synth_medium_observation_design.py`

Final validation completed:

- `git status --short --branch --untracked-files=all`
- `git diff --check`
- `uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
  (`4` passed)
- `uv run pytest tests/test_synth_medium_spread_impact.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_landscape.py --no-cov`
  (`5` passed)
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest` (`107` passed, coverage `93.54%`)
- `uv build`
- `uv run python scripts/build_synth_medium_observation_design.py`
  (`18` files written)
- `git status --ignored --short artifacts dist`
  (`!! artifacts/`, `!! dist/`)

No Goal 017 landscape change, Goal 018 spread-impact truth change,
reconstruction, reconstruction-rule screen, fitting, inference, real-data,
broad-sweep, remote-compute, commit, push, generated-artifact staging, or
Goal 020 work was performed.

## 2026-06-15 - Visual Review Polish

Review feedback accepted the observation tables/model as basically sound but
required narrow visual/auditability polish before acceptance. No observation
regime, survey probability, selected default, table schema, numerical outcome,
Goal 017 landscape, or Goal 018 truth change was made.

Visual contract changes:

- Redesigned `visuals/regime_comparison_montage.svg` as a readable comparison
  table with short labels (`Coverage`, `Post-impact support`,
  `False negatives`, `Detection rate`), visible numeric values, bars, and
  separate record/false-negative counts per regime.
- Added embedded SVG legend groups to the individual default map visuals:
  `survey_effort_surface_default.svg`,
  `observed_final_response_default.svg`,
  `truth_observed_mismatch_default.svg`, and
  `post_impact_support_default.svg`.
- Added the same decode keys to `review_montage.svg` so water/not-passable,
  no-survey or no-support cells, observed true extirpations, false negatives,
  late detections, and not-extirpated/uninformative cells are readable without
  consulting source code.
- Added a `Visual Decode Keys` section to generated `report.md`.
- Updated `spec/synth_medium_observation_design_review_pack.md` and
  `tests/test_synth_medium_observation_design.py` so the readable comparison
  layout and embedded legend contract are enforced.

Focused red-green evidence:

- The new visual-contract test initially failed on the pre-polish
  `regime_comparison_montage.svg`.
- After the SVG/report/spec implementation, focused Goal 019 tests passed:
  `uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
  (`5` passed).

Regenerated CLI output remains numerically unchanged:

- selected default regime `structured_response_observed_default`
- default survey records `21258`
- default false negatives `2313`
- recommendation `ready_for_human_observation_design_review`
- `18` files written

Final review-polish validation completed:

- `git diff --check`
- `uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_spread_impact.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_landscape.py --no-cov`
  (`5` passed)
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest` (`108` passed, coverage `93.56%`)
- `uv build`
- `uv run python scripts/build_synth_medium_observation_design.py`
  (`18` files written)
- `git status --ignored --short artifacts dist`
  (`!! artifacts/`, `!! dist/`)

No reconstruction, reconstruction-rule screen, fitting, inference, real-data,
broad-sweep, remote-compute, commit, push, generated-artifact staging, or
Goal 020 work was performed.

## 2026-06-15 - Regime Comparison SVG Clipping Fix

Review feedback found that `regime_comparison_montage.svg` was still not
acceptable for human visual review because the table content clipped at normal
preview size. The fix remained visual/layout-only.

Changes:

- Widened `regime_comparison_montage.svg` from `1180` to `1440` pixels and
  matched the `viewBox` width.
- Rebalanced the regime comparison table to use metric columns starting at
  `420` with `235`-pixel spacing, `132`-pixel bars, and a `1380`-pixel table
  background inside the `1440`-pixel viewBox.
- Added a visual layout test that parses the SVG width/viewBox and estimates
  text/rect right edges, requiring the comparison content to fit inside the
  width with a `40`-pixel margin and a minimum width of `1400`.
- Preserved the map legends and visual decode keys added in the previous
  polish.
- Updated `spec/synth_medium_observation_design_review_pack.md` so the
  comparison montage must fit inside the SVG width/viewBox with explicit right
  margin.

Focused red-green evidence:

- The strengthened visual-contract test failed against the pre-fix `1180`
  width comparison SVG.
- After the layout fix, focused Goal 019 tests passed:
  `uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
  (`5` passed).

Final clipping-fix validation completed:

- `git diff --check`
- `uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_spread_impact.py --no-cov`
  (`5` passed)
- `uv run pytest tests/test_synth_medium_landscape.py --no-cov`
  (`5` passed)
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest` (`108` passed, coverage `93.56%`)
- `uv build`
- `uv run python scripts/build_synth_medium_observation_design.py`
  (`18` files written)
- `git status --ignored --short artifacts dist`
  (`!! artifacts/`, `!! dist/`)

No observation regime, survey probability, selected default, table schema,
numerical/scientific outcome, Goal 017 landscape, Goal 018 truth,
reconstruction, fitting, inference, real-data, broad-sweep, remote-compute,
commit, push, generated-artifact staging, or Goal 020 work was performed.

## 2026-06-15 - Review Montage Overlap Fix

Review feedback found that `review_montage.svg` still had a human-review
blocker: top-panel legends collided with lower-panel titles in Quick Look
rendering. The fix remained visual/layout-only.

Changes:

- Increased `review_montage.svg` height from `1120` to `1360`.
- Reworked the montage into explicit two-column panel boxes with larger
  vertical spacing: row spacing `660`, panel top start `50`, panel box width
  `560`, map height `432`, and legends placed below maps with reserved space.
- Added per-panel `<g id="panel-...">` groups with deterministic layout
  attributes: `data-title-y`, `data-map-top`, `data-map-bottom`,
  `data-legend-top`, `data-legend-bottom`, and `data-panel-bottom`.
- Strengthened `tests/test_synth_medium_observation_design.py` so it parses
  these bounds and asserts title/map/legend ordering, panel bottom within SVG
  height, and at least `40` pixels between an upper legend and the next lower
  title in the same column.
- Preserved the comparison-table no-clipping test and all map legend/decode
  semantics.
- Updated `spec/synth_medium_observation_design_review_pack.md` so the review
  montage must reserve non-overlapping panel boxes and expose deterministic
  layout bounds.

Focused red-green evidence:

- The new review-montage layout test failed against the pre-fix montage because
  the required panel layout bounds were absent.
- After the layout fix, focused Goal 019 tests passed:
  `uv run pytest tests/test_synth_medium_observation_design.py --no-cov`
  (`5` passed).

No observation regime, survey probability, selected default, table schema,
numerical/scientific outcome, Goal 017 landscape, Goal 018 truth,
reconstruction, fitting, inference, real-data, broad-sweep, remote-compute,
commit, push, generated-artifact staging, or Goal 020 work was performed.
