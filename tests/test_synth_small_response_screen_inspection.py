from __future__ import annotations

from csv import DictReader
from json import dumps, loads
from pathlib import Path
from subprocess import run
from sys import executable

import pytest

from spatext.synth.small import (
    build_response_only_screen,
    build_synth_small_extirpation_reconstruction,
    build_synth_small_observations,
    inspect_synth_small_response_screen_artifacts,
)

FORBIDDEN_INSPECTION_FIELDS = {
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


def build_screen_bundle(tmp_path: Path) -> Path:
    observations_dir = tmp_path / "observations"
    build_synth_small_observations().write_artifacts(observations_dir)

    reconstruction_dir = tmp_path / "reconstruction"
    reconstruction = build_synth_small_extirpation_reconstruction(observations_dir)
    reconstruction.write_artifacts(reconstruction_dir)

    screen_dir = tmp_path / "screen"
    screen = build_response_only_screen(reconstruction_dir)
    screen.write_artifacts(screen_dir)
    return screen_dir


def assert_no_forbidden_fields(payload: object) -> None:
    if isinstance(payload, dict):
        assert set(payload).isdisjoint(FORBIDDEN_INSPECTION_FIELDS)
        for value in payload.values():
            assert_no_forbidden_fields(value)
    elif isinstance(payload, list | tuple):
        for value in payload:
            assert_no_forbidden_fields(value)


def test_response_screen_inspection_writes_review_bundle(tmp_path: Path) -> None:
    screen_dir = build_screen_bundle(tmp_path)

    inspection = inspect_synth_small_response_screen_artifacts(
        screen_dir,
        output_dir=tmp_path / "inspection",
    )

    assert inspection.passed is True
    for path in (
        inspection.verification_path,
        inspection.review_summary_path,
        inspection.group_review_path,
        inspection.report_path,
    ):
        assert path.exists()
        assert path.stat().st_size > 0

    verification = loads(inspection.verification_path.read_text(encoding="utf-8"))
    review = loads(inspection.review_summary_path.read_text(encoding="utf-8"))
    group_rows = read_csv_rows(inspection.group_review_path)

    assert verification["passed"] is True
    assert review["screen_decision"] == "screen_with_caution"
    assert review["site_count"] == 625
    assert review["review_flags"]["late_screen_bias_warning"] is True
    assert group_rows
    assert {row["group_type"] for row in group_rows} == {"region", "front_band"}


def test_response_screen_inspection_fails_loudly_on_missing_required_file(
    tmp_path: Path,
) -> None:
    screen_dir = build_screen_bundle(tmp_path)
    (screen_dir / "screen_summary.json").unlink()

    with pytest.raises(
        FileNotFoundError,
        match="missing required response screen artifacts",
    ):
        inspect_synth_small_response_screen_artifacts(screen_dir)


def test_response_screen_inspection_ignores_decoy_evaluation_payload(
    tmp_path: Path,
) -> None:
    screen_dir = build_screen_bundle(tmp_path)
    (screen_dir / "evaluation_metrics.json").write_text(
        dumps(
            {
                "true_extirpation": "decoy",
                "driver_arrival": "decoy",
                "evaluation_truth": "decoy",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    inspection = inspect_synth_small_response_screen_artifacts(
        screen_dir,
        output_dir=tmp_path / "inspection",
    )

    for name in ("verification.json", "review_summary.json"):
        payload = loads((inspection.output_dir / name).read_text(encoding="utf-8"))
        assert_no_forbidden_fields(payload)
    rows = read_csv_rows(inspection.group_review_path)
    assert rows
    assert set(rows[0]).isdisjoint(FORBIDDEN_INSPECTION_FIELDS)


def test_response_screen_inspection_cli_writes_default_bundle(tmp_path: Path) -> None:
    screen_dir = build_screen_bundle(tmp_path)

    completed = run(
        [
            executable,
            "scripts/inspect_synth_small_response_screen.py",
            "--artifact-dir",
            str(screen_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Response screen inspection passed" in completed.stdout
    verification = loads((screen_dir / "inspection" / "verification.json").read_text("utf-8"))
    assert verification["passed"] is True
