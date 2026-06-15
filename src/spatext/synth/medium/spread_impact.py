from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from heapq import heappop, heappush
from json import dumps
from math import exp
from os import PathLike
from pathlib import Path

from .landscape import (
    CsvRow,
    CsvValue,
    LandscapeCell,
    SynthMediumLandscapeResult,
    build_synth_medium_landscape,
    interpolate_hex,
    mean,
    quantile,
    safe_fraction,
    write_csv_rows,
)

DEFAULT_SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_DIR = Path("artifacts/synth_medium_spread_impact")
SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_FILES = (
    "simulation_config.json",
    "parameter_candidate_log.csv",
    "cell_truth.csv",
    "time_series_summary.csv",
    "source_contribution_summary.csv",
    "habitat_class_timing_summary.csv",
    "corridor_barrier_effect_summary.csv",
    "prey_impact_summary.csv",
    "recoverability_proxy_summary.csv",
    "verification.json",
    "report.md",
)
SYNTH_MEDIUM_SPREAD_IMPACT_VISUAL_FILES = (
    "predator_arrival_time.svg",
    "predator_occupancy_snapshots.svg",
    "prey_abundance_snapshots.svg",
    "prey_impact_time.svg",
    "source_contribution_map.svg",
    "arrival_impact_lag.svg",
    "review_montage.svg",
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "synth_medium_landscape_source_verified": True,
    "spread_impact_review_only": True,
    "visual_review_required": True,
    "parameter_tuning_bounded": True,
    "no_observation_model": True,
    "no_reconstruction_or_inference": True,
    "no_abc_pom_likelihood_or_posterior": True,
    "no_real_data": True,
}

HABITAT_CLASSES = (
    "low_quality_matrix",
    "medium_quality",
    "high_quality_patch",
    "corridor",
    "source_zone",
    "water",
)


@dataclass(frozen=True, slots=True)
class SpreadImpactCandidate:
    parameter_set_id: str
    horizon: int
    movement_scale: float
    matrix_conductance: float
    medium_conductance: float
    high_patch_conductance: float
    corridor_conductance: float
    source_conductance: float
    water_neighbor_penalty: float
    prey_impact_strength: float
    quasi_extirpation_fraction: float
    rationale: str

    def conductance_for(self, habitat_class: str) -> float:
        if habitat_class == "source_zone":
            return self.source_conductance
        if habitat_class == "corridor":
            return self.corridor_conductance
        if habitat_class == "high_quality_patch":
            return self.high_patch_conductance
        if habitat_class == "medium_quality":
            return self.medium_conductance
        if habitat_class == "low_quality_matrix":
            return self.matrix_conductance
        return 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "parameter_set_id": self.parameter_set_id,
            "horizon": self.horizon,
            "movement_scale": self.movement_scale,
            "matrix_conductance": self.matrix_conductance,
            "medium_conductance": self.medium_conductance,
            "high_patch_conductance": self.high_patch_conductance,
            "corridor_conductance": self.corridor_conductance,
            "source_conductance": self.source_conductance,
            "water_neighbor_penalty": self.water_neighbor_penalty,
            "prey_impact_strength": self.prey_impact_strength,
            "quasi_extirpation_fraction": self.quasi_extirpation_fraction,
            "rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class SynthMediumSpreadImpactConfig:
    selected_parameter_set_id: str = "balanced_corridor_detour_v2"
    candidate_ids: tuple[str, ...] = (
        "fast_corridor_saturation",
        "slow_matrix_underreach",
        "balanced_corridor_detour_v1",
        "balanced_corridor_detour_v2",
        "strong_impact_fast_loss",
    )
    max_candidate_count: int = 6
    review_times: tuple[int, ...] = (0, 20, 40, 60, 80, 100, 120)
    final_occupancy_min_fraction: float = 0.70
    final_occupancy_max_fraction: float = 0.97
    min_arrival_range: float = 70.0
    min_extirpated_passable_fraction: float = 0.35
    max_extirpated_passable_fraction: float = 0.85
    min_lag_range: float = 8.0
    material_source_min_fraction: float = 0.10
    minimum_recoverability_proxy_pass_count: int = 5

    def to_dict(self, selected_candidate: SpreadImpactCandidate) -> dict[str, object]:
        return {
            "selected_parameter_set_id": self.selected_parameter_set_id,
            "candidate_ids": list(self.candidate_ids),
            "max_candidate_count": self.max_candidate_count,
            "review_times": list(self.review_times),
            "review_gate_thresholds": {
                "final_occupancy_min_fraction": self.final_occupancy_min_fraction,
                "final_occupancy_max_fraction": self.final_occupancy_max_fraction,
                "min_arrival_range": self.min_arrival_range,
                "min_extirpated_passable_fraction": self.min_extirpated_passable_fraction,
                "max_extirpated_passable_fraction": self.max_extirpated_passable_fraction,
                "min_lag_range": self.min_lag_range,
                "material_source_min_fraction": self.material_source_min_fraction,
                "minimum_recoverability_proxy_pass_count": (
                    self.minimum_recoverability_proxy_pass_count
                ),
            },
            "selected_candidate": selected_candidate.to_dict(),
            **BOUNDARY_LABELS,
        }


@dataclass(frozen=True, slots=True)
class SpreadImpactCellTruth:
    landscape_cell: LandscapeCell
    conductance: float
    predator_arrival_time: float | None
    source_zone_id: str
    predator_final_occupied: bool
    prey_baseline_abundance: float | None
    prey_carrying_capacity: float | None
    prey_impact_time: float | None
    prey_extirpation_time: float | None
    arrival_to_extirpation_lag: float | None
    prey_final_abundance: float | None
    arrival_detour_index: float | None

    def to_csv_row(self) -> CsvRow:
        cell = self.landscape_cell
        return {
            "cell_id": cell.cell_id,
            "row": cell.row,
            "col": cell.col,
            "x_coord": cell.x_coord,
            "y_coord": cell.y_coord,
            "passability": cell.passability,
            "habitat_class": cell.habitat_class,
            "quality": cell.quality,
            "patch_id": cell.patch_id,
            "corridor_id": cell.corridor_id,
            "source_zone_id": cell.source_zone_id,
            "water_component_id": cell.water_component_id,
            "row_band": cell.row_band,
            "col_band": cell.col_band,
            "water_neighbor_count": cell.water_neighbor_count,
            "landscape_source_distance": cell.source_distance,
            "conductance": self.conductance,
            "predator_arrival_time": self.predator_arrival_time,
            "predator_source_zone_id": self.source_zone_id,
            "predator_final_occupied": self.predator_final_occupied,
            "prey_baseline_abundance": self.prey_baseline_abundance,
            "prey_carrying_capacity": self.prey_carrying_capacity,
            "prey_impact_time": self.prey_impact_time,
            "prey_extirpation_time": self.prey_extirpation_time,
            "arrival_to_extirpation_lag": self.arrival_to_extirpation_lag,
            "prey_final_abundance": self.prey_final_abundance,
            "arrival_detour_index": self.arrival_detour_index,
        }


@dataclass(frozen=True, slots=True)
class SpreadImpactCheck:
    name: str
    passed: bool
    details: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "details": self.details}


@dataclass(frozen=True, slots=True)
class CandidateEvaluation:
    candidate: SpreadImpactCandidate
    cell_truth_rows: tuple[SpreadImpactCellTruth, ...]
    metrics: dict[str, float | int | str | bool]
    selected_default: bool

    def to_log_row(self) -> CsvRow:
        status = (
            "selected_default" if self.selected_default else str(self.metrics["candidate_status"])
        )
        return {
            "parameter_set_id": self.candidate.parameter_set_id,
            "selected_default": self.selected_default,
            "candidate_status": status,
            "horizon": self.candidate.horizon,
            "movement_scale": self.candidate.movement_scale,
            "matrix_conductance": self.candidate.matrix_conductance,
            "medium_conductance": self.candidate.medium_conductance,
            "high_patch_conductance": self.candidate.high_patch_conductance,
            "corridor_conductance": self.candidate.corridor_conductance,
            "source_conductance": self.candidate.source_conductance,
            "water_neighbor_penalty": self.candidate.water_neighbor_penalty,
            "prey_impact_strength": self.candidate.prey_impact_strength,
            "quasi_extirpation_fraction": self.candidate.quasi_extirpation_fraction,
            "final_colonized_passable_count": self.metrics["final_colonized_passable_count"],
            "final_colonized_passable_fraction": self.metrics["final_colonized_passable_fraction"],
            "finite_extirpation_count": self.metrics["finite_extirpation_count"],
            "finite_extirpation_fraction": self.metrics["finite_extirpation_fraction"],
            "arrival_time_range": self.metrics["arrival_time_range"],
            "lag_range": self.metrics["lag_range"],
            "material_source_count": self.metrics["material_source_count"],
            "rejection_or_selection_rationale": self.metrics["candidate_rationale"],
        }


