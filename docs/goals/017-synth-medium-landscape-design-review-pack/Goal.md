# Goal 017: Synth-Medium Landscape Design Review Pack

## Objective

Build a deterministic `synth-medium` landscape generator and review pack that
creates a richer synthetic spatial substrate for later predator-spread and
prey-impact experiments, then stops for human visual and audit-table review.

This goal is landscape design only. It should not simulate predator spread,
prey response, observations, reconstruction, compatibility screens,
parameter recovery, or inference. The acceptance gate is whether Barry can
inspect the generated maps and audit tables and approve the landscape as a
credible next synthetic substrate.

## Context

Goals 009-016 showed that `synth-small` was valuable but likely exhausted as
an identifiability test:

- `synth-small` exposed response-only failure modes and made the finite-target
  and timing-error problems auditable.
- Goal 016 found that deterministic response-observable timing and
  finite-support rules carry some signal but do not restore compatibility or
  materially approach truth-guided references.
- The current `25 x 25` grid and simple front-band structure make spatial
  gains overfit-prone diagnostics rather than robust method evidence.

Barry's proposed next scientific move is to create a richer synthetic
landscape before attempting new backfitting or inference. The desired
landscape should be larger and more structured, with impassable water blocks,
low-quality matrix, high-quality patches, corridors, spatial aggregation, and
multiple colonisation/source zones along one frontier.

The orchestrator judgement is to split this into two goals:

- Goal 017: design and audit the `synth-medium` landscape only.
- Goal 018, only after Barry approves Goal 017 outputs: simulate predator
  spread and prey impact across the approved landscape.

## Scientific Question

Can we create a deterministic medium-sized landscape that is richer than
`synth-small`, visually interpretable, nontrivially connected, and suitable
for later spread/impact simulations without already building the simulation
or inference machinery?

## In Scope

- Add `spec/synth_medium_landscape.md`.
- Add a focused `synth-medium` landscape module, probably under
  `src/spatext/synth/medium/`.
- Add a CLI script, probably `scripts/build_synth_medium_landscape.py`.
- Generate a deterministic landscape with:
  - larger spatial extent than `synth-small`;
  - impassable water or barrier cells;
  - low-quality matrix cells;
  - high-quality habitat patches;
  - medium-quality transition/habitat-edge zones;
  - corridors connecting some higher-quality areas;
  - spatial contagion/aggregation rather than salt-and-pepper randomness;
  - multiple frontier/source zones along one broad invasion edge.
- Emit durable CSV/JSON/Markdown audit artifacts.
- Emit deterministic visual review artifacts, preferably SVG maps written
  without adding plotting dependencies:
  - habitat-class map;
  - quality-surface map;
  - water/barrier map;
  - corridor and seed/source-zone map;
  - reachable-area or distance-to-source map;
  - a compact review montage.
- Add tests for reproducibility, topology, connectivity, class counts,
  artifact contracts, visual file emission, and boundary labels.
- Update exports, README, `AGENTS.md` if the authoritative spec list changes,
  `spec/report_log.md`, and this goal log.

## Out Of Scope

- Predator spread simulation.
- Prey abundance dynamics or prey-impact simulation.
- Observation models.
- Extirpation reconstruction.
- Summary-vector or compatibility-screen changes.
- Response-rule adoption.
- ABC, POM, MCMC, likelihood fitting, posterior claims, or parameter
  recovery.
- Real-data analysis.
- Broad parameter sweeps.
- Remote compute.
- Commit or push.

## Landscape Design Requirements

The default design should be deterministic and seed-controlled. It should be
larger and less geometrically trivial than `synth-small`; a grid around
`60 x 60` to `80 x 80` is a reasonable target unless repo constraints argue
otherwise.

The generator should produce at least these conceptual layers:

- `cell_id`, row, column, and coordinates;
- passability (`land`, `water`, or other impassable barrier class);
- habitat class, e.g. `water`, `low_quality_matrix`, `medium_quality`,
  `high_quality_patch`, `corridor`, `source_zone`;
