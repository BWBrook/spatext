from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from itertools import pairwise
from json import dumps
from os import PathLike
from pathlib import Path

from .landscape import (
    CsvRow,
    CsvValue,
    interpolate_hex,
    mean,
    safe_fraction,
    write_csv_rows,
)
from .spread_impact import (
    SpreadImpactCellTruth,
    SynthMediumSpreadImpactResult,
    build_synth_medium_spread_impact_review_pack,
)

DEFAULT_SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_DIR = Path(
    "artifacts/synth_medium_observation_design"
)
SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_FILES = (
    "observation_design_config.json",
    "regime_summary.csv",
    "survey_schedule.csv",
    "observation_records.csv",
    "cell_observation_summary.csv",
    "truth_observation_bridge.csv",
    "false_negative_summary.csv",
    "coverage_gap_summary.csv",
    "effort_by_habitat_region_summary.csv",
    "recoverability_signal_summary.csv",
    "verification.json",
    "report.md",
)
SYNTH_MEDIUM_OBSERVATION_DESIGN_VISUAL_FILES = (
    "survey_effort_surface_default.svg",
    "observed_final_response_default.svg",
    "truth_observed_mismatch_default.svg",
    "post_impact_support_default.svg",
    "regime_comparison_montage.svg",
    "review_montage.svg",
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "synth_medium_spread_impact_source_verified": True,
    "observation_design_review_only": True,
    "response_only_observations": True,
    "full_observability_is_benchmark_only": True,
    "selected_default_is_imperfect_observation": True,
    "visual_review_required": True,
    "no_reconstruction_or_inference": True,
    "no_abc_pom_likelihood_or_posterior": True,
    "no_real_data": True,
}

TRUTH_EXPECTATIONS = {
    "selected_parameter_set_id": "balanced_corridor_detour_v2",
    "cell_count": 6048,
    "passable_cell_count": 5225,
    "water_cell_count": 823,
    "final_colonized_passable_count": 4605,
    "finite_prey_extirpation_count": 4289,
}

LegendItem = tuple[str, str]

SURVEY_EFFORT_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#f3f4f6", "No survey"),
    ("#dbeafe", "Low effort"),
    ("#1d4ed8", "High effort"),
)
FINAL_STATUS_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#15803d", "Late detection"),
    ("#7c3aed", "Post-impact non-detection"),
    ("#f59e0b", "No late support"),
    ("#d1d5db", "Never surveyed"),
)
MISMATCH_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#2563eb", "Observed true extirpation"),
    ("#dc2626", "False negative"),
    ("#ea580c", "Unexpected observed change"),
    ("#94a3b8", "Not extirpated / uninformative"),
)
POST_IMPACT_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#fee2e2", "No post-impact support"),
    ("#dcfce7", "Some support"),
    ("#166534", "Strong support"),
)

REGIME_IDS = (
    "truth_reference_full_observability",
    "structured_response_observed_default",
    "sparse_response_observed_stress",
)

REGIME_SUMMARY_COLUMNS = (
    "regime_id",
    "regime_role",
    "selected_default",
    "is_benchmark_only",
    "survey_time_count",
    "survey_record_count",
    "observation_record_count",
    "surveyed_passable_count",
    "surveyed_passable_fraction",
    "mean_effort",
    "detection_count",
    "detection_rate",
    "true_extirpated_count",
    "observed_response_change_count",
    "false_negative_count",
    "false_negative_fraction",
    "post_impact_support_count",
    "post_impact_support_fraction",
    "detected_response_time_min",
    "detected_response_time_max",
    "detected_response_time_range",
    "habitat_class_count_with_records",
    "col_band_count_with_records",
    "regime_recommendation",
)

SURVEY_SCHEDULE_COLUMNS = (
    "regime_id",
    "survey_id",
    "cell_id",
    "row",
    "col",
    "time",
    "effort",
    "habitat_class",
    "row_band",
    "col_band",
    "passability",
    "sampling_frame_member",
    "post_impact_window",
    "design_weight",
)

OBSERVATION_RECORD_COLUMNS = (
    "regime_id",
    "survey_id",
    "cell_id",
    "row",
    "col",
    "time",
    "effort",
    "passability",
    "observed_count",
    "detected",
)

CELL_OBSERVATION_SUMMARY_COLUMNS = (
    "regime_id",
    "cell_id",
    "row",
    "col",
    "habitat_class",
    "row_band",
    "col_band",
    "survey_count",
    "detection_count",
    "first_survey_time",
    "last_survey_time",
    "first_detection_time",
    "last_detection_time",
    "pre_impact_survey_count",
    "pre_impact_detection_count",
    "post_impact_survey_count",
    "post_impact_non_detection_count",
    "max_gap_between_surveys",
    "observed_response_change",
    "observed_response_time",
    "final_observed_status",
)

TRUTH_OBSERVATION_BRIDGE_COLUMNS = (
    "regime_id",
    "cell_id",
    "row",
    "col",
    "habitat_class",
    "row_band",
    "col_band",
    "predator_arrival_time",
    "prey_impact_time",
    "prey_extirpation_time",
    "true_extirpated_by_end",
    "survey_count",
    "detection_count",
    "post_impact_survey_count",
    "post_impact_non_detection_count",
    "observed_response_change",
    "observed_response_time",
    "false_negative",
)

FALSE_NEGATIVE_SUMMARY_COLUMNS = (
    "regime_id",
    "summary_group",
    "true_extirpated_count",
    "observed_response_change_count",
    "false_negative_count",
    "false_negative_fraction",
)

COVERAGE_GAP_SUMMARY_COLUMNS = (
    "regime_id",
    "summary_group",
    "passable_cell_count",
    "surveyed_cell_count",
    "surveyed_cell_fraction",
    "no_survey_count",
    "no_pre_impact_support_count",
    "no_post_impact_support_count",
    "mean_survey_count",
    "mean_max_survey_gap",
)

EFFORT_BY_HABITAT_REGION_SUMMARY_COLUMNS = (
    "regime_id",
    "habitat_class",
    "col_band",
    "cell_count",
    "survey_record_count",
    "mean_effort",
    "detection_rate",
    "post_impact_support_fraction",
    "false_negative_count",
)

RECOVERABILITY_SIGNAL_SUMMARY_COLUMNS = (
    "regime_id",
    "proxy_id",
    "observed_value",
    "threshold",
    "passes",
    "interpretation",
)


@dataclass(frozen=True, slots=True)
class ObservationRegime:
    regime_id: str
    regime_role: str
    selected_default: bool
    is_benchmark_only: bool
    survey_times: tuple[int, ...]
    frame_probability: float
    visit_probability: float
    effort_scale: float
    detection_scale: float
    post_impact_gap_strength: float
    perfect_observability: bool
    rationale: str


@dataclass(frozen=True, slots=True)
class SynthMediumObservationDesignConfig:
    selected_default_regime_id: str = "structured_response_observed_default"
    deterministic_seed: int = 20260615
    min_default_surveyed_fraction: float = 0.70
    max_default_surveyed_fraction: float = 0.98
    min_default_false_negative_count: int = 25
    max_default_false_negative_fraction: float = 0.65
    min_default_post_impact_support_fraction: float = 0.40
    min_default_detected_response_time_range: float = 60.0
    min_default_habitat_classes_with_records: int = 5
    min_default_col_bands_with_records: int = 3

    def to_dict(self) -> dict[str, object]:
        return {
            "selected_default_regime_id": self.selected_default_regime_id,
            "deterministic_seed": self.deterministic_seed,
            "review_gate_thresholds": {
                "min_default_surveyed_fraction": self.min_default_surveyed_fraction,
                "max_default_surveyed_fraction": self.max_default_surveyed_fraction,
                "min_default_false_negative_count": self.min_default_false_negative_count,
                "max_default_false_negative_fraction": self.max_default_false_negative_fraction,
                "min_default_post_impact_support_fraction": (
                    self.min_default_post_impact_support_fraction
                ),
                "min_default_detected_response_time_range": (
                    self.min_default_detected_response_time_range
                ),
                "min_default_habitat_classes_with_records": (
                    self.min_default_habitat_classes_with_records
                ),
                "min_default_col_bands_with_records": (self.min_default_col_bands_with_records),
            },
            "output_files": list(SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_FILES),
            "visual_files": [
                f"visuals/{name}" for name in SYNTH_MEDIUM_OBSERVATION_DESIGN_VISUAL_FILES
            ],
            **BOUNDARY_LABELS,
        }


