from __future__ import annotations

from csv import DictReader
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable

import pytest

from spatext.synth.small import (
    ResponseScreenEvaluationResult,
    build_response_only_screen,
    build_synth_small_compatibility_mismatch_audit,
    build_synth_small_compatibility_screen,
    build_synth_small_extirpation_reconstruction,
    build_synth_small_false_negative_mechanism_audit,
    build_synth_small_observation_support_counterfactual_screen,
    build_synth_small_observations,
    build_synth_small_summary_vector,
    build_synth_small_target_timing_residual_decomposition,
    evaluate_synth_small_response_screen,
)

RESIDUAL_FILES = {
    "residual_decomposition_config.json",
    "target_transform_definitions.csv",
    "site_target_transform_resolution.csv",
    "target_transform_summary_vectors.csv",
    "target_transform_component_losses.csv",
    "target_transform_rankings.csv",
    "component_delta_table.csv",
    "recommendation.json",
    "verification.json",
    "report.md",
}
TRANSFORM_IDS = (
    "status_quo_observed",
    "goal013_support_floor",
    "false_negative_true_time",
    "false_negative_true_time_detection_respecting",
    "all_extirpated_true_time",
)
NON_INFERENCE_LABELS = {
    "synthetic_only": True,
    "evaluation_only": True,
    "target_transform_diagnostic_only": True,
    "not_formal_inference": True,
    "no_default_observation_change": True,
    "no_reconstruction_rule_change": True,
    "no_scoring_change": True,
    "no_candidate_change": True,
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def build_residual_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path, Path, Path]:
    observation_dir = tmp_path / "observations"
    build_synth_small_observations().write_artifacts(observation_dir)

    reconstruction_dir = tmp_path / "reconstruction"
    build_synth_small_extirpation_reconstruction(observation_dir).write_artifacts(
        reconstruction_dir
    )

    screen_dir = tmp_path / "response_screen"
    build_response_only_screen(reconstruction_dir).write_artifacts(screen_dir)

    evaluation_dir = screen_dir / "evaluation"
    evaluate_result = build_response_screen_evaluation(
        screen_dir=screen_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    )
    evaluate_result.write_artifacts(evaluation_dir)

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

    counterfactual_dir = evaluation_dir / "observation_support_counterfactual"
    build_synth_small_observation_support_counterfactual_screen(
        evaluation_dir=evaluation_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
        false_negative_audit_dir=false_negative_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
    ).write_artifacts(counterfactual_dir)

    return (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        counterfactual_dir,
        summary_dir,
        compatibility_dir,
    )


def build_response_screen_evaluation(
    *,
    screen_dir: Path,
    reconstruction_dir: Path,
    observation_dir: Path,
) -> ResponseScreenEvaluationResult:
    return evaluate_synth_small_response_screen(
        screen_dir=screen_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    )


def assert_non_inference_labels(payload: dict[str, object]) -> None:
    for key, value in NON_INFERENCE_LABELS.items():
        assert payload[key] is value


