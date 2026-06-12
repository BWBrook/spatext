from __future__ import annotations

from csv import DictReader
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable

import pytest

from spatext.synth.small import (
    build_response_only_screen,
    build_synth_small_compatibility_mismatch_audit,
    build_synth_small_compatibility_screen,
    build_synth_small_extirpation_reconstruction,
    build_synth_small_false_negative_mechanism_audit,
    build_synth_small_observation_support_counterfactual_screen,
    build_synth_small_observations,
    build_synth_small_summary_vector,
    evaluate_synth_small_response_screen,
)

COUNTERFACTUAL_FILES = {
    "counterfactual_config.json",
    "scenario_definitions.csv",
    "site_counterfactual_resolution.csv",
    "scenario_reconstruction_summary.csv",
    "scenario_summary_vectors.csv",
    "scenario_compatibility_scores.csv",
    "scenario_rankings.csv",
    "recommendation.json",
    "verification.json",
    "report.md",
}
SCENARIO_IDS = (
    "status_quo",
    "truth_guided_absence_floor_all",
    "detection_blocker_respecting_floor",
    "late_followup_detection_blocker_respecting",
)
NON_INFERENCE_LABELS = {
    "synthetic_only": True,
    "evaluation_only": True,
    "counterfactual_only": True,
    "not_formal_inference": True,
    "no_default_observation_design_change": True,
    "no_reconstruction_rule_change": True,
    "no_scoring_change": True,
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def build_counterfactual_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
    observation_dir = tmp_path / "observations"
    build_synth_small_observations().write_artifacts(observation_dir)

    reconstruction_dir = tmp_path / "reconstruction"
    build_synth_small_extirpation_reconstruction(observation_dir).write_artifacts(
        reconstruction_dir
    )

    screen_dir = tmp_path / "response_screen"
    build_response_only_screen(reconstruction_dir).write_artifacts(screen_dir)

    evaluation_dir = screen_dir / "evaluation"
    evaluate_synth_small_response_screen(
        screen_dir=screen_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    ).write_artifacts(evaluation_dir)

    summary_dir = tmp_path / "summary_vector"
    build_synth_small_summary_vector(
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    ).write_artifacts(summary_dir)

    compatibility_dir = tmp_path / "compatibility_screen"
    build_synth_small_compatibility_screen(target_dir=summary_dir).write_artifacts(
        compatibility_dir
    )

    mismatch_dir = compatibility_dir / "mismatch_audit"
    build_synth_small_compatibility_mismatch_audit(
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        evaluation_dir=evaluation_dir,
    ).write_artifacts(mismatch_dir)

    false_negative_dir = evaluation_dir / "false_negative_audit"
    build_synth_small_false_negative_mechanism_audit(
        evaluation_dir=evaluation_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
        mismatch_audit_dir=mismatch_dir,
    ).write_artifacts(false_negative_dir)

    return (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        summary_dir,
        compatibility_dir,
    )


def assert_non_inference_labels(payload: dict[str, object]) -> None:
    for key, value in NON_INFERENCE_LABELS.items():
        assert payload[key] is value


def summary_map(path: Path) -> dict[str, dict[str, str]]:
    return {row["scenario_id"]: row for row in read_csv_rows(path)}


def ranking_map(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["scenario_id"], row["candidate_label"]): row for row in read_csv_rows(path)}


def site_map(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["scenario_id"], row["site_id"]): row for row in read_csv_rows(path)}


