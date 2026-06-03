from __future__ import annotations

from csv import DictReader, writer
from dataclasses import dataclass
from json import dumps, loads
from os import PathLike
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

REQUIRED_ARTIFACT_FILES = (
    "domain.json",
    "baseline_config.json",
    "predator_config.json",
    "diagnostics.json",
    "summary.json",
    "cells.csv",
    "surfaces.npz",
    "trajectories.npz",
    "suitability.svg",
    "initial_abundance.svg",
    "driver_arrival.svg",
    "true_extirpation.svg",
    "extirpation_lag.svg",
    "final_abundance.svg",
)

REQUIRED_SURFACE_KEYS = (
    "suitability",
    "carrying_capacity",
    "initial_abundance",
    "driver_arrival",
    "extirpation_threshold",
    "true_extirpation",
    "extirpation_lag",
    "final_abundance",
)

REQUIRED_TRAJECTORY_KEYS = (
    "prey_abundance",
    "predator_pressure",
)


@dataclass(frozen=True, slots=True)
class LoadedSynthSmallPredatorTruthBundle:
    artifact_dir: Path
    domain: dict[str, Any]
    baseline_config: dict[str, Any]
    predator_config: dict[str, Any]
    diagnostics: dict[str, Any]
    summary_payload: dict[str, Any]
    cells: tuple[dict[str, str], ...]
    suitability: FloatArray
    carrying_capacity: FloatArray
    initial_abundance: FloatArray
    driver_arrival: FloatArray
    extirpation_threshold: FloatArray
    true_extirpation: FloatArray
    extirpation_lag: FloatArray
    final_abundance: FloatArray
    prey_abundance: FloatArray
    predator_pressure: FloatArray


@dataclass(frozen=True, slots=True)
class VerificationCheck:
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
class ScientificWarning:
    name: str
    message: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True, slots=True)
class ParameterRow:
    group: str
    name: str
    value: str

    def to_csv_row(self) -> tuple[str, str, str]:
        return (self.group, self.name, self.value)


@dataclass(frozen=True, slots=True)
class GridSummaryRow:
    surface: str
    finite_count: int
    missing_count: int
    min_value: float | None
    max_value: float | None
    mean_value: float | None
    std_value: float | None
    sum_value: float | None

    def to_csv_row(self) -> tuple[str, str, str, str, str, str, str, str]:
        return (
            self.surface,
            str(self.finite_count),
            str(self.missing_count),
            stringify_nullable_float(self.min_value),
            stringify_nullable_float(self.max_value),
            stringify_nullable_float(self.mean_value),
            stringify_nullable_float(self.std_value),
            stringify_nullable_float(self.sum_value),
        )


@dataclass(frozen=True, slots=True)
class TrajectorySummaryRow:
    trajectory: str
    time_steps: int
    rows: int
    cols: int
    finite_count: int
    missing_count: int
    min_value: float | None
    max_value: float | None
    mean_value: float | None
    std_value: float | None
    initial_mean: float | None
    final_mean: float | None

    def to_csv_row(self) -> tuple[str, str, str, str, str, str, str, str, str, str, str, str]:
        return (
            self.trajectory,
            str(self.time_steps),
            str(self.rows),
            str(self.cols),
            str(self.finite_count),
            str(self.missing_count),
            stringify_nullable_float(self.min_value),
            stringify_nullable_float(self.max_value),
            stringify_nullable_float(self.mean_value),
            stringify_nullable_float(self.std_value),
            stringify_nullable_float(self.initial_mean),
            stringify_nullable_float(self.final_mean),
        )


@dataclass(frozen=True, slots=True)
class ExtirpationSummaryRow:
    metric: str
    value: str

    def to_csv_row(self) -> tuple[str, str]:
        return (self.metric, self.value)


@dataclass(frozen=True, slots=True)
class SynthSmallPredatorTruthInspectionResult:
    artifact_dir: Path
    output_dir: Path
    verification_checks: tuple[VerificationCheck, ...]
    scientific_warnings: tuple[ScientificWarning, ...]
    parameter_rows: tuple[ParameterRow, ...]
    surface_summary_rows: tuple[GridSummaryRow, ...]
    trajectory_summary_rows: tuple[TrajectorySummaryRow, ...]
    extirpation_summary_rows: tuple[ExtirpationSummaryRow, ...]
    report_path: Path
    verification_path: Path
    parameters_path: Path
    surface_summary_path: Path
    trajectory_summary_path: Path
    extirpation_summary_path: Path

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def verification_payload(self) -> dict[str, Any]:
        return {
            "artifact_dir": str(self.artifact_dir),
            "output_dir": str(self.output_dir),
            "passed": self.passed,
            "warning_count": len(self.scientific_warnings),
            "checks": [check.to_dict() for check in self.verification_checks],
            "warnings": [warning.to_dict() for warning in self.scientific_warnings],
        }


