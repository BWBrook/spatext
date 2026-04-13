from __future__ import annotations

from json import dumps, loads
from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest

from spatext.synth.small import build_synth_small_baseline, inspect_synth_small_artifacts


def build_bundle(tmp_path: Path) -> Path:
    artifact_dir = tmp_path / "baseline"
    result = build_synth_small_baseline()
    result.write_artifacts(artifact_dir)
    return artifact_dir


def overwrite_surfaces(
    artifact_dir: Path,
    *,
    suitability: np.ndarray | None = None,
    carrying_capacity: np.ndarray | None = None,
    equilibrium_abundance: np.ndarray | None = None,
    occupancy: np.ndarray | None = None,
) -> None:
    surfaces = np.load(artifact_dir / "surfaces.npz")
    try:
        updated = {
            "suitability": suitability if suitability is not None else surfaces["suitability"],
            "carrying_capacity": (
                carrying_capacity
                if carrying_capacity is not None
                else surfaces["carrying_capacity"]
            ),
            "equilibrium_abundance": (
                equilibrium_abundance
                if equilibrium_abundance is not None
                else surfaces["equilibrium_abundance"]
            ),
            "occupancy": occupancy if occupancy is not None else surfaces["occupancy"],
        }
    finally:
        surfaces.close()
    np.savez_compressed(artifact_dir / "surfaces.npz", **cast(dict[str, Any], updated))


def test_inspection_outputs_are_created_for_valid_bundle(tmp_path: Path) -> None:
    artifact_dir = build_bundle(tmp_path)

    inspection = inspect_synth_small_artifacts(artifact_dir)

    assert inspection.passed is True
    assert inspection.output_dir == artifact_dir / "inspection"
    assert inspection.verification_path.exists()
    assert inspection.parameters_path.exists()
    assert inspection.surface_summary_path.exists()
    assert inspection.report_path.exists()

    verification = loads(inspection.verification_path.read_text(encoding="utf-8"))
    assert verification["passed"] is True

    report_text = inspection.report_path.read_text(encoding="utf-8")
    assert "Synth-Small Baseline Inspection Report" in report_text
    assert "![Suitability](../suitability.svg)" in report_text


def test_parameter_table_rendering_is_deterministic(tmp_path: Path) -> None:
    artifact_dir = build_bundle(tmp_path)

    first = inspect_synth_small_artifacts(artifact_dir, output_dir=artifact_dir / "inspection-a")
    second = inspect_synth_small_artifacts(artifact_dir, output_dir=artifact_dir / "inspection-b")

    assert first.parameters_path.read_text(encoding="utf-8") == second.parameters_path.read_text(
        encoding="utf-8"
    )


def test_inspection_fails_loudly_on_missing_required_files(tmp_path: Path) -> None:
    artifact_dir = build_bundle(tmp_path)
    (artifact_dir / "config.json").unlink()

    with pytest.raises(FileNotFoundError, match="missing required synth-small artifact files"):
        inspect_synth_small_artifacts(artifact_dir)


def test_inspection_detects_shape_mismatch(tmp_path: Path) -> None:
    artifact_dir = build_bundle(tmp_path)
    surfaces = np.load(artifact_dir / "surfaces.npz")
    try:
        bad_carrying_capacity = surfaces["carrying_capacity"][:-1, :]
    finally:
        surfaces.close()
    overwrite_surfaces(artifact_dir, carrying_capacity=bad_carrying_capacity)

    inspection = inspect_synth_small_artifacts(artifact_dir)

    checks = {check.name: check for check in inspection.verification_checks}
    assert inspection.passed is False
    assert checks["shape_consistency"].passed is False


def test_inspection_detects_out_of_bounds_suitability(tmp_path: Path) -> None:
    artifact_dir = build_bundle(tmp_path)
    surfaces = np.load(artifact_dir / "surfaces.npz")
    try:
        suitability = np.array(surfaces["suitability"], copy=True)
    finally:
        surfaces.close()
    suitability[0, 0] = 1.5
    overwrite_surfaces(artifact_dir, suitability=suitability)

    inspection = inspect_synth_small_artifacts(artifact_dir)

    checks = {check.name: check for check in inspection.verification_checks}
    assert inspection.passed is False
    assert checks["suitability_bounds"].passed is False


def test_inspection_detects_non_binary_occupancy(tmp_path: Path) -> None:
    artifact_dir = build_bundle(tmp_path)
    surfaces = np.load(artifact_dir / "surfaces.npz")
    try:
        occupancy = np.array(surfaces["occupancy"], copy=True)
    finally:
        surfaces.close()
    occupancy[0, 0] = 2
    overwrite_surfaces(artifact_dir, occupancy=occupancy)

    inspection = inspect_synth_small_artifacts(artifact_dir)

    checks = {check.name: check for check in inspection.verification_checks}
    assert inspection.passed is False
    assert checks["occupancy_binary"].passed is False


def test_inspection_detects_inconsistent_summary_statistics(tmp_path: Path) -> None:
    artifact_dir = build_bundle(tmp_path)
    summary = loads((artifact_dir / "summary.json").read_text(encoding="utf-8"))
    summary["summary"]["equilibrium_abundance_mean"] = -1.0
    (artifact_dir / "summary.json").write_text(dumps(summary, indent=2) + "\n", encoding="utf-8")

    inspection = inspect_synth_small_artifacts(artifact_dir)

    checks = {check.name: check for check in inspection.verification_checks}
    assert inspection.passed is False
    assert checks["summary_consistency"].passed is False
