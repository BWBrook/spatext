from __future__ import annotations

from csv import DictReader, writer
from dataclasses import dataclass
from json import dumps, loads
from os import PathLike
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

BoolArray = NDArray[np.bool_]
FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int_]

REQUIRED_ARTIFACT_FILES = (
    "domain.json",
    "config.json",
    "diagnostics.json",
    "summary.json",
    "cells.csv",
    "edges.csv",
    "surfaces.npz",
    "suitability.svg",
    "carrying_capacity.svg",
    "equilibrium_abundance.svg",
    "equilibrium_occupancy.svg",
)


@dataclass(frozen=True, slots=True)
class LoadedSynthSmallArtifactBundle:
    artifact_dir: Path
    domain: dict[str, Any]
    config: dict[str, Any]
    diagnostics: dict[str, Any]
    summary_payload: dict[str, Any]
    cells: tuple[dict[str, str], ...]
    edges: tuple[tuple[int, int], ...]
    suitability: FloatArray
    carrying_capacity: FloatArray
    equilibrium_abundance: FloatArray
    occupancy: IntArray


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
class SurfaceSummaryRow:
    surface: str
    min_value: float
    max_value: float
    mean_value: float
    std_value: float
    sum_value: float

    def to_csv_row(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.surface,
            f"{self.min_value:.12g}",
            f"{self.max_value:.12g}",
            f"{self.mean_value:.12g}",
            f"{self.std_value:.12g}",
            f"{self.sum_value:.12g}",
        )


@dataclass(frozen=True, slots=True)
class ParameterRow:
    group: str
    name: str
    value: str

    def to_csv_row(self) -> tuple[str, str, str]:
        return (self.group, self.name, self.value)


@dataclass(frozen=True, slots=True)
class SynthSmallInspectionResult:
    artifact_dir: Path
    output_dir: Path
    verification_checks: tuple[VerificationCheck, ...]
    parameter_rows: tuple[ParameterRow, ...]
    surface_summary_rows: tuple[SurfaceSummaryRow, ...]
    report_path: Path
    verification_path: Path
    parameters_path: Path
    surface_summary_path: Path

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.verification_checks)

    def verification_payload(self) -> dict[str, Any]:
        return {
            "artifact_dir": str(self.artifact_dir),
            "output_dir": str(self.output_dir),
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.verification_checks],
        }


def inspect_synth_small_artifacts(
    artifact_dir: str | PathLike[str],
    *,
    output_dir: str | PathLike[str] | None = None,
) -> SynthSmallInspectionResult:
    bundle = load_synth_small_artifacts(artifact_dir)
    inspection_dir = (
        Path(output_dir) if output_dir is not None else bundle.artifact_dir / "inspection"
    )
    inspection_dir.mkdir(parents=True, exist_ok=True)

    checks = verify_synth_small_bundle(bundle)
    parameter_rows = build_parameter_rows(bundle)
    surface_summary_rows = build_surface_summary_rows(bundle)

    verification_path = inspection_dir / "verification.json"
    parameters_path = inspection_dir / "parameters.csv"
    surface_summary_path = inspection_dir / "surface_summary.csv"
    report_path = inspection_dir / "report.md"

    result = SynthSmallInspectionResult(
        artifact_dir=bundle.artifact_dir,
        output_dir=inspection_dir,
        verification_checks=checks,
        parameter_rows=parameter_rows,
        surface_summary_rows=surface_summary_rows,
        report_path=report_path,
        verification_path=verification_path,
        parameters_path=parameters_path,
        surface_summary_path=surface_summary_path,
    )

    verification_path.write_text(
        dumps(result.verification_payload(), indent=2) + "\n", encoding="utf-8"
    )
    write_parameter_table(parameter_rows, parameters_path)
    write_surface_summary_table(surface_summary_rows, surface_summary_path)
    report_path.write_text(render_report(bundle, result), encoding="utf-8")
    return result


