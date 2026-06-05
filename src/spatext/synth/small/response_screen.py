"""Response-only screening summaries for synth-small reconstruction artifacts."""

from __future__ import annotations

from collections import defaultdict
from csv import DictReader, writer
from dataclasses import asdict, dataclass
from json import dumps, loads
from os import PathLike
from pathlib import Path
from typing import Any

from .observations import parse_float, parse_int, stringify_float
from .reconstruction import (
    RECONSTRUCTION_FORBIDDEN_COLUMNS,
    RECONSTRUCTION_STATUS_INSUFFICIENT,
    RECONSTRUCTION_STATUS_NO_SURVEY,
    RECONSTRUCTION_STATUS_NOT_EXTINCTION,
    RECONSTRUCTION_STATUS_OBSERVED_EXTINCTION,
    SITE_RECONSTRUCTION_COLUMNS,
    TIME_DETECTION_SUMMARY_COLUMNS,
    parse_optional_int,
)

DEFAULT_RECONSTRUCTION_DIR = Path("artifacts/synth_small_extirpation_reconstruction")
DEFAULT_OUTPUT_DIR = Path("artifacts/synth_small_response_screen")

RESPONSE_SCREEN_INPUT_FILES = (
    "reconstruction_config.json",
    "site_reconstruction.csv",
    "time_detection_summary.csv",
    "verification.json",
)
RESPONSE_SCREEN_OUTPUT_FILES = (
    "response_screen_config.json",
    "screen_summary.json",
    "group_screen_summary.csv",
    "time_screen_summary.csv",
    "verification.json",
    "report.md",
)
GROUP_SCREEN_COLUMNS = (
    "group_type",
    "group",
    "site_count",
    "observed_extirpated_site_count",
    "not_observed_extirpated_site_count",
    "insufficient_history_count",
    "no_surveyed_times_count",
    "observed_extirpated_fraction",
    "insufficient_fraction",
    "first_observed_extirpation_time",
    "median_observed_extirpation_time",
    "last_observed_extirpation_time",
    "screen_note",
)
TIME_SCREEN_COLUMNS = (
    "time_index",
    "visit_count",
    "site_count",
    "observation_count",
    "detection_count",
    "detection_rate",
    "mean_observed_count",
    "mean_effort",
    "cumulative_detection_fraction",
)


@dataclass(frozen=True, slots=True)
class ResponseScreenConfig:
    """Configuration for the small response-only screening summary."""

    screen_name: str = "synth-small-response-only-screen"
    reconstruction_artifact_dir: str = str(DEFAULT_RECONSTRUCTION_DIR)
    low_information_fraction: float = 0.50

    def to_dict(self) -> dict[str, Any]:
        return {
            "screen_name": self.screen_name,
            "reconstruction_artifact_dir": self.reconstruction_artifact_dir,
            "low_information_fraction": self.low_information_fraction,
        }


@dataclass(frozen=True, slots=True)
class ResponseScreenVerificationCheck:
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
class GroupScreenSummaryRow:
    group_type: str
    group: str
    site_count: int
    observed_extirpated_site_count: int
    not_observed_extirpated_site_count: int
    insufficient_history_count: int
    no_surveyed_times_count: int
    observed_extirpated_fraction: float
    insufficient_fraction: float
    first_observed_extirpation_time: int | None
    median_observed_extirpation_time: float | None
    last_observed_extirpation_time: int | None
    screen_note: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.group_type,
            self.group,
            str(self.site_count),
            str(self.observed_extirpated_site_count),
            str(self.not_observed_extirpated_site_count),
            str(self.insufficient_history_count),
            str(self.no_surveyed_times_count),
            stringify_float(self.observed_extirpated_fraction),
            stringify_float(self.insufficient_fraction),
            ""
            if self.first_observed_extirpation_time is None
            else str(self.first_observed_extirpation_time),
            ""
            if self.median_observed_extirpation_time is None
            else stringify_float(self.median_observed_extirpation_time),
            ""
            if self.last_observed_extirpation_time is None
            else str(self.last_observed_extirpation_time),
            self.screen_note,
        )


