from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from json import dumps
from os import PathLike
from pathlib import Path

from .landscape import CsvRow, CsvValue, mean, write_csv_rows
from .observation_design_counterfactual_screen import (
    CounterfactualRegimeDefinition,
    baseline_reconstruction_by_cell,
    build_observation_row,
    copy_rows_for_regime,
    enrich_rows_as_survey_schedule,
    fit_table_label,
    render_map_panel,
    short_recommendation,
    short_regime_label,
    svg_header,
)
from .observations import (
    ObservationRegime,
    SynthMediumObservationDesignConfig,
    SynthMediumObservationDesignResult,
    build_cell_observation_summary_rows,
    build_regime_summary_rows,
    build_synth_medium_observation_design_review_pack,
    stable_unit,
)
from .response_reconstruction import (
    ReconstructionRule,
    SynthMediumResponseReconstructionConfig,
    best_ranking_row,
    build_reconstruction_error_summary_rows,
    build_support_gap_summary_rows,
    build_synth_medium_response_reconstruction_benchmark,
    build_truth_reconstruction_bridge_rows,
    csv_bool,
    csv_float,
    csv_int,
    default_reconstruction_rules,
    passable_truth_rows,
    ranking_loss,
    reconstruct_cell,
    residual_error_fill,
    round_float,
    support_gap_fill,
)
from .spread_impact import SpreadImpactCellTruth

DEFAULT_SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_DIR = Path(
    "artifacts/synth_medium_recoverability_target_observation_design"
)
SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_FILES = (
    "recoverability_target_config.json",
    "regime_definitions.csv",
    "observation_effort_summary.csv",
    "strata_effort_summary.csv",
    "reconstruction_benchmark_summary.csv",
    "support_gap_summary.csv",
    "baseline_to_candidate_delta.csv",
    "readiness_decision_summary.csv",
    "verification.json",
    "report.md",
)
SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES = (
    "effort_support_surfaces.svg",
    "support_gap_maps.svg",
    "residual_maps.svg",
    "recoverability_decision_montage.svg",
    "ceiling_reference_panel.svg",
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "recoverability_target_observation_design_review_only": True,
    "synth_medium_landscape_source_verified": True,
    "synth_medium_spread_impact_source_verified": True,
    "synth_medium_observation_design_source_verified": True,
    "synth_medium_response_reconstruction_source_verified": True,
    "synth_medium_observation_design_counterfactual_source_verified": True,
    "response_only_observation_designs": True,
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
BEST_FIELD_PLAUSIBLE_REGIME_ID = "integrated_recoverability_target_panel"

RESPONSE_RECONSTRUCTION_EXPECTATIONS: CsvRow = {
    "primary_default_rule_id": BASELINE_RULE_ID,
    "default_finite_recall": 0.524364653765,
    "default_false_negative_count": 2040,
    "default_false_positive_count": 304,
    "default_large_error_count": 809,
    "recommendation_class": "observation_design_not_recoverable_enough_for_backfitting",
}

REGIME_COLUMNS = (
    "regime_id",
    "regime_role",
    "plausibility_class",
    "counterfactual_class",
    "source_regime_id",
    "response_observable_trigger",
    "additional_support_semantics",
    "uses_hidden_truth_for_design",
    "field_plausibility_notes",
    "interpretation",
)
EFFORT_COLUMNS = (
    "regime_id",
    "regime_role",
    "plausibility_class",
    "counterfactual_class",
    "survey_record_count",
    "record_count_delta_from_baseline",
    "surveyed_cell_count",
    "surveyed_cell_count_delta_from_baseline",
    "mean_survey_count",
    "mean_effort",
    "post_impact_support_count",
    "post_impact_support_fraction",
    "detection_history_support_count",
    "post_detection_support_count",
    "final_absence_support_count",
    "false_negative_count",
    "false_negative_delta_from_baseline",
)
STRATA_COLUMNS = (
    "regime_id",
    "summary_group",
    "passable_cell_count",
    "survey_record_count",
    "surveyed_cell_count",
    "mean_survey_count",
    "mean_effort",
    "detection_history_support_count",
    "final_absence_support_count",
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
    "true_negative_count",
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
    "false_positive_delta_from_baseline",
    "large_error_delta_from_baseline",
    "loss_delta_from_baseline",
    "regime_recommendation_class",
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
    "specificity_delta",
    "precision_delta",
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
    "best_field_plausible_regime_id",
    "best_field_plausible_rule_id",
    "best_field_plausible_finite_recall",
    "best_field_plausible_false_negative_count",
    "best_field_plausible_false_positive_count",
    "best_field_plausible_large_error_count",
    "best_field_plausible_loss",
    "best_field_plausible_ready_for_reconstruction_review",
    "best_performing_ready_regime_id",
    "best_performing_ready_rule_id",
    "lowest_effort_ready_regime_id",
    "lowest_effort_ready_rule_id",
    "lowest_effort_ready_finite_recall",
    "lowest_effort_ready_false_negative_count",
    "lowest_effort_ready_false_positive_count",
    "lowest_effort_ready_large_error_count",
    "lowest_effort_ready_loss",
    "lowest_effort_ready_ready_for_reconstruction_review",
    "ceiling_regime_id",
    "ceiling_rule_id",
    "ceiling_finite_recall",
    "ceiling_false_negative_count",
    "ceiling_ready_for_reconstruction_review",
    "baseline_survey_record_count",
    "baseline_survey_record_delta_vs_baseline",
    "baseline_survey_record_ratio_vs_baseline",
    "baseline_survey_record_delta_vs_ceiling",
    "baseline_survey_record_ratio_vs_ceiling",
    "baseline_surveyed_cell_count",
    "baseline_final_absence_support_count",
    "best_field_plausible_survey_record_count",
    "best_field_plausible_survey_record_delta_vs_baseline",
    "best_field_plausible_survey_record_ratio_vs_baseline",
    "best_field_plausible_survey_record_delta_vs_ceiling",
    "best_field_plausible_survey_record_ratio_vs_ceiling",
    "best_field_plausible_surveyed_cell_count",
    "best_field_plausible_final_absence_support_count",
    "lowest_effort_ready_survey_record_count",
    "lowest_effort_ready_survey_record_delta_vs_baseline",
    "lowest_effort_ready_survey_record_ratio_vs_baseline",
    "lowest_effort_ready_survey_record_delta_vs_ceiling",
    "lowest_effort_ready_survey_record_ratio_vs_ceiling",
    "lowest_effort_ready_surveyed_cell_count",
    "lowest_effort_ready_final_absence_support_count",
    "ceiling_survey_record_count",
    "ceiling_survey_record_delta_vs_baseline",
    "ceiling_survey_record_ratio_vs_baseline",
    "ceiling_survey_record_delta_vs_ceiling",
    "ceiling_survey_record_ratio_vs_ceiling",
    "ceiling_surveyed_cell_count",
    "ceiling_final_absence_support_count",
    "limiting_failure_modes",
    "interpretation",
)

LegendItem = tuple[str, str]

EFFORT_LEGEND: tuple[LegendItem, ...] = (
    ("#ffffff", "Water / not passable"),
    ("#f3f4f6", "No survey"),
    ("#bfdbfe", "Moderate support"),
    ("#1d4ed8", "High support"),
)
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


@dataclass(frozen=True, slots=True)
class RecoverabilityTargetCheck:
    name: str
    passed: bool
    details: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "details": self.details}


@dataclass(frozen=True, slots=True)
class SynthMediumRecoverabilityTargetObservationDesignConfig:
    selected_baseline_regime_id: str = BASELINE_REGIME_ID
    primary_benchmark_rule_id: str = BASELINE_RULE_ID
    large_error_min: float = 24.0
    ready_finite_recall_min: float = 0.70
    ready_false_negative_max: int = 1350
    ready_false_positive_max: int = 750
    ready_median_abs_error_max: float = 18.0
    ready_large_error_count_max: int = 650
    meaningful_recall_improvement_min: float = 0.10

    def to_dict(self) -> dict[str, object]:
        return {
            "selected_baseline_regime_id": self.selected_baseline_regime_id,
            "primary_benchmark_rule_id": self.primary_benchmark_rule_id,
            "large_error_min": self.large_error_min,
            "review_gate_thresholds": {
                "ready_finite_recall_min": self.ready_finite_recall_min,
                "ready_false_negative_max": self.ready_false_negative_max,
                "ready_false_positive_max": self.ready_false_positive_max,
                "ready_median_abs_error_max": self.ready_median_abs_error_max,
                "ready_large_error_count_max": self.ready_large_error_count_max,
                "meaningful_recall_improvement_min": self.meaningful_recall_improvement_min,
            },
            "output_files": list(
                SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_FILES
            ),
            "visual_files": [
                f"visuals/{name}"
                for name in SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES
            ],
            **BOUNDARY_LABELS,
        }


