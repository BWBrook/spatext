from __future__ import annotations

from dataclasses import replace
from json import loads
from pathlib import Path

import numpy as np
import pytest

from spatext.synth.small import SynthSmallBaselineConfig, build_synth_small_baseline
from spatext.synth.small.baseline import (
    compute_allee_factor,
    hex_to_rgb,
    interpolate_hex,
    rgb_to_hex,
)


def test_synth_small_baseline_meets_acceptance_criteria() -> None:
    result = build_synth_small_baseline()

    assert result.domain.cell_count == 625
    assert result.suitability.shape == (25, 25)
    assert np.isfinite(result.suitability).all()
    assert float(np.min(result.suitability)) >= 0.0
    assert float(np.max(result.suitability)) <= 1.0

    assert result.carrying_capacity.shape == (25, 25)
    assert np.isfinite(result.carrying_capacity).all()
    assert float(np.min(result.carrying_capacity)) > 0.0

    assert result.diagnostics.converged
    assert result.diagnostics.steps < result.config.max_steps

    abundance = result.equilibrium_abundance
    assert abundance.shape == (25, 25)
    assert np.isfinite(abundance).all()
    assert (abundance >= 0.0).all()
    assert float(np.std(abundance)) > 1.0
    assert float(np.mean(abundance)) > 5.0
    assert float(np.max(abundance)) < float(np.max(result.carrying_capacity))

    occupancy = result.occupancy
    assert occupancy.any()
    assert (~occupancy).any()


def test_synth_small_baseline_is_reproducible() -> None:
    first = build_synth_small_baseline()
    second = build_synth_small_baseline()

    np.testing.assert_allclose(first.suitability, second.suitability)
    np.testing.assert_allclose(first.carrying_capacity, second.carrying_capacity)
    np.testing.assert_allclose(first.equilibrium_abundance, second.equilibrium_abundance)
    np.testing.assert_array_equal(first.occupancy, second.occupancy)
    assert first.diagnostics == second.diagnostics
    assert first.config == second.config


def test_synth_small_baseline_artifacts_are_emitted(tmp_path: Path) -> None:
    result = build_synth_small_baseline()
    output_dir = tmp_path / "synth-small"

    written_paths = result.write_artifacts(output_dir)

    expected_names = {
        "domain.json",
        "config.json",
        "diagnostics.json",
        "summary.json",
        "cells.csv",
        "edges.csv",
        "surfaces.npz",
        "suitability.svg",
        "carrying_capacity.svg",
        "equilibrium_abundance.svg",
        "equilibrium_occupancy.svg",
    }
    assert {path.name for path in written_paths} == expected_names
    for path in written_paths:
        assert path.exists()
        assert path.stat().st_size > 0

    domain = loads((output_dir / "domain.json").read_text(encoding="utf-8"))
    diagnostics = loads((output_dir / "diagnostics.json").read_text(encoding="utf-8"))
    summary = loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert domain["cell_count"] == 625
    assert diagnostics["converged"] is True
    assert summary["summary"]["occupancy_fraction"] > 0.0

    surfaces = np.load(output_dir / "surfaces.npz")
    assert surfaces["suitability"].shape == (25, 25)
    assert surfaces["carrying_capacity"].shape == (25, 25)
    assert surfaces["equilibrium_abundance"].shape == (25, 25)
    assert surfaces["occupancy"].shape == (25, 25)


def test_synth_small_baseline_fails_clearly_when_equilibrium_not_reached() -> None:
    config = replace(SynthSmallBaselineConfig(), max_steps=1)

    with pytest.raises(RuntimeError, match="failed to converge"):
        build_synth_small_baseline(config)


def test_synth_small_baseline_can_report_nonconvergence_without_raising() -> None:
    config = replace(SynthSmallBaselineConfig(), max_steps=1, raise_on_nonconvergence=False)

    result = build_synth_small_baseline(config)

    assert result.diagnostics.converged is False
    assert result.diagnostics.steps == 1


def test_helper_utilities_cover_allee_and_color_conversions() -> None:
    abundance = np.array([[2.0, 4.0]], dtype=np.float64)
    allee = compute_allee_factor(abundance, 3.0)
    assert np.all(allee > 0.0)
    assert np.all(allee < 1.0)

    assert hex_to_rgb("#0f766e") == (15, 118, 110)
    assert rgb_to_hex((15, 118, 110)) == "#0f766e"
    assert interpolate_hex("#000000", "#ffffff", 0.5) == "#808080"

    with pytest.raises(ValueError, match="expected 6 hex characters"):
        hex_to_rgb("#fff")
