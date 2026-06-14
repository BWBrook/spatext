# Synth-Medium Landscape Design Review Pack

Goal 017 adds the first `synth-medium` landscape substrate for human review
before any predator spread, prey-impact, observation, reconstruction, or
inference work begins. The landscape is synthetic-only and landscape-design
only. It exists to give Barry a deterministic, visually inspectable, and
table-auditable spatial substrate that is richer than the `25 x 25`
`synth-small` grid.

## Scope

This module generates a landscape review bundle only.

- It does not simulate predator spread.
- It does not simulate prey dynamics or prey impacts.
- It does not emit observations or reconstructed extirpation times.
- It does not change summary-vector, compatibility-screen, response-rule,
  scoring, candidate, ABC, POM, likelihood, posterior, or real-data contracts.
- It does not make a method claim from spatial/front-band gains.

The default output is a deterministic review pack under:

```text
artifacts/synth_medium_landscape/
```

## Default Landscape

The default landscape is a `72 x 84` rook-adjacent square grid. It is larger
than `synth-small` and deliberately contains spatial structure that is not a
simple homogeneous west-to-east front theatre.

Each cell has:

- `cell_id`, `row`, `col`, and normalized coordinates;
- `passability`, either `passable` or `water`;
- `habitat_class`, one of `water`, `low_quality_matrix`,
  `medium_quality`, `high_quality_patch`, `corridor`, or `source_zone`;
- continuous `quality` in `[0, 1]`;
- optional `patch_id`, `corridor_id`, and `source_zone_id`;
- optional `water_component_id`;
- source reachability and shortest-path source distance over the passable
  graph;
- component and coarse review fields useful for visual and table checks.

The deterministic layer order is:

1. broad low-quality matrix;
2. coherent water/barrier components;
3. aggregated high-quality habitat patches;
4. medium-quality transition zones around those patches;
5. visible corridors connecting selected patches and source zones;
6. multiple source zones along the western frontier.

Water is impassable and is excluded from graph adjacency. Source-distance
metadata are computed only over the passable graph.

## Output Files

The root bundle contains:

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

The `visuals/` subdirectory contains deterministic SVG review maps:

- `habitat_classes.svg`
- `quality_surface.svg`
- `water_barriers.svg`
- `corridors_and_sources.svg`
- `source_distance.svg`
- `review_montage.svg`

The SVG files are self-contained and generated without adding a plotting
dependency.

## Table Contracts

`cells.csv`
: One row per grid cell with location, passability, habitat class, quality,
  patch, corridor, water-component and source-zone IDs where relevant, source
  reachability, source distance, connected-component ID, coarse row/column
  bands, and local passable-neighbour counts.

`adjacency.csv`
: One row per undirected passable rook edge. Water cells must not appear as
  endpoints. The `edge_class` column records whether the edge touches a
  corridor or source-zone cell.

`patch_summary.csv`
: One row per high-quality patch with cell count, bounding box, mean/min/max
  quality, corridor connectivity, and source-reachable counts.

`corridor_summary.csv`
: One row per corridor with cell count, endpoint role, connected patch/source
  IDs, mean quality, and source-reachable counts.

`water_component_summary.csv`
: One row per water component with cell count, bounding box, boundary contact,
  and a simple fragmentation-risk label.

`source_zone_summary.csv`
: One row per source zone with frontier, cell count, bounding box, neighboring
  passable-cell count, and source-distance metadata.

`connectivity_summary.csv`
: Landscape-level and passable-component-level rows recording passable cell
  count, component sizes, unreachable passable count, source-reachable count,
  and shortest-path source-distance summaries.

`quality_summary.csv`
: Habitat-quality distribution by habitat class plus whole-landscape and
  passable-land rows, including class fractions and quantiles.

## Verification

`verification.json` must pass only when:

- the grid is larger than `synth-small`;
- all required habitat classes are present;
- water cells are excluded from passable adjacency endpoints;
- at least three source zones exist on the western frontier;
- most passable land is source-reachable;
- patch, corridor, water, source, connectivity, and quality summaries
  reconcile with `cells.csv`;
- all six SVG review files are included in the output contract;
- all landscape-only boundary labels are present.

JSON outputs include these labels:

- `synthetic_only: true`
- `landscape_design_only: true`
- `visual_review_required: true`
- `no_predator_spread: true`
- `no_prey_dynamics: true`
- `no_observation_model: true`
- `no_reconstruction_or_inference: true`
- `no_real_data: true`

## Recommendation Boundary

This goal can recommend whether the emitted landscape is ready for human
review or whether the landscape contract failed. It must not recommend or
start Goal 018 simulation, production reconstruction-rule changes, inference,
or real-data analysis.