@dataclass(frozen=True, slots=True)
class SynthMediumRecoverabilityTargetObservationDesignResult:
    config: SynthMediumRecoverabilityTargetObservationDesignConfig
    observation_design: SynthMediumObservationDesignResult
    regimes: tuple[CounterfactualRegimeDefinition, ...]
    rules: tuple[ReconstructionRule, ...]
    observation_rows_by_regime: dict[str, tuple[CsvRow, ...]]
    effort_summary_rows: tuple[CsvRow, ...]
    strata_effort_rows: tuple[CsvRow, ...]
    reconstructed_cell_rows: tuple[CsvRow, ...]
    bridge_rows: tuple[CsvRow, ...]
    error_summary_rows: tuple[CsvRow, ...]
    support_gap_rows: tuple[CsvRow, ...]
    ranking_rows: tuple[CsvRow, ...]
    delta_rows: tuple[CsvRow, ...]
    decision_rows: tuple[CsvRow, ...]
    verification_checks: tuple[RecoverabilityTargetCheck, ...]
    visual_svgs: dict[str, str]
    source_response_reconstruction_summary: dict[str, object]
    source_counterfactual_summary: dict[str, object]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    @property
    def recommendation_class(self) -> str:
        return str(self.decision_rows[0]["recommendation_class"])

    def summary_dict(self) -> dict[str, object]:
        baseline = baseline_ranking_row(self.ranking_rows)
        best = best_field_plausible_row(self.ranking_rows)
        ceiling = best_ranking_row(self.ranking_rows, CEILING_REGIME_ID)
        decision = self.decision_rows[0]
        return {
            "baseline_regime_id": self.config.selected_baseline_regime_id,
            "baseline_rule_id": self.config.primary_benchmark_rule_id,
            "candidate_regime_count": len(self.regimes),
            "rule_count": len(self.rules),
            "baseline_finite_recall": baseline["finite_recall"],
            "baseline_false_negative_count": baseline["false_negative_count"],
            "best_field_plausible_regime_id": best["regime_id"],
            "best_field_plausible_rule_id": best["rule_id"],
            "best_field_plausible_finite_recall": best["finite_recall"],
            "best_field_plausible_false_negative_count": best["false_negative_count"],
            "best_field_plausible_survey_record_count": decision[
                "best_field_plausible_survey_record_count"
            ],
            "lowest_effort_ready_regime_id": decision["lowest_effort_ready_regime_id"],
            "lowest_effort_ready_rule_id": decision["lowest_effort_ready_rule_id"],
            "lowest_effort_ready_survey_record_count": decision[
                "lowest_effort_ready_survey_record_count"
            ],
            "ceiling_rule_id": ceiling["rule_id"],
            "ceiling_finite_recall": ceiling["finite_recall"],
            "ceiling_false_negative_count": ceiling["false_negative_count"],
            "ceiling_survey_record_count": decision["ceiling_survey_record_count"],
            "recommendation_class": self.recommendation_class,
        }

    def config_payload(self) -> dict[str, object]:
        return {
            **self.config.to_dict(),
            "source_reconciliation": source_reconciliation(
                self.observation_design,
                self.source_response_reconstruction_summary,
                self.source_counterfactual_summary,
            ),
            "candidate_regimes": [regime_definition_row(regime) for regime in self.regimes],
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

        config_path = target_dir / "recoverability_target_config.json"
        config_path.write_text(
            dumps(self.config_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(config_path)

        table_specs: tuple[tuple[str, tuple[str, ...], tuple[CsvRow, ...]], ...] = (
            (
                "regime_definitions.csv",
                REGIME_COLUMNS,
                tuple(regime_definition_row(regime) for regime in self.regimes),
            ),
            ("observation_effort_summary.csv", EFFORT_COLUMNS, self.effort_summary_rows),
            ("strata_effort_summary.csv", STRATA_COLUMNS, self.strata_effort_rows),
            ("reconstruction_benchmark_summary.csv", RANKING_COLUMNS, self.ranking_rows),
            ("support_gap_summary.csv", SUPPORT_GAP_COLUMNS, self.support_gap_rows),
            ("baseline_to_candidate_delta.csv", DELTA_COLUMNS, self.delta_rows),
            ("readiness_decision_summary.csv", DECISION_COLUMNS, self.decision_rows),
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
        report_path.write_text(render_recoverability_target_report(self), encoding="utf-8")
        written.append(report_path)

        for visual_name in SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES:
            path = visuals_dir / visual_name
            path.write_text(self.visual_svgs[visual_name], encoding="utf-8")
            written.append(path)

        return tuple(written)


def build_synth_medium_recoverability_target_observation_design(
    config: SynthMediumRecoverabilityTargetObservationDesignConfig | None = None,
    *,
    observation_design: SynthMediumObservationDesignResult | None = None,
) -> SynthMediumRecoverabilityTargetObservationDesignResult:
    target_config = config or SynthMediumRecoverabilityTargetObservationDesignConfig()
    source = observation_design or build_synth_medium_observation_design_review_pack()
    baseline_benchmark = build_synth_medium_response_reconstruction_benchmark(
        observation_design=source
    )
    source_response_summary = baseline_benchmark.summary_dict()
    from .observation_design_counterfactual_screen import (
        build_synth_medium_observation_design_counterfactual_screen,
    )

    source_counterfactual_summary = build_synth_medium_observation_design_counterfactual_screen(
        observation_design=source
    ).summary_dict()

    regimes = default_recoverability_target_regimes()
    rules = default_reconstruction_rules()
    observation_rows_by_regime = build_target_observation_rows(source, regimes)
    passable_truth = passable_truth_rows(source)
    reconstructed_rows = build_target_reconstructed_rows(
        regimes, rules, passable_truth, observation_rows_by_regime
    )
    response_config = SynthMediumResponseReconstructionConfig(
        large_error_min=target_config.large_error_min
    )
    bridge_rows = build_truth_reconstruction_bridge_rows(
        source, reconstructed_rows, response_config
    )
    error_rows = annotate_error_rows(
        build_reconstruction_error_summary_rows(bridge_rows, response_config), regimes
    )
    support_rows = annotate_support_rows(
        build_support_gap_summary_rows(reconstructed_rows), regimes
    )
    ranking_rows = build_target_ranking_rows(error_rows, regimes, target_config)
    effort_rows = build_effort_summary_rows(
        source, regimes, observation_rows_by_regime, support_rows, reconstructed_rows
    )
    strata_rows = build_strata_effort_rows(
        source, regimes, observation_rows_by_regime, reconstructed_rows
    )
    delta_rows = build_delta_rows(ranking_rows, effort_rows, support_rows, regimes)
    decision_rows = build_decision_rows(ranking_rows, effort_rows, target_config)
    visual_svgs = build_visual_svgs(
        source, reconstructed_rows, bridge_rows, ranking_rows, effort_rows
    )
    checks = verify_recoverability_target_result(
        target_config,
        source,
        source_response_summary,
        source_counterfactual_summary,
        regimes,
        rules,
        effort_rows,
        strata_rows,
        reconstructed_rows,
        error_rows,
        support_rows,
        ranking_rows,
        delta_rows,
        decision_rows,
        visual_svgs,
    )
    return SynthMediumRecoverabilityTargetObservationDesignResult(
        config=target_config,
        observation_design=source,
        regimes=regimes,
        rules=rules,
        observation_rows_by_regime=observation_rows_by_regime,
        effort_summary_rows=effort_rows,
        strata_effort_rows=strata_rows,
        reconstructed_cell_rows=reconstructed_rows,
        bridge_rows=bridge_rows,
        error_summary_rows=error_rows,
        support_gap_rows=support_rows,
        ranking_rows=ranking_rows,
        delta_rows=delta_rows,
        decision_rows=decision_rows,
        verification_checks=checks,
        visual_svgs=visual_svgs,
        source_response_reconstruction_summary=source_response_summary,
        source_counterfactual_summary=source_counterfactual_summary,
    )


def default_recoverability_target_regimes() -> tuple[CounterfactualRegimeDefinition, ...]:
    return (
        CounterfactualRegimeDefinition(
            regime_id=BASELINE_REGIME_ID,
            regime_role="published_baseline",
            plausibility_class="published_baseline",
            counterfactual_class="baseline",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger="published Goal 019 default observation records",
            additional_support_semantics="no added records; exact baseline reconciliation",
            interpretation="Fixed Goal 019/020 baseline retained for comparison.",
        ),
        CounterfactualRegimeDefinition(
            regime_id="stratified_scheduled_panel",
            regime_role="candidate",
            plausibility_class="plausible_field_like",
            counterfactual_class="stratified_scheduled_panel",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger="landscape habitat, region, and front-band strata",
            additional_support_semantics=(
                "adds scheduled panel waves to a deterministic stratified cell frame"
            ),
            interpretation=(
                "Tests a serious scheduled field panel without using latent extirpation truth."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id="weak_strata_targeted_panel",
            regime_role="candidate",
            plausibility_class="plausible_field_like",
            counterfactual_class="weak_strata_targeted_panel",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger="low-quality matrix, east band, and water-edge strata",
            additional_support_semantics="adds extra waves to weak-but-observable landscape strata",
            interpretation=(
                "Targets known weak observation strata from response-observable landscape features."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id="post_detection_confirmation_panel",
            regime_role="candidate",
            plausibility_class="plausible_field_like",
            counterfactual_class="post_detection_confirmation_panel",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger="baseline detection history",
            additional_support_semantics="adds repeated revisits after the last observed detection",
            interpretation="Tests post-detection response-only confirmation support.",
        ),
        CounterfactualRegimeDefinition(
            regime_id="final_absence_revisit_panel",
            regime_role="candidate",
            plausibility_class="plausible_field_like",
            counterfactual_class="final_absence_revisit_panel",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger="baseline final-absence support gap classifications",
            additional_support_semantics="adds bounded final-absence confirmation revisits",
            interpretation=(
                "Targets cells that have observed occupancy but weak final-absence support."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id="high_cadence_rotating_panel",
            regime_role="candidate",
            plausibility_class="plausible_field_like",
            counterfactual_class="high_cadence_rotating_panel",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger="rotating deterministic landscape panel",
            additional_support_semantics="adds higher temporal cadence to a broad rotating panel",
            interpretation=(
                "Tests whether cadence, not only spatial coverage, controls timing error."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id=BEST_FIELD_PLAUSIBLE_REGIME_ID,
            regime_role="candidate",
            plausibility_class="plausible_field_like",
            counterfactual_class="integrated_recoverability_target_panel",
            source_regime_id=BASELINE_REGIME_ID,
            response_observable_trigger=(
                "landscape strata plus observed detections and final-absence support gaps"
            ),
            additional_support_semantics=(
                "combines scheduled stratified waves, weak-strata support, and "
                "confirmation revisits"
            ),
            interpretation=(
                "Most serious field-plausible candidate before considering a process "
                "observation model."
            ),
        ),
        CounterfactualRegimeDefinition(
            regime_id=CEILING_REGIME_ID,
            regime_role="diagnostic_ceiling",
            plausibility_class="unrealistic_diagnostic_ceiling",
            counterfactual_class="near_perfect_ceiling",
            source_regime_id="truth_reference_full_observability",
            response_observable_trigger="full benchmark visibility; not a field design",
            additional_support_semantics="copies the full-observability benchmark",
            interpretation="Unrealistic reference used only to bound recoverability.",
        ),
    )


def regime_definition_row(regime: CounterfactualRegimeDefinition) -> CsvRow:
    return {
        "regime_id": regime.regime_id,
        "regime_role": regime.regime_role,
        "plausibility_class": regime.plausibility_class,
        "counterfactual_class": regime.counterfactual_class,
        "source_regime_id": regime.source_regime_id,
        "response_observable_trigger": regime.response_observable_trigger,
        "additional_support_semantics": regime.additional_support_semantics,
        "uses_hidden_truth_for_design": False,
        "field_plausibility_notes": field_plausibility_notes(regime),
        "interpretation": regime.interpretation,
    }


def field_plausibility_notes(regime: CounterfactualRegimeDefinition) -> str:
    if regime.plausibility_class == "unrealistic_diagnostic_ceiling":
        return "diagnostic ceiling only; not field-plausible"
    if regime.regime_id == BASELINE_REGIME_ID:
        return "published baseline reference"
    return "field-plausible response-observable design candidate"


def build_target_observation_rows(
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
            build_added_target_rows(
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


def build_added_target_rows(
    config: SynthMediumObservationDesignConfig,
    regime: CounterfactualRegimeDefinition,
    passable_truth: tuple[SpreadImpactCellTruth, ...],
    baseline_summary: dict[int, CsvRow],
    baseline_reconstructed: dict[int, CsvRow],
    existing_rows: list[CsvRow],
) -> list[CsvRow]:
    existing_times = {(csv_int(row["cell_id"]), csv_int(row["time"])) for row in existing_rows}
    rows: list[CsvRow] = []
    observation_regime = observation_regime_for_target(regime)
    next_index = len(existing_rows) + 1
    for truth_row in passable_truth:
        cell_id = truth_row.landscape_cell.cell_id
        times = target_added_times_for_cell(
            regime, truth_row, baseline_summary[cell_id], baseline_reconstructed[cell_id]
        )
        for time in times:
            if (cell_id, time) in existing_times:
                continue
            rows.append(
                build_observation_row(config, observation_regime, truth_row, time, next_index)
            )
            existing_times.add((cell_id, time))
            next_index += 1
    return rows


def observation_regime_for_target(definition: CounterfactualRegimeDefinition) -> ObservationRegime:
    effort_scale = {
        "stratified_scheduled_panel": 1.18,
        "weak_strata_targeted_panel": 1.26,
        "post_detection_confirmation_panel": 1.24,
        "final_absence_revisit_panel": 1.22,
        "high_cadence_rotating_panel": 1.20,
        "integrated_recoverability_target_panel": 1.34,
    }.get(definition.counterfactual_class, 1.0)
    detection_scale = {
        "stratified_scheduled_panel": 0.88,
        "weak_strata_targeted_panel": 0.90,
        "post_detection_confirmation_panel": 0.92,
        "final_absence_revisit_panel": 0.90,
        "high_cadence_rotating_panel": 0.88,
        "integrated_recoverability_target_panel": 0.96,
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


def target_added_times_for_cell(
    regime: CounterfactualRegimeDefinition,
    truth_row: SpreadImpactCellTruth,
    baseline_summary: CsvRow,
    baseline_reconstructed: CsvRow,
) -> tuple[int, ...]:
    cell = truth_row.landscape_cell
    detection_count = csv_int(baseline_summary["detection_count"])
    last_detection = optional_int(baseline_summary["last_detection_time"])
    status = str(baseline_reconstructed["reconstruction_status"])
    class_id = regime.counterfactual_class
    if class_id == "stratified_scheduled_panel":
        in_frame = stable_unit(20260622, regime.regime_id, cell.cell_id, 1) < stratum_frame_rate(
            cell.habitat_class, cell.col_band
        )
        return (0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120) if in_frame else ()
    if class_id == "weak_strata_targeted_panel":
        weak = (
            cell.habitat_class == "low_quality_matrix"
            or cell.col_band in {"east_band", "central_band"}
            or cell.water_neighbor_count > 0
        )
        if not weak:
            return ()
        return (0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120)
    if class_id == "post_detection_confirmation_panel":
        if detection_count == 0 or last_detection is None:
            return ()
        return tuple(
            time
            for time in (
                last_detection + 6,
                last_detection + 12,
                last_detection + 24,
                last_detection + 36,
            )
            if time <= 120
        )
    if class_id == "final_absence_revisit_panel":
        if detection_count == 0 or last_detection is None:
            return ()
        if status not in {
            "no_post_detection_survey",
            "short_final_absence_run",
            "no_detection_history",
        }:
            return ()
        return tuple(
            time
            for time in (
                last_detection + 6,
                last_detection + 12,
                last_detection + 18,
                last_detection + 30,
                last_detection + 42,
            )
            if time <= 120
        )
    if class_id == "high_cadence_rotating_panel":
        in_frame = stable_unit(20260622, regime.regime_id, cell.cell_id, 5) < 0.70
        return (0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120) if in_frame else ()
    if class_id == "integrated_recoverability_target_panel":
        times: set[int] = set()
        broad_frame = stable_unit(20260622, regime.regime_id, cell.cell_id, 9) < 0.86
        weak = (
            cell.habitat_class == "low_quality_matrix"
            or cell.col_band in {"east_band", "central_band"}
            or cell.water_neighbor_count > 0
        )
        if broad_frame or weak:
            times.update((0, 8, 16, 24, 36, 48, 60, 72, 84, 96, 108, 120))
        if detection_count > 0 and last_detection is not None:
            times.update(
                time
                for time in (
                    last_detection + 6,
                    last_detection + 12,
                    last_detection + 18,
                    last_detection + 24,
                    last_detection + 36,
                    last_detection + 48,
                )
                if time <= 120
            )
        if status in {"no_post_detection_survey", "short_final_absence_run"}:
            times.update((96, 108, 120))
        return tuple(sorted(time for time in times if 0 <= time <= 120))
    return ()


def stratum_frame_rate(habitat_class: str, col_band: str) -> float:
    rate = {
        "source_zone": 0.84,
        "corridor": 0.78,
        "high_quality_patch": 0.74,
        "medium_quality": 0.68,
        "low_quality_matrix": 0.76,
    }[habitat_class]
    rate += {"west_band": 0.00, "central_band": 0.04, "east_band": 0.08}[col_band]
    return min(rate, 0.92)


def build_target_reconstructed_rows(
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
            "counterfactual_class": regime_map[str(row["regime_id"])].counterfactual_class,
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


def build_target_ranking_rows(
    error_rows: tuple[CsvRow, ...],
    regimes: tuple[CounterfactualRegimeDefinition, ...],
    config: SynthMediumRecoverabilityTargetObservationDesignConfig,
) -> tuple[CsvRow, ...]:
    all_rows = [row for row in error_rows if row["summary_group"] == "all_passable"]
    by_regime: dict[str, list[CsvRow]] = defaultdict(list)
    for row in all_rows:
        by_regime[str(row["regime_id"])].append(row)
    provisional: dict[str, list[tuple[float, CsvRow]]] = {}
    for regime_id, rows in by_regime.items():
        scored = [(ranking_loss(row), row) for row in rows]
        scored.sort(key=lambda item: (item[0], str(item[1]["rule_id"])))
        provisional[regime_id] = scored
    baseline = next(
        row
        for _, row in provisional[config.selected_baseline_regime_id]
        if row["rule_id"] == config.primary_benchmark_rule_id
    )
    baseline_loss = ranking_loss(baseline)
    ranked: list[CsvRow] = []
    for regime in regimes:
        for rank, (loss, row) in enumerate(provisional[regime.regime_id], start=1):
            ranked.append(
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
                    "true_negative_count": row["true_negative_count"],
                    "finite_recall": row["finite_recall"],
                    "specificity": row["specificity"],
                    "precision": row["precision"],
                    "median_absolute_error": row["median_absolute_error"],
                    "p90_absolute_error": row["p90_absolute_error"],
                    "large_error_count": row["large_error_count"],
                    "large_error_fraction": row["large_error_fraction"],
                    "loss": round_float(loss),
                    "finite_recall_delta_from_baseline": round_float(
                        csv_float(row["finite_recall"]) - csv_float(baseline["finite_recall"])
                    ),
                    "false_negative_delta_from_baseline": (
                        csv_int(row["false_negative_count"])
                        - csv_int(baseline["false_negative_count"])
                    ),
                    "false_positive_delta_from_baseline": (
                        csv_int(row["false_positive_count"])
                        - csv_int(baseline["false_positive_count"])
                    ),
                    "large_error_delta_from_baseline": (
                        csv_int(row["large_error_count"]) - csv_int(baseline["large_error_count"])
                    ),
                    "loss_delta_from_baseline": round_float(loss - baseline_loss),
                    "regime_recommendation_class": regime_recommendation_class(row, regime, config),
                }
            )
    return tuple(ranked)


def regime_recommendation_class(
    row: CsvRow,
    regime: CounterfactualRegimeDefinition,
    config: SynthMediumRecoverabilityTargetObservationDesignConfig,
) -> str:
    if regime.regime_id == config.selected_baseline_regime_id:
        return str(RESPONSE_RECONSTRUCTION_EXPECTATIONS["recommendation_class"])
    if regime.plausibility_class == "unrealistic_diagnostic_ceiling":
        return (
            "diagnostic_ceiling_recovers_signal"
            if csv_int(row["false_negative_count"]) == 0
            else "diagnostic_ceiling_failed"
        )
    ready = (
        csv_float(row["finite_recall"]) >= config.ready_finite_recall_min
        and csv_int(row["false_negative_count"]) <= config.ready_false_negative_max
        and csv_int(row["false_positive_count"]) <= config.ready_false_positive_max
        and csv_float(row["median_absolute_error"]) <= config.ready_median_abs_error_max
        and csv_int(row["large_error_count"]) <= config.ready_large_error_count_max
    )
    if ready:
        return "recoverability_review_ready"
    if (
        csv_float(row["finite_recall"]) >= config.ready_finite_recall_min - 0.06
        and csv_int(row["false_negative_count"]) <= config.ready_false_negative_max + 400
    ):
        return "field_plausible_improved_but_not_ready"
    return "field_plausible_not_recoverable_enough"


def build_effort_summary_rows(
    source: SynthMediumObservationDesignResult,
    regimes: tuple[CounterfactualRegimeDefinition, ...],
    rows_by_regime: dict[str, tuple[CsvRow, ...]],
    support_rows: tuple[CsvRow, ...],
    reconstructed_rows: tuple[CsvRow, ...],
) -> tuple[CsvRow, ...]:
    passable_truth = passable_truth_rows(source)
    truth_by_cell = {row.landscape_cell.cell_id: row for row in passable_truth}
    observation_regimes = tuple(observation_regime_for_summary(regime) for regime in regimes)
    survey_rows: list[CsvRow] = []
    observation_rows: list[CsvRow] = []
    cell_summary_rows: list[CsvRow] = []
    for regime in regimes:
        regime_rows = list(rows_by_regime[regime.regime_id])
        survey_rows.extend(enrich_rows_as_survey_schedule(regime_rows, truth_by_cell))
        observation_rows.extend(regime_rows)
        cell_summary_rows.extend(
            build_cell_observation_summary_rows(
                observation_regime_for_summary(regime), passable_truth, regime_rows
            )
        )
    regime_summary = build_regime_summary_rows(
        observation_regimes,
        passable_truth,
        tuple(survey_rows),
        tuple(observation_rows),
        tuple(cell_summary_rows),
    )
    baseline_summary = next(row for row in regime_summary if row["regime_id"] == BASELINE_REGIME_ID)
    regime_map = {regime.regime_id: regime for regime in regimes}
    rows: list[CsvRow] = []
    for summary in regime_summary:
        regime = regime_map[str(summary["regime_id"])]
        support = support_row_for(support_rows, regime.regime_id, BASELINE_RULE_ID)
        reconstructed = [
            row
            for row in reconstructed_rows
            if row["regime_id"] == regime.regime_id and row["rule_id"] == BASELINE_RULE_ID
        ]
        detection_history = sum(csv_int(row["detection_count"]) > 0 for row in reconstructed)
        rows.append(
            {
                "regime_id": regime.regime_id,
                "regime_role": regime.regime_role,
                "plausibility_class": regime.plausibility_class,
                "counterfactual_class": regime.counterfactual_class,
                "survey_record_count": summary["observation_record_count"],
                "record_count_delta_from_baseline": csv_int(summary["observation_record_count"])
                - csv_int(baseline_summary["observation_record_count"]),
                "surveyed_cell_count": summary["surveyed_passable_count"],
                "surveyed_cell_count_delta_from_baseline": (
                    csv_int(summary["surveyed_passable_count"])
                    - csv_int(baseline_summary["surveyed_passable_count"])
                ),
                "mean_survey_count": support["mean_survey_count"],
                "mean_effort": summary["mean_effort"],
                "post_impact_support_count": summary["post_impact_support_count"],
                "post_impact_support_fraction": summary["post_impact_support_fraction"],
                "detection_history_support_count": detection_history,
                "post_detection_support_count": detection_history,
                "final_absence_support_count": support["post_detection_absence_supported_count"],
                "false_negative_count": summary["false_negative_count"],
                "false_negative_delta_from_baseline": csv_int(summary["false_negative_count"])
                - csv_int(baseline_summary["false_negative_count"]),
            }
        )
    return tuple(rows)


def observation_regime_for_summary(regime: CounterfactualRegimeDefinition) -> ObservationRegime:
    if regime.regime_id == BASELINE_REGIME_ID:
        return ObservationRegime(
            regime_id=regime.regime_id,
            regime_role=regime.regime_role,
            selected_default=True,
            is_benchmark_only=False,
            survey_times=tuple(range(0, 121, 12)),
            frame_probability=1.0,
            visit_probability=1.0,
            effort_scale=1.0,
            detection_scale=1.0,
            post_impact_gap_strength=0.0,
            perfect_observability=False,
            rationale=regime.interpretation,
        )
    return (
        observation_regime_for_target(regime)
        if regime.regime_id != CEILING_REGIME_ID
        else ObservationRegime(
            regime_id=regime.regime_id,
            regime_role=regime.regime_role,
            selected_default=False,
            is_benchmark_only=True,
            survey_times=tuple(range(0, 121, 12)),
            frame_probability=1.0,
            visit_probability=1.0,
            effort_scale=1.0,
            detection_scale=1.0,
            post_impact_gap_strength=0.0,
            perfect_observability=True,
            rationale=regime.interpretation,
        )
    )


def build_strata_effort_rows(
    source: SynthMediumObservationDesignResult,
    regimes: tuple[CounterfactualRegimeDefinition, ...],
    rows_by_regime: dict[str, tuple[CsvRow, ...]],
    reconstructed_rows: tuple[CsvRow, ...],
) -> tuple[CsvRow, ...]:
    passable_truth = passable_truth_rows(source)
    rows: list[CsvRow] = []
    for regime in regimes:
        obs_by_cell: dict[int, list[CsvRow]] = defaultdict(list)
        for row in rows_by_regime[regime.regime_id]:
            obs_by_cell[csv_int(row["cell_id"])].append(row)
        rec_by_cell = {
            csv_int(row["cell_id"]): row
            for row in reconstructed_rows
            if row["regime_id"] == regime.regime_id and row["rule_id"] == BASELINE_RULE_ID
        }
        groups: dict[str, list[SpreadImpactCellTruth]] = defaultdict(list)
        for truth in passable_truth:
            groups["all_passable"].append(truth)
            groups[f"habitat:{truth.landscape_cell.habitat_class}"].append(truth)
            groups[f"col_band:{truth.landscape_cell.col_band}"].append(truth)
            groups[f"row_band:{truth.landscape_cell.row_band}"].append(truth)
        for group, truths in sorted(groups.items()):
            survey_records = [
                row for truth in truths for row in obs_by_cell.get(truth.landscape_cell.cell_id, [])
            ]
            surveyed_cells = {
                truth.landscape_cell.cell_id
                for truth in truths
                if obs_by_cell.get(truth.landscape_cell.cell_id)
            }
            survey_counts = [
                len(obs_by_cell.get(truth.landscape_cell.cell_id, [])) for truth in truths
            ]
            effort_values = [csv_float(row["effort"]) for row in survey_records]
            detection_history = sum(
                csv_int(rec_by_cell[truth.landscape_cell.cell_id]["detection_count"]) > 0
                for truth in truths
            )
            final_absence = sum(
                csv_bool(rec_by_cell[truth.landscape_cell.cell_id]["reconstructed_finite"])
                for truth in truths
            )
            rows.append(
                {
                    "regime_id": regime.regime_id,
                    "summary_group": group,
                    "passable_cell_count": len(truths),
                    "survey_record_count": len(survey_records),
                    "surveyed_cell_count": len(surveyed_cells),
                    "mean_survey_count": round_float(mean(float(value) for value in survey_counts)),
                    "mean_effort": round_float(mean(effort_values)) if effort_values else 0.0,
                    "detection_history_support_count": detection_history,
                    "final_absence_support_count": final_absence,
                }
            )
    return tuple(rows)


def build_delta_rows(
    ranking_rows: tuple[CsvRow, ...],
    effort_rows: tuple[CsvRow, ...],
    support_rows: tuple[CsvRow, ...],
    regimes: tuple[CounterfactualRegimeDefinition, ...],
) -> tuple[CsvRow, ...]:
    baseline = baseline_ranking_row(ranking_rows)
    baseline_effort = effort_summary_row(effort_rows, BASELINE_REGIME_ID)
    baseline_support = support_row_for(support_rows, BASELINE_REGIME_ID, BASELINE_RULE_ID)
    regime_map = {regime.regime_id: regime for regime in regimes}
    rows: list[CsvRow] = []
    for row in ranking_rows:
        if csv_int(row["rank"]) != 1:
            continue
        effort = effort_summary_row(effort_rows, str(row["regime_id"]))
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
                "false_positive_delta": row["false_positive_delta_from_baseline"],
                "specificity_delta": round_float(
                    csv_float(row["specificity"]) - csv_float(baseline["specificity"])
                ),
                "precision_delta": round_float(
                    csv_float(row["precision"]) - csv_float(baseline["precision"])
                ),
                "median_absolute_error_delta": optional_delta(
                    row["median_absolute_error"], baseline["median_absolute_error"]
                ),
                "p90_absolute_error_delta": optional_delta(
                    row["p90_absolute_error"], baseline["p90_absolute_error"]
                ),
                "large_error_delta": row["large_error_delta_from_baseline"],
                "loss_delta": row["loss_delta_from_baseline"],
                "record_count_delta": csv_int(effort["survey_record_count"])
                - csv_int(baseline_effort["survey_record_count"]),
                "surveyed_cell_count_delta": csv_int(effort["surveyed_cell_count"])
                - csv_int(baseline_effort["surveyed_cell_count"]),
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
    effort_rows: tuple[CsvRow, ...],
    config: SynthMediumRecoverabilityTargetObservationDesignConfig,
) -> tuple[CsvRow, ...]:
    baseline = baseline_ranking_row(ranking_rows)
    best = best_field_plausible_row(ranking_rows)
    lowest_effort_ready = lowest_effort_ready_field_plausible_row(ranking_rows, effort_rows)
    ceiling = best_ranking_row(ranking_rows, CEILING_REGIME_ID)
    best_ready = best["regime_recommendation_class"] == "recoverability_review_ready"
    lowest_effort_ready_flag = (
        lowest_effort_ready["regime_recommendation_class"] == "recoverability_review_ready"
    )
    ceiling_ready = ceiling["regime_recommendation_class"] == "diagnostic_ceiling_recovers_signal"
    baseline_effort = effort_summary_row(effort_rows, BASELINE_REGIME_ID)
    ceiling_effort = effort_summary_row(effort_rows, CEILING_REGIME_ID)
    baseline_records = csv_int(baseline_effort["survey_record_count"])
    ceiling_records = csv_int(ceiling_effort["survey_record_count"])
    limiting = limiting_failure_modes(best, config)
    if best_ready:
        recommendation = "recoverability_review_ready"
        interpretation = (
            "A high-intensity field-plausible recoverability-target design meets the "
            "deterministic review gates; human review should decide whether the effort burden "
            "is logistically acceptable before any fitting work."
        )
    elif ceiling_ready and csv_float(best["finite_recall"]) >= (
        csv_float(baseline["finite_recall"]) + config.meaningful_recall_improvement_min
    ):
        recommendation = "plausible_design_improves_but_process_model_needed"
        interpretation = (
            "The best field-plausible design improves the baseline but remains below one or more "
            "reconstruction-review gates; a process observation model should be considered "
            "before fitting."
        )
    elif ceiling_ready:
        recommendation = "only_unrealistic_observation_ceiling_recovers_signal"
        interpretation = (
            "Only the diagnostic ceiling recovers signal; field-plausible designs remain too weak."
        )
    else:
        recommendation = "recoverability_target_design_blocked"
        interpretation = "Source or table reconciliation failed before a recoverability decision."
    decision = {
        "decision_id": "final_decision",
        "recommendation_class": recommendation,
        "baseline_regime_id": BASELINE_REGIME_ID,
        "baseline_rule_id": BASELINE_RULE_ID,
        "baseline_finite_recall": baseline["finite_recall"],
        "baseline_false_negative_count": baseline["false_negative_count"],
        "baseline_large_error_count": baseline["large_error_count"],
        "best_field_plausible_regime_id": best["regime_id"],
        "best_field_plausible_rule_id": best["rule_id"],
        "best_field_plausible_finite_recall": best["finite_recall"],
        "best_field_plausible_false_negative_count": best["false_negative_count"],
        "best_field_plausible_false_positive_count": best["false_positive_count"],
        "best_field_plausible_large_error_count": best["large_error_count"],
        "best_field_plausible_loss": best["loss"],
        "best_field_plausible_ready_for_reconstruction_review": best_ready,
        "best_performing_ready_regime_id": best["regime_id"] if best_ready else "",
        "best_performing_ready_rule_id": best["rule_id"] if best_ready else "",
        "lowest_effort_ready_regime_id": lowest_effort_ready["regime_id"]
        if lowest_effort_ready_flag
        else "",
        "lowest_effort_ready_rule_id": lowest_effort_ready["rule_id"]
        if lowest_effort_ready_flag
        else "",
        "lowest_effort_ready_finite_recall": lowest_effort_ready["finite_recall"]
        if lowest_effort_ready_flag
        else "",
        "lowest_effort_ready_false_negative_count": lowest_effort_ready["false_negative_count"]
        if lowest_effort_ready_flag
        else "",
        "lowest_effort_ready_false_positive_count": lowest_effort_ready["false_positive_count"]
        if lowest_effort_ready_flag
        else "",
        "lowest_effort_ready_large_error_count": lowest_effort_ready["large_error_count"]
        if lowest_effort_ready_flag
        else "",
        "lowest_effort_ready_loss": lowest_effort_ready["loss"] if lowest_effort_ready_flag else "",
        "lowest_effort_ready_ready_for_reconstruction_review": lowest_effort_ready_flag,
        "ceiling_regime_id": CEILING_REGIME_ID,
        "ceiling_rule_id": ceiling["rule_id"],
        "ceiling_finite_recall": ceiling["finite_recall"],
        "ceiling_false_negative_count": ceiling["false_negative_count"],
        "ceiling_ready_for_reconstruction_review": ceiling_ready,
        "limiting_failure_modes": limiting,
        "interpretation": interpretation,
    }
    decision.update(
        decision_effort_fields(
            "baseline", BASELINE_REGIME_ID, effort_rows, baseline_records, ceiling_records
        )
    )
    decision.update(
        decision_effort_fields(
            "best_field_plausible",
            str(best["regime_id"]),
            effort_rows,
            baseline_records,
            ceiling_records,
        )
    )
    decision.update(
        decision_effort_fields(
            "lowest_effort_ready",
            str(lowest_effort_ready["regime_id"]) if lowest_effort_ready_flag else "",
            effort_rows,
            baseline_records,
            ceiling_records,
        )
    )
    decision.update(
        decision_effort_fields(
            "ceiling", CEILING_REGIME_ID, effort_rows, baseline_records, ceiling_records
        )
    )
    return (decision,)


def verify_recoverability_target_result(
    config: SynthMediumRecoverabilityTargetObservationDesignConfig,
    source: SynthMediumObservationDesignResult,
    response_summary: dict[str, object],
    counterfactual_summary: dict[str, object],
    regimes: tuple[CounterfactualRegimeDefinition, ...],
    rules: tuple[ReconstructionRule, ...],
    effort_rows: tuple[CsvRow, ...],
    strata_rows: tuple[CsvRow, ...],
    reconstructed_rows: tuple[CsvRow, ...],
    error_rows: tuple[CsvRow, ...],
    support_rows: tuple[CsvRow, ...],
    ranking_rows: tuple[CsvRow, ...],
    delta_rows: tuple[CsvRow, ...],
    decision_rows: tuple[CsvRow, ...],
    visual_svgs: dict[str, str],
) -> tuple[RecoverabilityTargetCheck, ...]:
    baseline = baseline_ranking_row(ranking_rows)
    plausible = [
        regime for regime in regimes if regime.plausibility_class == "plausible_field_like"
    ]
    ceiling = best_ranking_row(ranking_rows, CEILING_REGIME_ID)
    passable_cell_count = sum(
        row.landscape_cell.passability == "passable" for row in source.truth.cell_truth_rows
    )
    expected_reconstructed = len(regimes) * len(rules) * passable_cell_count
    checks = (
        RecoverabilityTargetCheck(
            "artifact_contract",
            set(SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_FILES)
            == {
                "recoverability_target_config.json",
                "regime_definitions.csv",
                "observation_effort_summary.csv",
                "strata_effort_summary.csv",
                "reconstruction_benchmark_summary.csv",
                "support_gap_summary.csv",
                "baseline_to_candidate_delta.csv",
                "readiness_decision_summary.csv",
                "verification.json",
                "report.md",
            }
            and set(visual_svgs)
            == set(SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES),
            {
                "root_file_count": len(
                    SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_FILES
                ),
                "visual_file_count": len(visual_svgs),
            },
        ),
        RecoverabilityTargetCheck(
            "source_reconciliation",
            source.passed
            and response_summary["primary_default_rule_id"] == BASELINE_RULE_ID
            and counterfactual_summary["baseline_regime_id"] == BASELINE_REGIME_ID,
            source_reconciliation(source, response_summary, counterfactual_summary),
        ),
        RecoverabilityTargetCheck(
            "published_baseline_reconciled",
            baseline["rule_id"] == BASELINE_RULE_ID
            and csv_float(baseline["finite_recall"])
            == RESPONSE_RECONSTRUCTION_EXPECTATIONS["default_finite_recall"]
            and csv_int(baseline["false_negative_count"])
            == RESPONSE_RECONSTRUCTION_EXPECTATIONS["default_false_negative_count"]
            and csv_int(baseline["false_positive_count"])
            == RESPONSE_RECONSTRUCTION_EXPECTATIONS["default_false_positive_count"]
            and csv_int(baseline["large_error_count"])
            == RESPONSE_RECONSTRUCTION_EXPECTATIONS["default_large_error_count"],
            {
                "finite_recall": baseline["finite_recall"],
                "false_negative_count": baseline["false_negative_count"],
                "false_positive_count": baseline["false_positive_count"],
                "large_error_count": baseline["large_error_count"],
            },
        ),
        RecoverabilityTargetCheck(
            "candidate_regime_contract",
            len(regimes) == 8
            and len(plausible) == 6
            and all(
                not bool(regime_definition_row(regime)["uses_hidden_truth_for_design"])
                for regime in plausible
            ),
            {"regime_count": len(regimes), "plausible_candidate_count": len(plausible)},
        ),
        RecoverabilityTargetCheck(
            "field_plausible_candidates_compared",
            best_field_plausible_row(ranking_rows)["plausibility_class"] == "plausible_field_like"
            and csv_float(best_field_plausible_row(ranking_rows)["finite_recall"])
            > csv_float(baseline["finite_recall"]),
            {
                "plausible_candidate_count": len(plausible),
                "best_field_plausible_regime_id": best_field_plausible_row(ranking_rows)[
                    "regime_id"
                ],
            },
        ),
        RecoverabilityTargetCheck(
            "ceiling_is_reference_only",
            csv_int(ceiling["false_negative_count"]) == 0
            and ceiling["plausibility_class"] == "unrealistic_diagnostic_ceiling",
            {
                "ceiling_finite_recall": ceiling["finite_recall"],
                "ceiling_false_negative_count": ceiling["false_negative_count"],
            },
        ),
        RecoverabilityTargetCheck(
            "table_reconciliation",
            len(effort_rows) == len(regimes)
            and len(delta_rows) == len(regimes)
            and len([row for row in ranking_rows if csv_int(row["rank"]) == 1]) == len(regimes)
            and len(strata_rows) >= len(regimes) * 10
            and len(reconstructed_rows) > 0
            and len(error_rows) > 0
            and len(support_rows) > 0
            and expected_reconstructed > 0,
            {
                "effort_row_count": len(effort_rows),
                "ranking_row_count": len(ranking_rows),
                "delta_row_count": len(delta_rows),
                "strata_row_count": len(strata_rows),
            },
        ),
        RecoverabilityTargetCheck(
            "visual_contract",
            visual_contract_passes(visual_svgs),
            {"visual_files": sorted(visual_svgs)},
        ),
    )
    return checks


def source_reconciliation(
    source: SynthMediumObservationDesignResult,
    response_summary: dict[str, object],
    counterfactual_summary: dict[str, object],
) -> dict[str, object]:
    truth_summary = source.truth.summary_dict()
    observation_summary = source.summary_dict()
    return {
        "landscape": {
            "cell_count": truth_summary["cell_count"],
            "passable_cell_count": truth_summary["passable_cell_count"],
            "water_cell_count": truth_summary["water_cell_count"],
        },
        "spread_impact": {
            "selected_parameter_set_id": truth_summary["selected_parameter_set_id"],
            "final_colonized_passable_count": truth_summary["final_colonized_passable_count"],
            "finite_prey_extirpation_count": truth_summary["finite_prey_extirpation_count"],
        },
        "observation_design": observation_summary,
        "response_reconstruction": response_summary,
        "observation_design_counterfactual": counterfactual_summary,
    }


def build_visual_svgs(
    source: SynthMediumObservationDesignResult,
    reconstructed_rows: tuple[CsvRow, ...],
    bridge_rows: tuple[CsvRow, ...],
    ranking_rows: tuple[CsvRow, ...],
    effort_rows: tuple[CsvRow, ...],
) -> dict[str, str]:
    best = best_field_plausible_row(ranking_rows)
    panels = (
        ("Baseline", BASELINE_REGIME_ID, BASELINE_RULE_ID),
        ("Best field-plausible", str(best["regime_id"]), str(best["rule_id"])),
        (
            "Diagnostic ceiling",
            CEILING_REGIME_ID,
            str(best_ranking_row(ranking_rows, CEILING_REGIME_ID)["rule_id"]),
        ),
    )
    return {
        "effort_support_surfaces.svg": render_effort_surfaces(source, reconstructed_rows, panels),
        "support_gap_maps.svg": render_support_gap_maps(source, reconstructed_rows, panels),
        "residual_maps.svg": render_residual_maps(source, bridge_rows, panels),
        "recoverability_decision_montage.svg": render_decision_montage(ranking_rows, effort_rows),
        "ceiling_reference_panel.svg": render_ceiling_reference_panel(
            source, bridge_rows, ranking_rows
        ),
    }


def render_effort_surfaces(
    source: SynthMediumObservationDesignResult,
    reconstructed_rows: tuple[CsvRow, ...],
    panels: tuple[tuple[str, str, str], ...],
) -> str:
    rows = source.truth.cell_truth_rows
    rec = {
        (row["regime_id"], row["rule_id"], csv_int(row["cell_id"])): row
        for row in reconstructed_rows
    }
    width = 820
    panel_height = 610
    height = 90 + panel_height * len(panels)
    lines = svg_header(width, height, "Effort and survey-support surfaces")
    lines.append(
        '<text x="20" y="32" font-size="22" font-family="monospace">'
        "Effort and survey-support surfaces</text>"
    )
    for index, (title, regime_id, rule_id) in enumerate(panels):
        panel_top = 52 + index * panel_height

        def fill(
            truth: SpreadImpactCellTruth,
            *,
            panel_regime_id: str = regime_id,
            panel_rule_id: str = rule_id,
        ) -> str:
            if truth.landscape_cell.passability != "passable":
                return "#ffffff"
            row = rec.get((panel_regime_id, panel_rule_id, truth.landscape_cell.cell_id))
            if row is None or csv_int(row["survey_count"]) == 0:
                return "#f3f4f6"
            if csv_int(row["survey_count"]) >= 14:
                return "#1d4ed8"
            return "#bfdbfe"

        render_map_panel(
            lines,
            rows,
            panel_id=f"effort-{index}",
            title=f"{title} effort/support",
            panel_top=panel_top,
            fill_for=fill,
            legend_items=EFFORT_LEGEND,
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_support_gap_maps(
    source: SynthMediumObservationDesignResult,
    reconstructed_rows: tuple[CsvRow, ...],
    panels: tuple[tuple[str, str, str], ...],
) -> str:
    rows = source.truth.cell_truth_rows
    rec = {
        (row["regime_id"], row["rule_id"], csv_int(row["cell_id"])): row
        for row in reconstructed_rows
    }
    width = 820
    panel_height = 610
    height = 90 + panel_height * len(panels)
    lines = svg_header(width, height, "Support-gap maps")
    lines.append(
        '<text x="20" y="32" font-size="22" font-family="monospace">Support-gap maps</text>'
    )
    for index, (title, regime_id, rule_id) in enumerate(panels):
        panel_top = 52 + index * panel_height

        def fill(
            truth: SpreadImpactCellTruth,
            *,
            panel_regime_id: str = regime_id,
            panel_rule_id: str = rule_id,
        ) -> str:
            if truth.landscape_cell.passability != "passable":
                return "#ffffff"
            return support_gap_fill(
                rec.get((panel_regime_id, panel_rule_id, truth.landscape_cell.cell_id))
            )

        render_map_panel(
            lines,
            rows,
            panel_id=f"support-{index}",
            title=f"{title} support gaps",
            panel_top=panel_top,
            fill_for=fill,
            legend_items=SUPPORT_LEGEND,
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_residual_maps(
    source: SynthMediumObservationDesignResult,
    bridge_rows: tuple[CsvRow, ...],
    panels: tuple[tuple[str, str, str], ...],
) -> str:
    rows = source.truth.cell_truth_rows
    bridge = {
        (row["regime_id"], row["rule_id"], csv_int(row["cell_id"])): row for row in bridge_rows
    }
    width = 820
    panel_height = 610
    height = 90 + panel_height * len(panels)
    lines = svg_header(width, height, "Reconstructed-vs-truth residual maps")
    lines.append(
        '<text x="20" y="32" font-size="22" font-family="monospace">'
        "Reconstructed-vs-truth residual maps</text>"
    )
    for index, (title, regime_id, rule_id) in enumerate(panels):
        panel_top = 52 + index * panel_height

        def fill(
            truth: SpreadImpactCellTruth,
            *,
            panel_regime_id: str = regime_id,
            panel_rule_id: str = rule_id,
        ) -> str:
            if truth.landscape_cell.passability != "passable":
                return "#ffffff"
            return residual_error_fill(
                bridge.get((panel_regime_id, panel_rule_id, truth.landscape_cell.cell_id))
            )

        render_map_panel(
            lines,
            rows,
            panel_id=f"residual-{index}",
            title=f"{title} residuals",
            panel_top=panel_top,
            fill_for=fill,
            legend_items=RESIDUAL_LEGEND,
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_decision_montage(
    ranking_rows: tuple[CsvRow, ...],
    effort_rows: tuple[CsvRow, ...],
) -> str:
    best_rows = sorted(
        (row for row in ranking_rows if csv_int(row["rank"]) == 1),
        key=lambda row: (
            0
            if row["regime_id"] == BASELINE_REGIME_ID
            else 2
            if row["regime_id"] == CEILING_REGIME_ID
            else 1,
            field_plausible_selection_key(row)
            if row["plausibility_class"] == "plausible_field_like"
            else (9, 0.0, 0, 0, 0.0, 0, str(row["regime_id"])),
        ),
    )
    effort_by_regime = {
        str(row["regime_id"]): csv_int(row["survey_record_count"]) for row in effort_rows
    }
    width = 1800
    height = 120 + 44 * len(best_rows)
    lines = svg_header(width, height, "Recoverability-target decision montage")
    lines.append(
        '<text x="24" y="34" font-size="22" font-family="monospace">'
        "Recoverability-target decision table</text>"
    )
    lines.append(
        '<text x="24" y="60" font-size="12" font-family="monospace">'
        "field-plausible rows are compared separately from the unrealistic diagnostic "
        "ceiling</text>"
    )
    columns = (
        ("Regime", 24, 34),
        ("Role", 340, 16),
        ("Rule", 500, 24),
        ("Recall", 720, 8),
        ("Records", 850, 8),
        ("False negatives", 980, 12),
        ("Large errors", 1170, 12),
        ("Loss", 1330, 8),
        ("Class", 1460, 24),
    )
    lines.append('<rect x="18" y="82" width="1710" height="30" fill="#f8fafc" />')
    for label, x, _ in columns:
        lines.append(
            f'<text x="{x}" y="102" font-size="12" font-family="monospace" '
            f'font-weight="bold">{label}</text>'
        )
    for index, row in enumerate(best_rows):
        y = 138 + index * 44
        fill = "#ffffff" if index % 2 == 0 else "#f8fafc"
        role = (
            "ceiling"
            if row["plausibility_class"] == "unrealistic_diagnostic_ceiling"
            else "field-plausible"
            if row["plausibility_class"] == "plausible_field_like"
            else "baseline"
        )
        values = (
            short_regime_label(str(row["regime_id"])),
            role,
            str(row["rule_id"]),
            f"{csv_float(row['finite_recall']):.3f}",
            str(effort_by_regime[str(row["regime_id"])]),
            str(row["false_negative_count"]),
            str(row["large_error_count"]),
            f"{csv_float(row['loss']):.3f}",
            short_recommendation(str(row["regime_recommendation_class"])),
        )
        lines.append(f'<rect x="18" y="{y - 26}" width="1710" height="34" fill="{fill}" />')
        for value, (_, x, max_chars) in zip(values, columns, strict=True):
            lines.append(
                f'<text x="{x}" y="{y - 5}" font-size="12" font-family="monospace">'
                f"{fit_table_label(value, max_chars)}</text>"
            )
        recall_bar = int(min(csv_float(row["finite_recall"]), 1.0) * 100)
        lines.append(f'<rect x="720" y="{y + 3}" width="100" height="8" fill="#e5e7eb" />')
        lines.append(f'<rect x="720" y="{y + 3}" width="{recall_bar}" height="8" fill="#2563eb" />')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_ceiling_reference_panel(
    source: SynthMediumObservationDesignResult,
    bridge_rows: tuple[CsvRow, ...],
    ranking_rows: tuple[CsvRow, ...],
) -> str:
    ceiling = best_ranking_row(ranking_rows, CEILING_REGIME_ID)
    return render_residual_maps(
        source,
        bridge_rows,
        (
            ("Best field-plausible", BEST_FIELD_PLAUSIBLE_REGIME_ID, BASELINE_RULE_ID),
            ("Diagnostic ceiling", CEILING_REGIME_ID, str(ceiling["rule_id"])),
        ),
    ).replace(
        "Reconstructed-vs-truth residual maps",
        "Ceiling reference panel",
        2,
    )


def visual_contract_passes(visual_svgs: dict[str, str]) -> bool:
    if set(visual_svgs) != set(SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES):
        return False
    for name, svg in visual_svgs.items():
        if not svg.lstrip().startswith("<svg"):
            return False
        if name != "recoverability_decision_montage.svg" and "Legend" not in svg:
            return False
    return True


def render_recoverability_target_report(
    result: SynthMediumRecoverabilityTargetObservationDesignResult,
) -> str:
    decision = result.decision_rows[0]
    lines = [
        "# Synth-Medium recoverability-target observation-design review pack",
        "",
        "This synthetic-only, review-only pack tests whether a more serious but still "
        "field-plausible response-observation design can make the published Goal 018 truth "
        "recoverable enough for later fitting review.",
        "",
        f"- Recommendation: `{result.recommendation_class}`",
        f"- Baseline: `{BASELINE_REGIME_ID}` / `{BASELINE_RULE_ID}`",
        f"- Best field-plausible candidate: `{decision['best_field_plausible_regime_id']}` / "
        f"`{decision['best_field_plausible_rule_id']}`",
        f"- Best field-plausible finite recall: `{decision['best_field_plausible_finite_recall']}`",
        "- Best field-plausible false negatives: "
        f"`{decision['best_field_plausible_false_negative_count']}`",
        "- Best field-plausible survey records: "
        f"`{decision['best_field_plausible_survey_record_count']}` "
        f"({csv_float(decision['best_field_plausible_survey_record_ratio_vs_baseline']):.3f}x "
        "baseline; "
        f"{csv_float(decision['best_field_plausible_survey_record_ratio_vs_ceiling']):.3f}x "
        "ceiling)",
        "- Lowest-effort ready candidate: "
        f"`{decision['lowest_effort_ready_regime_id']}` / "
        f"`{decision['lowest_effort_ready_rule_id']}` with "
        f"`{decision['lowest_effort_ready_survey_record_count']}` survey records",
        f"- Diagnostic ceiling finite recall: `{decision['ceiling_finite_recall']}`",
        f"- Diagnostic ceiling survey records: `{decision['ceiling_survey_record_count']}`",
        "",
        "The best-performing field-plausible design exceeds the diagnostic ceiling record count; "
        "the positive recommendation therefore means recoverability is possible under "
        "high-intensity field-plausible designs, not that fitting should begin without a "
        "human logistics review.",
        "",
        "## Visual review files",
        "",
    ]
    for visual_name in SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES:
        lines.append(f"- `visuals/{visual_name}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "No production observation design or reconstruction rule is adopted here. No fitting, "
            "ABC/POM/likelihood/MCMC/posterior, parameter recovery, real-data analysis, remote "
            "compute, broad sweep, or follow-on goal work is performed.",
            "",
        ]
    )
    return "\n".join(lines)


def baseline_ranking_row(ranking_rows: tuple[CsvRow, ...]) -> CsvRow:
    return next(
        row
        for row in ranking_rows
        if row["regime_id"] == BASELINE_REGIME_ID and row["rule_id"] == BASELINE_RULE_ID
    )


def best_field_plausible_row(ranking_rows: tuple[CsvRow, ...]) -> CsvRow:
    best_rows = [
        row
        for row in ranking_rows
        if csv_int(row["rank"]) == 1 and row["plausibility_class"] == "plausible_field_like"
    ]
    return sorted(best_rows, key=field_plausible_selection_key)[0]


def field_plausible_selection_key(row: CsvRow) -> tuple[int, float, int, int, float, int, str]:
    return (
        recommendation_priority(str(row["regime_recommendation_class"])),
        csv_float(row["loss"]),
        csv_int(row["false_negative_count"]),
        csv_int(row["large_error_count"]),
        -csv_float(row["finite_recall"]),
        csv_int(row["false_positive_count"]),
        str(row["regime_id"]),
    )


def recommendation_priority(recommendation_class: str) -> int:
    priorities = {
        "recoverability_review_ready": 0,
        "field_plausible_improved_but_not_ready": 1,
        "baseline_not_recoverable_enough": 2,
        "diagnostic_ceiling_recovers_signal": 3,
    }
    return priorities.get(recommendation_class, 9)


def lowest_effort_ready_field_plausible_row(
    ranking_rows: tuple[CsvRow, ...],
    effort_rows: tuple[CsvRow, ...],
) -> CsvRow:
    ready_rows = [
        row
        for row in ranking_rows
        if csv_int(row["rank"]) == 1
        and row["plausibility_class"] == "plausible_field_like"
        and row["regime_recommendation_class"] == "recoverability_review_ready"
    ]
    if not ready_rows:
        return best_field_plausible_row(ranking_rows)
    effort_by_regime = {
        str(row["regime_id"]): csv_int(row["survey_record_count"]) for row in effort_rows
    }
    return sorted(
        ready_rows,
        key=lambda row: (
            effort_by_regime[str(row["regime_id"])],
            csv_float(row["loss"]),
            csv_int(row["false_negative_count"]),
            csv_int(row["large_error_count"]),
            -csv_float(row["finite_recall"]),
            csv_int(row["false_positive_count"]),
            str(row["regime_id"]),
        ),
    )[0]


def decision_effort_fields(
    prefix: str,
    regime_id: str,
    effort_rows: tuple[CsvRow, ...],
    baseline_records: int,
    ceiling_records: int,
) -> CsvRow:
    if not regime_id:
        return {
            f"{prefix}_survey_record_count": "",
            f"{prefix}_survey_record_delta_vs_baseline": "",
            f"{prefix}_survey_record_ratio_vs_baseline": "",
            f"{prefix}_survey_record_delta_vs_ceiling": "",
            f"{prefix}_survey_record_ratio_vs_ceiling": "",
            f"{prefix}_surveyed_cell_count": "",
            f"{prefix}_final_absence_support_count": "",
        }
    effort = effort_summary_row(effort_rows, regime_id)
    survey_record_count = csv_int(effort["survey_record_count"])
    return {
        f"{prefix}_survey_record_count": survey_record_count,
        f"{prefix}_survey_record_delta_vs_baseline": survey_record_count - baseline_records,
        f"{prefix}_survey_record_ratio_vs_baseline": survey_record_count / baseline_records,
        f"{prefix}_survey_record_delta_vs_ceiling": survey_record_count - ceiling_records,
        f"{prefix}_survey_record_ratio_vs_ceiling": survey_record_count / ceiling_records,
        f"{prefix}_surveyed_cell_count": effort["surveyed_cell_count"],
        f"{prefix}_final_absence_support_count": effort["final_absence_support_count"],
    }


def support_row_for(rows: tuple[CsvRow, ...], regime_id: str, rule_id: str) -> CsvRow:
    return next(
        row
        for row in rows
        if row["regime_id"] == regime_id
        and row["rule_id"] == rule_id
        and row["summary_group"] == "all_passable"
    )


def effort_summary_row(rows: tuple[CsvRow, ...], regime_id: str) -> CsvRow:
    return next(row for row in rows if row["regime_id"] == regime_id)


def optional_int(value: CsvValue) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def optional_delta(value: CsvValue, baseline: CsvValue) -> float | None:
    if value is None or value == "" or baseline is None or baseline == "":
        return None
    return round_float(csv_float(value) - csv_float(baseline))


def delta_interpretation(
    row: CsvRow,
    regime: CounterfactualRegimeDefinition,
) -> str:
    if regime.regime_id == BASELINE_REGIME_ID:
        return "published baseline reference"
    if regime.plausibility_class == "unrealistic_diagnostic_ceiling":
        return "diagnostic ceiling only; not a field design"
    if row["regime_recommendation_class"] == "recoverability_review_ready":
        return "field-plausible candidate meets deterministic review gates"
    return "field-plausible candidate improves selected metrics but remains diagnostic"


def limiting_failure_modes(
    row: CsvRow,
    config: SynthMediumRecoverabilityTargetObservationDesignConfig,
) -> str:
    modes: list[str] = []
    if csv_float(row["finite_recall"]) < config.ready_finite_recall_min:
        modes.append("finite_recall")
    if csv_int(row["false_negative_count"]) > config.ready_false_negative_max:
        modes.append("false_negatives")
    if csv_int(row["false_positive_count"]) > config.ready_false_positive_max:
        modes.append("false_positives")
    if csv_float(row["median_absolute_error"]) > config.ready_median_abs_error_max:
        modes.append("median_abs_error")
    if csv_int(row["large_error_count"]) > config.ready_large_error_count_max:
        modes.append("large_errors")
    return ";".join(modes) if modes else "none"