def inspect_synth_small_predator_truth_artifacts(
    artifact_dir: str | PathLike[str],
    *,
    output_dir: str | PathLike[str] | None = None,
) -> SynthSmallPredatorTruthInspectionResult:
    bundle = load_synth_small_predator_truth_artifacts(artifact_dir)
    inspection_dir = (
        Path(output_dir) if output_dir is not None else bundle.artifact_dir / "inspection"
    )
    inspection_dir.mkdir(parents=True, exist_ok=True)

    checks = verify_predator_truth_bundle(bundle)
    warnings = build_scientific_warnings(bundle)
    parameter_rows = build_parameter_rows(bundle)
    surface_summary_rows = build_surface_summary_rows(bundle)
    trajectory_summary_rows = build_trajectory_summary_rows(bundle)
    extirpation_summary_rows = build_extirpation_summary_rows(bundle)

    verification_path = inspection_dir / "verification.json"
    parameters_path = inspection_dir / "parameters.csv"
    surface_summary_path = inspection_dir / "surface_summary.csv"
    trajectory_summary_path = inspection_dir / "trajectory_summary.csv"
    extirpation_summary_path = inspection_dir / "extirpation_summary.csv"
    report_path = inspection_dir / "report.md"

    result = SynthSmallPredatorTruthInspectionResult(
        artifact_dir=bundle.artifact_dir,
        output_dir=inspection_dir,
        verification_checks=checks,
        scientific_warnings=warnings,
        parameter_rows=parameter_rows,
        surface_summary_rows=surface_summary_rows,
        trajectory_summary_rows=trajectory_summary_rows,
        extirpation_summary_rows=extirpation_summary_rows,
        report_path=report_path,
        verification_path=verification_path,
        parameters_path=parameters_path,
        surface_summary_path=surface_summary_path,
        trajectory_summary_path=trajectory_summary_path,
        extirpation_summary_path=extirpation_summary_path,
    )

    verification_path.write_text(
        dumps(result.verification_payload(), indent=2) + "\n", encoding="utf-8"
    )
    write_parameter_table(parameter_rows, parameters_path)
    write_surface_summary_table(surface_summary_rows, surface_summary_path)
    write_trajectory_summary_table(trajectory_summary_rows, trajectory_summary_path)
    write_extirpation_summary_table(extirpation_summary_rows, extirpation_summary_path)
    report_path.write_text(render_report(bundle, result), encoding="utf-8")
    return result


