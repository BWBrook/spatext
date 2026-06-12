from __future__ import annotations

from csv import DictReader, DictWriter
from json import loads
from math import sqrt
from pathlib import Path
from subprocess import run
from sys import executable

import pytest

from spatext.synth.small import (
    build_synth_small_compatibility_screen,
    build_synth_small_extirpation_reconstruction,
    build_synth_small_observations,
    build_synth_small_summary_vector,
    default_compatibility_candidates,
)

COMPATIBILITY_SCREEN_FILES = {
    "compatibility_screen_config.json",
    "target_summary.json",
    "candidate_summaries.csv",
    "candidate_scores.csv",
    "coverage_score_breakdown.csv",
    "mode_rankings.csv",
    "verification.json",
    "report.md",
}
TARGET_MODES = {"ideal_true", "realistic_observed"}
CANDIDATE_LABELS = {"weaker_predation", "default", "stronger_predation"}
SCORE_COMPONENTS = {
    "finite_target_fraction",
    "lag_mean",
    "lag_std",
    "arrival_target_r2",
    "front_plane_gradient_magnitude",
    "coverage_curve_rmse",
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def write_csv_rows(path: Path, rows: tuple[dict[str, str], ...]) -> None:
    assert rows
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv_writer = DictWriter(handle, fieldnames=list(rows[0]))
        csv_writer.writeheader()
        csv_writer.writerows(rows)


def build_target_bundle(tmp_path: Path) -> Path:
    observation_dir = tmp_path / "observations"
    build_synth_small_observations().write_artifacts(observation_dir)

    reconstruction_dir = tmp_path / "reconstruction"
    build_synth_small_extirpation_reconstruction(observation_dir).write_artifacts(
        reconstruction_dir
    )

    target_dir = tmp_path / "summary_vector"
    build_synth_small_summary_vector(
        reconstruction_dir=reconstruction_dir,
        observation_dir=observation_dir,
    ).write_artifacts(target_dir)
    return target_dir


def ranking_map(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["target_mode"], row["candidate_label"]): row for row in read_csv_rows(path)}


