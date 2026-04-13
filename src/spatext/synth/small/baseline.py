from __future__ import annotations

from csv import writer
from dataclasses import asdict, dataclass, field
from json import dumps
from os import PathLike
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from spatext.spatial import CellGraphDomain, adjacency_edges, build_square_lattice_domain

BoolArray = NDArray[np.bool_]
FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class GaussianBumpConfig:
    center_row: float
    center_col: float
    sigma: float
    weight: float


@dataclass(frozen=True, slots=True)
class SuitabilitySurfaceConfig:
    baseline: float = 0.18
    primary_bump: GaussianBumpConfig = field(
        default_factory=lambda: GaussianBumpConfig(
            center_row=0.28,
            center_col=0.32,
            sigma=0.16,
            weight=0.58,
        )
    )
    secondary_bump: GaussianBumpConfig = field(
        default_factory=lambda: GaussianBumpConfig(
            center_row=0.74,
            center_col=0.68,
            sigma=0.21,
            weight=0.43,
        )
    )
    gradient_row_weight: float = -0.10
    gradient_col_weight: float = 0.08


@dataclass(frozen=True, slots=True)
class SynthSmallBaselineConfig:
    rows: int = 25
    cols: int = 25
    neighborhood: str = "rook"
    suitability: SuitabilitySurfaceConfig = field(default_factory=SuitabilitySurfaceConfig)
    carrying_capacity_max: float = 60.0
    carrying_capacity_floor_fraction: float = 0.22
    intrinsic_growth_rate: float = 0.55
    background_loss: float = 0.04
    dispersal_share: float = 0.18
    allee_scale: float = 0.0
    initial_fraction: float = 0.12
    convergence_tolerance: float = 1e-6
    consecutive_converged_steps: int = 20
    max_steps: int = 8000
    occupancy_threshold: float = 20.0
    raise_on_nonconvergence: bool = True

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EquilibriumDiagnostics:
    converged: bool
    steps: int
    max_relative_change: float
    consecutive_satisfied_steps: int
    tolerance: float

    def to_dict(self) -> dict[str, float | int | bool]:
        return {
            "converged": self.converged,
            "steps": self.steps,
            "max_relative_change": self.max_relative_change,
            "consecutive_satisfied_steps": self.consecutive_satisfied_steps,
            "tolerance": self.tolerance,
        }


@dataclass(frozen=True, slots=True)
class SynthSmallBaselineResult:
    config: SynthSmallBaselineConfig
    domain: CellGraphDomain
    suitability: FloatArray
    carrying_capacity: FloatArray
    equilibrium_abundance: FloatArray
    occupancy: BoolArray
    diagnostics: EquilibriumDiagnostics

    def to_summary_dict(self) -> dict[str, object]:
        return {
            "config": self.config.to_dict(),
            "domain": self.domain.to_metadata(),
            "diagnostics": self.diagnostics.to_dict(),
            "summary": {
                "suitability_min": float(np.min(self.suitability)),
                "suitability_max": float(np.max(self.suitability)),
                "carrying_capacity_min": float(np.min(self.carrying_capacity)),
                "carrying_capacity_max": float(np.max(self.carrying_capacity)),
                "equilibrium_abundance_min": float(np.min(self.equilibrium_abundance)),
                "equilibrium_abundance_max": float(np.max(self.equilibrium_abundance)),
                "equilibrium_abundance_mean": float(np.mean(self.equilibrium_abundance)),
                "equilibrium_abundance_std": float(np.std(self.equilibrium_abundance)),
                "occupancy_fraction": float(np.mean(self.occupancy.astype(np.float64))),
            },
        }

    def write_artifacts(self, output_dir: str | PathLike[str]) -> tuple[Path, ...]:
        return write_synth_small_baseline_artifacts(self, output_dir)


DEFAULT_CONFIG = SynthSmallBaselineConfig()


def default_synth_small_baseline_config() -> SynthSmallBaselineConfig:
    return DEFAULT_CONFIG


def build_synth_small_baseline(
    config: SynthSmallBaselineConfig | None = None,
) -> SynthSmallBaselineResult:
    baseline_config = config or default_synth_small_baseline_config()
    domain = build_square_lattice_domain(
        baseline_config.rows,
        baseline_config.cols,
        neighborhood=baseline_config.neighborhood,
    )
    suitability = generate_suitability_surface(domain, baseline_config)
    carrying_capacity = map_carrying_capacity(suitability, baseline_config)
    equilibrium_abundance, diagnostics = run_to_equilibrium(
        domain, carrying_capacity, baseline_config
    )
    if not diagnostics.converged and baseline_config.raise_on_nonconvergence:
        raise RuntimeError(
            "synth-small baseline failed to converge within the configured iteration cap"
        )
    occupancy = equilibrium_abundance > baseline_config.occupancy_threshold
    return SynthSmallBaselineResult(
        config=baseline_config,
        domain=domain,
        suitability=suitability,
        carrying_capacity=carrying_capacity,
        equilibrium_abundance=equilibrium_abundance,
        occupancy=occupancy,
        diagnostics=diagnostics,
    )


