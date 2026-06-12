"""Disk-first audit of synth-small response-screen false negatives."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from csv import DictReader, writer
from dataclasses import dataclass
from json import dumps, loads
from math import isfinite
from os import PathLike
from pathlib import Path
from statistics import median
from typing import Any, TypedDict

from .observations import stringify_float

DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR = Path("artifacts/synth_small_response_screen/evaluation")
DEFAULT_RECONSTRUCTION_DIR = Path("artifacts/synth_small_extirpation_reconstruction")
DEFAULT_OBSERVATION_DIR = Path("artifacts/synth_small_observations")
DEFAULT_FALSE_NEGATIVE_MISMATCH_AUDIT_DIR = Path(
    "artifacts/synth_small_compatibility_screen/mismatch_audit"
)
DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR = (
    DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR / "false_negative_audit"
)
FALSE_NEGATIVE_AUDIT_NAME = "synth-small-false-negative-mechanism-audit"
FALSE_NEGATIVE_AUDIT_OUTPUT_FILES = (
    "false_negative_audit_config.json",
    "false_negative_site_audit.csv",
    "mechanism_summary.csv",
    "group_mechanism_summary.csv",
    "observation_timing_summary.csv",
    "recommendation.json",
    "verification.json",
    "report.md",
)
EVALUATION_REQUIRED_FILES = (
    "screen_evaluation_summary.json",
    "group_evaluation_summary.csv",
    "site_evaluation_audit.csv",
    "verification.json",
)
RECONSTRUCTION_REQUIRED_FILES = (
    "site_reconstruction.csv",
    "time_detection_summary.csv",
    "verification.json",
)
OBSERVATION_REQUIRED_FILES = (
    "visits.csv",
    "observations.csv",
    "evaluation_truth.csv",
    "truth_reference.json",
)
MISMATCH_AUDIT_REQUIRED_FILES = (
    "evaluation_bridge_summary.json",
    "recommendation.json",
    "verification.json",
)
MECHANISM_PRIORITY = (
    "no_post_extirpation_surveys",
    "late_extirpation_near_survey_horizon",
    "post_extirpation_detection_blocks_absence",
    "insufficient_post_extirpation_survey_history",
    "sparse_or_low_effort_observation",
    "weak_east_or_edge_signal",
    "unclassified_false_negative",
)
FALSE_NEGATIVE_SITE_COLUMNS = (
    "site_id",
    "cell_id",
    "row",
    "col",
    "region",
    "front_band",
    "primary_mechanism",
    "secondary_flags",
    "true_extirpation_time",
    "observed_extirpation_time",
    "reconstruction_status",
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
)
MECHANISM_SUMMARY_COLUMNS = (
    "primary_mechanism",
    "false_negative_count",
    "false_negative_fraction",
    "mean_post_extirpation_survey_time_count",
    "mean_post_extirpation_detection_count",
    "mean_last_survey_minus_true_extirpation",
)
GROUP_MECHANISM_SUMMARY_COLUMNS = (
    "group_type",
    "group",
    "primary_mechanism",
    "false_negative_count",
    "group_false_negative_count",
    "group_share",
    "total_false_negative_share",
)
OBSERVATION_TIMING_SUMMARY_COLUMNS = (
    "summary_type",
    "label",
    "false_negative_count",
    "mean_post_extirpation_survey_time_count",
    "median_post_extirpation_survey_time_count",
    "mean_post_extirpation_detection_count",
    "mean_true_extirpation_time",
    "mean_last_survey_minus_true_extirpation",
    "mean_last_detection_minus_true_extirpation",
    "mean_first_post_survey_minus_true_extirpation",
    "mean_effort",
    "mean_min_effort",
    "mean_max_effort",
    "mean_post_extirpation_mean_effort",
    "low_mean_effort_count",
    "low_min_effort_count",
    "near_horizon_count",
    "no_post_extirpation_survey_count",
)


class GroupSignal(TypedDict):
    group: str
    false_negative_count: int


@dataclass(frozen=True, slots=True)
class FalseNegativeMechanismAuditConfig:
    """Configuration for the Goal 012 false-negative mechanism audit."""

    evaluation_dir: str = str(DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR)
    reconstruction_dir: str = str(DEFAULT_RECONSTRUCTION_DIR)
    observation_dir: str = str(DEFAULT_OBSERVATION_DIR)
    mismatch_audit_dir: str = str(DEFAULT_FALSE_NEGATIVE_MISMATCH_AUDIT_DIR)
    audit_name: str = FALSE_NEGATIVE_AUDIT_NAME
    min_final_absence_run: int = 2
    late_horizon_gap_max: float = 8.0
    sparse_visit_count_max: int = 12
    sparse_survey_time_count_max: int = 6
    sparse_detection_count_max: int = 2
    low_mean_effort_max: float = 0.9
    low_min_effort_max: float = 0.65

    def to_dict(self) -> dict[str, Any]:
        return {
            **audit_labels(),
            "audit_name": self.audit_name,
            "evaluation_dir": self.evaluation_dir,
            "reconstruction_dir": self.reconstruction_dir,
            "observation_dir": self.observation_dir,
            "mismatch_audit_dir": self.mismatch_audit_dir,
            "mechanism_priority": list(MECHANISM_PRIORITY),
            "thresholds": {
                "min_final_absence_run": self.min_final_absence_run,
                "late_horizon_gap_max": self.late_horizon_gap_max,
                "sparse_visit_count_max": self.sparse_visit_count_max,
                "sparse_survey_time_count_max": self.sparse_survey_time_count_max,
                "sparse_detection_count_max": self.sparse_detection_count_max,
                "low_mean_effort_max": self.low_mean_effort_max,
                "low_min_effort_max": self.low_min_effort_max,
            },
            "required_inputs": {
                "response_screen_evaluation": list(EVALUATION_REQUIRED_FILES),
                "extirpation_reconstruction": list(RECONSTRUCTION_REQUIRED_FILES),
                "observations": list(OBSERVATION_REQUIRED_FILES),
                "compatibility_mismatch_audit": list(MISMATCH_AUDIT_REQUIRED_FILES),
            },
            "output_files": list(FALSE_NEGATIVE_AUDIT_OUTPUT_FILES),
            "interpretation": {
                "classification": "synthetic_evaluation_mechanism_audit",
                "notes": [
                    "This audit explains emitted synthetic false negatives.",
                    "It does not change reconstruction or observation logic.",
                    "It is not formal inference.",
                ],
            },
        }


@dataclass(frozen=True, slots=True)
class LoadedFalseNegativeMechanismAuditInputs:
    evaluation_dir: Path
    reconstruction_dir: Path
    observation_dir: Path
    mismatch_audit_dir: Path
    evaluation_summary: dict[str, Any]
    group_evaluation_rows: tuple[dict[str, str], ...]
    site_evaluation_rows: tuple[dict[str, str], ...]
    evaluation_verification: dict[str, Any]
    reconstruction_rows: tuple[dict[str, str], ...]
    time_detection_rows: tuple[dict[str, str], ...]
    reconstruction_verification: dict[str, Any]
    visit_rows: tuple[dict[str, str], ...]
    observation_rows: tuple[dict[str, str], ...]
    truth_rows: tuple[dict[str, str], ...]
    truth_reference: dict[str, Any]
    mismatch_bridge_summary: dict[str, Any]
    mismatch_recommendation: dict[str, Any]
    mismatch_verification: dict[str, Any]


@dataclass(frozen=True, slots=True)
class FalseNegativeSiteAuditRow:
    site_id: str
    cell_id: int
    row: int
    col: int
    region: str
    front_band: str
    primary_mechanism: str
    secondary_flags: tuple[str, ...]
    true_extirpation_time: float
    observed_extirpation_time: float | None
    reconstruction_status: str
    visit_count: int
    survey_time_count: int
    detection_count: int
    first_detection_time: int | None
    last_detection_time: int | None
    final_absence_start_time: int | None
    final_absence_survey_time_count: int
    first_survey_time: int | None
    last_survey_time: int | None
    first_post_extirpation_survey_time: int | None
    post_extirpation_survey_time_count: int
    post_extirpation_detection_count: int
    post_extirpation_detection_time_count: int
    mean_effort: float
    min_effort: float
    max_effort: float
    post_extirpation_mean_effort: float | None
    last_detection_minus_true_extirpation: float | None
    first_post_survey_minus_true_extirpation: float | None
    last_survey_minus_true_extirpation: float | None

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.site_id,
            str(self.cell_id),
            str(self.row),
            str(self.col),
            self.region,
            self.front_band,
            self.primary_mechanism,
            ";".join(self.secondary_flags),
            stringify_float(self.true_extirpation_time),
            stringify_optional_float(self.observed_extirpation_time),
            self.reconstruction_status,
            str(self.visit_count),
            str(self.survey_time_count),
            str(self.detection_count),
            stringify_optional_int(self.first_detection_time),
            stringify_optional_int(self.last_detection_time),
            stringify_optional_int(self.final_absence_start_time),
            str(self.final_absence_survey_time_count),
            stringify_optional_int(self.first_survey_time),
            stringify_optional_int(self.last_survey_time),
            stringify_optional_int(self.first_post_extirpation_survey_time),
            str(self.post_extirpation_survey_time_count),
            str(self.post_extirpation_detection_count),
            str(self.post_extirpation_detection_time_count),
            stringify_float(self.mean_effort),
            stringify_float(self.min_effort),
            stringify_float(self.max_effort),
            stringify_optional_float(self.post_extirpation_mean_effort),
            stringify_optional_float(self.last_detection_minus_true_extirpation),
            stringify_optional_float(self.first_post_survey_minus_true_extirpation),
            stringify_optional_float(self.last_survey_minus_true_extirpation),
        )


@dataclass(frozen=True, slots=True)
class MechanismSummaryRow:
    primary_mechanism: str
    false_negative_count: int
    false_negative_fraction: float
    mean_post_extirpation_survey_time_count: float
    mean_post_extirpation_detection_count: float
    mean_last_survey_minus_true_extirpation: float | None

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.primary_mechanism,
            str(self.false_negative_count),
            stringify_float(self.false_negative_fraction),
            stringify_float(self.mean_post_extirpation_survey_time_count),
            stringify_float(self.mean_post_extirpation_detection_count),
            stringify_optional_float(self.mean_last_survey_minus_true_extirpation),
        )


@dataclass(frozen=True, slots=True)
class GroupMechanismSummaryRow:
    group_type: str
    group: str
    primary_mechanism: str
    false_negative_count: int
    group_false_negative_count: int
    group_share: float
    total_false_negative_share: float

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.group_type,
            self.group,
            self.primary_mechanism,
            str(self.false_negative_count),
            str(self.group_false_negative_count),
            stringify_float(self.group_share),
            stringify_float(self.total_false_negative_share),
        )


@dataclass(frozen=True, slots=True)
class ObservationTimingSummaryRow:
    summary_type: str
    label: str
    false_negative_count: int
    mean_post_extirpation_survey_time_count: float | None
    median_post_extirpation_survey_time_count: float | None
    mean_post_extirpation_detection_count: float | None
    mean_true_extirpation_time: float | None
    mean_last_survey_minus_true_extirpation: float | None
    mean_last_detection_minus_true_extirpation: float | None
    mean_first_post_survey_minus_true_extirpation: float | None
    mean_effort: float | None
    mean_min_effort: float | None
    mean_max_effort: float | None
    mean_post_extirpation_mean_effort: float | None
    low_mean_effort_count: int
    low_min_effort_count: int
    near_horizon_count: int
    no_post_extirpation_survey_count: int

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.summary_type,
            self.label,
            str(self.false_negative_count),
            stringify_optional_float(self.mean_post_extirpation_survey_time_count),
            stringify_optional_float(self.median_post_extirpation_survey_time_count),
            stringify_optional_float(self.mean_post_extirpation_detection_count),
            stringify_optional_float(self.mean_true_extirpation_time),
            stringify_optional_float(self.mean_last_survey_minus_true_extirpation),
            stringify_optional_float(self.mean_last_detection_minus_true_extirpation),
            stringify_optional_float(self.mean_first_post_survey_minus_true_extirpation),
            stringify_optional_float(self.mean_effort),
            stringify_optional_float(self.mean_min_effort),
            stringify_optional_float(self.mean_max_effort),
            stringify_optional_float(self.mean_post_extirpation_mean_effort),
            str(self.low_mean_effort_count),
            str(self.low_min_effort_count),
            str(self.near_horizon_count),
            str(self.no_post_extirpation_survey_count),
        )


@dataclass(frozen=True, slots=True)
class FalseNegativeMechanismAuditCheck:
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
class SynthSmallFalseNegativeMechanismAuditResult:
    config: FalseNegativeMechanismAuditConfig
    inputs: LoadedFalseNegativeMechanismAuditInputs
    site_rows: tuple[FalseNegativeSiteAuditRow, ...]
    mechanism_rows: tuple[MechanismSummaryRow, ...]
    group_rows: tuple[GroupMechanismSummaryRow, ...]
    timing_rows: tuple[ObservationTimingSummaryRow, ...]
    recommendation: dict[str, Any]
    verification_checks: tuple[FalseNegativeMechanismAuditCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    @property
    def false_negative_count(self) -> int:
        return len(self.site_rows)

    def config_payload(self) -> dict[str, Any]:
        return {
            **self.config.to_dict(),
            "false_negative_count": self.false_negative_count,
            "source_verifications": source_verifications(self.inputs),
        }

    def verification_payload(self) -> dict[str, Any]:
        return {
            **audit_labels(),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
        }

    def write_artifacts(
        self,
        output_dir: str | PathLike[str] = DEFAULT_FALSE_NEGATIVE_AUDIT_OUTPUT_DIR,
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "false_negative_audit_config.json"
        site_path = target_dir / "false_negative_site_audit.csv"
        mechanism_path = target_dir / "mechanism_summary.csv"
        group_path = target_dir / "group_mechanism_summary.csv"
        timing_path = target_dir / "observation_timing_summary.csv"
        recommendation_path = target_dir / "recommendation.json"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(dumps(self.config_payload(), indent=2) + "\n", encoding="utf-8")
        write_rows(
            FALSE_NEGATIVE_SITE_COLUMNS,
            (row.to_csv_row() for row in self.site_rows),
            site_path,
        )
        write_rows(
            MECHANISM_SUMMARY_COLUMNS,
            (row.to_csv_row() for row in self.mechanism_rows),
            mechanism_path,
        )
        write_rows(
            GROUP_MECHANISM_SUMMARY_COLUMNS,
            (row.to_csv_row() for row in self.group_rows),
            group_path,
        )
        write_rows(
            OBSERVATION_TIMING_SUMMARY_COLUMNS,
            (row.to_csv_row() for row in self.timing_rows),
            timing_path,
        )
        recommendation_path.write_text(
            dumps(self.recommendation, indent=2) + "\n",
            encoding="utf-8",
        )
        verification_path.write_text(
            dumps(self.verification_payload(), indent=2) + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_false_negative_audit_report(self), encoding="utf-8")
        return (
            config_path,
            site_path,
            mechanism_path,
            group_path,
            timing_path,
            recommendation_path,
            verification_path,
            report_path,
        )


def build_synth_small_false_negative_mechanism_audit(
    *,
    evaluation_dir: str | PathLike[str] = DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    reconstruction_dir: str | PathLike[str] = DEFAULT_RECONSTRUCTION_DIR,
    observation_dir: str | PathLike[str] = DEFAULT_OBSERVATION_DIR,
    mismatch_audit_dir: str | PathLike[str] = DEFAULT_FALSE_NEGATIVE_MISMATCH_AUDIT_DIR,
    config: FalseNegativeMechanismAuditConfig | None = None,
) -> SynthSmallFalseNegativeMechanismAuditResult:
    audit_config = config or FalseNegativeMechanismAuditConfig(
        evaluation_dir=str(evaluation_dir),
        reconstruction_dir=str(reconstruction_dir),
        observation_dir=str(observation_dir),
        mismatch_audit_dir=str(mismatch_audit_dir),
    )
    inputs = load_false_negative_mechanism_audit_inputs(
        evaluation_dir=audit_config.evaluation_dir,
        reconstruction_dir=audit_config.reconstruction_dir,
        observation_dir=audit_config.observation_dir,
        mismatch_audit_dir=audit_config.mismatch_audit_dir,
    )
    site_rows = build_false_negative_site_rows(inputs, audit_config)
    mechanism_rows = build_mechanism_summary_rows(site_rows)
    group_rows = build_group_mechanism_summary_rows(site_rows)
    timing_rows = build_observation_timing_summary_rows(site_rows, audit_config)
    recommendation = build_false_negative_recommendation(
        site_rows=site_rows,
        mechanism_rows=mechanism_rows,
        group_rows=group_rows,
        inputs=inputs,
    )
    checks = verify_false_negative_audit_result(
        inputs=inputs,
        site_rows=site_rows,
        mechanism_rows=mechanism_rows,
        group_rows=group_rows,
        timing_rows=timing_rows,
        recommendation=recommendation,
    )
    return SynthSmallFalseNegativeMechanismAuditResult(
        config=audit_config,
        inputs=inputs,
        site_rows=site_rows,
        mechanism_rows=mechanism_rows,
        group_rows=group_rows,
        timing_rows=timing_rows,
        recommendation=recommendation,
        verification_checks=checks,
    )


def load_false_negative_mechanism_audit_inputs(
    *,
    evaluation_dir: str | PathLike[str],
    reconstruction_dir: str | PathLike[str],
    observation_dir: str | PathLike[str],
    mismatch_audit_dir: str | PathLike[str],
) -> LoadedFalseNegativeMechanismAuditInputs:
    eval_dir = Path(evaluation_dir)
    recon_dir = Path(reconstruction_dir)
    obs_dir = Path(observation_dir)
    mismatch_dir = Path(mismatch_audit_dir)
    assert_required_files(eval_dir, EVALUATION_REQUIRED_FILES, "response-screen evaluation")
    assert_required_files(recon_dir, RECONSTRUCTION_REQUIRED_FILES, "reconstruction")
    assert_required_files(obs_dir, OBSERVATION_REQUIRED_FILES, "observations")
    assert_required_files(mismatch_dir, MISMATCH_AUDIT_REQUIRED_FILES, "mismatch audit")
    return LoadedFalseNegativeMechanismAuditInputs(
        evaluation_dir=eval_dir,
        reconstruction_dir=recon_dir,
        observation_dir=obs_dir,
        mismatch_audit_dir=mismatch_dir,
        evaluation_summary=read_json(eval_dir / "screen_evaluation_summary.json"),
        group_evaluation_rows=read_csv_rows(eval_dir / "group_evaluation_summary.csv"),
        site_evaluation_rows=read_csv_rows(eval_dir / "site_evaluation_audit.csv"),
        evaluation_verification=read_json(eval_dir / "verification.json"),
        reconstruction_rows=read_csv_rows(recon_dir / "site_reconstruction.csv"),
        time_detection_rows=read_csv_rows(recon_dir / "time_detection_summary.csv"),
        reconstruction_verification=read_json(recon_dir / "verification.json"),
        visit_rows=read_csv_rows(obs_dir / "visits.csv"),
        observation_rows=read_csv_rows(obs_dir / "observations.csv"),
        truth_rows=read_csv_rows(obs_dir / "evaluation_truth.csv"),
        truth_reference=read_json(obs_dir / "truth_reference.json"),
        mismatch_bridge_summary=read_json(mismatch_dir / "evaluation_bridge_summary.json"),
        mismatch_recommendation=read_json(mismatch_dir / "recommendation.json"),
        mismatch_verification=read_json(mismatch_dir / "verification.json"),
    )


def build_false_negative_site_rows(
    inputs: LoadedFalseNegativeMechanismAuditInputs,
    config: FalseNegativeMechanismAuditConfig,
) -> tuple[FalseNegativeSiteAuditRow, ...]:
    reconstruction_by_site = {row["site_id"]: row for row in inputs.reconstruction_rows}
    truth_by_site = {row["site_id"]: row for row in inputs.truth_rows}
    observation_rows_by_site: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inputs.observation_rows:
        observation_rows_by_site[row["site_id"]].append(row)

    output: list[FalseNegativeSiteAuditRow] = []
    false_negative_rows = [
        row for row in inputs.site_evaluation_rows if row["audit_classification"] == "fn"
    ]
    for evaluation_row in false_negative_rows:
        site_id = evaluation_row["site_id"]
        reconstruction_row = reconstruction_by_site[site_id]
        truth_row = truth_by_site[site_id]
        observation_rows = tuple(observation_rows_by_site[site_id])
        output.append(
            build_false_negative_site_row(
                evaluation_row=evaluation_row,
                reconstruction_row=reconstruction_row,
                truth_row=truth_row,
                observation_rows=observation_rows,
                config=config,
            )
        )
    return tuple(output)


def build_false_negative_site_row(
    *,
    evaluation_row: dict[str, str],
    reconstruction_row: dict[str, str],
    truth_row: dict[str, str],
    observation_rows: tuple[dict[str, str], ...],
    config: FalseNegativeMechanismAuditConfig,
) -> FalseNegativeSiteAuditRow:
    true_extirpation_time = parse_required_float(truth_row["true_extirpation"])
    survey_times = sorted({parse_int(row["time_index"]) for row in observation_rows})
    first_survey_time = survey_times[0] if survey_times else None
    last_survey_time = survey_times[-1] if survey_times else None
    first_detection_time = parse_optional_int(reconstruction_row["first_detection_time"])
    last_detection_time = parse_optional_int(reconstruction_row["last_detection_time"])
    effort_values = [parse_required_float(row["effort"]) for row in observation_rows]
    if not effort_values:
        raise ValueError(f"expected effort rows for {evaluation_row['site_id']}")
    post_survey_times = [time for time in survey_times if time > true_extirpation_time]
    post_effort_values = [
        parse_required_float(row["effort"])
        for row in observation_rows
        if parse_int(row["time_index"]) > true_extirpation_time
    ]
    post_detection_rows = [
        row
        for row in observation_rows
        if parse_int(row["time_index"]) > true_extirpation_time and parse_bool01(row["detected"])
    ]
    post_detection_times = {parse_int(row["time_index"]) for row in post_detection_rows}
    first_post_survey_time = min(post_survey_times) if post_survey_times else None
    last_detection_lag = (
        None if last_detection_time is None else last_detection_time - true_extirpation_time
    )
    first_post_survey_lag = (
        None if first_post_survey_time is None else first_post_survey_time - true_extirpation_time
    )
    last_survey_lag = None if last_survey_time is None else last_survey_time - true_extirpation_time
    final_absence_count = parse_int(reconstruction_row["final_absence_survey_time_count"])
    visit_count = parse_int(reconstruction_row["visit_count"])
    survey_time_count = parse_int(reconstruction_row["survey_time_count"])
    detection_count = parse_int(reconstruction_row["detection_count"])
    mean_effort = mean_required(effort_values)
    min_effort = min(effort_values)
    max_effort = max(effort_values)
    post_extirpation_mean_effort = mean_optional(post_effort_values)
    primary_mechanism = classify_primary_mechanism(
        region=evaluation_row["region"],
        front_band=evaluation_row["front_band"],
        post_extirpation_survey_time_count=len(post_survey_times),
        post_extirpation_detection_count=len(post_detection_rows),
        final_absence_survey_time_count=final_absence_count,
        visit_count=visit_count,
        survey_time_count=survey_time_count,
        detection_count=detection_count,
        mean_effort=mean_effort,
        min_effort=min_effort,
        last_survey_minus_true_extirpation=last_survey_lag,
        config=config,
    )
    secondary_flags = classify_secondary_flags(
        region=evaluation_row["region"],
        front_band=evaluation_row["front_band"],
        post_extirpation_survey_time_count=len(post_survey_times),
        post_extirpation_detection_count=len(post_detection_rows),
        visit_count=visit_count,
        survey_time_count=survey_time_count,
        detection_count=detection_count,
        mean_effort=mean_effort,
        min_effort=min_effort,
        last_survey_minus_true_extirpation=last_survey_lag,
        config=config,
    )
    return FalseNegativeSiteAuditRow(
        site_id=evaluation_row["site_id"],
        cell_id=parse_int(evaluation_row["cell_id"]),
        row=parse_int(evaluation_row["row"]),
        col=parse_int(evaluation_row["col"]),
        region=evaluation_row["region"],
        front_band=evaluation_row["front_band"],
        primary_mechanism=primary_mechanism,
        secondary_flags=secondary_flags,
        true_extirpation_time=true_extirpation_time,
        observed_extirpation_time=parse_optional_float(
            reconstruction_row["observed_extirpation_time"]
        ),
        reconstruction_status=reconstruction_row["reconstruction_status"],
        visit_count=visit_count,
        survey_time_count=survey_time_count,
        detection_count=detection_count,
        first_detection_time=first_detection_time,
        last_detection_time=last_detection_time,
        final_absence_start_time=parse_optional_int(reconstruction_row["final_absence_start_time"]),
        final_absence_survey_time_count=final_absence_count,
        first_survey_time=first_survey_time,
        last_survey_time=last_survey_time,
        first_post_extirpation_survey_time=first_post_survey_time,
        post_extirpation_survey_time_count=len(post_survey_times),
        post_extirpation_detection_count=len(post_detection_rows),
        post_extirpation_detection_time_count=len(post_detection_times),
        mean_effort=mean_effort,
        min_effort=min_effort,
        max_effort=max_effort,
        post_extirpation_mean_effort=post_extirpation_mean_effort,
        last_detection_minus_true_extirpation=last_detection_lag,
        first_post_survey_minus_true_extirpation=first_post_survey_lag,
        last_survey_minus_true_extirpation=last_survey_lag,
    )


def classify_primary_mechanism(
    *,
    region: str,
    front_band: str,
    post_extirpation_survey_time_count: int,
    post_extirpation_detection_count: int,
    final_absence_survey_time_count: int,
    visit_count: int,
    survey_time_count: int,
    detection_count: int,
    mean_effort: float,
    min_effort: float,
    last_survey_minus_true_extirpation: float | None,
    config: FalseNegativeMechanismAuditConfig,
) -> str:
    if post_extirpation_survey_time_count == 0:
        return "no_post_extirpation_surveys"
    if (
        post_extirpation_survey_time_count < config.min_final_absence_run
        and last_survey_minus_true_extirpation is not None
        and last_survey_minus_true_extirpation <= config.late_horizon_gap_max
    ):
        return "late_extirpation_near_survey_horizon"
    if post_extirpation_detection_count > 0:
        return "post_extirpation_detection_blocks_absence"
    if (
        post_extirpation_survey_time_count < config.min_final_absence_run
        or final_absence_survey_time_count < config.min_final_absence_run
    ):
        return "insufficient_post_extirpation_survey_history"
    if is_sparse_or_low_effort(
        visit_count=visit_count,
        survey_time_count=survey_time_count,
        detection_count=detection_count,
        mean_effort=mean_effort,
        min_effort=min_effort,
        config=config,
    ):
        return "sparse_or_low_effort_observation"
    if is_weak_east_or_edge_signal(region=region, front_band=front_band):
        return "weak_east_or_edge_signal"
    return "unclassified_false_negative"


def classify_secondary_flags(
    *,
    region: str,
    front_band: str,
    post_extirpation_survey_time_count: int,
    post_extirpation_detection_count: int,
    visit_count: int,
    survey_time_count: int,
    detection_count: int,
    mean_effort: float,
    min_effort: float,
    last_survey_minus_true_extirpation: float | None,
    config: FalseNegativeMechanismAuditConfig,
) -> tuple[str, ...]:
    flags: list[str] = []
    if is_weak_east_or_edge_signal(region=region, front_band=front_band):
        flags.append("weak_east_or_edge_signal")
    if is_sparse_or_low_effort(
        visit_count=visit_count,
        survey_time_count=survey_time_count,
        detection_count=detection_count,
        mean_effort=mean_effort,
        min_effort=min_effort,
        config=config,
    ):
        flags.append("sparse_or_low_effort_observation")
    if post_extirpation_detection_count > 0:
        flags.append("post_extirpation_detection_seen")
    if post_extirpation_survey_time_count < config.min_final_absence_run:
        flags.append("limited_post_extirpation_surveys")
    if (
        last_survey_minus_true_extirpation is not None
        and last_survey_minus_true_extirpation <= config.late_horizon_gap_max
    ):
        flags.append("near_survey_horizon")
    return tuple(flags)


def is_sparse_or_low_effort(
    *,
    visit_count: int,
    survey_time_count: int,
    detection_count: int,
    mean_effort: float,
    min_effort: float,
    config: FalseNegativeMechanismAuditConfig,
) -> bool:
    return (
        visit_count <= config.sparse_visit_count_max
        or survey_time_count <= config.sparse_survey_time_count_max
        or detection_count <= config.sparse_detection_count_max
        or mean_effort <= config.low_mean_effort_max
        or min_effort <= config.low_min_effort_max
    )


def is_weak_east_or_edge_signal(*, region: str, front_band: str) -> bool:
    return region == "east" or front_band == "east_band"


def build_mechanism_summary_rows(
    site_rows: tuple[FalseNegativeSiteAuditRow, ...],
) -> tuple[MechanismSummaryRow, ...]:
    total = len(site_rows)
    grouped: dict[str, list[FalseNegativeSiteAuditRow]] = defaultdict(list)
    for row in site_rows:
        grouped[row.primary_mechanism].append(row)
    rows: list[MechanismSummaryRow] = []
    for mechanism in MECHANISM_PRIORITY:
        members = grouped.get(mechanism, [])
        if not members:
            continue
        rows.append(
            MechanismSummaryRow(
                primary_mechanism=mechanism,
                false_negative_count=len(members),
                false_negative_fraction=len(members) / total if total else 0.0,
                mean_post_extirpation_survey_time_count=mean_required(
                    [member.post_extirpation_survey_time_count for member in members]
                ),
                mean_post_extirpation_detection_count=mean_required(
                    [member.post_extirpation_detection_count for member in members]
                ),
                mean_last_survey_minus_true_extirpation=mean_optional(
                    [member.last_survey_minus_true_extirpation for member in members]
                ),
            )
        )
    return tuple(rows)


def build_group_mechanism_summary_rows(
    site_rows: tuple[FalseNegativeSiteAuditRow, ...],
) -> tuple[GroupMechanismSummaryRow, ...]:
    total = len(site_rows)
    rows: list[GroupMechanismSummaryRow] = []
    for group_type in ("region", "front_band"):
        group_members: dict[str, list[FalseNegativeSiteAuditRow]] = defaultdict(list)
        for row in site_rows:
            group = row.region if group_type == "region" else row.front_band
            group_members[group].append(row)
        for group in sorted(group_members):
            members = group_members[group]
            mechanism_counts = Counter(member.primary_mechanism for member in members)
            for mechanism in MECHANISM_PRIORITY:
                count = mechanism_counts.get(mechanism, 0)
                if count == 0:
                    continue
                rows.append(
                    GroupMechanismSummaryRow(
                        group_type=group_type,
                        group=group,
                        primary_mechanism=mechanism,
                        false_negative_count=count,
                        group_false_negative_count=len(members),
                        group_share=count / len(members),
                        total_false_negative_share=count / total if total else 0.0,
                    )
                )
    return tuple(rows)


def build_observation_timing_summary_rows(
    site_rows: tuple[FalseNegativeSiteAuditRow, ...],
    config: FalseNegativeMechanismAuditConfig,
) -> tuple[ObservationTimingSummaryRow, ...]:
    rows: list[ObservationTimingSummaryRow] = [
        timing_summary_row("overall", "all", site_rows, config)
    ]
    for mechanism in MECHANISM_PRIORITY:
        members = tuple(row for row in site_rows if row.primary_mechanism == mechanism)
        if members:
            rows.append(timing_summary_row("primary_mechanism", mechanism, members, config))
    for region in sorted({row.region for row in site_rows}):
        members = tuple(row for row in site_rows if row.region == region)
        rows.append(timing_summary_row("region", region, members, config))
    for front_band in sorted({row.front_band for row in site_rows}):
        members = tuple(row for row in site_rows if row.front_band == front_band)
        rows.append(timing_summary_row("front_band", front_band, members, config))
    return tuple(rows)


def timing_summary_row(
    summary_type: str,
    label: str,
    rows: tuple[FalseNegativeSiteAuditRow, ...],
    config: FalseNegativeMechanismAuditConfig,
) -> ObservationTimingSummaryRow:
    post_survey_counts = [row.post_extirpation_survey_time_count for row in rows]
    return ObservationTimingSummaryRow(
        summary_type=summary_type,
        label=label,
        false_negative_count=len(rows),
        mean_post_extirpation_survey_time_count=mean_optional(post_survey_counts),
        median_post_extirpation_survey_time_count=median_optional(post_survey_counts),
        mean_post_extirpation_detection_count=mean_optional(
            [row.post_extirpation_detection_count for row in rows]
        ),
        mean_true_extirpation_time=mean_optional([row.true_extirpation_time for row in rows]),
        mean_last_survey_minus_true_extirpation=mean_optional(
            [row.last_survey_minus_true_extirpation for row in rows]
        ),
        mean_last_detection_minus_true_extirpation=mean_optional(
            [row.last_detection_minus_true_extirpation for row in rows]
        ),
        mean_first_post_survey_minus_true_extirpation=mean_optional(
            [row.first_post_survey_minus_true_extirpation for row in rows]
        ),
        mean_effort=mean_optional([row.mean_effort for row in rows]),
        mean_min_effort=mean_optional([row.min_effort for row in rows]),
        mean_max_effort=mean_optional([row.max_effort for row in rows]),
        mean_post_extirpation_mean_effort=mean_optional(
            [row.post_extirpation_mean_effort for row in rows]
        ),
        low_mean_effort_count=sum(
            1 for row in rows if row.mean_effort <= config.low_mean_effort_max
        ),
        low_min_effort_count=sum(1 for row in rows if row.min_effort <= config.low_min_effort_max),
        near_horizon_count=sum(
            1
            for row in rows
            if row.last_survey_minus_true_extirpation is not None
            and row.last_survey_minus_true_extirpation <= config.late_horizon_gap_max
        ),
        no_post_extirpation_survey_count=sum(
            1 for row in rows if row.post_extirpation_survey_time_count == 0
        ),
    )


def build_false_negative_recommendation(
    *,
    site_rows: tuple[FalseNegativeSiteAuditRow, ...],
    mechanism_rows: tuple[MechanismSummaryRow, ...],
    group_rows: tuple[GroupMechanismSummaryRow, ...],
    inputs: LoadedFalseNegativeMechanismAuditInputs,
) -> dict[str, Any]:
    mechanism_counts = {row.primary_mechanism: row.false_negative_count for row in mechanism_rows}
    dominant_primary_mechanisms = [
        mechanism
        for mechanism, _count in sorted(
            mechanism_counts.items(),
            key=lambda item: (-item[1], MECHANISM_PRIORITY.index(item[0])),
        )
    ]
    false_negative_count = len(site_rows)
    observation_gap_count = mechanism_counts.get(
        "no_post_extirpation_surveys", 0
    ) + mechanism_counts.get(
        "late_extirpation_near_survey_horizon",
        0,
    )
    post_detection_count = mechanism_counts.get("post_extirpation_detection_blocks_absence", 0)
    strongest_region = strongest_group_signal(group_rows, "region")
    strongest_front_band = strongest_group_signal(group_rows, "front_band")
    source_passed = all(source_verifications(inputs).values())
    bridge_count = int_payload(inputs.mismatch_bridge_summary.get("false_negative_count"), 0)
    recommendation_class = choose_recommendation_class(
        source_passed=source_passed,
        false_negative_count=false_negative_count,
        bridge_count=bridge_count,
        observation_gap_count=observation_gap_count,
        post_detection_count=post_detection_count,
        strongest_region_count=strongest_region["false_negative_count"],
    )
    return {
        **audit_labels(),
        "recommendation_class": recommendation_class,
        "false_negative_count": false_negative_count,
        "goal011_false_negative_count": bridge_count,
        "dominant_primary_mechanisms": dominant_primary_mechanisms,
        "mechanism_counts": mechanism_counts,
        "observation_gap_count": observation_gap_count,
        "post_extirpation_detection_count": post_detection_count,
        "strongest_region_signal": strongest_region,
        "strongest_front_band_signal": strongest_front_band,
        "rationale": recommendation_rationale(
            recommendation_class,
            observation_gap_count=observation_gap_count,
            false_negative_count=false_negative_count,
            strongest_region=strongest_region,
        ),
    }


def choose_recommendation_class(
    *,
    source_passed: bool,
    false_negative_count: int,
    bridge_count: int,
    observation_gap_count: int,
    post_detection_count: int,
    strongest_region_count: int,
) -> str:
    if not source_passed or false_negative_count != bridge_count:
        return "screen_contract_bug_suspected"
    if false_negative_count and observation_gap_count / false_negative_count >= 0.5:
        return "diagnose_post_extirpation_observation_gap_before_rule_change"
    if false_negative_count and post_detection_count / false_negative_count >= 0.5:
        return "diagnose_post_extirpation_detection_persistence_before_rule_change"
    if false_negative_count and strongest_region_count / false_negative_count >= 0.5:
        return "review_group_specific_observation_support"
    return "ready_for_reconstruction_rule_review"


def strongest_group_signal(
    group_rows: tuple[GroupMechanismSummaryRow, ...],
    group_type: str,
) -> GroupSignal:
    totals: Counter[str] = Counter()
    for row in group_rows:
        if row.group_type == group_type:
            totals[row.group] += row.false_negative_count
    if not totals:
        return {"group": "", "false_negative_count": 0}
    group, count = max(totals.items(), key=lambda item: (item[1], item[0]))
    return {"group": group, "false_negative_count": count}


def recommendation_rationale(
    recommendation_class: str,
    *,
    observation_gap_count: int,
    false_negative_count: int,
    strongest_region: GroupSignal,
) -> list[str]:
    if recommendation_class == "diagnose_post_extirpation_observation_gap_before_rule_change":
        return [
            (
                f"No or late post-extirpation survey coverage explains "
                f"{observation_gap_count} of {false_negative_count} false negatives."
            ),
            (
                "The strongest region signal is "
                f"{strongest_region['group']} with "
                f"{strongest_region['false_negative_count']} false negatives."
            ),
            (
                "This recommendation does not change reconstruction rules, "
                "observation design, scoring, or inference logic."
            ),
        ]
    if recommendation_class == "diagnose_post_extirpation_detection_persistence_before_rule_change":
        return [
            "Post-extirpation detections dominate the false-negative mechanism audit.",
            (
                "This recommendation does not change reconstruction rules, "
                "observation design, scoring, or inference logic."
            ),
        ]
    if recommendation_class == "review_group_specific_observation_support":
        return [
            "A group-level signal dominates after timing mechanisms are not dominant.",
            (
                "This recommendation does not change reconstruction rules, "
                "observation design, scoring, or inference logic."
            ),
        ]
    if recommendation_class == "ready_for_reconstruction_rule_review":
        return [
            "No single observation-gap or detection-persistence mechanism dominates.",
            (
                "A later bounded goal may review reconstruction-rule design, "
                "but this audit does not change it."
            ),
        ]
    return [
        "A source verification or Goal 011 bridge count failed to reconcile.",
        (
            "This recommendation does not change reconstruction rules, "
            "observation design, scoring, or inference logic."
        ),
    ]


def verify_false_negative_audit_result(
    *,
    inputs: LoadedFalseNegativeMechanismAuditInputs,
    site_rows: tuple[FalseNegativeSiteAuditRow, ...],
    mechanism_rows: tuple[MechanismSummaryRow, ...],
    group_rows: tuple[GroupMechanismSummaryRow, ...],
    timing_rows: tuple[ObservationTimingSummaryRow, ...],
    recommendation: dict[str, Any],
) -> tuple[FalseNegativeMechanismAuditCheck, ...]:
    source_passed = source_verifications(inputs)
    expected_fn_count = expected_false_negative_count(inputs)
    bridge_count = int_payload(inputs.mismatch_bridge_summary.get("false_negative_count"), 0)
    site_ids = [row.site_id for row in site_rows]
    mechanism_total = sum(row.false_negative_count for row in mechanism_rows)
    group_totals_valid = group_totals_reconcile(group_rows, site_rows)
    overall_timing = next((row for row in timing_rows if row.summary_type == "overall"), None)
    return (
        FalseNegativeMechanismAuditCheck(
            name="source_verifications",
            passed=all(source_passed.values()),
            message="all prerequisite verification payloads passed",
            details=source_passed,
        ),
        FalseNegativeMechanismAuditCheck(
            name="false_negative_count",
            passed=len(site_rows) == expected_fn_count == bridge_count,
            message="site rows match response-screen and Goal 011 false-negative counts",
            details={
                "site_row_count": len(site_rows),
                "evaluation_false_negative_count": expected_fn_count,
                "goal011_false_negative_count": bridge_count,
            },
        ),
        FalseNegativeMechanismAuditCheck(
            name="site_uniqueness",
            passed=len(site_ids) == len(set(site_ids)) and bool(site_ids),
            message="every false-negative site appears exactly once",
            details={"site_count": len(site_ids), "unique_site_count": len(set(site_ids))},
        ),
        FalseNegativeMechanismAuditCheck(
            name="primary_mechanisms",
            passed=all(row.primary_mechanism in MECHANISM_PRIORITY for row in site_rows)
            and mechanism_total == len(site_rows),
            message="every false negative has one primary mechanism and summaries reconcile",
            details={
                "mechanism_total": mechanism_total,
                "site_row_count": len(site_rows),
            },
        ),
        FalseNegativeMechanismAuditCheck(
            name="group_summaries",
            passed=group_totals_valid,
            message="group mechanism summaries reconcile to site rows",
            details={"group_summary_row_count": len(group_rows)},
        ),
        FalseNegativeMechanismAuditCheck(
            name="timing_summary",
            passed=overall_timing is not None
            and overall_timing.false_negative_count == len(site_rows),
            message="observation timing summary includes a reconciled overall row",
            details={
                "overall_count": None
                if overall_timing is None
                else overall_timing.false_negative_count,
                "site_row_count": len(site_rows),
            },
        ),
        FalseNegativeMechanismAuditCheck(
            name="recommendation",
            passed=recommendation["recommendation_class"]
            == "diagnose_post_extirpation_observation_gap_before_rule_change",
            message="recommendation remains diagnostic before reconstruction changes",
            details={"recommendation_class": recommendation["recommendation_class"]},
        ),
    )


def group_totals_reconcile(
    group_rows: tuple[GroupMechanismSummaryRow, ...],
    site_rows: tuple[FalseNegativeSiteAuditRow, ...],
) -> bool:
    for group_type in ("region", "front_band"):
        expected: Counter[str] = Counter()
        observed: Counter[str] = Counter()
        for site_row in site_rows:
            expected[site_row.region if group_type == "region" else site_row.front_band] += 1
        for group_row in group_rows:
            if group_row.group_type == group_type:
                observed[group_row.group] += group_row.false_negative_count
        if expected != observed:
            return False
    return True


def expected_false_negative_count(inputs: LoadedFalseNegativeMechanismAuditInputs) -> int:
    classification = dict_payload(inputs.evaluation_summary.get("classification"))
    if "false_negative_count" in classification:
        return int_payload(classification["false_negative_count"], 0)
    matrix = dict_payload(classification.get("confusion_matrix"))
    return int_payload(matrix.get("fn"), 0)


def source_verifications(inputs: LoadedFalseNegativeMechanismAuditInputs) -> dict[str, bool]:
    return {
        "response_screen_evaluation": bool(inputs.evaluation_verification.get("passed")),
        "extirpation_reconstruction": bool(inputs.reconstruction_verification.get("passed")),
        "compatibility_mismatch_audit": bool(inputs.mismatch_verification.get("passed")),
        "observation_inputs_present": bool(inputs.truth_reference),
    }


def render_false_negative_audit_report(
    result: SynthSmallFalseNegativeMechanismAuditResult,
) -> str:
    overall_timing = next(row for row in result.timing_rows if row.summary_type == "overall")
    lines = [
        "# Synth-Small False-Negative Mechanism Audit",
        "",
        "## Scope",
        "",
        (
            "This is a synthetic-only, evaluation-only, disk-first audit of "
            "response-screen false negatives. It does not change reconstruction "
            "rules, observation design, scoring, or inference logic."
        ),
        "",
        "## Summary",
        "",
        f"- False negatives audited: `{result.false_negative_count}`",
        f"- Recommendation: `{result.recommendation['recommendation_class']}`",
        "",
        "## Primary Mechanisms",
        "",
    ]
    for row in result.mechanism_rows:
        lines.append(
            "- "
            f"`{row.primary_mechanism}`: `{row.false_negative_count}` "
            f"({stringify_float(row.false_negative_fraction)})"
        )
    lines.extend(
        [
            "",
            "## Strongest Group Signals",
            "",
            "- "
            f"Region: `{result.recommendation['strongest_region_signal']['group']}` "
            f"(`{result.recommendation['strongest_region_signal']['false_negative_count']}`)",
            "- "
            f"Front band: `{result.recommendation['strongest_front_band_signal']['group']}` "
            f"(`{result.recommendation['strongest_front_band_signal']['false_negative_count']}`)",
            "",
            "## Effort Diagnostics",
            "",
            f"- Mean site effort: `{stringify_optional_float(overall_timing.mean_effort)}`",
            "- Mean site minimum effort: "
            f"`{stringify_optional_float(overall_timing.mean_min_effort)}`",
            f"- Low mean-effort sites: `{overall_timing.low_mean_effort_count}`",
            f"- Low minimum-effort sites: `{overall_timing.low_min_effort_count}`",
            "",
            "## Interpretation Limit",
            "",
            (
                "The audit identifies diagnostic mechanisms only. Any reconstruction "
                "rule, observation design, or inference change requires a later "
                "bounded goal."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def audit_labels() -> dict[str, bool]:
    return {
        "synthetic_only": True,
        "audit_only": True,
        "evaluation_only": True,
        "not_formal_inference": True,
        "no_reconstruction_change": True,
        "no_observation_design_change": True,
        "no_scoring_change": True,
    }


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
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    if not all(isinstance(key, str) for key in payload):
        raise ValueError(f"expected string JSON keys in {path}")
    return {key: value for key, value in payload.items()}


def write_rows(
    columns: tuple[str, ...],
    rows: Iterable[Sequence[str]],
    output_path: Path,
) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(columns)
        csv_writer.writerows(rows)


def parse_int(value: str) -> int:
    return int(value)


def parse_optional_int(value: str) -> int | None:
    if value == "":
        return None
    return int(value)


def parse_required_float(value: str) -> float:
    parsed = parse_optional_float(value)
    if parsed is None:
        raise ValueError("expected finite float")
    return parsed


def parse_optional_float(value: str) -> float | None:
    if value == "":
        return None
    parsed = float(value)
    return parsed if isfinite(parsed) else None


def parse_bool01(value: str) -> bool:
    if value == "1":
        return True
    if value == "0":
        return False
    raise ValueError(f"expected binary value 0/1, got {value!r}")


def stringify_optional_int(value: int | None) -> str:
    if value is None:
        return ""
    return str(value)


def stringify_optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return stringify_float(value)


def mean_required(values: Sequence[int | float]) -> float:
    if not values:
        raise ValueError("expected at least one value")
    return float(sum(values) / len(values))


def mean_optional(values: Sequence[int | float | None]) -> float | None:
    finite_values = [float(value) for value in values if value is not None]
    if not finite_values:
        return None
    return float(sum(finite_values) / len(finite_values))


def median_optional(values: Sequence[int | float | None]) -> float | None:
    finite_values = [float(value) for value in values if value is not None]
    if not finite_values:
        return None
    return float(median(finite_values))


def dict_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def int_payload(value: Any, fallback: int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value:
        return int(value)
    return fallback
