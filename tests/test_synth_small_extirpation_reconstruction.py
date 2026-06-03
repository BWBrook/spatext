from __future__ import annotations

from csv import DictReader
from json import loads
from pathlib import Path

import numpy as np

from spatext.synth.small import (
    build_synth_small_extirpation_reconstruction,
    build_synth_small_observations,
    inspect_synth_small_extirpation_reconstruction_artifacts,
)
from spatext.synth.small.observations import FORBIDDEN_ANALYST_COLUMNS

FORBIDDEN_OUTPUT_COLUMNS = FORBIDDEN_ANALYST_COLUMNS | frozenset({"predator_pressure"})


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def build_observation_bundle(tmp_path: Path) -> Path:
    observations_output = tmp_path / "observations"
    build_synth_small_observations().write_artifacts(observations_output)
    return observations_output


def build_reconstruction_bundle(tmp_path: Path) -> Path:
    obs_dir = build_observation_bundle(tmp_path)
    reconstruction_output = tmp_path / "reconstruction"
    result = build_synth_small_extirpation_reconstruction(obs_dir)
    result.write_artifacts(reconstruction_output)
    return reconstruction_output


def test_reconstruction_outputs_are_deterministic_under_default_inputs(tmp_path: Path) -> None:
    first = build_reconstruction_bundle(tmp_path / "first")
    second = build_reconstruction_bundle(tmp_path / "second")

    for name in ("site_reconstruction.csv", "time_detection_summary.csv"):
        assert (first / name).read_text(encoding="utf-8") == (second / name).read_text(
            encoding="utf-8"
        )

    first_metrics = loads((first / "evaluation_metrics.json").read_text(encoding="utf-8"))
    second_metrics = loads((second / "evaluation_metrics.json").read_text(encoding="utf-8"))
    assert first_metrics["confusion_matrix"] == second_metrics["confusion_matrix"]

    first_config = loads((first / "reconstruction_config.json").read_text(encoding="utf-8"))
    second_config = loads((second / "reconstruction_config.json").read_text(encoding="utf-8"))
    assert first_config["config"] == second_config["config"]


def test_reconstruction_outputs_required_files_and_schema(tmp_path: Path) -> None:
    output_dir = build_reconstruction_bundle(tmp_path)
    for name in (
        "reconstruction_config.json",
        "site_reconstruction.csv",
        "time_detection_summary.csv",
        "verification.json",
        "evaluation_metrics.json",
        "report.md",
    ):
        path = output_dir / name
        assert path.exists()
        assert path.stat().st_size > 0

    site_rows = read_csv_rows(output_dir / "site_reconstruction.csv")
    time_rows = read_csv_rows(output_dir / "time_detection_summary.csv")
    assert site_rows
    assert time_rows
    assert {
        "site_id",
        "cell_id",
        "row",
        "col",
        "region",
        "front_band",
    }.issubset(site_rows[0])
    assert {
        "time_index",
        "visit_count",
        "site_count",
        "observation_count",
        "detection_count",
    }.issubset(time_rows[0])


def test_reconstruction_output_has_no_hidden_truth_columns(tmp_path: Path) -> None:
    output_dir = build_reconstruction_bundle(tmp_path)
    site_rows = read_csv_rows(output_dir / "site_reconstruction.csv")
    assert set(site_rows[0]).isdisjoint(FORBIDDEN_OUTPUT_COLUMNS)


def test_reconstruction_handles_no_survey_and_no_detections(tmp_path: Path) -> None:
    observations_dir = build_observation_bundle(tmp_path)
    sites = read_csv_rows(observations_dir / "sites.csv")
    observations = read_csv_rows(observations_dir / "observations.csv")
    assert len(sites) >= 3

    no_survey_site = sites[0]["site_id"]
    never_detect_site = sites[1]["site_id"]
    filtered_observations = [
        row for row in observations if row["site_id"] not in (no_survey_site, never_detect_site)
    ]
    filtered_no_detect = [
        {
            **row,
            "detected": "0",
            "observed_count": "0",
        }
        for row in observations
        if row["site_id"] == never_detect_site
    ]
    with (observations_dir / "observations.csv").open("w", newline="", encoding="utf-8") as handle:
        header = observations[0].keys()
        handle.write(",".join(header) + "\n")
        for row in filtered_observations + filtered_no_detect:
            handle.write(",".join(row[col] for col in header) + "\n")

    result = build_synth_small_extirpation_reconstruction(observations_dir)
    status_by_site = {row.site_id: row.reconstruction_status for row in result.site_rows}
    assert status_by_site[no_survey_site] == "no_surveyed_times"
    assert status_by_site[never_detect_site] == "insufficient_history"


def test_evaluation_metrics_are_complete_and_finite_where_defined(tmp_path: Path) -> None:
    output_dir = build_reconstruction_bundle(tmp_path)
    metrics = loads((output_dir / "evaluation_metrics.json").read_text(encoding="utf-8"))

    assert {
        "site_coverage",
        "confusion_matrix",
        "sensitivity",
        "specificity",
        "precision",
    }.issubset(metrics)
    assert metrics["site_coverage"]["site_count"] == 625
    assert metrics["site_coverage"]["aligned_site_count"] == 625

    for value in (
        metrics["sensitivity"],
        metrics["specificity"],
        metrics["precision"],
    ):
        if value is not None:
            assert np.isfinite(value)

    temporal = metrics["temporal_error"]
    assert "count" in temporal
    if temporal["count"] > 0:
        assert np.isfinite(temporal["mae"])


def test_reconstruction_inspection_reports_are_written(tmp_path: Path) -> None:
    output_dir = build_reconstruction_bundle(tmp_path)
    inspection = inspect_synth_small_extirpation_reconstruction_artifacts(
        artifact_dir=output_dir,
        output_dir=tmp_path / "inspection",
    )

    assert inspection.passed is True
    assert inspection.verification_path.exists()
    assert inspection.verification_path.stat().st_size > 0
    assert inspection.report_path.exists()
    assert inspection.report_path.stat().st_size > 0
