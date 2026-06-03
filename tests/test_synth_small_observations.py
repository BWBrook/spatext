from __future__ import annotations

from csv import DictReader
from json import loads
from math import isfinite
from pathlib import Path

import pytest

from spatext.synth.small import (
    build_synth_small_observations,
    inspect_synth_small_observation_artifacts,
)

FORBIDDEN_ANALYST_COLUMNS = {
    "driver_arrival",
    "predator_pressure",
    "true_extirpation",
    "extirpation_lag",
    "extirpated_by_end",
    "initial_abundance",
    "final_abundance",
}


def csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def csv_header(path: Path) -> set[str]:
    rows = csv_rows(path)
    assert rows
    return set(rows[0])


def build_observation_bundle(tmp_path: Path) -> Path:
    output_dir = tmp_path / "observations"
    result = build_synth_small_observations()
    result.write_artifacts(output_dir)
    return output_dir


def test_synth_small_observations_are_reproducible_under_default_seed(
    tmp_path: Path,
) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    build_synth_small_observations().write_artifacts(first_dir)
    build_synth_small_observations().write_artifacts(second_dir)

    for name in (
        "observation_config.json",
        "truth_reference.json",
        "sites.csv",
        "visits.csv",
        "observations.csv",
        "evaluation_truth.csv",
    ):
        assert (first_dir / name).read_text(encoding="utf-8") == (second_dir / name).read_text(
            encoding="utf-8"
        )


def test_synth_small_observation_bundle_writes_required_files_and_schemas(
    tmp_path: Path,
) -> None:
    output_dir = build_observation_bundle(tmp_path)

    for name in (
        "observation_config.json",
        "truth_reference.json",
        "sites.csv",
        "visits.csv",
        "observations.csv",
        "evaluation_truth.csv",
    ):
        path = output_dir / name
        assert path.exists()
        assert path.stat().st_size > 0

    assert {
        "site_id",
        "cell_id",
        "row",
        "col",
        "region",
        "front_band",
    }.issubset(csv_header(output_dir / "sites.csv"))
    assert {
        "visit_id",
        "site_id",
        "cell_id",
        "time_index",
        "visit_replicate",
        "effort",
        "region",
    }.issubset(csv_header(output_dir / "visits.csv"))
    assert {
        "visit_id",
        "site_id",
        "cell_id",
        "time_index",
        "visit_replicate",
        "effort",
        "observed_count",
        "detected",
    }.issubset(csv_header(output_dir / "observations.csv"))
    assert {
        "site_id",
        "cell_id",
        "driver_arrival",
        "true_extirpation",
        "extirpation_lag",
        "extirpated_by_end",
    }.issubset(csv_header(output_dir / "evaluation_truth.csv"))


def test_analyst_facing_observation_tables_exclude_predator_truth_columns(
    tmp_path: Path,
) -> None:
    output_dir = build_observation_bundle(tmp_path)

    for name in ("sites.csv", "visits.csv", "observations.csv"):
        assert csv_header(output_dir / name).isdisjoint(FORBIDDEN_ANALYST_COLUMNS)


def test_observation_inspection_fails_loudly_on_missing_required_file(
    tmp_path: Path,
) -> None:
    output_dir = build_observation_bundle(tmp_path)
    (output_dir / "observations.csv").unlink()

    with pytest.raises(
        FileNotFoundError,
        match="missing required synth-small observation artifact files",
    ):
        inspect_synth_small_observation_artifacts(output_dir)


def test_observation_inspection_detects_malformed_detection_indicator(
    tmp_path: Path,
) -> None:
    output_dir = build_observation_bundle(tmp_path)
    rows = list(csv_rows(output_dir / "observations.csv"))
    rows[0]["observed_count"] = "3"
    rows[0]["detected"] = "0"
    header = tuple(rows[0])
    with (output_dir / "observations.csv").open("w", newline="", encoding="utf-8") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row[column] for column in header) + "\n")

    inspection = inspect_synth_small_observation_artifacts(output_dir)

    checks = {check.name: check for check in inspection.verification_checks}
    assert inspection.passed is False
    assert checks["observation_values"].passed is False


def test_observation_inspection_outputs_finite_recoverability_smoke_metrics(
    tmp_path: Path,
) -> None:
    output_dir = build_observation_bundle(tmp_path)

    inspection = inspect_synth_small_observation_artifacts(output_dir)

    assert inspection.passed is True
    for path in (
        inspection.verification_path,
        inspection.observation_summary_path,
        inspection.recoverability_smoke_path,
        inspection.report_path,
    ):
        assert path.exists()
        assert path.stat().st_size > 0

    verification = loads(inspection.verification_path.read_text(encoding="utf-8"))
    smoke = loads(inspection.recoverability_smoke_path.read_text(encoding="utf-8"))
    assert verification["passed"] is True
    assert smoke["passed"] is True
    assert (
        smoke["metrics"]["pre_driver_detection_rate"]
        > smoke["metrics"]["post_driver_detection_rate"]
    )
    assert (
        smoke["metrics"]["late_surviving_detection_rate"]
        > smoke["metrics"]["late_extirpated_detection_rate"]
    )
    assert smoke["metrics"]["late_detection_auc"] > 0.60
    assert all(isfinite(float(value)) for value in smoke["metrics"].values())

    report_text = inspection.report_path.read_text(encoding="utf-8")
    assert "Synth-Small Observation Inspection Report" in report_text
    assert "Analyst-facing predator-truth exclusion" in report_text
