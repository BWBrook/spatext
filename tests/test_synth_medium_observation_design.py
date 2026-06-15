from __future__ import annotations

from csv import DictReader
from itertools import pairwise
from json import loads
from pathlib import Path
from re import finditer, search
from subprocess import run
from sys import executable
from typing import NamedTuple

from spatext.synth.medium import (
    SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_FILES,
    SYNTH_MEDIUM_OBSERVATION_DESIGN_VISUAL_FILES,
    build_synth_medium_observation_design_review_pack,
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "synth_medium_spread_impact_source_verified": True,
    "observation_design_review_only": True,
    "response_only_observations": True,
    "full_observability_is_benchmark_only": True,
    "selected_default_is_imperfect_observation": True,
    "visual_review_required": True,
    "no_reconstruction_or_inference": True,
    "no_abc_pom_likelihood_or_posterior": True,
    "no_real_data": True,
}

FORBIDDEN_ANALYST_COLUMNS = {
    "predator_arrival_time",
    "predator_source_zone_id",
    "predator_final_occupied",
    "prey_extirpation_time",
    "prey_impact_time",
    "prey_baseline_abundance",
    "prey_final_abundance",
}


class PanelLayout(NamedTuple):
    panel_id: str
    column: int
    row: int
    title_y: float
    map_top: float
    map_bottom: float
    legend_top: float
    legend_bottom: float
    panel_bottom: float


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def assert_boundary_labels(payload: dict[str, object]) -> None:
    for key, value in BOUNDARY_LABELS.items():
        assert payload[key] is value


def assert_svg_content_fits_width(svg: str, *, min_width: int, margin: float) -> None:
    svg_match = search(
        r'<svg[^>]*width="(?P<width>\d+)"[^>]*'
        r'viewBox="0 0 (?P<view_width>\d+) (?P<view_height>\d+)"',
        svg,
    )
    assert svg_match is not None
    width = float(svg_match.group("width"))
    assert width == float(svg_match.group("view_width"))
    assert width >= min_width

    right_edges: list[float] = []
    for rect_match in finditer(r'<rect[^>]*x="([0-9.]+)"[^>]*width="([0-9.]+)"', svg):
        right_edges.append(float(rect_match.group(1)) + float(rect_match.group(2)))
    for text_match in finditer(
        r'<text[^>]*x="([0-9.]+)"[^>]*font-size="([0-9.]+)"[^>]*>([^<]*)</text>',
        svg,
    ):
        x = float(text_match.group(1))
        font_size = float(text_match.group(2))
        text = text_match.group(3)
        right_edges.append(x + len(text) * font_size * 0.65)
    assert max(right_edges) <= width - margin


def assert_review_montage_panels_do_not_overlap(svg: str) -> None:
    svg_match = search(
        r'<svg[^>]*height="(?P<height>\d+)"[^>]*viewBox="0 0 (?P<width>\d+) '
        r'(?P<view_height>\d+)"',
        svg,
    )
    assert svg_match is not None
    height = float(svg_match.group("height"))
    assert height == float(svg_match.group("view_height"))

    panel_matches = tuple(
        finditer(
            r'<g id="panel-(?P<id>[^"]+)" data-column="(?P<column>\d+)" '
            r'data-row="(?P<row>\d+)" data-title-y="(?P<title_y>[0-9.]+)" '
            r'data-map-top="(?P<map_top>[0-9.]+)" '
            r'data-map-bottom="(?P<map_bottom>[0-9.]+)" '
            r'data-legend-top="(?P<legend_top>[0-9.]+)" '
            r'data-legend-bottom="(?P<legend_bottom>[0-9.]+)" '
            r'data-panel-bottom="(?P<panel_bottom>[0-9.]+)">',
            svg,
        )
    )
    assert len(panel_matches) == 4
    panels = [
        PanelLayout(
            panel_id=match.group("id"),
            column=int(match.group("column")),
            row=int(match.group("row")),
            title_y=float(match.group("title_y")),
            map_top=float(match.group("map_top")),
            map_bottom=float(match.group("map_bottom")),
            legend_top=float(match.group("legend_top")),
            legend_bottom=float(match.group("legend_bottom")),
            panel_bottom=float(match.group("panel_bottom")),
        )
        for match in panel_matches
    ]
    for panel in panels:
        assert panel.title_y + 16 <= panel.map_top
        assert panel.map_bottom + 24 <= panel.legend_top
        assert panel.legend_bottom <= panel.panel_bottom
        assert panel.panel_bottom <= height - 20

    for column in {panel.column for panel in panels}:
        column_panels = sorted(
            (panel for panel in panels if panel.column == column),
            key=lambda panel: panel.row,
        )
        for previous, current in pairwise(column_panels):
            assert previous.legend_bottom + 40 <= current.title_y


