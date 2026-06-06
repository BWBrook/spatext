"""Disk-first inspection for synth-small response-screen artifacts."""

from __future__ import annotations

from csv import DictReader, writer
from dataclasses import dataclass
from json import dumps, loads
from os import PathLike
from pathlib import Path
from typing import Any

from .observations import parse_float, parse_int, stringify_float
from .response_screen import (
    GROUP_SCREEN_COLUMNS,
    RESPONSE_SCREEN_OUTPUT_FILES,
    TIME_SCREEN_COLUMNS,
)

DEFAULT_RESPONSE_SCREEN_DIR = Path("artifacts/synth_small_response_screen")

RESPONSE_SCREEN_INSPECTION_FILES = (
    "verification.json",
    "review_summary.json",
    "group_review_summary.csv",
    "report.md",
)

GROUP_REVIEW_COLUMNS = (
    "group_type",
    "group",
    "site_count",
    "observed_extirpated_fraction",
    "insufficient_fraction",
    "screen_note",
    "review_flag",
)

FORBIDDEN_INSPECTION_FIELDS = frozenset(
    {
        "driver_arrival",
        "predator_pressure",
        "true_extirpation",
        "extirpation_lag",
        "extirpated_by_end",
        "initial_abundance",
        "final_abundance",
        "evaluation_truth",
        "evaluation_metrics",
    }
)


@dataclass(frozen=True, slots=True)
class LoadedResponseScreenArtifactBundle:
    artifact_dir: Path
    response_screen_config: dict[str, Any]
    screen_summary: dict[str, Any]
    group_rows: tuple[dict[str, str], ...]
    time_rows: tuple[dict[str, str], ...]
    verification: dict[str, Any]
    report_text: str


@dataclass(frozen=True, slots=True)
class ResponseScreenInspectionCheck:
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
class GroupReviewRow:
    group_type: str
    group: str
    site_count: int
    observed_extirpated_fraction: float
    insufficient_fraction: float
    screen_note: str
    review_flag: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.group_type,
            self.group,
            str(self.site_count),
            stringify_float(self.observed_extirpated_fraction),
            stringify_float(self.insufficient_fraction),
            self.screen_note,
            self.review_flag,
        )


@dataclass(frozen=True, slots=True)
class ResponseScreenInspectionResult:
    artifact_dir: Path
    output_dir: Path
    verification_checks: tuple[ResponseScreenInspectionCheck, ...]
    review_summary: dict[str, Any]
    group_review_rows: tuple[GroupReviewRow, ...]
    verification_path: Path
    review_summary_path: Path
    group_review_path: Path
    report_path: Path

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)


def inspect_synth_small_response_screen_artifacts(
    artifact_dir: str | PathLike[str] = DEFAULT_RESPONSE_SCREEN_DIR,
    *,
    output_dir: str | PathLike[str] | None = None,
) -> ResponseScreenInspectionResult:
    bundle = load_response_screen_artifact_bundle(artifact_dir)
    inspection_dir = (
        Path(output_dir) if output_dir is not None else bundle.artifact_dir / "inspection"
    )
    inspection_dir.mkdir(parents=True, exist_ok=True)

    checks = verify_response_screen_artifact_bundle(bundle)
    group_review_rows = build_group_review_rows(bundle.group_rows)
    review_summary = build_review_summary(bundle, group_review_rows)

    verification_path = inspection_dir / "verification.json"
    review_summary_path = inspection_dir / "review_summary.json"
    group_review_path = inspection_dir / "group_review_summary.csv"
    report_path = inspection_dir / "report.md"

    verification_payload = {
        "artifact_dir": str(bundle.artifact_dir),
        "inspection_output_dir": str(inspection_dir),
        "passed": all(check.passed for check in checks),
        "checks": [check.to_dict() for check in checks],
    }
    verification_path.write_text(dumps(verification_payload, indent=2) + "\n", encoding="utf-8")
    review_summary_path.write_text(dumps(review_summary, indent=2) + "\n", encoding="utf-8")
    write_rows(
        GROUP_REVIEW_COLUMNS,
        (row.to_csv_row() for row in group_review_rows),
        group_review_path,
    )
    report_path.write_text(
        render_response_screen_inspection_report(
            bundle=bundle,
            checks=checks,
            review_summary=review_summary,
            group_review_rows=group_review_rows,
        ),
        encoding="utf-8",
    )

    return ResponseScreenInspectionResult(
        artifact_dir=bundle.artifact_dir,
        output_dir=inspection_dir,
        verification_checks=checks,
        review_summary=review_summary,
        group_review_rows=group_review_rows,
        verification_path=verification_path,
        review_summary_path=review_summary_path,
        group_review_path=group_review_path,
        report_path=report_path,
    )


