"""Response-observable timing-rule screen for synth-small diagnostics."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from csv import DictReader, writer
from dataclasses import dataclass, field
from json import dumps, loads
from math import isfinite
from os import PathLike
from pathlib import Path
from statistics import median
from typing import Any, cast

from .compatibility_screen import (
    CANDIDATE_SCORE_COLUMNS,
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
from .target_time_error_anatomy_audit import (
    DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR,
)
from .target_timing_residual_decomposition import (
    DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR,
)

DEFAULT_RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_OUTPUT_DIR = (
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR / "response_observable_timing_rule_screen"
)
RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_NAME = "synth-small-response-observable-timing-rule-screen"
STATUS_QUO_RULE_ID = "status_quo_observed"
CONSERVATIVE_FINITE_SUPPORT_RULE_ID = "nonfinite_supported_final_survey_gap_expansion"
BROAD_FINITE_SUPPORT_STRESS_RULE_ID = "nonfinite_last_survey_expansion"
GOAL013_SUPPORT_RULE_ID = "goal013_support_floor"
ALL_TRUE_RULE_ID = "all_extirpated_true_time"
TIMING_RULE_SCREEN_RULE_IDS = (
    STATUS_QUO_RULE_ID,
    "long_detection_gap_shift_minus4",
    "west_band_shift_minus4",
    "long_gap_or_west_band_shift_minus4",
    CONSERVATIVE_FINITE_SUPPORT_RULE_ID,
    BROAD_FINITE_SUPPORT_STRESS_RULE_ID,
    GOAL013_SUPPORT_RULE_ID,
    ALL_TRUE_RULE_ID,
)
RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_OUTPUT_FILES = (
    "timing_rule_screen_config.json",
    "rule_definitions.csv",
    "site_rule_resolution.csv",
    "rule_summary_vectors.csv",
    "rule_component_losses.csv",
    "rule_rankings.csv",
    "proxy_rule_performance.csv",
    "grid_simplicity_risk_audit.csv",
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
COUNTERFACTUAL_REQUIRED_FILES = (
    "site_counterfactual_resolution.csv",
    "scenario_rankings.csv",
    "verification.json",
)
TARGET_TIMING_RESIDUAL_REQUIRED_FILES = (
    "site_target_transform_resolution.csv",
    "target_transform_rankings.csv",
    "component_delta_table.csv",
    "verification.json",
)
TARGET_TIME_ERROR_ANATOMY_REQUIRED_FILES = (
    "site_target_time_error_audit.csv",
    "observable_proxy_summary.csv",
    "recommendation.json",
    "verification.json",
)
NON_INFERENCE_LABEL_KEYS = (
    "synthetic_only",
    "evaluation_only",
    "response_observable_rule_screen_only",
    "not_formal_inference",
    "no_default_observation_change",
    "no_reconstruction_rule_change",
    "no_scoring_change",
    "no_candidate_change",
    "no_richer_landscape_change",
    "no_pom_or_likelihood_change",
)
RULE_DEFINITION_COLUMNS = (
    "target_rule_id",
    "label",
    "rule_family",
    "eligibility_class",
    "response_observable_source_columns",
    "may_assign_finite_to_status_quo_nonfinite",
    "spatially_keyed",
    "uses_hidden_truth",
    "target_site_rule",
    "target_time_rule",
    "interpretation",
)
SITE_RULE_RESOLUTION_COLUMNS = (
    "target_rule_id",
    "site_id",
    "cell_id",
    "row",
    "col",
    "region",
    "front_band",
    "true_extirpated_by_end",
    "status_quo_target_time",
    "goal013_support_floor_target_time",
    "all_extirpated_true_time_target_time",
    "rule_target_time",
    "rule_finite",
    "true_extirpation_time",
    "rule_signed_error",
    "rule_absolute_error",
    "target_time_delta_from_status_quo",
    "target_time_delta_from_goal013_support_floor",
    "response_observable_proxy_flags",
    "truth_only_signal_flags",
    "mixed_signal_flags",
    "status_quo_nonfinite_to_finite",
    "rule_changes_target",
    "resolution_class",
)
RULE_SUMMARY_VECTOR_COLUMNS = (
    "target_rule_id",
    "row_type",
    "metric",
    "value",
    "coverage_fraction",
    "finite_target_count",
    "missing_reason",
)
RULE_COMPONENT_LOSS_COLUMNS = (
    "target_rule_id",
    *CANDIDATE_SCORE_COLUMNS[1:],
    "component_rank_within_rule_candidate",
)
RULE_RANKING_COLUMNS = (
    "target_rule_id",
    "rank",
    "candidate_label",
    "is_default",
    "predation_scale",
    "half_saturation",
    "ramp_duration",
    "total_weighted_loss",
    "compatibility_class",
    "invalid_reasons",
    "is_eligible_response_observable_rule",
    "eligibility_class",
    "finite_target_count",
    "true_extirpated_comparable_count",
    "mean_absolute_error",
    "median_absolute_error",
    "large_abs_error_count",
    "status_quo_nonfinite_to_finite_count",
    "status_quo_nonfinite_to_finite_true_extirpated_count",
    "status_quo_nonfinite_to_finite_not_true_extirpated_count",
    "loss_delta_from_status_quo",
    "loss_delta_from_goal013_support_floor",
    "loss_gap_fraction_closed_to_goal013_support_floor",
    "mean_absolute_error_delta_from_status_quo",
    "improves_loss_vs_status_quo",
    "finite_support_role",
    "grid_overfit_risk_class",
)
PROXY_RULE_PERFORMANCE_COLUMNS = (
    "signal_id",
    "target_rule_id",
    "eligibility_class",
    "affected_site_count",
    "true_extirpated_affected_site_count",
    "status_quo_nonfinite_true_extirpated_count",
    "rule_nonfinite_true_extirpated_count",
    "status_quo_large_abs_error_count",
    "rule_large_abs_error_count",
    "large_abs_error_delta_from_status_quo",
    "status_quo_mean_absolute_error",
    "rule_mean_absolute_error",
    "mean_absolute_error_delta_from_status_quo",
    "improved_site_count",
    "worsened_site_count",
    "unchanged_site_count",
    "rule_screen_role",
)
GRID_SIMPLICITY_RISK_COLUMNS = (
    "target_rule_id",
    "eligibility_class",
    "spatially_keyed",
    "finite_target_count",
    "default_total_weighted_loss",
    "loss_delta_from_status_quo",
    "mean_absolute_error_delta_from_status_quo",
    "west_band_mean_absolute_error_delta_from_status_quo",
    "non_west_band_mean_absolute_error_delta_from_status_quo",
    "large_abs_error_delta_from_status_quo",
    "overfit_risk_class",
    "interpretation",
)


@dataclass(frozen=True, slots=True)
class TimingRuleDefinition:
    target_rule_id: str
    label: str
    rule_family: str
    eligibility_class: str
    response_observable_source_columns: str
    may_assign_finite_to_status_quo_nonfinite: bool
    spatially_keyed: bool
    uses_hidden_truth: bool
    target_site_rule: str
    target_time_rule: str
    interpretation: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_rule_id,
            self.label,
            self.rule_family,
            self.eligibility_class,
            self.response_observable_source_columns,
            stringify_bool(self.may_assign_finite_to_status_quo_nonfinite),
            stringify_bool(self.spatially_keyed),
            stringify_bool(self.uses_hidden_truth),
            self.target_site_rule,
            self.target_time_rule,
            self.interpretation,
        )


def default_timing_rule_definitions() -> tuple[TimingRuleDefinition, ...]:
    return (
        TimingRuleDefinition(
            target_rule_id=STATUS_QUO_RULE_ID,
            label="Status quo observed target",
            rule_family="baseline",
            eligibility_class="status_quo_baseline",
            response_observable_source_columns=(
                "site_reconstruction.csv:observed_extirpation_time"
            ),
            may_assign_finite_to_status_quo_nonfinite=False,
            spatially_keyed=False,
            uses_hidden_truth=False,
            target_site_rule="all sites",
            target_time_rule="current observed_extirpation_time",
            interpretation="baseline reconstructed target; no rule change",
        ),
        TimingRuleDefinition(
            target_rule_id="long_detection_gap_shift_minus4",
            label="Long detection-to-target gap minus four",
            rule_family="lag_gap_shift",
            eligibility_class="response_observable",
            response_observable_source_columns=(
                "site_reconstruction.csv:last_detection_time,observed_extirpation_time"
            ),
            may_assign_finite_to_status_quo_nonfinite=False,
            spatially_keyed=False,
            uses_hidden_truth=False,
            target_site_rule="finite status-quo targets with long detection-to-target gaps",
            target_time_rule="observed_extirpation_time - 4 when gap >= 8",
            interpretation="tests the strongest non-spatial response-observable residual proxy",
        ),
        TimingRuleDefinition(
            target_rule_id="west_band_shift_minus4",
            label="West-band target minus four",
            rule_family="front_band_shift",
            eligibility_class="response_observable",
            response_observable_source_columns="sites.csv:front_band",
            may_assign_finite_to_status_quo_nonfinite=False,
            spatially_keyed=True,
            uses_hidden_truth=False,
            target_site_rule="finite status-quo targets in west_band",
            target_time_rule="observed_extirpation_time - 4 for west_band sites",
            interpretation=(
                "tests the data-derived spatial/front-band residual proxy; diagnostic only"
            ),
        ),
        TimingRuleDefinition(
            target_rule_id="long_gap_or_west_band_shift_minus4",
            label="Long-gap or west-band target minus four",
            rule_family="proxy_combination_shift",
            eligibility_class="response_observable",
            response_observable_source_columns=(
                "site_reconstruction.csv:last_detection_time,observed_extirpation_time; "
                "sites.csv:front_band"
            ),
            may_assign_finite_to_status_quo_nonfinite=False,
            spatially_keyed=True,
            uses_hidden_truth=False,
            target_site_rule="finite status-quo targets with long gaps or west_band membership",
            target_time_rule="observed_extirpation_time - 4 when either proxy is active",
            interpretation="tests a transparent combination of Goal 015 residual proxies",
        ),
        TimingRuleDefinition(
            target_rule_id=CONSERVATIVE_FINITE_SUPPORT_RULE_ID,
            label="Supported final-survey nonfinite expansion",
            rule_family="finite_target_expansion",
            eligibility_class="response_observable",
            response_observable_source_columns=(
                "site_reconstruction.csv:final_absence_survey_time_count,"
                "survey_time_count,detection_count,last_detection_time,last_survey_time"
            ),
            may_assign_finite_to_status_quo_nonfinite=True,
            spatially_keyed=False,
            uses_hidden_truth=False,
            target_site_rule=(
                "status-quo nonfinite sites with below-threshold final absence, "
                "at least eight survey times, at least one detection, and no "
                "detection for at least eight time steps before the last survey"
            ),
            target_time_rule=(
                "last_survey_time for supported nonfinite sites; status quo otherwise"
            ),
            interpretation=(
                "conservative response-observable finite-support candidate distinct "
                "from the all-nonfinite last-survey stress test"
            ),
        ),
        TimingRuleDefinition(
            target_rule_id=BROAD_FINITE_SUPPORT_STRESS_RULE_ID,
            label="Nonfinite sites at last survey",
            rule_family="finite_target_expansion",
            eligibility_class="response_observable",
            response_observable_source_columns="site_reconstruction.csv:last_survey_time",
            may_assign_finite_to_status_quo_nonfinite=True,
            spatially_keyed=False,
            uses_hidden_truth=False,
            target_site_rule="status-quo nonfinite sites with any survey history",
            target_time_rule="last_survey_time for nonfinite sites; status quo otherwise",
            interpretation=(
                "stress-tests response-only finite-target expansion without hidden truth"
            ),
        ),
        TimingRuleDefinition(
            target_rule_id=GOAL013_SUPPORT_RULE_ID,
            label="Goal 013 support-floor reference",
            rule_family="truth_guided_reference",
            eligibility_class="truth_guided_reference",
            response_observable_source_columns="",
            may_assign_finite_to_status_quo_nonfinite=True,
            spatially_keyed=False,
            uses_hidden_truth=True,
            target_site_rule="Goal 013 truth-guided absence support floor",
            target_time_rule="target_time_error_anatomy:support_floor_target_time",
            interpretation="truth-guided finite-target recovery reference",
        ),
        TimingRuleDefinition(
            target_rule_id=ALL_TRUE_RULE_ID,
            label="All extirpated true-time reference",
            rule_family="truth_only_reference",
            eligibility_class="truth_only_reference",
            response_observable_source_columns="",
            may_assign_finite_to_status_quo_nonfinite=True,
            spatially_keyed=False,
            uses_hidden_truth=True,
            target_site_rule="all truly extirpated sites",
            target_time_rule="evaluation_truth.csv:true_extirpation",
            interpretation="synthetic ideal-truth reference that reconciles Goal 010",
        ),
    )


@dataclass(frozen=True, slots=True)
class ResponseObservableTimingRuleScreenConfig:
    observation_dir: str = str(DEFAULT_OBSERVATION_DIR)
    reconstruction_dir: str = str(DEFAULT_RECONSTRUCTION_DIR)
    evaluation_dir: str = str(DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR)
    summary_vector_dir: str = str(DEFAULT_SUMMARY_VECTOR_DIR)
    compatibility_screen_dir: str = str(DEFAULT_COMPATIBILITY_SCREEN_DIR)
    observation_support_counterfactual_dir: str = str(
        DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR
    )
    target_timing_residual_dir: str = str(DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR)
    target_time_error_anatomy_dir: str = str(DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR)
    target_rule_definitions: tuple[TimingRuleDefinition, ...] = field(
        default_factory=default_timing_rule_definitions
    )
    coverage_breakpoints: tuple[float, ...] = DEFAULT_COVERAGE_BREAKPOINTS
    compatibility_config: CompatibilityScreenConfig = field(
        default_factory=lambda: CompatibilityScreenConfig(
            target_modes=TIMING_RULE_SCREEN_RULE_IDS,
            primary_target_mode=STATUS_QUO_RULE_ID,
        )
    )
    long_detection_to_target_gap_min: float = 8.0
    target_shift: float = 4.0
    large_error_min: float = 8.0
    supported_final_survey_gap_min: float = 8.0
    supported_final_survey_time_count_min: int = 8
    supported_final_detection_count_min: int = 1
    production_final_absence_run_min: int = 2
    material_loss_gap_fraction_min: float = 0.5
    sparse_visit_count_max: int = 12
    sparse_survey_time_count_max: int = 6
    sparse_detection_count_max: int = 2

    def to_dict(self) -> dict[str, Any]:
        return {
            **timing_rule_screen_labels(),
            "diagnostic_name": RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_NAME,
            "observation_dir": self.observation_dir,
            "reconstruction_dir": self.reconstruction_dir,
            "evaluation_dir": self.evaluation_dir,
            "summary_vector_dir": self.summary_vector_dir,
            "compatibility_screen_dir": self.compatibility_screen_dir,
            "observation_support_counterfactual_dir": (self.observation_support_counterfactual_dir),
            "target_timing_residual_dir": self.target_timing_residual_dir,
            "target_time_error_anatomy_dir": self.target_time_error_anatomy_dir,
            "target_rule_ids": [
                definition.target_rule_id for definition in self.target_rule_definitions
            ],
            "thresholds": {
                "long_detection_to_target_gap_min": self.long_detection_to_target_gap_min,
                "target_shift": self.target_shift,
                "large_error_min": self.large_error_min,
                "supported_final_survey_gap_min": self.supported_final_survey_gap_min,
                "supported_final_survey_time_count_min": (
                    self.supported_final_survey_time_count_min
                ),
                "supported_final_detection_count_min": (self.supported_final_detection_count_min),
                "production_final_absence_run_min": self.production_final_absence_run_min,
                "material_loss_gap_fraction_min": self.material_loss_gap_fraction_min,
                "sparse_visit_count_max": self.sparse_visit_count_max,
                "sparse_survey_time_count_max": self.sparse_survey_time_count_max,
                "sparse_detection_count_max": self.sparse_detection_count_max,
            },
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
            "required_inputs": {
                "observations": list(OBSERVATION_REQUIRED_FILES),
                "reconstruction": list(RECONSTRUCTION_REQUIRED_FILES),
                "response_screen_evaluation": list(EVALUATION_REQUIRED_FILES),
                "summary_vector": list(SUMMARY_VECTOR_REQUIRED_FILES),
                "compatibility_screen": list(COMPATIBILITY_REQUIRED_FILES),
                "observation_support_counterfactual": list(COUNTERFACTUAL_REQUIRED_FILES),
                "target_timing_residual_decomposition": list(TARGET_TIMING_RESIDUAL_REQUIRED_FILES),
                "target_time_error_anatomy": list(TARGET_TIME_ERROR_ANATOMY_REQUIRED_FILES),
            },
            "output_files": list(RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_OUTPUT_FILES),
        }


@dataclass(frozen=True, slots=True)
class LoadedResponseObservableTimingRuleInputs:
    observation_dir: Path
    reconstruction_dir: Path
    evaluation_dir: Path
    summary_vector_dir: Path
    compatibility_screen_dir: Path
    observation_support_counterfactual_dir: Path
    target_timing_residual_dir: Path
    target_time_error_anatomy_dir: Path
    observation_config: dict[str, Any]
    truth_rows: tuple[dict[str, str], ...]
    reconstruction_config: dict[str, Any]
    reconstruction_rows: tuple[dict[str, str], ...]
    reconstruction_verification: dict[str, Any]
    evaluation_summary: dict[str, Any]
    site_evaluation_rows: tuple[dict[str, str], ...]
    evaluation_verification: dict[str, Any]
    summary_vector_mode_summary: dict[str, Any]
    summary_vector_verification: dict[str, Any]
    compatibility_target_summary: dict[str, Any]
    compatibility_candidate_score_rows: tuple[dict[str, str], ...]
    compatibility_mode_ranking_rows: tuple[dict[str, str], ...]
    compatibility_verification: dict[str, Any]
    counterfactual_site_rows: tuple[dict[str, str], ...]
    counterfactual_ranking_rows: tuple[dict[str, str], ...]
    counterfactual_verification: dict[str, Any]
    residual_site_rows: tuple[dict[str, str], ...]
    residual_ranking_rows: tuple[dict[str, str], ...]
    residual_delta_rows: tuple[dict[str, str], ...]
    residual_verification: dict[str, Any]
    anatomy_site_rows: tuple[dict[str, str], ...]
    observable_proxy_rows: tuple[dict[str, str], ...]
    anatomy_recommendation: dict[str, Any]
    anatomy_verification: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SiteRuleResolutionRow:
    target_rule_id: str
    site_id: str
    cell_id: int
    row: int
    col: int
    region: str
    front_band: str
    true_extirpated_by_end: bool
    status_quo_target_time: float | None
    goal013_support_floor_target_time: float | None
    all_extirpated_true_time_target_time: float | None
    rule_target_time: float | None
    true_extirpation_time: float | None
    response_observable_proxy_flags: tuple[str, ...]
    truth_only_signal_flags: tuple[str, ...]
    mixed_signal_flags: tuple[str, ...]

    @property
    def rule_signed_error(self) -> float | None:
        return optional_difference(self.rule_target_time, self.true_extirpation_time)

    @property
    def rule_absolute_error(self) -> float | None:
        return optional_abs(self.rule_signed_error)

    @property
    def target_time_delta_from_status_quo(self) -> float | None:
        return optional_difference(self.rule_target_time, self.status_quo_target_time)

    @property
    def target_time_delta_from_goal013_support_floor(self) -> float | None:
        return optional_difference(
            self.rule_target_time,
            self.goal013_support_floor_target_time,
        )

    @property
    def status_quo_nonfinite_to_finite(self) -> bool:
        return self.status_quo_target_time is None and self.rule_target_time is not None

    @property
    def rule_changes_target(self) -> bool:
        return self.rule_target_time != self.status_quo_target_time

    @property
    def resolution_class(self) -> str:
        if self.rule_target_time is None:
            return "nonfinite"
        if self.status_quo_nonfinite_to_finite:
            return "status_quo_nonfinite_to_finite"
        if self.status_quo_target_time is None:
            return "finite_without_status_quo_comparison"
        if self.rule_target_time < self.status_quo_target_time:
            return "shifted_earlier"
        if self.rule_target_time > self.status_quo_target_time:
            return "shifted_later"
        return "unchanged"

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_rule_id,
            self.site_id,
            str(self.cell_id),
            str(self.row),
            str(self.col),
            self.region,
            self.front_band,
            stringify_bool(self.true_extirpated_by_end),
            stringify_optional_float(self.status_quo_target_time),
            stringify_optional_float(self.goal013_support_floor_target_time),
            stringify_optional_float(self.all_extirpated_true_time_target_time),
            stringify_optional_float(self.rule_target_time),
            stringify_bool(self.rule_target_time is not None),
            stringify_optional_float(self.true_extirpation_time),
            stringify_optional_float(self.rule_signed_error),
            stringify_optional_float(self.rule_absolute_error),
            stringify_optional_float(self.target_time_delta_from_status_quo),
            stringify_optional_float(self.target_time_delta_from_goal013_support_floor),
            ";".join(self.response_observable_proxy_flags),
            ";".join(self.truth_only_signal_flags),
            ";".join(self.mixed_signal_flags),
            stringify_bool(self.status_quo_nonfinite_to_finite),
            stringify_bool(self.rule_changes_target),
            self.resolution_class,
        )


@dataclass(frozen=True, slots=True)
class RuleSummaryVectorRow:
    target_rule_id: str
    row_type: str
    metric: str
    value: str
    coverage_fraction: float | None = None
    finite_target_count: int | None = None
    missing_reason: str = ""

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_rule_id,
            self.row_type,
            self.metric,
            self.value,
            stringify_optional_float(self.coverage_fraction),
            "" if self.finite_target_count is None else str(self.finite_target_count),
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class RuleComponentLossRow:
    target_rule_id: str
    candidate_label: str
    is_default: bool
    component: str
    target_value: float | None
    candidate_value: float | None
    scale: float
    weight: float
    absolute_gap: float | None
    normalized_abs_gap: float | None
    weighted_gap: float | None
    missing_reason: str
    component_rank_within_rule_candidate: int

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_rule_id,
            self.candidate_label,
            stringify_bool(self.is_default),
            self.component,
            stringify_optional_float(self.target_value),
            stringify_optional_float(self.candidate_value),
            stringify_float(self.scale),
            stringify_float(self.weight),
            stringify_optional_float(self.absolute_gap),
            stringify_optional_float(self.normalized_abs_gap),
            stringify_optional_float(self.weighted_gap),
            self.missing_reason,
            str(self.component_rank_within_rule_candidate),
        )


@dataclass(frozen=True, slots=True)
class RuleMetrics:
    finite_target_count: int
    true_extirpated_comparable_count: int
    mean_absolute_error: float | None
    median_absolute_error: float | None
    large_abs_error_count: int
    nonfinite_true_extirpated_count: int
    status_quo_nonfinite_to_finite_count: int
    status_quo_nonfinite_to_finite_true_extirpated_count: int
    status_quo_nonfinite_to_finite_not_true_extirpated_count: int


@dataclass(frozen=True, slots=True)
class RuleRankingRow:
    target_rule_id: str
    rank: int
    candidate_label: str
    is_default: bool
    predation_scale: float
    half_saturation: float
    ramp_duration: int
    total_weighted_loss: float | None
    compatibility_class: str
    invalid_reasons: tuple[str, ...]
    is_eligible_response_observable_rule: bool
    eligibility_class: str
    metrics: RuleMetrics
    loss_delta_from_status_quo: float | None
    loss_delta_from_goal013_support_floor: float | None
    loss_gap_fraction_closed_to_goal013_support_floor: float | None
    mean_absolute_error_delta_from_status_quo: float | None
    improves_loss_vs_status_quo: bool
    finite_support_role: str
    grid_overfit_risk_class: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_rule_id,
            str(self.rank),
            self.candidate_label,
            stringify_bool(self.is_default),
            stringify_float(self.predation_scale),
            stringify_float(self.half_saturation),
            str(self.ramp_duration),
            stringify_optional_float(self.total_weighted_loss),
            self.compatibility_class,
            ";".join(self.invalid_reasons),
            stringify_bool(self.is_eligible_response_observable_rule),
            self.eligibility_class,
            str(self.metrics.finite_target_count),
            str(self.metrics.true_extirpated_comparable_count),
            stringify_optional_float(self.metrics.mean_absolute_error),
            stringify_optional_float(self.metrics.median_absolute_error),
            str(self.metrics.large_abs_error_count),
            str(self.metrics.status_quo_nonfinite_to_finite_count),
            str(self.metrics.status_quo_nonfinite_to_finite_true_extirpated_count),
            str(self.metrics.status_quo_nonfinite_to_finite_not_true_extirpated_count),
            stringify_optional_float(self.loss_delta_from_status_quo),
            stringify_optional_float(self.loss_delta_from_goal013_support_floor),
            stringify_optional_float(self.loss_gap_fraction_closed_to_goal013_support_floor),
            stringify_optional_float(self.mean_absolute_error_delta_from_status_quo),
            stringify_bool(self.improves_loss_vs_status_quo),
            self.finite_support_role,
            self.grid_overfit_risk_class,
        )


@dataclass(frozen=True, slots=True)
class ProxyRulePerformanceRow:
    signal_id: str
    target_rule_id: str
    eligibility_class: str
    affected_site_count: int
    true_extirpated_affected_site_count: int
    status_quo_nonfinite_true_extirpated_count: int
    rule_nonfinite_true_extirpated_count: int
    status_quo_large_abs_error_count: int
    rule_large_abs_error_count: int
    large_abs_error_delta_from_status_quo: int
    status_quo_mean_absolute_error: float | None
    rule_mean_absolute_error: float | None
    mean_absolute_error_delta_from_status_quo: float | None
    improved_site_count: int
    worsened_site_count: int
    unchanged_site_count: int
    rule_screen_role: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.signal_id,
            self.target_rule_id,
            self.eligibility_class,
            str(self.affected_site_count),
            str(self.true_extirpated_affected_site_count),
            str(self.status_quo_nonfinite_true_extirpated_count),
            str(self.rule_nonfinite_true_extirpated_count),
            str(self.status_quo_large_abs_error_count),
            str(self.rule_large_abs_error_count),
            str(self.large_abs_error_delta_from_status_quo),
            stringify_optional_float(self.status_quo_mean_absolute_error),
            stringify_optional_float(self.rule_mean_absolute_error),
            stringify_optional_float(self.mean_absolute_error_delta_from_status_quo),
            str(self.improved_site_count),
            str(self.worsened_site_count),
            str(self.unchanged_site_count),
            self.rule_screen_role,
        )


@dataclass(frozen=True, slots=True)
class GridSimplicityRiskAuditRow:
    target_rule_id: str
    eligibility_class: str
    spatially_keyed: bool
    finite_target_count: int
    default_total_weighted_loss: float | None
    loss_delta_from_status_quo: float | None
    mean_absolute_error_delta_from_status_quo: float | None
    west_band_mean_absolute_error_delta_from_status_quo: float | None
    non_west_band_mean_absolute_error_delta_from_status_quo: float | None
    large_abs_error_delta_from_status_quo: int
    overfit_risk_class: str
    interpretation: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_rule_id,
            self.eligibility_class,
            stringify_bool(self.spatially_keyed),
            str(self.finite_target_count),
            stringify_optional_float(self.default_total_weighted_loss),
            stringify_optional_float(self.loss_delta_from_status_quo),
            stringify_optional_float(self.mean_absolute_error_delta_from_status_quo),
            stringify_optional_float(self.west_band_mean_absolute_error_delta_from_status_quo),
            stringify_optional_float(self.non_west_band_mean_absolute_error_delta_from_status_quo),
            str(self.large_abs_error_delta_from_status_quo),
            self.overfit_risk_class,
            self.interpretation,
        )


@dataclass(frozen=True, slots=True)
class TimingRuleScreenCheck:
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
class SynthSmallResponseObservableTimingRuleScreenResult:
    config: ResponseObservableTimingRuleScreenConfig
    inputs: LoadedResponseObservableTimingRuleInputs
    rule_definitions: tuple[TimingRuleDefinition, ...]
    site_rows: tuple[SiteRuleResolutionRow, ...]
    summary_vector_rows: tuple[RuleSummaryVectorRow, ...]
    component_loss_rows: tuple[RuleComponentLossRow, ...]
    ranking_rows: tuple[RuleRankingRow, ...]
    proxy_performance_rows: tuple[ProxyRulePerformanceRow, ...]
    grid_risk_rows: tuple[GridSimplicityRiskAuditRow, ...]
    recommendation: dict[str, Any]
    verification_checks: tuple[TimingRuleScreenCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def config_payload(self) -> dict[str, Any]:
        return {
            **self.config.to_dict(),
            "source_verifications": source_verifications(self.inputs),
        }

    def write_artifacts(
        self,
        output_dir: str | PathLike[str] = DEFAULT_RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_OUTPUT_DIR,
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "timing_rule_screen_config.json"
        definitions_path = target_dir / "rule_definitions.csv"
        sites_path = target_dir / "site_rule_resolution.csv"
        summaries_path = target_dir / "rule_summary_vectors.csv"
        losses_path = target_dir / "rule_component_losses.csv"
        rankings_path = target_dir / "rule_rankings.csv"
        proxy_path = target_dir / "proxy_rule_performance.csv"
        grid_path = target_dir / "grid_simplicity_risk_audit.csv"
        recommendation_path = target_dir / "recommendation.json"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(dumps(self.config_payload(), indent=2) + "\n", encoding="utf-8")
        write_rows(
            RULE_DEFINITION_COLUMNS,
            (row.to_csv_row() for row in self.rule_definitions),
            definitions_path,
        )
        write_rows(
            SITE_RULE_RESOLUTION_COLUMNS,
            (row.to_csv_row() for row in self.site_rows),
            sites_path,
        )
        write_rows(
            RULE_SUMMARY_VECTOR_COLUMNS,
            (row.to_csv_row() for row in self.summary_vector_rows),
            summaries_path,
        )
        write_rows(
            RULE_COMPONENT_LOSS_COLUMNS,
            (row.to_csv_row() for row in self.component_loss_rows),
            losses_path,
        )
        write_rows(
            RULE_RANKING_COLUMNS,
            (row.to_csv_row() for row in self.ranking_rows),
            rankings_path,
        )
        write_rows(
            PROXY_RULE_PERFORMANCE_COLUMNS,
            (row.to_csv_row() for row in self.proxy_performance_rows),
            proxy_path,
        )
        write_rows(
            GRID_SIMPLICITY_RISK_COLUMNS,
            (row.to_csv_row() for row in self.grid_risk_rows),
            grid_path,
        )
        recommendation_path.write_text(
            dumps(self.recommendation, indent=2) + "\n",
            encoding="utf-8",
        )
        verification_path.write_text(
            dumps(
                {
                    **timing_rule_screen_labels(),
                    "passed": self.passed,
                    "checks": [check.to_dict() for check in self.verification_checks],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_response_observable_timing_rule_report(self), "utf-8")
        return (
            config_path,
            definitions_path,
            sites_path,
            summaries_path,
            losses_path,
            rankings_path,
            proxy_path,
            grid_path,
            recommendation_path,
            verification_path,
            report_path,
        )


def build_synth_small_response_observable_timing_rule_screen(
    *,
    observation_dir: str | PathLike[str] = DEFAULT_OBSERVATION_DIR,
    reconstruction_dir: str | PathLike[str] = DEFAULT_RECONSTRUCTION_DIR,
    evaluation_dir: str | PathLike[str] = DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    summary_vector_dir: str | PathLike[str] = DEFAULT_SUMMARY_VECTOR_DIR,
    compatibility_screen_dir: str | PathLike[str] = DEFAULT_COMPATIBILITY_SCREEN_DIR,
    observation_support_counterfactual_dir: str | PathLike[str] = (
        DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR
    ),
    target_timing_residual_dir: str | PathLike[str] = (
        DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR
    ),
    target_time_error_anatomy_dir: str | PathLike[str] = (
        DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR
    ),
) -> SynthSmallResponseObservableTimingRuleScreenResult:
    config = ResponseObservableTimingRuleScreenConfig(
        observation_dir=str(observation_dir),
        reconstruction_dir=str(reconstruction_dir),
        evaluation_dir=str(evaluation_dir),
        summary_vector_dir=str(summary_vector_dir),
        compatibility_screen_dir=str(compatibility_screen_dir),
        observation_support_counterfactual_dir=str(observation_support_counterfactual_dir),
        target_timing_residual_dir=str(target_timing_residual_dir),
        target_time_error_anatomy_dir=str(target_time_error_anatomy_dir),
    )
    inputs = load_response_observable_timing_rule_inputs(
        observation_dir=config.observation_dir,
        reconstruction_dir=config.reconstruction_dir,
        evaluation_dir=config.evaluation_dir,
        summary_vector_dir=config.summary_vector_dir,
        compatibility_screen_dir=config.compatibility_screen_dir,
        observation_support_counterfactual_dir=config.observation_support_counterfactual_dir,
        target_timing_residual_dir=config.target_timing_residual_dir,
        target_time_error_anatomy_dir=config.target_time_error_anatomy_dir,
    )
    site_rows = build_site_rule_resolution_rows(inputs, config)
    target_rows_by_rule = build_summary_targets_by_rule(
        site_rows,
        inputs.anatomy_site_rows,
    )
    component_rows_by_rule, coverage_rows_by_rule, summary_rows = build_rule_summary_vectors(
        target_rows_by_rule,
        config,
    )
    score_rows, mode_rankings = build_rule_compatibility_rows(
        component_rows=component_rows_by_rule,
        coverage_rows=coverage_rows_by_rule,
        config=config,
    )
    component_loss_rows = build_rule_component_loss_rows(score_rows)
    metrics = rule_metrics_by_rule(site_rows, config)
    ranking_rows = build_rule_ranking_rows(
        mode_rankings=mode_rankings,
        definitions=config.target_rule_definitions,
        metrics=metrics,
    )
    proxy_rows = build_proxy_rule_performance_rows(
        inputs=inputs,
        definitions=config.target_rule_definitions,
        config=config,
    )
    grid_rows = build_grid_simplicity_risk_rows(
        definitions=config.target_rule_definitions,
        site_rows=site_rows,
        ranking_rows=ranking_rows,
        metrics=metrics,
    )
    recommendation = build_timing_rule_screen_recommendation(
        inputs=inputs,
        ranking_rows=ranking_rows,
        grid_rows=grid_rows,
        config=config,
    )
    verification = verify_timing_rule_screen_result(
        inputs=inputs,
        definitions=config.target_rule_definitions,
        site_rows=site_rows,
        component_loss_rows=component_loss_rows,
        ranking_rows=ranking_rows,
        proxy_rows=proxy_rows,
        grid_rows=grid_rows,
        recommendation=recommendation,
        config=config,
    )
    if not all(check.passed for check in verification):
        recommendation = {
            **recommendation,
            "recommendation_class": "timing_rule_screen_contract_failed",
        }
    return SynthSmallResponseObservableTimingRuleScreenResult(
        config=config,
        inputs=inputs,
        rule_definitions=config.target_rule_definitions,
        site_rows=site_rows,
        summary_vector_rows=summary_rows,
        component_loss_rows=component_loss_rows,
        ranking_rows=ranking_rows,
        proxy_performance_rows=proxy_rows,
        grid_risk_rows=grid_rows,
        recommendation=recommendation,
        verification_checks=verification,
    )


def load_response_observable_timing_rule_inputs(
    *,
    observation_dir: str | PathLike[str],
    reconstruction_dir: str | PathLike[str],
    evaluation_dir: str | PathLike[str],
    summary_vector_dir: str | PathLike[str],
    compatibility_screen_dir: str | PathLike[str],
    observation_support_counterfactual_dir: str | PathLike[str],
    target_timing_residual_dir: str | PathLike[str],
    target_time_error_anatomy_dir: str | PathLike[str],
) -> LoadedResponseObservableTimingRuleInputs:
    obs_dir = Path(observation_dir)
    recon_dir = Path(reconstruction_dir)
    eval_dir = Path(evaluation_dir)
    summary_dir = Path(summary_vector_dir)
    compatibility_dir = Path(compatibility_screen_dir)
    counterfactual_dir = Path(observation_support_counterfactual_dir)
    residual_dir = Path(target_timing_residual_dir)
    anatomy_dir = Path(target_time_error_anatomy_dir)

    assert_required_files(obs_dir, OBSERVATION_REQUIRED_FILES, "observations")
    assert_required_files(recon_dir, RECONSTRUCTION_REQUIRED_FILES, "reconstruction")
    assert_required_files(eval_dir, EVALUATION_REQUIRED_FILES, "response-screen evaluation")
    assert_required_files(summary_dir, SUMMARY_VECTOR_REQUIRED_FILES, "summary-vector bridge")
    assert_required_files(
        compatibility_dir,
        COMPATIBILITY_REQUIRED_FILES,
        "compatibility-screen bridge",
    )
    assert_required_files(
        counterfactual_dir,
        COUNTERFACTUAL_REQUIRED_FILES,
        "observation-support counterfactual",
    )
    assert_required_files(
        residual_dir,
        TARGET_TIMING_RESIDUAL_REQUIRED_FILES,
        "target-timing residual decomposition",
    )
    assert_required_files(
        anatomy_dir,
        TARGET_TIME_ERROR_ANATOMY_REQUIRED_FILES,
        "target-time error anatomy",
    )
    return LoadedResponseObservableTimingRuleInputs(
        observation_dir=obs_dir,
        reconstruction_dir=recon_dir,
        evaluation_dir=eval_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        target_timing_residual_dir=residual_dir,
        target_time_error_anatomy_dir=anatomy_dir,
        observation_config=read_json(obs_dir / "observation_config.json"),
        truth_rows=read_csv_rows(obs_dir / "evaluation_truth.csv"),
        reconstruction_config=read_json(recon_dir / "reconstruction_config.json"),
        reconstruction_rows=read_csv_rows(recon_dir / "site_reconstruction.csv"),
        reconstruction_verification=read_json(recon_dir / "verification.json"),
        evaluation_summary=read_json(eval_dir / "screen_evaluation_summary.json"),
        site_evaluation_rows=read_csv_rows(eval_dir / "site_evaluation_audit.csv"),
        evaluation_verification=read_json(eval_dir / "verification.json"),
        summary_vector_mode_summary=read_json(summary_dir / "mode_summary.json"),
        summary_vector_verification=read_json(summary_dir / "verification.json"),
        compatibility_target_summary=read_json(compatibility_dir / "target_summary.json"),
        compatibility_candidate_score_rows=read_csv_rows(
            compatibility_dir / "candidate_scores.csv"
        ),
        compatibility_mode_ranking_rows=read_csv_rows(compatibility_dir / "mode_rankings.csv"),
        compatibility_verification=read_json(compatibility_dir / "verification.json"),
        counterfactual_site_rows=read_csv_rows(
            counterfactual_dir / "site_counterfactual_resolution.csv"
        ),
        counterfactual_ranking_rows=read_csv_rows(counterfactual_dir / "scenario_rankings.csv"),
        counterfactual_verification=read_json(counterfactual_dir / "verification.json"),
        residual_site_rows=read_csv_rows(residual_dir / "site_target_transform_resolution.csv"),
        residual_ranking_rows=read_csv_rows(residual_dir / "target_transform_rankings.csv"),
        residual_delta_rows=read_csv_rows(residual_dir / "component_delta_table.csv"),
        residual_verification=read_json(residual_dir / "verification.json"),
        anatomy_site_rows=read_csv_rows(anatomy_dir / "site_target_time_error_audit.csv"),
        observable_proxy_rows=read_csv_rows(anatomy_dir / "observable_proxy_summary.csv"),
        anatomy_recommendation=read_json(anatomy_dir / "recommendation.json"),
        anatomy_verification=read_json(anatomy_dir / "verification.json"),
    )


def build_site_rule_resolution_rows(
    inputs: LoadedResponseObservableTimingRuleInputs,
    config: ResponseObservableTimingRuleScreenConfig,
) -> tuple[SiteRuleResolutionRow, ...]:
    rows: list[SiteRuleResolutionRow] = []
    for definition in config.target_rule_definitions:
        for source in inputs.anatomy_site_rows:
            target_time = target_time_for_rule(source, definition, config)
            rows.append(
                SiteRuleResolutionRow(
                    target_rule_id=definition.target_rule_id,
                    site_id=source["site_id"],
                    cell_id=parse_int(source["cell_id"]),
                    row=parse_int(source["row"]),
                    col=parse_int(source["col"]),
                    region=source["region"],
                    front_band=source["front_band"],
                    true_extirpated_by_end=parse_bool(source["true_extirpated_by_end"]),
                    status_quo_target_time=parse_optional_float(source["status_quo_target_time"]),
                    goal013_support_floor_target_time=parse_optional_float(
                        source["support_floor_target_time"]
                    ),
                    all_extirpated_true_time_target_time=parse_optional_float(
                        source["all_extirpated_true_time_target_time"]
                    ),
                    rule_target_time=target_time,
                    true_extirpation_time=parse_optional_float(source["true_extirpation_time"]),
                    response_observable_proxy_flags=split_flags(
                        source["response_observable_proxy_flags"]
                    ),
                    truth_only_signal_flags=split_flags(source["truth_only_signal_flags"]),
                    mixed_signal_flags=split_flags(source["mixed_signal_flags"]),
                )
            )
    return tuple(rows)


def target_time_for_rule(
    source: dict[str, str],
    definition: TimingRuleDefinition,
    config: ResponseObservableTimingRuleScreenConfig,
) -> float | None:
    status = parse_optional_float(source["status_quo_target_time"])
    support = parse_optional_float(source["support_floor_target_time"])
    true_time = parse_optional_float(source["true_extirpation_time"])
    last_detection = parse_optional_float(source["last_detection_time"])
    last_survey = parse_optional_float(source["last_survey_time"])
    if definition.target_rule_id == STATUS_QUO_RULE_ID:
        return status
    if definition.target_rule_id == "long_detection_gap_shift_minus4":
        if has_long_detection_gap(status, last_detection, config):
            return shift_target(status, config)
        return status
    if definition.target_rule_id == "west_band_shift_minus4":
        if status is not None and source["front_band"] == "west_band":
            return shift_target(status, config)
        return status
    if definition.target_rule_id == "long_gap_or_west_band_shift_minus4":
        if status is not None and (
            has_long_detection_gap(status, last_detection, config)
            or source["front_band"] == "west_band"
        ):
            return shift_target(status, config)
        return status
    if definition.target_rule_id == CONSERVATIVE_FINITE_SUPPORT_RULE_ID:
        if has_supported_final_survey_gap(source, config):
            return last_survey
        return status
    if definition.target_rule_id == BROAD_FINITE_SUPPORT_STRESS_RULE_ID:
        return status if status is not None else last_survey
    if definition.target_rule_id == GOAL013_SUPPORT_RULE_ID:
        return support
    if definition.target_rule_id == ALL_TRUE_RULE_ID:
        return true_time
    raise ValueError(f"unknown timing rule id: {definition.target_rule_id}")


def build_summary_targets_by_rule(
    site_rows: tuple[SiteRuleResolutionRow, ...],
    anatomy_rows: tuple[dict[str, str], ...],
) -> dict[str, tuple[SummaryVectorTargetRow, ...]]:
    driver_by_site = {
        row["site_id"]: parse_optional_float(row["driver_arrival"]) for row in anatomy_rows
    }
    output: dict[str, list[SummaryVectorTargetRow]] = defaultdict(list)
    for row in site_rows:
        output[row.target_rule_id].append(
            SummaryVectorTargetRow(
                site_id=row.site_id,
                cell_id=row.cell_id,
                grid_row=row.row,
                grid_col=row.col,
                driver_arrival=driver_by_site[row.site_id],
                target_time=row.rule_target_time,
            )
        )
    return {rule_id: tuple(rows) for rule_id, rows in output.items()}


def build_rule_summary_vectors(
    target_rows_by_rule: dict[str, tuple[SummaryVectorTargetRow, ...]],
    config: ResponseObservableTimingRuleScreenConfig,
) -> tuple[
    dict[str, tuple[SummaryComponentRow, ...]],
    dict[str, tuple[CoverageCurveRow, ...]],
    tuple[RuleSummaryVectorRow, ...],
]:
    component_rows_by_rule: dict[str, tuple[SummaryComponentRow, ...]] = {}
    coverage_rows_by_rule: dict[str, tuple[CoverageCurveRow, ...]] = {}
    summary_rows: list[RuleSummaryVectorRow] = []
    for definition in config.target_rule_definitions:
        rule_id = definition.target_rule_id
        component_rows = build_summary_component_rows(rule_id, target_rows_by_rule[rule_id])
        coverage_rows = build_coverage_curve_rows(
            mode=rule_id,
            rows=target_rows_by_rule[rule_id],
            coverage_breakpoints=config.coverage_breakpoints,
        )
        component_rows_by_rule[rule_id] = component_rows
        coverage_rows_by_rule[rule_id] = coverage_rows
        summary_rows.extend(
            RuleSummaryVectorRow(
                target_rule_id=rule_id,
                row_type="summary_component",
                metric=row.component,
                value=row.value,
                missing_reason=row.missing_reason,
            )
            for row in component_rows
        )
        summary_rows.extend(
            RuleSummaryVectorRow(
                target_rule_id=rule_id,
                row_type="coverage_curve",
                metric="target_time",
                value=row.target_time,
                coverage_fraction=row.coverage_fraction,
                finite_target_count=row.finite_target_count,
                missing_reason=row.missing_reason,
            )
            for row in coverage_rows
        )
    return component_rows_by_rule, coverage_rows_by_rule, tuple(summary_rows)


def build_rule_compatibility_rows(
    *,
    component_rows: dict[str, tuple[SummaryComponentRow, ...]],
    coverage_rows: dict[str, tuple[CoverageCurveRow, ...]],
    config: ResponseObservableTimingRuleScreenConfig,
) -> tuple[tuple[Any, ...], tuple[ModeRankingRow, ...]]:
    rule_ids = tuple(definition.target_rule_id for definition in config.target_rule_definitions)
    screen_config = CompatibilityScreenConfig(
        target_modes=rule_ids,
        primary_target_mode=STATUS_QUO_RULE_ID,
        candidates=config.compatibility_config.candidates,
        coverage_breakpoints=config.compatibility_config.coverage_breakpoints,
        required_components=config.compatibility_config.required_components,
        gap_settings=config.compatibility_config.gap_settings,
        compatible_loss_max=config.compatibility_config.compatible_loss_max,
        borderline_loss_max=config.compatibility_config.borderline_loss_max,
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
    score_rows: list[Any] = []
    for rule_id in rule_ids:
        target_components = {
            row.component: scalar_value(row.value, row.missing_reason)
            for row in component_rows[rule_id]
        }
        target_coverage = {
            row.coverage_fraction: scalar_value(row.target_time, row.missing_reason)
            for row in coverage_rows[rule_id]
        }
        for profile in profiles:
            mode_score, rows, _coverage_score_rows = score_candidate_against_target(
                target_mode=rule_id,
                target_components=target_components,
                target_coverage=target_coverage,
                profile=profile,
                config=screen_config,
                settings_by_component=settings_by_component,
            )
            mode_scores.append(mode_score)
            score_rows.extend(rows)
    return tuple(score_rows), build_mode_rankings(mode_scores, config=screen_config)


def build_rule_component_loss_rows(score_rows: tuple[Any, ...]) -> tuple[RuleComponentLossRow, ...]:
    ranks: dict[tuple[str, str, str], int] = {}
    by_rule_candidate: dict[tuple[str, str], list[Any]] = defaultdict(list)
    for row in score_rows:
        by_rule_candidate[(row.target_mode, row.candidate_label)].append(row)
    for key, rows in by_rule_candidate.items():
        ranked = sorted(
            rows,
            key=lambda row: (
                row.weighted_gap is None,
                -(row.weighted_gap or 0.0),
                row.component,
            ),
        )
        for rank, row in enumerate(ranked, start=1):
            ranks[(key[0], key[1], row.component)] = rank
    return tuple(
        RuleComponentLossRow(
            target_rule_id=row.target_mode,
            candidate_label=row.candidate_label,
            is_default=row.is_default,
            component=row.component,
            target_value=row.target_value,
            candidate_value=row.candidate_value,
            scale=row.scale,
            weight=row.weight,
            absolute_gap=row.absolute_gap,
            normalized_abs_gap=row.normalized_abs_gap,
            weighted_gap=row.weighted_gap,
            missing_reason=row.missing_reason,
            component_rank_within_rule_candidate=ranks[
                (row.target_mode, row.candidate_label, row.component)
            ],
        )
        for row in score_rows
    )


def build_rule_ranking_rows(
    *,
    mode_rankings: tuple[ModeRankingRow, ...],
    definitions: tuple[TimingRuleDefinition, ...],
    metrics: dict[str, RuleMetrics],
) -> tuple[RuleRankingRow, ...]:
    definitions_by_id = {definition.target_rule_id: definition for definition in definitions}
    status_by_candidate = {
        row.candidate.label: row for row in mode_rankings if row.target_mode == STATUS_QUO_RULE_ID
    }
    support_by_candidate = {
        row.candidate.label: row
        for row in mode_rankings
        if row.target_mode == GOAL013_SUPPORT_RULE_ID
    }
    status_metrics = metrics[STATUS_QUO_RULE_ID]
    output: list[RuleRankingRow] = []
    for row in mode_rankings:
        definition = definitions_by_id[row.target_mode]
        status = status_by_candidate[row.candidate.label]
        support = support_by_candidate[row.candidate.label]
        loss_delta = optional_difference(row.total_weighted_loss, status.total_weighted_loss)
        support_loss_delta = optional_difference(
            row.total_weighted_loss,
            support.total_weighted_loss,
        )
        mean_error_delta = optional_difference(
            metrics[row.target_mode].mean_absolute_error,
            status_metrics.mean_absolute_error,
        )
        output.append(
            RuleRankingRow(
                target_rule_id=row.target_mode,
                rank=row.rank,
                candidate_label=row.candidate.label,
                is_default=row.candidate.is_default,
                predation_scale=row.candidate.predation_scale,
                half_saturation=row.candidate.half_saturation,
                ramp_duration=row.candidate.ramp_duration,
                total_weighted_loss=row.total_weighted_loss,
                compatibility_class=row.compatibility_class,
                invalid_reasons=row.invalid_reasons,
                is_eligible_response_observable_rule=(
                    definition.eligibility_class == "response_observable"
                ),
                eligibility_class=definition.eligibility_class,
                metrics=metrics[row.target_mode],
                loss_delta_from_status_quo=loss_delta,
                loss_delta_from_goal013_support_floor=support_loss_delta,
                loss_gap_fraction_closed_to_goal013_support_floor=(
                    loss_gap_fraction_closed(
                        rule_loss=row.total_weighted_loss,
                        status_loss=status.total_weighted_loss,
                        support_loss=support.total_weighted_loss,
                    )
                ),
                mean_absolute_error_delta_from_status_quo=mean_error_delta,
                improves_loss_vs_status_quo=(loss_delta is not None and loss_delta < 0.0),
                finite_support_role=finite_support_role(definition),
                grid_overfit_risk_class=grid_overfit_risk_class(definition),
            )
        )
    return tuple(output)


def build_proxy_rule_performance_rows(
    *,
    inputs: LoadedResponseObservableTimingRuleInputs,
    definitions: tuple[TimingRuleDefinition, ...],
    config: ResponseObservableTimingRuleScreenConfig,
) -> tuple[ProxyRulePerformanceRow, ...]:
    residual_proxy_rows = [
        row
        for row in inputs.observable_proxy_rows
        if row["observability_class"] == "response_observable"
        and row["rule_screen_role"] == "residual_timing_candidate"
    ]
    output: list[ProxyRulePerformanceRow] = []
    for proxy in residual_proxy_rows:
        signal_id = proxy["signal_id"]
        affected = [
            row for row in inputs.anatomy_site_rows if site_matches_proxy(row, signal_id, config)
        ]
        true_affected = [row for row in affected if parse_bool(row["true_extirpated_by_end"])]
        status_errors: list[float] = []
        for row in true_affected:
            status_error = parse_optional_float(row["status_quo_absolute_error"])
            if status_error is not None:
                status_errors.append(status_error)
        status_nonfinite = sum(
            parse_optional_float(row["status_quo_target_time"]) is None for row in true_affected
        )
        for definition in definitions:
            rule_errors: list[float] = []
            improved = 0
            worsened = 0
            unchanged = 0
            rule_nonfinite = 0
            for row in true_affected:
                rule_target = target_time_for_rule(row, definition, config)
                true_time = parse_optional_float(row["true_extirpation_time"])
                status_abs = parse_optional_float(row["status_quo_absolute_error"])
                rule_abs = (
                    None
                    if rule_target is None or true_time is None
                    else abs(rule_target - true_time)
                )
                if rule_abs is None:
                    rule_nonfinite += 1
                else:
                    rule_errors.append(rule_abs)
                if status_abs is None and rule_abs is not None:
                    improved += 1
                elif status_abs is not None and rule_abs is None:
                    worsened += 1
                elif status_abs is not None and rule_abs is not None:
                    if rule_abs < status_abs:
                        improved += 1
                    elif rule_abs > status_abs:
                        worsened += 1
                    else:
                        unchanged += 1
            status_large = sum(error >= config.large_error_min for error in status_errors)
            rule_large = sum(error >= config.large_error_min for error in rule_errors)
            status_mean = mean(status_errors)
            rule_mean = mean(rule_errors)
            output.append(
                ProxyRulePerformanceRow(
                    signal_id=signal_id,
                    target_rule_id=definition.target_rule_id,
                    eligibility_class=definition.eligibility_class,
                    affected_site_count=len(affected),
                    true_extirpated_affected_site_count=len(true_affected),
                    status_quo_nonfinite_true_extirpated_count=status_nonfinite,
                    rule_nonfinite_true_extirpated_count=rule_nonfinite,
                    status_quo_large_abs_error_count=status_large,
                    rule_large_abs_error_count=rule_large,
                    large_abs_error_delta_from_status_quo=rule_large - status_large,
                    status_quo_mean_absolute_error=status_mean,
                    rule_mean_absolute_error=rule_mean,
                    mean_absolute_error_delta_from_status_quo=optional_difference(
                        rule_mean,
                        status_mean,
                    ),
                    improved_site_count=improved,
                    worsened_site_count=worsened,
                    unchanged_site_count=unchanged,
                    rule_screen_role=proxy["rule_screen_role"],
                )
            )
    return tuple(output)


def build_grid_simplicity_risk_rows(
    *,
    definitions: tuple[TimingRuleDefinition, ...],
    site_rows: tuple[SiteRuleResolutionRow, ...],
    ranking_rows: tuple[RuleRankingRow, ...],
    metrics: dict[str, RuleMetrics],
) -> tuple[GridSimplicityRiskAuditRow, ...]:
    default_rankings = {
        row.target_rule_id: row for row in ranking_rows if row.candidate_label == "default"
    }
    status = default_rankings[STATUS_QUO_RULE_ID]
    output: list[GridSimplicityRiskAuditRow] = []
    for definition in definitions:
        ranking = default_rankings[definition.target_rule_id]
        rule_metrics = metrics[definition.target_rule_id]
        output.append(
            GridSimplicityRiskAuditRow(
                target_rule_id=definition.target_rule_id,
                eligibility_class=definition.eligibility_class,
                spatially_keyed=definition.spatially_keyed,
                finite_target_count=rule_metrics.finite_target_count,
                default_total_weighted_loss=ranking.total_weighted_loss,
                loss_delta_from_status_quo=ranking.loss_delta_from_status_quo,
                mean_absolute_error_delta_from_status_quo=(
                    ranking.mean_absolute_error_delta_from_status_quo
                ),
                west_band_mean_absolute_error_delta_from_status_quo=(
                    group_mean_abs_error_delta(site_rows, definition.target_rule_id, "west_band")
                ),
                non_west_band_mean_absolute_error_delta_from_status_quo=(
                    group_mean_abs_error_delta(site_rows, definition.target_rule_id, "non_west")
                ),
                large_abs_error_delta_from_status_quo=(
                    rule_metrics.large_abs_error_count - status.metrics.large_abs_error_count
                ),
                overfit_risk_class=grid_overfit_risk_class(definition),
                interpretation=grid_risk_interpretation(definition),
            )
        )
    return tuple(output)


def build_timing_rule_screen_recommendation(
    *,
    inputs: LoadedResponseObservableTimingRuleInputs,
    ranking_rows: tuple[RuleRankingRow, ...],
    grid_rows: tuple[GridSimplicityRiskAuditRow, ...],
    config: ResponseObservableTimingRuleScreenConfig,
) -> dict[str, Any]:
    default_rows = [row for row in ranking_rows if row.candidate_label == "default"]
    status = ranking_by_rule(default_rows, STATUS_QUO_RULE_ID)
    support = ranking_by_rule(default_rows, GOAL013_SUPPORT_RULE_ID)
    all_true = ranking_by_rule(default_rows, ALL_TRUE_RULE_ID)
    conservative_finite_support = ranking_by_rule(
        default_rows,
        CONSERVATIVE_FINITE_SUPPORT_RULE_ID,
    )
    broad_finite_support_stress = ranking_by_rule(
        default_rows,
        BROAD_FINITE_SUPPORT_STRESS_RULE_ID,
    )
    eligible = [
        row
        for row in default_rows
        if row.is_eligible_response_observable_rule and row.total_weighted_loss is not None
    ]
    eligible_sorted = sorted(
        eligible,
        key=lambda row: (
            row.total_weighted_loss if row.total_weighted_loss is not None else float("inf"),
            row.target_rule_id,
        ),
    )
    compatible_eligible = [
        row for row in eligible_sorted if row.compatibility_class == "compatible"
    ]
    best = eligible_sorted[0] if eligible_sorted else None
    spatial_eligible = [
        row
        for row in eligible_sorted
        if grid_by_rule(grid_rows, row.target_rule_id).spatially_keyed
    ]
    nonspatial_eligible = [
        row
        for row in eligible_sorted
        if not grid_by_rule(grid_rows, row.target_rule_id).spatially_keyed
    ]
    if compatible_eligible:
        best_compatible = compatible_eligible[0]
        if grid_by_rule(grid_rows, best_compatible.target_rule_id).spatially_keyed:
            recommendation_class = "spatial_proxy_overfit_risk"
        else:
            recommendation_class = "response_observable_timing_rule_promising"
    elif best is not None:
        recommendation_class = "response_only_signal_insufficient"
    else:
        recommendation_class = "timing_rule_screen_contract_failed"
    conservative_materially_approaches = materially_approaches_goal013(
        conservative_finite_support,
        config_gap_fraction_min=config.material_loss_gap_fraction_min,
    )
    return {
        **timing_rule_screen_labels(),
        "recommendation_class": recommendation_class,
        "eligible_response_observable_rule_count": len(eligible),
        "compatible_eligible_response_observable_rule_count": len(compatible_eligible),
        "best_eligible_response_observable_rule": ranking_payload(best),
        "best_spatial_eligible_response_observable_rule": ranking_payload(
            spatial_eligible[0] if spatial_eligible else None
        ),
        "best_nonspatial_eligible_response_observable_rule": ranking_payload(
            nonspatial_eligible[0] if nonspatial_eligible else None
        ),
        "status_quo_reconciliation": ranking_payload(status),
        "goal013_support_floor_reconciliation": ranking_payload(support),
        "all_extirpated_true_time_reconciliation": ranking_payload(all_true),
        "finite_support_screen": {
            "conservative_candidate": ranking_payload(conservative_finite_support),
            "broad_stress_test": ranking_payload(broad_finite_support_stress),
            "goal013_support_floor_reference": ranking_payload(support),
            "all_true_reference": ranking_payload(all_true),
            "conservative_candidate_materially_approaches_goal013": (
                conservative_materially_approaches
            ),
            "material_loss_gap_fraction_min": (config.material_loss_gap_fraction_min),
            "interpretation": (
                "The conservative finite-support candidate is response-observable and "
                "distinct from the broad all-nonfinite last-survey stress test."
            ),
        },
        "goal015_reconciliation": {
            "recommendation_class": inputs.anatomy_recommendation.get("recommendation_class"),
            "residual_timing_candidate_count": inputs.anatomy_recommendation.get(
                "residual_timing_candidate_count"
            ),
            "top_residual_timing_candidate_proxies": inputs.anatomy_recommendation.get(
                "top_residual_timing_candidate_proxies"
            ),
        },
        "grid_simplicity_risk_assessment": {
            "spatial_rules_are_diagnostic_only": True,
            "spatially_keyed_eligible_rule_count": len(spatial_eligible),
            "best_spatial_rule_id": (
                spatial_eligible[0].target_rule_id if spatial_eligible else ""
            ),
            "best_nonspatial_rule_id": (
                nonspatial_eligible[0].target_rule_id if nonspatial_eligible else ""
            ),
            "interpretation": (
                "The current 25x25 synth-small grid has a simple front-band structure; "
                "spatial/front-band gains are overfit-prone diagnostics, not robust "
                "method evidence."
            ),
        },
        "rationale": [
            "The all-true reference still restores the Goal 010 ideal-truth bridge.",
            "The Goal 013 support-floor reference remains incompatible.",
            "The best eligible response-observable rule improves loss slightly but "
            "remains incompatible.",
            "The conservative finite-support candidate does not restore compatibility "
            "or materially approach the Goal 013 support-floor reference.",
            "The broad nonfinite last-survey expansion is retained only as a stress test.",
            "Spatial/front-band gains are audited as simple-grid diagnostics only.",
            "No production rule, observation design, scoring, candidate, or inference "
            "change is made here.",
        ],
    }


def verify_timing_rule_screen_result(
    *,
    inputs: LoadedResponseObservableTimingRuleInputs,
    definitions: tuple[TimingRuleDefinition, ...],
    site_rows: tuple[SiteRuleResolutionRow, ...],
    component_loss_rows: tuple[RuleComponentLossRow, ...],
    ranking_rows: tuple[RuleRankingRow, ...],
    proxy_rows: tuple[ProxyRulePerformanceRow, ...],
    grid_rows: tuple[GridSimplicityRiskAuditRow, ...],
    recommendation: dict[str, Any],
    config: ResponseObservableTimingRuleScreenConfig,
) -> tuple[TimingRuleScreenCheck, ...]:
    rule_ids = tuple(definition.target_rule_id for definition in definitions)
    default_rankings = {
        row.target_rule_id: row for row in ranking_rows if row.candidate_label == "default"
    }
    expected_score_rows = (
        len(definitions)
        * len(config.compatibility_config.candidates)
        * (len(config.compatibility_config.required_components) + 1)
    )
    prior = prior_goal_reconciliation_details(inputs, default_rankings)
    eligibility_counts = Counter(definition.eligibility_class for definition in definitions)
    conservative = default_rankings[CONSERVATIVE_FINITE_SUPPORT_RULE_ID]
    return (
        TimingRuleScreenCheck(
            name="source_verifications",
            passed=all(source_verifications(inputs).values()),
            message="all prerequisite verification payloads passed",
            details=source_verifications(inputs),
        ),
        TimingRuleScreenCheck(
            name="rule_definitions",
            passed=rule_ids == TIMING_RULE_SCREEN_RULE_IDS
            and eligibility_counts
            == {
                "status_quo_baseline": 1,
                "response_observable": 5,
                "truth_guided_reference": 1,
                "truth_only_reference": 1,
            },
            message="rule definitions separate eligible rules from references",
            details={
                "rule_ids": list(rule_ids),
                "eligibility_counts": dict(sorted(eligibility_counts.items())),
            },
        ),
        TimingRuleScreenCheck(
            name="site_rule_accounting",
            passed=len(site_rows) == 625 * len(definitions)
            and {row.target_rule_id for row in site_rows} == set(rule_ids),
            message="site-rule table has one row per synth-small site per rule",
            details={"site_rule_row_count": len(site_rows)},
        ),
        TimingRuleScreenCheck(
            name="prior_goal_reconciliation",
            passed=prior
            == {
                "status_quo_finite_target_count": 151,
                "status_quo_default_candidate_label": "default",
                "status_quo_default_class": "incompatible",
                "status_quo_default_loss": 3.522636357371111,
                "goal013_support_floor_finite_target_count": 252,
                "goal013_support_floor_default_candidate_label": "default",
                "goal013_support_floor_default_class": "incompatible",
                "goal013_support_floor_default_loss": 1.8850033139786202,
                "all_extirpated_true_time_finite_target_count": 252,
                "all_extirpated_true_time_default_candidate_label": "default",
                "all_extirpated_true_time_default_class": "compatible",
                "all_extirpated_true_time_default_loss": 0.0,
                "goal015_recommendation_class": "response_observable_rule_screen_ready",
                "goal015_residual_timing_candidate_count": 3,
            },
            message="status quo, Goal 013, Goal 014, and Goal 015 reconcile",
            details=prior,
        ),
        TimingRuleScreenCheck(
            name="component_loss_accounting",
            passed=len(component_loss_rows) == expected_score_rows
            and component_losses_match_rankings(component_loss_rows, ranking_rows),
            message="component losses have expected cardinality and sum to rankings",
            details={
                "score_row_count": len(component_loss_rows),
                "expected_score_row_count": expected_score_rows,
            },
        ),
        TimingRuleScreenCheck(
            name="proxy_rule_performance",
            passed={
                "long_detection_to_target_gap",
                "spatial_front_band_west_band_signal",
                "sparse_survey_history",
            }
            <= {row.signal_id for row in proxy_rows},
            message="proxy-stratified performance includes Goal 015 residual proxies",
            details={"proxy_row_count": len(proxy_rows)},
        ),
        TimingRuleScreenCheck(
            name="grid_simplicity_risk_audit",
            passed=any(
                row.overfit_risk_class == "simple_grid_spatial_proxy_overfit_risk"
                for row in grid_rows
            )
            and recommendation["grid_simplicity_risk_assessment"][
                "spatial_rules_are_diagnostic_only"
            ]
            is True,
            message="spatial/front-band gains are labelled overfit-prone diagnostics",
            details={"grid_risk_row_count": len(grid_rows)},
        ),
        TimingRuleScreenCheck(
            name="finite_support_accounting",
            passed=conservative.metrics.status_quo_nonfinite_to_finite_count > 0
            and conservative.metrics.status_quo_nonfinite_to_finite_count
            == (
                conservative.metrics.status_quo_nonfinite_to_finite_true_extirpated_count
                + conservative.metrics.status_quo_nonfinite_to_finite_not_true_extirpated_count
            )
            and recommendation["finite_support_screen"]["conservative_candidate"]["target_rule_id"]
            == CONSERVATIVE_FINITE_SUPPORT_RULE_ID
            and recommendation["finite_support_screen"][
                "conservative_candidate_materially_approaches_goal013"
            ]
            is False,
            message="conservative finite-support expansion is explicitly audited",
            details={
                "target_rule_id": conservative.target_rule_id,
                "status_quo_nonfinite_to_finite_count": (
                    conservative.metrics.status_quo_nonfinite_to_finite_count
                ),
                "status_quo_nonfinite_to_finite_true_extirpated_count": (
                    conservative.metrics.status_quo_nonfinite_to_finite_true_extirpated_count
                ),
                "status_quo_nonfinite_to_finite_not_true_extirpated_count": (
                    conservative.metrics.status_quo_nonfinite_to_finite_not_true_extirpated_count
                ),
                "finite_target_count": conservative.metrics.finite_target_count,
                "compatibility_class": conservative.compatibility_class,
                "total_weighted_loss": conservative.total_weighted_loss,
                "loss_delta_from_goal013_support_floor": (
                    conservative.loss_delta_from_goal013_support_floor
                ),
            },
        ),
        TimingRuleScreenCheck(
            name="recommendation",
            passed=recommendation["recommendation_class"] == "response_only_signal_insufficient"
            and recommendation["compatible_eligible_response_observable_rule_count"] == 0,
            message="recommendation remains diagnostic and does not adopt a rule",
            details={
                "recommendation_class": recommendation["recommendation_class"],
                "eligible_response_observable_rule_count": recommendation[
                    "eligible_response_observable_rule_count"
                ],
            },
        ),
    )


def prior_goal_reconciliation_details(
    inputs: LoadedResponseObservableTimingRuleInputs,
    default_rankings: dict[str, RuleRankingRow],
) -> dict[str, Any]:
    status = default_rankings[STATUS_QUO_RULE_ID]
    support = default_rankings[GOAL013_SUPPORT_RULE_ID]
    all_true = default_rankings[ALL_TRUE_RULE_ID]
    return {
        "status_quo_finite_target_count": status.metrics.finite_target_count,
        "status_quo_default_candidate_label": status.candidate_label,
        "status_quo_default_class": status.compatibility_class,
        "status_quo_default_loss": status.total_weighted_loss,
        "goal013_support_floor_finite_target_count": support.metrics.finite_target_count,
        "goal013_support_floor_default_candidate_label": support.candidate_label,
        "goal013_support_floor_default_class": support.compatibility_class,
        "goal013_support_floor_default_loss": support.total_weighted_loss,
        "all_extirpated_true_time_finite_target_count": all_true.metrics.finite_target_count,
        "all_extirpated_true_time_default_candidate_label": all_true.candidate_label,
        "all_extirpated_true_time_default_class": all_true.compatibility_class,
        "all_extirpated_true_time_default_loss": all_true.total_weighted_loss,
        "goal015_recommendation_class": inputs.anatomy_recommendation.get("recommendation_class"),
        "goal015_residual_timing_candidate_count": inputs.anatomy_recommendation.get(
            "residual_timing_candidate_count"
        ),
    }


def rule_metrics_by_rule(
    site_rows: tuple[SiteRuleResolutionRow, ...],
    config: ResponseObservableTimingRuleScreenConfig,
) -> dict[str, RuleMetrics]:
    grouped: dict[str, list[SiteRuleResolutionRow]] = defaultdict(list)
    for row in site_rows:
        grouped[row.target_rule_id].append(row)
    output: dict[str, RuleMetrics] = {}
    for rule_id, rows in grouped.items():
        finite_count = sum(row.rule_target_time is not None for row in rows)
        true_rows = [row for row in rows if row.true_extirpated_by_end]
        converted = [row for row in rows if row.status_quo_nonfinite_to_finite]
        comparable_errors = [
            row.rule_absolute_error for row in true_rows if row.rule_absolute_error is not None
        ]
        output[rule_id] = RuleMetrics(
            finite_target_count=finite_count,
            true_extirpated_comparable_count=len(comparable_errors),
            mean_absolute_error=mean(comparable_errors),
            median_absolute_error=median(comparable_errors) if comparable_errors else None,
            large_abs_error_count=sum(
                error >= config.large_error_min for error in comparable_errors
            ),
            nonfinite_true_extirpated_count=sum(row.rule_target_time is None for row in true_rows),
            status_quo_nonfinite_to_finite_count=len(converted),
            status_quo_nonfinite_to_finite_true_extirpated_count=sum(
                row.true_extirpated_by_end for row in converted
            ),
            status_quo_nonfinite_to_finite_not_true_extirpated_count=sum(
                not row.true_extirpated_by_end for row in converted
            ),
        )
    return output


def component_losses_match_rankings(
    component_loss_rows: tuple[RuleComponentLossRow, ...],
    ranking_rows: tuple[RuleRankingRow, ...],
) -> bool:
    ranking_map = {(row.target_rule_id, row.candidate_label): row for row in ranking_rows}
    grouped: dict[tuple[str, str], list[RuleComponentLossRow]] = defaultdict(list)
    for row in component_loss_rows:
        grouped[(row.target_rule_id, row.candidate_label)].append(row)
    for key, rows in grouped.items():
        ranking = ranking_map[key]
        if ranking.compatibility_class == "invalid":
            continue
        weighted = [row.weighted_gap for row in rows]
        if any(value is None for value in weighted):
            return False
        total = sum(value for value in weighted if value is not None)
        if ranking.total_weighted_loss is None or not approx_equal(
            ranking.total_weighted_loss,
            total,
        ):
            return False
    return True


def source_verifications(inputs: LoadedResponseObservableTimingRuleInputs) -> dict[str, bool]:
    return {
        "reconstruction": bool(inputs.reconstruction_verification.get("passed")),
        "response_screen_evaluation": bool(inputs.evaluation_verification.get("passed")),
        "summary_vector": bool(inputs.summary_vector_verification.get("passed")),
        "compatibility_screen": bool(inputs.compatibility_verification.get("passed")),
        "observation_support_counterfactual": bool(
            inputs.counterfactual_verification.get("passed")
        ),
        "target_timing_residual_decomposition": bool(inputs.residual_verification.get("passed")),
        "target_time_error_anatomy": bool(inputs.anatomy_verification.get("passed")),
    }


def render_response_observable_timing_rule_report(
    result: SynthSmallResponseObservableTimingRuleScreenResult,
) -> str:
    recommendation = result.recommendation
    best = recommendation["best_eligible_response_observable_rule"]
    lines = [
        "# Synth-Small Response-Observable Timing-Rule Screen",
        "",
        "## Boundary",
        "",
        "Synthetic-only, evaluation-only, response-observable rule screen. No rule "
        "adoption, scoring change, candidate change, richer landscape, ABC, POM, "
        "likelihood, posterior, real-data, or remote-compute work is performed.",
        "",
        "## Outcome",
        "",
        f"- Rules evaluated: `{len(result.rule_definitions)}`",
        "- Eligible response-observable rules: "
        f"`{recommendation['eligible_response_observable_rule_count']}`",
        "- Compatible eligible rules: "
        f"`{recommendation['compatible_eligible_response_observable_rule_count']}`",
        f"- Best eligible rule: `{best['target_rule_id']}`",
        f"- Best eligible compatibility class: `{best['compatibility_class']}`",
        f"- Best eligible loss: `{stringify_optional_float(best['total_weighted_loss'])}`",
        f"- Recommendation: `{recommendation['recommendation_class']}`",
        "",
        "## Reconciliation",
        "",
        "| Target | Finite targets | Default class | Default loss |",
        "| --- | ---: | --- | ---: |",
    ]
    for key, label in (
        ("status_quo_reconciliation", "Status quo"),
        ("goal013_support_floor_reconciliation", "Goal 013 support floor"),
        ("all_extirpated_true_time_reconciliation", "All true"),
    ):
        payload = recommendation[key]
        lines.append(
            f"| {label} | `{payload['finite_target_count']}` | "
            f"`{payload['compatibility_class']}` | "
            f"`{stringify_optional_float(payload['total_weighted_loss'])}` |"
        )
    lines.extend(
        [
            "",
            "## Finite-Support Screen",
            "",
            "| Rule | Converted nonfinite sites | True extirpated | Not true extirpated | "
            "Finite targets | Default class | Default loss | Gap closed to Goal 013 |",
            "| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
        ]
    )
    for key, label in (
        ("conservative_candidate", "Conservative supported final survey gap"),
        ("broad_stress_test", "Broad all-nonfinite last survey stress test"),
    ):
        payload = recommendation["finite_support_screen"][key]
        gap_fraction = stringify_optional_float(
            payload["loss_gap_fraction_closed_to_goal013_support_floor"]
        )
        lines.append(
            f"| {label} | `{payload['status_quo_nonfinite_to_finite_count']}` | "
            f"`{payload['status_quo_nonfinite_to_finite_true_extirpated_count']}` | "
            f"`{payload['status_quo_nonfinite_to_finite_not_true_extirpated_count']}` | "
            f"`{payload['finite_target_count']}` | `{payload['compatibility_class']}` | "
            f"`{stringify_optional_float(payload['total_weighted_loss'])}` | "
            f"`{gap_fraction}` |"
        )
    lines.extend(
        [
            "",
            "The conservative candidate remains incompatible and does not materially "
            "approach the Goal 013 support-floor reference under the deterministic "
            "loss-gap threshold.",
            "",
            "## Grid-Risk Interpretation",
            "",
            recommendation["grid_simplicity_risk_assessment"]["interpretation"],
            "",
        ]
    )
    return "\n".join(lines)


def timing_rule_screen_labels() -> dict[str, bool]:
    return {
        "synthetic_only": True,
        "evaluation_only": True,
        "response_observable_rule_screen_only": True,
        "not_formal_inference": True,
        "no_default_observation_change": True,
        "no_reconstruction_rule_change": True,
        "no_scoring_change": True,
        "no_candidate_change": True,
        "no_richer_landscape_change": True,
        "no_pom_or_likelihood_change": True,
    }


def ranking_payload(row: RuleRankingRow | None) -> dict[str, Any]:
    if row is None:
        return {}
    return {
        "target_rule_id": row.target_rule_id,
        "candidate_label": row.candidate_label,
        "finite_target_count": row.metrics.finite_target_count,
        "total_weighted_loss": row.total_weighted_loss,
        "compatibility_class": row.compatibility_class,
        "mean_absolute_error": row.metrics.mean_absolute_error,
        "large_abs_error_count": row.metrics.large_abs_error_count,
        "status_quo_nonfinite_to_finite_count": (row.metrics.status_quo_nonfinite_to_finite_count),
        "status_quo_nonfinite_to_finite_true_extirpated_count": (
            row.metrics.status_quo_nonfinite_to_finite_true_extirpated_count
        ),
        "status_quo_nonfinite_to_finite_not_true_extirpated_count": (
            row.metrics.status_quo_nonfinite_to_finite_not_true_extirpated_count
        ),
        "loss_delta_from_status_quo": row.loss_delta_from_status_quo,
        "loss_delta_from_goal013_support_floor": (row.loss_delta_from_goal013_support_floor),
        "loss_gap_fraction_closed_to_goal013_support_floor": (
            row.loss_gap_fraction_closed_to_goal013_support_floor
        ),
        "mean_absolute_error_delta_from_status_quo": (
            row.mean_absolute_error_delta_from_status_quo
        ),
        "improves_loss_vs_status_quo": row.improves_loss_vs_status_quo,
        "finite_support_role": row.finite_support_role,
        "grid_overfit_risk_class": row.grid_overfit_risk_class,
    }


def ranking_by_rule(rows: Iterable[RuleRankingRow], rule_id: str) -> RuleRankingRow:
    for row in rows:
        if row.target_rule_id == rule_id:
            return row
    raise ValueError(f"missing ranking row for {rule_id}")


def grid_by_rule(
    rows: tuple[GridSimplicityRiskAuditRow, ...],
    rule_id: str,
) -> GridSimplicityRiskAuditRow:
    for row in rows:
        if row.target_rule_id == rule_id:
            return row
    raise ValueError(f"missing grid-risk row for {rule_id}")


def site_matches_proxy(
    row: dict[str, str],
    signal_id: str,
    config: ResponseObservableTimingRuleScreenConfig,
) -> bool:
    flags = set(split_flags(row["response_observable_proxy_flags"]))
    if signal_id in flags:
        return True
    if signal_id == "sparse_survey_history":
        return (
            parse_int(row["visit_count"]) <= config.sparse_visit_count_max
            or parse_int(row["survey_time_count"]) <= config.sparse_survey_time_count_max
            or parse_int(row["detection_count"]) <= config.sparse_detection_count_max
        )
    if signal_id == "long_detection_to_target_gap":
        return has_long_detection_gap(
            parse_optional_float(row["status_quo_target_time"]),
            parse_optional_float(row["last_detection_time"]),
            config,
        )
    if signal_id == "spatial_front_band_west_band_signal":
        return row["front_band"] == "west_band"
    return False


def has_long_detection_gap(
    target_time: float | None,
    last_detection_time: float | None,
    config: ResponseObservableTimingRuleScreenConfig,
) -> bool:
    return (
        target_time is not None
        and last_detection_time is not None
        and target_time - last_detection_time >= config.long_detection_to_target_gap_min
    )


def has_supported_final_survey_gap(
    source: dict[str, str],
    config: ResponseObservableTimingRuleScreenConfig,
) -> bool:
    status = parse_optional_float(source["status_quo_target_time"])
    last_detection_time = parse_optional_float(source["last_detection_time"])
    last_survey_time = parse_optional_float(source["last_survey_time"])
    if status is not None or last_detection_time is None or last_survey_time is None:
        return False
    return (
        parse_int(source["final_absence_survey_time_count"])
        < config.production_final_absence_run_min
        and parse_int(source["survey_time_count"]) >= config.supported_final_survey_time_count_min
        and parse_int(source["detection_count"]) >= config.supported_final_detection_count_min
        and last_survey_time - last_detection_time >= config.supported_final_survey_gap_min
    )


def shift_target(
    target_time: float | None,
    config: ResponseObservableTimingRuleScreenConfig,
) -> float | None:
    if target_time is None:
        return None
    return max(0.0, target_time - config.target_shift)


def group_mean_abs_error_delta(
    site_rows: tuple[SiteRuleResolutionRow, ...],
    rule_id: str,
    group: str,
) -> float | None:
    status_errors: list[float] = []
    rule_errors: list[float] = []
    for row in site_rows:
        if row.target_rule_id not in {STATUS_QUO_RULE_ID, rule_id}:
            continue
        if not row.true_extirpated_by_end:
            continue
        if group == "west_band":
            in_group = row.front_band == "west_band"
        else:
            in_group = row.front_band != "west_band"
        if not in_group or row.rule_absolute_error is None:
            continue
        if row.target_rule_id == STATUS_QUO_RULE_ID:
            status_errors.append(row.rule_absolute_error)
        else:
            rule_errors.append(row.rule_absolute_error)
    return optional_difference(mean(rule_errors), mean(status_errors))


def grid_overfit_risk_class(definition: TimingRuleDefinition) -> str:
    if definition.eligibility_class == "status_quo_baseline":
        return "baseline"
    if definition.eligibility_class != "response_observable":
        return "not_applicable_reference"
    if definition.spatially_keyed:
        return "simple_grid_spatial_proxy_overfit_risk"
    return "response_observable_nonspatial"


def grid_risk_interpretation(definition: TimingRuleDefinition) -> str:
    if definition.spatially_keyed:
        return (
            "Uses front-band/site metadata on a constrained 25x25 grid; treat any gain "
            "as overfit-prone diagnostic evidence."
        )
    if definition.eligibility_class == "response_observable":
        return "Response-observable non-spatial diagnostic rule."
    if definition.eligibility_class == "status_quo_baseline":
        return "Baseline for comparison."
    return "Synthetic reference, not an eligible response-observable rule."


def finite_support_role(definition: TimingRuleDefinition) -> str:
    if definition.target_rule_id == STATUS_QUO_RULE_ID:
        return "baseline_no_expansion"
    if definition.target_rule_id == CONSERVATIVE_FINITE_SUPPORT_RULE_ID:
        return "conservative_finite_support_candidate"
    if definition.target_rule_id == BROAD_FINITE_SUPPORT_STRESS_RULE_ID:
        return "broad_finite_support_stress_test"
    if definition.target_rule_id == GOAL013_SUPPORT_RULE_ID:
        return "truth_guided_finite_support_reference"
    if definition.target_rule_id == ALL_TRUE_RULE_ID:
        return "truth_only_reference"
    return "timing_residual_rule"


def loss_gap_fraction_closed(
    *,
    rule_loss: float | None,
    status_loss: float | None,
    support_loss: float | None,
) -> float | None:
    if rule_loss is None or status_loss is None or support_loss is None:
        return None
    gap = status_loss - support_loss
    if gap <= 0.0:
        return None
    return (status_loss - rule_loss) / gap


def materially_approaches_goal013(
    row: RuleRankingRow,
    *,
    config_gap_fraction_min: float,
) -> bool:
    fraction = row.loss_gap_fraction_closed_to_goal013_support_floor
    return (
        row.compatibility_class != "invalid"
        and fraction is not None
        and fraction >= config_gap_fraction_min
    )


def mean(values: Iterable[float]) -> float | None:
    values_tuple = tuple(values)
    if not values_tuple:
        return None
    return sum(values_tuple) / len(values_tuple)


def optional_difference(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def optional_abs(value: float | None) -> float | None:
    return None if value is None else abs(value)


def parse_optional_float(value: str) -> float | None:
    if value == "":
        return None
    parsed = float(value)
    return parsed if isfinite(parsed) else None


def parse_int(value: str) -> int:
    return int(value)


def parse_bool(value: str) -> bool:
    return value.lower() == "true"


def split_flags(value: str) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(flag for flag in value.split(";") if flag)


def stringify_bool(value: bool) -> str:
    return "true" if value else "false"


def stringify_optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return stringify_float(value)


def approx_equal(left: float | None, right: float | None, *, tolerance: float = 1e-9) -> bool:
    if left is None or right is None:
        return False
    return abs(left - right) <= tolerance


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], loads(path.read_text(encoding="utf-8")))


def assert_required_files(path: Path, names: tuple[str, ...], label: str) -> None:
    missing = [name for name in names if not (path / name).exists()]
    if missing:
        raise FileNotFoundError(f"missing {label} files in {path}: {', '.join(missing)}")


def write_rows(columns: tuple[str, ...], rows: Iterable[tuple[str, ...]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(columns)
        csv_writer.writerows(rows)


__all__ = [
    "DEFAULT_RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_OUTPUT_DIR",
    "RESPONSE_OBSERVABLE_TIMING_RULE_SCREEN_OUTPUT_FILES",
    "ResponseObservableTimingRuleScreenConfig",
    "SynthSmallResponseObservableTimingRuleScreenResult",
    "TimingRuleDefinition",
    "TimingRuleScreenCheck",
    "build_synth_small_response_observable_timing_rule_screen",
    "default_timing_rule_definitions",
    "render_response_observable_timing_rule_report",
]
