from __future__ import annotations

from csv import DictReader
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable

import pytest

from spatext.synth.medium import (
    SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_FILES,
    SYNTH_MEDIUM_SPREAD_IMPACT_VISUAL_FILES,
    SynthMediumSpreadImpactConfig,
    build_synth_medium_spread_impact_review_pack,
)

BOUNDARY_LABELS = {
    "synthetic_only": True,
    "synth_medium_landscape_source_verified": True,
    "spread_impact_review_only": True,
    "visual_review_required": True,
    "parameter_tuning_bounded": True,
    "no_observation_model": True,
    "no_reconstruction_or_inference": True,
    "no_abc_pom_likelihood_or_posterior": True,
    "no_real_data": True,
}


def read_csv_rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return tuple(DictReader(handle))


def assert_boundary_labels(payload: dict[str, object]) -> None:
    for key, value in BOUNDARY_LABELS.items():
        assert payload[key] is value


def test_spread_impact_writes_reconciled_review_bundle(tmp_path: Path) -> None:
    result = build_synth_medium_spread_impact_review_pack()
    output_dir = tmp_path / "spread_impact"

    written = result.write_artifacts(output_dir)

    expected_root = set(SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_FILES) | {"visuals"}
    assert {path.name for path in output_dir.iterdir()} == expected_root
    assert {path.name for path in written} == set(SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_FILES) | set(
        SYNTH_MEDIUM_SPREAD_IMPACT_VISUAL_FILES
    )

    config = loads((output_dir / "simulation_config.json").read_text("utf-8"))
    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    cell_rows = read_csv_rows(output_dir / "cell_truth.csv")
    candidate_rows = read_csv_rows(output_dir / "parameter_candidate_log.csv")
    source_rows = read_csv_rows(output_dir / "source_contribution_summary.csv")
    habitat_rows = read_csv_rows(output_dir / "habitat_class_timing_summary.csv")
    barrier_rows = read_csv_rows(output_dir / "corridor_barrier_effect_summary.csv")
    recoverability_rows = read_csv_rows(output_dir / "recoverability_proxy_summary.csv")
    time_rows = read_csv_rows(output_dir / "time_series_summary.csv")
    report = (output_dir / "report.md").read_text("utf-8")

    assert_boundary_labels(config)
    assert_boundary_labels(verification)
    assert verification["passed"] is True
    assert verification["recommendation_class"] == "ready_for_human_spread_impact_review"
    assert config["selected_parameter_set_id"] == "balanced_corridor_detour_v2"
    assert len(candidate_rows) == 5
    assert sum(row["selected_default"] == "true" for row in candidate_rows) == 1

    assert len(cell_rows) == 6048
    passable_rows = [row for row in cell_rows if row["passability"] == "passable"]
    water_rows = [row for row in cell_rows if row["passability"] == "water"]
    assert len(passable_rows) == 5225
    assert len(water_rows) == 823
    assert all(row["predator_arrival_time"] == "" for row in water_rows)
    assert all(row["predator_final_occupied"] == "false" for row in water_rows)
    assert all(row["prey_baseline_abundance"] == "" for row in water_rows)

    source_zone_rows = [row for row in passable_rows if row["source_zone_id"]]
    assert source_zone_rows
    assert all(
        float(row["predator_arrival_time"]) == pytest.approx(0.0) for row in source_zone_rows
    )

    colonized_rows = [row for row in passable_rows if row["predator_final_occupied"] == "true"]
    impacted_rows = [row for row in passable_rows if row["prey_extirpation_time"]]
    assert 0.70 <= len(colonized_rows) / len(passable_rows) <= 0.97
    assert 0.35 <= len(impacted_rows) / len(passable_rows) <= 0.85
    arrival_times = [float(row["predator_arrival_time"]) for row in colonized_rows]
    impact_lags = [float(row["arrival_to_extirpation_lag"]) for row in impacted_rows]
    assert max(arrival_times) - min(arrival_times) >= 70.0
    assert min(impact_lags) > 0.0
    assert max(impact_lags) - min(impact_lags) >= 8.0

    material_sources = [
        row
        for row in source_rows
        if row["row_role"] == "source_contribution"
        and float(row["source_contribution_fraction_of_colonized_passable"]) >= 0.10
    ]
    assert len(material_sources) >= 2
    assert all(row["is_material_source"] == "true" for row in material_sources)

    source_contribution_rows = [
        row for row in source_rows if row["row_role"] == "source_contribution"
    ]
    assert sum(
        int(row["source_contributed_colonized_passable_count"]) for row in source_contribution_rows
    ) == len(colonized_rows)
    assert sum(
        float(row["source_contribution_fraction_of_colonized_passable"])
        for row in source_contribution_rows
    ) == pytest.approx(1.0)
    assert {row["source_contribution_denominator"] for row in source_contribution_rows} == {
        "final_colonized_passable_count"
    }

    uncolonized_rows = [
        row for row in source_rows if row["row_role"] == "uncolonized_passable_accounting"
    ]
    assert len(uncolonized_rows) == 1
    uncolonized_row = uncolonized_rows[0]
    assert uncolonized_row["source_zone_id"] == "uncolonized_passable"
    assert uncolonized_row["source_contributed_colonized_passable_count"] == ""
    assert uncolonized_row["source_contribution_fraction_of_colonized_passable"] == ""
    assert int(uncolonized_row["uncolonized_passable_count"]) == len(passable_rows) - len(
        colonized_rows
    )
    assert float(uncolonized_row["uncolonized_passable_fraction_of_all_passable"]) == pytest.approx(
        (len(passable_rows) - len(colonized_rows)) / len(passable_rows)
    )
    assert uncolonized_row["uncolonized_fraction_denominator"] == "all_passable_count"

    conductance = {row["habitat_class"]: float(row["mean_conductance"]) for row in habitat_rows}
    assert conductance["source_zone"] > conductance["low_quality_matrix"]
    assert conductance["corridor"] > conductance["low_quality_matrix"]
    assert conductance["high_quality_patch"] > conductance["low_quality_matrix"]

    barrier_map = {row["effect_group"]: row for row in barrier_rows}
    assert float(barrier_map["corridor"]["mean_predator_arrival_time"]) < float(
        barrier_map["low_quality_matrix"]["mean_predator_arrival_time"]
    )
    assert float(
        barrier_map["water_adjacent_low_quality_matrix"]["mean_arrival_detour_index"]
    ) > float(barrier_map["non_water_adjacent_low_quality_matrix"]["mean_arrival_detour_index"])

    proxies = {row["proxy_id"]: row for row in recoverability_rows}
    assert proxies["finite_predator_arrival_count"]["passes"] == "true"
    assert proxies["finite_prey_extirpation_count"]["passes"] == "true"
    assert "arrival_time_iqr" not in proxies
    assert "impact_lag_iqr" not in proxies
    assert proxies["arrival_time_range"]["passes"] == "true"
    assert proxies["impact_lag_range"]["passes"] == "true"
    assert proxies["material_source_count"]["observed_value"] == str(len(material_sources))

    final_time = max(float(row["time"]) for row in time_rows)
    final_summary = next(row for row in time_rows if float(row["time"]) == final_time)
    assert int(final_summary["predator_occupied_passable_count"]) == len(colonized_rows)
    assert int(final_summary["prey_extirpated_passable_count"]) == len(impacted_rows)

    for visual_name in SYNTH_MEDIUM_SPREAD_IMPACT_VISUAL_FILES:
        visual_path = output_dir / "visuals" / visual_name
        assert visual_path.exists()
        assert visual_path.stat().st_size > 1000
        assert visual_path.read_text("utf-8").lstrip().startswith("<svg")
        assert f"visuals/{visual_name}" in report