def generate_suitability_surface(
    domain: CellGraphDomain,
    config: SynthSmallBaselineConfig,
) -> FloatArray:
    row_axis = np.linspace(0.0, 1.0, domain.rows, dtype=np.float64)
    col_axis = np.linspace(0.0, 1.0, domain.cols, dtype=np.float64)
    row_grid, col_grid = np.meshgrid(row_axis, col_axis, indexing="ij")

    suitability = np.full((domain.rows, domain.cols), config.suitability.baseline, dtype=np.float64)
    suitability += config.suitability.primary_bump.weight * gaussian_surface(
        row_grid,
        col_grid,
        config.suitability.primary_bump,
    )
    suitability += config.suitability.secondary_bump.weight * gaussian_surface(
        row_grid,
        col_grid,
        config.suitability.secondary_bump,
    )
    suitability += linear_gradient(row_grid, col_grid, config.suitability)
    return np.clip(suitability, 0.0, 1.0)


def gaussian_surface(
    row_grid: FloatArray,
    col_grid: FloatArray,
    config: GaussianBumpConfig,
) -> FloatArray:
    squared_distance = (row_grid - config.center_row) ** 2 + (col_grid - config.center_col) ** 2
    return np.exp(-squared_distance / (2.0 * config.sigma**2))


def linear_gradient(
    row_grid: FloatArray,
    col_grid: FloatArray,
    config: SuitabilitySurfaceConfig,
) -> FloatArray:
    centered_row = 2.0 * (row_grid - 0.5)
    centered_col = 2.0 * (col_grid - 0.5)
    return config.gradient_row_weight * centered_row + config.gradient_col_weight * centered_col


def map_carrying_capacity(
    suitability: FloatArray,
    config: SynthSmallBaselineConfig,
) -> FloatArray:
    floor = config.carrying_capacity_floor_fraction
    scaled = floor + (1.0 - floor) * suitability
    return config.carrying_capacity_max * scaled


def run_to_equilibrium(
    domain: CellGraphDomain,
    carrying_capacity: FloatArray,
    config: SynthSmallBaselineConfig,
) -> tuple[FloatArray, EquilibriumDiagnostics]:
    abundance = config.initial_fraction * carrying_capacity
    consecutive_satisfied_steps = 0
    max_relative_change = float("inf")

    for step in range(1, config.max_steps + 1):
        next_abundance = prey_only_step(domain, abundance, carrying_capacity, config)
        denominator = np.maximum(1.0, abundance)
        max_relative_change = float(np.max(np.abs(next_abundance - abundance) / denominator))
        if max_relative_change < config.convergence_tolerance:
            consecutive_satisfied_steps += 1
        else:
            consecutive_satisfied_steps = 0

        abundance = next_abundance
        if consecutive_satisfied_steps >= config.consecutive_converged_steps:
            return abundance, EquilibriumDiagnostics(
                converged=True,
                steps=step,
                max_relative_change=max_relative_change,
                consecutive_satisfied_steps=consecutive_satisfied_steps,
                tolerance=config.convergence_tolerance,
            )

    return abundance, EquilibriumDiagnostics(
        converged=False,
        steps=config.max_steps,
        max_relative_change=max_relative_change,
        consecutive_satisfied_steps=consecutive_satisfied_steps,
        tolerance=config.convergence_tolerance,
    )


def prey_only_step(
    domain: CellGraphDomain,
    abundance: FloatArray,
    carrying_capacity: FloatArray,
    config: SynthSmallBaselineConfig,
) -> FloatArray:
    allee_factor = compute_allee_factor(abundance, config.allee_scale)
    growth_term = (
        config.intrinsic_growth_rate * allee_factor * (1.0 - (abundance / carrying_capacity))
        - config.background_loss
    )
    local_update = abundance * np.exp(growth_term)
    dispersed = domain.transition_matrix @ local_update.reshape(domain.cell_count)
    dispersed_grid = dispersed.reshape((domain.rows, domain.cols))
    next_abundance = (
        1.0 - config.dispersal_share
    ) * local_update + config.dispersal_share * dispersed_grid
    return np.clip(next_abundance, 0.0, None)


def compute_allee_factor(abundance: FloatArray, allee_scale: float) -> FloatArray:
    if allee_scale <= 0.0:
        return np.ones_like(abundance)
    return 1.0 - (allee_scale / (abundance + allee_scale))


