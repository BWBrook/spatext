"""Target-timing residual decomposition for synth-small diagnostics."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from csv import DictReader, writer
from dataclasses import dataclass, field
from json import dumps, loads
from math import isfinite
from os import PathLike
from pathlib import Path
from typing import Any

from .compatibility_screen import (
    CANDIDATE_SCORE_COLUMNS,
    MODE_RANKING_COLUMNS,
    CandidateScoreRow,
    CompatibilityScreenConfig,
    ModeRankingRow,
    build_candidate_profile,
    build_mode_rankings,
    scalar_value,
    score_candidate_against_target,
)
from .compatibility_screen import (
    DEFAULT_OUTPUT_DIR as DEFAULT_COMPATIBILITY_SCREEN_DIR,
)
from .false_negative_mechanism_audit import (
    DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
    DEFAULT_OBSERVATION_DIR,
    DEFAULT_RECONSTRUCTION_DIR,
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
)
from .observation_support_counterfactual_screen import (
    DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR,
)
from .observations import stringify_float
from .summary_vector import (
    DEFAULT_COVERAGE_BREAKPOINTS,
    CoverageCurveRow,
    SummaryComponentRow,
    SummaryVectorTargetRow,
    build_coverage_curve_rows,
    build_summary_component_rows,
)
from .summary_vector import (
    DEFAULT_OUTPUT_DIR as DEFAULT_SUMMARY_VECTOR_DIR,
)

DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR = (
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR / "target_timing_residual_decomposition"
)
TARGET_TIMING_RESIDUAL_DECOMPOSITION_NAME = "synth-small-target-timing-residual-decomposition"
TARGET_TRANSFORM_IDS = (
    "status_quo_observed",
    "goal013_support_floor",
    "false_negative_true_time",
    "false_negative_true_time_detection_respecting",
    "all_extirpated_true_time",
)
TARGET_TIMING_RESIDUAL_OUTPUT_FILES = (
    "residual_decomposition_config.json",
    "target_transform_definitions.csv",
    "site_target_transform_resolution.csv",
    "target_transform_summary_vectors.csv",
    "target_transform_component_losses.csv",
    "target_transform_rankings.csv",
    "component_delta_table.csv",
    "recommendation.json",
    "verification.json",
    "report.md",
)
OBSERVATION_REQUIRED_FILES = (
    "observation_config.json",
    "sites.csv",
    "visits.csv",
    "observations.csv",
    "evaluation_truth.csv",
    "truth_reference.json",
)
RECONSTRUCTION_REQUIRED_FILES = (
    "reconstruction_config.json",
    "site_reconstruction.csv",
    "time_detection_summary.csv",
    "verification.json",
)
EVALUATION_REQUIRED_FILES = (
    "screen_evaluation_summary.json",
    "site_evaluation_audit.csv",
    "verification.json",
)
FALSE_NEGATIVE_AUDIT_REQUIRED_FILES = (
    "false_negative_audit_config.json",
    "false_negative_site_audit.csv",
    "mechanism_summary.csv",
    "recommendation.json",
    "verification.json",
)
COUNTERFACTUAL_REQUIRED_FILES = (
    "counterfactual_config.json",
    "site_counterfactual_resolution.csv",
    "scenario_reconstruction_summary.csv",
    "scenario_summary_vectors.csv",
    "scenario_compatibility_scores.csv",
    "scenario_rankings.csv",
    "verification.json",
)
SUMMARY_VECTOR_REQUIRED_FILES = (
    "summary_vector_config.json",
    "summary_components.csv",
    "mode_summary.json",
    "coverage_curve.csv",
    "verification.json",
)
COMPATIBILITY_REQUIRED_FILES = (
    "target_summary.json",
    "candidate_scores.csv",
    "mode_rankings.csv",
    "coverage_score_breakdown.csv",
    "verification.json",
)
TARGET_TRANSFORM_DEFINITION_COLUMNS = (
    "target_transform_id",
    "label",
    "transform_type",
    "uses_hidden_truth",
    "diagnostic_upper_bound",
    "respects_post_extirpation_detections",
    "target_site_rule",
    "target_time_rule",
    "scientific_contrast",
    "interpretation_limit",
)
SITE_TARGET_TRANSFORM_COLUMNS = (
    "target_transform_id",
    "site_id",
    "cell_id",
    "row",
    "col",
    "region",
    "front_band",
    "false_negative",
    "primary_mechanism",
    "post_extirpation_detection_count",
    "driver_arrival",
    "status_quo_target_time",
    "transformed_target_time",
    "true_extirpation_time",
    "goal013_counterfactual_time",
    "target_time_delta_from_status_quo",
    "resolution_class",
    "uses_hidden_truth",
)
TARGET_TRANSFORM_SUMMARY_VECTOR_COLUMNS = (
    "target_transform_id",
    "row_type",
    "metric",
    "value",
    "coverage_fraction",
    "finite_target_count",
    "missing_reason",
)
TARGET_TRANSFORM_COMPONENT_LOSS_COLUMNS = ("target_transform_id", *CANDIDATE_SCORE_COLUMNS[1:])
TARGET_TRANSFORM_RANKING_COLUMNS = ("target_transform_id", *MODE_RANKING_COLUMNS[1:])
COMPONENT_DELTA_COLUMNS = (
    "target_transform_id",
    "candidate_label",
    "is_default",
    "component",
    "weighted_gap",
    "status_quo_weighted_gap",
    "delta_from_status_quo_weighted_gap",
    "goal013_support_floor_weighted_gap",
    "delta_from_goal013_support_floor_weighted_gap",
    "absolute_delta_from_status_quo_weighted_gap",
    "absolute_delta_from_goal013_support_floor_weighted_gap",
    "residual_rank_within_transform_candidate",
    "absolute_delta_from_status_quo_rank_within_transform_candidate",
    "absolute_delta_from_goal013_support_floor_rank_within_transform_candidate",
    "missing_reason",
)
NON_INFERENCE_LABEL_KEYS = (
    "synthetic_only",
    "evaluation_only",
    "target_transform_diagnostic_only",
    "not_formal_inference",
    "no_default_observation_change",
    "no_reconstruction_rule_change",
    "no_scoring_change",
    "no_candidate_change",
)
GOAL013_SUPPORT_SCENARIO_ID = "truth_guided_absence_floor_all"


@dataclass(frozen=True, slots=True)
class TargetTransformDefinition:
    target_transform_id: str
    label: str
    transform_type: str
    uses_hidden_truth: bool
    diagnostic_upper_bound: bool
    respects_post_extirpation_detections: bool
    target_site_rule: str
    target_time_rule: str
    scientific_contrast: str
    interpretation_limit: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_transform_id,
            self.label,
            self.transform_type,
            stringify_bool(self.uses_hidden_truth),
            stringify_bool(self.diagnostic_upper_bound),
            stringify_bool(self.respects_post_extirpation_detections),
            self.target_site_rule,
            self.target_time_rule,
            self.scientific_contrast,
            self.interpretation_limit,
        )


def default_target_transform_definitions() -> tuple[TargetTransformDefinition, ...]:
    """Return the ordered Goal 014 target-transform set."""

    return (
        TargetTransformDefinition(
            target_transform_id="status_quo_observed",
            label="Status quo observed target",
            transform_type="baseline",
            uses_hidden_truth=False,
            diagnostic_upper_bound=False,
            respects_post_extirpation_detections=True,
            target_site_rule="all sites use current reconstruction target",
            target_time_rule="site_reconstruction.csv:observed_extirpation_time",
            scientific_contrast="reconciles the Goal 010 realistic_observed baseline",
            interpretation_limit="baseline reconciliation only",
        ),
        TargetTransformDefinition(
            target_transform_id="goal013_support_floor",
            label="Goal 013 all false-negative support floor",
            transform_type="emitted_counterfactual",
            uses_hidden_truth=True,
            diagnostic_upper_bound=True,
            respects_post_extirpation_detections=False,
            target_site_rule="Goal 013 truth_guided_absence_floor_all resolutions",
            target_time_rule="counterfactual support time for resolved false negatives",
            scientific_contrast="separates finite-target restoration from timing accuracy",
            interpretation_limit="synthetic upper-bound target, not observation design",
        ),
        TargetTransformDefinition(
            target_transform_id="false_negative_true_time",
            label="False negatives at true extirpation time",
            transform_type="truth_guided_diagnostic",
            uses_hidden_truth=True,
            diagnostic_upper_bound=True,
            respects_post_extirpation_detections=False,
            target_site_rule="all Goal 012 false-negative sites",
            target_time_rule="evaluation_truth.csv:true_extirpation for false negatives",
            scientific_contrast="tests whether false-negative support timing alone is enough",
            interpretation_limit="truth-guided diagnostic target only",
        ),
        TargetTransformDefinition(
            target_transform_id="false_negative_true_time_detection_respecting",
            label="Detection-respecting false negatives at true time",
            transform_type="truth_guided_diagnostic",
            uses_hidden_truth=True,
            diagnostic_upper_bound=False,
            respects_post_extirpation_detections=True,
            target_site_rule="false negatives without post-extirpation detections",
            target_time_rule="evaluation_truth.csv:true_extirpation for unblocked false negatives",
            scientific_contrast="keeps post-extirpation detections as unresolved blockers",
            interpretation_limit="truth-guided diagnostic target only",
        ),
        TargetTransformDefinition(
            target_transform_id="all_extirpated_true_time",
            label="All extirpated sites at true time",
            transform_type="ideal_truth_reference",
            uses_hidden_truth=True,
            diagnostic_upper_bound=True,
            respects_post_extirpation_detections=False,
            target_site_rule="all truly extirpated finite target sites",
            target_time_rule="evaluation_truth.csv:true_extirpation for all finite truth targets",
            scientific_contrast="must reconcile with Goal 010 ideal_true compatibility",
            interpretation_limit="synthetic ideal-truth reference only",
        ),
    )


@dataclass(frozen=True, slots=True)
class TargetTimingResidualDecompositionConfig:
    observation_dir: str = str(DEFAULT_OBSERVATION_DIR)
    reconstruction_dir: str = str(DEFAULT_RECONSTRUCTION_DIR)
    evaluation_dir: str = str(DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR)
    false_negative_audit_dir: str = str(DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR)
    observation_support_counterfactual_dir: str = str(
        DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR
    )
    summary_vector_dir: str = str(DEFAULT_SUMMARY_VECTOR_DIR)
    compatibility_screen_dir: str = str(DEFAULT_COMPATIBILITY_SCREEN_DIR)
    target_transforms: tuple[TargetTransformDefinition, ...] = field(
        default_factory=default_target_transform_definitions
    )
    coverage_breakpoints: tuple[float, ...] = DEFAULT_COVERAGE_BREAKPOINTS
    compatibility_config: CompatibilityScreenConfig = field(
        default_factory=lambda: CompatibilityScreenConfig(
            target_modes=TARGET_TRANSFORM_IDS,
            primary_target_mode="status_quo_observed",
        )
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            **residual_labels(),
            "diagnostic_name": TARGET_TIMING_RESIDUAL_DECOMPOSITION_NAME,
            "observation_dir": self.observation_dir,
            "reconstruction_dir": self.reconstruction_dir,
            "evaluation_dir": self.evaluation_dir,
            "false_negative_audit_dir": self.false_negative_audit_dir,
            "observation_support_counterfactual_dir": (self.observation_support_counterfactual_dir),
            "summary_vector_dir": self.summary_vector_dir,
            "compatibility_screen_dir": self.compatibility_screen_dir,
            "target_transform_ids": [
                transform.target_transform_id for transform in self.target_transforms
            ],
            "coverage_breakpoints": list(self.coverage_breakpoints),
            "compatibility_contract": {
                "candidate_count": len(self.compatibility_config.candidates),
                "candidate_labels": [
                    candidate.label for candidate in self.compatibility_config.candidates
                ],
                "required_components": list(self.compatibility_config.required_components),
                "gap_settings": [
                    setting.to_dict() for setting in self.compatibility_config.gap_settings
                ],
                "compatible_loss_max": self.compatibility_config.compatible_loss_max,
                "borderline_loss_max": self.compatibility_config.borderline_loss_max,
            },
            "output_files": list(TARGET_TIMING_RESIDUAL_OUTPUT_FILES),
        }


@dataclass(frozen=True, slots=True)
class LoadedTargetTimingResidualInputs:
    observation_dir: Path
    reconstruction_dir: Path
    evaluation_dir: Path
    false_negative_audit_dir: Path
    observation_support_counterfactual_dir: Path
    summary_vector_dir: Path
    compatibility_screen_dir: Path
    observation_config: dict[str, Any]
    truth_rows: tuple[dict[str, str], ...]
    truth_reference: dict[str, Any]
    reconstruction_config: dict[str, Any]
    reconstruction_rows: tuple[dict[str, str], ...]
    reconstruction_verification: dict[str, Any]
    evaluation_summary: dict[str, Any]
    site_evaluation_rows: tuple[dict[str, str], ...]
    evaluation_verification: dict[str, Any]
    false_negative_config: dict[str, Any]
    false_negative_site_rows: tuple[dict[str, str], ...]
    false_negative_mechanism_rows: tuple[dict[str, str], ...]
    false_negative_recommendation: dict[str, Any]
    false_negative_verification: dict[str, Any]
    counterfactual_config: dict[str, Any]
    counterfactual_site_rows: tuple[dict[str, str], ...]
    counterfactual_summary_rows: tuple[dict[str, str], ...]
    counterfactual_score_rows: tuple[dict[str, str], ...]
    counterfactual_ranking_rows: tuple[dict[str, str], ...]
    counterfactual_verification: dict[str, Any]
    summary_vector_config: dict[str, Any]
    summary_vector_component_rows: tuple[dict[str, str], ...]
    summary_vector_coverage_rows: tuple[dict[str, str], ...]
    summary_vector_mode_summary: dict[str, Any]
    summary_vector_verification: dict[str, Any]
    compatibility_target_summary: dict[str, Any]
    compatibility_candidate_score_rows: tuple[dict[str, str], ...]
    compatibility_mode_ranking_rows: tuple[dict[str, str], ...]
    compatibility_coverage_score_rows: tuple[dict[str, str], ...]
    compatibility_verification: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SiteTargetTransformResolutionRow:
    target_transform_id: str
    site_id: str
    cell_id: int
    row: int
    col: int
    region: str
    front_band: str
    false_negative: bool
    primary_mechanism: str
    post_extirpation_detection_count: int
    driver_arrival: float | None
    status_quo_target_time: float | None
    transformed_target_time: float | None
    true_extirpation_time: float | None
    goal013_counterfactual_time: float | None
    target_time_delta_from_status_quo: float | None
    resolution_class: str
    uses_hidden_truth: bool

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_transform_id,
            self.site_id,
            str(self.cell_id),
            str(self.row),
            str(self.col),
            self.region,
            self.front_band,
            stringify_bool(self.false_negative),
            self.primary_mechanism,
            str(self.post_extirpation_detection_count),
            stringify_optional_float(self.driver_arrival),
            stringify_optional_float(self.status_quo_target_time),
            stringify_optional_float(self.transformed_target_time),
            stringify_optional_float(self.true_extirpation_time),
            stringify_optional_float(self.goal013_counterfactual_time),
            stringify_optional_float(self.target_time_delta_from_status_quo),
            self.resolution_class,
            stringify_bool(self.uses_hidden_truth),
        )


@dataclass(frozen=True, slots=True)
class TargetTransformSummaryVectorRow:
    target_transform_id: str
    row_type: str
    metric: str
    value: str
    coverage_fraction: float | None = None
    finite_target_count: int | None = None
    missing_reason: str = ""

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_transform_id,
            self.row_type,
            self.metric,
            self.value,
            stringify_optional_float(self.coverage_fraction),
            "" if self.finite_target_count is None else str(self.finite_target_count),
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class ComponentDeltaRow:
    target_transform_id: str
    candidate_label: str
    is_default: bool
    component: str
    weighted_gap: float | None
    status_quo_weighted_gap: float | None
    delta_from_status_quo_weighted_gap: float | None
    goal013_support_floor_weighted_gap: float | None
    delta_from_goal013_support_floor_weighted_gap: float | None
    residual_rank_within_transform_candidate: int
    absolute_delta_from_status_quo_rank_within_transform_candidate: int
    absolute_delta_from_goal013_support_floor_rank_within_transform_candidate: int
    missing_reason: str

    def to_csv_row(self) -> tuple[str, ...]:
        status_delta_abs = absolute_value(self.delta_from_status_quo_weighted_gap)
        support_delta_abs = absolute_value(self.delta_from_goal013_support_floor_weighted_gap)
        return (
            self.target_transform_id,
            self.candidate_label,
            stringify_bool(self.is_default),
            self.component,
            stringify_optional_float(self.weighted_gap),
            stringify_optional_float(self.status_quo_weighted_gap),
            stringify_optional_float(self.delta_from_status_quo_weighted_gap),
            stringify_optional_float(self.goal013_support_floor_weighted_gap),
            stringify_optional_float(self.delta_from_goal013_support_floor_weighted_gap),
            stringify_optional_float(status_delta_abs),
            stringify_optional_float(support_delta_abs),
            str(self.residual_rank_within_transform_candidate),
            str(self.absolute_delta_from_status_quo_rank_within_transform_candidate),
            str(self.absolute_delta_from_goal013_support_floor_rank_within_transform_candidate),
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class TargetTimingResidualCheck:
    name: str
    passed: bool
    message: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True, slots=True)
class SynthSmallTargetTimingResidualDecompositionResult:
    config: TargetTimingResidualDecompositionConfig
    inputs: LoadedTargetTimingResidualInputs
    site_rows: tuple[SiteTargetTransformResolutionRow, ...]
    summary_vector_rows: tuple[TargetTransformSummaryVectorRow, ...]
    score_rows: tuple[CandidateScoreRow, ...]
    ranking_rows: tuple[ModeRankingRow, ...]
    delta_rows: tuple[ComponentDeltaRow, ...]
    recommendation: dict[str, Any]
    verification_checks: tuple[TargetTimingResidualCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def config_payload(self) -> dict[str, Any]:
        return {
            **self.config.to_dict(),
            "source_verifications": source_verifications(self.inputs),
            "summary_vector_contract_interpretation": (
                summary_vector_contract_interpretation(self.inputs)
            ),
            "bridge_reconciliation": bridge_reconciliation_payload(
                inputs=self.inputs,
                summary_vector_rows=self.summary_vector_rows,
                ranking_rows=self.ranking_rows,
                score_rows=self.score_rows,
            ),
        }

    def verification_payload(self) -> dict[str, Any]:
        return {
            **residual_labels(),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
        }

    def write_artifacts(
        self,
        output_dir: str | PathLike[str] = DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR,
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "residual_decomposition_config.json"
        definitions_path = target_dir / "target_transform_definitions.csv"
        site_path = target_dir / "site_target_transform_resolution.csv"
        summary_path = target_dir / "target_transform_summary_vectors.csv"
        losses_path = target_dir / "target_transform_component_losses.csv"
        rankings_path = target_dir / "target_transform_rankings.csv"
        deltas_path = target_dir / "component_delta_table.csv"
        recommendation_path = target_dir / "recommendation.json"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(dumps(self.config_payload(), indent=2) + "\n", encoding="utf-8")
        write_rows(
            TARGET_TRANSFORM_DEFINITION_COLUMNS,
            (transform.to_csv_row() for transform in self.config.target_transforms),
            definitions_path,
        )
        write_rows(
            SITE_TARGET_TRANSFORM_COLUMNS,
            (row.to_csv_row() for row in self.site_rows),
            site_path,
        )
        write_rows(
            TARGET_TRANSFORM_SUMMARY_VECTOR_COLUMNS,
            (row.to_csv_row() for row in self.summary_vector_rows),
            summary_path,
        )
        write_rows(
            TARGET_TRANSFORM_COMPONENT_LOSS_COLUMNS,
            (target_transform_score_csv_row(row) for row in self.score_rows),
            losses_path,
        )
        write_rows(
            TARGET_TRANSFORM_RANKING_COLUMNS,
            (target_transform_ranking_csv_row(row) for row in self.ranking_rows),
            rankings_path,
        )
        write_rows(
            COMPONENT_DELTA_COLUMNS,
            (row.to_csv_row() for row in self.delta_rows),
            deltas_path,
        )
        recommendation_path.write_text(
            dumps(self.recommendation, indent=2) + "\n",
            encoding="utf-8",
        )
        verification_path.write_text(
            dumps(self.verification_payload(), indent=2) + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_target_timing_residual_report(self), encoding="utf-8")
        return (
            config_path,
            definitions_path,
            site_path,
            summary_path,
            losses_path,
            rankings_path,
            deltas_path,
            recommendation_path,
            verification_path,
            report_path,
        )


def build_synth_small_target_timing_residual_decomposition(
    *,
    observation_dir: str | PathLike[str] = DEFAULT_OBSERVATION_DIR,
    reconstruction_dir: str | PathLike[str] = DEFAULT_RECONSTRUCTION_DIR,
    evaluation_dir: str | PathLike[str] = DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    false_negative_audit_dir: str | PathLike[str] = DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
    observation_support_counterfactual_dir: str | PathLike[str] = (
        DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR
    ),
    summary_vector_dir: str | PathLike[str] = DEFAULT_SUMMARY_VECTOR_DIR,
    compatibility_screen_dir: str | PathLike[str] = DEFAULT_COMPATIBILITY_SCREEN_DIR,
    config: TargetTimingResidualDecompositionConfig | None = None,
) -> SynthSmallTargetTimingResidualDecompositionResult:
    residual_config = config or TargetTimingResidualDecompositionConfig(
        observation_dir=str(observation_dir),
        reconstruction_dir=str(reconstruction_dir),
        evaluation_dir=str(evaluation_dir),
        false_negative_audit_dir=str(false_negative_audit_dir),
        observation_support_counterfactual_dir=str(observation_support_counterfactual_dir),
        summary_vector_dir=str(summary_vector_dir),
        compatibility_screen_dir=str(compatibility_screen_dir),
    )
    inputs = load_target_timing_residual_inputs(
        observation_dir=residual_config.observation_dir,
        reconstruction_dir=residual_config.reconstruction_dir,
        evaluation_dir=residual_config.evaluation_dir,
        false_negative_audit_dir=residual_config.false_negative_audit_dir,
        observation_support_counterfactual_dir=(
            residual_config.observation_support_counterfactual_dir
        ),
        summary_vector_dir=residual_config.summary_vector_dir,
        compatibility_screen_dir=residual_config.compatibility_screen_dir,
    )
    site_rows = build_site_target_transform_rows(inputs, residual_config)
    target_rows = build_target_rows_by_transform(site_rows)
    component_rows, coverage_rows, summary_rows = build_target_transform_summary_vectors(
        target_rows,
        residual_config,
    )
    score_rows, ranking_rows = build_target_transform_compatibility_rows(
        component_rows=component_rows,
        coverage_rows=coverage_rows,
        config=residual_config.compatibility_config,
    )
    delta_rows = build_component_delta_rows(score_rows)
    recommendation = build_target_timing_residual_recommendation(
        ranking_rows=ranking_rows,
        score_rows=score_rows,
        summary_vector_rows=summary_rows,
    )
    checks = verify_target_timing_residual_result(
        inputs=inputs,
        config=residual_config,
        site_rows=site_rows,
        summary_vector_rows=summary_rows,
        score_rows=score_rows,
        ranking_rows=ranking_rows,
        delta_rows=delta_rows,
        recommendation=recommendation,
    )
    return SynthSmallTargetTimingResidualDecompositionResult(
        config=residual_config,
        inputs=inputs,
        site_rows=site_rows,
        summary_vector_rows=summary_rows,
        score_rows=score_rows,
        ranking_rows=ranking_rows,
        delta_rows=delta_rows,
        recommendation=recommendation,
        verification_checks=checks,
    )


def load_target_timing_residual_inputs(
    *,
    observation_dir: str | PathLike[str],
    reconstruction_dir: str | PathLike[str],
    evaluation_dir: str | PathLike[str],
    false_negative_audit_dir: str | PathLike[str],
    observation_support_counterfactual_dir: str | PathLike[str],
    summary_vector_dir: str | PathLike[str],
    compatibility_screen_dir: str | PathLike[str],
) -> LoadedTargetTimingResidualInputs:
    obs_dir = Path(observation_dir)
    recon_dir = Path(reconstruction_dir)
    eval_dir = Path(evaluation_dir)
    false_negative_dir = Path(false_negative_audit_dir)
    counterfactual_dir = Path(observation_support_counterfactual_dir)
    summary_dir = Path(summary_vector_dir)
    compatibility_dir = Path(compatibility_screen_dir)
    assert_required_files(obs_dir, OBSERVATION_REQUIRED_FILES, "observations")
    assert_required_files(recon_dir, RECONSTRUCTION_REQUIRED_FILES, "reconstruction")
    assert_required_files(eval_dir, EVALUATION_REQUIRED_FILES, "response-screen evaluation")
    assert_required_files(
        false_negative_dir,
        FALSE_NEGATIVE_AUDIT_REQUIRED_FILES,
        "false-negative audit",
    )
    assert_required_files(
        counterfactual_dir,
        COUNTERFACTUAL_REQUIRED_FILES,
        "observation-support counterfactual",
    )
    assert_required_files(summary_dir, SUMMARY_VECTOR_REQUIRED_FILES, "summary-vector bridge")
    assert_required_files(
        compatibility_dir,
        COMPATIBILITY_REQUIRED_FILES,
        "compatibility-screen bridge",
    )
    return LoadedTargetTimingResidualInputs(
        observation_dir=obs_dir,
        reconstruction_dir=recon_dir,
        evaluation_dir=eval_dir,
        false_negative_audit_dir=false_negative_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        observation_config=read_json(obs_dir / "observation_config.json"),
        truth_rows=read_csv_rows(obs_dir / "evaluation_truth.csv"),
        truth_reference=read_json(obs_dir / "truth_reference.json"),
        reconstruction_config=read_json(recon_dir / "reconstruction_config.json"),
        reconstruction_rows=read_csv_rows(recon_dir / "site_reconstruction.csv"),
        reconstruction_verification=read_json(recon_dir / "verification.json"),
        evaluation_summary=read_json(eval_dir / "screen_evaluation_summary.json"),
        site_evaluation_rows=read_csv_rows(eval_dir / "site_evaluation_audit.csv"),
        evaluation_verification=read_json(eval_dir / "verification.json"),
        false_negative_config=read_json(false_negative_dir / "false_negative_audit_config.json"),
        false_negative_site_rows=read_csv_rows(
            false_negative_dir / "false_negative_site_audit.csv"
        ),
        false_negative_mechanism_rows=read_csv_rows(false_negative_dir / "mechanism_summary.csv"),
        false_negative_recommendation=read_json(false_negative_dir / "recommendation.json"),
        false_negative_verification=read_json(false_negative_dir / "verification.json"),
        counterfactual_config=read_json(counterfactual_dir / "counterfactual_config.json"),
        counterfactual_site_rows=read_csv_rows(
            counterfactual_dir / "site_counterfactual_resolution.csv"
        ),
        counterfactual_summary_rows=read_csv_rows(
            counterfactual_dir / "scenario_reconstruction_summary.csv"
        ),
        counterfactual_score_rows=read_csv_rows(
            counterfactual_dir / "scenario_compatibility_scores.csv"
        ),
        counterfactual_ranking_rows=read_csv_rows(counterfactual_dir / "scenario_rankings.csv"),
        counterfactual_verification=read_json(counterfactual_dir / "verification.json"),
        summary_vector_config=read_json(summary_dir / "summary_vector_config.json"),
        summary_vector_component_rows=read_csv_rows(summary_dir / "summary_components.csv"),
        summary_vector_coverage_rows=read_csv_rows(summary_dir / "coverage_curve.csv"),
        summary_vector_mode_summary=read_json(summary_dir / "mode_summary.json"),
        summary_vector_verification=read_json(summary_dir / "verification.json"),
        compatibility_target_summary=read_json(compatibility_dir / "target_summary.json"),
        compatibility_candidate_score_rows=read_csv_rows(
            compatibility_dir / "candidate_scores.csv"
        ),
        compatibility_mode_ranking_rows=read_csv_rows(compatibility_dir / "mode_rankings.csv"),
        compatibility_coverage_score_rows=read_csv_rows(
            compatibility_dir / "coverage_score_breakdown.csv"
        ),
        compatibility_verification=read_json(compatibility_dir / "verification.json"),
    )


def build_site_target_transform_rows(
    inputs: LoadedTargetTimingResidualInputs,
    config: TargetTimingResidualDecompositionConfig,
) -> tuple[SiteTargetTransformResolutionRow, ...]:
    reconstruction_by_site = {row["site_id"]: row for row in inputs.reconstruction_rows}
    false_negative_by_site = {row["site_id"]: row for row in inputs.false_negative_site_rows}
    support_floor_by_site = {
        row["site_id"]: row
        for row in inputs.counterfactual_site_rows
        if row["scenario_id"] == GOAL013_SUPPORT_SCENARIO_ID
    }
    definitions_by_id = {
        definition.target_transform_id: definition for definition in config.target_transforms
    }
    output: list[SiteTargetTransformResolutionRow] = []
    for definition in config.target_transforms:
        for truth_row in inputs.truth_rows:
            site_id = truth_row["site_id"]
            reconstruction = reconstruction_by_site[site_id]
            false_negative = false_negative_by_site.get(site_id)
            support_floor = support_floor_by_site.get(site_id)
            status_quo_time = parse_optional_float(reconstruction["observed_extirpation_time"])
            true_time = parse_optional_float(truth_row["true_extirpation"])
            goal013_time = (
                parse_optional_float(support_floor["counterfactual_observed_extirpation_time"])
                if support_floor is not None
                else None
            )
            transformed_time, resolution_class = transformed_target_time(
                transform_id=definition.target_transform_id,
                status_quo_time=status_quo_time,
                true_time=true_time,
                false_negative_row=false_negative,
                support_floor_row=support_floor,
            )
            delta = optional_difference(transformed_time, status_quo_time)
            post_detection_count = (
                parse_int(false_negative["post_extirpation_detection_count"])
                if false_negative is not None
                else 0
            )
            output.append(
                SiteTargetTransformResolutionRow(
                    target_transform_id=definition.target_transform_id,
                    site_id=site_id,
                    cell_id=parse_int(truth_row["cell_id"]),
                    row=parse_int(truth_row["row"]),
                    col=parse_int(truth_row["col"]),
                    region=reconstruction["region"],
                    front_band=reconstruction["front_band"],
                    false_negative=false_negative is not None,
                    primary_mechanism=(
                        false_negative["primary_mechanism"] if false_negative is not None else ""
                    ),
                    post_extirpation_detection_count=post_detection_count,
                    driver_arrival=parse_optional_float(truth_row["driver_arrival"]),
                    status_quo_target_time=status_quo_time,
                    transformed_target_time=transformed_time,
                    true_extirpation_time=true_time,
                    goal013_counterfactual_time=goal013_time,
                    target_time_delta_from_status_quo=delta,
                    resolution_class=resolution_class,
                    uses_hidden_truth=definitions_by_id[
                        definition.target_transform_id
                    ].uses_hidden_truth,
                )
            )
    return tuple(output)


def transformed_target_time(
    *,
    transform_id: str,
    status_quo_time: float | None,
    true_time: float | None,
    false_negative_row: dict[str, str] | None,
    support_floor_row: dict[str, str] | None,
) -> tuple[float | None, str]:
    if transform_id == "status_quo_observed":
        return (
            status_quo_time,
            "unchanged_finite" if status_quo_time is not None else "unchanged_nonfinite",
        )
    if transform_id == "goal013_support_floor":
        if support_floor_row is not None and support_floor_row["resolved_false_negative"] == "true":
            return (
                parse_optional_float(support_floor_row["counterfactual_observed_extirpation_time"]),
                "goal013_support_floor_time",
            )
        return (
            status_quo_time,
            "unchanged_non_false_negative"
            if false_negative_row is None
            else "goal013_support_floor_unresolved",
        )
    if transform_id == "false_negative_true_time":
        if false_negative_row is not None:
            return true_time, "false_negative_true_time_replacement"
        return (
            status_quo_time,
            "unchanged_finite" if status_quo_time is not None else "unchanged_nonfinite",
        )
    if transform_id == "false_negative_true_time_detection_respecting":
        if false_negative_row is not None:
            post_detection_count = parse_int(false_negative_row["post_extirpation_detection_count"])
            if post_detection_count > 0:
                return status_quo_time, "post_extirpation_detection_blocker_unresolved"
            return true_time, "detection_respecting_false_negative_true_time"
        return (
            status_quo_time,
            "unchanged_finite" if status_quo_time is not None else "unchanged_nonfinite",
        )
    if transform_id == "all_extirpated_true_time":
        if true_time is None:
            return None, "true_non_extirpated_nonfinite"
        if approx_equal(status_quo_time, true_time):
            return true_time, "already_true_time"
        return true_time, "all_extirpated_true_time_replacement"
    raise ValueError(f"unknown target transform {transform_id!r}")


def build_target_rows_by_transform(
    site_rows: tuple[SiteTargetTransformResolutionRow, ...],
) -> dict[str, tuple[SummaryVectorTargetRow, ...]]:
    output: dict[str, list[SummaryVectorTargetRow]] = defaultdict(list)
    for row in site_rows:
        output[row.target_transform_id].append(
            SummaryVectorTargetRow(
                site_id=row.site_id,
                cell_id=row.cell_id,
                grid_row=row.row,
                grid_col=row.col,
                driver_arrival=row.driver_arrival,
                target_time=row.transformed_target_time,
            )
        )
    return {transform_id: tuple(rows) for transform_id, rows in output.items()}


def build_target_transform_summary_vectors(
    target_rows_by_transform: dict[str, tuple[SummaryVectorTargetRow, ...]],
    config: TargetTimingResidualDecompositionConfig,
) -> tuple[
    dict[str, tuple[SummaryComponentRow, ...]],
    dict[str, tuple[CoverageCurveRow, ...]],
    tuple[TargetTransformSummaryVectorRow, ...],
]:
    component_rows_by_transform: dict[str, tuple[SummaryComponentRow, ...]] = {}
    coverage_rows_by_transform: dict[str, tuple[CoverageCurveRow, ...]] = {}
    summary_rows: list[TargetTransformSummaryVectorRow] = []
    for transform in config.target_transforms:
        transform_id = transform.target_transform_id
        component_rows = build_summary_component_rows(
            transform_id,
            target_rows_by_transform[transform_id],
        )
        coverage_rows = build_coverage_curve_rows(
            mode=transform_id,
            rows=target_rows_by_transform[transform_id],
            coverage_breakpoints=config.coverage_breakpoints,
        )
        component_rows_by_transform[transform_id] = component_rows
        coverage_rows_by_transform[transform_id] = coverage_rows
        summary_rows.extend(
            TargetTransformSummaryVectorRow(
                target_transform_id=transform_id,
                row_type="summary_component",
                metric=row.component,
                value=row.value,
                missing_reason=row.missing_reason,
            )
            for row in component_rows
        )
        summary_rows.extend(
            TargetTransformSummaryVectorRow(
                target_transform_id=transform_id,
                row_type="coverage_curve",
                metric="target_time",
                value=row.target_time,
                coverage_fraction=row.coverage_fraction,
                finite_target_count=row.finite_target_count,
                missing_reason=row.missing_reason,
            )
            for row in coverage_rows
        )
    return component_rows_by_transform, coverage_rows_by_transform, tuple(summary_rows)


def build_target_transform_compatibility_rows(
    *,
    component_rows: dict[str, tuple[SummaryComponentRow, ...]],
    coverage_rows: dict[str, tuple[CoverageCurveRow, ...]],
    config: CompatibilityScreenConfig,
) -> tuple[tuple[CandidateScoreRow, ...], tuple[ModeRankingRow, ...]]:
    transform_ids = tuple(component_rows)
    screen_config = CompatibilityScreenConfig(
        target_modes=transform_ids,
        primary_target_mode="status_quo_observed",
        candidates=config.candidates,
        coverage_breakpoints=config.coverage_breakpoints,
        required_components=config.required_components,
        gap_settings=config.gap_settings,
        compatible_loss_max=config.compatible_loss_max,
        borderline_loss_max=config.borderline_loss_max,
    )
    profiles = tuple(
        build_candidate_profile(
            candidate,
            coverage_breakpoints=screen_config.coverage_breakpoints,
        )
        for candidate in screen_config.candidates
    )
    settings_by_component = {setting.component: setting for setting in screen_config.gap_settings}
    mode_scores = []
    score_rows: list[CandidateScoreRow] = []
    for transform_id in transform_ids:
        target_components = {
            row.component: scalar_value(row.value, row.missing_reason)
            for row in component_rows[transform_id]
        }
        target_coverage = {
            row.coverage_fraction: scalar_value(row.target_time, row.missing_reason)
            for row in coverage_rows[transform_id]
        }
        for profile in profiles:
            mode_score, rows, _coverage_score_rows = score_candidate_against_target(
                target_mode=transform_id,
                target_components=target_components,
                target_coverage=target_coverage,
                profile=profile,
                config=screen_config,
                settings_by_component=settings_by_component,
            )
            mode_scores.append(mode_score)
            score_rows.extend(rows)
    return tuple(score_rows), build_mode_rankings(mode_scores, config=screen_config)


def build_component_delta_rows(
    score_rows: tuple[CandidateScoreRow, ...],
) -> tuple[ComponentDeltaRow, ...]:
    score_map = {(row.target_mode, row.candidate_label, row.component): row for row in score_rows}
    status_map = {
        (row.candidate_label, row.component): row
        for row in score_rows
        if row.target_mode == "status_quo_observed"
    }
    support_map = {
        (row.candidate_label, row.component): row
        for row in score_rows
        if row.target_mode == "goal013_support_floor"
    }
    grouped: dict[tuple[str, str], list[CandidateScoreRow]] = defaultdict(list)
    for row in score_rows:
        grouped[(row.target_mode, row.candidate_label)].append(row)

    residual_ranks: dict[tuple[str, str, str], int] = {}
    status_delta_ranks: dict[tuple[str, str, str], int] = {}
    support_delta_ranks: dict[tuple[str, str, str], int] = {}
    for (transform_id, candidate_label), rows in grouped.items():
        residual_sorted = sorted(
            rows,
            key=lambda row: (
                -(row.weighted_gap if row.weighted_gap is not None else -1.0),
                row.component,
            ),
        )
        for rank, row in enumerate(residual_sorted, start=1):
            residual_ranks[(transform_id, candidate_label, row.component)] = rank

        status_delta_sorted = sorted(
            rows,
            key=lambda row: (
                -delta_magnitude(
                    row.weighted_gap,
                    status_map.get((candidate_label, row.component)),
                ),
                row.component,
            ),
        )
        for rank, row in enumerate(status_delta_sorted, start=1):
            status_delta_ranks[(transform_id, candidate_label, row.component)] = rank

        support_delta_sorted = sorted(
            rows,
            key=lambda row: (
                -delta_magnitude(
                    row.weighted_gap,
                    support_map.get((candidate_label, row.component)),
                ),
                row.component,
            ),
        )
        for rank, row in enumerate(support_delta_sorted, start=1):
            support_delta_ranks[(transform_id, candidate_label, row.component)] = rank

    output: list[ComponentDeltaRow] = []
    for key, row in score_map.items():
        _transform_id, candidate_label, component = key
        status = status_map.get((candidate_label, component))
        support = support_map.get((candidate_label, component))
        status_gap = status.weighted_gap if status is not None else None
        support_gap = support.weighted_gap if support is not None else None
        output.append(
            ComponentDeltaRow(
                target_transform_id=row.target_mode,
                candidate_label=row.candidate_label,
                is_default=row.is_default,
                component=row.component,
                weighted_gap=row.weighted_gap,
                status_quo_weighted_gap=status_gap,
                delta_from_status_quo_weighted_gap=optional_difference(
                    row.weighted_gap,
                    status_gap,
                ),
                goal013_support_floor_weighted_gap=support_gap,
                delta_from_goal013_support_floor_weighted_gap=optional_difference(
                    row.weighted_gap,
                    support_gap,
                ),
                residual_rank_within_transform_candidate=residual_ranks[
                    (row.target_mode, row.candidate_label, row.component)
                ],
                absolute_delta_from_status_quo_rank_within_transform_candidate=status_delta_ranks[
                    (row.target_mode, row.candidate_label, row.component)
                ],
                absolute_delta_from_goal013_support_floor_rank_within_transform_candidate=support_delta_ranks[
                    (row.target_mode, row.candidate_label, row.component)
                ],
                missing_reason=row.missing_reason,
            )
        )
    return tuple(
        sorted(
            output,
            key=lambda row: (
                TARGET_TRANSFORM_IDS.index(row.target_transform_id),
                int(not row.is_default),
                row.candidate_label,
                row.residual_rank_within_transform_candidate,
                row.component,
            ),
        )
    )


def build_target_timing_residual_recommendation(
    *,
    ranking_rows: tuple[ModeRankingRow, ...],
    score_rows: tuple[CandidateScoreRow, ...],
    summary_vector_rows: tuple[TargetTransformSummaryVectorRow, ...],
) -> dict[str, Any]:
    default_rows = default_rankings_by_transform(ranking_rows)
    all_true = default_rows["all_extirpated_true_time"]
    support = default_rows["goal013_support_floor"]
    restored_by = [
        transform_id
        for transform_id in TARGET_TRANSFORM_IDS
        if default_rows[transform_id].compatibility_class == "compatible"
    ]
    support_components = dominant_default_components(
        score_rows,
        "goal013_support_floor",
    )
    if all_true.compatibility_class != "compatible" or not approx_equal(
        all_true.total_weighted_loss,
        0.0,
    ):
        recommendation_class = "compatibility_contract_review_needed"
    elif support.compatibility_class != "compatible":
        recommendation_class = "timing_bias_drives_residual"
    else:
        recommendation_class = "ready_for_inference_design_discussion"

    return {
        **residual_labels(),
        "recommendation_class": recommendation_class,
        "compatibility_restored_by": restored_by,
        "status_quo": transform_payload(
            "status_quo_observed",
            default_rows["status_quo_observed"],
            summary_vector_rows,
        ),
        "goal013_support_floor": transform_payload(
            "goal013_support_floor",
            support,
            summary_vector_rows,
        ),
        "all_extirpated_true_time": transform_payload(
            "all_extirpated_true_time",
            all_true,
            summary_vector_rows,
        ),
        "dominant_goal013_support_floor_default_components": support_components[:4],
        "interpretation": (
            "Finite-target restoration alone does not restore compatibility; "
            "the residual is carried by target-time distribution, lag, and "
            "target-shape components under the unchanged Goal 009/010 bridge."
        ),
    }


def verify_target_timing_residual_result(
    *,
    inputs: LoadedTargetTimingResidualInputs,
    config: TargetTimingResidualDecompositionConfig,
    site_rows: tuple[SiteTargetTransformResolutionRow, ...],
    summary_vector_rows: tuple[TargetTransformSummaryVectorRow, ...],
    score_rows: tuple[CandidateScoreRow, ...],
    ranking_rows: tuple[ModeRankingRow, ...],
    delta_rows: tuple[ComponentDeltaRow, ...],
    recommendation: dict[str, Any],
) -> tuple[TargetTimingResidualCheck, ...]:
    source_passed = source_verifications(inputs)
    transform_ids = tuple(transform.target_transform_id for transform in config.target_transforms)
    row_counts_by_transform = Counter(row.target_transform_id for row in site_rows)
    bridge = bridge_reconciliation_payload(
        inputs=inputs,
        summary_vector_rows=summary_vector_rows,
        ranking_rows=ranking_rows,
        score_rows=score_rows,
    )
    expected_score_rows = (
        len(transform_ids)
        * len(config.compatibility_config.candidates)
        * (len(config.compatibility_config.required_components) + 1)
    )
    return (
        TargetTimingResidualCheck(
            name="source_verifications",
            passed=all(source_passed.values()),
            message="all prerequisite verification payloads passed",
            details=source_passed,
        ),
        TargetTimingResidualCheck(
            name="summary_vector_contract_interpretation",
            passed=summary_vector_contract_interpretation(inputs)[
                "using_existing_goal009_contract"
            ],
            message="Goal 009 summary-vector bridge uses its published artifact contract",
            details=summary_vector_contract_interpretation(inputs),
        ),
        TargetTimingResidualCheck(
            name="target_transform_set",
            passed=transform_ids == TARGET_TRANSFORM_IDS,
            message="target-transform set is small, deterministic, and ordered",
            details={"target_transform_ids": list(transform_ids)},
        ),
        TargetTimingResidualCheck(
            name="site_resolution_rows",
            passed=all(
                row_counts_by_transform[transform_id] == len(inputs.truth_rows)
                for transform_id in transform_ids
            ),
            message="each transform has one site-resolution row per site",
            details={
                "site_count": len(inputs.truth_rows),
                "row_counts_by_transform": dict(row_counts_by_transform),
            },
        ),
        TargetTimingResidualCheck(
            name="status_quo_reconciliation",
            passed=bool(bridge["status_quo_matches_existing_goal010"]),
            message="status quo reconciles existing Goal 010 realistic_observed bridge",
            details=bridge,
        ),
        TargetTimingResidualCheck(
            name="goal013_support_floor_reconciliation",
            passed=bool(bridge["goal013_support_floor_matches_existing_goal013"]),
            message="Goal 013 support-floor transform reconciles emitted counterfactual bundle",
            details=bridge,
        ),
        TargetTimingResidualCheck(
            name="all_extirpated_true_time_reconciliation",
            passed=bool(bridge["all_extirpated_true_time_matches_goal010_ideal_true"]),
            message="all-extirpated true-time transform restores Goal 010 ideal_true bridge",
            details=bridge,
        ),
        TargetTimingResidualCheck(
            name="component_loss_accounting",
            passed=len(score_rows) == expected_score_rows
            and component_losses_match_rankings(score_rows, ranking_rows),
            message=(
                "component score rows have expected cardinality and weighted gaps "
                "sum to ranking losses"
            ),
            details={
                "score_row_count": len(score_rows),
                "expected_score_row_count": expected_score_rows,
            },
        ),
        TargetTimingResidualCheck(
            name="component_delta_rows",
            passed=len(delta_rows) == len(score_rows)
            and any(
                row.target_transform_id == "goal013_support_floor"
                and row.candidate_label == "default"
                for row in delta_rows
            ),
            message="component deltas are emitted for every scored component",
            details={"delta_row_count": len(delta_rows)},
        ),
        TargetTimingResidualCheck(
            name="recommendation",
            passed=recommendation["recommendation_class"] == "timing_bias_drives_residual",
            message="recommendation remains diagnostic before rule/design/inference changes",
            details={"recommendation_class": recommendation["recommendation_class"]},
        ),
    )


def bridge_reconciliation_payload(
    *,
    inputs: LoadedTargetTimingResidualInputs,
    summary_vector_rows: tuple[TargetTransformSummaryVectorRow, ...],
    ranking_rows: tuple[ModeRankingRow, ...],
    score_rows: tuple[CandidateScoreRow, ...],
) -> dict[str, Any]:
    component_counts = finite_counts_by_transform(summary_vector_rows)
    default_rows = default_rankings_by_transform(ranking_rows)
    summary_vector_modes = dict_payload(inputs.summary_vector_mode_summary.get("mode_summaries"))
    target_summary_modes = dict_payload(inputs.compatibility_target_summary.get("mode_summaries"))
    summary_vector_realistic = dict_payload(summary_vector_modes.get("realistic_observed"))
    summary_vector_ideal = dict_payload(summary_vector_modes.get("ideal_true"))
    target_summary_realistic = dict_payload(target_summary_modes.get("realistic_observed"))
    target_summary_ideal = dict_payload(target_summary_modes.get("ideal_true"))
    goal010_realistic = goal010_top_row(inputs, "realistic_observed")
    goal010_ideal = goal010_top_row(inputs, "ideal_true")
    goal013_support_summary = goal013_summary_row(inputs, GOAL013_SUPPORT_SCENARIO_ID)
    goal013_support_top = goal013_top_row(inputs, GOAL013_SUPPORT_SCENARIO_ID)
    status_quo = default_rows["status_quo_observed"]
    support = default_rows["goal013_support_floor"]
    all_true = default_rows["all_extirpated_true_time"]

    goal010_realistic_loss = parse_optional_float(goal010_realistic.get("total_weighted_loss", ""))
    goal010_ideal_loss = parse_optional_float(goal010_ideal.get("total_weighted_loss", ""))
    goal013_support_loss = parse_optional_float(goal013_support_top.get("total_weighted_loss", ""))
    status_quo_matches = (
        component_counts["status_quo_observed"] == 151
        and component_counts["status_quo_observed"]
        == int_payload(summary_vector_realistic.get("finite_target_count"), -1)
        == int_payload(target_summary_realistic.get("finite_target_count"), -1)
        and goal010_realistic.get("candidate_label") == status_quo.candidate.label
        and goal010_realistic.get("compatibility_class") == status_quo.compatibility_class
        and approx_equal(goal010_realistic_loss, status_quo.total_weighted_loss)
    )
    support_matches = (
        component_counts["goal013_support_floor"]
        == parse_int(goal013_support_summary.get("finite_target_count", "-1"))
        == 252
        and goal013_support_top.get("candidate_label") == support.candidate.label
        and goal013_support_top.get("compatibility_class") == support.compatibility_class
        and approx_equal(goal013_support_loss, support.total_weighted_loss)
    )
    all_true_matches = (
        component_counts["all_extirpated_true_time"]
        == int_payload(summary_vector_ideal.get("finite_target_count"), -1)
        == int_payload(target_summary_ideal.get("finite_target_count"), -1)
        == 252
        and goal010_ideal.get("candidate_label") == all_true.candidate.label
        and goal010_ideal.get("compatibility_class") == all_true.compatibility_class
        and approx_equal(goal010_ideal_loss, all_true.total_weighted_loss)
        and approx_equal(all_true.total_weighted_loss, 0.0)
    )
    return {
        "summary_vector_realistic_observed_finite_target_count": int_payload(
            summary_vector_realistic.get("finite_target_count"), -1
        ),
        "summary_vector_ideal_true_finite_target_count": int_payload(
            summary_vector_ideal.get("finite_target_count"), -1
        ),
        "compatibility_target_realistic_observed_finite_target_count": int_payload(
            target_summary_realistic.get("finite_target_count"), -1
        ),
        "compatibility_target_ideal_true_finite_target_count": int_payload(
            target_summary_ideal.get("finite_target_count"), -1
        ),
        "goal010_realistic_observed_top_candidate_label": goal010_realistic.get(
            "candidate_label", ""
        ),
        "goal010_realistic_observed_top_compatibility_class": goal010_realistic.get(
            "compatibility_class", ""
        ),
        "goal010_realistic_observed_top_total_weighted_loss": goal010_realistic_loss,
        "goal010_ideal_true_top_candidate_label": goal010_ideal.get("candidate_label", ""),
        "goal010_ideal_true_top_compatibility_class": goal010_ideal.get("compatibility_class", ""),
        "goal010_ideal_true_top_total_weighted_loss": goal010_ideal_loss,
        "goal013_support_floor_top_candidate_label": goal013_support_top.get("candidate_label", ""),
        "goal013_support_floor_top_compatibility_class": goal013_support_top.get(
            "compatibility_class", ""
        ),
        "goal013_support_floor_top_total_weighted_loss": goal013_support_loss,
        "status_quo_finite_target_count": component_counts["status_quo_observed"],
        "status_quo_top_candidate_label": status_quo.candidate.label,
        "status_quo_top_compatibility_class": status_quo.compatibility_class,
        "status_quo_top_total_weighted_loss": status_quo.total_weighted_loss,
        "goal013_support_floor_finite_target_count": component_counts["goal013_support_floor"],
        "goal013_support_floor_transform_top_candidate_label": support.candidate.label,
        "goal013_support_floor_transform_top_compatibility_class": (support.compatibility_class),
        "goal013_support_floor_transform_total_weighted_loss": support.total_weighted_loss,
        "all_extirpated_true_time_finite_target_count": component_counts[
            "all_extirpated_true_time"
        ],
        "all_extirpated_true_time_top_candidate_label": all_true.candidate.label,
        "all_extirpated_true_time_top_compatibility_class": all_true.compatibility_class,
        "all_extirpated_true_time_top_total_weighted_loss": all_true.total_weighted_loss,
        "status_quo_matches_existing_goal010": status_quo_matches,
        "goal013_support_floor_matches_existing_goal013": support_matches,
        "all_extirpated_true_time_matches_goal010_ideal_true": all_true_matches,
        "default_score_sums_match_rankings": component_losses_match_rankings(
            score_rows,
            ranking_rows,
        ),
    }


def source_verifications(inputs: LoadedTargetTimingResidualInputs) -> dict[str, bool]:
    return {
        "observations": bool(inputs.truth_reference),
        "extirpation_reconstruction": bool(inputs.reconstruction_verification.get("passed")),
        "response_screen_evaluation": bool(inputs.evaluation_verification.get("passed")),
        "false_negative_audit": bool(inputs.false_negative_verification.get("passed")),
        "observation_support_counterfactual": bool(
            inputs.counterfactual_verification.get("passed")
        ),
        "summary_vector": bool(inputs.summary_vector_verification.get("passed")),
        "compatibility_screen": bool(inputs.compatibility_verification.get("passed")),
    }


def summary_vector_contract_interpretation(
    inputs: LoadedTargetTimingResidualInputs,
) -> dict[str, Any]:
    actual_files_present = {
        name: (inputs.summary_vector_dir / name).exists() for name in SUMMARY_VECTOR_REQUIRED_FILES
    }
    target_summary_present = (inputs.summary_vector_dir / "target_summary.json").exists()
    return {
        "packet_listed_target_summary_json": True,
        "target_summary_json_present": target_summary_present,
        "using_existing_goal009_contract": all(actual_files_present.values())
        and not target_summary_present,
        "existing_goal009_contract_files_present": actual_files_present,
        "compatibility_screen_target_summary_json_present": (
            inputs.compatibility_screen_dir / "target_summary.json"
        ).exists(),
        "interpretation": (
            "Goal 009 does not emit summary_vector/target_summary.json; "
            "Goal 014 verifies the published Goal 009 summary-vector files "
            "and the Goal 010 compatibility target_summary.json instead."
        ),
    }


def render_target_timing_residual_report(
    result: SynthSmallTargetTimingResidualDecompositionResult,
) -> str:
    default_rows = default_rankings_by_transform(result.ranking_rows)
    support_components = result.recommendation["dominant_goal013_support_floor_default_components"]
    lines = [
        "# Synth-Small Target-Timing Residual Decomposition",
        "",
        "## Scope",
        "",
        (
            "This is a synthetic-only, evaluation-only target-transform diagnostic. "
            "It does not change default observation design, production reconstruction "
            "rules, scoring, candidates, or inference logic."
        ),
        "",
        "## Transform Outcomes",
        "",
        "| Transform | Default loss | Default class |",
        "| --- | ---: | --- |",
    ]
    for transform_id in TARGET_TRANSFORM_IDS:
        row = default_rows[transform_id]
        lines.append(
            f"| `{transform_id}` | `{stringify_optional_float(row.total_weighted_loss)}` | "
            f"`{row.compatibility_class}` |"
        )
    lines.extend(
        [
            "",
            "## Dominant Goal 013 Support-Floor Residuals",
            "",
        ]
    )
    for component in support_components:
        lines.append(
            f"- `{component['component']}`: weighted gap "
            f"`{stringify_optional_float(component['weighted_gap'])}`"
        )
    lines.extend(
        [
            "",
            "`component_delta_table.csv` includes residual contribution ranks and "
            "absolute-delta ranks from both `status_quo_observed` and "
            "`goal013_support_floor` within each transform/candidate group.",
            "",
            "## Recommendation",
            "",
            f"- Class: `{result.recommendation['recommendation_class']}`",
            "- Compatibility restored by: "
            f"`{', '.join(result.recommendation['compatibility_restored_by']) or 'none'}`",
            "",
            "## Interpretation Limit",
            "",
            (
                "Truth-guided target transformations are diagnostic references only. "
                "Any reconstruction-rule, observation-design, candidate, ABC, POM, "
                "or real-data work requires a later bounded goal."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def residual_labels() -> dict[str, bool]:
    return {key: True for key in NON_INFERENCE_LABEL_KEYS}


def finite_counts_by_transform(
    rows: tuple[TargetTransformSummaryVectorRow, ...],
) -> dict[str, int]:
    return {
        row.target_transform_id: int(float(row.value))
        for row in rows
        if row.row_type == "summary_component" and row.metric == "finite_target_count"
    }


def default_rankings_by_transform(
    rows: tuple[ModeRankingRow, ...],
) -> dict[str, ModeRankingRow]:
    return {row.target_mode: row for row in rows if row.candidate.label == "default"}


def transform_payload(
    transform_id: str,
    ranking: ModeRankingRow,
    summary_vector_rows: tuple[TargetTransformSummaryVectorRow, ...],
) -> dict[str, Any]:
    finite_counts = finite_counts_by_transform(summary_vector_rows)
    return {
        "target_transform_id": transform_id,
        "finite_target_count": finite_counts[transform_id],
        "top_candidate_label": ranking.candidate.label,
        "top_total_weighted_loss": ranking.total_weighted_loss,
        "top_compatibility_class": ranking.compatibility_class,
    }


def dominant_default_components(
    score_rows: tuple[CandidateScoreRow, ...],
    transform_id: str,
) -> list[dict[str, Any]]:
    rows = [
        row
        for row in score_rows
        if row.target_mode == transform_id and row.candidate_label == "default"
    ]
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            -(row.weighted_gap if row.weighted_gap is not None else -1.0),
            row.component,
        ),
    )
    return [
        {
            "component": row.component,
            "weighted_gap": row.weighted_gap,
            "absolute_gap": row.absolute_gap,
        }
        for row in sorted_rows
    ]


def component_losses_match_rankings(
    score_rows: tuple[CandidateScoreRow, ...],
    ranking_rows: tuple[ModeRankingRow, ...],
) -> bool:
    score_sums: dict[tuple[str, str], float] = defaultdict(float)
    for score_row in score_rows:
        if score_row.weighted_gap is not None:
            score_sums[(score_row.target_mode, score_row.candidate_label)] += score_row.weighted_gap
    for ranking_row in ranking_rows:
        if ranking_row.total_weighted_loss is None:
            continue
        if not approx_equal(
            score_sums[(ranking_row.target_mode, ranking_row.candidate.label)],
            ranking_row.total_weighted_loss,
        ):
            return False
    return True


def goal010_top_row(
    inputs: LoadedTargetTimingResidualInputs,
    target_mode: str,
) -> dict[str, str]:
    rows = [
        row
        for row in inputs.compatibility_mode_ranking_rows
        if row["target_mode"] == target_mode and row["rank"] == "1"
    ]
    return rows[0] if rows else {}


def goal013_summary_row(
    inputs: LoadedTargetTimingResidualInputs,
    scenario_id: str,
) -> dict[str, str]:
    rows = [row for row in inputs.counterfactual_summary_rows if row["scenario_id"] == scenario_id]
    return rows[0] if rows else {}


def goal013_top_row(
    inputs: LoadedTargetTimingResidualInputs,
    scenario_id: str,
) -> dict[str, str]:
    rows = [
        row
        for row in inputs.counterfactual_ranking_rows
        if row["scenario_id"] == scenario_id and row["rank"] == "1"
    ]
    return rows[0] if rows else {}


def target_transform_score_csv_row(row: CandidateScoreRow) -> tuple[str, ...]:
    return row.to_csv_row()


def target_transform_ranking_csv_row(row: ModeRankingRow) -> tuple[str, ...]:
    return row.to_csv_row()


def assert_required_files(path: Path, names: tuple[str, ...], label: str) -> None:
    missing = [name for name in names if not (path / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(f"missing required {label} artifacts: {missing_text}")


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    payload: Any = loads(path.read_text(encoding="utf-8"))
    return dict_payload(payload)


def write_rows(columns: tuple[str, ...], rows: Iterable[tuple[str, ...]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(columns)
        csv_writer.writerows(rows)


def parse_int(value: str) -> int:
    return int(value)


def parse_optional_float(value: str) -> float | None:
    if value == "":
        return None
    parsed = float(value)
    if not isfinite(parsed):
        return None
    return parsed


def stringify_optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return stringify_float(value)


def stringify_bool(value: bool) -> str:
    return "true" if value else "false"


def optional_difference(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def delta_magnitude(
    weighted_gap: float | None,
    baseline_row: CandidateScoreRow | None,
) -> float:
    baseline_gap = baseline_row.weighted_gap if baseline_row is not None else None
    difference = optional_difference(weighted_gap, baseline_gap)
    if difference is None:
        return -1.0
    return abs(difference)


def absolute_value(value: float | None) -> float | None:
    if value is None:
        return None
    return abs(value)


def approx_equal(left: float | None, right: float | None, *, tolerance: float = 1e-9) -> bool:
    if left is None or right is None:
        return False
    return abs(left - right) <= tolerance


def dict_payload(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def int_payload(value: Any, fallback: int) -> int:
    if isinstance(value, bool):
        return fallback
    if isinstance(value, int):
        return value
    if isinstance(value, float) and isfinite(value):
        return int(value)
    return fallback


__all__ = [
    "DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR",
    "TARGET_TIMING_RESIDUAL_OUTPUT_FILES",
    "SiteTargetTransformResolutionRow",
    "SynthSmallTargetTimingResidualDecompositionResult",
    "TargetTimingResidualCheck",
    "TargetTimingResidualDecompositionConfig",
    "TargetTransformDefinition",
    "TargetTransformSummaryVectorRow",
    "build_synth_small_target_timing_residual_decomposition",
    "default_target_transform_definitions",
    "render_target_timing_residual_report",
]
