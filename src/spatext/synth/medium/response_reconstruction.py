from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
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
from .observations import (
    SynthMediumObservationDesignResult,
    build_synth_medium_observation_design_review_pack,
)
from .spread_impact import SpreadImpactCellTruth

DEFAULT_SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_DIR = Path(
    "artifacts/synth_medium_response_reconstruction_benchmark"
)
SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_FILES = (
    "response_reconstruction_config.json",
    "reconstruction_rule_definitions.csv",
    "reconstructed_cell_times.csv",
    "truth_reconstruction_bridge.csv",
    "reconstruction_error_summary.csv",
    "rule_regime_rankings.csv",
    "support_gap_summary.csv",
    "recoverability_signal_summary.csv",
    "verification.json",
    "report.md",
)
SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES = (
    "truth_response_time.svg",
    "default_primary_reconstructed_time.svg",
    "default_primary_residual_error.svg",
    "default_primary_support_gap.svg",
    "regime_rule_comparison_montage.svg",
    "review_montage.svg",
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "synth_medium_landscape_source_verified": True,
    "synth_medium_spread_impact_source_verified": True,
    "synth_medium_observation_design_source_verified": True,
    "response_reconstruction_benchmark_only": True,
    "response_only_reconstruction_rules": True,
    "full_observability_is_benchmark_only": True,
    "selected_default_is_imperfect_observation": True,
    "visual_review_required": True,
    "no_production_reconstruction_rule_adoption": True,
    "no_abc_pom_likelihood_or_posterior": True,
    "no_real_data": True,
}

REGIME_IDS = (
    "truth_reference_full_observability",
    "structured_response_observed_default",
    "sparse_response_observed_stress",
)
SELECTED_DEFAULT_REGIME_ID = "structured_response_observed_default"

SOURCE_EXPECTATIONS = {
    "landscape": {
        "cell_count": 6048,
        "passable_cell_count": 5225,
        "water_cell_count": 823,
    },
    "spread_impact": {
        "selected_parameter_set_id": "balanced_corridor_detour_v2",
        "final_colonized_passable_count": 4605,
        "finite_prey_extirpation_count": 4289,
    },
    "observation_design": {
        "selected_default_regime_id": SELECTED_DEFAULT_REGIME_ID,
        "default_survey_record_count": 21258,
        "default_false_negative_count": 2313,
    },
}

RECONSTRUCTION_RULE_COLUMNS = (
    "rule_id",
    "rule_label",
    "rule_scope",
    "min_final_absence_run",
    "time_estimator",
    "uses_hidden_truth",
    "response_observable_source_columns",
    "interpretation",
)
RECONSTRUCTED_CELL_COLUMNS = (
    "regime_id",
    "rule_id",
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
    "final_absence_start_time",
    "final_absence_survey_time_count",
    "reconstructed_finite",
    "reconstructed_response_time",
    "reconstruction_status",
    "support_class",
)
TRUTH_RECONSTRUCTION_BRIDGE_COLUMNS = (
    "regime_id",
    "rule_id",
    "cell_id",
    "row",
    "col",
    "habitat_class",
    "row_band",
    "col_band",
    "prey_extirpation_time",
    "true_extirpated_by_end",
    "reconstructed_finite",
    "reconstructed_response_time",
    "signed_error",
    "absolute_error",
    "error_class",
    "classification",
)
ERROR_SUMMARY_COLUMNS = (
    "regime_id",
    "rule_id",
    "summary_group",
    "cell_count",
    "true_extirpated_count",
    "finite_reconstructed_count",
    "true_positive_count",
    "false_positive_count",
    "false_negative_count",
    "true_negative_count",
    "finite_recall",
    "specificity",
    "precision",
    "mean_signed_error",
    "median_absolute_error",
    "p90_absolute_error",
    "large_error_count",
    "large_error_fraction",
)
RANKING_COLUMNS = (
    "regime_id",
    "rule_id",
    "rank",
    "finite_reconstructed_count",
    "true_positive_count",
    "false_positive_count",
    "false_negative_count",
    "finite_recall",
    "specificity",
    "precision",
    "median_absolute_error",
    "p90_absolute_error",
    "large_error_count",
    "large_error_fraction",
    "loss",
    "positive_control_status",
    "recommendation_class",
)
SUPPORT_GAP_COLUMNS = (
    "regime_id",
    "rule_id",
    "summary_group",
    "passable_cell_count",
    "surveyed_cell_count",
    "never_surveyed_count",
    "no_detection_history_count",
    "no_post_detection_survey_count",
    "post_detection_absence_supported_count",
    "finite_reconstructed_count",
    "mean_survey_count",
    "mean_final_absence_run",
)
RECOVERABILITY_SIGNAL_COLUMNS = (
    "regime_id",
    "proxy_id",
    "observed_value",
    "threshold",
    "passes",
    "interpretation",
)

LegendItem = tuple[str, str]

TRUTH_TIME_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#d1d5db", "No finite truth"),
    ("#dbeafe", "Early response"),
    ("#1d4ed8", "Late response"),
)
RECONSTRUCTED_TIME_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#d1d5db", "No reconstruction"),
    ("#dcfce7", "Early reconstructed"),
    ("#166534", "Late reconstructed"),
)
RESIDUAL_ERROR_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#d1d5db", "No finite comparison"),
    ("#2563eb", "Early bias"),
    ("#f8fafc", "Small error"),
    ("#dc2626", "Late bias"),
)
SUPPORT_GAP_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#d1d5db", "Never surveyed"),
    ("#f59e0b", "No detection history"),
    ("#f97316", "No final absence support"),
    ("#15803d", "Finite reconstruction support"),
)


@dataclass(frozen=True, slots=True)
class ReconstructionRule:
    rule_id: str
    rule_label: str
    min_final_absence_run: int
    time_estimator: str
    interpretation: str

    def to_csv_row(self) -> CsvRow:
        return {
            "rule_id": self.rule_id,
            "rule_label": self.rule_label,
            "rule_scope": "benchmark_only",
            "min_final_absence_run": self.min_final_absence_run,
            "time_estimator": self.time_estimator,
            "uses_hidden_truth": False,
            "response_observable_source_columns": (
                "observation_records.csv:time,detected,effort; "
                "survey_schedule.csv:habitat_class,row_band,col_band"
            ),
            "interpretation": self.interpretation,
        }


