from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable
from csv import writer
from dataclasses import dataclass
from itertools import pairwise
from json import dumps
from math import exp, hypot, sin
from os import PathLike
from pathlib import Path

type CsvValue = str | int | float | bool | None
type CsvRow = dict[str, CsvValue]

DEFAULT_SYNTH_MEDIUM_LANDSCAPE_OUTPUT_DIR = Path("artifacts/synth_medium_landscape")
SYNTH_MEDIUM_LANDSCAPE_OUTPUT_FILES = (
    "landscape_config.json",
    "cells.csv",
    "adjacency.csv",
    "patch_summary.csv",
    "corridor_summary.csv",
    "water_component_summary.csv",
    "source_zone_summary.csv",
    "connectivity_summary.csv",
    "quality_summary.csv",
    "verification.json",
    "report.md",
)
SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES = (
    "habitat_classes.svg",
    "quality_surface.svg",
    "water_barriers.svg",
    "corridors_and_sources.svg",
    "source_distance.svg",
    "review_montage.svg",
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "landscape_design_only": True,
    "visual_review_required": True,
    "no_predator_spread": True,
    "no_prey_dynamics": True,
    "no_observation_model": True,
    "no_reconstruction_or_inference": True,
    "no_real_data": True,
}

REQUIRED_HABITAT_CLASSES = (
    "water",
    "low_quality_matrix",
    "medium_quality",
    "high_quality_patch",
    "corridor",
    "source_zone",
)


@dataclass(frozen=True, slots=True)
class SynthMediumLandscapeConfig:
    rows: int = 72
    cols: int = 84
    neighborhood: str = "rook"
    deterministic_seed: int = 20260614
    source_reachability_min_fraction: float = 0.85
    source_frontier: str = "west"
    synth_small_reference_rows: int = 25
    synth_small_reference_cols: int = 25

    def to_dict(self) -> dict[str, object]:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "cell_count": self.rows * self.cols,
            "neighborhood": self.neighborhood,
            "deterministic_seed": self.deterministic_seed,
            "source_reachability_min_fraction": self.source_reachability_min_fraction,
            "source_frontier": self.source_frontier,
            "synth_small_reference_rows": self.synth_small_reference_rows,
            "synth_small_reference_cols": self.synth_small_reference_cols,
            "output_files": list(SYNTH_MEDIUM_LANDSCAPE_OUTPUT_FILES),
            "visual_files": [f"visuals/{name}" for name in SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES],
            **BOUNDARY_LABELS,
        }


@dataclass(frozen=True, slots=True)
class PatchDefinition:
    patch_id: str
    center_row: float
    center_col: float
    row_radius: float
    col_radius: float


@dataclass(frozen=True, slots=True)
class CorridorDefinition:
    corridor_id: str
    waypoints: tuple[tuple[int, int], ...]
    endpoint_role: str


@dataclass(frozen=True, slots=True)
class SourceZoneDefinition:
    source_zone_id: str
    row_start: int
    row_end: int
    col_start: int = 0
    col_end: int = 2
    frontier: str = "west"


@dataclass(frozen=True, slots=True)
class LandscapeCell:
    cell_id: int
    row: int
    col: int
    x_coord: float
    y_coord: float
    passability: str
    habitat_class: str
    quality: float
    patch_id: str
    corridor_id: str
    source_zone_id: str
    water_component_id: str
    source_reachable: bool
    source_distance: int | None
    passable_component_id: str
    row_band: str
    col_band: str
    passable_neighbor_count: int
    water_neighbor_count: int

    def to_csv_row(self) -> CsvRow:
        return {
            "cell_id": self.cell_id,
            "row": self.row,
            "col": self.col,
            "x_coord": self.x_coord,
            "y_coord": self.y_coord,
            "passability": self.passability,
            "habitat_class": self.habitat_class,
            "quality": self.quality,
            "patch_id": self.patch_id,
            "corridor_id": self.corridor_id,
            "source_zone_id": self.source_zone_id,
            "water_component_id": self.water_component_id,
            "source_reachable": self.source_reachable,
            "source_distance": self.source_distance,
            "passable_component_id": self.passable_component_id,
            "row_band": self.row_band,
            "col_band": self.col_band,
            "passable_neighbor_count": self.passable_neighbor_count,
            "water_neighbor_count": self.water_neighbor_count,
        }


@dataclass(frozen=True, slots=True)
class LandscapeAdjacencyEdge:
    source_cell_id: int
    target_cell_id: int
    source_row: int
    source_col: int
    target_row: int
    target_col: int
    edge_class: str

    def to_csv_row(self) -> CsvRow:
        return {
            "source_cell_id": self.source_cell_id,
            "target_cell_id": self.target_cell_id,
            "source_row": self.source_row,
            "source_col": self.source_col,
            "target_row": self.target_row,
            "target_col": self.target_col,
            "edge_class": self.edge_class,
        }


@dataclass(frozen=True, slots=True)
class SynthMediumLandscapeCheck:
    name: str
    passed: bool
    details: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "details": self.details}


