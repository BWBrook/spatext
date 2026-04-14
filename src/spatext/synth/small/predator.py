from __future__ import annotations

import re
from collections import deque
from csv import writer
from dataclasses import asdict, dataclass, field
from json import dumps
from os import PathLike
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from spatext.spatial import CellGraphDomain

from .baseline import (
    SynthSmallBaselineConfig,
    SynthSmallBaselineResult,
    build_synth_small_baseline,
    compute_allee_factor,
    interpolate_hex,
)

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True, slots=True)
class PredatorArrivalConfig:
    introduction_time: int = 4
    front_speed_cells_per_step: float = 1.0
    source_geometry: str = "western_boundary"


@dataclass(frozen=True, slots=True)
class PredatorPressureConfig:
    pre_arrival_leakage: float = 0.0
    ramp_duration: int = 8
    pressure_scale: float = 1.0
    pressure_exponent: float = 1.0


@dataclass(frozen=True, slots=True)
class TypeIIResponseConfig:
    predation_scale: float = 1.0
    half_saturation: float = 6.0


@dataclass(frozen=True, slots=True)
class TrueExtirpationConfig:
    quasi_extirpation_abundance: float = 3.0


@dataclass(frozen=True, slots=True)
class SynthSmallPredatorTruthConfig:
    baseline: SynthSmallBaselineConfig = field(default_factory=SynthSmallBaselineConfig)
    arrival: PredatorArrivalConfig = field(default_factory=PredatorArrivalConfig)
    pressure: PredatorPressureConfig = field(default_factory=PredatorPressureConfig)
    response: TypeIIResponseConfig = field(default_factory=TypeIIResponseConfig)
    extirpation: TrueExtirpationConfig = field(default_factory=TrueExtirpationConfig)
    post_arrival_buffer: int = 24

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredatorTruthDiagnostics:
    simulation_horizon: int
    predator_source_geometry: str
    introduction_time: int
    front_speed_cells_per_step: float
    pressure_ramp_duration: int
    predation_response_form: str
    extirpation_threshold_form: str
    pressure_scale: float
    pressure_exponent: float
    quasi_extirpation_abundance: float
    stayed_finite: bool
    stayed_nonnegative: bool
    used_nonnegative_clipping: bool
    used_missing_for_non_extirpated: bool
    baseline_converged: bool
    max_driver_arrival: int

    def to_dict(self) -> dict[str, int | float | str | bool]:
        return {
            "simulation_horizon": self.simulation_horizon,
            "predator_source_geometry": self.predator_source_geometry,
            "introduction_time": self.introduction_time,
            "front_speed_cells_per_step": self.front_speed_cells_per_step,
            "pressure_ramp_duration": self.pressure_ramp_duration,
            "predation_response_form": self.predation_response_form,
            "extirpation_threshold_form": self.extirpation_threshold_form,
            "pressure_scale": self.pressure_scale,
            "pressure_exponent": self.pressure_exponent,
            "quasi_extirpation_abundance": self.quasi_extirpation_abundance,
            "stayed_finite": self.stayed_finite,
            "stayed_nonnegative": self.stayed_nonnegative,
            "used_nonnegative_clipping": self.used_nonnegative_clipping,
            "used_missing_for_non_extirpated": self.used_missing_for_non_extirpated,
            "baseline_converged": self.baseline_converged,
            "max_driver_arrival": self.max_driver_arrival,
        }


