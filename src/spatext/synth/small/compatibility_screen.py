"""Synthetic compatibility screen for synth-small summary vectors."""

from __future__ import annotations

from csv import DictReader, writer
from dataclasses import dataclass, field
from json import dumps, loads
from math import isfinite, sqrt
from os import PathLike
from pathlib import Path
from typing import Any

import numpy as np

from .observations import stringify_float
from .predator import SynthSmallPredatorTruthResult, build_synth_small_predator_truth
from .sensitivity import SensitivityCandidate, config_for_candidate
from .summary_vector import (
    DEFAULT_COVERAGE_BREAKPOINTS,
    SUMMARY_VECTOR_MODES,
    CoverageCurveRow,
    SummaryComponentRow,
    SummaryVectorTargetRow,
    build_coverage_curve_rows,
    build_summary_component_rows,
)

DEFAULT_TARGET_DIR = Path("artifacts/synth_small_summary_vector")
DEFAULT_OUTPUT_DIR = Path("artifacts/synth_small_compatibility_screen")
DEFAULT_COMPATIBILITY_SCREEN_TARGET_DIR = DEFAULT_TARGET_DIR
DEFAULT_COMPATIBILITY_SCREEN_OUTPUT_DIR = DEFAULT_OUTPUT_DIR
PRIMARY_TARGET_MODE = "realistic_observed"
COMPATIBILITY_TARGET_MODES = SUMMARY_VECTOR_MODES
COMPATIBILITY_OUTPUT_FILES = (
    "compatibility_screen_config.json",
    "target_summary.json",
    "candidate_summaries.csv",
    "candidate_scores.csv",
    "coverage_score_breakdown.csv",
    "mode_rankings.csv",
    "verification.json",
    "report.md",
)
REQUIRED_TARGET_FILES = (
    "summary_vector_config.json",
    "summary_components.csv",
    "mode_summary.json",
    "coverage_curve.csv",
    "verification.json",
)
REQUIRED_SCORE_COMPONENTS = (
    "finite_target_fraction",
    "lag_mean",
    "lag_std",
    "arrival_target_r2",
    "front_plane_gradient_magnitude",
)
CANDIDATE_SUMMARY_COLUMNS = (
    "candidate_label",
    "predation_scale",
    "half_saturation",
    "ramp_duration",
    "is_default",
    "component",
    "value",
    "missing_reason",
)
CANDIDATE_SCORE_COLUMNS = (
    "target_mode",
    "candidate_label",
    "is_default",
    "component",
    "target_value",
    "candidate_value",
    "scale",
    "weight",
    "absolute_gap",
    "normalized_abs_gap",
    "weighted_gap",
    "missing_reason",
)
COVERAGE_SCORE_BREAKDOWN_COLUMNS = (
    "target_mode",
    "candidate_label",
    "is_default",
    "coverage_fraction",
    "target_time",
    "candidate_time",
    "absolute_gap",
    "squared_gap",
    "scale",
    "weight",
    "missing_reason",
)
MODE_RANKING_COLUMNS = (
    "target_mode",
    "rank",
    "candidate_label",
    "is_default",
    "predation_scale",
    "half_saturation",
    "ramp_duration",
    "total_weighted_loss",
    "compatibility_class",
    "invalid_reasons",
    "is_primary_target_mode",
)


@dataclass(frozen=True, slots=True)
class GapComponentSetting:
    component: str
    weight: float
    scale: float

    def to_dict(self) -> dict[str, float | str]:
        return {
            "component": self.component,
            "weight": self.weight,
            "scale": self.scale,
        }


DEFAULT_GAP_COMPONENT_SETTINGS = (
    GapComponentSetting("finite_target_fraction", 2.0, 0.25),
    GapComponentSetting("lag_mean", 1.0, 10.0),
    GapComponentSetting("lag_std", 1.0, 5.0),
    GapComponentSetting("arrival_target_r2", 1.0, 0.5),
    GapComponentSetting("front_plane_gradient_magnitude", 1.0, 1.0),
    GapComponentSetting("coverage_curve_rmse", 1.0, 10.0),
)


def default_compatibility_candidates() -> tuple[SensitivityCandidate, ...]:
    """Return the tiny deterministic candidate set for Goal 010."""

    return (
        SensitivityCandidate(
            "weaker_predation",
            predation_scale=0.75,
            half_saturation=6.0,
            ramp_duration=8,
        ),
        SensitivityCandidate(
            "default",
            predation_scale=1.0,
            half_saturation=6.0,
            ramp_duration=8,
            is_default=True,
        ),
        SensitivityCandidate(
            "stronger_predation",
            predation_scale=1.25,
            half_saturation=6.0,
            ramp_duration=8,
        ),
    )


