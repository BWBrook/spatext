from __future__ import annotations

from csv import writer
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from json import dumps
from os import PathLike
from pathlib import Path
from typing import Any, TypedDict

import numpy as np
from numpy.typing import NDArray

from .predator import (
    SynthSmallPredatorTruthConfig,
    SynthSmallPredatorTruthResult,
    build_synth_small_predator_truth,
    default_synth_small_predator_truth_config,
)

DEFAULT_OUTPUT_DIR = Path("artifacts/synth_small_predator_truth_sensitivity")
FloatArray = NDArray[np.float64]


class CandidateMetrics(TypedDict):
    verification_passed: bool
    extirpated_fraction: float
    surviving_fraction: float
    lag_min: float | None
    lag_max: float | None
    lag_mean: float | None
    lag_std: float | None
    low_initial_extirpation_rate: float
    high_initial_extirpation_rate: float
    west_band_extirpated_count: float
    east_band_extirpated_count: float
    final_abundance_mean: float
    used_nonnegative_clipping: bool


@dataclass(frozen=True, slots=True)
class SensitivityCandidate:
    label: str
    predation_scale: float
    half_saturation: float
    ramp_duration: int
    is_default: bool = False


@dataclass(frozen=True, slots=True)
class ReadinessCriteria:
    extirpated_fraction_min: float = 0.20
    extirpated_fraction_max: float = 0.80
    target_extirpated_fraction: float = 0.40
    lag_std_min: float = 2.0
    lag_std_score_target: float = 8.0
    required_pass_count_for_review: int = 4

    def to_dict(self) -> dict[str, float | int]:
        return {
            "extirpated_fraction_min": self.extirpated_fraction_min,
            "extirpated_fraction_max": self.extirpated_fraction_max,
            "target_extirpated_fraction": self.target_extirpated_fraction,
            "lag_std_min": self.lag_std_min,
            "lag_std_score_target": self.lag_std_score_target,
            "required_pass_count_for_review": self.required_pass_count_for_review,
        }


@dataclass(frozen=True, slots=True)
class SensitivityResultRow:
    label: str
    predation_scale: float
    half_saturation: float
    ramp_duration: int
    is_default: bool
    verification_passed: bool
    extirpated_fraction: float
    surviving_fraction: float
    lag_min: float | None
    lag_max: float | None
    lag_mean: float | None
    lag_std: float | None
    low_initial_extirpation_rate: float
    high_initial_extirpation_rate: float
    west_band_extirpated_count: int
    east_band_extirpated_count: int
    final_abundance_mean: float
    used_nonnegative_clipping: bool
    criterion_verification: bool
    criterion_extirpated_fraction: bool
    criterion_lag_variation: bool
    criterion_vulnerability_gradient: bool
    criterion_west_exceeds_east: bool
    criterion_no_clipping: bool
    criteria_passed: int
    readiness_classification: str
    readiness_score: float

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.label,
            stringify_value(self.predation_scale),
            stringify_value(self.half_saturation),
            stringify_value(self.ramp_duration),
            stringify_value(self.is_default),
            stringify_value(self.verification_passed),
            stringify_value(self.extirpated_fraction),
            stringify_value(self.surviving_fraction),
            stringify_value(self.lag_min),
            stringify_value(self.lag_max),
            stringify_value(self.lag_mean),
            stringify_value(self.lag_std),
            stringify_value(self.low_initial_extirpation_rate),
            stringify_value(self.high_initial_extirpation_rate),
            stringify_value(self.west_band_extirpated_count),
            stringify_value(self.east_band_extirpated_count),
            stringify_value(self.final_abundance_mean),
            stringify_value(self.used_nonnegative_clipping),
            stringify_value(self.criterion_verification),
            stringify_value(self.criterion_extirpated_fraction),
            stringify_value(self.criterion_lag_variation),
            stringify_value(self.criterion_vulnerability_gradient),
            stringify_value(self.criterion_west_exceeds_east),
            stringify_value(self.criterion_no_clipping),
            stringify_value(self.criteria_passed),
            self.readiness_classification,
            stringify_value(self.readiness_score),
        )

    def to_dict(self) -> dict[str, str | int | float | bool | None]:
        return {
            "label": self.label,
            "predation_scale": self.predation_scale,
            "half_saturation": self.half_saturation,
            "ramp_duration": self.ramp_duration,
            "is_default": self.is_default,
            "verification_passed": self.verification_passed,
            "extirpated_fraction": self.extirpated_fraction,
            "surviving_fraction": self.surviving_fraction,
            "lag_min": self.lag_min,
            "lag_max": self.lag_max,
            "lag_mean": self.lag_mean,
            "lag_std": self.lag_std,
            "low_initial_extirpation_rate": self.low_initial_extirpation_rate,
            "high_initial_extirpation_rate": self.high_initial_extirpation_rate,
            "west_band_extirpated_count": self.west_band_extirpated_count,
            "east_band_extirpated_count": self.east_band_extirpated_count,
            "final_abundance_mean": self.final_abundance_mean,
            "used_nonnegative_clipping": self.used_nonnegative_clipping,
            "criteria_passed": self.criteria_passed,
            "readiness_classification": self.readiness_classification,
            "readiness_score": self.readiness_score,
        }


