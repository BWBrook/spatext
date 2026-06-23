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
    SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_FILES,
    SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES,
    build_synth_medium_observation_design_counterfactual_screen,
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "synth_medium_landscape_source_verified": True,
    "synth_medium_spread_impact_source_verified": True,
    "synth_medium_observation_design_source_verified": True,
    "synth_medium_response_reconstruction_source_verified": True,
    "observation_design_counterfactual_screen_only": True,
    "response_only_observation_counterfactuals": True,
    "response_only_reconstruction_benchmark_reused": True,
    "published_baseline_preserved": True,
    "ceiling_regime_is_diagnostic_only": True,
    "visual_review_required": True,
    "no_production_observation_design_adoption": True,
    "no_production_reconstruction_rule_adoption": True,
    "no_abc_pom_likelihood_or_posterior": True,
    "no_real_data": True,
}

BASELINE_REGIME_ID = "structured_response_observed_default"
BASELINE_RULE_ID = "final_absence_run_1"


class PanelLayout(NamedTuple):
    panel_id: str
    title_y: float
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
    assert right_edges
    assert max(right_edges) <= width - margin


def assert_decision_table_text_stays_within_columns(svg: str) -> None:
    column_left_edges = {
        "rule": 460.0,
        "recall": 660.0,
        "false_negatives": 820.0,
        "large_errors": 1010.0,
        "loss": 1180.0,
        "class": 1320.0,
    }
    column_margin = 20.0
    text_rows = tuple(
        finditer(
            r'<text[^>]*x="(?P<x>[0-9.]+)"[^>]*y="(?P<y>[0-9.]+)"'
            r'[^>]*font-size="(?P<font_size>[0-9.]+)"[^>]*>(?P<text>[^<]*)</text>',
            svg,
        )
    )
    assert text_rows
    for match in text_rows:
        x = float(match.group("x"))
        y = float(match.group("y"))
        if y < 112:
            continue
        text = match.group("text")
        font_size = float(match.group("font_size"))
        right_edge = x + len(text) * font_size * 0.65
        if x == column_left_edges["rule"]:
            assert right_edge <= column_left_edges["recall"] - column_margin
        if x == column_left_edges["recall"]:
            assert right_edge <= column_left_edges["false_negatives"] - column_margin
        if x == column_left_edges["false_negatives"]:
            assert right_edge <= column_left_edges["large_errors"] - column_margin
        if x == column_left_edges["large_errors"]:
            assert right_edge <= column_left_edges["loss"] - column_margin
        if x == column_left_edges["loss"]:
            assert right_edge <= column_left_edges["class"] - column_margin


def assert_visual_panels_do_not_overlap(svg: str, *, min_panels: int = 3) -> None:
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
            r'data-panel-bottom="(?P<panel_bottom>[0-9.]+)">',
            svg,
        )
    )
    assert len(panel_matches) >= min_panels
    panels = [
        PanelLayout(
            panel_id=match.group("id"),
            title_y=float(match.group("title_y")),
            panel_bottom=float(match.group("panel_bottom")),
        )
        for match in panel_matches
    ]
    for panel in panels:
        assert panel.panel_bottom <= height - 20
    for previous, current in pairwise(sorted(panels, key=lambda panel: panel.title_y)):
        assert previous.panel_bottom + 30 <= current.title_y