@dataclass(frozen=True, slots=True)
class ObservationDesignCheck:
    name: str
    passed: bool
    details: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "details": self.details}


@dataclass(frozen=True, slots=True)
class SynthMediumObservationDesignResult:
    config: SynthMediumObservationDesignConfig
    truth: SynthMediumSpreadImpactResult
    regimes: tuple[ObservationRegime, ...]
    regime_summary_rows: tuple[CsvRow, ...]
    survey_schedule_rows: tuple[CsvRow, ...]
    observation_record_rows: tuple[CsvRow, ...]
    cell_observation_summary_rows: tuple[CsvRow, ...]
    truth_observation_bridge_rows: tuple[CsvRow, ...]
    false_negative_summary_rows: tuple[CsvRow, ...]
    coverage_gap_summary_rows: tuple[CsvRow, ...]
    effort_by_habitat_region_summary_rows: tuple[CsvRow, ...]
    recoverability_signal_summary_rows: tuple[CsvRow, ...]
    verification_checks: tuple[ObservationDesignCheck, ...]
    visual_svgs: dict[str, str]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    @property
    def recommendation_class(self) -> str:
        if self.passed:
            return "ready_for_human_observation_design_review"
        return "observation_design_review_blocked"

    def summary_dict(self) -> dict[str, object]:
        default_summary = regime_row(
            self.regime_summary_rows, self.config.selected_default_regime_id
        )
        return {
            "selected_default_regime_id": self.config.selected_default_regime_id,
            "regime_count": len(self.regimes),
            "default_survey_record_count": csv_int(default_summary["survey_record_count"]),
            "default_false_negative_count": csv_int(default_summary["false_negative_count"]),
            "default_post_impact_support_fraction": csv_float(
                default_summary["post_impact_support_fraction"]
            ),
            "recommendation_class": self.recommendation_class,
        }

    def config_payload(self) -> dict[str, object]:
        return {
            **self.config.to_dict(),
            "truth_source_summary": truth_source_summary(self.truth),
            "regimes": [regime_to_dict(regime) for regime in self.regimes],
            "summary": self.summary_dict(),
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

        config_path = target_dir / "observation_design_config.json"
        config_path.write_text(
            dumps(self.config_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(config_path)

        table_specs: tuple[tuple[str, tuple[str, ...], tuple[CsvRow, ...]], ...] = (
            ("regime_summary.csv", REGIME_SUMMARY_COLUMNS, self.regime_summary_rows),
            ("survey_schedule.csv", SURVEY_SCHEDULE_COLUMNS, self.survey_schedule_rows),
            (
                "observation_records.csv",
                OBSERVATION_RECORD_COLUMNS,
                self.observation_record_rows,
            ),
            (
                "cell_observation_summary.csv",
                CELL_OBSERVATION_SUMMARY_COLUMNS,
                self.cell_observation_summary_rows,
            ),
            (
                "truth_observation_bridge.csv",
                TRUTH_OBSERVATION_BRIDGE_COLUMNS,
                self.truth_observation_bridge_rows,
            ),
            (
                "false_negative_summary.csv",
                FALSE_NEGATIVE_SUMMARY_COLUMNS,
                self.false_negative_summary_rows,
            ),
            (
                "coverage_gap_summary.csv",
                COVERAGE_GAP_SUMMARY_COLUMNS,
                self.coverage_gap_summary_rows,
            ),
            (
                "effort_by_habitat_region_summary.csv",
                EFFORT_BY_HABITAT_REGION_SUMMARY_COLUMNS,
                self.effort_by_habitat_region_summary_rows,
            ),
            (
                "recoverability_signal_summary.csv",
                RECOVERABILITY_SIGNAL_SUMMARY_COLUMNS,
                self.recoverability_signal_summary_rows,
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
        report_path.write_text(render_observation_design_report(self), encoding="utf-8")
        written.append(report_path)

        for visual_name in SYNTH_MEDIUM_OBSERVATION_DESIGN_VISUAL_FILES:
            path = visuals_dir / visual_name
            path.write_text(self.visual_svgs[visual_name], encoding="utf-8")
            written.append(path)

        return tuple(written)


def build_synth_medium_observation_design_review_pack(
    config: SynthMediumObservationDesignConfig | None = None,
    *,
    truth: SynthMediumSpreadImpactResult | None = None,
) -> SynthMediumObservationDesignResult:
    observation_config = config or SynthMediumObservationDesignConfig()
    truth_result = truth or build_synth_medium_spread_impact_review_pack()
    validate_truth_source(truth_result)
    regimes = default_observation_regimes()
    if observation_config.selected_default_regime_id not in {
        regime.regime_id for regime in regimes
    }:
        raise ValueError("selected default regime must be included in regimes")

    passable_truth = tuple(
        row for row in truth_result.cell_truth_rows if row.landscape_cell.passability == "passable"
    )
    survey_rows: list[CsvRow] = []
    observation_rows: list[CsvRow] = []
    cell_summary_rows: list[CsvRow] = []
    bridge_rows: list[CsvRow] = []

    for regime in regimes:
        regime_survey_rows, regime_observation_rows = build_regime_observation_records(
            observation_config,
            regime,
            passable_truth,
        )
        survey_rows.extend(regime_survey_rows)
        observation_rows.extend(regime_observation_rows)
        summaries = build_cell_observation_summary_rows(
            regime,
            passable_truth,
            regime_observation_rows,
        )
        cell_summary_rows.extend(summaries)
        bridge_rows.extend(build_truth_observation_bridge_rows(passable_truth, summaries))

    regime_summary_rows = build_regime_summary_rows(
        regimes,
        passable_truth,
        tuple(survey_rows),
        tuple(observation_rows),
        tuple(cell_summary_rows),
    )
    false_negative_rows = build_false_negative_summary_rows(
        regimes, tuple(cell_summary_rows), passable_truth
    )
    coverage_gap_rows = build_coverage_gap_summary_rows(
        regimes, tuple(cell_summary_rows), passable_truth
    )
    effort_rows = build_effort_by_habitat_region_summary_rows(
        regimes,
        passable_truth,
        tuple(survey_rows),
        tuple(observation_rows),
        tuple(cell_summary_rows),
    )
    signal_rows = build_recoverability_signal_summary_rows(
        observation_config,
        regime_summary_rows,
    )
    visual_svgs = build_observation_design_visual_svgs(
        passable_truth,
        tuple(cell_summary_rows),
        regime_summary_rows,
    )
    checks = verify_observation_design_result(
        observation_config,
        truth_result,
        regimes,
        tuple(survey_rows),
        tuple(observation_rows),
        tuple(cell_summary_rows),
        tuple(bridge_rows),
        regime_summary_rows,
        signal_rows,
        visual_svgs,
    )
    return SynthMediumObservationDesignResult(
        config=observation_config,
        truth=truth_result,
        regimes=regimes,
        regime_summary_rows=regime_summary_rows,
        survey_schedule_rows=tuple(survey_rows),
        observation_record_rows=tuple(observation_rows),
        cell_observation_summary_rows=tuple(cell_summary_rows),
        truth_observation_bridge_rows=tuple(bridge_rows),
        false_negative_summary_rows=false_negative_rows,
        coverage_gap_summary_rows=coverage_gap_rows,
        effort_by_habitat_region_summary_rows=effort_rows,
        recoverability_signal_summary_rows=signal_rows,
        verification_checks=checks,
        visual_svgs=visual_svgs,
    )


def default_observation_regimes() -> tuple[ObservationRegime, ...]:
    return (
        ObservationRegime(
            regime_id="truth_reference_full_observability",
            regime_role="benchmark",
            selected_default=False,
            is_benchmark_only=True,
            survey_times=tuple(range(0, 121, 12)),
            frame_probability=1.0,
            visit_probability=1.0,
            effort_scale=1.0,
            detection_scale=1.0,
            post_impact_gap_strength=0.0,
            perfect_observability=True,
            rationale="Full response visibility benchmark only.",
        ),
        ObservationRegime(
            regime_id="structured_response_observed_default",
            regime_role="default",
            selected_default=True,
            is_benchmark_only=False,
            survey_times=tuple(range(0, 121, 12)),
            frame_probability=0.84,
            visit_probability=0.46,
            effort_scale=1.0,
            detection_scale=0.82,
            post_impact_gap_strength=0.30,
            perfect_observability=False,
            rationale="Plausible imperfect response-only survey design.",
        ),
        ObservationRegime(
            regime_id="sparse_response_observed_stress",
            regime_role="stress",
            selected_default=False,
            is_benchmark_only=False,
            survey_times=(0, 24, 48, 72, 96, 120),
            frame_probability=0.48,
            visit_probability=0.25,
            effort_scale=0.66,
            detection_scale=0.58,
            post_impact_gap_strength=0.55,
            perfect_observability=False,
            rationale="Low-information response-only stress test.",
        ),
    )


def validate_truth_source(truth: SynthMediumSpreadImpactResult) -> None:
    if not truth.passed:
        raise RuntimeError("synth-medium spread-impact source verification did not pass")
    summary = truth.summary_dict()
    for key, expected in TRUTH_EXPECTATIONS.items():
        if summary[key] != expected:
            raise RuntimeError(
                f"synth-medium spread-impact source mismatch for {key}: "
                f"expected {expected!r}, got {summary[key]!r}"
            )


def build_regime_observation_records(
    config: SynthMediumObservationDesignConfig,
    regime: ObservationRegime,
    passable_truth: tuple[SpreadImpactCellTruth, ...],
) -> tuple[list[CsvRow], list[CsvRow]]:
    survey_rows: list[CsvRow] = []
    observation_rows: list[CsvRow] = []
    survey_index = 0
    for truth_row in passable_truth:
        if not cell_in_sampling_frame(config, regime, truth_row):
            continue
        for time in regime.survey_times:
            if not survey_conducted(config, regime, truth_row, time):
                continue
            survey_index += 1
            survey_id = f"{regime.regime_id}_survey_{survey_index:06d}"
            effort = survey_effort(config, regime, truth_row, time)
            design_weight = survey_design_weight(config, regime, truth_row, time)
            post_impact_window = (
                truth_row.prey_extirpation_time is not None
                and float(time) >= truth_row.prey_extirpation_time
            )
            latent_abundance = latent_prey_abundance_at_time(truth_row, float(time))
            detected = observed_detected(config, regime, truth_row, time, effort, latent_abundance)
            observed_count = observed_count_for(
                config, regime, truth_row, time, effort, latent_abundance, detected
            )
            cell = truth_row.landscape_cell
            survey_rows.append(
                {
                    "regime_id": regime.regime_id,
                    "survey_id": survey_id,
                    "cell_id": cell.cell_id,
                    "row": cell.row,
                    "col": cell.col,
                    "time": time,
                    "effort": effort,
                    "habitat_class": cell.habitat_class,
                    "row_band": cell.row_band,
                    "col_band": cell.col_band,
                    "passability": cell.passability,
                    "sampling_frame_member": True,
                    "post_impact_window": post_impact_window,
                    "design_weight": design_weight,
                }
            )
            observation_rows.append(
                {
                    "regime_id": regime.regime_id,
                    "survey_id": survey_id,
                    "cell_id": cell.cell_id,
                    "row": cell.row,
                    "col": cell.col,
                    "time": time,
                    "effort": effort,
                    "passability": cell.passability,
                    "observed_count": observed_count,
                    "detected": detected,
                }
            )
    return survey_rows, observation_rows


def cell_in_sampling_frame(
    config: SynthMediumObservationDesignConfig,
    regime: ObservationRegime,
    truth_row: SpreadImpactCellTruth,
) -> bool:
    if regime.perfect_observability:
        return True
    cell = truth_row.landscape_cell
    probability = regime.frame_probability
    probability += {
        "source_zone": 0.06,
        "corridor": 0.05,
        "high_quality_patch": 0.03,
        "medium_quality": 0.01,
        "low_quality_matrix": -0.03,
    }[cell.habitat_class]
    probability += {"west_band": 0.04, "central_band": 0.0, "east_band": -0.04}[cell.col_band]
    probability += 0.03 if cell.water_neighbor_count == 0 else -0.03
    return stable_unit(config.deterministic_seed, regime.regime_id, cell.cell_id, 0) < clamp(
        probability, 0.08, 0.98
    )


def survey_conducted(
    config: SynthMediumObservationDesignConfig,
    regime: ObservationRegime,
    truth_row: SpreadImpactCellTruth,
    time: int,
) -> bool:
    if regime.perfect_observability:
        return True
    probability = survey_design_weight(config, regime, truth_row, time)
    return (
        stable_unit(
            config.deterministic_seed, regime.regime_id, truth_row.landscape_cell.cell_id, time
        )
        < probability
    )


def survey_design_weight(
    config: SynthMediumObservationDesignConfig,
    regime: ObservationRegime,
    truth_row: SpreadImpactCellTruth,
    time: int,
) -> float:
    cell = truth_row.landscape_cell
    time_scaled = time / 120.0
    probability = regime.visit_probability
    probability += {
        "source_zone": 0.06,
        "corridor": 0.05,
        "high_quality_patch": 0.03,
        "medium_quality": 0.00,
        "low_quality_matrix": -0.04,
    }[cell.habitat_class]
    probability += {"west_band": 0.05, "central_band": 0.01, "east_band": -0.05}[cell.col_band]
    probability += 0.04 * time_scaled
    probability -= 0.03 if cell.water_neighbor_count > 0 else 0.0
    if truth_row.prey_extirpation_time is not None and time >= truth_row.prey_extirpation_time:
        gap_noise = stable_unit(
            config.deterministic_seed + 31,
            regime.regime_id,
            cell.cell_id,
            int(truth_row.prey_extirpation_time),
        )
        probability -= regime.post_impact_gap_strength * (0.18 + 0.22 * gap_noise)
    return clamp(probability, 0.02, 1.0)


def survey_effort(
    config: SynthMediumObservationDesignConfig,
    regime: ObservationRegime,
    truth_row: SpreadImpactCellTruth,
    time: int,
) -> float:
    if regime.perfect_observability:
        return 1.0
    cell = truth_row.landscape_cell
    habitat_multiplier = {
        "source_zone": 1.22,
        "corridor": 1.14,
        "high_quality_patch": 1.10,
        "medium_quality": 1.00,
        "low_quality_matrix": 0.88,
    }[cell.habitat_class]
    region_multiplier = {"west_band": 1.10, "central_band": 1.00, "east_band": 0.86}[cell.col_band]
    time_multiplier = 0.88 + 0.22 * (time / 120.0)
    texture = 0.80 + 0.42 * stable_unit(
        config.deterministic_seed + 47,
        regime.regime_id,
        cell.cell_id,
        time,
    )
    effort = (
        regime.effort_scale * habitat_multiplier * region_multiplier * time_multiplier * texture
    )
    return round_float(max(0.12, effort))


def latent_prey_abundance_at_time(row: SpreadImpactCellTruth, time: float) -> float:
    baseline = row.prey_baseline_abundance or 0.0
    final = row.prey_final_abundance if row.prey_final_abundance is not None else baseline
    arrival = row.predator_arrival_time
    extirpation = row.prey_extirpation_time
    if arrival is None or time < arrival:
        return baseline
    if extirpation is None:
        decline_fraction = min(max((time - arrival) / 120.0, 0.0), 1.0)
    else:
        decline_fraction = min(max((time - arrival) / max(extirpation - arrival, 1.0), 0.0), 1.0)
    return round_float(baseline + (final - baseline) * decline_fraction)


def observed_detected(
    config: SynthMediumObservationDesignConfig,
    regime: ObservationRegime,
    truth_row: SpreadImpactCellTruth,
    time: int,
    effort: float,
    latent_abundance: float,
) -> bool:
    if regime.perfect_observability:
        if truth_row.prey_extirpation_time is None:
            return True
        return time < truth_row.prey_extirpation_time
    half_saturation = 38.0
    probability = (
        regime.detection_scale
        * effort
        * max(latent_abundance, 0.0)
        / (half_saturation + max(latent_abundance, 0.0))
    )
    if truth_row.prey_extirpation_time is not None and time >= truth_row.prey_extirpation_time:
        probability *= 0.28
    probability = clamp(probability, 0.0, 0.96)
    return (
        stable_unit(
            config.deterministic_seed + 59,
            regime.regime_id,
            truth_row.landscape_cell.cell_id,
            time,
        )
        < probability
    )


def observed_count_for(
    config: SynthMediumObservationDesignConfig,
    regime: ObservationRegime,
    truth_row: SpreadImpactCellTruth,
    time: int,
    effort: float,
    latent_abundance: float,
    detected: bool,
) -> int:
    if not detected:
        return 0
    if regime.perfect_observability:
        return max(1, round(latent_abundance / 10.0))
    texture = stable_unit(
        config.deterministic_seed + 83,
        regime.regime_id,
        truth_row.landscape_cell.cell_id,
        time,
    )
    expected = effort * (0.18 + 0.075 * max(latent_abundance, 0.0))
    return max(1, round(expected * (0.65 + 0.70 * texture)))


def build_cell_observation_summary_rows(
    regime: ObservationRegime,
    passable_truth: tuple[SpreadImpactCellTruth, ...],
    observation_rows: list[CsvRow],
) -> list[CsvRow]:
    observations_by_cell: dict[int, list[CsvRow]] = defaultdict(list)
    for row in observation_rows:
        observations_by_cell[csv_int(row["cell_id"])].append(row)
    summaries: list[CsvRow] = []
    truth_by_cell = {row.landscape_cell.cell_id: row for row in passable_truth}
    for cell_id in sorted(truth_by_cell):
        truth_row = truth_by_cell[cell_id]
        cell_observations = sorted(
            observations_by_cell.get(cell_id, []),
            key=lambda value: csv_int(value["time"]),
        )
        times = [csv_int(row["time"]) for row in cell_observations]
        detected_times = [
            csv_int(row["time"]) for row in cell_observations if csv_bool(row["detected"])
        ]
        extirpation_time = truth_row.prey_extirpation_time
        pre_rows = [
            row
            for row in cell_observations
            if extirpation_time is None or csv_int(row["time"]) < extirpation_time
        ]
        post_rows = [
            row
            for row in cell_observations
            if extirpation_time is not None and csv_int(row["time"]) >= extirpation_time
        ]
        pre_detection_count = sum(csv_bool(row["detected"]) for row in pre_rows)
        post_non_detection_rows = [row for row in post_rows if not csv_bool(row["detected"])]
        if regime.perfect_observability:
            observed_response_change = extirpation_time is not None
        else:
            observed_response_change = bool(
                extirpation_time is not None and pre_detection_count > 0 and post_non_detection_rows
            )
        observed_response_time = (
            min(csv_int(row["time"]) for row in post_non_detection_rows)
            if observed_response_change and post_non_detection_rows
            else (
                round(extirpation_time)
                if regime.perfect_observability and extirpation_time is not None
                else None
            )
        )
        final_status = final_observed_status(cell_observations, extirpation_time)
        cell = truth_row.landscape_cell
        summaries.append(
            {
                "regime_id": regime.regime_id,
                "cell_id": cell.cell_id,
                "row": cell.row,
                "col": cell.col,
                "habitat_class": cell.habitat_class,
                "row_band": cell.row_band,
                "col_band": cell.col_band,
                "survey_count": len(cell_observations),
                "detection_count": len(detected_times),
                "first_survey_time": min(times) if times else None,
                "last_survey_time": max(times) if times else None,
                "first_detection_time": min(detected_times) if detected_times else None,
                "last_detection_time": max(detected_times) if detected_times else None,
                "pre_impact_survey_count": len(pre_rows),
                "pre_impact_detection_count": pre_detection_count,
                "post_impact_survey_count": len(post_rows),
                "post_impact_non_detection_count": len(post_non_detection_rows),
                "max_gap_between_surveys": max_gap(times),
                "observed_response_change": observed_response_change,
                "observed_response_time": observed_response_time,
                "final_observed_status": final_status,
            }
        )
    return summaries


def final_observed_status(
    observations: list[CsvRow],
    extirpation_time: float | None,
) -> str:
    if not observations:
        return "never_surveyed"
    late_rows = sorted(observations, key=lambda value: csv_int(value["time"]))[-2:]
    if any(csv_bool(row["detected"]) for row in late_rows):
        return "late_detection"
    if extirpation_time is not None and any(
        csv_int(row["time"]) >= extirpation_time for row in late_rows
    ):
        return "late_non_detection_after_extirpation"
    return "late_non_detection_pre_or_unknown"


def build_truth_observation_bridge_rows(
    passable_truth: tuple[SpreadImpactCellTruth, ...],
    summaries: list[CsvRow],
) -> list[CsvRow]:
    truth_by_cell = {row.landscape_cell.cell_id: row for row in passable_truth}
    bridge_rows: list[CsvRow] = []
    for summary in summaries:
        truth_row = truth_by_cell[csv_int(summary["cell_id"])]
        true_extirpated = truth_row.prey_extirpation_time is not None
        observed_response_change = csv_bool(summary["observed_response_change"])
        cell = truth_row.landscape_cell
        bridge_rows.append(
            {
                "regime_id": summary["regime_id"],
                "cell_id": cell.cell_id,
                "row": cell.row,
                "col": cell.col,
                "habitat_class": cell.habitat_class,
                "row_band": cell.row_band,
                "col_band": cell.col_band,
                "predator_arrival_time": truth_row.predator_arrival_time,
                "prey_impact_time": truth_row.prey_impact_time,
                "prey_extirpation_time": truth_row.prey_extirpation_time,
                "true_extirpated_by_end": true_extirpated,
                "survey_count": summary["survey_count"],
                "detection_count": summary["detection_count"],
                "post_impact_survey_count": summary["post_impact_survey_count"],
                "post_impact_non_detection_count": summary["post_impact_non_detection_count"],
                "observed_response_change": observed_response_change,
                "observed_response_time": summary["observed_response_time"],
                "false_negative": true_extirpated and not observed_response_change,
            }
        )
    return bridge_rows


def build_regime_summary_rows(
    regimes: tuple[ObservationRegime, ...],
    passable_truth: tuple[SpreadImpactCellTruth, ...],
    survey_rows: tuple[CsvRow, ...],
    observation_rows: tuple[CsvRow, ...],
    cell_summary_rows: tuple[CsvRow, ...],
) -> tuple[CsvRow, ...]:
    rows: list[CsvRow] = []
    true_extirpated_count = sum(row.prey_extirpation_time is not None for row in passable_truth)
    for regime in regimes:
        regime_surveys = [row for row in survey_rows if row["regime_id"] == regime.regime_id]
        regime_observations = [
            row for row in observation_rows if row["regime_id"] == regime.regime_id
        ]
        regime_cells = [row for row in cell_summary_rows if row["regime_id"] == regime.regime_id]
        surveyed_cells = [row for row in regime_cells if csv_int(row["survey_count"]) > 0]
        observed_response_cells = [
            row for row in regime_cells if csv_bool(row["observed_response_change"])
        ]
        false_negative_count = true_extirpated_count - len(observed_response_cells)
        post_impact_support_cells = [
            row for row in regime_cells if csv_int(row["post_impact_survey_count"]) > 0
        ]
        response_times = [
            csv_float(row["observed_response_time"])
            for row in observed_response_cells
            if row["observed_response_time"] is not None
        ]
        detections = [row for row in regime_observations if csv_bool(row["detected"])]
        efforts = [csv_float(row["effort"]) for row in regime_surveys]
        habitat_classes = {
            row["habitat_class"] for row in regime_surveys if row["regime_id"] == regime.regime_id
        }
        col_bands = {
            row["col_band"] for row in regime_surveys if row["regime_id"] == regime.regime_id
        }
        rows.append(
            {
                "regime_id": regime.regime_id,
                "regime_role": regime.regime_role,
                "selected_default": regime.selected_default,
                "is_benchmark_only": regime.is_benchmark_only,
                "survey_time_count": len(regime.survey_times),
                "survey_record_count": len(regime_surveys),
                "observation_record_count": len(regime_observations),
                "surveyed_passable_count": len(surveyed_cells),
                "surveyed_passable_fraction": safe_fraction(
                    len(surveyed_cells), len(passable_truth)
                ),
                "mean_effort": mean_not_none(efforts),
                "detection_count": len(detections),
                "detection_rate": safe_fraction(len(detections), len(regime_observations)),
                "true_extirpated_count": true_extirpated_count,
                "observed_response_change_count": len(observed_response_cells),
                "false_negative_count": false_negative_count,
                "false_negative_fraction": safe_fraction(
                    false_negative_count, true_extirpated_count
                ),
                "post_impact_support_count": len(post_impact_support_cells),
                "post_impact_support_fraction": safe_fraction(
                    len(post_impact_support_cells), true_extirpated_count
                ),
                "detected_response_time_min": min(response_times) if response_times else None,
                "detected_response_time_max": max(response_times) if response_times else None,
                "detected_response_time_range": round_float(
                    max(response_times) - min(response_times)
                )
                if response_times
                else 0.0,
                "habitat_class_count_with_records": len(habitat_classes),
                "col_band_count_with_records": len(col_bands),
                "regime_recommendation": regime_recommendation(
                    regime,
                    len(surveyed_cells),
                    len(passable_truth),
                    false_negative_count,
                    true_extirpated_count,
                    len(post_impact_support_cells),
                    response_times,
                    len(habitat_classes),
                    len(col_bands),
                ),
            }
        )
    return tuple(rows)


def regime_recommendation(
    regime: ObservationRegime,
    surveyed_count: int,
    passable_count: int,
    false_negative_count: int,
    true_extirpated_count: int,
    post_impact_support_count: int,
    response_times: list[float],
    habitat_count: int,
    col_band_count: int,
) -> str:
    if regime.perfect_observability:
        return "benchmark_only"
    if regime.regime_role == "stress":
        return "low_information_stress"
    if (
        safe_fraction(surveyed_count, passable_count) >= 0.70
        and 0 < false_negative_count < true_extirpated_count
        and safe_fraction(post_impact_support_count, true_extirpated_count) >= 0.40
        and response_times
        and max(response_times) - min(response_times) >= 60.0
        and habitat_count >= 5
        and col_band_count >= 3
    ):
        return "ready_for_review"
    return "needs_redesign_before_review"


def build_false_negative_summary_rows(
    regimes: tuple[ObservationRegime, ...],
    cell_summary_rows: tuple[CsvRow, ...],
    passable_truth: tuple[SpreadImpactCellTruth, ...],
) -> tuple[CsvRow, ...]:
    truth_by_cell = {row.landscape_cell.cell_id: row for row in passable_truth}
    rows: list[CsvRow] = []
    for regime in regimes:
        summaries = [row for row in cell_summary_rows if row["regime_id"] == regime.regime_id]
        groups: list[tuple[str, list[CsvRow]]] = [("all_passable", summaries)]
        for habitat_class in sorted({str(row["habitat_class"]) for row in summaries}):
            groups.append(
                (
                    f"habitat_class:{habitat_class}",
                    [row for row in summaries if row["habitat_class"] == habitat_class],
                )
            )
        for col_band in sorted({str(row["col_band"]) for row in summaries}):
            groups.append(
                (
                    f"col_band:{col_band}",
                    [row for row in summaries if row["col_band"] == col_band],
                )
            )
        for group_name, group_rows in groups:
            true_extirpated = [
                row
                for row in group_rows
                if truth_by_cell[csv_int(row["cell_id"])].prey_extirpation_time is not None
            ]
            observed = [row for row in true_extirpated if csv_bool(row["observed_response_change"])]
            false_negative_count = len(true_extirpated) - len(observed)
            rows.append(
                {
                    "regime_id": regime.regime_id,
                    "summary_group": group_name,
                    "true_extirpated_count": len(true_extirpated),
                    "observed_response_change_count": len(observed),
                    "false_negative_count": false_negative_count,
                    "false_negative_fraction": safe_fraction(
                        false_negative_count, len(true_extirpated)
                    ),
                }
            )
    return tuple(rows)


def build_coverage_gap_summary_rows(
    regimes: tuple[ObservationRegime, ...],
    cell_summary_rows: tuple[CsvRow, ...],
    passable_truth: tuple[SpreadImpactCellTruth, ...],
) -> tuple[CsvRow, ...]:
    truth_by_cell = {row.landscape_cell.cell_id: row for row in passable_truth}
    rows: list[CsvRow] = []
    for regime in regimes:
        summaries = [row for row in cell_summary_rows if row["regime_id"] == regime.regime_id]
        groups: list[tuple[str, list[CsvRow]]] = [("all_passable", summaries)]
        for habitat_class in sorted({str(row["habitat_class"]) for row in summaries}):
            groups.append(
                (
                    f"habitat_class:{habitat_class}",
                    [row for row in summaries if row["habitat_class"] == habitat_class],
                )
            )
        for group_name, group_rows in groups:
            surveyed = [row for row in group_rows if csv_int(row["survey_count"]) > 0]
            true_extirpated = [
                row
                for row in group_rows
                if truth_by_cell[csv_int(row["cell_id"])].prey_extirpation_time is not None
            ]
            no_pre = [
                row for row in true_extirpated if csv_int(row["pre_impact_survey_count"]) == 0
            ]
            no_post = [
                row for row in true_extirpated if csv_int(row["post_impact_survey_count"]) == 0
            ]
            survey_counts = [csv_int(row["survey_count"]) for row in group_rows]
            gaps = [csv_float(row["max_gap_between_surveys"]) for row in group_rows]
            rows.append(
                {
                    "regime_id": regime.regime_id,
                    "summary_group": group_name,
                    "passable_cell_count": len(group_rows),
                    "surveyed_cell_count": len(surveyed),
                    "surveyed_cell_fraction": safe_fraction(len(surveyed), len(group_rows)),
                    "no_survey_count": len(group_rows) - len(surveyed),
                    "no_pre_impact_support_count": len(no_pre),
                    "no_post_impact_support_count": len(no_post),
                    "mean_survey_count": mean(survey_counts) if survey_counts else None,
                    "mean_max_survey_gap": mean(gaps) if gaps else None,
                }
            )
    return tuple(rows)


def build_effort_by_habitat_region_summary_rows(
    regimes: tuple[ObservationRegime, ...],
    passable_truth: tuple[SpreadImpactCellTruth, ...],
    survey_rows: tuple[CsvRow, ...],
    observation_rows: tuple[CsvRow, ...],
    cell_summary_rows: tuple[CsvRow, ...],
) -> tuple[CsvRow, ...]:
    rows: list[CsvRow] = []
    truth_by_cell = {row.landscape_cell.cell_id: row for row in passable_truth}
    all_groups = sorted(
        {
            (truth.landscape_cell.habitat_class, truth.landscape_cell.col_band)
            for truth in passable_truth
        }
    )
    for regime in regimes:
        for habitat_class, col_band in all_groups:
            group_truth = [
                truth
                for truth in passable_truth
                if truth.landscape_cell.habitat_class == habitat_class
                and truth.landscape_cell.col_band == col_band
            ]
            group_ids = {truth.landscape_cell.cell_id for truth in group_truth}
            group_surveys = [
                row
                for row in survey_rows
                if row["regime_id"] == regime.regime_id and csv_int(row["cell_id"]) in group_ids
            ]
            group_observations = [
                row
                for row in observation_rows
                if row["regime_id"] == regime.regime_id and csv_int(row["cell_id"]) in group_ids
            ]
            group_summaries = [
                row
                for row in cell_summary_rows
                if row["regime_id"] == regime.regime_id and csv_int(row["cell_id"]) in group_ids
            ]
            efforts = [csv_float(row["effort"]) for row in group_surveys]
            detections = [row for row in group_observations if csv_bool(row["detected"])]
            true_extirpated = [
                row
                for row in group_summaries
                if truth_by_cell[csv_int(row["cell_id"])].prey_extirpation_time is not None
            ]
            post_support = [
                row for row in true_extirpated if csv_int(row["post_impact_survey_count"]) > 0
            ]
            false_negative = [
                row for row in true_extirpated if not csv_bool(row["observed_response_change"])
            ]
            rows.append(
                {
                    "regime_id": regime.regime_id,
                    "habitat_class": habitat_class,
                    "col_band": col_band,
                    "cell_count": len(group_truth),
                    "survey_record_count": len(group_surveys),
                    "mean_effort": mean_not_none(efforts),
                    "detection_rate": safe_fraction(len(detections), len(group_observations)),
                    "post_impact_support_fraction": safe_fraction(
                        len(post_support), len(true_extirpated)
                    ),
                    "false_negative_count": len(false_negative),
                }
            )
    return tuple(rows)


def build_recoverability_signal_summary_rows(
    config: SynthMediumObservationDesignConfig,
    regime_rows: tuple[CsvRow, ...],
) -> tuple[CsvRow, ...]:
    regime_map = {row["regime_id"]: row for row in regime_rows}
    full = regime_map["truth_reference_full_observability"]
    default = regime_map["structured_response_observed_default"]
    sparse = regime_map["sparse_response_observed_stress"]
    specs = (
        (
            full["regime_id"],
            "benchmark_complete_coverage",
            full["surveyed_passable_fraction"],
            "== 1.0",
            csv_float(full["surveyed_passable_fraction"]) == 1.0,
            "Full-observability reference covers all passable cells.",
        ),
        (
            full["regime_id"],
            "benchmark_no_false_negatives",
            full["false_negative_count"],
            "== 0",
            csv_int(full["false_negative_count"]) == 0,
            "Full-observability reference has no designed response false negatives.",
        ),
        (
            default["regime_id"],
            "default_broad_uneven_coverage",
            default["surveyed_passable_fraction"],
            f">= {config.min_default_surveyed_fraction} and < 1.0",
            config.min_default_surveyed_fraction
            <= csv_float(default["surveyed_passable_fraction"])
            < 1.0,
            "Default regime covers broad but incomplete passable land.",
        ),
        (
            default["regime_id"],
            "default_false_negatives_nonzero",
            default["false_negative_count"],
            f">= {config.min_default_false_negative_count}",
            csv_int(default["false_negative_count"]) >= config.min_default_false_negative_count,
            "Default regime contains imperfect-detection false negatives.",
        ),
        (
            default["regime_id"],
            "default_post_impact_support",
            default["post_impact_support_fraction"],
            f">= {config.min_default_post_impact_support_fraction}",
            csv_float(default["post_impact_support_fraction"])
            >= config.min_default_post_impact_support_fraction,
            "Default regime has enough post-impact support for later review.",
        ),
        (
            default["regime_id"],
            "default_timing_signal",
            default["detected_response_time_range"],
            f">= {config.min_default_detected_response_time_range}",
            csv_float(default["detected_response_time_range"])
            >= config.min_default_detected_response_time_range,
            "Detected response changes are distributed through time.",
        ),
        (
            default["regime_id"],
            "default_spatial_signal",
            (
                f"{default['habitat_class_count_with_records']} habitat classes; "
                f"{default['col_band_count_with_records']} column bands"
            ),
            (
                f">= {config.min_default_habitat_classes_with_records} habitat classes "
                f"and >= {config.min_default_col_bands_with_records} column bands"
            ),
            csv_int(default["habitat_class_count_with_records"])
            >= config.min_default_habitat_classes_with_records
            and csv_int(default["col_band_count_with_records"])
            >= config.min_default_col_bands_with_records,
            "Default regime retains broad spatial observation signal.",
        ),
        (
            sparse["regime_id"],
            "stress_lower_information",
            (
                f"{sparse['observation_record_count']} records; "
                f"{sparse['false_negative_count']} false negatives"
            ),
            "fewer records and more false negatives than default",
            csv_int(sparse["observation_record_count"])
            < csv_int(default["observation_record_count"])
            and csv_int(sparse["false_negative_count"]) > csv_int(default["false_negative_count"]),
            "Sparse stress regime is lower-information than default.",
        ),
    )
    return tuple(
        {
            "regime_id": regime_id,
            "proxy_id": proxy_id,
            "observed_value": observed_value,
            "threshold": threshold,
            "passes": passes,
            "interpretation": interpretation,
        }
        for regime_id, proxy_id, observed_value, threshold, passes, interpretation in specs
    )


def verify_observation_design_result(
    config: SynthMediumObservationDesignConfig,
    truth: SynthMediumSpreadImpactResult,
    regimes: tuple[ObservationRegime, ...],
    survey_rows: tuple[CsvRow, ...],
    observation_rows: tuple[CsvRow, ...],
    cell_summary_rows: tuple[CsvRow, ...],
    bridge_rows: tuple[CsvRow, ...],
    regime_rows: tuple[CsvRow, ...],
    signal_rows: tuple[CsvRow, ...],
    visual_svgs: dict[str, str],
) -> tuple[ObservationDesignCheck, ...]:
    regime_map = {row["regime_id"]: row for row in regime_rows}
    full = regime_map["truth_reference_full_observability"]
    default = regime_map["structured_response_observed_default"]
    sparse = regime_map["sparse_response_observed_stress"]
    signal_map = {(row["regime_id"], row["proxy_id"]): row for row in signal_rows}
    observation_ids = {row["survey_id"] for row in observation_rows}
    survey_ids = {row["survey_id"] for row in survey_rows}
    water_survey_count = sum(row["passability"] != "passable" for row in survey_rows)
    default_signal_passes = all(
        csv_bool(signal_map[("structured_response_observed_default", proxy_id)]["passes"])
        for proxy_id in (
            "default_broad_uneven_coverage",
            "default_false_negatives_nonzero",
            "default_post_impact_support",
            "default_timing_signal",
            "default_spatial_signal",
        )
    )
    return (
        ObservationDesignCheck(
            name="artifact_contract",
            passed=set(visual_svgs) == set(SYNTH_MEDIUM_OBSERVATION_DESIGN_VISUAL_FILES)
            and all(
                svg.lstrip().startswith("<svg") and len(svg) > 1000 for svg in visual_svgs.values()
            ),
            details={
                "output_file_count": len(SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_FILES),
                "visual_file_count": len(visual_svgs),
            },
        ),
        ObservationDesignCheck(
            name="truth_source_reconciliation",
            passed=truth_source_summary(truth) == TRUTH_EXPECTATIONS,
            details=truth_source_summary(truth),
        ),
        ObservationDesignCheck(
            name="water_has_no_surveys",
            passed=water_survey_count == 0,
            details={"water_survey_count": water_survey_count},
        ),
        ObservationDesignCheck(
            name="full_observability_benchmark",
            passed=csv_float(full["surveyed_passable_fraction"]) == 1.0
            and csv_int(full["false_negative_count"]) == 0
            and full["is_benchmark_only"] is True,
            details={
                "surveyed_passable_fraction": full["surveyed_passable_fraction"],
                "false_negative_count": full["false_negative_count"],
            },
        ),
        ObservationDesignCheck(
            name="default_broad_uneven_coverage",
            passed=csv_bool(
                signal_map[
                    (
                        "structured_response_observed_default",
                        "default_broad_uneven_coverage",
                    )
                ]["passes"]
            )
            and csv_float(default["surveyed_passable_fraction"]) < 1.0,
            details={"surveyed_passable_fraction": default["surveyed_passable_fraction"]},
        ),
        ObservationDesignCheck(
            name="default_imperfect_detection_false_negatives",
            passed=csv_bool(
                signal_map[
                    (
                        "structured_response_observed_default",
                        "default_false_negatives_nonzero",
                    )
                ]["passes"]
            )
            and 0.0 < csv_float(default["detection_rate"]) < 1.0,
            details={
                "false_negative_count": default["false_negative_count"],
                "detection_rate": default["detection_rate"],
            },
        ),
        ObservationDesignCheck(
            name="default_post_impact_support",
            passed=csv_bool(
                signal_map[
                    (
                        "structured_response_observed_default",
                        "default_post_impact_support",
                    )
                ]["passes"]
            ),
            details={"post_impact_support_fraction": default["post_impact_support_fraction"]},
        ),
        ObservationDesignCheck(
            name="default_timing_signal",
            passed=csv_bool(
                signal_map[("structured_response_observed_default", "default_timing_signal")][
                    "passes"
                ]
            ),
            details={"detected_response_time_range": default["detected_response_time_range"]},
        ),
        ObservationDesignCheck(
            name="default_spatial_signal",
            passed=default_signal_passes,
            details={
                "habitat_class_count_with_records": default["habitat_class_count_with_records"],
                "col_band_count_with_records": default["col_band_count_with_records"],
            },
        ),
        ObservationDesignCheck(
            name="sparse_stress_lower_information",
            passed=csv_bool(
                signal_map[("sparse_response_observed_stress", "stress_lower_information")][
                    "passes"
                ]
            )
            and csv_float(sparse["post_impact_support_fraction"])
            < csv_float(default["post_impact_support_fraction"]),
            details={
                "default_observation_record_count": default["observation_record_count"],
                "sparse_observation_record_count": sparse["observation_record_count"],
                "default_false_negative_count": default["false_negative_count"],
                "sparse_false_negative_count": sparse["false_negative_count"],
            },
        ),
        ObservationDesignCheck(
            name="record_summary_reconciliation",
            passed=len(survey_rows) == len(observation_rows)
            and survey_ids == observation_ids
            and len(cell_summary_rows) == 5225 * len(regimes)
            and len(bridge_rows) == len(cell_summary_rows),
            details={
                "survey_row_count": len(survey_rows),
                "observation_row_count": len(observation_rows),
                "cell_summary_row_count": len(cell_summary_rows),
                "bridge_row_count": len(bridge_rows),
            },
        ),
    )


def build_observation_design_visual_svgs(
    passable_truth: tuple[SpreadImpactCellTruth, ...],
    cell_summary_rows: tuple[CsvRow, ...],
    regime_summary_rows: tuple[CsvRow, ...],
) -> dict[str, str]:
    default_rows = {
        csv_int(row["cell_id"]): row
        for row in cell_summary_rows
        if row["regime_id"] == "structured_response_observed_default"
    }
    return {
        "survey_effort_surface_default.svg": render_truth_grid_svg(
            passable_truth,
            lambda row: effort_fill(default_rows.get(row.landscape_cell.cell_id)),
            "Default survey effort surface",
            "legend-survey-effort",
            SURVEY_EFFORT_LEGEND,
        ),
        "observed_final_response_default.svg": render_truth_grid_svg(
            passable_truth,
            lambda row: final_status_fill(default_rows.get(row.landscape_cell.cell_id)),
            "Default final observed response status",
            "legend-final-status",
            FINAL_STATUS_LEGEND,
        ),
        "truth_observed_mismatch_default.svg": render_truth_grid_svg(
            passable_truth,
            lambda row: mismatch_fill(row, default_rows.get(row.landscape_cell.cell_id)),
            "Default truth-observed mismatch",
            "legend-mismatch",
            MISMATCH_LEGEND,
        ),
        "post_impact_support_default.svg": render_truth_grid_svg(
            passable_truth,
            lambda row: post_impact_support_fill(default_rows.get(row.landscape_cell.cell_id)),
            "Default post-impact support",
            "legend-post-impact",
            POST_IMPACT_LEGEND,
        ),
        "regime_comparison_montage.svg": render_regime_comparison_montage_svg(regime_summary_rows),
        "review_montage.svg": render_review_montage_svg(passable_truth, default_rows),
    }


def render_truth_grid_svg(
    rows: tuple[SpreadImpactCellTruth, ...],
    fill_for: Callable[[SpreadImpactCellTruth], str],
    title: str,
    legend_id: str,
    legend_items: tuple[LegendItem, ...],
) -> str:
    width = 860
    height = 72 * 7 + 64
    lines = svg_header(width, height, title)
    lines.append(f'<text x="10" y="24" font-size="18" font-family="monospace">{title}</text>')
    for row in rows:
        cell = row.landscape_cell
        x = cell.col * 7
        y = cell.row * 7 + 36
        lines.append(
            f'<rect x="{x}" y="{y}" width="7" height="7" fill="{fill_for(row)}" stroke="none" />'
        )
    append_legend(lines, legend_id, 615, 50, legend_items)
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_regime_comparison_montage_svg(regime_rows: tuple[CsvRow, ...]) -> str:
    width = 1440
    height = 360
    lines = svg_header(width, height, "Regime comparison montage")
    lines.append(
        '<text x="24" y="32" font-size="22" font-family="monospace">Regime comparison table</text>'
    )
    lines.append(
        '<text x="24" y="56" font-size="12" font-family="monospace" fill="#475569">'
        "Fractions use passable cells or true extirpations as defined in regime_summary.csv."
        "</text>"
    )
    metrics = (
        ("Coverage", "surveyed_passable_fraction", "#2563eb"),
        ("Post-impact support", "post_impact_support_fraction", "#16a34a"),
        ("False negatives", "false_negative_fraction", "#dc2626"),
        ("Detection rate", "detection_rate", "#7c3aed"),
    )
    metric_x = 420
    metric_width = 235
    bar_width = 132
    table_width = 1380
    lines.append(f'<rect x="20" y="76" width="{table_width}" height="32" fill="#f8fafc" />')
    lines.append(
        '<text x="32" y="98" font-size="13" font-family="monospace" '
        'font-weight="bold">Regime</text>'
    )
    for m_index, (label, _, _) in enumerate(metrics):
        x = metric_x + m_index * metric_width
        lines.append(
            f'<text x="{x}" y="98" font-size="13" font-family="monospace" '
            f'font-weight="bold">{label}</text>'
        )
    for r_index, row in enumerate(regime_rows):
        y = 142 + r_index * 70
        row_fill = "#ffffff" if r_index % 2 == 0 else "#f8fafc"
        lines.append(
            f'<rect x="20" y="{y - 26}" width="{table_width}" height="56" fill="{row_fill}" />'
        )
        lines.append(
            f'<text x="32" y="{y - 4}" font-size="13" font-family="monospace">'
            f"{row['regime_id']}</text>"
        )
        lines.append(
            f'<text x="32" y="{y + 16}" font-size="11" font-family="monospace" '
            f'fill="#475569">records {row["observation_record_count"]}; '
            f"FN {row['false_negative_count']}</text>"
        )
        for m_index, (_, metric, color) in enumerate(metrics):
            value = csv_float(row[metric])
            x = metric_x + m_index * metric_width
            filled_width = int(value * bar_width)
            lines.append(
                f'<rect x="{x}" y="{y - 18}" width="{bar_width}" height="14" fill="#e5e7eb" />'
            )
            lines.append(
                f'<rect x="{x}" y="{y - 18}" width="{filled_width}" height="14" fill="{color}" />'
            )
            lines.append(
                f'<text x="{x + bar_width + 12}" y="{y - 6}" font-size="12" '
                f'font-family="monospace">{value:.2f}</text>'
            )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_review_montage_svg(
    rows: tuple[SpreadImpactCellTruth, ...],
    default_rows: dict[int, CsvRow],
) -> str:
    width = 1180
    height = 1360
    lines = svg_header(width, height, "Observation design review montage")
    lines.append(
        '<text x="20" y="30" font-size="22" font-family="monospace">'
        "Observation design review montage</text>"
    )
    map_cell_size = 6
    map_height = 72 * map_cell_size
    panel_top_start = 50
    panel_column_spacing = 580
    panel_row_spacing = 660
    panel_box_width = 560
    legend_columns = 2
    legend_column_width = 260
    panels: tuple[
        tuple[
            str,
            Callable[[SpreadImpactCellTruth], str],
            str,
            tuple[LegendItem, ...],
        ],
        ...,
    ] = (
        (
            "Survey effort",
            lambda row: effort_fill(default_rows.get(row.landscape_cell.cell_id)),
            "legend-survey-effort",
            SURVEY_EFFORT_LEGEND,
        ),
        (
            "Observed final status",
            lambda row: final_status_fill(default_rows.get(row.landscape_cell.cell_id)),
            "legend-final-status",
            FINAL_STATUS_LEGEND,
        ),
        (
            "Truth/observed mismatch",
            lambda row: mismatch_fill(row, default_rows.get(row.landscape_cell.cell_id)),
            "legend-mismatch",
            MISMATCH_LEGEND,
        ),
        (
            "Post-impact support",
            lambda row: post_impact_support_fill(default_rows.get(row.landscape_cell.cell_id)),
            "legend-post-impact",
            POST_IMPACT_LEGEND,
        ),
    )
    for index, (title, fill_for, legend_id, legend_items) in enumerate(panels):
        column = index % 2
        row_index = index // 2
        origin_x = 20 + column * panel_column_spacing
        panel_top = panel_top_start + row_index * panel_row_spacing
        title_y = panel_top + 26
        map_top = panel_top + 48
        map_bottom = map_top + map_height
        legend_top = map_bottom + 30
        legend_bottom = legend_bottom_y(legend_top, legend_items, legend_columns)
        panel_bottom = legend_bottom + 20
        panel_id = legend_id.removeprefix("legend-")
        lines.append(
            f'<g id="panel-{panel_id}" data-column="{column}" data-row="{row_index}" '
            f'data-title-y="{title_y}" data-map-top="{map_top}" '
            f'data-map-bottom="{map_bottom}" data-legend-top="{legend_top}" '
            f'data-legend-bottom="{legend_bottom}" data-panel-bottom="{panel_bottom}">'
        )
        lines.append(
            f'<rect x="{origin_x - 8}" y="{panel_top}" width="{panel_box_width}" '
            f'height="{panel_bottom - panel_top}" fill="#ffffff" stroke="#cbd5e1" />'
        )
        lines.append(
            f'<text x="{origin_x}" y="{title_y}" font-size="16" '
            f'font-family="monospace">{title}</text>'
        )
        for row in rows:
            cell = row.landscape_cell
            x = origin_x + cell.col * map_cell_size
            y = map_top + cell.row * map_cell_size
            lines.append(
                f'<rect x="{x}" y="{y}" width="{map_cell_size}" height="{map_cell_size}" '
                f'fill="{fill_for(row)}" stroke="none" />'
            )
        append_legend(
            lines,
            legend_id,
            origin_x,
            legend_top,
            legend_items,
            columns=legend_columns,
            column_width=legend_column_width,
        )
        lines.append("</g>")
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def legend_bottom_y(y: int, items: tuple[LegendItem, ...], columns: int) -> int:
    row_count = (len(items) + columns - 1) // columns
    return y + 18 + max(row_count - 1, 0) * 20 + 12


def append_legend(
    lines: list[str],
    legend_id: str,
    x: int,
    y: int,
    items: tuple[LegendItem, ...],
    *,
    columns: int = 1,
    column_width: int = 185,
) -> None:
    lines.append(f'<g id="{legend_id}">')
    lines.append(
        f'<text x="{x}" y="{y}" font-size="13" font-family="monospace" '
        'font-weight="bold">Legend</text>'
    )
    for index, (color, label) in enumerate(items):
        column = index % columns
        row = index // columns
        item_x = x + column * column_width
        item_y = y + 18 + row * 20
        stroke = "#64748b" if color == "#ffffff" else "none"
        lines.append(
            f'<rect x="{item_x}" y="{item_y - 11}" width="12" height="12" '
            f'fill="{color}" stroke="{stroke}" />'
        )
        lines.append(
            f'<text x="{item_x + 18}" y="{item_y}" font-size="11" '
            f'font-family="monospace">{label}</text>'
        )
    lines.append("</g>")


def effort_fill(row: CsvRow | None) -> str:
    if row is None:
        return "#e5e7eb"
    survey_count = csv_int(row["survey_count"])
    if survey_count == 0:
        return "#f3f4f6"
    return interpolate_hex("#dbeafe", "#1d4ed8", min(survey_count / 8.0, 1.0))


def final_status_fill(row: CsvRow | None) -> str:
    if row is None:
        return "#e5e7eb"
    status = str(row["final_observed_status"])
    if status == "late_detection":
        return "#15803d"
    if status == "late_non_detection_after_extirpation":
        return "#7c3aed"
    if status == "late_non_detection_pre_or_unknown":
        return "#f59e0b"
    return "#d1d5db"


def mismatch_fill(truth_row: SpreadImpactCellTruth, row: CsvRow | None) -> str:
    if row is None:
        return "#e5e7eb"
    true_extirpated = truth_row.prey_extirpation_time is not None
    observed_change = csv_bool(row["observed_response_change"])
    if true_extirpated and observed_change:
        return "#2563eb"
    if true_extirpated and not observed_change:
        return "#dc2626"
    if not true_extirpated and observed_change:
        return "#ea580c"
    return "#94a3b8"


def post_impact_support_fill(row: CsvRow | None) -> str:
    if row is None:
        return "#e5e7eb"
    count = csv_int(row["post_impact_survey_count"])
    if count == 0:
        return "#fee2e2"
    return interpolate_hex("#dcfce7", "#166534", min(count / 5.0, 1.0))


def render_observation_design_report(result: SynthMediumObservationDesignResult) -> str:
    visual_lines = "\n".join(
        f"- [`visuals/{name}`](visuals/{name})"
        for name in SYNTH_MEDIUM_OBSERVATION_DESIGN_VISUAL_FILES
    )
    regime_lines = "\n".join(
        f"- `{row['regime_id']}`: records `{row['observation_record_count']}`, "
        f"coverage `{row['surveyed_passable_fraction']}`, false negatives "
        f"`{row['false_negative_count']}`, post-impact support "
        f"`{row['post_impact_support_fraction']}`"
        for row in result.regime_summary_rows
    )
    gate_lines = "\n".join(
        f"- `{check.name}`: `{'passed' if check.passed else 'failed'}`"
        for check in result.verification_checks
    )
    summary = result.summary_dict()
    return f"""# Synth-Medium Observation-Design Review Pack

## Boundary

This bundle is synthetic-only and observation-design-review-only. It uses the
accepted Goal 018 spread-impact truth without changing the Goal 017 landscape
or Goal 018 selected default. It emits response-only prey observations and does
not reconstruct extirpation times, fit parameters, run ABC/POM/likelihood/MCMC
or posterior workflows, analyse real data, or start a follow-on goal.

## Selected Default

- Regime: `{result.config.selected_default_regime_id}`
- Recommendation: `{result.recommendation_class}`
- Default survey records: `{summary["default_survey_record_count"]}`
- Default false negatives: `{summary["default_false_negative_count"]}`
- Default post-impact support fraction:
  `{summary["default_post_impact_support_fraction"]}`

## Regime Summary

{regime_lines}

## Review Gates

{gate_lines}

## Visual Review Files

{visual_lines}

## Visual Decode Keys

- `regime_comparison_montage.svg` is a regime comparison table with short
  metric labels, visible values, and separate horizontal bars for coverage,
  post-impact support, false negatives, and detection rate.
- Map SVGs include embedded legends. `Water / not passable` marks the white
  background where no response-only survey records should exist.
- Survey effort maps distinguish `No survey`, `Low effort`, and `High effort`.
- Final observed response maps distinguish `Late detection`,
  `Post-impact non-detection`, `No late support`, and `Never surveyed`.
- Truth/observed mismatch maps distinguish `Observed true extirpation`,
  `False negative`, `Unexpected observed change`, and
  `Not extirpated / uninformative`.
- Post-impact support maps distinguish `No post-impact support`,
  `Some support`, and `Strong support`.
"""


def truth_source_summary(truth: SynthMediumSpreadImpactResult) -> dict[str, object]:
    summary = truth.summary_dict()
    return {
        "selected_parameter_set_id": summary["selected_parameter_set_id"],
        "cell_count": summary["cell_count"],
        "passable_cell_count": summary["passable_cell_count"],
        "water_cell_count": summary["water_cell_count"],
        "final_colonized_passable_count": summary["final_colonized_passable_count"],
        "finite_prey_extirpation_count": summary["finite_prey_extirpation_count"],
    }


def regime_to_dict(regime: ObservationRegime) -> dict[str, object]:
    return {
        "regime_id": regime.regime_id,
        "regime_role": regime.regime_role,
        "selected_default": regime.selected_default,
        "is_benchmark_only": regime.is_benchmark_only,
        "survey_times": list(regime.survey_times),
        "frame_probability": regime.frame_probability,
        "visit_probability": regime.visit_probability,
        "effort_scale": regime.effort_scale,
        "detection_scale": regime.detection_scale,
        "post_impact_gap_strength": regime.post_impact_gap_strength,
        "perfect_observability": regime.perfect_observability,
        "rationale": regime.rationale,
    }


def regime_row(rows: tuple[CsvRow, ...], regime_id: str) -> CsvRow:
    return next(row for row in rows if row["regime_id"] == regime_id)


def stable_unit(seed: int, regime_id: str, cell_id: int, time: int) -> float:
    regime_value = sum((index + 1) * ord(char) for index, char in enumerate(regime_id))
    value = (
        seed * 1_000_003
        + regime_value * 9_176
        + cell_id * 1_103_515_245
        + time * 12_345
        + 0x9E3779B97F4A7C15
    ) & ((1 << 64) - 1)
    value ^= value >> 30
    value = (value * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    value ^= value >> 27
    value = (value * 0x94D049BB133111EB) & ((1 << 64) - 1)
    value ^= value >> 31
    return value / float(1 << 64)


def max_gap(times: list[int]) -> int:
    if len(times) < 2:
        return 120 if not times else max(times[0], 120 - times[0])
    sorted_times = sorted(times)
    gaps = [sorted_times[0], 120 - sorted_times[-1]]
    gaps.extend(right - left for left, right in pairwise(sorted_times))
    return max(gaps)


def mean_not_none(values: Iterable[float]) -> float | None:
    concrete = [float(value) for value in values]
    if not concrete:
        return None
    return mean(concrete)


def round_float(value: float) -> float:
    return round(float(value), 12)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def csv_int(value: CsvValue) -> int:
    if value is None or isinstance(value, bool):
        raise TypeError(f"expected integer-like CSV value, got {value!r}")
    return int(value)


def csv_float(value: CsvValue) -> float:
    if value is None or isinstance(value, bool):
        raise TypeError(f"expected float-like CSV value, got {value!r}")
    return float(value)


def csv_bool(value: CsvValue) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"expected boolean CSV value, got {value!r}")
    return value


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        '<rect width="100%" height="100%" fill="#ffffff" />',
    ]
