from __future__ import annotations

from dataclasses import replace
from json import loads
from pathlib import Path

import numpy as np
import pytest

from spatext.synth.small import (
    SynthSmallPredatorTruthConfig,
    build_synth_small_predator_truth,
)


def test_synth_small_predator_truth_meets_acceptance_criteria() -> None:
    result = build_synth_small_predator_truth()

    assert result.domain.cell_count == 625
    assert result.driver_arrival.shape == (25, 25)
    assert np.isfinite(result.driver_arrival).all()
    assert int(np.min(result.driver_arrival)) >= result.config.arrival.introduction_time
    assert int(np.max(result.driver_arrival)) > int(np.min(result.driver_arrival))
    np.testing.assert_array_equal(
        result.driver_arrival[:, 0],
        np.full(result.domain.rows, result.config.arrival.introduction_time, dtype=np.int64),
    )

    assert result.predator_pressure.shape[1:] == (25, 25)
    assert np.isfinite(result.predator_pressure).all()
    assert float(np.min(result.predator_pressure)) >= 0.0
    assert float(np.max(result.predator_pressure)) <= result.config.pressure.pressure_scale

    assert result.prey_abundance.shape == result.predator_pressure.shape
    assert np.isfinite(result.prey_abundance).all()
    assert float(np.min(result.prey_abundance)) >= 0.0

    assert result.true_extirpation.shape == (25, 25)
    finite_true_extirpation = result.true_extirpation[np.isfinite(result.true_extirpation)]
    assert finite_true_extirpation.size > 0
    assert finite_true_extirpation.size < result.domain.cell_count

    finite_lag = result.extirpation_lag[np.isfinite(result.extirpation_lag)]
    assert finite_lag.size == finite_true_extirpation.size
    assert float(np.min(finite_lag)) >= 0.0
    assert float(np.std(finite_lag)) > 0.0

    extirpated_fraction = finite_true_extirpation.size / result.domain.cell_count
    assert 0.05 < extirpated_fraction < 0.95

    initial_quartiles = np.quantile(result.initial_abundance, [0.25, 0.75])
    low_initial_mask = result.initial_abundance <= initial_quartiles[0]
    high_initial_mask = result.initial_abundance >= initial_quartiles[1]
    low_initial_extirpation_rate = float(
        np.mean(np.isfinite(result.true_extirpation[low_initial_mask]))
    )
    high_initial_extirpation_rate = float(
        np.mean(np.isfinite(result.true_extirpation[high_initial_mask]))
    )
    assert low_initial_extirpation_rate > high_initial_extirpation_rate


def test_synth_small_predator_truth_is_reproducible() -> None:
    first = build_synth_small_predator_truth()
    second = build_synth_small_predator_truth()

    np.testing.assert_array_equal(first.driver_arrival, second.driver_arrival)
    np.testing.assert_allclose(first.predator_pressure, second.predator_pressure)
    np.testing.assert_allclose(first.prey_abundance, second.prey_abundance)
    np.testing.assert_allclose(first.true_extirpation, second.true_extirpation, equal_nan=True)
    np.testing.assert_allclose(first.extirpation_lag, second.extirpation_lag, equal_nan=True)
    np.testing.assert_allclose(first.final_abundance, second.final_abundance)
    assert first.diagnostics == second.diagnostics
    assert first.config == second.config