def load_synth_small_predator_truth_artifacts(
    artifact_dir: str | PathLike[str],
) -> LoadedSynthSmallPredatorTruthBundle:
    bundle_dir = Path(artifact_dir)
    missing = [name for name in REQUIRED_ARTIFACT_FILES if not (bundle_dir / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(
            f"missing required synth-small predator-truth artifact files: {missing_text}"
        )

    domain = read_json(bundle_dir / "domain.json")
    baseline_config = read_json(bundle_dir / "baseline_config.json")
    predator_config = read_json(bundle_dir / "predator_config.json")
    diagnostics = read_json(bundle_dir / "diagnostics.json")
    summary_payload = read_json(bundle_dir / "summary.json")
    cells = read_csv_rows(bundle_dir / "cells.csv")
    surfaces = load_npz_arrays(
        bundle_dir / "surfaces.npz",
        REQUIRED_SURFACE_KEYS,
        label="surfaces.npz",
    )
    trajectories = load_npz_arrays(
        bundle_dir / "trajectories.npz",
        REQUIRED_TRAJECTORY_KEYS,
        label="trajectories.npz",
    )

    return LoadedSynthSmallPredatorTruthBundle(
        artifact_dir=bundle_dir,
        domain=domain,
        baseline_config=baseline_config,
        predator_config=predator_config,
        diagnostics=diagnostics,
        summary_payload=summary_payload,
        cells=cells,
        suitability=np.asarray(surfaces["suitability"], dtype=np.float64),
        carrying_capacity=np.asarray(surfaces["carrying_capacity"], dtype=np.float64),
        initial_abundance=np.asarray(surfaces["initial_abundance"], dtype=np.float64),
        driver_arrival=np.asarray(surfaces["driver_arrival"], dtype=np.float64),
        extirpation_threshold=np.asarray(
            surfaces["extirpation_threshold"],
            dtype=np.float64,
        ),
        true_extirpation=np.asarray(surfaces["true_extirpation"], dtype=np.float64),
        extirpation_lag=np.asarray(surfaces["extirpation_lag"], dtype=np.float64),
        final_abundance=np.asarray(surfaces["final_abundance"], dtype=np.float64),
        prey_abundance=np.asarray(trajectories["prey_abundance"], dtype=np.float64),
        predator_pressure=np.asarray(trajectories["predator_pressure"], dtype=np.float64),
    )


def read_json(path: Path) -> dict[str, Any]:
    payload = loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return cast(dict[str, Any], payload)


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def load_npz_arrays(path: Path, required_keys: tuple[str, ...], *, label: str) -> dict[str, Any]:
    try:
        archive = np.load(path)
    except (OSError, ValueError) as exc:
        raise ValueError(f"failed to load synth-small predator-truth {label}: {exc}") from exc

    try:
        missing = [key for key in required_keys if key not in archive.files]
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(
                f"missing required synth-small predator-truth arrays in {label}: {missing_text}"
            )
        return {key: np.asarray(archive[key]) for key in required_keys}
    finally:
        archive.close()


def verify_predator_truth_bundle(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[VerificationCheck, ...]:
    rows, cols, cell_count = domain_dimensions(bundle)
    expected_shape = (rows, cols)
    expected_trajectory_shape = (
        int(bundle.diagnostics.get("simulation_horizon", -1)) + 1,
        rows,
        cols,
    )
    surfaces = grid_surfaces(bundle)
    shape_consistent = all(values.shape == expected_shape for _, values in surfaces)
    trajectory_shape_consistent = (
        bundle.prey_abundance.shape == expected_trajectory_shape
        and bundle.predator_pressure.shape == expected_trajectory_shape
    )
    cells_consistent, cells_details = cells_match_bundle(bundle)
    driver_integral = bool(np.allclose(bundle.driver_arrival, np.rint(bundle.driver_arrival)))
    introduction_time = float(
        nested_number(bundle.predator_config, ("arrival", "introduction_time"), default=np.nan)
    )
    western_boundary_matches = bundle.driver_arrival.shape == expected_shape and np.allclose(
        bundle.driver_arrival[:, 0], introduction_time
    )
    pressure_scale = float(
        nested_number(bundle.predator_config, ("pressure", "pressure_scale"), default=np.nan)
    )
    prey_finite = np.isfinite(bundle.prey_abundance).all()
    pressure_finite = np.isfinite(bundle.predator_pressure).all()
    true_extirpation_valid, true_extirpation_details = extirpation_semantics(bundle)
    recomputed_summary = recompute_summary(bundle)
    declared_summary_raw = bundle.summary_payload.get("summary", {})
    declared_summary = declared_summary_raw if isinstance(declared_summary_raw, dict) else {}
    diagnostics_consistent, diagnostics_details = diagnostics_match_bundle(bundle)
    final_mean_decline = float(np.mean(bundle.final_abundance)) < float(
        np.mean(bundle.initial_abundance)
    )
    finite_lag = bundle.extirpation_lag[np.isfinite(bundle.extirpation_lag)]
    extirpated_fraction = extirpated_count(bundle) / cell_count

    return (
        VerificationCheck(
            name="shape_consistency",
            passed=shape_consistent,
            message="expected all grid surfaces to match domain shape",
            details={
                "expected_shape": list(expected_shape),
                "surface_shapes": {name: list(values.shape) for name, values in surfaces},
            },
        ),
        VerificationCheck(
            name="trajectory_shape_consistency",
            passed=trajectory_shape_consistent,
            message="expected trajectories to match simulation_horizon + domain shape",
            details={
                "expected_shape": list(expected_trajectory_shape),
                "prey_abundance_shape": list(bundle.prey_abundance.shape),
                "predator_pressure_shape": list(bundle.predator_pressure.shape),
            },
        ),
        VerificationCheck(
            name="cell_table_consistency",
            passed=cells_consistent,
            message="expected cells.csv to agree with loaded grid surfaces",
            details=cells_details,
        ),
        VerificationCheck(
            name="driver_arrival_valid",
            passed=bool(
                bundle.driver_arrival.shape == expected_shape
                and np.isfinite(bundle.driver_arrival).all()
                and driver_integral
                and float(np.min(bundle.driver_arrival)) >= introduction_time
                and western_boundary_matches
            ),
            message=(
                "expected finite integer driver arrival values aligned to the baseline grid "
                "with western-boundary arrival at introduction time"
            ),
            details={
                "min": finite_stat(bundle.driver_arrival, np.min),
                "max": finite_stat(bundle.driver_arrival, np.max),
                "introduction_time": introduction_time,
                "integer_valued": driver_integral,
                "western_boundary_matches": western_boundary_matches,
            },
        ),
        VerificationCheck(
            name="predator_pressure_valid",
            passed=bool(
                trajectory_shape_consistent
                and pressure_finite
                and float(np.min(bundle.predator_pressure)) >= -1e-12
                and float(np.max(bundle.predator_pressure)) <= pressure_scale + 1e-12
            ),
            message="expected finite predator pressure bounded by configured pressure_scale",
            details={
                "min": finite_stat(bundle.predator_pressure, np.min),
                "max": finite_stat(bundle.predator_pressure, np.max),
                "pressure_scale": pressure_scale,
            },
        ),
        VerificationCheck(
            name="prey_abundance_valid",
            passed=bool(
                trajectory_shape_consistent
                and prey_finite
                and float(np.min(bundle.prey_abundance)) >= -1e-12
            ),
            message="expected finite non-negative prey abundance trajectory",
            details={
                "min": finite_stat(bundle.prey_abundance, np.min),
                "max": finite_stat(bundle.prey_abundance, np.max),
            },
        ),
        VerificationCheck(
            name="trajectory_consistency",
            passed=bool(
                trajectory_shape_consistent
                and np.allclose(bundle.prey_abundance[0], bundle.initial_abundance)
                and np.allclose(bundle.prey_abundance[-1], bundle.final_abundance)
            ),
            message="expected trajectory endpoints to match initial and final abundance surfaces",
            details={
                "initial_matches": bool(
                    trajectory_shape_consistent
                    and np.allclose(bundle.prey_abundance[0], bundle.initial_abundance)
                ),
                "final_matches": bool(
                    trajectory_shape_consistent
                    and np.allclose(bundle.prey_abundance[-1], bundle.final_abundance)
                ),
            },
        ),
        VerificationCheck(
            name="extirpation_semantics",
            passed=true_extirpation_valid,
            message=(
                "expected true extirpation and lag arrays to use finite-or-missing semantics "
                "and never place extirpation before predator arrival"
            ),
            details=true_extirpation_details,
        ),
        VerificationCheck(
            name="summary_consistency",
            passed=summary_matches(recomputed_summary, declared_summary),
            message="expected summary.json values to match recomputation from loaded arrays",
            details={
                "declared_summary": declared_summary,
                "recomputed_summary": recomputed_summary,
            },
        ),
        VerificationCheck(
            name="diagnostics_consistency",
            passed=diagnostics_consistent,
            message="expected diagnostics.json to agree with loaded trajectories and surfaces",
            details=diagnostics_details,
        ),
        VerificationCheck(
            name="scientific_sanity",
            passed=bool(
                0.0 < extirpated_fraction < 1.0
                and finite_lag.size > 0
                and float(np.std(finite_lag)) > 0.0
                and final_mean_decline
            ),
            message=(
                "expected mixed extirpation/survival, variable lag, and lower final mean abundance"
            ),
            details={
                "extirpated_fraction": extirpated_fraction,
                "finite_lag_count": int(finite_lag.size),
                "finite_lag_std": finite_stat(finite_lag, np.std),
                "initial_abundance_mean": float(np.mean(bundle.initial_abundance)),
                "final_abundance_mean": float(np.mean(bundle.final_abundance)),
            },
        ),
    )


def domain_dimensions(bundle: LoadedSynthSmallPredatorTruthBundle) -> tuple[int, int, int]:
    rows = int(bundle.domain["rows"])
    cols = int(bundle.domain["cols"])
    cell_count = int(bundle.domain["cell_count"])
    return rows, cols, cell_count


def grid_surfaces(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[tuple[str, FloatArray], ...]:
    return (
        ("suitability", bundle.suitability),
        ("carrying_capacity", bundle.carrying_capacity),
        ("initial_abundance", bundle.initial_abundance),
        ("driver_arrival", bundle.driver_arrival),
        ("extirpation_threshold", bundle.extirpation_threshold),
        ("true_extirpation", bundle.true_extirpation),
        ("extirpation_lag", bundle.extirpation_lag),
        ("final_abundance", bundle.final_abundance),
    )


def cells_match_bundle(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[bool, dict[str, Any]]:
    rows, cols, cell_count = domain_dimensions(bundle)
    required_columns = {
        "cell_id",
        "row",
        "col",
        "suitability",
        "carrying_capacity",
        "initial_abundance",
        "driver_arrival",
        "extirpation_threshold",
        "true_extirpation",
        "extirpation_lag",
        "final_abundance",
        "extirpated_by_end",
    }
    if len(bundle.cells) != cell_count:
        return False, {"expected_rows": cell_count, "actual_rows": len(bundle.cells)}

    for row_index, cell in enumerate(bundle.cells):
        if not required_columns.issubset(cell):
            return False, {
                "first_bad_row": row_index,
                "reason": "missing required columns",
                "required_columns": sorted(required_columns),
                "actual_columns": sorted(cell),
            }
        try:
            cell_id = int(cell["cell_id"])
            row = int(cell["row"])
            col = int(cell["col"])
        except ValueError as exc:
            return False, {"first_bad_row": row_index, "reason": f"bad integer field: {exc}"}

        if cell_id != row_index or row != row_index // cols or col != row_index % cols:
            return False, {
                "first_bad_row": row_index,
                "reason": "cell_id/row/col sequence mismatch",
                "cell_id": cell_id,
                "row": row,
                "col": col,
            }
        if not (0 <= row < rows and 0 <= col < cols):
            return False, {"first_bad_row": row_index, "reason": "row/col out of bounds"}

        comparisons = {
            "suitability": (cell_float(cell, "suitability"), bundle.suitability[row, col]),
            "carrying_capacity": (
                cell_float(cell, "carrying_capacity"),
                bundle.carrying_capacity[row, col],
            ),
            "initial_abundance": (
                cell_float(cell, "initial_abundance"),
                bundle.initial_abundance[row, col],
            ),
            "driver_arrival": (cell_float(cell, "driver_arrival"), bundle.driver_arrival[row, col]),
            "extirpation_threshold": (
                cell_float(cell, "extirpation_threshold"),
                bundle.extirpation_threshold[row, col],
            ),
            "true_extirpation": (
                cell_nullable_float(cell, "true_extirpation"),
                bundle.true_extirpation[row, col],
            ),
            "extirpation_lag": (
                cell_nullable_float(cell, "extirpation_lag"),
                bundle.extirpation_lag[row, col],
            ),
            "final_abundance": (
                cell_float(cell, "final_abundance"),
                bundle.final_abundance[row, col],
            ),
        }
        for name, (actual, expected) in comparisons.items():
            if not nullable_allclose(actual, float(expected)):
                return False, {
                    "first_bad_row": row_index,
                    "field": name,
                    "csv_value": actual,
                    "array_value": float(expected),
                }

        expected_extirpated = int(np.isfinite(bundle.true_extirpation[row, col]))
        if int(cell["extirpated_by_end"]) != expected_extirpated:
            return False, {
                "first_bad_row": row_index,
                "field": "extirpated_by_end",
                "csv_value": cell["extirpated_by_end"],
                "array_value": expected_extirpated,
            }

    return True, {"expected_rows": cell_count, "actual_rows": len(bundle.cells)}


def cell_float(cell: dict[str, str], name: str) -> float:
    return float(cell[name])


def cell_nullable_float(cell: dict[str, str], name: str) -> float:
    value = cell[name]
    if value == "":
        return float("nan")
    return float(value)


def nullable_allclose(actual: float, expected: float) -> bool:
    if not np.isfinite(actual) and not np.isfinite(expected):
        return True
    return bool(np.isclose(actual, expected, atol=1e-9, rtol=1e-9))


def extirpation_semantics(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[bool, dict[str, Any]]:
    extirpated = np.isfinite(bundle.true_extirpation)
    surviving = ~extirpated
    finite_lags_for_extirpated = np.isfinite(bundle.extirpation_lag[extirpated]).all()
    missing_lags_for_survivors = np.isnan(bundle.extirpation_lag[surviving]).all()
    lag_matches = True
    no_negative_lag = True
    no_extirpation_before_arrival = True
    min_lag: float | None = None
    if np.any(extirpated):
        expected_lag = bundle.true_extirpation[extirpated] - bundle.driver_arrival[extirpated]
        observed_lag = bundle.extirpation_lag[extirpated]
        lag_matches = bool(np.allclose(observed_lag, expected_lag, atol=1e-9, rtol=1e-9))
        min_lag = float(np.min(expected_lag))
        no_negative_lag = bool(np.all(expected_lag >= -1e-12))
        no_extirpation_before_arrival = bool(
            np.all(bundle.true_extirpation[extirpated] >= bundle.driver_arrival[extirpated])
        )

    passed = bool(
        finite_lags_for_extirpated
        and missing_lags_for_survivors
        and lag_matches
        and no_negative_lag
        and no_extirpation_before_arrival
    )
    return passed, {
        "extirpated_count": int(np.sum(extirpated)),
        "surviving_count": int(np.sum(surviving)),
        "finite_lags_for_extirpated": bool(finite_lags_for_extirpated),
        "missing_lags_for_survivors": bool(missing_lags_for_survivors),
        "lag_matches": lag_matches,
        "min_lag": min_lag,
        "no_extirpation_before_arrival": no_extirpation_before_arrival,
    }


def recompute_summary(bundle: LoadedSynthSmallPredatorTruthBundle) -> dict[str, float | int | None]:
    extirpated = np.isfinite(bundle.true_extirpation)
    extirpated_n = int(np.sum(extirpated))
    cell_count = domain_dimensions(bundle)[2]
    finite_true_extirpation = bundle.true_extirpation[extirpated]
    finite_lag = bundle.extirpation_lag[np.isfinite(bundle.extirpation_lag)]
    return {
        "suitability_min": float(np.min(bundle.suitability)),
        "suitability_max": float(np.max(bundle.suitability)),
        "suitability_mean": float(np.mean(bundle.suitability)),
        "suitability_std": float(np.std(bundle.suitability)),
        "initial_abundance_min": float(np.min(bundle.initial_abundance)),
        "initial_abundance_max": float(np.max(bundle.initial_abundance)),
        "initial_abundance_mean": float(np.mean(bundle.initial_abundance)),
        "initial_abundance_std": float(np.std(bundle.initial_abundance)),
        "driver_arrival_min": int(np.min(bundle.driver_arrival)),
        "driver_arrival_max": int(np.max(bundle.driver_arrival)),
        "driver_arrival_mean": float(np.mean(bundle.driver_arrival)),
        "driver_arrival_std": float(np.std(bundle.driver_arrival)),
        "final_abundance_min": float(np.min(bundle.final_abundance)),
        "final_abundance_max": float(np.max(bundle.final_abundance)),
        "final_abundance_mean": float(np.mean(bundle.final_abundance)),
        "final_abundance_std": float(np.std(bundle.final_abundance)),
        "extirpation_threshold_min": float(np.min(bundle.extirpation_threshold)),
        "extirpation_threshold_max": float(np.max(bundle.extirpation_threshold)),
        "extirpation_threshold_mean": float(np.mean(bundle.extirpation_threshold)),
        "extirpated_count": extirpated_n,
        "extirpated_fraction": extirpated_n / cell_count,
        "surviving_count": cell_count - extirpated_n,
        "surviving_fraction": (cell_count - extirpated_n) / cell_count,
        "true_extirpation_min": finite_optional(finite_true_extirpation, np.min),
        "true_extirpation_max": finite_optional(finite_true_extirpation, np.max),
        "true_extirpation_mean": finite_optional(finite_true_extirpation, np.mean),
        "true_extirpation_std": finite_optional(finite_true_extirpation, np.std),
        "lag_min": finite_optional(finite_lag, np.min),
        "lag_max": finite_optional(finite_lag, np.max),
        "lag_mean": finite_optional(finite_lag, np.mean),
        "lag_std": finite_optional(finite_lag, np.std),
    }


def summary_matches(recomputed: dict[str, float | int | None], declared: dict[str, Any]) -> bool:
    for key, expected in recomputed.items():
        actual = declared.get(key)
        if expected is None:
            if actual is not None:
                return False
            continue
        if actual is None:
            return False
        if not np.isclose(float(actual), float(expected), atol=1e-9, rtol=1e-9):
            return False
    return True


def diagnostics_match_bundle(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[bool, dict[str, Any]]:
    finite_state = bool(
        np.isfinite(bundle.predator_pressure).all() and np.isfinite(bundle.prey_abundance).all()
    )
    nonnegative_state = bool(np.min(bundle.prey_abundance) >= -1e-12)
    max_driver_arrival = int(np.max(bundle.driver_arrival))
    simulation_horizon = int(bundle.prey_abundance.shape[0] - 1)
    checks = {
        "stayed_finite_matches": bool(bundle.diagnostics.get("stayed_finite") == finite_state),
        "stayed_nonnegative_matches": bool(
            bundle.diagnostics.get("stayed_nonnegative") == nonnegative_state
        ),
        "max_driver_arrival_matches": bool(
            int(bundle.diagnostics.get("max_driver_arrival", -1)) == max_driver_arrival
        ),
        "simulation_horizon_matches": bool(
            int(bundle.diagnostics.get("simulation_horizon", -1)) == simulation_horizon
        ),
        "baseline_converged": bool(bundle.diagnostics.get("baseline_converged", False)),
    }
    return all(checks.values()), {
        **checks,
        "computed_stayed_finite": finite_state,
        "computed_stayed_nonnegative": nonnegative_state,
        "computed_max_driver_arrival": max_driver_arrival,
        "computed_simulation_horizon": simulation_horizon,
    }


def build_scientific_warnings(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[ScientificWarning, ...]:
    warnings: list[ScientificWarning] = []
    extirpated_fraction = extirpated_count(bundle) / domain_dimensions(bundle)[2]
    if extirpated_fraction <= 0.05 or extirpated_fraction >= 0.95:
        warnings.append(
            ScientificWarning(
                name="near_degenerate_extirpation_fraction",
                message="extirpation fraction is near 0 or 1 and may be weak for recovery tests",
                details={"extirpated_fraction": extirpated_fraction},
            )
        )

    if bool(bundle.diagnostics.get("used_nonnegative_clipping", False)):
        warnings.append(
            ScientificWarning(
                name="nonnegative_clipping_used",
                message="the run used non-negative clipping and may need numerical review",
                details={"used_nonnegative_clipping": True},
            )
        )

    finite_lag = bundle.extirpation_lag[np.isfinite(bundle.extirpation_lag)]
    if finite_lag.size > 0 and float(np.std(finite_lag)) < 1e-9:
        warnings.append(
            ScientificWarning(
                name="low_lag_variation",
                message="finite extirpation lags are nearly constant",
                details={"lag_std": float(np.std(finite_lag))},
            )
        )

    vulnerability = vulnerability_metrics(bundle)
    low_rate = vulnerability["low_initial_extirpation_rate"]
    high_rate = vulnerability["high_initial_extirpation_rate"]
    if low_rate is not None and high_rate is not None and low_rate <= high_rate:
        warnings.append(
            ScientificWarning(
                name="low_density_vulnerability_reversal",
                message=(
                    "low-initial-abundance cells are not more likely to extirpate than "
                    "high-initial-abundance cells"
                ),
                details=vulnerability,
            )
        )

    if bundle.diagnostics.get("predation_response_form") != "type_ii":
        warnings.append(
            ScientificWarning(
                name="non_default_predation_response",
                message="predation response form differs from current Type II default",
                details={
                    "predation_response_form": bundle.diagnostics.get("predation_response_form")
                },
            )
        )

    if bundle.diagnostics.get("extirpation_threshold_form") != "absolute_quasi_extinction":
        warnings.append(
            ScientificWarning(
                name="non_default_extirpation_threshold",
                message=(
                    "extirpation threshold form differs from current absolute threshold default"
                ),
                details={
                    "extirpation_threshold_form": bundle.diagnostics.get(
                        "extirpation_threshold_form"
                    )
                },
            )
        )

    return tuple(warnings)


def build_parameter_rows(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[ParameterRow, ...]:
    rows: list[ParameterRow] = []
    for key in ("rows", "cols", "cell_count", "neighborhood"):
        rows.append(ParameterRow("domain", key, stringify_value(bundle.domain[key])))

    for name, value in flatten_mapping(bundle.baseline_config, prefix="baseline").items():
        rows.append(ParameterRow(parameter_group_for(name), name, stringify_value(value)))
    for name, value in flatten_mapping(bundle.predator_config, prefix="predator").items():
        rows.append(ParameterRow(parameter_group_for(name), name, stringify_value(value)))
    for name, value in flatten_mapping(bundle.diagnostics, prefix="diagnostics").items():
        rows.append(ParameterRow("diagnostics", name, stringify_value(value)))
    return tuple(rows)


def flatten_mapping(mapping: dict[str, Any], *, prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in mapping.items():
        path = key if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            flattened.update(flatten_mapping(value, prefix=path))
        else:
            flattened[path] = value
    return flattened


def parameter_group_for(name: str) -> str:
    if name.startswith("predator.arrival."):
        return "arrival"
    if name.startswith("predator.pressure."):
        return "pressure"
    if name.startswith("predator.response."):
        return "response"
    if name.startswith("predator.extirpation."):
        return "extirpation"
    if name.startswith("predator."):
        return "predator"
    if name.startswith("baseline.suitability."):
        return "baseline_suitability"
    if name.startswith("baseline."):
        return "baseline"
    return "parameters"


def build_surface_summary_rows(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[GridSummaryRow, ...]:
    return tuple(grid_summary_row(name, values) for name, values in grid_surfaces(bundle))


def grid_summary_row(name: str, values: FloatArray) -> GridSummaryRow:
    finite_mask = np.isfinite(values)
    finite_values = values[finite_mask]
    return GridSummaryRow(
        surface=name,
        finite_count=int(np.sum(finite_mask)),
        missing_count=int(values.size - np.sum(finite_mask)),
        min_value=finite_optional(finite_values, np.min),
        max_value=finite_optional(finite_values, np.max),
        mean_value=finite_optional(finite_values, np.mean),
        std_value=finite_optional(finite_values, np.std),
        sum_value=finite_optional(finite_values, np.sum),
    )


def build_trajectory_summary_rows(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[TrajectorySummaryRow, ...]:
    return (
        trajectory_summary_row("prey_abundance", bundle.prey_abundance),
        trajectory_summary_row("predator_pressure", bundle.predator_pressure),
    )


def trajectory_summary_row(name: str, values: FloatArray) -> TrajectorySummaryRow:
    finite_mask = np.isfinite(values)
    finite_values = values[finite_mask]
    return TrajectorySummaryRow(
        trajectory=name,
        time_steps=values.shape[0],
        rows=values.shape[1],
        cols=values.shape[2],
        finite_count=int(np.sum(finite_mask)),
        missing_count=int(values.size - np.sum(finite_mask)),
        min_value=finite_optional(finite_values, np.min),
        max_value=finite_optional(finite_values, np.max),
        mean_value=finite_optional(finite_values, np.mean),
        std_value=finite_optional(finite_values, np.std),
        initial_mean=finite_optional(values[0][np.isfinite(values[0])], np.mean),
        final_mean=finite_optional(values[-1][np.isfinite(values[-1])], np.mean),
    )


def build_extirpation_summary_rows(
    bundle: LoadedSynthSmallPredatorTruthBundle,
) -> tuple[ExtirpationSummaryRow, ...]:
    rows: list[ExtirpationSummaryRow] = []
    summary = recompute_summary(bundle)
    for key in (
        "extirpated_count",
        "extirpated_fraction",
        "surviving_count",
        "surviving_fraction",
        "driver_arrival_min",
        "driver_arrival_max",
        "true_extirpation_min",
        "true_extirpation_max",
        "lag_min",
        "lag_max",
        "lag_mean",
        "lag_std",
    ):
        rows.append(ExtirpationSummaryRow(key, stringify_value(summary[key])))

    for key, value in vulnerability_metrics(bundle).items():
        rows.append(ExtirpationSummaryRow(key, stringify_value(value)))
    return tuple(rows)


def vulnerability_metrics(bundle: LoadedSynthSmallPredatorTruthBundle) -> dict[str, float | int]:
    extirpated = np.isfinite(bundle.true_extirpation)
    low_threshold, high_threshold = np.quantile(bundle.initial_abundance, [0.25, 0.75])
    low_mask = bundle.initial_abundance <= low_threshold
    high_mask = bundle.initial_abundance >= high_threshold
    west_mask = np.zeros(bundle.initial_abundance.shape, dtype=np.bool_)
    east_mask = np.zeros(bundle.initial_abundance.shape, dtype=np.bool_)
    west_mask[:, :5] = True
    east_mask[:, -5:] = True
    return {
        "low_initial_threshold": float(low_threshold),
        "high_initial_threshold": float(high_threshold),
        "low_initial_extirpation_rate": float(np.mean(extirpated[low_mask])),
        "high_initial_extirpation_rate": float(np.mean(extirpated[high_mask])),
        "west_band_extirpated_count": int(np.sum(extirpated[west_mask])),
        "east_band_extirpated_count": int(np.sum(extirpated[east_mask])),
    }


def write_parameter_table(rows: tuple[ParameterRow, ...], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(["group", "name", "value"])
        for row in rows:
            csv_writer.writerow(row.to_csv_row())


def write_surface_summary_table(rows: tuple[GridSummaryRow, ...], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(
            ["surface", "finite_count", "missing_count", "min", "max", "mean", "std", "sum"]
        )
        for row in rows:
            csv_writer.writerow(row.to_csv_row())


def write_trajectory_summary_table(
    rows: tuple[TrajectorySummaryRow, ...], output_path: Path
) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(
            [
                "trajectory",
                "time_steps",
                "rows",
                "cols",
                "finite_count",
                "missing_count",
                "min",
                "max",
                "mean",
                "std",
                "initial_mean",
                "final_mean",
            ]
        )
        for row in rows:
            csv_writer.writerow(row.to_csv_row())


def write_extirpation_summary_table(
    rows: tuple[ExtirpationSummaryRow, ...], output_path: Path
) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(["metric", "value"])
        for row in rows:
            csv_writer.writerow(row.to_csv_row())


def render_report(
    bundle: LoadedSynthSmallPredatorTruthBundle,
    result: SynthSmallPredatorTruthInspectionResult,
) -> str:
    rows, cols, cell_count = domain_dimensions(bundle)
    lines = [
        "# Synth-Small Predator-Truth Inspection Report",
        "",
        (
            "This report verifies and summarizes an existing deterministic "
            "`synth-small` predator-response truth bundle loaded from disk."
        ),
        "",
        "## Overview",
        "",
        f"- Artifact directory: `{bundle.artifact_dir}`",
        f"- Inspection directory: `{result.output_dir}`",
        f"- Overall verification result: `{'PASS' if result.passed else 'FAIL'}`",
        f"- Scientific warnings: `{len(result.scientific_warnings)}`",
        "- Verification record: [verification.json](verification.json)",
        "- Parameter table: [parameters.csv](parameters.csv)",
        "- Surface summary: [surface_summary.csv](surface_summary.csv)",
        "- Trajectory summary: [trajectory_summary.csv](trajectory_summary.csv)",
        "- Extirpation summary: [extirpation_summary.csv](extirpation_summary.csv)",
        "",
        "## Verification Status",
        "",
        "| Check | Passed | Message |",
        "| --- | --- | --- |",
    ]
    for check in result.verification_checks:
        lines.append(f"| `{check.name}` | `{'yes' if check.passed else 'no'}` | {check.message} |")

    lines.extend(["", "## Scientific Warnings", ""])
    if result.scientific_warnings:
        lines.extend(["| Warning | Message |", "| --- | --- |"])
        for warning in result.scientific_warnings:
            lines.append(f"| `{warning.name}` | {warning.message} |")
    else:
        lines.append("No scientific warnings were emitted by the inspection layer.")

    lines.extend(
        [
            "",
            "## Domain Summary",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| rows | `{rows}` |",
            f"| cols | `{cols}` |",
            f"| cell_count | `{cell_count}` |",
            f"| neighborhood | `{bundle.domain['neighborhood']}` |",
            "",
            "## Parameter Table",
            "",
            "| Group | Name | Value |",
            "| --- | --- | --- |",
        ]
    )
    for parameter_row in result.parameter_rows:
        lines.append(
            f"| `{parameter_row.group}` | `{parameter_row.name}` | `{parameter_row.value}` |"
        )

    lines.extend(
        [
            "",
            "## Surface Summary",
            "",
            "| Surface | Finite | Missing | Min | Max | Mean | Std |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for surface_row in result.surface_summary_rows:
        lines.append(
            f"| `{surface_row.surface}` | `{surface_row.finite_count}` | "
            f"`{surface_row.missing_count}` | "
            f"`{stringify_nullable_float(surface_row.min_value)}` | "
            f"`{stringify_nullable_float(surface_row.max_value)}` | "
            f"`{stringify_nullable_float(surface_row.mean_value)}` | "
            f"`{stringify_nullable_float(surface_row.std_value)}` |"
        )

    lines.extend(
        [
            "",
            "## Trajectory Summary",
            "",
            "| Trajectory | Time Steps | Min | Max | Mean | Std | Initial Mean | Final Mean |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for trajectory_row in result.trajectory_summary_rows:
        lines.append(
            f"| `{trajectory_row.trajectory}` | `{trajectory_row.time_steps}` | "
            f"`{stringify_nullable_float(trajectory_row.min_value)}` | "
            f"`{stringify_nullable_float(trajectory_row.max_value)}` | "
            f"`{stringify_nullable_float(trajectory_row.mean_value)}` | "
            f"`{stringify_nullable_float(trajectory_row.std_value)}` | "
            f"`{stringify_nullable_float(trajectory_row.initial_mean)}` | "
            f"`{stringify_nullable_float(trajectory_row.final_mean)}` |"
        )

    lines.extend(
        [
            "",
            "## Extirpation and Vulnerability Summary",
            "",
            "| Metric | Value |",
            "| --- | --- |",
        ]
    )
    for extirpation_row in result.extirpation_summary_rows:
        lines.append(f"| `{extirpation_row.metric}` | `{extirpation_row.value}` |")

    lines.extend(
        [
            "",
            "## Figures",
            "",
            "### Suitability",
            "",
            "![Suitability](../suitability.svg)",
            "",
            "### Initial Abundance",
            "",
            "![Initial Abundance](../initial_abundance.svg)",
            "",
            "### Driver Arrival",
            "",
            "![Driver Arrival](../driver_arrival.svg)",
            "",
            "### True Extirpation",
            "",
            "![True Extirpation](../true_extirpation.svg)",
            "",
            "### Extirpation Lag",
            "",
            "![Extirpation Lag](../extirpation_lag.svg)",
            "",
            "### Final Abundance",
            "",
            "![Final Abundance](../final_abundance.svg)",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def nested_number(mapping: dict[str, Any], path: tuple[str, ...], *, default: float) -> float:
    current: Any = mapping
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    if isinstance(current, int | float):
        return float(current)
    return default


def extirpated_count(bundle: LoadedSynthSmallPredatorTruthBundle) -> int:
    return int(np.sum(np.isfinite(bundle.true_extirpation)))


def finite_optional(values: FloatArray, operation: Any) -> float | None:
    if values.size == 0:
        return None
    return float(operation(values))


def finite_stat(values: FloatArray, operation: Any) -> float | None:
    finite_values = values[np.isfinite(values)]
    return finite_optional(finite_values, operation)


def stringify_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def stringify_nullable_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.12g}"
