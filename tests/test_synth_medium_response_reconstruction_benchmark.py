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
    SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_FILES,
    SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES,
    build_synth_medium_response_reconstruction_benchmark,
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "synth_medium_landscape_source_verified": True,
    "synth_medium_spread_impact_source_verified": True,
    "synth_medium_observation_design_source_verified": True,
    "response_reconstruction_benchmark_only": True,
    "response_only_reconstruction_rules": True,
    "full_observability_is_benchmark_only": True,
    "selected_default_is_imperfect_observation": True,
    "visual_review_required": True,
    "no_production_reconstruction_rule_adoption": True,
    "no_abc_pom_likelihood_or_posterior": True,
    "no_real_data": True,
}

FORBIDDEN_RECONSTRUCTION_COLUMNS = {
    "predator_arrival_time",
    "prey_impact_time",
    "prey_extirpation_time",
    "true_extirpated_by_end",
    "true_response_time",
    "absolute_error",
    "signed_error",
}


class PanelLayout(NamedTuple):
    panel_id: str
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


def assert_review_panels_do_not_overlap(svg: str) -> None:
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
            r'<g id="panel-(?P<id>[^"]+)" data-title-y="(?P<title_y>[0-9.]+)" '
            r'data-map-top="(?P<map_top>[0-9.]+)" '
            r'data-map-bottom="(?P<map_bottom>[0-9.]+)" '
            r'data-legend-top="(?P<legend_top>[0-9.]+)" '
            r'data-legend-bottom="(?P<legend_bottom>[0-9.]+)" '
            r'data-panel-bottom="(?P<panel_bottom>[0-9.]+)">',
            svg,
        )
    )
    assert len(panel_matches) >= 4
    panels = [
        PanelLayout(
            panel_id=match.group("id"),
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
        assert panel.title_y + 14 <= panel.map_top
        assert panel.map_bottom + 18 <= panel.legend_top
        assert panel.legend_bottom <= panel.panel_bottom
        assert panel.panel_bottom <= height - 20

    for previous, current in pairwise(sorted(panels, key=lambda panel: panel.title_y)):
        assert previous.legend_bottom + 30 <= current.title_y


def test_response_reconstruction_writes_reconciled_review_bundle(tmp_path: Path) -> None:
    result = build_synth_medium_response_reconstruction_benchmark()
    output_dir = tmp_path / "response_reconstruction"

    written = result.write_artifacts(output_dir)

    expected_root = set(SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_FILES) | {"visuals"}
    assert {path.name for path in output_dir.iterdir()} == expected_root
    assert {path.name for path in written} == set(
        SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_FILES
    ) | set(SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES)

    config = loads((output_dir / "response_reconstruction_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    rule_rows = read_csv_rows(output_dir / "reconstruction_rule_definitions.csv")
    reconstructed_rows = read_csv_rows(output_dir / "reconstructed_cell_times.csv")
    bridge_rows = read_csv_rows(output_dir / "truth_reconstruction_bridge.csv")
    error_rows = read_csv_rows(output_dir / "reconstruction_error_summary.csv")
    ranking_rows = read_csv_rows(output_dir / "rule_regime_rankings.csv")
    support_rows = read_csv_rows(output_dir / "support_gap_summary.csv")
    signal_rows = read_csv_rows(output_dir / "recoverability_signal_summary.csv")
    report = (output_dir / "report.md").read_text("utf-8")

    assert_boundary_labels(config)
    assert_boundary_labels(verification)
    assert verification["passed"] is True
    assert verification["recommendation_class"] in {
        "response_reconstruction_ready_for_human_review",
        "default_observation_design_recoverability_marginal",
        "observation_design_not_recoverable_enough_for_backfitting",
    }
    assert config["selected_default_regime_id"] == "structured_response_observed_default"
    assert config["source_reconciliation"]["landscape"]["cell_count"] == 6048
    assert config["source_reconciliation"]["landscape"]["passable_cell_count"] == 5225
    assert (
        config["source_reconciliation"]["spread_impact"]["selected_parameter_set_id"]
        == "balanced_corridor_detour_v2"
    )
    assert config["source_reconciliation"]["spread_impact"]["finite_prey_extirpation_count"] == 4289
    assert (
        config["source_reconciliation"]["observation_design"]["default_survey_record_count"]
        == 21258
    )
    assert (
        config["source_reconciliation"]["observation_design"]["default_false_negative_count"]
        == 2313
    )

    rule_ids = {row["rule_id"] for row in rule_rows}
    assert {
        "final_absence_run_2",
        "final_absence_run_1",
        "midpoint_after_last_detection",
    } <= rule_ids
    assert all(row["rule_scope"] == "benchmark_only" for row in rule_rows)
    assert all(row["uses_hidden_truth"] == "false" for row in rule_rows)

    regime_ids = {
        "truth_reference_full_observability",
        "structured_response_observed_default",
        "sparse_response_observed_stress",
    }
    assert {row["regime_id"] for row in ranking_rows} == regime_ids
    assert len(reconstructed_rows) == 5225 * len(regime_ids) * len(rule_rows)
    assert len(bridge_rows) == len(reconstructed_rows)
    assert set(reconstructed_rows[0]).isdisjoint(FORBIDDEN_RECONSTRUCTION_COLUMNS)

    ranking_map = {(row["regime_id"], row["rule_id"]): row for row in ranking_rows}
    benchmark_best = next(
        row
        for row in ranking_rows
        if row["regime_id"] == "truth_reference_full_observability" and row["rank"] == "1"
    )
    default_best = next(
        row
        for row in ranking_rows
        if row["regime_id"] == "structured_response_observed_default" and row["rank"] == "1"
    )
    sparse_best = next(
        row
        for row in ranking_rows
        if row["regime_id"] == "sparse_response_observed_stress" and row["rank"] == "1"
    )

    assert benchmark_best["positive_control_status"] == "passed"
    assert int(benchmark_best["true_positive_count"]) == 4289
    assert int(benchmark_best["false_negative_count"]) == 0
    assert float(benchmark_best["median_absolute_error"]) <= 12.0
    assert default_best["regime_id"] == "structured_response_observed_default"
    assert int(default_best["finite_reconstructed_count"]) > int(
        sparse_best["finite_reconstructed_count"]
    )
    assert float(default_best["finite_recall"]) > float(sparse_best["finite_recall"])
    assert float(default_best["loss"]) < float(sparse_best["loss"])
    assert int(default_best["large_error_count"]) > 0
    assert default_best["recommendation_class"] == verification["recommendation_class"]

    for regime_id in regime_ids:
        ranks = sorted(int(row["rank"]) for row in ranking_rows if row["regime_id"] == regime_id)
        assert ranks == list(range(1, len(rule_rows) + 1))

    default_support = next(
        row
        for row in support_rows
        if row["regime_id"] == "structured_response_observed_default"
        and row["rule_id"] == default_best["rule_id"]
        and row["summary_group"] == "all_passable"
    )
    assert int(default_support["passable_cell_count"]) == 5225
    assert int(default_support["surveyed_cell_count"]) == 4411
    assert int(default_support["never_surveyed_count"]) > 0
    assert int(default_support["post_detection_absence_supported_count"]) > 0

    error_groups = {(row["regime_id"], row["rule_id"], row["summary_group"]) for row in error_rows}
    assert (
        "structured_response_observed_default",
        default_best["rule_id"],
        "all_passable",
    ) in error_groups
    assert (
        "structured_response_observed_default",
        default_best["rule_id"],
        "habitat:low_quality_matrix",
    ) in error_groups
    assert (
        "structured_response_observed_default",
        default_best["rule_id"],
        "col_band:west_band",
    ) in error_groups

    signal_map = {(row["regime_id"], row["proxy_id"]): row for row in signal_rows}
    assert (
        signal_map[("truth_reference_full_observability", "benchmark_positive_control")]["passes"]
        == "true"
    )
    assert (
        signal_map[("structured_response_observed_default", "default_nontrivial_reconstruction")][
            "passes"
        ]
        == "true"
    )
    assert (
        signal_map[("sparse_response_observed_stress", "stress_lower_information_than_default")][
            "passes"
        ]
        == "true"
    )

    assert "response-only reconstruction benchmark" in report
    assert verification["recommendation_class"] in report
    assert default_best["rule_id"] in report
    for visual_name in SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES:
        visual_path = output_dir / "visuals" / visual_name
        assert visual_path.exists()
        assert visual_path.stat().st_size > 1000
        assert visual_path.read_text("utf-8").lstrip().startswith("<svg")
        assert f"visuals/{visual_name}" in report

    assert ranking_map[(benchmark_best["regime_id"], benchmark_best["rule_id"])] == benchmark_best


def test_response_reconstruction_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    build_synth_medium_response_reconstruction_benchmark().write_artifacts(first_dir)
    build_synth_medium_response_reconstruction_benchmark().write_artifacts(second_dir)

    relative_files = tuple(SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_OUTPUT_FILES) + tuple(
        f"visuals/{name}" for name in SYNTH_MEDIUM_RESPONSE_RECONSTRUCTION_VISUAL_FILES
    )
    for relative_file in relative_files:
        assert (first_dir / relative_file).read_text("utf-8") == (
            second_dir / relative_file
        ).read_text("utf-8")


def test_response_reconstruction_verification_exposes_review_gates(tmp_path: Path) -> None:
    output_dir = tmp_path / "response_reconstruction"
    build_synth_medium_response_reconstruction_benchmark().write_artifacts(output_dir)

    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    checks = {check["name"]: check for check in verification["checks"]}

    expected_checks = {
        "artifact_contract",
        "source_reconciliation",
        "response_only_reconstruction_schema",
        "full_observability_positive_control",
        "default_nontrivial_reconstruction",
        "default_error_distribution_audited",
        "sparse_stress_lower_information",
        "table_reconciliation",
        "visual_contract",
    }
    assert expected_checks <= set(checks)
    assert all(checks[name]["passed"] is True for name in expected_checks)
    assert (
        checks["table_reconciliation"]["details"]["bridge_row_count"]
        == checks["table_reconciliation"]["details"]["reconstructed_row_count"]
    )


def test_response_reconstruction_visuals_are_self_decoding(tmp_path: Path) -> None:
    output_dir = tmp_path / "response_reconstruction"
    build_synth_medium_response_reconstruction_benchmark().write_artifacts(output_dir)

    comparison = (output_dir / "visuals" / "regime_rule_comparison_montage.svg").read_text("utf-8")
    assert_svg_content_fits_width(comparison, min_width=1500, margin=40.0)
    assert "Regime/rule comparison table" in comparison
    assert "Recall" in comparison
    assert "Median error" in comparison
    assert "Large errors" in comparison
    assert "Loss" in comparison
    assert "truth_reference_full_observability" in comparison
    assert "structured_response_observed_default" in comparison
    assert "sparse_response_observed_stress" in comparison

    expected_legend_labels = {
        "truth_response_time.svg": {
            "Water / not passable",
            "No finite truth",
            "Early response",
            "Late response",
        },
        "default_primary_reconstructed_time.svg": {
            "Water / not passable",
            "No reconstruction",
            "Early reconstructed",
            "Late reconstructed",
        },
        "default_primary_residual_error.svg": {
            "Water / not passable",
            "No finite comparison",
            "Early bias",
            "Small error",
            "Late bias",
        },
        "default_primary_support_gap.svg": {
            "Water / not passable",
            "Never surveyed",
            "No detection history",
            "No final absence support",
            "Finite reconstruction support",
        },
    }
    for visual_name, labels in expected_legend_labels.items():
        svg = (output_dir / "visuals" / visual_name).read_text("utf-8")
        assert "Legend" in svg
        assert 'id="legend-' in svg
        for label in labels:
            assert label in svg

    review = (output_dir / "visuals" / "review_montage.svg").read_text("utf-8")
    assert_review_panels_do_not_overlap(review)
    for label in {
        "Truth response time",
        "Default reconstructed time",
        "Default residual error",
        "Default support gap",
        "Water / not passable",
        "Finite reconstruction support",
    }:
        assert label in review


def test_response_reconstruction_cli(tmp_path: Path) -> None:
    output_dir = tmp_path / "response_reconstruction"
    completed = run(
        [
            executable,
            "scripts/benchmark_synth_medium_response_reconstruction.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Synth-medium response reconstruction benchmark complete" in completed.stdout
    assert "Selected default regime: structured_response_observed_default" in completed.stdout
    assert "Recommendation:" in completed.stdout
    assert "Wrote 16 files" in completed.stdout
    assert (output_dir / "visuals" / "review_montage.svg").exists()
