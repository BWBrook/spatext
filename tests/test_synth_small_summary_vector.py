from __future__ import annotations

from csv import DictReader, DictWriter
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable

import pytest

from spatext.synth.small import (
    build_synth_small_extirpation_reconstruction,
    build_synth_small_observations,
    build_synth_small_summary_vector,
)

SUMMARY_VECTOR_FILES = {
    "summary_vector_config.json",
    "summary_components.csv",
    "mode_summary.json",
    "coverage_curve.csv",
    "verification.json",
    "report.md",
}
FORBIDDEN_RESPONSE_FIELDS = {
    "driver_arrival",
    "predator_pressure",
    "true_extirpation",
    "extirpation_lag",
    "extirpated_by_end",
    "initial_abundance",
    "final_abundance",
    "evaluation_truth",
    "evaluation_metrics",
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def build_summary_inputs(tmp_path: Path) -> tuple[Path, Path]:
    observation_dir = tmp_path / "observations"
    build_synth_small_observations().write_artifacts(observation_dir)

    reconstruction_dir = tmp_path / "reconstruction"
    reconstruction = build_synth_small_extirpation_reconstruction(observation_dir)
    reconstruction.write_artifacts(reconstruction_dir)
    return observation_dir, reconstruction_dir


def component_map(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["mode"], row["component"]): row for row in read_csv_rows(path)}


def snapshot_reconstruction_response_files(reconstruction_dir: Path) -> dict[str, str]:
    names = (
        "reconstruction_config.json",
        "site_reconstruction.csv",
        "time_detection_summary.csv",
        "verification.json",
        "report.md",
    )
    return {name: (reconstruction_dir / name).read_text(encoding="utf-8") for name in names}


def assert_no_forbidden_response_fields(payload: object) -> None:
    if isinstance(payload, dict):
        assert set(payload).isdisjoint(FORBIDDEN_RESPONSE_FIELDS)
        for value in payload.values():
            assert_no_forbidden_response_fields(value)
    elif isinstance(payload, list | tuple):
        for value in payload:
            assert_no_forbidden_response_fields(value)


def blank_observed_extirpation_targets(reconstruction_dir: Path) -> None:
    path = reconstruction_dir / "site_reconstruction.csv"
    rows = list(read_csv_rows(path))
    assert rows
    fieldnames = list(rows[0])
    for row in rows:
        row["observed_extirpated_by_end"] = "0"
        row["observed_extirpation_time"] = ""
        row["reconstruction_status"] = "not_observed_extirpated_by_end"
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = DictWriter(handle, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(rows)


def test_summary_vector_writes_both_synthetic_modes(tmp_path: Path) -> None:
    observation_dir, reconstruction_dir = build_summary_inputs(tmp_path)

    result = build_synth_small_summary_vector(
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    )
    output_dir = tmp_path / "summary_vector"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == SUMMARY_VECTOR_FILES

    config = loads((output_dir / "summary_vector_config.json").read_text(encoding="utf-8"))
    mode_summary = loads((output_dir / "mode_summary.json").read_text(encoding="utf-8"))
    verification = loads((output_dir / "verification.json").read_text(encoding="utf-8"))
    components = component_map(output_dir / "summary_components.csv")
    coverage_rows = read_csv_rows(output_dir / "coverage_curve.csv")

    assert config["synthetic_only"] is True
    assert mode_summary["synthetic_only"] is True
    assert set(mode_summary["modes"]) == {"ideal_true", "realistic_observed"}
    assert verification["passed"] is True

    assert components[("ideal_true", "finite_target_count")]["value"] == "252"
    assert components[("realistic_observed", "finite_target_count")]["value"] == "151"
    assert components[("ideal_true", "lag_count")]["value"] == "252"
    assert components[("realistic_observed", "lag_count")]["value"] == "151"
    assert components[("ideal_true", "arrival_target_r2")]["missing_reason"] == ""
    assert (
        components[("realistic_observed", "front_plane_gradient_magnitude")]["missing_reason"] == ""
    )
    assert len(coverage_rows) == 10
    assert {row["mode"] for row in coverage_rows} == {"ideal_true", "realistic_observed"}


def test_summary_vector_records_missing_reasons_for_undefined_metrics(
    tmp_path: Path,
) -> None:
    observation_dir, reconstruction_dir = build_summary_inputs(tmp_path)
    blank_observed_extirpation_targets(reconstruction_dir)

    result = build_synth_small_summary_vector(
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    )
    output_dir = tmp_path / "summary_vector"
    result.write_artifacts(output_dir)

    components = component_map(output_dir / "summary_components.csv")
    coverage_rows = read_csv_rows(output_dir / "coverage_curve.csv")

    assert components[("realistic_observed", "finite_target_count")]["value"] == "0"
    assert components[("realistic_observed", "lag_mean")]["value"] == ""
    assert components[("realistic_observed", "lag_mean")]["missing_reason"] == (
        "no_finite_lag_pairs"
    )
    assert components[("realistic_observed", "arrival_target_r2")]["missing_reason"] == (
        "insufficient_finite_pairs"
    )
    assert {
        row["missing_reason"] for row in coverage_rows if row["mode"] == "realistic_observed"
    } == {"no_finite_target"}


def test_summary_vector_does_not_rewrite_response_only_artifacts(tmp_path: Path) -> None:
    observation_dir, reconstruction_dir = build_summary_inputs(tmp_path)
    before = snapshot_reconstruction_response_files(reconstruction_dir)

    build_synth_small_summary_vector(
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    ).write_artifacts(tmp_path / "summary_vector")

    assert snapshot_reconstruction_response_files(reconstruction_dir) == before
    for name, text in before.items():
        if name.endswith(".json"):
            assert_no_forbidden_response_fields(loads(text))
        elif name.endswith(".csv"):
            rows = read_csv_rows(reconstruction_dir / name)
            assert rows
            assert set(rows[0]).isdisjoint(FORBIDDEN_RESPONSE_FIELDS)


def test_summary_vector_fails_loudly_when_required_truth_artifact_is_missing(
    tmp_path: Path,
) -> None:
    observation_dir, reconstruction_dir = build_summary_inputs(tmp_path)
    (observation_dir / "evaluation_truth.csv").unlink()

    with pytest.raises(FileNotFoundError, match=r"evaluation_truth\.csv"):
        build_synth_small_summary_vector(
            reconstruction_dir=reconstruction_dir,
            observation_dir=observation_dir,
        )


def test_summary_vector_cli_writes_default_bundle(tmp_path: Path) -> None:
    observation_dir, reconstruction_dir = build_summary_inputs(tmp_path)
    output_dir = tmp_path / "summary_vector"

    completed = run(
        [
            executable,
            "scripts/build_synth_small_summary_vector.py",
            "--reconstruction-dir",
            str(reconstruction_dir),
            "--observation-dir",
            str(observation_dir),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Summary vector complete" in completed.stdout
    mode_summary = loads((output_dir / "mode_summary.json").read_text(encoding="utf-8"))
    assert mode_summary["synthetic_only"] is True
    assert set(mode_summary["modes"]) == {"ideal_true", "realistic_observed"}