def test_spread_impact_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    build_synth_medium_spread_impact_review_pack().write_artifacts(first_dir)
    build_synth_medium_spread_impact_review_pack().write_artifacts(second_dir)

    relative_files = tuple(SYNTH_MEDIUM_SPREAD_IMPACT_OUTPUT_FILES) + tuple(
        f"visuals/{name}" for name in SYNTH_MEDIUM_SPREAD_IMPACT_VISUAL_FILES
    )
    for relative_file in relative_files:
        assert (first_dir / relative_file).read_text("utf-8") == (
            second_dir / relative_file
        ).read_text("utf-8")


def test_spread_impact_verification_exposes_review_gates(tmp_path: Path) -> None:
    output_dir = tmp_path / "spread_impact"
    build_synth_medium_spread_impact_review_pack().write_artifacts(output_dir)

    verification = loads((output_dir / "verification.json").read_text("utf-8"))
    checks = {check["name"]: check for check in verification["checks"]}

    expected_checks = {
        "artifact_contract",
        "landscape_reconciliation",
        "water_never_colonized",
        "source_zone_seeding",
        "bounded_candidate_tuning",
        "spread_not_trivial_or_instant",
        "broad_arrival_distribution",
        "informative_prey_impact",
        "nonzero_lag_distribution",
        "multiple_material_sources",
        "habitat_conductance_gradient",
        "barrier_detour_signal",
        "recoverability_proxy_readiness",
    }
    assert expected_checks <= set(checks)
    assert all(checks[name]["passed"] is True for name in expected_checks)


def test_spread_impact_cli(tmp_path: Path) -> None:
    output_dir = tmp_path / "spread_impact"
    completed = run(
        [
            executable,
            "scripts/simulate_synth_medium_spread_impact.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Synth-medium spread-impact review pack complete" in completed.stdout
    assert "Selected parameter set: balanced_corridor_detour_v2" in completed.stdout
    assert "Recommendation: ready_for_human_spread_impact_review" in completed.stdout
    assert "Wrote 18 files" in completed.stdout
    assert (output_dir / "visuals" / "review_montage.svg").exists()


def test_spread_impact_rejects_unbounded_candidate_sets() -> None:
    candidates = tuple(f"candidate_{index}" for index in range(7))
    with pytest.raises(ValueError, match="bounded"):
        build_synth_medium_spread_impact_review_pack(
            SynthMediumSpreadImpactConfig(candidate_ids=candidates)
        )
