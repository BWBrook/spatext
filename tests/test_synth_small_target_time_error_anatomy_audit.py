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
    build_synth_small_summary_vector,
    build_synth_small_target_time_error_anatomy_audit,
    build_synth_small_target_timing_residual_decomposition,
    evaluate_synth_small_response_screen,
)

ERROR_ANATOMY_FILES = {
    "target_time_error_anatomy_config.json",
    "site_target_time_error_audit.csv",
    "target_time_error_group_summary.csv",
    "error_mechanism_summary.csv",
    "observable_proxy_summary.csv",
    "transform_error_contrast.csv",
    "bias_classification_summary.csv",
    "recommendation.json",
    "verification.json",
    "report.md",
}
NON_INFERENCE_LABELS = {
    "synthetic_only": True,
    "evaluation_only": True,
    "error_anatomy_diagnostic_only": True,
    "not_formal_inference": True,
    "no_default_observation_change": True,
    "no_reconstruction_rule_change": True,
    "no_scoring_change": True,
    "no_candidate_change": True,
}
SITE_REQUIRED_COLUMNS = {
    "status_quo_signed_error",
    "status_quo_absolute_error",
    "support_floor_signed_error",
    "support_floor_absolute_error",
    "response_observable_proxy_flags",
    "truth_only_signal_flags",
    "mixed_signal_flags",
}
PROXY_REQUIRED_COLUMNS = {
    "true_extirpated_affected_site_count",
    "support_floor_large_abs_error_site_count",
    "support_floor_large_abs_error_fraction",
    "rule_screen_role",
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def build_error_anatomy_inputs(
    tmp_path: Path,
) -> tuple[Path, Path, Path, Path, Path, Path]:
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

    return (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        counterfactual_dir,
        residual_dir,
    )


def assert_non_inference_labels(payload: dict[str, object]) -> None:
    for key, value in NON_INFERENCE_LABELS.items():
        assert payload[key] is value


def test_error_anatomy_writes_reconciled_site_audit(tmp_path: Path) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        counterfactual_dir,
        residual_dir,
    ) = build_error_anatomy_inputs(tmp_path)

    result = build_synth_small_target_time_error_anatomy_audit(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        false_negative_audit_dir=false_negative_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        target_timing_residual_dir=residual_dir,
    )
    output_dir = tmp_path / "target_time_error_anatomy"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == ERROR_ANATOMY_FILES

    config = loads((output_dir / "target_time_error_anatomy_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))
    sites = read_csv_rows(output_dir / "site_target_time_error_audit.csv")

    assert_non_inference_labels(config)
    assert_non_inference_labels(verification)
    assert_non_inference_labels(recommendation)
    assert verification["passed"] is True
    checks = {check["name"]: check for check in verification["checks"]}
    assert checks["prior_goal_reconciliation"]["passed"] is True
    assert checks["prior_goal_reconciliation"]["details"] == {
        "site_count": 625,
        "ideal_true_finite_target_count": 252,
        "status_quo_finite_target_count": 151,
        "false_negative_count": 101,
        "support_floor_finite_target_count": 252,
        "all_extirpated_true_time_restores_compatibility": True,
    }

    assert len(sites) == 625
    assert len({row["site_id"] for row in sites}) == 625
    assert set(sites[0]) >= SITE_REQUIRED_COLUMNS
    assert sum(row["true_extirpated_by_end"] == "true" for row in sites) == 252
    assert sum(row["status_quo_finite"] == "true" for row in sites) == 151
    assert sum(row["support_floor_finite"] == "true" for row in sites) == 252
    assert sum(row["false_negative"] == "true" for row in sites) == 101

    sites_by_id = {row["site_id"]: row for row in sites}
    west_finite = sites_by_id["site_000"]
    assert west_finite["status_quo_signed_error"] == "2"
    assert west_finite["support_floor_signed_error"] == "2"
    assert west_finite["status_quo_error_direction"] == "late"
    assert west_finite["support_floor_error_magnitude_class"] == "small_abs_1_to_3"
    assert "spatial_front_band_west_band_signal" in west_finite[
        "response_observable_proxy_flags"
    ].split(";")

    no_post = sites_by_id["site_014"]
    assert no_post["false_negative"] == "true"
    assert no_post["primary_mechanism"] == "no_post_extirpation_surveys"
    assert no_post["status_quo_error_direction"] == "nonfinite"
    assert no_post["support_floor_signed_error"] == "1"
    assert no_post["support_floor_improves_absolute_error"] == "true"
    assert all(
        "weak_east_or_edge_signal" not in row["response_observable_proxy_flags"].split(";")
        for row in sites
    )


def test_group_summaries_proxy_inventory_and_recommendation_are_auditable(
    tmp_path: Path,
) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        counterfactual_dir,
        residual_dir,
    ) = build_error_anatomy_inputs(tmp_path)
    output_dir = tmp_path / "target_time_error_anatomy"

    build_synth_small_target_time_error_anatomy_audit(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        false_negative_audit_dir=false_negative_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        target_timing_residual_dir=residual_dir,
    ).write_artifacts(output_dir)

    groups = read_csv_rows(output_dir / "target_time_error_group_summary.csv")
    mechanisms = read_csv_rows(output_dir / "error_mechanism_summary.csv")
    proxies = read_csv_rows(output_dir / "observable_proxy_summary.csv")
    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))

    group_map = {(row["group_type"], row["group"]): row for row in groups}
    assert group_map[("overall", "all_sites")]["site_count"] == "625"
    assert group_map[("overall", "all_sites")]["true_extirpated_count"] == "252"
    assert group_map[("overall", "all_sites")]["support_floor_late_count"] == "235"
    assert float(group_map[("overall", "all_sites")]["support_floor_mean_absolute_error"]) == (
        pytest.approx(4.98015873015873)
    )
    assert (
        group_map[("primary_mechanism", "not_false_negative")][
            "support_floor_large_abs_error_count"
        ]
        == "73"
    )
    assert float(
        group_map[("primary_mechanism", "no_post_extirpation_surveys")][
            "support_floor_mean_absolute_error"
        ]
    ) == pytest.approx(1.0)

    mechanism_counts = {
        row["mechanism_label"]: int(row["true_extirpated_count"]) for row in mechanisms
    }
    assert mechanism_counts["not_false_negative"] == 151
    assert mechanism_counts["no_post_extirpation_surveys"] == 39
    assert mechanism_counts["post_extirpation_detection_blocks_absence"] == 28

    proxy_classes = Counter(row["observability_class"] for row in proxies)
    assert proxy_classes["response_observable"] >= 3
    assert proxy_classes["truth_only"] >= 2
    assert proxy_classes["mixed"] >= 2
    proxy_by_id = {row["signal_id"]: row for row in proxies}
    assert set(proxies[0]) >= PROXY_REQUIRED_COLUMNS
    assert proxy_by_id["status_quo_nonfinite"]["affected_site_count"] == "474"
    assert proxy_by_id["status_quo_nonfinite"]["rule_screen_role"] == (
        "finite_target_support_context"
    )
    assert proxy_by_id["status_quo_nonfinite"]["support_floor_large_abs_error_site_count"] == "0"
    assert proxy_by_id["short_final_absence_run"]["rule_screen_role"] == (
        "finite_target_support_context"
    )
    assert proxy_by_id["short_final_absence_run"]["support_floor_large_abs_error_site_count"] == "0"
    assert proxy_by_id["long_detection_to_target_gap"]["rule_screen_role"] == (
        "residual_timing_candidate"
    )
    assert (
        proxy_by_id["long_detection_to_target_gap"]["true_extirpated_affected_site_count"] == "79"
    )
    assert (
        proxy_by_id["long_detection_to_target_gap"]["support_floor_large_abs_error_site_count"]
        == "49"
    )
    assert float(
        proxy_by_id["long_detection_to_target_gap"]["support_floor_large_abs_error_fraction"]
    ) == pytest.approx(49 / 79)
    assert proxy_by_id["spatial_front_band_west_band_signal"]["observability_class"] == (
        "response_observable"
    )
    assert proxy_by_id["spatial_front_band_west_band_signal"]["source_artifact_columns"] == (
        "sites.csv:region,front_band"
    )
    assert proxy_by_id["spatial_front_band_west_band_signal"]["rule_screen_role"] == (
        "residual_timing_candidate"
    )
    assert (
        proxy_by_id["spatial_front_band_west_band_signal"]["true_extirpated_affected_site_count"]
        == "112"
    )
    assert (
        proxy_by_id["spatial_front_band_west_band_signal"][
            "support_floor_large_abs_error_site_count"
        ]
        == "49"
    )
    assert proxy_by_id["target_time_signed_error"]["observability_class"] == "truth_only"
    assert proxy_by_id["target_time_signed_error"]["rule_screen_role"] == ("truth_only_reference")
    assert proxy_by_id["near_horizon_to_true_extirpation"]["observability_class"] == "mixed"
    assert proxy_by_id["near_horizon_to_true_extirpation"]["rule_screen_role"] == (
        "mixed_evaluation_context"
    )

    assert recommendation["recommendation_class"] == "response_observable_rule_screen_ready"
    assert recommendation["residual_timing_candidate_count"] >= 2
    assert recommendation["top_residual_timing_candidate_proxies"][0] == {
        "signal_id": "long_detection_to_target_gap",
        "support_floor_large_abs_error_site_count": 49,
        "support_floor_large_abs_error_fraction": pytest.approx(49 / 79),
    }
    assert any(
        row["signal_id"] == "spatial_front_band_west_band_signal"
        for row in recommendation["top_residual_timing_candidate_proxies"]
    )
    assert recommendation["status_quo_finite_target_count"] == 151
    assert recommendation["support_floor_finite_target_count"] == 252
    assert recommendation["dominant_remaining_error_group"] == {
        "group_type": "primary_mechanism",
        "group": "not_false_negative",
        "large_abs_error_count": 73,
    }
    assert recommendation["strongest_spatial_signal"]["group"] == "west_band"