@dataclass(frozen=True, slots=True)
class SynthMediumSpreadImpactResult:
    config: SynthMediumSpreadImpactConfig
    selected_candidate: SpreadImpactCandidate
    landscape: SynthMediumLandscapeResult
    cell_truth_rows: tuple[SpreadImpactCellTruth, ...]
    parameter_candidate_log_rows: tuple[CsvRow, ...]
    time_series_summary_rows: tuple[CsvRow, ...]
    source_contribution_summary_rows: tuple[CsvRow, ...]
    habitat_class_timing_summary_rows: tuple[CsvRow, ...]
    corridor_barrier_effect_summary_rows: tuple[CsvRow, ...]
    prey_impact_summary_rows: tuple[CsvRow, ...]
    recoverability_proxy_summary_rows: tuple[CsvRow, ...]
    verification_checks: tuple[SpreadImpactCheck, ...]
    visual_svgs: dict[str, str]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    @property
    def recommendation_class(self) -> str:
        if self.passed:
            return "ready_for_human_spread_impact_review"
        return "spread_impact_review_blocked"

    def summary_dict(self) -> dict[str, object]:
        passable_rows = [
            row for row in self.cell_truth_rows if row.landscape_cell.passability == "passable"
        ]
        colonized_rows = [row for row in passable_rows if row.predator_final_occupied]
        extirpated_rows = [row for row in passable_rows if row.prey_extirpation_time is not None]
        material_sources = [
            row
            for row in self.source_contribution_summary_rows
            if row["row_role"] == "source_contribution"
            and csv_float(row["source_contribution_fraction_of_colonized_passable"])
            >= self.config.material_source_min_fraction
        ]
        return {
            "selected_parameter_set_id": self.selected_candidate.parameter_set_id,
            "cell_count": len(self.cell_truth_rows),
            "passable_cell_count": len(passable_rows),
            "water_cell_count": len(self.cell_truth_rows) - len(passable_rows),
            "final_colonized_passable_count": len(colonized_rows),
            "final_colonized_passable_fraction": safe_fraction(
                len(colonized_rows), len(passable_rows)
            ),
            "finite_prey_extirpation_count": len(extirpated_rows),
            "finite_prey_extirpation_fraction": safe_fraction(
                len(extirpated_rows), len(passable_rows)
            ),
            "material_source_count": len(material_sources),
            "recommendation_class": self.recommendation_class,
        }

    def config_payload(self) -> dict[str, object]:
        return {
            **self.config.to_dict(self.selected_candidate),
            "landscape_summary": self.landscape.summary_dict(),
            "summary": self.summary_dict(),
            "output_files": list(SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_FILES),
            "visual_files": [f"visuals/{name}" for name in SYNTH_MEDIUM_SPREAD_IMPACT_VISUAL_FILES],
        }

    def verification_payload(self) -> dict[str, object]:
        return {
            **BOUNDARY_LABELS,
            "passed": self.passed,
            "recommendation_class": self.recommendation_class,
            "checks": [check.to_dict() for check in self.verification_checks],
            "summary": self.summary_dict(),
        }

    def write_artifacts(self, output_dir: str | PathLike[str]) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        visuals_dir = target_dir / "visuals"
        visuals_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []

        config_path = target_dir / "simulation_config.json"
        config_path.write_text(
            dumps(self.config_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(config_path)

        table_specs: tuple[tuple[str, tuple[str, ...], tuple[CsvRow, ...]], ...] = (
            (
                "parameter_candidate_log.csv",
                PARAMETER_CANDIDATE_LOG_COLUMNS,
                self.parameter_candidate_log_rows,
            ),
            (
                "cell_truth.csv",
                CELL_TRUTH_COLUMNS,
                tuple(row.to_csv_row() for row in self.cell_truth_rows),
            ),
            (
                "time_series_summary.csv",
                TIME_SERIES_SUMMARY_COLUMNS,
                self.time_series_summary_rows,
            ),
            (
                "source_contribution_summary.csv",
                SOURCE_CONTRIBUTION_SUMMARY_COLUMNS,
                self.source_contribution_summary_rows,
            ),
            (
                "habitat_class_timing_summary.csv",
                HABITAT_CLASS_TIMING_SUMMARY_COLUMNS,
                self.habitat_class_timing_summary_rows,
            ),
            (
                "corridor_barrier_effect_summary.csv",
                CORRIDOR_BARRIER_EFFECT_SUMMARY_COLUMNS,
                self.corridor_barrier_effect_summary_rows,
            ),
            ("prey_impact_summary.csv", PREY_IMPACT_SUMMARY_COLUMNS, self.prey_impact_summary_rows),
            (
                "recoverability_proxy_summary.csv",
                RECOVERABILITY_PROXY_SUMMARY_COLUMNS,
                self.recoverability_proxy_summary_rows,
            ),
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
        report_path.write_text(render_spread_impact_report(self), encoding="utf-8")
        written.append(report_path)

        for visual_name in SYNTH_MEDIUM_SPREAD_IMPACT_VISUAL_FILES:
            path = visuals_dir / visual_name
            path.write_text(self.visual_svgs[visual_name], encoding="utf-8")
            written.append(path)

        return tuple(written)


PARAMETER_CANDIDATE_LOG_COLUMNS = (
    "parameter_set_id",
    "selected_default",
    "candidate_status",
    "horizon",
    "movement_scale",
    "matrix_conductance",
    "medium_conductance",
    "high_patch_conductance",
    "corridor_conductance",
    "source_conductance",
    "water_neighbor_penalty",
    "prey_impact_strength",
    "quasi_extirpation_fraction",
    "final_colonized_passable_count",
    "final_colonized_passable_fraction",
    "finite_extirpation_count",
    "finite_extirpation_fraction",
    "arrival_time_range",
    "lag_range",
    "material_source_count",
    "rejection_or_selection_rationale",
)

CELL_TRUTH_COLUMNS = (
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
    "row_band",
    "col_band",
    "water_neighbor_count",
    "landscape_source_distance",
    "conductance",
    "predator_arrival_time",
    "predator_source_zone_id",
    "predator_final_occupied",
    "prey_baseline_abundance",
    "prey_carrying_capacity",
    "prey_impact_time",
    "prey_extirpation_time",
    "arrival_to_extirpation_lag",
    "prey_final_abundance",
    "arrival_detour_index",
)

TIME_SERIES_SUMMARY_COLUMNS = (
    "time",
    "predator_occupied_passable_count",
    "predator_occupied_passable_fraction",
    "prey_impacted_passable_count",
    "prey_extirpated_passable_count",
    "mean_prey_abundance_passable",
)

SOURCE_CONTRIBUTION_SUMMARY_COLUMNS = (
    "row_role",
    "source_zone_id",
    "source_contributed_colonized_passable_count",
    "source_contribution_fraction_of_colonized_passable",
    "source_contribution_denominator",
    "uncolonized_passable_count",
    "uncolonized_passable_fraction_of_all_passable",
    "uncolonized_fraction_denominator",
    "material_source_threshold_fraction_of_colonized_passable",
    "is_material_source",
    "mean_predator_arrival_time",
    "min_predator_arrival_time",
    "max_predator_arrival_time",
    "mean_prey_extirpation_time",
)

HABITAT_CLASS_TIMING_SUMMARY_COLUMNS = (
    "habitat_class",
    "cell_count",
    "passable_cell_count",
    "mean_conductance",
    "finite_arrival_count",
    "finite_arrival_fraction",
    "mean_predator_arrival_time",
    "median_predator_arrival_time",
    "mean_prey_extirpation_time",
    "extirpated_count",
    "extirpated_fraction",
)

CORRIDOR_BARRIER_EFFECT_SUMMARY_COLUMNS = (
    "effect_group",
    "passable_cell_count",
    "finite_arrival_count",
    "mean_predator_arrival_time",
    "mean_landscape_source_distance",
    "mean_arrival_detour_index",
    "mean_conductance",
    "extirpated_count",
)

PREY_IMPACT_SUMMARY_COLUMNS = (
    "summary_group",
    "passable_cell_count",
    "impacted_count",
    "extirpated_count",
    "extirpated_fraction",
    "mean_lag",
    "min_extirpation_time",
    "max_extirpation_time",
    "mean_baseline_abundance",
    "mean_final_abundance",
)

RECOVERABILITY_PROXY_SUMMARY_COLUMNS = (
    "proxy_id",
    "observed_value",
    "threshold",
    "passes",
    "interpretation",
)


def default_spread_impact_candidates() -> tuple[SpreadImpactCandidate, ...]:
    return (
        SpreadImpactCandidate(
            parameter_set_id="fast_corridor_saturation",
            horizon=120,
            movement_scale=0.58,
            matrix_conductance=0.46,
            medium_conductance=0.82,
            high_patch_conductance=1.02,
            corridor_conductance=1.30,
            source_conductance=1.48,
            water_neighbor_penalty=0.22,
            prey_impact_strength=1.18,
            quasi_extirpation_fraction=0.27,
            rationale="Fast movement stress test; tends to over-saturate spread too early.",
        ),
        SpreadImpactCandidate(
            parameter_set_id="slow_matrix_underreach",
            horizon=120,
            movement_scale=0.92,
            matrix_conductance=0.32,
            medium_conductance=0.62,
            high_patch_conductance=0.88,
            corridor_conductance=1.08,
            source_conductance=1.35,
            water_neighbor_penalty=0.45,
            prey_impact_strength=0.95,
            quasi_extirpation_fraction=0.25,
            rationale=(
                "Slow-matrix stress test; preserves detours but under-reaches eastern habitat."
            ),
        ),
        SpreadImpactCandidate(
            parameter_set_id="balanced_corridor_detour_v1",
            horizon=120,
            movement_scale=0.76,
            matrix_conductance=0.40,
            medium_conductance=0.70,
            high_patch_conductance=0.96,
            corridor_conductance=1.22,
            source_conductance=1.42,
            water_neighbor_penalty=0.36,
            prey_impact_strength=1.00,
            quasi_extirpation_fraction=0.24,
            rationale="Balanced first pass; useful spread but prey impact is slightly too weak.",
        ),
        SpreadImpactCandidate(
            parameter_set_id="balanced_corridor_detour_v2",
            horizon=120,
            movement_scale=0.88,
            matrix_conductance=0.33,
            medium_conductance=0.64,
            high_patch_conductance=0.90,
            corridor_conductance=1.12,
            source_conductance=1.36,
            water_neighbor_penalty=0.46,
            prey_impact_strength=0.94,
            quasi_extirpation_fraction=0.26,
            rationale=(
                "Selected default: conservative finite spread, low-matrix detours, "
                "source mixing, and non-synchronous prey lags."
            ),
        ),
        SpreadImpactCandidate(
            parameter_set_id="strong_impact_fast_loss",
            horizon=120,
            movement_scale=0.70,
            matrix_conductance=0.39,
            medium_conductance=0.73,
            high_patch_conductance=0.98,
            corridor_conductance=1.26,
            source_conductance=1.44,
            water_neighbor_penalty=0.40,
            prey_impact_strength=1.65,
            quasi_extirpation_fraction=0.34,
            rationale=(
                "Strong-impact stress test; spread is usable but prey losses become too abrupt."
            ),
        ),
    )


def build_synth_medium_spread_impact_review_pack(
    config: SynthMediumSpreadImpactConfig | None = None,
) -> SynthMediumSpreadImpactResult:
    spread_config = config or SynthMediumSpreadImpactConfig()
    validate_spread_impact_config(spread_config)
    landscape = build_synth_medium_landscape()
    if not landscape.passed:
        raise RuntimeError("accepted synth-medium landscape verification did not pass")

    candidate_map = {
        candidate.parameter_set_id: candidate for candidate in default_spread_impact_candidates()
    }
    candidates = tuple(candidate_map[candidate_id] for candidate_id in spread_config.candidate_ids)
    evaluations = tuple(
        evaluate_candidate(
            spread_config,
            landscape,
            candidate,
            selected_default=candidate.parameter_set_id == spread_config.selected_parameter_set_id,
        )
        for candidate in candidates
    )
    selected_evaluation = next(
        evaluation for evaluation in evaluations if evaluation.selected_default
    )
    selected_candidate = selected_evaluation.candidate
    cell_truth_rows = selected_evaluation.cell_truth_rows

    time_series_rows = build_time_series_summary_rows(
        spread_config, selected_candidate, cell_truth_rows
    )
    source_rows = build_source_contribution_summary_rows(spread_config, cell_truth_rows)
    habitat_rows = build_habitat_class_timing_summary_rows(selected_candidate, cell_truth_rows)
    barrier_rows = build_corridor_barrier_effect_summary_rows(cell_truth_rows)
    prey_rows = build_prey_impact_summary_rows(cell_truth_rows)
    recoverability_rows = build_recoverability_proxy_summary_rows(
        spread_config,
        selected_evaluation.metrics,
        barrier_rows,
    )
    candidate_log_rows = tuple(evaluation.to_log_row() for evaluation in evaluations)
    visual_svgs = build_spread_impact_visual_svgs(
        spread_config, selected_candidate, cell_truth_rows
    )
    verification_checks = verify_spread_impact_result(
        spread_config,
        landscape,
        cell_truth_rows,
        candidate_log_rows,
        time_series_rows,
        source_rows,
        habitat_rows,
        barrier_rows,
        recoverability_rows,
        visual_svgs,
    )

    return SynthMediumSpreadImpactResult(
        config=spread_config,
        selected_candidate=selected_candidate,
        landscape=landscape,
        cell_truth_rows=cell_truth_rows,
        parameter_candidate_log_rows=candidate_log_rows,
        time_series_summary_rows=time_series_rows,
        source_contribution_summary_rows=source_rows,
        habitat_class_timing_summary_rows=habitat_rows,
        corridor_barrier_effect_summary_rows=barrier_rows,
        prey_impact_summary_rows=prey_rows,
        recoverability_proxy_summary_rows=recoverability_rows,
        verification_checks=verification_checks,
        visual_svgs=visual_svgs,
    )


def validate_spread_impact_config(config: SynthMediumSpreadImpactConfig) -> None:
    if len(config.candidate_ids) > config.max_candidate_count:
        raise ValueError("candidate tuning must remain bounded")
    candidate_ids = {candidate.parameter_set_id for candidate in default_spread_impact_candidates()}
    missing = set(config.candidate_ids) - candidate_ids
    if missing:
        raise ValueError(f"unknown spread-impact candidate IDs: {sorted(missing)}")
    if config.selected_parameter_set_id not in config.candidate_ids:
        raise ValueError("selected parameter set must be included in candidate_ids")
    if config.review_times != tuple(sorted(config.review_times)):
        raise ValueError("review_times must be sorted")


def evaluate_candidate(
    config: SynthMediumSpreadImpactConfig,
    landscape: SynthMediumLandscapeResult,
    candidate: SpreadImpactCandidate,
    *,
    selected_default: bool,
) -> CandidateEvaluation:
    arrivals, sources = compute_weighted_arrival(landscape, candidate)
    cell_truth_rows = build_cell_truth_rows(landscape, candidate, arrivals, sources)
    metrics = evaluate_candidate_metrics(config, candidate, cell_truth_rows)
    return CandidateEvaluation(
        candidate=candidate,
        cell_truth_rows=cell_truth_rows,
        metrics=metrics,
        selected_default=selected_default,
    )


def compute_weighted_arrival(
    landscape: SynthMediumLandscapeResult,
    candidate: SpreadImpactCandidate,
) -> tuple[dict[int, float], dict[int, str]]:
    cell_by_id = {cell.cell_id: cell for cell in landscape.cells}
    neighbors: dict[int, list[int]] = {cell.cell_id: [] for cell in landscape.cells}
    for edge in landscape.adjacency:
        neighbors[edge.source_cell_id].append(edge.target_cell_id)
        neighbors[edge.target_cell_id].append(edge.source_cell_id)

    arrivals: dict[int, float] = {}
    source_labels: dict[int, str] = {}
    heap: list[tuple[float, str, int]] = []
    for cell in sorted(landscape.cells, key=lambda value: value.cell_id):
        if not cell.source_zone_id:
            continue
        arrivals[cell.cell_id] = 0.0
        source_labels[cell.cell_id] = cell.source_zone_id
        heappush(heap, (0.0, cell.source_zone_id, cell.cell_id))

    while heap:
        arrival, source_zone_id, cell_id = heappop(heap)
        if arrival > arrivals[cell_id] + 1e-12:
            continue
        if source_zone_id != source_labels[cell_id]:
            continue
        source_cell = cell_by_id[cell_id]
        for neighbor_id in sorted(neighbors[cell_id]):
            target_cell = cell_by_id[neighbor_id]
            if target_cell.passability != "passable":
                continue
            edge_cost = spread_edge_cost(candidate, source_cell, target_cell)
            next_arrival = arrival + edge_cost
            prior = arrivals.get(neighbor_id)
            prior_source = source_labels.get(neighbor_id, "")
            if (
                prior is None
                or next_arrival < prior - 1e-12
                or (abs(next_arrival - prior) <= 1e-12 and source_zone_id < prior_source)
            ):
                arrivals[neighbor_id] = next_arrival
                source_labels[neighbor_id] = source_zone_id
                heappush(heap, (next_arrival, source_zone_id, neighbor_id))
    return arrivals, source_labels


def spread_edge_cost(
    candidate: SpreadImpactCandidate,
    source_cell: LandscapeCell,
    target_cell: LandscapeCell,
) -> float:
    source_conductance = candidate.conductance_for(source_cell.habitat_class)
    target_conductance = candidate.conductance_for(target_cell.habitat_class)
    mean_conductance = max((source_conductance + target_conductance) / 2.0, 1e-6)
    water_penalty = (
        candidate.water_neighbor_penalty
        * (source_cell.water_neighbor_count + target_cell.water_neighbor_count)
        / 4.0
    )
    return candidate.movement_scale / mean_conductance + water_penalty


def build_cell_truth_rows(
    landscape: SynthMediumLandscapeResult,
    candidate: SpreadImpactCandidate,
    arrivals: dict[int, float],
    sources: dict[int, str],
) -> tuple[SpreadImpactCellTruth, ...]:
    rows: list[SpreadImpactCellTruth] = []
    for cell in sorted(landscape.cells, key=lambda value: value.cell_id):
        conductance = round_float(candidate.conductance_for(cell.habitat_class))
        if cell.passability != "passable":
            rows.append(
                SpreadImpactCellTruth(
                    landscape_cell=cell,
                    conductance=0.0,
                    predator_arrival_time=None,
                    source_zone_id="",
                    predator_final_occupied=False,
                    prey_baseline_abundance=None,
                    prey_carrying_capacity=None,
                    prey_impact_time=None,
                    prey_extirpation_time=None,
                    arrival_to_extirpation_lag=None,
                    prey_final_abundance=None,
                    arrival_detour_index=None,
                )
            )
            continue

        arrival_time = round_float(arrivals[cell.cell_id])
        source_zone_id = sources[cell.cell_id]
        final_occupied = arrival_time <= candidate.horizon
        baseline_abundance = round_float(18.0 + (112.0 * cell.quality))
        carrying_capacity = round_float(24.0 + (132.0 * cell.quality))
        lag = compute_extirpation_lag(candidate, cell, arrival_time)
        impact_time = round_float(arrival_time + (0.45 * lag)) if final_occupied else None
        extirpation_time = round_float(arrival_time + lag) if final_occupied else None
        if extirpation_time is not None and extirpation_time > candidate.horizon:
            extirpation_time = None
        final_abundance = prey_abundance_at_time(
            candidate,
            baseline_abundance,
            arrival_time,
            lag,
            candidate.horizon,
        )
        detour_index = None
        if cell.source_distance is not None:
            unweighted_reference = (
                candidate.movement_scale
                * cell.source_distance
                / max(
                    candidate.medium_conductance,
                    1e-6,
                )
            )
            detour_index = round_float(arrival_time - unweighted_reference)
        rows.append(
            SpreadImpactCellTruth(
                landscape_cell=cell,
                conductance=conductance,
                predator_arrival_time=arrival_time,
                source_zone_id=source_zone_id,
                predator_final_occupied=final_occupied,
                prey_baseline_abundance=baseline_abundance,
                prey_carrying_capacity=carrying_capacity,
                prey_impact_time=impact_time,
                prey_extirpation_time=extirpation_time,
                arrival_to_extirpation_lag=lag if extirpation_time is not None else None,
                prey_final_abundance=final_abundance,
                arrival_detour_index=detour_index,
            )
        )
    return tuple(rows)


def compute_extirpation_lag(
    candidate: SpreadImpactCandidate,
    cell: LandscapeCell,
    arrival_time: float,
) -> float:
    source_distance_component = 0.035 * float(cell.source_distance or 0)
    habitat_component = 11.0 * cell.quality
    water_component = 1.15 * cell.water_neighbor_count
    deterministic_texture = ((cell.row * 5 + cell.col * 3) % 9) * 0.45
    impact_component = max(0.0, 2.3 - candidate.prey_impact_strength)
    arrival_component = 0.012 * arrival_time
    return round_float(
        4.8
        + habitat_component
        + source_distance_component
        + water_component
        + deterministic_texture
        + impact_component
        + arrival_component
    )


def prey_abundance_at_time(
    candidate: SpreadImpactCandidate,
    baseline_abundance: float,
    arrival_time: float,
    lag: float,
    time: float,
) -> float:
    if time < arrival_time:
        return baseline_abundance
    threshold = baseline_abundance * candidate.quasi_extirpation_fraction
    if time >= arrival_time + lag:
        time_after_extirpation = time - (arrival_time + lag)
        return round_float(max(threshold * 0.35, threshold * exp(-0.035 * time_after_extirpation)))
    elapsed_fraction = (time - arrival_time) / max(lag, 1e-6)
    abundance = baseline_abundance - elapsed_fraction * (baseline_abundance - threshold)
    return round_float(max(abundance, threshold))


def evaluate_candidate_metrics(
    config: SynthMediumSpreadImpactConfig,
    candidate: SpreadImpactCandidate,
    rows: tuple[SpreadImpactCellTruth, ...],
) -> dict[str, float | int | str | bool]:
    passable_rows = [row for row in rows if row.landscape_cell.passability == "passable"]
    colonized_rows = [row for row in passable_rows if row.predator_final_occupied]
    extirpated_rows = [row for row in passable_rows if row.prey_extirpation_time is not None]
    arrival_times = [
        row.predator_arrival_time for row in colonized_rows if row.predator_arrival_time is not None
    ]
    lags = [
        row.arrival_to_extirpation_lag
        for row in extirpated_rows
        if row.arrival_to_extirpation_lag is not None
    ]
    source_counts = Counter(row.source_zone_id for row in colonized_rows)
    material_source_count = sum(
        count / max(len(colonized_rows), 1) >= config.material_source_min_fraction
        for count in source_counts.values()
    )
    final_fraction = safe_fraction(len(colonized_rows), len(passable_rows))
    extirpated_fraction = safe_fraction(len(extirpated_rows), len(passable_rows))
    arrival_range = round_float(max(arrival_times) - min(arrival_times)) if arrival_times else 0.0
    lag_range = round_float(max(lags) - min(lags)) if lags else 0.0
    if final_fraction < config.final_occupancy_min_fraction:
        status = "rejected_under_reaching_spread"
        rationale = "Final spread is too sparse for review."
    elif final_fraction > config.final_occupancy_max_fraction:
        status = "rejected_over_saturated_spread"
        rationale = "Final spread is too saturated for a review target."
    elif extirpated_fraction < config.min_extirpated_passable_fraction:
        status = "rejected_weak_prey_impact"
        rationale = "Finite prey extirpation count is too low."
    elif extirpated_fraction > config.max_extirpated_passable_fraction:
        status = "rejected_excessive_prey_impact"
        rationale = "Finite prey extirpation count is too high."
    elif material_source_count < 2:
        status = "rejected_source_dominance"
        rationale = "Fewer than two source zones contribute materially."
    else:
        status = "passes_review_gates"
        rationale = candidate.rationale
    return {
        "final_colonized_passable_count": len(colonized_rows),
        "final_colonized_passable_fraction": final_fraction,
        "finite_extirpation_count": len(extirpated_rows),
        "finite_extirpation_fraction": extirpated_fraction,
        "arrival_time_range": arrival_range,
        "lag_range": lag_range,
        "material_source_count": material_source_count,
        "candidate_status": status,
        "candidate_rationale": rationale,
    }


def build_time_series_summary_rows(
    config: SynthMediumSpreadImpactConfig,
    candidate: SpreadImpactCandidate,
    rows: tuple[SpreadImpactCellTruth, ...],
) -> tuple[CsvRow, ...]:
    passable_rows = [row for row in rows if row.landscape_cell.passability == "passable"]
    review_times = tuple(dict.fromkeys((*config.review_times, candidate.horizon)))
    summary_rows: list[CsvRow] = []
    for time in review_times:
        occupied_count = sum(
            row.predator_arrival_time is not None and row.predator_arrival_time <= time
            for row in passable_rows
        )
        impacted_count = sum(
            row.prey_impact_time is not None and row.prey_impact_time <= time
            for row in passable_rows
        )
        extirpated_count = sum(
            row.prey_extirpation_time is not None and row.prey_extirpation_time <= time
            for row in passable_rows
        )
        abundances = [
            prey_abundance_at_time(
                candidate,
                row.prey_baseline_abundance or 0.0,
                row.predator_arrival_time or candidate.horizon + 1.0,
                row.arrival_to_extirpation_lag
                or compute_extirpation_lag(
                    candidate,
                    row.landscape_cell,
                    row.predator_arrival_time or 0.0,
                ),
                float(time),
            )
            for row in passable_rows
        ]
        summary_rows.append(
            {
                "time": time,
                "predator_occupied_passable_count": occupied_count,
                "predator_occupied_passable_fraction": safe_fraction(
                    occupied_count, len(passable_rows)
                ),
                "prey_impacted_passable_count": impacted_count,
                "prey_extirpated_passable_count": extirpated_count,
                "mean_prey_abundance_passable": mean(abundances),
            }
        )
    return tuple(summary_rows)


def build_source_contribution_summary_rows(
    config: SynthMediumSpreadImpactConfig,
    rows: tuple[SpreadImpactCellTruth, ...],
) -> tuple[CsvRow, ...]:
    passable_rows = [row for row in rows if row.landscape_cell.passability == "passable"]
    colonized_rows = [row for row in passable_rows if row.predator_final_occupied]
    source_ids = sorted({row.source_zone_id for row in colonized_rows if row.source_zone_id})
    summary_rows: list[CsvRow] = []
    for source_id in source_ids:
        source_rows = [row for row in colonized_rows if row.source_zone_id == source_id]
        arrival_times = [
            row.predator_arrival_time
            for row in source_rows
            if row.predator_arrival_time is not None
        ]
        extirpation_times = [
            row.prey_extirpation_time
            for row in source_rows
            if row.prey_extirpation_time is not None
        ]
        summary_rows.append(
            {
                "row_role": "source_contribution",
                "source_zone_id": source_id,
                "source_contributed_colonized_passable_count": len(source_rows),
                "source_contribution_fraction_of_colonized_passable": safe_fraction(
                    len(source_rows), len(colonized_rows)
                ),
                "source_contribution_denominator": "final_colonized_passable_count",
                "uncolonized_passable_count": None,
                "uncolonized_passable_fraction_of_all_passable": None,
                "uncolonized_fraction_denominator": None,
                "material_source_threshold_fraction_of_colonized_passable": (
                    config.material_source_min_fraction
                ),
                "is_material_source": safe_fraction(len(source_rows), len(colonized_rows))
                >= config.material_source_min_fraction,
                "mean_predator_arrival_time": mean_not_none(arrival_times),
                "min_predator_arrival_time": min(arrival_times) if arrival_times else None,
                "max_predator_arrival_time": max(arrival_times) if arrival_times else None,
                "mean_prey_extirpation_time": mean_not_none(extirpation_times),
            }
        )
    uncolonized_rows = [row for row in passable_rows if not row.predator_final_occupied]
    summary_rows.append(
        {
            "row_role": "uncolonized_passable_accounting",
            "source_zone_id": "uncolonized_passable",
            "source_contributed_colonized_passable_count": None,
            "source_contribution_fraction_of_colonized_passable": None,
            "source_contribution_denominator": None,
            "uncolonized_passable_count": len(uncolonized_rows),
            "uncolonized_passable_fraction_of_all_passable": safe_fraction(
                len(uncolonized_rows), len(passable_rows)
            ),
            "uncolonized_fraction_denominator": "all_passable_count",
            "material_source_threshold_fraction_of_colonized_passable": (
                config.material_source_min_fraction
            ),
            "is_material_source": False,
            "mean_predator_arrival_time": None,
            "min_predator_arrival_time": None,
            "max_predator_arrival_time": None,
            "mean_prey_extirpation_time": None,
        }
    )
    return tuple(summary_rows)


def build_habitat_class_timing_summary_rows(
    candidate: SpreadImpactCandidate,
    rows: tuple[SpreadImpactCellTruth, ...],
) -> tuple[CsvRow, ...]:
    summary_rows: list[CsvRow] = []
    for habitat_class in HABITAT_CLASSES:
        class_rows = [row for row in rows if row.landscape_cell.habitat_class == habitat_class]
        passable_rows = [row for row in class_rows if row.landscape_cell.passability == "passable"]
        arrival_times = [
            row.predator_arrival_time
            for row in passable_rows
            if row.predator_arrival_time is not None
        ]
        extirpation_times = [
            row.prey_extirpation_time
            for row in passable_rows
            if row.prey_extirpation_time is not None
        ]
        conductance = candidate.conductance_for(habitat_class)
        extirpated_count = len(extirpation_times)
        summary_rows.append(
            {
                "habitat_class": habitat_class,
                "cell_count": len(class_rows),
                "passable_cell_count": len(passable_rows),
                "mean_conductance": conductance,
                "finite_arrival_count": len(arrival_times),
                "finite_arrival_fraction": safe_fraction(len(arrival_times), len(passable_rows)),
                "mean_predator_arrival_time": mean_not_none(arrival_times),
                "median_predator_arrival_time": quantile_not_none(arrival_times, 0.5),
                "mean_prey_extirpation_time": mean_not_none(extirpation_times),
                "extirpated_count": extirpated_count,
                "extirpated_fraction": safe_fraction(extirpated_count, len(passable_rows)),
            }
        )
    return tuple(summary_rows)


def build_corridor_barrier_effect_summary_rows(
    rows: tuple[SpreadImpactCellTruth, ...],
) -> tuple[CsvRow, ...]:
    passable_rows = [row for row in rows if row.landscape_cell.passability == "passable"]
    groups = (
        ("all_passable", passable_rows),
        (
            "corridor",
            [row for row in passable_rows if row.landscape_cell.habitat_class == "corridor"],
        ),
        (
            "low_quality_matrix",
            [
                row
                for row in passable_rows
                if row.landscape_cell.habitat_class == "low_quality_matrix"
            ],
        ),
        (
            "water_adjacent_passable",
            [row for row in passable_rows if row.landscape_cell.water_neighbor_count > 0],
        ),
        (
            "non_water_adjacent_passable",
            [row for row in passable_rows if row.landscape_cell.water_neighbor_count == 0],
        ),
        (
            "water_adjacent_low_quality_matrix",
            [
                row
                for row in passable_rows
                if row.landscape_cell.water_neighbor_count > 0
                and row.landscape_cell.habitat_class == "low_quality_matrix"
            ],
        ),
        (
            "non_water_adjacent_low_quality_matrix",
            [
                row
                for row in passable_rows
                if row.landscape_cell.water_neighbor_count == 0
                and row.landscape_cell.habitat_class == "low_quality_matrix"
            ],
        ),
    )
    return tuple(
        build_effect_group_row(effect_group, group_rows) for effect_group, group_rows in groups
    )


def build_effect_group_row(effect_group: str, rows: list[SpreadImpactCellTruth]) -> CsvRow:
    arrival_times = [
        row.predator_arrival_time for row in rows if row.predator_arrival_time is not None
    ]
    source_distances = [
        float(row.landscape_cell.source_distance)
        for row in rows
        if row.landscape_cell.source_distance is not None
    ]
    detours = [row.arrival_detour_index for row in rows if row.arrival_detour_index is not None]
    conductance = [row.conductance for row in rows]
    extirpated_count = sum(row.prey_extirpation_time is not None for row in rows)
    return {
        "effect_group": effect_group,
        "passable_cell_count": len(rows),
        "finite_arrival_count": len(arrival_times),
        "mean_predator_arrival_time": mean_not_none(arrival_times),
        "mean_landscape_source_distance": mean(source_distances) if source_distances else None,
        "mean_arrival_detour_index": mean_not_none(detours),
        "mean_conductance": mean(conductance) if conductance else None,
        "extirpated_count": extirpated_count,
    }


def build_prey_impact_summary_rows(
    rows: tuple[SpreadImpactCellTruth, ...],
) -> tuple[CsvRow, ...]:
    passable_rows = [row for row in rows if row.landscape_cell.passability == "passable"]
    groups: list[tuple[str, list[SpreadImpactCellTruth]]] = [("all_passable", passable_rows)]
    for habitat_class in (
        "low_quality_matrix",
        "medium_quality",
        "high_quality_patch",
        "corridor",
        "source_zone",
    ):
        groups.append(
            (
                f"habitat_class:{habitat_class}",
                [row for row in passable_rows if row.landscape_cell.habitat_class == habitat_class],
            )
        )
    return tuple(build_prey_impact_row(group_name, group_rows) for group_name, group_rows in groups)


def build_prey_impact_row(group_name: str, rows: list[SpreadImpactCellTruth]) -> CsvRow:
    impacted_rows = [row for row in rows if row.prey_impact_time is not None]
    extirpated_rows = [row for row in rows if row.prey_extirpation_time is not None]
    lags = [
        row.arrival_to_extirpation_lag
        for row in extirpated_rows
        if row.arrival_to_extirpation_lag is not None
    ]
    extirpation_times = [
        row.prey_extirpation_time
        for row in extirpated_rows
        if row.prey_extirpation_time is not None
    ]
    baseline = [
        row.prey_baseline_abundance for row in rows if row.prey_baseline_abundance is not None
    ]
    final = [row.prey_final_abundance for row in rows if row.prey_final_abundance is not None]
    return {
        "summary_group": group_name,
        "passable_cell_count": len(rows),
        "impacted_count": len(impacted_rows),
        "extirpated_count": len(extirpated_rows),
        "extirpated_fraction": safe_fraction(len(extirpated_rows), len(rows)),
        "mean_lag": mean_not_none(lags),
        "min_extirpation_time": min(extirpation_times) if extirpation_times else None,
        "max_extirpation_time": max(extirpation_times) if extirpation_times else None,
        "mean_baseline_abundance": mean_not_none(baseline),
        "mean_final_abundance": mean_not_none(final),
    }


def build_recoverability_proxy_summary_rows(
    config: SynthMediumSpreadImpactConfig,
    metrics: dict[str, float | int | str | bool],
    barrier_rows: tuple[CsvRow, ...],
) -> tuple[CsvRow, ...]:
    barrier_map = {row["effect_group"]: row for row in barrier_rows}
    corridor_arrival = csv_float(barrier_map["corridor"]["mean_predator_arrival_time"])
    matrix_arrival = csv_float(barrier_map["low_quality_matrix"]["mean_predator_arrival_time"])
    water_adjacent_matrix_detour = csv_float(
        barrier_map["water_adjacent_low_quality_matrix"]["mean_arrival_detour_index"]
    )
    non_water_adjacent_matrix_detour = csv_float(
        barrier_map["non_water_adjacent_low_quality_matrix"]["mean_arrival_detour_index"]
    )
    proxy_specs = (
        (
            "finite_predator_arrival_count",
            metrics["final_colonized_passable_count"],
            ">= 3658",
            int(metrics["final_colonized_passable_count"]) >= 3658,
            "Enough passable cells are colonized for a later target surface.",
        ),
        (
            "finite_prey_extirpation_count",
            metrics["finite_extirpation_count"],
            "between 1828 and 4441",
            config.min_extirpated_passable_fraction
            <= float(metrics["finite_extirpation_fraction"])
            <= config.max_extirpated_passable_fraction,
            "Finite prey extirpations are common but not universal.",
        ),
        (
            "arrival_time_range",
            metrics["arrival_time_range"],
            f">= {config.min_arrival_range}",
            float(metrics["arrival_time_range"]) >= config.min_arrival_range,
            "Predator arrivals span a broad time range.",
        ),
        (
            "impact_lag_range",
            metrics["lag_range"],
            f">= {config.min_lag_range}",
            float(metrics["lag_range"]) >= config.min_lag_range,
            "Arrival-to-extirpation lag is nonconstant.",
        ),
        (
            "material_source_count",
            metrics["material_source_count"],
            ">= 2",
            int(metrics["material_source_count"]) >= 2,
            "Multiple source zones contribute materially.",
        ),
        (
            "corridor_matrix_contrast",
            round_float(matrix_arrival - corridor_arrival),
            "> 0",
            corridor_arrival < matrix_arrival,
            "Corridor cells are faster than low-quality matrix on average.",
        ),
        (
            "water_detour_contrast",
            round_float(water_adjacent_matrix_detour - non_water_adjacent_matrix_detour),
            "> 0",
            water_adjacent_matrix_detour > non_water_adjacent_matrix_detour,
            "Low-quality matrix cells adjacent to water show a detour penalty.",
        ),
    )
    return tuple(
        {
            "proxy_id": proxy_id,
            "observed_value": observed_value,
            "threshold": threshold,
            "passes": passes,
            "interpretation": interpretation,
        }
        for proxy_id, observed_value, threshold, passes, interpretation in proxy_specs
    )


def verify_spread_impact_result(
    config: SynthMediumSpreadImpactConfig,
    landscape: SynthMediumLandscapeResult,
    rows: tuple[SpreadImpactCellTruth, ...],
    candidate_log_rows: tuple[CsvRow, ...],
    time_rows: tuple[CsvRow, ...],
    source_rows: tuple[CsvRow, ...],
    habitat_rows: tuple[CsvRow, ...],
    barrier_rows: tuple[CsvRow, ...],
    recoverability_rows: tuple[CsvRow, ...],
    visual_svgs: dict[str, str],
) -> tuple[SpreadImpactCheck, ...]:
    passable_rows = [row for row in rows if row.landscape_cell.passability == "passable"]
    water_rows = [row for row in rows if row.landscape_cell.passability == "water"]
    colonized_rows = [row for row in passable_rows if row.predator_final_occupied]
    extirpated_rows = [row for row in passable_rows if row.prey_extirpation_time is not None]
    arrival_times = [
        row.predator_arrival_time for row in colonized_rows if row.predator_arrival_time is not None
    ]
    lags = [
        row.arrival_to_extirpation_lag
        for row in extirpated_rows
        if row.arrival_to_extirpation_lag is not None
    ]
    final_time = max(csv_float(row["time"]) for row in time_rows)
    final_summary = next(row for row in time_rows if csv_float(row["time"]) == final_time)
    landscape_summary = landscape.summary_dict()
    material_sources = [
        row
        for row in source_rows
        if row["row_role"] == "source_contribution"
        and csv_float(row["source_contribution_fraction_of_colonized_passable"])
        >= config.material_source_min_fraction
    ]
    habitat_map = {row["habitat_class"]: row for row in habitat_rows}
    barrier_map = {row["effect_group"]: row for row in barrier_rows}
    recoverability_pass_count = sum(row["passes"] is True for row in recoverability_rows)
    return (
        SpreadImpactCheck(
            name="artifact_contract",
            passed=set(visual_svgs) == set(SYNTH_MEDIUM_SPREAD_IMPACT_VISUAL_FILES)
            and all(
                svg.lstrip().startswith("<svg") and len(svg) > 1000 for svg in visual_svgs.values()
            ),
            details={
                "output_file_count": len(SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_FILES),
                "visual_file_count": len(visual_svgs),
            },
        ),
        SpreadImpactCheck(
            name="landscape_reconciliation",
            passed=len(rows) == len(landscape.cells)
            and len(passable_rows) == object_int(landscape_summary["passable_cell_count"])
            and len(water_rows) == object_int(landscape_summary["water_cell_count"]),
            details={
                "cell_count": len(rows),
                "landscape_cell_count": len(landscape.cells),
                "passable_cell_count": len(passable_rows),
                "water_cell_count": len(water_rows),
            },
        ),
        SpreadImpactCheck(
            name="water_never_colonized",
            passed=all(
                row.predator_arrival_time is None
                and not row.predator_final_occupied
                and row.prey_baseline_abundance is None
                for row in water_rows
            ),
            details={"water_cell_count": len(water_rows)},
        ),
        SpreadImpactCheck(
            name="source_zone_seeding",
            passed=all(
                row.predator_arrival_time == 0.0
                for row in passable_rows
                if row.landscape_cell.source_zone_id
            ),
            details={
                "source_zone_cell_count": sum(
                    bool(row.landscape_cell.source_zone_id) for row in passable_rows
                )
            },
        ),
        SpreadImpactCheck(
            name="bounded_candidate_tuning",
            passed=len(candidate_log_rows) <= config.max_candidate_count
            and sum(row["selected_default"] is True for row in candidate_log_rows) == 1,
            details={
                "candidate_count": len(candidate_log_rows),
                "selected_parameter_set_id": config.selected_parameter_set_id,
            },
        ),
        SpreadImpactCheck(
            name="spread_not_trivial_or_instant",
            passed=config.final_occupancy_min_fraction
            <= safe_fraction(len(colonized_rows), len(passable_rows))
            <= config.final_occupancy_max_fraction,
            details={
                "final_colonized_passable_count": len(colonized_rows),
                "final_colonized_passable_fraction": safe_fraction(
                    len(colonized_rows), len(passable_rows)
                ),
            },
        ),
        SpreadImpactCheck(
            name="broad_arrival_distribution",
            passed=bool(arrival_times)
            and round_float(max(arrival_times) - min(arrival_times)) >= config.min_arrival_range,
            details={
                "arrival_min": min(arrival_times) if arrival_times else None,
                "arrival_max": max(arrival_times) if arrival_times else None,
                "arrival_range": round_float(max(arrival_times) - min(arrival_times))
                if arrival_times
                else None,
            },
        ),
        SpreadImpactCheck(
            name="informative_prey_impact",
            passed=config.min_extirpated_passable_fraction
            <= safe_fraction(len(extirpated_rows), len(passable_rows))
            <= config.max_extirpated_passable_fraction
            and csv_int(final_summary["prey_extirpated_passable_count"]) == len(extirpated_rows),
            details={
                "finite_prey_extirpation_count": len(extirpated_rows),
                "finite_prey_extirpation_fraction": safe_fraction(
                    len(extirpated_rows), len(passable_rows)
                ),
            },
        ),
        SpreadImpactCheck(
            name="nonzero_lag_distribution",
            passed=bool(lags)
            and min(lags) > 0.0
            and round_float(max(lags) - min(lags)) >= config.min_lag_range,
            details={
                "lag_min": min(lags) if lags else None,
                "lag_max": max(lags) if lags else None,
                "lag_range": round_float(max(lags) - min(lags)) if lags else None,
            },
        ),
        SpreadImpactCheck(
            name="multiple_material_sources",
            passed=len(material_sources) >= 2,
            details={"material_source_count": len(material_sources)},
        ),
        SpreadImpactCheck(
            name="habitat_conductance_gradient",
            passed=csv_float(habitat_map["source_zone"]["mean_conductance"])
            > csv_float(habitat_map["low_quality_matrix"]["mean_conductance"])
            and csv_float(habitat_map["corridor"]["mean_conductance"])
            > csv_float(habitat_map["low_quality_matrix"]["mean_conductance"])
            and csv_float(habitat_map["high_quality_patch"]["mean_conductance"])
            > csv_float(habitat_map["low_quality_matrix"]["mean_conductance"]),
            details={
                "source_zone": habitat_map["source_zone"]["mean_conductance"],
                "corridor": habitat_map["corridor"]["mean_conductance"],
                "high_quality_patch": habitat_map["high_quality_patch"]["mean_conductance"],
                "low_quality_matrix": habitat_map["low_quality_matrix"]["mean_conductance"],
            },
        ),
        SpreadImpactCheck(
            name="barrier_detour_signal",
            passed=csv_float(
                barrier_map["water_adjacent_low_quality_matrix"]["mean_arrival_detour_index"]
            )
            > csv_float(
                barrier_map["non_water_adjacent_low_quality_matrix"]["mean_arrival_detour_index"]
            ),
            details={
                "water_adjacent_low_quality_matrix_detour_index": barrier_map[
                    "water_adjacent_low_quality_matrix"
                ]["mean_arrival_detour_index"],
                "non_water_adjacent_low_quality_matrix_detour_index": barrier_map[
                    "non_water_adjacent_low_quality_matrix"
                ]["mean_arrival_detour_index"],
            },
        ),
        SpreadImpactCheck(
            name="recoverability_proxy_readiness",
            passed=recoverability_pass_count >= config.minimum_recoverability_proxy_pass_count,
            details={
                "passing_proxy_count": recoverability_pass_count,
                "minimum_required": config.minimum_recoverability_proxy_pass_count,
            },
        ),
    )


def build_spread_impact_visual_svgs(
    config: SynthMediumSpreadImpactConfig,
    candidate: SpreadImpactCandidate,
    rows: tuple[SpreadImpactCellTruth, ...],
) -> dict[str, str]:
    return {
        "predator_arrival_time.svg": render_truth_grid_svg(
            rows,
            title="Synth-Medium Predator Arrival Time",
            color_mode="arrival",
        ),
        "predator_occupancy_snapshots.svg": render_snapshot_svg(
            rows,
            title="Predator Occupancy Snapshots",
            mode="predator_occupancy",
            times=config.review_times,
            candidate=candidate,
        ),
        "prey_abundance_snapshots.svg": render_snapshot_svg(
            rows,
            title="Prey Abundance Snapshots",
            mode="prey_abundance",
            times=config.review_times,
            candidate=candidate,
        ),
        "prey_impact_time.svg": render_truth_grid_svg(
            rows,
            title="Prey Extirpation Time",
            color_mode="extirpation",
        ),
        "source_contribution_map.svg": render_truth_grid_svg(
            rows,
            title="Predator Source Contribution",
            color_mode="source",
        ),
        "arrival_impact_lag.svg": render_truth_grid_svg(
            rows,
            title="Arrival To Extirpation Lag",
            color_mode="lag",
        ),
        "review_montage.svg": render_review_montage_svg(config, candidate, rows),
    }


def render_truth_grid_svg(
    rows: tuple[SpreadImpactCellTruth, ...],
    *,
    title: str,
    color_mode: str,
    cell_size: int = 7,
) -> str:
    max_row = max(row.landscape_cell.row for row in rows)
    max_col = max(row.landscape_cell.col for row in rows)
    width = (max_col + 1) * cell_size + 84
    height = (max_row + 1) * cell_size + 108
    finite_values = numeric_values_for_mode(rows, color_mode)
    value_min = min(finite_values) if finite_values else 0.0
    value_max = max(finite_values) if finite_values else 1.0
    parts = svg_header(width, height, title)
    for row in rows:
        cell = row.landscape_cell
        fill = truth_cell_fill(row, color_mode, value_min, value_max)
        x = 42 + (cell.col * cell_size)
        y = 42 + (cell.row * cell_size)
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
            f'fill="{fill}" stroke="#ffffff" stroke-width="0.15"/>'
        )
    parts.append(
        f'<text x="42" y="{height - 14}" font-size="12" font-family="monospace">'
        f"mode={color_mode} min={value_min:.3f} max={value_max:.3f}</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_snapshot_svg(
    rows: tuple[SpreadImpactCellTruth, ...],
    *,
    title: str,
    mode: str,
    times: tuple[int, ...],
    candidate: SpreadImpactCandidate,
) -> str:
    cell_size = 3
    max_row = max(row.landscape_cell.row for row in rows)
    max_col = max(row.landscape_cell.col for row in rows)
    panel_width = (max_col + 1) * cell_size + 56
    panel_height = (max_row + 1) * cell_size + 42
    columns = 2
    width = panel_width * columns
    height = panel_height * ((len(times) + 1) // columns)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]
    max_baseline = max(
        row.prey_baseline_abundance or 0.0
        for row in rows
        if row.landscape_cell.passability == "passable"
    )
    for index, time in enumerate(times):
        panel_col = index % columns
        panel_row = index // columns
        offset_x = panel_col * panel_width
        offset_y = panel_row * panel_height
        parts.append(
            f'<text x="{offset_x + 28}" y="{offset_y + 18}" font-size="12" '
            f'font-family="monospace">{title} t={time}</text>'
        )
        for row in rows:
            cell = row.landscape_cell
            fill = snapshot_fill(row, mode, float(time), candidate, max_baseline)
            x = offset_x + 28 + (cell.col * cell_size)
            y = offset_y + 28 + (cell.row * cell_size)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'fill="{fill}" stroke="#ffffff" stroke-width="0.05"/>'
            )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_review_montage_svg(
    config: SynthMediumSpreadImpactConfig,
    candidate: SpreadImpactCandidate,
    rows: tuple[SpreadImpactCellTruth, ...],
) -> str:
    del config
    cell_size = 3
    max_row = max(row.landscape_cell.row for row in rows)
    max_col = max(row.landscape_cell.col for row in rows)
    panel_width = (max_col + 1) * cell_size + 56
    panel_height = (max_row + 1) * cell_size + 42
    panels = (
        ("Arrival", "arrival"),
        ("Source", "source"),
        ("Extirpation", "extirpation"),
        ("Lag", "lag"),
        ("Final Occupancy", "final_occupancy"),
        ("Final Abundance", "final_abundance"),
    )
    width = panel_width * 2
    height = panel_height * 3
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]
    max_baseline = max(
        row.prey_baseline_abundance or 0.0
        for row in rows
        if row.landscape_cell.passability == "passable"
    )
    for index, (title, mode) in enumerate(panels):
        panel_col = index % 2
        panel_row = index // 2
        offset_x = panel_col * panel_width
        offset_y = panel_row * panel_height
        parts.append(
            f'<text x="{offset_x + 28}" y="{offset_y + 18}" font-size="12" '
            f'font-family="monospace">{title}</text>'
        )
        values = numeric_values_for_mode(rows, mode)
        value_min = min(values) if values else 0.0
        value_max = max(values) if values else 1.0
        for row in rows:
            cell = row.landscape_cell
            if mode == "final_occupancy":
                fill = snapshot_fill(
                    row, "predator_occupancy", candidate.horizon, candidate, max_baseline
                )
            elif mode == "final_abundance":
                fill = snapshot_fill(
                    row, "prey_abundance", candidate.horizon, candidate, max_baseline
                )
            else:
                fill = truth_cell_fill(row, mode, value_min, value_max)
            x = offset_x + 28 + (cell.col * cell_size)
            y = offset_y + 28 + (cell.row * cell_size)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'fill="{fill}" stroke="#ffffff" stroke-width="0.05"/>'
            )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="42" y="24" font-size="18" font-family="monospace">{title}</text>',
    ]