- continuous habitat quality or suitability in `[0, 1]` for passable cells;
- deterministic high-quality patch IDs;
- deterministic water/barrier component IDs;
- deterministic corridor IDs;
- source/colonisation zone IDs along one frontier;
- graph-neighbour relationships for passable cells;
- distance to nearest source over the passable graph;
- reachability from the source zones;
- optional local-neighbourhood/context summaries that help audit contagion.

The landscape should avoid two failure modes:

- a near-linear homogeneous wave theatre equivalent to `synth-small`;
- visually random speckle with no ecologically interpretable aggregation.

## Required Outputs

Write a deterministic artifact bundle under:

```text
artifacts/synth_medium_landscape/
```

Required files:

- `landscape_config.json`
- `cells.csv`
- `adjacency.csv`
- `patch_summary.csv`
- `corridor_summary.csv`
- `water_component_summary.csv`
- `source_zone_summary.csv`
- `connectivity_summary.csv`
- `quality_summary.csv`
- `verification.json`
- `report.md`

Required visual review files under:

```text
artifacts/synth_medium_landscape/visuals/
```

- `habitat_classes.svg`
- `quality_surface.svg`
- `water_barriers.svg`
- `corridors_and_sources.svg`
- `source_distance.svg`
- `review_montage.svg`

The JSON outputs must clearly label:

- `synthetic_only: true`
- `landscape_design_only: true`
- `visual_review_required: true`
- `no_predator_spread: true`
- `no_prey_dynamics: true`
- `no_observation_model: true`
- `no_reconstruction_or_inference: true`
- `no_real_data: true`

## Audit Table Requirements

`cells.csv`
: One row per grid cell with location, passability, habitat class, quality,
  patch/corridor/source IDs where relevant, source reachability, source
  distance, and enough categorical fields for visual checks.

`adjacency.csv`
: Passable graph edges. Water/barrier cells must not appear as passable graph
  endpoints. Include edge endpoint IDs and edge class if useful.

`patch_summary.csv`
: One row per high-quality patch or habitat component, with cell count,
  bounding box, quality summaries, and whether it connects to a corridor.

`corridor_summary.csv`
: One row per corridor, with cell count, endpoints or connected patch IDs,
  mean quality, and whether it reaches a source zone.

`water_component_summary.csv`
: One row per water/barrier component, with cell count, bounding box, and
  whether it fragments passable land.

`source_zone_summary.csv`
: One row per source/colonisation zone, with frontier location, cell count,
  neighbouring passable cells, and distance-surface metadata.

`connectivity_summary.csv`
: Landscape-level and component-level connectivity checks, including passable
  cell count, largest connected passable component, unreachable passable
  count, source-reachable count, and shortest-path distance summaries.

`quality_summary.csv`
: Habitat-quality distribution by class and whole landscape, including min,
  max, mean, quantiles, and class fractions.

## Visual Review Requirements

The visuals should be designed for human sanity checking, not publication
polish. They should make it easy to answer:

- Are water/barrier cells visually coherent and impassable?
- Are habitat patches aggregated rather than speckled?
- Are corridors visible and ecologically interpretable?
- Are source zones multiple and on the intended frontier?
- Is the source-distance surface nontrivial and not simply a linear gradient?
- Is there enough heterogeneity to support a future spread simulation?

The report should include relative links to all visual files and a compact
interpretive summary. If SVG rendering is used, keep files deterministic and
self-contained.

## Acceptance Criteria

- The spec exists and is implemented.
- The CLI writes the required bundle and visual review files.
- The landscape is deterministic: repeated builds with the same config produce
  identical core CSV/JSON/SVG contents.
- The grid is larger than `synth-small`.
- Water/barrier cells are impassable and excluded from passable adjacency.
- Passable land has at least one large source-reachable component.
- There are multiple source zones along one frontier.
- Habitat classes include low-quality matrix, higher-quality patches, and
  corridors.
- Patch, corridor, water, quality, source-zone, and connectivity audit tables
  reconcile with `cells.csv`.
- Visual files exist, are non-empty, and are referenced from `report.md`.
- `verification.json` passes and records the landscape-design-only boundary.
- Focused tests pass.
- Proportionate full repository validation passes.
- Generated artifacts remain unstaged.
- No commit or push is performed.
- On completion or blockage, send a short wake-up to the SpatExt orchestrator
  thread and wait for review.
