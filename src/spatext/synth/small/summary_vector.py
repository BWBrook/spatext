"""Synthetic summary-vector bridge for synth-small method development."""

from __future__ import annotations

from csv import DictReader, writer
from dataclasses import dataclass
from json import dumps, loads
from math import sqrt
from os import PathLike
from pathlib import Path
from typing import Any

import numpy as np

from .observations import parse_int, parse_optional_float, stringify_float

DEFAULT_RECONSTRUCTION_DIR = Path("artifacts/synth_small_extirpation_reconstruction")
DEFAULT_OBSERVATION_DIR = Path("artifacts/synth_small_observations")
DEFAULT_OUTPUT_DIR = Path("artifacts/synth_small_summary_vector")
DEFAULT_COVERAGE_BREAKPOINTS = (0.0, 0.25, 0.5, 0.75, 1.0)

SUMMARY_VECTOR_MODES = ("ideal_true", "realistic_observed")
SUMMARY_VECTOR_OUTPUT_FILES = (
    "summary_vector_config.json",
    "summary_components.csv",
    "mode_summary.json",
    "coverage_curve.csv",
    "verification.json",
    "report.md",
)
SUMMARY_COMPONENT_COLUMNS = (
    "mode",
    "component",
    "value",
    "missing_reason",
)
COVERAGE_CURVE_COLUMNS = (
    "mode",
    "coverage_fraction",
    "target_time",
    "finite_target_count",
    "missing_reason",
)
REQUIRED_COMPONENTS = (
    "finite_driver_arrival_count",
    "finite_target_count",
    "finite_target_fraction",
    "lag_count",
    "lag_mean",
    "lag_median",
    "lag_std",
    "lag_min",
    "lag_max",
    "arrival_target_r2",
    "front_plane_row_slope",
    "front_plane_col_slope",
    "front_plane_gradient_magnitude",
)


@dataclass(frozen=True, slots=True)
class SummaryVectorConfig:
    """Configuration for the synthetic summary-vector bridge."""

    summary_name: str = "synth-small-summary-vector"
    reconstruction_dir: str = str(DEFAULT_RECONSTRUCTION_DIR)
    observation_dir: str = str(DEFAULT_OBSERVATION_DIR)
    coverage_breakpoints: tuple[float, ...] = DEFAULT_COVERAGE_BREAKPOINTS

    def to_dict(self) -> dict[str, Any]:
        return {
            "synthetic_only": True,
            "summary_name": self.summary_name,
            "reconstruction_dir": self.reconstruction_dir,
            "observation_dir": self.observation_dir,
            "modes": list(SUMMARY_VECTOR_MODES),
            "coverage_breakpoints": list(self.coverage_breakpoints),
            "field_provenance": {
                "ideal_true": {
                    "target": "evaluation_truth.csv:true_extirpation",
                    "driver_arrival": "evaluation_truth.csv:driver_arrival",
                },
                "realistic_observed": {
                    "target": "site_reconstruction.csv:observed_extirpation_time",
                    "driver_arrival": "evaluation_truth.csv:driver_arrival",
                },
            },
            "not_formal_inference": True,
        }


@dataclass(frozen=True, slots=True)
class SummaryComponentRow:
    mode: str
    component: str
    value: str
    missing_reason: str = ""

    def to_csv_row(self) -> tuple[str, ...]:
        return (self.mode, self.component, self.value, self.missing_reason)


@dataclass(frozen=True, slots=True)
class CoverageCurveRow:
    mode: str
    coverage_fraction: float
    target_time: str
    finite_target_count: int
    missing_reason: str = ""

    def to_csv_row(self) -> tuple[str, ...]:
        return (
            self.mode,
            stringify_float(self.coverage_fraction),
            self.target_time,
            str(self.finite_target_count),
            self.missing_reason,
        )


