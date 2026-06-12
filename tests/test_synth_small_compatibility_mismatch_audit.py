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
    build_synth_small_observations,
    build_synth_small_summary_vector,
    evaluate_synth_small_response_screen,
)

MISMATCH_AUDIT_FILES = {
    "mismatch_audit_config.json",
    "target_delta_summary.csv",
    "score_contribution_summary.csv",
    "coverage_gap_summary.csv",
    "evaluation_bridge_summary.json",
    "recommendation.json",
    "verification.json",
    "report.md",
}
NON_INFERENCE_LABELS = {
    "synthetic_only": True,
    "audit_only": True,
    "not_formal_inference": True,
    "no_scoring_change": True,
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def build_audit_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
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

    return summary_dir, compatibility_dir, evaluation_dir


def assert_non_inference_labels(payload: dict[str, object]) -> None:
    for key, value in NON_INFERENCE_LABELS.items():
        assert payload[key] is value


def test_mismatch_audit_writes_disk_first_bundle(tmp_path: Path) -> None:
    summary_dir, compatibility_dir, evaluation_dir = build_audit_inputs(tmp_path)

    result = build_synth_small_compatibility_mismatch_audit(
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        evaluation_dir=evaluation_dir,
    )
    output_dir = tmp_path / "mismatch_audit"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == MISMATCH_AUDIT_FILES

    config = loads((output_dir / "mismatch_audit_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))
    target_deltas = read_csv_rows(output_dir / "target_delta_summary.csv")
    score_contributions = read_csv_rows(output_dir / "score_contribution_summary.csv")
    coverage_gaps = read_csv_rows(output_dir / "coverage_gap_summary.csv")

    assert_non_inference_labels(config)
    assert_non_inference_labels(verification)
    assert_non_inference_labels(recommendation)
    assert config["top_target_mode"] == "realistic_observed"
    assert config["top_candidate_label"] == "default"
    assert verification["passed"] is True

    delta_by_metric = {row["metric"]: row for row in target_deltas}
    assert delta_by_metric["finite_target_count"]["ideal_true_value"] == "252"
    assert delta_by_metric["finite_target_count"]["realistic_observed_value"] == "151"
    assert delta_by_metric["finite_target_count"]["delta"] == "-101"
    assert delta_by_metric["coverage_target_time:0.75"]["delta"] == "-7.25"

    assert [row["component"] for row in score_contributions[:3]] == [
        "finite_target_fraction",
        "arrival_target_r2",
        "coverage_curve_rmse",
    ]
    assert float(score_contributions[0]["weighted_gap"]) == pytest.approx(1.2928)
    assert float(score_contributions[0]["loss_share"]) == pytest.approx(0.36699785866219)

    assert len(coverage_gaps) == 5
    coverage_zero = next(row for row in coverage_gaps if row["coverage_fraction"] == "0")
    assert coverage_zero["target_time"] == "4"
    assert coverage_zero["candidate_time"] == "15"
    assert coverage_zero["signed_gap"] == "11"
    rmse = float(coverage_zero["rmse"])
    squared_gap_sum = sum(float(row["squared_gap"]) for row in coverage_gaps)
    assert rmse == pytest.approx((squared_gap_sum / len(coverage_gaps)) ** 0.5)


def test_bridge_links_finite_target_drop_to_false_negatives(tmp_path: Path) -> None:
    summary_dir, compatibility_dir, evaluation_dir = build_audit_inputs(tmp_path)
    output_dir = tmp_path / "mismatch_audit"

    build_synth_small_compatibility_mismatch_audit(
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        evaluation_dir=evaluation_dir,
    ).write_artifacts(output_dir)

    bridge = loads((output_dir / "evaluation_bridge_summary.json").read_text("utf-8"))

    assert_non_inference_labels(bridge)
    assert bridge["ideal_true_finite_target_count"] == 252
    assert bridge["realistic_observed_finite_target_count"] == 151
    assert bridge["finite_target_drop"] == 101
    assert bridge["false_negative_count"] == 101
    assert bridge["false_negative_bridge_difference"] == 0
    assert bridge["false_negative_bridge_fraction"] == pytest.approx(1.0)
    assert bridge["bridge_class"] == "finite_target_drop_matches_false_negatives"
    assert bridge["confusion_matrix"] == {"tp": 151, "fp": 0, "tn": 373, "fn": 101}


def test_recommendation_is_diagnostic_not_inference(tmp_path: Path) -> None:
    summary_dir, compatibility_dir, evaluation_dir = build_audit_inputs(tmp_path)
    output_dir = tmp_path / "mismatch_audit"

    build_synth_small_compatibility_mismatch_audit(
        summary_vector_dir=summary_dir,
        compatibility_screen_dir=compatibility_dir,
        evaluation_dir=evaluation_dir,
    ).write_artifacts(output_dir)

    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))

    assert recommendation["recommendation_class"] == (
        "diagnose_observation_reconstruction_before_abc"
    )
    assert recommendation["ideal_default_class"] == "compatible"
    assert recommendation["all_realistic_candidates_incompatible"] is True
    assert recommendation["dominant_mismatch_components"][:3] == [
        "finite_target_fraction",
        "arrival_target_r2",
        "coverage_curve_rmse",
    ]
    assert "not an ABC" in " ".join(recommendation["rationale"])


def test_mismatch_audit_cli_writes_default_bundle(tmp_path: Path) -> None:
    summary_dir, compatibility_dir, evaluation_dir = build_audit_inputs(tmp_path)
    output_dir = tmp_path / "mismatch_audit"

    completed = run(
        [
            executable,
            "scripts/audit_synth_small_compatibility_mismatch.py",
            "--summary-vector-dir",
            str(summary_dir),
            "--compatibility-screen-dir",
            str(compatibility_dir),
            "--evaluation-dir",
            str(evaluation_dir),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Compatibility mismatch audit complete" in completed.stdout
    assert "Recommendation: diagnose_observation_reconstruction_before_abc" in completed.stdout
    assert "Finite-target drop: 101" in completed.stdout
    assert "False negatives: 101" in completed.stdout
    assert "Wrote 8 files" in completed.stdout
    assert {path.name for path in output_dir.iterdir()} == MISMATCH_AUDIT_FILES