@dataclass(frozen=True, slots=True)
class CompatibilityScreenConfig:
    """Configuration for the synthetic compatibility screen."""

    target_dir: str = str(DEFAULT_TARGET_DIR)
    primary_target_mode: str = PRIMARY_TARGET_MODE
    target_modes: tuple[str, ...] = COMPATIBILITY_TARGET_MODES
    candidates: tuple[SensitivityCandidate, ...] = field(
        default_factory=default_compatibility_candidates
    )
    coverage_breakpoints: tuple[float, ...] = DEFAULT_COVERAGE_BREAKPOINTS
    required_components: tuple[str, ...] = REQUIRED_SCORE_COMPONENTS
    gap_settings: tuple[GapComponentSetting, ...] = DEFAULT_GAP_COMPONENT_SETTINGS
    compatible_loss_max: float = 0.25
    borderline_loss_max: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "synthetic_only": True,
            "screen_name": "synth-small-compatibility-screen",
            "target_dir": self.target_dir,
            "target_modes": list(self.target_modes),
            "primary_target_mode": self.primary_target_mode,
            "candidate_count": len(self.candidates),
            "candidates": [candidate_to_dict(candidate) for candidate in self.candidates],
            "coverage_breakpoints": list(self.coverage_breakpoints),
            "required_components": list(self.required_components),
            "gap_settings": [setting.to_dict() for setting in self.gap_settings],
            "weights": {setting.component: setting.weight for setting in self.gap_settings},
            "scales": {setting.component: setting.scale for setting in self.gap_settings},
            "gates": {
                "finite_target_fraction": "finite_and_positive",
                "lag_mean": "finite",
                "lag_std": "finite_and_positive",
                "arrival_target_r2": "finite",
                "front_plane_gradient_magnitude": "finite",
                "coverage_curve": "finite_for_all_required_breakpoints",
            },
            "compatibility_classes": {
                "compatible": f"loss <= {self.compatible_loss_max}",
                "borderline": (f"{self.compatible_loss_max} < loss <= {self.borderline_loss_max}"),
                "incompatible": f"loss > {self.borderline_loss_max}",
                "invalid": "required values or gates failed",
            },
            "missingness": {
                "required_component_missing": "invalid",
                "coverage_breakpoint_missing": "invalid",
                "invalid_reasons_are_emitted": True,
            },
            "audit_outputs": {
                "coverage_score_breakdown.csv": (
                    "one row per target mode, candidate, and coverage breakpoint "
                    "with target time, candidate time, absolute gap, and squared gap"
                ),
            },
            "not_formal_inference": True,
        }


@dataclass(frozen=True, slots=True)
class LoadedCompatibilityTargetBundle:
    target_dir: Path
    config: dict[str, Any]
    component_rows: tuple[dict[str, str], ...]
    mode_summary: dict[str, Any]
    coverage_rows: tuple[dict[str, str], ...]
    verification: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ScalarValue:
    value: float | None
    missing_reason: str


@dataclass(frozen=True, slots=True)
class CandidateProfile:
    candidate: SensitivityCandidate
    component_rows: tuple[SummaryComponentRow, ...]
    coverage_rows: tuple[CoverageCurveRow, ...]


@dataclass(frozen=True, slots=True)
class CandidateSummaryRow:
    candidate_label: str
    predation_scale: float
    half_saturation: float
    ramp_duration: int
    is_default: bool
    component: str
    value: str
    missing_reason: str

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.candidate_label,
            stringify_float(self.predation_scale),
            stringify_float(self.half_saturation),
            str(self.ramp_duration),
            stringify_bool(self.is_default),
            self.component,
            self.value,
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class CandidateScoreRow:
    target_mode: str
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
    missing_reason: str = ""

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_mode,
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
        )


@dataclass(frozen=True, slots=True)
class CoverageScoreBreakdownRow:
    target_mode: str
    candidate_label: str
    is_default: bool
    coverage_fraction: float
    target_time: float | None
    candidate_time: float | None
    absolute_gap: float | None
    squared_gap: float | None
    scale: float
    weight: float
    missing_reason: str = ""

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_mode,
            self.candidate_label,
            stringify_bool(self.is_default),
            stringify_float(self.coverage_fraction),
            stringify_optional_float(self.target_time),
            stringify_optional_float(self.candidate_time),
            stringify_optional_float(self.absolute_gap),
            stringify_optional_float(self.squared_gap),
            stringify_float(self.scale),
            stringify_float(self.weight),
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class CandidateModeScore:
    target_mode: str
    candidate: SensitivityCandidate
    total_weighted_loss: float | None
    compatibility_class: str
    invalid_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ModeRankingRow:
    target_mode: str
    rank: int
    candidate: SensitivityCandidate
    total_weighted_loss: float | None
    compatibility_class: str
    invalid_reasons: tuple[str, ...]
    is_primary_target_mode: bool

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.target_mode,
            str(self.rank),
            self.candidate.label,
            stringify_bool(self.candidate.is_default),
            stringify_float(self.candidate.predation_scale),
            stringify_float(self.candidate.half_saturation),
            str(self.candidate.ramp_duration),
            stringify_optional_float(self.total_weighted_loss),
            self.compatibility_class,
            ";".join(self.invalid_reasons),
            stringify_bool(self.is_primary_target_mode),
        )


