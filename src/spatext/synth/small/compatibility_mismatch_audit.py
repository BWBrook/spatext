"""Disk-first audit of the synth-small compatibility mismatch."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from csv import DictReader, writer
from dataclasses import dataclass
from json import dumps, loads
from math import isfinite, sqrt
from os import PathLike
from pathlib import Path
from typing import Any

from .observations import stringify_float

DEFAULT_SUMMARY_VECTOR_DIR = Path("artifacts/synth_small_summary_vector")
DEFAULT_COMPATIBILITY_SCREEN_DIR = Path("artifacts/synth_small_compatibility_screen")
DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR = Path("artifacts/synth_small_response_screen/evaluation")
DEFAULT_COMPATIBILITY_MISMATCH_AUDIT_OUTPUT_DIR = (
    DEFAULT_COMPATIBILITY_SCREEN_DIR / "mismatch_audit"
)
MISMATCH_AUDIT_NAME = "synth-small-compatibility-mismatch-audit"
MISMATCH_AUDIT_TOP_TARGET_MODE = "realistic_observed"
MISMATCH_AUDIT_OUTPUT_FILES = (
    "mismatch_audit_config.json",
    "target_delta_summary.csv",
    "score_contribution_summary.csv",
    "coverage_gap_summary.csv",
    "evaluation_bridge_summary.json",
    "recommendation.json",
    "verification.json",
    "report.md",
)
SUMMARY_VECTOR_REQUIRED_FILES = (
    "summary_components.csv",
    "coverage_curve.csv",
    "mode_summary.json",
    "verification.json",
)
COMPATIBILITY_SCREEN_REQUIRED_FILES = (
    "compatibility_screen_config.json",
    "target_summary.json",
    "candidate_scores.csv",
    "coverage_score_breakdown.csv",
    "mode_rankings.csv",
    "verification.json",
)
EVALUATION_REQUIRED_FILES = (
    "screen_evaluation_summary.json",
    "group_evaluation_summary.csv",
    "site_evaluation_audit.csv",
    "verification.json",
)
TARGET_DELTA_COLUMNS = (
    "summary_type",
    "metric",
    "ideal_true_value",
    "realistic_observed_value",
    "delta",
    "absolute_delta",
    "missing_reason",
)
SCORE_CONTRIBUTION_COLUMNS = (
    "target_mode",
    "candidate_label",
    "rank",
    "component",
    "target_value",
    "candidate_value",
    "absolute_gap",
    "scale",
    "weight",
    "normalized_abs_gap",
    "weighted_gap",
    "loss_share",
    "missing_reason",
)
COVERAGE_GAP_COLUMNS = (
    "target_mode",
    "candidate_label",
    "coverage_fraction",
    "target_time",
    "candidate_time",
    "signed_gap",
    "absolute_gap",
    "squared_gap",
    "rmse",
    "scale",
    "weight",
    "missing_reason",
)


@dataclass(frozen=True, slots=True)
class CompatibilityMismatchAuditConfig:
    """Configuration for the Goal 011 disk-first mismatch audit."""

    summary_vector_dir: str = str(DEFAULT_SUMMARY_VECTOR_DIR)
    compatibility_screen_dir: str = str(DEFAULT_COMPATIBILITY_SCREEN_DIR)
    evaluation_dir: str = str(DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR)
    audit_name: str = MISMATCH_AUDIT_NAME
    top_target_mode: str = MISMATCH_AUDIT_TOP_TARGET_MODE

    def to_dict(self) -> dict[str, Any]:
        return {
            **non_inference_labels(),
            "audit_name": self.audit_name,
            "summary_vector_dir": self.summary_vector_dir,
            "compatibility_screen_dir": self.compatibility_screen_dir,
            "evaluation_dir": self.evaluation_dir,
            "top_target_mode": self.top_target_mode,
            "required_inputs": {
                "summary_vector": list(SUMMARY_VECTOR_REQUIRED_FILES),
                "compatibility_screen": list(COMPATIBILITY_SCREEN_REQUIRED_FILES),
                "response_screen_evaluation": list(EVALUATION_REQUIRED_FILES),
            },
            "output_files": list(MISMATCH_AUDIT_OUTPUT_FILES),
            "interpretation": {
                "classification": "synthetic_method_development_audit",
                "notes": [
                    "This audit explains already-emitted synthetic artifacts.",
                    "It does not change Goal 010 scores, weights, thresholds, ranks, or classes.",
                    "It is not formal inference.",
                ],
            },
        }


@dataclass(frozen=True, slots=True)
class LoadedCompatibilityMismatchAuditInputs:
    summary_vector_dir: Path
    compatibility_screen_dir: Path
    evaluation_dir: Path
    summary_components: tuple[dict[str, str], ...]
    coverage_curve: tuple[dict[str, str], ...]
    mode_summary: dict[str, Any]
    summary_verification: dict[str, Any]
    compatibility_config: dict[str, Any]
    target_summary: dict[str, Any]
    candidate_scores: tuple[dict[str, str], ...]
    coverage_score_breakdown: tuple[dict[str, str], ...]
    mode_rankings: tuple[dict[str, str], ...]
    compatibility_verification: dict[str, Any]
    evaluation_summary: dict[str, Any]
    group_evaluation_rows: tuple[dict[str, str], ...]
    site_evaluation_rows: tuple[dict[str, str], ...]
    evaluation_verification: dict[str, Any]


@dataclass(frozen=True, slots=True)
class TargetDeltaSummaryRow:
    summary_type: str
    metric: str
    ideal_true_value: float | None
    realistic_observed_value: float | None
    delta: float | None
    absolute_delta: float | None
    missing_reason: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.summary_type,
            self.metric,
            stringify_optional_float(self.ideal_true_value),
            stringify_optional_float(self.realistic_observed_value),
            stringify_optional_float(self.delta),
            stringify_optional_float(self.absolute_delta),
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class ScoreContributionSummaryRow:
    target_mode: str
    candidate_label: str
    rank: int
    component: str
    target_value: float | None
    candidate_value: float | None
    absolute_gap: float | None
    scale: float | None
    weight: float | None
    normalized_abs_gap: float | None
    weighted_gap: float | None
    loss_share: float | None
    missing_reason: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_mode,
            self.candidate_label,
            str(self.rank),
            self.component,
            stringify_optional_float(self.target_value),
            stringify_optional_float(self.candidate_value),
            stringify_optional_float(self.absolute_gap),
            stringify_optional_float(self.scale),
            stringify_optional_float(self.weight),
            stringify_optional_float(self.normalized_abs_gap),
            stringify_optional_float(self.weighted_gap),
            stringify_optional_float(self.loss_share),
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class CoverageGapSummaryRow:
    target_mode: str
    candidate_label: str
    coverage_fraction: float
    target_time: float | None
    candidate_time: float | None
    signed_gap: float | None
    absolute_gap: float | None
    squared_gap: float | None
    rmse: float | None
    scale: float | None
    weight: float | None
    missing_reason: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_mode,
            self.candidate_label,
            stringify_float(self.coverage_fraction),
            stringify_optional_float(self.target_time),
            stringify_optional_float(self.candidate_time),
            stringify_optional_float(self.signed_gap),
            stringify_optional_float(self.absolute_gap),
            stringify_optional_float(self.squared_gap),
            stringify_optional_float(self.rmse),
            stringify_optional_float(self.scale),
            stringify_optional_float(self.weight),
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class CompatibilityMismatchAuditCheck:
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
class SynthSmallCompatibilityMismatchAuditResult:
    config: CompatibilityMismatchAuditConfig
    inputs: LoadedCompatibilityMismatchAuditInputs
    top_ranking_row: dict[str, str]
    target_delta_rows: tuple[TargetDeltaSummaryRow, ...]
    score_contribution_rows: tuple[ScoreContributionSummaryRow, ...]
    coverage_gap_rows: tuple[CoverageGapSummaryRow, ...]
    evaluation_bridge_summary: dict[str, Any]
    recommendation: dict[str, Any]
    verification_checks: tuple[CompatibilityMismatchAuditCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    @property
    def top_candidate_label(self) -> str:
        return self.top_ranking_row["candidate_label"]

    def config_payload(self) -> dict[str, Any]:
        return {
            **self.config.to_dict(),
            "top_candidate_label": self.top_candidate_label,
            "source_verifications": source_verifications(self.inputs),
        }

    def verification_payload(self) -> dict[str, Any]:
        return {
            **non_inference_labels(),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
        }

    def write_artifacts(
        self,
        output_dir: str | PathLike[str] = DEFAULT_COMPATIBILITY_MISMATCH_AUDIT_OUTPUT_DIR,
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "mismatch_audit_config.json"
        target_delta_path = target_dir / "target_delta_summary.csv"
        score_contribution_path = target_dir / "score_contribution_summary.csv"
        coverage_gap_path = target_dir / "coverage_gap_summary.csv"
        bridge_path = target_dir / "evaluation_bridge_summary.json"
        recommendation_path = target_dir / "recommendation.json"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(dumps(self.config_payload(), indent=2) + "\n", encoding="utf-8")
        write_rows(
            TARGET_DELTA_COLUMNS,
            (row.to_csv_row() for row in self.target_delta_rows),
            target_delta_path,
        )
        write_rows(
            SCORE_CONTRIBUTION_COLUMNS,
            (row.to_csv_row() for row in self.score_contribution_rows),
            score_contribution_path,
        )
        write_rows(
            COVERAGE_GAP_COLUMNS,
            (row.to_csv_row() for row in self.coverage_gap_rows),
            coverage_gap_path,
        )
        bridge_path.write_text(
            dumps(self.evaluation_bridge_summary, indent=2) + "\n",
            encoding="utf-8",
        )
        recommendation_path.write_text(
            dumps(self.recommendation, indent=2) + "\n",
            encoding="utf-8",
        )
        verification_path.write_text(
            dumps(self.verification_payload(), indent=2) + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_mismatch_audit_report(self), encoding="utf-8")
        return (
            config_path,
            target_delta_path,
            score_contribution_path,
            coverage_gap_path,
            bridge_path,
            recommendation_path,
            verification_path,
            report_path,
        )


def build_synth_small_compatibility_mismatch_audit(
    *,
    summary_vector_dir: str | PathLike[str] = DEFAULT_SUMMARY_VECTOR_DIR,
    compatibility_screen_dir: str | PathLike[str] = DEFAULT_COMPATIBILITY_SCREEN_DIR,
    evaluation_dir: str | PathLike[str] = DEFAULT_RESPONSE_SCREEN_EVALUATION_DIR,
    config: CompatibilityMismatchAuditConfig | None = None,
) -> SynthSmallCompatibilityMismatchAuditResult:
    audit_config = config or CompatibilityMismatchAuditConfig(
        summary_vector_dir=str(summary_vector_dir),
        compatibility_screen_dir=str(compatibility_screen_dir),
        evaluation_dir=str(evaluation_dir),
    )
    inputs = load_compatibility_mismatch_audit_inputs(
        summary_vector_dir=audit_config.summary_vector_dir,
        compatibility_screen_dir=audit_config.compatibility_screen_dir,
        evaluation_dir=audit_config.evaluation_dir,
    )
    top_ranking_row = top_ranking_for_mode(inputs.mode_rankings, audit_config.top_target_mode)
    target_delta_rows = build_target_delta_rows(inputs)
    score_contribution_rows = build_score_contribution_rows(
        candidate_scores=inputs.candidate_scores,
        top_ranking_row=top_ranking_row,
    )
    coverage_gap_rows = build_coverage_gap_rows(
        coverage_rows=inputs.coverage_score_breakdown,
        top_ranking_row=top_ranking_row,
    )
    evaluation_bridge_summary = build_evaluation_bridge_summary(inputs)
    recommendation = build_recommendation_payload(
        inputs=inputs,
        top_ranking_row=top_ranking_row,
        score_contribution_rows=score_contribution_rows,
        evaluation_bridge_summary=evaluation_bridge_summary,
    )
    checks = verify_mismatch_audit_result(
        inputs=inputs,
        top_ranking_row=top_ranking_row,
        score_contribution_rows=score_contribution_rows,
        coverage_gap_rows=coverage_gap_rows,
        evaluation_bridge_summary=evaluation_bridge_summary,
        recommendation=recommendation,
    )
    return SynthSmallCompatibilityMismatchAuditResult(
        config=audit_config,
        inputs=inputs,
        top_ranking_row=top_ranking_row,
        target_delta_rows=target_delta_rows,
        score_contribution_rows=score_contribution_rows,
        coverage_gap_rows=coverage_gap_rows,
        evaluation_bridge_summary=evaluation_bridge_summary,
        recommendation=recommendation,
        verification_checks=checks,
    )


def load_compatibility_mismatch_audit_inputs(
    *,
    summary_vector_dir: str | PathLike[str],
    compatibility_screen_dir: str | PathLike[str],
    evaluation_dir: str | PathLike[str],
) -> LoadedCompatibilityMismatchAuditInputs:
    summary_dir = Path(summary_vector_dir)
    compatibility_dir = Path(compatibility_screen_dir)
    eval_dir = Path(evaluation_dir)
    assert_required_files(summary_dir, SUMMARY_VECTOR_REQUIRED_FILES, "summary-vector")
    assert_required_files(
        compatibility_dir,
        COMPATIBILITY_SCREEN_REQUIRED_FILES,
        "compatibility-screen",
    )
    assert_required_files(eval_dir, EVALUATION_REQUIRED_FILES, "response-screen evaluation")
    return LoadedCompatibilityMismatchAuditInputs(
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        evaluation_dir=eval_dir,
        summary_components=read_csv_rows(summary_dir / "summary_components.csv"),
        coverage_curve=read_csv_rows(summary_dir / "coverage_curve.csv"),
        mode_summary=read_json(summary_dir / "mode_summary.json"),
        summary_verification=read_json(summary_dir / "verification.json"),
        compatibility_config=read_json(compatibility_dir / "compatibility_screen_config.json"),
        target_summary=read_json(compatibility_dir / "target_summary.json"),
        candidate_scores=read_csv_rows(compatibility_dir / "candidate_scores.csv"),
        coverage_score_breakdown=read_csv_rows(compatibility_dir / "coverage_score_breakdown.csv"),
        mode_rankings=read_csv_rows(compatibility_dir / "mode_rankings.csv"),
        compatibility_verification=read_json(compatibility_dir / "verification.json"),
        evaluation_summary=read_json(eval_dir / "screen_evaluation_summary.json"),
        group_evaluation_rows=read_csv_rows(eval_dir / "group_evaluation_summary.csv"),
        site_evaluation_rows=read_csv_rows(eval_dir / "site_evaluation_audit.csv"),
        evaluation_verification=read_json(eval_dir / "verification.json"),
    )


def build_target_delta_rows(
    inputs: LoadedCompatibilityMismatchAuditInputs,
) -> tuple[TargetDeltaSummaryRow, ...]:
    component_rows_by_mode = rows_by_key(
        inputs.summary_components,
        mode_key="mode",
        value_key="component",
    )
    coverage_rows_by_mode = rows_by_key(
        inputs.coverage_curve,
        mode_key="mode",
        value_key="coverage_fraction",
    )
    components = ordered_unique(row["component"] for row in inputs.summary_components)
    coverage_fractions = ordered_unique(row["coverage_fraction"] for row in inputs.coverage_curve)
    rows: list[TargetDeltaSummaryRow] = []

    for component in components:
        rows.append(
            target_delta_row(
                summary_type="component",
                metric=component,
                ideal_row=component_rows_by_mode.get("ideal_true", {}).get(component),
                realistic_row=component_rows_by_mode.get("realistic_observed", {}).get(component),
                value_column="value",
            )
        )
    for coverage_fraction in coverage_fractions:
        rows.append(
            target_delta_row(
                summary_type="coverage_curve",
                metric=f"coverage_target_time:{coverage_fraction}",
                ideal_row=coverage_rows_by_mode.get("ideal_true", {}).get(coverage_fraction),
                realistic_row=coverage_rows_by_mode.get("realistic_observed", {}).get(
                    coverage_fraction
                ),
                value_column="target_time",
            )
        )
    return tuple(rows)


def target_delta_row(
    *,
    summary_type: str,
    metric: str,
    ideal_row: dict[str, str] | None,
    realistic_row: dict[str, str] | None,
    value_column: str,
) -> TargetDeltaSummaryRow:
    ideal_value = row_optional_float(ideal_row, value_column)
    realistic_value = row_optional_float(realistic_row, value_column)
    delta = (
        None if ideal_value is None or realistic_value is None else realistic_value - ideal_value
    )
    return TargetDeltaSummaryRow(
        summary_type=summary_type,
        metric=metric,
        ideal_true_value=ideal_value,
        realistic_observed_value=realistic_value,
        delta=delta,
        absolute_delta=None if delta is None else abs(delta),
        missing_reason=combined_missing_reason(ideal_row, realistic_row),
    )


def build_score_contribution_rows(
    *,
    candidate_scores: tuple[dict[str, str], ...],
    top_ranking_row: dict[str, str],
) -> tuple[ScoreContributionSummaryRow, ...]:
    target_mode = top_ranking_row["target_mode"]
    candidate_label = top_ranking_row["candidate_label"]
    selected = [
        row
        for row in candidate_scores
        if row["target_mode"] == target_mode and row["candidate_label"] == candidate_label
    ]
    total_loss = sum(
        value
        for value in (parse_optional_float(row["weighted_gap"]) for row in selected)
        if value is not None
    )
    sorted_rows = sorted(
        selected,
        key=lambda row: (
            -(parse_optional_float(row["weighted_gap"]) or 0.0),
            row["component"],
        ),
    )
    output: list[ScoreContributionSummaryRow] = []
    for rank, row in enumerate(sorted_rows, start=1):
        weighted_gap = parse_optional_float(row["weighted_gap"])
        output.append(
            ScoreContributionSummaryRow(
                target_mode=target_mode,
                candidate_label=candidate_label,
                rank=rank,
                component=row["component"],
                target_value=parse_optional_float(row["target_value"]),
                candidate_value=parse_optional_float(row["candidate_value"]),
                absolute_gap=parse_optional_float(row["absolute_gap"]),
                scale=parse_optional_float(row["scale"]),
                weight=parse_optional_float(row["weight"]),
                normalized_abs_gap=parse_optional_float(row["normalized_abs_gap"]),
                weighted_gap=weighted_gap,
                loss_share=(
                    None if weighted_gap is None or total_loss <= 0.0 else weighted_gap / total_loss
                ),
                missing_reason=row["missing_reason"],
            )
        )
    return tuple(output)


def build_coverage_gap_rows(
    *,
    coverage_rows: tuple[dict[str, str], ...],
    top_ranking_row: dict[str, str],
) -> tuple[CoverageGapSummaryRow, ...]:
    target_mode = top_ranking_row["target_mode"]
    candidate_label = top_ranking_row["candidate_label"]
    selected = sorted(
        (
            row
            for row in coverage_rows
            if row["target_mode"] == target_mode and row["candidate_label"] == candidate_label
        ),
        key=lambda row: parse_optional_float(row["coverage_fraction"]) or 0.0,
    )
    squared_gaps = [
        value
        for value in (parse_optional_float(row["squared_gap"]) for row in selected)
        if value is not None
    ]
    rmse = sqrt(sum(squared_gaps) / len(squared_gaps)) if squared_gaps else None
    output: list[CoverageGapSummaryRow] = []
    for row in selected:
        target_time = parse_optional_float(row["target_time"])
        candidate_time = parse_optional_float(row["candidate_time"])
        signed_gap = (
            None if target_time is None or candidate_time is None else candidate_time - target_time
        )
        output.append(
            CoverageGapSummaryRow(
                target_mode=target_mode,
                candidate_label=candidate_label,
                coverage_fraction=parse_required_float(row["coverage_fraction"]),
                target_time=target_time,
                candidate_time=candidate_time,
                signed_gap=signed_gap,
                absolute_gap=parse_optional_float(row["absolute_gap"]),
                squared_gap=parse_optional_float(row["squared_gap"]),
                rmse=rmse,
                scale=parse_optional_float(row["scale"]),
                weight=parse_optional_float(row["weight"]),
                missing_reason=row["missing_reason"],
            )
        )
    return tuple(output)


def build_evaluation_bridge_summary(
    inputs: LoadedCompatibilityMismatchAuditInputs,
) -> dict[str, Any]:
    ideal_count = finite_target_count(inputs.summary_components, "ideal_true")
    realistic_count = finite_target_count(inputs.summary_components, "realistic_observed")
    finite_drop = (
        None if ideal_count is None or realistic_count is None else ideal_count - realistic_count
    )
    matrix = confusion_matrix(inputs.evaluation_summary)
    false_negative_count = int_payload(
        dict_payload(inputs.evaluation_summary.get("classification")).get("false_negative_count"),
        fallback=matrix.get("fn", 0),
    )
    bridge_difference = None if finite_drop is None else finite_drop - false_negative_count
    bridge_fraction = (
        None if finite_drop is None or finite_drop <= 0 else false_negative_count / finite_drop
    )
    failure_modes = dict_payload(inputs.evaluation_summary.get("failure_modes"))
    return {
        **non_inference_labels(),
        "screen_decision": inputs.evaluation_summary.get("screen_decision"),
        "site_count": inputs.evaluation_summary.get("site_count"),
        "ideal_true_finite_target_count": ideal_count,
        "realistic_observed_finite_target_count": realistic_count,
        "finite_target_drop": finite_drop,
        "confusion_matrix": matrix,
        "false_negative_count": false_negative_count,
        "false_positive_count": matrix.get("fp", 0),
        "false_negative_bridge_difference": bridge_difference,
        "false_negative_bridge_fraction": bridge_fraction,
        "bridge_class": bridge_class(
            finite_drop=finite_drop,
            false_negative_count=false_negative_count,
            bridge_difference=bridge_difference,
            bridge_fraction=bridge_fraction,
        ),
        "failure_modes": failure_modes,
        "group_evaluation_row_count": len(inputs.group_evaluation_rows),
        "site_evaluation_row_count": len(inputs.site_evaluation_rows),
        "interpretation": {
            "classification": "synthetic_method_development_bridge",
            "notes": [
                "The bridge compares finite target loss to response-screen false negatives.",
                "It explains an emitted compatibility-screen mismatch and does not fit a model.",
            ],
        },
    }


def build_recommendation_payload(
    *,
    inputs: LoadedCompatibilityMismatchAuditInputs,
    top_ranking_row: dict[str, str],
    score_contribution_rows: tuple[ScoreContributionSummaryRow, ...],
    evaluation_bridge_summary: dict[str, Any],
) -> dict[str, Any]:
    ideal_default = ranking_for(inputs.mode_rankings, "ideal_true", "default")
    realistic_rows = [
        row for row in inputs.mode_rankings if row["target_mode"] == MISMATCH_AUDIT_TOP_TARGET_MODE
    ]
    all_realistic_incompatible = bool(realistic_rows) and all(
        row["compatibility_class"] == "incompatible" for row in realistic_rows
    )
    ideal_default_class = None if ideal_default is None else ideal_default["compatibility_class"]
    bridge_fraction = evaluation_bridge_summary.get("false_negative_bridge_fraction")
    source_passed = all(source_verifications(inputs).values())
    recommendation_class = choose_recommendation_class(
        source_passed=source_passed,
        ideal_default_class=ideal_default_class,
        all_realistic_incompatible=all_realistic_incompatible,
        bridge_fraction=bridge_fraction if isinstance(bridge_fraction, float) else None,
    )
    dominant_components = [
        row.component
        for row in score_contribution_rows
        if row.weighted_gap is not None and row.weighted_gap > 0.0
    ]
    return {
        **non_inference_labels(),
        "recommendation_class": recommendation_class,
        "top_target_mode": top_ranking_row["target_mode"],
        "top_candidate_label": top_ranking_row["candidate_label"],
        "top_candidate_loss": parse_optional_float(top_ranking_row["total_weighted_loss"]),
        "top_candidate_class": top_ranking_row["compatibility_class"],
        "ideal_default_class": ideal_default_class,
        "all_realistic_candidates_incompatible": all_realistic_incompatible,
        "realistic_candidate_classes": {
            row["candidate_label"]: row["compatibility_class"] for row in realistic_rows
        },
        "dominant_mismatch_components": dominant_components,
        "finite_target_drop": evaluation_bridge_summary["finite_target_drop"],
        "false_negative_count": evaluation_bridge_summary["false_negative_count"],
        "false_negative_bridge_fraction": bridge_fraction,
        "bridge_class": evaluation_bridge_summary["bridge_class"],
        "rationale": recommendation_rationale(
            recommendation_class,
            dominant_components=dominant_components,
            bridge_summary=evaluation_bridge_summary,
        ),
    }


def verify_mismatch_audit_result(
    *,
    inputs: LoadedCompatibilityMismatchAuditInputs,
    top_ranking_row: dict[str, str],
    score_contribution_rows: tuple[ScoreContributionSummaryRow, ...],
    coverage_gap_rows: tuple[CoverageGapSummaryRow, ...],
    evaluation_bridge_summary: dict[str, Any],
    recommendation: dict[str, Any],
) -> tuple[CompatibilityMismatchAuditCheck, ...]:
    source_passed = source_verifications(inputs)
    ideal_default = ranking_for(inputs.mode_rankings, "ideal_true", "default")
    realistic_rows = [
        row for row in inputs.mode_rankings if row["target_mode"] == MISMATCH_AUDIT_TOP_TARGET_MODE
    ]
    coverage_score = score_row_for(
        inputs.candidate_scores,
        target_mode=top_ranking_row["target_mode"],
        candidate_label=top_ranking_row["candidate_label"],
        component="coverage_curve_rmse",
    )
    reconstructed_rmse = coverage_gap_rows[0].rmse if coverage_gap_rows else None
    source_rmse = (
        None if coverage_score is None else parse_optional_float(coverage_score["absolute_gap"])
    )
    finite_drop = evaluation_bridge_summary.get("finite_target_drop")
    false_negative_count = evaluation_bridge_summary.get("false_negative_count")
    return (
        CompatibilityMismatchAuditCheck(
            name="source_verifications",
            passed=all(source_passed.values()),
            message="all prerequisite source verification payloads passed",
            details=source_passed,
        ),
        CompatibilityMismatchAuditCheck(
            name="top_realistic_candidate",
            passed=top_ranking_row["target_mode"] == MISMATCH_AUDIT_TOP_TARGET_MODE
            and top_ranking_row["rank"] == "1"
            and bool(top_ranking_row["candidate_label"]),
            message="top ranked realistic_observed candidate was identified from disk",
            details={
                "target_mode": top_ranking_row["target_mode"],
                "candidate_label": top_ranking_row["candidate_label"],
                "compatibility_class": top_ranking_row["compatibility_class"],
            },
        ),
        CompatibilityMismatchAuditCheck(
            name="ideal_default_compatible",
            passed=ideal_default is not None
            and ideal_default["compatibility_class"] == "compatible",
            message="ideal_true default remains a compatibility-screen positive control",
            details={} if ideal_default is None else dict(ideal_default),
        ),
        CompatibilityMismatchAuditCheck(
            name="all_realistic_candidates_incompatible",
            passed=bool(realistic_rows)
            and all(row["compatibility_class"] == "incompatible" for row in realistic_rows),
            message="all realistic_observed candidates are incompatible in Goal 010 output",
            details={row["candidate_label"]: row["compatibility_class"] for row in realistic_rows},
        ),
        CompatibilityMismatchAuditCheck(
            name="score_contributions_present",
            passed=bool(score_contribution_rows)
            and all(
                row.target_mode == MISMATCH_AUDIT_TOP_TARGET_MODE for row in score_contribution_rows
            ),
            message="score contribution rows were emitted for the top realistic candidate",
            details={"score_contribution_row_count": len(score_contribution_rows)},
        ),
        CompatibilityMismatchAuditCheck(
            name="coverage_rmse_reconstructs",
            passed=source_rmse is not None
            and reconstructed_rmse is not None
            and abs(source_rmse - reconstructed_rmse) <= 1e-9,
            message="coverage_gap_summary reconstructs the Goal 010 coverage RMSE",
            details={
                "source_rmse": source_rmse,
                "reconstructed_rmse": reconstructed_rmse,
                "coverage_gap_row_count": len(coverage_gap_rows),
            },
        ),
        CompatibilityMismatchAuditCheck(
            name="finite_target_false_negative_bridge",
            passed=isinstance(finite_drop, int)
            and isinstance(false_negative_count, int)
            and evaluation_bridge_summary["bridge_class"]
            == "finite_target_drop_matches_false_negatives",
            message="finite-target drop is bridged to response-screen false negatives",
            details={
                "finite_target_drop": finite_drop,
                "false_negative_count": false_negative_count,
                "bridge_class": evaluation_bridge_summary["bridge_class"],
            },
        ),
        CompatibilityMismatchAuditCheck(
            name="recommendation_label",
            passed=recommendation["recommendation_class"]
            == "diagnose_observation_reconstruction_before_abc",
            message="current audit recommends observation/reconstruction diagnosis before ABC",
            details={"recommendation_class": recommendation["recommendation_class"]},
        ),
    )


def top_ranking_for_mode(
    mode_rankings: tuple[dict[str, str], ...],
    target_mode: str,
) -> dict[str, str]:
    matching = [
        row for row in mode_rankings if row["target_mode"] == target_mode and row["rank"] == "1"
    ]
    if len(matching) != 1:
        raise ValueError(f"expected one rank-1 row for target mode {target_mode!r}")
    return matching[0]


def ranking_for(
    mode_rankings: tuple[dict[str, str], ...],
    target_mode: str,
    candidate_label: str,
) -> dict[str, str] | None:
    for row in mode_rankings:
        if row["target_mode"] == target_mode and row["candidate_label"] == candidate_label:
            return row
    return None


def score_row_for(
    candidate_scores: tuple[dict[str, str], ...],
    *,
    target_mode: str,
    candidate_label: str,
    component: str,
) -> dict[str, str] | None:
    for row in candidate_scores:
        if (
            row["target_mode"] == target_mode
            and row["candidate_label"] == candidate_label
            and row["component"] == component
        ):
            return row
    return None


def rows_by_key(
    rows: tuple[dict[str, str], ...],
    *,
    mode_key: str,
    value_key: str,
) -> dict[str, dict[str, dict[str, str]]]:
    output: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        output.setdefault(row[mode_key], {})[row[value_key]] = row
    return output


def finite_target_count(
    component_rows: tuple[dict[str, str], ...],
    mode: str,
) -> int | None:
    for row in component_rows:
        if row["mode"] == mode and row["component"] == "finite_target_count":
            value = parse_optional_float(row["value"])
            if value is None:
                return None
            return round(value)
    return None


def source_verifications(inputs: LoadedCompatibilityMismatchAuditInputs) -> dict[str, bool]:
    return {
        "summary_vector": bool(inputs.summary_verification.get("passed")),
        "compatibility_screen": bool(inputs.compatibility_verification.get("passed")),
        "response_screen_evaluation": bool(inputs.evaluation_verification.get("passed")),
    }


def confusion_matrix(evaluation_summary: dict[str, Any]) -> dict[str, int]:
    classification = dict_payload(evaluation_summary.get("classification"))
    raw_matrix = dict_payload(classification.get("confusion_matrix"))
    return {key: int_payload(raw_matrix.get(key), fallback=0) for key in ("tp", "fp", "tn", "fn")}


def bridge_class(
    *,
    finite_drop: int | None,
    false_negative_count: int,
    bridge_difference: int | None,
    bridge_fraction: float | None,
) -> str:
    if finite_drop is None or bridge_difference is None or bridge_fraction is None:
        return "insufficient_bridge_inputs"
    if finite_drop <= 0:
        return "no_finite_target_drop"
    if bridge_difference == 0:
        return "finite_target_drop_matches_false_negatives"
    if bridge_fraction >= 0.8:
        return "finite_target_drop_largely_explained_by_false_negatives"
    if false_negative_count > 0:
        return "finite_target_drop_partly_explained_by_false_negatives"
    return "finite_target_drop_not_explained_by_false_negatives"


def choose_recommendation_class(
    *,
    source_passed: bool,
    ideal_default_class: str | None,
    all_realistic_incompatible: bool,
    bridge_fraction: float | None,
) -> str:
    if not source_passed or ideal_default_class != "compatible":
        return "screen_contract_bug_suspected"
    if all_realistic_incompatible and bridge_fraction is not None and bridge_fraction >= 0.8:
        return "diagnose_observation_reconstruction_before_abc"
    if all_realistic_incompatible:
        return "candidate_expansion_may_be_warranted"
    return "ready_for_next_inference_design"


def recommendation_rationale(
    recommendation_class: str,
    *,
    dominant_components: list[str],
    bridge_summary: dict[str, Any],
) -> list[str]:
    if recommendation_class == "diagnose_observation_reconstruction_before_abc":
        return [
            (
                "The ideal_true default candidate remains compatible, so the "
                "deterministic simulator path still acts as a positive control."
            ),
            (
                "All realistic_observed candidates remain incompatible, with "
                "dominant weighted gaps from "
            )
            + ", ".join(dominant_components[:3])
            + ".",
            (
                "The finite-target drop equals the response-screen false-negative "
                "count, so the mismatch is explained before any candidate "
                "expansion or inference."
            ),
            "This is not an ABC, POM, likelihood, posterior, or parameter-recovery result.",
        ]
    if recommendation_class == "candidate_expansion_may_be_warranted":
        return [
            (
                "The positive-control screen is intact, but the false-negative "
                "bridge does not explain most realistic-observed mismatch."
            ),
            "Candidate expansion may be considered later under a separate bounded goal.",
            "This is not an ABC, POM, likelihood, posterior, or parameter-recovery result.",
        ]
    if recommendation_class == "ready_for_next_inference_design":
        return [
            "Both target modes avoid the current incompatibility warning.",
            "A later bounded goal may design the next inference step.",
            "This is not an ABC, POM, likelihood, posterior, or parameter-recovery result.",
        ]
    return [
        "A prerequisite verification or ranking invariant did not match the expected contract.",
        f"Bridge class: {bridge_summary.get('bridge_class')}.",
        "This is not an ABC, POM, likelihood, posterior, or parameter-recovery result.",
    ]


def render_mismatch_audit_report(result: SynthSmallCompatibilityMismatchAuditResult) -> str:
    bridge = result.evaluation_bridge_summary
    recommendation = result.recommendation
    lines = [
        "# Synth-Small Compatibility Mismatch Audit",
        "",
        "## Scope",
        "",
        (
            "This is a synthetic-only, disk-first audit of the Goal 010 "
            "`realistic_observed` compatibility mismatch. It does not change "
            "screen scores, thresholds, ranks, classes, or candidate settings."
        ),
        "",
        "## Result",
        "",
        f"- Top realistic_observed candidate: `{result.top_candidate_label}`",
        f"- Top realistic_observed class: `{result.top_ranking_row['compatibility_class']}`",
        f"- Recommendation: `{recommendation['recommendation_class']}`",
        f"- Finite-target drop: `{bridge['finite_target_drop']}`",
        f"- Response-screen false negatives: `{bridge['false_negative_count']}`",
        f"- Bridge class: `{bridge['bridge_class']}`",
        "",
        "## Dominant Score Components",
        "",
    ]
    for row in result.score_contribution_rows[:3]:
        lines.append(
            f"- `{row.component}`: weighted_gap=`{stringify_optional_float(row.weighted_gap)}`"
        )
    lines.extend(
        [
            "",
            "## Coverage RMSE Audit",
            "",
            (
                "`coverage_gap_summary.csv` carries one row per coverage "
                "breakpoint with target time, candidate time, signed gap, "
                "squared gap, and reconstructed RMSE."
            ),
            "",
            "## Interpretation Limit",
            "",
            (
                "The recommendation is a method-development diagnostic before "
                "ABC/POM or any broader inference design."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def non_inference_labels() -> dict[str, bool]:
    return {
        "synthetic_only": True,
        "audit_only": True,
        "not_formal_inference": True,
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


def row_optional_float(row: dict[str, str] | None, key: str) -> float | None:
    if row is None:
        return None
    return parse_optional_float(row[key])


def parse_optional_float(value: str) -> float | None:
    if value == "":
        return None
    parsed = float(value)
    return parsed if isfinite(parsed) else None


def parse_required_float(value: str) -> float:
    parsed = parse_optional_float(value)
    if parsed is None:
        raise ValueError("expected finite float")
    return parsed


def stringify_optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return stringify_float(value)


def combined_missing_reason(
    ideal_row: dict[str, str] | None,
    realistic_row: dict[str, str] | None,
) -> str:
    reasons: list[str] = []
    if ideal_row is None:
        reasons.append("ideal_true:missing_row")
    elif ideal_row.get("missing_reason"):
        reasons.append(f"ideal_true:{ideal_row['missing_reason']}")
    if realistic_row is None:
        reasons.append("realistic_observed:missing_row")
    elif realistic_row.get("missing_reason"):
        reasons.append(f"realistic_observed:{realistic_row['missing_reason']}")
    return ";".join(reasons)


def ordered_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def dict_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def int_payload(value: Any, *, fallback: int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value:
        return int(value)
    return fallback