def test_counterfactual_screen_writes_reconciled_synthetic_bundle(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        summary_dir,
        compatibility_dir,
    ) = build_counterfactual_inputs(tmp_path)

    result = build_synth_small_observation_support_counterfactual_screen(
        evaluation_dir=evaluation_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
        false_negative_audit_dir=false_negative_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
    )
    output_dir = tmp_path / "observation_support_counterfactual"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == COUNTERFACTUAL_FILES

    config = loads((output_dir / "counterfactual_config.json").read_text("utf-8"))
    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    scenarios = read_csv_rows(output_dir / "scenario_definitions.csv")
    summaries = summary_map(output_dir / "scenario_reconstruction_summary.csv")
    rankings = ranking_map(output_dir / "scenario_rankings.csv")

    assert_non_inference_labels(config)
    assert_non_inference_labels(verification)
    assert_non_inference_labels(recommendation)
    assert verification["passed"] is True
    assert config["source_verifications"]["summary_vector"] is True
    assert config["source_verifications"]["compatibility_screen"] is True
    assert verification["checks"][0]["details"]["summary_vector"] is True
    assert verification["checks"][0]["details"]["compatibility_screen"] is True
    assert tuple(row["scenario_id"] for row in scenarios) == SCENARIO_IDS
    assert config["scenario_count"] == 4
    assert config["status_quo_finite_target_count"] == 151
    assert config["false_negative_count"] == 101
    bridge = config["bridge_reconciliation"]
    assert bridge["summary_vector_realistic_observed_finite_target_count"] == 151
    assert bridge["summary_vector_ideal_true_finite_target_count"] == 252
    assert bridge["compatibility_target_realistic_observed_finite_target_count"] == 151
    assert bridge["compatibility_target_ideal_true_finite_target_count"] == 252
    assert bridge["goal010_realistic_observed_top_candidate_label"] == "default"
    assert bridge["goal010_realistic_observed_top_compatibility_class"] == "incompatible"
    assert bridge["status_quo_matches_existing_goal010"] is True
    assert bridge["ideal_true_finite_target_count_matches"] is True
    assert bridge["goal010_default_score_sum_matches_ranking_loss"] is True
    assert bridge["goal010_realistic_observed_top_total_weighted_loss"] == pytest.approx(
        3.52263635737
    )
    assert bridge["goal010_realistic_observed_default_score_sum"] == pytest.approx(3.52263635737)
    assert recommendation["recommendation_class"] == (
        "finite_target_support_improves_but_compatibility_not_restored"
    )

    assert summaries["status_quo"]["finite_target_count"] == "151"
    assert summaries["status_quo"]["remaining_false_negative_count"] == "101"
    assert summaries["status_quo"]["restores_status_quo_finite_drop"] == "false"
    assert summaries["status_quo"]["top_candidate_label"] == "default"
    assert summaries["status_quo"]["top_compatibility_class"] == "incompatible"
    assert float(summaries["status_quo"]["top_total_weighted_loss"]) == pytest.approx(
        3.522636357371111
    )

    all_support = summaries["truth_guided_absence_floor_all"]
    assert all_support["finite_target_count"] == "252"
    assert all_support["resolved_false_negative_count"] == "101"
    assert all_support["restores_status_quo_finite_drop"] == "true"
    assert all_support["top_compatibility_class"] == "incompatible"
    assert float(all_support["top_total_weighted_loss"]) == pytest.approx(1.8850033139786202)

    detection_respecting = summaries["detection_blocker_respecting_floor"]
    assert detection_respecting["finite_target_count"] == "202"
    assert detection_respecting["resolved_false_negative_count"] == "51"
    assert detection_respecting["remaining_post_extirpation_detection_blocker_count"] == "50"

    late_followup = summaries["late_followup_detection_blocker_respecting"]
    assert late_followup["finite_target_count"] == "198"
    assert late_followup["resolved_false_negative_count"] == "47"

    assert rankings[("status_quo", "default")]["rank"] == "1"
    assert rankings[("truth_guided_absence_floor_all", "default")]["rank"] == "1"
    assert {row["top_compatibility_class"] for row in summaries.values()} == {"incompatible"}