@dataclass(frozen=True, slots=True)
class SummaryVectorVerificationCheck:
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
class LoadedSummaryVectorInputs:
    reconstruction_dir: Path
    observation_dir: Path
    reconstruction_rows: tuple[dict[str, str], ...]
    reconstruction_verification: dict[str, Any]
    truth_rows: tuple[dict[str, str], ...]


@dataclass(frozen=True, slots=True)
class SummaryVectorTargetRow:
    site_id: str
    cell_id: int
    grid_row: int
    grid_col: int
    driver_arrival: float | None
    target_time: float | None


@dataclass(frozen=True, slots=True)
class SynthSmallSummaryVectorResult:
    config: SummaryVectorConfig
    inputs: LoadedSummaryVectorInputs
    mode_targets: dict[str, tuple[SummaryVectorTargetRow, ...]]
    component_rows: tuple[SummaryComponentRow, ...]
    coverage_rows: tuple[CoverageCurveRow, ...]
    mode_summary: dict[str, Any]
    verification_checks: tuple[SummaryVectorVerificationCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def write_artifacts(
        self,
        output_dir: str | PathLike[str] = DEFAULT_OUTPUT_DIR,
    ) -> tuple[Path, ...]:
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        config_path = target_dir / "summary_vector_config.json"
        components_path = target_dir / "summary_components.csv"
        mode_summary_path = target_dir / "mode_summary.json"
        coverage_path = target_dir / "coverage_curve.csv"
        verification_path = target_dir / "verification.json"
        report_path = target_dir / "report.md"

        config_path.write_text(dumps(self.config.to_dict(), indent=2) + "\n", encoding="utf-8")
        write_rows(
            SUMMARY_COMPONENT_COLUMNS,
            (row.to_csv_row() for row in self.component_rows),
            components_path,
        )
        mode_summary_path.write_text(dumps(self.mode_summary, indent=2) + "\n", encoding="utf-8")
        write_rows(
            COVERAGE_CURVE_COLUMNS,
            (row.to_csv_row() for row in self.coverage_rows),
            coverage_path,
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
        report_path.write_text(render_summary_vector_report(self), encoding="utf-8")
        return (
            config_path,
            components_path,
            mode_summary_path,
            coverage_path,
            verification_path,
            report_path,
        )


def build_synth_small_summary_vector(
    *,
    reconstruction_dir: str | PathLike[str] = DEFAULT_RECONSTRUCTION_DIR,
    observation_dir: str | PathLike[str] = DEFAULT_OBSERVATION_DIR,
    config: SummaryVectorConfig | None = None,
) -> SynthSmallSummaryVectorResult:
    summary_config = config or SummaryVectorConfig(
        reconstruction_dir=str(reconstruction_dir),
        observation_dir=str(observation_dir),
    )
    inputs = load_summary_vector_inputs(reconstruction_dir, observation_dir)
    mode_targets = build_mode_targets(inputs)
    component_rows = tuple(
        row
        for mode in SUMMARY_VECTOR_MODES
        for row in build_summary_component_rows(mode, mode_targets[mode])
    )
    coverage_rows = tuple(
        row
        for mode in SUMMARY_VECTOR_MODES
        for row in build_coverage_curve_rows(
            mode=mode,
            rows=mode_targets[mode],
            coverage_breakpoints=summary_config.coverage_breakpoints,
        )
    )
    mode_summary = build_mode_summary(summary_config, mode_targets, component_rows)
    checks = verify_summary_vector_result(
        inputs=inputs,
        mode_targets=mode_targets,
        component_rows=component_rows,
        coverage_rows=coverage_rows,
        mode_summary=mode_summary,
        config=summary_config,
    )
    return SynthSmallSummaryVectorResult(
        config=summary_config,
        inputs=inputs,
        mode_targets=mode_targets,
        component_rows=component_rows,
        coverage_rows=coverage_rows,
        mode_summary=mode_summary,
        verification_checks=checks,
    )


def load_summary_vector_inputs(
    reconstruction_dir: str | PathLike[str],
    observation_dir: str | PathLike[str],
) -> LoadedSummaryVectorInputs:
    reconstruction_path = Path(reconstruction_dir)
    observation_path = Path(observation_dir)
    required_paths = (
        reconstruction_path / "site_reconstruction.csv",
        reconstruction_path / "verification.json",
        observation_path / "evaluation_truth.csv",
    )
    missing = [path.name for path in required_paths if not path.exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(f"missing required summary-vector input artifacts: {missing_text}")
    return LoadedSummaryVectorInputs(
        reconstruction_dir=reconstruction_path,
        observation_dir=observation_path,
        reconstruction_rows=read_csv_rows(reconstruction_path / "site_reconstruction.csv"),
        reconstruction_verification=read_json(reconstruction_path / "verification.json"),
        truth_rows=read_csv_rows(observation_path / "evaluation_truth.csv"),
    )


def build_mode_targets(
    inputs: LoadedSummaryVectorInputs,
) -> dict[str, tuple[SummaryVectorTargetRow, ...]]:
    truth_by_site = {row["site_id"]: row for row in inputs.truth_rows}
    ideal_rows: list[SummaryVectorTargetRow] = []
    observed_rows: list[SummaryVectorTargetRow] = []
    for row in inputs.reconstruction_rows:
        site_id = row["site_id"]
        truth = truth_by_site.get(site_id)
        if truth is None:
            raise ValueError(f"evaluation_truth.csv is missing site_id {site_id!r}")
        if row["cell_id"] != truth["cell_id"]:
            raise ValueError(f"cell_id mismatch for site_id {site_id!r}")
        driver_arrival = parse_optional_float(truth["driver_arrival"])
        cell_id = parse_int(row["cell_id"])
        grid_row = parse_int(row["row"])
        grid_col = parse_int(row["col"])
        ideal_rows.append(
            SummaryVectorTargetRow(
                site_id=site_id,
                cell_id=cell_id,
                grid_row=grid_row,
                grid_col=grid_col,
                driver_arrival=driver_arrival,
                target_time=parse_optional_float(truth["true_extirpation"]),
            )
        )
        observed_rows.append(
            SummaryVectorTargetRow(
                site_id=site_id,
                cell_id=cell_id,
                grid_row=grid_row,
                grid_col=grid_col,
                driver_arrival=driver_arrival,
                target_time=parse_optional_float(row["observed_extirpation_time"]),
            )
        )
    return {
        "ideal_true": tuple(ideal_rows),
        "realistic_observed": tuple(observed_rows),
    }


def build_summary_component_rows(
    mode: str,
    rows: tuple[SummaryVectorTargetRow, ...],
) -> tuple[SummaryComponentRow, ...]:
    driver_rows = [row for row in rows if row.driver_arrival is not None]
    target_rows = [row for row in driver_rows if row.target_time is not None]
    lag_values = finite_lag_values(driver_rows)

    output: list[SummaryComponentRow] = [
        defined_component(mode, "finite_driver_arrival_count", len(driver_rows)),
        defined_component(mode, "finite_target_count", len(target_rows)),
    ]
    if driver_rows:
        output.append(
            defined_component(mode, "finite_target_fraction", len(target_rows) / len(driver_rows))
        )
    else:
        output.append(missing_component(mode, "finite_target_fraction", "no_finite_driver_arrival"))

    output.append(defined_component(mode, "lag_count", len(lag_values)))
    output.extend(lag_summary_components(mode, lag_values))
    output.append(arrival_target_r2_component(mode, target_rows))
    output.extend(front_plane_components(mode, target_rows))
    return tuple(output)


def finite_lag_values(rows: list[SummaryVectorTargetRow]) -> list[float]:
    output: list[float] = []
    for row in rows:
        if row.driver_arrival is None or row.target_time is None:
            continue
        output.append(row.target_time - row.driver_arrival)
    return output


def lag_summary_components(
    mode: str,
    lag_values: list[float],
) -> tuple[SummaryComponentRow, ...]:
    if not lag_values:
        return (
            missing_component(mode, "lag_mean", "no_finite_lag_pairs"),
            missing_component(mode, "lag_median", "no_finite_lag_pairs"),
            missing_component(mode, "lag_std", "no_finite_lag_pairs"),
            missing_component(mode, "lag_min", "no_finite_lag_pairs"),
            missing_component(mode, "lag_max", "no_finite_lag_pairs"),
        )
    values = np.array(lag_values, dtype=float)
    return (
        defined_component(mode, "lag_mean", float(np.mean(values))),
        defined_component(mode, "lag_median", float(np.median(values))),
        defined_component(mode, "lag_std", float(np.std(values))),
        defined_component(mode, "lag_min", float(np.min(values))),
        defined_component(mode, "lag_max", float(np.max(values))),
    )


def arrival_target_r2_component(
    mode: str,
    rows: list[SummaryVectorTargetRow],
) -> SummaryComponentRow:
    if len(rows) < 2:
        return missing_component(mode, "arrival_target_r2", "insufficient_finite_pairs")
    arrivals = np.array([row.driver_arrival for row in rows], dtype=float)
    targets = np.array([row.target_time for row in rows], dtype=float)
    if np.ptp(arrivals) == 0.0 or np.ptp(targets) == 0.0:
        return missing_component(mode, "arrival_target_r2", "constant_arrival_or_target")
    correlation = float(np.corrcoef(arrivals, targets)[0, 1])
    return defined_component(mode, "arrival_target_r2", correlation * correlation)


def front_plane_components(
    mode: str,
    rows: list[SummaryVectorTargetRow],
) -> tuple[SummaryComponentRow, ...]:
    if not rows:
        return (
            missing_component(mode, "front_plane_row_slope", "no_finite_target"),
            missing_component(mode, "front_plane_col_slope", "no_finite_target"),
            missing_component(mode, "front_plane_gradient_magnitude", "no_finite_target"),
        )
    if len(rows) < 3:
        return (
            missing_component(mode, "front_plane_row_slope", "insufficient_finite_pairs"),
            missing_component(mode, "front_plane_col_slope", "insufficient_finite_pairs"),
            missing_component(mode, "front_plane_gradient_magnitude", "insufficient_finite_pairs"),
        )
    design = np.array([[1.0, row.grid_row, row.grid_col] for row in rows], dtype=float)
    if int(np.linalg.matrix_rank(design)) < 3:
        return (
            missing_component(mode, "front_plane_row_slope", "singular_front_plane"),
            missing_component(mode, "front_plane_col_slope", "singular_front_plane"),
            missing_component(mode, "front_plane_gradient_magnitude", "singular_front_plane"),
        )
    targets = np.array([row.target_time for row in rows], dtype=float)
    coefficients = np.linalg.lstsq(design, targets, rcond=None)[0]
    row_slope = float(coefficients[1])
    col_slope = float(coefficients[2])
    return (
        defined_component(mode, "front_plane_row_slope", row_slope),
        defined_component(mode, "front_plane_col_slope", col_slope),
        defined_component(
            mode, "front_plane_gradient_magnitude", sqrt(row_slope**2 + col_slope**2)
        ),
    )


def build_coverage_curve_rows(
    *,
    mode: str,
    rows: tuple[SummaryVectorTargetRow, ...],
    coverage_breakpoints: tuple[float, ...],
) -> tuple[CoverageCurveRow, ...]:
    finite_targets = sorted(row.target_time for row in rows if row.target_time is not None)
    output: list[CoverageCurveRow] = []
    for fraction in coverage_breakpoints:
        if not finite_targets:
            output.append(
                CoverageCurveRow(
                    mode=mode,
                    coverage_fraction=fraction,
                    target_time="",
                    finite_target_count=0,
                    missing_reason="no_finite_target",
                )
            )
            continue
        threshold = float(np.quantile(np.array(finite_targets, dtype=float), fraction))
        output.append(
            CoverageCurveRow(
                mode=mode,
                coverage_fraction=fraction,
                target_time=stringify_float(threshold),
                finite_target_count=len(finite_targets),
            )
        )
    return tuple(output)


def build_mode_summary(
    config: SummaryVectorConfig,
    mode_targets: dict[str, tuple[SummaryVectorTargetRow, ...]],
    component_rows: tuple[SummaryComponentRow, ...],
) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for mode in SUMMARY_VECTOR_MODES:
        rows = mode_targets[mode]
        mode_components = [row for row in component_rows if row.mode == mode]
        finite_driver_count = sum(row.driver_arrival is not None for row in rows)
        finite_target_count = sum(
            row.driver_arrival is not None and row.target_time is not None for row in rows
        )
        summaries[mode] = {
            "target_source": (
                "evaluation_truth.csv:true_extirpation"
                if mode == "ideal_true"
                else "site_reconstruction.csv:observed_extirpation_time"
            ),
            "driver_arrival_source": "evaluation_truth.csv:driver_arrival",
            "site_count": len(rows),
            "finite_driver_arrival_count": finite_driver_count,
            "finite_target_count": finite_target_count,
            "finite_target_fraction": (
                finite_target_count / finite_driver_count if finite_driver_count else None
            ),
            "component_count": len(mode_components),
            "undefined_component_count": sum(bool(row.missing_reason) for row in mode_components),
        }
    return {
        "synthetic_only": True,
        "summary_name": config.summary_name,
        "modes": list(SUMMARY_VECTOR_MODES),
        "mode_summaries": summaries,
        "interpretation": {
            "classification": "synthetic_method_development_only",
            "not_formal_inference": True,
            "notes": [
                "This bundle computes reusable S(T_X, T_P) summaries.",
                "The ideal_true mode uses synthetic truth.",
                "The realistic_observed mode uses reconstructed response-side targets.",
                "No compatibility screen, ABC, likelihood, posterior, or real-data claim is made.",
            ],
        },
    }


def verify_summary_vector_result(
    *,
    inputs: LoadedSummaryVectorInputs,
    mode_targets: dict[str, tuple[SummaryVectorTargetRow, ...]],
    component_rows: tuple[SummaryComponentRow, ...],
    coverage_rows: tuple[CoverageCurveRow, ...],
    mode_summary: dict[str, Any],
    config: SummaryVectorConfig,
) -> tuple[SummaryVectorVerificationCheck, ...]:
    component_modes = {row.mode for row in component_rows}
    coverage_modes = {row.mode for row in coverage_rows}
    components_by_mode = {
        mode: {row.component for row in component_rows if row.mode == mode}
        for mode in SUMMARY_VECTOR_MODES
    }
    missing_components = {
        mode: sorted(set(REQUIRED_COMPONENTS) - components_by_mode[mode])
        for mode in SUMMARY_VECTOR_MODES
    }
    missing_reason_rows = [
        row.component
        for row in component_rows
        if (row.value == "" and not row.missing_reason)
        or (row.value != "" and bool(row.missing_reason))
    ]
    missing_reason_coverage_rows = [
        row.mode
        for row in coverage_rows
        if (row.target_time == "" and not row.missing_reason)
        or (row.target_time != "" and bool(row.missing_reason))
    ]
    return (
        SummaryVectorVerificationCheck(
            name="input_files",
            passed=all(
                path.exists()
                for path in (
                    inputs.reconstruction_dir / "site_reconstruction.csv",
                    inputs.reconstruction_dir / "verification.json",
                    inputs.observation_dir / "evaluation_truth.csv",
                )
            ),
            message="required summary-vector inputs are present",
            details={
                "reconstruction_dir": str(inputs.reconstruction_dir),
                "observation_dir": str(inputs.observation_dir),
            },
        ),
        SummaryVectorVerificationCheck(
            name="source_reconstruction_verification",
            passed=bool(inputs.reconstruction_verification.get("passed")),
            message="source reconstruction verification passed",
            details={"source_passed": bool(inputs.reconstruction_verification.get("passed"))},
        ),
        SummaryVectorVerificationCheck(
            name="mode_targets",
            passed=set(mode_targets) == set(SUMMARY_VECTOR_MODES)
            and all(mode_targets[mode] for mode in SUMMARY_VECTOR_MODES),
            message="both summary-vector modes were built",
            details={mode: len(mode_targets[mode]) for mode in SUMMARY_VECTOR_MODES},
        ),
        SummaryVectorVerificationCheck(
            name="required_components",
            passed=component_modes == set(SUMMARY_VECTOR_MODES)
            and not any(missing_components.values()),
            message="required summary components are present for both modes",
            details={"missing_components": missing_components},
        ),
        SummaryVectorVerificationCheck(
            name="coverage_rows",
            passed=coverage_modes == set(SUMMARY_VECTOR_MODES)
            and len(coverage_rows) == len(SUMMARY_VECTOR_MODES) * len(config.coverage_breakpoints),
            message="coverage rows were emitted for all modes and breakpoints",
            details={
                "coverage_row_count": len(coverage_rows),
                "coverage_breakpoint_count": len(config.coverage_breakpoints),
            },
        ),
        SummaryVectorVerificationCheck(
            name="missing_reasons",
            passed=not missing_reason_rows and not missing_reason_coverage_rows,
            message="undefined metrics use explicit missing reasons",
            details={
                "component_issue_count": len(missing_reason_rows),
                "coverage_issue_count": len(missing_reason_coverage_rows),
            },
        ),
        SummaryVectorVerificationCheck(
            name="synthetic_only_labels",
            passed=mode_summary.get("synthetic_only") is True
            and mode_summary.get("interpretation", {}).get("not_formal_inference") is True,
            message="mode summary is labelled synthetic-only and not formal inference",
            details={"synthetic_only": mode_summary.get("synthetic_only")},
        ),
    )


def defined_component(
    mode: str,
    component: str,
    value: int | float,
) -> SummaryComponentRow:
    return SummaryComponentRow(mode=mode, component=component, value=format_component_value(value))


def missing_component(
    mode: str,
    component: str,
    reason: str,
) -> SummaryComponentRow:
    return SummaryComponentRow(mode=mode, component=component, value="", missing_reason=reason)


def format_component_value(value: int | float) -> str:
    if isinstance(value, int):
        return str(value)
    return stringify_float(value)


def render_summary_vector_report(result: SynthSmallSummaryVectorResult) -> str:
    mode_summaries = result.mode_summary["mode_summaries"]
    lines = [
        "# Synth-Small Summary Vector",
        "",
        "## Scope",
        "",
        "This is a synthetic-only method-development summary layer.",
        "It computes reusable `S(T_X, T_P)` summaries and does not fit a model.",
        "",
        "## Modes",
    ]
    for mode in SUMMARY_VECTOR_MODES:
        summary = mode_summaries[mode]
        lines.extend(
            [
                f"- `{mode}`",
                f"  - target source: `{summary['target_source']}`",
                f"  - finite targets: `{summary['finite_target_count']}`",
                f"  - finite target fraction: `{value_or_na(summary['finite_target_fraction'])}`",
                f"  - undefined components: `{summary['undefined_component_count']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Hidden truth is used only inside this synthetic summary-vector bundle.",
            "No response-only reconstruction, screen, inspection, or evaluation artifacts "
            "are rewritten.",
            "No ABC, POM, likelihood, posterior, parameter sweep, or real-data claim is made.",
        ]
    )
    return "\n".join(lines) + "\n"


def value_or_na(value: float | None) -> str:
    if value is None:
        return "NA"
    return stringify_float(value)


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