@dataclass(frozen=True, slots=True)
class SensitivityRunResult:
    output_dir: Path
    rows: tuple[SensitivityResultRow, ...]
    rankings: tuple[SensitivityResultRow, ...]
    default_row: SensitivityResultRow
    best_row: SensitivityResultRow
    readiness_path: Path
    sweep_results_path: Path
    candidate_rankings_path: Path
    decision_memo_path: Path


CSV_HEADER = (
    "label",
    "predation_scale",
    "half_saturation",
    "ramp_duration",
    "is_default",
    "verification_passed",
    "extirpated_fraction",
    "surviving_fraction",
    "lag_min",
    "lag_max",
    "lag_mean",
    "lag_std",
    "low_initial_extirpation_rate",
    "high_initial_extirpation_rate",
    "west_band_extirpated_count",
    "east_band_extirpated_count",
    "final_abundance_mean",
    "used_nonnegative_clipping",
    "criterion_verification",
    "criterion_extirpated_fraction",
    "criterion_lag_variation",
    "criterion_vulnerability_gradient",
    "criterion_west_exceeds_east",
    "criterion_no_clipping",
    "criteria_passed",
    "readiness_classification",
    "readiness_score",
)


def default_sensitivity_candidates() -> tuple[SensitivityCandidate, ...]:
    candidates: list[SensitivityCandidate] = []
    for predation_scale in (0.75, 1.0, 1.25):
        for half_saturation in (4.0, 6.0, 8.0):
            for ramp_duration in (6, 8, 10):
                is_default = (
                    predation_scale == 1.0 and half_saturation == 6.0 and ramp_duration == 8
                )
                label = (
                    "default"
                    if is_default
                    else (f"pred{predation_scale:g}_half{half_saturation:g}_ramp{ramp_duration}")
                )
                candidates.append(
                    SensitivityCandidate(
                        label=label,
                        predation_scale=predation_scale,
                        half_saturation=half_saturation,
                        ramp_duration=ramp_duration,
                        is_default=is_default,
                    )
                )
    return tuple(candidates)