def ranking_map(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    return {
        (row["target_transform_id"], row["candidate_label"]): row for row in read_csv_rows(path)
    }


def summary_component_map(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    return {
        (row["target_transform_id"], row["metric"]): row
        for row in read_csv_rows(path)
        if row["row_type"] == "summary_component"
    }


def test_residual_decomposition_writes_reconciled_diagnostic_bundle(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        counterfactual_dir,
        summary_dir,
        compatibility_dir,
    ) = build_residual_inputs(tmp_path)

    result = build_synth_small_target_timing_residual_decomposition(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        false_negative_audit_dir=false_negative_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
    )
    output_dir = tmp_path / "target_timing_residual_decomposition"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == RESIDUAL_FILES

    config = loads((output_dir / "residual_decomposition_config.json").read_text("utf-8"))
    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    definitions = read_csv_rows(output_dir / "target_transform_definitions.csv")
    rankings = ranking_map(output_dir / "target_transform_rankings.csv")
    components = summary_component_map(output_dir / "target_transform_summary_vectors.csv")

    assert_non_inference_labels(config)
    assert_non_inference_labels(verification)
    assert_non_inference_labels(recommendation)
    assert verification["passed"] is True
    checks = {check["name"]: check for check in verification["checks"]}
    assert checks["component_loss_accounting"]["passed"] is True
    assert checks["component_loss_accounting"]["details"]["score_row_count"] == 90
    assert checks["component_loss_accounting"]["details"]["expected_score_row_count"] == 90
    assert tuple(row["target_transform_id"] for row in definitions) == TRANSFORM_IDS
    assert config["source_verifications"]["summary_vector"] is True
    assert config["source_verifications"]["compatibility_screen"] is True
    assert config["summary_vector_contract_interpretation"]["target_summary_json_present"] is False
    assert (
        config["summary_vector_contract_interpretation"]["using_existing_goal009_contract"] is True
    )

    status_quo = rankings[("status_quo_observed", "default")]
    assert components[("status_quo_observed", "finite_target_count")]["value"] == "151"
    assert status_quo["rank"] == "1"
    assert status_quo["compatibility_class"] == "incompatible"
    assert float(status_quo["total_weighted_loss"]) == pytest.approx(3.52263635737)

    support_floor = rankings[("goal013_support_floor", "default")]
    assert components[("goal013_support_floor", "finite_target_count")]["value"] == "252"
    assert support_floor["rank"] == "1"
    assert support_floor["compatibility_class"] == "incompatible"
    assert float(support_floor["total_weighted_loss"]) == pytest.approx(1.88500331398)

    ideal = rankings[("all_extirpated_true_time", "default")]
    assert components[("all_extirpated_true_time", "finite_target_count")]["value"] == "252"
    assert ideal["rank"] == "1"
    assert ideal["compatibility_class"] == "compatible"
    assert float(ideal["total_weighted_loss"]) == pytest.approx(0.0)
    assert recommendation["recommendation_class"] == "timing_bias_drives_residual"
    assert recommendation["compatibility_restored_by"] == ["all_extirpated_true_time"]


def test_site_resolution_and_component_deltas_are_auditable(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        counterfactual_dir,
        summary_dir,
        compatibility_dir,
    ) = build_residual_inputs(tmp_path)
    output_dir = tmp_path / "target_timing_residual_decomposition"

    build_synth_small_target_timing_residual_decomposition(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        false_negative_audit_dir=false_negative_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
    ).write_artifacts(output_dir)

    sites = {
        (row["target_transform_id"], row["site_id"]): row
        for row in read_csv_rows(output_dir / "site_target_transform_resolution.csv")
    }
    losses = read_csv_rows(output_dir / "target_transform_component_losses.csv")
    rankings = ranking_map(output_dir / "target_transform_rankings.csv")
    deltas = read_csv_rows(output_dir / "component_delta_table.csv")

    assert len(sites) == 625 * len(TRANSFORM_IDS)
    assert {
        "absolute_delta_from_status_quo_rank_within_transform_candidate",
        "absolute_delta_from_goal013_support_floor_rank_within_transform_candidate",
    } <= set(deltas[0])

    false_negative = sites[("false_negative_true_time", "site_014")]
    assert false_negative["false_negative"] == "true"
    assert false_negative["primary_mechanism"] == "no_post_extirpation_surveys"
    assert false_negative["status_quo_target_time"] == ""
    assert false_negative["transformed_target_time"] == "49"
    assert false_negative["resolution_class"] == "false_negative_true_time_replacement"

    blocker = sites[("false_negative_true_time_detection_respecting", "site_005")]
    assert blocker["post_extirpation_detection_count"] == "1"
    assert blocker["transformed_target_time"] == ""
    assert blocker["resolution_class"] == "post_extirpation_detection_blocker_unresolved"

    for transform_id in TRANSFORM_IDS:
        rows = [
            row
            for row in losses
            if row["target_transform_id"] == transform_id and row["candidate_label"] == "default"
        ]
        weighted_sum = sum(float(row["weighted_gap"] or 0.0) for row in rows)
        ranking_loss = float(rankings[(transform_id, "default")]["total_weighted_loss"])
        assert weighted_sum == pytest.approx(ranking_loss)

    support_deltas = [
        row
        for row in deltas
        if row["target_transform_id"] == "goal013_support_floor"
        and row["candidate_label"] == "default"
    ]
    assert support_deltas[0]["component"] == "coverage_curve_rmse"
    assert float(support_deltas[0]["weighted_gap"]) == pytest.approx(0.676110198119)
    assert {row["component"] for row in support_deltas[:4]} == {
        "coverage_curve_rmse",
        "lag_mean",
        "front_plane_gradient_magnitude",
        "arrival_target_r2",
    }
    assert all(
        row["delta_from_goal013_support_floor_weighted_gap"] == "0" for row in support_deltas
    )

    ideal_default_deltas = [
        row
        for row in deltas
        if row["target_transform_id"] == "all_extirpated_true_time"
        and row["candidate_label"] == "default"
    ]
    ideal_by_support_delta_rank = sorted(
        ideal_default_deltas,
        key=lambda row: int(
            row["absolute_delta_from_goal013_support_floor_rank_within_transform_candidate"]
        ),
    )
    assert [row["component"] for row in ideal_by_support_delta_rank[:4]] == [
        "coverage_curve_rmse",
        "lag_mean",
        "front_plane_gradient_magnitude",
        "arrival_target_r2",
    ]
    assert [
        row["absolute_delta_from_goal013_support_floor_rank_within_transform_candidate"]
        for row in ideal_by_support_delta_rank[:4]
    ] == ["1", "2", "3", "4"]


def test_target_timing_residual_cli_writes_default_bundle(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        counterfactual_dir,
        summary_dir,
        compatibility_dir,
    ) = build_residual_inputs(tmp_path)
    output_dir = tmp_path / "target_timing_residual_decomposition"

    completed = run(
        [
            executable,
            "scripts/analyze_synth_small_target_timing_residuals.py",
            "--observation-dir",
            str(observation_dir),
            "--reconstruction-dir",
            str(reconstruction_dir),
            "--evaluation-dir",
            str(evaluation_dir),
            "--false-negative-audit-dir",
            str(false_negative_dir),
            "--observation-support-counterfactual-dir",
            str(counterfactual_dir),
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

    assert "Target-timing residual decomposition complete" in completed.stdout
    assert "Transforms evaluated: 5" in completed.stdout
    assert "Goal 010 ideal true restored by: all_extirpated_true_time" in completed.stdout
    assert "Recommendation: timing_bias_drives_residual" in completed.stdout
    assert "Wrote 10 files" in completed.stdout