@dataclass(frozen=True, slots=True)
class SynthSmallPredatorTruthResult:
    config: SynthSmallPredatorTruthConfig
    baseline: SynthSmallBaselineResult
    driver_arrival: IntArray
    predator_pressure: FloatArray
    prey_abundance: FloatArray
    true_extirpation: FloatArray
    extirpation_lag: FloatArray
    extirpation_threshold: FloatArray
    diagnostics: PredatorTruthDiagnostics

    @property
    def domain(self) -> CellGraphDomain:
        return self.baseline.domain

    @property
    def suitability(self) -> FloatArray:
        return self.baseline.suitability

    @property
    def carrying_capacity(self) -> FloatArray:
        return self.baseline.carrying_capacity

    @property
    def initial_abundance(self) -> FloatArray:
        return self.baseline.equilibrium_abundance

    @property
    def final_abundance(self) -> FloatArray:
        return np.asarray(self.prey_abundance[-1], dtype=np.float64)

    @property
    def extirpated_mask(self) -> NDArray[np.bool_]:
        return np.isfinite(self.true_extirpation)

    def to_summary_dict(self) -> dict[str, object]:
        extirpated = self.extirpated_mask
        extirpated_count = int(np.sum(extirpated))
        surviving_count = self.domain.cell_count - extirpated_count
        finite_true_extirpation = self.true_extirpation[extirpated]
        finite_lag = self.extirpation_lag[np.isfinite(self.extirpation_lag)]
        return {
            "domain": self.domain.to_metadata(),
            "summary": {
                "suitability_min": float(np.min(self.suitability)),
                "suitability_max": float(np.max(self.suitability)),
                "suitability_mean": float(np.mean(self.suitability)),
                "suitability_std": float(np.std(self.suitability)),
                "initial_abundance_min": float(np.min(self.initial_abundance)),
                "initial_abundance_max": float(np.max(self.initial_abundance)),
                "initial_abundance_mean": float(np.mean(self.initial_abundance)),
                "initial_abundance_std": float(np.std(self.initial_abundance)),
                "driver_arrival_min": int(np.min(self.driver_arrival)),
                "driver_arrival_max": int(np.max(self.driver_arrival)),
                "driver_arrival_mean": float(np.mean(self.driver_arrival)),
                "driver_arrival_std": float(np.std(self.driver_arrival)),
                "final_abundance_min": float(np.min(self.final_abundance)),
                "final_abundance_max": float(np.max(self.final_abundance)),
                "final_abundance_mean": float(np.mean(self.final_abundance)),
                "final_abundance_std": float(np.std(self.final_abundance)),
                "extirpation_threshold_min": float(np.min(self.extirpation_threshold)),
                "extirpation_threshold_max": float(np.max(self.extirpation_threshold)),
                "extirpation_threshold_mean": float(np.mean(self.extirpation_threshold)),
                "extirpated_count": extirpated_count,
                "extirpated_fraction": extirpated_count / self.domain.cell_count,
                "surviving_count": surviving_count,
                "surviving_fraction": surviving_count / self.domain.cell_count,
                "true_extirpation_min": finite_min(finite_true_extirpation),
                "true_extirpation_max": finite_max(finite_true_extirpation),
                "true_extirpation_mean": finite_mean(finite_true_extirpation),
                "true_extirpation_std": finite_std(finite_true_extirpation),
                "lag_min": finite_min(finite_lag),
                "lag_max": finite_max(finite_lag),
                "lag_mean": finite_mean(finite_lag),
                "lag_std": finite_std(finite_lag),
            },
        }

    def write_artifacts(self, output_dir: str | PathLike[str]) -> tuple[Path, ...]:
        return write_synth_small_predator_truth_artifacts(self, output_dir)


DEFAULT_CONFIG = SynthSmallPredatorTruthConfig()


def default_synth_small_predator_truth_config() -> SynthSmallPredatorTruthConfig:
    return DEFAULT_CONFIG