def test_site_counterfactual_resolution_respects_detection_blockers(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        summary_dir,
        compatibility_dir,
    ) = build_counterfactual_inputs(tmp_path)
    output_dir = tmp_path / "observation_support_counterfactual"

    build_synth_small_observation_support_counterfactual_screen(
        evaluation_dir=evaluation_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
        false_negative_audit_dir=false_negative_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
    ).write_artifacts(output_dir)

    sites = site_map(output_dir / "site_counterfactual_resolution.csv")

    assert len(sites) == 101 * len(SCENARIO_IDS)

    post_detection_all = sites[("truth_guided_absence_floor_all", "site_005")]
    assert post_detection_all["primary_mechanism"] == ("post_extirpation_detection_blocks_absence")
    assert post_detection_all["post_extirpation_detection_count"] == "1"
    assert post_detection_all["resolved_false_negative"] == "true"
    assert post_detection_all["counterfactual_observed_extirpation_time"] == "45"
    assert post_detection_all["synthetic_support_survey_count"] == "2"
    assert post_detection_all["unresolved_reason"] == ""

    post_detection_respected = sites[("detection_blocker_respecting_floor", "site_005")]
    assert post_detection_respected["resolved_false_negative"] == "false"
    assert post_detection_respected["counterfactual_observed_extirpation_time"] == ""
    assert post_detection_respected["unresolved_reason"] == "post_extirpation_detection_blocker"

    no_post = sites[("detection_blocker_respecting_floor", "site_014")]
    assert no_post["primary_mechanism"] == "no_post_extirpation_surveys"
    assert no_post["post_extirpation_detection_count"] == "0"
    assert no_post["resolved_false_negative"] == "true"
    assert no_post["counterfactual_observed_extirpation_time"] == "50"

    late_with_detection = sites[("late_followup_detection_blocker_respecting", "site_006")]
    assert late_with_detection["primary_mechanism"] == "late_extirpation_near_survey_horizon"
    assert late_with_detection["post_extirpation_detection_count"] == "1"
    assert late_with_detection["resolved_false_negative"] == "false"
    assert late_with_detection["unresolved_reason"] == "post_extirpation_detection_blocker"


def test_summary_and_score_outputs_are_machine_readable(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        summary_dir,
        compatibility_dir,
    ) = build_counterfactual_inputs(tmp_path)
    output_dir = tmp_path / "observation_support_counterfactual"

    build_synth_small_observation_support_counterfactual_screen(
        evaluation_dir=evaluation_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
        false_negative_audit_dir=false_negative_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
    ).write_artifacts(output_dir)

    vectors = read_csv_rows(output_dir / "scenario_summary_vectors.csv")
    scores = read_csv_rows(output_dir / "scenario_compatibility_scores.csv")
    rankings = read_csv_rows(output_dir / "scenario_rankings.csv")

    assert {row["scenario_id"] for row in vectors} == set(SCENARIO_IDS)
    assert {row["row_type"] for row in vectors} == {"summary_component", "coverage_curve"}
    assert {row["metric"] for row in vectors if row["row_type"] == "coverage_curve"} == {
        "target_time"
    }
    assert {row["metric"] for row in vectors if row["row_type"] == "summary_component"} >= {
        "finite_target_count",
        "finite_target_fraction",
        "lag_mean",
        "lag_std",
        "arrival_target_r2",
        "front_plane_gradient_magnitude",
    }

    assert len(scores) == len(SCENARIO_IDS) * 3 * 6
    assert {row["component"] for row in scores} == {
        "finite_target_fraction",
        "lag_mean",
        "lag_std",
        "arrival_target_r2",
        "front_plane_gradient_magnitude",
        "coverage_curve_rmse",
    }
    assert len(rankings) == len(SCENARIO_IDS) * 3


def test_observation_support_counterfactual_cli_writes_default_bundle(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        summary_dir,
        compatibility_dir,
    ) = build_counterfactual_inputs(tmp_path)
    output_dir = tmp_path / "observation_support_counterfactual"

    completed = run(
        [
            executable,
            "scripts/run_synth_small_observation_support_counterfactual.py",
            "--evaluation-dir",
            str(evaluation_dir),
            "--reconstruction-dir",
            str(reconstruction_dir),
            "--observation-dir",
            str(observation_dir),
            "--false-negative-audit-dir",
            str(false_negative_dir),
            "--summary-vector-dir",
            str(summary_dir),
            "--compatibility-screen-dir",
            str(compatibility_dir),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Observation-support counterfactual screen complete" in completed.stdout
    assert "Status quo finite targets: 151" in completed.stdout
    assert "False negatives audited: 101" in completed.stdout
    assert "Wrote 10 files" in completed.stdout

    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))
    assert recommendation["recommendation_class"] == (
        "finite_target_support_improves_but_compatibility_not_restored"
    )
