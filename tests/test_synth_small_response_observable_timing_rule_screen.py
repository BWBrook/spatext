from __future__ import annotations

from collections import Counter
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
    build_synth_small_response_observable_timing_rule_screen,
    build_synth_small_summary_vector,
    build_synth_small_target_time_error_anatomy_audit,
    build_synth_small_target_timing_residual_decomposition,
    evaluate_synth_small_response_screen,
)

RULE_SCREEN_FILES = {
    "timing_rule_screen_config.json",
    "rule_definitions.csv",
    "site_rule_resolution.csv",
    "rule_summary_vectors.csv",
    "rule_component_losses.csv",
    "rule_rankings.csv",
    "proxy_rule_performance.csv",
    "grid_simplicity_risk_audit.csv",
    "recommendation.json",
    "verification.json",
    "report.md",
}
RULE_IDS = (
    "status_quo_observed",
    "long_detection_gap_shift_minus4",
    "west_band_shift_minus4",
    "long_gap_or_west_band_shift_minus4",
    "nonfinite_supported_final_survey_gap_expansion",
    "nonfinite_last_survey_expansion",
    "goal013_support_floor",
    "all_extirpated_true_time",
)
CONSERVATIVE_FINITE_SUPPORT_RULE_ID = "nonfinite_supported_final_survey_gap_expansion"
NON_INFERENCE_LABELS = {
    "synthetic_only": True,
    "evaluation_only": True,
    "response_observable_rule_screen_only": True,
    "not_formal_inference": True,
    "no_default_observation_change": True,
    "no_reconstruction_rule_change": True,
    "no_scoring_change": True,
    "no_candidate_change": True,
    "no_richer_landscape_change": True,
    "no_pom_or_likelihood_change": True,
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def build_rule_screen_inputs(
    tmp_path: Path,
) -> tuple[Path, Path, Path, Path, Path, Path, Path, Path]:
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

    counterfactual_dir = evaluation_dir / "observation_support_counterfactual"
    build_synth_small_observation_support_counterfactual_screen(
        evaluation_dir=evaluation_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
        false_negative_audit_dir=false_negative_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
    ).write_artifacts(counterfactual_dir)

    residual_dir = evaluation_dir / "target_timing_residual_decomposition"
    build_synth_small_target_timing_residual_decomposition(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        false_negative_audit_dir=false_negative_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
    ).write_artifacts(residual_dir)

    anatomy_dir = evaluation_dir / "target_time_error_anatomy"
    build_synth_small_target_time_error_anatomy_audit(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        false_negative_audit_dir=false_negative_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        target_timing_residual_dir=residual_dir,
    ).write_artifacts(anatomy_dir)

    return (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        summary_dir,
        compatibility_dir,
        counterfactual_dir,
        residual_dir,
        anatomy_dir,
    )


def assert_non_inference_labels(payload: dict[str, object]) -> None:
    for key, value in NON_INFERENCE_LABELS.items():
        assert payload[key] is value


def default_ranking_map(path: Path) -> dict[str, dict[str, str]]:
    return {
        row["target_rule_id"]: row
        for row in read_csv_rows(path)
        if row["candidate_label"] == "default"
    }


def conservative_supported_final_survey_gap_site_ids(
    anatomy_dir: Path,
) -> set[str]:
    expected: set[str] = set()
    for row in read_csv_rows(anatomy_dir / "site_target_time_error_audit.csv"):
        if row["status_quo_finite"] == "true":
            continue
        if not row["last_detection_time"] or not row["last_survey_time"]:
            continue
        final_absence_count = int(row["final_absence_survey_time_count"])
        survey_time_count = int(row["survey_time_count"])
        detection_count = int(row["detection_count"])
        final_gap = float(row["last_survey_time"]) - float(row["last_detection_time"])
        if (
            final_absence_count < 2
            and survey_time_count >= 8
            and detection_count >= 1
            and final_gap >= 8
        ):
            expected.add(row["site_id"])
    return expected


def test_timing_rule_screen_writes_reconciled_rule_bundle(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        summary_dir,
        compatibility_dir,
        counterfactual_dir,
        residual_dir,
        anatomy_dir,
    ) = build_rule_screen_inputs(tmp_path)

    result = build_synth_small_response_observable_timing_rule_screen(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        target_timing_residual_dir=residual_dir,
        target_time_error_anatomy_dir=anatomy_dir,
    )
    output_dir = tmp_path / "response_observable_timing_rule_screen"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == RULE_SCREEN_FILES

    config = loads((output_dir / "timing_rule_screen_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))
    definitions = read_csv_rows(output_dir / "rule_definitions.csv")
    site_rows = read_csv_rows(output_dir / "site_rule_resolution.csv")
    rankings = default_ranking_map(output_dir / "rule_rankings.csv")

    assert_non_inference_labels(config)
    assert_non_inference_labels(verification)
    assert_non_inference_labels(recommendation)
    assert verification["passed"] is True
    checks = {check["name"]: check for check in verification["checks"]}
    assert checks["prior_goal_reconciliation"]["passed"] is True
    assert checks["component_loss_accounting"]["details"] == {
        "score_row_count": 144,
        "expected_score_row_count": 144,
    }

    assert tuple(row["target_rule_id"] for row in definitions) == RULE_IDS
    eligibility_counts = Counter(row["eligibility_class"] for row in definitions)
    assert eligibility_counts == {
        "status_quo_baseline": 1,
        "response_observable": 5,
        "truth_guided_reference": 1,
        "truth_only_reference": 1,
    }
    assert {row["target_rule_id"] for row in definitions if row["spatially_keyed"] == "true"} == {
        "west_band_shift_minus4",
        "long_gap_or_west_band_shift_minus4",
    }
    assert (
        next(
            row for row in definitions if row["target_rule_id"] == "nonfinite_last_survey_expansion"
        )["may_assign_finite_to_status_quo_nonfinite"]
        == "true"
    )
    conservative_definition = next(
        row for row in definitions if row["target_rule_id"] == CONSERVATIVE_FINITE_SUPPORT_RULE_ID
    )
    assert conservative_definition["may_assign_finite_to_status_quo_nonfinite"] == "true"
    assert conservative_definition["rule_family"] == "finite_target_expansion"
    assert (
        "final_absence_survey_time_count"
        in conservative_definition["response_observable_source_columns"]
    )
    assert "last_detection_time" in conservative_definition["response_observable_source_columns"]
    assert "last_survey_time" in conservative_definition["response_observable_source_columns"]

    assert len(site_rows) == 625 * len(RULE_IDS)
    assert sum(row["target_rule_id"] == "status_quo_observed" for row in site_rows) == 625
    assert (
        sum(
            row["target_rule_id"] == "status_quo_observed" and row["rule_finite"] == "true"
            for row in site_rows
        )
        == 151
    )
    assert (
        sum(
            row["target_rule_id"] == "goal013_support_floor" and row["rule_finite"] == "true"
            for row in site_rows
        )
        == 252
    )
    assert (
        sum(
            row["target_rule_id"] == "all_extirpated_true_time" and row["rule_finite"] == "true"
            for row in site_rows
        )
        == 252
    )

    status_quo = rankings["status_quo_observed"]
    assert status_quo["finite_target_count"] == "151"
    assert status_quo["compatibility_class"] == "incompatible"
    assert float(status_quo["total_weighted_loss"]) == pytest.approx(3.52263635737)

    support = rankings["goal013_support_floor"]
    assert support["finite_target_count"] == "252"
    assert support["compatibility_class"] == "incompatible"
    assert float(support["total_weighted_loss"]) == pytest.approx(1.88500331398)

    all_true = rankings["all_extirpated_true_time"]
    assert all_true["finite_target_count"] == "252"
    assert all_true["compatibility_class"] == "compatible"
    assert float(all_true["total_weighted_loss"]) == pytest.approx(0.0)

    best = recommendation["best_eligible_response_observable_rule"]
    assert best["target_rule_id"] == CONSERVATIVE_FINITE_SUPPORT_RULE_ID
    assert best["compatibility_class"] == "incompatible"
    assert float(best["total_weighted_loss"]) == pytest.approx(3.17643512355137)
    assert best["improves_loss_vs_status_quo"] is True
    assert recommendation["recommendation_class"] == "response_only_signal_insufficient"
    assert recommendation["eligible_response_observable_rule_count"] == 5
    assert recommendation["compatible_eligible_response_observable_rule_count"] == 0


def test_conservative_finite_support_expansion_is_auditable(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        summary_dir,
        compatibility_dir,
        counterfactual_dir,
        residual_dir,
        anatomy_dir,
    ) = build_rule_screen_inputs(tmp_path)
    output_dir = tmp_path / "response_observable_timing_rule_screen"

    build_synth_small_response_observable_timing_rule_screen(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        target_timing_residual_dir=residual_dir,
        target_time_error_anatomy_dir=anatomy_dir,
    ).write_artifacts(output_dir)

    rankings = default_ranking_map(output_dir / "rule_rankings.csv")
    site_rows = read_csv_rows(output_dir / "site_rule_resolution.csv")
    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))
    expected_site_ids = conservative_supported_final_survey_gap_site_ids(anatomy_dir)
    conservative_site_rows = [
        row for row in site_rows if row["target_rule_id"] == CONSERVATIVE_FINITE_SUPPORT_RULE_ID
    ]
    conservative_converted = [
        row for row in conservative_site_rows if row["status_quo_nonfinite_to_finite"] == "true"
    ]
    stress_converted = [
        row
        for row in site_rows
        if row["target_rule_id"] == "nonfinite_last_survey_expansion"
        and row["status_quo_nonfinite_to_finite"] == "true"
    ]

    assert {row["site_id"] for row in conservative_converted} == expected_site_ids
    assert 0 < len(conservative_converted) < len(stress_converted)

    true_converted = sum(row["true_extirpated_by_end"] == "true" for row in conservative_converted)
    not_true_converted = sum(
        row["true_extirpated_by_end"] == "false" for row in conservative_converted
    )
    conservative = rankings[CONSERVATIVE_FINITE_SUPPORT_RULE_ID]
    assert {
        "status_quo_nonfinite_to_finite_count",
        "status_quo_nonfinite_to_finite_true_extirpated_count",
        "status_quo_nonfinite_to_finite_not_true_extirpated_count",
        "loss_delta_from_goal013_support_floor",
        "loss_gap_fraction_closed_to_goal013_support_floor",
        "finite_support_role",
    } <= set(conservative)
    assert int(conservative["status_quo_nonfinite_to_finite_count"]) == len(conservative_converted)
    assert (
        int(conservative["status_quo_nonfinite_to_finite_true_extirpated_count"]) == true_converted
    )
    assert (
        int(conservative["status_quo_nonfinite_to_finite_not_true_extirpated_count"])
        == not_true_converted
    )
    assert int(conservative["finite_target_count"]) == 151 + len(conservative_converted)
    assert conservative["compatibility_class"] == "incompatible"
    assert float(conservative["loss_delta_from_goal013_support_floor"]) > 0
    assert conservative["finite_support_role"] == "conservative_finite_support_candidate"

    finite_support = recommendation["finite_support_screen"]
    assert (
        finite_support["conservative_candidate"]["target_rule_id"]
        == CONSERVATIVE_FINITE_SUPPORT_RULE_ID
    )
    assert finite_support["conservative_candidate"]["status_quo_nonfinite_to_finite_count"] == len(
        conservative_converted
    )
    assert (
        finite_support["conservative_candidate"][
            "status_quo_nonfinite_to_finite_true_extirpated_count"
        ]
        == true_converted
    )
    assert (
        finite_support["conservative_candidate"][
            "status_quo_nonfinite_to_finite_not_true_extirpated_count"
        ]
        == not_true_converted
    )
    assert finite_support["broad_stress_test"]["target_rule_id"] == (
        "nonfinite_last_survey_expansion"
    )
    assert finite_support["conservative_candidate_materially_approaches_goal013"] is False
    assert "conservative finite-support" in " ".join(recommendation["rationale"])


def test_proxy_performance_and_grid_risk_are_auditable(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        summary_dir,
        compatibility_dir,
        counterfactual_dir,
        residual_dir,
        anatomy_dir,
    ) = build_rule_screen_inputs(tmp_path)
    output_dir = tmp_path / "response_observable_timing_rule_screen"

    build_synth_small_response_observable_timing_rule_screen(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        target_timing_residual_dir=residual_dir,
        target_time_error_anatomy_dir=anatomy_dir,
    ).write_artifacts(output_dir)

    proxy_rows = {
        (row["signal_id"], row["target_rule_id"]): row
        for row in read_csv_rows(output_dir / "proxy_rule_performance.csv")
    }
    grid_rows = {
        row["target_rule_id"]: row
        for row in read_csv_rows(output_dir / "grid_simplicity_risk_audit.csv")
    }
    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))

    long_gap = proxy_rows[("long_detection_to_target_gap", "long_detection_gap_shift_minus4")]
    assert long_gap["true_extirpated_affected_site_count"] == "79"
    assert long_gap["status_quo_large_abs_error_count"] == "49"
    assert long_gap["rule_large_abs_error_count"] == "27"
    assert float(long_gap["rule_mean_absolute_error"]) == pytest.approx(6.46835443038)

    spatial = proxy_rows[("spatial_front_band_west_band_signal", "west_band_shift_minus4")]
    assert spatial["true_extirpated_affected_site_count"] == "112"
    assert spatial["status_quo_large_abs_error_count"] == "49"
    assert spatial["rule_large_abs_error_count"] == "25"
    assert spatial["rule_nonfinite_true_extirpated_count"] == "14"

    sparse = proxy_rows[("sparse_survey_history", "long_detection_gap_shift_minus4")]
    assert sparse["true_extirpated_affected_site_count"] == "52"
    assert sparse["status_quo_nonfinite_true_extirpated_count"] == "31"
    assert sparse["rule_large_abs_error_count"] == "6"

    west_risk = grid_rows["west_band_shift_minus4"]
    assert west_risk["spatially_keyed"] == "true"
    assert west_risk["overfit_risk_class"] == "simple_grid_spatial_proxy_overfit_risk"
    assert float(west_risk["west_band_mean_absolute_error_delta_from_status_quo"]) < 0
    assert recommendation["grid_simplicity_risk_assessment"]["spatial_rules_are_diagnostic_only"]