def build_synth_small_predator_truth(
    config: SynthSmallPredatorTruthConfig | None = None,
) -> SynthSmallPredatorTruthResult:
    truth_config = config or default_synth_small_predator_truth_config()
    validate_predator_truth_config(truth_config)

    baseline = build_synth_small_baseline(truth_config.baseline)
    driver_arrival = build_driver_arrival_surface(baseline.domain, truth_config.arrival)
    simulation_horizon = int(np.max(driver_arrival)) + truth_config.post_arrival_buffer
    predator_pressure, prey_abundance, used_nonnegative_clipping = run_predator_truth_dynamics(
        baseline,
        driver_arrival,
        truth_config,
        simulation_horizon,
    )
    if not np.isfinite(predator_pressure).all():
        raise RuntimeError("predator pressure trajectory contained non-finite values")
    if not np.isfinite(prey_abundance).all():
        raise RuntimeError("prey abundance trajectory contained non-finite values")
    if float(np.min(prey_abundance)) < 0.0:
        raise RuntimeError("prey abundance trajectory became negative")

    extirpation_threshold = compute_true_extirpation_threshold(
        baseline.equilibrium_abundance,
        truth_config.extirpation,
    )
    true_extirpation = compute_true_extirpation_surface(prey_abundance, extirpation_threshold)
    extirpation_lag = np.full(baseline.equilibrium_abundance.shape, np.nan, dtype=np.float64)
    extirpated = np.isfinite(true_extirpation)
    extirpation_lag[extirpated] = (
        true_extirpation[extirpated] - driver_arrival.astype(np.float64)[extirpated]
    )

    diagnostics = PredatorTruthDiagnostics(
        simulation_horizon=simulation_horizon,
        predator_source_geometry=truth_config.arrival.source_geometry,
        introduction_time=truth_config.arrival.introduction_time,
        front_speed_cells_per_step=truth_config.arrival.front_speed_cells_per_step,
        pressure_ramp_duration=truth_config.pressure.ramp_duration,
        predation_response_form="type_ii",
        extirpation_threshold_form="absolute_quasi_extinction",
        pressure_scale=truth_config.pressure.pressure_scale,
        pressure_exponent=truth_config.pressure.pressure_exponent,
        quasi_extirpation_abundance=truth_config.extirpation.quasi_extirpation_abundance,
        stayed_finite=True,
        stayed_nonnegative=True,
        used_nonnegative_clipping=used_nonnegative_clipping,
        used_missing_for_non_extirpated=True,
        baseline_converged=baseline.diagnostics.converged,
        max_driver_arrival=int(np.max(driver_arrival)),
    )
    return SynthSmallPredatorTruthResult(
        config=truth_config,
        baseline=baseline,
        driver_arrival=driver_arrival,
        predator_pressure=predator_pressure,
        prey_abundance=prey_abundance,
        true_extirpation=true_extirpation,
        extirpation_lag=extirpation_lag,
        extirpation_threshold=extirpation_threshold,
        diagnostics=diagnostics,
    )


def validate_predator_truth_config(config: SynthSmallPredatorTruthConfig) -> None:
    if config.arrival.source_geometry != "western_boundary":
        raise ValueError(f"unsupported source geometry: {config.arrival.source_geometry}")
    if config.arrival.introduction_time < 0:
        raise ValueError("introduction_time must be non-negative")
    if config.arrival.front_speed_cells_per_step <= 0.0:
        raise ValueError("front_speed_cells_per_step must be positive")
    if config.pressure.ramp_duration <= 0:
        raise ValueError("ramp_duration must be positive")
    if not 0.0 <= config.pressure.pre_arrival_leakage <= 1.0:
        raise ValueError("pre_arrival_leakage must lie in [0, 1]")
    if config.pressure.pressure_scale <= 0.0:
        raise ValueError("pressure_scale must be positive")
    if config.pressure.pressure_exponent <= 0.0:
        raise ValueError("pressure_exponent must be positive")
    if config.response.predation_scale <= 0.0:
        raise ValueError("predation_scale must be positive")
    if config.response.half_saturation <= 0.0:
        raise ValueError("half_saturation must be positive")
    if config.extirpation.quasi_extirpation_abundance <= 0.0:
        raise ValueError("quasi_extirpation_abundance must be positive")
    if config.post_arrival_buffer <= 0:
        raise ValueError("post_arrival_buffer must be positive")


def build_driver_arrival_surface(
    domain: CellGraphDomain,
    config: PredatorArrivalConfig,
) -> IntArray:
    source_ids = western_boundary_source_ids(domain)
    graph_distance = graph_distance_from_sources(domain, source_ids).astype(np.float64)
    arrival = config.introduction_time + np.ceil(
        graph_distance / config.front_speed_cells_per_step
    ).astype(np.int64)
    return arrival.reshape((domain.rows, domain.cols))