def numeric_values_for_mode(rows: tuple[SpreadImpactCellTruth, ...], mode: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = value_for_mode(row, mode)
        if value is not None:
            values.append(value)
    return values


def value_for_mode(row: SpreadImpactCellTruth, mode: str) -> float | None:
    if mode == "arrival":
        return row.predator_arrival_time
    if mode == "extirpation":
        return row.prey_extirpation_time
    if mode == "lag":
        return row.arrival_to_extirpation_lag
    if mode == "final_abundance":
        return row.prey_final_abundance
    return None


def truth_cell_fill(
    row: SpreadImpactCellTruth,
    mode: str,
    value_min: float,
    value_max: float,
) -> str:
    cell = row.landscape_cell
    if cell.passability == "water":
        return "#4f9cc9"
    if mode == "source":
        return source_color(row.source_zone_id) if row.predator_final_occupied else "#d1d5db"
    value = value_for_mode(row, mode)
    if value is None:
        return "#d1d5db"
    if mode == "arrival":
        return interpolate_hex("#fff7cc", "#5a2a83", normalize_value(value, value_min, value_max))
    if mode == "extirpation":
        return interpolate_hex("#eff6ff", "#b91c1c", normalize_value(value, value_min, value_max))
    if mode == "lag":
        return interpolate_hex("#fef3c7", "#92400e", normalize_value(value, value_min, value_max))
    if mode == "final_abundance":
        return interpolate_hex("#f8f4d8", "#166534", normalize_value(value, value_min, value_max))
    return "#d1d5db"


def snapshot_fill(
    row: SpreadImpactCellTruth,
    mode: str,
    time: float,
    candidate: SpreadImpactCandidate,
    max_baseline: float,
) -> str:
    cell = row.landscape_cell
    if cell.passability == "water":
        return "#4f9cc9"
    if mode == "predator_occupancy":
        if row.predator_arrival_time is not None and row.predator_arrival_time <= time:
            return source_color(row.source_zone_id)
        return "#ece9d1"
    if mode == "prey_abundance":
        if row.prey_baseline_abundance is None or row.predator_arrival_time is None:
            value = row.prey_baseline_abundance or 0.0
        else:
            lag = row.arrival_to_extirpation_lag or compute_extirpation_lag(
                candidate,
                row.landscape_cell,
                row.predator_arrival_time,
            )
            value = prey_abundance_at_time(
                candidate,
                row.prey_baseline_abundance,
                row.predator_arrival_time,
                lag,
                time,
            )
        return interpolate_hex("#f4edc8", "#166534", value / max(max_baseline, 1e-6))
    raise ValueError(f"unsupported snapshot mode: {mode}")


def source_color(source_zone_id: str) -> str:
    return {
        "source_west_north": "#7c3aed",
        "source_west_mid": "#0f766e",
        "source_west_south": "#dc2626",
    }.get(source_zone_id, "#64748b")


def normalize_value(value: float, value_min: float, value_max: float) -> float:
    return (value - value_min) / max(value_max - value_min, 1e-12)


def render_spread_impact_report(result: SynthMediumSpreadImpactResult) -> str:
    summary = result.summary_dict()
    visual_lines = "\n".join(
        f"- [`visuals/{name}`](visuals/{name})" for name in SYNTH_MEDIUM_SPREAD_IMPACT_VISUAL_FILES
    )
    gate_lines = "\n".join(
        f"- `{check.name}`: `{'passed' if check.passed else 'failed'}`"
        for check in result.verification_checks
    )
    candidate_lines = "\n".join(
        f"- `{row['parameter_set_id']}`: `{row['candidate_status']}`; "
        f"colonized `{row['final_colonized_passable_count']}`, "
        f"extirpated `{row['finite_extirpation_count']}`"
        for row in result.parameter_candidate_log_rows
    )
    source_lines = "\n".join(
        f"- `{row['source_zone_id']}`: contributed "
        f"`{row['source_contributed_colonized_passable_count']}` colonized passable cells; "
        f"fraction of `{row['source_contribution_denominator']}` = "
        f"`{row['source_contribution_fraction_of_colonized_passable']}`; "
        f"material source = `{row['is_material_source']}`"
        for row in result.source_contribution_summary_rows
        if row["row_role"] == "source_contribution"
    )
    uncolonized_accounting = next(
        row
        for row in result.source_contribution_summary_rows
        if row["row_role"] == "uncolonized_passable_accounting"
    )
    proxy_lines = "\n".join(
        f"- `{row['proxy_id']}`: observed `{row['observed_value']}`; "
        f"threshold `{row['threshold']}`; passes `{row['passes']}`"
        for row in result.recoverability_proxy_summary_rows
    )
    return f"""# Synth-Medium Spread-Impact Review Pack

## Boundary

This bundle is synthetic-only and spread-impact-review-only. It uses the
accepted Goal 017 landscape without changing its design contract. It does not
create observations, reconstruct extirpation from observations, fit parameters,
run ABC/POM/likelihood/MCMC/posterior workflows, analyse real data, or start a
follow-on goal.

## Selected Default

- Parameter set: `{result.selected_candidate.parameter_set_id}`
- Recommendation: `{result.recommendation_class}`
- Final colonized passable cells: `{summary["final_colonized_passable_count"]}`
- Finite prey extirpations: `{summary["finite_prey_extirpation_count"]}`
- Material source count: `{summary["material_source_count"]}`

## Candidate Tuning Summary

{candidate_lines}

## Source Contribution Denominators

Source contribution fractions are fractions of final colonized passable cells,
not fractions of all passable cells:

{source_lines}

The uncolonized row is an all-passable accounting row:

- `{uncolonized_accounting["source_zone_id"]}`: uncolonized passable cells
  `{uncolonized_accounting["uncolonized_passable_count"]}`; fraction of
  `{uncolonized_accounting["uncolonized_fraction_denominator"]}` =
  `{uncolonized_accounting["uncolonized_passable_fraction_of_all_passable"]}`.

## Recoverability Proxies

{proxy_lines}

## Review Gates

{gate_lines}

## Visual Review Files

{visual_lines}

## Interpretation

The selected default is intended as a deterministic synthetic truth object for
human visual and audit-table review. The candidate is not estimated from data
and should not be treated as a fitted or posterior-supported scenario.
"""


def round_float(value: float) -> float:
    return round(float(value), 12)


def mean_not_none(values: Iterable[float | None]) -> float | None:
    concrete = [float(value) for value in values if value is not None]
    if not concrete:
        return None
    return mean(concrete)


def quantile_not_none(values: Iterable[float | None], probability: float) -> float | None:
    concrete = [float(value) for value in values if value is not None]
    if not concrete:
        return None
    return quantile(concrete, probability)


def csv_float(value: CsvValue) -> float:
    if value is None or isinstance(value, bool):
        raise TypeError(f"expected float-like CSV value, got {value!r}")
    return float(value)


def csv_int(value: CsvValue) -> int:
    if value is None or isinstance(value, bool):
        raise TypeError(f"expected integer-like CSV value, got {value!r}")
    return int(value)


def object_int(value: object) -> int:
    if value is None or isinstance(value, bool):
        raise TypeError(f"expected integer-like object, got {value!r}")
    if isinstance(value, (str, int, float)):
        return int(value)
    raise TypeError(f"expected integer-like object, got {value!r}")


def csv_bool(value: CsvValue) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"expected boolean CSV value, got {value!r}")
    return value
