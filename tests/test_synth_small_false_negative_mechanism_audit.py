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
    build_synth_small_observations,
    build_synth_small_summary_vector,
    evaluate_synth_small_response_screen,
)

FALSE_NEGATIVE_AUDIT_FILES = {
    "false_negative_audit_config.json",
    "false_negative_site_audit.csv",
    "mechanism_summary.csv",
    "group_mechanism_summary.csv",
    "observation_timing_summary.csv",
    "recommendation.json",
    "verification.json",
    "report.md",
}
NON_INFERENCE_LABELS = {
    "synthetic_only": True,
    "audit_only": True,
    "evaluation_only": True,
    "not_formal_inference": True,
    "no_reconstruction_change": True,
    "no_observation_design_change": True,
    "no_scoring_change": True,
}
EXPECTED_MECHANISM_COUNTS = {
    "no_post_extirpation_surveys": 39,
    "late_extirpation_near_survey_horizon": 30,
    "post_extirpation_detection_blocks_absence": 28,
    "insufficient_post_extirpation_survey_history": 4,
}
SITE_EFFORT_COLUMNS = {
    "mean_effort",
    "min_effort",
    "max_effort",
    "post_extirpation_mean_effort",
}
TIMING_EFFORT_COLUMNS = {
    "mean_effort",
    "mean_min_effort",
    "mean_max_effort",
    "mean_post_extirpation_mean_effort",
    "low_mean_effort_count",
    "low_min_effort_count",
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def build_false_negative_audit_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
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

    return observation_dir, reconstruction_dir, evaluation_dir, mismatch_dir


def assert_non_inference_labels(payload: dict[str, object]) -> None:
    for key, value in NON_INFERENCE_LABELS.items():
        assert payload[key] is value


def test_false_negative_audit_writes_reconciled_bundle(tmp_path: Path) -> None:
    observation_dir, reconstruction_dir, evaluation_dir, mismatch_dir = (
        build_false_negative_audit_inputs(tmp_path)
    )

    result = build_synth_small_false_negative_mechanism_audit(
        evaluation_dir=evaluation_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
        mismatch_audit_dir=mismatch_dir,
    )
    output_dir = tmp_path / "false_negative_audit"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == FALSE_NEGATIVE_AUDIT_FILES

    config = loads((output_dir / "false_negative_audit_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))
    sites = read_csv_rows(output_dir / "false_negative_site_audit.csv")
    mechanisms = read_csv_rows(output_dir / "mechanism_summary.csv")
    groups = read_csv_rows(output_dir / "group_mechanism_summary.csv")
    timing = read_csv_rows(output_dir / "observation_timing_summary.csv")

    assert_non_inference_labels(config)
    assert_non_inference_labels(verification)
    assert_non_inference_labels(recommendation)
    assert verification["passed"] is True
    assert config["false_negative_count"] == 101
    assert config["thresholds"]["low_mean_effort_max"] == 0.9
    assert config["thresholds"]["low_min_effort_max"] == 0.65

    assert len(sites) == 101
    assert len({row["site_id"] for row in sites}) == 101
    assert set(sites[0]) >= SITE_EFFORT_COLUMNS
    assert Counter(row["primary_mechanism"] for row in sites) == EXPECTED_MECHANISM_COUNTS
    assert all(row["primary_mechanism"] for row in sites)
    assert all(row["mean_effort"] for row in sites)
    assert all(row["min_effort"] for row in sites)
    assert all(row["max_effort"] for row in sites)

    mechanism_counts = {
        row["primary_mechanism"]: int(row["false_negative_count"]) for row in mechanisms
    }
    assert mechanism_counts == EXPECTED_MECHANISM_COUNTS
    assert sum(mechanism_counts.values()) == 101

    group_counts = {
        (row["group_type"], row["group"], row["primary_mechanism"]): int(
            row["false_negative_count"]
        )
        for row in groups
    }
    assert group_counts[("region", "east", "no_post_extirpation_surveys")] == 28
    assert group_counts[("front_band", "middle_band", "no_post_extirpation_surveys")] == 32

    overall = next(row for row in timing if row["summary_type"] == "overall")
    assert set(overall) >= TIMING_EFFORT_COLUMNS
    assert overall["false_negative_count"] == "101"
    assert overall["near_horizon_count"] == "78"
    assert overall["no_post_extirpation_survey_count"] == "39"
    assert overall["low_mean_effort_count"] == "1"
    assert overall["low_min_effort_count"] == "6"
    assert float(overall["mean_effort"]) == pytest.approx(1.0682292389839694)
    assert float(overall["mean_post_extirpation_mean_effort"]) == pytest.approx(1.1374860906258883)


def test_false_negative_site_timing_features_are_auditable(tmp_path: Path) -> None:
    observation_dir, reconstruction_dir, evaluation_dir, mismatch_dir = (
        build_false_negative_audit_inputs(tmp_path)
    )
    output_dir = tmp_path / "false_negative_audit"

    build_synth_small_false_negative_mechanism_audit(
        evaluation_dir=evaluation_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
        mismatch_audit_dir=mismatch_dir,
    ).write_artifacts(output_dir)

    sites = {
        row["site_id"]: row for row in read_csv_rows(output_dir / "false_negative_site_audit.csv")
    }

    post_detection = sites["site_005"]
    assert post_detection["primary_mechanism"] == "post_extirpation_detection_blocks_absence"
    assert post_detection["true_extirpation_time"] == "44"
    assert post_detection["last_detection_time"] == "52"
    assert post_detection["post_extirpation_survey_time_count"] == "2"
    assert post_detection["post_extirpation_detection_count"] == "1"
    assert float(post_detection["mean_effort"]) == pytest.approx(1.22746874887275)
    assert float(post_detection["min_effort"]) == pytest.approx(0.920078305373)
    assert float(post_detection["max_effort"]) == pytest.approx(1.4568029368)
    assert float(post_detection["post_extirpation_mean_effort"]) == pytest.approx(1.16086095237025)
    assert float(post_detection["last_detection_minus_true_extirpation"]) == pytest.approx(8.0)
    assert float(post_detection["first_post_survey_minus_true_extirpation"]) == pytest.approx(4.0)

    no_post = sites["site_014"]
    assert no_post["primary_mechanism"] == "no_post_extirpation_surveys"
    assert no_post["post_extirpation_survey_time_count"] == "0"
    assert no_post["first_post_extirpation_survey_time"] == ""
    assert float(no_post["mean_effort"]) == pytest.approx(1.0887438120322)
    assert no_post["post_extirpation_mean_effort"] == ""
    assert float(no_post["last_survey_minus_true_extirpation"]) == pytest.approx(-5.0)

    insufficient = sites["site_357"]
    assert insufficient["primary_mechanism"] == "insufficient_post_extirpation_survey_history"
    assert insufficient["post_extirpation_survey_time_count"] == "1"
    assert insufficient["post_extirpation_detection_count"] == "0"
    assert float(insufficient["post_extirpation_mean_effort"]) == pytest.approx(1.27387087915)
    assert float(insufficient["first_post_survey_minus_true_extirpation"]) == pytest.approx(15.0)


def test_recommendation_points_to_observation_gap_before_rule_change(
    tmp_path: Path,
) -> None:
    observation_dir, reconstruction_dir, evaluation_dir, mismatch_dir = (
        build_false_negative_audit_inputs(tmp_path)
    )
    output_dir = tmp_path / "false_negative_audit"

    build_synth_small_false_negative_mechanism_audit(
        evaluation_dir=evaluation_dir,
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
        mismatch_audit_dir=mismatch_dir,
    ).write_artifacts(output_dir)

    recommendation = loads((output_dir / "recommendation.json").read_text("utf-8"))

    assert recommendation["recommendation_class"] == (
        "diagnose_post_extirpation_observation_gap_before_rule_change"
    )
    assert recommendation["false_negative_count"] == 101
    assert recommendation["dominant_primary_mechanisms"][:3] == [
        "no_post_extirpation_surveys",
        "late_extirpation_near_survey_horizon",
        "post_extirpation_detection_blocks_absence",
    ]
    assert recommendation["strongest_region_signal"] == {
        "group": "east",
        "false_negative_count": 41,
    }
    assert "does not change reconstruction" in " ".join(recommendation["rationale"])


def test_false_negative_audit_cli_writes_default_bundle(tmp_path: Path) -> None:
    observation_dir, reconstruction_dir, evaluation_dir, mismatch_dir = (
        build_false_negative_audit_inputs(tmp_path)
    )
    output_dir = tmp_path / "false_negative_audit"

    completed = run(
        [
            executable,
            "scripts/audit_synth_small_false_negatives.py",
            "--evaluation-dir",
            str(evaluation_dir),
            "--reconstruction-dir",
            str(reconstruction_dir),
            "--observation-dir",
            str(observation_dir),
            "--mismatch-audit-dir",
            str(mismatch_dir),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "False-negative mechanism audit complete" in completed.stdout
    assert "False negatives audited: 101" in completed.stdout
    assert (
        "Recommendation: diagnose_post_extirpation_observation_gap_before_rule_change"
        in completed.stdout
    )
    assert "Dominant mechanism: no_post_extirpation_surveys (39)" in completed.stdout
    assert "Wrote 8 files" in completed.stdout
    assert {path.name for path in output_dir.iterdir()} == FALSE_NEGATIVE_AUDIT_FILES