def western_boundary_source_ids(domain: CellGraphDomain) -> tuple[int, ...]:
    return tuple(int(index) for index in np.flatnonzero(domain.coordinates[:, 1] == 0))


def graph_distance_from_sources(domain: CellGraphDomain, source_ids: tuple[int, ...]) -> IntArray:
    distance = np.full(domain.cell_count, -1, dtype=np.int64)
    queue: deque[int] = deque()
    for source_id in source_ids:
        distance[source_id] = 0
        queue.append(source_id)

    while queue:
        source = queue.popleft()
        for target in domain.adjacency[source]:
            if distance[target] != -1:
                continue
            distance[target] = distance[source] + 1
            queue.append(target)

    if (distance < 0).any():
        raise RuntimeError("graph distance computation left unreachable cells in the domain")
    return distance


def run_predator_truth_dynamics(
    baseline: SynthSmallBaselineResult,
    driver_arrival: IntArray,
    config: SynthSmallPredatorTruthConfig,
    simulation_horizon: int,
) -> tuple[FloatArray, FloatArray, bool]:
    predator_pressure = np.zeros(
        (simulation_horizon + 1, baseline.domain.rows, baseline.domain.cols),
        dtype=np.float64,
    )
    prey_abundance = np.zeros_like(predator_pressure)
    prey_abundance[0] = baseline.equilibrium_abundance
    used_nonnegative_clipping = False

    for time_index in range(simulation_horizon + 1):
        predator_pressure[time_index] = compute_predator_pressure_surface(
            driver_arrival,
            time_index,
            config.pressure,
        )

    for time_index in range(simulation_horizon):
        next_abundance, clipped = predator_response_step(
            baseline.domain,
            prey_abundance[time_index],
            baseline.carrying_capacity,
            predator_pressure[time_index],
            config.baseline,
            config.response,
        )
        if not np.isfinite(next_abundance).all():
            raise RuntimeError("predator-response step produced non-finite abundance values")
        prey_abundance[time_index + 1] = next_abundance
        used_nonnegative_clipping = used_nonnegative_clipping or clipped

    return predator_pressure, prey_abundance, used_nonnegative_clipping


def compute_predator_pressure_surface(
    driver_arrival: IntArray,
    time_index: int,
    config: PredatorPressureConfig,
) -> FloatArray:
    arrival_float = driver_arrival.astype(np.float64)
    delta = time_index - arrival_float
    pressure = np.full(driver_arrival.shape, config.pre_arrival_leakage, dtype=np.float64)
    post_arrival = delta >= 0.0
    if np.any(post_arrival):
        ramp_rate = 6.0 / config.ramp_duration
        logistic = 1.0 / (
            1.0 + np.exp(-ramp_rate * (delta[post_arrival] - (config.ramp_duration / 2.0)))
        )
        ramped = 0.2 + 0.8 * logistic
        bounded = np.maximum(config.pre_arrival_leakage, np.minimum(1.0, ramped))
        pressure[post_arrival] = bounded
    return config.pressure_scale * np.power(pressure, config.pressure_exponent)


def predator_response_step(
    domain: CellGraphDomain,
    abundance: FloatArray,
    carrying_capacity: FloatArray,
    pressure: FloatArray,
    baseline_config: SynthSmallBaselineConfig,
    response_config: TypeIIResponseConfig,
) -> tuple[FloatArray, bool]:
    allee_factor = compute_allee_factor(abundance, baseline_config.allee_scale)
    predation_mortality = compute_type_ii_predation_mortality(
        abundance,
        pressure,
        response_config,
    )
    growth_term = (
        baseline_config.intrinsic_growth_rate
        * allee_factor
        * (1.0 - (abundance / carrying_capacity))
        - predation_mortality
        - baseline_config.background_loss
    )
    local_update = abundance * np.exp(growth_term)
    dispersed = domain.transition_matrix @ local_update.reshape(domain.cell_count)
    dispersed_grid = dispersed.reshape((domain.rows, domain.cols))
    raw_next_abundance = (
        1.0 - baseline_config.dispersal_share
    ) * local_update + baseline_config.dispersal_share * dispersed_grid
    used_nonnegative_clipping = bool(np.any(raw_next_abundance < 0.0))
    return np.clip(raw_next_abundance, 0.0, None), used_nonnegative_clipping