def test_observation_design_writes_reconciled_review_bundle(tmp_path: Path) -> None:
    result = build_synth_medium_observation_design_review_pack()
    output_dir = tmp_path / "observation_design"

    written = result.write_artifacts(output_dir)

    expected_root = set(SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_FILES) | {"visuals"}
    assert {path.name for path in output_dir.iterdir()} == expected_root
    assert {path.name for path in written} == set(
        SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_FILES
    ) | set(SYNTH_MEDIUM_OBSERVATION_DESIGN_VISUAL_FILES)

    config = loads((output_dir / "observation_design_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    regime_rows = read_csv_rows(output_dir / "regime_summary.csv")
    schedule_rows = read_csv_rows(output_dir / "survey_schedule.csv")
    observation_rows = read_csv_rows(output_dir / "observation_records.csv")
    cell_rows = read_csv_rows(output_dir / "cell_observation_summary.csv")
    bridge_rows = read_csv_rows(output_dir / "truth_observation_bridge.csv")
    false_negative_rows = read_csv_rows(output_dir / "false_negative_summary.csv")
    coverage_rows = read_csv_rows(output_dir / "coverage_gap_summary.csv")
    effort_rows = read_csv_rows(output_dir / "effort_by_habitat_region_summary.csv")
    signal_rows = read_csv_rows(output_dir / "recoverability_signal_summary.csv")
    report = (output_dir / "report.md").read_text("utf-8")

    assert_boundary_labels(config)
    assert_boundary_labels(verification)
    assert verification["passed"] is True
    assert verification["recommendation_class"] == "ready_for_human_observation_design_review"
    assert config["selected_default_regime_id"] == "structured_response_observed_default"
    assert (
        config["truth_source_summary"]["selected_parameter_set_id"] == "balanced_corridor_detour_v2"
    )
    assert config["truth_source_summary"]["cell_count"] == 6048
    assert config["truth_source_summary"]["passable_cell_count"] == 5225
    assert config["truth_source_summary"]["water_cell_count"] == 823
    assert config["truth_source_summary"]["final_colonized_passable_count"] == 4605
    assert config["truth_source_summary"]["finite_prey_extirpation_count"] == 4289

    assert {row["regime_id"] for row in regime_rows} == {
        "truth_reference_full_observability",
        "structured_response_observed_default",
        "sparse_response_observed_stress",
    }
    regime_map = {row["regime_id"]: row for row in regime_rows}
    assert regime_map["truth_reference_full_observability"]["regime_role"] == "benchmark"
    assert regime_map["structured_response_observed_default"]["selected_default"] == "true"
    assert regime_map["sparse_response_observed_stress"]["regime_role"] == "stress"

    assert len(cell_rows) == 5225 * 3
    assert len(bridge_rows) == len(cell_rows)
    assert len(schedule_rows) == len(observation_rows)
    assert all(row["passability"] == "passable" for row in schedule_rows)
    assert all(row["passability"] == "passable" for row in observation_rows)
    assert set(observation_rows[0]).isdisjoint(FORBIDDEN_ANALYST_COLUMNS)

    full = regime_map["truth_reference_full_observability"]
    default = regime_map["structured_response_observed_default"]
    sparse = regime_map["sparse_response_observed_stress"]
    assert float(full["surveyed_passable_fraction"]) == 1.0
    assert int(full["false_negative_count"]) == 0
    assert full["is_benchmark_only"] == "true"

    default_coverage = float(default["surveyed_passable_fraction"])
    assert 0.70 <= default_coverage < 1.0
    assert 0 < int(default["false_negative_count"]) < 4289
    assert 0.40 <= float(default["post_impact_support_fraction"]) < 1.0
    assert float(default["detected_response_time_range"]) >= 60.0
    assert 0.0 < float(default["detection_rate"]) < 1.0
    assert default["regime_recommendation"] == "ready_for_review"

    assert int(sparse["observation_record_count"]) < int(default["observation_record_count"])
    assert float(sparse["post_impact_support_fraction"]) < float(
        default["post_impact_support_fraction"]
    )
    assert int(sparse["false_negative_count"]) > int(default["false_negative_count"])

    default_false_negative = next(
        row
        for row in false_negative_rows
        if row["regime_id"] == "structured_response_observed_default"
        and row["summary_group"] == "all_passable"
    )
    assert int(default_false_negative["false_negative_count"]) == int(
        default["false_negative_count"]
    )

    default_gap = next(
        row
        for row in coverage_rows
        if row["regime_id"] == "structured_response_observed_default"
        and row["summary_group"] == "all_passable"
    )
    assert int(default_gap["no_post_impact_support_count"]) > 0
    assert int(default_gap["surveyed_cell_count"]) == int(default["surveyed_passable_count"])

    default_effort_groups = [
        row for row in effort_rows if row["regime_id"] == "structured_response_observed_default"
    ]
    assert {row["habitat_class"] for row in default_effort_groups} >= {
        "low_quality_matrix",
        "medium_quality",
        "high_quality_patch",
        "corridor",
        "source_zone",
    }
    assert len({row["col_band"] for row in default_effort_groups}) >= 3

    signal_map = {(row["regime_id"], row["proxy_id"]): row for row in signal_rows}
    assert (
        signal_map[("structured_response_observed_default", "default_post_impact_support")][
            "passes"
        ]
        == "true"
    )
    assert (
        signal_map[("structured_response_observed_default", "default_timing_signal")]["passes"]
        == "true"
    )
    assert (
        signal_map[("structured_response_observed_default", "default_spatial_signal")]["passes"]
        == "true"
    )
    assert (
        signal_map[("sparse_response_observed_stress", "stress_lower_information")]["passes"]
        == "true"
    )

    for visual_name in SYNTH_MEDIUM_OBSERVATION_DESIGN_VISUAL_FILES:
        visual_path = output_dir / "visuals" / visual_name
        assert visual_path.exists()
        assert visual_path.stat().st_size > 1000
        assert visual_path.read_text("utf-8").lstrip().startswith("<svg")
        assert f"visuals/{visual_name}" in report


def test_observation_design_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    build_synth_medium_observation_design_review_pack().write_artifacts(first_dir)
    build_synth_medium_observation_design_review_pack().write_artifacts(second_dir)

    relative_files = tuple(SYNTH_MEDIUM_OBSERVATION_DESIGN_OUTPUT_FILES) + tuple(
        f"visuals/{name}" for name in SYNTH_MEDIUM_OBSERVATION_DESIGN_VISUAL_FILES
    )
    for relative_file in relative_files:
        assert (first_dir / relative_file).read_text("utf-8") == (
            second_dir / relative_file
        ).read_text("utf-8")


def test_observation_design_verification_exposes_review_gates(tmp_path: Path) -> None:
    output_dir = tmp_path / "observation_design"
    build_synth_medium_observation_design_review_pack().write_artifacts(output_dir)

    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    checks = {check["name"]: check for check in verification["checks"]}

    expected_checks = {
        "artifact_contract",
        "truth_source_reconciliation",
        "water_has_no_surveys",
        "full_observability_benchmark",
        "default_broad_uneven_coverage",
        "default_imperfect_detection_false_negatives",
        "default_post_impact_support",
        "default_timing_signal",
        "default_spatial_signal",
        "sparse_stress_lower_information",
        "record_summary_reconciliation",
    }
    assert expected_checks <= set(checks)
    assert all(checks[name]["passed"] is True for name in expected_checks)


def test_observation_design_visuals_are_self_decoding(tmp_path: Path) -> None:
    output_dir = tmp_path / "observation_design"
    build_synth_medium_observation_design_review_pack().write_artifacts(output_dir)

    comparison = (output_dir / "visuals" / "regime_comparison_montage.svg").read_text("utf-8")
    assert_svg_content_fits_width(comparison, min_width=1400, margin=40.0)
    assert "Regime comparison table" in comparison
    assert "Coverage" in comparison
    assert "Post-impact support" in comparison
    assert "False negatives" in comparison
    assert "Detection rate" in comparison
    assert "truth_reference_full_observability" in comparison
    assert "structured_response_observed_default" in comparison
    assert "sparse_response_observed_stress" in comparison
    assert "surveyed_passable_fraction" not in comparison
    assert "post_impact_support_fraction" not in comparison

    expected_legend_labels = {
        "survey_effort_surface_default.svg": {
            "Water / not passable",
            "No survey",
            "Low effort",
            "High effort",
        },
        "observed_final_response_default.svg": {
            "Water / not passable",
            "Late detection",
            "Post-impact non-detection",
            "No late support",
            "Never surveyed",
        },
        "truth_observed_mismatch_default.svg": {
            "Water / not passable",
            "Observed true extirpation",
            "False negative",
            "Not extirpated / uninformative",
        },
        "post_impact_support_default.svg": {
            "Water / not passable",
            "No post-impact support",
            "Some support",
            "Strong support",
        },
    }
    for visual_name, labels in expected_legend_labels.items():
        svg = (output_dir / "visuals" / visual_name).read_text("utf-8")
        assert "Legend" in svg
        assert 'id="legend-' in svg
        for label in labels:
            assert label in svg

    review_montage = (output_dir / "visuals" / "review_montage.svg").read_text("utf-8")
    assert_review_montage_panels_do_not_overlap(review_montage)
    for panel_id in (
        "legend-survey-effort",
        "legend-final-status",
        "legend-mismatch",
        "legend-post-impact",
    ):
        assert panel_id in review_montage
    for label in {
        "Water / not passable",
        "No survey",
        "Late detection",
        "False negative",
        "No post-impact support",
    }:
        assert label in review_montage

    report = (output_dir / "report.md").read_text("utf-8")
    assert "## Visual Decode Keys" in report
    assert "regime comparison table" in report
    assert "Water / not passable" in report


def test_observation_design_cli(tmp_path: Path) -> None:
    output_dir = tmp_path / "observation_design"
    completed = run(
        [
            executable,
            "scripts/build_synth_medium_observation_design.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Synth-medium observation-design review pack complete" in completed.stdout
    assert "Selected default regime: structured_response_observed_default" in completed.stdout
    assert "Recommendation: ready_for_human_observation_design_review" in completed.stdout
    assert "Wrote 18 files" in completed.stdout
    assert (output_dir / "visuals" / "review_montage.svg").exists()