def load_synth_small_artifacts(artifact_dir: str | PathLike[str]) -> LoadedSynthSmallArtifactBundle:
    bundle_dir = Path(artifact_dir)
    missing = [name for name in REQUIRED_ARTIFACT_FILES if not (bundle_dir / name).exists()]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise FileNotFoundError(f"missing required synth-small artifact files: {missing_text}")

    domain = read_json(bundle_dir / "domain.json")
    config = read_json(bundle_dir / "config.json")
    diagnostics = read_json(bundle_dir / "diagnostics.json")
    summary_payload = read_json(bundle_dir / "summary.json")
    cells = read_csv_rows(bundle_dir / "cells.csv")
    edges = read_edges(bundle_dir / "edges.csv")
    surfaces = np.load(bundle_dir / "surfaces.npz")

    try:
        suitability = np.asarray(surfaces["suitability"], dtype=np.float64)
        carrying_capacity = np.asarray(surfaces["carrying_capacity"], dtype=np.float64)
        equilibrium_abundance = np.asarray(surfaces["equilibrium_abundance"], dtype=np.float64)
        occupancy = np.asarray(surfaces["occupancy"])
    finally:
        surfaces.close()

    return LoadedSynthSmallArtifactBundle(
        artifact_dir=bundle_dir,
        domain=domain,
        config=config,
        diagnostics=diagnostics,
        summary_payload=summary_payload,
        cells=cells,
        edges=edges,
        suitability=suitability,
        carrying_capacity=carrying_capacity,
        equilibrium_abundance=equilibrium_abundance,
        occupancy=occupancy,
    )


def read_json(path: Path) -> dict[str, Any]:
    payload = loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return cast(dict[str, Any], payload)


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def read_edges(path: Path) -> tuple[tuple[int, int], ...]:
    rows = read_csv_rows(path)
    return tuple((int(row["source"]), int(row["target"])) for row in rows)


def verify_synth_small_bundle(
    bundle: LoadedSynthSmallArtifactBundle,
) -> tuple[VerificationCheck, ...]:
    rows = int(bundle.domain["rows"])
    cols = int(bundle.domain["cols"])
    cell_count = int(bundle.domain["cell_count"])
    expected_shape = (rows, cols)
    shape_consistent = (
        bundle.suitability.shape == expected_shape
        and bundle.carrying_capacity.shape == expected_shape
        and bundle.equilibrium_abundance.shape == expected_shape
        and bundle.occupancy.shape == expected_shape
        and len(bundle.cells) == cell_count
    )
    occupancy_values = np.unique(bundle.occupancy)
    recomputed_summary = recompute_summary(bundle)
    declared_summary_raw = bundle.summary_payload.get("summary", {})
    declared_summary = declared_summary_raw if isinstance(declared_summary_raw, dict) else {}
    edge_targets_valid = all(
        0 <= source < cell_count and 0 <= target < cell_count for source, target in bundle.edges
    )
    abundance_margin = (
        float(np.max(bundle.equilibrium_abundance - bundle.carrying_capacity))
        if bundle.equilibrium_abundance.shape == bundle.carrying_capacity.shape
        else float("inf")
    )

    checks = (
        VerificationCheck(
            name="shape_consistency",
            passed=shape_consistent,
            message=(
                "expected all surfaces and cells to match shape "
                f"{expected_shape} and cell_count {cell_count}"
            ),
            details={
                "expected_shape": list(expected_shape),
                "suitability_shape": list(bundle.suitability.shape),
                "carrying_capacity_shape": list(bundle.carrying_capacity.shape),
                "equilibrium_abundance_shape": list(bundle.equilibrium_abundance.shape),
                "occupancy_shape": list(bundle.occupancy.shape),
                "cells_rows": len(bundle.cells),
                "cell_count": cell_count,
            },
        ),
        VerificationCheck(
            name="domain_graph_consistency",
            passed=(
                len(bundle.edges) > 0
                and edge_targets_valid
                and len(set(bundle.edges)) == len(bundle.edges)
            ),
            message=(
                "expected a non-empty undirected edge list with valid endpoints and no duplicates"
            ),
            details={
                "edge_count": len(bundle.edges),
                "edge_targets_valid": edge_targets_valid,
                "unique_edge_count": len(set(bundle.edges)),
            },
        ),
        VerificationCheck(
            name="suitability_bounds",
            passed=bool(
                np.isfinite(bundle.suitability).all()
                and float(np.min(bundle.suitability)) >= 0.0
                and float(np.max(bundle.suitability)) <= 1.0
            ),
            message="expected suitability to be finite and bounded in [0, 1]",
            details={
                "min": float(np.min(bundle.suitability)),
                "max": float(np.max(bundle.suitability)),
            },
        ),
        VerificationCheck(
            name="carrying_capacity_positive",
            passed=bool(
                np.isfinite(bundle.carrying_capacity).all()
                and float(np.min(bundle.carrying_capacity)) > 0.0
            ),
            message="expected carrying capacity to be finite and strictly positive",
            details={
                "min": float(np.min(bundle.carrying_capacity)),
                "max": float(np.max(bundle.carrying_capacity)),
            },
        ),
        VerificationCheck(
            name="equilibrium_abundance_valid",
            passed=bool(
                np.isfinite(bundle.equilibrium_abundance).all()
                and np.greater_equal(bundle.equilibrium_abundance, 0.0).all()
                and abundance_margin <= 1e-8
            ),
            message=(
                "expected equilibrium abundance to be finite, non-negative, "
                "and not exceed carrying capacity"
            ),
            details={
                "min": float(np.min(bundle.equilibrium_abundance)),
                "max": float(np.max(bundle.equilibrium_abundance)),
                "max_capacity_margin": abundance_margin,
            },
        ),
        VerificationCheck(
            name="occupancy_binary",
            passed=set(int(value) for value in occupancy_values.tolist()).issubset({0, 1}),
            message="expected occupancy array to contain only binary values after load",
            details={"unique_values": [int(value) for value in occupancy_values.tolist()]},
        ),
        VerificationCheck(
            name="diagnostics_converged",
            passed=bool(bundle.diagnostics.get("converged", False)),
            message="expected diagnostics to indicate convergence",
            details=bundle.diagnostics,
        ),
        VerificationCheck(
            name="summary_consistency",
            passed=summary_matches(recomputed_summary, declared_summary),
            message="expected summary.json values to match recomputation from loaded surfaces",
            details={
                "declared_summary": declared_summary,
                "recomputed_summary": recomputed_summary,
            },
        ),
        VerificationCheck(
            name="scientific_sanity",
            passed=(
                float(np.std(bundle.suitability)) > 0.0
                and float(np.std(bundle.equilibrium_abundance)) > 0.0
                and 0.0 < float(np.mean(bundle.occupancy.astype(np.float64))) < 1.0
                and expected_shape == (25, 25)
            ),
            message=(
                "expected non-degenerate spatial structure and the intended 25 x 25 benchmark shape"
            ),
            details={
                "suitability_std": float(np.std(bundle.suitability)),
                "equilibrium_abundance_std": float(np.std(bundle.equilibrium_abundance)),
                "occupancy_fraction": float(np.mean(bundle.occupancy.astype(np.float64))),
                "shape": list(expected_shape),
            },
        ),
    )
    return checks