@dataclass(frozen=True, slots=True)
class SynthMediumLandscapeResult:
    config: SynthMediumLandscapeConfig
    cells: tuple[LandscapeCell, ...]
    adjacency: tuple[LandscapeAdjacencyEdge, ...]
    patch_summary_rows: tuple[CsvRow, ...]
    corridor_summary_rows: tuple[CsvRow, ...]
    water_component_summary_rows: tuple[CsvRow, ...]
    source_zone_summary_rows: tuple[CsvRow, ...]
    connectivity_summary_rows: tuple[CsvRow, ...]
    quality_summary_rows: tuple[CsvRow, ...]
    verification_checks: tuple[SynthMediumLandscapeCheck, ...]
    visual_svgs: dict[str, str]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def summary_dict(self) -> dict[str, object]:
        habitat_counts: dict[str, int] = {}
        for cell in self.cells:
            habitat_counts[cell.habitat_class] = habitat_counts.get(cell.habitat_class, 0) + 1
        passable_count = sum(cell.passability == "passable" for cell in self.cells)
        reachable_count = sum(cell.source_reachable for cell in self.cells)
        water_count = habitat_counts.get("water", 0)
        return {
            "rows": self.config.rows,
            "cols": self.config.cols,
            "cell_count": len(self.cells),
            "passable_cell_count": passable_count,
            "water_cell_count": water_count,
            "water_fraction": water_count / len(self.cells),
            "source_reachable_cell_count": reachable_count,
            "source_reachable_fraction_of_passable": safe_fraction(reachable_count, passable_count),
            "habitat_class_counts": habitat_counts,
            "patch_count": len(self.patch_summary_rows),
            "corridor_count": len(self.corridor_summary_rows),
            "source_zone_count": len(self.source_zone_summary_rows),
        }

    def config_payload(self) -> dict[str, object]:
        return {**self.config.to_dict(), "summary": self.summary_dict()}

    def verification_payload(self) -> dict[str, object]:
        return {
            **BOUNDARY_LABELS,
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
            "summary": self.summary_dict(),
        }

    def write_artifacts(self, output_dir: str | PathLike[str]) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        visuals_dir = target_dir / "visuals"
        visuals_dir.mkdir(parents=True, exist_ok=True)

        written: list[Path] = []
        config_path = target_dir / "landscape_config.json"
        config_path.write_text(
            dumps(self.config_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(config_path)

        table_specs: tuple[tuple[str, tuple[str, ...], tuple[CsvRow, ...]], ...] = (
            ("cells.csv", CELL_COLUMNS, tuple(cell.to_csv_row() for cell in self.cells)),
            (
                "adjacency.csv",
                ADJACENCY_COLUMNS,
                tuple(edge.to_csv_row() for edge in self.adjacency),
            ),
            ("patch_summary.csv", PATCH_SUMMARY_COLUMNS, self.patch_summary_rows),
            ("corridor_summary.csv", CORRIDOR_SUMMARY_COLUMNS, self.corridor_summary_rows),
            (
                "water_component_summary.csv",
                WATER_COMPONENT_SUMMARY_COLUMNS,
                self.water_component_summary_rows,
            ),
            ("source_zone_summary.csv", SOURCE_ZONE_SUMMARY_COLUMNS, self.source_zone_summary_rows),
            (
                "connectivity_summary.csv",
                CONNECTIVITY_SUMMARY_COLUMNS,
                self.connectivity_summary_rows,
            ),
            ("quality_summary.csv", QUALITY_SUMMARY_COLUMNS, self.quality_summary_rows),
        )
        for filename, columns, rows in table_specs:
            path = target_dir / filename
            write_csv_rows(path, columns, rows)
            written.append(path)

        verification_path = target_dir / "verification.json"
        verification_path.write_text(
            dumps(self.verification_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(verification_path)

        report_path = target_dir / "report.md"
        report_path.write_text(render_synth_medium_landscape_report(self), encoding="utf-8")
        written.append(report_path)

        for visual_name in SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES:
            path = visuals_dir / visual_name
            path.write_text(self.visual_svgs[visual_name], encoding="utf-8")
            written.append(path)

        return tuple(written)


CELL_COLUMNS = (
    "cell_id",
    "row",
    "col",
    "x_coord",
    "y_coord",
    "passability",
    "habitat_class",
    "quality",
    "patch_id",
    "corridor_id",
    "source_zone_id",
    "water_component_id",
    "source_reachable",
    "source_distance",
    "passable_component_id",
    "row_band",
    "col_band",
    "passable_neighbor_count",
    "water_neighbor_count",
)
ADJACENCY_COLUMNS = (
    "source_cell_id",
    "target_cell_id",
    "source_row",
    "source_col",
    "target_row",
    "target_col",
    "edge_class",
)
PATCH_SUMMARY_COLUMNS = (
    "patch_id",
    "cell_count",
    "min_row",
    "max_row",
    "min_col",
    "max_col",
    "mean_quality",
    "min_quality",
    "max_quality",
    "connected_to_corridor",
    "connected_corridor_ids",
    "source_reachable_cell_count",
    "source_reachable_fraction",
)
CORRIDOR_SUMMARY_COLUMNS = (
    "corridor_id",
    "cell_count",
    "endpoint_role",
    "connected_patch_ids",
    "connected_source_zone_ids",
    "mean_quality",
    "source_reachable_cell_count",
    "source_reachable_fraction",
)
WATER_COMPONENT_SUMMARY_COLUMNS = (
    "water_component_id",
    "cell_count",
    "min_row",
    "max_row",
    "min_col",
    "max_col",
    "touches_boundary",
    "fragmentation_risk_class",
)
SOURCE_ZONE_SUMMARY_COLUMNS = (
    "source_zone_id",
    "frontier",
    "cell_count",
    "min_row",
    "max_row",
    "min_col",
    "max_col",
    "neighbouring_passable_cell_count",
    "mean_quality",
    "min_source_distance",
    "max_source_distance",
    "mean_source_distance",
)
CONNECTIVITY_SUMMARY_COLUMNS = (
    "summary_scope",
    "component_id",
    "passable_cell_count",
    "passable_component_count",
    "largest_connected_passable_component_cell_count",
    "source_reachable_cell_count",
    "unreachable_passable_cell_count",
    "source_reachable_fraction",
    "min_source_distance",
    "max_source_distance",
    "mean_source_distance",
)
QUALITY_SUMMARY_COLUMNS = (
    "habitat_class",
    "cell_count",
    "cell_fraction",
    "min_quality",
    "q25_quality",
    "median_quality",
    "mean_quality",
    "q75_quality",
    "max_quality",
)


def default_synth_medium_landscape_config() -> SynthMediumLandscapeConfig:
    return SynthMediumLandscapeConfig()


def build_synth_medium_landscape(
    config: SynthMediumLandscapeConfig | None = None,
) -> SynthMediumLandscapeResult:
    landscape_config = config or default_synth_medium_landscape_config()
    validate_config(landscape_config)

    water_mask = build_water_mask(landscape_config)
    patch_ids = build_patch_ids(landscape_config, water_mask)
    medium_mask = build_medium_quality_mask(landscape_config, water_mask, patch_ids)
    source_zone_ids = build_source_zone_ids(landscape_config, water_mask)
    corridor_ids = build_corridor_ids(landscape_config, water_mask, patch_ids, source_zone_ids)
    water_component_ids = label_components(landscape_config, water_mask, "water_component")

    passable_mask = [
        [not water_mask[row][col] for col in range(landscape_config.cols)]
        for row in range(landscape_config.rows)
    ]
    adjacency = build_passable_adjacency(
        landscape_config,
        passable_mask,
        corridor_ids,
        source_zone_ids,
        patch_ids,
    )
    passable_component_ids = label_components(
        landscape_config,
        passable_mask,
        "passable_component",
    )
    source_distances = compute_source_distances(landscape_config, passable_mask, source_zone_ids)

    cells = build_cells(
        landscape_config,
        water_mask,
        patch_ids,
        medium_mask,
        source_zone_ids,
        corridor_ids,
        water_component_ids,
        passable_component_ids,
        source_distances,
    )
    patch_summary_rows = build_patch_summary_rows(landscape_config, cells)
    corridor_summary_rows = build_corridor_summary_rows(landscape_config, cells)
    water_component_summary_rows = build_water_component_summary_rows(landscape_config, cells)
    source_zone_summary_rows = build_source_zone_summary_rows(landscape_config, cells)
    connectivity_summary_rows = build_connectivity_summary_rows(landscape_config, cells)
    quality_summary_rows = build_quality_summary_rows(cells)
    visual_svgs = build_visual_svgs(landscape_config, cells)
    checks = verify_synth_medium_landscape(
        landscape_config,
        cells,
        adjacency,
        patch_summary_rows,
        corridor_summary_rows,
        water_component_summary_rows,
        source_zone_summary_rows,
        connectivity_summary_rows,
        quality_summary_rows,
        visual_svgs,
    )

    return SynthMediumLandscapeResult(
        config=landscape_config,
        cells=cells,
        adjacency=adjacency,
        patch_summary_rows=patch_summary_rows,
        corridor_summary_rows=corridor_summary_rows,
        water_component_summary_rows=water_component_summary_rows,
        source_zone_summary_rows=source_zone_summary_rows,
        connectivity_summary_rows=connectivity_summary_rows,
        quality_summary_rows=quality_summary_rows,
        verification_checks=checks,
        visual_svgs=visual_svgs,
    )


def validate_config(config: SynthMediumLandscapeConfig) -> None:
    if (
        config.rows <= config.synth_small_reference_rows
        or config.cols <= config.synth_small_reference_cols
    ):
        raise ValueError("synth-medium landscape must be larger than synth-small")
    if config.neighborhood != "rook":
        raise ValueError(f"unsupported neighborhood: {config.neighborhood}")
    if not 0.0 < config.source_reachability_min_fraction <= 1.0:
        raise ValueError("source_reachability_min_fraction must lie in (0, 1]")
    if config.source_frontier != "west":
        raise ValueError(f"unsupported source frontier: {config.source_frontier}")


def build_water_mask(config: SynthMediumLandscapeConfig) -> list[list[bool]]:
    mask = [[False for _ in range(config.cols)] for _ in range(config.rows)]
    lakes = (
        (0.18, 0.30, 0.095, 0.135),
        (0.49, 0.53, 0.095, 0.090),
        (0.78, 0.30, 0.085, 0.130),
        (0.25, 0.74, 0.070, 0.095),
    )
    for row in range(config.rows):
        row_fraction = normalized(row, config.rows)
        channel_col = round((0.59 + 0.035 * sin(row / 5.0)) * (config.cols - 1))
        in_channel_band = 12 <= row <= config.rows - 12 and not (28 <= row <= 34 or 50 <= row <= 55)
        for col in range(config.cols):
            col_fraction = normalized(col, config.cols)
            in_lake = any(
                ellipse_distance(
                    row_fraction,
                    col_fraction,
                    center_row,
                    center_col,
                    row_radius,
                    col_radius,
                )
                <= 1.0
                for center_row, center_col, row_radius, col_radius in lakes
            )
            in_channel = in_channel_band and abs(col - channel_col) <= 1
            mask[row][col] = in_lake or in_channel
    return mask


def build_patch_ids(
    config: SynthMediumLandscapeConfig,
    water_mask: list[list[bool]],
) -> list[list[str]]:
    patch_grid = [["" for _ in range(config.cols)] for _ in range(config.rows)]
    for patch in patch_definitions(config):
        for row in range(config.rows):
            row_fraction = normalized(row, config.rows)
            for col in range(config.cols):
                if water_mask[row][col]:
                    continue
                col_fraction = normalized(col, config.cols)
                if (
                    ellipse_distance(
                        row_fraction,
                        col_fraction,
                        patch.center_row,
                        patch.center_col,
                        patch.row_radius,
                        patch.col_radius,
                    )
                    <= 1.0
                    and not patch_grid[row][col]
                ):
                    patch_grid[row][col] = patch.patch_id
    return patch_grid


def build_medium_quality_mask(
    config: SynthMediumLandscapeConfig,
    water_mask: list[list[bool]],
    patch_ids: list[list[str]],
) -> list[list[bool]]:
    medium_mask = [[False for _ in range(config.cols)] for _ in range(config.rows)]
    for patch in patch_definitions(config):
        for row in range(config.rows):
            row_fraction = normalized(row, config.rows)
            for col in range(config.cols):
                if water_mask[row][col] or patch_ids[row][col]:
                    continue
                col_fraction = normalized(col, config.cols)
                if (
                    ellipse_distance(
                        row_fraction,
                        col_fraction,
                        patch.center_row,
                        patch.center_col,
                        patch.row_radius,
                        patch.col_radius,
                    )
                    <= 1.55
                ):
                    medium_mask[row][col] = True
    return medium_mask


def build_source_zone_ids(
    config: SynthMediumLandscapeConfig,
    water_mask: list[list[bool]],
) -> list[list[str]]:
    grid = [["" for _ in range(config.cols)] for _ in range(config.rows)]
    for source_zone in source_zone_definitions(config):
        for row in range(source_zone.row_start, source_zone.row_end + 1):
            for col in range(source_zone.col_start, source_zone.col_end + 1):
                if not water_mask[row][col]:
                    grid[row][col] = source_zone.source_zone_id
    return grid


def build_corridor_ids(
    config: SynthMediumLandscapeConfig,
    water_mask: list[list[bool]],
    patch_ids: list[list[str]],
    source_zone_ids: list[list[str]],
) -> list[list[str]]:
    grid = [["" for _ in range(config.cols)] for _ in range(config.rows)]
    for corridor in corridor_definitions(config):
        cells = cells_along_polyline(corridor.waypoints, thickness=1, config=config)
        for row, col in cells:
            if water_mask[row][col] or patch_ids[row][col] or source_zone_ids[row][col]:
                continue
            grid[row][col] = corridor.corridor_id
    return grid


def build_passable_adjacency(
    config: SynthMediumLandscapeConfig,
    passable_mask: list[list[bool]],
    corridor_ids: list[list[str]],
    source_zone_ids: list[list[str]],
    patch_ids: list[list[str]],
) -> tuple[LandscapeAdjacencyEdge, ...]:
    edges: list[LandscapeAdjacencyEdge] = []
    for row in range(config.rows):
        for col in range(config.cols):
            if not passable_mask[row][col]:
                continue
            for target_row, target_col in ((row + 1, col), (row, col + 1)):
                if not in_bounds(config, target_row, target_col):
                    continue
                if not passable_mask[target_row][target_col]:
                    continue
                edge_class = classify_edge(
                    (row, col),
                    (target_row, target_col),
                    corridor_ids,
                    source_zone_ids,
                    patch_ids,
                )
                edges.append(
                    LandscapeAdjacencyEdge(
                        source_cell_id=cell_id(row, col, config.cols),
                        target_cell_id=cell_id(target_row, target_col, config.cols),
                        source_row=row,
                        source_col=col,
                        target_row=target_row,
                        target_col=target_col,
                        edge_class=edge_class,
                    )
                )
    return tuple(edges)


def classify_edge(
    source: tuple[int, int],
    target: tuple[int, int],
    corridor_ids: list[list[str]],
    source_zone_ids: list[list[str]],
    patch_ids: list[list[str]],
) -> str:
    endpoints = (source, target)
    if any(source_zone_ids[row][col] for row, col in endpoints):
        return "source_touching"
    if any(corridor_ids[row][col] for row, col in endpoints):
        return "corridor_touching"
    if any(patch_ids[row][col] for row, col in endpoints):
        return "patch_touching"
    return "matrix"


def label_components(
    config: SynthMediumLandscapeConfig,
    mask: list[list[bool]],
    prefix: str,
) -> list[list[str]]:
    labels = [["" for _ in range(config.cols)] for _ in range(config.rows)]
    component_index = 0
    for row in range(config.rows):
        for col in range(config.cols):
            if not mask[row][col] or labels[row][col]:
                continue
            component_index += 1
            label = f"{prefix}_{component_index}"
            queue: deque[tuple[int, int]] = deque([(row, col)])
            labels[row][col] = label
            while queue:
                current_row, current_col = queue.popleft()
                for neighbor_row, neighbor_col in rook_neighbors(config, current_row, current_col):
                    if not mask[neighbor_row][neighbor_col] or labels[neighbor_row][neighbor_col]:
                        continue
                    labels[neighbor_row][neighbor_col] = label
                    queue.append((neighbor_row, neighbor_col))
    return labels


def compute_source_distances(
    config: SynthMediumLandscapeConfig,
    passable_mask: list[list[bool]],
    source_zone_ids: list[list[str]],
) -> list[list[int | None]]:
    distances: list[list[int | None]] = [
        [None for _ in range(config.cols)] for _ in range(config.rows)
    ]
    queue: deque[tuple[int, int]] = deque()
    for row in range(config.rows):
        for col in range(config.cols):
            if source_zone_ids[row][col]:
                distances[row][col] = 0
                queue.append((row, col))
    while queue:
        row, col = queue.popleft()
        current_distance = distances[row][col]
        if current_distance is None:
            continue
        for neighbor_row, neighbor_col in rook_neighbors(config, row, col):
            if not passable_mask[neighbor_row][neighbor_col]:
                continue
            if distances[neighbor_row][neighbor_col] is not None:
                continue
            distances[neighbor_row][neighbor_col] = current_distance + 1
            queue.append((neighbor_row, neighbor_col))
    return distances


def build_cells(
    config: SynthMediumLandscapeConfig,
    water_mask: list[list[bool]],
    patch_ids: list[list[str]],
    medium_mask: list[list[bool]],
    source_zone_ids: list[list[str]],
    corridor_ids: list[list[str]],
    water_component_ids: list[list[str]],
    passable_component_ids: list[list[str]],
    source_distances: list[list[int | None]],
) -> tuple[LandscapeCell, ...]:
    cells: list[LandscapeCell] = []
    for row in range(config.rows):
        for col in range(config.cols):
            passability = "water" if water_mask[row][col] else "passable"
            habitat_class = classify_habitat(
                row,
                col,
                water_mask,
                patch_ids,
                medium_mask,
                source_zone_ids,
                corridor_ids,
            )
            quality = compute_quality(config, row, col, habitat_class, patch_ids[row][col])
            passable_neighbor_count = 0
            water_neighbor_count = 0
            for neighbor_row, neighbor_col in rook_neighbors(config, row, col):
                if water_mask[neighbor_row][neighbor_col]:
                    water_neighbor_count += 1
                else:
                    passable_neighbor_count += 1
            source_distance = source_distances[row][col]
            cells.append(
                LandscapeCell(
                    cell_id=cell_id(row, col, config.cols),
                    row=row,
                    col=col,
                    x_coord=normalized(col, config.cols),
                    y_coord=normalized(row, config.rows),
                    passability=passability,
                    habitat_class=habitat_class,
                    quality=quality,
                    patch_id=patch_ids[row][col] if habitat_class == "high_quality_patch" else "",
                    corridor_id=corridor_ids[row][col] if habitat_class == "corridor" else "",
                    source_zone_id=source_zone_ids[row][col],
                    water_component_id=water_component_ids[row][col],
                    source_reachable=source_distance is not None and passability == "passable",
                    source_distance=source_distance if passability == "passable" else None,
                    passable_component_id=passable_component_ids[row][col],
                    row_band=row_band(row, config.rows),
                    col_band=col_band(col, config.cols),
                    passable_neighbor_count=passable_neighbor_count,
                    water_neighbor_count=water_neighbor_count,
                )
            )
    return tuple(cells)


def classify_habitat(
    row: int,
    col: int,
    water_mask: list[list[bool]],
    patch_ids: list[list[str]],
    medium_mask: list[list[bool]],
    source_zone_ids: list[list[str]],
    corridor_ids: list[list[str]],
) -> str:
    if water_mask[row][col]:
        return "water"
    if source_zone_ids[row][col]:
        return "source_zone"
    if corridor_ids[row][col]:
        return "corridor"
    if patch_ids[row][col]:
        return "high_quality_patch"
    if medium_mask[row][col]:
        return "medium_quality"
    return "low_quality_matrix"


def compute_quality(
    config: SynthMediumLandscapeConfig,
    row: int,
    col: int,
    habitat_class: str,
    patch_id: str,
) -> float:
    row_fraction = normalized(row, config.rows)
    col_fraction = normalized(col, config.cols)
    broad_gradient = 0.03 * (1.0 - col_fraction) + 0.02 * sin(row_fraction * 10.0)
    if habitat_class == "water":
        return 0.0
    if habitat_class == "source_zone":
        return round_float(0.88 + 0.04 * (1.0 - abs(row_fraction - 0.5)))
    if habitat_class == "corridor":
        return round_float(0.68 + 0.03 * sin((row + col) / 9.0))
    if habitat_class == "high_quality_patch":
        patch = next(
            definition
            for definition in patch_definitions(config)
            if definition.patch_id == patch_id
        )
        distance = ellipse_distance(
            row_fraction,
            col_fraction,
            patch.center_row,
            patch.center_col,
            patch.row_radius,
            patch.col_radius,
        )
        return round_float(0.80 + 0.13 * max(0.0, 1.0 - distance))
    if habitat_class == "medium_quality":
        return round_float(
            0.52 + 0.06 * gaussian_bump(row_fraction, col_fraction, 0.58, 0.55, 0.35)
        )
    low_quality = (
        0.22
        + broad_gradient
        + 0.035
        * gaussian_bump(
            row_fraction,
            col_fraction,
            0.42,
            0.68,
            0.22,
        )
    )
    return round_float(min(max(low_quality, 0.15), 0.39))


def build_patch_summary_rows(
    config: SynthMediumLandscapeConfig,
    cells: tuple[LandscapeCell, ...],
) -> tuple[CsvRow, ...]:
    rows: list[CsvRow] = []
    cell_lookup = cell_lookup_by_coordinate(cells)
    for patch in patch_definitions(config):
        patch_cells = [cell for cell in cells if cell.patch_id == patch.patch_id]
        if not patch_cells:
            continue
        connected_corridor_ids = sorted(
            {
                neighbor.corridor_id
                for cell in patch_cells
                for neighbor in neighboring_cells(config, cell, cell_lookup)
                if neighbor.corridor_id
            }
        )
        reachable_count = sum(cell.source_reachable for cell in patch_cells)
        rows.append(
            {
                "patch_id": patch.patch_id,
                "cell_count": len(patch_cells),
                "min_row": min(cell.row for cell in patch_cells),
                "max_row": max(cell.row for cell in patch_cells),
                "min_col": min(cell.col for cell in patch_cells),
                "max_col": max(cell.col for cell in patch_cells),
                "mean_quality": mean(cell.quality for cell in patch_cells),
                "min_quality": min(cell.quality for cell in patch_cells),
                "max_quality": max(cell.quality for cell in patch_cells),
                "connected_to_corridor": bool(connected_corridor_ids),
                "connected_corridor_ids": ";".join(connected_corridor_ids),
                "source_reachable_cell_count": reachable_count,
                "source_reachable_fraction": safe_fraction(reachable_count, len(patch_cells)),
            }
        )
    return tuple(rows)


def build_corridor_summary_rows(
    config: SynthMediumLandscapeConfig,
    cells: tuple[LandscapeCell, ...],
) -> tuple[CsvRow, ...]:
    rows: list[CsvRow] = []
    cell_lookup = cell_lookup_by_coordinate(cells)
    definitions = {
        definition.corridor_id: definition for definition in corridor_definitions(config)
    }
    for corridor_id in sorted(definitions):
        corridor_cells = [cell for cell in cells if cell.corridor_id == corridor_id]
        if not corridor_cells:
            continue
        connected_patch_ids = sorted(
            {
                neighbor.patch_id
                for cell in corridor_cells
                for neighbor in neighboring_cells(config, cell, cell_lookup)
                if neighbor.patch_id
            }
        )
        connected_source_zone_ids = sorted(
            {
                neighbor.source_zone_id
                for cell in corridor_cells
                for neighbor in neighboring_cells(config, cell, cell_lookup)
                if neighbor.source_zone_id
            }
        )
        reachable_count = sum(cell.source_reachable for cell in corridor_cells)
        rows.append(
            {
                "corridor_id": corridor_id,
                "cell_count": len(corridor_cells),
                "endpoint_role": definitions[corridor_id].endpoint_role,
                "connected_patch_ids": ";".join(connected_patch_ids),
                "connected_source_zone_ids": ";".join(connected_source_zone_ids),
                "mean_quality": mean(cell.quality for cell in corridor_cells),
                "source_reachable_cell_count": reachable_count,
                "source_reachable_fraction": safe_fraction(reachable_count, len(corridor_cells)),
            }
        )
    return tuple(rows)


def build_water_component_summary_rows(
    config: SynthMediumLandscapeConfig,
    cells: tuple[LandscapeCell, ...],
) -> tuple[CsvRow, ...]:
    component_ids = sorted({cell.water_component_id for cell in cells if cell.water_component_id})
    rows: list[CsvRow] = []
    for component_id in component_ids:
        component_cells = [cell for cell in cells if cell.water_component_id == component_id]
        touches_boundary = any(
            cell.row in (0, config.rows - 1) or cell.col in (0, config.cols - 1)
            for cell in component_cells
        )
        row_span = (
            max(cell.row for cell in component_cells)
            - min(cell.row for cell in component_cells)
            + 1
        )
        col_span = (
            max(cell.col for cell in component_cells)
            - min(cell.col for cell in component_cells)
            + 1
        )
        fragmentation_risk = (
            "major_barrier"
            if row_span >= config.rows * 0.35 or col_span >= config.cols * 0.35
            else "local_barrier"
        )
        rows.append(
            {
                "water_component_id": component_id,
                "cell_count": len(component_cells),
                "min_row": min(cell.row for cell in component_cells),
                "max_row": max(cell.row for cell in component_cells),
                "min_col": min(cell.col for cell in component_cells),
                "max_col": max(cell.col for cell in component_cells),
                "touches_boundary": touches_boundary,
                "fragmentation_risk_class": fragmentation_risk,
            }
        )
    return tuple(rows)


def build_source_zone_summary_rows(
    config: SynthMediumLandscapeConfig,
    cells: tuple[LandscapeCell, ...],
) -> tuple[CsvRow, ...]:
    rows: list[CsvRow] = []
    cell_lookup = cell_lookup_by_coordinate(cells)
    for source_zone in source_zone_definitions(config):
        source_cells = [cell for cell in cells if cell.source_zone_id == source_zone.source_zone_id]
        if not source_cells:
            continue
        neighbor_ids = {
            neighbor.cell_id
            for cell in source_cells
            for neighbor in neighboring_cells(config, cell, cell_lookup)
            if neighbor.passability == "passable" and not neighbor.source_zone_id
        }
        distances = [
            cell.source_distance for cell in source_cells if cell.source_distance is not None
        ]
        rows.append(
            {
                "source_zone_id": source_zone.source_zone_id,
                "frontier": source_zone.frontier,
                "cell_count": len(source_cells),
                "min_row": min(cell.row for cell in source_cells),
                "max_row": max(cell.row for cell in source_cells),
                "min_col": min(cell.col for cell in source_cells),
                "max_col": max(cell.col for cell in source_cells),
                "neighbouring_passable_cell_count": len(neighbor_ids),
                "mean_quality": mean(cell.quality for cell in source_cells),
                "min_source_distance": min(distances),
                "max_source_distance": max(distances),
                "mean_source_distance": mean(float(distance) for distance in distances),
            }
        )
    return tuple(rows)


def build_connectivity_summary_rows(
    config: SynthMediumLandscapeConfig,
    cells: tuple[LandscapeCell, ...],
) -> tuple[CsvRow, ...]:
    passable_cells = [cell for cell in cells if cell.passability == "passable"]
    component_ids = sorted({cell.passable_component_id for cell in passable_cells})
    component_sizes = {
        component_id: sum(cell.passable_component_id == component_id for cell in passable_cells)
        for component_id in component_ids
    }
    largest_component_size = max(component_sizes.values(), default=0)
    rows: list[CsvRow] = [
        connectivity_row(
            summary_scope="landscape",
            component_id="all_passable",
            passable_cells=passable_cells,
            passable_component_count=len(component_ids),
            largest_component_size=largest_component_size,
        )
    ]
    for component_id in component_ids:
        component_cells = [
            cell for cell in passable_cells if cell.passable_component_id == component_id
        ]
        rows.append(
            connectivity_row(
                summary_scope="passable_component",
                component_id=component_id,
                passable_cells=component_cells,
                passable_component_count=1,
                largest_component_size=len(component_cells),
            )
        )
    return tuple(rows)


def connectivity_row(
    *,
    summary_scope: str,
    component_id: str,
    passable_cells: list[LandscapeCell],
    passable_component_count: int,
    largest_component_size: int,
) -> CsvRow:
    reachable = [cell for cell in passable_cells if cell.source_reachable]
    distances = [cell.source_distance for cell in reachable if cell.source_distance is not None]
    return {
        "summary_scope": summary_scope,
        "component_id": component_id,
        "passable_cell_count": len(passable_cells),
        "passable_component_count": passable_component_count,
        "largest_connected_passable_component_cell_count": largest_component_size,
        "source_reachable_cell_count": len(reachable),
        "unreachable_passable_cell_count": len(passable_cells) - len(reachable),
        "source_reachable_fraction": safe_fraction(len(reachable), len(passable_cells)),
        "min_source_distance": min(distances) if distances else None,
        "max_source_distance": max(distances) if distances else None,
        "mean_source_distance": mean(float(distance) for distance in distances)
        if distances
        else None,
    }


def build_quality_summary_rows(cells: tuple[LandscapeCell, ...]) -> tuple[CsvRow, ...]:
    groups: list[tuple[str, list[LandscapeCell]]] = [
        ("all_cells", list(cells)),
        ("all_passable", [cell for cell in cells if cell.passability == "passable"]),
    ]
    for habitat_class in REQUIRED_HABITAT_CLASSES:
        groups.append(
            (habitat_class, [cell for cell in cells if cell.habitat_class == habitat_class])
        )

    total_count = len(cells)
    rows: list[CsvRow] = []
    for habitat_class, group_cells in groups:
        qualities = [cell.quality for cell in group_cells]
        rows.append(
            {
                "habitat_class": habitat_class,
                "cell_count": len(group_cells),
                "cell_fraction": safe_fraction(len(group_cells), total_count),
                "min_quality": min(qualities),
                "q25_quality": quantile(qualities, 0.25),
                "median_quality": quantile(qualities, 0.50),
                "mean_quality": mean(qualities),
                "q75_quality": quantile(qualities, 0.75),
                "max_quality": max(qualities),
            }
        )
    return tuple(rows)


def build_visual_svgs(
    config: SynthMediumLandscapeConfig,
    cells: tuple[LandscapeCell, ...],
) -> dict[str, str]:
    return {
        "habitat_classes.svg": render_grid_svg(
            config,
            cells,
            title="Synth-Medium Habitat Classes",
            color_mode="habitat",
        ),
        "quality_surface.svg": render_grid_svg(
            config,
            cells,
            title="Synth-Medium Quality Surface",
            color_mode="quality",
        ),
        "water_barriers.svg": render_grid_svg(
            config,
            cells,
            title="Synth-Medium Water Barriers",
            color_mode="water",
        ),
        "corridors_and_sources.svg": render_grid_svg(
            config,
            cells,
            title="Synth-Medium Corridors And Sources",
            color_mode="corridors",
        ),
        "source_distance.svg": render_grid_svg(
            config,
            cells,
            title="Synth-Medium Source Distance",
            color_mode="distance",
        ),
        "review_montage.svg": render_review_montage_svg(config, cells),
    }


def verify_synth_medium_landscape(
    config: SynthMediumLandscapeConfig,
    cells: tuple[LandscapeCell, ...],
    adjacency: tuple[LandscapeAdjacencyEdge, ...],
    patch_rows: tuple[CsvRow, ...],
    corridor_rows: tuple[CsvRow, ...],
    water_rows: tuple[CsvRow, ...],
    source_rows: tuple[CsvRow, ...],
    connectivity_rows: tuple[CsvRow, ...],
    quality_rows: tuple[CsvRow, ...],
    visual_svgs: dict[str, str],
) -> tuple[SynthMediumLandscapeCheck, ...]:
    habitat_counts = count_by(cells, lambda cell: cell.habitat_class)
    passable_cells = [cell for cell in cells if cell.passability == "passable"]
    reachable_count = sum(cell.source_reachable for cell in passable_cells)
    water_cell_ids = {cell.cell_id for cell in cells if cell.passability == "water"}
    landscape_row = next(row for row in connectivity_rows if row["summary_scope"] == "landscape")
    quality_counts = {str(row["habitat_class"]): csv_int(row["cell_count"]) for row in quality_rows}
    patch_count_reconciles = sum(
        csv_int(row["cell_count"]) for row in patch_rows
    ) == habitat_counts.get("high_quality_patch", 0)
    corridor_count_reconciles = sum(
        csv_int(row["cell_count"]) for row in corridor_rows
    ) == habitat_counts.get("corridor", 0)
    water_count_reconciles = sum(
        csv_int(row["cell_count"]) for row in water_rows
    ) == habitat_counts.get("water", 0)
    source_count_reconciles = sum(
        csv_int(row["cell_count"]) for row in source_rows
    ) == habitat_counts.get("source_zone", 0)
    quality_reconciles = quality_counts.get("all_cells") == len(cells) and quality_counts.get(
        "all_passable"
    ) == len(passable_cells)
    class_quality_reconciles = all(
        quality_counts.get(habitat_class) == habitat_counts.get(habitat_class, 0)
        for habitat_class in REQUIRED_HABITAT_CLASSES
    )
    connectivity_reconciles = (
        csv_int(landscape_row["passable_cell_count"]) == len(passable_cells)
        and csv_int(landscape_row["source_reachable_cell_count"]) == reachable_count
        and csv_int(landscape_row["unreachable_passable_cell_count"])
        == len(passable_cells) - reachable_count
    )

    checks = (
        SynthMediumLandscapeCheck(
            name="dimensions_larger_than_synth_small",
            passed=(
                config.rows > config.synth_small_reference_rows
                and config.cols > config.synth_small_reference_cols
            ),
            details={
                "rows": config.rows,
                "cols": config.cols,
                "synth_small_rows": config.synth_small_reference_rows,
                "synth_small_cols": config.synth_small_reference_cols,
            },
        ),
        SynthMediumLandscapeCheck(
            name="required_habitat_classes",
            passed=set(REQUIRED_HABITAT_CLASSES) <= set(habitat_counts),
            details={"habitat_class_counts": habitat_counts},
        ),
        SynthMediumLandscapeCheck(
            name="water_excluded_from_passable_adjacency",
            passed=all(
                edge.source_cell_id not in water_cell_ids
                and edge.target_cell_id not in water_cell_ids
                for edge in adjacency
            ),
            details={"water_cell_count": len(water_cell_ids), "edge_count": len(adjacency)},
        ),
        SynthMediumLandscapeCheck(
            name="multiple_western_source_zones",
            passed=len(source_rows) >= 3
            and {row["frontier"] for row in source_rows} == {"west"}
            and all(csv_int(row["min_col"]) == 0 for row in source_rows),
            details={"source_zone_count": len(source_rows), "frontier": "west"},
        ),
        SynthMediumLandscapeCheck(
            name="source_reachability",
            passed=safe_fraction(reachable_count, len(passable_cells))
            >= config.source_reachability_min_fraction,
            details={
                "passable_cell_count": len(passable_cells),
                "source_reachable_cell_count": reachable_count,
                "source_reachable_fraction": safe_fraction(reachable_count, len(passable_cells)),
                "minimum_required_fraction": config.source_reachability_min_fraction,
            },
        ),
        SynthMediumLandscapeCheck(
            name="summary_reconciliation",
            passed=(
                patch_count_reconciles
                and corridor_count_reconciles
                and water_count_reconciles
                and source_count_reconciles
                and quality_reconciles
                and class_quality_reconciles
                and connectivity_reconciles
            ),
            details={
                "patch_count_reconciles": patch_count_reconciles,
                "corridor_count_reconciles": corridor_count_reconciles,
                "water_count_reconciles": water_count_reconciles,
                "source_count_reconciles": source_count_reconciles,
                "quality_reconciles": quality_reconciles,
                "class_quality_reconciles": class_quality_reconciles,
                "connectivity_reconciles": connectivity_reconciles,
            },
        ),
        SynthMediumLandscapeCheck(
            name="visual_review_contract",
            passed=set(visual_svgs) == set(SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES)
            and all(
                svg.lstrip().startswith("<svg") and len(svg) > 1000 for svg in visual_svgs.values()
            ),
            details={
                "visual_file_count": len(visual_svgs),
                "visual_files": [f"visuals/{name}" for name in SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES],
            },
        ),
    )
    return checks


def render_synth_medium_landscape_report(result: SynthMediumLandscapeResult) -> str:
    summary = result.summary_dict()
    verification = "passed" if result.passed else "failed"
    visual_lines = "\n".join(
        f"- [`visuals/{name}`](visuals/{name})" for name in SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES
    )
    habitat_counts = summary["habitat_class_counts"]
    assert isinstance(habitat_counts, dict)
    habitat_lines = "\n".join(
        f"- `{name}`: `{habitat_counts.get(name, 0)}`" for name in REQUIRED_HABITAT_CLASSES
    )
    return f"""# Synth-Medium Landscape Review Pack

## Boundary

This bundle is synthetic-only and landscape-design-only. It does not simulate
predator spread, prey dynamics, observations, extirpation reconstruction,
summary-vector or compatibility changes, response-rule adoption, inference, or
real-data analysis.

## Summary

- Dimensions: `{result.config.rows} x {result.config.cols}`
- Cell count: `{summary["cell_count"]}`
- Passable cells: `{summary["passable_cell_count"]}`
- Water cells: `{summary["water_cell_count"]}`
- Source-reachable passable fraction: `{summary["source_reachable_fraction_of_passable"]:.6f}`
- Patch count: `{summary["patch_count"]}`
- Corridor count: `{summary["corridor_count"]}`
- Source-zone count: `{summary["source_zone_count"]}`
- Verification: `{verification}`

## Habitat Counts

{habitat_lines}

## Visual Review Files

{visual_lines}

## Review Notes

The default landscape uses coherent water components, aggregated high-quality
patches, medium-quality transition zones, visible corridors, and multiple
western source zones. The source-distance surface is graph-derived over
passable cells and is intended for visual sanity checking before any Goal 018
spread or impact simulation is attempted.
"""


def render_grid_svg(
    config: SynthMediumLandscapeConfig,
    cells: tuple[LandscapeCell, ...],
    *,
    title: str,
    color_mode: str,
    cell_size: int = 7,
) -> str:
    margin = 42
    footer = 24
    width = config.cols * cell_size + (2 * margin)
    height = config.rows * cell_size + (2 * margin) + footer
    max_distance = max(
        (cell.source_distance for cell in cells if cell.source_distance is not None),
        default=1,
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{margin}" y="24" font-size="18" font-family="monospace">{title}</text>',
    ]
    for cell in cells:
        fill = cell_fill(cell, color_mode, max_distance)
        x = margin + (cell.col * cell_size)
        y = margin + (cell.row * cell_size)
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
            f'fill="{fill}" stroke="#ffffff" stroke-width="0.15"/>'
        )
    parts.append(
        f'<text x="{margin}" y="{height - 10}" font-size="12" '
        f'font-family="monospace">rows={config.rows} cols={config.cols} mode={color_mode}</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_review_montage_svg(
    config: SynthMediumLandscapeConfig,
    cells: tuple[LandscapeCell, ...],
) -> str:
    cell_size = 3
    panel_margin = 28
    panel_width = (config.cols * cell_size) + (2 * panel_margin)
    panel_height = (config.rows * cell_size) + panel_margin + 18
    width = panel_width * 2
    height = panel_height * 3
    max_distance = max(
        (cell.source_distance for cell in cells if cell.source_distance is not None),
        default=1,
    )
    panels = (
        ("Habitat", "habitat"),
        ("Quality", "quality"),
        ("Water", "water"),
        ("Corridors Sources", "corridors"),
        ("Source Distance", "distance"),
        ("Passability", "passability"),
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]
    for index, (title, mode) in enumerate(panels):
        panel_col = index % 2
        panel_row = index // 2
        offset_x = panel_col * panel_width
        offset_y = panel_row * panel_height
        parts.append(
            f'<text x="{offset_x + panel_margin}" y="{offset_y + 18}" '
            f'font-size="12" font-family="monospace">{title}</text>'
        )
        for cell in cells:
            fill = cell_fill(cell, mode, max_distance)
            x = offset_x + panel_margin + (cell.col * cell_size)
            y = offset_y + panel_margin + (cell.row * cell_size)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'fill="{fill}" stroke="#ffffff" stroke-width="0.05"/>'
            )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def cell_fill(cell: LandscapeCell, color_mode: str, max_distance: int) -> str:
    if color_mode == "habitat":
        return habitat_color(cell.habitat_class)
    if color_mode == "quality":
        if cell.passability == "water":
            return "#4f9cc9"
        return interpolate_hex("#f7f3dd", "#2f7d42", cell.quality)
    if color_mode == "water":
        return "#1d6fa5" if cell.passability == "water" else "#e9f5df"
    if color_mode == "corridors":
        if cell.passability == "water":
            return "#4f9cc9"
        if cell.source_zone_id:
            return "#9f3f8d"
        if cell.corridor_id:
            return "#d99a2b"
        if cell.patch_id:
            return "#3b7f32"
        return "#ece9d1"
    if color_mode == "distance":
        if cell.passability == "water":
            return "#4f9cc9"
        if cell.source_distance is None:
            return "#111827"
        return interpolate_hex("#f7f7d4", "#522c8a", cell.source_distance / max(max_distance, 1))
    if color_mode == "passability":
        return "#4f9cc9" if cell.passability == "water" else "#6aa84f"
    raise ValueError(f"unsupported color mode: {color_mode}")


def habitat_color(habitat_class: str) -> str:
    return {
        "water": "#4f9cc9",
        "low_quality_matrix": "#e7e5d0",
        "medium_quality": "#a4c48d",
        "high_quality_patch": "#397a35",
        "corridor": "#d9a441",
        "source_zone": "#9f3f8d",
    }[habitat_class]


def patch_definitions(config: SynthMediumLandscapeConfig) -> tuple[PatchDefinition, ...]:
    return (
        PatchDefinition("patch_northwest", 0.18, 0.18, 0.070, 0.085),
        PatchDefinition("patch_north_central", 0.23, 0.46, 0.075, 0.090),
        PatchDefinition("patch_mid_east", 0.45, 0.72, 0.090, 0.085),
        PatchDefinition("patch_southwest", 0.75, 0.18, 0.085, 0.095),
        PatchDefinition("patch_south_central", 0.67, 0.51, 0.085, 0.100),
        PatchDefinition("patch_southeast", 0.80, 0.77, 0.080, 0.100),
    )


def source_zone_definitions(config: SynthMediumLandscapeConfig) -> tuple[SourceZoneDefinition, ...]:
    return (
        SourceZoneDefinition("source_west_north", 6, 13),
        SourceZoneDefinition("source_west_mid", 31, 39),
        SourceZoneDefinition("source_west_south", 56, 65),
    )


def corridor_definitions(config: SynthMediumLandscapeConfig) -> tuple[CorridorDefinition, ...]:
    return (
        CorridorDefinition(
            "corridor_north_source_to_central",
            (
                (10, 3),
                (12, 12),
                (16, 26),
                (17, 37),
            ),
            "source_to_patch",
        ),
        CorridorDefinition(
            "corridor_mid_source_to_south_central",
            (
                (35, 3),
                (42, 15),
                (47, 29),
                (49, 41),
            ),
            "source_to_patch",
        ),
        CorridorDefinition(
            "corridor_south_source_to_southwest",
            (
                (61, 3),
                (58, 10),
                (54, 16),
            ),
            "source_to_patch",
        ),
        CorridorDefinition(
            "corridor_central_to_mid_east",
            (
                (49, 45),
                (42, 53),
                (34, 61),
            ),
            "patch_to_patch",
        ),
        CorridorDefinition(
            "corridor_south_central_to_southeast",
            (
                (54, 49),
                (58, 59),
                (62, 70),
            ),
            "patch_to_patch",
        ),
    )


def cells_along_polyline(
    waypoints: tuple[tuple[int, int], ...],
    *,
    thickness: int,
    config: SynthMediumLandscapeConfig,
) -> set[tuple[int, int]]:
    cells: set[tuple[int, int]] = set()
    for start, end in pairwise(waypoints):
        for row, col in cells_along_line(start, end):
            for delta_row in range(-thickness, thickness + 1):
                for delta_col in range(-thickness, thickness + 1):
                    target_row = row + delta_row
                    target_col = col + delta_col
                    if (
                        in_bounds(config, target_row, target_col)
                        and abs(delta_row) + abs(delta_col) <= thickness
                    ):
                        cells.add((target_row, target_col))
    return cells


def cells_along_line(start: tuple[int, int], end: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    start_row, start_col = start
    end_row, end_col = end
    steps = max(abs(end_row - start_row), abs(end_col - start_col))
    if steps == 0:
        return (start,)
    cells: list[tuple[int, int]] = []
    for step in range(steps + 1):
        fraction = step / steps
        row = round(start_row + (end_row - start_row) * fraction)
        col = round(start_col + (end_col - start_col) * fraction)
        cells.append((row, col))
    return tuple(dict.fromkeys(cells))


def neighboring_cells(
    config: SynthMediumLandscapeConfig,
    cell: LandscapeCell,
    cell_lookup: dict[tuple[int, int], LandscapeCell],
) -> tuple[LandscapeCell, ...]:
    return tuple(cell_lookup[(row, col)] for row, col in rook_neighbors(config, cell.row, cell.col))


def cell_lookup_by_coordinate(
    cells: tuple[LandscapeCell, ...],
) -> dict[tuple[int, int], LandscapeCell]:
    return {(cell.row, cell.col): cell for cell in cells}


def rook_neighbors(
    config: SynthMediumLandscapeConfig,
    row: int,
    col: int,
) -> tuple[tuple[int, int], ...]:
    candidates = ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1))
    return tuple(
        (target_row, target_col)
        for target_row, target_col in candidates
        if in_bounds(config, target_row, target_col)
    )


def in_bounds(config: SynthMediumLandscapeConfig, row: int, col: int) -> bool:
    return 0 <= row < config.rows and 0 <= col < config.cols


def cell_id(row: int, col: int, cols: int) -> int:
    return row * cols + col


def normalized(index: int, count: int) -> float:
    return index / max(count - 1, 1)


def ellipse_distance(
    row_fraction: float,
    col_fraction: float,
    center_row: float,
    center_col: float,
    row_radius: float,
    col_radius: float,
) -> float:
    return hypot(
        (row_fraction - center_row) / row_radius,
        (col_fraction - center_col) / col_radius,
    )


def gaussian_bump(
    row_fraction: float,
    col_fraction: float,
    center_row: float,
    center_col: float,
    sigma: float,
) -> float:
    squared_distance = (row_fraction - center_row) ** 2 + (col_fraction - center_col) ** 2
    return exp(-squared_distance / (2.0 * sigma**2))


def row_band(row: int, rows: int) -> str:
    fraction = normalized(row, rows)
    if fraction < 1.0 / 3.0:
        return "north_band"
    if fraction < 2.0 / 3.0:
        return "middle_band"
    return "south_band"


def col_band(col: int, cols: int) -> str:
    fraction = normalized(col, cols)
    if fraction < 1.0 / 3.0:
        return "west_band"
    if fraction < 2.0 / 3.0:
        return "central_band"
    return "east_band"


def count_by(
    cells: tuple[LandscapeCell, ...],
    key_function: Callable[[LandscapeCell], str],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for cell in cells:
        key = key_function(cell)
        counts[key] = counts.get(key, 0) + 1
    return counts


def mean(values: Iterable[float]) -> float:
    concrete = [float(value) for value in values]
    if not concrete:
        return 0.0
    return round_float(sum(concrete) / len(concrete))


def quantile(values: list[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return round_float((1.0 - fraction) * ordered[lower] + fraction * ordered[upper])


def safe_fraction(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round_float(numerator / denominator)


def round_float(value: float) -> float:
    return round(float(value), 12)


def write_csv_rows(path: Path, columns: tuple[str, ...], rows: tuple[CsvRow, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(columns)
        for row in rows:
            csv_writer.writerow([format_csv_value(row[column]) for column in columns])


def format_csv_value(value: CsvValue) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def csv_int(value: CsvValue) -> int:
    if value is None or isinstance(value, bool):
        raise TypeError(f"expected integer-like CSV value, got {value!r}")
    return int(value)


def interpolate_hex(start: str, end: str, fraction: float) -> str:
    clamped = min(max(fraction, 0.0), 1.0)
    start_rgb = hex_to_rgb(start)
    end_rgb = hex_to_rgb(end)
    blended = (
        round((1.0 - clamped) * start_rgb[0] + clamped * end_rgb[0]),
        round((1.0 - clamped) * start_rgb[1] + clamped * end_rgb[1]),
        round((1.0 - clamped) * start_rgb[2] + clamped * end_rgb[2]),
    )
    return rgb_to_hex(blended)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    stripped = value.lstrip("#")
    if len(stripped) != 6:
        raise ValueError(f"expected 6 hex characters, got: {value}")
    return (
        int(stripped[0:2], 16),
        int(stripped[2:4], 16),
        int(stripped[4:6], 16),
    )


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    red, green, blue = rgb
    return f"#{red:02x}{green:02x}{blue:02x}"
