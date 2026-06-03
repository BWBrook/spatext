from __future__ import annotations

from json import loads
from pathlib import Path

import numpy as np

from spatext.synth.small import (
    ReadinessCriteria,
    SensitivityCandidate,
    build_synth_small_predator_truth,
    default_sensitivity_candidates,
    run_predator_truth_sensitivity,
)
from spatext.synth.small.sensitivity import (
    classify_readiness,
    extract_metrics,
    render_decision_memo,
)


def test_default_sensitivity_candidates_include_one_default() -> None:
    candidates = default_sensitivity_candidates()

    assert len(candidates) == 27
    defaults = [candidate for candidate in candidates if candidate.is_default]
    assert defaults == [
        SensitivityCandidate(
            label="default",
            predation_scale=1.0,
            half_saturation=6.0,
            ramp_duration=8,
            is_default=True,
        )
    ]


def test_extract_metrics_matches_current_default_truth() -> None:
    result = build_synth_small_predator_truth()

    metrics = extract_metrics(result)

    assert metrics["verification_passed"] is True
    assert metrics["extirpated_fraction"] == 252 / 625
    assert metrics["surviving_fraction"] == 373 / 625
    assert metrics["lag_min"] == 11.0
    assert metrics["lag_max"] == 41.0
    assert metrics["low_initial_extirpation_rate"] > metrics["high_initial_extirpation_rate"]
    assert metrics["west_band_extirpated_count"] > metrics["east_band_extirpated_count"]
    assert metrics["used_nonnegative_clipping"] is False


def test_classify_readiness_uses_criteria_count() -> None:
    criteria = ReadinessCriteria(required_pass_count_for_review=4)

    assert (
        classify_readiness(
            criterion_verification=True,
            criteria_passed=6,
            total_criteria=6,
            criteria=criteria,
        )
        == "observation_ready"
    )
    assert (
        classify_readiness(
            criterion_verification=True,
            criteria_passed=4,
            total_criteria=6,
            criteria=criteria,
        )
        == "review"
    )
    assert (
        classify_readiness(
            criterion_verification=False,
            criteria_passed=6,
            total_criteria=6,
            criteria=criteria,
        )
        == "not_ready"
    )


def test_sensitivity_run_writes_expected_outputs_for_small_candidate_set(tmp_path: Path) -> None:
    candidates = (
        SensitivityCandidate("low", 0.75, 6.0, 8),
        SensitivityCandidate("default", 1.0, 6.0, 8, is_default=True),
        SensitivityCandidate("high", 1.25, 6.0, 8),
    )
    output_dir = tmp_path / "sensitivity"

    result = run_predator_truth_sensitivity(output_dir, candidates=candidates)

    assert result.output_dir == output_dir
    assert len(result.rows) == 3
    assert result.default_row.label == "default"
    assert result.default_row.readiness_classification == "observation_ready"
    assert result.best_row in result.rankings
    for path in (
        result.sweep_results_path,
        result.candidate_rankings_path,
        result.readiness_path,
        result.decision_memo_path,
    ):
        assert path.exists()
        assert path.stat().st_size > 0

    readiness = loads(result.readiness_path.read_text(encoding="utf-8"))
    assert readiness["candidate_count"] == 3
    assert readiness["default_candidate"]["label"] == "default"
    assert readiness["default_candidate"]["readiness_classification"] == "observation_ready"
    assert "recommendation" in readiness


def test_decision_memo_mentions_default_and_best_candidate(tmp_path: Path) -> None:
    result = run_predator_truth_sensitivity(
        tmp_path / "sensitivity",
        candidates=(
            SensitivityCandidate("default", 1.0, 6.0, 8, is_default=True),
            SensitivityCandidate("nearby", 1.0, 4.0, 8),
        ),
    )

    memo = render_decision_memo(
        result.rows,
        result.rankings,
        result.default_row,
        result.best_row,
        ReadinessCriteria(),
    )

    assert "Default classification" in memo
    assert result.default_row.readiness_classification in memo
    assert result.best_row.label in memo
    assert "Scientific Limits" in memo


def test_sensitivity_scores_are_finite_for_default_grid(tmp_path: Path) -> None:
    result = run_predator_truth_sensitivity(
        candidates=default_sensitivity_candidates(),
        output_dir=tmp_path / "full-grid",
    )

    assert all(np.isfinite(row.readiness_score) for row in result.rows)
    assert result.default_row.readiness_classification == "observation_ready"