def recompute_summary(bundle: LoadedSynthSmallArtifactBundle) -> dict[str, float]:
    return {
        "suitability_min": float(np.min(bundle.suitability)),
        "suitability_max": float(np.max(bundle.suitability)),
        "carrying_capacity_min": float(np.min(bundle.carrying_capacity)),
        "carrying_capacity_max": float(np.max(bundle.carrying_capacity)),
        "equilibrium_abundance_min": float(np.min(bundle.equilibrium_abundance)),
        "equilibrium_abundance_max": float(np.max(bundle.equilibrium_abundance)),
        "equilibrium_abundance_mean": float(np.mean(bundle.equilibrium_abundance)),
        "equilibrium_abundance_std": float(np.std(bundle.equilibrium_abundance)),
        "occupancy_fraction": float(np.mean(bundle.occupancy.astype(np.float64))),
    }


def summary_matches(recomputed: dict[str, float], declared: dict[str, Any]) -> bool:
    for key, expected in recomputed.items():
        actual = declared.get(key)
        if actual is None:
            return False
        if not np.isclose(float(actual), expected, atol=1e-9, rtol=1e-9):
            return False
    return True


def build_parameter_rows(bundle: LoadedSynthSmallArtifactBundle) -> tuple[ParameterRow, ...]:
    rows: list[ParameterRow] = []
    for key in ("rows", "cols", "cell_count", "neighborhood"):
        rows.append(ParameterRow("domain", key, stringify_value(bundle.domain[key])))

    for name, value in flatten_mapping(bundle.config).items():
        if name in {"rows", "cols", "neighborhood"}:
            continue
        rows.append(ParameterRow(parameter_group_for(name), name, stringify_value(value)))

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
    if name.startswith("suitability."):
        return "suitability"
    if name in {"dispersal_share", "neighborhood"}:
        return "dispersal"
    if name in {
        "convergence_tolerance",
        "consecutive_converged_steps",
        "max_steps",
        "raise_on_nonconvergence",
    }:
        return "convergence"
    if name == "occupancy_threshold":
        return "occupancy"
    if name in {"rows", "cols"}:
        return "domain"
    return "demography"