@dataclass(frozen=True, slots=True)
class CompatibilityScreenVerificationCheck:
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
class SynthSmallCompatibilityScreenResult:
    config: CompatibilityScreenConfig
    target_bundle: LoadedCompatibilityTargetBundle
    target_summary: dict[str, Any]
    candidate_summaries: tuple[CandidateSummaryRow, ...]
    score_rows: tuple[CandidateScoreRow, ...]
    coverage_score_rows: tuple[CoverageScoreBreakdownRow, ...]
    ranking_rows: tuple[ModeRankingRow, ...]
    verification_checks: tuple[CompatibilityScreenVerificationCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def write_artifacts(
        self,
        output_dir: str | PathLike[str] = DEFAULT_OUTPUT_DIR,
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "compatibility_screen_config.json"
        target_summary_path = target_dir / "target_summary.json"
        candidate_summaries_path = target_dir / "candidate_summaries.csv"
        candidate_scores_path = target_dir / "candidate_scores.csv"
        coverage_scores_path = target_dir / "coverage_score_breakdown.csv"
        mode_rankings_path = target_dir / "mode_rankings.csv"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(
            dumps(self.config.to_dict(), indent=2) + "\n",
            encoding="utf-8",
        )
        target_summary_path.write_text(
            dumps(self.target_summary, indent=2) + "\n",
            encoding="utf-8",
        )
        write_rows(
            CANDIDATE_SUMMARY_COLUMNS,
            (row.to_csv_row() for row in self.candidate_summaries),
            candidate_summaries_path,
        )
        write_rows(
            CANDIDATE_SCORE_COLUMNS,
            (row.to_csv_row() for row in self.score_rows),
            candidate_scores_path,
        )
        write_rows(
            COVERAGE_SCORE_BREAKDOWN_COLUMNS,
            (row.to_csv_row() for row in self.coverage_score_rows),
            coverage_scores_path,
        )
        write_rows(
            MODE_RANKING_COLUMNS,
            (row.to_csv_row() for row in self.ranking_rows),
            mode_rankings_path,
        )
        verification_path.write_text(
            dumps(
                {
                    "synthetic_only": True,
                    "passed": self.passed,
                    "checks": [check.to_dict() for check in self.verification_checks],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_compatibility_screen_report(self), encoding="utf-8")
        return (
            config_path,
            target_summary_path,
            candidate_summaries_path,
            candidate_scores_path,
            coverage_scores_path,
            mode_rankings_path,
            verification_path,
            report_path,
        )


def build_synth_small_compatibility_screen(
    *,
    target_dir: str | PathLike[str] = DEFAULT_TARGET_DIR,
    candidates: tuple[SensitivityCandidate, ...] | None = None,
    config: CompatibilityScreenConfig | None = None,
) -> SynthSmallCompatibilityScreenResult:
    candidate_set = candidates if candidates is not None else default_compatibility_candidates()
    screen_config = config or CompatibilityScreenConfig(
        target_dir=str(target_dir),
        candidates=candidate_set,
    )
    bundle = load_compatibility_target_bundle(screen_config.target_dir)
    target_components = component_maps_by_mode(bundle.component_rows)
    target_coverage = coverage_maps_by_mode(bundle.coverage_rows)
    profiles = tuple(
        build_candidate_profile(
            candidate,
            coverage_breakpoints=screen_config.coverage_breakpoints,
        )
        for candidate in screen_config.candidates
    )
    candidate_summaries = tuple(
        row for profile in profiles for row in candidate_summary_rows(profile)
    )

    mode_scores: list[CandidateModeScore] = []
    score_rows: list[CandidateScoreRow] = []
    coverage_score_rows: list[CoverageScoreBreakdownRow] = []
    settings_by_component = {setting.component: setting for setting in screen_config.gap_settings}
    for mode in screen_config.target_modes:
        for profile in profiles:
            mode_score, rows, coverage_rows = score_candidate_against_target(
                target_mode=mode,
                target_components=target_components.get(mode, {}),
                target_coverage=target_coverage.get(mode, {}),
                profile=profile,
                config=screen_config,
                settings_by_component=settings_by_component,
            )
            mode_scores.append(mode_score)
            score_rows.extend(rows)
            coverage_score_rows.extend(coverage_rows)

    ranking_rows = build_mode_rankings(mode_scores, config=screen_config)
    target_summary = build_target_summary_payload(
        bundle=bundle,
        config=screen_config,
        target_components=target_components,
        target_coverage=target_coverage,
    )
    verification_checks = verify_compatibility_screen_result(
        config=screen_config,
        bundle=bundle,
        candidate_summaries=candidate_summaries,
        score_rows=tuple(score_rows),
        coverage_score_rows=tuple(coverage_score_rows),
        ranking_rows=ranking_rows,
    )
    return SynthSmallCompatibilityScreenResult(
        config=screen_config,
        target_bundle=bundle,
        target_summary=target_summary,
        candidate_summaries=candidate_summaries,
        score_rows=tuple(score_rows),
        coverage_score_rows=tuple(coverage_score_rows),
        ranking_rows=ranking_rows,
        verification_checks=verification_checks,
    )


def load_compatibility_target_bundle(
    target_dir: str | PathLike[str],
) -> LoadedCompatibilityTargetBundle:
    path = Path(target_dir)
    missing = [name for name in REQUIRED_TARGET_FILES if not (path / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(f"missing required compatibility target artifacts: {missing_text}")
    return LoadedCompatibilityTargetBundle(
        target_dir=path,
        config=read_json(path / "summary_vector_config.json"),
        component_rows=read_csv_rows(path / "summary_components.csv"),
        mode_summary=read_json(path / "mode_summary.json"),
        coverage_rows=read_csv_rows(path / "coverage_curve.csv"),
        verification=read_json(path / "verification.json"),
    )


def build_candidate_profile(
    candidate: SensitivityCandidate,
    *,
    coverage_breakpoints: tuple[float, ...],
) -> CandidateProfile:
    truth = build_synth_small_predator_truth(config_for_candidate(candidate))
    rows = target_rows_from_truth(truth)
    return CandidateProfile(
        candidate=candidate,
        component_rows=build_summary_component_rows(candidate.label, rows),
        coverage_rows=build_coverage_curve_rows(
            mode=candidate.label,
            rows=rows,
            coverage_breakpoints=coverage_breakpoints,
        ),
    )


def target_rows_from_truth(
    truth: SynthSmallPredatorTruthResult,
) -> tuple[SummaryVectorTargetRow, ...]:
    rows: list[SummaryVectorTargetRow] = []
    for cell_id, (row, col) in enumerate(truth.domain.coordinates.tolist()):
        raw_target = float(truth.true_extirpation[row, col])
        rows.append(
            SummaryVectorTargetRow(
                site_id=f"site_{cell_id:03d}",
                cell_id=cell_id,
                grid_row=int(row),
                grid_col=int(col),
                driver_arrival=float(truth.driver_arrival[row, col]),
                target_time=None if not isfinite(raw_target) else raw_target,
            )
        )
    return tuple(rows)


def candidate_summary_rows(profile: CandidateProfile) -> tuple[CandidateSummaryRow, ...]:
    return tuple(
        CandidateSummaryRow(
            candidate_label=profile.candidate.label,
            predation_scale=profile.candidate.predation_scale,
            half_saturation=profile.candidate.half_saturation,
            ramp_duration=profile.candidate.ramp_duration,
            is_default=profile.candidate.is_default,
            component=row.component,
            value=row.value,
            missing_reason=row.missing_reason,
        )
        for row in profile.component_rows
    )


def score_candidate_against_target(
    *,
    target_mode: str,
    target_components: dict[str, ScalarValue],
    target_coverage: dict[float, ScalarValue],
    profile: CandidateProfile,
    config: CompatibilityScreenConfig,
    settings_by_component: dict[str, GapComponentSetting],
) -> tuple[
    CandidateModeScore,
    tuple[CandidateScoreRow, ...],
    tuple[CoverageScoreBreakdownRow, ...],
]:
    candidate_components = {
        row.component: scalar_value(row.value, row.missing_reason) for row in profile.component_rows
    }
    candidate_coverage = {
        row.coverage_fraction: scalar_value(row.target_time, row.missing_reason)
        for row in profile.coverage_rows
    }
    score_rows: list[CandidateScoreRow] = []
    invalid_reasons: list[str] = []
    total_loss = 0.0

    for component in config.required_components:
        setting = settings_by_component[component]
        target_value = target_components.get(component, ScalarValue(None, "missing_component"))
        candidate_value = candidate_components.get(
            component, ScalarValue(None, "missing_component")
        )
        component_reasons = missing_or_gate_reasons(
            component=component,
            target_value=target_value,
            candidate_value=candidate_value,
        )
        invalid_reasons.extend(component_reasons)
        if component_reasons:
            score_rows.append(
                CandidateScoreRow(
                    target_mode=target_mode,
                    candidate_label=profile.candidate.label,
                    is_default=profile.candidate.is_default,
                    component=component,
                    target_value=target_value.value,
                    candidate_value=candidate_value.value,
                    scale=setting.scale,
                    weight=setting.weight,
                    absolute_gap=None,
                    normalized_abs_gap=None,
                    weighted_gap=None,
                    missing_reason=";".join(component_reasons),
                )
            )
            continue

        target_scalar = expect_float(target_value.value)
        candidate_scalar = expect_float(candidate_value.value)
        absolute_gap = abs(candidate_scalar - target_scalar)
        normalized_gap = absolute_gap / setting.scale
        weighted_gap = normalized_gap * setting.weight
        total_loss += weighted_gap
        score_rows.append(
            CandidateScoreRow(
                target_mode=target_mode,
                candidate_label=profile.candidate.label,
                is_default=profile.candidate.is_default,
                component=component,
                target_value=target_scalar,
                candidate_value=candidate_scalar,
                scale=setting.scale,
                weight=setting.weight,
                absolute_gap=absolute_gap,
                normalized_abs_gap=normalized_gap,
                weighted_gap=weighted_gap,
            )
        )

    coverage_setting = settings_by_component["coverage_curve_rmse"]
    coverage_reasons: list[str] = []
    coverage_diffs: list[float] = []
    coverage_breakdown_rows: list[CoverageScoreBreakdownRow] = []
    for breakpoint in config.coverage_breakpoints:
        target_value = target_coverage.get(breakpoint, ScalarValue(None, "missing_breakpoint"))
        candidate_value = candidate_coverage.get(
            breakpoint, ScalarValue(None, "missing_breakpoint")
        )
        breakpoint_reasons: list[str] = []
        if target_value.value is None or not isfinite(target_value.value):
            breakpoint_reasons.append(
                f"target_missing:coverage_curve:{stringify_float(breakpoint)}"
            )
        if candidate_value.value is None or not isfinite(candidate_value.value):
            breakpoint_reasons.append(
                f"candidate_missing:coverage_curve:{stringify_float(breakpoint)}"
            )
        coverage_reasons.extend(breakpoint_reasons)
        if breakpoint_reasons:
            coverage_breakdown_rows.append(
                CoverageScoreBreakdownRow(
                    target_mode=target_mode,
                    candidate_label=profile.candidate.label,
                    is_default=profile.candidate.is_default,
                    coverage_fraction=breakpoint,
                    target_time=target_value.value,
                    candidate_time=candidate_value.value,
                    absolute_gap=None,
                    squared_gap=None,
                    scale=coverage_setting.scale,
                    weight=coverage_setting.weight,
                    missing_reason=";".join(breakpoint_reasons),
                )
            )
            continue

        target_time = expect_float(target_value.value)
        candidate_time = expect_float(candidate_value.value)
        difference = candidate_time - target_time
        absolute_gap = abs(difference)
        squared_gap = difference * difference
        coverage_diffs.append(difference)
        coverage_breakdown_rows.append(
            CoverageScoreBreakdownRow(
                target_mode=target_mode,
                candidate_label=profile.candidate.label,
                is_default=profile.candidate.is_default,
                coverage_fraction=breakpoint,
                target_time=target_time,
                candidate_time=candidate_time,
                absolute_gap=absolute_gap,
                squared_gap=squared_gap,
                scale=coverage_setting.scale,
                weight=coverage_setting.weight,
            )
        )

    invalid_reasons.extend(coverage_reasons)
    if coverage_reasons:
        score_rows.append(
            CandidateScoreRow(
                target_mode=target_mode,
                candidate_label=profile.candidate.label,
                is_default=profile.candidate.is_default,
                component="coverage_curve_rmse",
                target_value=None,
                candidate_value=None,
                scale=coverage_setting.scale,
                weight=coverage_setting.weight,
                absolute_gap=None,
                normalized_abs_gap=None,
                weighted_gap=None,
                missing_reason=";".join(unique_reasons(coverage_reasons)),
            )
        )
    else:
        rmse = sqrt(float(np.mean(np.square(np.array(coverage_diffs, dtype=float)))))
        normalized_gap = rmse / coverage_setting.scale
        weighted_gap = normalized_gap * coverage_setting.weight
        total_loss += weighted_gap
        score_rows.append(
            CandidateScoreRow(
                target_mode=target_mode,
                candidate_label=profile.candidate.label,
                is_default=profile.candidate.is_default,
                component="coverage_curve_rmse",
                target_value=None,
                candidate_value=None,
                scale=coverage_setting.scale,
                weight=coverage_setting.weight,
                absolute_gap=rmse,
                normalized_abs_gap=normalized_gap,
                weighted_gap=weighted_gap,
            )
        )

    reasons = unique_reasons(invalid_reasons)
    return (
        CandidateModeScore(
            target_mode=target_mode,
            candidate=profile.candidate,
            total_weighted_loss=None if reasons else total_loss,
            compatibility_class=compatibility_class(total_loss, reasons, config),
            invalid_reasons=reasons,
        ),
        tuple(score_rows),
        tuple(coverage_breakdown_rows),
    )


def missing_or_gate_reasons(
    *,
    component: str,
    target_value: ScalarValue,
    candidate_value: ScalarValue,
) -> tuple[str, ...]:
    reasons: list[str] = []
    for prefix, value in (("target", target_value), ("candidate", candidate_value)):
        if value.value is None or not isfinite(value.value):
            reasons.append(f"{prefix}_missing:{component}")
            continue
        if value.missing_reason:
            reasons.append(f"{prefix}_missing:{component}")
            continue
        if component in {"finite_target_fraction", "lag_std"} and value.value <= 0.0:
            reasons.append(f"{prefix}_gate:{component}:nonpositive")
    return tuple(reasons)


def build_mode_rankings(
    scores: list[CandidateModeScore],
    *,
    config: CompatibilityScreenConfig,
) -> tuple[ModeRankingRow, ...]:
    output: list[ModeRankingRow] = []
    for mode in config.target_modes:
        mode_scores = [score for score in scores if score.target_mode == mode]
        ranked = sorted(mode_scores, key=score_sort_key)
        output.extend(
            ModeRankingRow(
                target_mode=mode,
                rank=rank,
                candidate=score.candidate,
                total_weighted_loss=score.total_weighted_loss,
                compatibility_class=score.compatibility_class,
                invalid_reasons=score.invalid_reasons,
                is_primary_target_mode=mode == config.primary_target_mode,
            )
            for rank, score in enumerate(ranked, start=1)
        )
    return tuple(output)


def score_sort_key(score: CandidateModeScore) -> tuple[int, float, int, str]:
    return (
        int(score.compatibility_class == "invalid"),
        score.total_weighted_loss if score.total_weighted_loss is not None else float("inf"),
        int(not score.candidate.is_default),
        score.candidate.label,
    )


def compatibility_class(
    total_loss: float,
    invalid_reasons: tuple[str, ...],
    config: CompatibilityScreenConfig,
) -> str:
    if invalid_reasons:
        return "invalid"
    if total_loss <= config.compatible_loss_max:
        return "compatible"
    if total_loss <= config.borderline_loss_max:
        return "borderline"
    return "incompatible"


def build_target_summary_payload(
    *,
    bundle: LoadedCompatibilityTargetBundle,
    config: CompatibilityScreenConfig,
    target_components: dict[str, dict[str, ScalarValue]],
    target_coverage: dict[str, dict[float, ScalarValue]],
) -> dict[str, Any]:
    component_status = {}
    coverage_status = {}
    for mode in config.target_modes:
        component_status[mode] = {
            component: scalar_value_to_dict(
                target_components.get(mode, {}).get(
                    component, ScalarValue(None, "missing_component")
                )
            )
            for component in config.required_components
        }
        coverage_status[mode] = {
            stringify_float(breakpoint): scalar_value_to_dict(
                target_coverage.get(mode, {}).get(
                    breakpoint, ScalarValue(None, "missing_breakpoint")
                )
            )
            for breakpoint in config.coverage_breakpoints
        }
    return {
        "synthetic_only": True,
        "target_dir": str(bundle.target_dir),
        "target_modes": list(config.target_modes),
        "primary_target_mode": config.primary_target_mode,
        "summary_vector_passed": bool(bundle.verification.get("passed")),
        "mode_summaries": bundle.mode_summary.get("mode_summaries", {}),
        "required_component_status": component_status,
        "coverage_status": coverage_status,
        "interpretation": {
            "classification": "synthetic_method_development_only",
            "not_formal_inference": True,
            "notes": [
                "This target summary is consumed by a deterministic compatibility screen.",
                "realistic_observed is the primary review target.",
                "ideal_true remains a synthetic diagnostic target.",
            ],
        },
    }


def verify_compatibility_screen_result(
    *,
    config: CompatibilityScreenConfig,
    bundle: LoadedCompatibilityTargetBundle,
    candidate_summaries: tuple[CandidateSummaryRow, ...],
    score_rows: tuple[CandidateScoreRow, ...],
    coverage_score_rows: tuple[CoverageScoreBreakdownRow, ...],
    ranking_rows: tuple[ModeRankingRow, ...],
) -> tuple[CompatibilityScreenVerificationCheck, ...]:
    target_files_present = all(
        (bundle.target_dir / name).exists() for name in REQUIRED_TARGET_FILES
    )
    component_modes = {row["mode"] for row in bundle.component_rows}
    coverage_modes = {row["mode"] for row in bundle.coverage_rows}
    candidate_labels = {candidate.label for candidate in config.candidates}
    ranking_modes = {row.target_mode for row in ranking_rows}
    valid_modes = {row.target_mode for row in ranking_rows if row.compatibility_class != "invalid"}
    invalid_without_reasons = [
        row.candidate.label
        for row in ranking_rows
        if row.compatibility_class == "invalid" and not row.invalid_reasons
    ]
    expected_coverage_score_rows = (
        len(config.target_modes) * len(config.candidates) * len(config.coverage_breakpoints)
    )
    return (
        CompatibilityScreenVerificationCheck(
            name="target_files",
            passed=target_files_present,
            message="required Goal 009 target summary-vector files are present",
            details={"target_dir": str(bundle.target_dir)},
        ),
        CompatibilityScreenVerificationCheck(
            name="source_summary_vector_verification",
            passed=bool(bundle.verification.get("passed")),
            message="source summary-vector verification passed",
            details={"source_passed": bool(bundle.verification.get("passed"))},
        ),
        CompatibilityScreenVerificationCheck(
            name="target_modes",
            passed=set(config.target_modes) <= component_modes
            and set(config.target_modes) <= coverage_modes,
            message="both compatibility-screen target modes are available",
            details={
                "component_modes": sorted(component_modes),
                "coverage_modes": sorted(coverage_modes),
            },
        ),
        CompatibilityScreenVerificationCheck(
            name="candidate_set",
            passed=len(config.candidates) == 3
            and candidate_labels == {"weaker_predation", "default", "stronger_predation"}
            and sum(candidate.is_default for candidate in config.candidates) == 1,
            message="tiny deterministic candidate set is explicit and includes one default",
            details={"candidate_labels": sorted(candidate_labels)},
        ),
        CompatibilityScreenVerificationCheck(
            name="candidate_summaries",
            passed={row.candidate_label for row in candidate_summaries} == candidate_labels,
            message="candidate summaries were emitted for every candidate",
            details={"summary_row_count": len(candidate_summaries)},
        ),
        CompatibilityScreenVerificationCheck(
            name="score_rows",
            passed={row.component for row in score_rows}
            == set(config.required_components) | {"coverage_curve_rmse"},
            message="weighted-gap score rows include required components and coverage RMSE",
            details={"score_row_count": len(score_rows)},
        ),
        CompatibilityScreenVerificationCheck(
            name="coverage_score_breakdown",
            passed=len(coverage_score_rows) == expected_coverage_score_rows
            and {row.target_mode for row in coverage_score_rows} == set(config.target_modes)
            and {row.candidate_label for row in coverage_score_rows} == candidate_labels,
            message="coverage RMSE audit rows were emitted for every breakpoint",
            details={
                "coverage_score_row_count": len(coverage_score_rows),
                "expected_coverage_score_row_count": expected_coverage_score_rows,
            },
        ),
        CompatibilityScreenVerificationCheck(
            name="mode_rankings",
            passed=ranking_modes == set(config.target_modes)
            and len(ranking_rows) == len(config.target_modes) * len(config.candidates),
            message="rankings were emitted for every candidate in every target mode",
            details={"ranking_row_count": len(ranking_rows)},
        ),
        CompatibilityScreenVerificationCheck(
            name="valid_candidate_per_mode",
            passed=set(config.target_modes) <= valid_modes,
            message="each target mode has at least one valid candidate",
            details={"valid_modes": sorted(valid_modes)},
        ),
        CompatibilityScreenVerificationCheck(
            name="invalid_reasons",
            passed=not invalid_without_reasons,
            message="invalid rows carry explicit reasons",
            details={"invalid_without_reasons": invalid_without_reasons},
        ),
        CompatibilityScreenVerificationCheck(
            name="synthetic_only_labels",
            passed=bool(bundle.config.get("synthetic_only"))
            and bool(bundle.mode_summary.get("synthetic_only")),
            message="target and screen outputs are synthetic-only labelled",
            details={
                "source_config_synthetic_only": bool(bundle.config.get("synthetic_only")),
                "mode_summary_synthetic_only": bool(bundle.mode_summary.get("synthetic_only")),
            },
        ),
    )


def render_compatibility_screen_report(result: SynthSmallCompatibilityScreenResult) -> str:
    class_counts = compatibility_class_counts(result.ranking_rows)
    lines = [
        "# Synth-Small Compatibility Screen",
        "",
        (
            "This synthetic-only screen ranks a tiny deterministic candidate set "
            "against the Goal 009 summary-vector targets. It is not formal "
            "inference, ABC, POM, likelihood fitting, or a posterior claim."
        ),
        "",
        "## Configuration",
        "",
        f"- Target directory: `{result.config.target_dir}`",
        f"- Primary target mode: `{result.config.primary_target_mode}`",
        f"- Candidate count: `{len(result.config.candidates)}`",
        f"- Coverage audit rows: `{len(result.coverage_score_rows)}`",
        f"- Verification: `{'passed' if result.passed else 'failed'}`",
        "",
        "The coverage-curve RMSE contribution is auditable in "
        "`coverage_score_breakdown.csv`, with one row per target mode, "
        "candidate, and coverage breakpoint.",
        "",
        "## Compatibility Classes",
        "",
    ]
    for class_name in ("compatible", "borderline", "incompatible", "invalid"):
        lines.append(f"- `{class_name}`: `{class_counts.get(class_name, 0)}`")

    lines.extend(
        [
            "",
            "## Mode Rankings",
            "",
            ("| Target Mode | Rank | Candidate | Class | Weighted Loss | Invalid Reasons |"),
            "| --- | ---: | --- | --- | ---: | --- |",
        ]
    )
    for row in result.ranking_rows:
        loss = stringify_optional_float(row.total_weighted_loss) or "NA"
        reasons = "; ".join(row.invalid_reasons) if row.invalid_reasons else ""
        lines.append(
            f"| `{row.target_mode}` | `{row.rank}` | `{row.candidate.label}` | "
            f"`{row.compatibility_class}` | `{loss}` | `{reasons}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation Limits",
            "",
            (
                "`realistic_observed` is the primary review target because it carries "
                "the current response-side synthetic target. Differences between "
                "`ideal_true` and `realistic_observed` should be read as information "
                "loss from the observation/reconstruction path, not as posterior "
                "evidence about predator parameters."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def component_maps_by_mode(
    rows: tuple[dict[str, str], ...],
) -> dict[str, dict[str, ScalarValue]]:
    output: dict[str, dict[str, ScalarValue]] = {}
    for row in rows:
        output.setdefault(row["mode"], {})[row["component"]] = scalar_value(
            row["value"],
            row["missing_reason"],
        )
    return output


def coverage_maps_by_mode(
    rows: tuple[dict[str, str], ...],
) -> dict[str, dict[float, ScalarValue]]:
    output: dict[str, dict[float, ScalarValue]] = {}
    for row in rows:
        output.setdefault(row["mode"], {})[float(row["coverage_fraction"])] = scalar_value(
            row["target_time"],
            row["missing_reason"],
        )
    return output


def scalar_value(value: str, missing_reason: str) -> ScalarValue:
    if value == "":
        return ScalarValue(None, missing_reason)
    parsed = float(value)
    return ScalarValue(parsed if isfinite(parsed) else None, missing_reason)


def scalar_value_to_dict(value: ScalarValue) -> dict[str, float | str | None]:
    return {
        "value": value.value,
        "missing_reason": value.missing_reason,
    }


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
    rows: Any,
    output_path: Path,
) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(columns)
        csv_writer.writerows(rows)


def candidate_to_dict(candidate: SensitivityCandidate) -> dict[str, Any]:
    return {
        "label": candidate.label,
        "predation_scale": candidate.predation_scale,
        "half_saturation": candidate.half_saturation,
        "ramp_duration": candidate.ramp_duration,
        "is_default": candidate.is_default,
    }


def compatibility_class_counts(
    rows: tuple[ModeRankingRow, ...],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.compatibility_class] = counts.get(row.compatibility_class, 0) + 1
    return counts


def unique_reasons(reasons: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(reason for reason in reasons if reason))


def expect_float(value: float | None) -> float:
    if value is None:
        raise ValueError("expected finite float")
    return value


def stringify_optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return stringify_float(value)


def stringify_bool(value: bool) -> str:
    return "true" if value else "false"
