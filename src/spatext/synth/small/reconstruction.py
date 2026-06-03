"""Response-only extirpation reconstruction utilities for synth-small workflows."""

from __future__ import annotations

from collections import defaultdict
from csv import DictReader
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from json import dumps, loads
from os import PathLike
from pathlib import Path
from typing import Any

import numpy as np

from .observations import (
    FORBIDDEN_ANALYST_COLUMNS,
    LoadedSynthSmallObservationBundle,
    load_synth_small_observation_artifacts,
    parse_bool,
    parse_float,
    parse_int,
    parse_optional_float,
    stringify_bool,
    stringify_float,
    write_dataclass_csv,
)

DEFAULT_OBSERVATION_DIR = Path("artifacts/synth_small_observations")
DEFAULT_OUTPUT_DIR = Path("artifacts/synth_small_extirpation_reconstruction")
DEFAULT_MIN_FINAL_ABSENCE_RUN = 2

SITE_RECONSTRUCTION_COLUMNS = (
    "site_id",
    "cell_id",
    "row",
    "col",
    "region",
    "front_band",
    "visit_count",
    "survey_time_count",
    "detection_count",
    "first_detection_time",
    "last_detection_time",
    "final_absence_start_time",
    "final_absence_survey_time_count",
    "observed_extirpated_by_end",
    "observed_extirpation_time",
    "reconstruction_status",
)

TIME_DETECTION_SUMMARY_COLUMNS = (
    "time_index",
    "visit_count",
    "site_count",
    "observation_count",
    "detection_count",
    "detection_rate",
    "mean_observed_count",
    "mean_effort",
)

REQUIRED_OUTPUT_FILES = (
    "reconstruction_config.json",
    "site_reconstruction.csv",
    "time_detection_summary.csv",
    "verification.json",
    "evaluation_metrics.json",
    "report.md",
)

RECONSTRUCTION_STATUS_OBSERVED_EXTINCTION = "observed_extirpated_by_end"
RECONSTRUCTION_STATUS_NOT_EXTINCTION = "not_observed_extirpated_by_end"
RECONSTRUCTION_STATUS_INSUFFICIENT = "insufficient_history"
RECONSTRUCTION_STATUS_NO_SURVEY = "no_surveyed_times"
RECONSTRUCTION_STATUSES = (
    RECONSTRUCTION_STATUS_OBSERVED_EXTINCTION,
    RECONSTRUCTION_STATUS_NOT_EXTINCTION,
    RECONSTRUCTION_STATUS_INSUFFICIENT,
    RECONSTRUCTION_STATUS_NO_SURVEY,
)

EVALUATION_REQUIRED_KEYS = {
    "site_coverage",
    "reconstruction_status_counts",
    "confusion_matrix",
    "sensitivity",
    "specificity",
    "precision",
    "temporal_error",
    "bias_by_region",
    "bias_by_front_band",
    "interpretation",
    "limits",
}

RECONSTRUCTION_FORBIDDEN_COLUMNS = frozenset(
    FORBIDDEN_ANALYST_COLUMNS | frozenset({"predator_pressure"})
)


@dataclass(frozen=True, slots=True)
class ReconstructionConfig:
    """Runtime configuration for response-only reconstruction."""

    rule_name: str = "final-absence-run"
    min_final_absence_run: int = DEFAULT_MIN_FINAL_ABSENCE_RUN
    observation_artifact_dir: str = str(DEFAULT_OBSERVATION_DIR)

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_name": self.rule_name,
            "min_final_absence_run": self.min_final_absence_run,
            "observation_artifact_dir": self.observation_artifact_dir,
            "forbidden_output_columns": sorted(RECONSTRUCTION_FORBIDDEN_COLUMNS),
        }


@dataclass(frozen=True, slots=True)
class SiteReconstructionRow:
    site_id: str
    cell_id: int
    row: int
    col: int
    region: str
    front_band: str
    visit_count: int
    survey_time_count: int
    detection_count: int
    first_detection_time: int | None
    last_detection_time: int | None
    final_absence_start_time: int | None
    final_absence_survey_time_count: int
    observed_extirpated_by_end: bool
    observed_extirpation_time: int | None
    reconstruction_status: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.site_id,
            str(self.cell_id),
            str(self.row),
            str(self.col),
            self.region,
            self.front_band,
            str(self.visit_count),
            str(self.survey_time_count),
            str(self.detection_count),
            _optional_int_string(self.first_detection_time),
            _optional_int_string(self.last_detection_time),
            _optional_int_string(self.final_absence_start_time),
            str(self.final_absence_survey_time_count),
            stringify_bool(self.observed_extirpated_by_end),
            _optional_int_string(self.observed_extirpation_time),
            self.reconstruction_status,
        )


@dataclass(frozen=True, slots=True)
class TimeDetectionSummaryRow:
    time_index: int
    visit_count: int
    site_count: int
    observation_count: int
    detection_count: int
    detection_rate: float
    mean_observed_count: float
    mean_effort: float

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            str(self.time_index),
            str(self.visit_count),
            str(self.site_count),
            str(self.observation_count),
            str(self.detection_count),
            stringify_float(self.detection_rate),
            stringify_float(self.mean_observed_count),
            stringify_float(self.mean_effort),
        )