def write_synth_small_baseline_artifacts(
    result: SynthSmallBaselineResult,
    output_dir: str | PathLike[str],
) -> tuple[Path, ...]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    domain_json = target_dir / "domain.json"
    config_json = target_dir / "config.json"
    diagnostics_json = target_dir / "diagnostics.json"
    summary_json = target_dir / "summary.json"
    cells_csv = target_dir / "cells.csv"
    edges_csv = target_dir / "edges.csv"
    surfaces_npz = target_dir / "surfaces.npz"
    suitability_svg = target_dir / "suitability.svg"
    carrying_capacity_svg = target_dir / "carrying_capacity.svg"
    equilibrium_abundance_svg = target_dir / "equilibrium_abundance.svg"
    occupancy_svg = target_dir / "equilibrium_occupancy.svg"

    domain_json.write_text(dumps(result.domain.to_metadata(), indent=2) + "\n", encoding="utf-8")
    config_json.write_text(dumps(result.config.to_dict(), indent=2) + "\n", encoding="utf-8")
    diagnostics_json.write_text(
        dumps(result.diagnostics.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    summary_json.write_text(dumps(result.to_summary_dict(), indent=2) + "\n", encoding="utf-8")
    write_cells_csv(result, cells_csv)
    write_edges_csv(result.domain, edges_csv)
    np.savez_compressed(
        surfaces_npz,
        suitability=result.suitability,
        carrying_capacity=result.carrying_capacity,
        equilibrium_abundance=result.equilibrium_abundance,
        occupancy=result.occupancy.astype(np.int8),
    )
    write_heatmap_svg(result.suitability, suitability_svg, title="Suitability Surface")
    write_heatmap_svg(result.carrying_capacity, carrying_capacity_svg, title="Carrying Capacity")
    write_heatmap_svg(
        result.equilibrium_abundance,
        equilibrium_abundance_svg,
        title="Equilibrium Abundance",
    )
    write_boolean_svg(result.occupancy, occupancy_svg, title="Equilibrium Occupancy")

    return (
        domain_json,
        config_json,
        diagnostics_json,
        summary_json,
        cells_csv,
        edges_csv,
        surfaces_npz,
        suitability_svg,
        carrying_capacity_svg,
        equilibrium_abundance_svg,
        occupancy_svg,
    )


def write_cells_csv(result: SynthSmallBaselineResult, output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(
            [
                "cell_id",
                "row",
                "col",
                "suitability",
                "carrying_capacity",
                "equilibrium_abundance",
                "occupancy",
            ]
        )
        for cell_id, (row, col) in enumerate(result.domain.coordinates.tolist()):
            csv_writer.writerow(
                [
                    cell_id,
                    row,
                    col,
                    float(result.suitability[row, col]),
                    float(result.carrying_capacity[row, col]),
                    float(result.equilibrium_abundance[row, col]),
                    int(result.occupancy[row, col]),
                ]
            )


def write_edges_csv(domain: CellGraphDomain, output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(["source", "target"])
        for source, target in adjacency_edges(domain.adjacency):
            csv_writer.writerow([source, target])


def write_heatmap_svg(surface: FloatArray, output_path: Path, *, title: str) -> None:
    min_value = float(np.min(surface))
    max_value = float(np.max(surface))
    value_range = max(max_value - min_value, 1e-12)
    rows, cols = surface.shape
    cell_size = 20
    margin = 36
    width = cols * cell_size + (2 * margin)
    height = rows * cell_size + (2 * margin) + 40
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{margin}" y="24" font-size="18" font-family="monospace">{title}</text>',
        (
            f'<text x="{margin}" y="{height - 10}" font-size="12" '
            f'font-family="monospace">min={min_value:.3f} max={max_value:.3f}</text>'
        ),
    ]
    for row in range(rows):
        for col in range(cols):
            normalized = (float(surface[row, col]) - min_value) / value_range
            fill = interpolate_hex("#f4f9f4", "#0b5d1e", normalized)
            x = margin + (col * cell_size)
            y = margin + (row * cell_size)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'fill="{fill}" stroke="#d1d5db" stroke-width="0.5"/>'
            )
    parts.append("</svg>")
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_boolean_svg(surface: BoolArray, output_path: Path, *, title: str) -> None:
    rows, cols = surface.shape
    cell_size = 20
    margin = 36
    width = cols * cell_size + (2 * margin)
    height = rows * cell_size + (2 * margin) + 40
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{margin}" y="24" font-size="18" font-family="monospace">{title}</text>',
        (
            f'<text x="{margin}" y="{height - 10}" font-size="12" '
            'font-family="monospace">false=gray true=teal</text>'
        ),
    ]
    for row in range(rows):
        for col in range(cols):
            fill = "#0f766e" if bool(surface[row, col]) else "#d1d5db"
            x = margin + (col * cell_size)
            y = margin + (row * cell_size)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'fill="{fill}" stroke="#f8fafc" stroke-width="0.5"/>'
            )
    parts.append("</svg>")
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def interpolate_hex(start: str, end: str, fraction: float) -> str:
    clamped_fraction = min(max(fraction, 0.0), 1.0)
    start_rgb = hex_to_rgb(start)
    end_rgb = hex_to_rgb(end)
    blended = (
        round((1.0 - clamped_fraction) * start_rgb[0] + clamped_fraction * end_rgb[0]),
        round((1.0 - clamped_fraction) * start_rgb[1] + clamped_fraction * end_rgb[1]),
        round((1.0 - clamped_fraction) * start_rgb[2] + clamped_fraction * end_rgb[2]),
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