def test_timing_rule_screen_cli(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        summary_dir,
        compatibility_dir,
        counterfactual_dir,
        residual_dir,
        anatomy_dir,
    ) = build_rule_screen_inputs(tmp_path)
    output_dir = tmp_path / "response_observable_timing_rule_screen"

    command = [
        executable,
        "scripts/screen_synth_small_response_observable_timing_rules.py",
        "--observation-dir",
        str(observation_dir),
        "--reconstruction-dir",
        str(reconstruction_dir),
        "--evaluation-dir",
        str(evaluation_dir),
        "--summary-vector-dir",
        str(summary_dir),
        "--compatibility-screen-dir",
        str(compatibility_dir),
        "--observation-support-counterfactual-dir",
        str(counterfactual_dir),
        "--target-timing-residual-dir",
        str(residual_dir),
        "--target-time-error-anatomy-dir",
        str(anatomy_dir),
        "--output-dir",
        str(output_dir),
    ]
    completed = run(command, check=True, capture_output=True, text=True)

    assert "Response-observable timing-rule screen complete" in completed.stdout
    assert "Recommendation: response_only_signal_insufficient" in completed.stdout
    assert f"Best eligible rule: {CONSERVATIVE_FINITE_SUPPORT_RULE_ID}" in completed.stdout
    assert set(path.name for path in output_dir.iterdir()) == RULE_SCREEN_FILES