@dataclass(frozen=True, slots=True)
class ReconstructionVerificationCheck:
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
class SynthSmallExtirpationReconstructionResult:
    config: ReconstructionConfig
    observation_bundle_dir: Path
    site_rows: tuple[SiteReconstructionRow, ...]
    time_summary_rows: tuple[TimeDetectionSummaryRow, ...]
    verification_checks: tuple[ReconstructionVerificationCheck, ...]
    evaluation_metrics: dict[str, Any]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def verification_payload(self) -> dict[str, Any]:
        return {
            "artifact_dir": str(self.observation_bundle_dir),
            "output_dir": str(self.output_dir),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
            "site_count": len(self.site_rows),
            "time_row_count": len(self.time_summary_rows),
        }

    @property
    def output_dir(self) -> Path:
        return DEFAULT_OUTPUT_DIR

    def write_artifacts(self, output_dir: str | PathLike[str] | None = None) -> tuple[Path, ...]:
        target_dir = Path(output_dir) if output_dir is not None else self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        reconstruction_config_path = target_dir / "reconstruction_config.json"
        site_reconstruction_path = target_dir / "site_reconstruction.csv"
        time_summary_path = target_dir / "time_detection_summary.csv"
        verification_path = target_dir / "verification.json"
        evaluation_metrics_path = target_dir / "evaluation_metrics.json"
        report_path = target_dir / "report.md"

        reconstruction_config_path.write_text(
            dumps(
                {
                    "generated_at": datetime.now(tz=UTC).isoformat(),
                    "config": self.config.to_dict(),
                    "artifact_dir": str(self.observation_bundle_dir),
                    "site_count": len(self.site_rows),
                    "time_count": len(self.time_summary_rows),
                    "passed": self.passed,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        write_dataclass_csv(
            SITE_RECONSTRUCTION_COLUMNS,
            (row.to_csv_row() for row in self.site_rows),
            site_reconstruction_path,
        )
        write_dataclass_csv(
            TIME_DETECTION_SUMMARY_COLUMNS,
            (row.to_csv_row() for row in self.time_summary_rows),
            time_summary_path,
        )
        verification_path.write_text(
            dumps(self.verification_payload(), indent=2) + "\n",
            encoding="utf-8",
        )
        evaluation_metrics_path.write_text(
            dumps(self.evaluation_metrics, indent=2) + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_reconstruction_report(self), encoding="utf-8")
        return (
            reconstruction_config_path,
            site_reconstruction_path,
            time_summary_path,
            verification_path,
            evaluation_metrics_path,
            report_path,
        )


@dataclass(frozen=True, slots=True)
class LoadedReconstructionBundle:
    artifact_dir: Path
    reconstruction_config: dict[str, Any]
    site_rows: tuple[dict[str, str], ...]
    time_summary_rows: tuple[dict[str, str], ...]
    verification: dict[str, Any]
    evaluation_metrics: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ExtirpationReconstructionInspectionResult:
    artifact_dir: Path
    output_dir: Path
    verification_checks: tuple[ReconstructionVerificationCheck, ...]
    verification_path: Path
    report_path: Path

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)


def default_reconstruction_config() -> ReconstructionConfig:
    return ReconstructionConfig()


def build_synth_small_extirpation_reconstruction(
    artifact_dir: str | PathLike[str] = DEFAULT_OBSERVATION_DIR,
    *,
    config: ReconstructionConfig | None = None,
) -> SynthSmallExtirpationReconstructionResult:
    reconstruction_config = config or default_reconstruction_config()
    if reconstruction_config.min_final_absence_run < 1:
        raise ValueError("min_final_absence_run must be at least 1")

    obs_bundle = load_synth_small_observation_artifacts(artifact_dir)
    site_rows = build_site_reconstruction_rows(
        obs_bundle, reconstruction_config.min_final_absence_run
    )
    time_summary_rows = build_time_detection_summary_rows(obs_bundle)
    checks = verify_reconstruction_rows(site_rows, time_summary_rows, obs_bundle=obs_bundle)
    metrics = evaluate_against_hidden_truth(site_rows, obs_bundle.evaluation_truth)

    return SynthSmallExtirpationReconstructionResult(
        config=reconstruction_config,
        observation_bundle_dir=obs_bundle.artifact_dir,
        site_rows=site_rows,
        time_summary_rows=time_summary_rows,
        verification_checks=checks,
        evaluation_metrics=metrics,
    )


def inspect_synth_small_extirpation_reconstruction_artifacts(
    artifact_dir: str | PathLike[str] = DEFAULT_OUTPUT_DIR,
    *,
    output_dir: str | PathLike[str] | None = None,
) -> ExtirpationReconstructionInspectionResult:
    bundle = load_synth_small_extirpation_reconstruction_artifacts(artifact_dir)
    inspection_dir = (
        Path(output_dir) if output_dir is not None else bundle.artifact_dir / "inspection"
    )
    inspection_dir.mkdir(parents=True, exist_ok=True)

    parsed_site_rows = parse_site_reconstruction_rows(bundle.site_rows)
    parsed_time_rows = parse_time_summary_rows(bundle.time_summary_rows)
    checks = verify_loaded_reconstruction_bundle(
        parsed_site_rows,
        parsed_time_rows,
        bundle,
    )
    payload = {
        "artifact_dir": str(bundle.artifact_dir),
        "inspection_output_dir": str(inspection_dir),
        "passed": all(check.passed for check in checks),
        "checks": [check.to_dict() for check in checks],
    }

    verification_path = inspection_dir / "verification.json"
    report_path = inspection_dir / "report.md"
    verification_path.write_text(dumps(payload, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        render_reconstruction_report(
            SynthSmallExtirpationReconstructionResult(
                config=default_reconstruction_config(),
                observation_bundle_dir=bundle.artifact_dir,
                site_rows=parsed_site_rows,
                time_summary_rows=parsed_time_rows,
                verification_checks=tuple(checks),
                evaluation_metrics=bundle.evaluation_metrics,
            )
        ),
        encoding="utf-8",
    )
    return ExtirpationReconstructionInspectionResult(
        artifact_dir=bundle.artifact_dir,
        output_dir=inspection_dir,
        verification_checks=checks,
        verification_path=verification_path,
        report_path=report_path,
    )


def build_site_reconstruction_rows(
    bundle: LoadedSynthSmallObservationBundle,
    min_final_absence_run: int = DEFAULT_MIN_FINAL_ABSENCE_RUN,
) -> tuple[SiteReconstructionRow, ...]:
    observations_by_site: dict[str, dict[int, list[dict[str, str]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in bundle.observations:
        observations_by_site[row["site_id"]][parse_int(row["time_index"])].append(row)

    site_rows: list[SiteReconstructionRow] = []
    for site in bundle.sites:
        site_id = site["site_id"]
        per_time = observations_by_site.get(site_id, {})
        if not per_time:
            site_rows.append(
                SiteReconstructionRow(
                    site_id=site_id,
                    cell_id=parse_int(site["cell_id"]),
                    row=parse_int(site["row"]),
                    col=parse_int(site["col"]),
                    region=site["region"],
                    front_band=site["front_band"],
                    visit_count=0,
                    survey_time_count=0,
                    detection_count=0,
                    first_detection_time=None,
                    last_detection_time=None,
                    final_absence_start_time=None,
                    final_absence_survey_time_count=0,
                    observed_extirpated_by_end=False,
                    observed_extirpation_time=None,
                    reconstruction_status=RECONSTRUCTION_STATUS_NO_SURVEY,
                )
            )
            continue

        times = sorted(per_time)
        detected_by_time: dict[int, bool] = {}
        effort_by_time: dict[int, float] = {}
        detection_count_by_time: dict[int, int] = {}
        detection_count_total = 0

        for time_index in times:
            rows = per_time[time_index]
            effort_sum = 0.0
            detection_count = 0
            for row in rows:
                effort_sum += parse_float(row["effort"])
                detected = parse_bool(row["detected"])
                detection_count += 1 if detected else 0
            detection_count_by_time[time_index] = detection_count
            effort_by_time[time_index] = effort_sum
            detected_by_time[time_index] = detection_count > 0
            detection_count_total += detection_count

        detected_times = [time_index for time_index in times if detected_by_time[time_index]]
        if not detected_times:
            site_rows.append(
                SiteReconstructionRow(
                    site_id=site_id,
                    cell_id=parse_int(site["cell_id"]),
                    row=parse_int(site["row"]),
                    col=parse_int(site["col"]),
                    region=site["region"],
                    front_band=site["front_band"],
                    visit_count=sum(len(per_time[t]) for t in times),
                    survey_time_count=len(times),
                    detection_count=0,
                    first_detection_time=None,
                    last_detection_time=None,
                    final_absence_start_time=None,
                    final_absence_survey_time_count=0,
                    observed_extirpated_by_end=False,
                    observed_extirpation_time=None,
                    reconstruction_status=(
                        RECONSTRUCTION_STATUS_INSUFFICIENT
                        if len(times) > 0
                        else RECONSTRUCTION_STATUS_NO_SURVEY
                    ),
                )
            )
            continue

        first_detection_time = min(detected_times)
        last_detection_time = max(detected_times)
        final_absence_times: list[int] = []
        last_index = times.index(last_detection_time)
        for time_index in times[last_index + 1 :]:
            if not _is_valid_absence_tail_time(
                time_index=time_index,
                effort_by_time=effort_by_time,
                detection_count_by_time=detection_count_by_time,
            ):
                break
            final_absence_times.append(time_index)
        # no additional stopping condition needed because we only require
        # consecutive surveyed times in the observed schedule

        observed_extinction = len(final_absence_times) >= min_final_absence_run
        final_start = final_absence_times[0] if observed_extinction else None
        observed_time = final_start if observed_extinction else None
        final_absence_count = len(final_absence_times) if observed_extinction else 0
        status = (
            RECONSTRUCTION_STATUS_OBSERVED_EXTINCTION
            if observed_extinction
            else RECONSTRUCTION_STATUS_NOT_EXTINCTION
        )

        site_rows.append(
            SiteReconstructionRow(
                site_id=site_id,
                cell_id=parse_int(site["cell_id"]),
                row=parse_int(site["row"]),
                col=parse_int(site["col"]),
                region=site["region"],
                front_band=site["front_band"],
                visit_count=sum(len(per_time[t]) for t in times),
                survey_time_count=len(times),
                detection_count=detection_count_total,
                first_detection_time=first_detection_time,
                last_detection_time=last_detection_time,
                final_absence_start_time=final_start,
                final_absence_survey_time_count=final_absence_count,
                observed_extirpated_by_end=observed_extinction,
                observed_extirpation_time=observed_time,
                reconstruction_status=status,
            )
        )
    return tuple(site_rows)


def _is_valid_absence_tail_time(
    *,
    time_index: int,
    effort_by_time: dict[int, float],
    detection_count_by_time: dict[int, int],
) -> bool:
    if effort_by_time.get(time_index, 0.0) <= 0.0:
        return False
    return detection_count_by_time.get(time_index, 0) == 0


def build_time_detection_summary_rows(
    bundle: LoadedSynthSmallObservationBundle,
) -> tuple[TimeDetectionSummaryRow, ...]:
    rows_by_time: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in bundle.observations:
        rows_by_time[parse_int(row["time_index"])].append(row)

    summary_rows: list[TimeDetectionSummaryRow] = []
    for time_index in sorted(rows_by_time):
        rows = rows_by_time[time_index]
        visit_count = len(rows)
        site_count = len({row["site_id"] for row in rows})
        detection_count = sum(parse_bool(row["detected"]) for row in rows)
        observed_counts = [parse_int(row["observed_count"]) for row in rows]
        efforts = [parse_float(row["effort"]) for row in rows]
        summary_rows.append(
            TimeDetectionSummaryRow(
                time_index=time_index,
                visit_count=visit_count,
                site_count=site_count,
                observation_count=visit_count,
                detection_count=detection_count,
                detection_rate=(detection_count / visit_count) if visit_count else float("nan"),
                mean_observed_count=float(sum(observed_counts) / visit_count),
                mean_effort=float(sum(efforts) / visit_count),
            )
        )
    return tuple(summary_rows)


def verify_reconstruction_rows(
    site_rows: tuple[SiteReconstructionRow, ...],
    time_summary_rows: tuple[TimeDetectionSummaryRow, ...],
    *,
    obs_bundle: LoadedSynthSmallObservationBundle | None = None,
) -> tuple[ReconstructionVerificationCheck, ...]:
    status_valid = all(row.reconstruction_status in RECONSTRUCTION_STATUSES for row in site_rows)
    counts_non_negative = all(
        row.visit_count >= 0
        and row.survey_time_count >= 0
        and row.detection_count >= 0
        and row.final_absence_survey_time_count >= 0
        for row in site_rows
    )
    chronology_valid = all(
        row.first_detection_time is None
        or row.last_detection_time is None
        or row.first_detection_time <= row.last_detection_time
        for row in site_rows
    )
    time_summary_finite = all(
        row.detection_count <= row.observation_count
        and row.detection_rate >= 0.0
        and row.detection_rate <= 1.0
        and row.observation_count >= 0
        for row in time_summary_rows
    )
    status_timing = all(
        (
            (not row.observed_extirpated_by_end)
            or (
                row.observed_extirpation_time is not None
                and row.final_absence_survey_time_count >= 1
                and row.final_absence_start_time is not None
            )
        )
        and (row.observed_extirpation_time is None or row.observed_extirpated_by_end)
        for row in site_rows
    )
    no_hidden_truth_leak = _site_rows_no_forbidden_columns()
    status_row_counts = {
        RECONSTRUCTION_STATUS_OBSERVED_EXTINCTION: 0,
        RECONSTRUCTION_STATUS_NOT_EXTINCTION: 0,
        RECONSTRUCTION_STATUS_INSUFFICIENT: 0,
        RECONSTRUCTION_STATUS_NO_SURVEY: 0,
    }
    for row in site_rows:
        status_row_counts[row.reconstruction_status] += 1

    checks = (
        ReconstructionVerificationCheck(
            name="status_validity",
            passed=status_valid,
            message="all reconstruction_status values are known states",
            details={
                "invalid_status_count": sum(
                    1
                    for row in site_rows
                    if row.reconstruction_status not in RECONSTRUCTION_STATUSES
                )
            },
        ),
        ReconstructionVerificationCheck(
            name="counts_and_chronology",
            passed=counts_non_negative and chronology_valid,
            message="counts and detection chronology are finite and ordered",
            details={
                "counts_non_negative": counts_non_negative,
                "chronology_valid": chronology_valid,
            },
        ),
        ReconstructionVerificationCheck(
            name="time_summary_consistency",
            passed=time_summary_finite,
            message="time summary rows are internally consistent",
            details={
                "time_row_count": len(time_summary_rows),
                "invalid_time_rows": sum(
                    1
                    for row in time_summary_rows
                    if row.detection_count > row.observation_count
                    or row.detection_rate < 0.0
                    or row.detection_rate > 1.0
                ),
            },
        ),
        ReconstructionVerificationCheck(
            name="status_timing_consistency",
            passed=status_timing,
            message="extirpation timing is reported only for observed-extirpated sites",
            details={
                "rows_with_extirpation_time_without_status": sum(
                    1
                    for row in site_rows
                    if row.observed_extirpation_time is not None
                    and not row.observed_extirpated_by_end
                )
            },
        ),
        ReconstructionVerificationCheck(
            name="output_schema_no_truth_leak",
            passed=no_hidden_truth_leak,
            message="response-only output columns are free of hidden-truth fields",
            details={"forbidden_columns": sorted(RECONSTRUCTION_FORBIDDEN_COLUMNS)},
        ),
        ReconstructionVerificationCheck(
            name="status_coverage_summary",
            passed=True,
            message="status counts computed",
            details=status_row_counts | {"required_fields_present": True},
        ),
        ReconstructionVerificationCheck(
            name="artifact_config_consistency",
            passed=obs_bundle is not None,
            message="reconstruction artifact can be evaluated",
            details={"observation_bundle_available": obs_bundle is not None},
        ),
    )
    return checks


def evaluate_against_hidden_truth(
    site_rows: tuple[SiteReconstructionRow, ...],
    evaluation_truth_rows: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    truth_by_site = {row["site_id"]: row for row in evaluation_truth_rows}
    aligned_sites = [row for row in site_rows if row.site_id in truth_by_site]
    surveyed_sites = sum(1 for row in site_rows if row.survey_time_count > 0)

    tp = fp = tn = fn = 0
    temporal_errors: list[float] = []

    for row in aligned_sites:
        truth = truth_by_site[row.site_id]
        true_extirpated = parse_bool(truth["extirpated_by_end"])
        pred_extirpated = row.observed_extirpated_by_end

        if pred_extirpated and true_extirpated:
            tp += 1
        elif pred_extirpated and not true_extirpated:
            fp += 1
        elif (not pred_extirpated) and true_extirpated:
            fn += 1
        else:
            tn += 1

        if row.observed_extirpated_by_end and row.observed_extirpation_time is not None:
            true_extirpation = parse_optional_float(truth["true_extirpation"])
            if true_extirpation is not None:
                temporal_errors.append(float(row.observed_extirpation_time) - true_extirpation)

    confusion = {"tp": tp, "fp": fp, "tn": tn, "fn": fn}
    classification = _classification_metrics(tp, fp, tn, fn)
    status_counts = _status_counts(site_rows)

    metrics = {
        "site_coverage": {
            "site_count": len(site_rows),
            "surveyed_site_count": surveyed_sites,
            "aligned_site_count": len(aligned_sites),
            "coverage": surveyed_sites / len(site_rows) if site_rows else float("nan"),
        },
        "reconstruction_status_counts": status_counts,
        "confusion_matrix": confusion,
        "sensitivity": classification["sensitivity"],
        "specificity": classification["specificity"],
        "precision": classification["precision"],
        "temporal_error": _temporal_error_payload(temporal_errors),
        "bias_by_region": build_group_bias_payload(
            site_rows,
            truth_by_site,
            by_field="region",
        ),
        "bias_by_front_band": build_group_bias_payload(
            site_rows,
            truth_by_site,
            by_field="front_band",
        ),
        "interpretation": recommend_next_step(
            classification,
            status_counts,
            surveyed_sites=surveyed_sites,
            total_sites=len(site_rows),
        ),
    }
    metrics["limits"] = _baseline_limits()
    metrics["passed"] = _all_classification_defined(classification)
    metrics["metrics"] = dict(metrics)
    return metrics


def _all_classification_defined(classification: dict[str, float | None]) -> bool:
    return all(
        classification[field] is not None for field in ("sensitivity", "specificity", "precision")
    )


def _status_counts(site_rows: tuple[SiteReconstructionRow, ...]) -> dict[str, int]:
    status_counts = {status: 0 for status in RECONSTRUCTION_STATUSES}
    for row in site_rows:
        status_counts[row.reconstruction_status] += 1
    return status_counts


def _classification_metrics(tp: int, fp: int, tn: int, fn: int) -> dict[str, float | None]:
    sensitivity = tp / (tp + fn) if (tp + fn) else None
    specificity = tn / (tn + fp) if (tn + fp) else None
    precision = tp / (tp + fp) if (tp + fp) else None
    return {
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": precision,
        "balanced_accuracy": ((sensitivity or 0.0) + (specificity or 0.0)) / 2.0
        if sensitivity is not None and specificity is not None
        else None,
    }


def build_group_bias_payload(
    site_rows: tuple[SiteReconstructionRow, ...],
    truth_by_site: dict[str, dict[str, str]],
    by_field: str,
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[SiteReconstructionRow]] = defaultdict(list)
    for row in site_rows:
        if row.site_id not in truth_by_site:
            continue
        key = row.region if by_field == "region" else row.front_band
        groups[key].append(row)

    output: dict[str, dict[str, Any]] = {}
    for group_key, rows in groups.items():
        tp = fp = tn = fn = 0
        errors: list[float] = []
        for row in rows:
            truth = truth_by_site[row.site_id]
            true_extirpated = parse_bool(truth["extirpated_by_end"])
            pred_extirpated = row.observed_extirpated_by_end
            if pred_extirpated and true_extirpated:
                tp += 1
            elif pred_extirpated and not true_extirpated:
                fp += 1
            elif (not pred_extirpated) and true_extirpated:
                fn += 1
            else:
                tn += 1
            if pred_extirpated and row.observed_extirpation_time is not None:
                true_extirpation = parse_optional_float(truth["true_extirpation"])
                if true_extirpation is not None:
                    errors.append(float(row.observed_extirpation_time) - true_extirpation)
        metrics = _classification_metrics(tp, fp, tn, fn)
        temporal_error_payload = _temporal_error_payload(errors)
        output[group_key] = {
            "site_count": len(rows),
            "sensitivity": metrics["sensitivity"],
            "specificity": metrics["specificity"],
            "precision": metrics["precision"],
            "balanced_accuracy": metrics["balanced_accuracy"],
            "temporal_error_count": temporal_error_payload["count"],
            "mean_temporal_error": temporal_error_payload["mean_error"],
            "median_temporal_error": temporal_error_payload["median_error"],
            "mae_temporal_error": temporal_error_payload["mae"],
        }
    return output


def _temporal_error_payload(errors: list[float]) -> dict[str, Any]:
    if not errors:
        return {
            "count": 0,
            "mean_error": None,
            "median_error": None,
            "mae": None,
            "median_absolute_error": None,
        }
    values = np.asarray(errors, dtype=float)
    abs_values = np.abs(values)
    return {
        "count": int(values.size),
        "mean_error": float(np.mean(values)),
        "median_error": float(np.median(values)),
        "mae": float(np.mean(abs_values)),
        "median_absolute_error": float(np.median(abs_values)),
    }


def recommend_next_step(
    classification: dict[str, float | None],
    status_counts: dict[str, int],
    surveyed_sites: int,
    total_sites: int,
) -> dict[str, Any]:
    coverage = surveyed_sites / total_sites if total_sites else 0.0
    insufficient_fraction = (
        status_counts[RECONSTRUCTION_STATUS_INSUFFICIENT] / total_sites if total_sites else 0.0
    )
    sensitivity = classification["sensitivity"]
    precision = classification["precision"]
    ready = bool(
        coverage >= 0.4
        and insufficient_fraction <= 0.70
        and sensitivity is not None
        and sensitivity >= 0.25
        and precision is not None
        and precision >= 0.10
    )

    notes: list[str] = []
    if coverage < 0.4:
        notes.append("Increase survey coverage before moving to an inference layer.")
    if insufficient_fraction > 0.70:
        notes.append("Large fraction of sites remain insufficient-history under this rule.")
    if sensitivity is None or sensitivity < 0.25:
        notes.append(
            "Sensitivity to true extirpated sites is low; "
            "refine the rule or increase late-survey effort."
        )
    if precision is None or precision < 0.10:
        notes.append("Precision of observed-extirpation calls is low.")

    if not notes:
        notes.append(
            "This baseline reconstruction provides moderate signal for moving onward with caution."
        )

    return {
        "ready_for_next_step": ready,
        "recommended_next_step": (
            "Proceed to response-only ABC/POM design with explicit cautionary controls."
            if ready
            else "Refine the reconstruction rule and re-evaluate before ABC/POM."
        ),
        "notes": notes,
        "coverage": coverage,
    }


def _baseline_limits() -> list[str]:
    return [
        "No hidden truth is used to compute `observed_extirpation_time`.",
        "A `T_X^obs` label is issued only when a final absence run exists.",
        "Sites with no detections are conservatively tagged as insufficient history.",
        "This run is a baseline reconstruction; it is not a fitted model.",
    ]


def render_reconstruction_report(result: SynthSmallExtirpationReconstructionResult) -> str:
    metrics = result.evaluation_metrics
    coverage = metrics["site_coverage"]
    status_counts = metrics["reconstruction_status_counts"]
    matrix = metrics["confusion_matrix"]
    interpretation = metrics["interpretation"]
    temporal = metrics["temporal_error"]

    lines: list[str] = [
        "# Synth-Small Response-Only Extirpation Reconstruction",
        "",
        "## Scope",
        "",
        (
            "This artifact estimates a conservative observed extirpation proxy "
            "`T_X^obs` using only `sites.csv`, `visits.csv`, `observations.csv`, "
            "and `observation_config.json` from the synth-small observation bundle."
        ),
        "Hidden truth is used only in a separate evaluation step.",
        "",
        "## Inputs",
        f"- Observation bundle: `{result.config.observation_artifact_dir}`",
        f"- Final-absence rule: `{result.config.rule_name}`",
        f"- Minimum final-absence length: `{result.config.min_final_absence_run}`",
        "",
        "## Response-Only Boundary",
        "- `site_reconstruction.csv` contains only analyst-facing fields.",
        "- `reconstruction_config.json` records the rule and forbidden truth fields.",
        "- Hidden-truth columns (for example `true_extirpation`, `extirpated_by_end`, "
        "`driver_arrival`) are excluded from all reconstruction decisions.",
        "",
        "## Reconstruction Outcome",
        f"- Total sites: `{coverage['site_count']}`",
        f"- Surveyed sites: `{coverage['surveyed_site_count']}`",
        f"- Site coverage: `{coverage['coverage']:.6g}`",
        f"- Aligned sites with evaluation truth: `{coverage['aligned_site_count']}`",
        f"- `observed_extirpated_by_end`: `"
        f"{status_counts[RECONSTRUCTION_STATUS_OBSERVED_EXTINCTION]}`",
        f"- `not_observed_extirpated_by_end`: `"
        f"{status_counts[RECONSTRUCTION_STATUS_NOT_EXTINCTION]}`",
        f"- `insufficient_history`: `{status_counts[RECONSTRUCTION_STATUS_INSUFFICIENT]}`",
        f"- `no_surveyed_times`: `{status_counts[RECONSTRUCTION_STATUS_NO_SURVEY]}`",
        "",
        "## Confusion and Classification",
        f"- TP / FP / TN / FN: `{matrix['tp']} / {matrix['fp']} / {matrix['tn']} / {matrix['fn']}`",
        f"- Sensitivity: `{_value_or_na(metrics['sensitivity'])}`",
        f"- Specificity: `{_value_or_na(metrics['specificity'])}`",
        f"- Precision: `{_value_or_na(metrics['precision'])}`",
        "",
        "## Temporal Error (Observed vs. True)",
        f"- Temporal error count: `{temporal['count']}`",
        f"- Mean error: `{_value_or_na(temporal['mean_error'])}`",
        f"- Median error: `{_value_or_na(temporal['median_error'])}`",
        f"- MAE: `{_value_or_na(temporal['mae'])}`",
        "",
        "## Spatial Bias",
        "",
        "### By Region",
    ]
    for region in sorted(metrics["bias_by_region"]):
        payload = metrics["bias_by_region"][region]
        lines.append(
            "- "
            f"{region}: "
            f"sensitivity={_value_or_na(payload['sensitivity'])}, "
            f"specificity={_value_or_na(payload['specificity'])}, "
            f"precision={_value_or_na(payload['precision'])}, "
            f"mae={_value_or_na(payload['mae_temporal_error'])}"
        )
    lines.append("")
    lines.append("### By Front Band")
    for front_band in sorted(metrics["bias_by_front_band"]):
        payload = metrics["bias_by_front_band"][front_band]
        lines.append(
            "- "
            f"{front_band}: "
            f"sensitivity={_value_or_na(payload['sensitivity'])}, "
            f"specificity={_value_or_na(payload['specificity'])}, "
            f"precision={_value_or_na(payload['precision'])}, "
            f"mae={_value_or_na(payload['mae_temporal_error'])}"
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            f"- Ready for next step: `{str(interpretation['ready_for_next_step']).lower()}`",
            f"- {interpretation['recommended_next_step']}",
            "",
            "### Notes",
        ]
    )
    for note in interpretation["notes"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Limits"])
    for note in metrics["limits"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def _value_or_na(value: float | None) -> str:
    if value is None:
        return "NA"
    return f"{value:.6g}"


def _site_rows_no_forbidden_columns() -> bool:
    return not set(SITE_RECONSTRUCTION_COLUMNS).intersection(RECONSTRUCTION_FORBIDDEN_COLUMNS)


def load_synth_small_extirpation_reconstruction_artifacts(
    artifact_dir: str | PathLike[str],
) -> LoadedReconstructionBundle:
    artifact_path = Path(artifact_dir)
    missing = [name for name in REQUIRED_OUTPUT_FILES if not (artifact_path / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(
            f"missing required synth-small extirpation reconstruction artifacts: {missing_text}"
        )
    return LoadedReconstructionBundle(
        artifact_dir=artifact_path,
        reconstruction_config=read_json(artifact_path / "reconstruction_config.json"),
        site_rows=read_csv_rows(artifact_path / "site_reconstruction.csv"),
        time_summary_rows=read_csv_rows(artifact_path / "time_detection_summary.csv"),
        verification=read_json(artifact_path / "verification.json"),
        evaluation_metrics=read_json(artifact_path / "evaluation_metrics.json"),
    )


def verify_loaded_reconstruction_bundle(
    site_rows: tuple[SiteReconstructionRow, ...],
    time_rows: tuple[TimeDetectionSummaryRow, ...],
    bundle: LoadedReconstructionBundle,
) -> tuple[ReconstructionVerificationCheck, ...]:
    parseable = site_rows_and_time_rows_parseable(site_rows, time_rows)
    detected_site_columns = set(asdict(site_rows[0]).keys()) if site_rows else set()
    missing_columns = [
        column for column in SITE_RECONSTRUCTION_COLUMNS if column not in detected_site_columns
    ]
    return (
        ReconstructionVerificationCheck(
            name="required_columns",
            passed=not missing_columns,
            message="required site reconstruction columns are present",
            details={"missing_columns": missing_columns},
        ),
        ReconstructionVerificationCheck(
            name="forbidden_columns",
            passed=_site_rows_no_forbidden_columns(),
            message="no hidden-truth columns are included in reconstruction schema",
            details={"forbidden_columns": sorted(RECONSTRUCTION_FORBIDDEN_COLUMNS)},
        ),
        ReconstructionVerificationCheck(
            name="evaluation_payload",
            passed=EVALUATION_REQUIRED_KEYS.issubset(bundle.evaluation_metrics.keys()),
            message="evaluation metrics include required keys",
            details={"required_keys": sorted(EVALUATION_REQUIRED_KEYS)},
        ),
        ReconstructionVerificationCheck(
            name="parsable_artifacts",
            passed=parseable,
            message="stored artifact tables are parsable and numerically coherent",
            details={
                "site_row_count": len(site_rows),
                "time_row_count": len(time_rows),
                "verification_is_dict": isinstance(bundle.verification, dict),
            },
        ),
    )


def site_rows_and_time_rows_parseable(
    site_rows: tuple[SiteReconstructionRow, ...],
    time_rows: tuple[TimeDetectionSummaryRow, ...],
) -> bool:
    return all(
        row.visit_count >= 0
        and row.survey_time_count >= 0
        and row.detection_count >= 0
        and row.final_absence_survey_time_count >= 0
        and row.reconstruction_status in RECONSTRUCTION_STATUSES
        and (row.observed_extirpation_time is None or row.observed_extirpation_time >= 0)
        for row in site_rows
    ) and all(
        row.visit_count >= 0
        and row.site_count >= 0
        and row.observation_count >= 0
        and row.detection_count >= 0
        and row.detection_count <= row.observation_count
        and row.observation_count >= 0
        and _finite_float(row.detection_rate)
        and _finite_float(row.mean_observed_count)
        and _finite_float(row.mean_effort)
        for row in time_rows
    )


def parse_site_reconstruction_rows(
    rows: tuple[dict[str, str], ...],
) -> tuple[SiteReconstructionRow, ...]:
    parsed: list[SiteReconstructionRow] = []
    for row in rows:
        parsed.append(
            SiteReconstructionRow(
                site_id=row["site_id"],
                cell_id=parse_int(row["cell_id"]),
                row=parse_int(row["row"]),
                col=parse_int(row["col"]),
                region=row["region"],
                front_band=row["front_band"],
                visit_count=parse_int(row["visit_count"]),
                survey_time_count=parse_int(row["survey_time_count"]),
                detection_count=parse_int(row["detection_count"]),
                first_detection_time=parse_optional_int(row["first_detection_time"]),
                last_detection_time=parse_optional_int(row["last_detection_time"]),
                final_absence_start_time=parse_optional_int(row["final_absence_start_time"]),
                final_absence_survey_time_count=parse_int(row["final_absence_survey_time_count"]),
                observed_extirpated_by_end=parse_bool(row["observed_extirpated_by_end"]),
                observed_extirpation_time=parse_optional_int(row["observed_extirpation_time"]),
                reconstruction_status=row["reconstruction_status"],
            )
        )
    return tuple(parsed)


def parse_time_summary_rows(
    rows: tuple[dict[str, str], ...],
) -> tuple[TimeDetectionSummaryRow, ...]:
    parsed: list[TimeDetectionSummaryRow] = []
    for row in rows:
        parsed.append(
            TimeDetectionSummaryRow(
                time_index=parse_int(row["time_index"]),
                visit_count=parse_int(row["visit_count"]),
                site_count=parse_int(row["site_count"]),
                observation_count=parse_int(row["observation_count"]),
                detection_count=parse_int(row["detection_count"]),
                detection_rate=parse_float(row["detection_rate"]),
                mean_observed_count=parse_float(row["mean_observed_count"]),
                mean_effort=parse_float(row["mean_effort"]),
            )
        )
    return tuple(parsed)


def parse_optional_int(value: str) -> int | None:
    if value == "":
        return None
    return parse_int(value)


def _optional_int_string(value: int | None) -> str:
    return "" if value is None else str(value)


def _finite_float(value: float) -> bool:
    try:
        return (
            float(value) == float(value)
            and float(value) != float("inf")
            and float(value) != float("-inf")
        )
    except ValueError:
        return False


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    payload = loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return payload
