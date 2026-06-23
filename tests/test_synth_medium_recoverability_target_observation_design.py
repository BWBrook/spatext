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
    SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_FILES,
    SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES,
    build_synth_medium_recoverability_target_observation_design,
)
from spatext.synth.medium.landscape import CsvRow
from spatext.synth.medium.recoverability_target_observation_design import (
    best_field_plausible_row,
)

BASELINE_REGIME_ID = "structured_response_observed_default"
BASELINE_RULE_ID = "final_absence_run_1"
CEILING_REGIME_ID = "near_perfect_response_observation_ceiling"

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "recoverability_target_observation_design_review_only": True,
    "synth_medium_landscape_source_verified": True,
    "synth_medium_spread_impact_source_verified": True,
    "synth_medium_observation_design_source_verified": True,
    "synth_medium_response_reconstruction_source_verified": True,
    "synth_medium_observation_design_counterfactual_source_verified": True,
    "response_only_observation_designs": True,
    "response_only_reconstruction_benchmark_reused": True,
    "published_baseline_preserved": True,
    "ceiling_regime_is_diagnostic_only": True,
    "visual_review_required": True,
    "no_production_observation_design_adoption": True,
    "no_production_reconstruction_rule_adoption": True,
    "no_abc_pom_likelihood_or_posterior": True,
    "no_real_data": True,
}


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


def assert_visual_panels_do_not_overlap(svg: str, *, min_panels: int = 3) -> None:
    svg_match = search(
        r'<svg[^>]*height="(?P<height>\d+)"[^>]*viewBox="0 0 (?P<width>\d+) '
        r'(?P<view_height>\d+)"',
        svg,
    )
    assert svg_match is not None
    height = float(svg_match.group("height"))
    assert height == float(svg_match.group("view_height"))
    panels = [
        PanelLayout(
            panel_id=match.group("id"),
            title_y=float(match.group("title_y")),
            panel_bottom=float(match.group("panel_bottom")),
        )
        for match in finditer(
            r'<g id="panel-(?P<id>[^"]+)" data-title-y="(?P<title_y>[0-9.]+)" '
            r'data-panel-bottom="(?P<panel_bottom>[0-9.]+)">',
            svg,
        )
    ]
    assert len(panels) >= min_panels
    for panel in panels:
        assert panel.panel_bottom <= height - 20
    for previous, current in pairwise(sorted(panels, key=lambda panel: panel.title_y)):
        assert previous.panel_bottom + 30 <= current.title_y


