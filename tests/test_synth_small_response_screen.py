from __future__ import annotations

from csv import DictReader
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable

from spatext.synth.small import (
    build_response_only_screen,
    build_synth_small_extirpation_reconstruction,
    build_synth_small_observations,
)

FORBIDDEN_SCREEN_FIELDS = {
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


def build_reconstruction_bundle(tmp_path: Path) -> Path:
    observations_dir = tmp_path / "observations"
    build_synth_small_observations().write_artifacts(observations_dir)

    reconstruction_dir = tmp_path / "reconstruction"
    result = build_synth_small_extirpation_reconstruction(observations_dir)
    result.write_artifacts(reconstruction_dir)
    return reconstruction_dir


def assert_no_forbidden_fields(payload: object) -> None:
    if isinstance(payload, dict):
        assert set(payload).isdisjoint(FORBIDDEN_SCREEN_FIELDS)
        for value in payload.values():
            assert_no_forbidden_fields(value)
    elif isinstance(payload, list | tuple):
        for value in payload:
            assert_no_forbidden_fields(value)


def test_response_screen_writes_response_only_artifacts(tmp_path: Path) -> None:
    reconstruction_dir = build_reconstruction_bundle(tmp_path)

    result = build_response_only_screen(reconstruction_dir)
    output_dir = tmp_path / "screen"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == {
        "response_screen_config.json",
        "screen_summary.json",
        "group_screen_summary.csv",
        "time_screen_summary.csv",
        "verification.json",
        "report.md",
    }

    summary = loads((output_dir / "screen_summary.json").read_text(encoding="utf-8"))
    verification = loads((output_dir / "verification.json").read_text(encoding="utf-8"))
    groups = read_csv_rows(output_dir / "group_screen_summary.csv")
    times = read_csv_rows(output_dir / "time_screen_summary.csv")

    assert summary["site_count"] == 625
    assert summary["observed_extirpated_site_count"] == 151
    assert summary["screen_decision"] == "screen_with_caution"
    assert summary["failure_modes"]["not_observed_extirpated_fraction"] > 0.70
    assert summary["failure_modes"]["late_screen_bias_warning"] is True
    assert verification["passed"] is True
    assert groups
    assert times
    assert {row["group_type"] for row in groups} == {"region", "front_band"}
    assert all("observed_extirpated_fraction" in row for row in groups)
    assert all("detection_rate" in row for row in times)


def test_response_screen_outputs_are_deterministic(tmp_path: Path) -> None:
    reconstruction_dir = build_reconstruction_bundle(tmp_path)
    first_dir = tmp_path / "first_screen"
    second_dir = tmp_path / "second_screen"

    build_response_only_screen(reconstruction_dir).write_artifacts(first_dir)
    build_response_only_screen(reconstruction_dir).write_artifacts(second_dir)

    for name in (
        "response_screen_config.json",
        "screen_summary.json",
        "group_screen_summary.csv",
        "time_screen_summary.csv",
        "verification.json",
        "report.md",
    ):
        assert (first_dir / name).read_text(encoding="utf-8") == (second_dir / name).read_text(
            encoding="utf-8"
        )


def test_response_screen_artifacts_do_not_emit_hidden_truth_fields(tmp_path: Path) -> None:
    reconstruction_dir = build_reconstruction_bundle(tmp_path)
    output_dir = tmp_path / "screen"

    build_response_only_screen(reconstruction_dir).write_artifacts(output_dir)

    for name in (
        "response_screen_config.json",
        "screen_summary.json",
        "verification.json",
    ):
        payload = loads((output_dir / name).read_text(encoding="utf-8"))
        assert_no_forbidden_fields(payload)

    for name in ("group_screen_summary.csv", "time_screen_summary.csv"):
        rows = read_csv_rows(output_dir / name)
        assert rows
        assert set(rows[0]).isdisjoint(FORBIDDEN_SCREEN_FIELDS)


def test_response_screen_cli_writes_default_bundle(tmp_path: Path) -> None:
    reconstruction_dir = build_reconstruction_bundle(tmp_path)
    output_dir = tmp_path / "screen"

    completed = run(
        [
            executable,
            "scripts/run_synth_small_response_screen.py",
            "--reconstruction-dir",
            str(reconstruction_dir),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Response screen complete" in completed.stdout
    summary = loads((output_dir / "screen_summary.json").read_text(encoding="utf-8"))
    assert summary["screen_decision"] == "screen_with_caution"
    assert (
        (output_dir / "report.md")
        .read_text(encoding="utf-8")
        .startswith("# Synth-Small Response-Only Screen")
    )