def stringify_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def build_surface_summary_rows(
    bundle: LoadedSynthSmallArtifactBundle,
) -> tuple[SurfaceSummaryRow, ...]:
    surfaces = (
        ("suitability", bundle.suitability.astype(np.float64)),
        ("carrying_capacity", bundle.carrying_capacity.astype(np.float64)),
        ("equilibrium_abundance", bundle.equilibrium_abundance.astype(np.float64)),
        ("occupancy", bundle.occupancy.astype(np.float64)),
    )
    rows = [surface_summary_row(name, values) for name, values in surfaces]
    return tuple(rows)


def surface_summary_row(name: str, values: FloatArray) -> SurfaceSummaryRow:
    return SurfaceSummaryRow(
        surface=name,
        min_value=float(np.min(values)),
        max_value=float(np.max(values)),
        mean_value=float(np.mean(values)),
        std_value=float(np.std(values)),
        sum_value=float(np.sum(values)),
    )


def write_parameter_table(rows: tuple[ParameterRow, ...], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(["group", "name", "value"])
        for row in rows:
            csv_writer.writerow(row.to_csv_row())


def write_surface_summary_table(rows: tuple[SurfaceSummaryRow, ...], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = writer(handle)
        csv_writer.writerow(["surface", "min", "max", "mean", "std", "sum"])
        for row in rows:
            csv_writer.writerow(row.to_csv_row())


def render_report(
    bundle: LoadedSynthSmallArtifactBundle,
    result: SynthSmallInspectionResult,
) -> str:
    lines = [
        "# Synth-Small Baseline Inspection Report",
        "",
        (
            "This report verifies and summarizes an existing "
            "`synth-small` artifact bundle loaded from disk."
        ),
        "",
        "## Overview",
        "",
        f"- Artifact directory: `{bundle.artifact_dir}`",
        f"- Inspection directory: `{result.output_dir}`",
        f"- Overall verification result: `{'PASS' if result.passed else 'FAIL'}`",
        "- Verification record: [verification.json](verification.json)",
        "- Parameter table: [parameters.csv](parameters.csv)",
        "- Surface summary: [surface_summary.csv](surface_summary.csv)",
        "",
        "## Verification Status",
        "",
        "| Check | Passed | Message |",
        "| --- | --- | --- |",
    ]
    for check in result.verification_checks:
        lines.append(f"| `{check.name}` | `{'yes' if check.passed else 'no'}` | {check.message} |")

    lines.extend(
        [
            "",
            "## Domain and Graph Summary",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| rows | `{bundle.domain['rows']}` |",
            f"| cols | `{bundle.domain['cols']}` |",
            f"| cell_count | `{bundle.domain['cell_count']}` |",
            f"| neighborhood | `{bundle.domain['neighborhood']}` |",
            f"| edge_count | `{len(bundle.edges)}` |",
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

    diagnostics = bundle.diagnostics
    lines.extend(
        [
            "",
            "## Diagnostics",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| converged | `{diagnostics['converged']}` |",
            f"| steps | `{diagnostics['steps']}` |",
            f"| max_relative_change | `{diagnostics['max_relative_change']}` |",
            f"| consecutive_satisfied_steps | `{diagnostics['consecutive_satisfied_steps']}` |",
            f"| tolerance | `{diagnostics['tolerance']}` |",
            "",
            "## Surface Summary",
            "",
            "| Surface | Min | Max | Mean | Std | Sum |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for summary_row in result.surface_summary_rows:
        lines.append(
            f"| `{summary_row.surface}` | `{summary_row.min_value:.6g}` | "
            f"`{summary_row.max_value:.6g}` | `{summary_row.mean_value:.6g}` | "
            f"`{summary_row.std_value:.6g}` | `{summary_row.sum_value:.6g}` |"
        )

    lines.extend(
        [
            "",
            "## Figures",
            "",
            "### Suitability",
            "",
            "![Suitability](../suitability.svg)",
            "",
            "### Carrying Capacity",
            "",
            "![Carrying Capacity](../carrying_capacity.svg)",
            "",
            "### Equilibrium Abundance",
            "",
            "![Equilibrium Abundance](../equilibrium_abundance.svg)",
            "",
            "### Equilibrium Occupancy",
            "",
            "![Equilibrium Occupancy](../equilibrium_occupancy.svg)",
            "",
        ]
    )
    return "\n".join(lines) + "\n"