def test_transform_contrast_bias_classification_and_cli(
    tmp_path: Path,
) -> None:
    (
        observation_dir,
        reconstruction_dir,
        evaluation_dir,
        false_negative_dir,
        counterfactual_dir,
        residual_dir,
    ) = build_error_anatomy_inputs(tmp_path)
    output_dir = tmp_path / "target_time_error_anatomy"

    build_synth_small_target_time_error_anatomy_audit(
        observation_dir=observation_dir,
        reconstruction_dir=reconstruction_dir,
        evaluation_dir=evaluation_dir,
        false_negative_audit_dir=false_negative_dir,
        observation_support_counterfactual_dir=counterfactual_dir,
        target_timing_residual_dir=residual_dir,
    ).write_artifacts(output_dir)

    transforms = {
        row["target_transform_id"]: row
        for row in read_csv_rows(output_dir / "transform_error_contrast.csv")
    }
    bias_rows = {
        row["bias_class"]: row
        for row in read_csv_rows(output_dir / "bias_classification_summary.csv")
    }

    assert transforms["status_quo_observed"]["finite_true_extirpated_target_count"] == "151"
    assert transforms["status_quo_observed"]["nonfinite_true_extirpated_count"] == "101"
    assert float(transforms["status_quo_observed"]["mean_absolute_error"]) == pytest.approx(
        7.642384105960265
    )
    assert transforms["goal013_support_floor"]["finite_true_extirpated_target_count"] == "252"
    assert transforms["goal013_support_floor"]["default_compatibility_class"] == "incompatible"
    assert transforms["all_extirpated_true_time"]["restores_goal010_ideal_truth"] == "true"
    assert transforms["all_extirpated_true_time"]["default_compatibility_class"] == "compatible"
    assert float(transforms["all_extirpated_true_time"]["mean_absolute_error"]) == pytest.approx(
        0.0
    )

    assert bias_rows["late_bias"]["classification"] == "dominant"
    assert bias_rows["late_bias"]["affected_site_count"] == "235"
    assert bias_rows["spatial_structure"]["classification"] == "dominant"
    assert bias_rows["spatial_structure"]["evidence_label"] == "west_band"
    assert bias_rows["detection_persistence_association"]["classification"] == "secondary"

    cli_output_dir = tmp_path / "target_time_error_anatomy_cli"
    completed = run(
        [
            executable,
            "scripts/audit_synth_small_target_time_errors.py",
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
            "--target-timing-residual-dir",
            str(residual_dir),
            "--output-dir",
            str(cli_output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Target-time error anatomy audit complete" in completed.stdout
    assert "Sites audited: 625" in completed.stdout
    assert "True extirpated sites: 252" in completed.stdout
    assert "Recommendation: response_observable_rule_screen_ready" in completed.stdout
    assert "Wrote 10 files" in completed.stdout
    assert {path.name for path in cli_output_dir.iterdir()} == ERROR_ANATOMY_FILES