def test_synth_small_predator_truth_artifacts_are_emitted(tmp_path: Path) -> None:
    result = build_synth_small_predator_truth()
    output_dir = tmp_path / "synth-small-predator"

    written_paths = result.write_artifacts(output_dir)

    expected_names = {
        "domain.json",
        "baseline_config.json",
        "predator_config.json",
        "diagnostics.json",
        "summary.json",
        "cells.csv",
        "surfaces.npz",
        "trajectories.npz",
        "suitability.svg",
        "initial_abundance.svg",
        "driver_arrival.svg",
        "true_extirpation.svg",
        "extirpation_lag.svg",
        "final_abundance.svg",
    }
    assert {path.name for path in written_paths} == expected_names
    for path in written_paths:
        assert path.exists()
        assert path.stat().st_size > 0

    summary_payload = loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    diagnostics_payload = loads((output_dir / "diagnostics.json").read_text(encoding="utf-8"))
    surfaces = np.load(output_dir / "surfaces.npz")
    trajectories = np.load(output_dir / "trajectories.npz")
    try:
        assert diagnostics_payload["predation_response_form"] == "type_ii"
        assert diagnostics_payload["extirpation_threshold_form"] == "absolute_quasi_extinction"
        assert diagnostics_payload["stayed_finite"] is True
        assert diagnostics_payload["stayed_nonnegative"] is True

        extirpated_count = int(np.sum(np.isfinite(surfaces["true_extirpation"])))
        assert summary_payload["summary"]["extirpated_count"] == extirpated_count
        assert (
            summary_payload["summary"]["surviving_count"]
            == result.domain.cell_count - extirpated_count
        )

        np.testing.assert_allclose(surfaces["initial_abundance"], result.initial_abundance)
        np.testing.assert_array_equal(surfaces["driver_arrival"], result.driver_arrival)
        np.testing.assert_allclose(
            surfaces["extirpation_threshold"],
            result.extirpation_threshold,
        )
        np.testing.assert_allclose(
            surfaces["true_extirpation"],
            result.true_extirpation,
            equal_nan=True,
        )
        np.testing.assert_allclose(
            surfaces["extirpation_lag"],
            result.extirpation_lag,
            equal_nan=True,
        )
        np.testing.assert_allclose(surfaces["final_abundance"], result.final_abundance)

        np.testing.assert_allclose(trajectories["prey_abundance"], result.prey_abundance)
        np.testing.assert_allclose(trajectories["predator_pressure"], result.predator_pressure)
    finally:
        surfaces.close()
        trajectories.close()

    initial_svg = (output_dir / "initial_abundance.svg").read_text(encoding="utf-8")
    final_svg = (output_dir / "final_abundance.svg").read_text(encoding="utf-8")
    arrival_svg = (output_dir / "driver_arrival.svg").read_text(encoding="utf-8")
    extirpation_svg = (output_dir / "true_extirpation.svg").read_text(encoding="utf-8")

    abundance_min = float(np.min(result.final_abundance))
    abundance_max = float(np.max(result.initial_abundance))
    assert f"scale min={abundance_min:.3f} max={abundance_max:.3f}" in initial_svg
    assert f"scale min={abundance_min:.3f} max={abundance_max:.3f}" in final_svg
    assert "Color scale" in initial_svg
    assert "Color scale" in final_svg

    time_min = float(np.min(result.driver_arrival))
    time_max = float(np.nanmax(result.true_extirpation))
    assert f"scale min={time_min:.3f} max={time_max:.3f}" in arrival_svg
    assert f"scale min={time_min:.3f} max={time_max:.3f}" in extirpation_svg
    assert "Missing" in extirpation_svg


def test_true_extirpation_and_lag_use_missing_or_finite_values() -> None:
    result = build_synth_small_predator_truth()

    extirpated = np.isfinite(result.true_extirpation)
    surviving = ~extirpated

    assert np.isfinite(result.extirpation_lag[extirpated]).all()
    assert np.isnan(result.extirpation_lag[surviving]).all()
    np.testing.assert_allclose(
        result.extirpation_lag[extirpated],
        result.true_extirpation[extirpated] - result.driver_arrival.astype(np.float64)[extirpated],
    )


def test_extirpation_threshold_is_positive_and_spatially_constant() -> None:
    result = build_synth_small_predator_truth()

    assert np.isfinite(result.extirpation_threshold).all()
    np.testing.assert_allclose(
        result.extirpation_threshold,
        np.full(
            (result.domain.rows, result.domain.cols),
            result.config.extirpation.quasi_extirpation_abundance,
        ),
    )


def test_invalid_predator_truth_configuration_fails_clearly() -> None:
    invalid_config = replace(
        SynthSmallPredatorTruthConfig(),
        arrival=replace(
            SynthSmallPredatorTruthConfig().arrival,
            front_speed_cells_per_step=0.0,
        ),
    )

    with pytest.raises(ValueError, match="front_speed_cells_per_step must be positive"):
        build_synth_small_predator_truth(invalid_config)
