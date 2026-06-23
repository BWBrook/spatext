from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from json import dumps
from os import PathLike
from pathlib import Path

from .landscape import CsvRow, CsvValue, write_csv_rows
from .observations import (
    ObservationRegime,
    SynthMediumObservationDesignConfig,
    SynthMediumObservationDesignResult,
    build_cell_observation_summary_rows,
    build_regime_summary_rows,
    build_synth_medium_observation_design_review_pack,
    csv_float,
    csv_int,
    latent_prey_abundance_at_time,
    observed_count_for,
    observed_detected,
    round_float,
    stable_unit,
    survey_effort,
)
from .response_reconstruction import (
    ReconstructionRule,
    SynthMediumResponseReconstructionConfig,
    SynthMediumResponseReconstructionResult,
    best_ranking_row,
    build_reconstruction_error_summary_rows,
    build_support_gap_summary_rows,
    build_synth_medium_response_reconstruction_benchmark,
    build_truth_reconstruction_bridge_rows,
    default_reconstruction_rules,
    passable_truth_rows,
    ranking_loss,
    reconstruct_cell,
    residual_error_fill,
    support_gap_fill,
)
from .spread_impact import SpreadImpactCellTruth

DEFAULT_SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_DIR = Path(
    "artifacts/synth_medium_observation_design_counterfactual_screen"
)
SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_FILES = (
    "counterfactual_screen_config.json",
    "counterfactual_regime_definitions.csv",
    "counterfactual_observation_summary.csv",
    "counterfactual_reconstruction_rankings.csv",
    "counterfactual_support_gap_summary.csv",
    "counterfactual_error_summary.csv",
    "baseline_to_counterfactual_delta.csv",
    "recoverability_decision_summary.csv",
    "verification.json",
    "report.md",
)
SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES = (
    "recoverability_decision_montage.svg",
    "support_gap_comparison_montage.svg",
    "residual_comparison_baseline_best.svg",
    "baseline_to_best_plausible_delta.svg",
    "ceiling_comparison_panel.svg",
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "synth_medium_landscape_source_verified": True,
    "synth_medium_spread_impact_source_verified": True,
    "synth_medium_observation_design_source_verified": True,
    "synth_medium_response_reconstruction_source_verified": True,
    "observation_design_counterfactual_screen_only": True,
    "response_only_observation_counterfactuals": True,
    "response_only_reconstruction_benchmark_reused": True,
    "published_baseline_preserved": True,
    "ceiling_regime_is_diagnostic_only": True,
    "visual_review_required": True,
    "no_production_observation_design_adoption": True,
    "no_production_reconstruction_rule_adoption": True,
    "no_abc_pom_likelihood_or_posterior": True,
    "no_real_data": True,
}

BASELINE_REGIME_ID = "structured_response_observed_default"
BASELINE_RULE_ID = "final_absence_run_1"
CEILING_REGIME_ID = "near_perfect_response_observation_ceiling"

RESPONSE_RECONSTRUCTION_EXPECTATIONS: CsvRow = {
    "primary_default_rule_id": BASELINE_RULE_ID,
    "default_finite_recall": 0.524364653765,
    "default_false_negative_count": 2040,
    "default_false_positive_count": 304,
    "default_large_error_count": 809,
    "recommendation_class": "observation_design_not_recoverable_enough_for_backfitting",
}

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
        "selected_default_regime_id": BASELINE_REGIME_ID,
        "default_survey_record_count": 21258,
        "default_false_negative_count": 2313,
    },
    "response_reconstruction": RESPONSE_RECONSTRUCTION_EXPECTATIONS,
}

REGIME_DEFINITION_COLUMNS = (
    "regime_id",
    "regime_role",
    "plausibility_class",
    "counterfactual_class",
    "source_regime_id",
    "response_observable_trigger",
    "additional_support_semantics",
    "interpretation",
)
OBSERVATION_SUMMARY_COLUMNS = (
    "regime_id",
    "regime_role",
    "plausibility_class",
    "counterfactual_class",
    "record_count",
    "record_count_delta_from_baseline",
    "surveyed_cell_count",
    "surveyed_cell_count_delta_from_baseline",
    "post_impact_support_count",
    "post_impact_support_fraction",
    "post_impact_support_delta_from_baseline",
    "detection_history_support_count",
    "detection_history_support_delta_from_baseline",
    "final_absence_support_count",
    "final_absence_support_delta_from_baseline",
    "false_negative_count",
    "false_negative_delta_from_baseline",
    "mean_survey_count",
    "mean_effort",
)
RANKING_COLUMNS = (
    "regime_id",
    "rule_id",
    "rank",
    "regime_role",
    "plausibility_class",
    "counterfactual_class",
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
    "finite_recall_delta_from_baseline",
    "false_negative_delta_from_baseline",
    "large_error_delta_from_baseline",
    "loss_delta_from_baseline",
    "recommendation_class",
    "regime_recommendation_class",
)
SUPPORT_GAP_COLUMNS = (
    "regime_id",
    "rule_id",
    "summary_group",
    "regime_role",
    "plausibility_class",
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
ERROR_SUMMARY_COLUMNS = (
    "regime_id",
    "rule_id",
    "summary_group",
    "regime_role",
    "plausibility_class",
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
DELTA_COLUMNS = (
    "regime_id",
    "rule_id",
    "regime_role",
    "plausibility_class",
    "counterfactual_class",
    "baseline_regime_id",
    "baseline_rule_id",
    "finite_recall_delta",
    "false_negative_delta",
    "false_positive_delta",
    "median_absolute_error_delta",
    "p90_absolute_error_delta",
    "large_error_delta",
    "loss_delta",
    "record_count_delta",
    "surveyed_cell_count_delta",
    "final_absence_support_delta",
    "interpretation",
)
DECISION_COLUMNS = (
    "decision_id",
    "recommendation_class",
    "baseline_regime_id",
    "baseline_rule_id",
    "baseline_finite_recall",
    "baseline_false_negative_count",
    "baseline_large_error_count",
    "best_plausible_regime_id",
    "best_plausible_rule_id",
    "best_plausible_finite_recall",
    "best_plausible_false_negative_count",
    "best_plausible_large_error_count",
    "best_plausible_ready_for_reconstruction_review",
    "ceiling_regime_id",
    "ceiling_rule_id",
    "ceiling_finite_recall",
    "ceiling_false_negative_count",
    "ceiling_ready_for_reconstruction_review",
    "interpretation",
)

LegendItem = tuple[str, str]

SUPPORT_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#d1d5db", "Never surveyed"),
    ("#f59e0b", "No detection history"),
    ("#f97316", "No final absence support"),
    ("#15803d", "Finite reconstruction support"),
)
RESIDUAL_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#d1d5db", "No finite comparison"),
    ("#2563eb", "Early bias"),
    ("#f8fafc", "Small error"),
    ("#dc2626", "Late bias"),
)
DELTA_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#d1d5db", "No change / no finite truth"),
    ("#15803d", "Improved from baseline"),
    ("#f59e0b", "Changed but still unresolved"),
    ("#dc2626", "Worse than baseline"),
)


@dataclass(frozen=True, slots=True)
class CounterfactualRegimeDefinition:
    regime_id: str
    regime_role: str
    plausibility_class: str
    counterfactual_class: str
    source_regime_id: str
    response_observable_trigger: str
    additional_support_semantics: str
    interpretation: str

    def to_csv_row(self) -> CsvRow:
        return {
            "regime_id": self.regime_id,
            "regime_role": self.regime_role,
            "plausibility_class": self.plausibility_class,
            "counterfactual_class": self.counterfactual_class,
            "source_regime_id": self.source_regime_id,
            "response_observable_trigger": self.response_observable_trigger,
            "additional_support_semantics": self.additional_support_semantics,
            "interpretation": self.interpretation,
        }

    def as_observation_regime(self) -> ObservationRegime:
        return ObservationRegime(
            regime_id=self.regime_id,
            regime_role=self.regime_role,
            selected_default=self.regime_id == BASELINE_REGIME_ID,
            is_benchmark_only=self.plausibility_class == "unrealistic_diagnostic_ceiling",
            survey_times=tuple(range(0, 121, 12)),
            frame_probability=1.0,
            visit_probability=1.0,
            effort_scale=1.0,
            detection_scale=1.0,
            post_impact_gap_strength=0.0,
            perfect_observability=self.plausibility_class == "unrealistic_diagnostic_ceiling",
            rationale=self.interpretation,
        )