def score_map(path: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    return {
        (row["target_mode"], row["candidate_label"], row["component"]): row
        for row in read_csv_rows(path)
    }


def test_default_compatibility_candidates_are_tiny_and_explicit() -> None:
    candidates = default_compatibility_candidates()

    assert tuple(candidate.label for candidate in candidates) == (
        "weaker_predation",
        "default",
        "stronger_predation",
    )
    assert len(candidates) == 3
    assert sum(candidate.is_default for candidate in candidates) == 1
    assert {
        (
            candidate.label,
            candidate.predation_scale,
            candidate.half_saturation,
            candidate.ramp_duration,
        )
        for candidate in candidates
    } == {
        ("weaker_predation", 0.75, 6.0, 8),
        ("default", 1.0, 6.0, 8),
        ("stronger_predation", 1.25, 6.0, 8),
    }


def test_compatibility_screen_writes_ranked_synthetic_bundle(tmp_path: Path) -> None:
    target_dir = build_target_bundle(tmp_path)

    result = build_synth_small_compatibility_screen(target_dir=target_dir)
    output_dir = tmp_path / "compatibility_screen"
    written = result.write_artifacts(output_dir)

    assert {path.name for path in written} == COMPATIBILITY_SCREEN_FILES

    config = loads((output_dir / "compatibility_screen_config.json").read_text(encoding="utf-8"))
    target_summary = loads((output_dir / "target_summary.json").read_text(encoding="utf-8"))
    verification = loads((output_dir / "verification.json").read_text(encoding="utf-8"))
    rankings = read_csv_rows(output_dir / "mode_rankings.csv")
    scores = read_csv_rows(output_dir / "candidate_scores.csv")
    coverage_breakdown = read_csv_rows(output_dir / "coverage_score_breakdown.csv")
    candidate_summaries = read_csv_rows(output_dir / "candidate_summaries.csv")

    assert config["synthetic_only"] is True
    assert config["not_formal_inference"] is True
    assert config["primary_target_mode"] == "realistic_observed"
    assert set(config["target_modes"]) == TARGET_MODES
    assert config["candidate_count"] == 3
    assert {candidate["label"] for candidate in config["candidates"]} == CANDIDATE_LABELS
    assert target_summary["synthetic_only"] is True
    assert set(target_summary["target_modes"]) == TARGET_MODES
    assert verification["passed"] is True

    assert len(rankings) == 6
    assert {row["target_mode"] for row in rankings} == TARGET_MODES
    assert {row["candidate_label"] for row in rankings} == CANDIDATE_LABELS
    assert {row["compatibility_class"] for row in rankings} <= {
        "compatible",
        "borderline",
        "incompatible",
        "invalid",
    }
    assert {
        row["candidate_label"] for row in rankings if row["is_primary_target_mode"] == "true"
    } == CANDIDATE_LABELS
    assert {row["component"] for row in scores} == SCORE_COMPONENTS
    assert len(coverage_breakdown) == 30
    assert {row["target_mode"] for row in coverage_breakdown} == TARGET_MODES
    assert {row["candidate_label"] for row in coverage_breakdown} == CANDIDATE_LABELS
    assert {row["coverage_fraction"] for row in coverage_breakdown} == {
        "0",
        "0.25",
        "0.5",
        "0.75",
        "1",
    }
    assert {row["candidate_label"] for row in candidate_summaries} == CANDIDATE_LABELS


def test_coverage_score_breakdown_reconstructs_rmse_rows(tmp_path: Path) -> None:
    target_dir = build_target_bundle(tmp_path)
    output_dir = tmp_path / "compatibility_screen"

    build_synth_small_compatibility_screen(target_dir=target_dir).write_artifacts(output_dir)
    scores = score_map(output_dir / "candidate_scores.csv")
    coverage_rows = read_csv_rows(output_dir / "coverage_score_breakdown.csv")

    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in coverage_rows:
        grouped.setdefault((row["target_mode"], row["candidate_label"]), []).append(row)

    assert set(grouped) == {
        (target_mode, candidate_label)
        for target_mode in TARGET_MODES
        for candidate_label in CANDIDATE_LABELS
    }

    for key, rows in grouped.items():
        score = scores[(*key, "coverage_curve_rmse")]
        assert len(rows) == 5
        assert {row["missing_reason"] for row in rows} == {""}
        rmse = sqrt(sum(float(row["squared_gap"]) for row in rows) / len(rows))
        assert float(score["absolute_gap"]) == pytest.approx(rmse)
        assert float(score["normalized_abs_gap"]) == pytest.approx(rmse / float(score["scale"]))
        assert float(score["weighted_gap"]) == pytest.approx(
            rmse * float(score["weight"]) / float(score["scale"])
        )

    default_ideal_rows = grouped[("ideal_true", "default")]
    assert {float(row["absolute_gap"]) for row in default_ideal_rows} == {0.0}
    assert {float(row["squared_gap"]) for row in default_ideal_rows} == {0.0}


def test_default_candidate_is_exact_or_near_exact_for_ideal_true(tmp_path: Path) -> None:
    target_dir = build_target_bundle(tmp_path)
    output_dir = tmp_path / "compatibility_screen"

    build_synth_small_compatibility_screen(target_dir=target_dir).write_artifacts(output_dir)
    rankings = ranking_map(output_dir / "mode_rankings.csv")

    default_row = rankings[("ideal_true", "default")]
    assert default_row["rank"] == "1"
    assert default_row["compatibility_class"] == "compatible"
    assert float(default_row["total_weighted_loss"]) == pytest.approx(0.0, abs=1e-9)
    assert default_row["invalid_reasons"] == ""


def test_missing_required_target_component_yields_invalid_reasons(tmp_path: Path) -> None:
    target_dir = build_target_bundle(tmp_path)
    component_path = target_dir / "summary_components.csv"
    component_rows = tuple(
        {
            **row,
            "value": "",
            "missing_reason": "test_removed_required_component",
        }
        if row["mode"] == "realistic_observed" and row["component"] == "lag_mean"
        else row
        for row in read_csv_rows(component_path)
    )
    write_csv_rows(component_path, component_rows)

    output_dir = tmp_path / "compatibility_screen"
    build_synth_small_compatibility_screen(target_dir=target_dir).write_artifacts(output_dir)
    rankings = read_csv_rows(output_dir / "mode_rankings.csv")

    realistic_rows = [row for row in rankings if row["target_mode"] == "realistic_observed"]
    ideal_rows = [row for row in rankings if row["target_mode"] == "ideal_true"]

    assert {row["compatibility_class"] for row in realistic_rows} == {"invalid"}
    assert all("target_missing:lag_mean" in row["invalid_reasons"] for row in realistic_rows)
    assert any(row["compatibility_class"] != "invalid" for row in ideal_rows)


def test_compatibility_screen_cli_writes_default_bundle(tmp_path: Path) -> None:
    target_dir = build_target_bundle(tmp_path)
    output_dir = tmp_path / "compatibility_screen"

    completed = run(
        [
            executable,
            "scripts/run_synth_small_compatibility_screen.py",
            "--target-dir",
            str(target_dir),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Compatibility screen complete" in completed.stdout
    assert "Primary target mode: realistic_observed" in completed.stdout

    rankings = read_csv_rows(output_dir / "mode_rankings.csv")
    assert len(rankings) == 6
    assert {row["candidate_label"] for row in rankings} == CANDIDATE_LABELS
