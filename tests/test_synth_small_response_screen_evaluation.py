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
    evaluate_synth_small_response_screen,
    inspect_synth_small_response_screen_artifacts,
)

RESPONSE_SCREEN_FILES = (
    "response_screen_config.json",
    "screen_summary.json",
    "group_screen_summary.csv",
    "time_screen_summary.csv",
    "verification.json",
    "report.md",
)
INSPECTION_FILES = (
    "inspection/verification.json",
    "inspection/review_summary.json",
    "inspection/group_review_summary.csv",
    "inspection/report.md",
)
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


def build_screen_stack(tmp_path: Path) -> tuple[Path, Path, Path]:
    observation_dir = tmp_path / "observations"
    build_synth_small_observations().write_artifacts(observation_dir)

    reconstruction_dir = tmp_path / "reconstruction"
    reconstruction = build_synth_small_extirpation_reconstruction(observation_dir)
    reconstruction.write_artifacts(reconstruction_dir)

    screen_dir = tmp_path / "screen"
    screen = build_response_only_screen(reconstruction_dir)
    screen.write_artifacts(screen_dir)
    inspection = inspect_synth_small_response_screen_artifacts(screen_dir)
    assert inspection.passed is True
    return observation_dir, reconstruction_dir, screen_dir


def snapshot_screen_contract(screen_dir: Path) -> dict[str, str]:
    names = RESPONSE_SCREEN_FILES + INSPECTION_FILES
    return {name: (screen_dir / name).read_text(encoding="utf-8") for name in names}


def assert_no_forbidden_response_fields(payload: object) -> None:
    if isinstance(payload, dict):
        assert set(payload).isdisjoint(FORBIDDEN_RESPONSE_FIELDS)
        for value in payload.values():
            assert_no_forbidden_response_fields(value)
    elif isinstance(payload, list | tuple):
        for value in payload:
            assert_no_forbidden_response_fields(value)


def test_response_screen_evaluation_writes_synthetic_only_audit(tmp_path: Path) -> None:
    observation_dir, reconstruction_dir, screen_dir = build_screen_stack(tmp_path)
    before = snapshot_screen_contract(screen_dir)

    result = evaluate_synth_small_response_screen(
        screen_dir=screen_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    )
    output_dir = tmp_path / "evaluation"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == {
        "evaluation_config.json",
        "screen_evaluation_summary.json",
        "group_evaluation_summary.csv",
        "site_evaluation_audit.csv",
        "verification.json",
        "report.md",
    }
    assert snapshot_screen_contract(screen_dir) == before

    summary = loads((output_dir / "screen_evaluation_summary.json").read_text("utf-8"))
    groups = read_csv_rows(output_dir / "group_evaluation_summary.csv")
    sites = read_csv_rows(output_dir / "site_evaluation_audit.csv")
    verification = loads((output_dir / "verification.json").read_text("utf-8"))

    assert summary["evaluation_only"] is True
    assert summary["screen_decision"] == "screen_with_caution"
    assert summary["classification"]["confusion_matrix"] == {
        "tp": 151,
        "fp": 0,
        "tn": 373,
        "fn": 101,
    }
    assert summary["classification"]["false_negative_count"] == 101
    assert summary["failure_modes"]["weak_signal_group_count"] >= 2
    assert verification["passed"] is True
    assert groups
    assert sites
    assert {"true_extirpated_by_end", "screen_call"}.issubset(sites[0])


def test_response_screen_evaluation_outputs_are_labelled_evaluation_only(
    tmp_path: Path,
) -> None:
    observation_dir, reconstruction_dir, screen_dir = build_screen_stack(tmp_path)
    output_dir = tmp_path / "evaluation"

    evaluate_synth_small_response_screen(
        screen_dir=screen_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    ).write_artifacts(output_dir)

    for name in (
        "evaluation_config.json",
        "screen_evaluation_summary.json",
        "verification.json",
    ):
        payload = loads((output_dir / name).read_text("utf-8"))
        assert payload["evaluation_only"] is True

    for name in RESPONSE_SCREEN_FILES:
        path = screen_dir / name
        if path.suffix == ".json":
            assert_no_forbidden_response_fields(loads(path.read_text("utf-8")))
        elif path.suffix == ".csv":
            rows = read_csv_rows(path)
            assert rows
            assert set(rows[0]).isdisjoint(FORBIDDEN_RESPONSE_FIELDS)


def test_response_screen_evaluation_fails_without_truth_artifact(tmp_path: Path) -> None:
    observation_dir, reconstruction_dir, screen_dir = build_screen_stack(tmp_path)
    (observation_dir / "evaluation_truth.csv").unlink()

    try:
        evaluate_synth_small_response_screen(
            screen_dir=screen_dir,
            reconstruction_dir=reconstruction_dir,
            observation_dir=observation_dir,
        )
    except FileNotFoundError as exc:
        assert "evaluation_truth.csv" in str(exc)
    else:
        raise AssertionError("missing evaluation truth should fail loudly")


def test_response_screen_evaluation_cli_writes_default_bundle(tmp_path: Path) -> None:
    observation_dir, reconstruction_dir, screen_dir = build_screen_stack(tmp_path)
    output_dir = tmp_path / "evaluation"

    completed = run(
        [
            executable,
            "scripts/evaluate_synth_small_response_screen.py",
            "--screen-dir",
            str(screen_dir),
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

    assert "Response screen evaluation complete" in completed.stdout
    summary = loads((output_dir / "screen_evaluation_summary.json").read_text("utf-8"))
    assert summary["evaluation_only"] is True
    assert summary["screen_decision"] == "screen_with_caution"