@dataclass(frozen=True, slots=True)
class SynthMediumObservationDesignCounterfactualConfig:
    selected_baseline_regime_id: str = BASELINE_REGIME_ID
    primary_benchmark_rule_id: str = BASELINE_RULE_ID
    large_error_min: float = 24.0
    plausible_ready_finite_recall_min: float = 0.72
    plausible_ready_false_negative_max: int = 900
    plausible_ready_median_abs_error_max: float = 16.0
    plausible_ready_large_error_count_max: int = 520
    meaningful_recall_improvement_min: float = 0.05

    def to_dict(self) -> dict[str, object]:
        return {
            "selected_baseline_regime_id": self.selected_baseline_regime_id,
            "primary_benchmark_rule_id": self.primary_benchmark_rule_id,
            "large_error_min": self.large_error_min,
            "review_gate_thresholds": {
                "plausible_ready_finite_recall_min": self.plausible_ready_finite_recall_min,
                "plausible_ready_false_negative_max": self.plausible_ready_false_negative_max,
                "plausible_ready_median_abs_error_max": (self.plausible_ready_median_abs_error_max),
                "plausible_ready_large_error_count_max": (
                    self.plausible_ready_large_error_count_max
                ),
                "meaningful_recall_improvement_min": self.meaningful_recall_improvement_min,
            },
            "output_files": list(SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_FILES),
            "visual_files": [
                f"visuals/{name}"
                for name in SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES
            ],
            **BOUNDARY_LABELS,
        }


@dataclass(frozen=True, slots=True)
class ObservationDesignCounterfactualCheck:
    name: str
    passed: bool
    details: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "details": self.details}


