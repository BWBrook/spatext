# Plan

## 1. Confirm State And Branch

- Report actual working directory and Git state.
- Fetch `origin`.
- Confirm `origin/main` includes Goal 016 commit `fdd865b` or newer.
- Create local branch
  `codex/spatext-goal017-synth-medium-landscape-review` from `origin/main`,
  preserving this untracked Goal 017 packet.
- If branch creation or checkout fails, stop and report the exact blocker. Do
  not force, delete, reset, rebase, or repair by improvisation.

## 2. Refresh Contracts

- Read `AGENTS.md`, `README.md`, `spec/problem_statement.md`,
  `spec/theory.md`, and `spec/report_log.md`.
- Before editing `spec/report_log.md`, search current interaction headings so
  the new entry does not duplicate an earlier number.
- Read the current `synth-small` landscape and truth specs:
  - `spec/synth_small_baseline.md`;
  - `spec/synth_small_predator_truth.md`;
  - `spec/synth_small_observations.md`;
  - `spec/synth_small_response_observable_timing_rule_screen.md`.
- Read Goal 016 and this Goal 017 packet.
- Read the current source/test surfaces for:
  - `src/spatext/spatial.py`;
  - `src/spatext/synth/small/baseline.py`;
  - `src/spatext/synth/small/predator.py`;
  - existing synth-small tests that demonstrate artifact-writing style.

## 3. Write The Spec First

- Add `spec/synth_medium_landscape.md`.
- Define:
  - purpose and scope;
  - default deterministic config;
  - landscape layers;
  - passability and adjacency contract;
  - habitat class and quality-surface contract;
  - water/barrier component contract;
  - patch and corridor contracts;
  - source-zone and source-distance contracts;
  - visual review artifact contract;
  - output artifact contract;
  - verification checks;
  - landscape-only boundary labels;
  - acceptance criteria.

## 4. Test First

- Add `tests/test_synth_medium_landscape.py`.
- Cover:
  - deterministic rebuild with identical CSV/JSON/SVG output;
  - grid dimensions larger than synth-small;
  - required habitat classes exist;
  - water/barrier cells are excluded from passable adjacency;
  - multiple source zones exist on one intended frontier;
  - passable cells include a large source-reachable component;
  - patch, corridor, water, source-zone, quality, and connectivity summaries
    reconcile with `cells.csv`;
  - required visual files exist and are non-empty;
  - `report.md` references all visual files;
  - verification passes and includes landscape-only boundary labels;
  - CLI execution writes the required bundle.
- Run the focused test and confirm it fails before implementation.

## 5. Implement The Landscape Generator

- Create a focused `synth-medium` package surface, probably:
  - `src/spatext/synth/medium/__init__.py`;
  - `src/spatext/synth/medium/landscape.py`.
- Implement deterministic config dataclasses for grid size, seed, water,
  patch, corridor, and source-zone parameters.
- Build the landscape in transparent deterministic layers:
  - broad low-quality matrix;
  - spatially aggregated high-quality patches;
  - medium-quality transition or edge zones;
  - corridors between selected patches and/or source zones;
  - impassable water/barrier components with coherent shapes;
  - multiple source zones along one frontier.
- Build passable adjacency using repo-local graph conventions where practical.
- Compute source reachability and passable shortest-path distances.
- Compute patch, corridor, water, source-zone, connectivity, and quality
  summaries.
- Render deterministic SVG review maps without adding plotting dependencies
  unless a dependency is already approved by the repo.
- Keep implementation modular enough that Goal 018 can consume the landscape
  bundle later without reworking the format.

## 6. Add CLI And Exports

- Add `scripts/build_synth_medium_landscape.py`.
- Export the public API from `src/spatext/synth/medium/__init__.py`.
- If useful for discoverability, update `src/spatext/synth/__init__.py`, but
  avoid broad package restructuring.

## 7. Update Docs And Log

- Update `README.md` with the `synth-medium` landscape design surface,
  command, artifact path, and visual-review expectation.
- Update `AGENTS.md` if the authoritative spec list needs the new spec.
- Update `spec/report_log.md`.
- Update this goal `Log.md` throughout the run with checkpoints and validation
  evidence.

## 8. Validate

Run a proportionate validation ladder:

```bash
git status --short --branch
git diff --check
uv run pytest tests/test_synth_medium_landscape.py --no-cov
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

Run the new CLI:

```bash
uv run python scripts/build_synth_medium_landscape.py
```

Check generated/build artifact handling:

```bash
git status --ignored --short artifacts dist
```

## 9. Report And Wake Up

- Report changed files.
- Report validation results.
- Report generated artifact path and required files.
- Report landscape dimensions, cell counts, habitat class counts, water
  fraction, passable fraction, source-zone count, patch count, corridor count,
  and source-reachable fraction.
- Report visual review file paths.
- Report audit-table highlights and verification outcome.
- Confirm generated artifacts remain unstaged.
- Confirm no predator spread, prey dynamics, observations, reconstruction,
  fitting, inference, real-data work, commit, or push was performed.
- Send a short wake-up to the SpatExt orchestrator thread when complete or
  blocked, then wait for review.