@dataclass(frozen=True, slots=True)
class SynthMediumResponseReconstructionConfig:
    selected_default_regime_id: str = SELECTED_DEFAULT_REGIME_ID
    large_error_min: float = 24.0
    benchmark_median_abs_error_max: float = 12.0
    default_min_finite_recall: float = 0.35
    default_ready_finite_recall: float = 0.60
    default_ready_median_abs_error_max: float = 18.0
    default_ready_large_error_fraction_max: float = 0.35
    default_marginal_loss_max: float = 1.45

    def to_dict(self) -> dict[str, object]:
        return {
            "selected_default_regime_id": self.selected_default_regime_id,
            "large_error_min": self.large_error_min,
            "review_gate_thresholds": {
                "benchmark_median_abs_error_max": self.benchmark_median_abs_error_max,
                "default_min_finite_recall": self.default_min_finite_recall,
                "default_ready_finite_recall": self.default_ready_finite_recall,
                "default_ready_median_abs_error_max": (self.default_ready_median_abs_error_max),
                "default_ready_large_error_fraction_max": (
                    self.default_ready_large_error_fraction_max
                ),
                "default_marginal_loss_max": self.default_marginal_loss_max,
            },
            "output_files": list(SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_FILES),
            "visual_files": [
                f"visuals/{name}" for name in SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES
            ],
            **BOUNDARY_LABELS,
        }


@dataclass(frozen=True, slots=True)
class ResponseReconstructionCheck:
    name: str
    passed: bool
    details: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "details": self.details}