def run_predator_truth_sensitivity(
    output_dir: str | PathLike[str] = DEFAULT_OUTPUT_DIR,
    *,
    candidates: tuple[SensitivityCandidate, ...] | None = None,
    criteria: ReadinessCriteria | None = None,
) -> SensitivityRunResult:
    sweep_candidates = candidates or default_sensitivity_candidates()
    readiness_criteria = criteria or ReadinessCriteria()
    if not any(candidate.is_default for candidate in sweep_candidates):
        raise ValueError("sensitivity sweep must include an explicitly labelled default candidate")

    rows = tuple(
        evaluate_candidate(candidate, criteria=readiness_criteria) for candidate in sweep_candidates
    )
    rankings = tuple(sorted(rows, key=ranking_key))
    default_row = next(row for row in rows if row.is_default)
    best_row = rankings[0]

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    sweep_results_path = target_dir / "sweep_results.csv"
    candidate_rankings_path = target_dir / "candidate_rankings.csv"
    readiness_path = target_dir / "readiness.json"
    decision_memo_path = target_dir / "decision_memo.md"

    write_rows_csv(rows, sweep_results_path)
    write_rows_csv(rankings, candidate_rankings_path, include_rank=True)
    readiness_path.write_text(
        dumps(
            readiness_payload(
                rows,
                rankings,
                default_row,
                best_row,
                readiness_criteria,
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    decision_memo_path.write_text(
        render_decision_memo(rows, rankings, default_row, best_row, readiness_criteria),
        encoding="utf-8",
    )

    return SensitivityRunResult(
        output_dir=target_dir,
        rows=rows,
        rankings=rankings,
        default_row=default_row,
        best_row=best_row,
        readiness_path=readiness_path,
        sweep_results_path=sweep_results_path,
        candidate_rankings_path=candidate_rankings_path,
        decision_memo_path=decision_memo_path,
    )


def evaluate_candidate(
    candidate: SensitivityCandidate,
    *,
    criteria: ReadinessCriteria,
) -> SensitivityResultRow:
    result = build_synth_small_predator_truth(config_for_candidate(candidate))
    metrics = extract_metrics(result)
    criterion_verification = bool(metrics["verification_passed"])
    criterion_extirpated_fraction = bool(
        criteria.extirpated_fraction_min
        <= float(metrics["extirpated_fraction"])
        <= criteria.extirpated_fraction_max
    )
    lag_std = metrics["lag_std"]
    criterion_lag_variation = bool(lag_std is not None and lag_std >= criteria.lag_std_min)
    criterion_vulnerability_gradient = bool(
        float(metrics["low_initial_extirpation_rate"])
        > float(metrics["high_initial_extirpation_rate"])
    )
    criterion_west_exceeds_east = bool(
        int(metrics["west_band_extirpated_count"]) > int(metrics["east_band_extirpated_count"])
    )
    criterion_no_clipping = not bool(metrics["used_nonnegative_clipping"])
    criterion_values = (
        criterion_verification,
        criterion_extirpated_fraction,
        criterion_lag_variation,
        criterion_vulnerability_gradient,
        criterion_west_exceeds_east,
        criterion_no_clipping,
    )
    criteria_passed = sum(int(value) for value in criterion_values)
    readiness_classification = classify_readiness(
        criterion_verification=criterion_verification,
        criteria_passed=criteria_passed,
        total_criteria=len(criterion_values),
        criteria=criteria,
    )
    readiness_score = score_candidate(
        metrics,
        criteria=criteria,
        criterion_values=criterion_values,
    )

    return SensitivityResultRow(
        label=candidate.label,
        predation_scale=candidate.predation_scale,
        half_saturation=candidate.half_saturation,
        ramp_duration=candidate.ramp_duration,
        is_default=candidate.is_default,
        verification_passed=criterion_verification,
        extirpated_fraction=float(metrics["extirpated_fraction"]),
        surviving_fraction=float(metrics["surviving_fraction"]),
        lag_min=nullable_float(metrics["lag_min"]),
        lag_max=nullable_float(metrics["lag_max"]),
        lag_mean=nullable_float(metrics["lag_mean"]),
        lag_std=nullable_float(metrics["lag_std"]),
        low_initial_extirpation_rate=float(metrics["low_initial_extirpation_rate"]),
        high_initial_extirpation_rate=float(metrics["high_initial_extirpation_rate"]),
        west_band_extirpated_count=int(metrics["west_band_extirpated_count"]),
        east_band_extirpated_count=int(metrics["east_band_extirpated_count"]),
        final_abundance_mean=float(metrics["final_abundance_mean"]),
        used_nonnegative_clipping=bool(metrics["used_nonnegative_clipping"]),
        criterion_verification=criterion_verification,
        criterion_extirpated_fraction=criterion_extirpated_fraction,
        criterion_lag_variation=criterion_lag_variation,
        criterion_vulnerability_gradient=criterion_vulnerability_gradient,
        criterion_west_exceeds_east=criterion_west_exceeds_east,
        criterion_no_clipping=criterion_no_clipping,
        criteria_passed=criteria_passed,
        readiness_classification=readiness_classification,
        readiness_score=readiness_score,
    )


def config_for_candidate(candidate: SensitivityCandidate) -> SynthSmallPredatorTruthConfig:
    base = default_synth_small_predator_truth_config()
    return replace(
        base,
        pressure=replace(base.pressure, ramp_duration=candidate.ramp_duration),
        response=replace(
            base.response,
            predation_scale=candidate.predation_scale,
            half_saturation=candidate.half_saturation,
        ),
    )


def extract_metrics(result: SynthSmallPredatorTruthResult) -> CandidateMetrics:
    extirpated = np.isfinite(result.true_extirpation)
    extirpated_count = int(np.sum(extirpated))
    cell_count = result.domain.cell_count
    finite_lag = result.extirpation_lag[np.isfinite(result.extirpation_lag)]
    low_threshold, high_threshold = np.quantile(result.initial_abundance, [0.25, 0.75])
    low_mask = result.initial_abundance <= low_threshold
    high_mask = result.initial_abundance >= high_threshold
    west_mask = np.zeros(result.initial_abundance.shape, dtype=np.bool_)
    east_mask = np.zeros(result.initial_abundance.shape, dtype=np.bool_)
    west_mask[:, :5] = True
    east_mask[:, -5:] = True
    return {
        "verification_passed": verify_result_contract(result),
        "extirpated_fraction": extirpated_count / cell_count,
        "surviving_fraction": (cell_count - extirpated_count) / cell_count,
        "lag_min": finite_optional(finite_lag, np.min),
        "lag_max": finite_optional(finite_lag, np.max),
        "lag_mean": finite_optional(finite_lag, np.mean),
        "lag_std": finite_optional(finite_lag, np.std),
        "low_initial_extirpation_rate": float(np.mean(extirpated[low_mask])),
        "high_initial_extirpation_rate": float(np.mean(extirpated[high_mask])),
        "west_band_extirpated_count": float(np.sum(extirpated[west_mask])),
        "east_band_extirpated_count": float(np.sum(extirpated[east_mask])),
        "final_abundance_mean": float(np.mean(result.final_abundance)),
        "used_nonnegative_clipping": result.diagnostics.used_nonnegative_clipping,
    }


def verify_result_contract(result: SynthSmallPredatorTruthResult) -> bool:
    extirpated = np.isfinite(result.true_extirpation)
    surviving = ~extirpated
    lag_matches = True
    no_negative_lag = True
    if np.any(extirpated):
        expected_lag = result.true_extirpation[extirpated] - result.driver_arrival[extirpated]
        lag_matches = bool(
            np.allclose(result.extirpation_lag[extirpated], expected_lag, atol=1e-9, rtol=1e-9)
        )
        no_negative_lag = bool(np.all(expected_lag >= -1e-12))
    return bool(
        result.diagnostics.stayed_finite
        and result.diagnostics.stayed_nonnegative
        and result.baseline.diagnostics.converged
        and np.isfinite(result.predator_pressure).all()
        and np.isfinite(result.prey_abundance).all()
        and float(np.min(result.prey_abundance)) >= -1e-12
        and np.isfinite(result.driver_arrival).all()
        and np.isfinite(result.extirpation_lag[extirpated]).all()
        and np.isnan(result.extirpation_lag[surviving]).all()
        and lag_matches
        and no_negative_lag
    )


def classify_readiness(
    *,
    criterion_verification: bool,
    criteria_passed: int,
    total_criteria: int,
    criteria: ReadinessCriteria,
) -> str:
    if criterion_verification and criteria_passed == total_criteria:
        return "observation_ready"
    if criterion_verification and criteria_passed >= criteria.required_pass_count_for_review:
        return "review"
    return "not_ready"


def score_candidate(
    metrics: CandidateMetrics,
    *,
    criteria: ReadinessCriteria,
    criterion_values: tuple[bool, ...],
) -> float:
    if not bool(metrics["verification_passed"]):
        return -1.0

    extirpated_fraction = float(metrics["extirpated_fraction"])
    extirpation_score = 1.0 - min(
        abs(extirpated_fraction - criteria.target_extirpated_fraction)
        / criteria.target_extirpated_fraction,
        1.0,
    )
    lag_std = metrics["lag_std"]
    lag_score = 0.0 if lag_std is None else min(float(lag_std) / criteria.lag_std_score_target, 1.0)
    vulnerability_score = max(
        0.0,
        min(
            float(metrics["low_initial_extirpation_rate"])
            - float(metrics["high_initial_extirpation_rate"]),
            1.0,
        ),
    )
    west_count = float(metrics["west_band_extirpated_count"])
    east_count = float(metrics["east_band_extirpated_count"])
    west_score = max(0.0, (west_count - east_count) / max(west_count + east_count, 1.0))
    criteria_score = sum(int(value) for value in criterion_values) / len(criterion_values)
    no_clipping_score = 0.0 if bool(metrics["used_nonnegative_clipping"]) else 1.0
    return (
        (2.0 * extirpation_score)
        + (1.5 * lag_score)
        + (2.0 * vulnerability_score)
        + west_score
        + no_clipping_score
        + criteria_score
    )


def ranking_key(row: SensitivityResultRow) -> tuple[float, int, float]:
    return (-row.readiness_score, int(not row.is_default), row.extirpated_fraction)


def write_rows_csv(
    rows: tuple[SensitivityResultRow, ...],
    output_path: Path,
    *,
    include_rank: bool = False,
) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        if include_rank:
            csv_writer.writerow(("rank", *CSV_HEADER))
            for rank, row in enumerate(rows, start=1):
                csv_writer.writerow((str(rank), *row.to_csv_row()))
        else:
            csv_writer.writerow(CSV_HEADER)
            for row in rows:
                csv_writer.writerow(row.to_csv_row())


def readiness_payload(
    rows: tuple[SensitivityResultRow, ...],
    rankings: tuple[SensitivityResultRow, ...],
    default_row: SensitivityResultRow,
    best_row: SensitivityResultRow,
    criteria: ReadinessCriteria,
) -> dict[str, Any]:
    ready_count = sum(row.readiness_classification == "observation_ready" for row in rows)
    review_count = sum(row.readiness_classification == "review" for row in rows)
    not_ready_count = sum(row.readiness_classification == "not_ready" for row in rows)
    return {
        "created_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "candidate_count": len(rows),
        "criteria": criteria.to_dict(),
        "class_counts": {
            "observation_ready": ready_count,
            "review": review_count,
            "not_ready": not_ready_count,
        },
        "default_candidate": default_row.to_dict(),
        "best_candidate": best_row.to_dict(),
        "top_ranked_labels": [row.label for row in rankings[:5]],
        "recommendation": recommendation_for(default_row, best_row),
    }


def recommendation_for(default_row: SensitivityResultRow, best_row: SensitivityResultRow) -> str:
    if default_row.readiness_classification == "observation_ready":
        if default_row.label == best_row.label:
            return "keep_default_for_first_observation_layer"
        return "default_is_ready_but_review_best_ranked_candidate_before_observation"
    if best_row.readiness_classification == "observation_ready":
        return "tune_or_review_default_before_observation_layer"
    return "do_not_add_observation_layer_until_deterministic_benchmark_is_reviewed"


def render_decision_memo(
    rows: tuple[SensitivityResultRow, ...],
    rankings: tuple[SensitivityResultRow, ...],
    default_row: SensitivityResultRow,
    best_row: SensitivityResultRow,
    criteria: ReadinessCriteria,
) -> str:
    recommendation = recommendation_for(default_row, best_row)
    lines = [
        "# Synth-Small Predator-Truth Sensitivity Decision Memo",
        "",
        (
            "This memo summarizes a small deterministic sensitivity sweep around "
            "the current predator-truth default. It does not add noisy "
            "observations or fit parameters."
        ),
        "",
        "## Readiness Criteria",
        "",
        "- Verification passes: required",
        (
            "- Extirpated fraction: "
            f"`{criteria.extirpated_fraction_min}` to `{criteria.extirpated_fraction_max}`"
        ),
        f"- Finite lag standard deviation: at least `{criteria.lag_std_min}`",
        "- Low-initial-abundance extirpation rate exceeds high-initial-abundance rate",
        "- West-band extirpated count exceeds east-band count",
        "- Numerical clipping is not used",
        "",
        "## Decision Summary",
        "",
        f"- Candidate count: `{len(rows)}`",
        f"- Default classification: `{default_row.readiness_classification}`",
        f"- Default readiness score: `{default_row.readiness_score:.6g}`",
        f"- Best-ranked candidate: `{best_row.label}`",
        f"- Best-ranked classification: `{best_row.readiness_classification}`",
        f"- Best-ranked readiness score: `{best_row.readiness_score:.6g}`",
        f"- Recommendation: `{recommendation}`",
        "",
        "## Default Candidate",
        "",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    for metric, value in display_metrics(default_row):
        lines.append(f"| `{metric}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Top Ranked Candidates",
            "",
            (
                "| Rank | Label | Classification | Score | Extirpated Fraction | "
                "Lag Std | Low Rate | High Rate | West Count | East Count |"
            ),
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for rank, row in enumerate(rankings[:10], start=1):
        lines.append(
            f"| `{rank}` | `{row.label}` | `{row.readiness_classification}` | "
            f"`{row.readiness_score:.6g}` | `{row.extirpated_fraction:.6g}` | "
            f"`{stringify_value(row.lag_std)}` | "
            f"`{row.low_initial_extirpation_rate:.6g}` | "
            f"`{row.high_initial_extirpation_rate:.6g}` | "
            f"`{row.west_band_extirpated_count}` | `{row.east_band_extirpated_count}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            interpretation_for(default_row, best_row),
            "",
            "## Scientific Limits",
            "",
            (
                "The readiness labels are deterministic benchmark labels. They "
                "do not prove that the eventual observation model will recover "
                "parameters, and they do not replace ecological judgement about "
                "whether the spatial pattern is the right synthetic story."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def display_metrics(row: SensitivityResultRow) -> tuple[tuple[str, str], ...]:
    return (
        ("label", row.label),
        ("predation_scale", stringify_value(row.predation_scale)),
        ("half_saturation", stringify_value(row.half_saturation)),
        ("ramp_duration", stringify_value(row.ramp_duration)),
        ("classification", row.readiness_classification),
        ("readiness_score", stringify_value(row.readiness_score)),
        ("extirpated_fraction", stringify_value(row.extirpated_fraction)),
        ("surviving_fraction", stringify_value(row.surviving_fraction)),
        ("lag_min", stringify_value(row.lag_min)),
        ("lag_max", stringify_value(row.lag_max)),
        ("lag_mean", stringify_value(row.lag_mean)),
        ("lag_std", stringify_value(row.lag_std)),
        ("low_initial_extirpation_rate", stringify_value(row.low_initial_extirpation_rate)),
        ("high_initial_extirpation_rate", stringify_value(row.high_initial_extirpation_rate)),
        ("west_band_extirpated_count", stringify_value(row.west_band_extirpated_count)),
        ("east_band_extirpated_count", stringify_value(row.east_band_extirpated_count)),
        ("used_nonnegative_clipping", stringify_value(row.used_nonnegative_clipping)),
    )


def interpretation_for(default_row: SensitivityResultRow, best_row: SensitivityResultRow) -> str:
    if default_row.readiness_classification == "observation_ready":
        if default_row.label == best_row.label:
            return (
                "The current default passes every readiness criterion and is the "
                "best-ranked candidate in this local sweep. It is reasonable to "
                "carry this deterministic benchmark into the first observation-layer goal."
            )
        return (
            "The current default passes every readiness criterion, although another "
            "nearby candidate ranks slightly higher under the scoring rule. The "
            "default is defensible for the first observation-layer goal, but Barry "
            "may still prefer the best-ranked candidate after reviewing the maps."
        )
    if best_row.readiness_classification == "observation_ready":
        return (
            "The current default does not pass every readiness criterion, but at "
            "least one nearby candidate does. Review the ranking before adding "
            "observations, because modest deterministic tuning may be warranted."
        )
    return (
        "No candidate in this small local sweep is clearly observation-ready. "
        "The deterministic benchmark should be reviewed before the observation "
        "layer is added."
    )


def finite_optional(values: FloatArray, operation: Any) -> float | None:
    if values.size == 0:
        return None
    return float(operation(values))


def nullable_float(value: float | bool | None) -> float | None:
    if value is None:
        return None
    return float(value)


def stringify_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)