def test_counterfactual_screen_writes_reconciled_review_bundle(tmp_path: Path) -> None:
    result = build_synth_medium_observation_design_counterfactual_screen()
    output_dir = tmp_path / "counterfactual_screen"

    written = result.write_artifacts(output_dir)

    expected_root = set(SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_FILES) | {"visuals"}
    assert {path.name for path in output_dir.iterdir()} == expected_root
    assert {path.name for path in written} == set(
        SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_FILES
    ) | set(SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES)

    config = loads((output_dir / "counterfactual_screen_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    regime_rows = read_csv_rows(output_dir / "counterfactual_regime_definitions.csv")
    observation_rows = read_csv_rows(output_dir / "counterfactual_observation_summary.csv")
    ranking_rows = read_csv_rows(output_dir / "counterfactual_reconstruction_rankings.csv")
    support_rows = read_csv_rows(output_dir / "counterfactual_support_gap_summary.csv")
    error_rows = read_csv_rows(output_dir / "counterfactual_error_summary.csv")
    delta_rows = read_csv_rows(output_dir / "baseline_to_counterfactual_delta.csv")
    decision_rows = read_csv_rows(output_dir / "recoverability_decision_summary.csv")
    report = (output_dir / "report.md").read_text("utf-8")

    assert_boundary_labels(config)
    assert_boundary_labels(verification)
    assert verification["passed"] is True
    assert config["source_reconciliation"]["landscape"]["cell_count"] == 6048
    assert config["source_reconciliation"]["landscape"]["passable_cell_count"] == 5225
    assert (
        config["source_reconciliation"]["spread_impact"]["selected_parameter_set_id"]
        == "balanced_corridor_detour_v2"
    )
    assert (
        config["source_reconciliation"]["observation_design"]["selected_default_regime_id"]
        == BASELINE_REGIME_ID
    )
    assert (
        config["source_reconciliation"]["response_reconstruction"]["primary_default_rule_id"]
        == BASELINE_RULE_ID
    )

    regime_map = {row["regime_id"]: row for row in regime_rows}
    assert set(regime_map) == {
        BASELINE_REGIME_ID,
        "post_impact_followup_boost",
        "final_absence_confirmation_support",
        "weak_area_targeted_support",
        "balanced_habitat_region_support",
        "near_perfect_response_observation_ceiling",
    }
    assert regime_map[BASELINE_REGIME_ID]["regime_role"] == "published_baseline"
    assert regime_map["near_perfect_response_observation_ceiling"]["plausibility_class"] == (
        "unrealistic_diagnostic_ceiling"
    )
    plausible_regimes = [
        row for row in regime_rows if row["plausibility_class"] == "plausible_field_like"
    ]
    assert len(plausible_regimes) == 4
    assert {
        "post_impact_followup",
        "final_absence_confirmation",
        "weak_area_coverage",
        "balanced_spatial_stratification",
    } <= {row["counterfactual_class"] for row in plausible_regimes}

    assert len(observation_rows) == len(regime_rows)
    assert all(int(row["record_count"]) >= 0 for row in observation_rows)
    assert all("record_count_delta_from_baseline" in row for row in observation_rows)
    assert all("final_absence_support_count" in row for row in observation_rows)
    assert all("detection_history_support_count" in row for row in observation_rows)

    best_rows = [row for row in ranking_rows if row["rank"] == "1"]
    assert len(best_rows) == len(regime_rows)
    ranking_map = {(row["regime_id"], row["rule_id"]): row for row in ranking_rows}
    baseline_best = ranking_map[(BASELINE_REGIME_ID, BASELINE_RULE_ID)]
    assert baseline_best["rank"] == "1"
    assert float(baseline_best["finite_recall"]) == 0.524364653765
    assert int(baseline_best["false_negative_count"]) == 2040
    assert int(baseline_best["false_positive_count"]) == 304
    assert int(baseline_best["large_error_count"]) == 809
    assert baseline_best["recommendation_class"] == (
        "observation_design_not_recoverable_enough_for_backfitting"
    )

    ceiling_best = next(
        row for row in best_rows if row["regime_id"] == "near_perfect_response_observation_ceiling"
    )
    assert ceiling_best["plausibility_class"] == "unrealistic_diagnostic_ceiling"
    assert int(ceiling_best["false_negative_count"]) == 0
    assert float(ceiling_best["finite_recall"]) > float(baseline_best["finite_recall"])

    decision_map = {row["decision_id"]: row for row in decision_rows}
    best_plausible = next(
        row
        for row in best_rows
        if row["regime_id"] == decision_map["final_decision"]["best_plausible_regime_id"]
    )
    assert float(best_plausible["finite_recall"]) > float(baseline_best["finite_recall"])
    assert int(best_plausible["false_negative_count"]) < int(baseline_best["false_negative_count"])
    assert best_plausible["regime_recommendation_class"] != (
        "response_reconstruction_ready_for_human_review"
    )

    assert any(
        row["regime_id"] == best_plausible["regime_id"]
        and row["rule_id"] == best_plausible["rule_id"]
        and row["summary_group"] == "all_passable"
        for row in support_rows
    )
    assert any(
        row["regime_id"] == best_plausible["regime_id"]
        and row["rule_id"] == best_plausible["rule_id"]
        and row["summary_group"] == "habitat:low_quality_matrix"
        for row in error_rows
    )
    assert any(row["regime_id"] == best_plausible["regime_id"] for row in delta_rows)

    assert decision_map["final_decision"]["recommendation_class"] in {
        "plausible_observation_design_can_support_reconstruction_review",
        "only_unrealistic_observation_ceiling_recovers_signal",
        "observation_design_counterfactuals_still_not_recoverable",
        "needs_process_observation_model_before_fitting",
    }
    assert decision_map["final_decision"]["baseline_rule_id"] == BASELINE_RULE_ID
    assert decision_map["final_decision"]["best_plausible_regime_id"] == best_plausible["regime_id"]
    assert decision_map["final_decision"]["ceiling_regime_id"] == (
        "near_perfect_response_observation_ceiling"
    )
    if (
        decision_map["final_decision"]["recommendation_class"]
        == "only_unrealistic_observation_ceiling_recovers_signal"
    ):
        assert (
            decision_map["final_decision"]["best_plausible_ready_for_reconstruction_review"]
            == "false"
        )
        assert decision_map["final_decision"]["ceiling_ready_for_reconstruction_review"] == "true"

    assert "observation-design recoverability counterfactual screen" in report
    assert decision_map["final_decision"]["recommendation_class"] in report
    for visual_name in SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES:
        visual_path = output_dir / "visuals" / visual_name
        assert visual_path.exists()
        assert visual_path.stat().st_size > 1000
        assert visual_path.read_text("utf-8").lstrip().startswith("<svg")
        assert f"visuals/{visual_name}" in report


def test_counterfactual_screen_verification_exposes_review_gates(tmp_path: Path) -> None:
    output_dir = tmp_path / "counterfactual_screen"
    build_synth_medium_observation_design_counterfactual_screen().write_artifacts(output_dir)

    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    checks = {check["name"]: check for check in verification["checks"]}

    expected_checks = {
        "artifact_contract",
        "source_reconciliation",
        "published_baseline_reconciled",
        "counterfactual_regime_contract",
        "plausible_counterfactuals_improve_baseline",
        "ceiling_is_separated_from_plausible_claims",
        "table_reconciliation",
        "visual_contract",
    }
    assert expected_checks <= set(checks)
    assert all(checks[name]["passed"] is True for name in expected_checks)
    assert checks["published_baseline_reconciled"]["details"]["false_negative_count"] == 2040
    assert (
        checks["table_reconciliation"]["details"]["ranking_row_count"]
        == checks["table_reconciliation"]["details"]["expected_ranking_row_count"]
    )


def test_counterfactual_visuals_are_self_decoding(tmp_path: Path) -> None:
    output_dir = tmp_path / "counterfactual_screen"
    build_synth_medium_observation_design_counterfactual_screen().write_artifacts(output_dir)

    comparison = (output_dir / "visuals" / "recoverability_decision_montage.svg").read_text("utf-8")
    assert_svg_content_fits_width(comparison, min_width=1400, margin=40.0)
    assert_decision_table_text_stays_within_columns(comparison)
    for label in {
        "Regime",
        "Recall",
        "False negatives",
        "Large errors",
        "Loss",
        "plausible",
        "ceiling",
    }:
        assert label in comparison

    review = (output_dir / "visuals" / "support_gap_comparison_montage.svg").read_text("utf-8")
    assert_visual_panels_do_not_overlap(review, min_panels=3)
    for label in {
        "Legend",
        "Baseline support gaps",
        "Best plausible support gaps",
        "Never surveyed",
        "No detection history",
        "Finite reconstruction support",
    }:
        assert label in review

    residuals = (output_dir / "visuals" / "residual_comparison_baseline_best.svg").read_text(
        "utf-8"
    )
    assert_visual_panels_do_not_overlap(residuals, min_panels=2)
    for label in {
        "Baseline residuals",
        "Best plausible residuals",
        "Early bias",
        "Late bias",
    }:
        assert label in residuals

    delta = (output_dir / "visuals" / "baseline_to_best_plausible_delta.svg").read_text("utf-8")
    assert "Baseline-to-best plausible delta" in delta
    assert "Improved from baseline" in delta

    ceiling = (output_dir / "visuals" / "ceiling_comparison_panel.svg").read_text("utf-8")
    assert "Diagnostic ceiling" in ceiling
    assert "Unrealistic benchmark" in ceiling


def test_counterfactual_screen_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    build_synth_medium_observation_design_counterfactual_screen().write_artifacts(first_dir)
    build_synth_medium_observation_design_counterfactual_screen().write_artifacts(second_dir)

    relative_files = tuple(SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_OUTPUT_FILES) + tuple(
        f"visuals/{name}" for name in SYNTH_MEDIUM_OBSERVATION_DESIGN_COUNTERFACTUAL_VISUAL_FILES
    )
    for relative_file in relative_files:
        assert (first_dir / relative_file).read_text("utf-8") == (
            second_dir / relative_file
        ).read_text("utf-8")


def test_counterfactual_screen_cli(tmp_path: Path) -> None:
    output_dir = tmp_path / "counterfactual_screen"
    completed = run(
        [
            executable,
            "scripts/screen_synth_medium_observation_design_counterfactuals.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Synth-medium observation-design counterfactual screen complete" in completed.stdout
    assert "Baseline regime: structured_response_observed_default" in completed.stdout
    assert "Baseline primary rule: final_absence_run_1" in completed.stdout
    assert "Decision recommendation:" in completed.stdout
    assert "Wrote 15 files" in completed.stdout
    assert (output_dir / "visuals" / "recoverability_decision_montage.svg").exists()