@dataclass(frozen=True, slots=True)
class SynthMediumResponseReconstructionResult:
    config: SynthMediumResponseReconstructionConfig
    observation_design: SynthMediumObservationDesignResult
    rules: tuple[ReconstructionRule, ...]
    reconstructed_cell_rows: tuple[CsvRow, ...]
    truth_reconstruction_bridge_rows: tuple[CsvRow, ...]
    reconstruction_error_summary_rows: tuple[CsvRow, ...]
    rule_regime_ranking_rows: tuple[CsvRow, ...]
    support_gap_summary_rows: tuple[CsvRow, ...]
    recoverability_signal_summary_rows: tuple[CsvRow, ...]
    verification_checks: tuple[ResponseReconstructionCheck, ...]
    visual_svgs: dict[str, str]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    @property
    def recommendation_class(self) -> str:
        default_best = best_ranking_row(
            self.rule_regime_ranking_rows, self.config.selected_default_regime_id
        )
        if not self.passed:
            return "observation_design_not_recoverable_enough_for_backfitting"
        if (
            csv_float(default_best["finite_recall"]) >= self.config.default_ready_finite_recall
            and csv_float(default_best["median_absolute_error"])
            <= self.config.default_ready_median_abs_error_max
            and csv_float(default_best["large_error_fraction"])
            <= self.config.default_ready_large_error_fraction_max
        ):
            return "response_reconstruction_ready_for_human_review"
        if csv_float(default_best["loss"]) <= self.config.default_marginal_loss_max:
            return "default_observation_design_recoverability_marginal"
        return "observation_design_not_recoverable_enough_for_backfitting"

    def summary_dict(self) -> dict[str, object]:
        default_best = best_ranking_row(
            self.rule_regime_ranking_rows, self.config.selected_default_regime_id
        )
        benchmark_best = best_ranking_row(
            self.rule_regime_ranking_rows, "truth_reference_full_observability"
        )
        sparse_best = best_ranking_row(
            self.rule_regime_ranking_rows, "sparse_response_observed_stress"
        )
        return {
            "selected_default_regime_id": self.config.selected_default_regime_id,
            "rule_count": len(self.rules),
            "primary_default_rule_id": default_best["rule_id"],
            "default_best_finite_recall": default_best["finite_recall"],
            "default_best_median_absolute_error": default_best["median_absolute_error"],
            "default_best_large_error_count": default_best["large_error_count"],
            "benchmark_best_rule_id": benchmark_best["rule_id"],
            "benchmark_positive_control_status": benchmark_best["positive_control_status"],
            "sparse_best_rule_id": sparse_best["rule_id"],
            "recommendation_class": self.recommendation_class,
        }

    def config_payload(self) -> dict[str, object]:
        return {
            **self.config.to_dict(),
            "source_reconciliation": source_reconciliation(self.observation_design),
            "rules": [rule.to_csv_row() for rule in self.rules],
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

        config_path = target_dir / "response_reconstruction_config.json"
        config_path.write_text(
            dumps(self.config_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(config_path)

        table_specs: tuple[tuple[str, tuple[str, ...], tuple[CsvRow, ...]], ...] = (
            (
                "reconstruction_rule_definitions.csv",
                RECONSTRUCTION_RULE_COLUMNS,
                tuple(rule.to_csv_row() for rule in self.rules),
            ),
            (
                "reconstructed_cell_times.csv",
                RECONSTRUCTED_CELL_COLUMNS,
                self.reconstructed_cell_rows,
            ),
            (
                "truth_reconstruction_bridge.csv",
                TRUTH_RECONSTRUCTION_BRIDGE_COLUMNS,
                self.truth_reconstruction_bridge_rows,
            ),
            (
                "reconstruction_error_summary.csv",
                ERROR_SUMMARY_COLUMNS,
                self.reconstruction_error_summary_rows,
            ),
            (
                "rule_regime_rankings.csv",
                RANKING_COLUMNS,
                self.rule_regime_ranking_rows,
            ),
            ("support_gap_summary.csv", SUPPORT_GAP_COLUMNS, self.support_gap_summary_rows),
            (
                "recoverability_signal_summary.csv",
                RECOVERABILITY_SIGNAL_COLUMNS,
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
        report_path.write_text(render_response_reconstruction_report(self), encoding="utf-8")
        written.append(report_path)

        for visual_name in SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES:
            path = visuals_dir / visual_name
            path.write_text(self.visual_svgs[visual_name], encoding="utf-8")
            written.append(path)

        return tuple(written)


def build_synth_medium_response_reconstruction_benchmark(
    config: SynthMediumResponseReconstructionConfig | None = None,
    *,
    observation_design: SynthMediumObservationDesignResult | None = None,
) -> SynthMediumResponseReconstructionResult:
    reconstruction_config = config or SynthMediumResponseReconstructionConfig()
    source = observation_design or build_synth_medium_observation_design_review_pack()
    rules = default_reconstruction_rules()
    reconstructed_rows = build_reconstructed_cell_rows(source, rules)
    bridge_rows = build_truth_reconstruction_bridge_rows(
        source, reconstructed_rows, reconstruction_config
    )
    error_rows = build_reconstruction_error_summary_rows(bridge_rows, reconstruction_config)
    ranking_rows = build_rule_regime_ranking_rows(error_rows, reconstruction_config)
    support_rows = build_support_gap_summary_rows(reconstructed_rows)
    signal_rows = build_recoverability_signal_summary_rows(
        ranking_rows,
        support_rows,
        reconstruction_config,
    )
    visual_svgs = build_response_reconstruction_visual_svgs(
        source,
        reconstructed_rows,
        bridge_rows,
        ranking_rows,
        reconstruction_config,
    )
    checks = verify_response_reconstruction_result(
        reconstruction_config,
        source,
        rules,
        reconstructed_rows,
        bridge_rows,
        error_rows,
        ranking_rows,
        support_rows,
        signal_rows,
        visual_svgs,
    )
    return SynthMediumResponseReconstructionResult(
        config=reconstruction_config,
        observation_design=source,
        rules=rules,
        reconstructed_cell_rows=reconstructed_rows,
        truth_reconstruction_bridge_rows=bridge_rows,
        reconstruction_error_summary_rows=error_rows,
        rule_regime_ranking_rows=ranking_rows,
        support_gap_summary_rows=support_rows,
        recoverability_signal_summary_rows=signal_rows,
        verification_checks=checks,
        visual_svgs=visual_svgs,
    )


def default_reconstruction_rules() -> tuple[ReconstructionRule, ...]:
    return (
        ReconstructionRule(
            rule_id="final_absence_run_2",
            rule_label="Final absence run length 2",
            min_final_absence_run=2,
            time_estimator="first_final_absence",
            interpretation=(
                "Conservative response-only benchmark: requires detection history and at "
                "least two final surveyed non-detection times after the last detection."
            ),
        ),
        ReconstructionRule(
            rule_id="final_absence_run_1",
            rule_label="Final absence run length 1",
            min_final_absence_run=1,
            time_estimator="first_final_absence",
            interpretation=(
                "Timing-sensitive response-only benchmark: one final surveyed "
                "non-detection after detection history is enough to make a finite time."
            ),
        ),
        ReconstructionRule(
            rule_id="midpoint_after_last_detection",
            rule_label="Midpoint after last detection",
            min_final_absence_run=1,
            time_estimator="midpoint_last_detection_to_first_absence",
            interpretation=(
                "Response-only timing benchmark: uses the midpoint between the last "
                "detection and first final absence as an interval-censored proxy."
            ),
        ),
    )


def build_reconstructed_cell_rows(
    source: SynthMediumObservationDesignResult,
    rules: tuple[ReconstructionRule, ...],
) -> tuple[CsvRow, ...]:
    observations_by_regime_cell: dict[tuple[str, int], list[CsvRow]] = defaultdict(list)
    for row in source.observation_record_rows:
        observations_by_regime_cell[(str(row["regime_id"]), csv_int(row["cell_id"]))].append(row)

    passable_truth = passable_truth_rows(source)
    rows: list[CsvRow] = []
    for regime_id in REGIME_IDS:
        for rule in rules:
            for truth_row in passable_truth:
                cell = truth_row.landscape_cell
                observations = sorted(
                    observations_by_regime_cell.get((regime_id, cell.cell_id), []),
                    key=lambda value: csv_int(value["time"]),
                )
                rows.append(reconstruct_cell(regime_id, rule, truth_row, observations))
    return tuple(rows)


def reconstruct_cell(
    regime_id: str,
    rule: ReconstructionRule,
    truth_row: SpreadImpactCellTruth,
    observations: list[CsvRow],
) -> CsvRow:
    cell = truth_row.landscape_cell
    times = [csv_int(row["time"]) for row in observations]
    detected_times = [csv_int(row["time"]) for row in observations if csv_bool(row["detected"])]
    final_absence_times: list[int] = []
    if detected_times:
        last_detection = max(detected_times)
        after_last_detection = [
            row for row in observations if csv_int(row["time"]) > last_detection
        ]
        for row in sorted(
            after_last_detection, key=lambda value: csv_int(value["time"]), reverse=True
        ):
            if csv_bool(row["detected"]):
                break
            final_absence_times.append(csv_int(row["time"]))
        final_absence_times = sorted(final_absence_times)
    final_absence_count = len(final_absence_times)
    final_absence_start = min(final_absence_times) if final_absence_times else None
    reconstructed_finite = bool(
        detected_times
        and final_absence_start is not None
        and final_absence_count >= rule.min_final_absence_run
    )
    if reconstructed_finite:
        assert final_absence_start is not None
        if rule.time_estimator == "midpoint_last_detection_to_first_absence":
            response_time: float | None = round_float(
                (max(detected_times) + final_absence_start) / 2
            )
        else:
            response_time = float(final_absence_start)
    else:
        response_time = None
    status = reconstruction_status(
        observations,
        detected_times,
        final_absence_times,
        rule.min_final_absence_run,
    )
    return {
        "regime_id": regime_id,
        "rule_id": rule.rule_id,
        "cell_id": cell.cell_id,
        "row": cell.row,
        "col": cell.col,
        "habitat_class": cell.habitat_class,
        "row_band": cell.row_band,
        "col_band": cell.col_band,
        "survey_count": len(observations),
        "detection_count": len(detected_times),
        "first_survey_time": min(times) if times else None,
        "last_survey_time": max(times) if times else None,
        "first_detection_time": min(detected_times) if detected_times else None,
        "last_detection_time": max(detected_times) if detected_times else None,
        "final_absence_start_time": final_absence_start,
        "final_absence_survey_time_count": final_absence_count,
        "reconstructed_finite": reconstructed_finite,
        "reconstructed_response_time": response_time,
        "reconstruction_status": status,
        "support_class": support_class(observations, detected_times, reconstructed_finite),
    }


def reconstruction_status(
    observations: list[CsvRow],
    detected_times: list[int],
    final_absence_times: list[int],
    min_final_absence_run: int,
) -> str:
    if not observations:
        return "no_survey"
    if not detected_times:
        return "no_detection_history"
    if not final_absence_times:
        return "no_post_detection_survey"
    if len(final_absence_times) < min_final_absence_run:
        return "short_final_absence_run"
    return "finite_reconstructed"


def support_class(
    observations: list[CsvRow],
    detected_times: list[int],
    reconstructed_finite: bool,
) -> str:
    if not observations:
        return "never_surveyed"
    if not detected_times:
        return "no_detection_history"
    if reconstructed_finite:
        return "finite_reconstruction_support"
    return "insufficient_final_absence_support"


def build_truth_reconstruction_bridge_rows(
    source: SynthMediumObservationDesignResult,
    reconstructed_rows: tuple[CsvRow, ...],
    config: SynthMediumResponseReconstructionConfig,
) -> tuple[CsvRow, ...]:
    truth_by_cell = {row.landscape_cell.cell_id: row for row in passable_truth_rows(source)}
    rows: list[CsvRow] = []
    for row in reconstructed_rows:
        truth_row = truth_by_cell[csv_int(row["cell_id"])]
        true_time = truth_row.prey_extirpation_time
        true_finite = true_time is not None
        reconstructed_finite = csv_bool(row["reconstructed_finite"])
        reconstructed_time = optional_float(row["reconstructed_response_time"])
        signed_error = (
            round_float(reconstructed_time - true_time)
            if reconstructed_finite and true_time is not None and reconstructed_time is not None
            else None
        )
        absolute_error = abs(signed_error) if signed_error is not None else None
        rows.append(
            {
                "regime_id": row["regime_id"],
                "rule_id": row["rule_id"],
                "cell_id": row["cell_id"],
                "row": row["row"],
                "col": row["col"],
                "habitat_class": row["habitat_class"],
                "row_band": row["row_band"],
                "col_band": row["col_band"],
                "prey_extirpation_time": true_time,
                "true_extirpated_by_end": true_finite,
                "reconstructed_finite": reconstructed_finite,
                "reconstructed_response_time": reconstructed_time,
                "signed_error": signed_error,
                "absolute_error": absolute_error,
                "error_class": error_class(signed_error, config.large_error_min),
                "classification": classification(true_finite, reconstructed_finite),
            }
        )
    return tuple(rows)


def build_reconstruction_error_summary_rows(
    bridge_rows: tuple[CsvRow, ...],
    config: SynthMediumResponseReconstructionConfig,
) -> tuple[CsvRow, ...]:
    groups: dict[tuple[str, str, str], list[CsvRow]] = defaultdict(list)
    for row in bridge_rows:
        keys = (
            "all_passable",
            f"habitat:{row['habitat_class']}",
            f"col_band:{row['col_band']}",
            f"row_band:{row['row_band']}",
        )
        for key in keys:
            groups[(str(row["regime_id"]), str(row["rule_id"]), key)].append(row)
    return tuple(
        build_error_summary_row(regime_id, rule_id, group, rows, config)
        for regime_id, rule_id, group in sorted(groups)
        for rows in (groups[(regime_id, rule_id, group)],)
    )


def build_error_summary_row(
    regime_id: str,
    rule_id: str,
    group: str,
    rows: list[CsvRow],
    config: SynthMediumResponseReconstructionConfig,
) -> CsvRow:
    true_extirpated = [row for row in rows if csv_bool(row["true_extirpated_by_end"])]
    reconstructed = [row for row in rows if csv_bool(row["reconstructed_finite"])]
    true_positive = [row for row in rows if row["classification"] == "true_positive"]
    false_positive = [row for row in rows if row["classification"] == "false_positive"]
    false_negative = [row for row in rows if row["classification"] == "false_negative"]
    true_negative = [row for row in rows if row["classification"] == "true_negative"]
    signed_errors = [
        csv_float(row["signed_error"]) for row in true_positive if row["signed_error"] is not None
    ]
    absolute_errors = [
        csv_float(row["absolute_error"])
        for row in true_positive
        if row["absolute_error"] is not None
    ]
    large_errors = [value for value in absolute_errors if value >= config.large_error_min]
    return {
        "regime_id": regime_id,
        "rule_id": rule_id,
        "summary_group": group,
        "cell_count": len(rows),
        "true_extirpated_count": len(true_extirpated),
        "finite_reconstructed_count": len(reconstructed),
        "true_positive_count": len(true_positive),
        "false_positive_count": len(false_positive),
        "false_negative_count": len(false_negative),
        "true_negative_count": len(true_negative),
        "finite_recall": safe_fraction(len(true_positive), len(true_extirpated)),
        "specificity": safe_fraction(len(true_negative), len(rows) - len(true_extirpated)),
        "precision": safe_fraction(len(true_positive), len(reconstructed)),
        "mean_signed_error": mean_or_none(signed_errors),
        "median_absolute_error": quantile_or_none(absolute_errors, 0.5),
        "p90_absolute_error": quantile_or_none(absolute_errors, 0.9),
        "large_error_count": len(large_errors),
        "large_error_fraction": safe_fraction(len(large_errors), len(true_positive)),
    }


def build_rule_regime_ranking_rows(
    error_rows: tuple[CsvRow, ...],
    config: SynthMediumResponseReconstructionConfig,
) -> tuple[CsvRow, ...]:
    all_rows = [row for row in error_rows if row["summary_group"] == "all_passable"]
    by_regime: dict[str, list[CsvRow]] = defaultdict(list)
    for row in all_rows:
        by_regime[str(row["regime_id"])].append(row)
    ranked_rows: list[CsvRow] = []
    provisional: dict[str, list[tuple[float, CsvRow]]] = {}
    for regime_id, rows in by_regime.items():
        scored = [(ranking_loss(row), row) for row in rows]
        scored.sort(key=lambda item: (item[0], str(item[1]["rule_id"])))
        provisional[regime_id] = scored

    default_best_loss = provisional[SELECTED_DEFAULT_REGIME_ID][0][0]
    recommendation = recommendation_from_default_best(
        provisional[SELECTED_DEFAULT_REGIME_ID][0][1],
        default_best_loss,
        config,
    )
    for regime_id in REGIME_IDS:
        for rank, (loss, row) in enumerate(provisional[regime_id], start=1):
            positive_control_status = "not_applicable"
            if regime_id == "truth_reference_full_observability":
                positive_control_status = (
                    "passed"
                    if csv_int(row["false_negative_count"]) == 0
                    and csv_float(row["median_absolute_error"])
                    <= config.benchmark_median_abs_error_max
                    else "failed"
                )
            ranked_rows.append(
                {
                    "regime_id": regime_id,
                    "rule_id": row["rule_id"],
                    "rank": rank,
                    "finite_reconstructed_count": row["finite_reconstructed_count"],
                    "true_positive_count": row["true_positive_count"],
                    "false_positive_count": row["false_positive_count"],
                    "false_negative_count": row["false_negative_count"],
                    "finite_recall": row["finite_recall"],
                    "specificity": row["specificity"],
                    "precision": row["precision"],
                    "median_absolute_error": row["median_absolute_error"],
                    "p90_absolute_error": row["p90_absolute_error"],
                    "large_error_count": row["large_error_count"],
                    "large_error_fraction": row["large_error_fraction"],
                    "loss": round_float(loss),
                    "positive_control_status": positive_control_status,
                    "recommendation_class": recommendation
                    if regime_id == SELECTED_DEFAULT_REGIME_ID and rank == 1
                    else "",
                }
            )
    return tuple(ranked_rows)


def ranking_loss(row: CsvRow) -> float:
    false_negative_penalty = 1.0 - csv_float(row["finite_recall"])
    false_positive_penalty = 1.0 - csv_float(row["specificity"])
    large_error_penalty = csv_float(row["large_error_fraction"])
    median_error_penalty = min(csv_float(row["median_absolute_error"]) / 48.0, 1.5)
    p90_error_penalty = min(csv_float(row["p90_absolute_error"]) / 72.0, 1.5)
    return (
        false_negative_penalty * 1.6
        + false_positive_penalty * 0.9
        + large_error_penalty * 0.9
        + median_error_penalty * 0.6
        + p90_error_penalty * 0.4
    )


def recommendation_from_default_best(
    default_best: CsvRow,
    loss: float,
    config: SynthMediumResponseReconstructionConfig,
) -> str:
    if (
        csv_float(default_best["finite_recall"]) >= config.default_ready_finite_recall
        and csv_float(default_best["median_absolute_error"])
        <= config.default_ready_median_abs_error_max
        and csv_float(default_best["large_error_fraction"])
        <= config.default_ready_large_error_fraction_max
    ):
        return "response_reconstruction_ready_for_human_review"
    if (
        csv_float(default_best["finite_recall"]) >= config.default_min_finite_recall
        and loss <= config.default_marginal_loss_max
    ):
        return "default_observation_design_recoverability_marginal"
    return "observation_design_not_recoverable_enough_for_backfitting"


def build_support_gap_summary_rows(reconstructed_rows: tuple[CsvRow, ...]) -> tuple[CsvRow, ...]:
    groups: dict[tuple[str, str, str], list[CsvRow]] = defaultdict(list)
    for row in reconstructed_rows:
        keys = (
            "all_passable",
            f"habitat:{row['habitat_class']}",
            f"col_band:{row['col_band']}",
        )
        for key in keys:
            groups[(str(row["regime_id"]), str(row["rule_id"]), key)].append(row)
    return tuple(
        build_support_gap_row(regime_id, rule_id, group, rows)
        for regime_id, rule_id, group in sorted(groups)
        for rows in (groups[(regime_id, rule_id, group)],)
    )


def build_support_gap_row(
    regime_id: str,
    rule_id: str,
    group: str,
    rows: list[CsvRow],
) -> CsvRow:
    surveyed = [row for row in rows if csv_int(row["survey_count"]) > 0]
    never_surveyed = [row for row in rows if row["reconstruction_status"] == "no_survey"]
    no_detection = [row for row in rows if row["reconstruction_status"] == "no_detection_history"]
    no_post_detection = [
        row for row in rows if row["reconstruction_status"] == "no_post_detection_survey"
    ]
    supported = [row for row in rows if csv_bool(row["reconstructed_finite"])]
    survey_counts = [csv_int(row["survey_count"]) for row in rows]
    absence_runs = [csv_int(row["final_absence_survey_time_count"]) for row in rows]
    return {
        "regime_id": regime_id,
        "rule_id": rule_id,
        "summary_group": group,
        "passable_cell_count": len(rows),
        "surveyed_cell_count": len(surveyed),
        "never_surveyed_count": len(never_surveyed),
        "no_detection_history_count": len(no_detection),
        "no_post_detection_survey_count": len(no_post_detection),
        "post_detection_absence_supported_count": len(supported),
        "finite_reconstructed_count": len(supported),
        "mean_survey_count": round_float(mean(float(value) for value in survey_counts)),
        "mean_final_absence_run": round_float(mean(float(value) for value in absence_runs)),
    }


def build_recoverability_signal_summary_rows(
    ranking_rows: tuple[CsvRow, ...],
    support_rows: tuple[CsvRow, ...],
    config: SynthMediumResponseReconstructionConfig,
) -> tuple[CsvRow, ...]:
    full_best = best_ranking_row(ranking_rows, "truth_reference_full_observability")
    default_best = best_ranking_row(ranking_rows, SELECTED_DEFAULT_REGIME_ID)
    sparse_best = best_ranking_row(ranking_rows, "sparse_response_observed_stress")
    default_support = support_row(
        support_rows,
        SELECTED_DEFAULT_REGIME_ID,
        str(default_best["rule_id"]),
        "all_passable",
    )
    rows = [
        {
            "regime_id": "truth_reference_full_observability",
            "proxy_id": "benchmark_positive_control",
            "observed_value": full_best["median_absolute_error"],
            "threshold": config.benchmark_median_abs_error_max,
            "passes": full_best["positive_control_status"] == "passed",
            "interpretation": (
                "full-observability benchmark reconstructs finite truth within survey tolerance"
            ),
        },
        {
            "regime_id": SELECTED_DEFAULT_REGIME_ID,
            "proxy_id": "default_nontrivial_reconstruction",
            "observed_value": default_best["finite_recall"],
            "threshold": config.default_min_finite_recall,
            "passes": csv_float(default_best["finite_recall"]) >= config.default_min_finite_recall,
            "interpretation": "default observations retain nontrivial finite response-time support",
        },
        {
            "regime_id": SELECTED_DEFAULT_REGIME_ID,
            "proxy_id": "default_error_distribution_quantified",
            "observed_value": default_best["large_error_count"],
            "threshold": config.large_error_min,
            "passes": csv_int(default_best["large_error_count"]) > 0,
            "interpretation": (
                "default timing errors are spatially visible rather than hidden in one mean"
            ),
        },
        {
            "regime_id": SELECTED_DEFAULT_REGIME_ID,
            "proxy_id": "default_support_gaps_audited",
            "observed_value": default_support["never_surveyed_count"],
            "threshold": 0,
            "passes": csv_int(default_support["post_detection_absence_supported_count"]) > 0,
            "interpretation": (
                "response-only support gaps are exposed alongside finite reconstructions"
            ),
        },
        {
            "regime_id": "sparse_response_observed_stress",
            "proxy_id": "stress_lower_information_than_default",
            "observed_value": sparse_best["finite_recall"],
            "threshold": default_best["finite_recall"],
            "passes": csv_float(sparse_best["finite_recall"])
            < csv_float(default_best["finite_recall"])
            and csv_float(sparse_best["loss"]) > csv_float(default_best["loss"]),
            "interpretation": "sparse stress has lower recall and worse loss than the default",
        },
    ]
    return tuple(rows)


def verify_response_reconstruction_result(
    config: SynthMediumResponseReconstructionConfig,
    source: SynthMediumObservationDesignResult,
    rules: tuple[ReconstructionRule, ...],
    reconstructed_rows: tuple[CsvRow, ...],
    bridge_rows: tuple[CsvRow, ...],
    error_rows: tuple[CsvRow, ...],
    ranking_rows: tuple[CsvRow, ...],
    support_rows: tuple[CsvRow, ...],
    signal_rows: tuple[CsvRow, ...],
    visual_svgs: dict[str, str],
) -> tuple[ResponseReconstructionCheck, ...]:
    reconciliation = source_reconciliation(source)
    reconstructed_columns = set(RECONSTRUCTED_CELL_COLUMNS)
    forbidden_columns = {
        "predator_arrival_time",
        "prey_impact_time",
        "prey_extirpation_time",
        "true_extirpated_by_end",
        "true_response_time",
        "absolute_error",
        "signed_error",
    }
    full_best = best_ranking_row(ranking_rows, "truth_reference_full_observability")
    default_best = best_ranking_row(ranking_rows, SELECTED_DEFAULT_REGIME_ID)
    sparse_best = best_ranking_row(ranking_rows, "sparse_response_observed_stress")
    signal_map = {(row["regime_id"], row["proxy_id"]): row for row in signal_rows}
    expected_rows = 5225 * len(REGIME_IDS) * len(rules)
    return (
        ResponseReconstructionCheck(
            name="artifact_contract",
            passed=set(visual_svgs) == set(SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES)
            and all(
                svg.lstrip().startswith("<svg") and len(svg) > 1000 for svg in visual_svgs.values()
            ),
            details={
                "output_file_count": len(SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_FILES),
                "visual_file_count": len(visual_svgs),
            },
        ),
        ResponseReconstructionCheck(
            name="source_reconciliation",
            passed=reconciliation == SOURCE_EXPECTATIONS,
            details={"source_reconciliation": reconciliation},
        ),
        ResponseReconstructionCheck(
            name="response_only_reconstruction_schema",
            passed=reconstructed_columns.isdisjoint(forbidden_columns)
            and all(not rule.to_csv_row()["uses_hidden_truth"] for rule in rules),
            details={
                "forbidden_columns_present": sorted(reconstructed_columns & forbidden_columns)
            },
        ),
        ResponseReconstructionCheck(
            name="full_observability_positive_control",
            passed=full_best["positive_control_status"] == "passed"
            and csv_int(full_best["false_negative_count"]) == 0,
            details={
                "best_rule_id": full_best["rule_id"],
                "median_absolute_error": full_best["median_absolute_error"],
                "false_negative_count": full_best["false_negative_count"],
            },
        ),
        ResponseReconstructionCheck(
            name="default_nontrivial_reconstruction",
            passed=csv_bool(
                signal_map[(SELECTED_DEFAULT_REGIME_ID, "default_nontrivial_reconstruction")][
                    "passes"
                ]
            ),
            details={
                "best_rule_id": default_best["rule_id"],
                "finite_recall": default_best["finite_recall"],
                "finite_reconstructed_count": default_best["finite_reconstructed_count"],
            },
        ),
        ResponseReconstructionCheck(
            name="default_error_distribution_audited",
            passed=csv_bool(
                signal_map[(SELECTED_DEFAULT_REGIME_ID, "default_error_distribution_quantified")][
                    "passes"
                ]
            )
            and any(
                row["regime_id"] == SELECTED_DEFAULT_REGIME_ID
                and row["rule_id"] == default_best["rule_id"]
                and str(row["summary_group"]).startswith("habitat:")
                for row in error_rows
            ),
            details={
                "large_error_count": default_best["large_error_count"],
                "median_absolute_error": default_best["median_absolute_error"],
            },
        ),
        ResponseReconstructionCheck(
            name="sparse_stress_lower_information",
            passed=csv_bool(
                signal_map[
                    ("sparse_response_observed_stress", "stress_lower_information_than_default")
                ]["passes"]
            ),
            details={
                "default_loss": default_best["loss"],
                "sparse_loss": sparse_best["loss"],
                "default_finite_recall": default_best["finite_recall"],
                "sparse_finite_recall": sparse_best["finite_recall"],
            },
        ),
        ResponseReconstructionCheck(
            name="table_reconciliation",
            passed=len(reconstructed_rows) == expected_rows
            and len(bridge_rows) == len(reconstructed_rows)
            and len(ranking_rows) == len(REGIME_IDS) * len(rules)
            and bool(error_rows)
            and bool(support_rows),
            details={
                "expected_reconstructed_row_count": expected_rows,
                "reconstructed_row_count": len(reconstructed_rows),
                "bridge_row_count": len(bridge_rows),
                "ranking_row_count": len(ranking_rows),
            },
        ),
        ResponseReconstructionCheck(
            name="visual_contract",
            passed=visual_layout_contract_passes(visual_svgs),
            details={"visual_files": sorted(visual_svgs)},
        ),
    )


def build_response_reconstruction_visual_svgs(
    source: SynthMediumObservationDesignResult,
    reconstructed_rows: tuple[CsvRow, ...],
    bridge_rows: tuple[CsvRow, ...],
    ranking_rows: tuple[CsvRow, ...],
    config: SynthMediumResponseReconstructionConfig,
) -> dict[str, str]:
    truth_rows = passable_truth_rows(source)
    default_best = best_ranking_row(ranking_rows, config.selected_default_regime_id)
    primary_rule = str(default_best["rule_id"])
    reconstructed_by_cell = {
        csv_int(row["cell_id"]): row
        for row in reconstructed_rows
        if row["regime_id"] == config.selected_default_regime_id and row["rule_id"] == primary_rule
    }
    bridge_by_cell = {
        csv_int(row["cell_id"]): row
        for row in bridge_rows
        if row["regime_id"] == config.selected_default_regime_id and row["rule_id"] == primary_rule
    }
    return {
        "truth_response_time.svg": render_grid_svg(
            truth_rows,
            lambda row: truth_time_fill(row.prey_extirpation_time),
            "Truth response time",
            "legend-truth-response-time",
            TRUTH_TIME_LEGEND,
        ),
        "default_primary_reconstructed_time.svg": render_grid_svg(
            truth_rows,
            lambda row: reconstructed_time_fill(
                reconstructed_by_cell.get(row.landscape_cell.cell_id)
            ),
            f"Default reconstructed time ({primary_rule})",
            "legend-reconstructed-time",
            RECONSTRUCTED_TIME_LEGEND,
        ),
        "default_primary_residual_error.svg": render_grid_svg(
            truth_rows,
            lambda row: residual_error_fill(bridge_by_cell.get(row.landscape_cell.cell_id)),
            f"Default residual error ({primary_rule})",
            "legend-residual-error",
            RESIDUAL_ERROR_LEGEND,
        ),
        "default_primary_support_gap.svg": render_grid_svg(
            truth_rows,
            lambda row: support_gap_fill(reconstructed_by_cell.get(row.landscape_cell.cell_id)),
            f"Default support gap ({primary_rule})",
            "legend-support-gap",
            SUPPORT_GAP_LEGEND,
        ),
        "regime_rule_comparison_montage.svg": render_regime_rule_comparison_svg(ranking_rows),
        "review_montage.svg": render_review_montage_svg(
            truth_rows,
            reconstructed_by_cell,
            bridge_by_cell,
            primary_rule,
        ),
    }


def render_grid_svg(
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


def render_regime_rule_comparison_svg(ranking_rows: tuple[CsvRow, ...]) -> str:
    width = 1580
    height = 520
    lines = svg_header(width, height, "Regime/rule comparison montage")
    lines.append(
        '<text x="24" y="32" font-size="22" font-family="monospace">'
        "Regime/rule comparison table</text>"
    )
    metrics = (
        ("Recall", "finite_recall", "#2563eb", 1.0),
        ("Median error", "median_absolute_error", "#16a34a", 60.0),
        ("Large errors", "large_error_count", "#dc2626", 4289.0),
        ("Loss", "loss", "#7c3aed", 2.5),
    )
    metric_x = 600
    metric_width = 225
    bar_width = 120
    table_width = 1520
    lines.append(f'<rect x="20" y="58" width="{table_width}" height="32" fill="#f8fafc" />')
    lines.append(
        '<text x="32" y="80" font-size="13" font-family="monospace" '
        'font-weight="bold">Regime / rule</text>'
    )
    for index, (label, _, _, _) in enumerate(metrics):
        x = metric_x + index * metric_width
        lines.append(
            f'<text x="{x}" y="80" font-size="13" font-family="monospace" '
            f'font-weight="bold">{label}</text>'
        )
    sorted_rows = sorted(
        ranking_rows, key=lambda row: (str(row["regime_id"]), csv_int(row["rank"]))
    )
    for index, row in enumerate(sorted_rows):
        y = 120 + index * 42
        fill = "#ffffff" if index % 2 == 0 else "#f8fafc"
        lines.append(
            f'<rect x="20" y="{y - 24}" width="{table_width}" height="34" fill="{fill}" />'
        )
        lines.append(
            f'<text x="32" y="{y - 4}" font-size="12" font-family="monospace">'
            f"{row['regime_id']} / {row['rule_id']} (rank {row['rank']})</text>"
        )
        for metric_index, (_, metric, color, scale) in enumerate(metrics):
            value = csv_float(row[metric])
            x = metric_x + metric_index * metric_width
            bar_fraction = min(value / scale, 1.0)
            if metric in {"median_absolute_error", "large_error_count", "loss"}:
                label = f"{value:.2f}" if metric != "large_error_count" else str(int(value))
            else:
                label = f"{value:.2f}"
            lines.append(
                f'<rect x="{x}" y="{y - 18}" width="{bar_width}" height="14" fill="#e5e7eb" />'
            )
            lines.append(
                f'<rect x="{x}" y="{y - 18}" width="{int(bar_fraction * bar_width)}" '
                f'height="14" fill="{color}" />'
            )
            lines.append(
                f'<text x="{x + bar_width + 10}" y="{y - 6}" font-size="12" '
                f'font-family="monospace">{label}</text>'
            )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_review_montage_svg(
    rows: tuple[SpreadImpactCellTruth, ...],
    reconstructed_by_cell: dict[int, CsvRow],
    bridge_by_cell: dict[int, CsvRow],
    primary_rule: str,
) -> str:
    width = 780
    panel_height = 620
    height = 64 + 4 * panel_height
    lines = svg_header(width, height, "Response reconstruction review montage")
    lines.append(
        '<text x="20" y="30" font-size="22" font-family="monospace">'
        "Response reconstruction review montage</text>"
    )
    panels: tuple[
        tuple[str, Callable[[SpreadImpactCellTruth], str], str, tuple[LegendItem, ...]], ...
    ] = (
        (
            "Truth response time",
            lambda row: truth_time_fill(row.prey_extirpation_time),
            "legend-truth-response-time",
            TRUTH_TIME_LEGEND,
        ),
        (
            f"Default reconstructed time ({primary_rule})",
            lambda row: reconstructed_time_fill(
                reconstructed_by_cell.get(row.landscape_cell.cell_id)
            ),
            "legend-reconstructed-time",
            RECONSTRUCTED_TIME_LEGEND,
        ),
        (
            f"Default residual error ({primary_rule})",
            lambda row: residual_error_fill(bridge_by_cell.get(row.landscape_cell.cell_id)),
            "legend-residual-error",
            RESIDUAL_ERROR_LEGEND,
        ),
        (
            f"Default support gap ({primary_rule})",
            lambda row: support_gap_fill(reconstructed_by_cell.get(row.landscape_cell.cell_id)),
            "legend-support-gap",
            SUPPORT_GAP_LEGEND,
        ),
    )
    map_cell_size = 6
    map_height = 72 * map_cell_size
    for index, (title, fill_for, legend_id, legend_items) in enumerate(panels):
        panel_top = 44 + index * panel_height
        title_y = panel_top + 26
        map_top = panel_top + 48
        map_bottom = map_top + map_height
        legend_top = map_bottom + 26
        legend_bottom = legend_bottom_y(legend_top, legend_items)
        panel_bottom = legend_bottom + 24
        panel_id = legend_id.removeprefix("legend-")
        lines.append(
            f'<g id="panel-{panel_id}" data-title-y="{title_y}" '
            f'data-map-top="{map_top}" data-map-bottom="{map_bottom}" '
            f'data-legend-top="{legend_top}" data-legend-bottom="{legend_bottom}" '
            f'data-panel-bottom="{panel_bottom}">'
        )
        lines.append(
            f'<rect x="14" y="{panel_top}" width="742" height="{panel_bottom - panel_top}" '
            'fill="#ffffff" stroke="#cbd5e1" />'
        )
        lines.append(
            f'<text x="24" y="{title_y}" font-size="16" font-family="monospace">{title}</text>'
        )
        for row in rows:
            cell = row.landscape_cell
            x = 24 + cell.col * map_cell_size
            y = map_top + cell.row * map_cell_size
            lines.append(
                f'<rect x="{x}" y="{y}" width="{map_cell_size}" height="{map_cell_size}" '
                f'fill="{fill_for(row)}" stroke="none" />'
            )
        append_legend(lines, legend_id, 24, legend_top, legend_items, columns=2)
        lines.append("</g>")
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def visual_layout_contract_passes(visual_svgs: dict[str, str]) -> bool:
    if set(visual_svgs) != set(SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES):
        return False
    comparison = visual_svgs["regime_rule_comparison_montage.svg"]
    if 'width="1580"' not in comparison or "Regime/rule comparison table" not in comparison:
        return False
    review = visual_svgs["review_montage.svg"]
    return all(label in review for label in ("data-legend-bottom", "data-panel-bottom", "Legend"))


def render_response_reconstruction_report(
    result: SynthMediumResponseReconstructionResult,
) -> str:
    visual_lines = "\n".join(
        f"- [`visuals/{name}`](visuals/{name})"
        for name in SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES
    )
    ranking_lines = "\n".join(
        f"- `{row['regime_id']}` / `{row['rule_id']}` rank `{row['rank']}`: "
        f"recall `{row['finite_recall']}`, median error "
        f"`{row['median_absolute_error']}`, large errors "
        f"`{row['large_error_count']}`, loss `{row['loss']}`"
        for row in result.rule_regime_ranking_rows
        if csv_int(row["rank"]) == 1
    )
    gate_lines = "\n".join(
        f"- `{check.name}`: `{'passed' if check.passed else 'failed'}`"
        for check in result.verification_checks
    )
    summary = result.summary_dict()
    return f"""# Synth-Medium Response Reconstruction Benchmark

## Boundary

This response-only reconstruction benchmark is synthetic-only and review-only.
It consumes the accepted Goal 017 landscape, Goal 018 spread-impact truth, and
Goal 019 observation design. The rules are benchmark diagnostics, not
production reconstruction-rule adoption. Truth is used only in synthetic audit
tables after response-only reconstructed times are built.

No fitting, ABC/POM/likelihood/MCMC/posterior work, parameter recovery,
real-data analysis, remote compute, production rule adoption, or follow-on goal
work is performed.

## Summary

- Selected default regime: `{result.config.selected_default_regime_id}`
- Primary default rule: `{summary["primary_default_rule_id"]}`
- Recommendation: `{result.recommendation_class}`
- Benchmark positive-control status:
  `{summary["benchmark_positive_control_status"]}`
- Default best finite recall: `{summary["default_best_finite_recall"]}`
- Default best median absolute error:
  `{summary["default_best_median_absolute_error"]}`
- Default best large-error count: `{summary["default_best_large_error_count"]}`

## Best Rule By Regime

{ranking_lines}

## Review Gates

{gate_lines}

## Visual Review Files

{visual_lines}

## Visual Decode Keys

- `truth_response_time.svg` shows the fixed Goal 018 prey response/extirpation
  truth. Grey cells have no finite truth.
- `default_primary_reconstructed_time.svg` shows the selected default regime
  under the best-ranked default benchmark rule.
- `default_primary_residual_error.svg` shows early bias, small errors, and
  late bias for finite truth/reconstruction comparisons.
- `default_primary_support_gap.svg` shows response-only support classes:
  never surveyed, no detection history, no final absence support, and finite
  reconstruction support.
- `regime_rule_comparison_montage.svg` is a bounded comparison table with
  visible labels, values, and bars for recall, median error, large errors, and
  loss.
"""


def source_reconciliation(
    source: SynthMediumObservationDesignResult,
) -> dict[str, dict[str, object]]:
    truth_summary = source.truth.summary_dict()
    landscape_summary = source.truth.landscape.summary_dict()
    observation_summary = source.summary_dict()
    return {
        "landscape": {
            "cell_count": landscape_summary["cell_count"],
            "passable_cell_count": landscape_summary["passable_cell_count"],
            "water_cell_count": landscape_summary["water_cell_count"],
        },
        "spread_impact": {
            "selected_parameter_set_id": truth_summary["selected_parameter_set_id"],
            "final_colonized_passable_count": truth_summary["final_colonized_passable_count"],
            "finite_prey_extirpation_count": truth_summary["finite_prey_extirpation_count"],
        },
        "observation_design": {
            "selected_default_regime_id": observation_summary["selected_default_regime_id"],
            "default_survey_record_count": observation_summary["default_survey_record_count"],
            "default_false_negative_count": observation_summary["default_false_negative_count"],
        },
    }


def passable_truth_rows(
    source: SynthMediumObservationDesignResult,
) -> tuple[SpreadImpactCellTruth, ...]:
    return tuple(
        row for row in source.truth.cell_truth_rows if row.landscape_cell.passability == "passable"
    )


def best_ranking_row(rows: tuple[CsvRow, ...], regime_id: str) -> CsvRow:
    return min(
        (row for row in rows if row["regime_id"] == regime_id),
        key=lambda row: csv_int(row["rank"]),
    )


def support_row(
    rows: tuple[CsvRow, ...],
    regime_id: str,
    rule_id: str,
    group: str,
) -> CsvRow:
    return next(
        row
        for row in rows
        if row["regime_id"] == regime_id
        and row["rule_id"] == rule_id
        and row["summary_group"] == group
    )


def classification(true_finite: bool, reconstructed_finite: bool) -> str:
    if true_finite and reconstructed_finite:
        return "true_positive"
    if true_finite and not reconstructed_finite:
        return "false_negative"
    if not true_finite and reconstructed_finite:
        return "false_positive"
    return "true_negative"


def error_class(signed_error: float | None, large_error_min: float) -> str:
    if signed_error is None:
        return "no_finite_comparison"
    if signed_error <= -large_error_min:
        return "early_large_error"
    if signed_error >= large_error_min:
        return "late_large_error"
    return "small_error"


def truth_time_fill(value: float | None) -> str:
    if value is None:
        return "#d1d5db"
    return interpolate_hex("#dbeafe", "#1d4ed8", clamp((value - 12.0) / 108.0, 0.0, 1.0))


def reconstructed_time_fill(row: CsvRow | None) -> str:
    if row is None or not csv_bool(row["reconstructed_finite"]):
        return "#d1d5db"
    value = csv_float(row["reconstructed_response_time"])
    return interpolate_hex("#dcfce7", "#166534", clamp((value - 12.0) / 108.0, 0.0, 1.0))


def residual_error_fill(row: CsvRow | None) -> str:
    if row is None or row["signed_error"] is None:
        return "#d1d5db"
    signed_error = csv_float(row["signed_error"])
    if signed_error < -24:
        return "#2563eb"
    if signed_error > 24:
        return "#dc2626"
    if signed_error < 0:
        return interpolate_hex("#f8fafc", "#2563eb", min(abs(signed_error) / 24, 1.0))
    return interpolate_hex("#f8fafc", "#dc2626", min(signed_error / 24, 1.0))


def support_gap_fill(row: CsvRow | None) -> str:
    if row is None:
        return "#ffffff"
    support = str(row["support_class"])
    if support == "never_surveyed":
        return "#d1d5db"
    if support == "no_detection_history":
        return "#f59e0b"
    if support == "finite_reconstruction_support":
        return "#15803d"
    return "#f97316"


def append_legend(
    lines: list[str],
    legend_id: str,
    x: int,
    y: int,
    items: tuple[LegendItem, ...],
    *,
    columns: int = 1,
    column_width: int = 290,
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
        lines.append(
            f'<rect x="{item_x}" y="{item_y - 10}" width="14" height="14" '
            f'fill="{color}" stroke="#334155" stroke-width="0.4" />'
        )
        lines.append(
            f'<text x="{item_x + 20}" y="{item_y + 1}" font-size="11" '
            f'font-family="monospace">{label}</text>'
        )
    lines.append("</g>")


def legend_bottom_y(y: int, items: tuple[LegendItem, ...], columns: int = 2) -> int:
    row_count = (len(items) + columns - 1) // columns
    return y + 18 + max(row_count - 1, 0) * 20 + 12


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f"<title>{title}</title>",
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]


def mean_or_none(values: list[float]) -> float | None:
    return round_float(mean(values)) if values else None


def quantile_or_none(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return round_float(ordered[0])
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return round_float(ordered[lower] + (ordered[upper] - ordered[lower]) * fraction)


def round_float(value: float) -> float:
    return round(value, 12)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def csv_int(value: CsvValue) -> int:
    if isinstance(value, bool) or value is None:
        raise TypeError(f"expected int-like value, got {value!r}")
    return int(value)


def csv_float(value: CsvValue) -> float:
    if isinstance(value, bool) or value is None:
        raise TypeError(f"expected float-like value, got {value!r}")
    return float(value)


def optional_float(value: CsvValue) -> float | None:
    if value is None or value == "":
        return None
    return csv_float(value)


def csv_bool(value: CsvValue) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)
