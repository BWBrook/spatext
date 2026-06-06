"""Synthetic-only evaluation audit for synth-small response-screen artifacts."""

from __future__ import annotations

from collections import defaultdict
from csv import DictReader, writer
from dataclasses import dataclass
from json import dumps, loads
from os import PathLike
from pathlib import Path
from typing import Any

from .observations import parse_bool, parse_int, parse_optional_float, stringify_float
from .reconstruction import parse_optional_int
from .response_screen import DEFAULT_OUTPUT_DIR as DEFAULT_SCREEN_DIR
from .response_screen_inspect import load_response_screen_artifact_bundle

DEFAULT_RECONSTRUCTION_DIR = Path("artifacts/synth_small_extirpation_reconstruction")
DEFAULT_OBSERVATION_DIR = Path("artifacts/synth_small_observations")
DEFAULT_EVALUATION_DIR = DEFAULT_SCREEN_DIR / "evaluation"

EVALUATION_OUTPUT_FILES = (
    "evaluation_config.json",
    "screen_evaluation_summary.json",
    "group_evaluation_summary.csv",
    "site_evaluation_audit.csv",
    "verification.json",
    "report.md",
)
SITE_EVALUATION_COLUMNS = (
    "site_id",
    "cell_id",
    "row",
    "col",
    "region",
    "front_band",
    "screen_call",
    "true_extirpated_by_end",
    "audit_classification",
    "observed_extirpation_time",
    "true_extirpation_time",
)
GROUP_EVALUATION_COLUMNS = (
    "group_type",
    "group",
    "site_count",
    "screen_observed_count",
    "true_extirpated_count",
    "tp",
    "fp",
    "tn",
    "fn",
    "sensitivity",
    "specificity",
    "precision",
    "false_negative_fraction",
    "screen_note",
)


@dataclass(frozen=True, slots=True)
class ResponseScreenEvaluationConfig:
    screen_dir: str = str(DEFAULT_SCREEN_DIR)
    reconstruction_dir: str = str(DEFAULT_RECONSTRUCTION_DIR)
    observation_dir: str = str(DEFAULT_OBSERVATION_DIR)
    evaluation_name: str = "synth-small-response-screen-evaluation"

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluation_only": True,
            "evaluation_name": self.evaluation_name,
            "screen_dir": self.screen_dir,
            "reconstruction_dir": self.reconstruction_dir,
            "observation_dir": self.observation_dir,
        }


@dataclass(frozen=True, slots=True)
class SiteEvaluationRow:
    site_id: str
    cell_id: int
    row: int
    col: int
    region: str
    front_band: str
    screen_call: bool
    true_extirpated_by_end: bool
    audit_classification: str
    observed_extirpation_time: int | None
    true_extirpation_time: float | None

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.site_id,
            str(self.cell_id),
            str(self.row),
            str(self.col),
            self.region,
            self.front_band,
            str(self.screen_call).lower(),
            str(self.true_extirpated_by_end).lower(),
            self.audit_classification,
            "" if self.observed_extirpation_time is None else str(self.observed_extirpation_time),
            ""
            if self.true_extirpation_time is None
            else stringify_float(self.true_extirpation_time),
        )


@dataclass(frozen=True, slots=True)
class GroupEvaluationRow:
    group_type: str
    group: str
    site_count: int
    screen_observed_count: int
    true_extirpated_count: int
    tp: int
    fp: int
    tn: int
    fn: int
    sensitivity: float | None
    specificity: float | None
    precision: float | None
    false_negative_fraction: float
    screen_note: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.group_type,
            self.group,
            str(self.site_count),
            str(self.screen_observed_count),
            str(self.true_extirpated_count),
            str(self.tp),
            str(self.fp),
            str(self.tn),
            str(self.fn),
            "" if self.sensitivity is None else stringify_float(self.sensitivity),
            "" if self.specificity is None else stringify_float(self.specificity),
            "" if self.precision is None else stringify_float(self.precision),
            stringify_float(self.false_negative_fraction),
            self.screen_note,
        )


