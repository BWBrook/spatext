from __future__ import annotations

from collections import Counter
from csv import DictReader
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable

import pytest

from spatext.synth.medium import (
    SYNTH_MEDIUM_LANDSCAPE_OUTPUT_FILES,
    SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES,
    build_synth_medium_landscape,
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "landscape_design_only": True,
    "visual_review_required": True,
    "no_predator_spread": True,
    "no_prey_dynamics": True,
    "no_observation_model": True,
    "no_reconstruction_or_inference": True,
    "no_real_data": True,
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def assert_boundary_labels(payload: dict[str, object]) -> None:
    for key, value in BOUNDARY_LABELS.items():
        assert payload[key] is value


def test_synth_medium_landscape_writes_reconciled_review_bundle(tmp_path: Path) -> None:
    result = build_synth_medium_landscape()
    output_dir = tmp_path / "synth_medium_landscape"

    written = result.write_artifacts(output_dir)

    expected_root = set(SYNTH_MEDIUM_LANDSCAPE_OUTPUT_FILES) | {"visuals"}
    assert {path.name for path in output_dir.iterdir()} == expected_root
    assert {path.name for path in written} == set(SYNTH_MEDIUM_LANDSCAPE_OUTPUT_FILES) | set(
        SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES
    )

    config = loads((output_dir / "landscape_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    cells = read_csv_rows(output_dir / "cells.csv")
    adjacency = read_csv_rows(output_dir / "adjacency.csv")
    patch_rows = read_csv_rows(output_dir / "patch_summary.csv")
    corridor_rows = read_csv_rows(output_dir / "corridor_summary.csv")
    water_rows = read_csv_rows(output_dir / "water_component_summary.csv")
    source_rows = read_csv_rows(output_dir / "source_zone_summary.csv")
    connectivity_rows = read_csv_rows(output_dir / "connectivity_summary.csv")
    quality_rows = read_csv_rows(output_dir / "quality_summary.csv")
    report = (output_dir / "report.md").read_text("utf-8")

    assert config["rows"] > 25
    assert config["cols"] > 25
    assert len(cells) == config["rows"] * config["cols"]
    assert_boundary_labels(config)
    assert_boundary_labels(verification)
    assert verification["passed"] is True

    class_counts = Counter(row["habitat_class"] for row in cells)
    assert {
        "water",
        "low_quality_matrix",
        "medium_quality",
        "high_quality_patch",
        "corridor",
        "source_zone",
    } <= set(class_counts)
    assert class_counts["water"] > 0
    assert class_counts["high_quality_patch"] > 0
    assert class_counts["corridor"] > 0

    water_cell_ids = {row["cell_id"] for row in cells if row["passability"] == "water"}
    assert water_cell_ids
    for edge in adjacency:
        assert edge["source_cell_id"] not in water_cell_ids
        assert edge["target_cell_id"] not in water_cell_ids

    source_zone_ids = {row["source_zone_id"] for row in source_rows}
    assert len(source_zone_ids) >= 3
    assert {row["frontier"] for row in source_rows} == {"west"}
    assert all(int(row["min_col"]) == 0 for row in source_rows)

    passable_cells = [row for row in cells if row["passability"] == "passable"]
    reachable_cells = [row for row in passable_cells if row["source_reachable"] == "true"]
    assert len(reachable_cells) / len(passable_cells) >= 0.85
    assert max(float(row["source_distance"]) for row in reachable_cells) > 50.0

    assert sum(int(row["cell_count"]) for row in patch_rows) == class_counts["high_quality_patch"]
    assert sum(int(row["cell_count"]) for row in corridor_rows) == class_counts["corridor"]
    assert sum(int(row["cell_count"]) for row in water_rows) == class_counts["water"]
    assert sum(int(row["cell_count"]) for row in source_rows) == class_counts["source_zone"]

    quality_counts = {row["habitat_class"]: int(row["cell_count"]) for row in quality_rows}
    assert quality_counts["all_cells"] == len(cells)
    assert quality_counts["all_passable"] == len(passable_cells)
    for habitat_class, count in class_counts.items():
        assert quality_counts[habitat_class] == count

    landscape_connectivity = next(
        row for row in connectivity_rows if row["summary_scope"] == "landscape"
    )
    assert int(landscape_connectivity["passable_cell_count"]) == len(passable_cells)
    assert int(landscape_connectivity["source_reachable_cell_count"]) == len(reachable_cells)
    assert int(landscape_connectivity["unreachable_passable_cell_count"]) == (
        len(passable_cells) - len(reachable_cells)
    )

    for visual_name in SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES:
        visual_path = output_dir / "visuals" / visual_name
        assert visual_path.exists()
        assert visual_path.stat().st_size > 1000
        assert visual_path.read_text("utf-8").lstrip().startswith("<svg")
        assert f"visuals/{visual_name}" in report


def test_synth_medium_landscape_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    build_synth_medium_landscape().write_artifacts(first_dir)
    build_synth_medium_landscape().write_artifacts(second_dir)

    relative_files = tuple(SYNTH_MEDIUM_LANDSCAPE_OUTPUT_FILES) + tuple(
        f"visuals/{name}" for name in SYNTH_MEDIUM_LANDSCAPE_VISUAL_FILES
    )
    for relative_file in relative_files:
        assert (first_dir / relative_file).read_text("utf-8") == (
            second_dir / relative_file
        ).read_text("utf-8")


def test_synth_medium_landscape_verification_exposes_review_contract(tmp_path: Path) -> None:
    output_dir = tmp_path / "synth_medium_landscape"
    build_synth_medium_landscape().write_artifacts(output_dir)

    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    checks = {check["name"]: check for check in verification["checks"]}

    assert checks["dimensions_larger_than_synth_small"]["passed"] is True
    assert checks["required_habitat_classes"]["passed"] is True
    assert checks["water_excluded_from_passable_adjacency"]["passed"] is True
    assert checks["multiple_western_source_zones"]["passed"] is True
    assert checks["source_reachability"]["passed"] is True
    assert checks["summary_reconciliation"]["passed"] is True
    assert checks["visual_review_contract"]["passed"] is True


def test_synth_medium_landscape_cli(tmp_path: Path) -> None:
    output_dir = tmp_path / "synth_medium_landscape"
    completed = run(
        [
            executable,
            "scripts/build_synth_medium_landscape.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Synth-medium landscape review pack complete" in completed.stdout
    assert "Dimensions: 72 x 84" in completed.stdout
    assert "Wrote 17 files" in completed.stdout
    assert "Verification: passed" in completed.stdout
    assert (output_dir / "visuals" / "review_montage.svg").exists()


def test_synth_medium_landscape_rejects_too_small_config() -> None:
    from spatext.synth.medium import SynthMediumLandscapeConfig

    with pytest.raises(ValueError, match="larger than synth-small"):
        build_synth_medium_landscape(SynthMediumLandscapeConfig(rows=25, cols=25))
