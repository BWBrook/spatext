from __future__ import annotations

from json import dumps, loads
from pathlib import Path

import numpy as np
import pytest

from spatext.synth.small import (
    build_synth_small_predator_truth,
    inspect_synth_small_predator_truth_artifacts,
)


def build_predator_bundle(tmp_path: Path) -> Path:
    artifact_dir = tmp_path / "predator-truth"
    result = build_synth_small_predator_truth()
    result.write_artifacts(artifact_dir)
    return artifact_dir


def overwrite_surfaces(
    artifact_dir: Path,
    *,
    true_extirpation: np.ndarray | None = None,
    extirpation_lag: np.ndarray | None = None,
    final_abundance: np.ndarray | None = None,
) -> None:
    surfaces = np.load(artifact_dir / "surfaces.npz")
    try:
        updated = {
            "suitability": surfaces["suitability"],
            "carrying_capacity": surfaces["carrying_capacity"],
            "initial_abundance": surfaces["initial_abundance"],
            "driver_arrival": surfaces["driver_arrival"],
            "extirpation_threshold": surfaces["extirpation_threshold"],
            "true_extirpation": (
                true_extirpation if true_extirpation is not None else surfaces["true_extirpation"]
            ),
            "extirpation_lag": (
                extirpation_lag if extirpation_lag is not None else surfaces["extirpation_lag"]
            ),
            "final_abundance": (
                final_abundance if final_abundance is not None else surfaces["final_abundance"]
            ),
        }
    finally:
        surfaces.close()
    np.savez_compressed(artifact_dir / "surfaces.npz", **updated)


def overwrite_trajectories(
    artifact_dir: Path,
    *,
    prey_abundance: np.ndarray | None = None,
) -> None:
    trajectories = np.load(artifact_dir / "trajectories.npz")
    try:
        updated = {
            "prey_abundance": (
                prey_abundance if prey_abundance is not None else trajectories["prey_abundance"]
            ),
            "predator_pressure": trajectories["predator_pressure"],
        }
    finally:
        trajectories.close()
    np.savez_compressed(artifact_dir / "trajectories.npz", **updated)


def test_predator_truth_inspection_outputs_are_created_for_valid_bundle(
    tmp_path: Path,
) -> None:
    artifact_dir = build_predator_bundle(tmp_path)

    inspection = inspect_synth_small_predator_truth_artifacts(artifact_dir)

    assert inspection.passed is True
    assert inspection.output_dir == artifact_dir / "inspection"
    assert inspection.verification_path.exists()
    assert inspection.parameters_path.exists()
    assert inspection.surface_summary_path.exists()
    assert inspection.trajectory_summary_path.exists()
    assert inspection.extirpation_summary_path.exists()
    assert inspection.report_path.exists()

    verification = loads(inspection.verification_path.read_text(encoding="utf-8"))
    assert verification["passed"] is True
    assert verification["warning_count"] == 0

    report_text = inspection.report_path.read_text(encoding="utf-8")
    assert "Synth-Small Predator-Truth Inspection Report" in report_text
    assert "![Driver Arrival](../driver_arrival.svg)" in report_text
    assert "low_initial_extirpation_rate" in report_text


def test_predator_truth_inspection_fails_loudly_on_missing_required_files(
    tmp_path: Path,
) -> None:
    artifact_dir = build_predator_bundle(tmp_path)
    (artifact_dir / "summary.json").unlink()

    with pytest.raises(
        FileNotFoundError,
        match="missing required synth-small predator-truth artifact files",
    ):
        inspect_synth_small_predator_truth_artifacts(artifact_dir)


def test_predator_truth_inspection_fails_loudly_on_corrupted_npz(
    tmp_path: Path,
) -> None:
    artifact_dir = build_predator_bundle(tmp_path)
    (artifact_dir / "surfaces.npz").write_text("not an npz archive", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match=r"failed to load synth-small predator-truth surfaces\.npz",
    ):
        inspect_synth_small_predator_truth_artifacts(artifact_dir)


def test_predator_truth_inspection_detects_extirpation_before_arrival(
    tmp_path: Path,
) -> None:
    artifact_dir = build_predator_bundle(tmp_path)
    surfaces = np.load(artifact_dir / "surfaces.npz")
    try:
        true_extirpation = np.array(surfaces["true_extirpation"], copy=True)
        extirpation_lag = np.array(surfaces["extirpation_lag"], copy=True)
        driver_arrival = np.array(surfaces["driver_arrival"], copy=True)
    finally:
        surfaces.close()
    true_extirpation[0, 0] = float(driver_arrival[0, 0] - 1)
    extirpation_lag[0, 0] = -1.0
    overwrite_surfaces(
        artifact_dir,
        true_extirpation=true_extirpation,
        extirpation_lag=extirpation_lag,
    )

    inspection = inspect_synth_small_predator_truth_artifacts(artifact_dir)

    checks = {check.name: check for check in inspection.verification_checks}
    assert inspection.passed is False
    assert checks["extirpation_semantics"].passed is False


def test_predator_truth_inspection_detects_trajectory_endpoint_mismatch(
    tmp_path: Path,
) -> None:
    artifact_dir = build_predator_bundle(tmp_path)
    trajectories = np.load(artifact_dir / "trajectories.npz")
    try:
        prey_abundance = np.array(trajectories["prey_abundance"], copy=True)
    finally:
        trajectories.close()
    prey_abundance[-1, 0, 0] += 10.0
    overwrite_trajectories(artifact_dir, prey_abundance=prey_abundance)

    inspection = inspect_synth_small_predator_truth_artifacts(artifact_dir)

    checks = {check.name: check for check in inspection.verification_checks}
    assert inspection.passed is False
    assert checks["trajectory_consistency"].passed is False


def test_predator_truth_inspection_detects_inconsistent_summary(
    tmp_path: Path,
) -> None:
    artifact_dir = build_predator_bundle(tmp_path)
    summary = loads((artifact_dir / "summary.json").read_text(encoding="utf-8"))
    summary["summary"]["extirpated_count"] = -1
    (artifact_dir / "summary.json").write_text(
        dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    inspection = inspect_synth_small_predator_truth_artifacts(artifact_dir)

    checks = {check.name: check for check in inspection.verification_checks}
    assert inspection.passed is False
    assert checks["summary_consistency"].passed is False