@dataclass(frozen=True, slots=True)
class SynthMediumObservationDesignCounterfactualResult:
    config: SynthMediumObservationDesignCounterfactualConfig
    observation_design: SynthMediumObservationDesignResult
    regimes: tuple[CounterfactualRegimeDefinition, ...]
    rules: tuple[ReconstructionRule, ...]
    observation_summary_rows: tuple[CsvRow, ...]
    reconstructed_cell_rows: tuple[CsvRow, ...]
    truth_reconstruction_bridge_rows: tuple[CsvRow, ...]
    reconstruction_error_summary_rows: tuple[CsvRow, ...]
    support_gap_summary_rows: tuple[CsvRow, ...]
    ranking_rows: tuple[CsvRow, ...]
    delta_rows: tuple[CsvRow, ...]
    decision_rows: tuple[CsvRow, ...]
    verification_checks: tuple[ObservationDesignCounterfactualCheck, ...]
    visual_svgs: dict[str, str]
    source_reconstruction_summary: dict[str, object]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    @property
    def recommendation_class(self) -> str:
        return str(self.decision_rows[0]["recommendation_class"])

    def summary_dict(self) -> dict[str, object]:
        baseline = baseline_ranking_row(self.ranking_rows)
        best_plausible = best_plausible_row(self.ranking_rows)
        ceiling = best_ranking_row(self.ranking_rows, CEILING_REGIME_ID)
        return {
            "baseline_regime_id": self.config.selected_baseline_regime_id,
            "baseline_rule_id": self.config.primary_benchmark_rule_id,
            "regime_count": len(self.regimes),
            "rule_count": len(self.rules),
            "baseline_finite_recall": baseline["finite_recall"],
            "baseline_false_negative_count": baseline["false_negative_count"],
            "best_plausible_regime_id": best_plausible["regime_id"],
            "best_plausible_rule_id": best_plausible["rule_id"],
            "best_plausible_finite_recall": best_plausible["finite_recall"],
            "best_plausible_false_negative_count": best_plausible["false_negative_count"],
            "ceiling_rule_id": ceiling["rule_id"],
            "ceiling_finite_recall": ceiling["finite_recall"],
            "ceiling_false_negative_count": ceiling["false_negative_count"],
            "recommendation_class": self.recommendation_class,
        }

    def config_payload(self) -> dict[str, object]:
        return {
            **self.config.to_dict(),
            "source_reconciliation": source_reconciliation(
                self.observation_design,
                self.source_reconstruction_summary,
            ),
            "counterfactual_regimes": [regime.to_csv_row() for regime in self.regimes],
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

        config_path = target_dir / "counterfactual_screen_config.json"
        config_path.write_text(
            dumps(self.config_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(config_path)

        table_specs: tuple[tuple[str, tuple[str, ...], tuple[CsvRow, ...]], ...] = (
            (
                "counterfactual_regime_definitions.csv",
                REGIME_DEFINITION_COLUMNS,
                tuple(regime.to_csv_row() for regime in self.regimes),
            ),
            (
                "counterfactual_observation_summary.csv",
                OBSERVATION_SUMMARY_COLUMNS,
                self.observation_summary_rows,
            ),
            (
                "counterfactual_reconstruction_rankings.csv",
                RANKING_COLUMNS,
                self.ranking_rows,
            ),
            (
                "counterfactual_support_gap_summary.csv",
                SUPPORT_GAP_COLUMNS,
                self.support_gap_summary_rows,
            ),
            (
                "counterfactual_error_summary.csv",
                ERROR_SUMMARY_COLUMNS,
                self.reconstruction_error_summary_rows,
            ),
            ("baseline_to_counterfactual_delta.csv", DELTA_COLUMNS, self.delta_rows),
            (
                "recoverability_decision_summary.csv",
                DECISION_COLUMNS,
                self.decision_rows,
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
        report_path.write_text(
            render_observation_design_counterfactual_report(self),
            encoding="utf-8",
        )
        written.append(report_path)

        for visual_name in SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES:
            path = visuals_dir / visual_name
            path.write_text(self.visual_svgs[visual_name], encoding="utf-8")
            written.append(path)

        return tuple(written)


def build_synth_medium_observation_design_counterfactual_screen(
    config: SynthMediumObservationDesignCounterfactualConfig | None = None,
    *,
    observation_design: SynthMediumObservationDesignResult | None = None,
) -> SynthMediumObservationDesignCounterfactualResult:
    screen_config = config or SynthMediumObservationDesignCounterfactualConfig()
    source = observation_design or build_synth_medium_observation_design_review_pack()
    baseline_benchmark = build_synth_medium_response_reconstruction_benchmark(
        observation_design=source
    )
    source_reconstruction_summary = response_reconstruction_source_summary(baseline_benchmark)
    regimes = default_counterfactual_regimes()
    rules = default_reconstruction_rules()
    observation_rows_by_regime = build_counterfactual_observation_rows(source, regimes)
    passable_truth = passable_truth_rows(source)

    reconstructed_rows = build_counterfactual_reconstructed_rows(
        regimes,
        rules,
        passable_truth,
        observation_rows_by_regime,
    )
    bridge_rows = build_truth_reconstruction_bridge_rows(
        source,
        reconstructed_rows,
        SynthMediumResponseReconstructionConfig(large_error_min=screen_config.large_error_min),
    )
    error_rows = annotate_error_rows(
        build_reconstruction_error_summary_rows(
            bridge_rows,
            SynthMediumResponseReconstructionConfig(large_error_min=screen_config.large_error_min),
        ),
        regimes,
    )
    support_rows = annotate_support_rows(
        build_support_gap_summary_rows(reconstructed_rows),
        regimes,
    )
    ranking_rows = build_counterfactual_ranking_rows(
        error_rows,
        regimes,
        screen_config,
    )
    observation_summary_rows = build_counterfactual_observation_summary_rows(
        source,
        regimes,
        observation_rows_by_regime,
        support_rows,
        reconstructed_rows,
    )
    delta_rows = build_baseline_delta_rows(
        ranking_rows,
        observation_summary_rows,
        support_rows,
        regimes,
    )
    decision_rows = build_decision_rows(ranking_rows, screen_config)
    visual_svgs = build_counterfactual_visual_svgs(
        source,
        reconstructed_rows,
        bridge_rows,
        ranking_rows,
    )
    checks = verify_counterfactual_result(
        screen_config,
        source,
        source_reconstruction_summary,
        regimes,
        rules,
        observation_summary_rows,
        reconstructed_rows,
        bridge_rows,
        error_rows,
        support_rows,
        ranking_rows,
        delta_rows,
        decision_rows,
        visual_svgs,
    )
    return SynthMediumObservationDesignCounterfactualResult(
        config=screen_config,
        observation_design=source,
        regimes=regimes,
        rules=rules,
        observation_summary_rows=observation_summary_rows,
        reconstructed_cell_rows=reconstructed_rows,
        truth_reconstruction_bridge_rows=bridge_rows,
        reconstruction_error_summary_rows=error_rows,
        support_gap_summary_rows=support_rows,
        ranking_rows=ranking_rows,
        delta_rows=delta_rows,
        decision_rows=decision_rows,
        verification_checks=checks,
        visual_svgs=visual_svgs,
        source_reconstruction_summary=source_reconstruction_summary,
    )


def default_counterfactual_regimes() -> tuple[CounterfactualRegimeDefinition, ...]:
    return (
        CounterfactualRegimeDefinition(
            regime_id=BASELINE_REGIME_ID,
            regime_role="published_baseline",
            plausibility_class="published_baseline",
            counterfactual_class="baseline",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger="published Goal 019 default observation records",
            additional_support_semantics="no added records; exact baseline reconciliation",
            interpretation=(
                "Published Goal 019 default and Goal 020 benchmark result preserved as "
                "the fixed comparison baseline."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id="post_impact_followup_boost",
            regime_role="counterfactual",
            plausibility_class="plausible_field_like",
            counterfactual_class="post_impact_followup",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger=(
                "cells with detection history receive bounded late follow-up survey support"
            ),
            additional_support_semantics=(
                "adds at most three late follow-up surveys after detection"
            ),
            interpretation=(
                "Tests whether field-like late follow-up after observed occupancy can "
                "recover final-absence support."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id="final_absence_confirmation_support",
            regime_role="counterfactual",
            plausibility_class="plausible_field_like",
            counterfactual_class="final_absence_confirmation",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger=(
                "baseline cells with detection history but insufficient post-detection "
                "absence support"
            ),
            additional_support_semantics="adds two confirmation visits after last detection",
            interpretation=(
                "Targets the direct Goal 020 support gap without using hidden truth to "
                "select cells."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id="weak_area_targeted_support",
            regime_role="counterfactual",
            plausibility_class="plausible_field_like",
            counterfactual_class="weak_area_coverage",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger=(
                "low-quality matrix and west/east band cells highlighted by published "
                "support/error diagnostics"
            ),
            additional_support_semantics="adds deterministic extra waves in weakly recovered areas",
            interpretation=(
                "Tests whether targeted response-observable weak-area support can close "
                "the matrix and region gaps."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id="balanced_habitat_region_support",
            regime_role="counterfactual",
            plausibility_class="plausible_field_like",
            counterfactual_class="balanced_spatial_stratification",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger=(
                "balanced deterministic sampling across habitat class and column-band strata"
            ),
            additional_support_semantics="adds moderate stratified survey support across groups",
            interpretation=(
                "Tests whether broad but still imperfect stratified effort reduces spatial "
                "bias enough for reconstruction review."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id=CEILING_REGIME_ID,
            regime_role="diagnostic_ceiling",
            plausibility_class="unrealistic_diagnostic_ceiling",
            counterfactual_class="near_perfect_ceiling",
            source_regime_id="truth_reference_full_observability",
            response_observable_trigger=(
                "complete benchmark-style response visibility; not a field-like design"
            ),
            additional_support_semantics=(
                "copies the full-observability benchmark under a ceiling label"
            ),
            interpretation=(
                "Synthetic diagnostic upper bound only. It must not be used to claim a "
                "plausible observation design is ready."
            ),
        ),
    )


def build_counterfactual_observation_rows(
    source: SynthMediumObservationDesignResult,
    regimes: tuple[CounterfactualRegimeDefinition, ...],
) -> dict[str, tuple[CsvRow, ...]]:
    base_rows = [
        row for row in source.observation_record_rows if row["regime_id"] == BASELINE_REGIME_ID
    ]
    full_rows = [
        row
        for row in source.observation_record_rows
        if row["regime_id"] == "truth_reference_full_observability"
    ]
    passable_truth = passable_truth_rows(source)
    baseline_summary = {
        csv_int(row["cell_id"]): row
        for row in source.cell_observation_summary_rows
        if row["regime_id"] == BASELINE_REGIME_ID
    }
    baseline_reconstructed = baseline_reconstruction_by_cell(source)

    rows_by_regime: dict[str, tuple[CsvRow, ...]] = {}
    for regime in regimes:
        if regime.regime_id == BASELINE_REGIME_ID:
            rows_by_regime[regime.regime_id] = tuple(copy_rows_for_regime(base_rows, regime))
            continue
        if regime.regime_id == CEILING_REGIME_ID:
            rows_by_regime[regime.regime_id] = tuple(copy_rows_for_regime(full_rows, regime))
            continue

        copied_rows = list(copy_rows_for_regime(base_rows, regime))
        copied_rows.extend(
            build_added_counterfactual_rows(
                source.config,
                regime,
                passable_truth,
                baseline_summary,
                baseline_reconstructed,
                copied_rows,
            )
        )
        rows_by_regime[regime.regime_id] = tuple(
            sorted(
                copied_rows,
                key=lambda row: (
                    csv_int(row["cell_id"]),
                    csv_int(row["time"]),
                    str(row["survey_id"]),
                ),
            )
        )
    return rows_by_regime


def copy_rows_for_regime(
    rows: list[CsvRow],
    regime: CounterfactualRegimeDefinition,
) -> list[CsvRow]:
    copied: list[CsvRow] = []
    for index, row in enumerate(rows, start=1):
        copied.append(
            {
                **row,
                "regime_id": regime.regime_id,
                "survey_id": f"{regime.regime_id}_base_{index:06d}",
            }
        )
    return copied


def baseline_reconstruction_by_cell(
    source: SynthMediumObservationDesignResult,
) -> dict[int, CsvRow]:
    rules = default_reconstruction_rules()
    observations_by_cell: dict[int, list[CsvRow]] = defaultdict(list)
    for row in source.observation_record_rows:
        if row["regime_id"] == BASELINE_REGIME_ID:
            observations_by_cell[csv_int(row["cell_id"])].append(row)
    reconstructed: dict[int, CsvRow] = {}
    for truth_row in passable_truth_rows(source):
        row = reconstruct_cell(
            BASELINE_REGIME_ID,
            next(rule for rule in rules if rule.rule_id == BASELINE_RULE_ID),
            truth_row,
            sorted(
                observations_by_cell.get(truth_row.landscape_cell.cell_id, []),
                key=lambda value: csv_int(value["time"]),
            ),
        )
        reconstructed[truth_row.landscape_cell.cell_id] = row
    return reconstructed


def build_added_counterfactual_rows(
    config: SynthMediumObservationDesignConfig,
    regime: CounterfactualRegimeDefinition,
    passable_truth: tuple[SpreadImpactCellTruth, ...],
    baseline_summary: dict[int, CsvRow],
    baseline_reconstructed: dict[int, CsvRow],
    existing_rows: list[CsvRow],
) -> list[CsvRow]:
    existing_times = {(csv_int(row["cell_id"]), csv_int(row["time"])) for row in existing_rows}
    rows: list[CsvRow] = []
    observation_regime = observation_regime_for_counterfactual(regime)
    next_index = len(existing_rows) + 1
    for truth_row in passable_truth:
        cell_id = truth_row.landscape_cell.cell_id
        times = added_times_for_cell(
            regime, truth_row, baseline_summary[cell_id], baseline_reconstructed[cell_id]
        )
        for time in times:
            if (cell_id, time) in existing_times:
                continue
            rows.append(
                build_observation_row(
                    config,
                    observation_regime,
                    truth_row,
                    time,
                    next_index,
                )
            )
            existing_times.add((cell_id, time))
            next_index += 1
    return rows


def observation_regime_for_counterfactual(
    definition: CounterfactualRegimeDefinition,
) -> ObservationRegime:
    effort_scale = {
        "post_impact_followup": 1.12,
        "final_absence_confirmation": 1.10,
        "weak_area_coverage": 1.08,
        "balanced_spatial_stratification": 1.02,
    }.get(definition.counterfactual_class, 1.0)
    detection_scale = {
        "post_impact_followup": 0.88,
        "final_absence_confirmation": 0.86,
        "weak_area_coverage": 0.84,
        "balanced_spatial_stratification": 0.82,
    }.get(definition.counterfactual_class, 1.0)
    return ObservationRegime(
        regime_id=definition.regime_id,
        regime_role=definition.regime_role,
        selected_default=False,
        is_benchmark_only=False,
        survey_times=tuple(range(0, 121, 12)),
        frame_probability=1.0,
        visit_probability=1.0,
        effort_scale=effort_scale,
        detection_scale=detection_scale,
        post_impact_gap_strength=0.0,
        perfect_observability=False,
        rationale=definition.interpretation,
    )


def added_times_for_cell(
    regime: CounterfactualRegimeDefinition,
    truth_row: SpreadImpactCellTruth,
    baseline_summary: CsvRow,
    baseline_reconstructed: CsvRow,
) -> tuple[int, ...]:
    cell = truth_row.landscape_cell
    detection_count = csv_int(baseline_summary["detection_count"])
    last_detection = optional_int(baseline_summary["last_detection_time"])
    if regime.counterfactual_class == "post_impact_followup":
        if detection_count == 0 or last_detection is None:
            return ()
        return tuple(
            time
            for time in (last_detection + 12, last_detection + 24, last_detection + 36)
            if 0 <= time <= 120
        )
    if regime.counterfactual_class == "final_absence_confirmation":
        status = str(baseline_reconstructed["reconstruction_status"])
        if detection_count == 0 or last_detection is None:
            return ()
        if status not in {"no_post_detection_survey", "short_final_absence_run"}:
            return ()
        return tuple(time for time in (last_detection + 12, last_detection + 24) if time <= 120)
    if regime.counterfactual_class == "weak_area_coverage":
        weak_area = cell.habitat_class == "low_quality_matrix" or cell.col_band in {
            "west_band",
            "east_band",
        }
        if not weak_area:
            return ()
        if stable_unit(20260621, regime.regime_id, cell.cell_id, 7) > 0.68:
            return ()
        return (36, 60, 84, 108, 120)
    if regime.counterfactual_class == "balanced_spatial_stratification":
        if stable_unit(20260621, regime.regime_id, cell.cell_id, 11) > 0.46:
            return ()
        return (24, 48, 72, 96, 120)
    return ()


def build_observation_row(
    config: SynthMediumObservationDesignConfig,
    regime: ObservationRegime,
    truth_row: SpreadImpactCellTruth,
    time: int,
    survey_index: int,
) -> CsvRow:
    effort = survey_effort(config, regime, truth_row, time)
    latent_abundance = latent_prey_abundance_at_time(truth_row, float(time))
    detected = observed_detected(config, regime, truth_row, time, effort, latent_abundance)
    observed_count = observed_count_for(
        config,
        regime,
        truth_row,
        time,
        effort,
        latent_abundance,
        detected,
    )
    cell = truth_row.landscape_cell
    return {
        "regime_id": regime.regime_id,
        "survey_id": f"{regime.regime_id}_added_{survey_index:06d}",
        "cell_id": cell.cell_id,
        "row": cell.row,
        "col": cell.col,
        "time": time,
        "effort": effort,
        "passability": cell.passability,
        "observed_count": observed_count,
        "detected": detected,
    }


def build_counterfactual_reconstructed_rows(
    regimes: tuple[CounterfactualRegimeDefinition, ...],
    rules: tuple[ReconstructionRule, ...],
    passable_truth: tuple[SpreadImpactCellTruth, ...],
    observation_rows_by_regime: dict[str, tuple[CsvRow, ...]],
) -> tuple[CsvRow, ...]:
    rows: list[CsvRow] = []
    for regime in regimes:
        observations_by_cell: dict[int, list[CsvRow]] = defaultdict(list)
        for row in observation_rows_by_regime[regime.regime_id]:
            observations_by_cell[csv_int(row["cell_id"])].append(row)
        for rule in rules:
            for truth_row in passable_truth:
                rows.append(
                    reconstruct_cell(
                        regime.regime_id,
                        rule,
                        truth_row,
                        sorted(
                            observations_by_cell.get(truth_row.landscape_cell.cell_id, []),
                            key=lambda value: csv_int(value["time"]),
                        ),
                    )
                )
    return tuple(rows)


def annotate_error_rows(
    rows: tuple[CsvRow, ...],
    regimes: tuple[CounterfactualRegimeDefinition, ...],
) -> tuple[CsvRow, ...]:
    regime_map = {regime.regime_id: regime for regime in regimes}
    return tuple(
        {
            **row,
            "regime_role": regime_map[str(row["regime_id"])].regime_role,
            "plausibility_class": regime_map[str(row["regime_id"])].plausibility_class,
        }
        for row in rows
    )


def annotate_support_rows(
    rows: tuple[CsvRow, ...],
    regimes: tuple[CounterfactualRegimeDefinition, ...],
) -> tuple[CsvRow, ...]:
    regime_map = {regime.regime_id: regime for regime in regimes}
    return tuple(
        {
            **row,
            "regime_role": regime_map[str(row["regime_id"])].regime_role,
            "plausibility_class": regime_map[str(row["regime_id"])].plausibility_class,
        }
        for row in rows
    )


def build_counterfactual_ranking_rows(
    error_rows: tuple[CsvRow, ...],
    regimes: tuple[CounterfactualRegimeDefinition, ...],
    config: SynthMediumObservationDesignCounterfactualConfig,
) -> tuple[CsvRow, ...]:
    regime_map = {regime.regime_id: regime for regime in regimes}
    all_rows = [row for row in error_rows if row["summary_group"] == "all_passable"]
    by_regime: dict[str, list[CsvRow]] = defaultdict(list)
    for row in all_rows:
        by_regime[str(row["regime_id"])].append(row)
    provisional: dict[str, list[tuple[float, CsvRow]]] = {}
    for regime_id, rows in by_regime.items():
        scored = [(ranking_loss(row), row) for row in rows]
        scored.sort(key=lambda item: (item[0], str(item[1]["rule_id"])))
        provisional[regime_id] = scored
    baseline_row = next(
        row
        for loss, row in provisional[config.selected_baseline_regime_id]
        if row["rule_id"] == config.primary_benchmark_rule_id
    )
    baseline_loss = ranking_loss(baseline_row)
    ranked_rows: list[CsvRow] = []
    for regime in regimes:
        for rank, (loss, row) in enumerate(provisional[regime.regime_id], start=1):
            recommendation_class = regime_recommendation_class(
                row,
                loss,
                regime_map[str(row["regime_id"])],
                config,
            )
            ranked_rows.append(
                {
                    "regime_id": regime.regime_id,
                    "rule_id": row["rule_id"],
                    "rank": rank,
                    "regime_role": regime.regime_role,
                    "plausibility_class": regime.plausibility_class,
                    "counterfactual_class": regime.counterfactual_class,
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
                    "finite_recall_delta_from_baseline": round_float(
                        csv_float(row["finite_recall"]) - csv_float(baseline_row["finite_recall"])
                    ),
                    "false_negative_delta_from_baseline": (
                        csv_int(row["false_negative_count"])
                        - csv_int(baseline_row["false_negative_count"])
                    ),
                    "large_error_delta_from_baseline": (
                        csv_int(row["large_error_count"])
                        - csv_int(baseline_row["large_error_count"])
                    ),
                    "loss_delta_from_baseline": round_float(loss - baseline_loss),
                    "recommendation_class": recommendation_class,
                    "regime_recommendation_class": recommendation_class,
                }
            )
    return tuple(ranked_rows)


def regime_recommendation_class(
    row: CsvRow,
    loss: float,
    regime: CounterfactualRegimeDefinition,
    config: SynthMediumObservationDesignCounterfactualConfig,
) -> str:
    if regime.regime_id == config.selected_baseline_regime_id:
        return str(RESPONSE_RECONSTRUCTION_EXPECTATIONS["recommendation_class"])
    ready = (
        csv_float(row["finite_recall"]) >= config.plausible_ready_finite_recall_min
        and csv_int(row["false_negative_count"]) <= config.plausible_ready_false_negative_max
        and csv_float(row["median_absolute_error"]) <= config.plausible_ready_median_abs_error_max
        and csv_int(row["large_error_count"]) <= config.plausible_ready_large_error_count_max
    )
    if regime.plausibility_class == "unrealistic_diagnostic_ceiling":
        return (
            "diagnostic_ceiling_recovers_signal"
            if csv_int(row["false_negative_count"]) == 0
            else "diagnostic_ceiling_failed"
        )
    if ready:
        return "response_reconstruction_ready_for_human_review"
    if csv_float(row["finite_recall"]) >= 0.60 and loss < 1.65:
        return "recoverability_improved_but_not_fit_ready"
    return "observation_design_not_recoverable_enough_for_backfitting"


def build_counterfactual_observation_summary_rows(
    source: SynthMediumObservationDesignResult,
    regimes: tuple[CounterfactualRegimeDefinition, ...],
    observation_rows_by_regime: dict[str, tuple[CsvRow, ...]],
    support_rows: tuple[CsvRow, ...],
    reconstructed_rows: tuple[CsvRow, ...],
) -> tuple[CsvRow, ...]:
    passable_truth = passable_truth_rows(source)
    observation_regimes = tuple(regime.as_observation_regime() for regime in regimes)
    truth_by_cell = {row.landscape_cell.cell_id: row for row in passable_truth}
    all_survey_rows: list[CsvRow] = []
    all_observation_rows: list[CsvRow] = []
    all_cell_summaries: list[CsvRow] = []
    for regime_def in regimes:
        observation_regime = regime_def.as_observation_regime()
        regime_rows = list(observation_rows_by_regime[regime_def.regime_id])
        all_survey_rows.extend(enrich_rows_as_survey_schedule(regime_rows, truth_by_cell))
        all_observation_rows.extend(regime_rows)
        all_cell_summaries.extend(
            build_cell_observation_summary_rows(observation_regime, passable_truth, regime_rows)
        )
    regime_summary = build_regime_summary_rows(
        observation_regimes,
        passable_truth,
        tuple(all_survey_rows),
        tuple(all_observation_rows),
        tuple(all_cell_summaries),
    )
    baseline_regime_summary = next(
        row for row in regime_summary if row["regime_id"] == BASELINE_REGIME_ID
    )
    baseline_support = support_row_for(support_rows, BASELINE_REGIME_ID, BASELINE_RULE_ID)
    baseline_reconstructed = [
        row
        for row in reconstructed_rows
        if row["regime_id"] == BASELINE_REGIME_ID and row["rule_id"] == BASELINE_RULE_ID
    ]
    baseline_detection_history = sum(
        csv_int(row["detection_count"]) > 0 for row in baseline_reconstructed
    )
    summary_rows: list[CsvRow] = []
    regime_map = {regime.regime_id: regime for regime in regimes}
    for summary in regime_summary:
        regime = regime_map[str(summary["regime_id"])]
        support = support_row_for(support_rows, regime.regime_id, BASELINE_RULE_ID)
        reconstructed = [
            row
            for row in reconstructed_rows
            if row["regime_id"] == regime.regime_id and row["rule_id"] == BASELINE_RULE_ID
        ]
        detection_history = sum(csv_int(row["detection_count"]) > 0 for row in reconstructed)
        summary_rows.append(
            {
                "regime_id": regime.regime_id,
                "regime_role": regime.regime_role,
                "plausibility_class": regime.plausibility_class,
                "counterfactual_class": regime.counterfactual_class,
                "record_count": summary["observation_record_count"],
                "record_count_delta_from_baseline": csv_int(summary["observation_record_count"])
                - csv_int(baseline_regime_summary["observation_record_count"]),
                "surveyed_cell_count": summary["surveyed_passable_count"],
                "surveyed_cell_count_delta_from_baseline": (
                    csv_int(summary["surveyed_passable_count"])
                    - csv_int(baseline_regime_summary["surveyed_passable_count"])
                ),
                "post_impact_support_count": summary["post_impact_support_count"],
                "post_impact_support_fraction": summary["post_impact_support_fraction"],
                "post_impact_support_delta_from_baseline": round_float(
                    csv_float(summary["post_impact_support_fraction"])
                    - csv_float(baseline_regime_summary["post_impact_support_fraction"])
                ),
                "detection_history_support_count": detection_history,
                "detection_history_support_delta_from_baseline": (
                    detection_history - baseline_detection_history
                ),
                "final_absence_support_count": support["post_detection_absence_supported_count"],
                "final_absence_support_delta_from_baseline": (
                    csv_int(support["post_detection_absence_supported_count"])
                    - csv_int(baseline_support["post_detection_absence_supported_count"])
                ),
                "false_negative_count": summary["false_negative_count"],
                "false_negative_delta_from_baseline": csv_int(summary["false_negative_count"])
                - csv_int(baseline_regime_summary["false_negative_count"]),
                "mean_survey_count": support["mean_survey_count"],
                "mean_effort": summary["mean_effort"],
            }
        )
    return tuple(summary_rows)


def enrich_rows_as_survey_schedule(
    rows: list[CsvRow],
    truth_by_cell: dict[int, SpreadImpactCellTruth],
) -> list[CsvRow]:
    enriched: list[CsvRow] = []
    for row in rows:
        truth_row = truth_by_cell[csv_int(row["cell_id"])]
        cell = truth_row.landscape_cell
        time = csv_int(row["time"])
        enriched.append(
            {
                **row,
                "habitat_class": cell.habitat_class,
                "row_band": cell.row_band,
                "col_band": cell.col_band,
                "sampling_frame_member": True,
                "post_impact_window": (
                    truth_row.prey_extirpation_time is not None
                    and float(time) >= truth_row.prey_extirpation_time
                ),
                "design_weight": 1.0,
            }
        )
    return enriched


def build_baseline_delta_rows(
    ranking_rows: tuple[CsvRow, ...],
    observation_summary_rows: tuple[CsvRow, ...],
    support_rows: tuple[CsvRow, ...],
    regimes: tuple[CounterfactualRegimeDefinition, ...],
) -> tuple[CsvRow, ...]:
    baseline = baseline_ranking_row(ranking_rows)
    baseline_obs = observation_summary_row(observation_summary_rows, BASELINE_REGIME_ID)
    baseline_support = support_row_for(support_rows, BASELINE_REGIME_ID, BASELINE_RULE_ID)
    rows: list[CsvRow] = []
    regime_map = {regime.regime_id: regime for regime in regimes}
    for row in ranking_rows:
        if row["rank"] != 1:
            continue
        obs = observation_summary_row(observation_summary_rows, str(row["regime_id"]))
        support = support_row_for(support_rows, str(row["regime_id"]), str(row["rule_id"]))
        regime = regime_map[str(row["regime_id"])]
        rows.append(
            {
                "regime_id": row["regime_id"],
                "rule_id": row["rule_id"],
                "regime_role": regime.regime_role,
                "plausibility_class": regime.plausibility_class,
                "counterfactual_class": regime.counterfactual_class,
                "baseline_regime_id": BASELINE_REGIME_ID,
                "baseline_rule_id": BASELINE_RULE_ID,
                "finite_recall_delta": row["finite_recall_delta_from_baseline"],
                "false_negative_delta": row["false_negative_delta_from_baseline"],
                "false_positive_delta": (
                    csv_int(row["false_positive_count"]) - csv_int(baseline["false_positive_count"])
                ),
                "median_absolute_error_delta": optional_delta(
                    row["median_absolute_error"], baseline["median_absolute_error"]
                ),
                "p90_absolute_error_delta": optional_delta(
                    row["p90_absolute_error"], baseline["p90_absolute_error"]
                ),
                "large_error_delta": row["large_error_delta_from_baseline"],
                "loss_delta": row["loss_delta_from_baseline"],
                "record_count_delta": csv_int(obs["record_count"])
                - csv_int(baseline_obs["record_count"]),
                "surveyed_cell_count_delta": csv_int(obs["surveyed_cell_count"])
                - csv_int(baseline_obs["surveyed_cell_count"]),
                "final_absence_support_delta": (
                    csv_int(support["post_detection_absence_supported_count"])
                    - csv_int(baseline_support["post_detection_absence_supported_count"])
                ),
                "interpretation": delta_interpretation(row, regime),
            }
        )
    return tuple(rows)


def build_decision_rows(
    ranking_rows: tuple[CsvRow, ...],
    config: SynthMediumObservationDesignCounterfactualConfig,
) -> tuple[CsvRow, ...]:
    baseline = baseline_ranking_row(ranking_rows)
    best_plausible = best_plausible_row(ranking_rows)
    ceiling = best_ranking_row(ranking_rows, CEILING_REGIME_ID)
    best_plausible_ready = (
        best_plausible["regime_recommendation_class"]
        == "response_reconstruction_ready_for_human_review"
    )
    ceiling_ready = ceiling["regime_recommendation_class"] == "diagnostic_ceiling_recovers_signal"
    if best_plausible_ready:
        recommendation = "plausible_observation_design_can_support_reconstruction_review"
        interpretation = (
            "A plausible counterfactual meets the deterministic reconstruction-review gates."
        )
    elif ceiling_ready:
        recommendation = "only_unrealistic_observation_ceiling_recovers_signal"
        interpretation = (
            "The diagnostic ceiling recovers signal, but plausible field-like designs remain "
            "below review gates; do not proceed to fitting from these response-only data."
        )
    elif (
        csv_float(best_plausible["finite_recall"])
        >= csv_float(baseline["finite_recall"]) + config.meaningful_recall_improvement_min
    ):
        recommendation = "needs_process_observation_model_before_fitting"
        interpretation = (
            "Plausible designs improve recall but leave too much structured support loss for "
            "a direct response-time reconstruction target."
        )
    else:
        recommendation = "observation_design_counterfactuals_still_not_recoverable"
        interpretation = (
            "Plausible counterfactual support does not materially improve the published baseline."
        )
    return (
        {
            "decision_id": "final_decision",
            "recommendation_class": recommendation,
            "baseline_regime_id": BASELINE_REGIME_ID,
            "baseline_rule_id": BASELINE_RULE_ID,
            "baseline_finite_recall": baseline["finite_recall"],
            "baseline_false_negative_count": baseline["false_negative_count"],
            "baseline_large_error_count": baseline["large_error_count"],
            "best_plausible_regime_id": best_plausible["regime_id"],
            "best_plausible_rule_id": best_plausible["rule_id"],
            "best_plausible_finite_recall": best_plausible["finite_recall"],
            "best_plausible_false_negative_count": best_plausible["false_negative_count"],
            "best_plausible_large_error_count": best_plausible["large_error_count"],
            "best_plausible_ready_for_reconstruction_review": best_plausible_ready,
            "ceiling_regime_id": CEILING_REGIME_ID,
            "ceiling_rule_id": ceiling["rule_id"],
            "ceiling_finite_recall": ceiling["finite_recall"],
            "ceiling_false_negative_count": ceiling["false_negative_count"],
            "ceiling_ready_for_reconstruction_review": ceiling_ready,
            "interpretation": interpretation,
        },
    )


def verify_counterfactual_result(
    config: SynthMediumObservationDesignCounterfactualConfig,
    source: SynthMediumObservationDesignResult,
    source_reconstruction_summary: dict[str, object],
    regimes: tuple[CounterfactualRegimeDefinition, ...],
    rules: tuple[ReconstructionRule, ...],
    observation_summary_rows: tuple[CsvRow, ...],
    reconstructed_rows: tuple[CsvRow, ...],
    bridge_rows: tuple[CsvRow, ...],
    error_rows: tuple[CsvRow, ...],
    support_rows: tuple[CsvRow, ...],
    ranking_rows: tuple[CsvRow, ...],
    delta_rows: tuple[CsvRow, ...],
    decision_rows: tuple[CsvRow, ...],
    visual_svgs: dict[str, str],
) -> tuple[ObservationDesignCounterfactualCheck, ...]:
    reconciliation = source_reconciliation(source, source_reconstruction_summary)
    baseline = baseline_ranking_row(ranking_rows)
    best_plausible = best_plausible_row(ranking_rows)
    ceiling = best_ranking_row(ranking_rows, CEILING_REGIME_ID)
    plausible = [
        regime for regime in regimes if regime.plausibility_class == "plausible_field_like"
    ]
    expected_reconstructed_rows = 5225 * len(regimes) * len(rules)
    expected_ranking_rows = len(regimes) * len(rules)
    return (
        ObservationDesignCounterfactualCheck(
            name="artifact_contract",
            passed=set(visual_svgs)
            == set(SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES)
            and all(
                svg.lstrip().startswith("<svg") and len(svg) > 1000 for svg in visual_svgs.values()
            ),
            details={
                "output_file_count": len(
                    SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_FILES
                ),
                "visual_file_count": len(visual_svgs),
            },
        ),
        ObservationDesignCounterfactualCheck(
            name="source_reconciliation",
            passed=reconciliation == SOURCE_EXPECTATIONS,
            details={"source_reconciliation": reconciliation},
        ),
        ObservationDesignCounterfactualCheck(
            name="published_baseline_reconciled",
            passed=baseline_matches_expectation(baseline),
            details={
                "primary_default_rule_id": baseline["rule_id"],
                "finite_recall": baseline["finite_recall"],
                "false_negative_count": baseline["false_negative_count"],
                "false_positive_count": baseline["false_positive_count"],
                "large_error_count": baseline["large_error_count"],
            },
        ),
        ObservationDesignCounterfactualCheck(
            name="counterfactual_regime_contract",
            passed=len(regimes) == 6
            and len(plausible) == 4
            and any(regime.regime_id == CEILING_REGIME_ID for regime in regimes)
            and len({row["regime_id"] for row in observation_summary_rows}) == len(regimes),
            details={
                "regime_count": len(regimes),
                "plausible_field_like_count": len(plausible),
                "regime_ids": [regime.regime_id for regime in regimes],
            },
        ),
        ObservationDesignCounterfactualCheck(
            name="plausible_counterfactuals_improve_baseline",
            passed=csv_float(best_plausible["finite_recall"])
            >= csv_float(baseline["finite_recall"]) + config.meaningful_recall_improvement_min
            and csv_int(best_plausible["false_negative_count"])
            < csv_int(baseline["false_negative_count"]),
            details={
                "best_plausible_regime_id": best_plausible["regime_id"],
                "baseline_finite_recall": baseline["finite_recall"],
                "best_plausible_finite_recall": best_plausible["finite_recall"],
                "baseline_false_negative_count": baseline["false_negative_count"],
                "best_plausible_false_negative_count": best_plausible["false_negative_count"],
            },
        ),
        ObservationDesignCounterfactualCheck(
            name="ceiling_is_separated_from_plausible_claims",
            passed=ceiling["plausibility_class"] == "unrealistic_diagnostic_ceiling"
            and csv_int(ceiling["false_negative_count"]) == 0
            and decision_rows[0]["ceiling_regime_id"] == CEILING_REGIME_ID,
            details={
                "ceiling_rule_id": ceiling["rule_id"],
                "ceiling_false_negative_count": ceiling["false_negative_count"],
                "decision_recommendation": decision_rows[0]["recommendation_class"],
            },
        ),
        ObservationDesignCounterfactualCheck(
            name="table_reconciliation",
            passed=len(reconstructed_rows) == expected_reconstructed_rows
            and len(bridge_rows) == len(reconstructed_rows)
            and len(ranking_rows) == expected_ranking_rows
            and len(delta_rows) == len(regimes)
            and bool(error_rows)
            and bool(support_rows),
            details={
                "expected_reconstructed_row_count": expected_reconstructed_rows,
                "reconstructed_row_count": len(reconstructed_rows),
                "bridge_row_count": len(bridge_rows),
                "expected_ranking_row_count": expected_ranking_rows,
                "ranking_row_count": len(ranking_rows),
            },
        ),
        ObservationDesignCounterfactualCheck(
            name="visual_contract",
            passed=visual_contract_passes(visual_svgs),
            details={"visual_files": sorted(visual_svgs)},
        ),
    )


def build_counterfactual_visual_svgs(
    source: SynthMediumObservationDesignResult,
    reconstructed_rows: tuple[CsvRow, ...],
    bridge_rows: tuple[CsvRow, ...],
    ranking_rows: tuple[CsvRow, ...],
) -> dict[str, str]:
    baseline = baseline_ranking_row(ranking_rows)
    best_plausible = best_plausible_row(ranking_rows)
    ceiling = best_ranking_row(ranking_rows, CEILING_REGIME_ID)
    return {
        "recoverability_decision_montage.svg": render_recoverability_decision_montage(ranking_rows),
        "support_gap_comparison_montage.svg": render_support_gap_comparison_montage(
            source,
            reconstructed_rows,
            (
                ("Baseline support gaps", BASELINE_REGIME_ID, str(baseline["rule_id"])),
                (
                    "Best plausible support gaps",
                    str(best_plausible["regime_id"]),
                    str(best_plausible["rule_id"]),
                ),
                ("Ceiling support gaps", CEILING_REGIME_ID, str(ceiling["rule_id"])),
            ),
        ),
        "residual_comparison_baseline_best.svg": render_residual_comparison_montage(
            source,
            bridge_rows,
            (
                ("Baseline residuals", BASELINE_REGIME_ID, str(baseline["rule_id"])),
                (
                    "Best plausible residuals",
                    str(best_plausible["regime_id"]),
                    str(best_plausible["rule_id"]),
                ),
            ),
        ),
        "baseline_to_best_plausible_delta.svg": render_delta_map(
            source,
            bridge_rows,
            BASELINE_REGIME_ID,
            str(baseline["rule_id"]),
            str(best_plausible["regime_id"]),
            str(best_plausible["rule_id"]),
        ),
        "ceiling_comparison_panel.svg": render_residual_comparison_montage(
            source,
            bridge_rows,
            (
                (
                    "Best plausible residuals",
                    str(best_plausible["regime_id"]),
                    str(best_plausible["rule_id"]),
                ),
                ("Diagnostic ceiling residuals", CEILING_REGIME_ID, str(ceiling["rule_id"])),
            ),
            title="Diagnostic ceiling comparison panel",
            subtitle=(
                "Unrealistic benchmark: separates upper-bound recoverability "
                "from field-like claims."
            ),
        ),
    }


def render_recoverability_decision_montage(ranking_rows: tuple[CsvRow, ...]) -> str:
    best_rows = sorted(
        (row for row in ranking_rows if csv_int(row["rank"]) == 1),
        key=lambda row: (
            0
            if row["regime_id"] == BASELINE_REGIME_ID
            else 2
            if row["regime_id"] == CEILING_REGIME_ID
            else 1,
            str(row["regime_id"]),
        ),
    )
    width = 1500
    height = 430
    lines = svg_header(width, height, "Regime recoverability decision montage")
    lines.append(
        '<text x="24" y="34" font-size="22" font-family="monospace">'
        "Regime recoverability decision table</text>"
    )
    lines.append(
        '<text x="24" y="60" font-size="12" font-family="monospace">'
        "plausible = field-like counterfactual; ceiling = unrealistic diagnostic benchmark</text>"
    )
    columns = (
        ("Regime", 24, 34),
        ("Role", 330, 12),
        ("Rule", 460, 22),
        ("Recall", 660, 8),
        ("False negatives", 820, 12),
        ("Large errors", 1010, 12),
        ("Loss", 1180, 8),
        ("Class", 1320, 20),
    )
    lines.append('<rect x="18" y="82" width="1440" height="30" fill="#f8fafc" />')
    for label, x, _ in columns:
        lines.append(
            f'<text x="{x}" y="102" font-size="12" font-family="monospace" '
            f'font-weight="bold">{label}</text>'
        )
    for index, row in enumerate(best_rows):
        y = 140 + index * 46
        fill = "#ffffff" if index % 2 == 0 else "#f8fafc"
        role = (
            "ceiling"
            if row["plausibility_class"] == "unrealistic_diagnostic_ceiling"
            else "plausible"
            if row["plausibility_class"] == "plausible_field_like"
            else "baseline"
        )
        values = (
            short_regime_label(str(row["regime_id"])),
            role,
            short_rule_label(str(row["rule_id"])),
            f"{csv_float(row['finite_recall']):.3f}",
            str(row["false_negative_count"]),
            str(row["large_error_count"]),
            f"{csv_float(row['loss']):.3f}",
            short_recommendation(str(row["regime_recommendation_class"])),
        )
        lines.append(f'<rect x="18" y="{y - 26}" width="1440" height="36" fill="{fill}" />')
        for value, (_, x, max_chars) in zip(values, columns, strict=True):
            bounded_value = fit_table_label(value, max_chars)
            lines.append(
                f'<text x="{x}" y="{y - 4}" font-size="12" font-family="monospace">'
                f"{bounded_value}</text>"
            )
        recall_x = 660
        recall_bar = int(min(csv_float(row["finite_recall"]), 1.0) * 100)
        lines.append(f'<rect x="{recall_x}" y="{y + 4}" width="100" height="8" fill="#e5e7eb" />')
        lines.append(
            f'<rect x="{recall_x}" y="{y + 4}" width="{recall_bar}" height="8" fill="#2563eb" />'
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_support_gap_comparison_montage(
    source: SynthMediumObservationDesignResult,
    reconstructed_rows: tuple[CsvRow, ...],
    panels: tuple[tuple[str, str, str], ...],
) -> str:
    rows = source.truth.cell_truth_rows
    maps = {
        (row["regime_id"], row["rule_id"], csv_int(row["cell_id"])): row
        for row in reconstructed_rows
    }
    width = 820
    panel_height = 610
    height = 90 + panel_height * len(panels)
    lines = svg_header(width, height, "Support gap comparison montage")
    lines.append(
        '<text x="20" y="32" font-size="22" font-family="monospace">'
        "Support gap comparison montage</text>"
    )
    for index, (title, regime_id, rule_id) in enumerate(panels):
        panel_top = 52 + index * panel_height

        def fill_support(
            truth: SpreadImpactCellTruth,
            *,
            panel_regime_id: str = regime_id,
            panel_rule_id: str = rule_id,
        ) -> str:
            if truth.landscape_cell.passability != "passable":
                return "#ffffff"
            return support_gap_fill(
                maps.get((panel_regime_id, panel_rule_id, truth.landscape_cell.cell_id))
            )

        render_map_panel(
            lines,
            rows,
            panel_id=f"support-{index}",
            title=title,
            panel_top=panel_top,
            fill_for=fill_support,
            legend_items=SUPPORT_LEGEND,
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_residual_comparison_montage(
    source: SynthMediumObservationDesignResult,
    bridge_rows: tuple[CsvRow, ...],
    panels: tuple[tuple[str, str, str], ...],
    *,
    title: str = "Residual comparison baseline vs best plausible",
    subtitle: str | None = None,
) -> str:
    rows = source.truth.cell_truth_rows
    maps = {(row["regime_id"], row["rule_id"], csv_int(row["cell_id"])): row for row in bridge_rows}
    width = 820
    panel_height = 610
    header = 78 if subtitle else 58
    height = header + 32 + panel_height * len(panels)
    lines = svg_header(width, height, title)
    lines.append(f'<text x="20" y="32" font-size="22" font-family="monospace">{title}</text>')
    if subtitle:
        lines.append(
            f'<text x="20" y="56" font-size="12" font-family="monospace">{subtitle}</text>'
        )
    for index, (panel_title, regime_id, rule_id) in enumerate(panels):
        panel_top = header - 6 + index * panel_height

        def fill_residual(
            truth: SpreadImpactCellTruth,
            *,
            panel_regime_id: str = regime_id,
            panel_rule_id: str = rule_id,
        ) -> str:
            if truth.landscape_cell.passability != "passable":
                return "#ffffff"
            return residual_error_fill(
                maps.get((panel_regime_id, panel_rule_id, truth.landscape_cell.cell_id))
            )

        render_map_panel(
            lines,
            rows,
            panel_id=f"residual-{index}",
            title=panel_title,
            panel_top=panel_top,
            fill_for=fill_residual,
            legend_items=RESIDUAL_LEGEND,
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_delta_map(
    source: SynthMediumObservationDesignResult,
    bridge_rows: tuple[CsvRow, ...],
    baseline_regime_id: str,
    baseline_rule_id: str,
    best_regime_id: str,
    best_rule_id: str,
) -> str:
    rows = source.truth.cell_truth_rows
    bridge = {
        (row["regime_id"], row["rule_id"], csv_int(row["cell_id"])): row for row in bridge_rows
    }
    width = 820
    height = 650
    lines = svg_header(width, height, "Baseline-to-best plausible delta map")
    lines.append(
        '<text x="20" y="32" font-size="22" font-family="monospace">'
        "Baseline-to-best plausible delta map</text>"
    )
    render_map_panel(
        lines,
        rows,
        panel_id="delta",
        title="Baseline-to-best plausible delta",
        panel_top=50,
        fill_for=lambda truth: delta_fill(
            bridge.get((baseline_regime_id, baseline_rule_id, truth.landscape_cell.cell_id)),
            bridge.get((best_regime_id, best_rule_id, truth.landscape_cell.cell_id)),
            truth,
        ),
        legend_items=DELTA_LEGEND,
    )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_map_panel(
    lines: list[str],
    rows: tuple[SpreadImpactCellTruth, ...],
    *,
    panel_id: str,
    title: str,
    panel_top: int,
    fill_for: Callable[[SpreadImpactCellTruth], str],
    legend_items: tuple[LegendItem, ...],
) -> None:
    map_cell_size = 6
    map_height = 72 * map_cell_size
    title_y = panel_top + 26
    map_top = panel_top + 48
    map_bottom = map_top + map_height
    legend_top = map_bottom + 24
    legend_bottom = legend_bottom_y(legend_top, legend_items)
    panel_bottom = legend_bottom + 24
    lines.append(
        f'<g id="panel-{panel_id}" data-title-y="{title_y}" data-panel-bottom="{panel_bottom}">'
    )
    lines.append(
        f'<rect x="14" y="{panel_top}" width="760" height="{panel_bottom - panel_top}" '
        'fill="#ffffff" stroke="#cbd5e1" />'
    )
    lines.append(
        f'<text x="24" y="{title_y}" font-size="16" font-family="monospace">{title}</text>'
    )
    for truth in rows:
        cell = truth.landscape_cell
        x = 24 + cell.col * map_cell_size
        y = map_top + cell.row * map_cell_size
        lines.append(
            f'<rect x="{x}" y="{y}" width="{map_cell_size}" height="{map_cell_size}" '
            f'fill="{fill_for(truth)}" stroke="none" />'
        )
    append_legend(lines, "Legend", 24, legend_top, legend_items, columns=2)
    lines.append("</g>")


def delta_fill(
    baseline_row: CsvRow | None,
    best_row: CsvRow | None,
    truth: SpreadImpactCellTruth,
) -> str:
    if truth.landscape_cell.passability != "passable":
        return "#ffffff"
    if baseline_row is None or best_row is None:
        return "#d1d5db"
    baseline_class = str(baseline_row["classification"])
    best_class = str(best_row["classification"])
    if baseline_class != "true_positive" and best_class == "true_positive":
        return "#15803d"
    if baseline_class == "true_positive" and best_class != "true_positive":
        return "#dc2626"
    if baseline_class != best_class:
        return "#f59e0b"
    return "#d1d5db"


def visual_contract_passes(visual_svgs: dict[str, str]) -> bool:
    if set(visual_svgs) != set(SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES):
        return False
    comparison = visual_svgs["recoverability_decision_montage.svg"]
    if 'width="1500"' not in comparison or "False negatives" not in comparison:
        return False
    for svg in visual_svgs.values():
        if "Legend" not in svg and "recoverability decision table" not in svg:
            return False
    return True


def render_observation_design_counterfactual_report(
    result: SynthMediumObservationDesignCounterfactualResult,
) -> str:
    visual_lines = "\n".join(
        f"- [`visuals/{name}`](visuals/{name})"
        for name in SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES
    )
    best_lines = "\n".join(
        f"- `{row['regime_id']}` / `{row['rule_id']}`: recall "
        f"`{row['finite_recall']}`, false negatives `{row['false_negative_count']}`, "
        f"large errors `{row['large_error_count']}`, loss `{row['loss']}`"
        for row in result.ranking_rows
        if csv_int(row["rank"]) == 1
    )
    gate_lines = "\n".join(
        f"- `{check.name}`: `{'passed' if check.passed else 'failed'}`"
        for check in result.verification_checks
    )
    decision = result.decision_rows[0]
    summary = result.summary_dict()
    return f"""# Synth-Medium Observation-Design Recoverability Counterfactual Screen

## Boundary

This observation-design recoverability counterfactual screen is synthetic-only
and review-only. It preserves the accepted Goal 017 landscape, Goal 018
spread-impact truth, Goal 019 published observation design, and Goal 020
response-reconstruction benchmark. Counterfactual regimes are diagnostic
design-screen scenarios, not production observation-design adoption.

No production reconstruction rule, fitting, ABC/POM/likelihood/MCMC/posterior
work, parameter recovery, real-data analysis, remote compute, or follow-on goal
work is performed.

## Summary

- Baseline regime: `{summary["baseline_regime_id"]}`
- Baseline primary rule: `{summary["baseline_rule_id"]}`
- Best plausible regime: `{summary["best_plausible_regime_id"]}`
- Best plausible rule: `{summary["best_plausible_rule_id"]}`
- Ceiling rule: `{summary["ceiling_rule_id"]}`
- Decision recommendation: `{result.recommendation_class}`

## Decision

`{decision["recommendation_class"]}`: {decision["interpretation"]}

## Best Rule By Regime

{best_lines}

## Review Gates

{gate_lines}

## Visual Review Files

{visual_lines}

## Interpretation Guardrail

The `near_perfect_response_observation_ceiling` regime is an unrealistic
diagnostic upper bound. It is separated from plausible field-like
counterfactuals in all ranking, decision, and visual artifacts so that a
ceiling-only recovery cannot be mistaken for evidence that the published
default observation design is ready for fitting.
"""


def source_reconciliation(
    source: SynthMediumObservationDesignResult,
    source_reconstruction_summary: dict[str, object],
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
        "response_reconstruction": source_reconstruction_summary,
    }


def response_reconstruction_source_summary(
    result: SynthMediumResponseReconstructionResult,
) -> dict[str, object]:
    default_best = best_ranking_row(result.rule_regime_ranking_rows, BASELINE_REGIME_ID)
    return {
        "primary_default_rule_id": default_best["rule_id"],
        "default_finite_recall": default_best["finite_recall"],
        "default_false_negative_count": default_best["false_negative_count"],
        "default_false_positive_count": default_best["false_positive_count"],
        "default_large_error_count": default_best["large_error_count"],
        "recommendation_class": result.recommendation_class,
    }


def baseline_matches_expectation(row: CsvRow) -> bool:
    expected = RESPONSE_RECONSTRUCTION_EXPECTATIONS
    return (
        row["rule_id"] == expected["primary_default_rule_id"]
        and csv_float(row["finite_recall"]) == expected["default_finite_recall"]
        and csv_int(row["false_negative_count"]) == expected["default_false_negative_count"]
        and csv_int(row["false_positive_count"]) == expected["default_false_positive_count"]
        and csv_int(row["large_error_count"]) == expected["default_large_error_count"]
        and row["regime_recommendation_class"] == expected["recommendation_class"]
    )


def baseline_ranking_row(ranking_rows: tuple[CsvRow, ...]) -> CsvRow:
    return next(
        row
        for row in ranking_rows
        if row["regime_id"] == BASELINE_REGIME_ID and row["rule_id"] == BASELINE_RULE_ID
    )


def best_plausible_row(ranking_rows: tuple[CsvRow, ...]) -> CsvRow:
    return max(
        (
            row
            for row in ranking_rows
            if row["plausibility_class"] == "plausible_field_like" and csv_int(row["rank"]) == 1
        ),
        key=lambda row: (
            csv_float(row["finite_recall"]),
            -csv_int(row["false_negative_count"]),
            -csv_float(row["loss"]),
        ),
    )


def support_row_for(rows: tuple[CsvRow, ...], regime_id: str, rule_id: str) -> CsvRow:
    return next(
        row
        for row in rows
        if row["regime_id"] == regime_id
        and row["rule_id"] == rule_id
        and row["summary_group"] == "all_passable"
    )


def observation_summary_row(rows: tuple[CsvRow, ...], regime_id: str) -> CsvRow:
    return next(row for row in rows if row["regime_id"] == regime_id)


def optional_int(value: CsvValue) -> int | None:
    if value is None or value == "":
        return None
    return csv_int(value)


def optional_delta(value: CsvValue, baseline: CsvValue) -> float | None:
    if value in {None, ""} or baseline in {None, ""}:
        return None
    return round_float(csv_float(value) - csv_float(baseline))


def delta_interpretation(row: CsvRow, regime: CounterfactualRegimeDefinition) -> str:
    if regime.regime_id == BASELINE_REGIME_ID:
        return "published baseline; deltas are zero by definition"
    if regime.plausibility_class == "unrealistic_diagnostic_ceiling":
        return "diagnostic ceiling; upper-bound recovery is not a field-like design claim"
    if csv_int(row["false_negative_count"]) < csv_int(
        RESPONSE_RECONSTRUCTION_EXPECTATIONS["default_false_negative_count"]
    ):
        return "plausible support improves recall but must still pass readiness gates"
    return "plausible support does not materially improve the published baseline"


def short_regime_label(regime_id: str) -> str:
    replacements = {
        BASELINE_REGIME_ID: "baseline_default",
        "post_impact_followup_boost": "post_impact_followup",
        "final_absence_confirmation_support": "final_absence_confirm",
        "weak_area_targeted_support": "weak_area_target",
        "balanced_habitat_region_support": "balanced_strata",
        CEILING_REGIME_ID: "near_perfect_ceiling",
    }
    return replacements.get(regime_id, regime_id)


def short_rule_label(rule_id: str) -> str:
    replacements = {
        "midpoint_after_last_detection": "midpoint_after_last_det",
    }
    return replacements.get(rule_id, rule_id)


def fit_table_label(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    if max_chars <= 3:
        return value[:max_chars]
    return f"{value[: max_chars - 3]}..."


def short_recommendation(value: str) -> str:
    replacements = {
        "observation_design_not_recoverable_enough_for_backfitting": "not_recoverable",
        "recoverability_improved_but_not_fit_ready": "improved_not_ready",
        "response_reconstruction_ready_for_human_review": "ready_for_review",
        "diagnostic_ceiling_recovers_signal": "ceiling_recovers",
        "diagnostic_ceiling_failed": "ceiling_failed",
    }
    return replacements.get(value, value)


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f"<title>{title}</title>",
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]


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
    lines.append(f'<g id="{legend_id.lower().replace(" ", "-")}">')
    lines.append(
        f'<text x="{x}" y="{y}" font-size="13" font-family="monospace" '
        f'font-weight="bold">{legend_id}</text>'
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