@dataclass(frozen=True, slots=True)
class TimeScreenSummaryRow:
    time_index: int
    visit_count: int
    site_count: int
    observation_count: int
    detection_count: int
    detection_rate: float
    mean_observed_count: float
    mean_effort: float
    cumulative_detection_fraction: float

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
            stringify_float(self.cumulative_detection_fraction),
        )


@dataclass(frozen=True, slots=True)
class LoadedResponseScreenInputs:
    reconstruction_dir: Path
    reconstruction_config: dict[str, Any]
    site_rows: tuple[dict[str, str], ...]
    time_rows: tuple[dict[str, str], ...]
    reconstruction_verification: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ResponseOnlyScreenResult:
    config: ResponseScreenConfig
    reconstruction_dir: Path
    summary: dict[str, Any]
    group_rows: tuple[GroupScreenSummaryRow, ...]
    time_rows: tuple[TimeScreenSummaryRow, ...]
    verification_checks: tuple[ResponseScreenVerificationCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def verification_payload(self) -> dict[str, Any]:
        return {
            "reconstruction_dir": str(self.reconstruction_dir),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
        }

    def write_artifacts(
        self, output_dir: str | PathLike[str] = DEFAULT_OUTPUT_DIR
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "response_screen_config.json"
        summary_path = target_dir / "screen_summary.json"
        group_path = target_dir / "group_screen_summary.csv"
        time_path = target_dir / "time_screen_summary.csv"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(
            dumps(
                {
                    "config": self.config.to_dict(),
                    "passed": self.passed,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        summary_path.write_text(dumps(self.summary, indent=2) + "\n", encoding="utf-8")
        write_rows(GROUP_SCREEN_COLUMNS, (row.to_csv_row() for row in self.group_rows), group_path)
        write_rows(TIME_SCREEN_COLUMNS, (row.to_csv_row() for row in self.time_rows), time_path)
        verification_path.write_text(
            dumps(self.verification_payload(), indent=2) + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_response_screen_report(self), encoding="utf-8")
        return (
            config_path,
            summary_path,
            group_path,
            time_path,
            verification_path,
            report_path,
        )


def build_response_only_screen(
    reconstruction_dir: str | PathLike[str] = DEFAULT_RECONSTRUCTION_DIR,
    *,
    config: ResponseScreenConfig | None = None,
) -> ResponseOnlyScreenResult:
    screen_config = config or ResponseScreenConfig(
        reconstruction_artifact_dir=str(reconstruction_dir)
    )
    inputs = load_response_screen_inputs(reconstruction_dir)
    group_rows = build_group_screen_rows(inputs.site_rows, screen_config)
    time_rows = build_time_screen_rows(inputs.time_rows)
    summary = build_screen_summary(inputs.site_rows, group_rows, time_rows, screen_config)
    checks = verify_response_screen_inputs(inputs, group_rows, time_rows, summary)
    return ResponseOnlyScreenResult(
        config=screen_config,
        reconstruction_dir=inputs.reconstruction_dir,
        summary=summary,
        group_rows=group_rows,
        time_rows=time_rows,
        verification_checks=checks,
    )


def load_response_screen_inputs(
    reconstruction_dir: str | PathLike[str],
) -> LoadedResponseScreenInputs:
    artifact_dir = Path(reconstruction_dir)
    missing = [name for name in RESPONSE_SCREEN_INPUT_FILES if not (artifact_dir / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(f"missing required response screen input artifacts: {missing_text}")
    return LoadedResponseScreenInputs(
        reconstruction_dir=artifact_dir,
        reconstruction_config=read_json(artifact_dir / "reconstruction_config.json"),
        site_rows=read_csv_rows(artifact_dir / "site_reconstruction.csv"),
        time_rows=read_csv_rows(artifact_dir / "time_detection_summary.csv"),
        reconstruction_verification=read_json(artifact_dir / "verification.json"),
    )


def build_group_screen_rows(
    site_rows: tuple[dict[str, str], ...],
    config: ResponseScreenConfig,
) -> tuple[GroupScreenSummaryRow, ...]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in site_rows:
        groups[("region", row["region"])].append(row)
        groups[("front_band", row["front_band"])].append(row)

    output: list[GroupScreenSummaryRow] = []
    for group_type, group in sorted(groups):
        rows = groups[(group_type, group)]
        output.append(build_group_screen_row(group_type, group, rows, config))
    return tuple(output)


def build_group_screen_row(
    group_type: str,
    group: str,
    rows: list[dict[str, str]],
    config: ResponseScreenConfig,
) -> GroupScreenSummaryRow:
    site_count = len(rows)
    observed = [
        row
        for row in rows
        if row["reconstruction_status"] == RECONSTRUCTION_STATUS_OBSERVED_EXTINCTION
    ]
    not_observed = [
        row for row in rows if row["reconstruction_status"] == RECONSTRUCTION_STATUS_NOT_EXTINCTION
    ]
    insufficient = [
        row for row in rows if row["reconstruction_status"] == RECONSTRUCTION_STATUS_INSUFFICIENT
    ]
    no_survey = [
        row for row in rows if row["reconstruction_status"] == RECONSTRUCTION_STATUS_NO_SURVEY
    ]
    observed_times = sorted(
        observed_time
        for row in observed
        if (observed_time := parse_optional_int(row["observed_extirpation_time"])) is not None
    )
    observed_fraction = len(observed) / site_count if site_count else 0.0
    insufficient_fraction = (len(insufficient) + len(no_survey)) / site_count if site_count else 0.0
    note = "informative"
    if insufficient_fraction > config.low_information_fraction:
        note = "low_information"
    elif observed_fraction == 0.0:
        note = "no_observed_extirpation"
    elif observed_fraction < 0.10:
        note = "weak_observed_extirpation_signal"
    return GroupScreenSummaryRow(
        group_type=group_type,
        group=group,
        site_count=site_count,
        observed_extirpated_site_count=len(observed),
        not_observed_extirpated_site_count=len(not_observed),
        insufficient_history_count=len(insufficient),
        no_surveyed_times_count=len(no_survey),
        observed_extirpated_fraction=observed_fraction,
        insufficient_fraction=insufficient_fraction,
        first_observed_extirpation_time=observed_times[0] if observed_times else None,
        median_observed_extirpation_time=median_ints(observed_times),
        last_observed_extirpation_time=observed_times[-1] if observed_times else None,
        screen_note=note,
    )


def build_time_screen_rows(
    time_rows: tuple[dict[str, str], ...],
) -> tuple[TimeScreenSummaryRow, ...]:
    parsed = sorted(time_rows, key=lambda row: parse_int(row["time_index"]))
    total_detections = sum(parse_int(row["detection_count"]) for row in parsed)
    running_detections = 0
    output: list[TimeScreenSummaryRow] = []
    for row in parsed:
        running_detections += parse_int(row["detection_count"])
        output.append(
            TimeScreenSummaryRow(
                time_index=parse_int(row["time_index"]),
                visit_count=parse_int(row["visit_count"]),
                site_count=parse_int(row["site_count"]),
                observation_count=parse_int(row["observation_count"]),
                detection_count=parse_int(row["detection_count"]),
                detection_rate=parse_float(row["detection_rate"]),
                mean_observed_count=parse_float(row["mean_observed_count"]),
                mean_effort=parse_float(row["mean_effort"]),
                cumulative_detection_fraction=(
                    running_detections / total_detections if total_detections else 0.0
                ),
            )
        )
    return tuple(output)


def build_screen_summary(
    site_rows: tuple[dict[str, str], ...],
    group_rows: tuple[GroupScreenSummaryRow, ...],
    time_rows: tuple[TimeScreenSummaryRow, ...],
    config: ResponseScreenConfig,
) -> dict[str, Any]:
    site_count = len(site_rows)
    observed_count = sum(
        row["reconstruction_status"] == RECONSTRUCTION_STATUS_OBSERVED_EXTINCTION
        for row in site_rows
    )
    not_observed_count = sum(
        row["reconstruction_status"] == RECONSTRUCTION_STATUS_NOT_EXTINCTION for row in site_rows
    )
    insufficient_count = sum(
        row["reconstruction_status"] == RECONSTRUCTION_STATUS_INSUFFICIENT for row in site_rows
    )
    no_survey_count = sum(
        row["reconstruction_status"] == RECONSTRUCTION_STATUS_NO_SURVEY for row in site_rows
    )
    surveyed_count = sum(parse_int(row["survey_time_count"]) > 0 for row in site_rows)
    sufficient_count = site_count - insufficient_count - no_survey_count
    not_observed_fraction = not_observed_count / site_count if site_count else 0.0
    insufficient_fraction = insufficient_count / site_count if site_count else 0.0
    no_survey_fraction = no_survey_count / site_count if site_count else 0.0
    low_information_groups = [
        asdict(row)
        for row in group_rows
        if row.screen_note in {"low_information", "no_observed_extirpation"}
    ]
    screen_decision = (
        "screen_with_caution" if observed_count > 0 and sufficient_count > 0 else "do_not_screen"
    )
    if insufficient_fraction > config.low_information_fraction:
        screen_decision = "do_not_screen"
    return {
        "screen_name": config.screen_name,
        "site_count": site_count,
        "surveyed_site_count": surveyed_count,
        "sufficient_history_site_count": sufficient_count,
        "observed_extirpated_site_count": observed_count,
        "not_observed_extirpated_site_count": not_observed_count,
        "insufficient_history_count": insufficient_count,
        "no_surveyed_times_count": no_survey_count,
        "observed_extirpated_fraction": observed_count / site_count if site_count else 0.0,
        "sufficient_history_fraction": sufficient_count / site_count if site_count else 0.0,
        "screen_decision": screen_decision,
        "failure_modes": {
            "not_observed_extirpated_fraction": not_observed_fraction,
            "insufficient_history_fraction": insufficient_fraction,
            "no_survey_fraction": no_survey_fraction,
            "late_screen_bias_warning": not_observed_fraction > config.low_information_fraction,
            "low_information_group_count": len(low_information_groups),
        },
        "low_information_groups": low_information_groups,
        "time_coverage": {
            "survey_time_count": len(time_rows),
            "first_time_index": time_rows[0].time_index if time_rows else None,
            "last_time_index": time_rows[-1].time_index if time_rows else None,
            "mean_detection_rate": (
                sum(row.detection_rate for row in time_rows) / len(time_rows) if time_rows else 0.0
            ),
        },
        "uncertainty": {
            "classification": "cautionary_screen_only",
            "notes": [
                "Observed absence is a conservative response-side signal, not a fitted process.",
                "Groups with no observed extirpation calls should be treated as weak information.",
                "The screen is suitable for ranking later synthetic summaries, "
                "not for posterior claims.",
            ],
        },
        "limits": [
            "Screen decisions use only reconstructed response-side fields.",
            "The screen does not estimate driver arrival, pressure, or process parameters.",
            "Low-information groups remain valid outputs rather than implementation failures.",
        ],
    }


def verify_response_screen_inputs(
    inputs: LoadedResponseScreenInputs,
    group_rows: tuple[GroupScreenSummaryRow, ...],
    time_rows: tuple[TimeScreenSummaryRow, ...],
    summary: dict[str, Any],
) -> tuple[ResponseScreenVerificationCheck, ...]:
    site_columns = set(inputs.site_rows[0]) if inputs.site_rows else set()
    time_columns = set(inputs.time_rows[0]) if inputs.time_rows else set()
    missing_site_columns = sorted(set(SITE_RECONSTRUCTION_COLUMNS) - site_columns)
    missing_time_columns = sorted(set(TIME_DETECTION_SUMMARY_COLUMNS) - time_columns)
    excluded_columns_present = bool(site_columns & RECONSTRUCTION_FORBIDDEN_COLUMNS)
    reconstruction_passed = bool(inputs.reconstruction_verification.get("passed"))
    return (
        ResponseScreenVerificationCheck(
            name="input_files",
            passed=all(
                (inputs.reconstruction_dir / name).exists() for name in RESPONSE_SCREEN_INPUT_FILES
            ),
            message="required response-screen inputs are present",
            details={"input_file_count": len(RESPONSE_SCREEN_INPUT_FILES)},
        ),
        ResponseScreenVerificationCheck(
            name="required_columns",
            passed=not missing_site_columns and not missing_time_columns,
            message="required reconstruction columns are present",
            details={
                "missing_site_column_count": len(missing_site_columns),
                "missing_time_column_count": len(missing_time_columns),
            },
        ),
        ResponseScreenVerificationCheck(
            name="response_only_schema",
            passed=not excluded_columns_present,
            message="screen input schema contains only response-side fields",
            details={"excluded_field_count": int(excluded_columns_present)},
        ),
        ResponseScreenVerificationCheck(
            name="source_verification",
            passed=reconstruction_passed,
            message="source reconstruction verification passed",
            details={"source_passed": reconstruction_passed},
        ),
        ResponseScreenVerificationCheck(
            name="screen_outputs",
            passed=bool(group_rows) and bool(time_rows) and summary["site_count"] > 0,
            message="screen summary rows were computed",
            details={
                "group_row_count": len(group_rows),
                "time_row_count": len(time_rows),
                "site_count": summary["site_count"],
            },
        ),
    )


def render_response_screen_report(result: ResponseOnlyScreenResult) -> str:
    summary = result.summary
    failure = summary["failure_modes"]
    lines = [
        "# Synth-Small Response-Only Screen",
        "",
        "## Scope",
        "",
        "This bundle summarizes the existing reconstructed response surface.",
        "It is a bounded screen and does not fit a process model.",
        "",
        "## Screen Summary",
        f"- Sites: `{summary['site_count']}`",
        f"- Observed extirpated sites: `{summary['observed_extirpated_site_count']}`",
        f"- Not observed extirpated sites: `{summary['not_observed_extirpated_site_count']}`",
        f"- Insufficient-history sites: `{summary['insufficient_history_count']}`",
        f"- Screen decision: `{summary['screen_decision']}`",
        "",
        "## Failure Modes",
        f"- Not observed extirpated fraction: `{failure['not_observed_extirpated_fraction']:.6g}`",
        f"- Insufficient-history fraction: `{failure['insufficient_history_fraction']:.6g}`",
        f"- No-survey fraction: `{failure['no_survey_fraction']:.6g}`",
        f"- Late-screen bias warning: `{str(failure['late_screen_bias_warning']).lower()}`",
        f"- Low-information group count: `{failure['low_information_group_count']}`",
        "",
        "## Group Notes",
    ]
    for row in result.group_rows:
        lines.append(
            "- "
            f"{row.group_type}/{row.group}: "
            f"observed_fraction={row.observed_extirpated_fraction:.6g}, "
            f"insufficient_fraction={row.insufficient_fraction:.6g}, "
            f"note={row.screen_note}"
        )
    lines.extend(
        [
            "",
            "## Limits",
        ]
    )
    for note in summary["limits"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def write_rows(
    columns: tuple[str, ...],
    rows: Any,
    path: Path,
) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(columns)
        csv_writer.writerows(rows)


def median_ints(values: list[int]) -> float | None:
    if not values:
        return None
    midpoint = len(values) // 2
    if len(values) % 2:
        return float(values[midpoint])
    return (values[midpoint - 1] + values[midpoint]) / 2.0


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    payload = loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return payload