def load_response_screen_artifact_bundle(
    artifact_dir: str | PathLike[str],
) -> LoadedResponseScreenArtifactBundle:
    artifact_path = Path(artifact_dir)
    missing = [name for name in RESPONSE_SCREEN_OUTPUT_FILES if not (artifact_path / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(f"missing required response screen artifacts: {missing_text}")
    return LoadedResponseScreenArtifactBundle(
        artifact_dir=artifact_path,
        response_screen_config=read_json(artifact_path / "response_screen_config.json"),
        screen_summary=read_json(artifact_path / "screen_summary.json"),
        group_rows=read_csv_rows(artifact_path / "group_screen_summary.csv"),
        time_rows=read_csv_rows(artifact_path / "time_screen_summary.csv"),
        verification=read_json(artifact_path / "verification.json"),
        report_text=(artifact_path / "report.md").read_text(encoding="utf-8"),
    )


def verify_response_screen_artifact_bundle(
    bundle: LoadedResponseScreenArtifactBundle,
) -> tuple[ResponseScreenInspectionCheck, ...]:
    group_columns = set(bundle.group_rows[0]) if bundle.group_rows else set()
    time_columns = set(bundle.time_rows[0]) if bundle.time_rows else set()
    required_group_missing = sorted(set(GROUP_SCREEN_COLUMNS) - group_columns)
    required_time_missing = sorted(set(TIME_SCREEN_COLUMNS) - time_columns)
    forbidden_columns = sorted((group_columns | time_columns) & FORBIDDEN_INSPECTION_FIELDS)
    summary_forbidden = sorted(find_forbidden_keys(bundle.screen_summary))
    source_passed = bool(bundle.verification.get("passed"))
    decision = bundle.screen_summary.get("screen_decision")
    report_has_caution = "Response-Only" in bundle.report_text and "Screen" in bundle.report_text
    return (
        ResponseScreenInspectionCheck(
            name="required_files",
            passed=all(
                (bundle.artifact_dir / name).exists() for name in RESPONSE_SCREEN_OUTPUT_FILES
            ),
            message="required response-screen artifact files are present",
            details={"file_count": len(RESPONSE_SCREEN_OUTPUT_FILES)},
        ),
        ResponseScreenInspectionCheck(
            name="required_columns",
            passed=not required_group_missing and not required_time_missing,
            message="required screen table columns are present",
            details={
                "missing_group_columns": required_group_missing,
                "missing_time_columns": required_time_missing,
            },
        ),
        ResponseScreenInspectionCheck(
            name="response_only_boundary",
            passed=not forbidden_columns and not summary_forbidden,
            message="inspection inputs omit hidden-truth and evaluation fields",
            details={
                "forbidden_columns": forbidden_columns,
                "forbidden_summary_keys": summary_forbidden,
            },
        ),
        ResponseScreenInspectionCheck(
            name="source_screen_verification",
            passed=source_passed,
            message="source response screen verification passed",
            details={"source_passed": source_passed},
        ),
        ResponseScreenInspectionCheck(
            name="reviewable_decision",
            passed=decision in {"screen_with_caution", "do_not_screen"} and report_has_caution,
            message="screen decision and report are reviewable",
            details={"screen_decision": decision, "report_has_caution": report_has_caution},
        ),
        ResponseScreenInspectionCheck(
            name="numeric_coherence",
            passed=screen_tables_are_numeric(bundle.group_rows, bundle.time_rows),
            message="screen tables are numerically parseable and coherent",
            details={
                "group_row_count": len(bundle.group_rows),
                "time_row_count": len(bundle.time_rows),
            },
        ),
    )


def build_group_review_rows(rows: tuple[dict[str, str], ...]) -> tuple[GroupReviewRow, ...]:
    output: list[GroupReviewRow] = []
    for row in rows:
        observed_fraction = parse_float(row["observed_extirpated_fraction"])
        insufficient_fraction = parse_float(row["insufficient_fraction"])
        review_flag = "review"
        if row["screen_note"] in {"low_information", "no_observed_extirpation"}:
            review_flag = "low_information"
        elif observed_fraction < 0.10:
            review_flag = "weak_signal"
        elif insufficient_fraction > 0.50:
            review_flag = "sparse_history"
        output.append(
            GroupReviewRow(
                group_type=row["group_type"],
                group=row["group"],
                site_count=parse_int(row["site_count"]),
                observed_extirpated_fraction=observed_fraction,
                insufficient_fraction=insufficient_fraction,
                screen_note=row["screen_note"],
                review_flag=review_flag,
            )
        )
    return tuple(output)


def build_review_summary(
    bundle: LoadedResponseScreenArtifactBundle,
    group_review_rows: tuple[GroupReviewRow, ...],
) -> dict[str, Any]:
    summary = bundle.screen_summary
    failure_modes = summary["failure_modes"]
    low_information_groups = [
        {
            "group_type": row.group_type,
            "group": row.group,
            "review_flag": row.review_flag,
        }
        for row in group_review_rows
        if row.review_flag in {"low_information", "weak_signal", "sparse_history"}
    ]
    return {
        "screen_decision": summary["screen_decision"],
        "site_count": summary["site_count"],
        "observed_extirpated_site_count": summary["observed_extirpated_site_count"],
        "not_observed_extirpated_site_count": summary["not_observed_extirpated_site_count"],
        "insufficient_history_count": summary["insufficient_history_count"],
        "observed_extirpated_fraction": summary["observed_extirpated_fraction"],
        "review_flags": {
            "late_screen_bias_warning": failure_modes["late_screen_bias_warning"],
            "not_observed_extirpated_fraction": failure_modes["not_observed_extirpated_fraction"],
            "low_information_group_count": len(low_information_groups),
        },
        "low_information_groups": low_information_groups,
        "interpretation": {
            "classification": "disk_first_review_only",
            "notes": [
                "Inspection consumes emitted screen artifacts from disk.",
                "The inspection does not rebuild the response screen or run inference.",
                "Weak-information groups are review targets, not failures.",
            ],
        },
    }


def render_response_screen_inspection_report(
    *,
    bundle: LoadedResponseScreenArtifactBundle,
    checks: tuple[ResponseScreenInspectionCheck, ...],
    review_summary: dict[str, Any],
    group_review_rows: tuple[GroupReviewRow, ...],
) -> str:
    lines = [
        "# Synth-Small Response Screen Inspection",
        "",
        "## Scope",
        "",
        "This inspection reloads an emitted response-screen bundle from disk.",
        "It does not rebuild the screen, fit a model, or read evaluation truth.",
        "",
        "## Source Bundle",
        f"- Artifact directory: `{bundle.artifact_dir}`",
        f"- Source screen decision: `{review_summary['screen_decision']}`",
        f"- Verification passed: `{str(all(check.passed for check in checks)).lower()}`",
        "",
        "## Review Summary",
        f"- Sites: `{review_summary['site_count']}`",
        f"- Observed extirpated sites: `{review_summary['observed_extirpated_site_count']}`",
        (
            "- Not observed extirpated sites: "
            f"`{review_summary['not_observed_extirpated_site_count']}`"
        ),
        (
            "- Late-screen bias warning: "
            f"`{str(review_summary['review_flags']['late_screen_bias_warning']).lower()}`"
        ),
        "",
        "## Checks",
    ]
    for check in checks:
        lines.append(f"- {check.name}: `{str(check.passed).lower()}` - {check.message}")
    lines.extend(["", "## Group Review Flags"])
    for row in group_review_rows:
        lines.append(
            "- "
            f"{row.group_type}/{row.group}: "
            f"observed_fraction={row.observed_extirpated_fraction:.6g}, "
            f"insufficient_fraction={row.insufficient_fraction:.6g}, "
            f"flag={row.review_flag}"
        )
    return "\n".join(lines) + "\n"


def screen_tables_are_numeric(
    group_rows: tuple[dict[str, str], ...],
    time_rows: tuple[dict[str, str], ...],
) -> bool:
    try:
        group_ok = all(
            parse_int(row["site_count"]) >= 0
            and 0.0 <= parse_float(row["observed_extirpated_fraction"]) <= 1.0
            and 0.0 <= parse_float(row["insufficient_fraction"]) <= 1.0
            for row in group_rows
        )
        time_ok = all(
            parse_int(row["time_index"]) >= 0
            and parse_int(row["visit_count"]) >= 0
            and 0.0 <= parse_float(row["detection_rate"]) <= 1.0
            and 0.0 <= parse_float(row["cumulative_detection_fraction"]) <= 1.0
            for row in time_rows
        )
    except KeyError, ValueError:
        return False
    return group_ok and time_ok


def find_forbidden_keys(payload: object) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        found.update(set(payload) & FORBIDDEN_INSPECTION_FIELDS)
        for value in payload.values():
            found.update(find_forbidden_keys(value))
    elif isinstance(payload, list):
        for value in payload:
            found.update(find_forbidden_keys(value))
    return found


def write_rows(columns: tuple[str, ...], rows: Any, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(columns)
        csv_writer.writerows(rows)


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    payload = loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return payload