def compute_type_ii_predation_mortality(
    abundance: FloatArray,
    pressure: FloatArray,
    config: TypeIIResponseConfig,
) -> FloatArray:
    return (
        config.predation_scale
        * pressure
        * config.half_saturation
        / (config.half_saturation + abundance)
    )


def compute_true_extirpation_threshold(
    reference_surface: FloatArray,
    config: TrueExtirpationConfig,
) -> FloatArray:
    return np.full(
        reference_surface.shape,
        config.quasi_extirpation_abundance,
        dtype=np.float64,
    )


def compute_true_extirpation_surface(
    prey_abundance: FloatArray,
    threshold: FloatArray,
) -> FloatArray:
    true_extirpation = np.full(threshold.shape, np.nan, dtype=np.float64)
    for time_index in range(1, prey_abundance.shape[0]):
        newly_extirpated = (
            np.isnan(true_extirpation)
            & (prey_abundance[time_index - 1] > threshold)
            & (prey_abundance[time_index] <= threshold)
        )
        true_extirpation[newly_extirpated] = float(time_index)
    return true_extirpation


def write_synth_small_predator_truth_artifacts(
    result: SynthSmallPredatorTruthResult,
    output_dir: str | PathLike[str],
) -> tuple[Path, ...]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    domain_json = target_dir / "domain.json"
    baseline_config_json = target_dir / "baseline_config.json"
    predator_config_json = target_dir / "predator_config.json"
    diagnostics_json = target_dir / "diagnostics.json"
    summary_json = target_dir / "summary.json"
    cells_csv = target_dir / "cells.csv"
    surfaces_npz = target_dir / "surfaces.npz"
    trajectories_npz = target_dir / "trajectories.npz"
    suitability_svg = target_dir / "suitability.svg"
    initial_abundance_svg = target_dir / "initial_abundance.svg"
    driver_arrival_svg = target_dir / "driver_arrival.svg"
    true_extirpation_svg = target_dir / "true_extirpation.svg"
    extirpation_lag_svg = target_dir / "extirpation_lag.svg"
    final_abundance_svg = target_dir / "final_abundance.svg"

    abundance_scale = shared_finite_range(result.initial_abundance, result.final_abundance)
    time_scale = shared_finite_range(
        result.driver_arrival.astype(np.float64),
        result.true_extirpation,
    )
    lag_scale = shared_finite_range(result.extirpation_lag)

    domain_json.write_text(dumps(result.domain.to_metadata(), indent=2) + "\n", encoding="utf-8")
    baseline_config_json.write_text(
        dumps(result.config.baseline.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    predator_config_json.write_text(
        dumps(
            {
                "arrival": asdict(result.config.arrival),
                "pressure": asdict(result.config.pressure),
                "response": asdict(result.config.response),
                "extirpation": asdict(result.config.extirpation),
                "post_arrival_buffer": result.config.post_arrival_buffer,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    diagnostics_json.write_text(
        dumps(result.diagnostics.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    summary_json.write_text(dumps(result.to_summary_dict(), indent=2) + "\n", encoding="utf-8")
    write_predator_truth_cells_csv(result, cells_csv)
    np.savez_compressed(
        surfaces_npz,
        suitability=result.suitability,
        carrying_capacity=result.carrying_capacity,
        initial_abundance=result.initial_abundance,
        driver_arrival=result.driver_arrival,
        extirpation_threshold=result.extirpation_threshold,
        true_extirpation=result.true_extirpation,
        extirpation_lag=result.extirpation_lag,
        final_abundance=result.final_abundance,
    )
    np.savez_compressed(
        trajectories_npz,
        prey_abundance=result.prey_abundance,
        predator_pressure=result.predator_pressure,
    )
    write_numeric_surface_svg(
        result.suitability,
        suitability_svg,
        title="Suitability Surface",
        start_color="#f4f9f4",
        end_color="#0b5d1e",
    )
    write_numeric_surface_svg(
        result.initial_abundance,
        initial_abundance_svg,
        title="Initial Abundance",
        start_color="#f0fdf4",
        end_color="#166534",
        color_min=abundance_scale[0],
        color_max=abundance_scale[1],
    )
    write_numeric_surface_svg(
        result.driver_arrival.astype(np.float64),
        driver_arrival_svg,
        title="Driver Arrival Time",
        start_color="#eff6ff",
        end_color="#1d4ed8",
        color_min=time_scale[0],
        color_max=time_scale[1],
    )
    write_numeric_surface_svg(
        result.true_extirpation,
        true_extirpation_svg,
        title="True Extirpation Time",
        start_color="#eff6ff",
        end_color="#1d4ed8",
        color_min=time_scale[0],
        color_max=time_scale[1],
    )
    write_numeric_surface_svg(
        result.extirpation_lag,
        extirpation_lag_svg,
        title="Extirpation Lag",
        start_color="#fefce8",
        end_color="#a16207",
        color_min=lag_scale[0],
        color_max=lag_scale[1],
    )
    write_numeric_surface_svg(
        result.final_abundance,
        final_abundance_svg,
        title="Final Abundance",
        start_color="#f0fdf4",
        end_color="#166534",
        color_min=abundance_scale[0],
        color_max=abundance_scale[1],
    )

    return (
        domain_json,
        baseline_config_json,
        predator_config_json,
        diagnostics_json,
        summary_json,
        cells_csv,
        surfaces_npz,
        trajectories_npz,
        suitability_svg,
        initial_abundance_svg,
        driver_arrival_svg,
        true_extirpation_svg,
        extirpation_lag_svg,
        final_abundance_svg,
    )


def write_predator_truth_cells_csv(
    result: SynthSmallPredatorTruthResult, output_path: Path
) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(
            [
                "cell_id",
                "row",
                "col",
                "suitability",
                "carrying_capacity",
                "initial_abundance",
                "driver_arrival",
                "extirpation_threshold",
                "true_extirpation",
                "extirpation_lag",
                "final_abundance",
                "extirpated_by_end",
            ]
        )
        for cell_id, (row, col) in enumerate(result.domain.coordinates.tolist()):
            true_extirpation = float(result.true_extirpation[row, col])
            lag = float(result.extirpation_lag[row, col])
            csv_writer.writerow(
                [
                    cell_id,
                    row,
                    col,
                    float(result.suitability[row, col]),
                    float(result.carrying_capacity[row, col]),
                    float(result.initial_abundance[row, col]),
                    int(result.driver_arrival[row, col]),
                    float(result.extirpation_threshold[row, col]),
                    format_nullable_number(true_extirpation),
                    format_nullable_number(lag),
                    float(result.final_abundance[row, col]),
                    int(np.isfinite(true_extirpation)),
                ]
            )


def format_nullable_number(value: float) -> str:
    if not np.isfinite(value):
        return ""
    rounded = round(value)
    if np.isclose(value, rounded, atol=1e-12):
        return str(int(rounded))
    return f"{value:.12g}"


def write_numeric_surface_svg(
    surface: FloatArray,
    output_path: Path,
    *,
    title: str,
    start_color: str,
    end_color: str,
    color_min: float | None = None,
    color_max: float | None = None,
    missing_color: str = "#d1d5db",
) -> None:
    finite_mask = np.isfinite(surface)
    rows, cols = surface.shape
    cell_size = 20
    margin = 36
    width = cols * cell_size + (2 * margin)
    scale_bar_height = 18
    scale_bar_width = max(180, cols * cell_size)
    scale_bar_x = margin
    scale_bar_y = rows * cell_size + margin + 18
    width = max(width, scale_bar_x + scale_bar_width + margin)
    height = rows * cell_size + (2 * margin) + 96
    if np.any(finite_mask):
        finite_values = surface[finite_mask]
        inferred_min = float(np.min(finite_values))
        inferred_max = float(np.max(finite_values))
        min_value = inferred_min if color_min is None else color_min
        max_value = inferred_max if color_max is None else color_max
        value_range = max(max_value - min_value, 1e-12)
        label = f"scale min={min_value:.3f} max={max_value:.3f}"
        if np.any(~finite_mask):
            label += " missing=gray"
    else:
        min_value = 0.0 if color_min is None else color_min
        max_value = 0.0 if color_max is None else color_max
        value_range = 1.0
        label = "all values missing"

    gradient_id = gradient_id_for_title(title)
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        (
            "<defs>"
            f'<linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="100%" y2="0%">'
            f'<stop offset="0%" stop-color="{start_color}"/>'
            f'<stop offset="100%" stop-color="{end_color}"/>'
            "</linearGradient>"
            "</defs>"
        ),
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{margin}" y="24" font-size="18" font-family="monospace">{title}</text>',
        (
            f'<text x="{margin}" y="{height - 10}" font-size="12" '
            f'font-family="monospace">{label}</text>'
        ),
    ]
    for row in range(rows):
        for col in range(cols):
            value = float(surface[row, col])
            if np.isfinite(value):
                normalized = (value - min_value) / value_range
                fill = interpolate_hex(start_color, end_color, normalized)
            else:
                fill = missing_color
            x = margin + (col * cell_size)
            y = margin + (row * cell_size)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'fill="{fill}" stroke="#d1d5db" stroke-width="0.5"/>'
            )
    parts.extend(
        [
            (
                f'<rect x="{scale_bar_x}" y="{scale_bar_y}" width="{scale_bar_width}" '
                f'height="{scale_bar_height}" fill="url(#{gradient_id})" '
                'stroke="#374151" stroke-width="0.8"/>'
            ),
            (
                f'<text x="{scale_bar_x}" y="{scale_bar_y - 6}" font-size="12" '
                'font-family="monospace">Color scale</text>'
            ),
            (
                f'<text x="{scale_bar_x}" y="{scale_bar_y + scale_bar_height + 16}" '
                f'font-size="12" font-family="monospace">{min_value:.3f}</text>'
            ),
            (
                f'<text x="{scale_bar_x + scale_bar_width - 42}" '
                f'y="{scale_bar_y + scale_bar_height + 16}" font-size="12" '
                f'font-family="monospace">{max_value:.3f}</text>'
            ),
        ]
    )
    if np.any(~finite_mask):
        parts.append(
            f'<rect x="{scale_bar_x + scale_bar_width + 18}" y="{scale_bar_y}" '
            f'width="{scale_bar_height}" height="{scale_bar_height}" fill="{missing_color}" '
            'stroke="#374151" stroke-width="0.8"/>'
        )
        parts.append(
            f'<text x="{scale_bar_x + scale_bar_width + 44}" '
            f'y="{scale_bar_y + scale_bar_height - 3}" font-size="12" '
            'font-family="monospace">Missing</text>'
        )
    parts.append("</svg>")
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def shared_finite_range(*surfaces: FloatArray) -> tuple[float, float]:
    finite_chunks = [
        surface[np.isfinite(surface)] for surface in surfaces if np.isfinite(surface).any()
    ]
    if not finite_chunks:
        return 0.0, 1.0
    combined = np.concatenate(finite_chunks)
    return float(np.min(combined)), float(np.max(combined))


def gradient_id_for_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"scale-{slug or 'surface'}"


def finite_min(values: FloatArray) -> float | None:
    if values.size == 0:
        return None
    return float(np.min(values))


def finite_max(values: FloatArray) -> float | None:
    if values.size == 0:
        return None
    return float(np.max(values))


def finite_mean(values: FloatArray) -> float | None:
    if values.size == 0:
        return None
    return float(np.mean(values))


def finite_std(values: FloatArray) -> float | None:
    if values.size == 0:
        return None
    return float(np.std(values))