@dataclass(frozen=True, slots=True)
class ResponseScreenEvaluationCheck:
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
class ResponseScreenEvaluationResult:
    config: ResponseScreenEvaluationConfig
    summary: dict[str, Any]
    group_rows: tuple[GroupEvaluationRow, ...]
    site_rows: tuple[SiteEvaluationRow, ...]
    verification_checks: tuple[ResponseScreenEvaluationCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def write_artifacts(
        self,
        output_dir: str | PathLike[str] = DEFAULT_EVALUATION_DIR,
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "evaluation_config.json"
        summary_path = target_dir / "screen_evaluation_summary.json"
        group_path = target_dir / "group_evaluation_summary.csv"
        site_path = target_dir / "site_evaluation_audit.csv"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(
            dumps({"evaluation_only": True, "config": self.config.to_dict()}, indent=2) + "\n",
            encoding="utf-8",
        )
        summary_path.write_text(dumps(self.summary, indent=2) + "\n", encoding="utf-8")
        write_rows(
            GROUP_EVALUATION_COLUMNS, (row.to_csv_row() for row in self.group_rows), group_path
        )
        write_rows(SITE_EVALUATION_COLUMNS, (row.to_csv_row() for row in self.site_rows), site_path)
        verification_path.write_text(
            dumps(
                {
                    "evaluation_only": True,
                    "passed": self.passed,
                    "checks": [check.to_dict() for check in self.verification_checks],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_response_screen_evaluation_report(self), encoding="utf-8")
        return (
            config_path,
            summary_path,
            group_path,
            site_path,
            verification_path,
            report_path,
        )


def evaluate_synth_small_response_screen(
    *,
    screen_dir: str | PathLike[str] = DEFAULT_SCREEN_DIR,
    reconstruction_dir: str | PathLike[str] = DEFAULT_RECONSTRUCTION_DIR,
    observation_dir: str | PathLike[str] = DEFAULT_OBSERVATION_DIR,
) -> ResponseScreenEvaluationResult:
    config = ResponseScreenEvaluationConfig(
        screen_dir=str(screen_dir),
        reconstruction_dir=str(reconstruction_dir),
        observation_dir=str(observation_dir),
    )
    screen_bundle = load_response_screen_artifact_bundle(screen_dir)
    reconstruction_rows = read_csv_rows(Path(reconstruction_dir) / "site_reconstruction.csv")
    evaluation_metrics = read_json(Path(reconstruction_dir) / "evaluation_metrics.json")
    truth_rows = read_csv_rows(Path(observation_dir) / "evaluation_truth.csv")

    site_rows = build_site_evaluation_rows(reconstruction_rows, truth_rows)
    screen_notes = screen_notes_by_group(screen_bundle.group_rows)
    group_rows = build_group_evaluation_rows(site_rows, screen_notes)
    summary = build_evaluation_summary(screen_bundle.screen_summary, site_rows, group_rows)
    checks = verify_response_screen_evaluation(
        screen_summary=screen_bundle.screen_summary,
        evaluation_metrics=evaluation_metrics,
        site_rows=site_rows,
        group_rows=group_rows,
        summary=summary,
    )

    return ResponseScreenEvaluationResult(
        config=config,
        summary=summary,
        group_rows=group_rows,
        site_rows=site_rows,
        verification_checks=checks,
    )


def build_site_evaluation_rows(
    reconstruction_rows: tuple[dict[str, str], ...],
    truth_rows: tuple[dict[str, str], ...],
) -> tuple[SiteEvaluationRow, ...]:
    truth_by_site = {row["site_id"]: row for row in truth_rows}
    rows: list[SiteEvaluationRow] = []
    for row in reconstruction_rows:
        truth = truth_by_site[row["site_id"]]
        screen_call = parse_bool(row["observed_extirpated_by_end"])
        true_extirpated = parse_bool(truth["extirpated_by_end"])
        rows.append(
            SiteEvaluationRow(
                site_id=row["site_id"],
                cell_id=parse_int(row["cell_id"]),
                row=parse_int(row["row"]),
                col=parse_int(row["col"]),
                region=row["region"],
                front_band=row["front_band"],
                screen_call=screen_call,
                true_extirpated_by_end=true_extirpated,
                audit_classification=classify_site(screen_call, true_extirpated),
                observed_extirpation_time=parse_optional_int(row["observed_extirpation_time"]),
                true_extirpation_time=parse_optional_float(truth["true_extirpation"]),
            )
        )
    return tuple(rows)


def build_group_evaluation_rows(
    site_rows: tuple[SiteEvaluationRow, ...],
    screen_notes: dict[tuple[str, str], str],
) -> tuple[GroupEvaluationRow, ...]:
    grouped: dict[tuple[str, str], list[SiteEvaluationRow]] = defaultdict(list)
    for row in site_rows:
        grouped[("region", row.region)].append(row)
        grouped[("front_band", row.front_band)].append(row)

    rows: list[GroupEvaluationRow] = []
    for group_type, group in sorted(grouped):
        members = grouped[(group_type, group)]
        matrix = confusion_from_rows(members)
        metrics = classification_metrics(matrix)
        true_extirpated_count = matrix["tp"] + matrix["fn"]
        rows.append(
            GroupEvaluationRow(
                group_type=group_type,
                group=group,
                site_count=len(members),
                screen_observed_count=matrix["tp"] + matrix["fp"],
                true_extirpated_count=true_extirpated_count,
                tp=matrix["tp"],
                fp=matrix["fp"],
                tn=matrix["tn"],
                fn=matrix["fn"],
                sensitivity=metrics["sensitivity"],
                specificity=metrics["specificity"],
                precision=metrics["precision"],
                false_negative_fraction=(
                    matrix["fn"] / true_extirpated_count if true_extirpated_count else 0.0
                ),
                screen_note=screen_notes.get((group_type, group), "not_reported"),
            )
        )
    return tuple(rows)


def build_evaluation_summary(
    screen_summary: dict[str, Any],
    site_rows: tuple[SiteEvaluationRow, ...],
    group_rows: tuple[GroupEvaluationRow, ...],
) -> dict[str, Any]:
    matrix = confusion_from_rows(site_rows)
    metrics = classification_metrics(matrix)
    false_negative_groups = [
        {
            "group_type": row.group_type,
            "group": row.group,
            "false_negative_fraction": row.false_negative_fraction,
            "screen_note": row.screen_note,
        }
        for row in group_rows
        if row.false_negative_fraction >= 0.5 and row.true_extirpated_count > 0
    ]
    weak_signal_groups = [
        {
            "group_type": row.group_type,
            "group": row.group,
            "screen_note": row.screen_note,
            "sensitivity": row.sensitivity,
        }
        for row in group_rows
        if row.screen_note in {"weak_observed_extirpation_signal", "no_observed_extirpation"}
    ]
    return {
        "evaluation_only": True,
        "screen_decision": screen_summary["screen_decision"],
        "site_count": len(site_rows),
        "classification": {
            "confusion_matrix": matrix,
            "sensitivity": metrics["sensitivity"],
            "specificity": metrics["specificity"],
            "precision": metrics["precision"],
            "false_negative_count": matrix["fn"],
            "false_positive_count": matrix["fp"],
        },
        "failure_modes": {
            "false_negative_group_count": len(false_negative_groups),
            "weak_signal_group_count": len(weak_signal_groups),
            "false_negative_groups": false_negative_groups,
            "weak_signal_groups": weak_signal_groups,
        },
        "interpretation": {
            "classification": "synthetic_evaluation_only",
            "notes": [
                "This audit uses synthetic evaluation truth after screen emission.",
                "It does not change the response-only screen decision.",
                "False negatives and weak eastern signal are method-development diagnostics.",
            ],
        },
    }


def verify_response_screen_evaluation(
    *,
    screen_summary: dict[str, Any],
    evaluation_metrics: dict[str, Any],
    site_rows: tuple[SiteEvaluationRow, ...],
    group_rows: tuple[GroupEvaluationRow, ...],
    summary: dict[str, Any],
) -> tuple[ResponseScreenEvaluationCheck, ...]:
    computed_matrix = summary["classification"]["confusion_matrix"]
    expected_matrix = evaluation_metrics.get("confusion_matrix", {})
    return (
        ResponseScreenEvaluationCheck(
            name="evaluation_namespace",
            passed=summary["evaluation_only"] is True,
            message="evaluation summary is explicitly labelled evaluation-only",
            details={"evaluation_only": summary["evaluation_only"]},
        ),
        ResponseScreenEvaluationCheck(
            name="screen_decision_preserved",
            passed=summary["screen_decision"] == screen_summary.get("screen_decision"),
            message="response-screen decision is copied, not recomputed",
            details={"screen_decision": summary["screen_decision"]},
        ),
        ResponseScreenEvaluationCheck(
            name="classification_matches_goal005_metrics",
            passed=computed_matrix == expected_matrix,
            message="site-level audit matches existing Goal 005 evaluation metrics",
            details={"computed": computed_matrix, "expected": expected_matrix},
        ),
        ResponseScreenEvaluationCheck(
            name="site_rows_complete",
            passed=len(site_rows) == summary["site_count"] and bool(site_rows),
            message="site audit rows align with summary site count",
            details={"site_row_count": len(site_rows), "summary_site_count": summary["site_count"]},
        ),
        ResponseScreenEvaluationCheck(
            name="group_rows_complete",
            passed=bool(group_rows),
            message="group evaluation rows were computed",
            details={"group_row_count": len(group_rows)},
        ),
    )


def classify_site(screen_call: bool, true_extirpated: bool) -> str:
    if screen_call and true_extirpated:
        return "tp"
    if screen_call and not true_extirpated:
        return "fp"
    if (not screen_call) and true_extirpated:
        return "fn"
    return "tn"


def confusion_from_rows(
    rows: tuple[SiteEvaluationRow, ...] | list[SiteEvaluationRow],
) -> dict[str, int]:
    matrix = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for row in rows:
        matrix[row.audit_classification] += 1
    return matrix


def classification_metrics(matrix: dict[str, int]) -> dict[str, float | None]:
    tp = matrix["tp"]
    fp = matrix["fp"]
    tn = matrix["tn"]
    fn = matrix["fn"]
    return {
        "sensitivity": tp / (tp + fn) if (tp + fn) else None,
        "specificity": tn / (tn + fp) if (tn + fp) else None,
        "precision": tp / (tp + fp) if (tp + fp) else None,
    }


def screen_notes_by_group(rows: tuple[dict[str, str], ...]) -> dict[tuple[str, str], str]:
    return {(row["group_type"], row["group"]): row["screen_note"] for row in rows}


def render_response_screen_evaluation_report(result: ResponseScreenEvaluationResult) -> str:
    summary = result.summary
    matrix = summary["classification"]["confusion_matrix"]
    lines = [
        "# Synth-Small Response Screen Evaluation",
        "",
        "## Scope",
        "",
        "This is a synthetic-only evaluation audit.",
        "It uses evaluation truth after response-screen artifacts already exist.",
        "It does not change the response-only screen decision or fit a model.",
        "",
        "## Summary",
        f"- Screen decision: `{summary['screen_decision']}`",
        f"- Site count: `{summary['site_count']}`",
        f"- TP / FP / TN / FN: `{matrix['tp']} / {matrix['fp']} / {matrix['tn']} / {matrix['fn']}`",
        f"- Sensitivity: `{value_or_na(summary['classification']['sensitivity'])}`",
        f"- Specificity: `{value_or_na(summary['classification']['specificity'])}`",
        f"- Precision: `{value_or_na(summary['classification']['precision'])}`",
        "",
        "## Failure Modes",
    ]
    for group in summary["failure_modes"]["weak_signal_groups"]:
        lines.append(
            "- "
            f"{group['group_type']}/{group['group']}: "
            f"screen_note={group['screen_note']}, "
            f"sensitivity={value_or_na(group['sensitivity'])}"
        )
    return "\n".join(lines) + "\n"


def value_or_na(value: float | None) -> str:
    if value is None:
        return "NA"
    return f"{value:.6g}"


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
