"""Target-time error anatomy audit for synth-small diagnostics."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from csv import DictReader, writer
from dataclasses import dataclass, replace
from json import dumps, loads
from math import isfinite
from os import PathLike
from pathlib import Path
from statistics import median
from typing import Any

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
from .target_timing_residual_decomposition import (
    DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR,
    TARGET_TRANSFORM_IDS,
)

DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR = (
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR / "target_time_error_anatomy"
)
TARGET_TIME_ERROR_ANATOMY_NAME = "synth-small-target-time-error-anatomy-audit"
TARGET_TIME_ERROR_ANATOMY_OUTPUT_FILES = (
    "target_time_error_anatomy_config.json",
    "site_target_time_error_audit.csv",
    "target_time_error_group_summary.csv",
    "error_mechanism_summary.csv",
    "observable_proxy_summary.csv",
    "transform_error_contrast.csv",
    "bias_classification_summary.csv",
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
    "observation_timing_summary.csv",
    "recommendation.json",
    "verification.json",
)
COUNTERFACTUAL_REQUIRED_FILES = (
    "counterfactual_config.json",
    "site_counterfactual_resolution.csv",
    "scenario_reconstruction_summary.csv",
    "scenario_rankings.csv",
    "verification.json",
)
TARGET_TIMING_RESIDUAL_REQUIRED_FILES = (
    "residual_decomposition_config.json",
    "site_target_transform_resolution.csv",
    "target_transform_rankings.csv",
    "component_delta_table.csv",
    "recommendation.json",
    "verification.json",
)
NON_INFERENCE_LABEL_KEYS = (
    "synthetic_only",
    "evaluation_only",
    "error_anatomy_diagnostic_only",
    "not_formal_inference",
    "no_default_observation_change",
    "no_reconstruction_rule_change",
    "no_scoring_change",
    "no_candidate_change",
)
SITE_ERROR_COLUMNS = (
    "site_id",
    "cell_id",
    "row",
    "col",
    "region",
    "front_band",
    "driver_arrival",
    "true_extirpation_time",
    "true_extirpated_by_end",
    "status_quo_target_time",
    "status_quo_finite",
    "status_quo_signed_error",
    "status_quo_absolute_error",
    "status_quo_error_direction",
    "status_quo_error_magnitude_class",
    "support_floor_target_time",
    "support_floor_finite",
    "support_floor_signed_error",
    "support_floor_absolute_error",
    "support_floor_error_direction",
    "support_floor_error_magnitude_class",
    "support_floor_improves_absolute_error",
    "support_floor_error_delta_from_status_quo",
    "support_floor_resolution_status",
    "all_extirpated_true_time_target_time",
    "all_extirpated_true_time_signed_error",
    "audit_classification",
    "false_negative",
    "primary_mechanism",
    "secondary_flags",
    "visit_count",
    "survey_time_count",
    "detection_count",
    "first_detection_time",
    "last_detection_time",
    "final_absence_start_time",
    "final_absence_survey_time_count",
    "first_survey_time",
    "last_survey_time",
    "first_post_extirpation_survey_time",
    "post_extirpation_survey_time_count",
    "post_extirpation_detection_count",
    "post_extirpation_detection_time_count",
    "mean_effort",
    "min_effort",
    "max_effort",
    "post_extirpation_mean_effort",
    "last_detection_minus_true_extirpation",
    "first_post_survey_minus_true_extirpation",
    "last_survey_minus_true_extirpation",
    "near_horizon_class",
    "survey_gap_class",
    "post_extirpation_detection_class",
    "status_quo_finite_class",
    "response_observable_proxy_flags",
    "truth_only_signal_flags",
    "mixed_signal_flags",
)
GROUP_SUMMARY_COLUMNS = (
    "group_type",
    "group",
    "site_count",
    "true_extirpated_count",
    "status_quo_finite_target_count",
    "support_floor_finite_target_count",
    "status_quo_error_count",
    "support_floor_error_count",
    "status_quo_mean_signed_error",
    "status_quo_median_signed_error",
    "status_quo_mean_absolute_error",
    "status_quo_median_absolute_error",
    "status_quo_late_count",
    "status_quo_early_count",
    "status_quo_exact_count",
    "status_quo_nonfinite_true_extirpated_count",
    "support_floor_mean_signed_error",
    "support_floor_median_signed_error",
    "support_floor_mean_absolute_error",
    "support_floor_median_absolute_error",
    "support_floor_late_count",
    "support_floor_early_count",
    "support_floor_exact_count",
    "support_floor_nonfinite_true_extirpated_count",
    "support_floor_large_abs_error_count",
    "support_floor_improved_count",
    "support_floor_worsened_count",
    "support_floor_unchanged_count",
)
MECHANISM_SUMMARY_COLUMNS = (
    "mechanism_label",
    "site_count",
    "true_extirpated_count",
    "status_quo_finite_target_count",
    "support_floor_finite_target_count",
    "status_quo_mean_absolute_error",
    "support_floor_mean_absolute_error",
    "support_floor_late_count",
    "support_floor_large_abs_error_count",
    "support_floor_improved_count",
    "dominant_error_direction",
    "observability_class",
    "later_rule_screen_relevance",
)
OBSERVABLE_PROXY_COLUMNS = (
    "signal_id",
    "observability_class",
    "source_artifact_columns",
    "affected_site_count",
    "true_extirpated_affected_site_count",
    "support_floor_large_abs_error_site_count",
    "support_floor_large_abs_error_fraction",
    "suitable_for_later_response_observable_rule_screen",
    "rule_screen_role",
    "interpretation",
)
TRANSFORM_CONTRAST_COLUMNS = (
    "target_transform_id",
    "finite_true_extirpated_target_count",
    "nonfinite_true_extirpated_count",
    "mean_signed_error",
    "median_signed_error",
    "mean_absolute_error",
    "median_absolute_error",
    "late_count",
    "early_count",
    "exact_count",
    "large_abs_error_count",
    "default_candidate_label",
    "default_total_weighted_loss",
    "default_compatibility_class",
    "restores_goal010_ideal_truth",
)
BIAS_CLASSIFICATION_COLUMNS = (
    "bias_class",
    "classification",
    "affected_site_count",
    "evidence_label",
    "evidence_value",
    "observability_class",
    "source_artifact_columns",
    "interpretation",
)
GOAL013_SUPPORT_SCENARIO_ID = "truth_guided_absence_floor_all"
GOAL013_SUPPORT_TRANSFORM_ID = "goal013_support_floor"
ALL_TRUE_TRANSFORM_ID = "all_extirpated_true_time"


@dataclass(frozen=True, slots=True)
class TargetTimeErrorAnatomyConfig:
    """Configuration for the Goal 015 target-time error anatomy audit."""

    observation_dir: str = str(DEFAULT_OBSERVATION_DIR)
    reconstruction_dir: str = str(DEFAULT_RECONSTRUCTION_DIR)
    evaluation_dir: str = str(DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR)
    false_negative_audit_dir: str = str(DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR)
    observation_support_counterfactual_dir: str = str(
        DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR
    )
    target_timing_residual_dir: str = str(DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR)
    large_error_min: float = 8.0
    moderate_error_min: float = 4.0
    sparse_visit_count_max: int = 12
    sparse_survey_time_count_max: int = 6
    sparse_detection_count_max: int = 2
    near_horizon_gap_max: float = 8.0
    long_detection_to_target_gap_min: float = 8.0

    def to_dict(self) -> dict[str, Any]:
        return {
            **error_anatomy_labels(),
            "diagnostic_name": TARGET_TIME_ERROR_ANATOMY_NAME,
            "observation_dir": self.observation_dir,
            "reconstruction_dir": self.reconstruction_dir,
            "evaluation_dir": self.evaluation_dir,
            "false_negative_audit_dir": self.false_negative_audit_dir,
            "observation_support_counterfactual_dir": (self.observation_support_counterfactual_dir),
            "target_timing_residual_dir": self.target_timing_residual_dir,
            "thresholds": {
                "large_error_min": self.large_error_min,
                "moderate_error_min": self.moderate_error_min,
                "sparse_visit_count_max": self.sparse_visit_count_max,
                "sparse_survey_time_count_max": self.sparse_survey_time_count_max,
                "sparse_detection_count_max": self.sparse_detection_count_max,
                "near_horizon_gap_max": self.near_horizon_gap_max,
                "long_detection_to_target_gap_min": self.long_detection_to_target_gap_min,
            },
            "required_inputs": {
                "observations": list(OBSERVATION_REQUIRED_FILES),
                "reconstruction": list(RECONSTRUCTION_REQUIRED_FILES),
                "response_screen_evaluation": list(EVALUATION_REQUIRED_FILES),
                "false_negative_audit": list(FALSE_NEGATIVE_AUDIT_REQUIRED_FILES),
                "observation_support_counterfactual": list(COUNTERFACTUAL_REQUIRED_FILES),
                "target_timing_residual_decomposition": list(TARGET_TIMING_RESIDUAL_REQUIRED_FILES),
            },
            "output_files": list(TARGET_TIME_ERROR_ANATOMY_OUTPUT_FILES),
        }


@dataclass(frozen=True, slots=True)
class LoadedTargetTimeErrorAnatomyInputs:
    observation_dir: Path
    reconstruction_dir: Path
    evaluation_dir: Path
    false_negative_audit_dir: Path
    observation_support_counterfactual_dir: Path
    target_timing_residual_dir: Path
    observation_config: dict[str, Any]
    site_rows: tuple[dict[str, str], ...]
    visit_rows: tuple[dict[str, str], ...]
    observation_rows: tuple[dict[str, str], ...]
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
    false_negative_timing_rows: tuple[dict[str, str], ...]
    false_negative_recommendation: dict[str, Any]
    false_negative_verification: dict[str, Any]
    counterfactual_config: dict[str, Any]
    counterfactual_site_rows: tuple[dict[str, str], ...]
    counterfactual_summary_rows: tuple[dict[str, str], ...]
    counterfactual_ranking_rows: tuple[dict[str, str], ...]
    counterfactual_verification: dict[str, Any]
    residual_config: dict[str, Any]
    residual_site_rows: tuple[dict[str, str], ...]
    residual_ranking_rows: tuple[dict[str, str], ...]
    residual_delta_rows: tuple[dict[str, str], ...]
    residual_recommendation: dict[str, Any]
    residual_verification: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SiteObservationFeatures:
    visit_count: int
    survey_time_count: int
    detection_count: int
    first_detection_time: float | None
    last_detection_time: float | None
    first_survey_time: float | None
    last_survey_time: float | None
    first_post_extirpation_survey_time: float | None
    post_extirpation_survey_time_count: int
    post_extirpation_detection_count: int
    post_extirpation_detection_time_count: int
    mean_effort: float | None
    min_effort: float | None
    max_effort: float | None
    post_extirpation_mean_effort: float | None
    last_detection_minus_true_extirpation: float | None
    first_post_survey_minus_true_extirpation: float | None
    last_survey_minus_true_extirpation: float | None


@dataclass(frozen=True, slots=True)
class SiteTargetTimeErrorAuditRow:
    site_id: str
    cell_id: int
    row: int
    col: int
    region: str
    front_band: str
    driver_arrival: float | None
    true_extirpation_time: float | None
    true_extirpated_by_end: bool
    status_quo_target_time: float | None
    support_floor_target_time: float | None
    all_extirpated_true_time_target_time: float | None
    audit_classification: str
    false_negative: bool
    primary_mechanism: str
    secondary_flags: str
    features: SiteObservationFeatures
    final_absence_start_time: float | None
    final_absence_survey_time_count: int
    near_horizon_class: str
    survey_gap_class: str
    post_extirpation_detection_class: str
    status_quo_finite_class: str
    support_floor_resolution_status: str
    response_observable_proxy_flags: tuple[str, ...]
    truth_only_signal_flags: tuple[str, ...]
    mixed_signal_flags: tuple[str, ...]

    @property
    def status_quo_finite(self) -> bool:
        return self.status_quo_target_time is not None

    @property
    def support_floor_finite(self) -> bool:
        return self.support_floor_target_time is not None

    @property
    def status_quo_signed_error(self) -> float | None:
        return optional_difference(self.status_quo_target_time, self.true_extirpation_time)

    @property
    def support_floor_signed_error(self) -> float | None:
        return optional_difference(self.support_floor_target_time, self.true_extirpation_time)

    @property
    def all_extirpated_true_time_signed_error(self) -> float | None:
        return optional_difference(
            self.all_extirpated_true_time_target_time,
            self.true_extirpation_time,
        )

    @property
    def status_quo_absolute_error(self) -> float | None:
        return optional_abs(self.status_quo_signed_error)

    @property
    def support_floor_absolute_error(self) -> float | None:
        return optional_abs(self.support_floor_signed_error)

    @property
    def support_floor_improves_absolute_error(self) -> bool:
        if self.true_extirpation_time is None or self.support_floor_absolute_error is None:
            return False
        if self.status_quo_absolute_error is None:
            return True
        return self.support_floor_absolute_error < self.status_quo_absolute_error

    @property
    def support_floor_error_delta_from_status_quo(self) -> float | None:
        if self.support_floor_absolute_error is None or self.status_quo_absolute_error is None:
            return None
        return self.support_floor_absolute_error - self.status_quo_absolute_error

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.site_id,
            str(self.cell_id),
            str(self.row),
            str(self.col),
            self.region,
            self.front_band,
            stringify_optional_float(self.driver_arrival),
            stringify_optional_float(self.true_extirpation_time),
            stringify_bool(self.true_extirpated_by_end),
            stringify_optional_float(self.status_quo_target_time),
            stringify_bool(self.status_quo_finite),
            stringify_optional_float(self.status_quo_signed_error),
            stringify_optional_float(self.status_quo_absolute_error),
            error_direction(self.status_quo_signed_error, self.true_extirpation_time),
            error_magnitude_class(self.status_quo_absolute_error, self.true_extirpation_time),
            stringify_optional_float(self.support_floor_target_time),
            stringify_bool(self.support_floor_finite),
            stringify_optional_float(self.support_floor_signed_error),
            stringify_optional_float(self.support_floor_absolute_error),
            error_direction(self.support_floor_signed_error, self.true_extirpation_time),
            error_magnitude_class(self.support_floor_absolute_error, self.true_extirpation_time),
            stringify_bool(self.support_floor_improves_absolute_error),
            stringify_optional_float(self.support_floor_error_delta_from_status_quo),
            self.support_floor_resolution_status,
            stringify_optional_float(self.all_extirpated_true_time_target_time),
            stringify_optional_float(self.all_extirpated_true_time_signed_error),
            self.audit_classification,
            stringify_bool(self.false_negative),
            self.primary_mechanism,
            self.secondary_flags,
            str(self.features.visit_count),
            str(self.features.survey_time_count),
            str(self.features.detection_count),
            stringify_optional_float(self.features.first_detection_time),
            stringify_optional_float(self.features.last_detection_time),
            stringify_optional_float(self.final_absence_start_time),
            str(self.final_absence_survey_time_count),
            stringify_optional_float(self.features.first_survey_time),
            stringify_optional_float(self.features.last_survey_time),
            stringify_optional_float(self.features.first_post_extirpation_survey_time),
            str(self.features.post_extirpation_survey_time_count),
            str(self.features.post_extirpation_detection_count),
            str(self.features.post_extirpation_detection_time_count),
            stringify_optional_float(self.features.mean_effort),
            stringify_optional_float(self.features.min_effort),
            stringify_optional_float(self.features.max_effort),
            stringify_optional_float(self.features.post_extirpation_mean_effort),
            stringify_optional_float(self.features.last_detection_minus_true_extirpation),
            stringify_optional_float(self.features.first_post_survey_minus_true_extirpation),
            stringify_optional_float(self.features.last_survey_minus_true_extirpation),
            self.near_horizon_class,
            self.survey_gap_class,
            self.post_extirpation_detection_class,
            self.status_quo_finite_class,
            join_flags(self.response_observable_proxy_flags),
            join_flags(self.truth_only_signal_flags),
            join_flags(self.mixed_signal_flags),
        )


@dataclass(frozen=True, slots=True)
class GroupSummaryRow:
    group_type: str
    group: str
    rows: tuple[SiteTargetTimeErrorAuditRow, ...]

    def to_csv_row(self) -> tuple[str, ...]:
        status_errors = finite_values(row.status_quo_signed_error for row in self.rows)
        support_errors = finite_values(row.support_floor_signed_error for row in self.rows)
        true_rows = [row for row in self.rows if row.true_extirpated_by_end]
        return (
            self.group_type,
            self.group,
            str(len(self.rows)),
            str(len(true_rows)),
            str(sum(row.status_quo_finite and row.true_extirpated_by_end for row in self.rows)),
            str(sum(row.support_floor_finite and row.true_extirpated_by_end for row in self.rows)),
            str(len(status_errors)),
            str(len(support_errors)),
            stringify_optional_float(mean_value(status_errors)),
            stringify_optional_float(median_value(status_errors)),
            stringify_optional_float(mean_abs_value(status_errors)),
            stringify_optional_float(median_abs_value(status_errors)),
            str(sum(value > 0 for value in status_errors)),
            str(sum(value < 0 for value in status_errors)),
            str(sum(value == 0 for value in status_errors)),
            str(
                sum(
                    row.true_extirpated_by_end and row.status_quo_signed_error is None
                    for row in self.rows
                )
            ),
            stringify_optional_float(mean_value(support_errors)),
            stringify_optional_float(median_value(support_errors)),
            stringify_optional_float(mean_abs_value(support_errors)),
            stringify_optional_float(median_abs_value(support_errors)),
            str(sum(value > 0 for value in support_errors)),
            str(sum(value < 0 for value in support_errors)),
            str(sum(value == 0 for value in support_errors)),
            str(
                sum(
                    row.true_extirpated_by_end and row.support_floor_signed_error is None
                    for row in self.rows
                )
            ),
            str(sum(abs(value) >= 8.0 for value in support_errors)),
            str(sum(row.support_floor_improves_absolute_error for row in self.rows)),
            str(sum(support_floor_worsens(row) for row in self.rows)),
            str(sum(support_floor_unchanged(row) for row in self.rows)),
        )


@dataclass(frozen=True, slots=True)
class ErrorMechanismSummaryRow:
    mechanism_label: str
    rows: tuple[SiteTargetTimeErrorAuditRow, ...]

    def to_csv_row(self) -> tuple[str, ...]:
        true_rows = tuple(row for row in self.rows if row.true_extirpated_by_end)
        status_errors = finite_values(row.status_quo_signed_error for row in true_rows)
        support_errors = finite_values(row.support_floor_signed_error for row in true_rows)
        late_count = sum(value > 0 for value in support_errors)
        early_count = sum(value < 0 for value in support_errors)
        exact_count = sum(value == 0 for value in support_errors)
        dominant = dominant_direction(late_count, early_count, exact_count)
        observability = (
            "response_observable" if self.mechanism_label == "not_false_negative" else "mixed"
        )
        relevance = (
            "candidate_response_observable_rule_screen_signal"
            if self.mechanism_label == "not_false_negative"
            else "synthetic_mechanism_context"
        )
        return (
            self.mechanism_label,
            str(len(self.rows)),
            str(len(true_rows)),
            str(sum(row.status_quo_finite for row in true_rows)),
            str(sum(row.support_floor_finite for row in true_rows)),
            stringify_optional_float(mean_abs_value(status_errors)),
            stringify_optional_float(mean_abs_value(support_errors)),
            str(late_count),
            str(sum(abs(value) >= 8.0 for value in support_errors)),
            str(sum(row.support_floor_improves_absolute_error for row in true_rows)),
            dominant,
            observability,
            relevance,
        )


@dataclass(frozen=True, slots=True)
class ObservableProxyRow:
    signal_id: str
    observability_class: str
    source_artifact_columns: str
    affected_site_count: int
    true_extirpated_affected_site_count: int
    support_floor_large_abs_error_site_count: int
    support_floor_large_abs_error_fraction: float
    suitable_for_later_response_observable_rule_screen: bool
    rule_screen_role: str
    interpretation: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.signal_id,
            self.observability_class,
            self.source_artifact_columns,
            str(self.affected_site_count),
            str(self.true_extirpated_affected_site_count),
            str(self.support_floor_large_abs_error_site_count),
            stringify_float(self.support_floor_large_abs_error_fraction),
            stringify_bool(self.suitable_for_later_response_observable_rule_screen),
            self.rule_screen_role,
            self.interpretation,
        )


@dataclass(frozen=True, slots=True)
class TransformErrorContrastRow:
    target_transform_id: str
    finite_true_extirpated_target_count: int
    nonfinite_true_extirpated_count: int
    mean_signed_error: float | None
    median_signed_error: float | None
    mean_absolute_error: float | None
    median_absolute_error: float | None
    late_count: int
    early_count: int
    exact_count: int
    large_abs_error_count: int
    default_candidate_label: str
    default_total_weighted_loss: float | None
    default_compatibility_class: str
    restores_goal010_ideal_truth: bool

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_transform_id,
            str(self.finite_true_extirpated_target_count),
            str(self.nonfinite_true_extirpated_count),
            stringify_optional_float(self.mean_signed_error),
            stringify_optional_float(self.median_signed_error),
            stringify_optional_float(self.mean_absolute_error),
            stringify_optional_float(self.median_absolute_error),
            str(self.late_count),
            str(self.early_count),
            str(self.exact_count),
            str(self.large_abs_error_count),
            self.default_candidate_label,
            stringify_optional_float(self.default_total_weighted_loss),
            self.default_compatibility_class,
            stringify_bool(self.restores_goal010_ideal_truth),
        )


@dataclass(frozen=True, slots=True)
class BiasClassificationRow:
    bias_class: str
    classification: str
    affected_site_count: int
    evidence_label: str
    evidence_value: str
    observability_class: str
    source_artifact_columns: str
    interpretation: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.bias_class,
            self.classification,
            str(self.affected_site_count),
            self.evidence_label,
            self.evidence_value,
            self.observability_class,
            self.source_artifact_columns,
            self.interpretation,
        )


@dataclass(frozen=True, slots=True)
class TargetTimeErrorAnatomyCheck:
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
class SynthSmallTargetTimeErrorAnatomyResult:
    config: TargetTimeErrorAnatomyConfig
    inputs: LoadedTargetTimeErrorAnatomyInputs
    site_rows: tuple[SiteTargetTimeErrorAuditRow, ...]
    group_rows: tuple[GroupSummaryRow, ...]
    mechanism_rows: tuple[ErrorMechanismSummaryRow, ...]
    proxy_rows: tuple[ObservableProxyRow, ...]
    transform_rows: tuple[TransformErrorContrastRow, ...]
    bias_rows: tuple[BiasClassificationRow, ...]
    recommendation: dict[str, Any]
    verification_checks: tuple[TargetTimeErrorAnatomyCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def config_payload(self) -> dict[str, Any]:
        return {
            **self.config.to_dict(),
            "source_verifications": source_verifications(self.inputs),
            "site_count": len(self.site_rows),
            "prior_goal_reconciliation": prior_goal_reconciliation_details(
                self.site_rows,
                self.transform_rows,
                self.inputs,
            ),
        }

    def verification_payload(self) -> dict[str, Any]:
        return {
            **error_anatomy_labels(),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
        }

    def write_artifacts(
        self,
        output_dir: str | PathLike[str] = DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR,
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "target_time_error_anatomy_config.json"
        site_path = target_dir / "site_target_time_error_audit.csv"
        group_path = target_dir / "target_time_error_group_summary.csv"
        mechanism_path = target_dir / "error_mechanism_summary.csv"
        proxy_path = target_dir / "observable_proxy_summary.csv"
        transform_path = target_dir / "transform_error_contrast.csv"
        bias_path = target_dir / "bias_classification_summary.csv"
        recommendation_path = target_dir / "recommendation.json"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(dumps(self.config_payload(), indent=2) + "\n", encoding="utf-8")
        write_rows(SITE_ERROR_COLUMNS, (row.to_csv_row() for row in self.site_rows), site_path)
        write_rows(
            GROUP_SUMMARY_COLUMNS,
            (row.to_csv_row() for row in self.group_rows),
            group_path,
        )
        write_rows(
            MECHANISM_SUMMARY_COLUMNS,
            (row.to_csv_row() for row in self.mechanism_rows),
            mechanism_path,
        )
        write_rows(
            OBSERVABLE_PROXY_COLUMNS,
            (row.to_csv_row() for row in self.proxy_rows),
            proxy_path,
        )
        write_rows(
            TRANSFORM_CONTRAST_COLUMNS,
            (row.to_csv_row() for row in self.transform_rows),
            transform_path,
        )
        write_rows(
            BIAS_CLASSIFICATION_COLUMNS,
            (row.to_csv_row() for row in self.bias_rows),
            bias_path,
        )
        recommendation_path.write_text(
            dumps(self.recommendation, indent=2) + "\n",
            encoding="utf-8",
        )
        verification_path.write_text(
            dumps(self.verification_payload(), indent=2) + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_target_time_error_anatomy_report(self), encoding="utf-8")
        return (
            config_path,
            site_path,
            group_path,
            mechanism_path,
            proxy_path,
            transform_path,
            bias_path,
            recommendation_path,
            verification_path,
            report_path,
        )


def build_synth_small_target_time_error_anatomy_audit(
    *,
    observation_dir: str | PathLike[str] = DEFAULT_OBSERVATION_DIR,
    reconstruction_dir: str | PathLike[str] = DEFAULT_RECONSTRUCTION_DIR,
    evaluation_dir: str | PathLike[str] = DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    false_negative_audit_dir: str | PathLike[str] = DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
    observation_support_counterfactual_dir: str | PathLike[str] = (
        DEFAULT_OBSERVATION_SUPPORT_COUNTERFACTUAL_OUTPUT_DIR
    ),
    target_timing_residual_dir: str | PathLike[str] = (
        DEFAULT_TARGET_TIMING_RESIDUAL_DECOMPOSITION_OUTPUT_DIR
    ),
    config: TargetTimeErrorAnatomyConfig | None = None,
) -> SynthSmallTargetTimeErrorAnatomyResult:
    audit_config = config or TargetTimeErrorAnatomyConfig(
        observation_dir=str(observation_dir),
        reconstruction_dir=str(reconstruction_dir),
        evaluation_dir=str(evaluation_dir),
        false_negative_audit_dir=str(false_negative_audit_dir),
        observation_support_counterfactual_dir=str(observation_support_counterfactual_dir),
        target_timing_residual_dir=str(target_timing_residual_dir),
    )
    inputs = load_target_time_error_anatomy_inputs(
        observation_dir=audit_config.observation_dir,
        reconstruction_dir=audit_config.reconstruction_dir,
        evaluation_dir=audit_config.evaluation_dir,
        false_negative_audit_dir=audit_config.false_negative_audit_dir,
        observation_support_counterfactual_dir=(
            audit_config.observation_support_counterfactual_dir
        ),
        target_timing_residual_dir=audit_config.target_timing_residual_dir,
    )
    site_rows = build_site_target_time_error_rows(inputs, audit_config)
    group_rows = build_group_summary_rows(site_rows)
    mechanism_rows = build_error_mechanism_summary_rows(site_rows)
    proxy_rows = build_observable_proxy_rows(site_rows)
    transform_rows = build_transform_error_contrast_rows(inputs)
    bias_rows = build_bias_classification_rows(site_rows, group_rows)
    recommendation = build_target_time_error_anatomy_recommendation(
        site_rows=site_rows,
        group_rows=group_rows,
        proxy_rows=proxy_rows,
        transform_rows=transform_rows,
    )
    checks = verify_target_time_error_anatomy_result(
        inputs=inputs,
        site_rows=site_rows,
        group_rows=group_rows,
        proxy_rows=proxy_rows,
        transform_rows=transform_rows,
        recommendation=recommendation,
    )
    if not all(check.passed for check in checks):
        recommendation = {
            **recommendation,
            "recommendation_class": "target_time_error_contract_failed",
        }
    return SynthSmallTargetTimeErrorAnatomyResult(
        config=audit_config,
        inputs=inputs,
        site_rows=site_rows,
        group_rows=group_rows,
        mechanism_rows=mechanism_rows,
        proxy_rows=proxy_rows,
        transform_rows=transform_rows,
        bias_rows=bias_rows,
        recommendation=recommendation,
        verification_checks=checks,
    )


def load_target_time_error_anatomy_inputs(
    *,
    observation_dir: str | PathLike[str],
    reconstruction_dir: str | PathLike[str],
    evaluation_dir: str | PathLike[str],
    false_negative_audit_dir: str | PathLike[str],
    observation_support_counterfactual_dir: str | PathLike[str],
    target_timing_residual_dir: str | PathLike[str],
) -> LoadedTargetTimeErrorAnatomyInputs:
    obs_dir = Path(observation_dir)
    recon_dir = Path(reconstruction_dir)
    eval_dir = Path(evaluation_dir)
    false_negative_dir = Path(false_negative_audit_dir)
    counterfactual_dir = Path(observation_support_counterfactual_dir)
    residual_dir = Path(target_timing_residual_dir)
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
    assert_required_files(
        residual_dir,
        TARGET_TIMING_RESIDUAL_REQUIRED_FILES,
        "target-timing residual decomposition",
    )
    return LoadedTargetTimeErrorAnatomyInputs(
        observation_dir=obs_dir,
        reconstruction_dir=recon_dir,
        evaluation_dir=eval_dir,
        false_negative_audit_dir=false_negative_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        target_timing_residual_dir=residual_dir,
        observation_config=read_json(obs_dir / "observation_config.json"),
        site_rows=read_csv_rows(obs_dir / "sites.csv"),
        visit_rows=read_csv_rows(obs_dir / "visits.csv"),
        observation_rows=read_csv_rows(obs_dir / "observations.csv"),
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
        false_negative_timing_rows=read_csv_rows(
            false_negative_dir / "observation_timing_summary.csv"
        ),
        false_negative_recommendation=read_json(false_negative_dir / "recommendation.json"),
        false_negative_verification=read_json(false_negative_dir / "verification.json"),
        counterfactual_config=read_json(counterfactual_dir / "counterfactual_config.json"),
        counterfactual_site_rows=read_csv_rows(
            counterfactual_dir / "site_counterfactual_resolution.csv"
        ),
        counterfactual_summary_rows=read_csv_rows(
            counterfactual_dir / "scenario_reconstruction_summary.csv"
        ),
        counterfactual_ranking_rows=read_csv_rows(counterfactual_dir / "scenario_rankings.csv"),
        counterfactual_verification=read_json(counterfactual_dir / "verification.json"),
        residual_config=read_json(residual_dir / "residual_decomposition_config.json"),
        residual_site_rows=read_csv_rows(residual_dir / "site_target_transform_resolution.csv"),
        residual_ranking_rows=read_csv_rows(residual_dir / "target_transform_rankings.csv"),
        residual_delta_rows=read_csv_rows(residual_dir / "component_delta_table.csv"),
        residual_recommendation=read_json(residual_dir / "recommendation.json"),
        residual_verification=read_json(residual_dir / "verification.json"),
    )


def build_site_target_time_error_rows(
    inputs: LoadedTargetTimeErrorAnatomyInputs,
    config: TargetTimeErrorAnatomyConfig,
) -> tuple[SiteTargetTimeErrorAuditRow, ...]:
    reconstruction_by_site = {row["site_id"]: row for row in inputs.reconstruction_rows}
    evaluation_by_site = {row["site_id"]: row for row in inputs.site_evaluation_rows}
    false_negative_by_site = {row["site_id"]: row for row in inputs.false_negative_site_rows}
    transform_by_key = {
        (row["target_transform_id"], row["site_id"]): row for row in inputs.residual_site_rows
    }
    features_by_site = build_observation_features_by_site(inputs)
    output: list[SiteTargetTimeErrorAuditRow] = []
    for truth_row in inputs.truth_rows:
        site_id = truth_row["site_id"]
        reconstruction = reconstruction_by_site[site_id]
        evaluation = evaluation_by_site[site_id]
        false_negative = false_negative_by_site.get(site_id)
        true_time = parse_optional_float(truth_row["true_extirpation"])
        status_quo_time = parse_optional_float(reconstruction["observed_extirpation_time"])
        support_transform = transform_by_key[(GOAL013_SUPPORT_TRANSFORM_ID, site_id)]
        all_true_transform = transform_by_key[(ALL_TRUE_TRANSFORM_ID, site_id)]
        support_time = parse_optional_float(support_transform["transformed_target_time"])
        all_true_time = parse_optional_float(all_true_transform["transformed_target_time"])
        features = features_by_site[site_id]
        true_extirpated = true_time is not None
        primary_mechanism = primary_mechanism_for_site(
            true_extirpated=true_extirpated,
            false_negative_row=false_negative,
        )
        row = SiteTargetTimeErrorAuditRow(
            site_id=site_id,
            cell_id=parse_int(truth_row["cell_id"]),
            row=parse_int(truth_row["row"]),
            col=parse_int(truth_row["col"]),
            region=reconstruction["region"],
            front_band=reconstruction["front_band"],
            driver_arrival=parse_optional_float(truth_row["driver_arrival"]),
            true_extirpation_time=true_time,
            true_extirpated_by_end=true_extirpated,
            status_quo_target_time=status_quo_time,
            support_floor_target_time=support_time,
            all_extirpated_true_time_target_time=all_true_time,
            audit_classification=evaluation["audit_classification"],
            false_negative=false_negative is not None,
            primary_mechanism=primary_mechanism,
            secondary_flags="" if false_negative is None else false_negative["secondary_flags"],
            features=features,
            final_absence_start_time=parse_optional_float(
                reconstruction["final_absence_start_time"]
            ),
            final_absence_survey_time_count=parse_int(
                reconstruction["final_absence_survey_time_count"]
            ),
            near_horizon_class=near_horizon_class(features, config),
            survey_gap_class=survey_gap_class(features),
            post_extirpation_detection_class=post_extirpation_detection_class(features),
            status_quo_finite_class=status_quo_finite_class(true_extirpated, status_quo_time),
            support_floor_resolution_status=support_floor_resolution_status(
                true_extirpated=true_extirpated,
                false_negative=false_negative is not None,
                support_time=support_time,
                status_quo_time=status_quo_time,
            ),
            response_observable_proxy_flags=response_observable_proxy_flags(
                reconstruction,
                features,
                config,
            ),
            truth_only_signal_flags=truth_only_signal_flags(true_extirpated),
            mixed_signal_flags=mixed_signal_flags(
                false_negative=false_negative is not None,
                features=features,
                near_horizon=near_horizon_class(features, config),
                support_time=support_time,
                status_quo_time=status_quo_time,
            ),
        )
        output.append(row)
    return add_data_derived_spatial_proxy_flags(tuple(output))


def build_observation_features_by_site(
    inputs: LoadedTargetTimeErrorAnatomyInputs,
) -> dict[str, SiteObservationFeatures]:
    truth_by_site = {row["site_id"]: row for row in inputs.truth_rows}
    visits_by_site: dict[str, list[dict[str, str]]] = defaultdict(list)
    observations_by_site: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inputs.visit_rows:
        visits_by_site[row["site_id"]].append(row)
    for row in inputs.observation_rows:
        observations_by_site[row["site_id"]].append(row)

    output: dict[str, SiteObservationFeatures] = {}
    for site_id, truth_row in truth_by_site.items():
        visits = visits_by_site.get(site_id, [])
        observations = observations_by_site.get(site_id, [])
        survey_times = sorted({parse_required_float(row["time_index"]) for row in visits})
        detection_times = sorted(
            {
                parse_required_float(row["time_index"])
                for row in observations
                if parse_bool(row["detected"])
            }
        )
        efforts = [parse_required_float(row["effort"]) for row in visits]
        true_time = parse_optional_float(truth_row["true_extirpation"])
        if true_time is None:
            post_visits: list[dict[str, str]] = []
            post_observations: list[dict[str, str]] = []
            post_survey_times: list[float] = []
            post_detection_times: list[float] = []
        else:
            post_visits = [
                row for row in visits if parse_required_float(row["time_index"]) > true_time
            ]
            post_observations = [
                row for row in observations if parse_required_float(row["time_index"]) > true_time
            ]
            post_survey_times = sorted(
                {parse_required_float(row["time_index"]) for row in post_visits}
            )
            post_detection_times = sorted(
                {
                    parse_required_float(row["time_index"])
                    for row in post_observations
                    if parse_bool(row["detected"])
                }
            )
        post_efforts = [parse_required_float(row["effort"]) for row in post_visits]
        first_post = first_value(post_survey_times)
        last_survey = last_value(survey_times)
        last_detection = last_value(detection_times)
        output[site_id] = SiteObservationFeatures(
            visit_count=len(visits),
            survey_time_count=len(survey_times),
            detection_count=sum(parse_bool(row["detected"]) for row in observations),
            first_detection_time=first_value(detection_times),
            last_detection_time=last_detection,
            first_survey_time=first_value(survey_times),
            last_survey_time=last_survey,
            first_post_extirpation_survey_time=first_post,
            post_extirpation_survey_time_count=len(post_survey_times),
            post_extirpation_detection_count=sum(
                parse_bool(row["detected"]) for row in post_observations
            ),
            post_extirpation_detection_time_count=len(post_detection_times),
            mean_effort=mean_value(efforts),
            min_effort=min(efforts) if efforts else None,
            max_effort=max(efforts) if efforts else None,
            post_extirpation_mean_effort=mean_value(post_efforts),
            last_detection_minus_true_extirpation=optional_difference(last_detection, true_time),
            first_post_survey_minus_true_extirpation=optional_difference(first_post, true_time),
            last_survey_minus_true_extirpation=optional_difference(last_survey, true_time),
        )
    return output


def build_group_summary_rows(
    site_rows: tuple[SiteTargetTimeErrorAuditRow, ...],
) -> tuple[GroupSummaryRow, ...]:
    grouped: list[GroupSummaryRow] = [GroupSummaryRow("overall", "all_sites", site_rows)]
    dimensions: tuple[tuple[str, str], ...] = (
        ("false_negative_status", "false_negative_class"),
        ("primary_mechanism", "primary_mechanism"),
        ("region", "region"),
        ("front_band", "front_band"),
        ("post_extirpation_detection_class", "post_extirpation_detection_class"),
        ("near_horizon_class", "near_horizon_class"),
        ("survey_gap_class", "survey_gap_class"),
        ("status_quo_finite_class", "status_quo_finite_class"),
        ("support_floor_resolution_status", "support_floor_resolution_status"),
    )
    for group_type, attr in dimensions:
        by_group: dict[str, list[SiteTargetTimeErrorAuditRow]] = defaultdict(list)
        for row in site_rows:
            by_group[group_value(row, attr)].append(row)
        for group in sorted(by_group):
            grouped.append(GroupSummaryRow(group_type, group, tuple(by_group[group])))
    return tuple(grouped)


def build_error_mechanism_summary_rows(
    site_rows: tuple[SiteTargetTimeErrorAuditRow, ...],
) -> tuple[ErrorMechanismSummaryRow, ...]:
    by_mechanism: dict[str, list[SiteTargetTimeErrorAuditRow]] = defaultdict(list)
    for row in site_rows:
        if row.true_extirpated_by_end:
            by_mechanism[row.primary_mechanism].append(row)
    return tuple(
        ErrorMechanismSummaryRow(mechanism, tuple(by_mechanism[mechanism]))
        for mechanism in sorted(by_mechanism)
    )


def build_observable_proxy_rows(
    site_rows: tuple[SiteTargetTimeErrorAuditRow, ...],
) -> tuple[ObservableProxyRow, ...]:
    strongest_spatial = strongest_spatial_group(build_group_summary_rows(site_rows))
    spatial_signal_id = spatial_proxy_signal_id(strongest_spatial)
    spatial_group_type = str(strongest_spatial["group_type"])
    spatial_group = str(strongest_spatial["group"])
    return (
        observable_proxy_row(
            site_rows,
            signal_id="status_quo_nonfinite",
            observability_class="response_observable",
            source_artifact_columns=(
                "site_reconstruction.csv:observed_extirpated_by_end,observed_extirpation_time"
            ),
            predicate=lambda row: not row.status_quo_finite,
            suitable_for_later_response_observable_rule_screen=False,
            rule_screen_role="finite_target_support_context",
            interpretation="identifies sites unresolved by the current response-only rule",
        ),
        observable_proxy_row(
            site_rows,
            signal_id="short_final_absence_run",
            observability_class="response_observable",
            source_artifact_columns="site_reconstruction.csv:final_absence_survey_time_count",
            predicate=lambda row: row.final_absence_survey_time_count < 2,
            suitable_for_later_response_observable_rule_screen=False,
            rule_screen_role="finite_target_support_context",
            interpretation="captures insufficient final sustained-absence support",
        ),
        observable_proxy_row(
            site_rows,
            signal_id="sparse_survey_history",
            observability_class="response_observable",
            source_artifact_columns=(
                "site_reconstruction.csv:visit_count,survey_time_count,detection_count"
            ),
            predicate=lambda row: (
                row.features.visit_count <= 12
                or row.features.survey_time_count <= 6
                or row.features.detection_count <= 2
            ),
            suitable_for_later_response_observable_rule_screen=True,
            rule_screen_role="residual_timing_candidate",
            interpretation=(
                "flags low visit, survey-time, or detection support and reports residual "
                "large-error coverage"
            ),
        ),
        observable_proxy_row(
            site_rows,
            signal_id=spatial_signal_id,
            observability_class="response_observable",
            source_artifact_columns="sites.csv:region,front_band",
            predicate=lambda row: spatial_proxy_row_matches(
                row,
                group_type=spatial_group_type,
                group=spatial_group,
            ),
            suitable_for_later_response_observable_rule_screen=True,
            rule_screen_role="residual_timing_candidate",
            interpretation=(
                "data-derived spatial/front-band signal for remaining large timing errors"
            ),
        ),
        observable_proxy_row(
            site_rows,
            signal_id="long_detection_to_target_gap",
            observability_class="response_observable",
            source_artifact_columns=(
                "site_reconstruction.csv:last_detection_time,observed_extirpation_time"
            ),
            predicate=long_detection_to_target_gap,
            suitable_for_later_response_observable_rule_screen=True,
            rule_screen_role="residual_timing_candidate",
            interpretation=(
                "audits how far finite final-absence targets sit after the last detection"
            ),
        ),
        observable_proxy_row(
            site_rows,
            signal_id="target_time_signed_error",
            observability_class="truth_only",
            source_artifact_columns=(
                "evaluation_truth.csv:true_extirpation; "
                "site_target_transform_resolution.csv:transformed_target_time"
            ),
            predicate=lambda row: row.true_extirpated_by_end,
            suitable_for_later_response_observable_rule_screen=False,
            rule_screen_role="truth_only_reference",
            interpretation="direct timing error exists only under synthetic truth",
        ),
        observable_proxy_row(
            site_rows,
            signal_id="all_extirpated_true_time_reference",
            observability_class="truth_only",
            source_artifact_columns=(
                "target_timing_residual_decomposition/site_target_transform_resolution.csv:"
                "all_extirpated_true_time"
            ),
            predicate=lambda row: row.true_extirpated_by_end,
            suitable_for_later_response_observable_rule_screen=False,
            rule_screen_role="truth_only_reference",
            interpretation="ideal truth reference reconciles the Goal 010 bridge",
        ),
        observable_proxy_row(
            site_rows,
            signal_id="near_horizon_to_true_extirpation",
            observability_class="mixed",
            source_artifact_columns=(
                "observations.csv:time_index; evaluation_truth.csv:true_extirpation"
            ),
            predicate=lambda row: row.near_horizon_class == "near_horizon",
            suitable_for_later_response_observable_rule_screen=False,
            rule_screen_role="mixed_evaluation_context",
            interpretation="survey timing is observed but the true-time horizon is synthetic",
        ),
        observable_proxy_row(
            site_rows,
            signal_id="post_extirpation_detection_persistence",
            observability_class="mixed",
            source_artifact_columns=(
                "observations.csv:detected,time_index; evaluation_truth.csv:true_extirpation"
            ),
            predicate=lambda row: row.features.post_extirpation_detection_count > 0,
            suitable_for_later_response_observable_rule_screen=False,
            rule_screen_role="mixed_evaluation_context",
            interpretation="detections are observed but post-extirpation status is truth-labelled",
        ),
        observable_proxy_row(
            site_rows,
            signal_id="goal013_support_floor_resolution",
            observability_class="mixed",
            source_artifact_columns=(
                "observation_support_counterfactual/site_counterfactual_resolution.csv"
            ),
            predicate=lambda row: row.support_floor_improves_absolute_error,
            suitable_for_later_response_observable_rule_screen=False,
            rule_screen_role="mixed_evaluation_context",
            interpretation="truth-guided support is diagnostic and not an observation design",
        ),
    )


def observable_proxy_row(
    site_rows: tuple[SiteTargetTimeErrorAuditRow, ...],
    *,
    signal_id: str,
    observability_class: str,
    source_artifact_columns: str,
    predicate: Callable[[SiteTargetTimeErrorAuditRow], bool],
    suitable_for_later_response_observable_rule_screen: bool,
    rule_screen_role: str,
    interpretation: str,
) -> ObservableProxyRow:
    affected_rows = [row for row in site_rows if predicate(row)]
    true_rows = [row for row in affected_rows if row.true_extirpated_by_end]
    large_rows = [
        row
        for row in true_rows
        if row.support_floor_absolute_error is not None and row.support_floor_absolute_error >= 8.0
    ]
    fraction = len(large_rows) / len(true_rows) if true_rows else 0.0
    return ObservableProxyRow(
        signal_id=signal_id,
        observability_class=observability_class,
        source_artifact_columns=source_artifact_columns,
        affected_site_count=len(affected_rows),
        true_extirpated_affected_site_count=len(true_rows),
        support_floor_large_abs_error_site_count=len(large_rows),
        support_floor_large_abs_error_fraction=fraction,
        suitable_for_later_response_observable_rule_screen=(
            suitable_for_later_response_observable_rule_screen
        ),
        rule_screen_role=rule_screen_role,
        interpretation=interpretation,
    )


def build_transform_error_contrast_rows(
    inputs: LoadedTargetTimeErrorAnatomyInputs,
) -> tuple[TransformErrorContrastRow, ...]:
    rows_by_transform: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inputs.residual_site_rows:
        rows_by_transform[row["target_transform_id"]].append(row)
    ranking_by_transform = {
        row["target_transform_id"]: row
        for row in inputs.residual_ranking_rows
        if row["candidate_label"] == "default"
    }
    output: list[TransformErrorContrastRow] = []
    for transform_id in TARGET_TRANSFORM_IDS:
        transform_rows = rows_by_transform[transform_id]
        errors: list[float] = []
        nonfinite = 0
        for row in transform_rows:
            true_time = parse_optional_float(row["true_extirpation_time"])
            if true_time is None:
                continue
            target_time = parse_optional_float(row["transformed_target_time"])
            if target_time is None:
                nonfinite += 1
            else:
                errors.append(target_time - true_time)
        ranking = ranking_by_transform[transform_id]
        loss = parse_optional_float(ranking["total_weighted_loss"])
        compatibility_class = ranking["compatibility_class"]
        restores = (
            transform_id == ALL_TRUE_TRANSFORM_ID
            and compatibility_class == "compatible"
            and approx_equal(loss, 0.0)
        )
        output.append(
            TransformErrorContrastRow(
                target_transform_id=transform_id,
                finite_true_extirpated_target_count=len(errors),
                nonfinite_true_extirpated_count=nonfinite,
                mean_signed_error=mean_value(errors),
                median_signed_error=median_value(errors),
                mean_absolute_error=mean_abs_value(errors),
                median_absolute_error=median_abs_value(errors),
                late_count=sum(value > 0 for value in errors),
                early_count=sum(value < 0 for value in errors),
                exact_count=sum(value == 0 for value in errors),
                large_abs_error_count=sum(abs(value) >= 8.0 for value in errors),
                default_candidate_label=ranking["candidate_label"],
                default_total_weighted_loss=loss,
                default_compatibility_class=compatibility_class,
                restores_goal010_ideal_truth=restores,
            )
        )
    return tuple(output)


def build_bias_classification_rows(
    site_rows: tuple[SiteTargetTimeErrorAuditRow, ...],
    group_rows: tuple[GroupSummaryRow, ...],
) -> tuple[BiasClassificationRow, ...]:
    true_count = sum(row.true_extirpated_by_end for row in site_rows)
    support_errors = finite_values(row.support_floor_signed_error for row in site_rows)
    late_count = sum(value > 0 for value in support_errors)
    early_count = sum(value < 0 for value in support_errors)
    near_horizon_count = sum(row.near_horizon_class == "near_horizon" for row in site_rows)
    post_detection_count = sum(
        row.features.post_extirpation_detection_count > 0 for row in site_rows
    )
    strongest_spatial = strongest_spatial_group(group_rows)
    support_improved = sum(row.support_floor_improves_absolute_error for row in site_rows)
    return (
        BiasClassificationRow(
            bias_class="late_bias",
            classification="dominant" if late_count / true_count > 0.5 else "secondary",
            affected_site_count=late_count,
            evidence_label="support_floor_late_count",
            evidence_value=f"{late_count}/{true_count}",
            observability_class="mixed",
            source_artifact_columns=("site_target_time_error_audit.csv:support_floor_signed_error"),
            interpretation="support-floor target errors are overwhelmingly late",
        ),
        BiasClassificationRow(
            bias_class="early_bias",
            classification="minor",
            affected_site_count=early_count,
            evidence_label="support_floor_early_count",
            evidence_value=f"{early_count}/{true_count}",
            observability_class="mixed",
            source_artifact_columns=("site_target_time_error_audit.csv:support_floor_signed_error"),
            interpretation="early errors are present but not the dominant bias",
        ),
        BiasClassificationRow(
            bias_class="end_window_compression",
            classification="secondary",
            affected_site_count=near_horizon_count,
            evidence_label="near_horizon_count",
            evidence_value=f"{near_horizon_count}/{true_count}",
            observability_class="mixed",
            source_artifact_columns=(
                "observations.csv:time_index; evaluation_truth.csv:true_extirpation"
            ),
            interpretation=(
                "near-horizon timing contributes but does not explain all residual error"
            ),
        ),
        BiasClassificationRow(
            bias_class="spatial_structure",
            classification="dominant",
            affected_site_count=strongest_spatial["large_abs_error_count"],
            evidence_label=strongest_spatial["group"],
            evidence_value=stringify_float(strongest_spatial["mean_absolute_error"]),
            observability_class="response_observable",
            source_artifact_columns="sites.csv:region,front_band",
            interpretation="remaining large errors are spatially concentrated",
        ),
        BiasClassificationRow(
            bias_class="survey_gap_association",
            classification="secondary",
            affected_site_count=support_improved,
            evidence_label="support_floor_improved_count",
            evidence_value=str(support_improved),
            observability_class="response_observable",
            source_artifact_columns=(
                "site_reconstruction.csv:survey_time_count,final_absence_survey_time_count"
            ),
            interpretation="support floor resolves finite-target gaps but not residual timing bias",
        ),
        BiasClassificationRow(
            bias_class="detection_persistence_association",
            classification="secondary",
            affected_site_count=post_detection_count,
            evidence_label="post_extirpation_detection_count",
            evidence_value=str(post_detection_count),
            observability_class="mixed",
            source_artifact_columns=(
                "observations.csv:detected; evaluation_truth.csv:true_extirpation"
            ),
            interpretation="post-extirpation detections matter but do not dominate residual loss",
        ),
        BiasClassificationRow(
            bias_class="truth_only_dependency",
            classification="required_for_audit_not_rule",
            affected_site_count=true_count,
            evidence_label="true_extirpation_time",
            evidence_value=str(true_count),
            observability_class="truth_only",
            source_artifact_columns="evaluation_truth.csv:true_extirpation",
            interpretation="direct error labels are synthetic-only validation diagnostics",
        ),
    )


def build_target_time_error_anatomy_recommendation(
    *,
    site_rows: tuple[SiteTargetTimeErrorAuditRow, ...],
    group_rows: tuple[GroupSummaryRow, ...],
    proxy_rows: tuple[ObservableProxyRow, ...],
    transform_rows: tuple[TransformErrorContrastRow, ...],
) -> dict[str, Any]:
    support_transform = transform_by_id(transform_rows, GOAL013_SUPPORT_TRANSFORM_ID)
    all_true_transform = transform_by_id(transform_rows, ALL_TRUE_TRANSFORM_ID)
    dominant_group = dominant_remaining_error_group(group_rows)
    strongest_spatial = strongest_spatial_group(group_rows)
    proxy_class_counts = Counter(row.observability_class for row in proxy_rows)
    suitable_proxy_count = sum(
        row.suitable_for_later_response_observable_rule_screen for row in proxy_rows
    )
    residual_candidates = residual_timing_candidate_proxy_payloads(proxy_rows)
    if not all_true_transform.restores_goal010_ideal_truth:
        recommendation_class = "target_time_error_contract_failed"
    elif residual_candidates:
        recommendation_class = "response_observable_rule_screen_ready"
    elif support_transform.nonfinite_true_extirpated_count > 0:
        recommendation_class = "survey_design_gap_dominates"
    else:
        recommendation_class = "timing_bias_truth_only_not_observable"
    return {
        **error_anatomy_labels(),
        "recommendation_class": recommendation_class,
        "site_count": len(site_rows),
        "true_extirpated_site_count": sum(row.true_extirpated_by_end for row in site_rows),
        "status_quo_finite_target_count": sum(
            row.true_extirpated_by_end and row.status_quo_finite for row in site_rows
        ),
        "support_floor_finite_target_count": sum(
            row.true_extirpated_by_end and row.support_floor_finite for row in site_rows
        ),
        "support_floor_mean_absolute_error": support_transform.mean_absolute_error,
        "all_extirpated_true_time_restores_compatibility": (
            all_true_transform.restores_goal010_ideal_truth
        ),
        "dominant_remaining_error_group": dominant_group,
        "strongest_spatial_signal": strongest_spatial,
        "observable_proxy_class_counts": dict(sorted(proxy_class_counts.items())),
        "suitable_response_observable_proxy_count": suitable_proxy_count,
        "residual_timing_candidate_count": len(residual_candidates),
        "top_residual_timing_candidate_proxies": residual_candidates[:3],
        "rationale": [
            "Goal 013 support floor restores finite targets but remains incompatible.",
            "The remaining large absolute errors are concentrated in already finite "
            "status-quo targets.",
            "The recommendation is supported only by response-observable residual-timing "
            "candidate proxies with nonzero large-error coverage.",
            "No reconstruction, observation, scoring, candidate, or inference change is made here.",
        ],
    }


def residual_timing_candidate_proxy_payloads(
    proxy_rows: tuple[ObservableProxyRow, ...],
) -> list[dict[str, Any]]:
    candidates = [
        row
        for row in proxy_rows
        if row.observability_class == "response_observable"
        and row.rule_screen_role == "residual_timing_candidate"
        and row.support_floor_large_abs_error_site_count > 0
    ]
    return [
        {
            "signal_id": row.signal_id,
            "support_floor_large_abs_error_site_count": (
                row.support_floor_large_abs_error_site_count
            ),
            "support_floor_large_abs_error_fraction": row.support_floor_large_abs_error_fraction,
        }
        for row in sorted(
            candidates,
            key=lambda row: (
                -row.support_floor_large_abs_error_site_count,
                -row.support_floor_large_abs_error_fraction,
                row.signal_id,
            ),
        )
    ]


def verify_target_time_error_anatomy_result(
    *,
    inputs: LoadedTargetTimeErrorAnatomyInputs,
    site_rows: tuple[SiteTargetTimeErrorAuditRow, ...],
    group_rows: tuple[GroupSummaryRow, ...],
    proxy_rows: tuple[ObservableProxyRow, ...],
    transform_rows: tuple[TransformErrorContrastRow, ...],
    recommendation: dict[str, Any],
) -> tuple[TargetTimeErrorAnatomyCheck, ...]:
    source_passed = source_verifications(inputs)
    prior = prior_goal_reconciliation_details(site_rows, transform_rows, inputs)
    group_overall = group_by_type_and_label(group_rows)[("overall", "all_sites")]
    proxy_classes = {row.observability_class for row in proxy_rows}
    return (
        TargetTimeErrorAnatomyCheck(
            name="source_verifications",
            passed=all(source_passed.values()),
            message="all prerequisite verification payloads passed",
            details=source_passed,
        ),
        TargetTimeErrorAnatomyCheck(
            name="site_accounting",
            passed=len(site_rows) == len(inputs.site_rows) == len(inputs.truth_rows) == 625
            and len({row.site_id for row in site_rows}) == len(site_rows),
            message="site audit contains one row per synth-small site",
            details={
                "site_count": len(site_rows),
                "truth_row_count": len(inputs.truth_rows),
                "observation_site_count": len(inputs.site_rows),
            },
        ),
        TargetTimeErrorAnatomyCheck(
            name="prior_goal_reconciliation",
            passed=prior
            == {
                "site_count": 625,
                "ideal_true_finite_target_count": 252,
                "status_quo_finite_target_count": 151,
                "false_negative_count": 101,
                "support_floor_finite_target_count": 252,
                "all_extirpated_true_time_restores_compatibility": True,
            },
            message="Goal 012-014 site counts and bridge restoration reconcile",
            details=prior,
        ),
        TargetTimeErrorAnatomyCheck(
            name="group_summary_accounting",
            passed=group_overall.rows == site_rows
            and int(group_overall.to_csv_row()[2]) == len(site_rows)
            and int(group_overall.to_csv_row()[3]) == 252,
            message="overall group summary reconciles to the site-level table",
            details={"group_row_count": len(group_rows), "overall_site_count": len(site_rows)},
        ),
        TargetTimeErrorAnatomyCheck(
            name="observable_proxy_inventory",
            passed={"response_observable", "truth_only", "mixed"} <= proxy_classes,
            message="proxy inventory separates response-observable, truth-only, and mixed signals",
            details={"observability_classes": sorted(proxy_classes)},
        ),
        TargetTimeErrorAnatomyCheck(
            name="transform_contrast_reconciliation",
            passed=transform_by_id(
                transform_rows,
                ALL_TRUE_TRANSFORM_ID,
            ).restores_goal010_ideal_truth
            and transform_by_id(
                transform_rows, GOAL013_SUPPORT_TRANSFORM_ID
            ).default_compatibility_class
            == "incompatible",
            message="transform contrast preserves Goal 014 bridge outcome",
            details={
                row.target_transform_id: {
                    "finite_true_extirpated_target_count": (
                        row.finite_true_extirpated_target_count
                    ),
                    "default_compatibility_class": row.default_compatibility_class,
                    "restores_goal010_ideal_truth": row.restores_goal010_ideal_truth,
                }
                for row in transform_rows
            },
        ),
        TargetTimeErrorAnatomyCheck(
            name="recommendation",
            passed=recommendation["recommendation_class"] == "response_observable_rule_screen_ready"
            and int_payload(recommendation.get("residual_timing_candidate_count"), 0) > 0,
            message=(
                "recommendation remains diagnostic and is supported by residual-timing "
                "proxy coverage"
            ),
            details={
                "recommendation_class": recommendation["recommendation_class"],
                "residual_timing_candidate_count": recommendation.get(
                    "residual_timing_candidate_count"
                ),
            },
        ),
    )


def prior_goal_reconciliation_details(
    site_rows: tuple[SiteTargetTimeErrorAuditRow, ...],
    transform_rows: tuple[TransformErrorContrastRow, ...],
    inputs: LoadedTargetTimeErrorAnatomyInputs,
) -> dict[str, Any]:
    _ = inputs
    return {
        "site_count": len(site_rows),
        "ideal_true_finite_target_count": sum(row.true_extirpated_by_end for row in site_rows),
        "status_quo_finite_target_count": sum(
            row.true_extirpated_by_end and row.status_quo_finite for row in site_rows
        ),
        "false_negative_count": sum(row.false_negative for row in site_rows),
        "support_floor_finite_target_count": sum(
            row.true_extirpated_by_end and row.support_floor_finite for row in site_rows
        ),
        "all_extirpated_true_time_restores_compatibility": transform_by_id(
            transform_rows,
            ALL_TRUE_TRANSFORM_ID,
        ).restores_goal010_ideal_truth,
    }


def source_verifications(inputs: LoadedTargetTimeErrorAnatomyInputs) -> dict[str, bool]:
    return {
        "observations": bool(inputs.truth_reference),
        "extirpation_reconstruction": bool(inputs.reconstruction_verification.get("passed")),
        "response_screen_evaluation": bool(inputs.evaluation_verification.get("passed")),
        "false_negative_audit": bool(inputs.false_negative_verification.get("passed")),
        "observation_support_counterfactual": bool(
            inputs.counterfactual_verification.get("passed")
        ),
        "target_timing_residual_decomposition": bool(inputs.residual_verification.get("passed")),
    }


def render_target_time_error_anatomy_report(
    result: SynthSmallTargetTimeErrorAnatomyResult,
) -> str:
    recommendation = result.recommendation
    transforms = {row.target_transform_id: row for row in result.transform_rows}
    lines = [
        "# Synth-Small Target-Time Error Anatomy Audit",
        "",
        "## Scope",
        "",
        (
            "This is a synthetic-only, evaluation-only error-anatomy diagnostic. "
            "It does not change default observation design, production "
            "reconstruction rules, scoring, candidates, or inference logic."
        ),
        "",
        "## Site Accounting",
        "",
        f"- Sites audited: `{len(result.site_rows)}`",
        f"- True extirpated sites: `{recommendation['true_extirpated_site_count']}`",
        f"- Status-quo finite targets: `{recommendation['status_quo_finite_target_count']}`",
        f"- Support-floor finite targets: `{recommendation['support_floor_finite_target_count']}`",
        "",
        "## Transform Error Contrast",
        "",
        "| Transform | Finite true targets | Mean abs error | Default loss | Class |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for transform_id in TARGET_TRANSFORM_IDS:
        row = transforms[transform_id]
        lines.append(
            "| "
            f"`{transform_id}` | `{row.finite_true_extirpated_target_count}` | "
            f"`{stringify_optional_float(row.mean_absolute_error)}` | "
            f"`{stringify_optional_float(row.default_total_weighted_loss)}` | "
            f"`{row.default_compatibility_class}` |"
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"- Class: `{recommendation['recommendation_class']}`",
            "- Dominant remaining error group: "
            f"`{recommendation['dominant_remaining_error_group']['group']}`",
            f"- Strongest spatial signal: `{recommendation['strongest_spatial_signal']['group']}`",
            "- Residual-timing candidate proxies: "
            f"`{recommendation['residual_timing_candidate_count']}`",
            "",
            "## Residual-Timing Candidate Proxies",
            "",
            "| Signal | Large-error sites | Large-error fraction |",
            "| --- | ---: | ---: |",
        ]
    )
    for proxy in recommendation["top_residual_timing_candidate_proxies"]:
        lines.append(
            "| "
            f"`{proxy['signal_id']}` | "
            f"`{proxy['support_floor_large_abs_error_site_count']}` | "
            f"`{stringify_float(proxy['support_floor_large_abs_error_fraction'])}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Limit",
            "",
            (
                "Direct target-time errors require synthetic truth. Response-observable "
                "signals identified here require a later bounded rule-screen goal before "
                "any reconstruction-rule change."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def primary_mechanism_for_site(
    *,
    true_extirpated: bool,
    false_negative_row: dict[str, str] | None,
) -> str:
    if false_negative_row is not None:
        return false_negative_row["primary_mechanism"]
    if true_extirpated:
        return "not_false_negative"
    return "not_true_extirpated"


def near_horizon_class(
    features: SiteObservationFeatures,
    config: TargetTimeErrorAnatomyConfig,
) -> str:
    if features.last_survey_minus_true_extirpation is None:
        return "not_true_extirpated"
    if features.last_survey_minus_true_extirpation <= config.near_horizon_gap_max:
        return "near_horizon"
    return "not_near_horizon"


def survey_gap_class(features: SiteObservationFeatures) -> str:
    if features.last_survey_minus_true_extirpation is None:
        return "not_true_extirpated"
    if features.post_extirpation_survey_time_count == 0:
        return "no_post_extirpation_survey"
    if features.post_extirpation_survey_time_count == 1:
        return "single_post_extirpation_survey_time"
    return "multiple_post_extirpation_survey_times"


def post_extirpation_detection_class(features: SiteObservationFeatures) -> str:
    if features.last_survey_minus_true_extirpation is None:
        return "not_true_extirpated"
    if features.post_extirpation_detection_count > 0:
        return "post_extirpation_detection_seen"
    return "no_post_extirpation_detection"


def status_quo_finite_class(true_extirpated: bool, status_quo_time: float | None) -> str:
    if not true_extirpated:
        return "not_true_extirpated"
    return "status_quo_finite" if status_quo_time is not None else "status_quo_nonfinite"


def support_floor_resolution_status(
    *,
    true_extirpated: bool,
    false_negative: bool,
    support_time: float | None,
    status_quo_time: float | None,
) -> str:
    if not true_extirpated:
        return "not_true_extirpated"
    if false_negative and support_time is not None:
        return "false_negative_resolved_by_support_floor"
    if false_negative:
        return "false_negative_unresolved"
    if status_quo_time is not None:
        return "status_quo_already_finite"
    return "status_quo_nonfinite_non_false_negative"


def response_observable_proxy_flags(
    reconstruction: dict[str, str],
    features: SiteObservationFeatures,
    config: TargetTimeErrorAnatomyConfig,
) -> tuple[str, ...]:
    flags: list[str] = []
    status_time = parse_optional_float(reconstruction["observed_extirpation_time"])
    if status_time is None:
        flags.append("status_quo_nonfinite")
    else:
        flags.append("status_quo_finite")
    if features.visit_count <= config.sparse_visit_count_max:
        flags.append("low_visit_count")
    if features.survey_time_count <= config.sparse_survey_time_count_max:
        flags.append("low_survey_time_count")
    if features.detection_count <= config.sparse_detection_count_max:
        flags.append("low_detection_count")
    if parse_int(reconstruction["final_absence_survey_time_count"]) < 2:
        flags.append("short_final_absence_run")
    if (
        features.last_detection_time is not None
        and status_time is not None
        and status_time - features.last_detection_time >= config.long_detection_to_target_gap_min
    ):
        flags.append("long_detection_to_target_gap")
    return tuple(flags)


def add_data_derived_spatial_proxy_flags(
    rows: tuple[SiteTargetTimeErrorAuditRow, ...],
) -> tuple[SiteTargetTimeErrorAuditRow, ...]:
    strongest_spatial = strongest_spatial_group(build_group_summary_rows(rows))
    signal_id = spatial_proxy_signal_id(strongest_spatial)
    group_type = str(strongest_spatial["group_type"])
    group = str(strongest_spatial["group"])
    output: list[SiteTargetTimeErrorAuditRow] = []
    for row in rows:
        if spatial_proxy_row_matches(row, group_type=group_type, group=group):
            output.append(
                replace(
                    row,
                    response_observable_proxy_flags=(
                        *row.response_observable_proxy_flags,
                        signal_id,
                    ),
                )
            )
        else:
            output.append(row)
    return tuple(output)


def spatial_proxy_signal_id(spatial_signal: dict[str, Any]) -> str:
    group_type = str(spatial_signal["group_type"])
    group = str(spatial_signal["group"])
    return f"spatial_{slugify(group_type)}_{slugify(group)}_signal"


def spatial_proxy_row_matches(
    row: SiteTargetTimeErrorAuditRow,
    *,
    group_type: str,
    group: str,
) -> bool:
    if group_type == "front_band":
        return row.front_band == group
    if group_type == "region":
        return row.region == group
    return False


def slugify(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value.lower())


def truth_only_signal_flags(true_extirpated: bool) -> tuple[str, ...]:
    if not true_extirpated:
        return ()
    return ("true_extirpation_time", "target_time_signed_error")


def mixed_signal_flags(
    *,
    false_negative: bool,
    features: SiteObservationFeatures,
    near_horizon: str,
    support_time: float | None,
    status_quo_time: float | None,
) -> tuple[str, ...]:
    flags: list[str] = []
    if false_negative:
        flags.append("false_negative_truth_label")
    if near_horizon == "near_horizon":
        flags.append("near_horizon_to_true_extirpation")
    if features.post_extirpation_detection_count > 0:
        flags.append("post_extirpation_detection_persistence")
    if status_quo_time is None and support_time is not None:
        flags.append("goal013_support_floor_truth_guided_resolution")
    return tuple(flags)


def group_value(row: SiteTargetTimeErrorAuditRow, attr: str) -> str:
    if attr == "false_negative_class":
        if row.false_negative:
            return "false_negative"
        if row.true_extirpated_by_end:
            return "true_extirpated_not_false_negative"
        return "not_true_extirpated"
    value = getattr(row, attr)
    if not isinstance(value, str):
        raise TypeError(f"expected group value to be str for {attr}")
    return value


def long_detection_to_target_gap(row: SiteTargetTimeErrorAuditRow) -> bool:
    if row.status_quo_target_time is None or row.features.last_detection_time is None:
        return False
    return row.status_quo_target_time - row.features.last_detection_time >= 8.0


def support_floor_worsens(row: SiteTargetTimeErrorAuditRow) -> bool:
    if not row.true_extirpated_by_end:
        return False
    if row.status_quo_absolute_error is None or row.support_floor_absolute_error is None:
        return False
    return row.support_floor_absolute_error > row.status_quo_absolute_error


def support_floor_unchanged(row: SiteTargetTimeErrorAuditRow) -> bool:
    if not row.true_extirpated_by_end:
        return False
    if row.status_quo_absolute_error is None or row.support_floor_absolute_error is None:
        return False
    return row.support_floor_absolute_error == row.status_quo_absolute_error


def dominant_direction(late_count: int, early_count: int, exact_count: int) -> str:
    counts = {
        "late": late_count,
        "early": early_count,
        "exact": exact_count,
    }
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def dominant_remaining_error_group(
    group_rows: tuple[GroupSummaryRow, ...],
) -> dict[str, Any]:
    rows = [
        row
        for row in group_rows
        if row.group_type == "primary_mechanism" and row.group != "not_true_extirpated"
    ]
    ranked = sorted(
        rows,
        key=lambda row: (
            -support_floor_large_abs_error_count(row),
            row.group,
        ),
    )
    top = ranked[0]
    return {
        "group_type": top.group_type,
        "group": top.group,
        "large_abs_error_count": support_floor_large_abs_error_count(top),
    }


def strongest_spatial_group(
    group_rows: tuple[GroupSummaryRow, ...],
) -> dict[str, Any]:
    rows = [row for row in group_rows if row.group_type in {"region", "front_band"}]
    ranked = sorted(
        rows,
        key=lambda row: (
            -(
                mean_abs_value(finite_values(site.support_floor_signed_error for site in row.rows))
                or 0.0
            ),
            -support_floor_large_abs_error_count(row),
            row.group,
        ),
    )
    top = ranked[0]
    mean_abs = mean_abs_value(finite_values(site.support_floor_signed_error for site in top.rows))
    return {
        "group_type": top.group_type,
        "group": top.group,
        "mean_absolute_error": mean_abs,
        "large_abs_error_count": support_floor_large_abs_error_count(top),
    }


def support_floor_large_abs_error_count(row: GroupSummaryRow) -> int:
    return sum(
        value >= 8.0
        for value in finite_values(site.support_floor_absolute_error for site in row.rows)
    )


def group_by_type_and_label(
    group_rows: tuple[GroupSummaryRow, ...],
) -> dict[tuple[str, str], GroupSummaryRow]:
    return {(row.group_type, row.group): row for row in group_rows}


def transform_by_id(
    transform_rows: tuple[TransformErrorContrastRow, ...],
    transform_id: str,
) -> TransformErrorContrastRow:
    return next(row for row in transform_rows if row.target_transform_id == transform_id)


def error_direction(error: float | None, true_time: float | None) -> str:
    if true_time is None:
        return "not_comparable"
    if error is None:
        return "nonfinite"
    if error > 0:
        return "late"
    if error < 0:
        return "early"
    return "exact"


def error_magnitude_class(error: float | None, true_time: float | None) -> str:
    if true_time is None:
        return "not_comparable"
    if error is None:
        return "nonfinite"
    if error == 0:
        return "exact"
    if error < 4.0:
        return "small_abs_1_to_3"
    if error < 8.0:
        return "moderate_abs_4_to_7"
    return "large_abs_ge_8"


def finite_values(values: Iterable[float | None]) -> list[float]:
    return [value for value in values if value is not None and isfinite(value)]


def mean_value(values: Iterable[float]) -> float | None:
    collected = list(values)
    if not collected:
        return None
    return sum(collected) / len(collected)


def median_value(values: Iterable[float]) -> float | None:
    collected = list(values)
    if not collected:
        return None
    return float(median(collected))


def mean_abs_value(values: Iterable[float]) -> float | None:
    collected = [abs(value) for value in values]
    return mean_value(collected)


def median_abs_value(values: Iterable[float]) -> float | None:
    collected = [abs(value) for value in values]
    return median_value(collected)


def first_value(values: list[float]) -> float | None:
    return values[0] if values else None


def last_value(values: list[float]) -> float | None:
    return values[-1] if values else None


def optional_difference(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def optional_abs(value: float | None) -> float | None:
    if value is None:
        return None
    return abs(value)


def approx_equal(left: float | None, right: float | None, *, tolerance: float = 1e-9) -> bool:
    if left is None or right is None:
        return False
    return abs(left - right) <= tolerance


def assert_required_files(path: Path, names: tuple[str, ...], label: str) -> None:
    missing = [name for name in names if not (path / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(f"missing required {label} artifacts: {missing_text}")


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return dict_payload(loads(path.read_text(encoding="utf-8")))


def write_rows(columns: tuple[str, ...], rows: Iterable[tuple[str, ...]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(columns)
        csv_writer.writerows(rows)


def parse_int(value: str) -> int:
    return int(value)


def parse_bool(value: str) -> bool:
    return value.lower() in {"1", "true"}


def parse_required_float(value: str) -> float:
    if value == "":
        raise ValueError("expected finite float, got blank value")
    parsed = float(value)
    if not isfinite(parsed):
        raise ValueError(f"expected finite float, got {value!r}")
    return parsed


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


def join_flags(flags: tuple[str, ...]) -> str:
    return ";".join(flags)


def error_anatomy_labels() -> dict[str, bool]:
    return {key: True for key in NON_INFERENCE_LABEL_KEYS}


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
    "DEFAULT_TARGET_TIME_ERROR_ANATOMY_OUTPUT_DIR",
    "TARGET_TIME_ERROR_ANATOMY_OUTPUT_FILES",
    "BiasClassificationRow",
    "ErrorMechanismSummaryRow",
    "GroupSummaryRow",
    "LoadedTargetTimeErrorAnatomyInputs",
    "ObservableProxyRow",
    "SiteObservationFeatures",
    "SiteTargetTimeErrorAuditRow",
    "SynthSmallTargetTimeErrorAnatomyResult",
    "TargetTimeErrorAnatomyCheck",
    "TargetTimeErrorAnatomyConfig",
    "TransformErrorContrastRow",
    "build_synth_small_target_time_error_anatomy_audit",
    "render_target_time_error_anatomy_report",
]