def test_recoverability_target_design_writes_review_bundle(tmp_path: Path) -> None:
    result = build_synth_medium_recoverability_target_observation_design()
    output_dir = tmp_path / "target_design"

    written = result.write_artifacts(output_dir)

    expected_root = set(SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_FILES) | {
        "visuals"
    }
    assert {path.name for path in output_dir.iterdir()} == expected_root
    assert {path.name for path in written} == set(
        SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_FILES
    ) | set(SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES)

    config = loads((output_dir / "recoverability_target_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    regime_rows = read_csv_rows(output_dir / "regime_definitions.csv")
    effort_rows = read_csv_rows(output_dir / "observation_effort_summary.csv")
    strata_rows = read_csv_rows(output_dir / "strata_effort_summary.csv")
    ranking_rows = read_csv_rows(output_dir / "reconstruction_benchmark_summary.csv")
    support_rows = read_csv_rows(output_dir / "support_gap_summary.csv")
    delta_rows = read_csv_rows(output_dir / "baseline_to_candidate_delta.csv")
    decision_rows = read_csv_rows(output_dir / "readiness_decision_summary.csv")
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
        "stratified_scheduled_panel",
        "weak_strata_targeted_panel",
        "post_detection_confirmation_panel",
        "final_absence_revisit_panel",
        "high_cadence_rotating_panel",
        "integrated_recoverability_target_panel",
        CEILING_REGIME_ID,
    }
    assert regime_map[BASELINE_REGIME_ID]["regime_role"] == "published_baseline"
    assert regime_map[CEILING_REGIME_ID]["plausibility_class"] == ("unrealistic_diagnostic_ceiling")
    plausible_rows = [
        row for row in regime_rows if row["plausibility_class"] == "plausible_field_like"
    ]
    assert len(plausible_rows) == 6
    assert all(row["uses_hidden_truth_for_design"] == "false" for row in plausible_rows)

    assert len(effort_rows) == len(regime_rows)
    assert all("survey_record_count" in row for row in effort_rows)
    assert all("record_count_delta_from_baseline" in row for row in effort_rows)
    assert all("post_detection_support_count" in row for row in effort_rows)
    assert any(
        row["regime_id"] == "weak_strata_targeted_panel"
        and row["summary_group"] == "habitat:low_quality_matrix"
        for row in strata_rows
    )
    assert any(
        row["regime_id"] == "integrated_recoverability_target_panel"
        and row["summary_group"] == "col_band:east_band"
        for row in strata_rows
    )

    best_rows = [row for row in ranking_rows if row["rank"] == "1"]
    assert len(best_rows) == len(regime_rows)
    ranking_map = {(row["regime_id"], row["rule_id"]): row for row in ranking_rows}
    baseline_best = ranking_map[(BASELINE_REGIME_ID, BASELINE_RULE_ID)]
    assert baseline_best["rank"] == "1"
    assert float(baseline_best["finite_recall"]) == 0.524364653765
    assert int(baseline_best["false_negative_count"]) == 2040
    assert int(baseline_best["false_positive_count"]) == 304
    assert int(baseline_best["large_error_count"]) == 809

    decision = decision_rows[0]
    effort_map = {row["regime_id"]: row for row in effort_rows}
    assert decision["recommendation_class"] in {
        "recoverability_review_ready",
        "plausible_design_improves_but_process_model_needed",
        "only_unrealistic_observation_ceiling_recovers_signal",
        "recoverability_target_design_blocked",
    }
    assert decision["baseline_regime_id"] == BASELINE_REGIME_ID
    assert decision["ceiling_regime_id"] == CEILING_REGIME_ID
    assert decision["best_field_plausible_regime_id"] == ("integrated_recoverability_target_panel")
    assert (
        decision["best_performing_ready_regime_id"] == (decision["best_field_plausible_regime_id"])
    )
    assert decision["lowest_effort_ready_regime_id"] == "weak_strata_targeted_panel"
    assert decision["lowest_effort_ready_regime_id"] != decision["best_performing_ready_regime_id"]
    assert float(decision["best_field_plausible_finite_recall"]) > float(
        baseline_best["finite_recall"]
    )
    assert int(decision["best_field_plausible_false_negative_count"]) < int(
        baseline_best["false_negative_count"]
    )
    assert int(decision["ceiling_false_negative_count"]) == 0
    for prefix, regime_id in {
        "baseline": BASELINE_REGIME_ID,
        "best_field_plausible": decision["best_field_plausible_regime_id"],
        "lowest_effort_ready": decision["lowest_effort_ready_regime_id"],
        "ceiling": CEILING_REGIME_ID,
    }.items():
        effort = effort_map[regime_id]
        survey_record_count = int(effort["survey_record_count"])
        baseline_records = int(effort_map[BASELINE_REGIME_ID]["survey_record_count"])
        ceiling_records = int(effort_map[CEILING_REGIME_ID]["survey_record_count"])
        assert int(decision[f"{prefix}_survey_record_count"]) == survey_record_count
        assert int(decision[f"{prefix}_survey_record_delta_vs_baseline"]) == (
            survey_record_count - baseline_records
        )
        assert float(decision[f"{prefix}_survey_record_ratio_vs_baseline"]) == (
            float(f"{survey_record_count / baseline_records:.12g}")
        )
        assert int(decision[f"{prefix}_survey_record_delta_vs_ceiling"]) == (
            survey_record_count - ceiling_records
        )
        assert float(decision[f"{prefix}_survey_record_ratio_vs_ceiling"]) == (
            float(f"{survey_record_count / ceiling_records:.12g}")
        )
        assert int(decision[f"{prefix}_surveyed_cell_count"]) == int(effort["surveyed_cell_count"])
        assert int(decision[f"{prefix}_final_absence_support_count"]) == int(
            effort["final_absence_support_count"]
        )
    assert int(decision["best_field_plausible_survey_record_count"]) > int(
        decision["ceiling_survey_record_count"]
    )

    assert any(
        row["regime_id"] == decision["best_field_plausible_regime_id"]
        and row["summary_group"] == "all_passable"
        for row in support_rows
    )
    assert any(row["regime_id"] == decision["best_field_plausible_regime_id"] for row in delta_rows)
    assert "recoverability-target observation-design review pack" in report
    assert decision["recommendation_class"] in report
    assert "exceeds the diagnostic ceiling record count" in report
    for visual_name in SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES:
        visual_path = output_dir / "visuals" / visual_name
        assert visual_path.exists()
        assert visual_path.stat().st_size > 1000
        assert visual_path.read_text("utf-8").lstrip().startswith("<svg")
        assert f"visuals/{visual_name}" in report


def test_recoverability_target_verification_exposes_review_gates(tmp_path: Path) -> None:
    output_dir = tmp_path / "target_design"
    build_synth_medium_recoverability_target_observation_design().write_artifacts(output_dir)

    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    checks = {check["name"]: check for check in verification["checks"]}
    expected_checks = {
        "artifact_contract",
        "source_reconciliation",
        "published_baseline_reconciled",
        "candidate_regime_contract",
        "field_plausible_candidates_compared",
        "ceiling_is_reference_only",
        "table_reconciliation",
        "visual_contract",
    }
    assert expected_checks <= set(checks)
    assert all(checks[name]["passed"] is True for name in expected_checks)
    assert checks["published_baseline_reconciled"]["details"]["false_negative_count"] == 2040
    assert (
        checks["field_plausible_candidates_compared"]["details"]["plausible_candidate_count"] == 6
    )


def test_recoverability_target_visuals_are_self_decoding(tmp_path: Path) -> None:
    output_dir = tmp_path / "target_design"
    build_synth_medium_recoverability_target_observation_design().write_artifacts(output_dir)

    decision = (output_dir / "visuals" / "recoverability_decision_montage.svg").read_text("utf-8")
    assert_svg_content_fits_width(decision, min_width=1500, margin=40.0)
    for label in {
        "Regime",
        "Role",
        "Rule",
        "Recall",
        "Records",
        "False negatives",
        "Large errors",
        "Loss",
        "baseline",
        "field-plausible",
        "ceiling",
    }:
        assert label in decision

    for visual_name in {
        "effort_support_surfaces.svg",
        "support_gap_maps.svg",
        "residual_maps.svg",
        "ceiling_reference_panel.svg",
    }:
        svg = (output_dir / "visuals" / visual_name).read_text("utf-8")
        assert_visual_panels_do_not_overlap(svg, min_panels=2)
        for label in {"Legend", "Water / not passable"}:
            assert label in svg


def test_recoverability_target_design_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    build_synth_medium_recoverability_target_observation_design().write_artifacts(first_dir)
    build_synth_medium_recoverability_target_observation_design().write_artifacts(second_dir)

    relative_files = tuple(SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_OUTPUT_FILES) + (
        tuple(
            f"visuals/{name}"
            for name in SYNTH_MEDIUM_RECOVERABILITY_TARGET_OBSERVATION_DESIGN_VISUAL_FILES
        )
    )
    for relative_file in relative_files:
        assert (first_dir / relative_file).read_text("utf-8") == (
            second_dir / relative_file
        ).read_text("utf-8")


def test_recoverability_target_cli(tmp_path: Path) -> None:
    output_dir = tmp_path / "target_design"
    completed = run(
        [
            executable,
            "scripts/build_synth_medium_recoverability_target_observation_design.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Synth-medium recoverability-target observation-design review pack complete" in (
        completed.stdout
    )
    assert "Baseline regime: structured_response_observed_default" in completed.stdout
    assert "Candidate regime count: 8" in completed.stdout
    assert "Best field-plausible regime: integrated_recoverability_target_panel" in (
        completed.stdout
    )
    assert "Decision recommendation:" in completed.stdout
    assert "Wrote 15 files" in completed.stdout
    assert (output_dir / "visuals" / "recoverability_decision_montage.svg").exists()


def test_best_field_plausible_selection_uses_criteria_not_regime_id() -> None:
    rows: tuple[CsvRow, ...] = (
        {
            "regime_id": "integrated_recoverability_target_panel",
            "rank": 1,
            "plausibility_class": "plausible_field_like",
            "regime_recommendation_class": "recoverability_review_ready",
            "loss": 0.90,
            "false_negative_count": 500,
            "large_error_count": 600,
            "finite_recall": 0.88,
            "false_positive_count": 240,
        },
        {
            "regime_id": "weak_strata_targeted_panel",
            "rank": 1,
            "plausibility_class": "plausible_field_like",
            "regime_recommendation_class": "recoverability_review_ready",
            "loss": 0.80,
            "false_negative_count": 520,
            "large_error_count": 620,
            "finite_recall": 0.87,
            "false_positive_count": 260,
        },
    )

    assert best_field_plausible_row(rows)["regime_id"] == "weak_strata_targeted_panel"
