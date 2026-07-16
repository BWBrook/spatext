from __future__ import annotations

import inspect
import json
import math
import re
import subprocess
from collections.abc import Iterator
from dataclasses import FrozenInstanceError, asdict, fields, replace
from hashlib import sha256
from importlib import import_module
from itertools import product
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import numpy as np
import pytest

from spatext.observe import (
    EffectiveCountRates,
    poisson_log_probability,
    state_count_log_probability,
)

CORE_MODULE = "spatext.synth.medium.latent_response_observation_recovery"
CANONICAL_Q_MIN = -0.8125964200108078
CANONICAL_Q_MAX = 2.294433352026396
AMENDMENT_TEST_NAMES = (
    "test_lro_3a_001_scenario_registry_truth_access_scope_and_variants_are_literal",
    "test_lro_3a_002_truth_access_rejects_missing_extra_reordered_or_unknown",
    "test_lro_3a_003_stress_truth_cannot_enter_analyst_fit",
    "test_lro_3a_004_control_truth_cannot_enter_starts_objective_or_profiles",
    "test_lro_3a_005_fit_execution_schema_key_sort_and_failure_rows_are_literal",
    "test_lro_3a_006_fit_variant_is_in_every_fit_derived_primary_key",
    "test_lro_3a_007_arrival_emits_complete_correct_permuted_pairs",
    "test_lro_3a_008_arrival_primary_tables_use_permuted_only",
    "test_lro_3a_009_equal_shared_fits_have_no_fake_replicate_id",
    "test_lro_3a_010_equal_bootstrap_pairs_are_complete_and_recomputable",
    "test_lro_3a_011_every_primary_science_row_reconciles_to_one_fit_row",
    "test_lro_3l_001_event_censor_indices_and_126_label_are_literal",
    "test_lro_3l_002_one_hot_event_and_censor_score_zero",
    "test_lro_3l_003_one_category_displacement_scores_point_zero_five_six_six",
    "test_lro_3l_004_event_six_vs_censor_scores_one_one_twenty_one_twenty",
    "test_lro_3l_005_brier_and_expected_value_match_hand_calculation",
    "test_lro_3l_006_discrete_quantiles_use_first_crossing",
    "test_lro_3l_007_scaled_interval_expected_value_matches_21_path_enumeration",
    "test_lro_3l_008_odd_even_medians_and_bayes_risk_are_literal",
    "test_lro_3l_009_process_oracle_probabilities_precede_truth",
    "test_lro_3l_010_batched_and_scalar_weights_score_identically",
    "test_lro_3l_011_empty_histories_retain_process_paths_and_cells",
    "test_lro_3l_012_censored_truth_remains_in_every_denominator",
    "test_lro_3l_013_invalid_probability_or_truth_fails_complete_diagnostic",
    "test_lro_3l_014_applicability_and_frame_sizes_are_literal",
    "test_lro_3l_015_failed_fit_retains_three_diagnostic_unavailable_rows",
    "test_lro_3l_016_inapplicable_attempts_emit_three_not_applicable_rows",
    "test_lro_3l_017_metric_values_and_availability_never_change_recommendation",
    "test_lro_3l_018_missing_or_malformed_row_is_schema_failure_only",
    "test_lro_3l_019_no_latent_threshold_object_or_pass_count_exists",
    "test_lro_3l_020_valid_fit_with_failed_prerequisite_or_invalid_posterior_is_unavailable_diagnostic",
    "test_lro_3d_001_nested_denominators_imputations_and_even_median_are_literal",
    "test_lro_3d_002_nested_coverage_and_convergence_boundaries_are_unchanged",
    "test_lro_3d_003_missing_recovery_row_is_contract_failure_not_imputation",
    "test_lro_3d_004_sparse_coverage_and_width_use_all_24",
    "test_lro_3d_005_sparse_equal_width_passes_next_value_below_fails",
    "test_lro_3d_006_sparse_failed_fit_cannot_be_rescued_by_imputation",
    "test_lro_3d_007_sparse_low_error_or_24_coverage_adds_no_gate",
    "test_lro_3d_008_zero_driver_touching_zero_is_not_exclusion",
    "test_lro_3d_009_zero_driver_six_passes_seven_confounds",
    "test_lro_3d_010_zero_driver_failed_open_missing_are_undecidable",
    "test_lro_3d_011_known_truth_stress_recovery_is_descriptive_full_denominator",
    "test_lro_3d_012_continuous_abundance_has_no_parameter_truth_claim",
    "test_lro_3d_013_control_summary_denominators_reconcile_to_fit_evidence",
    "test_lro_3d_014_failed_predictive_fit_emits_27_unavailable_rows",
    "test_lro_3r_001_each_oracle_failure_maps_to_model_contract_failed",
    "test_lro_3r_002_dense_complete_scientific_failure_maps_to_confounding",
    "test_lro_3r_003_structured_recovery_only_failure_maps_to_observation_limited",
    "test_lro_3r_004_structured_coverage_predictive_fit_or_plugin_failure_is_rank_one",
    "test_lro_3r_005_structured_accepted_estimand_unidentified_is_rank_two",
    "test_lro_3r_006_sparse_honesty_failure_is_rank_one",
    "test_lro_3r_007_alignment_correlation_boundary_and_availability_are_rank_one",
    "test_lro_3r_008_alignment_22_wins_passes_21_confounds",
    "test_lro_3r_009_alignment_warning_is_mandatory_and_scientific",
    "test_lro_3r_010_equal_p_boundary_refit_completeness_and_status_independence",
    "test_lro_3r_011_dropout_and_frailty_warning_is_conditional_on_narrow_wrong",
    "test_lro_3r_012_continuous_abundance_warning_is_mandatory",
    "test_lro_3r_013_each_control_and_stress_is_required_for_top_pass",
    "test_lro_3r_014_rank_three_requires_every_nonstructured_gate",
    "test_lro_3r_015_rank_precedence_and_canonical_reasons_are_stable",
    "test_lro_3r_016_unknown_missing_duplicate_or_contradictory_never_passes",
    "test_lro_3r_017_local_and_global_reducers_are_total",
    "test_lro_3r_018_transportability_class_is_invariant",
    "test_lro_3r_019_every_stress_fit_plugin_or_predictive_unavailability_is_rank_one",
    "test_lro_3r_020_all_required_global_and_scenario_gates_pass_reaches_rank_four",
    "test_lro_3s_001_exact_22_file_manifest_and_null_config_hashes",
    "test_lro_3s_002_verification_represents_other_21_files",
    "test_lro_3s_003_external_snapshot_includes_all_22_files",
    "test_lro_3s_004_config_and_receipt_self_hashes_are_not_file_hashes",
    "test_lro_3s_005_phase_guards_require_typed_hash_identities",
    "test_lro_3s_006_task3_calibration_dispatch_smoke_is_fixture_only",
    "test_lro_3s_007_task3_smoke_cannot_reach_live_calibration_runner",
    "test_lro_3s_008_task4_is_first_live_benchmark_and_calibration_owner",
    "test_lro_3s_009_scenario_definitions_use_contract_order",
    "test_lro_3s_010_two_fixture_bundles_are_byte_identical",
    "test_post_exposure_log_append_accepts_exact_provenance_suffix_and_parent",
    "test_post_exposure_log_append_rejects_prefix_change_or_analytical_payload",
    "test_post_exposure_zero_exit_requires_complete_unchanged_envelope",
    "test_post_exposure_nonzero_without_mutation_allows_one_approved_exact_retry",
    "test_post_exposure_second_nonmutating_nonzero_stops_without_invalidation",
    "test_post_exposure_mutation_invalidates_for_zero_or_nonzero_exit",
    "test_post_exposure_guard_detects_each_immutable_byte_class",
    "test_post_exposure_guard_wraps_each_command_not_batch",
    "test_config_emission_fails_closed_on_identity_or_footprint_mismatch",
    "test_freeze_fails_closed_on_identity_or_footprint_mismatch",
    "test_holdout_pre_receipt_guard_fails_before_receipt_and_rng",
    "test_holdout_post_receipt_guard_failure_burns_namespace_before_rng",
    "test_holdout_success_freezes_represented_and_complete_artifact_snapshots",
    "test_holdout_and_artifact_generating_commands_are_never_retryable",
    "test_allowed_new_candidate_paths_are_hashed_but_extra_untracked_path_fails",
    "test_exact_staging_changes_only_predeclared_index_blobs",
    "test_authorized_commit_merge_and_push_transitions_are_literal",
    "test_candidate_footprint_presence_vector_is_phase_specific",
    "test_supersession_record_preserves_log_target_and_binds_live_parent",
    "test_holdout_receipt_exposure_fields_self_hash_and_later_invalidation_are_immutable",
    "test_task6_validation_dispatch_is_postholdout_only",
    "test_terminal_attestation_is_exactly_reviewed_appended_and_staged_once",
    "test_potentially_mutating_hooks_are_noops_before_freeze",
)
EXPECTED_FIT_EXECUTION_HEADER = (
    "scenario_id",
    "split_id",
    "fit_scope",
    "fit_variant",
    "fit_index",
    "source_replicate_first",
    "source_replicate_last",
    "source_replicate_count",
    "fit_succeeded",
    "converged_start_count",
    "best_start_index",
    "best_two_log_likelihoods_agree",
    "at_boundary",
    "boundary_parameter_ids",
    "alpha_estimate",
    "beta_driver_estimate",
    "beta_quality_estimate",
    "lambda_quasi_estimate",
    "lambda_present_estimate",
    "lambda_equal_estimate",
    "log_likelihood",
    "heldout_log_score",
    "fit_failure_class",
    "failure_code",
    "evidence_row_type",
    "design_kind",
    "design_provenance",
    "design_role",
    "design_n_rows",
    "design_n_columns",
    "design_rank",
    "design_condition_number",
    "design_passed",
    "design_failure_code",
    "design_frame_cell_count",
    "design_frame_sha256",
)
EXPECTED_CONTROL_DECISION_HEADER = (
    "decision_row_id",
    "decision_row_type",
    "scenario_id",
    "parameter_id",
    "structural_status",
    "practical_status",
    "gate_family",
    "gate_result",
    "test_statistic",
    "bootstrap_replicates",
    "bootstrap_converged_count",
    "bootstrap_failed_count",
    "p_value",
    "alignment_correlation",
    "silent_misspecification_failure",
    "attempted_replicates",
    "evaluable_replicates",
    "event_count",
    "acceptance_lower_count",
    "acceptance_upper_count",
    "recommendation_rank",
    "recommendation_class",
    "transportability_class",
    "interpretation",
)
EXPECTED_EQUAL_EMISSION_STATUS_ROWS = (
    ("alpha", "unidentified", "unidentified"),
    ("beta_driver", "unidentified", "unidentified"),
    ("beta_quality", "unidentified", "unidentified"),
    ("lambda_quasi", "unidentified", "unidentified"),
    ("lambda_present", "identified", "not_applicable"),
    ("lambda_equal", "identified", "identified"),
)
EXPECTED_NON_GENERATIVE_COMMANDS = (
    ("git", "diff", "--check"),
    ("uv", "run", "ruff", "format", "--check", "."),
    ("uv", "run", "ruff", "check", "."),
    ("uv", "run", "mypy", "src", "tests"),
    ("uv", "run", "pytest"),
    ("uv", "build"),
    ("uv", "run", "pre-commit", "run", "--all-files"),
    (
        "uv",
        "run",
        "python",
        "scripts/run_synth_medium_latent_response_observation_recovery.py",
        "--phase",
        "verify",
        "--frozen-config",
        "artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json",
    ),
    (
        "uv",
        "run",
        "python",
        "scripts/run_synth_medium_latent_response_observation_recovery.py",
        "--phase",
        "verify-tracked-state",
        "--frozen-config",
        "artifacts/synth_medium_latent_response_observation_recovery/recovery_gate_config.json",
    ),
    (
        "shasum",
        "-a",
        "256",
        "docs/goals/023-synth-medium-latent-response-observation-recovery-gate/holdout_receipt.json",
    ),
    ("git", "status", "--ignored", "--short", "artifacts", "dist"),
    ("git", "status", "--short", "--branch", "--untracked-files=all"),
)
EXPECTED_SCENARIO_PARAMETER_TRUTH_ROWS = (
    ("process_oracle_observed_transition", "alpha", -6.0),
    ("process_oracle_observed_transition", "beta_driver", 1.25),
    ("process_oracle_observed_transition", "beta_quality", -0.60),
    ("observation_oracle_fixed_transition", "lambda_quasi", 0.15),
    ("observation_oracle_fixed_transition", "lambda_present", 4.0),
    *tuple(
        (scenario_id, parameter_id, truth)
        for scenario_id in (
            "dense_count_exact_model",
            "structured_imperfect_effort",
            "sparse_expected_failure",
        )
        for parameter_id, truth in (
            ("alpha", -6.0),
            ("beta_driver", 1.25),
            ("beta_quality", -0.60),
            ("lambda_quasi", 0.15),
            ("lambda_present", 4.0),
        )
    ),
    ("zero_driver_effect_negative_control", "alpha", -6.0),
    ("zero_driver_effect_negative_control", "beta_driver", 0.0),
    ("zero_driver_effect_negative_control", "beta_quality", -0.60),
    ("zero_driver_effect_negative_control", "lambda_quasi", 0.15),
    ("zero_driver_effect_negative_control", "lambda_present", 4.0),
    *tuple(
        (scenario_id, parameter_id, truth)
        for scenario_id in (
            "permuted_arrival_alignment_stress",
            "informative_dropout_misspecification_stress",
        )
        for parameter_id, truth in (
            ("alpha", -6.0),
            ("beta_driver", 1.25),
            ("beta_quality", -0.60),
            ("lambda_quasi", 0.15),
            ("lambda_present", 4.0),
        )
    ),
    *tuple(
        ("goal018_continuous_abundance_stress", parameter_id, None)
        for parameter_id in (
            "alpha",
            "beta_driver",
            "beta_quality",
            "lambda_quasi",
            "lambda_present",
        )
    ),
    ("spatial_frailty_stress", "alpha", -6.0),
    ("spatial_frailty_stress", "beta_driver", 1.25),
    ("spatial_frailty_stress", "beta_quality", -0.60),
    ("spatial_frailty_stress", "lambda_quasi", 0.15),
    ("spatial_frailty_stress", "lambda_present", 4.0),
)
EXPECTED_ENUM_DOMAINS = {
    "scenario_role": ("oracle", "exact_joint", "expected_failure", "negative_control", "stress"),
    "generation_model": (
        "exact_binary",
        "zero_driver",
        "equal_emission",
        "informative_dropout",
        "continuous_abundance",
        "spatial_frailty",
    ),
    "fit_model": ("process_oracle", "observation_oracle", "ordered_joint", "equal_emission_joint"),
    "schedule_id": ("process_truth", "dense_6", "structured_12", "sparse_24"),
    "effort_rule": ("not_applicable", "unit", "structured", "sparse"),
    "expected_behavior": (
        "recover",
        "weaken_honestly",
        "no_false_signal",
        "unidentifiable",
        "predictive_warning",
    ),
    "truth_access_class": ("oracle_only", "analyst_firewalled", "stress_evaluator_only"),
    "transportability_class": ("scheduled_count_only_point_process_bridge_required",),
    "gate_family": (
        "process_oracle",
        "observation_oracle",
        "dense_joint",
        "structured_joint",
        "sparse_honesty",
        "zero_driver_control",
        "arrival_alignment_control",
        "equal_emission_control",
        "informative_dropout_stress",
        "continuous_abundance_stress",
        "spatial_frailty_stress",
        "parameter_status",
        "final_recommendation",
    ),
}
EXPECTED_VISUAL_SOURCE_TABLES = (
    (
        "visuals/parameter_recovery.svg",
        ("model_parameter_contract.csv", "replicate_recovery.csv"),
    ),
    ("visuals/coverage_calibration.svg", ("coverage_calibration.csv",)),
    ("visuals/latent_time_calibration.svg", ("latent_time_calibration.csv",)),
    ("visuals/identifiability_profiles.svg", ("identifiability_profiles.csv",)),
    (
        "visuals/control_comparison.svg",
        ("fit_execution_evidence.csv", "control_decision_summary.csv"),
    ),
    (
        "visuals/review_montage.svg",
        (
            "visuals/parameter_recovery.svg",
            "visuals/coverage_calibration.svg",
            "visuals/latent_time_calibration.svg",
            "visuals/identifiability_profiles.svg",
            "visuals/control_comparison.svg",
        ),
    ),
)


class _ArithmeticFloat(float):
    hidden_transition_time = 6

    def __mul__(self, other: object, /) -> float:
        return 1_000_000.0

    def __rmul__(self, other: object, /) -> float:
        return -1_000_000.0


class _HostileInt(int):
    hidden_true_state = 1


class _RevealingTuple(tuple[Any, ...]):
    _hidden: tuple[Any, ...]
    _iteration_count: int

    def __new__(
        cls,
        visible: tuple[Any, ...],
        hidden: tuple[Any, ...],
    ) -> _RevealingTuple:
        instance = super().__new__(cls, visible)
        instance._hidden = hidden
        instance._iteration_count = 0
        return instance

    def __iter__(self) -> Iterator[Any]:
        self._iteration_count += 1
        if self._iteration_count == 1:
            return super().__iter__()
        return iter(self._hidden)


class _RecordingProcessGenerator:
    def __init__(self, values: np.ndarray[Any, np.dtype[np.float64]]) -> None:
        self.values = values
        self.calls: list[tuple[tuple[int, int], object]] = []

    def random(
        self,
        *,
        size: tuple[int, int],
        dtype: object,
    ) -> np.ndarray[Any, np.dtype[np.float64]]:
        self.calls.append((size, dtype))
        assert self.values.shape == size
        return self.values.copy()


class _RecordingObservationGenerator:
    def __init__(self, counts: np.ndarray[Any, np.dtype[np.int64]]) -> None:
        self.counts = counts
        self.calls: list[np.ndarray[Any, np.dtype[np.float64]]] = []

    def poisson(
        self,
        lam: np.ndarray[Any, np.dtype[np.float64]],
    ) -> np.ndarray[Any, np.dtype[np.int64]]:
        self.calls.append(lam.copy())
        assert self.counts.shape == lam.shape
        return self.counts.copy()


def _core() -> Any:
    return import_module(CORE_MODULE)


def _joint_parameters(core: Any) -> Any:
    return core.JointParameters(
        alpha=-6.0,
        beta_driver=1.25,
        beta_quality=-0.60,
        lambda_quasi=0.15,
        lambda_present=4.0,
    )


def _process_parameters(core: Any) -> Any:
    return core.ProcessParameters(alpha=-6.0, beta_driver=1.25, beta_quality=-0.60)


def _op(core: Any, *, time: int, count: int, effort: float = 1.0) -> Any:
    return core.CountOpportunity(time=time, count=count, effort=effort)


def _history(
    core: Any,
    *opportunities: Any,
    quality: float = -0.60,
    tp: float | None = 0.0,
) -> Any:
    return core.AnalystHistory(
        cell_id=17,
        standardized_quality=quality,
        predator_arrival_time=tp,
        opportunities=tuple(opportunities),
    )


def _poisson_log(count: int, mean: float) -> float:
    return count * math.log(mean) - mean - math.lgamma(count + 1)


def _hazard(*, alpha: float, beta_driver: float, beta_quality: float, g: float, q: float) -> float:
    eta = alpha + beta_driver * g + beta_quality * q
    return -math.expm1(-math.exp(eta))


def _rng_payload(
    *,
    scenario_id: str = "dense_count_exact_model",
    split: str = "development",
    replicate_index: object = 0,
    component: str = "process",
    draw_index: object = None,
) -> dict[str, object]:
    return {
        "goal": "023",
        "master_seed": 20260711,
        "scenario_id": scenario_id,
        "split": split,
        "replicate_index": replicate_index,
        "component": component,
        "draw_index": draw_index,
    }


def _small_design_cells(core: Any) -> tuple[Any, ...]:
    return (
        core.DesignCell(1, -1.0, 0.0, "north_band"),
        core.DesignCell(3, 0.25, None, "middle_band"),
        core.DesignCell(8, 1.0, 60.0, "south_band"),
    )


@pytest.fixture(scope="module")
def canonical_design_cells() -> tuple[Any, ...]:
    core = _core()
    landscape_module = import_module("spatext.synth.medium.landscape")
    landscape = landscape_module.build_synth_medium_landscape()
    passable = tuple(
        sorted(
            (cell for cell in landscape.cells if cell.passability != "water"),
            key=lambda cell: cell.cell_id,
        )
    )
    quality = np.asarray([cell.quality for cell in passable], dtype=np.float64)
    standardized = (quality - quality.mean()) / quality.std(ddof=0)
    assert len(passable) == 5225
    return tuple(
        core.DesignCell(
            cell_id=cell.cell_id,
            standardized_quality=float(standardized[index]),
            predator_arrival_time=None,
            row_band=cell.row_band,
        )
        for index, cell in enumerate(passable)
    )


def test_lro_2a1_001_model_grid_and_parameter_contracts_are_frozen() -> None:
    core = _core()

    assert tuple(range(0, 121, 6)) == core.MODEL_TIMES
    assert core.ALPHA_SUPPORT == (-10.0, -2.0)
    assert core.BETA_DRIVER_SUPPORT == (-3.0, 3.0)
    assert core.BETA_QUALITY_SUPPORT == (-2.0, 2.0)
    assert core.LAMBDA_QUASI_SUPPORT == (0.01, 1.0)
    assert core.LAMBDA_PRESENT_SUPPORT == (0.25, 10.0)

    process = _process_parameters(core)
    joint = _joint_parameters(core)
    assert joint.process == process
    assert joint.rates == EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)
    assert core.ProcessParameters(-10.0, -3.0, -2.0)
    assert core.ProcessParameters(-2.0, 3.0, 2.0)
    assert core.JointParameters(-10.0, -3.0, -2.0, 0.01, 0.25)
    assert core.JointParameters(-2.0, 3.0, 2.0, 1.0, 10.0)
    with pytest.raises(FrozenInstanceError):
        process.alpha = -5.0
    with pytest.raises(FrozenInstanceError):
        joint.lambda_present = 5.0


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("alpha", -10.0001),
        ("alpha", -1.9999),
        ("beta_driver", -3.0001),
        ("beta_driver", 3.0001),
        ("beta_quality", -2.0001),
        ("beta_quality", 2.0001),
        ("alpha", math.nan),
        ("beta_driver", math.inf),
        ("beta_quality", True),
    ],
)
def test_lro_2a1_002_process_parameters_reject_values_outside_exact_support(
    name: str,
    value: object,
) -> None:
    core = _core()
    values: dict[str, object] = {
        "alpha": -6.0,
        "beta_driver": 1.25,
        "beta_quality": -0.60,
    }
    values[name] = value

    with pytest.raises(ValueError, match=name):
        core.ProcessParameters(**values)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("lambda_quasi", 0.0099),
        ("lambda_quasi", 1.0001),
        ("lambda_present", 0.2499),
        ("lambda_present", 10.0001),
        ("lambda_quasi", math.nan),
        ("lambda_present", math.inf),
        ("lambda_present", True),
    ],
)
def test_lro_2a1_003_joint_parameters_reject_rate_support_violations(
    name: str,
    value: object,
) -> None:
    core = _core()
    values: dict[str, object] = {
        "alpha": -6.0,
        "beta_driver": 1.25,
        "beta_quality": -0.60,
        "lambda_quasi": 0.15,
        "lambda_present": 4.0,
    }
    values[name] = value

    with pytest.raises(ValueError, match=name):
        core.JointParameters(**values)


def test_lro_2a1_004_joint_parameters_require_strict_rate_ordering() -> None:
    core = _core()

    with pytest.raises(ValueError, match="lambda_present must be greater than lambda_quasi"):
        core.JointParameters(
            alpha=-6.0,
            beta_driver=1.25,
            beta_quality=-0.60,
            lambda_quasi=0.25,
            lambda_present=0.25,
        )


def test_lro_2a1_005_analyst_oracle_and_truth_types_are_physically_separate() -> None:
    core = _core()
    type_names = (
        "AnalystHistory",
        "ProcessOracleOutcome",
        "ObservationOracleHistory",
        "LatentProcessTruth",
    )
    classes = [getattr(core, name) for name in type_names]

    assert len(set(classes)) == 4
    assert all(cls.__mro__[1] is object for cls in classes)
    analyst_fields = {field.name for field in fields(core.AnalystHistory)}
    assert analyst_fields == {
        "cell_id",
        "standardized_quality",
        "predator_arrival_time",
        "opportunities",
    }
    assert not analyst_fields & {
        "scenario_id",
        "split",
        "replicate_index",
        "seed",
        "generating_parameters",
        "true_states",
        "transition_time",
    }
    process_oracle = core.ProcessOracleOutcome(17, -0.60, 0.0, 6)
    observation_oracle = core.ObservationOracleHistory(17, (), ())
    truth = core.LatentProcessTruth(17, 6)
    for value, attribute in (
        (process_oracle, "transition_time"),
        (observation_oracle, "states"),
        (truth, "transition_time"),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(value, attribute, None)


def test_lro_2a1_006_analyst_history_is_frozen_and_rejects_truth_fields() -> None:
    core = _core()
    history = _history(core, _op(core, time=0, count=2))

    with pytest.raises(FrozenInstanceError):
        history.standardized_quality = 0.0
    with pytest.raises(TypeError):
        core.AnalystHistory(
            cell_id=17,
            standardized_quality=-0.60,
            predator_arrival_time=0.0,
            opportunities=(),
            true_states=(0,) * 21,
        )


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"cell_id": -1}, "cell_id"),
        ({"cell_id": 6048}, "cell_id"),
        ({"cell_id": True}, "cell_id"),
        ({"cell_id": 1.5}, "cell_id"),
        ({"standardized_quality": math.nan}, "standardized_quality"),
        ({"standardized_quality": math.inf}, "standardized_quality"),
        ({"standardized_quality": True}, "standardized_quality"),
        ({"predator_arrival_time": -0.1}, "predator_arrival_time"),
        ({"predator_arrival_time": True}, "predator_arrival_time"),
    ],
)
def test_lro_2a1_007_analyst_history_validates_cell_quality_and_finite_arrival(
    kwargs: dict[str, object],
    message: str,
) -> None:
    core = _core()
    values: dict[str, object] = {
        "cell_id": 17,
        "standardized_quality": -0.60,
        "predator_arrival_time": 0.0,
        "opportunities": (),
    }
    values.update(kwargs)

    with pytest.raises(ValueError, match=message):
        core.AnalystHistory(**values)


@pytest.mark.parametrize("arrival", [None, math.nan, math.inf, -math.inf])
def test_lro_2a1_008_nonfinite_arrival_is_valid_and_sets_driver_to_zero(
    arrival: float | None,
) -> None:
    core = _core()
    history = _history(core, tp=arrival)
    primitives = core.process_log_primitives(
        standardized_quality=history.standardized_quality,
        predator_arrival_time=history.predator_arrival_time,
        parameters=_process_parameters(core),
        interval_count=20,
    )

    np.testing.assert_array_equal(primitives.driver, np.zeros(20, dtype=np.float64))


@pytest.mark.parametrize(
    ("time", "count", "effort", "message"),
    [
        (-6, 0, 1.0, "time"),
        (3, 0, 1.0, "time"),
        (126, 0, 1.0, "time"),
        (True, 0, 1.0, "time"),
        (0, -1, 1.0, "count"),
        (0, 1.5, 1.0, "count"),
        (0, True, 1.0, "count"),
        (0, 1_000_000_001, 1.0, "count"),
        (0, 0, 0.0, "effort"),
        (0, 0, -1.0, "effort"),
        (0, 0, math.nan, "effort"),
        (0, 0, math.inf, "effort"),
    ],
)
def test_lro_2a1_009_count_opportunity_validates_time_count_and_effort(
    time: int,
    count: object,
    effort: float,
    message: str,
) -> None:
    core = _core()

    with pytest.raises(ValueError, match=message):
        core.CountOpportunity(time=time, count=count, effort=effort)


def test_lro_2a1_010_analyst_opportunities_must_be_a_sorted_unique_tuple() -> None:
    core = _core()
    first = _op(core, time=0, count=1)
    second = _op(core, time=6, count=0)

    with pytest.raises(ValueError, match="tuple"):
        core.AnalystHistory(17, -0.60, 0.0, [first, second])
    with pytest.raises(ValueError, match="strictly increasing"):
        _history(core, second, first)
    with pytest.raises(ValueError, match="strictly increasing"):
        _history(core, first, _op(core, time=0, count=2))


def test_lro_2a1_011_process_primitives_are_stable_float64_readonly_arrays() -> None:
    core = _core()
    primitives = core.process_log_primitives(
        standardized_quality=CANONICAL_Q_MAX,
        predator_arrival_time=0.0,
        parameters=core.ProcessParameters(alpha=-2.0, beta_driver=3.0, beta_quality=2.0),
        interval_count=20,
    )

    for array in (
        primitives.driver,
        primitives.eta,
        primitives.log_survival,
        primitives.log_hazard,
    ):
        assert array.dtype == np.float64
        assert np.all(np.isfinite(array))
        assert not array.flags.writeable
    np.testing.assert_allclose(primitives.log_survival, -np.exp(primitives.eta))
    np.testing.assert_allclose(
        primitives.log_hazard,
        np.log(-np.expm1(-np.exp(primitives.eta))),
        rtol=0.0,
        atol=0.0,
    )


@pytest.mark.parametrize(
    ("quality", "parameters"),
    [
        (CANONICAL_Q_MIN, (-10.0, -3.0, 2.0)),
        (CANONICAL_Q_MAX, (-10.0, -3.0, -2.0)),
        (CANONICAL_Q_MIN, (-2.0, 3.0, -2.0)),
        (CANONICAL_Q_MAX, (-2.0, 3.0, 2.0)),
    ],
)
def test_lro_2a1_012_support_extremes_cover_actual_canonical_quality_range(
    quality: float,
    parameters: tuple[float, float, float],
) -> None:
    core = _core()
    alpha, beta_driver, beta_quality = parameters
    primitives = core.process_log_primitives(
        standardized_quality=quality,
        predator_arrival_time=0.0,
        parameters=core.ProcessParameters(alpha, beta_driver, beta_quality),
        interval_count=20,
    )
    hazards = core.hazard_probabilities(primitives)

    assert hazards.dtype == np.float64
    assert not hazards.flags.writeable
    assert np.all(np.isfinite(hazards))
    assert np.all((hazards > 0.0) & (hazards <= 1.0))


def test_lro_2a1_013_zero_driver_removes_arrival_dependence_but_not_background_risk() -> None:
    core = _core()
    parameters = core.ProcessParameters(alpha=-6.0, beta_driver=0.0, beta_quality=-0.60)
    early = core.process_log_primitives(
        standardized_quality=CANONICAL_Q_MIN,
        predator_arrival_time=0.0,
        parameters=parameters,
        interval_count=20,
    )
    absent = core.process_log_primitives(
        standardized_quality=CANONICAL_Q_MIN,
        predator_arrival_time=math.nan,
        parameters=parameters,
        interval_count=20,
    )
    other_quality = core.process_log_primitives(
        standardized_quality=CANONICAL_Q_MAX,
        predator_arrival_time=math.nan,
        parameters=parameters,
        interval_count=20,
    )

    np.testing.assert_array_equal(early.eta, absent.eta)
    assert np.all(np.exp(early.log_survival) < 1.0)
    assert not np.array_equal(early.eta, other_quality.eta)


def test_lro_2a1_014_event_and_censor_path_masses_normalize_for_1_2_and_20_intervals() -> None:
    core = _core()
    parameters = _process_parameters(core)

    for interval_count in (1, 2, 20):
        primitives = core.process_log_primitives(
            standardized_quality=-0.60,
            predator_arrival_time=0.0,
            parameters=parameters,
            interval_count=interval_count,
        )
        log_masses = core.transition_log_path_masses(primitives)

        assert log_masses.dtype == np.float64
        assert log_masses.shape == (interval_count + 1,)
        assert not log_masses.flags.writeable
        assert np.exp(log_masses).sum() == pytest.approx(1.0, abs=1e-14)


def test_lro_2a1_015_process_oracle_event_and_censor_match_handwritten_products() -> None:
    core = _core()
    parameters = _process_parameters(core)
    event = core.ProcessOracleOutcome(
        cell_id=17,
        standardized_quality=-0.60,
        predator_arrival_time=0.0,
        transition_time=12,
    )
    censor = core.ProcessOracleOutcome(
        cell_id=17,
        standardized_quality=-0.60,
        predator_arrival_time=0.0,
        transition_time=None,
    )
    primitives = core.process_log_primitives(
        standardized_quality=-0.60,
        predator_arrival_time=0.0,
        parameters=parameters,
        interval_count=2,
    )
    hazards = core.hazard_probabilities(primitives)

    expected_event = math.log1p(-hazards[0]) + math.log(hazards[1])
    expected_censor = math.log1p(-hazards[0]) + math.log1p(-hazards[1])
    assert core.process_oracle_log_likelihood(event, parameters, interval_count=2) == pytest.approx(
        expected_event
    )
    assert core.process_oracle_log_likelihood(
        censor, parameters, interval_count=2
    ) == pytest.approx(expected_censor)


def test_lro_2a1_016_truth_state_is_present_at_t0_and_post_transition_at_endpoint() -> None:
    core = _core()
    truth = core.LatentProcessTruth(cell_id=17, transition_time=6)

    assert truth.state_at(0) == 0
    assert truth.state_at(6) == 1
    assert truth.state_at(120) == 1
    censor = core.LatentProcessTruth(cell_id=17, transition_time=None)
    assert all(censor.state_at(time) == 0 for time in core.MODEL_TIMES)


def test_lro_2a1_017_observation_oracle_uses_post_transition_states_and_observe_kernel() -> None:
    core = _core()
    opportunities = (
        _op(core, time=0, count=3, effort=0.5),
        _op(core, time=6, count=1, effort=1.0),
        _op(core, time=18, count=0, effort=1.3),
    )
    oracle = core.ObservationOracleHistory(
        cell_id=17,
        opportunities=opportunities,
        states=(0, 1, 1),
    )
    rates = EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)
    expected = sum(
        state_count_log_probability(
            count=opportunity.count,
            effort=opportunity.effort,
            state=state,
            rates=rates,
        )
        for opportunity, state in zip(opportunities, oracle.states, strict=True)
    )

    assert core.observation_oracle_log_likelihood(oracle, rates) == pytest.approx(expected)


def test_lro_2a1_018_observation_oracle_rejects_nonabsorbing_or_t0_extirpated_states() -> None:
    core = _core()
    opportunities = (
        _op(core, time=0, count=1),
        _op(core, time=6, count=0),
        _op(core, time=12, count=1),
    )

    with pytest.raises(ValueError, match="t0 state must be present"):
        core.ObservationOracleHistory(17, opportunities, (1, 1, 1))
    with pytest.raises(ValueError, match="absorbing"):
        core.ObservationOracleHistory(17, opportunities, (0, 1, 0))


def test_lro_2a1_019_one_interval_joint_likelihood_matches_handwritten_mixture() -> None:
    core = _core()
    parameters = _joint_parameters(core)
    history = _history(
        core,
        _op(core, time=0, count=2, effort=0.5),
        _op(core, time=6, count=0, effort=1.0),
    )
    q = history.standardized_quality
    h1 = _hazard(alpha=-6.0, beta_driver=1.25, beta_quality=-0.60, g=0.2, q=q)
    baseline = _poisson_log(2, 0.5 * 4.0)
    event_emission = math.exp(_poisson_log(0, 0.15))
    censor_emission = math.exp(_poisson_log(0, 4.0))
    expected = baseline + math.log(h1 * event_emission + (1.0 - h1) * censor_emission)

    enumerated = core.joint_log_likelihood_enumeration(history, parameters, interval_count=1)
    forwarded = core.joint_log_likelihood_forward(history, parameters, interval_count=1)
    assert enumerated == pytest.approx(expected)
    assert forwarded == pytest.approx(expected)


def test_lro_2a1_020_two_interval_joint_matches_independent_brute_force() -> None:
    core = _core()
    parameters = _joint_parameters(core)
    history = _history(
        core,
        _op(core, time=0, count=1, effort=0.75),
        _op(core, time=12, count=2, effort=1.1),
    )
    q = history.standardized_quality
    h1 = _hazard(alpha=-6.0, beta_driver=1.25, beta_quality=-0.60, g=0.2, q=q)
    h2 = _hazard(alpha=-6.0, beta_driver=1.25, beta_quality=-0.60, g=0.4, q=q)
    baseline = _poisson_log(1, 0.75 * 4.0)
    post = math.exp(_poisson_log(2, 1.1 * 0.15))
    present = math.exp(_poisson_log(2, 1.1 * 4.0))
    mixture = h1 * post + (1.0 - h1) * h2 * post + (1.0 - h1) * (1.0 - h2) * present
    expected = baseline + math.log(mixture)

    enumerated = core.joint_log_likelihood_enumeration(history, parameters, interval_count=2)
    forwarded = core.joint_log_likelihood_forward(history, parameters, interval_count=2)
    assert enumerated == pytest.approx(expected)
    assert forwarded == pytest.approx(expected)


@pytest.mark.parametrize(
    "opportunities",
    [
        (),
        ((0, 0, 1.0), (6, 0, 1.0), (120, 0, 1.0)),
        ((0, 2, 0.7), (18, 1, 1.3), (54, 0, 0.8), (120, 3, 1.0)),
        ((0, 1, 1.0), (24, 0, 0.6), (48, 2, 0.6), (96, 0, 0.6)),
    ],
)
def test_lro_2a1_021_enumeration_and_forward_agree_for_full_irregular_histories(
    opportunities: tuple[tuple[int, int, float], ...],
) -> None:
    core = _core()
    history = _history(
        core,
        *(
            _op(core, time=time, count=count, effort=effort)
            for time, count, effort in opportunities
        ),
    )
    parameters = _joint_parameters(core)

    enumerated = core.joint_log_likelihood_enumeration(history, parameters)
    forwarded = core.joint_log_likelihood_forward(history, parameters)
    assert math.isfinite(enumerated)
    assert forwarded == pytest.approx(enumerated, abs=1e-11)
    if not opportunities:
        assert enumerated == pytest.approx(0.0, abs=1e-13)


def test_lro_2a1_022_omitted_emissions_leave_all_intervening_transition_intervals() -> None:
    core = _core()
    parameters = _joint_parameters(core)
    history = _history(core, _op(core, time=0, count=2), _op(core, time=120, count=0))

    weights = core.joint_path_posterior_weights(history, parameters)
    assert weights.shape == (21,)
    assert np.count_nonzero(weights > 0.0) == 21
    assert weights.sum() == pytest.approx(1.0, abs=1e-14)


def test_lro_2a1_023_path_posterior_weights_are_normalized_and_match_prior_without_counts() -> None:
    core = _core()
    parameters = _joint_parameters(core)
    history = _history(core)
    weights = core.joint_path_posterior_weights(history, parameters)
    primitives = core.process_log_primitives(
        standardized_quality=history.standardized_quality,
        predator_arrival_time=history.predator_arrival_time,
        parameters=parameters.process,
        interval_count=20,
    )
    expected = np.exp(core.transition_log_path_masses(primitives))

    assert weights.dtype == np.float64
    assert not weights.flags.writeable
    assert weights.shape == (21,)
    assert weights.sum() == pytest.approx(1.0, abs=1e-14)
    np.testing.assert_allclose(weights, expected, rtol=1e-13, atol=1e-15)


def test_lro_2a1_024_joint_signatures_accept_analyst_history_not_truth_types() -> None:
    core = _core()
    forbidden = {
        "scenario",
        "split",
        "replicate",
        "seed",
        "generating_parameters",
        "true_states",
        "transition_time",
        "truth",
    }

    for function in (
        core.joint_log_likelihood_enumeration,
        core.joint_log_likelihood_forward,
        core.joint_path_posterior_weights,
    ):
        signature = inspect.signature(function)
        assert signature.parameters["history"].annotation in {
            "AnalystHistory",
            core.AnalystHistory,
        }
        assert not forbidden & set(signature.parameters)

    truth = core.LatentProcessTruth(cell_id=17, transition_time=6)
    with pytest.raises(TypeError, match="AnalystHistory"):
        core.joint_log_likelihood_enumeration(truth, _joint_parameters(core))

    forward_source = inspect.getsource(core.joint_log_likelihood_forward)
    enumeration_source = inspect.getsource(core.joint_log_likelihood_enumeration)
    assert "joint_log_likelihood_enumeration" not in forward_source
    assert "logsumexp" in enumeration_source


def test_lro_2a1_025_forbidden_truth_cannot_alter_joint_likelihood() -> None:
    core = _core()
    history = _history(core, _op(core, time=0, count=2), _op(core, time=12, count=0))
    parameters = _joint_parameters(core)
    early_truth = core.LatentProcessTruth(cell_id=17, transition_time=6)
    censored_truth = core.LatentProcessTruth(cell_id=17, transition_time=None)

    first = core.joint_log_likelihood_enumeration(history, parameters)
    assert early_truth != censored_truth
    second = core.joint_log_likelihood_enumeration(history, parameters)
    assert second == first


def test_lro_2a1_026_nonfinite_likelihood_evaluation_raises_never_returns_sentinel() -> None:
    core = _core()
    history = _history(core, quality=1e308)

    with pytest.raises(core.LikelihoodEvaluationError, match="nonfinite"):
        core.joint_log_likelihood_enumeration(history, _joint_parameters(core))


@pytest.mark.parametrize("interval_count", [0, 21, True, 1.5])
def test_lro_2a1_027_interval_count_must_be_an_integer_from_1_to_20(
    interval_count: object,
) -> None:
    core = _core()

    with pytest.raises(ValueError, match="interval_count"):
        core.process_log_primitives(
            standardized_quality=-0.60,
            predator_arrival_time=0.0,
            parameters=_process_parameters(core),
            interval_count=interval_count,
        )


def test_lro_2a1_028_history_cannot_observe_after_requested_process_horizon() -> None:
    core = _core()
    history = _history(core, _op(core, time=12, count=1))

    with pytest.raises(ValueError, match="process horizon"):
        core.joint_log_likelihood_enumeration(
            history,
            _joint_parameters(core),
            interval_count=1,
        )


def test_lro_2a1_029_process_oracle_rejects_event_outside_requested_horizon() -> None:
    core = _core()
    outcome = core.ProcessOracleOutcome(17, -0.60, 0.0, 18)

    with pytest.raises(ValueError, match="process horizon"):
        core.process_oracle_log_likelihood(
            outcome,
            _process_parameters(core),
            interval_count=2,
        )


def test_lro_2a1_030_observation_oracle_empty_history_has_zero_log_likelihood() -> None:
    core = _core()
    oracle = core.ObservationOracleHistory(cell_id=17, opportunities=(), states=())
    rates = EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)

    assert core.observation_oracle_log_likelihood(oracle, rates) == 0.0


def test_lro_2a1_031_poisson_hand_formula_helper_matches_shared_kernel() -> None:
    assert _poisson_log(7, 3.25) == pytest.approx(poisson_log_probability(count=7, mean=3.25))


@pytest.mark.parametrize(
    "target",
    [
        "process_parameter",
        "joint_rate",
        "analyst_quality",
        "analyst_arrival",
        "opportunity_effort",
    ],
)
def test_lro_2a1_032_float_subclass_overloads_cannot_enter_model_inputs(target: str) -> None:
    core = _core()

    with pytest.raises(ValueError):
        if target == "process_parameter":
            core.ProcessParameters(_ArithmeticFloat(-6.0), 1.25, -0.60)
        elif target == "joint_rate":
            core.JointParameters(-6.0, 1.25, -0.60, 0.15, _ArithmeticFloat(4.0))
        elif target == "analyst_quality":
            core.AnalystHistory(17, _ArithmeticFloat(-0.60), 0.0, ())
        elif target == "analyst_arrival":
            core.AnalystHistory(17, -0.60, _ArithmeticFloat(0.0), ())
        else:
            core.CountOpportunity(0, 0, _ArithmeticFloat(1.0))


@pytest.mark.parametrize("target", ["analyst_opportunities", "oracle_states"])
def test_lro_2a1_033_tuple_subclass_cannot_reveal_hidden_values_after_validation(
    target: str,
) -> None:
    core = _core()
    present = _op(core, time=0, count=2)
    hidden = _op(core, time=0, count=999)

    with pytest.raises(ValueError, match="tuple"):
        if target == "analyst_opportunities":
            core.AnalystHistory(
                17,
                -0.60,
                0.0,
                _RevealingTuple((present,), (hidden,)),
            )
        else:
            core.ObservationOracleHistory(
                17,
                (present,),
                _RevealingTuple((0,), (1,)),
            )


@pytest.mark.parametrize(
    "target",
    ["cell_id", "time", "count", "state", "transition_time", "interval_count"],
)
def test_lro_2a1_034_integer_subclasses_are_rejected_at_exact_primitive_boundary(
    target: str,
) -> None:
    core = _core()

    with pytest.raises(ValueError):
        if target == "cell_id":
            core.AnalystHistory(_HostileInt(17), -0.60, 0.0, ())
        elif target == "time":
            core.CountOpportunity(_HostileInt(6), 0, 1.0)
        elif target == "count":
            core.CountOpportunity(6, _HostileInt(0), 1.0)
        elif target == "state":
            core.ObservationOracleHistory(17, (_op(core, time=0, count=0),), (_HostileInt(0),))
        elif target == "transition_time":
            core.LatentProcessTruth(17, _HostileInt(6))
        else:
            core.process_log_primitives(
                standardized_quality=-0.60,
                predator_arrival_time=0.0,
                parameters=_process_parameters(core),
                interval_count=_HostileInt(1),
            )


@pytest.mark.parametrize(
    "array_name",
    [
        "driver",
        "eta",
        "log_survival",
        "log_hazard",
        "hazards",
        "path_masses",
        "posterior_weights",
    ],
)
def test_lro_2a1_035_public_arrays_cannot_restore_writability_or_change_results(
    array_name: str,
) -> None:
    core = _core()
    parameters = _joint_parameters(core)
    history = _history(core, _op(core, time=0, count=2), _op(core, time=12, count=0))
    primitives = core.process_log_primitives(
        standardized_quality=history.standardized_quality,
        predator_arrival_time=history.predator_arrival_time,
        parameters=parameters.process,
    )
    arrays = {
        "driver": primitives.driver,
        "eta": primitives.eta,
        "log_survival": primitives.log_survival,
        "log_hazard": primitives.log_hazard,
        "hazards": core.hazard_probabilities(primitives),
        "path_masses": core.transition_log_path_masses(primitives),
        "posterior_weights": core.joint_path_posterior_weights(history, parameters),
    }
    selected = arrays[array_name]
    original = selected.copy()
    likelihood_before = core.joint_log_likelihood_enumeration(history, parameters)

    with pytest.raises(ValueError):
        selected.setflags(write=True)
    with pytest.raises(ValueError):
        selected[0] = selected[0] + 1.0

    np.testing.assert_array_equal(selected, original)
    assert core.joint_log_likelihood_enumeration(history, parameters) == likelihood_before


def test_lro_2a1_036_exact_builtin_numbers_are_stored_as_canonical_primitives() -> None:
    core = _core()
    process = core.ProcessParameters(-6, 1, 0)
    joint = core.JointParameters(-6, 1, 0, 0.15, 4)
    opportunity = core.CountOpportunity(0, 2, 1)
    history = core.AnalystHistory(17, 0, 0, (opportunity,))

    assert all(
        type(value) is float for value in (process.alpha, process.beta_driver, process.beta_quality)
    )
    assert all(
        type(value) is float
        for value in (
            joint.alpha,
            joint.beta_driver,
            joint.beta_quality,
            joint.lambda_quasi,
            joint.lambda_present,
            opportunity.effort,
            history.standardized_quality,
            history.predator_arrival_time,
        )
    )
    assert type(history.cell_id) is int
    assert type(opportunity.time) is int
    assert type(opportunity.count) is int


def test_lro_2a2_001_rng_payload_uses_exact_canonical_json_digest_and_entropy_words() -> None:
    core = _core()
    payload = _rng_payload()

    canonical = core.canonical_rng_payload_json(payload)
    assert canonical == (
        '{"component":"process","draw_index":null,"goal":"023",'
        '"master_seed":20260711,"replicate_index":0,'
        '"scenario_id":"dense_count_exact_model","split":"development"}'
    )
    assert canonical.isascii()
    assert core.rng_payload_sha256(payload) == (
        "e7928c352cbc24709b93269d85cfc8f01747268704eac132e91ce65be474a87d"
    )
    assert core.rng_entropy_words(payload) == (
        3885141045,
        750527600,
        2610112157,
        2244987120,
        390538887,
        82493746,
        3910985307,
        3832850557,
    )


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            _rng_payload(),
            [10510340404464842761, 2174300553185413078, 258851366587855250],
        ),
        (
            _rng_payload(
                scenario_id="structured_imperfect_effort",
                split="calibration",
                replicate_index=7,
                component="predictive_reference",
                draw_index=0,
            ),
            [11123817839291538733, 6431681636083337449, 10453666639700693841],
        ),
    ],
)
def test_lro_2a2_002_pcg64dxsm_reproduces_frozen_nonholdout_vectors(
    payload: dict[str, object],
    expected: list[int],
) -> None:
    core = _core()

    generator = core.rng_from_payload(payload)

    assert type(generator) is np.random.Generator
    assert type(generator.bit_generator) is np.random.PCG64DXSM
    np.testing.assert_array_equal(
        generator.bit_generator.random_raw(3),
        np.asarray(expected, dtype=np.uint64),
    )


def test_lro_2a2_003_rng_payload_schema_and_literal_values_are_exact() -> None:
    core = _core()
    valid = _rng_payload()
    invalid_payloads: list[object] = [
        {key: value for key, value in valid.items() if key != "draw_index"},
        {**valid, "extra": 1},
        {**valid, "goal": "23"},
        {**valid, "master_seed": 20260712},
        {**valid, "master_seed": True},
        {**valid, "scenario_id": "unknown_scenario"},
        {**valid, "split": "preview"},
        {**valid, "component": "unknown_component"},
        tuple(valid.items()),
    ]

    for payload in invalid_payloads:
        with pytest.raises((TypeError, ValueError)):
            core.validate_rng_payload(payload)


def test_lro_2a2_004_every_invalid_nonholdout_combination_fails_before_seed_sequence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    nested = (
        "process_oracle_observed_transition",
        "observation_oracle_fixed_transition",
        "dense_count_exact_model",
        "structured_imperfect_effort",
    )
    nonnested = (
        "sparse_expected_failure",
        "zero_driver_effect_negative_control",
        "permuted_arrival_alignment_stress",
        "informative_dropout_misspecification_stress",
        "goal018_continuous_abundance_stress",
        "spatial_frailty_stress",
    )
    invalid_payloads = [
        *(
            _rng_payload(scenario_id=scenario_id, replicate_index=replicate_index)
            for scenario_id in (*nested, *nonnested)
            for replicate_index in (-1, 12, True, 1.5)
        ),
        *(
            _rng_payload(
                scenario_id=scenario_id,
                split="calibration",
                replicate_index=replicate_index,
            )
            for scenario_id in nested
            for replicate_index in (-1, 24)
        ),
        *(
            _rng_payload(
                scenario_id=scenario_id,
                split="calibration",
                replicate_index=0,
            )
            for scenario_id in nonnested
        ),
        _rng_payload(component="process", draw_index=0),
        _rng_payload(component="predictive_reference", draw_index=None),
        _rng_payload(component="predictive_reference", draw_index=-1),
        _rng_payload(component="predictive_reference", draw_index=199),
        _rng_payload(component="predictive_reference", draw_index=True),
        _rng_payload(
            scenario_id="process_oracle_observed_transition",
            component="observation",
        ),
        _rng_payload(
            scenario_id="process_oracle_observed_transition",
            component="predictive_reference",
            draw_index=0,
        ),
        _rng_payload(component="dropout"),
        _rng_payload(component="frailty"),
        _rng_payload(component="bootstrap", draw_index=0),
        _rng_payload(
            scenario_id="no_emission_contrast_negative_control",
            component="bootstrap",
            draw_index=1,
        ),
        *(
            _rng_payload(
                scenario_id="no_emission_contrast_negative_control",
                replicate_index=replicate_index,
                component="process",
            )
            for replicate_index in (-1, 24, True, 1.5)
        ),
        _rng_payload(
            scenario_id="no_emission_contrast_negative_control",
            replicate_index=12,
            component="predictive_reference",
            draw_index=0,
        ),
        _rng_payload(
            scenario_id="no_emission_contrast_negative_control",
            replicate_index=24,
            component="bootstrap",
            draw_index=0,
        ),
    ]
    seed_sequence_calls = 0

    def forbidden_seed_sequence(*args: object, **kwargs: object) -> None:
        del args, kwargs
        nonlocal seed_sequence_calls
        seed_sequence_calls += 1
        raise AssertionError("invalid payload reached SeedSequence")

    monkeypatch.setattr(core.np.random, "SeedSequence", forbidden_seed_sequence)
    for payload in invalid_payloads:
        with pytest.raises(ValueError):
            core.rng_from_payload(payload)

    assert seed_sequence_calls == 0


def test_lro_2a2_005_valid_nonholdout_boundaries_cover_every_partition_class() -> None:
    core = _core()
    payloads = (
        _rng_payload(
            scenario_id="process_oracle_observed_transition",
            replicate_index=11,
        ),
        _rng_payload(
            scenario_id="structured_imperfect_effort",
            split="calibration",
            replicate_index=23,
            component="predictive_reference",
            draw_index=198,
        ),
        _rng_payload(
            scenario_id="sparse_expected_failure",
            replicate_index=11,
            component="pit_randomization",
        ),
        _rng_payload(
            scenario_id="informative_dropout_misspecification_stress",
            replicate_index=11,
            component="dropout",
        ),
        _rng_payload(
            scenario_id="spatial_frailty_stress",
            replicate_index=11,
            component="frailty",
        ),
        _rng_payload(
            scenario_id="no_emission_contrast_negative_control",
            replicate_index=23,
            component="process",
        ),
        _rng_payload(
            scenario_id="no_emission_contrast_negative_control",
            replicate_index=23,
            component="observation",
        ),
        _rng_payload(
            scenario_id="no_emission_contrast_negative_control",
            replicate_index=23,
            component="bootstrap",
            draw_index=0,
        ),
    )

    validated = tuple(core.validate_rng_payload(payload) for payload in payloads)

    assert tuple(value.replicate_index for value in validated) == (
        11,
        23,
        11,
        11,
        11,
        23,
        23,
        23,
    )
    assert validated[1].draw_index == 198


def test_lro_2a2_006_process_simulation_consumes_one_full_c_order_uniform_array() -> None:
    core = _core()
    cells = _small_design_cells(core)
    uniforms = np.zeros((len(cells), 20), dtype=np.float64, order="C")
    generator = _RecordingProcessGenerator(uniforms)

    truth = core.simulate_latent_process(cells, _process_parameters(core), generator)

    assert generator.calls == [((len(cells), 20), np.float64)]
    assert truth.cell_ids.dtype == np.int64
    assert truth.cell_ids.shape == (len(cells),)
    assert truth.states.dtype == np.float64
    assert truth.states.shape == (len(cells), 21)
    assert truth.transition_times.dtype == np.float64
    assert truth.transition_times.shape == (len(cells),)
    np.testing.assert_array_equal(truth.states[:, 0], 0.0)
    np.testing.assert_array_equal(truth.states[:, 1:], 1.0)
    np.testing.assert_array_equal(truth.transition_times, 6.0)
    for array in (truth.cell_ids, truth.states, truth.transition_times):
        assert array.flags.c_contiguous
        assert not array.flags.writeable
        with pytest.raises(ValueError):
            array.setflags(write=True)


def test_lro_2a2_007_absorption_never_shortens_process_rng_consumption() -> None:
    core = _core()
    cells = _small_design_cells(core)
    full_values = np.full((len(cells), 20), 0.5, dtype=np.float64)
    full_values[:, 0] = 0.0
    generator = _RecordingProcessGenerator(full_values)

    truth = core.simulate_latent_process(cells, _process_parameters(core), generator)

    assert np.all(truth.transition_times == 6.0)
    assert generator.calls == [((len(cells), 20), np.float64)]
    assert generator.values.size == len(cells) * 20


def test_lro_2a2_008_process_inputs_fail_before_rng_and_outputs_validate_exact_arrays() -> None:
    core = _core()
    cells = _small_design_cells(core)
    generator = _RecordingProcessGenerator(np.zeros((len(cells), 20), dtype=np.float64))

    with pytest.raises(ValueError, match="cell_id"):
        core.simulate_latent_process(tuple(reversed(cells)), _process_parameters(core), generator)
    assert generator.calls == []

    with pytest.raises(ValueError, match="states"):
        core.ProcessSimulationTruth(
            cell_ids=np.asarray([1], dtype=np.int64),
            states=np.zeros((1, 21), dtype=np.int64),
            transition_times=np.asarray([math.nan], dtype=np.float64),
        )


def test_lro_2a2_009_observation_simulation_uses_one_complete_canonical_poisson_call() -> None:
    core = _core()
    cells = _small_design_cells(core)[:2]
    cell_ids = np.asarray([cell.cell_id for cell in cells], dtype=np.int64)
    states = np.zeros((2, 21), dtype=np.float64)
    states[0, 1:] = 1.0
    truth = core.ProcessSimulationTruth(
        cell_ids=cell_ids,
        states=states,
        transition_times=np.asarray([6.0, math.nan], dtype=np.float64),
    )
    schedule = (
        core.ScheduledOpportunity(1, 0, 1.0, -1.0, 0.0),
        core.ScheduledOpportunity(1, 6, 1.0, -1.0, 0.0),
        core.ScheduledOpportunity(3, 0, 0.5, 0.25, None),
        core.ScheduledOpportunity(3, 6, 0.5, 0.25, None),
    )
    generator = _RecordingObservationGenerator(np.asarray([0, 1, 2, 3], dtype=np.int64))
    rates = EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)

    histories = core.simulate_observation_histories(schedule, truth, rates, generator)

    assert len(generator.calls) == 1
    np.testing.assert_array_equal(
        generator.calls[0],
        np.asarray([4.0, 0.15, 2.0, 2.0], dtype=np.float64),
    )
    assert tuple(history.cell_id for history in histories) == (1, 3)
    assert tuple(
        opportunity.count for history in histories for opportunity in history.opportunities
    ) == (0, 1, 2, 3)
    assert {field.name for field in fields(type(histories[0]))} == {
        "cell_id",
        "standardized_quality",
        "predator_arrival_time",
        "opportunities",
    }
    assert not hasattr(histories[0], "states")
    assert not hasattr(histories[0], "transition_times")


def test_lro_2a2_010_observation_order_and_truth_alignment_fail_before_poisson() -> None:
    core = _core()
    cells = _small_design_cells(core)[:2]
    process_generator = _RecordingProcessGenerator(np.zeros((2, 20), dtype=np.float64))
    truth = core.simulate_latent_process(cells, _process_parameters(core), process_generator)
    schedule = (
        core.ScheduledOpportunity(3, 0, 1.0, 0.25, None),
        core.ScheduledOpportunity(1, 0, 1.0, -1.0, 0.0),
    )
    observation_generator = _RecordingObservationGenerator(np.zeros(2, dtype=np.int64))

    with pytest.raises(ValueError, match="canonical opportunity order"):
        core.simulate_observation_histories(
            schedule,
            truth,
            EffectiveCountRates(4.0, 0.15),
            observation_generator,
        )

    assert observation_generator.calls == []


def test_lro_2a2_011_scenario_schedule_table_is_literal_and_complete() -> None:
    core = _core()
    expected = {
        "process_oracle_observed_transition": ("process_truth", "not_applicable"),
        "observation_oracle_fixed_transition": ("structured_12", "structured"),
        "dense_count_exact_model": ("dense_6", "unit"),
        "structured_imperfect_effort": ("structured_12", "structured"),
        "sparse_expected_failure": ("sparse_24", "sparse"),
        "zero_driver_effect_negative_control": ("dense_6", "unit"),
        "permuted_arrival_alignment_stress": ("structured_12", "structured"),
        "no_emission_contrast_negative_control": ("dense_6", "unit"),
        "informative_dropout_misspecification_stress": (
            "structured_12",
            "structured",
        ),
        "goal018_continuous_abundance_stress": ("structured_12", "structured"),
        "spatial_frailty_stress": ("structured_12", "structured"),
    }

    observed = {
        scenario_id: (
            core.scenario_schedule_definition(scenario_id).schedule_id,
            core.scenario_schedule_definition(scenario_id).effort_rule,
        )
        for scenario_id in expected
    }

    assert observed == expected
    with pytest.raises(ValueError, match="scenario_id"):
        core.scenario_schedule_definition("unknown")


def test_lro_2a2_012_canonical_schedules_have_exact_counts_order_and_effort(
    canonical_design_cells: tuple[Any, ...],
) -> None:
    core = _core()
    cells = canonical_design_cells

    assert (
        core.build_canonical_schedule(
            cells,
            "process_oracle_observed_transition",
        )
        == ()
    )

    dense = core.build_canonical_schedule(cells, "dense_count_exact_model")
    assert len(dense) == 5225 * 21
    assert (dense[0].cell_id, dense[0].time, dense[0].effort) == (
        cells[0].cell_id,
        0,
        1.0,
    )
    assert (dense[-1].cell_id, dense[-1].time, dense[-1].effort) == (
        cells[-1].cell_id,
        120,
        1.0,
    )
    assert tuple((row.cell_id, row.time) for row in dense) == tuple(
        sorted((row.cell_id, row.time) for row in dense)
    )
    with pytest.raises(FrozenInstanceError):
        dense[0].effort = 2.0

    structured = core.build_canonical_schedule(cells, "structured_imperfect_effort")
    assert len(structured) == 5225 * 11
    assert {row.time for row in structured} == set(range(0, 121, 12))
    assert all(
        row.effort
        == pytest.approx(0.7 + 0.6 * min(max((row.standardized_quality + 2.0) / 4.0, 0.0), 1.0))
        for row in structured
    )

    sparse = core.build_canonical_schedule(cells, "sparse_expected_failure")
    assert len(sparse) == 1306 * 6
    assert {row.time for row in sparse} == set(range(0, 121, 24))
    assert all(row.effort == 0.6 for row in sparse)
    assert tuple((row.cell_id, row.time) for row in sparse) == tuple(
        sorted((row.cell_id, row.time) for row in sparse)
    )


def test_lro_2a2_013_sparse_and_alignment_frames_match_independent_hash_ranking(
    canonical_design_cells: tuple[Any, ...],
) -> None:
    core = _core()
    cells = canonical_design_cells
    cell_ids = tuple(cell.cell_id for cell in cells)

    expected_sparse_rank = sorted(
        cell_ids,
        key=lambda cell_id: (
            sha256(f"023|sparse_expected_failure|cell_id={cell_id}".encode("ascii")).digest(),
            cell_id,
        ),
    )
    expected_sparse = tuple(sorted(expected_sparse_rank[:1306]))
    assert core.sparse_frame_cell_ids(cells) == expected_sparse

    expected_alignment_rank = sorted(
        cell_ids,
        key=lambda cell_id: (
            sha256(f"023|alignment_score|cell_id={cell_id}".encode("ascii")).digest(),
            cell_id,
        ),
    )
    expected_score = tuple(sorted(expected_alignment_rank[:1045]))
    expected_fit = tuple(sorted(set(cell_ids) - set(expected_score)))
    frame = core.alignment_frame(cells)
    assert frame.score_cell_ids == expected_score
    assert frame.fit_cell_ids == expected_fit
    assert len(frame.score_cell_ids) == 1045
    assert len(frame.fit_cell_ids) == 4180
    assert not set(frame.score_cell_ids) & set(frame.fit_cell_ids)


def test_lro_2a2_014_quality_quintiles_use_global_quality_cell_id_rank(
    canonical_design_cells: tuple[Any, ...],
) -> None:
    core = _core()

    labels = core.quality_quintile_labels(canonical_design_cells)

    assert len(labels) == 5225
    assert tuple(labels.count(f"q{index}") for index in range(1, 6)) == (
        1045,
        1045,
        1045,
        1045,
        1045,
    )
    ranked = sorted(
        range(5225),
        key=lambda index: (
            canonical_design_cells[index].standardized_quality,
            canonical_design_cells[index].cell_id,
        ),
    )
    for rank, cell_index in enumerate(ranked):
        assert labels[cell_index] == f"q{min(5, 1 + (5 * rank) // 5225)}"


def test_lro_2a2_015_arrival_permutation_rotates_complete_values_within_blocks() -> None:
    core = _core()
    row_bands = ("north_band", "middle_band", "south_band")
    cells = tuple(
        core.DesignCell(
            cell_id=index,
            standardized_quality=float(index),
            predator_arrival_time=None if index == 2 else float(index * 6),
            row_band=row_bands[(index // 4) % len(row_bands)],
        )
        for index in range(20)
    )

    permuted = core.permute_arrival_within_blocks(cells)

    assert permuted.dtype == np.float64
    assert permuted.shape == (20,)
    assert not permuted.flags.writeable
    np.testing.assert_allclose(
        permuted[:4],
        np.asarray([math.nan, 18.0, 0.0, 6.0], dtype=np.float64),
        equal_nan=True,
    )
    assert np.count_nonzero(~np.isfinite(permuted)) == 1
    np.testing.assert_allclose(
        np.sort(permuted[np.isfinite(permuted)]),
        np.arange(0.0, 120.0, 6.0)[np.arange(20) != 2],
    )


def test_lro_2a2_016_generalized_svd_rank_and_condition_follow_frozen_convention() -> None:
    core = _core()
    matrix_three = np.diag(np.asarray([4.0, 2.0, 1.0], dtype=np.float64))
    matrix_five = np.zeros((7, 5), dtype=np.float64)
    matrix_five[:5, :] = np.diag(np.asarray([5.0, 4.0, 3.0, 2.0, 1.0]))
    deficient = matrix_five.copy()
    deficient[:, -1] = 0.0

    assert core.svd_rank_condition(matrix_three) == pytest.approx((3, 4.0))
    assert core.svd_rank_condition(matrix_five) == pytest.approx((5, 5.0))
    rank, condition = core.svd_rank_condition(deficient)
    assert rank == 4
    assert condition == math.inf
    with pytest.raises(ValueError, match="float64"):
        core.svd_rank_condition(matrix_three.astype(np.float32))


def test_lro_2a2_017_design_diagnostics_keep_provenance_and_roles_distinct() -> None:
    core = _core()
    cells = (
        core.DesignCell(1, -1.0, 0.0, "north_band"),
        core.DesignCell(3, -0.5, 12.0, "north_band"),
        core.DesignCell(8, 0.0, 24.0, "middle_band"),
        core.DesignCell(13, 0.5, 36.0, "middle_band"),
        core.DesignCell(21, 1.0, None, "south_band"),
        core.DesignCell(34, 1.5, 90.0, "south_band"),
    )
    states = np.zeros((6, 21), dtype=np.float64)
    transition_times = np.asarray([6.0, 12.0, 18.0, 24.0, math.nan, math.nan])
    for row, transition_time in enumerate(transition_times):
        if math.isfinite(float(transition_time)):
            states[row, int(transition_time // 6) :] = 1.0
    truth = core.ProcessSimulationTruth(
        cell_ids=np.asarray([cell.cell_id for cell in cells], dtype=np.int64),
        states=states,
        transition_times=transition_times,
    )
    histories = tuple(
        core.AnalystHistory(
            cell_id=cell.cell_id,
            standardized_quality=cell.standardized_quality,
            predator_arrival_time=cell.predator_arrival_time,
            opportunities=(),
        )
        for cell in cells
    )

    potential = core.potential_design_diagnostic(cells)
    oracle = core.process_oracle_truth_at_risk_diagnostic(cells, truth)
    weights = core.joint_plugin_at_risk_weights(histories, _joint_parameters(core))
    plugin = core.joint_plugin_smoothed_at_risk_diagnostic(
        histories,
        _joint_parameters(core),
    )
    failed_plugin = core.joint_plugin_smoothed_at_risk_diagnostic(histories, None)

    assert potential.provenance == "potential_design"
    assert potential.role == "ANALYST-PREFLIGHT"
    assert (potential.n_rows, potential.n_columns, potential.rank) == (120, 3, 3)
    assert potential.passed
    assert oracle.provenance == "process_oracle_truth_at_risk"
    assert oracle.role == "ORACLE-BENCHMARK-ONLY"
    assert oracle.n_rows == 50
    assert oracle.n_columns == 3
    assert plugin.provenance == "joint_plugin_smoothed_at_risk"
    assert plugin.role == "ANALYST-JOINT-PRACTICAL"
    assert plugin.n_rows == 120
    assert plugin.n_columns == 3
    assert plugin.passed
    assert weights.dtype == np.float64
    assert weights.shape == (6, 20)
    assert not weights.flags.writeable
    np.testing.assert_array_equal(weights[:, 0], 1.0)
    first_primitives = core.process_log_primitives(
        standardized_quality=cells[0].standardized_quality,
        predator_arrival_time=cells[0].predator_arrival_time,
        parameters=_process_parameters(core),
    )
    assert weights[0, 1] == pytest.approx(math.exp(first_primitives.log_survival[0]))
    assert not failed_plugin.passed
    assert failed_plugin.failure_reason == "joint_fit_failed_or_nonfinite"


def test_lro_2a2_018_truth_at_risk_cannot_enter_analyst_or_joint_surfaces() -> None:
    core = _core()
    joint_forbidden = {
        "truth",
        "states",
        "transition_time",
        "scenario_id",
        "split",
        "replicate_index",
        "seed",
    }
    schedule_forbidden = joint_forbidden - {"scenario_id"}
    assert not schedule_forbidden & set(inspect.signature(core.build_canonical_schedule).parameters)
    for function in (
        core.potential_design_diagnostic,
        core.joint_plugin_at_risk_weights,
        core.joint_plugin_smoothed_at_risk_diagnostic,
        core.joint_log_likelihood_enumeration,
        core.joint_log_likelihood_forward,
    ):
        assert not joint_forbidden & set(inspect.signature(function).parameters)

    plugin_source = inspect.getsource(core.joint_plugin_smoothed_at_risk_diagnostic)
    weight_source = inspect.getsource(core.joint_plugin_at_risk_weights)
    assert "process_oracle_truth_at_risk" not in plugin_source
    assert "process_oracle_truth_at_risk" not in weight_source
    assert "LatentProcessTruth" not in plugin_source
    assert "ProcessSimulationTruth" not in plugin_source


def test_lro_2a2_019_task_scope_contains_no_live_holdout_execution_work() -> None:
    core = _core()
    source = inspect.getsource(core)
    module_functions = {
        name
        for name, value in inspect.getmembers(core, inspect.isfunction)
        if value.__module__ == CORE_MODULE
    }

    assert "qmc.Halton" not in source
    assert core.CANONICAL_ARTIFACT_RELATIVE_PATH == (
        "artifacts/synth_medium_latent_response_observation_recovery"
    )
    assert (
        sum(
            core.CANONICAL_ARTIFACT_RELATIVE_PATH in " ".join(spec.argv)
            for spec in core.NON_GENERATIVE_COMMAND_REGISTRY
        )
        == 2
    )
    assert not any(
        name.startswith(("write_artifact", "run_scenario", "run_calibration", "run_holdout"))
        for name in module_functions
    )
    assert "run_holdout(" not in source
    assert "run_calibration(" not in source


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ((-1, 0.0, None, "north_band"), "cell_id"),
        ((6048, 0.0, None, "north_band"), "cell_id"),
        ((1, math.nan, None, "north_band"), "standardized_quality"),
        ((1, 0.0, -1.0, "north_band"), "predator_arrival_time"),
        ((1, 0.0, None, "east_band"), "row_band"),
    ],
)
def test_lro_2a2_020_design_cell_schema_rejects_invalid_domain(
    args: tuple[object, ...],
    message: str,
) -> None:
    core = _core()

    with pytest.raises(ValueError, match=message):
        core.DesignCell(*args)


def test_lro_2b01_001_ordered_rate_forward_map_is_literal_at_corners_and_kink() -> None:
    core = _core()

    assert core.RATE_ORDER_GAP == 1e-9
    expected = (
        (0.0, 0.0, 0.25, 0.01),
        (0.0, 1.0, 0.25, 0.25 - 1e-9),
        (1.0, 0.0, 10.0, 0.01),
        (1.0, 1.0, 10.0, 1.0),
        (0.5, 0.25, 5.125, 0.2575),
    )
    for p_frac, q_frac, lambda_present, lambda_quasi in expected:
        rates = core.ordered_rates_from_fractions(p_frac, q_frac)
        assert rates.lambda_present == pytest.approx(lambda_present, rel=0.0, abs=1e-15)
        assert rates.lambda_quasi == pytest.approx(lambda_quasi, rel=0.0, abs=1e-15)
        assert rates.lambda_present > rates.lambda_quasi

    kink_fraction = ((1.0 + core.RATE_ORDER_GAP) - 0.25) / 9.75
    below = core.ordered_rates_from_fractions(kink_fraction - 1e-12, 0.7)
    at = core.ordered_rates_from_fractions(kink_fraction, 0.7)
    above = core.ordered_rates_from_fractions(kink_fraction + 1e-12, 0.7)
    assert below.lambda_quasi < at.lambda_quasi
    assert above.lambda_quasi == pytest.approx(at.lambda_quasi, rel=0.0, abs=1e-15)


@pytest.mark.parametrize(
    ("p_frac", "q_frac"),
    [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0), (0.137, 0.863)],
)
def test_lro_2b01_002_ordered_rate_inverse_round_trips_exact_map(
    p_frac: float,
    q_frac: float,
) -> None:
    core = _core()

    rates = core.ordered_rates_from_fractions(p_frac, q_frac)
    fractions = core.ordered_rate_fractions_from_natural(
        rates.lambda_present,
        rates.lambda_quasi,
    )

    assert fields(type(fractions))[0].name == "p_frac"
    assert fields(type(fractions))[1].name == "q_frac"
    assert fractions.p_frac == pytest.approx(p_frac, rel=0.0, abs=2e-16)
    assert fractions.q_frac == pytest.approx(q_frac, rel=0.0, abs=2e-15)
    with pytest.raises(FrozenInstanceError):
        fractions.p_frac = 0.5


@pytest.mark.parametrize(
    ("function_name", "args"),
    [
        ("ordered_rates_from_fractions", (-1e-15, 0.5)),
        ("ordered_rates_from_fractions", (1.0 + 1e-15, 0.5)),
        ("ordered_rates_from_fractions", (0.5, -1e-15)),
        ("ordered_rates_from_fractions", (0.5, 1.0 + 1e-15)),
        ("ordered_rates_from_fractions", (math.nan, 0.5)),
        ("ordered_rates_from_fractions", (0.5, math.inf)),
        ("ordered_rates_from_fractions", (True, 0.5)),
        ("ordered_rates_from_fractions", (_ArithmeticFloat(0.5), 0.5)),
        ("ordered_rate_fractions_from_natural", (0.249, 0.1)),
        ("ordered_rate_fractions_from_natural", (10.001, 0.1)),
        ("ordered_rate_fractions_from_natural", (4.0, 0.009)),
        ("ordered_rate_fractions_from_natural", (4.0, 1.001)),
        ("ordered_rate_fractions_from_natural", (0.25, 0.25)),
        ("ordered_rate_fractions_from_natural", (0.25, 0.3)),
        ("ordered_rate_fractions_from_natural", (math.inf, 0.1)),
        ("ordered_rate_fractions_from_natural", (4.0, math.nan)),
    ],
)
def test_lro_2b01_003_ordered_rate_maps_reject_invalid_inputs(
    function_name: str,
    args: tuple[object, object],
) -> None:
    core = _core()

    with pytest.raises(ValueError):
        getattr(core, function_name)(*args)


def test_lro_2b01_004_conditional_profile_rate_maps_are_literal_and_strict() -> None:
    core = _core()

    fixed_present = core.rates_with_fixed_lambda_present(0.6, 1.0)
    assert fixed_present.lambda_present == 0.6
    assert fixed_present.lambda_quasi == pytest.approx(0.6 - 1e-9, abs=1e-15)
    capped_present = core.rates_with_fixed_lambda_present(4.0, 1.0)
    assert capped_present == EffectiveCountRates(lambda_present=4.0, lambda_quasi=1.0)

    fixed_quasi = core.rates_with_fixed_lambda_quasi(0.6, 0.0)
    assert fixed_quasi.lambda_quasi == 0.6
    assert fixed_quasi.lambda_present == pytest.approx(0.6 + 1e-9, abs=1e-15)
    high = core.rates_with_fixed_lambda_quasi(1.0, 1.0)
    assert high == EffectiveCountRates(lambda_present=10.0, lambda_quasi=1.0)

    invalid = (
        (core.rates_with_fixed_lambda_present, (0.249, 0.0)),
        (core.rates_with_fixed_lambda_present, (10.0001, 0.5)),
        (core.rates_with_fixed_lambda_quasi, (0.009, 0.5)),
        (core.rates_with_fixed_lambda_quasi, (1.001, 0.5)),
        (core.rates_with_fixed_lambda_quasi, (1.0, True)),
    )
    for function, args in invalid:
        with pytest.raises(ValueError):
            function(*args)


def test_lro_2b01_005_projection_and_dedup_boundaries_are_inclusive() -> None:
    core = _core()

    assert core.COORDINATE_PROJECTION_TOLERANCE == 1e-12
    assert core.START_DEDUPLICATION_TOLERANCE == 1e-10
    assert core.project_unit_coordinate(-1e-12) == 0.0
    assert core.project_unit_coordinate(1.0 + 1e-12) == 1.0
    with pytest.raises(ValueError, match="projection"):
        core.project_unit_coordinate(float(np.nextafter(-1e-12, -math.inf)))
    with pytest.raises(ValueError, match="projection"):
        core.project_unit_coordinate(float(np.nextafter(1.0 + 1e-12, math.inf)))
    with pytest.raises(ValueError, match="projection"):
        core.project_unit_coordinate(-1.0001e-12)
    with pytest.raises(ValueError, match="projection"):
        core.project_unit_coordinate(1.0 + 1.1e-12)

    starts = (
        np.asarray([0.1, 0.2], dtype=np.float64),
        np.asarray([0.1 + 1e-10, 0.2], dtype=np.float64),
        np.asarray([0.1 + 1.0001e-10, 0.2], dtype=np.float64),
        np.asarray([0.8, 0.9], dtype=np.float64),
    )
    deduplicated = core.deduplicate_coordinate_starts(starts)

    assert len(deduplicated) == 3
    np.testing.assert_array_equal(deduplicated[0], starts[0])
    np.testing.assert_array_equal(deduplicated[1], starts[2])
    np.testing.assert_array_equal(deduplicated[2], starts[3])
    for start in deduplicated:
        assert start.dtype == np.float64
        assert not start.flags.writeable


def _independent_radical_inverse(index: int, base: int) -> float:
    inverse = 0.0
    factor = 1.0 / base
    remaining = index
    while remaining:
        remaining, digit = divmod(remaining, base)
        inverse += digit * factor
        factor /= base
    return inverse


def test_lro_2b02_001_positive_halton_starts_match_literal_eight_row_table() -> None:
    core = _core()
    literal = np.asarray(
        [
            [-6.0, -0.9, -1.08, 0.178571428571, 0.131818181818],
            [-7.8, 0.9, -0.36, 0.307142857143, 0.213636363636],
            [-4.2, -2.1, 0.36, 0.435714285714, 0.295454545455],
            [-8.7, -0.3, 1.08, 0.564285714286, 0.377272727273],
            [-5.1, 1.5, -1.656, 0.692857142857, 0.459090909091],
            [-6.9, -1.5, -0.936, 0.821428571429, 0.540909090909],
            [-3.3, 0.3, -0.216, 0.0683673469388, 0.622727272727],
            [-9.15, 2.1, 0.504, 0.19693877551, 0.704545454545],
        ],
        dtype=np.float64,
    )

    starts = core.halton_optimization_starts(8)

    assert starts.dtype == np.float64
    assert starts.shape == (8, 5)
    assert not starts.flags.writeable
    np.testing.assert_allclose(starts, literal, rtol=0.0, atol=5e-13)


def test_lro_2b02_002_halton_values_use_indices_one_to_sixteen_and_frozen_bases() -> None:
    core = _core()
    bases = (2, 3, 5, 7, 11)
    supports = (
        core.ALPHA_SUPPORT,
        core.BETA_DRIVER_SUPPORT,
        core.BETA_QUALITY_SUPPORT,
        (0.0, 1.0),
        (0.0, 1.0),
    )
    expected = np.empty((16, 5), dtype=np.float64)
    for row, index in enumerate(range(1, 17)):
        for column, (base, support) in enumerate(zip(bases, supports, strict=True)):
            unit = 0.05 + 0.90 * _independent_radical_inverse(index, base)
            expected[row, column] = support[0] + (support[1] - support[0]) * unit

    starts = core.halton_optimization_starts(16)

    np.testing.assert_array_equal(starts, expected)
    np.testing.assert_array_equal(starts[:8], core.halton_optimization_starts(8))
    with pytest.raises(ValueError, match="8 or 16"):
        core.halton_optimization_starts(0)
    with pytest.raises(ValueError, match="8 or 16"):
        core.halton_optimization_starts(9)
    with pytest.raises(ValueError, match="8 or 16"):
        core.halton_optimization_starts(True)


def test_lro_2b02_003_oracle_and_joint_starts_are_exact_same_row_subsets() -> None:
    core = _core()
    global_starts = core.global_optimization_starts()
    process_starts = core.process_oracle_optimization_starts()
    observation_starts = core.observation_oracle_optimization_starts()

    np.testing.assert_array_equal(global_starts, core.halton_optimization_starts(8))
    np.testing.assert_array_equal(process_starts, global_starts[:, :3])
    np.testing.assert_array_equal(observation_starts, global_starts[:, 3:5])
    assert process_starts.shape == (8, 3)
    assert observation_starts.shape == (8, 2)
    assert not global_starts.flags.writeable
    assert not process_starts.flags.writeable
    assert not observation_starts.flags.writeable


def test_lro_2b02_004_start_surfaces_accept_no_data_truth_rng_or_scenario_inputs() -> None:
    core = _core()
    functions = (
        core.global_optimization_starts,
        core.process_oracle_optimization_starts,
        core.observation_oracle_optimization_starts,
    )

    assert all(not inspect.signature(function).parameters for function in functions)
    sources = "\n".join(inspect.getsource(function) for function in functions)
    for forbidden in (
        "history",
        "truth",
        "scenario",
        "split",
        "replicate",
        "rng",
        "random",
        "seed",
    ):
        assert forbidden not in sources.lower()


def _batch_histories(core: Any, *, interval_count: int) -> tuple[Any, ...]:
    opportunities = {
        1: (
            (_op(core, time=0, count=2, effort=0.7), _op(core, time=6, count=0)),
            (_op(core, time=6, count=1, effort=1.2),),
            (),
        ),
        2: (
            (_op(core, time=0, count=2, effort=0.7), _op(core, time=12, count=0)),
            (_op(core, time=6, count=1, effort=1.2),),
            (),
        ),
        20: (
            (
                _op(core, time=0, count=2, effort=0.7),
                _op(core, time=18, count=1, effort=1.2),
                _op(core, time=120, count=0, effort=0.6),
            ),
            (_op(core, time=6, count=1), _op(core, time=54, count=0, effort=1.3)),
            (),
        ),
    }[interval_count]
    metadata = (
        (2, -1.0, 0.0),
        (10, 0.25, None),
        (31, 1.25, 60.0),
    )
    return tuple(
        core.AnalystHistory(
            cell_id=cell_id,
            standardized_quality=quality,
            predator_arrival_time=arrival,
            opportunities=cell_opportunities,
        )
        for (cell_id, quality, arrival), cell_opportunities in zip(
            metadata,
            opportunities,
            strict=True,
        )
    )


def _issued_fit_frame(
    core: Any,
    scenario_id: str = "permuted_arrival_alignment_stress",
) -> Any:
    return core.issue_analyst_fit_frame(scenario_id)


def _authoritative_fit_histories(
    core: Any,
    scenario_id: str = "permuted_arrival_alignment_stress",
) -> tuple[Any, ...]:
    frame = _issued_fit_frame(core, scenario_id)
    return tuple(
        core.AnalystHistory(
            cell_id=cell_id,
            standardized_quality=float((index % 5) - 2) / 2.0,
            predator_arrival_time=float((index % 21) * 6),
            opportunities=(core.CountOpportunity(time=0, count=0, effort=1.0),),
        )
        for index, cell_id in enumerate(frame.cell_ids)
    )


def test_lro_2b03_001_analyst_batch_is_immutable_canonical_and_truth_free() -> None:
    core = _core()
    histories = _batch_histories(core, interval_count=20)

    batch = core.analyst_batch_from_histories(histories)

    assert {field.name for field in fields(type(batch))} == {
        "cell_ids",
        "standardized_quality",
        "predator_arrival_time",
        "counts",
        "efforts",
        "retained_mask",
    }
    assert not {field.name for field in fields(type(batch))} & {
        "truth",
        "states",
        "transition_times",
        "generating_parameters",
        "scenario_id",
        "split",
        "replicate_index",
        "seed",
    }
    np.testing.assert_array_equal(batch.cell_ids, np.asarray([2, 10, 31], dtype=np.int64))
    assert batch.counts.shape == (3, 21)
    assert batch.efforts.shape == (3, 21)
    assert batch.retained_mask.shape == (3, 21)
    assert batch.retained_mask.dtype == np.bool_
    assert int(batch.retained_mask.sum()) == 5
    assert math.isnan(float(batch.predator_arrival_time[1]))
    for array in (
        batch.cell_ids,
        batch.standardized_quality,
        batch.predator_arrival_time,
        batch.counts,
        batch.efforts,
        batch.retained_mask,
    ):
        assert array.flags.c_contiguous
        assert not array.flags.writeable
        with pytest.raises(ValueError):
            array.setflags(write=True)
    with pytest.raises(FrozenInstanceError):
        batch.counts = batch.counts.copy()


@pytest.mark.parametrize("interval_count", [1, 2, 20])
def test_lro_2b03_002_batched_likelihood_matches_scalar_enumeration_and_forward(
    interval_count: int,
) -> None:
    core = _core()
    histories = _batch_histories(core, interval_count=interval_count)
    parameters = _joint_parameters(core)
    batch = core.analyst_batch_from_histories(histories)

    cell_values = core.batched_joint_cell_log_likelihoods(
        batch,
        parameters,
        interval_count=interval_count,
    )
    total = core.batched_joint_log_likelihood(
        batch,
        parameters,
        interval_count=interval_count,
    )
    enumerated = np.asarray(
        [
            core.joint_log_likelihood_enumeration(
                history,
                parameters,
                interval_count=interval_count,
            )
            for history in histories
        ],
        dtype=np.float64,
    )
    forwarded = np.asarray(
        [
            core.joint_log_likelihood_forward(
                history,
                parameters,
                interval_count=interval_count,
            )
            for history in histories
        ],
        dtype=np.float64,
    )

    assert cell_values.dtype == np.float64
    assert not cell_values.flags.writeable
    np.testing.assert_allclose(cell_values, enumerated, rtol=0.0, atol=2e-12)
    np.testing.assert_allclose(cell_values, forwarded, rtol=0.0, atol=2e-12)
    assert total == pytest.approx(float(enumerated.sum(dtype=np.float64)), abs=2e-12)


@pytest.mark.parametrize("interval_count", [1, 2, 20])
def test_lro_2b03_003_batched_posterior_matches_scalar_cell_by_cell(
    interval_count: int,
) -> None:
    core = _core()
    histories = _batch_histories(core, interval_count=interval_count)
    parameters = _joint_parameters(core)
    batch = core.analyst_batch_from_histories(histories)

    weights = core.batched_joint_path_posterior_weights(
        batch,
        parameters,
        interval_count=interval_count,
    )

    assert weights.shape == (3, interval_count + 1)
    assert weights.dtype == np.float64
    assert not weights.flags.writeable
    np.testing.assert_allclose(weights.sum(axis=1), 1.0, rtol=0.0, atol=2e-15)
    for row, history in enumerate(histories):
        expected = core.joint_path_posterior_weights(
            history,
            parameters,
            interval_count=interval_count,
        )
        np.testing.assert_allclose(weights[row], expected, rtol=2e-13, atol=2e-15)


def test_lro_2b03_004_batch_kernel_is_genuinely_separate_from_scalar_oracles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    histories = _batch_histories(core, interval_count=20)
    batch = core.analyst_batch_from_histories(histories)
    parameters = _joint_parameters(core)

    def forbidden(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("batched kernel called a scalar oracle")

    for name in (
        "joint_log_likelihood_enumeration",
        "joint_log_likelihood_forward",
        "joint_path_posterior_weights",
        "_joint_log_path_terms",
        "process_log_primitives",
        "state_count_log_probability",
    ):
        monkeypatch.setattr(core, name, forbidden)

    assert math.isfinite(core.batched_joint_log_likelihood(batch, parameters))
    weights = core.batched_joint_path_posterior_weights(batch, parameters)
    np.testing.assert_allclose(weights.sum(axis=1), 1.0, atol=2e-15)


def test_lro_2b03_005_batch_rejects_noncanonical_or_out_of_horizon_inputs() -> None:
    core = _core()
    histories = _batch_histories(core, interval_count=20)

    with pytest.raises(ValueError, match="sorted"):
        core.analyst_batch_from_histories(tuple(reversed(histories)))
    batch = core.analyst_batch_from_histories(histories)
    with pytest.raises(ValueError, match="process horizon"):
        core.batched_joint_log_likelihood(batch, _joint_parameters(core), interval_count=2)


def test_lro_2b03_006_plugin_at_risk_uses_equivalent_batched_posterior(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    histories = _batch_histories(core, interval_count=20)
    parameters = _joint_parameters(core)
    scalar_path_weights = np.asarray(
        [core.joint_path_posterior_weights(history, parameters) for history in histories],
        dtype=np.float64,
    )
    expected = np.empty((len(histories), 20), dtype=np.float64)
    expected[:, 0] = 1.0
    for interval_index in range(1, 20):
        expected[:, interval_index] = scalar_path_weights[:, interval_index:].sum(
            axis=1,
            dtype=np.float64,
        )

    original_batched = core.batched_joint_path_posterior_weights
    batched_calls = 0

    def recording_batched(*args: object, **kwargs: object) -> Any:
        nonlocal batched_calls
        batched_calls += 1
        return original_batched(*args, **kwargs)

    def forbidden_scalar(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("plug-in gate called the scalar posterior oracle")

    monkeypatch.setattr(core, "batched_joint_path_posterior_weights", recording_batched)
    monkeypatch.setattr(core, "joint_path_posterior_weights", forbidden_scalar)
    observed = core.joint_plugin_at_risk_weights(histories, parameters)

    assert batched_calls == 1
    assert observed.dtype == np.float64
    assert not observed.flags.writeable
    np.testing.assert_allclose(observed, expected, rtol=2e-13, atol=2e-15)


def test_lro_2b04_001_optimizer_adapter_uses_one_literal_lbfgsb_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    x0 = core.global_optimization_starts()[0]
    calls: list[dict[str, object]] = []

    def fake_minimize(
        objective: Any,
        received_x0: np.ndarray[Any, np.dtype[np.float64]],
        *,
        method: str,
        jac: str,
        bounds: tuple[tuple[float, float], ...],
        options: dict[str, object],
    ) -> SimpleNamespace:
        calls.append(
            {
                "x0": received_x0.copy(),
                "method": method,
                "jac": jac,
                "bounds": bounds,
                "options": options.copy(),
            }
        )
        return SimpleNamespace(
            success=True,
            status=0,
            fun=objective(received_x0),
            x=received_x0.copy(),
        )

    monkeypatch.setattr(core.scipy.optimize, "minimize", fake_minimize)
    attempt = core._run_optimizer_start(
        "joint",
        lambda coordinates: float(np.square(coordinates - x0).sum()),
        start_index=1,
        x0=x0,
    )

    assert attempt.succeeded
    assert attempt.start_index == 1
    assert attempt.objective_value == 0.0
    assert attempt.log_likelihood == 0.0
    assert len(calls) == 1
    np.testing.assert_array_equal(calls[0]["x0"], x0)
    assert calls[0]["method"] == "L-BFGS-B"
    assert calls[0]["jac"] == "3-point"
    assert calls[0]["bounds"] == core.optimization_bounds("joint")
    assert calls[0]["options"] == {
        "ftol": 1e-12,
        "gtol": 1e-6,
        "maxiter": 1000,
        "maxfun": 20000,
        "maxls": 50,
        "finite_diff_rel_step": 1e-5,
    }


def test_lro_2b04_002_optimizer_subsets_map_exact_coordinates_to_natural_types() -> None:
    core = _core()
    expected = {
        "process_oracle": (3, core.ProcessParameters),
        "observation_oracle": (2, EffectiveCountRates),
        "joint": (5, core.JointParameters),
    }

    for kind, (column_count, expected_type) in expected.items():
        starts = core.optimization_starts(kind)
        bounds = core.optimization_bounds(kind)
        natural = core.optimization_coordinates_to_natural(kind, starts[0])
        assert starts.shape == (8, column_count)
        assert len(bounds) == column_count
        assert type(natural) is expected_type
        assert not starts.flags.writeable
    assert core.optimization_bounds("process_oracle") == (
        core.ALPHA_SUPPORT,
        core.BETA_DRIVER_SUPPORT,
        core.BETA_QUALITY_SUPPORT,
    )
    assert core.optimization_bounds("observation_oracle") == ((0.0, 1.0), (0.0, 1.0))
    assert core.optimization_bounds("joint")[-2:] == ((0.0, 1.0), (0.0, 1.0))
    with pytest.raises(ValueError, match="optimizer kind"):
        core.optimization_starts("truth_oracle")


def test_lro_2b04_003_result_validator_rejects_every_invalid_result_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    x0 = core.global_optimization_starts()[0]
    invalid_results = [
        SimpleNamespace(success=False, status=0, fun=0.0, x=x0.copy()),
        SimpleNamespace(success=True, status=1, fun=0.0, x=x0.copy()),
        SimpleNamespace(success=True, status=0, fun=math.nan, x=x0.copy()),
        SimpleNamespace(success=True, status=0, fun=0.0, x=np.full(5, math.inf)),
        SimpleNamespace(success=True, status=0, fun=0.0, x=np.zeros(4)),
        SimpleNamespace(success=True, status=0, fun=0.0, x=np.asarray([-11, 0, 0, 0.5, 0.5])),
    ]
    calls = 0

    def fake_minimize(*args: object, **kwargs: object) -> SimpleNamespace:
        del args, kwargs
        nonlocal calls
        result = invalid_results[calls]
        calls += 1
        return result

    monkeypatch.setattr(core.scipy.optimize, "minimize", fake_minimize)
    attempts = tuple(
        core._run_optimizer_start("joint", lambda _: 0.0, start_index=index + 1, x0=x0)
        for index in range(len(invalid_results))
    )

    assert calls == len(invalid_results)
    assert not any(attempt.succeeded for attempt in attempts)
    assert all(attempt.coordinates is None for attempt in attempts)
    assert all(attempt.log_likelihood is None for attempt in attempts)
    assert all(attempt.failure_reason for attempt in attempts)

    monkeypatch.setattr(
        core.scipy.optimize,
        "minimize",
        lambda *args, **kwargs: SimpleNamespace(
            success=True,
            status=0,
            fun=0.0,
            x=x0.copy(),
        ),
    )

    def invalid_natural(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise ValueError("injected invalid natural transform")

    monkeypatch.setattr(core, "optimization_coordinates_to_natural", invalid_natural)
    transform_failure = core._run_optimizer_start(
        "joint",
        lambda _: 0.0,
        start_index=7,
        x0=x0,
    )
    assert not transform_failure.succeeded
    assert transform_failure.failure_reason == "invalid_result_coordinates_or_natural_map"


def test_lro_2b04_004_raised_or_nonfinite_evaluation_invalidates_a_finite_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    x0 = core.global_optimization_starts()[0]

    def raising_minimize(objective: Any, received_x0: Any, **kwargs: object) -> Any:
        del kwargs
        objective(received_x0)
        raise AssertionError("unreachable")

    monkeypatch.setattr(core.scipy.optimize, "minimize", raising_minimize)

    def raising_objective(_: Any) -> float:
        raise RuntimeError("injected objective failure")

    raised = core._run_optimizer_start(
        "joint",
        raising_objective,
        start_index=1,
        x0=x0,
    )
    assert not raised.succeeded
    assert "objective" in raised.failure_reason

    def finite_after_nan(objective: Any, received_x0: Any, **kwargs: object) -> Any:
        del kwargs
        bad = received_x0.copy()
        bad[0] += 0.125
        assert math.isinf(objective(bad))
        return SimpleNamespace(success=True, status=0, fun=0.0, x=received_x0.copy())

    def sometimes_nan(coordinates: Any) -> float:
        return math.nan if coordinates[0] != x0[0] else 0.0

    monkeypatch.setattr(core.scipy.optimize, "minimize", finite_after_nan)
    nonfinite = core._run_optimizer_start(
        "joint",
        sometimes_nan,
        start_index=2,
        x0=x0,
    )
    assert not nonfinite.succeeded
    assert nonfinite.failure_reason == "invalid_or_nonfinite_objective_evaluation"


def test_lro_2b04_005_multistart_continues_sorts_and_applies_six_of_eight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    starts = core.global_optimization_starts()
    responses: list[object] = [
        RuntimeError("injected start failure"),
        SimpleNamespace(success=True, status=0, fun=math.nan, x=starts[1].copy()),
        SimpleNamespace(success=True, status=0, fun=-10.0, x=starts[2].copy()),
        SimpleNamespace(success=True, status=0, fun=-10.0, x=starts[3].copy()),
        SimpleNamespace(success=True, status=0, fun=-9.0, x=starts[4].copy()),
        SimpleNamespace(success=True, status=0, fun=-8.0, x=starts[5].copy()),
        SimpleNamespace(success=True, status=0, fun=-7.0, x=starts[6].copy()),
        SimpleNamespace(success=True, status=0, fun=-6.0, x=starts[7].copy()),
    ]
    call_count = 0

    def fake_minimize(*args: object, **kwargs: object) -> Any:
        del args, kwargs
        nonlocal call_count
        response = responses[call_count]
        call_count += 1
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(core.scipy.optimize, "minimize", fake_minimize)
    fit = core._run_multistart_optimization("joint", lambda _: 0.0)

    assert call_count == 8
    assert len(fit.attempts) == 8
    assert fit.converged_start_count == 6
    assert fit.converged
    assert tuple(row.start_index for row in fit.ranked_successes) == (3, 4, 5, 6, 7, 8)
    assert fit.best_start_index == 3
    assert fit.best_log_likelihood == 10.0
    assert fit.best_coordinates is not None and not fit.best_coordinates.flags.writeable


def test_lro_2b04_006_best_two_rule_is_inclusive_and_tie_sort_uses_start_index() -> None:
    core = _core()
    best = 100.0
    tolerance = 1e-6 * (1.0 + abs(best))

    assert core.best_two_log_likelihoods_agree(best, best - tolerance)
    assert core.best_two_log_likelihoods_agree(best, best - tolerance + 1e-12)
    assert not core.best_two_log_likelihoods_agree(best, best - tolerance - 1e-12)
    immediate_above = float(np.nextafter(1e-6, math.inf))
    assert not core.best_two_log_likelihoods_agree(0.0, -immediate_above)

    starts = core.global_optimization_starts()
    attempts = tuple(
        core.OptimizerStartResult(
            start_index=index,
            start_coordinates=starts[index - 1],
            succeeded=index <= 5,
            coordinates=starts[index - 1] if index <= 5 else None,
            objective_value=-3.0 if index <= 5 else None,
            log_likelihood=3.0 if index <= 5 else None,
            failure_reason=None if index <= 5 else "injected",
        )
        for index in range(1, 9)
    )
    classified = core.classify_multistart_attempts("joint", attempts)
    assert not classified.converged
    assert classified.converged_start_count == 5
    assert tuple(row.start_index for row in classified.ranked_successes) == (1, 2, 3, 4, 5)


def test_lro_2b05_001_one_rank_diagnostic_handles_three_and_five_columns() -> None:
    core = _core()
    matrix_three = np.diag(np.asarray([4.0, 2.0, 1.0], dtype=np.float64))
    matrix_five = np.zeros((7, 5), dtype=np.float64)
    matrix_five[:5] = np.diag(np.asarray([5.0, 4.0, 3.0, 2.0, 1.0]))

    three = core.matrix_rank_diagnostic(
        matrix_three,
        required_columns=3,
        provenance="potential_design",
        role="ANALYST-PREFLIGHT",
    )
    five = core.matrix_rank_diagnostic(
        matrix_five,
        required_columns=5,
        provenance="canonical_noncollision_audit",
        role="SUPPORTING-LOCAL-NONCOLLISION",
    )

    assert (three.n_rows, three.n_columns, three.rank, three.condition_number) == (
        3,
        3,
        3,
        4.0,
    )
    assert (five.n_rows, five.n_columns, five.rank, five.condition_number) == (
        7,
        5,
        5,
        5.0,
    )
    assert three.passed and five.passed
    assert three.provenance == "potential_design"
    assert five.provenance == "canonical_noncollision_audit"


def test_lro_2b05_002_rank_and_condition_failures_are_literal() -> None:
    core = _core()
    deficient = np.eye(5, dtype=np.float64)
    deficient[:, -1] = 0.0
    condition_boundary = np.diag(np.asarray([1.0, 1.0, 1.0, 1.0, 1e-8], dtype=np.float64))

    rank_failure = core.matrix_rank_diagnostic(
        deficient,
        required_columns=5,
        provenance="injected",
        role="TEST",
    )
    condition_failure = core.matrix_rank_diagnostic(
        condition_boundary,
        required_columns=5,
        provenance="injected",
        role="TEST",
    )

    assert rank_failure.rank == 4
    assert rank_failure.condition_number == math.inf
    assert not rank_failure.passed
    assert condition_failure.rank == 5
    assert condition_failure.condition_number == pytest.approx(1e8)
    assert not condition_failure.passed


def test_lro_2b05_003_rank_diagnostic_rejects_wrong_empty_and_nonfinite_matrices() -> None:
    core = _core()
    invalid = (
        np.eye(3, dtype=np.float32),
        np.empty((0, 3), dtype=np.float64),
        np.empty((3, 0), dtype=np.float64),
        np.asarray([[1.0, 0.0, math.nan]], dtype=np.float64),
    )

    for matrix in invalid:
        with pytest.raises(ValueError):
            core.matrix_rank_diagnostic(
                matrix,
                required_columns=matrix.shape[1],
                provenance="injected",
                role="TEST",
            )
    with pytest.raises(ValueError, match="required_columns"):
        core.matrix_rank_diagnostic(
            np.eye(3, dtype=np.float64),
            required_columns=5,
            provenance="injected",
            role="TEST",
        )


@pytest.fixture(scope="module")
def canonical_source_arrival_cells() -> tuple[Any, ...]:
    core = _core()
    spread_module = import_module("spatext.synth.medium.spread_impact")
    spread = spread_module.build_synth_medium_spread_impact_review_pack()
    passable_rows = tuple(
        sorted(
            (row for row in spread.cell_truth_rows if row.landscape_cell.passability != "water"),
            key=lambda row: row.landscape_cell.cell_id,
        )
    )
    quality = np.asarray(
        [row.landscape_cell.quality for row in passable_rows],
        dtype=np.float64,
    )
    standardized = (quality - quality.mean()) / quality.std(ddof=0)
    cells = tuple(
        core.DesignCell(
            cell_id=row.landscape_cell.cell_id,
            standardized_quality=float(standardized[index]),
            predator_arrival_time=row.predator_arrival_time,
            row_band=row.landscape_cell.row_band,
        )
        for index, row in enumerate(passable_rows)
    )
    assert len(cells) == 5225
    return cells


@pytest.fixture(scope="module")
def canonical_audit_designs(
    canonical_source_arrival_cells: tuple[Any, ...],
) -> dict[str, Any]:
    core = _core()
    return {
        schedule_id: core.audit_design_from_schedule(
            core.build_canonical_schedule(canonical_source_arrival_cells, scenario_id),
            schedule_id=schedule_id,
        )
        for schedule_id, scenario_id in (
            ("dense", "dense_count_exact_model"),
            ("structured", "structured_imperfect_effort"),
            ("sparse", "sparse_expected_failure"),
        )
    }


@pytest.fixture(scope="module")
def canonical_nine_audit_preflight(
    canonical_audit_designs: dict[str, Any],
) -> Any:
    core = _core()
    return core.run_nine_audit_preflight(
        tuple(
            canonical_audit_designs[schedule_id]
            for schedule_id in ("dense", "structured", "sparse")
        )
    )


def test_lro_2b06_001_audit_vector_is_stable_canonical_and_block_ordered() -> None:
    core = _core()
    schedule = (
        core.ScheduledOpportunity(2, 0, 1.0, -0.5, 0.0),
        core.ScheduledOpportunity(2, 6, 2.0, -0.5, 0.0),
        core.ScheduledOpportunity(10, 0, 0.5, 0.75, None),
        core.ScheduledOpportunity(10, 12, 1.5, 0.75, None),
    )
    design = core.audit_design_from_schedule(schedule, schedule_id="toy")
    parameters = _joint_parameters(core)

    vector = core.canonical_audit_vector(design, parameters)

    expected_mu: list[float] = []
    expected_log_p0: list[float] = []
    for opportunity in schedule:
        if opportunity.time == 0:
            survival = 1.0
        else:
            cumulative_hazard = 0.0
            for endpoint in range(6, opportunity.time + 1, 6):
                driver = (
                    0.0
                    if opportunity.predator_arrival_time is None
                    else max((endpoint - opportunity.predator_arrival_time) / 30.0, 0.0)
                )
                eta = -6.0 + 1.25 * driver - 0.60 * opportunity.standardized_quality
                cumulative_hazard += math.exp(eta)
            survival = math.exp(-cumulative_hazard)
        mean = opportunity.effort * (4.0 * survival + 0.15 * (1.0 - survival))
        p0 = survival * math.exp(-opportunity.effort * 4.0) + (1.0 - survival) * math.exp(
            -opportunity.effort * 0.15
        )
        expected_mu.append(math.log1p(mean))
        expected_log_p0.append(math.log(p0))
    expected = np.asarray(expected_mu + expected_log_p0, dtype=np.float64)

    assert {field.name for field in fields(type(design))} == {
        "schedule_id",
        "cell_ids",
        "standardized_quality",
        "predator_arrival_time",
        "opportunity_cell_index",
        "opportunity_time_index",
        "efforts",
    }
    assert not hasattr(design, "counts")
    assert not hasattr(design, "truth")
    assert vector.dtype == np.float64
    assert not vector.flags.writeable
    np.testing.assert_allclose(vector, expected, rtol=2e-14, atol=2e-15)
    np.testing.assert_allclose(vector[:4], expected_mu, rtol=2e-14, atol=2e-15)
    np.testing.assert_allclose(vector[4:], expected_log_p0, rtol=2e-14, atol=2e-15)


def test_lro_2b06_002_scaled_jacobian_uses_literal_natural_steps_and_widths() -> None:
    core = _core()
    schedule = (
        core.ScheduledOpportunity(2, 0, 1.0, -0.5, 0.0),
        core.ScheduledOpportunity(2, 6, 2.0, -0.5, 0.0),
        core.ScheduledOpportunity(10, 0, 0.5, 0.75, None),
        core.ScheduledOpportunity(10, 12, 1.5, 0.75, None),
    )
    design = core.audit_design_from_schedule(schedule, schedule_id="toy")
    parameters = _joint_parameters(core)

    jacobian = core.scaled_audit_jacobian(design, parameters)

    assert core.AUDIT_CENTRAL_DIFFERENCE_FRACTION == 1e-5
    assert core.NATURAL_PARAMETER_SUPPORT_WIDTHS == (8.0, 6.0, 4.0, 0.99, 9.75)
    assert core.AUDIT_CENTRAL_DIFFERENCE_STEPS == (
        8e-5,
        6e-5,
        4e-5,
        9.9e-6,
        9.75e-5,
    )
    assert jacobian.shape == (8, 5)
    assert jacobian.dtype == np.float64
    assert not jacobian.flags.writeable

    step = core.AUDIT_CENTRAL_DIFFERENCE_STEPS[1]
    plus = core.JointParameters(-6.0, 1.25 + step, -0.60, 0.15, 4.0)
    minus = core.JointParameters(-6.0, 1.25 - step, -0.60, 0.15, 4.0)
    expected_column = (
        (core.canonical_audit_vector(design, plus) - core.canonical_audit_vector(design, minus))
        / (2.0 * step)
        * core.NATURAL_PARAMETER_SUPPORT_WIDTHS[1]
    )
    np.testing.assert_allclose(jacobian[:, 1], expected_column, rtol=0.0, atol=1e-12)


def test_lro_2b06_003_all_nine_canonical_local_audits_have_rank_five(
    canonical_audit_designs: dict[str, Any],
) -> None:
    core = _core()
    targets = {
        "A": core.JointParameters(-6.0, 1.25, -0.60, 0.15, 4.0),
        "B": core.JointParameters(-5.0, 0.50, 0.50, 0.30, 2.50),
        "C": core.JointParameters(-7.0, -0.50, -1.00, 0.60, 6.00),
    }

    diagnostics = {
        (schedule_id, target_id): core.canonical_audit_jacobian_diagnostic(
            design,
            target,
        )
        for schedule_id, design in canonical_audit_designs.items()
        for target_id, target in targets.items()
    }

    assert len(diagnostics) == 9
    for (schedule_id, target_id), diagnostic in diagnostics.items():
        assert diagnostic.provenance == f"canonical_noncollision_audit:{schedule_id}:{target_id}"
        assert diagnostic.role == "SUPPORTING-LOCAL-NONCOLLISION"
        assert diagnostic.n_columns == 5
        assert diagnostic.rank == 5
        assert diagnostic.condition_number < 1e8
        assert diagnostic.passed


def test_lro_2b06_004_audit_and_design_diagnostics_use_five_and_three_columns(
    canonical_audit_designs: dict[str, Any],
) -> None:
    core = _core()
    dense_design = canonical_audit_designs["dense"]
    audit = core.canonical_audit_jacobian_diagnostic(
        dense_design,
        core.JointParameters(-6.0, 1.25, -0.60, 0.15, 4.0),
    )
    cells = tuple(
        core.DesignCell(
            cell_id=int(cell_id),
            standardized_quality=float(quality),
            predator_arrival_time=(None if math.isnan(float(arrival)) else float(arrival)),
            row_band="north_band",
        )
        for cell_id, quality, arrival in zip(
            dense_design.cell_ids,
            dense_design.standardized_quality,
            dense_design.predator_arrival_time,
            strict=True,
        )
    )
    potential = core.potential_design_diagnostic(cells)

    assert (audit.n_columns, audit.rank) == (5, 5)
    assert (potential.n_columns, potential.rank) == (3, 3)


def test_lro_2b07_001_inverse_rmse_and_distance_frontier_are_literal() -> None:
    core = _core()
    assert core.INVERSE_AUDIT_RMSE_THRESHOLD == 5e-5
    assert core.INVERSE_AUDIT_DISTANCE_THRESHOLD == 0.01
    assert core.INVERSE_AUDIT_REQUIRED_SUCCESSES == 12
    assert core.inverse_audit_rmse(
        np.asarray([0.0, 1.0], dtype=np.float64),
        np.asarray([0.0, 0.0], dtype=np.float64),
    ) == pytest.approx(math.sqrt(0.5))

    target = core.JointParameters(-6.0, 1.25, -0.60, 0.15, 4.0)
    assert core.scaled_natural_parameter_distance(target, target) == 0.0
    shifted = core.JointParameters(-5.92, 1.25, -0.60, 0.15, 4.0)
    assert core.scaled_natural_parameter_distance(shifted, target) == pytest.approx(0.01)

    below = float(np.nextafter(0.01, 0.0))
    above_rmse = float(np.nextafter(5e-5, math.inf))
    assert core.inverse_solution_is_recovery(5e-5, below)
    assert not core.inverse_solution_is_collision(5e-5, below)
    assert not core.inverse_solution_is_recovery(5e-5, 0.01)
    assert core.inverse_solution_is_collision(5e-5, 0.01)
    assert not core.inverse_solution_is_recovery(above_rmse, 0.0)
    assert not core.inverse_solution_is_collision(above_rmse, 1.0)


def test_lro_2b07_002_all_nine_inverse_audits_reproduce_frozen_counts(
    canonical_nine_audit_preflight: Any,
) -> None:
    preflight = canonical_nine_audit_preflight
    expected = {
        ("dense", "A"): 16,
        ("dense", "B"): 15,
        ("dense", "C"): 2,
        ("structured", "A"): 16,
        ("structured", "B"): 14,
        ("structured", "C"): 3,
        ("sparse", "A"): 15,
        ("sparse", "B"): 16,
        ("sparse", "C"): 16,
    }

    observed = {
        (audit.schedule_id, audit.target_id): audit.recovery_count for audit in preflight.audits
    }

    assert observed == expected
    assert tuple((audit.schedule_id, audit.target_id) for audit in preflight.audits) == tuple(
        expected
    )
    assert all(audit.collision_count == 0 for audit in preflight.audits)
    assert all(audit.successful_search_count >= 12 for audit in preflight.audits)
    assert all(audit.local_diagnostic.rank == 5 for audit in preflight.audits)
    assert all(audit.local_diagnostic.condition_number < 1e8 for audit in preflight.audits)
    assert all(audit.passed for audit in preflight.audits)
    assert preflight.passed
    assert preflight.estimation_authorized


def test_lro_2b07_003_inverse_preflight_records_are_typed_immutable_and_complete(
    canonical_nine_audit_preflight: Any,
) -> None:
    core = _core()
    preflight = canonical_nine_audit_preflight

    assert len(preflight.audits) == 9
    assert all(len(audit.searches) == 16 for audit in preflight.audits)
    assert all(
        tuple(search.start_index for search in audit.searches) == tuple(range(1, 17))
        for audit in preflight.audits
    )
    assert all(
        search.start_coordinates.dtype == np.float64
        and not search.start_coordinates.flags.writeable
        for audit in preflight.audits
        for search in audit.searches
    )
    assert all(
        search.natural_parameters is None
        or (
            search.natural_parameters.dtype == np.float64
            and not search.natural_parameters.flags.writeable
        )
        for audit in preflight.audits
        for search in audit.searches
    )
    with pytest.raises(FrozenInstanceError):
        preflight.passed = False
    source = inspect.getsource(core.run_canonical_inverse_audit)
    assert "_run_frozen_lbfgsb_start" in source
    assert "scipy.optimize.minimize" not in source


def test_lro_2b07_004_inverse_preflight_accepts_only_count_free_designs() -> None:
    core = _core()
    signature = inspect.signature(core.run_nine_audit_preflight)
    assert set(signature.parameters) == {"designs"}
    forbidden = {"count", "history", "truth", "rng", "seed", "scenario", "split"}
    assert not forbidden & set(signature.parameters)
    assert {field.name for field in fields(core.AuditDesign)} == {
        "schedule_id",
        "cell_ids",
        "standardized_quality",
        "predator_arrival_time",
        "opportunity_cell_index",
        "opportunity_time_index",
        "efforts",
    }


def test_lro_2b08_001_three_literal_fixtures_pass_only_by_failing_rank_five(
    canonical_audit_designs: dict[str, Any],
) -> None:
    core = _core()
    fixtures = (
        core.equal_emission_fixture(canonical_audit_designs["dense"]),
        core.deficient_design_fixture(),
        core.absent_state_support_fixture(),
    )

    assert tuple(result.fixture_id for result in fixtures) == (
        "equal_emission_fixture",
        "deficient_design_fixture",
        "absent_state_support_fixture",
    )
    for result in fixtures:
        assert result.diagnostic.n_columns == 5
        assert result.diagnostic.rank < 5
        assert result.diagnostic.condition_number == math.inf
        assert not result.diagnostic.passed
        assert not result.inverse_search_attempted
        assert result.control_passed
    assert fixtures[0].process_derivative_max_abs == 0.0
    assert fixtures[1].diagnostic.n_rows == 32 * 21 * 2
    assert fixtures[2].diagnostic.n_rows == 32 * 2


def test_lro_2b08_002_equal_emission_fixture_never_uses_ordered_map_or_inverse_search(
    canonical_audit_designs: dict[str, Any],
) -> None:
    core = _core()
    source = inspect.getsource(core.equal_emission_fixture)

    assert "lambda_equal" in source
    assert "require_ordering=False" in source
    assert "ordered_rates_from_fractions" not in source
    assert "run_canonical_inverse_audit" not in source
    assert "_run_frozen_lbfgsb_start" not in source
    result = core.equal_emission_fixture(canonical_audit_designs["dense"])
    assert result.diagnostic.provenance == "equal_emission_fixture"


def test_lro_2b08_003_each_injected_audit_failure_has_a_literal_stop_reason() -> None:
    core = _core()
    passing_local = core.DesignDiagnostic(
        provenance="injected",
        role="TEST",
        n_rows=10,
        n_columns=5,
        rank=5,
        condition_number=10.0,
        passed=True,
    )
    rank_failure = core.DesignDiagnostic(
        provenance="injected",
        role="TEST",
        n_rows=10,
        n_columns=5,
        rank=4,
        condition_number=math.inf,
        passed=False,
        failure_reason="rank_deficient",
    )
    condition_failure = core.DesignDiagnostic(
        provenance="injected",
        role="TEST",
        n_rows=10,
        n_columns=5,
        rank=5,
        condition_number=1e8,
        passed=False,
        failure_reason="condition_limit_failed",
    )

    assert core.inverse_audit_failure_reason(rank_failure, 16, 16, 0) == (
        "canonical_local_rank_or_condition_failure"
    )
    assert core.inverse_audit_failure_reason(condition_failure, 16, 16, 0) == (
        "canonical_local_rank_or_condition_failure"
    )
    assert core.inverse_audit_failure_reason(passing_local, 11, 11, 0) == (
        "fewer_than_twelve_of_sixteen_inverse_searches_succeeded"
    )
    assert core.inverse_audit_failure_reason(passing_local, 12, 0, 0) == (
        "no_inverse_search_recovered_target"
    )
    assert core.inverse_audit_failure_reason(passing_local, 16, 15, 1) == (
        "inverse_audit_collision_detected"
    )
    assert core.inverse_audit_failure_reason(passing_local, 16, 16, 0) is None


def _synthetic_joint_fit(core: Any, *, parameters: Any | None = None, llmax: float = 0.0) -> Any:
    natural = _joint_parameters(core) if parameters is None else parameters
    fractions = core.ordered_rate_fractions_from_natural(
        natural.lambda_present,
        natural.lambda_quasi,
    )
    coordinates = np.asarray(
        [
            natural.alpha,
            natural.beta_driver,
            natural.beta_quality,
            fractions.p_frac,
            fractions.q_frac,
        ],
        dtype=np.float64,
    )
    starts = core.global_optimization_starts()
    attempts = tuple(
        core.OptimizerStartResult(
            start_index=index,
            start_coordinates=starts[index - 1],
            succeeded=True,
            coordinates=coordinates,
            objective_value=-llmax,
            log_likelihood=llmax,
            failure_reason=None,
        )
        for index in range(1, 9)
    )
    return core.MultiStartFitResult(
        optimizer_kind="joint",
        attempts=attempts,
        ranked_successes=attempts,
        converged=True,
        converged_start_count=8,
        best_start_index=1,
        best_coordinates=coordinates,
        best_log_likelihood=llmax,
        failure_reason=None,
    )


def _synthetic_multistart_fit(
    core: Any,
    optimizer_kind: str,
    *,
    coordinates: np.ndarray[Any, np.dtype[np.float64]] | None = None,
    objective_value: float = 0.0,
) -> Any:
    selected = (
        core.optimization_starts(optimizer_kind)[0]
        if coordinates is None
        else np.asarray(coordinates, dtype=np.float64)
    )
    starts = core.optimization_starts(optimizer_kind)
    attempts = tuple(
        core.OptimizerStartResult(
            start_index=index,
            start_coordinates=starts[index - 1],
            succeeded=True,
            coordinates=selected,
            objective_value=objective_value,
            log_likelihood=-objective_value,
            failure_reason=None,
        )
        for index in range(1, 9)
    )
    return core.MultiStartFitResult(
        optimizer_kind=optimizer_kind,
        attempts=attempts,
        ranked_successes=attempts,
        converged=True,
        converged_start_count=8,
        best_start_index=1,
        best_coordinates=selected,
        best_log_likelihood=-objective_value,
        failure_reason=None,
    )


def _process_oracle_outcomes(core: Any) -> tuple[Any, ...]:
    return (
        core.ProcessOracleOutcome(1, -1.0, 0.0, 6),
        core.ProcessOracleOutcome(3, -0.5, 12.0, 12),
        core.ProcessOracleOutcome(8, 0.0, 24.0, 18),
        core.ProcessOracleOutcome(13, 0.5, 36.0, 24),
        core.ProcessOracleOutcome(21, 1.0, None, None),
        core.ProcessOracleOutcome(34, 1.5, 90.0, None),
    )


def _observation_oracle_histories(core: Any) -> tuple[Any, ...]:
    return (
        core.ObservationOracleHistory(
            cell_id=1,
            opportunities=(
                _op(core, time=0, count=3),
                _op(core, time=6, count=2, effort=0.8),
            ),
            states=(0, 0),
        ),
        core.ObservationOracleHistory(
            cell_id=3,
            opportunities=(
                _op(core, time=0, count=4),
                _op(core, time=12, count=0, effort=1.2),
            ),
            states=(0, 1),
        ),
    )


def _joint_vector(parameters: Any) -> np.ndarray[Any, np.dtype[np.float64]]:
    return np.asarray(
        [
            parameters.alpha,
            parameters.beta_driver,
            parameters.beta_quality,
            parameters.lambda_quasi,
            parameters.lambda_present,
        ],
        dtype=np.float64,
    )


def test_lro_2b09_001_profile_conditional_maps_and_projections_are_literal() -> None:
    core = _core()
    mle = _joint_parameters(core)

    process_target = core.profile_nuisance_to_natural(
        "joint",
        "beta_driver",
        0.5,
        np.asarray([-6.0, -0.60, 0.5, 0.5], dtype=np.float64),
    )
    assert process_target.beta_driver == 0.5
    assert process_target.lambda_present == pytest.approx(5.125)

    fixed_present = core.profile_nuisance_to_natural(
        "joint",
        "lambda_present",
        0.6,
        np.asarray([-6.0, 1.25, -0.60, 1.0], dtype=np.float64),
    )
    assert fixed_present.lambda_present == 0.6
    assert fixed_present.lambda_quasi == pytest.approx(0.6 - 1e-9)

    fixed_quasi = core.profile_nuisance_to_natural(
        "joint",
        "lambda_quasi",
        0.6,
        np.asarray([-6.0, 1.25, -0.60, 0.0], dtype=np.float64),
    )
    assert fixed_quasi.lambda_quasi == 0.6
    assert fixed_quasi.lambda_present == pytest.approx(0.6 + 1e-9)

    projected = core.project_natural_to_profile_nuisance(
        "joint",
        "lambda_present",
        0.6,
        mle,
    )
    assert projected.shape == (4,)
    assert not projected.flags.writeable
    np.testing.assert_array_equal(projected[:3], [-6.0, 1.25, -0.60])

    invalid_candidate = core.JointParameters(-6.0, 1.25, -0.60, 1.0, 4.0)
    with pytest.raises(ValueError, match="projection"):
        core.project_natural_to_profile_nuisance(
            "joint",
            "lambda_present",
            0.5,
            invalid_candidate,
        )
    with pytest.raises(ValueError, match="profile target"):
        core.profile_nuisance_bounds("joint", "lambda_equal", 1.0)


def test_lro_2b09_002_profile_start_order_deduplicates_and_caps_at_eight() -> None:
    core = _core()
    mle = _joint_parameters(core)

    starts = core.build_profile_nuisance_starts(
        "joint",
        "beta_driver",
        0.5,
        global_natural=mle,
        nearest_natural=mle,
    )

    assert 1 <= len(starts) <= 8
    assert starts[0].source == "global_mle"
    assert all(start.source != "nearest_same_side" for start in starts)
    assert tuple(start.source_order for start in starts) == tuple(
        sorted(start.source_order for start in starts)
    )
    assert all(not start.coordinates.flags.writeable for start in starts)
    for left_index, left in enumerate(starts):
        for right in starts[left_index + 1 :]:
            assert np.max(np.abs(left.coordinates - right.coordinates)) > 1e-10


def test_lro_2b09_003_adaptive_profile_targets_step_once_and_end_at_bound() -> None:
    core = _core()

    lower = core.adaptive_profile_target_values("beta_driver", 1.25, "lower")
    upper = core.adaptive_profile_target_values("beta_driver", 1.25, "upper")

    assert lower[0] == pytest.approx(1.25 - 0.02 * 6.0)
    assert lower[1] == pytest.approx(1.25 - 0.02 * 6.0 * 1.6)
    assert upper[0] == pytest.approx(1.25 + 0.02 * 6.0)
    assert upper[1] == pytest.approx(1.25 + 0.02 * 6.0 * 1.6)
    assert lower[-1] == -3.0
    assert upper[-1] == 3.0
    assert len(lower) == len(set(lower))
    assert len(upper) == len(set(upper))


def test_lro_2b09_004_two_sided_profile_uses_sign_change_and_literal_brent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    mle = _joint_parameters(core)
    fit = _synthetic_joint_fit(core)
    center = _joint_vector(mle)
    scales = np.asarray([0.5, 0.2, 0.5, 0.2, 0.5], dtype=np.float64)
    original_brentq = core.scipy.optimize.brentq
    calls: list[tuple[float, float, float, int, float, float]] = []

    def objective(parameters: Any) -> float:
        standardized = (_joint_vector(parameters) - center) / scales
        return float(np.square(standardized).sum())

    def recording_brentq(
        function: Any,
        lower: float,
        upper: float,
        *,
        xtol: float,
        maxiter: int,
    ) -> float:
        lower_value = function(lower)
        upper_value = function(upper)
        calls.append((lower, upper, xtol, maxiter, lower_value, upper_value))
        assert lower_value * upper_value <= 0.0
        return float(original_brentq(function, lower, upper, xtol=xtol, maxiter=maxiter))

    monkeypatch.setattr(core.scipy.optimize, "brentq", recording_brentq)
    profile = core._profile_parameter(
        fit,
        "beta_driver",
        objective,
    )

    expected_half_width = 0.2 * math.sqrt(core.PROFILE_LR_CUTOFF / 2.0)
    assert profile.global_fit_valid
    assert profile.practically_identifiable
    assert profile.lower.interval_endpoint == pytest.approx(1.25 - expected_half_width, abs=7e-5)
    assert profile.upper.interval_endpoint == pytest.approx(1.25 + expected_half_width, abs=7e-5)
    assert profile.lower.crossed_cutoff and profile.upper.crossed_cutoff
    assert not profile.lower.open_side and not profile.upper.open_side
    assert len(calls) == 2
    assert all(call[2] == 6e-5 and call[3] == 100 for call in calls)


def test_lro_2b09_005_bound_without_crossing_stays_open_and_unidentified() -> None:
    core = _core()
    profile = core._profile_parameter(
        _synthetic_joint_fit(core),
        "beta_driver",
        lambda _: 0.0,
    )

    assert profile.global_fit_valid
    assert profile.lower.open_side and profile.upper.open_side
    assert profile.lower.interval_endpoint is None
    assert profile.upper.interval_endpoint is None
    assert not profile.lower.crossed_cutoff
    assert not profile.upper.crossed_cutoff
    assert not profile.practically_identifiable


def test_lro_2b09_006_failed_nuisance_starts_leave_sides_open(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()

    def failed_minimize(*args: object, **kwargs: object) -> SimpleNamespace:
        del args, kwargs
        return SimpleNamespace(success=False, status=1, fun=0.0, x=np.zeros(4))

    monkeypatch.setattr(core.scipy.optimize, "minimize", failed_minimize)
    profile = core._profile_parameter(
        _synthetic_joint_fit(core),
        "beta_driver",
        lambda _: 0.0,
    )

    assert all(not point.succeeded for point in profile.lower.points)
    assert all(not point.succeeded for point in profile.upper.points)
    assert profile.lower.open_side and profile.upper.open_side
    assert not profile.practically_identifiable


def test_lro_2b10_001_profile_llmax_invalidation_boundary_is_strict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    llmax = 0.0
    tolerance = 1e-6 * (1.0 + abs(llmax))
    below = float(np.nextafter(tolerance, 0.0))
    above = float(np.nextafter(tolerance, math.inf))

    assert not core.profile_log_likelihood_exceeds_global_maximum(below, llmax)
    assert not core.profile_log_likelihood_exceeds_global_maximum(tolerance, llmax)
    assert core.profile_log_likelihood_exceeds_global_maximum(above, llmax)

    minimize_calls = 0
    original_minimize = core.scipy.optimize.minimize

    def recording_minimize(*args: object, **kwargs: object) -> Any:
        nonlocal minimize_calls
        minimize_calls += 1
        return original_minimize(*args, **kwargs)

    monkeypatch.setattr(core.scipy.optimize, "minimize", recording_minimize)
    invalid = core._profile_parameter(
        _synthetic_joint_fit(core, llmax=llmax),
        "beta_driver",
        lambda _: -above,
    )

    assert minimize_calls > 0
    assert not invalid.global_fit_valid
    assert not invalid.practically_identifiable
    assert invalid.failure_reason == "profile_log_likelihood_exceeds_global_maximum"
    assert invalid.upper.points == ()


def test_lro_2b10_002_practical_classification_requires_strict_one_percent_interior() -> None:
    core = _core()
    exact_boundary = -3.0 + 0.01 * 6.0
    just_inside = float(np.nextafter(exact_boundary, math.inf))

    assert not core.practical_identifiability_classification(
        "beta_driver",
        exact_boundary,
        lower_endpoint=-2.95,
        upper_endpoint=0.0,
        lower_crossed=True,
        upper_crossed=True,
    )
    assert core.practical_identifiability_classification(
        "beta_driver",
        just_inside,
        lower_endpoint=-2.95,
        upper_endpoint=0.0,
        lower_crossed=True,
        upper_crossed=True,
    )
    assert not core.practical_identifiability_classification(
        "beta_driver",
        0.0,
        lower_endpoint=None,
        upper_endpoint=1.0,
        lower_crossed=False,
        upper_crossed=True,
    )


def test_lro_2b10_003_profile_parameter_subsets_are_literal_and_equal_control_has_none() -> None:
    core = _core()

    assert core.profiled_parameter_names("process_oracle") == (
        "alpha",
        "beta_driver",
        "beta_quality",
    )
    assert core.profiled_parameter_names("observation_oracle") == (
        "lambda_quasi",
        "lambda_present",
    )
    assert core.profiled_parameter_names("joint") == (
        "alpha",
        "beta_driver",
        "beta_quality",
        "lambda_quasi",
        "lambda_present",
    )
    assert core.profiled_parameter_names("equal_emission_control") == ()


def test_lro_2b10_004_joint_fit_refuses_estimation_before_preflight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    histories = _batch_histories(core, interval_count=20)
    blocked_preflight = object.__new__(core.NineAuditPreflightResult)
    optimizer_calls = 0

    def forbidden_optimizer(*args: object, **kwargs: object) -> None:
        del args, kwargs
        nonlocal optimizer_calls
        optimizer_calls += 1
        raise AssertionError("blocked fit reached optimizer")

    monkeypatch.setattr(core, "_run_multistart_optimization", forbidden_optimizer)
    result = core.fit_joint_analyst_histories(
        histories,
        fit_frame=_issued_fit_frame(core),
        preflight=blocked_preflight,
    )

    assert optimizer_calls == 0
    assert not result.converged
    assert result.parameters is None
    assert result.multistart is None
    assert result.failure_reason == "nine_audit_preflight_not_authorized"


def test_lro_2b10_005_joint_fit_uses_batched_analyst_objective_after_preflight(
    monkeypatch: pytest.MonkeyPatch,
    canonical_nine_audit_preflight: Any,
) -> None:
    core = _core()
    histories = _authoritative_fit_histories(core)
    fit_frame = _issued_fit_frame(core)
    expected_fit = _synthetic_joint_fit(core)
    objective_calls = 0

    def fake_multistart(kind: str, objective: Any) -> Any:
        assert kind == "joint"
        nonlocal objective_calls
        value = objective(core.global_optimization_starts()[0])
        objective_calls += 1
        assert math.isfinite(value)
        return expected_fit

    monkeypatch.setattr(core, "_run_multistart_optimization", fake_multistart)
    result = core.fit_joint_analyst_histories(
        histories,
        fit_frame=fit_frame,
        preflight=canonical_nine_audit_preflight,
    )

    assert objective_calls == 1
    assert result.converged
    assert result.parameters == _joint_parameters(core)
    assert result.potential_diagnostic is not None
    assert result.potential_diagnostic.provenance == "potential_design"
    assert result.potential_diagnostic.passed
    assert result.plugin_diagnostic is not None
    assert result.plugin_diagnostic.provenance == "joint_plugin_smoothed_at_risk"
    assert result.failure_reason is None
    assert core.joint_fit_design_frame_identity(result) == (
        4180,
        fit_frame.cell_sha256,
    )


def test_lro_2b10_006_joint_fit_surface_is_analyst_only() -> None:
    core = _core()
    signature = inspect.signature(core.fit_joint_analyst_histories)
    assert set(signature.parameters) == {"histories", "fit_frame", "preflight"}
    forbidden = {
        "truth",
        "states",
        "transition_time",
        "generating_parameters",
        "scenario_id",
        "split",
        "replicate_index",
        "seed",
    }
    assert not forbidden & set(signature.parameters)
    source = inspect.getsource(core.fit_joint_analyst_histories)
    assert "batched_joint_log_likelihood" in source
    assert "ProcessSimulationTruth" not in source
    assert "LatentProcessTruth" not in source


def test_lro_2b10_007_authorized_preflight_requires_complete_nine_audit_record() -> None:
    core = _core()

    with pytest.raises(TypeError, match="run_nine_audit_preflight"):
        core.NineAuditPreflightResult(
            audits=(),
            passed=True,
            estimation_authorized=True,
            failure_reason=None,
        )


def test_lro_2b11_001_deployable_fit_and_profile_surfaces_are_typed_and_callback_free() -> None:
    core = _core()
    expected_parameters = {
        "fit_process_oracle_outcomes": {"outcomes", "preflight"},
        "fit_observation_oracle_histories": {"histories", "preflight"},
        "fit_joint_analyst_histories": {"histories", "fit_frame", "preflight"},
        "profile_process_oracle_outcomes": {
            "outcomes",
            "fit",
            "parameter_name",
            "preflight",
        },
        "profile_observation_oracle_histories": {
            "histories",
            "fit",
            "parameter_name",
            "preflight",
        },
        "profile_joint_analyst_histories": {
            "histories",
            "fit",
            "parameter_name",
            "preflight",
        },
    }

    for name, expected in expected_parameters.items():
        function = getattr(core, name)
        assert set(inspect.signature(function).parameters) == expected
        assert "Callable" not in inspect.getsource(function)
    for raw_callback_surface in (
        "run_optimizer_start",
        "run_multistart_optimization",
        "profile_parameter",
    ):
        assert not hasattr(core, raw_callback_surface)


def test_lro_2b11_002_fabricated_preflight_cannot_touch_data_optimizer_or_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    fabricated = object.__new__(core.NineAuditPreflightResult)
    data_touched = False
    primitive_calls = 0

    class EvaluatorObject:
        def __iter__(self) -> Iterator[object]:
            nonlocal data_touched
            data_touched = True
            return iter(())

    def forbidden_primitive(*args: object, **kwargs: object) -> None:
        del args, kwargs
        nonlocal primitive_calls
        primitive_calls += 1
        raise AssertionError("fabricated preflight reached an optimization primitive")

    monkeypatch.setattr(core, "_run_multistart_optimization", forbidden_primitive)
    monkeypatch.setattr(core, "_profile_parameter", forbidden_primitive)
    evaluator = EvaluatorObject()

    fit_results = (
        core.fit_process_oracle_outcomes(evaluator, preflight=fabricated),
        core.fit_observation_oracle_histories(evaluator, preflight=fabricated),
        core.fit_joint_analyst_histories(
            evaluator,
            fit_frame=_issued_fit_frame(core),
            preflight=fabricated,
        ),
    )
    assert all(
        result.failure_reason == "nine_audit_preflight_not_authorized" for result in fit_results
    )
    for profile_function, parameter_name in (
        (core.profile_process_oracle_outcomes, "alpha"),
        (core.profile_observation_oracle_histories, "lambda_quasi"),
        (core.profile_joint_analyst_histories, "beta_driver"),
    ):
        with pytest.raises(ValueError, match="nine-audit preflight"):
            profile_function(
                evaluator,
                object(),
                parameter_name,
                preflight=fabricated,
            )
    assert not data_touched
    assert primitive_calls == 0


def test_lro_2b11_003_canonical_preflight_drives_typed_internal_fit_and_profile_objectives(
    monkeypatch: pytest.MonkeyPatch,
    canonical_nine_audit_preflight: Any,
) -> None:
    core = _core()
    process_outcomes = _process_oracle_outcomes(core)
    observation_histories = _observation_oracle_histories(core)
    analyst_histories = _authoritative_fit_histories(core)
    analyst_fit_frame = _issued_fit_frame(core)
    fit_objectives: dict[str, float] = {}
    profile_objectives: dict[str, float] = {}

    def deterministic_multistart(kind: str, objective: Any) -> Any:
        coordinates = core.optimization_starts(kind)[0]
        value = float(objective(coordinates))
        assert math.isfinite(value)
        fit_objectives[kind] = value
        return _synthetic_multistart_fit(
            core,
            kind,
            coordinates=coordinates,
            objective_value=value,
        )

    def recording_profile(global_fit: Any, parameter_name: str, objective: Any) -> Any:
        natural = core.optimization_coordinates_to_natural(
            global_fit.optimizer_kind,
            global_fit.best_coordinates,
        )
        profile_objectives[global_fit.optimizer_kind] = float(objective(natural))
        support = {
            "alpha": core.ALPHA_SUPPORT,
            "beta_quality": core.BETA_QUALITY_SUPPORT,
            "lambda_quasi": core.LAMBDA_QUASI_SUPPORT,
        }[parameter_name]
        empty = core.ProfileSideResult(
            side="lower",
            points=(),
            crossed_cutoff=False,
            open_side=True,
            interval_endpoint=None,
            bracket=None,
        )
        return core.ParameterProfileResult(
            optimizer_kind=global_fit.optimizer_kind,
            parameter_name=parameter_name,
            mle=float(support[0]),
            support=support,
            llmax=float(global_fit.best_log_likelihood),
            lower=empty,
            upper=core.ProfileSideResult(
                side="upper",
                points=(),
                crossed_cutoff=False,
                open_side=True,
                interval_endpoint=None,
                bracket=None,
            ),
            practically_identifiable=False,
            global_fit_valid=True,
            failure_reason=None,
        )

    monkeypatch.setattr(core, "_run_multistart_optimization", deterministic_multistart)
    process_fit = core.fit_process_oracle_outcomes(
        process_outcomes,
        preflight=canonical_nine_audit_preflight,
    )
    observation_fit = core.fit_observation_oracle_histories(
        observation_histories,
        preflight=canonical_nine_audit_preflight,
    )
    joint_fit = core.fit_joint_analyst_histories(
        analyst_histories,
        fit_frame=analyst_fit_frame,
        preflight=canonical_nine_audit_preflight,
    )

    assert type(process_fit) is core.ProcessOracleFitResult
    assert type(process_fit.parameters) is core.ProcessParameters
    assert process_fit.at_risk_diagnostic is not None
    assert process_fit.at_risk_diagnostic.provenance == "process_oracle_truth_at_risk"
    assert process_fit.at_risk_diagnostic.passed
    assert type(observation_fit) is core.ObservationOracleFitResult
    assert type(observation_fit.rates) is EffectiveCountRates
    assert type(joint_fit) is core.JointFitResult
    assert type(joint_fit.parameters) is core.JointParameters

    monkeypatch.setattr(core, "_profile_parameter", recording_profile)
    profiles = (
        core.profile_process_oracle_outcomes(
            process_outcomes,
            process_fit,
            "alpha",
            preflight=canonical_nine_audit_preflight,
        ),
        core.profile_observation_oracle_histories(
            observation_histories,
            observation_fit,
            "lambda_quasi",
            preflight=canonical_nine_audit_preflight,
        ),
        core.profile_joint_analyst_histories(
            analyst_histories,
            joint_fit,
            "beta_quality",
            preflight=canonical_nine_audit_preflight,
        ),
    )
    assert tuple(profile.optimizer_kind for profile in profiles) == (
        "process_oracle",
        "observation_oracle",
        "joint",
    )
    assert fit_objectives.keys() == profile_objectives.keys()
    for kind in fit_objectives:
        assert profile_objectives[kind] == pytest.approx(fit_objectives[kind])


def test_lro_2b11_004_evaluators_truth_callables_and_oracle_data_are_firewalled(
    canonical_nine_audit_preflight: Any,
) -> None:
    core = _core()
    evaluator_touched = False
    closure_called = False

    class EvaluatorObject:
        true_states = (0, 1)
        generating_parameters = _joint_parameters(core)

        def __iter__(self) -> Iterator[object]:
            nonlocal evaluator_touched
            evaluator_touched = True
            return iter(())

    def truth_bearing_closure(_: object) -> float:
        nonlocal closure_called
        closure_called = True
        return float(EvaluatorObject.true_states[0])

    evaluator = EvaluatorObject()
    for fit_function, extra_kwargs in (
        (core.fit_process_oracle_outcomes, {}),
        (core.fit_observation_oracle_histories, {}),
        (core.fit_joint_analyst_histories, {"fit_frame": _issued_fit_frame(core)}),
    ):
        with pytest.raises(ValueError, match="tuple"):
            fit_function(
                evaluator,
                preflight=canonical_nine_audit_preflight,
                **extra_kwargs,
            )
        with pytest.raises(TypeError):
            fit_function(
                (truth_bearing_closure,),
                preflight=canonical_nine_audit_preflight,
                **extra_kwargs,
            )

    oracle_at_risk = _process_oracle_outcomes(core)
    with pytest.raises(TypeError, match="AnalystHistory"):
        core.fit_joint_analyst_histories(
            oracle_at_risk,
            fit_frame=_issued_fit_frame(core),
            preflight=canonical_nine_audit_preflight,
        )
    for fit_function, data, extra_kwargs in (
        (core.fit_process_oracle_outcomes, oracle_at_risk, {}),
        (
            core.fit_observation_oracle_histories,
            _observation_oracle_histories(core),
            {},
        ),
        (
            core.fit_joint_analyst_histories,
            _authoritative_fit_histories(core),
            {"fit_frame": _issued_fit_frame(core)},
        ),
    ):
        with pytest.raises(TypeError):
            fit_function(
                data,
                preflight=canonical_nine_audit_preflight,
                objective=truth_bearing_closure,
                **extra_kwargs,
            )
    assert not evaluator_touched
    assert not closure_called


def test_lro_2b12_001_canonical_source_preserves_every_finite_arrival(
    canonical_source_arrival_cells: tuple[Any, ...],
) -> None:
    core = _core()
    arrivals = np.asarray(
        [cell.predator_arrival_time for cell in canonical_source_arrival_cells],
        dtype=np.float64,
    )

    assert arrivals.shape == (5225,)
    assert np.all(np.isfinite(arrivals))
    assert np.count_nonzero(arrivals > core.MODEL_TIMES[-1]) == 620
    assert float(arrivals.max()) == pytest.approx(205.910318172679, abs=1e-12)
    latest = canonical_source_arrival_cells[int(np.argmax(arrivals))]
    primitives = core.process_log_primitives(
        standardized_quality=latest.standardized_quality,
        predator_arrival_time=latest.predator_arrival_time,
        parameters=_process_parameters(core),
    )
    np.testing.assert_array_equal(primitives.driver, np.zeros(20, dtype=np.float64))


def test_lro_2b12_002_permutation_correlation_frame_keeps_complete_source_values(
    canonical_source_arrival_cells: tuple[Any, ...],
) -> None:
    core = _core()
    original = np.asarray(
        [cell.predator_arrival_time for cell in canonical_source_arrival_cells],
        dtype=np.float64,
    )
    permuted = core.permute_arrival_within_blocks(canonical_source_arrival_cells)
    finite_pairs = np.isfinite(original) & np.isfinite(permuted)

    assert np.count_nonzero(finite_pairs) == 5225
    np.testing.assert_array_equal(np.sort(permuted), np.sort(original))
    correlation = float(np.corrcoef(original[finite_pairs], permuted[finite_pairs])[0, 1])
    assert math.isfinite(correlation)


def _fit_row(core: Any, **updates: object) -> dict[str, object]:
    row: dict[str, object] = {name: None for name in core.FIT_EXECUTION_EVIDENCE_HEADER}
    row.update(
        scenario_id="dense_count_exact_model",
        split_id="development",
        fit_scope="replicate",
        fit_variant="canonical",
        fit_index=0,
        source_replicate_first=0,
        source_replicate_last=0,
        source_replicate_count=1,
        fit_succeeded=False,
        fit_failure_class="optimizer_or_nonfinite_failure",
        failure_code="typed_failure",
        evidence_row_type="fit_result",
    )
    row.update(updates)
    return row


_FIXTURE_JOINT_RESULTS: dict[str, Any] = {}


def _fixture_joint_result(core: Any, scenario_id: str) -> Any:
    cached = _FIXTURE_JOINT_RESULTS.get(scenario_id)
    if cached is not None:
        return cached
    frame = core.issue_analyst_fit_frame(scenario_id)
    n_rows = frame.cell_count * 20
    potential = core.DesignDiagnostic(
        provenance="potential_design",
        role="ANALYST-PREFLIGHT",
        n_rows=n_rows,
        n_columns=3,
        rank=3,
        condition_number=2.0,
        passed=True,
    )
    plugin = replace(
        potential,
        provenance="joint_plugin_smoothed_at_risk",
        role="ANALYST-JOINT-PRACTICAL",
    )
    result = core.JointFitResult(
        converged=True,
        parameters=_joint_parameters(core),
        multistart=_synthetic_joint_fit(core),
        potential_diagnostic=potential,
        plugin_diagnostic=plugin,
        fit_frame=frame,
        fit_frame_cell_count=frame.cell_count,
        fit_frame_sha256=frame.cell_sha256,
        failure_class=None,
        failure_reason=None,
    )
    _FIXTURE_JOINT_RESULTS[scenario_id] = result
    return result


def _design_row(
    core: Any,
    fit_row: dict[str, object],
    *,
    design_kind: str,
    rank: int = 3,
    condition_number: float | None = 2.0,
    passed: bool = True,
    failure_code: str | None = None,
    **updates: object,
) -> dict[str, object]:
    labels = {
        "potential": ("potential_design", "ANALYST-PREFLIGHT"),
        "oracle": ("process_oracle_truth_at_risk", "ORACLE-BENCHMARK-ONLY"),
        "plugin": ("joint_plugin_smoothed_at_risk", "ANALYST-JOINT-PRACTICAL"),
    }
    provenance, role = labels[design_kind]
    scenario_id = cast(str, fit_row["scenario_id"])
    fit_variant = cast(str, fit_row["fit_variant"])
    joint_result = (
        _fixture_joint_result(core, scenario_id)
        if "plugin" in core.required_design_kinds(scenario_id, fit_variant)
        else None
    )
    frame_count, frame_sha256 = core.persisted_design_frame_identity(
        scenario_id,
        fit_variant,
        joint_fit_result=joint_result,
    )
    row: dict[str, object] = {name: None for name in EXPECTED_FIT_EXECUTION_HEADER}
    for name in (
        "scenario_id",
        "split_id",
        "fit_scope",
        "fit_variant",
        "fit_index",
        "source_replicate_first",
        "source_replicate_last",
        "source_replicate_count",
    ):
        row[name] = fit_row[name]
    row.update(
        evidence_row_type="design_diagnostic",
        design_kind=design_kind,
        design_provenance=provenance,
        design_role=role,
        design_n_rows=core.expected_potential_design_rows(cast(str, fit_row["scenario_id"])),
        design_n_columns=3,
        design_rank=rank,
        design_condition_number=condition_number,
        design_passed=passed,
        design_failure_code=failure_code,
        design_frame_cell_count=frame_count,
        design_frame_sha256=frame_sha256,
    )
    row.update(updates)
    return row


def _fit_evidence_sort_key(core: Any, row: dict[str, object]) -> tuple[object, ...]:
    row_type = cast(str, row["evidence_row_type"])
    design_kind = row["design_kind"]
    return (
        row["scenario_id"],
        row["split_id"],
        row["fit_scope"],
        row["fit_variant"],
        row["fit_index"],
        core.FIT_EVIDENCE_ROW_TYPES.index(row_type),
        -1 if design_kind is None else core.DESIGN_KINDS.index(cast(str, design_kind)),
    )


def _complete_design_rows(
    core: Any,
    fit_rows: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], ...]:
    return tuple(
        _design_row(core, fit, design_kind=design_kind)
        for fit in fit_rows
        for design_kind in core.required_design_kinds(
            cast(str, fit["scenario_id"]), cast(str, fit["fit_variant"])
        )
    )


def _successful_fit_row(core: Any, **updates: object) -> dict[str, object]:
    scenario_id = str(updates.get("scenario_id", "dense_count_exact_model"))
    variant = str(updates.get("fit_variant", "canonical"))
    row = _fit_row(
        core,
        fit_succeeded=True,
        converged_start_count=None if variant == "equal_rate" else 8,
        best_start_index=None if variant == "equal_rate" else 1,
        best_two_log_likelihoods_agree=None if variant == "equal_rate" else True,
        at_boundary=False,
        boundary_parameter_ids=None,
        fit_failure_class=None,
        failure_code=None,
        log_likelihood=-100.0,
        heldout_log_score=-10.0 if scenario_id == "permuted_arrival_alignment_stress" else None,
    )
    parameter_ids = core.FIT_PARAMETER_IDS.get(scenario_id, core.ORDERED_PARAMETER_IDS)
    estimates = {
        "alpha": -6.0,
        "beta_driver": 1.0,
        "beta_quality": -0.5,
        "lambda_quasi": 0.2,
        "lambda_present": 4.0,
    }
    if variant == "equal_rate":
        row["lambda_equal_estimate"] = 1.0
    else:
        for parameter_id in parameter_ids:
            row[f"{parameter_id}_estimate"] = estimates[parameter_id]
    row.update(updates)
    return row


def _equal_fit_rows(core: Any) -> tuple[dict[str, object], ...]:
    observed = tuple(
        _successful_fit_row(
            core,
            scenario_id="no_emission_contrast_negative_control",
            split_id="holdout",
            fit_scope="scenario_shared",
            fit_variant=variant,
            fit_index=0,
            source_replicate_first=0,
            source_replicate_last=23,
            source_replicate_count=24,
            log_likelihood=-100.0 + (variant == "ordered_emission"),
        )
        for variant in ("equal_rate", "ordered_emission")
    )
    bootstrap = tuple(
        _successful_fit_row(
            core,
            scenario_id="no_emission_contrast_negative_control",
            split_id="holdout",
            fit_scope="bootstrap_shared",
            fit_variant=variant,
            fit_index=bundle,
            source_replicate_first=0,
            source_replicate_last=23,
            source_replicate_count=24,
            log_likelihood=-100.0 + (variant == "ordered_emission"),
        )
        for bundle in range(199)
        for variant in ("equal_rate", "ordered_emission")
    )
    return (*observed, *bootstrap)


def _zero_driver_fit_and_profile_rows(
    core: Any,
    intervals: tuple[tuple[float | None, float | None] | None, ...],
) -> tuple[tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    fits = tuple(
        _successful_fit_row(
            core,
            scenario_id="zero_driver_effect_negative_control",
            split_id="holdout",
            fit_index=index,
            source_replicate_first=index,
            source_replicate_last=index,
        )
        for index in range(24)
    )
    recovery_rows: tuple[dict[str, object], ...] = tuple(
        {
            "scenario_id": "zero_driver_effect_negative_control",
            "split_id": "holdout",
            "replicate_id": index,
            "fit_variant": "canonical",
            "parameter_id": "beta_driver",
            "truth_value": 0.0,
            "estimate": 1.0,
            "interval_lower": interval[0] if interval is not None else None,
            "interval_upper": interval[1] if interval is not None else None,
            "interval_width": (
                interval[1] - interval[0]
                if interval is not None and interval[0] is not None and interval[1] is not None
                else None
            ),
            "converged": True,
            "converged_start_count": 8,
            "at_boundary": False,
            "profile_two_sided": interval is not None,
            "truth_in_interval": (
                interval[0] <= 0.0 <= interval[1]
                if interval is not None and interval[0] is not None and interval[1] is not None
                else None
            ),
            "log_likelihood": -100.0,
            "signed_error": 1.0,
            "absolute_error": 1.0,
            "gate_result": "pass",
        }
        for index, interval in enumerate(intervals)
    )
    return fits, recovery_rows


def _tracked_manifest(core: Any) -> tuple[tuple[tuple[str, str], ...], str]:
    entries = tuple(
        (path, sha256(path.encode()).hexdigest()) for path in sorted(core.ANALYTICAL_PATHS)
    )
    digest = sha256(
        "".join(f"{file_hash}  {path}\n" for path, file_hash in entries).encode()
    ).hexdigest()
    return entries, digest


def _valid_config_payload(
    core: Any, *, tracked_state_sha256: str | None = None
) -> dict[str, object]:
    if tracked_state_sha256 is None:
        _, tracked_state_sha256 = _tracked_manifest(core)
    repo_root = Path(__file__).resolve().parents[1]
    spec_sha256 = sha256(
        (repo_root / "spec/synth_medium_latent_response_observation_recovery_gate.md").read_bytes()
    ).hexdigest()
    source_receipt = json.loads((repo_root / core.SOURCE_RECEIPT_RELATIVE_PATH).read_bytes())
    source_sha256 = sha256(
        (
            f"landscape_sha256={source_receipt['landscape_sha256']}\n"
            f"arrival_sha256={source_receipt['arrival_sha256']}\n"
        ).encode()
    ).hexdigest()
    return {
        "schema_version": "v1",
        "spec_sha256": spec_sha256,
        "source_sha256": source_sha256,
        "tracked_state_sha256": tracked_state_sha256,
        "model": dict(core.FROZEN_MODEL_CONFIG),
        "estimator": dict(core.FROZEN_ESTIMATOR_CONFIG),
        "parameters": [dict(row) for row in core.CONFIG_PARAMETER_ROWS],
        "scenarios": [asdict(row) for row in core.SCENARIO_DEFINITIONS],
        "seed_partitions": dict(core.FROZEN_SEED_PARTITIONS),
        "gates": dict(core.FROZEN_GATE_CONFIG),
        "artifact_manifest": list(core.expected_artifact_manifest()),
        "boundary_labels": dict(core.FROZEN_BOUNDARY_LABELS),
    }


def _holdout_receipt_payload(core: Any, config: Any) -> dict[str, object]:
    return {
        "schema_version": "v1",
        "spec_sha256": config.payload["spec_sha256"],
        "config_sha256": config.config_sha256,
        "source_sha256": config.payload["source_sha256"],
        "tracked_state_sha256": config.payload["tracked_state_sha256"],
        "seed_namespace": "goal023-holdout-v1",
        "exposed": True,
        "invalidated": False,
        "no_contract_change": True,
    }


def _preholdout_payload(core: Any, config: Any) -> dict[str, object]:
    entries, tracked_state = _tracked_manifest(core)
    return {
        "schema_version": "v1",
        "spec_sha256": config.payload["spec_sha256"],
        "config_sha256": config.config_sha256,
        "source_sha256": config.payload["source_sha256"],
        "tracked_state_sha256": tracked_state,
        "tracked_file_manifest": [{"path": path, "sha256": digest} for path, digest in entries],
    }


def _preholdout_payload_for_guard(config: Any, guard: Any) -> dict[str, object]:
    return {
        "schema_version": "v1",
        "spec_sha256": config.payload["spec_sha256"],
        "config_sha256": config.config_sha256,
        "source_sha256": config.payload["source_sha256"],
        "tracked_state_sha256": guard.analytical_sha256,
        "tracked_file_manifest": [
            {"path": path, "sha256": digest} for path, digest in guard.analytical_entries
        ],
    }


def _phase_tree(core: Any, root: Any, phase: str) -> tuple[Any, dict[str, str]]:
    normalized = "pre_freeze" if phase == "config_emission" else phase
    count = core.PHASE_PRESENCE_COUNTS[normalized]
    for relative_path in core.PUBLICATION_PATHS[:count]:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            source = Path(__file__).resolve().parents[1] / relative_path
            if relative_path in (
                "spec/synth_medium_latent_response_observation_recovery_gate.md",
                f"{core.GOAL_DIRECTORY}/source_digest_receipt.json",
            ):
                path.write_bytes(source.read_bytes())
            else:
                path.write_bytes(f"{relative_path}\n".encode())
    state: dict[str, str] = {
        "branch": core.PINNED_BRANCH,
        "head": core.PINNED_COMMIT,
        "base": core.PINNED_COMMIT,
        "status": "".join(f"?? {path}\n" for path in core.PUBLICATION_PATHS[:count]),
    }

    def git_runner(command: tuple[str, ...]) -> str:
        if command == ("branch", "--show-current"):
            return state["branch"] + "\n"
        if command == ("rev-parse", "HEAD"):
            return state["head"] + "\n"
        if command == ("rev-parse", "origin/main"):
            return state["base"] + "\n"
        if command == ("status", "--porcelain=v1", "--untracked-files=all"):
            return state["status"]
        raise AssertionError(command)

    return core.capture_phase_guard(root, normalized, git_runner=git_runner), state


def _mutate_phase_state(core: Any, root: Any, state: dict[str, str], mutation: str) -> None:
    if mutation in ("branch", "head", "base"):
        state[mutation] = "wrong"
    elif mutation == "unknown":
        state["status"] += "?? extra.txt\n"
    elif mutation == "status":
        state["status"] = "R  old -> new\n"
    elif mutation == "manifest":
        (root / core.ANALYTICAL_PATHS[0]).write_bytes(b"changed\n")
    else:
        raise AssertionError(mutation)


def test_lro_3a_001_scenario_registry_truth_access_scope_and_variants_are_literal() -> None:
    core = _core()
    assert core.validate_scenario_registry(core.SCENARIO_EVIDENCE_REGISTRY) == (
        "process_oracle_observed_transition",
        "observation_oracle_fixed_transition",
        "dense_count_exact_model",
        "structured_imperfect_effort",
        "sparse_expected_failure",
        "zero_driver_effect_negative_control",
        "permuted_arrival_alignment_stress",
        "no_emission_contrast_negative_control",
        "informative_dropout_misspecification_stress",
        "goal018_continuous_abundance_stress",
        "spatial_frailty_stress",
    )
    assert core.SCENARIO_EVIDENCE_REGISTRY[6].primary_fit_variant == "permuted_alignment"
    assert core.SCENARIO_EVIDENCE_REGISTRY[7].fit_scope == "scenario_shared"
    assert core.SCENARIO_PARAMETER_TRUTH_ROWS == EXPECTED_SCENARIO_PARAMETER_TRUTH_ROWS
    assert not any(
        scenario_id == "no_emission_contrast_negative_control"
        for scenario_id, _, _ in core.SCENARIO_PARAMETER_TRUTH_ROWS
    )


def test_lro_3a_002_truth_access_rejects_missing_extra_reordered_or_unknown() -> None:
    core = _core()
    registry = core.SCENARIO_EVIDENCE_REGISTRY
    for invalid in (registry[:-1], (*registry, registry[0]), registry[::-1]):
        with pytest.raises(ValueError):
            core.validate_scenario_registry(invalid)
    with pytest.raises(ValueError):
        core.validate_scenario_registry(
            (
                *(
                    core.ScenarioEvidence(
                        registry[0].scenario_id,
                        "unknown",
                        registry[0].fit_scope,
                        registry[0].primary_fit_variant,
                        registry[0].comparator_fit_variant,
                        registry[0].latent_time_applicable,
                        registry[0].latent_time_sample_size,
                    ),
                ),
                *registry[1:],
            )
        )


def test_lro_3a_003_stress_truth_cannot_enter_analyst_fit() -> None:
    core = _core()
    for key in ("original_alignment", "dropout_state", "goal018_abundance", "frailty"):
        with pytest.raises(ValueError, match="truth firewall"):
            core.validate_analyst_fit_payload({"counts": (), key: object()})


def test_lro_3a_004_control_truth_cannot_enter_starts_objective_or_profiles() -> None:
    core = _core()
    for key in ("generating_zero_label", "generating_equal_label"):
        for surface in ("starts", "objective", "profiles", "tie_breaking"):
            with pytest.raises(ValueError, match="control truth"):
                core.validate_control_fit_payload({surface: {key: True}})


def test_lro_3a_005_fit_execution_schema_key_sort_and_failure_rows_are_literal() -> None:
    core = _core()
    assert core.FIT_EXECUTION_EVIDENCE_HEADER == EXPECTED_FIT_EXECUTION_HEADER
    failed = core.validate_fit_execution_rows((_fit_row(core),))
    assert failed[0]["failure_code"] == "typed_failure"
    assert tuple(failed[0]) == EXPECTED_FIT_EXECUTION_HEADER
    assert failed[0]["evidence_row_type"] == "fit_result"
    assert all(
        failed[0][name] is None
        for name in (
            "alpha_estimate",
            "beta_driver_estimate",
            "beta_quality_estimate",
            "lambda_quasi_estimate",
            "lambda_present_estimate",
            "lambda_equal_estimate",
            "log_likelihood",
            "heldout_log_score",
            "at_boundary",
            "boundary_parameter_ids",
        )
    )
    with pytest.raises(ValueError, match="replicate identity"):
        core.validate_fit_execution_rows(
            (
                _fit_row(
                    core,
                    fit_index=7,
                    source_replicate_first=0,
                    source_replicate_last=99,
                    source_replicate_count=100,
                ),
            )
        )
    with pytest.raises(ValueError, match="sorted"):
        core.validate_fit_execution_rows(
            (
                _fit_row(core, fit_index=1, source_replicate_first=1, source_replicate_last=1),
                _fit_row(core),
            )
        )
    with pytest.raises(ValueError, match="scope"):
        core.validate_fit_execution_rows(
            (
                _fit_row(
                    core,
                    scenario_id="no_emission_contrast_negative_control",
                    fit_scope="replicate",
                    fit_variant="equal_rate",
                ),
            )
        )
    with pytest.raises(ValueError, match="estimate"):
        core.validate_fit_execution_rows(
            (
                _fit_row(
                    core,
                    fit_succeeded=True,
                    converged_start_count=8,
                    best_start_index=1,
                    best_two_log_likelihoods_agree=True,
                    at_boundary=False,
                    log_likelihood=-1.0,
                    fit_failure_class=None,
                    failure_code=None,
                ),
            )
        )
    with pytest.raises(ValueError, match="calibration"):
        core.validate_fit_execution_row(
            _successful_fit_row(
                core,
                scenario_id="sparse_expected_failure",
                split_id="calibration",
            )
        )

    fit = _successful_fit_row(core)
    potential = _design_row(core, fit, design_kind="potential")
    plugin = _design_row(core, fit, design_kind="plugin")
    validated = core.validate_fit_execution_rows((fit, potential, plugin))
    assert tuple(row["evidence_row_type"] for row in validated) == (
        "fit_result",
        "design_diagnostic",
        "design_diagnostic",
    )
    assert tuple(row["design_kind"] for row in validated[1:]) == ("potential", "plugin")
    assert core.required_design_kinds("dense_count_exact_model", "canonical") == (
        "potential",
        "plugin",
    )
    boundary_pass = _design_row(
        core,
        fit,
        design_kind="plugin",
        condition_number=float(np.nextafter(1e8, 0.0)),
    )
    core.validate_fit_execution_row(boundary_pass)
    for invalid in (
        _design_row(
            core,
            fit,
            design_kind="plugin",
            condition_number=1e8,
            passed=True,
        ),
        _design_row(core, fit, design_kind="plugin", rank=2, passed=True),
        _design_row(core, fit, design_kind="plugin", condition_number=math.inf),
        potential | {"design_provenance": "joint_plugin_smoothed_at_risk"},
        potential | {"design_role": "ORACLE-BENCHMARK-ONLY"},
    ):
        with pytest.raises(ValueError, match=r"design|rank|condition|provenance|role|finite"):
            core.validate_fit_execution_row(invalid)
    core.validate_fit_execution_row(
        _design_row(
            core,
            fit,
            design_kind="plugin",
            condition_number=1e8,
            passed=False,
            failure_code="condition_limit_failed",
        )
    )
    core.validate_fit_execution_row(
        _design_row(
            core,
            fit,
            design_kind="plugin",
            rank=2,
            condition_number=None,
            passed=False,
            failure_code="rank_deficient",
        )
    )
    with pytest.raises(ValueError, match="calibration"):
        core.validate_fit_execution_row(
            _fit_row(
                core,
                scenario_id="no_emission_contrast_negative_control",
                split_id="calibration",
                fit_scope="scenario_shared",
                fit_variant="equal_rate",
                source_replicate_last=23,
                source_replicate_count=24,
            )
        )
    with pytest.raises(ValueError, match=r"best.two"):
        core.validate_fit_execution_row(_fit_row(core, best_two_log_likelihoods_agree="not-a-bool"))
    for field, value in (
        ("alpha_estimate", -10.0000001),
        ("beta_driver_estimate", 3.0000001),
        ("beta_quality_estimate", -2.0000001),
        ("lambda_quasi_estimate", 0.0099999),
        ("lambda_present_estimate", 10.0000001),
    ):
        with pytest.raises(ValueError, match="natural support"):
            core.validate_fit_execution_row(_successful_fit_row(core, **{field: value}))
    with pytest.raises(ValueError, match="boundary"):
        core.validate_fit_execution_row(
            _successful_fit_row(
                core,
                at_boundary=True,
                boundary_parameter_ids="alpha",
            )
        )
    equal_boundary = _successful_fit_row(
        core,
        scenario_id="no_emission_contrast_negative_control",
        split_id="holdout",
        fit_scope="scenario_shared",
        fit_variant="equal_rate",
        fit_index=0,
        source_replicate_first=0,
        source_replicate_last=23,
        source_replicate_count=24,
        lambda_equal_estimate=0.01,
        at_boundary=True,
        boundary_parameter_ids="lambda_equal",
    )
    with pytest.raises(ValueError, match=r"equal.rate.*interior"):
        core.validate_fit_execution_row(equal_boundary)
    equal_boundary_failure = _fit_row(
        core,
        scenario_id="no_emission_contrast_negative_control",
        split_id="holdout",
        fit_scope="scenario_shared",
        fit_variant="equal_rate",
        fit_index=0,
        source_replicate_first=0,
        source_replicate_last=23,
        source_replicate_count=24,
        fit_failure_class="equal_rate_noninterior_failure",
        failure_code="equal_rate_mle_noninterior",
    )
    assert (
        core.validate_fit_execution_row(equal_boundary_failure)["failure_code"]
        == "equal_rate_mle_noninterior"
    )
    sparse_frame = tuple(
        _fit_row(
            core,
            scenario_id="sparse_expected_failure",
            fit_index=index,
            source_replicate_first=index,
            source_replicate_last=index,
        )
        for index in range(12)
    )
    assert (
        len(
            core.validate_complete_fit_execution_frame(
                sparse_frame,
                scenario_id="sparse_expected_failure",
                split_id="development",
            )
        )
        == 12
    )
    with pytest.raises(ValueError, match="complete fit frame"):
        core.validate_complete_fit_execution_frame(
            sparse_frame[:-1],
            scenario_id="sparse_expected_failure",
            split_id="development",
        )
    assert all(
        row.calibration_replicates == 0
        for row in core.SCENARIO_DEFINITIONS
        if row.scenario_id not in core.NESTED_SCENARIOS
    )
    with pytest.raises(ValueError, match="calibration"):
        core.validate_rng_payload(
            _rng_payload(scenario_id="sparse_expected_failure", split="calibration")
        )


def test_lro_3a_006_fit_variant_is_in_every_fit_derived_primary_key() -> None:
    core = _core()
    assert set(core.FIT_DERIVED_PRIMARY_KEYS) == {
        "replicate_recovery.csv",
        "coverage_calibration.csv",
        "latent_time_calibration.csv",
        "predictive_replicate_diagnostics.csv",
        "predictive_check_summary.csv",
        "identifiability_profiles.csv",
    }
    assert all("fit_variant" in key for key in core.FIT_DERIVED_PRIMARY_KEYS.values())


def test_lro_3a_007_arrival_emits_complete_correct_permuted_pairs() -> None:
    core = _core()
    fit_ids, score_ids = core.authoritative_alignment_frame_cell_ids()
    assert core.expected_potential_design_rows("permuted_arrival_alignment_stress") == 83600
    rows = tuple(
        _successful_fit_row(
            core,
            scenario_id="permuted_arrival_alignment_stress",
            fit_variant=variant,
            fit_index=index,
            source_replicate_first=index,
            source_replicate_last=index,
            heldout_log_score=-10.0 if variant == "correct_alignment" else -12.0,
        )
        for index in range(12)
        for variant in ("correct_alignment", "permuted_alignment")
    )
    assert (
        core.validate_arrival_fit_pairs(
            rows,
            fit_cell_ids=fit_ids,
            score_cell_ids=score_ids,
        )
        == 12
    )
    with pytest.raises(ValueError, match="pair"):
        core.validate_arrival_fit_pairs(
            rows[:2],
            fit_cell_ids=fit_ids,
            score_cell_ids=score_ids,
        )
    with pytest.raises(ValueError, match="duplicate"):
        core.validate_arrival_fit_pairs(
            (*rows, rows[0]),
            fit_cell_ids=fit_ids,
            score_cell_ids=score_ids,
        )
    with pytest.raises(ValueError, match="fixed disjoint"):
        core.validate_arrival_fit_pairs(
            rows,
            fit_cell_ids=fit_ids[:-1],
            score_cell_ids=score_ids,
        )
    swapped_fit_ids = tuple(sorted((*fit_ids[:-1], score_ids[0])))
    swapped_score_ids = tuple(sorted((fit_ids[-1], *score_ids[1:])))
    with pytest.raises(ValueError, match="fixed disjoint"):
        core.validate_arrival_fit_pairs(
            rows,
            fit_cell_ids=swapped_fit_ids,
            score_cell_ids=swapped_score_ids,
        )
    arrival_fit = rows[0]
    frame_count, frame_sha256 = core.authoritative_design_frame_identity(
        "permuted_arrival_alignment_stress"
    )
    assert (frame_count, len(fit_ids), len(score_ids)) == (4180, 4180, 1045)
    assert frame_sha256 == core.cell_identity_sha256(fit_ids)
    with pytest.raises(ValueError, match=r"fit.frame|83.?600|row count"):
        core.validate_fit_execution_row(
            _design_row(
                core,
                arrival_fit,
                design_kind="potential",
                design_n_rows=104500,
            )
        )


def test_lro_3a_008_arrival_primary_tables_use_permuted_only() -> None:
    core = _core()
    for table in core.FIT_DERIVED_PRIMARY_KEYS:
        with pytest.raises(ValueError, match="comparator"):
            core.validate_primary_fit_variant(
                table, "permuted_arrival_alignment_stress", "correct_alignment"
            )


def test_lro_3a_009_equal_shared_fits_have_no_fake_replicate_id() -> None:
    core = _core()
    rows = tuple(
        _fit_row(
            core,
            scenario_id="no_emission_contrast_negative_control",
            fit_scope="scenario_shared",
            fit_variant=variant,
            fit_index=0,
            source_replicate_first=0,
            source_replicate_last=11,
            source_replicate_count=12,
            fit_failure_class=(
                "equal_rate_noninterior_failure"
                if variant == "equal_rate"
                else "optimizer_or_nonfinite_failure"
            ),
            failure_code=(
                "equal_rate_mle_noninterior"
                if variant == "equal_rate"
                else "ordered_emission_optimizer_failed"
            ),
        )
        for variant in ("equal_rate", "ordered_emission")
    )
    assert len(core.validate_fit_execution_rows(rows)) == 2
    with pytest.raises(ValueError):
        core.validate_fit_execution_rows((rows[0] | {"fit_index": 4}, rows[1]))


def test_lro_3a_010_equal_bootstrap_pairs_are_complete_and_recomputable() -> None:
    core = _core()
    rows = _equal_fit_rows(core)
    bootstrap = rows[2:]
    reconstructed = core.recompute_equal_emission_bootstrap(rows)
    assert reconstructed["bootstrap_replicates"] == 199
    assert reconstructed["observed_statistic"] == 2.0
    assert reconstructed["p_value"] == 1.0
    with pytest.raises(ValueError, match="199"):
        core.recompute_equal_emission_bootstrap(rows[:-2])
    with pytest.raises(ValueError, match="observed"):
        core.recompute_equal_emission_bootstrap(bootstrap)
    mixed = list(rows)
    mixed[0] = mixed[0] | {
        "split_id": "development",
        "source_replicate_last": 11,
        "source_replicate_count": 12,
    }
    with pytest.raises(ValueError, match="split"):
        core.recompute_equal_emission_bootstrap(mixed)


def test_lro_3a_011_every_primary_science_row_reconciles_to_one_fit_row(
    monkeypatch: pytest.MonkeyPatch,
    canonical_nine_audit_preflight: Any,
    complete_science_tables: dict[str, tuple[dict[str, object], ...]],
) -> None:
    core = _core()
    recovery_rows, recovery_fits = _recovery_frame(
        core,
        scenario_id="dense_count_exact_model",
        split_id="development",
        parameter_id="beta_driver",
        widths=(1.0,),
        signed_errors=(0.0,),
    )
    core.validate_primary_science_foreign_keys(
        "replicate_recovery.csv", recovery_rows, recovery_fits
    )
    forged_truth_row = recovery_rows[0] | {
        "truth_value": 1.0,
        "signed_error": 0.25,
        "absolute_error": 0.25,
    }
    with pytest.raises(ValueError, match=r"truth|authority"):
        core.validate_replicate_recovery_row(forged_truth_row)
    fit_mismatch = recovery_rows[0] | {
        "estimate": 1.0,
        "signed_error": -0.25,
        "absolute_error": 0.25,
    }
    with pytest.raises(ValueError, match=r"fit|reconcile|estimate|evidence"):
        core.validate_primary_science_foreign_keys(
            "replicate_recovery.csv",
            (fit_mismatch,),
            recovery_fits,
        )

    zero_rows, zero_fits = _recovery_frame(
        core,
        scenario_id="zero_driver_effect_negative_control",
        split_id="holdout",
        parameter_id="beta_driver",
        widths=(2.0,),
        signed_errors=(0.0,),
    )
    zero_truth_free = zero_rows[0] | {
        "truth_value": None,
        "truth_in_interval": None,
        "signed_error": None,
        "absolute_error": None,
    }
    with pytest.raises(ValueError, match=r"truth|zero.driver"):
        core.validate_replicate_recovery_row(zero_truth_free)
    with pytest.raises(ValueError, match=r"truth|reconcile"):
        core.validate_primary_science_foreign_keys(
            "replicate_recovery.csv", (zero_truth_free,), zero_fits
        )

    dense_rows, dense_fits = _recovery_frame(
        core,
        scenario_id="dense_count_exact_model",
        split_id="holdout",
        parameter_id="beta_driver",
        widths=tuple([1.0] * 48),
        signed_errors=tuple([0.0] * 48),
    )
    forged_dense_rows = tuple(
        row
        | {
            "truth_value": 0.0,
            "truth_in_interval": False,
            "signed_error": 1.25,
            "absolute_error": 1.25,
        }
        for row in dense_rows
    )
    with pytest.raises(ValueError, match=r"truth|authority"):
        core.summarize_attempted_recovery(
            forged_dense_rows,
            fit_rows=dense_fits,
            attempted=48,
            support_width=6.0,
        )

    failed_fit = _fit_row(core)
    latent_rows = core.build_latent_diagnostic_rows(
        scenario_id="dense_count_exact_model",
        split_id="development",
        replicate_id=0,
        fit_succeeded=False,
    )
    core.validate_primary_science_foreign_keys(
        "latent_time_calibration.csv", latent_rows, (failed_fit,)
    )
    with pytest.raises(ValueError, match=r"fit|status|reconcile"):
        core.validate_primary_science_foreign_keys(
            "latent_time_calibration.csv",
            tuple(row | {"fit_succeeded": True} for row in latent_rows),
            (failed_fit,),
        )

    predictive_rows = core.failed_predictive_rows(
        scenario_id="dense_count_exact_model",
        split_id="development",
        replicate_id=0,
        opportunity_frame=core.deterministic_predictive_opportunity_frame(
            "dense_count_exact_model", "development", 0
        ),
    )
    core.validate_primary_science_foreign_keys(
        "predictive_replicate_diagnostics.csv", predictive_rows, (failed_fit,)
    )
    with pytest.raises(ValueError, match=r"27|complete|schema"):
        core.validate_primary_science_foreign_keys(
            "predictive_replicate_diagnostics.csv", predictive_rows[:-1], (failed_fit,)
        )

    profile_fit = _successful_fit_row(core)
    profile_rows = tuple(
        {
            "scenario_id": "dense_count_exact_model",
            "split_id": "development",
            "replicate_id": 0,
            "fit_variant": "canonical",
            "parameter_id": "alpha",
            "grid_index": grid_index,
            "parameter_value": parameter_value,
            "profile_log_likelihood": profile_likelihood,
            "likelihood_ratio_delta": delta,
            "nuisance_converged": True,
            "inside_interval": True,
        }
        for grid_index, parameter_value, profile_likelihood, delta in (
            (0, -7.0, -101.0, 2.0),
            (1, -6.0, -100.0, 0.0),
            (2, -5.0, -101.0, 2.0),
        )
    )
    core.validate_primary_science_foreign_keys(
        "identifiability_profiles.csv", profile_rows, (profile_fit,)
    )
    with pytest.raises(ValueError, match=r"likelihood|delta|profile"):
        core.validate_primary_science_foreign_keys(
            "identifiability_profiles.csv",
            (profile_rows[0] | {"likelihood_ratio_delta": 1.0}, *profile_rows[1:]),
            (profile_fit,),
        )

    contradictory_fit = _successful_fit_row(core, beta_driver_estimate=1.25)
    contradictory_recovery = {
        "scenario_id": "dense_count_exact_model",
        "split_id": "development",
        "replicate_id": 0,
        "fit_variant": "canonical",
        "parameter_id": "beta_driver",
        "truth_value": 1.25,
        "estimate": 1.25,
        "interval_lower": -3.0,
        "interval_upper": 3.0,
        "interval_width": 6.0,
        "converged": True,
        "converged_start_count": 8,
        "at_boundary": False,
        "profile_two_sided": True,
        "truth_in_interval": True,
        "log_likelihood": -100.0,
        "signed_error": 0.0,
        "absolute_error": 0.0,
        "gate_result": "pass",
    }
    contradictory_profile = tuple(
        {
            "scenario_id": "dense_count_exact_model",
            "split_id": "development",
            "replicate_id": 0,
            "fit_variant": "canonical",
            "parameter_id": "beta_driver",
            "grid_index": grid_index,
            "parameter_value": parameter_value,
            "profile_log_likelihood": profile_likelihood,
            "likelihood_ratio_delta": delta,
            "nuisance_converged": True,
            "inside_interval": delta <= core.PROFILE_LR_CUTOFF,
        }
        for grid_index, parameter_value, profile_likelihood, delta in (
            (0, -3.0, -102.0, 4.0),
            (1, 1.25, -100.0, 0.0),
            (2, 3.0, -102.0, 4.0),
        )
    )
    with pytest.raises(ValueError, match=r"profile|interval|root|cross"):
        core.validate_recovery_profile_reconciliation(
            (contradictory_recovery,), contradictory_profile, (contradictory_fit,)
        )
    root_likelihood = -100.0 - core.PROFILE_LR_CUTOFF / 2.0
    root_delta = 2.0 * (-100.0 - root_likelihood)
    consistent_profile = tuple(
        {
            "scenario_id": "dense_count_exact_model",
            "split_id": "development",
            "replicate_id": 0,
            "fit_variant": "canonical",
            "parameter_id": "beta_driver",
            "grid_index": grid_index,
            "parameter_value": parameter_value,
            "profile_log_likelihood": profile_likelihood,
            "likelihood_ratio_delta": delta,
            "nuisance_converged": True,
            "inside_interval": delta <= core.PROFILE_LR_CUTOFF,
        }
        for grid_index, parameter_value, profile_likelihood, delta in (
            (0, -3.0, -102.0, 4.0),
            (1, 0.75, root_likelihood, root_delta),
            (2, 1.25, -100.0, 0.0),
            (3, 1.75, root_likelihood, root_delta),
            (4, 3.0, -102.0, 4.0),
        )
    )
    consistent_recovery = contradictory_recovery | {
        "interval_lower": 0.75,
        "interval_upper": 1.75,
        "interval_width": 1.0,
    }
    core.validate_recovery_profile_reconciliation(
        (consistent_recovery,), consistent_profile, (contradictory_fit,)
    )
    open_profile = tuple(
        row
        for row in (
            consistent_profile[0]
            | {
                "grid_index": 0,
                "profile_log_likelihood": -101.0,
                "likelihood_ratio_delta": 2.0,
                "inside_interval": True,
            },
            consistent_profile[2] | {"grid_index": 1},
            consistent_profile[-1]
            | {
                "grid_index": 2,
                "profile_log_likelihood": -101.0,
                "likelihood_ratio_delta": 2.0,
                "inside_interval": True,
            },
        )
    )
    open_recovery = contradictory_recovery | {
        "interval_lower": None,
        "interval_upper": None,
        "interval_width": None,
        "profile_two_sided": False,
        "truth_in_interval": None,
        "gate_result": "fail",
    }
    core.validate_recovery_profile_reconciliation(
        (open_recovery,), open_profile, (contradictory_fit,)
    )
    with pytest.raises(ValueError, match=r"missing|profile"):
        core.validate_recovery_profile_reconciliation(
            (consistent_recovery,), (), (contradictory_fit,)
        )

    validated_bundle = core.validate_science_bundle(**complete_science_tables)
    assert tuple(dict(validated_bundle.scenario_results)) == core.SCENARIO_IDS
    for table_name in (
        "fit_rows",
        "recovery_rows",
        "profile_rows",
        "coverage_rows",
        "latent_rows",
        "predictive_rows",
        "predictive_summary_rows",
        "control_rows",
    ):
        with pytest.raises(
            ValueError,
            match=r"complete|frame|profile|control|identity|schema|latent|predictive|coverage|fit",
        ):
            core.validate_science_bundle(
                **(complete_science_tables | {table_name: complete_science_tables[table_name][:-1]})
            )
    with pytest.raises(ValueError, match=r"duplicate|frame|identity"):
        core.validate_science_bundle(
            **(
                complete_science_tables
                | {
                    "fit_rows": tuple(
                        sorted(
                            (
                                *complete_science_tables["fit_rows"],
                                complete_science_tables["fit_rows"][0],
                            ),
                            key=lambda row: _fit_evidence_sort_key(core, row),
                        )
                    )
                }
            )
        )

    assert len(validated_bundle.design_rows) == 1695
    target_design = next(
        row
        for row in complete_science_tables["fit_rows"]
        if row["scenario_id"] == "structured_imperfect_effort"
        and row["split_id"] == "holdout"
        and row["evidence_row_type"] == "design_diagnostic"
        and row["design_kind"] == "plugin"
    )
    without_design = tuple(
        row for row in complete_science_tables["fit_rows"] if row is not target_design
    )
    with pytest.raises(ValueError, match=r"design.*missing|design identity"):
        core.validate_science_bundle(**(complete_science_tables | {"fit_rows": without_design}))
    duplicated_design = tuple(
        sorted(
            (*complete_science_tables["fit_rows"], target_design),
            key=lambda row: _fit_evidence_sort_key(core, row),
        )
    )
    with pytest.raises(ValueError, match=r"duplicate|design identity"):
        core.validate_science_bundle(**(complete_science_tables | {"fit_rows": duplicated_design}))

    boundary_design = _with_design_update(
        core,
        complete_science_tables,
        scenario_id="structured_imperfect_effort",
        design_kind="plugin",
        update={"design_condition_number": float(np.nextafter(1e8, 0.0))},
    )
    assert core.validate_science_bundle(**boundary_design).recommendation.recommendation_rank == 4
    design_failures: tuple[tuple[str, str, dict[str, object], str], ...] = (
        (
            "process_oracle_observed_transition",
            "potential",
            {
                "design_rank": 2,
                "design_condition_number": None,
                "design_passed": False,
                "design_failure_code": "rank_deficient",
            },
            "contract_failure:process_oracle_failed",
        ),
        (
            "process_oracle_observed_transition",
            "oracle",
            {
                "design_rank": 2,
                "design_condition_number": None,
                "design_passed": False,
                "design_failure_code": "rank_deficient",
            },
            "contract_failure:process_oracle_failed",
        ),
        (
            "dense_count_exact_model",
            "plugin",
            {
                "design_rank": 2,
                "design_condition_number": None,
                "design_passed": False,
                "design_failure_code": "rank_deficient",
            },
            "contract_failure:dense_evidence_invalid",
        ),
        (
            "structured_imperfect_effort",
            "plugin",
            {
                "design_condition_number": 1e8,
                "design_passed": False,
                "design_failure_code": "condition_limit_failed",
            },
            "contract_failure:structured_not_calibrated",
        ),
    )
    for scenario_id, design_kind, update, _expected_reason in design_failures:
        candidate = _with_design_update(
            core,
            complete_science_tables,
            scenario_id=scenario_id,
            design_kind=design_kind,
            update=update,
            recompute_controls=False,
        )
        with pytest.raises(ValueError, match=r"fit.*design|state|contradict"):
            core.validate_science_bundle(**candidate)

    failed_fit = _fit_row(core, failure_code="joint_optimizer_failed")
    passing_potential_row = _design_row(core, failed_fit, design_kind="potential")
    joint_not_evaluated = _design_row(
        core,
        failed_fit,
        design_kind="plugin",
        rank=0,
        condition_number=None,
        passed=False,
        failure_code="joint_fit_failed_or_nonfinite",
    )
    core.validate_fit_design_state_machine(
        (failed_fit,), (passing_potential_row, joint_not_evaluated)
    )
    failed_potential_fit = failed_fit | {
        "fit_failure_class": "potential_rank_gate_failure",
        "failure_code": "potential_design_rank_failed",
    }
    failed_potential_row = _design_row(
        core,
        failed_potential_fit,
        design_kind="potential",
        rank=2,
        condition_number=None,
        passed=False,
        failure_code="rank_deficient",
    )
    downstream_not_evaluated = _design_row(
        core,
        failed_potential_fit,
        design_kind="plugin",
        rank=0,
        condition_number=None,
        passed=False,
        failure_code="not_evaluated_potential_failed",
    )
    core.validate_fit_design_state_machine(
        (failed_potential_fit,), (failed_potential_row, downstream_not_evaluated)
    )
    with pytest.raises(ValueError, match=r"downstream|potential|state"):
        core.validate_fit_design_state_machine(
            (failed_potential_fit,),
            (
                failed_potential_row,
                _design_row(core, failed_potential_fit, design_kind="plugin"),
            ),
        )
    with pytest.raises(ValueError, match=r"failed fit|state|contradiction"):
        core.validate_fit_design_state_machine(
            (failed_fit,),
            (passing_potential_row, _design_row(core, failed_fit, design_kind="plugin")),
        )

    failed_oracle_fit = _fit_row(
        core,
        scenario_id="process_oracle_observed_transition",
        failure_code="process_oracle_optimizer_failed",
    )
    oracle_potential = _design_row(core, failed_oracle_fit, design_kind="potential")
    oracle_not_evaluated = _design_row(
        core,
        failed_oracle_fit,
        design_kind="oracle",
        rank=0,
        condition_number=None,
        passed=False,
        failure_code="process_oracle_fit_failed_or_nonfinite",
    )
    core.validate_fit_design_state_machine(
        (failed_oracle_fit,), (oracle_potential, oracle_not_evaluated)
    )

    _fit_ids, score_ids = core.authoritative_alignment_frame_cell_ids()
    fit_frame = _issued_fit_frame(core)
    fit_frame_kwargs = {
        "fit_frame": fit_frame,
        "fit_frame_cell_count": fit_frame.cell_count,
        "fit_frame_sha256": fit_frame.cell_sha256,
    }
    score_histories = tuple(
        core.AnalystHistory(
            cell_id=cell_id,
            standardized_quality=float((index % 5) - 2) / 2.0,
            predator_arrival_time=float((index % 21) * 6),
            opportunities=(core.CountOpportunity(time=0, count=0, effort=1.0),),
        )
        for index, cell_id in enumerate(score_ids)
    )
    score_optimizer_called = False

    def score_optimizer(_kind: str, _objective: object) -> Any:
        nonlocal score_optimizer_called
        score_optimizer_called = True
        return _synthetic_joint_fit(core)

    monkeypatch.setattr(core, "_run_multistart_optimization", score_optimizer)
    with pytest.raises(ValueError, match=r"canonical fit frame"):
        core.fit_joint_analyst_histories(
            score_histories,
            fit_frame=fit_frame,
            preflight=canonical_nine_audit_preflight,
        )
    with pytest.raises(ValueError, match=r"canonical fit frame"):
        core.fit_joint_analyst_histories(
            _authoritative_fit_histories(core, "dense_count_exact_model"),
            fit_frame=fit_frame,
            preflight=canonical_nine_audit_preflight,
        )
    assert score_optimizer_called is False

    passing_design = core.DesignDiagnostic(
        provenance="potential_design",
        role="ANALYST-PREFLIGHT",
        n_rows=fit_frame.cell_count * 20,
        n_columns=3,
        rank=3,
        condition_number=2.0,
        passed=True,
    )
    failed_plugin = core.DesignDiagnostic(
        provenance="joint_plugin_smoothed_at_risk",
        role="ANALYST-JOINT-PRACTICAL",
        n_rows=fit_frame.cell_count * 20,
        n_columns=3,
        rank=2,
        condition_number=math.inf,
        passed=False,
        failure_reason="rank_deficient",
    )
    impossible_positive_dimensions = (
        ("potential_design", "ANALYST-PREFLIGHT"),
        ("joint_plugin_smoothed_at_risk", "ANALYST-JOINT-PRACTICAL"),
        ("process_oracle_truth_at_risk", "ORACLE-BENCHMARK-ONLY"),
    )
    for provenance, role in impossible_positive_dimensions:
        for n_rows in (1, 2):
            with pytest.raises(ValueError, match=r"rank|row|dimension"):
                core.DesignDiagnostic(
                    provenance=provenance,
                    role=role,
                    n_rows=n_rows,
                    n_columns=3,
                    rank=3,
                    condition_number=1.0,
                    passed=True,
                )
        valid_square = core.DesignDiagnostic(
            provenance=provenance,
            role=role,
            n_rows=3,
            n_columns=3,
            rank=3,
            condition_number=1.0,
            passed=True,
        )
        assert valid_square.passed is True
    forged_updates: tuple[dict[str, object], ...] = (
        {"rank": 2, "passed": True},
        {"condition_number": 1e8, "passed": True},
        {"condition_number": math.nan, "passed": True},
        {"n_rows": 0},
        {"failure_reason": "rank_deficient"},
    )
    for update in forged_updates:
        forged = object.__new__(core.DesignDiagnostic)
        for name, value in asdict(passing_design).items():
            object.__setattr__(forged, name, update.get(name, value))
        with pytest.raises(
            (TypeError, ValueError), match=r"design|rank|condition|dimension|failure"
        ):
            core.JointFitResult(
                converged=True,
                parameters=_joint_parameters(core),
                multistart=_synthetic_joint_fit(core),
                potential_diagnostic=forged,
                plugin_diagnostic=replace(
                    passing_design,
                    provenance="joint_plugin_smoothed_at_risk",
                    role="ANALYST-JOINT-PRACTICAL",
                ),
                **fit_frame_kwargs,
                failure_class=None,
                failure_reason=None,
            )
        plugin_forged = object.__new__(core.DesignDiagnostic)
        for name, value in asdict(forged).items():
            object.__setattr__(
                plugin_forged,
                name,
                (
                    "joint_plugin_smoothed_at_risk"
                    if name == "provenance"
                    else "ANALYST-JOINT-PRACTICAL"
                    if name == "role"
                    else value
                ),
            )
        with pytest.raises(
            (TypeError, ValueError), match=r"design|rank|condition|dimension|failure"
        ):
            core.JointFitResult(
                converged=True,
                parameters=_joint_parameters(core),
                multistart=_synthetic_joint_fit(core),
                potential_diagnostic=passing_design,
                plugin_diagnostic=plugin_forged,
                **fit_frame_kwargs,
                failure_class=None,
                failure_reason=None,
            )
        oracle_forged = object.__new__(core.DesignDiagnostic)
        for name, value in asdict(forged).items():
            object.__setattr__(
                oracle_forged,
                name,
                (
                    "process_oracle_truth_at_risk"
                    if name == "provenance"
                    else "ORACLE-BENCHMARK-ONLY"
                    if name == "role"
                    else value
                ),
            )
        with pytest.raises(
            (TypeError, ValueError), match=r"design|rank|condition|dimension|failure"
        ):
            core.ProcessOracleFitResult(
                converged=True,
                parameters=_process_parameters(core),
                multistart=_synthetic_multistart_fit(core, "process_oracle"),
                at_risk_diagnostic=oracle_forged,
                failure_class=None,
                failure_reason=None,
            )
    constructor_rejected = False
    try:
        core.JointFitResult(
            converged=True,
            parameters=_joint_parameters(core),
            multistart=_synthetic_joint_fit(core),
            potential_diagnostic=passing_design,
            plugin_diagnostic=failed_plugin,
            **fit_frame_kwargs,
            failure_class="plugin_rank_gate_failure",
            failure_reason="joint_plugin_design_gate_failed",
        )
    except ValueError:
        constructor_rejected = True
    with pytest.raises(ValueError, match=r"propagate one typed failure"):
        core.JointFitResult(
            converged=False,
            parameters=None,
            multistart=None,
            potential_diagnostic=None,
            plugin_diagnostic=None,
            **fit_frame_kwargs,
            failure_class="preflight_or_input_failure",
            failure_reason="",
        )

    histories = _authoritative_fit_histories(core)
    monkeypatch.setattr(
        core,
        "_run_multistart_optimization",
        lambda _kind, _objective: _synthetic_joint_fit(core),
    )
    monkeypatch.setattr(
        core,
        "joint_plugin_smoothed_at_risk_diagnostic",
        lambda _histories, _parameters: failed_plugin,
    )
    failed_result = core.fit_joint_analyst_histories(
        histories,
        fit_frame=fit_frame,
        preflight=canonical_nine_audit_preflight,
    )
    assert (
        constructor_rejected,
        failed_result.converged,
        failed_result.parameters,
        failed_result.multistart is not None and failed_result.multistart.converged,
        failed_result.plugin_diagnostic is failed_plugin,
        failed_result.failure_reason,
    ) == (
        True,
        False,
        None,
        True,
        True,
        "joint_plugin_design_gate_failed",
    )

    contradictory_fit_rows: list[dict[str, object]] = []
    for row in complete_science_tables["fit_rows"]:
        target = (
            row["scenario_id"] == "no_emission_contrast_negative_control"
            and row["split_id"] == "holdout"
            and row["fit_scope"] == "bootstrap_shared"
            and row["fit_variant"] == "ordered_emission"
            and row["fit_index"] == 0
        )
        if target and row["evidence_row_type"] == "fit_result":
            contradictory_fit_rows.append(
                row
                | {
                    "fit_succeeded": False,
                    "fit_failure_class": "optimizer_or_nonfinite_failure",
                    "converged_start_count": 0,
                    "best_start_index": None,
                    "best_two_log_likelihoods_agree": False,
                    "at_boundary": None,
                    "boundary_parameter_ids": None,
                    "alpha_estimate": None,
                    "beta_driver_estimate": None,
                    "beta_quality_estimate": None,
                    "lambda_quasi_estimate": None,
                    "lambda_present_estimate": None,
                    "lambda_equal_estimate": None,
                    "log_likelihood": None,
                    "heldout_log_score": None,
                    "failure_code": "ordered_bootstrap_fit_failed",
                }
            )
        elif (
            target
            and row["evidence_row_type"] == "design_diagnostic"
            and row["design_kind"] == "plugin"
        ):
            contradictory_fit_rows.append(
                row
                | {
                    "design_rank": 2,
                    "design_condition_number": None,
                    "design_passed": False,
                    "design_failure_code": "rank_deficient",
                }
            )
        else:
            contradictory_fit_rows.append(row)
    contradictory_tables = complete_science_tables | {"fit_rows": tuple(contradictory_fit_rows)}
    with pytest.raises(ValueError, match=r"failure|transition|optimizer|design"):
        core.recompute_control_decision_rows(
            **{
                name: value
                for name, value in contradictory_tables.items()
                if name != "control_rows"
            }
        )

    assert core.FIT_FAILURE_TRANSITION_TABLE == (
        ("preflight_or_input_failure", "none", "not_persistable"),
        ("potential_rank_gate_failure", "potential", "rank_deficient"),
        ("potential_condition_gate_failure", "potential", "condition_limit_failed"),
        ("optimizer_or_nonfinite_failure", "downstream", "fit_failed_or_nonfinite"),
        ("plugin_rank_gate_failure", "plugin", "rank_deficient"),
        ("plugin_condition_gate_failure", "plugin", "condition_limit_failed"),
        ("oracle_rank_gate_failure", "oracle", "rank_deficient"),
        ("oracle_condition_gate_failure", "oracle", "condition_limit_failed"),
        ("equal_rate_noninterior_failure", "none", "not_applicable"),
    )

    def transitioned_complete_fit_rows(
        *,
        scenario_id: str,
        split_id: str,
        fit_scope: str,
        fit_variant: str,
        fit_index: int,
        failure_class: str,
    ) -> tuple[dict[str, object], ...]:
        identity = (scenario_id, split_id, fit_scope, fit_variant, fit_index)
        optimizer_fields: tuple[object, object, object]
        if failure_class in {
            "plugin_rank_gate_failure",
            "plugin_condition_gate_failure",
        }:
            optimizer_fields = (8, 1, True)
        elif failure_class == "optimizer_or_nonfinite_failure":
            optimizer_fields = (0, None, False)
        else:
            optimizer_fields = (None, None, None)
        transitioned: list[dict[str, object]] = []
        for row in complete_science_tables["fit_rows"]:
            row_identity = tuple(
                row[name]
                for name in (
                    "scenario_id",
                    "split_id",
                    "fit_scope",
                    "fit_variant",
                    "fit_index",
                )
            )
            if row_identity != identity:
                transitioned.append(row)
                continue
            if row["evidence_row_type"] == "fit_result":
                transitioned.append(
                    row
                    | {
                        "fit_succeeded": False,
                        "converged_start_count": optimizer_fields[0],
                        "best_start_index": optimizer_fields[1],
                        "best_two_log_likelihoods_agree": optimizer_fields[2],
                        "at_boundary": None,
                        "boundary_parameter_ids": None,
                        "alpha_estimate": None,
                        "beta_driver_estimate": None,
                        "beta_quality_estimate": None,
                        "lambda_quasi_estimate": None,
                        "lambda_present_estimate": None,
                        "lambda_equal_estimate": None,
                        "log_likelihood": None,
                        "heldout_log_score": None,
                        "fit_failure_class": failure_class,
                        "failure_code": f"fixture_{failure_class}",
                    }
                )
                continue
            design_kind = cast(str, row["design_kind"])
            update: dict[str, object] = {}
            if failure_class == "potential_rank_gate_failure":
                update = (
                    {
                        "design_rank": 2,
                        "design_condition_number": None,
                        "design_passed": False,
                        "design_failure_code": "rank_deficient",
                    }
                    if design_kind == "potential"
                    else {
                        "design_rank": 0,
                        "design_condition_number": None,
                        "design_passed": False,
                        "design_failure_code": "not_evaluated_potential_failed",
                    }
                )
            elif failure_class == "potential_condition_gate_failure":
                update = (
                    {
                        "design_rank": 3,
                        "design_condition_number": 1e8,
                        "design_passed": False,
                        "design_failure_code": "condition_limit_failed",
                    }
                    if design_kind == "potential"
                    else {
                        "design_rank": 0,
                        "design_condition_number": None,
                        "design_passed": False,
                        "design_failure_code": "not_evaluated_potential_failed",
                    }
                )
            elif failure_class == "optimizer_or_nonfinite_failure" and design_kind != ("potential"):
                update = {
                    "design_rank": 0,
                    "design_condition_number": None,
                    "design_passed": False,
                    "design_failure_code": (
                        "process_oracle_fit_failed_or_nonfinite"
                        if design_kind == "oracle"
                        else "joint_fit_failed_or_nonfinite"
                    ),
                }
            elif (
                failure_class
                in {
                    "plugin_rank_gate_failure",
                    "oracle_rank_gate_failure",
                }
                and design_kind == failure_class.split("_", maxsplit=1)[0]
            ):
                update = {
                    "design_rank": 2,
                    "design_condition_number": None,
                    "design_passed": False,
                    "design_failure_code": "rank_deficient",
                }
            elif (
                failure_class
                in {
                    "plugin_condition_gate_failure",
                    "oracle_condition_gate_failure",
                }
                and design_kind == failure_class.split("_", maxsplit=1)[0]
            ):
                update = {
                    "design_rank": 3,
                    "design_condition_number": 1e8,
                    "design_passed": False,
                    "design_failure_code": "condition_limit_failed",
                }
            transitioned.append(row | update)
        return tuple(transitioned)

    joint_transition_classes = (
        "potential_rank_gate_failure",
        "potential_condition_gate_failure",
        "optimizer_or_nonfinite_failure",
        "plugin_rank_gate_failure",
        "plugin_condition_gate_failure",
    )
    for failure_class in joint_transition_classes:
        candidate_rows = transitioned_complete_fit_rows(
            scenario_id="no_emission_contrast_negative_control",
            split_id="holdout",
            fit_scope="bootstrap_shared",
            fit_variant="ordered_emission",
            fit_index=0,
            failure_class=failure_class,
        )
        fits = tuple(row for row in candidate_rows if row["evidence_row_type"] == "fit_result")
        designs = tuple(
            row for row in candidate_rows if row["evidence_row_type"] == "design_diagnostic"
        )
        core.validate_fit_design_state_machine(fits, designs)
        candidate_tables = complete_science_tables | {"fit_rows": candidate_rows}
        controls = core.recompute_control_decision_rows(
            **{name: value for name, value in candidate_tables.items() if name != "control_rows"}
        )
        core.validate_science_bundle(**(candidate_tables | {"control_rows": controls}))

    for scenario_id, fit_variant, failure_class in (
        (
            "process_oracle_observed_transition",
            "canonical",
            "optimizer_or_nonfinite_failure",
        ),
        (
            "process_oracle_observed_transition",
            "canonical",
            "oracle_rank_gate_failure",
        ),
        (
            "process_oracle_observed_transition",
            "canonical",
            "oracle_condition_gate_failure",
        ),
        (
            "observation_oracle_fixed_transition",
            "canonical",
            "optimizer_or_nonfinite_failure",
        ),
    ):
        candidate_rows = transitioned_complete_fit_rows(
            scenario_id=scenario_id,
            split_id="development",
            fit_scope="replicate",
            fit_variant=fit_variant,
            fit_index=0,
            failure_class=failure_class,
        )
        core.validate_fit_design_state_machine(
            tuple(row for row in candidate_rows if row["evidence_row_type"] == "fit_result"),
            tuple(row for row in candidate_rows if row["evidence_row_type"] == "design_diagnostic"),
        )

    equal_noninterior_rows = transitioned_complete_fit_rows(
        scenario_id="no_emission_contrast_negative_control",
        split_id="holdout",
        fit_scope="bootstrap_shared",
        fit_variant="equal_rate",
        fit_index=0,
        failure_class="equal_rate_noninterior_failure",
    )
    equal_noninterior_rows = tuple(
        row
        | {
            "failure_code": "equal_rate_mle_noninterior",
        }
        if row["evidence_row_type"] == "fit_result"
        and row["scenario_id"] == "no_emission_contrast_negative_control"
        and row["split_id"] == "holdout"
        and row["fit_scope"] == "bootstrap_shared"
        and row["fit_variant"] == "equal_rate"
        and row["fit_index"] == 0
        else row
        for row in equal_noninterior_rows
    )
    core.validate_fit_design_state_machine(
        tuple(row for row in equal_noninterior_rows if row["evidence_row_type"] == "fit_result"),
        tuple(
            row for row in equal_noninterior_rows if row["evidence_row_type"] == "design_diagnostic"
        ),
    )
    preflight_rows = transitioned_complete_fit_rows(
        scenario_id="dense_count_exact_model",
        split_id="development",
        fit_scope="replicate",
        fit_variant="canonical",
        fit_index=0,
        failure_class="preflight_or_input_failure",
    )
    with pytest.raises(ValueError, match=r"typed fit failure|applicable|failure class"):
        core.validate_fit_design_state_machine(
            tuple(row for row in preflight_rows if row["evidence_row_type"] == "fit_result"),
            tuple(row for row in preflight_rows if row["evidence_row_type"] == "design_diagnostic"),
        )


def _one_hot(index: int, count: int = 1) -> np.ndarray[Any, np.dtype[np.float64]]:
    values = np.zeros((count, 21), dtype=np.float64)
    values[:, index] = 1.0
    return values


def test_lro_3l_001_event_censor_indices_and_126_label_are_literal() -> None:
    core = _core()
    assert tuple(range(6, 127, 6)) == core.LATENT_PATH_VALUES
    assert core.censor_transition_index(120) == 20
    assert core.censor_transition_index(None) == 21
    assert core.LATENT_CENSOR_LABEL_IS_BIOLOGICAL is False


def test_lro_3l_002_one_hot_event_and_censor_score_zero() -> None:
    core = _core()
    result = core.evaluate_latent_transition_diagnostics(
        cell_ids=(1, 2),
        path_probabilities=np.eye(21, dtype=np.float64)[[0, 20]],
        truth_transition_times=(6, None),
    )
    assert all(
        value == 0.0
        for value in (
            *result.observed_values.values(),
            *result.expected_values.values(),
            *result.errors.values(),
        )
    )


def test_lro_3l_003_one_category_displacement_scores_point_zero_five_six_six() -> None:
    core = _core()
    result = core.evaluate_latent_transition_diagnostics(
        cell_ids=(1,), path_probabilities=_one_hot(1), truth_transition_times=(6,)
    )
    assert result.observed_values == {
        "transition_brier": 0.05,
        "transition_interval_score": 6.0,
        "transition_median_absolute_error": 6.0,
    }


def test_lro_3l_004_event_six_vs_censor_scores_one_one_twenty_one_twenty() -> None:
    core = _core()
    result = core.evaluate_latent_transition_diagnostics(
        cell_ids=(1,), path_probabilities=_one_hot(20), truth_transition_times=(6,)
    )
    assert result.observed_values == {
        "transition_brier": 1.0,
        "transition_interval_score": 120.0,
        "transition_median_absolute_error": 120.0,
    }


def test_lro_3l_005_brier_and_expected_value_match_hand_calculation() -> None:
    core = _core()
    probabilities = np.zeros((1, 21), dtype=np.float64)
    probabilities[0, (0, 20)] = 0.5
    result = core.evaluate_latent_transition_diagnostics(
        cell_ids=(1,), path_probabilities=probabilities, truth_transition_times=(6,)
    )
    assert result.observed_values["transition_brier"] == pytest.approx(0.25)
    assert result.expected_values["transition_brier"] == pytest.approx(0.25)


def test_lro_3l_006_discrete_quantiles_use_first_crossing() -> None:
    core = _core()
    probabilities = np.zeros(21, dtype=np.float64)
    probabilities[[0, 10, 20]] = (0.05, 0.45, 0.50)
    assert core.latent_quantiles(probabilities) == (6.0, 66.0, 126.0)


def test_lro_3l_007_scaled_interval_expected_value_matches_21_path_enumeration() -> None:
    core = _core()
    probabilities = np.full((1, 21), 1 / 21, dtype=np.float64)
    result = core.evaluate_latent_transition_diagnostics(
        cell_ids=(1,), path_probabilities=probabilities, truth_transition_times=(60,)
    )
    lower, _, upper = core.latent_quantiles(probabilities[0])
    expected = sum(
        (1 / 21) * (0.05 * (upper - lower) + max(lower - value, 0) + max(value - upper, 0))
        for value in core.LATENT_PATH_VALUES
    )
    assert result.expected_values["transition_interval_score"] == pytest.approx(expected)


def test_lro_3l_008_odd_even_medians_and_bayes_risk_are_literal() -> None:
    core = _core()
    assert core.ordinary_median(np.asarray([1.0, 9.0, 3.0])) == 3.0
    assert core.ordinary_median(np.asarray([1.0, 3.0, 9.0, 11.0])) == 6.0
    probabilities = np.vstack((_one_hot(0), _one_hot(1))).reshape(2, 21)
    result = core.evaluate_latent_transition_diagnostics(
        cell_ids=(1, 2), path_probabilities=probabilities, truth_transition_times=(6, 12)
    )
    assert result.expected_values["transition_median_absolute_error"] == 0.0


def test_lro_3l_009_process_oracle_probabilities_precede_truth() -> None:
    core = _core()
    calls: list[object] = []

    def build_probabilities(analyst: object) -> np.ndarray[Any, np.dtype[np.float64]]:
        calls.append(analyst)
        return _one_hot(0)

    probabilities = core.build_process_oracle_probabilities(
        analyst_visible={"quality": (0.0,), "arrival": (6.0,)},
        builder=build_probabilities,
    )
    assert calls == [{"quality": (0.0,), "arrival": (6.0,)}]
    first = core.evaluate_latent_transition_diagnostics(
        cell_ids=(1,), path_probabilities=probabilities, truth_transition_times=(6,)
    )
    second = core.evaluate_latent_transition_diagnostics(
        cell_ids=(1,), path_probabilities=probabilities, truth_transition_times=(12,)
    )
    assert first.observed_values != second.observed_values


def test_lro_3l_010_batched_and_scalar_weights_score_identically() -> None:
    core = _core()
    irregular = np.zeros((4, 21), dtype=np.float64)
    irregular[0, (0, 1)] = (0.25, 0.75)
    irregular[1, (5, 10, 20)] = (0.1, 0.6, 0.3)
    irregular[2] = np.arange(1, 22, dtype=np.float64)
    irregular[2] /= irregular[2].sum()
    irregular[3, (0, 20)] = (0.5, 0.5)
    fixtures = {
        "dense": (
            np.vstack((_one_hot(0), _one_hot(10), _one_hot(20))).reshape(3, 21),
            (6, 66, None),
        ),
        "structured": (
            np.vstack((_one_hot(2), _one_hot(7), _one_hot(14), _one_hot(20))).reshape(4, 21),
            (18, 48, 90, None),
        ),
        "sparse": (
            np.vstack((_one_hot(1), _one_hot(19), _one_hot(20))).reshape(3, 21),
            (12, 120, None),
        ),
        "irregular": (irregular, (12, 66, 120, None)),
    }
    assert tuple(fixtures) == ("dense", "structured", "sparse", "irregular")
    for probabilities, truth in fixtures.values():
        cell_ids = tuple(range(1, len(truth) + 1))
        batched = core.evaluate_latent_transition_diagnostics(
            cell_ids=cell_ids,
            path_probabilities=probabilities,
            truth_transition_times=truth,
        )
        scalar = tuple(
            core.evaluate_latent_transition_diagnostics(
                cell_ids=(cell_id,),
                path_probabilities=probabilities[index : index + 1],
                truth_transition_times=(truth[index],),
            )
            for index, cell_id in enumerate(cell_ids)
        )
        for field in ("observed_values", "expected_values", "errors"):
            batched_values = getattr(batched, field)
            scalar_values = tuple(getattr(item, field) for item in scalar)
            for metric_id in core.LATENT_METRIC_IDS:
                values = np.asarray([item[metric_id] for item in scalar_values], dtype=np.float64)
                expected = (
                    core.ordinary_median(values)
                    if metric_id == "transition_median_absolute_error" and field != "errors"
                    else float(np.mean(values))
                )
                if field == "errors":
                    expected = (
                        batched.observed_values[metric_id] - batched.expected_values[metric_id]
                    )
                assert batched_values[metric_id] == pytest.approx(expected, abs=1e-12)


def test_lro_3l_011_empty_histories_retain_process_paths_and_cells() -> None:
    core = _core()
    cell_ids = core.authoritative_latent_cell_ids("informative_dropout_misspecification_stress")
    rows = core.build_latent_diagnostic_rows(
        scenario_id="informative_dropout_misspecification_stress",
        split_id="holdout",
        replicate_id=0,
        fit_succeeded=True,
        cell_ids=cell_ids,
        path_probabilities=np.tile(_one_hot(20), (5225, 1)),
        truth_transition_times=tuple([None] * 5225),
        evaluator_cell_ids=cell_ids,
        prerequisite_valid=True,
    )
    assert len(rows) == 3 and all(row["sample_size"] == 5225 for row in rows)
    assert all(row["diagnostic_available"] is True for row in rows)


def test_lro_3l_012_censored_truth_remains_in_every_denominator() -> None:
    core = _core()
    result = core.evaluate_latent_transition_diagnostics(
        cell_ids=(1, 2),
        path_probabilities=np.vstack((_one_hot(0), _one_hot(20))).reshape(2, 21),
        truth_transition_times=(6, None),
    )
    assert result.sample_size == 2


def test_lro_3l_013_invalid_probability_or_truth_fails_complete_diagnostic() -> None:
    core = _core()
    valid = np.vstack((_one_hot(0), _one_hot(20))).reshape(2, 21)
    invalid_arrays = (valid[:, :-1], valid * np.nan, valid * -1, valid * 0.5)
    for probabilities in invalid_arrays:
        with pytest.raises(ValueError):
            core.evaluate_latent_transition_diagnostics(
                cell_ids=(1, 2),
                path_probabilities=probabilities,
                truth_transition_times=(6, None),
            )
    with pytest.raises(ValueError):
        core.evaluate_latent_transition_diagnostics(
            cell_ids=(1, 1), path_probabilities=valid, truth_transition_times=(6, None)
        )


def test_lro_3l_014_applicability_and_frame_sizes_are_literal() -> None:
    core = _core()
    assert (
        tuple(
            (row.scenario_id, row.latent_time_applicable, row.latent_time_sample_size)
            for row in core.SCENARIO_EVIDENCE_REGISTRY
        )
        == core.LATENT_APPLICABILITY
    )
    assert {size for _, _, size in core.LATENT_APPLICABILITY} == {0, 1045, 1306, 5225}
    landscape = import_module("spatext.synth.medium.landscape").build_synth_medium_landscape()
    actual_passable_ids = tuple(
        sorted(cell.cell_id for cell in landscape.cells if cell.passability != "water")
    )
    forged_ids = tuple(range(5225))
    assert forged_ids != actual_passable_ids
    forged_rows = core.build_latent_diagnostic_rows(
        scenario_id="dense_count_exact_model",
        split_id="holdout",
        replicate_id=0,
        fit_succeeded=True,
        cell_ids=forged_ids,
        path_probabilities=np.tile(_one_hot(0), (5225, 1)),
        truth_transition_times=tuple([6] * 5225),
        evaluator_cell_ids=forged_ids,
        prerequisite_valid=True,
    )
    assert all(row["diagnostic_available"] is False for row in forged_rows)
    for scenario_id, size in (
        ("sparse_expected_failure", 1306),
        ("permuted_arrival_alignment_stress", 1045),
    ):
        ids = core.authoritative_latent_cell_ids(scenario_id)
        assert len(ids) == size
        rows = core.build_latent_diagnostic_rows(
            scenario_id=scenario_id,
            split_id="holdout",
            replicate_id=0,
            fit_succeeded=True,
            cell_ids=ids,
            path_probabilities=np.tile(_one_hot(20), (size, 1)),
            truth_transition_times=tuple([None] * size),
            evaluator_cell_ids=ids,
            prerequisite_valid=True,
        )
        core.validate_latent_diagnostic_rows(rows)
        assert all(row["diagnostic_available"] is True for row in rows)


def test_lro_3l_015_failed_fit_retains_three_diagnostic_unavailable_rows() -> None:
    core = _core()
    rows = core.build_latent_diagnostic_rows(
        scenario_id="dense_count_exact_model",
        split_id="holdout",
        replicate_id=2,
        fit_succeeded=False,
    )
    assert len(rows) == 3
    assert all(
        row["sample_size"] == 5225
        and row["diagnostic_available"] is False
        and row["gate_result"] == "diagnostic"
        for row in rows
    )


def test_lro_3l_016_inapplicable_attempts_emit_three_not_applicable_rows() -> None:
    core = _core()
    for scenario_id in (
        "observation_oracle_fixed_transition",
        "no_emission_contrast_negative_control",
        "goal018_continuous_abundance_stress",
    ):
        rows = core.build_latent_diagnostic_rows(
            scenario_id=scenario_id, split_id="holdout", replicate_id=0, fit_succeeded=None
        )
        assert all(
            row["sample_size"] == 0
            and row["fit_succeeded"] is None
            and row["gate_result"] == "not_applicable"
            for row in rows
        )


def test_lro_3l_017_metric_values_and_availability_never_change_recommendation() -> None:
    core = _core()
    vector = {scenario_id: "pass" for scenario_id in core.SCENARIO_IDS}
    expected = core.reduce_recommendation(vector)
    cell_ids = core.authoritative_latent_cell_ids("dense_count_exact_model")
    for rows in (
        core.build_latent_diagnostic_rows(
            scenario_id="dense_count_exact_model",
            split_id="holdout",
            replicate_id=0,
            fit_succeeded=False,
        ),
        core.build_latent_diagnostic_rows(
            scenario_id="dense_count_exact_model",
            split_id="holdout",
            replicate_id=0,
            fit_succeeded=True,
            cell_ids=cell_ids,
            path_probabilities=np.tile(_one_hot(0), (5225, 1)),
            truth_transition_times=tuple([6] * 5225),
            evaluator_cell_ids=cell_ids,
            prerequisite_valid=True,
        ),
    ):
        core.validate_latent_diagnostic_rows(rows)
        assert core.reduce_recommendation(vector, latent_rows=rows) == expected
    malformed = [dict(row) for row in rows]
    for row in malformed:
        row.update(
            sample_size=1,
            diagnostic_available=False,
            observed_value=999.0,
            gate_result="pass",
        )
    with pytest.raises(ValueError, match="latent"):
        core.validate_latent_diagnostic_rows(malformed)


def test_lro_3l_018_missing_or_malformed_row_is_schema_failure_only() -> None:
    core = _core()
    rows = core.build_latent_diagnostic_rows(
        scenario_id="dense_count_exact_model",
        split_id="holdout",
        replicate_id=0,
        fit_succeeded=False,
    )
    with pytest.raises(ValueError, match="latent artifact schema"):
        core.validate_latent_diagnostic_rows(rows[:-1])
    assert core.validate_latent_diagnostic_rows(rows) is None


def test_lro_3l_019_no_latent_threshold_object_or_pass_count_exists() -> None:
    core = _core()
    configs: tuple[dict[str, object], ...] = (
        {"latent_time_thresholds": {}},
        {"latent_pass_count": 1},
    )
    for config in configs:
        with pytest.raises(ValueError, match="latent threshold"):
            core.validate_no_latent_thresholds(config)
    core.validate_no_latent_thresholds({"gates": {}})


def test_lro_3l_020_valid_fit_with_failed_prerequisite_or_invalid_posterior_is_unavailable_diagnostic(  # noqa: E501
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    core = _core()
    evaluator_calls = 0
    original_evaluator = core.evaluate_latent_transition_diagnostics

    def observed_evaluator(**kwargs: object) -> Any:
        nonlocal evaluator_calls
        evaluator_calls += 1
        return original_evaluator(**kwargs)

    monkeypatch.setattr(core, "evaluate_latent_transition_diagnostics", observed_evaluator)
    canonical_ids = core.authoritative_latent_cell_ids("dense_count_exact_model")
    recommendation = core.reduce_recommendation(_passing_vector(core))
    for kwargs in (
        {"prerequisite_valid": False},
        {
            "prerequisite_valid": True,
            "cell_ids": canonical_ids,
            "path_probabilities": np.full((len(canonical_ids), 21), np.nan),
            "truth_transition_times": tuple([6] * len(canonical_ids)),
            "evaluator_cell_ids": canonical_ids,
        },
    ):
        rows = core.build_latent_diagnostic_rows(
            scenario_id="dense_count_exact_model",
            split_id="holdout",
            replicate_id=0,
            fit_succeeded=True,
            **kwargs,
        )
        assert all(
            row["fit_succeeded"] is True
            and row["diagnostic_available"] is False
            and row["observed_value"] is None
            for row in rows
        )
        assert core.reduce_recommendation(_passing_vector(core), latent_rows=rows) == recommendation
    assert evaluator_calls == 1, "invalid posterior never reached the owned evaluator"


def _recovery_frame(
    core: Any,
    *,
    scenario_id: str,
    split_id: str,
    parameter_id: str,
    widths: tuple[float, ...],
    signed_errors: tuple[float, ...],
    failed_count: int = 0,
) -> tuple[tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    truth_by_parameter = {
        "alpha": -6.0,
        "beta_driver": 0.0 if scenario_id == "zero_driver_effect_negative_control" else 1.25,
        "beta_quality": -0.60,
        "lambda_quasi": 0.15,
        "lambda_present": 4.0,
    }
    supports = {
        "alpha": (-10.0, -2.0),
        "beta_driver": (-3.0, 3.0),
        "beta_quality": (-2.0, 2.0),
        "lambda_quasi": (0.01, 1.0),
        "lambda_present": (0.25, 10.0),
    }
    truth = truth_by_parameter[parameter_id]
    lower_support, upper_support = supports[parameter_id]
    rows: list[dict[str, object]] = []
    fits: list[dict[str, object]] = []
    for replicate_id, (width, signed_error) in enumerate(zip(widths, signed_errors, strict=True)):
        estimate = truth + signed_error
        exact_signed_error = estimate - truth
        lower = max(lower_support, truth - width / 2.0)
        upper = min(upper_support, lower + width)
        lower = upper - width
        fit = _successful_fit_row(
            core,
            scenario_id=scenario_id,
            split_id=split_id,
            fit_index=replicate_id,
            source_replicate_first=replicate_id,
            source_replicate_last=replicate_id,
            **{f"{parameter_id}_estimate": estimate},
        )
        fits.append(fit)
        rows.append(
            {
                "scenario_id": scenario_id,
                "split_id": split_id,
                "replicate_id": replicate_id,
                "fit_variant": fit["fit_variant"],
                "parameter_id": parameter_id,
                "truth_value": truth,
                "estimate": estimate,
                "interval_lower": lower,
                "interval_upper": upper,
                "interval_width": width,
                "converged": True,
                "converged_start_count": 8,
                "at_boundary": False,
                "profile_two_sided": True,
                "truth_in_interval": lower <= truth <= upper,
                "log_likelihood": -100.0,
                "signed_error": exact_signed_error,
                "absolute_error": abs(exact_signed_error),
                "gate_result": "pass",
            }
        )
    for replicate_id in range(len(widths), len(widths) + failed_count):
        fits.append(
            _fit_row(
                core,
                scenario_id=scenario_id,
                split_id=split_id,
                fit_index=replicate_id,
                source_replicate_first=replicate_id,
                source_replicate_last=replicate_id,
            )
        )
        rows.append(
            {
                "scenario_id": scenario_id,
                "split_id": split_id,
                "replicate_id": replicate_id,
                "fit_variant": "canonical",
                "parameter_id": parameter_id,
                "truth_value": truth,
                "estimate": None,
                "interval_lower": None,
                "interval_upper": None,
                "interval_width": None,
                "converged": False,
                "converged_start_count": None,
                "at_boundary": None,
                "profile_two_sided": False,
                "truth_in_interval": None,
                "log_likelihood": None,
                "signed_error": None,
                "absolute_error": None,
                "gate_result": "fail",
            }
        )
    return tuple(rows), tuple(fits)


def test_lro_3d_001_nested_denominators_imputations_and_even_median_are_literal() -> None:
    core = _core()
    widths = tuple([1.0] * 23 + [3.0, 5.0] + [7.0] * 21)
    signed_errors = tuple([-0.1] * 23 + [0.3] + [0.5] * 22)
    rows, fits = _recovery_frame(
        core,
        scenario_id="dense_count_exact_model",
        split_id="holdout",
        parameter_id="alpha",
        widths=widths,
        signed_errors=signed_errors,
        failed_count=2,
    )
    summary = core.summarize_attempted_recovery(
        rows,
        fit_rows=fits,
        attempted=48,
        support_width=8.0,
    )
    assert summary["replicate_count"] == 48 and summary["converged_count"] == 46
    assert summary["coverage_count"] == 46
    assert summary["median_interval_width"] == 4.0
    assert summary["median_absolute_error"] == pytest.approx(0.4)
    assert summary["maximum_interval_width"] == 8.0
    assert summary["median_signed_error"] == pytest.approx(0.1)
    coverage_row = {
        "scenario_id": "dense_count_exact_model",
        "split_id": "holdout",
        "fit_variant": "canonical",
        "parameter_id": "alpha",
        "replicate_count": 48,
        "converged_count": 46,
        "coverage_count": 46,
        "coverage_fraction": 46 / 48,
        "acceptance_lower_count": 36,
        "acceptance_upper_count": 48,
        "median_signed_error": summary["median_signed_error"],
        "median_absolute_error": summary["median_absolute_error"],
        "median_interval_width": 4.0,
        "maximum_absolute_error": 8.0,
        "maximum_interval_width": 8.0,
        "gate_result": "fail",
    }
    core.validate_coverage_summary_rows((coverage_row,), recovery_rows=rows, fit_rows=fits)
    with pytest.raises(ValueError, match=r"coverage summary|recompute"):
        core.validate_coverage_summary_rows(
            (coverage_row | {"coverage_count": 48},),
            recovery_rows=rows,
            fit_rows=fits,
        )
    for impossible in (
        tuple(row | {"interval_width": -1.0} for row in rows),
        tuple(row | {"absolute_error": float("inf")} for row in rows),
    ):
        with pytest.raises(
            ValueError, match=r"finite|negative|width|error|schema|interval|algebra"
        ):
            core.summarize_attempted_recovery(
                impossible,
                fit_rows=fits,
                attempted=48,
                support_width=8.0,
            )


def test_lro_3d_002_nested_coverage_and_convergence_boundaries_are_unchanged() -> None:
    core = _core()
    assert core.nested_gate(coverage_count=36, converged_count=46, minimum_converged=46)
    assert not core.nested_gate(coverage_count=35, converged_count=46, minimum_converged=46)
    assert not core.nested_gate(coverage_count=36, converged_count=45, minimum_converged=46)
    assert core.nested_gate(coverage_count=36, converged_count=44, minimum_converged=44)
    assert not core.nested_gate(coverage_count=36, converged_count=43, minimum_converged=44)


def test_lro_3d_003_missing_recovery_row_is_contract_failure_not_imputation() -> None:
    core = _core()
    rows, fits = _recovery_frame(
        core,
        scenario_id="dense_count_exact_model",
        split_id="holdout",
        parameter_id="alpha",
        widths=tuple([2.0] * 47),
        signed_errors=tuple([0.0] * 47),
    )
    with pytest.raises(ValueError, match="missing recovery row"):
        core.summarize_attempted_recovery(
            rows,
            fit_rows=fits,
            attempted=48,
            support_width=8.0,
        )


def test_lro_3d_004_sparse_coverage_and_width_use_all_24() -> None:
    core = _core()
    rows, fits = _recovery_frame(
        core,
        scenario_id="sparse_expected_failure",
        split_id="holdout",
        parameter_id="beta_driver",
        widths=tuple([1.0] * 11 + [3.0, 5.0] + [5.0] * 9),
        signed_errors=tuple([0.0] * 22),
        failed_count=2,
    )
    summary = core.summarize_attempted_recovery(
        rows,
        fit_rows=fits,
        attempted=24,
        support_width=6.0,
    )
    assert summary["coverage_count"] == 22
    assert summary["median_interval_width"] == 4.0
    assert core.sparse_honesty(
        coverage_count=22, sparse_width=4.0, structured_width=4.0, predictive_pass=True
    )


def test_lro_3d_005_sparse_equal_width_passes_next_value_below_fails() -> None:
    core = _core()
    assert core.sparse_honesty(
        coverage_count=18, sparse_width=3.0, structured_width=3.0, predictive_pass=True
    )
    assert not core.sparse_honesty(
        coverage_count=18,
        sparse_width=np.nextafter(3.0, 0.0),
        structured_width=3.0,
        predictive_pass=True,
    )


def test_lro_3d_006_sparse_failed_fit_cannot_be_rescued_by_imputation() -> None:
    core = _core()
    assert not core.sparse_honesty(
        coverage_count=24, sparse_width=6.0, structured_width=1.0, predictive_pass=False
    )


def test_lro_3d_007_sparse_low_error_or_24_coverage_adds_no_gate() -> None:
    core = _core()
    assert core.sparse_honesty(
        coverage_count=24,
        sparse_width=6.0,
        structured_width=6.0,
        predictive_pass=True,
        descriptive_error=999.0,
    )


def test_lro_3d_008_zero_driver_touching_zero_is_not_exclusion() -> None:
    core = _core()
    assert not core.interval_excludes_zero(0.0, 1.0)
    assert not core.interval_excludes_zero(-1.0, 0.0)
    assert not core.interval_excludes_zero(-1.0, 1.0)


def test_lro_3d_009_zero_driver_six_passes_seven_confounds() -> None:
    core = _core()
    assert core.zero_driver_decision(tuple([(1.0, 2.0)] * 6 + [(-1.0, 1.0)] * 18)) == "pass"
    assert core.zero_driver_decision(tuple([(1.0, 2.0)] * 7 + [(-1.0, 1.0)] * 17)) == (
        "confounding:zero_driver_false_signal"
    )


def test_lro_3d_010_zero_driver_failed_open_missing_are_undecidable() -> None:
    core = _core()
    for interval in ((None, 1.0), (-1.0, None), None):
        values = tuple([(-1.0, 1.0)] * 23 + [interval])
        assert core.zero_driver_decision(values) == "contract_failure:zero_driver_unavailable"


def test_lro_3d_011_known_truth_stress_recovery_is_descriptive_full_denominator() -> None:
    core = _core()
    rows, fits = _recovery_frame(
        core,
        scenario_id="informative_dropout_misspecification_stress",
        split_id="holdout",
        parameter_id="beta_driver",
        widths=tuple([2.0] * 23),
        signed_errors=tuple([0.0] * 23),
        failed_count=1,
    )
    summary = core.summarize_stress_recovery(
        rows,
        fit_rows=fits,
        support_width=6.0,
    )
    assert summary["attempted_replicates"] == 24
    assert summary["acceptance_lower_count"] is None
    assert summary["gate_result"] == "warning"


def test_lro_3d_012_continuous_abundance_has_no_parameter_truth_claim() -> None:
    core = _core()
    row = core.continuous_abundance_recovery_row(estimate=1.0, interval=(0.0, 2.0))
    assert row["estimate"] == 1.0 and row["interval_width"] == 2.0
    for key in ("truth_value", "truth_in_interval", "signed_error", "absolute_error"):
        assert row[key] is None


def test_lro_3d_013_control_summary_denominators_reconcile_to_fit_evidence(
    monkeypatch: pytest.MonkeyPatch,
    complete_science_tables: dict[str, tuple[dict[str, object], ...]],
) -> None:
    core = _core()
    arrival_rows = tuple(
        _successful_fit_row(
            core,
            scenario_id="permuted_arrival_alignment_stress",
            split_id="holdout",
            fit_variant=variant,
            fit_index=index,
            source_replicate_first=index,
            source_replicate_last=index,
            heldout_log_score=-1.0 if variant == "correct_alignment" else -2.0,
        )
        for index in range(24)
        for variant in ("correct_alignment", "permuted_alignment")
    )
    intervals = tuple([(-1.0, 1.0)] * 24)
    zero_fits, zero_recovery = _zero_driver_fit_and_profile_rows(core, intervals)
    with pytest.raises(ValueError, match=r"zero.driver"):
        core.reconcile_control_summary(
            fit_rows=(*arrival_rows, *_equal_fit_rows(core)),
            zero_recovery_rows=zero_recovery,
        )
    summary = core.reconcile_control_summary(
        fit_rows=(*zero_fits, *arrival_rows, *_equal_fit_rows(core)),
        zero_recovery_rows=zero_recovery,
    )
    assert summary == {
        "zero_attempted": 24,
        "zero_evaluable": 24,
        "zero_event_count": 0,
        "zero_decision": "pass",
        "arrival_attempted": 24,
        "arrival_evaluable": 24,
        "arrival_wins": 24,
        "arrival_event_count": 24,
        "bootstrap_converged_count": 199,
        "bootstrap_failed_count": 0,
        "equal_test_statistic": 2.0,
        "equal_p_value": 1.0,
    }
    decision_rows = tuple(
        row
        | (
            {
                "test_statistic": 2.0,
                "p_value": 1.0,
                "event_count": 199,
            }
            if row["decision_row_id"] == "scenario_gate|no_emission_contrast_negative_control"
            else {}
        )
        for row in _control_decision_rows(core)
    )
    core.validate_control_decision_reconciliation(
        decision_rows,
        fit_rows=(*zero_fits, *arrival_rows, *_equal_fit_rows(core)),
        zero_recovery_rows=zero_recovery,
    )
    contradictory_gates = tuple(
        row | {"gate_result": "fail"} if row["decision_row_type"] == "scenario_gate" else row
        for row in decision_rows
    )
    with pytest.raises(ValueError, match=r"scenario|recommendation|final|reconcile"):
        core.validate_control_decision_reconciliation(
            contradictory_gates,
            fit_rows=(*zero_fits, *arrival_rows, *_equal_fit_rows(core)),
            zero_recovery_rows=zero_recovery,
        )
    contradictory_silent = tuple(
        row | {"silent_misspecification_failure": True}
        if row["decision_row_id"] == "scenario_gate|permuted_arrival_alignment_stress"
        else row
        for row in decision_rows
    )
    with pytest.raises(ValueError, match=r"silent|arrival|reconcile"):
        core.validate_control_decision_reconciliation(
            contradictory_silent,
            fit_rows=(*zero_fits, *arrival_rows, *_equal_fit_rows(core)),
            zero_recovery_rows=zero_recovery,
        )
    with pytest.raises(ValueError, match=r"arrival decision|reconcile"):
        core.validate_control_decision_reconciliation(
            tuple(
                row | {"event_count": 23}
                if row["decision_row_id"] == "scenario_gate|permuted_arrival_alignment_stress"
                else row
                for row in decision_rows
            ),
            fit_rows=(*zero_fits, *arrival_rows, *_equal_fit_rows(core)),
            zero_recovery_rows=zero_recovery,
        )
    with pytest.raises(ValueError, match=r"24|frame"):
        core.reconcile_control_summary(
            fit_rows=(*zero_fits, *arrival_rows, *_equal_fit_rows(core)),
            zero_recovery_rows=zero_recovery[:-1],
        )
    with pytest.raises(ValueError, match="24 complete arrival"):
        core.reconcile_control_summary(
            fit_rows=(*zero_fits, *arrival_rows[:-1], *_equal_fit_rows(core)),
            zero_recovery_rows=zero_recovery,
        )
    mixed_arrival_rows = tuple(
        _successful_fit_row(
            core,
            scenario_id="permuted_arrival_alignment_stress",
            split_id="development" if index < 12 else "holdout",
            fit_variant=variant,
            fit_index=index,
            source_replicate_first=index,
            source_replicate_last=index,
            heldout_log_score=-1.0 if variant == "correct_alignment" else -2.0,
        )
        for index in range(24)
        for variant in ("correct_alignment", "permuted_alignment")
    )
    with pytest.raises(ValueError, match="holdout"):
        core.reconcile_control_summary(
            fit_rows=(*zero_fits, *mixed_arrival_rows, *_equal_fit_rows(core)),
            zero_recovery_rows=zero_recovery,
        )
    contradictory = list(zero_recovery)
    contradictory[0] = contradictory[0] | {"interval_upper": 2.0}
    with pytest.raises(ValueError, match=r"reconcile|algebra"):
        core.reconcile_control_summary(
            fit_rows=(*zero_fits, *arrival_rows, *_equal_fit_rows(core)),
            zero_recovery_rows=contradictory,
        )
    null_truth = tuple(
        row
        | {
            "truth_value": None,
            "truth_in_interval": None,
            "signed_error": None,
            "absolute_error": None,
        }
        for row in zero_recovery
    )
    with pytest.raises(ValueError, match=r"truth|zero.driver"):
        core.reconcile_control_summary(
            fit_rows=(*zero_fits, *arrival_rows, *_equal_fit_rows(core)),
            zero_recovery_rows=null_truth,
        )

    core.validate_science_bundle(**complete_science_tables)
    complete_controls = complete_science_tables["control_rows"]
    mutations = (
        (
            "scenario_gate|dense_count_exact_model",
            {"gate_result": "fail", "interpretation": "confounding:dense_joint_failed"},
        ),
        (
            "scenario_gate|permuted_arrival_alignment_stress",
            {"alignment_correlation": float(np.nextafter(0.25, math.inf))},
        ),
        (
            "scenario_gate|permuted_arrival_alignment_stress",
            {"silent_misspecification_failure": True},
        ),
        (
            "parameter_status|no_emission_contrast_negative_control|alpha",
            {"practical_status": "identified"},
        ),
        (
            "final_decision",
            {
                "gate_result": "fail",
                "recommendation_rank": 1,
                "recommendation_class": "model_contract_failed",
            },
        ),
    )
    for decision_id, update in mutations:
        contradictory_rows = tuple(
            row | update if row["decision_row_id"] == decision_id else row
            for row in complete_controls
        )
        with pytest.raises(ValueError, match=r"control|scenario|status|final|reconstruction"):
            core.validate_science_bundle(
                **(complete_science_tables | {"control_rows": contradictory_rows})
            )

    failed_equal_fit = _fit_row(
        core,
        scenario_id="no_emission_contrast_negative_control",
        split_id="holdout",
        fit_scope="bootstrap_shared",
        fit_variant="ordered_emission",
        fit_index=0,
        source_replicate_first=0,
        source_replicate_last=23,
        source_replicate_count=24,
        failure_code="ordered_bootstrap_fit_failed",
    )
    failed_equal_fits = tuple(
        failed_equal_fit
        if row["scenario_id"] == "no_emission_contrast_negative_control"
        and row["split_id"] == "holdout"
        and row["fit_scope"] == "bootstrap_shared"
        and row["fit_variant"] == "ordered_emission"
        and row["fit_index"] == 0
        and row["evidence_row_type"] == "fit_result"
        else row
        | {
            "design_rank": 0,
            "design_condition_number": None,
            "design_passed": False,
            "design_failure_code": "joint_fit_failed_or_nonfinite",
        }
        if row["scenario_id"] == "no_emission_contrast_negative_control"
        and row["split_id"] == "holdout"
        and row["fit_scope"] == "bootstrap_shared"
        and row["fit_variant"] == "ordered_emission"
        and row["fit_index"] == 0
        and row["evidence_row_type"] == "design_diagnostic"
        and row["design_kind"] == "plugin"
        else row
        for row in complete_science_tables["fit_rows"]
    )
    failed_equal_tables = complete_science_tables | {"fit_rows": failed_equal_fits}
    failed_equal_controls = core.recompute_control_decision_rows(
        **{name: value for name, value in failed_equal_tables.items() if name != "control_rows"}
    )
    core.validate_science_bundle(**(failed_equal_tables | {"control_rows": failed_equal_controls}))
    equal_control = next(
        row
        for row in failed_equal_controls
        if row["decision_row_id"] == "scenario_gate|no_emission_contrast_negative_control"
    )
    assert (
        equal_control["bootstrap_converged_count"],
        equal_control["bootstrap_failed_count"],
        equal_control["event_count"],
        equal_control["p_value"],
        equal_control["gate_result"],
    ) == (198, 1, None, None, "fail")

    reached: list[str] = []
    original_reduce_scenario = core.reduce_scenario

    def recording_reduce_scenario(scenario_id: str, evidence: Any) -> str:
        if scenario_id == "zero_driver_effect_negative_control":
            reached.append(scenario_id)
        return cast(str, original_reduce_scenario(scenario_id, evidence))

    monkeypatch.setattr(core, "reduce_scenario", recording_reduce_scenario)
    observed: list[tuple[str, str, float, str]] = []
    for label, target in (
        ("stouffer_boundary", 3.0),
        ("stouffer_open_failure", float(np.nextafter(3.0, math.inf))),
    ):
        candidate = _with_stouffer_target(
            core,
            complete_science_tables,
            scenario_id="zero_driver_effect_negative_control",
            target=target,
        )
        bundle = core.validate_science_bundle(**candidate)
        summary = next(
            row
            for row in candidate["predictive_summary_rows"]
            if row["scenario_id"] == "zero_driver_effect_negative_control"
            and row["split_id"] == "holdout"
        )
        observed.append(
            (
                label,
                dict(bundle.scenario_results)["zero_driver_effect_negative_control"],
                cast(float, summary["stouffer_z"]),
                cast(str, summary["gate_result"]),
            )
        )

    for label, adjusted_p in (
        ("holm_boundary", 0.01),
        ("holm_open_failure", float(np.nextafter(0.01, 0.0))),
    ):
        monkeypatch.setattr(
            core,
            "kstwo",
            SimpleNamespace(sf=lambda _stat, _count, value=adjusted_p: value / 27.0),
        )
        candidate = _with_stouffer_target(
            core,
            complete_science_tables,
            scenario_id="zero_driver_effect_negative_control",
            target=0.0,
        )
        bundle = core.validate_science_bundle(**candidate)
        summary = next(
            row
            for row in candidate["predictive_summary_rows"]
            if row["scenario_id"] == "zero_driver_effect_negative_control"
            and row["split_id"] == "holdout"
        )
        observed.append(
            (
                label,
                dict(bundle.scenario_results)["zero_driver_effect_negative_control"],
                cast(float, summary["holm_adjusted_p"]),
                cast(str, summary["gate_result"]),
            )
        )

    assert reached
    assert observed == [
        ("stouffer_boundary", "pass", 3.0, "pass"),
        (
            "stouffer_open_failure",
            "contract_failure:zero_driver_unavailable",
            float(np.nextafter(3.0, math.inf)),
            "fail",
        ),
        ("holm_boundary", "pass", 0.01, "pass"),
        (
            "holm_open_failure",
            "contract_failure:zero_driver_unavailable",
            float(np.nextafter(0.01, 0.0)),
            "fail",
        ),
    ]


def _predictive_summary_fixture(
    core: Any,
    *,
    residual: float,
) -> tuple[
    tuple[dict[str, object], ...],
    tuple[dict[str, object], ...],
    tuple[dict[str, object], ...],
]:
    pits = tuple((replicate_id + 0.5) / 12.0 for replicate_id in range(12))
    predictive_rows: list[dict[str, object]] = []
    fit_rows: list[dict[str, object]] = []
    reference_sd = 1.0
    reference_mean = 0.0
    observed = residual
    for replicate_id, pit in enumerate(pits):
        fit_rows.append(
            _successful_fit_row(
                core,
                fit_index=replicate_id,
                source_replicate_first=replicate_id,
                source_replicate_last=replicate_id,
            )
        )
        predictive_rows.extend(
            row
            | {
                "fit_succeeded": True,
                "diagnostic_available": True,
                "observed_value": observed,
                "reference_mean": reference_mean,
                "reference_sd": reference_sd,
                "reference_mcse": reference_sd / math.sqrt(199.0),
                "standardized_residual": residual,
                "standardized_residual_nonfinite": False,
                "randomized_pit": pit,
            }
            for row in core.failed_predictive_rows(
                scenario_id="dense_count_exact_model",
                split_id="development",
                replicate_id=replicate_id,
                opportunity_frame=core.deterministic_predictive_opportunity_frame(
                    "dense_count_exact_model", "development", replicate_id
                ),
            )
        )
    ordered = np.asarray(sorted(pits), dtype=np.float64)
    indices = np.arange(1, 13, dtype=np.float64)
    ks_statistic = float(
        max(
            np.max(indices / 12.0 - ordered),
            np.max(ordered - (indices - 1.0) / 12.0),
        )
    )
    raw_p = float(core.kstwo.sf(ks_statistic, 12))
    adjusted_p = min(1.0, 27.0 * raw_p)
    residual_values = np.full(12, residual, dtype=np.float64)
    mean_residual = float(np.mean(residual_values))
    stouffer_z = float(residual_values.sum() / math.sqrt(float(residual_values.size)))
    warning = adjusted_p < 0.01 or abs(stouffer_z) > 3.0
    summary_rows = tuple(
        {
            "scenario_id": "dense_count_exact_model",
            "split_id": "development",
            "fit_variant": "canonical",
            "stratum_type": stratum_type,
            "stratum_value": stratum_value,
            "metric_id": metric_id,
            "replicate_count": 12,
            "diagnostic_count": 12,
            "failed_fit_count": 0,
            "mean_standardized_residual": mean_residual,
            "stouffer_z": stouffer_z,
            "ks_statistic": ks_statistic,
            "raw_p": raw_p,
            "holm_adjusted_p": adjusted_p,
            "warning": warning,
            "gate_result": "fail" if warning else "pass",
        }
        for stratum_type, stratum_value in core.PREDICTIVE_STRATA
        for metric_id in core.PREDICTIVE_METRICS
    )
    return summary_rows, tuple(predictive_rows), tuple(fit_rows)


def _rebuild_predictive_summary_group(
    core: Any,
    *,
    predictive_rows: tuple[dict[str, object], ...],
    fit_rows: tuple[dict[str, object], ...],
    scenario_id: str,
    split_id: str,
    fit_variant: str,
) -> tuple[dict[str, object], ...]:
    attempted = core._split_replicate_count(scenario_id, split_id)
    source = tuple(
        row
        for row in predictive_rows
        if (row["scenario_id"], row["split_id"], row["fit_variant"])
        == (scenario_id, split_id, fit_variant)
    )
    computed: list[dict[str, object]] = []
    raw_values: list[float | None] = []
    for stratum_type, stratum_value in core.PREDICTIVE_STRATA:
        for metric_id in core.PREDICTIVE_METRICS:
            cell = tuple(
                row
                for row in source
                if (row["stratum_type"], row["stratum_value"], row["metric_id"])
                == (stratum_type, stratum_value, metric_id)
            )
            available = tuple(row for row in cell if row["diagnostic_available"] is True)
            residuals = np.asarray(
                [
                    float(cast(float, row["standardized_residual"]))
                    for row in available
                    if row["standardized_residual"] is not None
                ],
                dtype=np.float64,
            )
            pits = np.asarray(
                [float(cast(float, row["randomized_pit"])) for row in available],
                dtype=np.float64,
            )
            mean_residual = float(np.mean(residuals)) if residuals.size else None
            stouffer = (
                float(residuals.sum() / math.sqrt(float(residuals.size)))
                if residuals.size
                else None
            )
            if pits.size:
                ordered = np.sort(pits)
                indices = np.arange(1, pits.size + 1, dtype=np.float64)
                ks_statistic = float(
                    max(
                        np.max(indices / pits.size - ordered),
                        np.max(ordered - (indices - 1.0) / pits.size),
                    )
                )
                raw_p = float(core.kstwo.sf(ks_statistic, pits.size))
            else:
                ks_statistic = None
                raw_p = None
            base_warning = (
                len(available) != attempted
                or any(row["fit_succeeded"] is not True for row in cell)
                or any(row["standardized_residual_nonfinite"] is True for row in cell)
                or mean_residual is None
                or stouffer is None
                or raw_p is None
            )
            computed.append(
                {
                    "scenario_id": scenario_id,
                    "split_id": split_id,
                    "fit_variant": fit_variant,
                    "stratum_type": stratum_type,
                    "stratum_value": stratum_value,
                    "metric_id": metric_id,
                    "replicate_count": attempted,
                    "diagnostic_count": len(available),
                    "failed_fit_count": sum(row["fit_succeeded"] is False for row in cell),
                    "mean_standardized_residual": mean_residual,
                    "stouffer_z": stouffer,
                    "ks_statistic": ks_statistic,
                    "raw_p": raw_p,
                    "base_warning": base_warning,
                }
            )
            raw_values.append(raw_p)
    adjusted: list[float | None] = [None] * 27
    finite_order = sorted(
        (index for index, value in enumerate(raw_values) if value is not None),
        key=lambda index: (cast(float, raw_values[index]), index),
    )
    running = 0.0
    for rank, cell_index in enumerate(finite_order):
        running = max(running, (27 - rank) * cast(float, raw_values[cell_index]))
        adjusted[cell_index] = min(1.0, running)
    result: list[dict[str, object]] = []
    for index, row in enumerate(computed):
        base_warning = cast(bool, row.pop("base_warning"))
        warning = core.predictive_warning_required(
            incomplete_or_nonfinite=base_warning,
            holm_adjusted_p=adjusted[index],
            stouffer_z=cast(float | None, row["stouffer_z"]),
        )
        result.append(
            row
            | {
                "holm_adjusted_p": adjusted[index],
                "warning": warning,
                "gate_result": "fail" if warning else "pass",
            }
        )
    rows = tuple(result)
    core.validate_predictive_summary_rows(
        rows,
        predictive_rows=source,
        fit_rows=fit_rows,
    )
    return rows


def _replace_predictive_holdout_group(
    core: Any,
    tables: dict[str, tuple[dict[str, object], ...]],
    *,
    scenario_id: str,
    transform: Any,
) -> dict[str, tuple[dict[str, object], ...]]:
    registry = core.SCENARIO_EVIDENCE_REGISTRY[core.SCENARIO_IDS.index(scenario_id)]
    identity = (scenario_id, "holdout", registry.primary_fit_variant)
    predictive_rows = tuple(
        transform(row)
        if (row["scenario_id"], row["split_id"], row["fit_variant"]) == identity
        else row
        for row in tables["predictive_rows"]
    )
    summary_rows = tuple(
        row
        for summary_scenario, summary_split, summary_variant in core.science_identity_frames()[
            "predictive_summary"
        ]
        for row in _rebuild_predictive_summary_group(
            core,
            predictive_rows=predictive_rows,
            fit_rows=tables["fit_rows"],
            scenario_id=summary_scenario,
            split_id=summary_split,
            fit_variant=summary_variant,
        )
    )
    without_controls = tables | {
        "predictive_rows": predictive_rows,
        "predictive_summary_rows": summary_rows,
    }
    controls = core.recompute_control_decision_rows(
        **{name: value for name, value in without_controls.items() if name != "control_rows"}
    )
    return without_controls | {"control_rows": controls}


def _with_stouffer_target(
    core: Any,
    tables: dict[str, tuple[dict[str, object], ...]],
    *,
    scenario_id: str,
    target: float,
) -> dict[str, tuple[dict[str, object], ...]]:
    attempted = core._split_replicate_count(scenario_id, "holdout")
    first_residual = target * math.sqrt(float(attempted))

    def transform(row: dict[str, object]) -> dict[str, object]:
        residual = first_residual if row["replicate_id"] == 0 else 0.0
        reference_sd = 1.0 / max(1.0, abs(residual))
        return row | {
            "fit_succeeded": True,
            "diagnostic_available": True,
            "observed_value": residual * reference_sd,
            "reference_mean": 0.0,
            "reference_sd": reference_sd,
            "reference_mcse": reference_sd / math.sqrt(199.0),
            "standardized_residual": residual,
            "standardized_residual_nonfinite": False,
        }

    return _replace_predictive_holdout_group(
        core,
        tables,
        scenario_id=scenario_id,
        transform=transform,
    )


def _with_forced_predictive_warning(
    core: Any,
    tables: dict[str, tuple[dict[str, object], ...]],
    *,
    scenario_id: str,
    finite_rule_also_fires: bool,
) -> dict[str, tuple[dict[str, object], ...]]:
    first_cell = (*core.PREDICTIVE_STRATA[0], core.PREDICTIVE_METRICS[0])
    second_cell = (*core.PREDICTIVE_STRATA[0], core.PREDICTIVE_METRICS[1])

    def transform(row: dict[str, object]) -> dict[str, object]:
        cell = (row["stratum_type"], row["stratum_value"], row["metric_id"])
        finite = row | {
            "observed_value": 0.0,
            "reference_mean": 0.0,
            "reference_sd": 1.0,
            "reference_mcse": 1.0 / math.sqrt(199.0),
            "standardized_residual": 0.0,
            "standardized_residual_nonfinite": False,
        }
        if row["replicate_id"] == 0 and cell == first_cell:
            return finite | {
                "observed_value": 1.0,
                "reference_sd": 0.0,
                "reference_mcse": 0.0,
                "standardized_residual": None,
                "standardized_residual_nonfinite": True,
            }
        if finite_rule_also_fires and cell == second_cell:
            return finite | {
                "observed_value": 1.0,
                "standardized_residual": 1.0,
            }
        return finite

    return _replace_predictive_holdout_group(
        core,
        tables,
        scenario_id=scenario_id,
        transform=transform,
    )


def _with_design_update(
    core: Any,
    tables: dict[str, tuple[dict[str, object], ...]],
    *,
    scenario_id: str,
    design_kind: str,
    update: dict[str, object],
    recompute_controls: bool = True,
) -> dict[str, tuple[dict[str, object], ...]]:
    changed = False
    fit_rows: list[dict[str, object]] = []
    for row in tables["fit_rows"]:
        if (
            not changed
            and row["scenario_id"] == scenario_id
            and row["split_id"] == "holdout"
            and row["evidence_row_type"] == "design_diagnostic"
            and row["design_kind"] == design_kind
        ):
            fit_rows.append(row | update)
            changed = True
        else:
            fit_rows.append(row)
    assert changed
    without_controls = tables | {"fit_rows": tuple(fit_rows)}
    if not recompute_controls:
        return without_controls
    controls = core.recompute_control_decision_rows(
        **{name: value for name, value in without_controls.items() if name != "control_rows"}
    )
    return without_controls | {"control_rows": controls}


@pytest.fixture(scope="module")
def complete_science_tables() -> dict[str, tuple[dict[str, object], ...]]:
    core = _core()
    frames = core.science_identity_frames()
    fit_result_rows: list[dict[str, object]] = []
    truth = {
        (scenario_id, parameter_id): truth_value
        for scenario_id, parameter_id, truth_value in core.SCENARIO_PARAMETER_TRUTH_ROWS
    }
    for scenario_id, split_id, fit_scope, fit_variant, fit_index in frames["fit"]:
        if fit_scope == "replicate":
            fit = _successful_fit_row(
                core,
                scenario_id=scenario_id,
                split_id=split_id,
                fit_scope=fit_scope,
                fit_variant=fit_variant,
                fit_index=fit_index,
                source_replicate_first=fit_index,
                source_replicate_last=fit_index,
                source_replicate_count=1,
                **(
                    {"heldout_log_score": (-1.0 if fit_variant == "correct_alignment" else -2.0)}
                    if scenario_id == "permuted_arrival_alignment_stress"
                    else {}
                ),
            )
            for parameter_id in core.FIT_PARAMETER_IDS.get(scenario_id, core.ORDERED_PARAMETER_IDS):
                truth_value = truth.get((scenario_id, parameter_id))
                if truth_value is not None:
                    fit[f"{parameter_id}_estimate"] = truth_value
            fit_result_rows.append(fit)
            continue
        last = 11 if split_id == "development" else 23
        fit_result_rows.append(
            _successful_fit_row(
                core,
                scenario_id=scenario_id,
                split_id=split_id,
                fit_scope=fit_scope,
                fit_variant=fit_variant,
                fit_index=fit_index,
                source_replicate_first=0,
                source_replicate_last=23 if fit_scope == "bootstrap_shared" else last,
                source_replicate_count=24 if fit_scope == "bootstrap_shared" else last + 1,
                log_likelihood=-100.0 + (fit_variant == "ordered_emission"),
            )
        )
    fit_result_rows.sort(
        key=lambda row: tuple(
            row[name]
            for name in ("scenario_id", "split_id", "fit_scope", "fit_variant", "fit_index")
        )
    )
    fit_results = tuple(fit_result_rows)
    design_rows = _complete_design_rows(core, fit_results)
    fit_rows = tuple(
        sorted((*fit_results, *design_rows), key=lambda row: _fit_evidence_sort_key(core, row))
    )
    fit_lookup = {
        (
            row["scenario_id"],
            row["split_id"],
            row["fit_scope"],
            row["fit_variant"],
            row["fit_index"],
        ): row
        for row in fit_results
    }
    supports = {
        "alpha": core.ALPHA_SUPPORT,
        "beta_driver": core.BETA_DRIVER_SUPPORT,
        "beta_quality": core.BETA_QUALITY_SUPPORT,
        "lambda_quasi": core.LAMBDA_QUASI_SUPPORT,
        "lambda_present": core.LAMBDA_PRESENT_SUPPORT,
    }
    recovery_rows: list[dict[str, object]] = []
    profile_rows: list[dict[str, object]] = []
    descriptive = {
        "permuted_arrival_alignment_stress",
        "informative_dropout_misspecification_stress",
        "goal018_continuous_abundance_stress",
        "spatial_frailty_stress",
    }
    root_likelihood = -100.0 - core.PROFILE_LR_CUTOFF / 2.0
    root_delta = 2.0 * (-100.0 - root_likelihood)
    for scenario_id, split_id, replicate_id, fit_variant, parameter_id in frames["recovery"]:
        fit = fit_lookup[(scenario_id, split_id, "replicate", fit_variant, replicate_id)]
        truth_value = truth[(scenario_id, parameter_id)]
        if fit["fit_succeeded"] is not True:
            recovery_rows.append(
                {
                    "scenario_id": scenario_id,
                    "split_id": split_id,
                    "replicate_id": replicate_id,
                    "fit_variant": fit_variant,
                    "parameter_id": parameter_id,
                    "truth_value": truth_value,
                    "estimate": None,
                    "interval_lower": None,
                    "interval_upper": None,
                    "interval_width": None,
                    "converged": False,
                    "converged_start_count": fit["converged_start_count"],
                    "at_boundary": None,
                    "profile_two_sided": False,
                    "truth_in_interval": None,
                    "log_likelihood": None,
                    "signed_error": None,
                    "absolute_error": None,
                    "gate_result": "warning" if scenario_id in descriptive else "fail",
                }
            )
            continue
        estimate = float(cast(float, fit[f"{parameter_id}_estimate"]))
        lower_support, upper_support = supports[cast(str, parameter_id)]
        half_width = (
            cast(
                float,
                core.FROZEN_GATE_CONFIG["profile_width_limits"][parameter_id],
            )
            / 4.0
        )
        if scenario_id == "sparse_expected_failure" and parameter_id == "beta_driver":
            half_width = 0.5
        if scenario_id == "zero_driver_effect_negative_control" and parameter_id == "beta_driver":
            half_width = 0.5
        lower = estimate - half_width
        upper = estimate + half_width
        signed_error = None if truth_value is None else estimate - float(cast(float, truth_value))
        recovery_rows.append(
            {
                "scenario_id": scenario_id,
                "split_id": split_id,
                "replicate_id": replicate_id,
                "fit_variant": fit_variant,
                "parameter_id": parameter_id,
                "truth_value": truth_value,
                "estimate": estimate,
                "interval_lower": lower,
                "interval_upper": upper,
                "interval_width": upper - lower,
                "converged": True,
                "converged_start_count": fit["converged_start_count"],
                "at_boundary": fit["at_boundary"],
                "profile_two_sided": True,
                "truth_in_interval": (
                    None
                    if truth_value is None
                    else lower <= float(cast(float, truth_value)) <= upper
                ),
                "log_likelihood": fit["log_likelihood"],
                "signed_error": signed_error,
                "absolute_error": None if signed_error is None else abs(signed_error),
                "gate_result": "diagnostic" if scenario_id in descriptive else "pass",
            }
        )
        for grid_index, parameter_value, likelihood, delta in (
            (0, lower_support, -102.0, 4.0),
            (1, lower, root_likelihood, root_delta),
            (2, estimate, -100.0, 0.0),
            (3, upper, root_likelihood, root_delta),
            (4, upper_support, -102.0, 4.0),
        ):
            profile_rows.append(
                {
                    "scenario_id": scenario_id,
                    "split_id": split_id,
                    "replicate_id": replicate_id,
                    "fit_variant": fit_variant,
                    "parameter_id": parameter_id,
                    "grid_index": grid_index,
                    "parameter_value": parameter_value,
                    "profile_log_likelihood": likelihood,
                    "likelihood_ratio_delta": delta,
                    "nuisance_converged": True,
                    "inside_interval": delta <= core.PROFILE_LR_CUTOFF,
                }
            )
    recovery_rows.sort(
        key=lambda row: tuple(
            row[name]
            for name in ("scenario_id", "split_id", "replicate_id", "fit_variant", "parameter_id")
        )
    )
    profile_rows.sort(
        key=lambda row: tuple(
            row[name]
            for name in (
                "scenario_id",
                "split_id",
                "replicate_id",
                "fit_variant",
                "parameter_id",
                "grid_index",
            )
        )
    )

    coverage_rows: list[dict[str, object]] = []
    for scenario_id, split_id, fit_variant, parameter_id in frames["coverage"]:
        source = tuple(
            row
            for row in recovery_rows
            if (row["scenario_id"], row["split_id"], row["fit_variant"], row["parameter_id"])
            == (scenario_id, split_id, fit_variant, parameter_id)
        )
        source_fits = tuple(
            row
            for row in fit_results
            if row["scenario_id"] == scenario_id
            and row["split_id"] == split_id
            and row["fit_variant"] == fit_variant
        )
        attempted = core._split_replicate_count(scenario_id, split_id)
        support = supports[cast(str, parameter_id)]
        summary = core.summarize_attempted_recovery(
            source,
            fit_rows=source_fits,
            attempted=attempted,
            support_width=support[1] - support[0],
        )
        truth_free = scenario_id == "goal018_continuous_abundance_stress"
        bounds = (
            (36, 48)
            if scenario_id in core.NESTED_SCENARIOS and split_id == "holdout"
            else (18, 24)
            if scenario_id == "sparse_expected_failure" and split_id == "holdout"
            else (None, None)
        )
        if scenario_id in core.NESTED_SCENARIOS and split_id == "holdout":
            limit = core.FROZEN_GATE_CONFIG["convergence_limits"][scenario_id]
            width_limit = core.FROZEN_GATE_CONFIG["profile_width_limits"][parameter_id]
            error_limit = core.FROZEN_GATE_CONFIG["absolute_error_limits"][parameter_id]
            passed = (
                core.nested_gate(
                    coverage_count=summary["coverage_count"],
                    converged_count=summary["converged_count"],
                    minimum_converged=math.ceil(attempted * limit),
                )
                and summary["median_interval_width"] <= width_limit
                and summary["median_absolute_error"] <= error_limit
            )
            gate_result = "pass" if passed else "fail"
        elif scenario_id == "sparse_expected_failure" and split_id == "holdout":
            gate_result = "pass" if 18 <= cast(int, summary["coverage_count"]) <= 24 else "fail"
        else:
            complete = all(
                row["converged"] is True and row["profile_two_sided"] is True for row in source
            )
            gate_result = "diagnostic" if complete else "warning"
        coverage_rows.append(
            {
                "scenario_id": scenario_id,
                "split_id": split_id,
                "fit_variant": fit_variant,
                "parameter_id": parameter_id,
                "replicate_count": attempted,
                "converged_count": summary["converged_count"],
                "coverage_count": None if truth_free else summary["coverage_count"],
                "coverage_fraction": (
                    None if truth_free else cast(int, summary["coverage_count"]) / attempted
                ),
                "acceptance_lower_count": bounds[0],
                "acceptance_upper_count": bounds[1],
                "median_signed_error": summary["median_signed_error"],
                "median_absolute_error": (None if truth_free else summary["median_absolute_error"]),
                "median_interval_width": summary["median_interval_width"],
                "maximum_absolute_error": (
                    None if truth_free else summary["maximum_absolute_error"]
                ),
                "maximum_interval_width": summary["maximum_interval_width"],
                "gate_result": gate_result,
            }
        )
    coverage_rows.sort(
        key=lambda row: tuple(
            row[name] for name in ("scenario_id", "split_id", "fit_variant", "parameter_id")
        )
    )

    latent_rows: list[dict[str, object]] = []
    latent_applicable = {
        scenario_id: applicable for scenario_id, applicable, _ in core.LATENT_APPLICABILITY
    }
    for scenario_id, split_id, replicate_id, fit_variant in frames["latent"]:
        fit = fit_lookup[(scenario_id, split_id, "replicate", fit_variant, replicate_id)]
        latent_rows.extend(
            core.build_latent_diagnostic_rows(
                scenario_id=scenario_id,
                split_id=split_id,
                replicate_id=replicate_id,
                fit_succeeded=(fit["fit_succeeded"] if latent_applicable[scenario_id] else None),
            )
        )

    predictive_rows: list[dict[str, object]] = []
    for scenario_id, split_id, replicate_id, fit_variant in frames["predictive"]:
        scope = (
            "scenario_shared"
            if scenario_id == "no_emission_contrast_negative_control"
            else "replicate"
        )
        fit_index = 0 if scope == "scenario_shared" else replicate_id
        fit = fit_lookup[(scenario_id, split_id, scope, fit_variant, fit_index)]
        base_rows = core.failed_predictive_rows(
            scenario_id=scenario_id,
            split_id=split_id,
            replicate_id=replicate_id,
            opportunity_frame=core.deterministic_predictive_opportunity_frame(
                scenario_id, split_id, replicate_id
            ),
        )
        if fit["fit_succeeded"] is True:
            pit = (replicate_id + 0.5) / core._split_replicate_count(scenario_id, split_id)
            residual = (
                1.0
                if split_id == "holdout"
                and scenario_id
                in {
                    "permuted_arrival_alignment_stress",
                    "goal018_continuous_abundance_stress",
                }
                else 0.0
            )
            predictive_rows.extend(
                row
                | {
                    "fit_succeeded": True,
                    "diagnostic_available": True,
                    "observed_value": residual,
                    "reference_mean": 0.0,
                    "reference_sd": 1.0,
                    "reference_mcse": 1.0 / math.sqrt(199.0),
                    "standardized_residual": residual,
                    "standardized_residual_nonfinite": False,
                    "randomized_pit": pit,
                }
                for row in base_rows
            )
        else:
            predictive_rows.extend(base_rows)

    predictive_summary_rows: list[dict[str, object]] = []
    for scenario_id, split_id, fit_variant in frames["predictive_summary"]:
        attempted = core._split_replicate_count(scenario_id, split_id)
        source = tuple(
            row
            for row in predictive_rows
            if (row["scenario_id"], row["split_id"], row["fit_variant"])
            == (scenario_id, split_id, fit_variant)
        )
        computed: list[dict[str, object]] = []
        raw_values: list[float | None] = []
        for stratum_type, stratum_value in core.PREDICTIVE_STRATA:
            for metric_id in core.PREDICTIVE_METRICS:
                cell = tuple(
                    row
                    for row in source
                    if (row["stratum_type"], row["stratum_value"], row["metric_id"])
                    == (stratum_type, stratum_value, metric_id)
                )
                available = tuple(row for row in cell if row["diagnostic_available"] is True)
                residuals = np.asarray(
                    [row["standardized_residual"] for row in available], dtype=np.float64
                )
                pits = np.asarray([row["randomized_pit"] for row in available], dtype=np.float64)
                mean_residual = float(np.mean(residuals)) if residuals.size else None
                stouffer = (
                    float(residuals.sum() / math.sqrt(float(residuals.size)))
                    if residuals.size
                    else None
                )
                if pits.size:
                    ordered = np.sort(pits)
                    indices = np.arange(1, pits.size + 1, dtype=np.float64)
                    ks_statistic = float(
                        max(
                            np.max(indices / pits.size - ordered),
                            np.max(ordered - (indices - 1.0) / pits.size),
                        )
                    )
                    raw_p = float(core.kstwo.sf(ks_statistic, pits.size))
                else:
                    ks_statistic = None
                    raw_p = None
                computed.append(
                    {
                        "scenario_id": scenario_id,
                        "split_id": split_id,
                        "fit_variant": fit_variant,
                        "stratum_type": stratum_type,
                        "stratum_value": stratum_value,
                        "metric_id": metric_id,
                        "replicate_count": attempted,
                        "diagnostic_count": len(available),
                        "failed_fit_count": sum(row["fit_succeeded"] is False for row in cell),
                        "mean_standardized_residual": mean_residual,
                        "stouffer_z": stouffer,
                        "ks_statistic": ks_statistic,
                        "raw_p": raw_p,
                    }
                )
                raw_values.append(raw_p)
        adjusted: list[float | None] = [None] * 27
        finite_order = sorted(
            (index for index, value in enumerate(raw_values) if value is not None),
            key=lambda index: (cast(float, raw_values[index]), index),
        )
        running = 0.0
        for rank, cell_index in enumerate(finite_order):
            running = max(running, (27 - rank) * cast(float, raw_values[cell_index]))
            adjusted[cell_index] = min(1.0, running)
        for index, row in enumerate(computed):
            base_warning = (
                row["diagnostic_count"] != attempted
                or row["failed_fit_count"] != 0
                or row["mean_standardized_residual"] is None
                or row["stouffer_z"] is None
                or row["raw_p"] is None
            )
            warning = core.predictive_warning_required(
                incomplete_or_nonfinite=base_warning,
                holm_adjusted_p=adjusted[index],
                stouffer_z=cast(float | None, row["stouffer_z"]),
            )
            row["holm_adjusted_p"] = adjusted[index]
            row["warning"] = warning
            row["gate_result"] = "fail" if warning else "pass"
            predictive_summary_rows.append(row)

    tables = {
        "fit_rows": tuple(fit_rows),
        "recovery_rows": tuple(recovery_rows),
        "profile_rows": tuple(profile_rows),
        "coverage_rows": tuple(coverage_rows),
        "latent_rows": tuple(latent_rows),
        "predictive_rows": tuple(predictive_rows),
        "predictive_summary_rows": tuple(predictive_summary_rows),
    }
    controls = core.recompute_control_decision_rows(**tables)
    return tables | {"control_rows": controls}


def test_lro_3d_014_failed_predictive_fit_emits_27_unavailable_rows(
    monkeypatch: pytest.MonkeyPatch,
    complete_science_tables: dict[str, tuple[dict[str, object], ...]],
) -> None:
    core = _core()
    baseline_records = core._predictive_opportunity_records("dense_count_exact_model")
    baseline_frame = core.deterministic_predictive_opportunity_frame(
        "dense_count_exact_model", "holdout", 0
    )
    swapped_quality = tuple(
        replace(
            opportunity,
            quality_stratum=(
                "q2"
                if opportunity.quality_stratum == "q1"
                else "q1"
                if opportunity.quality_stratum == "q2"
                else opportunity.quality_stratum
            ),
        )
        for opportunity in baseline_frame.opportunities
    )
    swapped_time = tuple(
        replace(
            opportunity,
            time_band=(
                "late"
                if opportunity.time_band == "early"
                else "early"
                if opportunity.time_band == "late"
                else opportunity.time_band
            ),
        )
        for opportunity in baseline_frame.opportunities
    )

    def candidate_digest(opportunities: tuple[Any, ...]) -> str:
        return cast(
            str,
            core.canonical_predictive_opportunity_sha256(
                scenario_id="dense_count_exact_model",
                split_id="holdout",
                replicate_id=0,
                frame_role="fit",
                opportunities=opportunities,
            ),
        )

    quality_swap_digest = candidate_digest(swapped_quality)
    time_swap_digest = candidate_digest(swapped_time)
    schedule = core.build_canonical_schedule(
        core.authoritative_source_design_cells(), "dense_count_exact_model"
    )
    production_frame = core.predictive_opportunity_frame_from_schedule(
        scenario_id="dense_count_exact_model",
        split_id="holdout",
        replicate_id=0,
        schedule=schedule,
    )
    metric_rows = core.predictive_metrics_from_opportunity_frame(
        production_frame,
        {opportunity.keep_key: 0 for opportunity in production_frame.opportunities},
    )
    incomplete_metric_counts = {
        opportunity.keep_key: 0 for opportunity in production_frame.opportunities[1:]
    }
    with pytest.raises(ValueError, match=r"counts|retained|key"):
        core.predictive_metrics_from_opportunity_frame(
            production_frame,
            incomplete_metric_counts,
        )
    mutated_effort_schedule = (
        replace(schedule[0], effort=float(np.nextafter(schedule[0].effort, math.inf))),
        *schedule[1:],
    )
    with pytest.raises(ValueError, match=r"schedule|effort"):
        core.predictive_opportunity_frame_from_schedule(
            scenario_id="dense_count_exact_model",
            split_id="holdout",
            replicate_id=0,
            schedule=mutated_effort_schedule,
        )
    assert (
        len(baseline_records[0]) == 5,
        quality_swap_digest != baseline_frame.opportunity_frame_sha256,
        time_swap_digest != baseline_frame.opportunity_frame_sha256,
        hasattr(core, "predictive_opportunity_frame_from_schedule"),
        production_frame == baseline_frame,
        len(metric_rows) == 27,
        all(
            len({row["sample_size"] for row in metric_rows[index : index + 3]}) == 1
            for index in range(0, 27, 3)
        ),
    ) == (True, True, True, True, True, True, True)
    rows = core.failed_predictive_rows(
        scenario_id="dense_count_exact_model",
        split_id="holdout",
        replicate_id=0,
        opportunity_frame=core.deterministic_predictive_opportunity_frame(
            "dense_count_exact_model", "holdout", 0
        ),
    )
    assert len(rows) == 27
    assert tuple(rows[0]) == core.PREDICTIVE_REPLICATE_DIAGNOSTICS_HEADER
    assert tuple(dict.fromkeys((row["stratum_type"], row["stratum_value"]) for row in rows)) == (
        ("all", "all"),
        ("habitat_quality_quintile", "q1"),
        ("habitat_quality_quintile", "q2"),
        ("habitat_quality_quintile", "q3"),
        ("habitat_quality_quintile", "q4"),
        ("habitat_quality_quintile", "q5"),
        ("time_band", "early"),
        ("time_band", "middle"),
        ("time_band", "late"),
    )
    assert all(
        row["fit_succeeded"] is False
        and row["diagnostic_available"] is False
        and row["observed_value"] is None
        and row["reference_mean"] is None
        and row["reference_sd"] is None
        and row["reference_mcse"] is None
        and row["standardized_residual"] is None
        and row["standardized_residual_nonfinite"] is False
        and row["randomized_pit"] is None
        for row in rows
    )
    core.validate_predictive_replicate_rows(rows)
    for semantic_digest in (quality_swap_digest, time_swap_digest):
        semantic_mutation = tuple(
            row | {"opportunity_frame_sha256": semantic_digest} for row in rows
        )
        with pytest.raises(ValueError, match=r"opportunity|frame|binding"):
            core.validate_predictive_replicate_rows(
                semantic_mutation,
                opportunity_frame=baseline_frame,
            )
    expected_frame = core.deterministic_predictive_opportunity_frame(
        "dense_count_exact_model", "holdout", 0
    )
    assert rows[0]["opportunity_frame_count"] == expected_frame.opportunity_count
    assert rows[0]["opportunity_frame_sha256"] == expected_frame.opportunity_frame_sha256
    assert rows[0]["dropout_mask_sha256"] is None
    impossible = tuple(row | {"sample_size": 999999} for row in rows)
    with pytest.raises(ValueError, match=r"sample_size|opportunity|frame"):
        core.validate_predictive_replicate_rows(impossible)
    metric_disagreement = list(rows)
    metric_disagreement[1] = metric_disagreement[1] | {"sample_size": 3}
    with pytest.raises(ValueError, match=r"sample_size|metric|stratum"):
        core.validate_predictive_replicate_rows(metric_disagreement)
    for field, value in (
        ("opportunity_frame_count", expected_frame.opportunity_count - 1),
        ("opportunity_frame_sha256", "0" * 64),
    ):
        mutation = list(rows)
        mutation[0] = mutation[0] | {field: value}
        with pytest.raises(ValueError, match=r"opportunity|frame|binding"):
            core.validate_predictive_replicate_rows(mutation)

    arrival_frame = core.deterministic_predictive_opportunity_frame(
        "permuted_arrival_alignment_stress", "holdout", 0
    )
    arrival_rows = core.failed_predictive_rows(
        scenario_id="permuted_arrival_alignment_stress",
        split_id="holdout",
        replicate_id=0,
        opportunity_frame=arrival_frame,
    )
    assert (arrival_frame.frame_role, arrival_frame.opportunity_count) == ("score", 1045 * 11)
    fit_frame_mutation = list(arrival_rows)
    fit_frame_mutation[0] = fit_frame_mutation[0] | {"opportunity_frame_sha256": "f" * 64}
    with pytest.raises(ValueError, match=r"opportunity|frame|binding"):
        core.validate_predictive_replicate_rows(fit_frame_mutation)

    dropout_frame = core.deterministic_predictive_opportunity_frame(
        "informative_dropout_misspecification_stress", "holdout", 0
    )
    dropout_rows = core.failed_predictive_rows(
        scenario_id="informative_dropout_misspecification_stress",
        split_id="holdout",
        replicate_id=0,
        opportunity_frame=dropout_frame,
    )
    assert dropout_frame.dropout_mask_sha256 is not None
    dropout_keep = {
        opportunity.keep_key: opportunity.kept for opportunity in dropout_frame.opportunities
    }
    kept_key = next(key for key, kept in dropout_keep.items() if kept)
    dropped_key = next(key for key, kept in dropout_keep.items() if not kept)
    swapped_keep = dropout_keep | {kept_key: False, dropped_key: True}
    dropout_schedule = core.build_canonical_schedule(
        core.authoritative_source_design_cells(),
        "informative_dropout_misspecification_stress",
    )
    keyed_mask_mutation = core.predictive_opportunity_frame_from_schedule(
        scenario_id="informative_dropout_misspecification_stress",
        split_id="holdout",
        replicate_id=0,
        schedule=dropout_schedule,
        keep_by_key=swapped_keep,
    )
    assert (
        keyed_mask_mutation.opportunity_count,
        keyed_mask_mutation.opportunity_frame_sha256 != dropout_frame.opportunity_frame_sha256,
        keyed_mask_mutation.dropout_mask_sha256 != dropout_frame.dropout_mask_sha256,
    ) == (dropout_frame.opportunity_count, True, True)
    with pytest.raises(ValueError, match=r"opportunity|frame|dropout|mask|binding"):
        core.validate_predictive_replicate_rows(
            dropout_rows,
            opportunity_frame=keyed_mask_mutation,
        )
    mask_mutation = list(dropout_rows)
    mask_mutation[0] = mask_mutation[0] | {"dropout_mask_sha256": "0" * 64}
    with pytest.raises(ValueError, match=r"dropout|mask|binding"):
        core.validate_predictive_replicate_rows(mask_mutation)
    available = [
        row
        | {
            "fit_succeeded": True,
            "diagnostic_available": True,
            "observed_value": 0.5,
            "reference_mean": 0.5,
            "reference_sd": 1.0,
            "reference_mcse": 1.0 / math.sqrt(199),
            "standardized_residual": 0.0,
            "standardized_residual_nonfinite": False,
            "randomized_pit": 0.5,
        }
        for row in rows
    ]
    available[0] = available[0] | {
        "observed_value": 1.0,
        "reference_mean": 0.0,
        "reference_sd": 0.0,
        "reference_mcse": 0.0,
        "standardized_residual": None,
        "standardized_residual_nonfinite": True,
    }
    core.validate_predictive_replicate_rows(available)
    core.validate_predictive_warning_binding(available, warning=True)
    with pytest.raises(ValueError, match="mandatory"):
        core.validate_predictive_warning_binding(available, warning=False)
    for update, message in (
        ({"observed_value": -0.1}, "domain"),
        ({"reference_mcse": 0.25}, "MCSE"),
        ({"standardized_residual": 0.25}, "residual"),
    ):
        invalid = list(available)
        invalid[1] = invalid[1] | update
        with pytest.raises(ValueError, match=message):
            core.validate_predictive_replicate_rows(invalid)

    complete_failed = tuple(
        row
        for replicate_id in range(12)
        for row in core.failed_predictive_rows(
            scenario_id="dense_count_exact_model",
            split_id="development",
            replicate_id=replicate_id,
            opportunity_frame=core.deterministic_predictive_opportunity_frame(
                "dense_count_exact_model", "development", replicate_id
            ),
        )
    )
    failed_fits = tuple(
        _fit_row(
            core,
            fit_index=replicate_id,
            source_replicate_first=replicate_id,
            source_replicate_last=replicate_id,
        )
        for replicate_id in range(12)
    )
    summary_rows = tuple(
        {
            "scenario_id": "dense_count_exact_model",
            "split_id": "development",
            "fit_variant": "canonical",
            "stratum_type": stratum_type,
            "stratum_value": stratum_value,
            "metric_id": metric_id,
            "replicate_count": 12,
            "diagnostic_count": 0,
            "failed_fit_count": 12,
            "mean_standardized_residual": None,
            "stouffer_z": None,
            "ks_statistic": None,
            "raw_p": None,
            "holm_adjusted_p": None,
            "warning": True,
            "gate_result": "fail",
        }
        for stratum_type, stratum_value in core.PREDICTIVE_STRATA
        for metric_id in core.PREDICTIVE_METRICS
    )
    core.validate_predictive_summary_rows(
        summary_rows,
        predictive_rows=complete_failed,
        fit_rows=failed_fits,
    )
    with pytest.raises(ValueError, match=r"warning|gate|reproduce"):
        core.validate_predictive_summary_rows(
            (summary_rows[0] | {"warning": False}, *summary_rows[1:]),
            predictive_rows=complete_failed,
            fit_rows=failed_fits,
        )

    high_rows, high_source, high_fits = _predictive_summary_fixture(core, residual=1.0)
    high_contradiction = tuple(row | {"warning": False, "gate_result": "pass"} for row in high_rows)
    with pytest.raises(ValueError, match=r"Stouffer|warning|gate|reproduce"):
        core.validate_predictive_summary_rows(
            high_contradiction,
            predictive_rows=high_source,
            fit_rows=high_fits,
        )

    boundary_rows, boundary_source, boundary_fits = _predictive_summary_fixture(
        core, residual=(3.0 - 1e-12) / math.sqrt(12.0)
    )
    assert all(row["warning"] is False and row["gate_result"] == "pass" for row in boundary_rows)
    core.validate_predictive_summary_rows(
        boundary_rows,
        predictive_rows=boundary_source,
        fit_rows=boundary_fits,
    )

    for holm_value, expected_warning in ((0.01, False), (0.009, True)):
        monkeypatch.setattr(
            core,
            "kstwo",
            SimpleNamespace(sf=lambda _statistic, _count, value=holm_value: value / 27.0),
        )
        holm_rows, holm_source, holm_fits = _predictive_summary_fixture(core, residual=0.0)
        assert all(row["holm_adjusted_p"] == holm_value for row in holm_rows)
        if expected_warning:
            contradiction = tuple(row | {"warning": False} for row in holm_rows)
            with pytest.raises(ValueError, match=r"Holm|warning|gate|reproduce"):
                core.validate_predictive_summary_rows(
                    contradiction,
                    predictive_rows=holm_source,
                    fit_rows=holm_fits,
                )
        else:
            core.validate_predictive_summary_rows(
                holm_rows,
                predictive_rows=holm_source,
                fit_rows=holm_fits,
            )
    assert not core.predictive_warning_required(
        incomplete_or_nonfinite=False,
        holm_adjusted_p=0.01,
        stouffer_z=3.0,
    )
    assert core.predictive_warning_required(
        incomplete_or_nonfinite=False,
        holm_adjusted_p=float(np.nextafter(0.01, 0.0)),
        stouffer_z=3.0,
    )
    assert core.predictive_warning_required(
        incomplete_or_nonfinite=False,
        holm_adjusted_p=0.01,
        stouffer_z=float(np.nextafter(3.0, math.inf)),
    )

    original_reduce_scenario = core.reduce_scenario
    reached: list[str] = []
    stress_reasons = {
        "permuted_arrival_alignment_stress": (
            "contract_failure:alignment_contract_or_availability_failed"
        ),
        "informative_dropout_misspecification_stress": (
            "contract_failure:informative_dropout_unavailable"
        ),
        "goal018_continuous_abundance_stress": (
            "contract_failure:continuous_abundance_unavailable"
        ),
        "spatial_frailty_stress": "contract_failure:spatial_frailty_unavailable",
    }

    def recording_reduce_scenario(scenario_id: str, evidence: Any) -> str:
        if scenario_id in stress_reasons:
            reached.append(scenario_id)
        return cast(str, original_reduce_scenario(scenario_id, evidence))

    monkeypatch.setattr(core, "reduce_scenario", recording_reduce_scenario)
    first_cell = (*core.PREDICTIVE_STRATA[0], core.PREDICTIVE_METRICS[0])
    second_cell = (*core.PREDICTIVE_STRATA[0], core.PREDICTIVE_METRICS[1])

    def forced_only(row: dict[str, object]) -> dict[str, object]:
        cell = (row["stratum_type"], row["stratum_value"], row["metric_id"])
        finite = row | {
            "observed_value": 0.0,
            "reference_mean": 0.0,
            "reference_sd": 1.0,
            "reference_mcse": 1.0 / math.sqrt(199.0),
            "standardized_residual": 0.0,
            "standardized_residual_nonfinite": False,
        }
        if row["replicate_id"] == 0 and cell == first_cell:
            return finite | {
                "observed_value": 1.0,
                "reference_mean": 0.0,
                "reference_sd": 0.0,
                "reference_mcse": 0.0,
                "standardized_residual": None,
                "standardized_residual_nonfinite": True,
            }
        return finite

    def forced_and_finite(row: dict[str, object]) -> dict[str, object]:
        forced = forced_only(row)
        cell = (row["stratum_type"], row["stratum_value"], row["metric_id"])
        if cell == second_cell:
            return forced | {
                "observed_value": 1.0,
                "reference_mean": 0.0,
                "reference_sd": 1.0,
                "reference_mcse": 1.0 / math.sqrt(199.0),
                "standardized_residual": 1.0,
                "standardized_residual_nonfinite": False,
            }
        return forced

    observed_reasons: list[tuple[str, str, str, int, str]] = []
    for scenario_id, expected_reason in stress_reasons.items():
        for label, transform in (
            ("forced_only", forced_only),
            ("forced_and_finite_rule", forced_and_finite),
        ):
            candidate = _replace_predictive_holdout_group(
                core,
                complete_science_tables,
                scenario_id=scenario_id,
                transform=transform,
            )
            bundle = core.validate_science_bundle(**candidate)
            reason = dict(bundle.scenario_results)[scenario_id]
            control = next(
                row
                for row in bundle.control_rows
                if row["decision_row_id"] == f"scenario_gate|{scenario_id}"
            )
            observed_reasons.append(
                (
                    scenario_id,
                    label,
                    reason,
                    bundle.recommendation.recommendation_rank,
                    cast(str, control["gate_result"]),
                )
            )
            assert reason == expected_reason
    assert set(reached) == set(stress_reasons)
    assert all(rank == 1 and gate == "fail" for _, _, _, rank, gate in observed_reasons)


def _passing_evidence(scenario_id: str) -> dict[str, object]:
    core = _core()
    values: dict[str, object] = {
        "schema_valid": True,
        "design_pass": True,
        "fit_available": True,
        "convergence_pass": True,
        "coverage_pass": True,
        "recovery_pass": True,
        "predictive_available": True,
        "predictive_pass": True,
        "plugin_available": True,
        "plugin_rank": 3,
        "plugin_condition": 1e7,
        "identified": True,
        "sparse_coverage_pass": True,
        "sparse_width_pass": True,
        "decidable_intervals": 24,
        "zero_exclusions": 0,
        "alignment_correlation": 0.0,
        "alignment_pairs": 24,
        "alignment_wins": 24,
        "warning_available": True,
        "warning_forced": False,
        "equal_p": 0.5,
        "equal_refits": 199,
        "equal_status_exact": True,
        "equal_status_rows": tuple(
            {
                "parameter_id": parameter_id,
                "structural_status": structural_status,
                "practical_status": practical_status,
            }
            for parameter_id, structural_status, practical_status in (
                EXPECTED_EQUAL_EMISSION_STATUS_ROWS
            )
        ),
        "bootstrap_available": True,
        "narrow_wrong": False,
    }
    return {name: values[name] for name in core.SCENARIO_EVIDENCE_FIELDS[scenario_id]}


def _passing_vector(core: Any) -> dict[str, str]:
    return {
        scenario_id: core.reduce_scenario(scenario_id, _passing_evidence(scenario_id))
        for scenario_id in core.SCENARIO_IDS
    }


def _control_decision_rows(core: Any) -> tuple[dict[str, object], ...]:
    gate_family = dict(
        zip(
            core.SCENARIO_IDS,
            EXPECTED_ENUM_DOMAINS["gate_family"][:11],
            strict=True,
        )
    )

    def empty_row() -> dict[str, object]:
        row: dict[str, object] = {name: None for name in EXPECTED_CONTROL_DECISION_HEADER}
        row.update(
            silent_misspecification_failure=False,
            transportability_class="scheduled_count_only_point_process_bridge_required",
            interpretation="literal test evidence",
        )
        return row

    rows: list[dict[str, object]] = []
    for scenario_id in core.SCENARIO_IDS:
        row = empty_row()
        row.update(
            decision_row_id=f"scenario_gate|{scenario_id}",
            decision_row_type="scenario_gate",
            scenario_id=scenario_id,
            gate_family=gate_family[scenario_id],
            gate_result="pass",
        )
        if scenario_id == "zero_driver_effect_negative_control":
            row.update(
                attempted_replicates=24,
                evaluable_replicates=24,
                event_count=0,
                acceptance_lower_count=0,
                acceptance_upper_count=6,
            )
        elif scenario_id == "permuted_arrival_alignment_stress":
            row.update(
                alignment_correlation=core.authoritative_alignment_correlation(),
                attempted_replicates=24,
                evaluable_replicates=24,
                event_count=24,
                acceptance_lower_count=22,
                acceptance_upper_count=24,
            )
        elif scenario_id == "no_emission_contrast_negative_control":
            row.update(
                test_statistic=0.0,
                bootstrap_replicates=199,
                bootstrap_converged_count=199,
                bootstrap_failed_count=0,
                p_value=0.5,
                attempted_replicates=24,
                evaluable_replicates=24,
                event_count=99,
            )
        rows.append(row)
    for parameter_id, structural, practical in EXPECTED_EQUAL_EMISSION_STATUS_ROWS:
        row = empty_row()
        row.update(
            decision_row_id=(
                f"parameter_status|no_emission_contrast_negative_control|{parameter_id}"
            ),
            decision_row_type="parameter_status",
            scenario_id="no_emission_contrast_negative_control",
            parameter_id=parameter_id,
            structural_status=structural,
            practical_status=practical,
            gate_family="parameter_status",
            gate_result="diagnostic",
        )
        rows.append(row)
    final = empty_row()
    final.update(
        decision_row_id="final_decision",
        decision_row_type="final_decision",
        gate_family="final_recommendation",
        gate_result="pass",
        recommendation_rank=4,
        recommendation_class="latent_response_observation_gate_passed",
    )
    rows.append(final)
    return tuple(sorted(rows, key=lambda row: cast(str, row["decision_row_id"])))


def test_lro_3r_001_each_oracle_failure_maps_to_model_contract_failed() -> None:
    core = _core()
    for scenario_id in core.SCENARIO_IDS[:2]:
        for key in (
            "schema_valid",
            "design_pass",
            "fit_available",
            "coverage_pass",
            "convergence_pass",
            "recovery_pass",
        ):
            reason = core.reduce_scenario(
                scenario_id, _passing_evidence(scenario_id) | {key: False}
            )
            assert reason.startswith("contract_failure:")
            assert (
                core.reduce_recommendation(
                    _passing_vector(core) | {scenario_id: reason}
                ).recommendation_rank
                == 1
            )


def test_lro_3r_002_dense_complete_scientific_failure_maps_to_confounding() -> None:
    core = _core()
    for key in (
        "convergence_pass",
        "coverage_pass",
        "recovery_pass",
        "predictive_pass",
        "identified",
    ):
        reason = core.reduce_scenario(
            "dense_count_exact_model",
            _passing_evidence("dense_count_exact_model") | {key: False},
        )
        assert reason == "confounding:dense_joint_failed"
        result = core.reduce_recommendation(
            _passing_vector(core) | {"dense_count_exact_model": reason}
        )
        assert (result.recommendation_rank, result.recommendation_class) == (
            2,
            "process_observation_confounded",
        )


def test_lro_3r_003_structured_recovery_only_failure_maps_to_observation_limited() -> None:
    core = _core()
    reason = core.reduce_scenario(
        "structured_imperfect_effort",
        _passing_evidence("structured_imperfect_effort") | {"recovery_pass": False},
    )
    result = core.reduce_recommendation(
        _passing_vector(core) | {"structured_imperfect_effort": reason}
    )
    assert reason == "structured_limitation:structured_precision_recovery_failed"
    assert result.recommendation_rank == 3


def test_lro_3r_004_structured_coverage_predictive_fit_or_plugin_failure_is_rank_one() -> None:
    core = _core()
    failures = (
        {"coverage_pass": False},
        {"fit_available": False},
        {"predictive_available": False},
        {"predictive_pass": False},
        {"plugin_rank": 2},
        {"plugin_rank": 4},
        {"plugin_condition": 0.5},
        {"plugin_condition": 1e8},
        {"plugin_available": False},
    )
    for failure in failures:
        reason = core.reduce_scenario(
            "structured_imperfect_effort",
            _passing_evidence("structured_imperfect_effort") | failure,
        )
        assert reason == "contract_failure:structured_not_calibrated"


def test_lro_3r_005_structured_accepted_estimand_unidentified_is_rank_two() -> None:
    core = _core()
    reason = core.reduce_scenario(
        "structured_imperfect_effort",
        _passing_evidence("structured_imperfect_effort") | {"identified": False},
    )
    assert reason == "confounding:structured_estimand_unidentified"


def test_lro_3r_006_sparse_honesty_failure_is_rank_one() -> None:
    core = _core()
    for key in (
        "schema_valid",
        "fit_available",
        "predictive_available",
        "predictive_pass",
        "sparse_coverage_pass",
        "sparse_width_pass",
    ):
        assert core.reduce_scenario(
            "sparse_expected_failure",
            _passing_evidence("sparse_expected_failure") | {key: False},
        ) == ("contract_failure:sparse_honesty_failed")


def test_lro_3r_007_alignment_correlation_boundary_and_availability_are_rank_one() -> None:
    core = _core()
    assert (
        core.reduce_scenario(
            "permuted_arrival_alignment_stress",
            _passing_evidence("permuted_arrival_alignment_stress")
            | {"alignment_correlation": 0.25},
        )
        == "pass"
    )
    for value in (np.nextafter(0.25, 1.0), float("nan")):
        assert core.reduce_scenario(
            "permuted_arrival_alignment_stress",
            _passing_evidence("permuted_arrival_alignment_stress")
            | {"alignment_correlation": value},
        ).startswith("contract_failure")
    assert core.reduce_scenario(
        "permuted_arrival_alignment_stress",
        _passing_evidence("permuted_arrival_alignment_stress") | {"alignment_pairs": 23},
    ).startswith("contract_failure")


def test_lro_3r_008_alignment_22_wins_passes_21_confounds() -> None:
    core = _core()
    passing_reason = core.reduce_scenario(
        "permuted_arrival_alignment_stress",
        _passing_evidence("permuted_arrival_alignment_stress") | {"alignment_wins": 22},
    )
    confounding_reason = core.reduce_scenario(
        "permuted_arrival_alignment_stress",
        _passing_evidence("permuted_arrival_alignment_stress") | {"alignment_wins": 21},
    )
    assert passing_reason == "pass"
    assert confounding_reason == "confounding:arrival_alignment_not_discriminated"
    assert (
        core.reduce_recommendation(
            _passing_vector(core) | {"permuted_arrival_alignment_stress": passing_reason}
        ).recommendation_rank
        == 4
    )
    confounded = core.reduce_recommendation(
        _passing_vector(core) | {"permuted_arrival_alignment_stress": confounding_reason}
    )
    assert (confounded.recommendation_rank, confounded.recommendation_class) == (
        2,
        "process_observation_confounded",
    )


def test_lro_3r_009_alignment_warning_is_mandatory_and_scientific() -> None:
    core = _core()
    for update in ({"warning_available": False}, {"warning_forced": True}):
        assert core.reduce_scenario(
            "permuted_arrival_alignment_stress",
            _passing_evidence("permuted_arrival_alignment_stress") | update,
        ) == ("contract_failure:alignment_silent_misspecification")


def test_lro_3r_010_equal_p_boundary_refit_completeness_and_status_independence() -> None:
    core = _core()
    assert core.CONTROL_DECISION_SUMMARY_HEADER == EXPECTED_CONTROL_DECISION_HEADER
    status_rows = tuple(
        {
            "parameter_id": parameter_id,
            "structural_status": structural,
            "practical_status": practical,
        }
        for parameter_id, structural, practical in EXPECTED_EQUAL_EMISSION_STATUS_ROWS
    )
    assert (
        tuple(
            (
                row["parameter_id"],
                row["structural_status"],
                row["practical_status"],
            )
            for row in core.validate_equal_emission_status_rows(status_rows)
        )
        == EXPECTED_EQUAL_EMISSION_STATUS_ROWS
    )
    control_rows = _control_decision_rows(core)
    assert len(core.validate_control_decision_rows(control_rows)) == 18
    changed_control_rows = tuple(
        row | {"structural_status": "identified"}
        if cast(str, row["decision_row_id"]).endswith("|alpha")
        else row
        for row in control_rows
    )
    with pytest.raises(ValueError, match=r"status|literal"):
        core.validate_control_decision_rows(changed_control_rows)
    assert (
        core.reduce_scenario(
            "no_emission_contrast_negative_control",
            _passing_evidence("no_emission_contrast_negative_control")
            | {"equal_p": 0.05, "equal_status_rows": status_rows},
        )
        == "pass"
    )
    changed_statuses = list(status_rows)
    changed_statuses[0] = changed_statuses[0] | {"structural_status": "identified"}
    for update in (
        {"equal_p": np.nextafter(0.05, 0.0)},
        {"equal_p": 1.01},
        {"equal_refits": 198},
        {"equal_status_rows": tuple(changed_statuses)},
        {"equal_status_rows": status_rows[:-1]},
        {"fit_available": False},
        {"bootstrap_available": False},
        {"predictive_available": False},
        {"plugin_available": False},
    ):
        assert core.reduce_scenario(
            "no_emission_contrast_negative_control",
            _passing_evidence("no_emission_contrast_negative_control") | update,
        ).startswith("contract_failure")


def test_lro_3r_011_dropout_and_frailty_warning_is_conditional_on_narrow_wrong() -> None:
    core = _core()
    for scenario_id in ("informative_dropout_misspecification_stress", "spatial_frailty_stress"):
        assert (
            core.reduce_scenario(
                scenario_id,
                _passing_evidence(scenario_id) | {"warning_available": False},
            )
            == "pass"
        )
        assert core.reduce_scenario(
            scenario_id,
            _passing_evidence(scenario_id) | {"narrow_wrong": True, "warning_available": False},
        ).startswith("contract_failure")
        assert core.reduce_scenario(
            scenario_id,
            _passing_evidence(scenario_id) | {"narrow_wrong": False, "warning_forced": True},
        ).startswith("contract_failure")


def test_lro_3r_012_continuous_abundance_warning_is_mandatory() -> None:
    core = _core()
    assert (
        core.reduce_scenario(
            "goal018_continuous_abundance_stress",
            _passing_evidence("goal018_continuous_abundance_stress"),
        )
        == "pass"
    )
    assert core.reduce_scenario(
        "goal018_continuous_abundance_stress",
        _passing_evidence("goal018_continuous_abundance_stress") | {"warning_available": False},
    ).startswith("contract_failure")
    assert core.reduce_scenario(
        "goal018_continuous_abundance_stress",
        _passing_evidence("goal018_continuous_abundance_stress") | {"warning_forced": True},
    ).startswith("contract_failure")


def test_lro_3r_013_each_control_and_stress_is_required_for_top_pass() -> None:
    core = _core()
    passing = _passing_vector(core)
    assert core.reduce_recommendation(passing).recommendation_rank == 4
    for scenario_id in core.SCENARIO_IDS[5:]:
        reduced = dict(passing)
        reduced.pop(scenario_id)
        assert core.reduce_recommendation(reduced).recommendation_rank == 1


def test_lro_3r_014_rank_three_requires_every_nonstructured_gate() -> None:
    core = _core()
    vector = _passing_vector(core) | {
        "structured_imperfect_effort": "structured_limitation:structured_precision_recovery_failed"
    }
    assert core.reduce_recommendation(vector).recommendation_rank == 3
    for scenario_id in core.SCENARIO_IDS[4:]:
        assert (
            core.reduce_recommendation(
                vector | {scenario_id: "contract_failure:test"}
            ).recommendation_rank
            == 1
        )


def test_lro_3r_015_rank_precedence_and_canonical_reasons_are_stable() -> None:
    core = _core()
    vector = _passing_vector(core) | {
        "dense_count_exact_model": "confounding:dense_joint_failed",
        "structured_imperfect_effort": "structured_limitation:structured_precision_recovery_failed",
        "sparse_expected_failure": "contract_failure:sparse_honesty_failed",
    }
    result = core.reduce_recommendation(vector)
    assert result.recommendation_rank == 1
    assert result.reasons == (
        "confounding:dense_joint_failed",
        "structured_limitation:structured_precision_recovery_failed",
        "contract_failure:sparse_honesty_failed",
    )
    assert result.reason == "contract_failure:sparse_honesty_failed"


def test_lro_3r_016_unknown_missing_duplicate_or_contradictory_never_passes() -> None:
    core = _core()
    for vector in (
        {},
        _passing_vector(core) | {"unknown": "pass"},
        _passing_vector(core) | {core.SCENARIO_IDS[0]: "unknown"},
    ):
        assert core.reduce_recommendation(vector).recommendation_rank == 1
    impossible = _passing_vector(core) | {
        "process_oracle_observed_transition": "confounding:not_a_canonical_oracle_reason"
    }
    assert core.reduce_recommendation(impossible).recommendation_rank == 1
    for scenario_id, next_scenario in zip(
        core.SCENARIO_IDS, (*core.SCENARIO_IDS[1:], core.SCENARIO_IDS[0]), strict=True
    ):
        foreign_reason = next(
            reason for reason in core.SCENARIO_LOCAL_REASONS[next_scenario] if reason != "pass"
        )
        vector = _passing_vector(core) | {scenario_id: foreign_reason}
        assert core.reduce_recommendation(vector).reason == (
            "incomplete_or_contradictory_decision_vector"
        )


def test_lro_3r_017_local_and_global_reducers_are_total() -> None:
    core = _core()
    for scenario_id in core.SCENARIO_IDS:
        for key in _passing_evidence(scenario_id):
            reason = core.reduce_scenario(scenario_id, _passing_evidence(scenario_id) | {key: None})
            assert isinstance(reason, str) and reason
    assert core.reduce_recommendation(_passing_vector(core)).recommendation_rank in (1, 2, 3, 4)
    for scenario_id, reasons in core.SCENARIO_LOCAL_REASONS.items():
        for reason in reasons:
            result = core.reduce_recommendation(_passing_vector(core) | {scenario_id: reason})
            assert result.recommendation_rank in (1, 2, 3, 4)
    contradictions = (
        {"fit_available": False, "convergence_pass": True},
        {"predictive_available": False, "predictive_pass": True},
        {"plugin_available": False, "plugin_rank": 3},
        {"warning_available": True, "predictive_available": False},
        {"warning_forced": True},
    )
    for scenario_id in core.SCENARIO_IDS:
        for contradiction in contradictions:
            assert core.reduce_scenario(
                scenario_id, _passing_evidence(scenario_id) | contradiction
            ).startswith("contract_failure:")
    availability_precedence = {
        "permuted_arrival_alignment_stress": (
            "contract_failure:alignment_contract_or_availability_failed"
        ),
        "informative_dropout_misspecification_stress": (
            "contract_failure:informative_dropout_unavailable"
        ),
        "goal018_continuous_abundance_stress": (
            "contract_failure:continuous_abundance_unavailable"
        ),
        "spatial_frailty_stress": "contract_failure:spatial_frailty_unavailable",
    }
    for scenario_id, expected_reason in availability_precedence.items():
        evidence = _passing_evidence(scenario_id) | {
            "fit_available": False,
            "warning_forced": True,
        }
        assert core.reduce_scenario(scenario_id, evidence) == expected_reason
    passing_vector = _passing_vector(core)
    for scenario_id in core.SCENARIO_IDS:
        base = _passing_evidence(scenario_id)
        boolean_names = tuple(name for name, value in base.items() if type(value) is bool)
        for states in product((False, True), repeat=len(boolean_names)):
            evidence = base | dict(zip(boolean_names, states, strict=True))
            reason = core.reduce_scenario(scenario_id, evidence)
            assert reason in core.SCENARIO_LOCAL_REASONS[scenario_id]
            result = core.reduce_recommendation(passing_vector | {scenario_id: reason})
            assert (result.recommendation_rank, result.recommendation_class) in tuple(
                enumerate(core.RECOMMENDATION_CLASSES, start=1)
            )
    nonpass = {
        scenario_id: tuple(reason for reason in reasons if reason != "pass")
        for scenario_id, reasons in core.SCENARIO_LOCAL_REASONS.items()
    }
    for left_index, left_scenario in enumerate(core.SCENARIO_IDS):
        for right_scenario in core.SCENARIO_IDS[left_index + 1 :]:
            for left_reason, right_reason in product(
                nonpass[left_scenario], nonpass[right_scenario]
            ):
                result = core.reduce_recommendation(
                    passing_vector
                    | {
                        left_scenario: left_reason,
                        right_scenario: right_reason,
                    }
                )
                assert (result.recommendation_rank, result.recommendation_class) in tuple(
                    enumerate(core.RECOMMENDATION_CLASSES, start=1)
                )


def test_lro_3r_018_transportability_class_is_invariant() -> None:
    core = _core()
    vectors = [
        _passing_vector(core),
        {},
        _passing_vector(core) | {"dense_count_exact_model": "confounding:dense_joint_failed"},
        _passing_vector(core)
        | {
            "structured_imperfect_effort": (
                "structured_limitation:structured_precision_recovery_failed"
            )
        },
    ]
    assert {core.reduce_recommendation(vector).transportability_class for vector in vectors} == {
        "scheduled_count_only_point_process_bridge_required"
    }


def test_lro_3r_019_every_stress_fit_plugin_or_predictive_unavailability_is_rank_one() -> None:
    core = _core()
    for scenario_id in (
        "permuted_arrival_alignment_stress",
        "informative_dropout_misspecification_stress",
        "goal018_continuous_abundance_stress",
        "spatial_frailty_stress",
    ):
        for key in ("fit_available", "plugin_available", "predictive_available"):
            assert core.reduce_scenario(
                scenario_id, _passing_evidence(scenario_id) | {key: False}
            ).startswith("contract_failure:")


def test_lro_3r_020_all_required_global_and_scenario_gates_pass_reaches_rank_four(
    complete_science_tables: dict[str, tuple[dict[str, object], ...]],
) -> None:
    core = _core()
    bundle = core.validate_science_bundle(**complete_science_tables)
    assert dict(bundle.scenario_results) == {
        scenario_id: "pass" for scenario_id in core.SCENARIO_IDS
    }
    assert len(complete_science_tables["fit_rows"]) == 2685
    assert len(complete_science_tables["recovery_rows"]) == 2340
    assert len(complete_science_tables["profile_rows"]) == 11700
    assert len(complete_science_tables["control_rows"]) == 18
    final = next(
        row
        for row in complete_science_tables["control_rows"]
        if row["decision_row_id"] == "final_decision"
    )
    assert (
        bundle.recommendation.recommendation_rank,
        bundle.recommendation.recommendation_class,
        final["recommendation_rank"],
        final["recommendation_class"],
        final["gate_result"],
    ) == (
        4,
        "latent_response_observation_gate_passed",
        4,
        "latent_response_observation_gate_passed",
        "pass",
    )


def _write_fixture_artifacts(core: Any, root: Any) -> None:
    for relative_path in core.ARTIFACT_PATHS:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"{relative_path}\n".encode())


def test_lro_3s_001_exact_22_file_manifest_and_null_config_hashes(
    tmp_path: Path,
    complete_science_tables: dict[str, tuple[dict[str, object], ...]],
) -> None:
    core = _core()
    manifest = core.expected_artifact_manifest()
    assert len(manifest) == 22
    assert tuple(entry["path"] for entry in manifest) == core.ARTIFACT_PATHS
    assert all(entry["required"] is True and entry["sha256"] is None for entry in manifest)
    for invalid in (
        manifest[:-1],
        (*manifest, manifest[0]),
        manifest[::-1],
        (*manifest[:-1], manifest[-1] | {"sha256": "x"}),
    ):
        with pytest.raises(ValueError):
            core.validate_expected_artifact_manifest(invalid)
    source_provenance = {
        "schema_version": "v1",
        "source_commit": "53462d0365babf2c8070714a930f69b4071af276",
        "parameter_set_id": "balanced_corridor_detour_v2",
        "source_apis": [
            "spatext.synth.medium.landscape.build_synth_medium_landscape",
            "spatext.synth.medium.spread_impact.build_synth_medium_spread_impact_review_pack",
        ],
        "expected_counts": {
            "landscape_cell_count": 6048,
            "passable_cell_count": 5225,
            "water_cell_count": 823,
            "final_colonized_passable_count": 4605,
            "finite_prey_extirpation_count": 4289,
        },
        "reconciled_counts": {
            "landscape_cell_count": 6048,
            "passable_cell_count": 5225,
            "water_cell_count": 823,
            "final_colonized_passable_count": 4605,
            "finite_prey_extirpation_count": 4289,
        },
        "landscape_sha256": ("53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a"),
        "arrival_sha256": ("5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba"),
        "passed": True,
    }
    core.validate_source_provenance_document(source_provenance)
    with pytest.raises(ValueError, match="source provenance"):
        core.validate_source_provenance_document(source_provenance | {"schema_version": "v2"})
    measured_units = [
        {
            "task_id": f"runtime|{scenario_id}",
            "scenario_id": scenario_id,
            "benchmark_split": "calibration" if index < 4 else "development",
            "benchmark_replicate_first": 0,
            "benchmark_replicate_last": (
                23 if scenario_id == "no_emission_contrast_negative_control" else 0
            ),
            "measured_duration_seconds": 1.0,
            "calibration_repeat_count": 0 if index >= 4 else 24,
            "holdout_repeat_count": 48 if index < 4 else 24,
            "includes_profiles": scenario_id
            not in {
                "observation_oracle_fixed_transition",
                "no_emission_contrast_negative_control",
                "goal018_continuous_abundance_stress",
            },
            "predictive_reference_count": 199,
            "scientific_row": scenario_id != "no_emission_contrast_negative_control",
        }
        for index, scenario_id in enumerate(core.SCENARIO_IDS)
    ]
    runtime_projection = {
        "schema_version": "v1",
        "workers": 8,
        "safety_factor": 1.20,
        "measured_task_units": measured_units,
        "equal_bootstrap_task_unit": {
            "task_id": "runtime|equal-bootstrap|0",
            "benchmark_split": "development",
            "bundle_index": 0,
            "pseudo_replicate_first": 0,
            "pseudo_replicate_last": 23,
            "measured_duration_seconds": 1.0,
            "calibration_repeat_count": 0,
            "holdout_repeat_count": 199,
            "scientific_row": False,
        },
        "calibration_task_durations": [{"task_id": "calibration|0", "duration_seconds": 1.0}],
        "holdout_task_durations": [{"task_id": "holdout|0", "duration_seconds": 1.0}],
        "calibration_worker_loads": [0.0] * 8,
        "holdout_worker_loads": [0.0] * 8,
        "projected_calibration_seconds": 0.0,
        "projected_holdout_seconds": 0.0,
        "holdout_payload_instantiated": False,
        "scientific_rows_emitted": False,
        "passed": True,
    }
    with pytest.raises(ValueError, match=r"runtime|task|LPT|projection|safety"):
        core.validate_runtime_projection_document(runtime_projection)
    valid_runtime = core.build_runtime_projection_document(
        measured_duration_seconds={
            scenario_id: 1.0 + index / 10.0 for index, scenario_id in enumerate(core.SCENARIO_IDS)
        },
        equal_bootstrap_duration_seconds=0.75,
    )
    core.validate_runtime_projection_document(valid_runtime)
    measured = cast(list[dict[str, object]], valid_runtime["measured_task_units"])
    assert tuple(unit["task_id"] for unit in measured) == tuple(
        f"benchmark|scenario={scenario_id}" for scenario_id in core.SCENARIO_IDS
    )
    assert tuple(unit["includes_profiles"] for unit in measured) == tuple(
        scenario_id != "no_emission_contrast_negative_control" for scenario_id in core.SCENARIO_IDS
    )
    assert tuple(unit["predictive_reference_count"] for unit in measured) == (
        0,
        *([199] * 10),
    )
    equal_runtime = cast(dict[str, object], valid_runtime["equal_bootstrap_task_unit"])
    assert equal_runtime["calibration_repeat_count"] == 0
    assert equal_runtime["holdout_repeat_count"] == 199
    assert len(valid_runtime["calibration_task_durations"]) == 96
    assert len(valid_runtime["holdout_task_durations"]) == 536
    calibration_tasks = cast(list[dict[str, object]], valid_runtime["calibration_task_durations"])
    holdout_tasks = cast(list[dict[str, object]], valid_runtime["holdout_task_durations"])
    assert calibration_tasks[0]["task_id"] == (
        "calibration|scenario=process_oracle_observed_transition|replicate=0000"
    )
    assert calibration_tasks[-1]["task_id"] == (
        "calibration|scenario=structured_imperfect_effort|replicate=0023"
    )
    equal_bundle_index = next(
        index
        for index, task in enumerate(holdout_tasks)
        if task["task_id"] == "holdout|scenario=no_emission_contrast_negative_control|bundle=0000"
    )
    assert holdout_tasks[equal_bundle_index + 1]["task_id"] == (
        "holdout|scenario=no_emission_contrast_negative_control|component=bootstrap|draw=0000"
    )
    assert holdout_tasks[equal_bundle_index + 199]["task_id"] == (
        "holdout|scenario=no_emission_contrast_negative_control|component=bootstrap|draw=0198"
    )
    assert valid_runtime["calibration_worker_loads"] == core.deterministic_lpt_worker_loads(
        calibration_tasks
    )
    assert valid_runtime["holdout_worker_loads"] == core.deterministic_lpt_worker_loads(
        holdout_tasks
    )
    assert valid_runtime["safety_factor"] == 1.20
    assert valid_runtime["projected_calibration_seconds"] == (
        1.20 * max(cast(list[float], valid_runtime["calibration_worker_loads"]))
    )
    assert valid_runtime["projected_holdout_seconds"] == (
        1.20 * max(cast(list[float], valid_runtime["holdout_worker_loads"]))
    )
    for runtime_contradiction in (
        {"safety_factor": 9.0},
        {
            "calibration_task_durations": cast(
                list[object], valid_runtime["calibration_task_durations"]
            )[:1]
        },
        {"holdout_worker_loads": [0.0] * 8},
        {"projected_holdout_seconds": 0.0},
        {"passed": not valid_runtime["passed"]},
    ):
        with pytest.raises(ValueError, match=r"runtime|task|LPT|projection|passed"):
            core.validate_runtime_projection_document(valid_runtime | runtime_contradiction)
    with pytest.raises(ValueError, match=r"workers|runtime"):
        core.validate_runtime_projection_document(valid_runtime | {"workers": 4})
    shape_only_holdout_manifest = {
        "schema_version": "v1",
        "spec_sha256": "1" * 64,
        "config_sha256": "2" * 64,
        "source_sha256": "3" * 64,
        "tracked_state_sha256": "4" * 64,
        "seed_namespace": "goal023-holdout-v1",
        "receipt_sha256": "5" * 64,
        "exposed": True,
        "invalidated": False,
        "no_contract_change": True,
    }
    core.validate_holdout_manifest_document(shape_only_holdout_manifest)
    with pytest.raises(ValueError, match=r"namespace|literal"):
        core.validate_holdout_manifest_document(
            shape_only_holdout_manifest | {"seed_namespace": "other"}
        )

    config_document, _ = core._canonical_config_document(_valid_config_payload(core))
    holdout_without_hash = {
        "schema_version": "v1",
        "spec_sha256": config_document["spec_sha256"],
        "config_sha256": config_document["config_sha256"],
        "source_sha256": config_document["source_sha256"],
        "tracked_state_sha256": config_document["tracked_state_sha256"],
        "seed_namespace": "goal023-holdout-v1",
        "exposed": True,
        "invalidated": False,
        "no_contract_change": True,
    }
    holdout_manifest = holdout_without_hash | {
        "receipt_sha256": sha256(core.canonical_json_bytes(holdout_without_hash)).hexdigest()
    }
    _write_fixture_artifacts(core, tmp_path)
    artifact_details = core.build_artifact_manifest_document(tmp_path)
    science_bundle = core.validate_science_bundle(**complete_science_tables)
    base_predictive_states = dict(science_bundle.predictive_states)
    assert (
        base_predictive_states["zero_driver_effect_negative_control"],
        base_predictive_states["permuted_arrival_alignment_stress"],
        base_predictive_states["goal018_continuous_abundance_stress"],
    ) == (
        core.PredictiveScenarioState(True, True, False, False, False),
        core.PredictiveScenarioState(True, False, True, True, False),
        core.PredictiveScenarioState(True, False, True, True, False),
    )
    verification_inputs = {
        "config_payload": config_document,
        "runtime_projection": valid_runtime,
        "source_provenance": source_provenance,
        "holdout_manifest": holdout_manifest,
        "artifact_manifest_details": artifact_details,
        "artifact_root": tmp_path,
        "science_bundle": science_bundle,
    }
    verification = core.build_verification_document(**verification_inputs)
    core.validate_verification_document(verification, **verification_inputs)
    assert verification["passed"] is True
    assert verification["recommendation_class"] == "latent_response_observation_gate_passed"
    assert all(
        check["details"].get("design_row_count") == 1695
        and check["details"].get("design_evidence_sha256") == science_bundle.design_evidence_sha256
        for check in verification["checks"][:11]
    )
    assert (
        verification["recommendation_class"] == science_bundle.recommendation.recommendation_class
    )
    assert verification["checks"][-2]["details"] == artifact_details

    integrated_mutations = (
        (
            "zero_driver_effect_negative_control",
            _with_stouffer_target(
                core,
                complete_science_tables,
                scenario_id="zero_driver_effect_negative_control",
                target=float(np.nextafter(3.0, math.inf)),
            ),
            "contract_failure:zero_driver_unavailable",
        ),
        (
            "permuted_arrival_alignment_stress",
            _with_forced_predictive_warning(
                core,
                complete_science_tables,
                scenario_id="permuted_arrival_alignment_stress",
                finite_rule_also_fires=True,
            ),
            "contract_failure:alignment_contract_or_availability_failed",
        ),
    )
    for scenario_id, candidate, expected_reason in integrated_mutations:
        candidate_bundle = core.validate_science_bundle(**candidate)
        candidate_control = next(
            row
            for row in candidate_bundle.control_rows
            if row["decision_row_id"] == f"scenario_gate|{scenario_id}"
        )
        candidate_final = next(
            row
            for row in candidate_bundle.control_rows
            if row["decision_row_id"] == "final_decision"
        )
        assert dict(candidate_bundle.scenario_results)[scenario_id] == expected_reason
        assert (candidate_control["gate_result"], candidate_control["interpretation"]) == (
            "fail",
            expected_reason,
        )
        assert (
            candidate_final["recommendation_rank"],
            candidate_final["recommendation_class"],
            candidate_bundle.recommendation.recommendation_rank,
            candidate_bundle.recommendation.recommendation_class,
        ) == (1, "model_contract_failed", 1, "model_contract_failed")
        candidate_inputs = verification_inputs | {"science_bundle": candidate_bundle}
        candidate_verification = core.build_verification_document(**candidate_inputs)
        core.validate_verification_document(candidate_verification, **candidate_inputs)
        scenario_check = next(
            check
            for check in candidate_verification["checks"]
            if check["name"] == core.SCENARIO_GATE_FAMILY[scenario_id]
        )
        assert scenario_check["passed"] is False
        assert scenario_check["details"]["reason"] == expected_reason
        if scenario_id == "zero_driver_effect_negative_control":
            assert (
                scenario_check["details"]["predictive_complete_finite"],
                scenario_check["details"]["predictive_pass"],
                scenario_check["details"]["finite_rule_fired"],
                scenario_check["details"]["scientific_warning_available"],
                scenario_check["details"]["forced_warning"],
            ) == (True, False, True, True, False)
        if scenario_id == "permuted_arrival_alignment_stress":
            assert (
                scenario_check["details"]["predictive_complete_finite"],
                scenario_check["details"]["predictive_pass"],
                scenario_check["details"]["finite_rule_fired"],
                scenario_check["details"]["scientific_warning_available"],
                scenario_check["details"]["forced_warning"],
            ) == (False, False, True, False, True)
        assert (
            candidate_verification["recommendation_class"],
            candidate_verification["passed"],
        ) == ("model_contract_failed", False)

    contradictory_design = _with_design_update(
        core,
        complete_science_tables,
        scenario_id="structured_imperfect_effort",
        design_kind="plugin",
        update={
            "design_condition_number": 1e8,
            "design_passed": False,
            "design_failure_code": "condition_limit_failed",
        },
        recompute_controls=False,
    )
    with pytest.raises(ValueError, match=r"fit.*design|state|contradict"):
        core.validate_science_bundle(**contradictory_design)

    impossible = verification | {
        "checks": [
            {"name": check["name"], "passed": False, "details": {}}
            for check in cast(list[dict[str, object]], verification["checks"])
        ],
        "recommendation_class": "latent_response_observation_gate_passed",
        "passed": True,
    }
    with pytest.raises(ValueError, match=r"verification|manifest|passed|details|recommendation"):
        core.validate_verification_document(impossible, **verification_inputs)
    for verification_contradiction in (
        {
            "checks": cast(list[object], verification["checks"])[:-1],
        },
        {"passed": not verification["passed"]},
        {"recommendation_class": "model_contract_failed"},
    ):
        with pytest.raises(ValueError, match=r"verification|checks|recommendation|passed"):
            core.validate_verification_document(
                verification | verification_contradiction,
                **verification_inputs,
            )
    (tmp_path / "report.md").write_text("changed represented bytes\n")
    with pytest.raises(ValueError, match=r"artifact|manifest|live"):
        core.validate_verification_document(verification, **verification_inputs)


def test_lro_3s_002_verification_represents_other_21_files(tmp_path: Any) -> None:
    core = _core()
    _write_fixture_artifacts(core, tmp_path)
    document = core.build_artifact_manifest_document(tmp_path)
    assert tuple(entry["path"] for entry in document["entries"]) == tuple(
        path for path in core.ARTIFACT_PATHS if path != "verification.json"
    )
    assert len(document["entries"]) == 21
    independent_entries = tuple(
        (relative_path, sha256((tmp_path / relative_path).read_bytes()).hexdigest())
        for relative_path in core.ARTIFACT_PATHS
        if relative_path != "verification.json"
    )
    independent_digest = sha256(
        "".join(
            f"{digest}  {relative_path}\n" for relative_path, digest in independent_entries
        ).encode()
    ).hexdigest()
    assert document["entries"] == [
        {"path": relative_path, "sha256": digest} for relative_path, digest in independent_entries
    ]
    assert document["represented_artifact_set_sha256"] == independent_digest
    assert core.validate_artifact_manifest_details(document) == document
    with pytest.raises(ValueError, match=r"digest|manifest"):
        core.validate_artifact_manifest_details(
            document | {"represented_artifact_set_sha256": "0" * 64}
        )
    (tmp_path / "extra.txt").write_text("extra\n")
    with pytest.raises(ValueError, match="represented"):
        core.build_artifact_manifest_document(tmp_path)


def test_lro_3s_003_external_snapshot_includes_all_22_files(tmp_path: Any) -> None:
    core = _core()
    _write_fixture_artifacts(core, tmp_path)
    assert len(core.artifact_snapshot(tmp_path).entries) == 22
    (tmp_path / "extra.txt").write_text("extra\n")
    with pytest.raises(ValueError, match="exact 22-file"):
        core.artifact_snapshot(tmp_path)
    (tmp_path / "extra.txt").unlink()
    (tmp_path / core.ARTIFACT_PATHS[0]).write_bytes(b"")
    with pytest.raises(ValueError):
        core.artifact_snapshot(tmp_path)


def test_lro_3s_004_config_and_receipt_self_hashes_are_not_file_hashes(tmp_path: Any) -> None:
    core = _core()
    repo_root = Path(__file__).resolve().parents[1]
    authority = core.capture_live_authority(repo_root)
    assert (
        authority.spec_sha256
        == sha256((repo_root / core.AUTHORITATIVE_SPEC_RELATIVE_PATH).read_bytes()).hexdigest()
    )
    assert authority.source_sha256 == (
        "6969917a4ce6dd196bd5db740f53ab18c48d57667107e121d60e96b357ba3eb0"
    )
    assert authority.source_receipt_file_sha256 == core.ACCEPTED_SOURCE_RECEIPT_FILE_SHA256
    forged_authority_root = tmp_path / "forged-authority"
    for relative_path in (
        core.AUTHORITATIVE_SPEC_RELATIVE_PATH,
        core.SOURCE_RECEIPT_RELATIVE_PATH,
    ):
        target = forged_authority_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((repo_root / relative_path).read_bytes())
    source_receipt = forged_authority_root / core.SOURCE_RECEIPT_RELATIVE_PATH
    source_receipt.write_bytes(source_receipt.read_bytes() + b" ")
    with pytest.raises(ValueError, match="source receipt file SHA"):
        core.capture_live_authority(forged_authority_root)

    phase_root = tmp_path / "authority-phase"
    guard, _ = _phase_tree(core, phase_root, "config_emission")
    for field in ("spec_sha256", "source_sha256"):
        output = tmp_path / f"false-{field}.json"
        payload = _valid_config_payload(core, tracked_state_sha256=guard.analytical_sha256) | {
            field: "0" * 64
        }
        with pytest.raises(ValueError, match="live authority"):
            core.guard_config_emission(guard, output, payload=payload)
        assert not output.exists()

    config = tmp_path / "recovery_gate_config.json"
    core.write_canonical_config(config, _valid_config_payload(core))
    config_identity = core.load_frozen_config_identity(config)
    assert config_identity.payload["schema_version"] == "v1"
    assert config_identity.config_sha256 != config_identity.config_file_sha256
    independent_without_hash = dict(config_identity.payload)
    independent_embedded = independent_without_hash.pop("config_sha256")
    independent_without_hash_bytes = (
        json.dumps(
            independent_without_hash,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")
    assert independent_embedded == sha256(independent_without_hash_bytes).hexdigest()
    assert config_identity.config_file_sha256 == sha256(config.read_bytes()).hexdigest()
    assert tuple(config_identity.payload["parameters"]) == core.CONFIG_PARAMETER_ROWS
    assert tuple(row["parameter_id"] for row in config_identity.payload["parameters"]) == (
        "alpha",
        "beta_driver",
        "beta_quality",
        "lambda_quasi",
        "lambda_present",
    )
    assert config_identity.payload["seed_partitions"] == core.FROZEN_SEED_PARTITIONS
    assert config_identity.payload["model"] == core.FROZEN_MODEL_CONFIG
    assert config_identity.payload["estimator"] == core.FROZEN_ESTIMATOR_CONFIG
    assert config_identity.payload["gates"] == core.FROZEN_GATE_CONFIG
    assert config_identity.payload["gates"]["coverage_gate_count"] == 15
    assert config_identity.payload["gates"]["negative_false_positive_rate"] == 0.10
    assert config_identity.payload["gates"]["sparse_coverage_alpha"] == 0.05
    assert config_identity.payload["gates"]["pit_familywise_alpha"] == 0.01
    wrong_schema_version = _valid_config_payload(core) | {"schema_version": "anything-nonempty"}
    wrong_schema_path = tmp_path / "wrong-schema-version.json"
    with pytest.raises(ValueError, match=r"schema.version|literal"):
        core.write_canonical_config(wrong_schema_path, wrong_schema_version)
    assert not wrong_schema_path.exists()
    invalid_payloads: list[dict[str, object]] = []
    missing_parameter_field = _valid_config_payload(core)
    missing_rows = [dict(row) for row in core.CONFIG_PARAMETER_ROWS]
    missing_rows[0].pop("role")
    missing_parameter_field["parameters"] = missing_rows
    invalid_payloads.append(missing_parameter_field)
    reordered_parameters = _valid_config_payload(core)
    reordered_parameters["parameters"] = [dict(row) for row in reversed(core.CONFIG_PARAMETER_ROWS)]
    invalid_payloads.append(reordered_parameters)
    wrong_support = _valid_config_payload(core)
    wrong_support_rows = [dict(row) for row in core.CONFIG_PARAMETER_ROWS]
    wrong_support_rows[1]["lower_bound"] = -2.0
    wrong_support["parameters"] = wrong_support_rows
    invalid_payloads.append(wrong_support)
    wrong_model = _valid_config_payload(core)
    wrong_model["model"] = dict(core.FROZEN_MODEL_CONFIG) | {"hazard_link": "logit"}
    invalid_payloads.append(wrong_model)
    wrong_estimator = _valid_config_payload(core)
    wrong_estimator["estimator"] = dict(core.FROZEN_ESTIMATOR_CONFIG) | {"deterministic_starts": 7}
    invalid_payloads.append(wrong_estimator)
    wrong_seed = _valid_config_payload(core)
    wrong_seed["seed_partitions"] = dict(core.FROZEN_SEED_PARTITIONS) | {
        "control_holdout_replicates": 23
    }
    invalid_payloads.append(wrong_seed)
    wrong_scenario = _valid_config_payload(core)
    wrong_scenarios = [asdict(row) for row in core.SCENARIO_DEFINITIONS]
    wrong_scenarios[-1]["calibration_replicates"] = 24
    wrong_scenario["scenarios"] = wrong_scenarios
    invalid_payloads.append(wrong_scenario)
    wrong_gate = _valid_config_payload(core)
    wrong_gate["gates"] = dict(core.FROZEN_GATE_CONFIG) | {"pit_familywise_alpha": 0.05}
    invalid_payloads.append(wrong_gate)
    for index, invalid_payload in enumerate(invalid_payloads):
        invalid_path = tmp_path / f"invalid-config-{index}.json"
        with pytest.raises(ValueError, match=r"literal|complete|frozen|parameters|scenarios"):
            core.write_canonical_config(invalid_path, invalid_payload)
        assert not invalid_path.exists()
    holdout = tmp_path / "holdout_receipt.json"
    core.write_canonical_receipt(holdout, _holdout_receipt_payload(core, config_identity))
    receipt_identity = core.load_holdout_receipt_identity(holdout)
    assert receipt_identity.receipt_sha256 != receipt_identity.holdout_receipt_file_sha256
    independent_receipt = dict(receipt_identity.payload)
    receipt_self_hash = independent_receipt.pop("receipt_sha256")
    independent_receipt_bytes = (
        json.dumps(
            independent_receipt,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")
    assert receipt_self_hash == sha256(independent_receipt_bytes).hexdigest()
    assert receipt_identity.holdout_receipt_file_sha256 == sha256(holdout.read_bytes()).hexdigest()
    preholdout = tmp_path / "preholdout_state_receipt.json"
    preholdout.write_bytes(core.canonical_json_bytes(_preholdout_payload(core, config_identity)))
    assert (
        core.load_receipt_file_identity(preholdout).file_sha256
        == sha256(preholdout.read_bytes()).hexdigest()
    )
    with pytest.raises(TypeError):
        core.require_phase_identities(config_identity, config_identity, receipt_identity)
    minimal_config = tmp_path / "minimal_config.json"
    with pytest.raises(ValueError, match="schema"):
        core.write_canonical_config(minimal_config, {})
    assert not minimal_config.exists()
    minimal_receipt = tmp_path / "minimal_receipt.json"
    core.write_canonical_receipt(minimal_receipt, {"exposed": True})
    with pytest.raises(ValueError, match="schema"):
        core.load_holdout_receipt_identity(minimal_receipt)


def test_lro_3s_005_phase_guards_require_typed_hash_identities(tmp_path: Any) -> None:
    core = _core()
    config = tmp_path / "recovery_gate_config.json"
    core.write_canonical_config(config, _valid_config_payload(core))
    identity = core.load_frozen_config_identity(config)
    with pytest.raises(TypeError):
        core.require_phase_identities({}, None, None)
    assert core.require_phase_identities(identity, None, None)[0] == identity
    forged = core.FrozenConfigIdentity(tmp_path / "unchecked.json", {}, "a" * 64, "b" * 64, b"{}\n")
    with pytest.raises(ValueError, match="validated"):
        core.require_phase_identities(forged, None, None)


def test_lro_3s_006_task3_calibration_dispatch_smoke_is_fixture_only(tmp_path: Any) -> None:
    core = _core()
    result = core.dispatch_fixture_calibration(
        workers=4,
        output_dir=tmp_path,
        services={"run_fixture_tasks": core.fixture_task_service()},
    )
    assert tuple(result[key] for key in core.FIXTURE_ZERO_COUNTERS) == (False, False, 0, 0)

    def lying_service(*, side_effects: dict[str, Any], **_: object) -> dict[str, object]:
        side_effects["rng_factory"]()
        return dict(core.FIXTURE_ZERO_COUNTERS)

    with pytest.raises(TypeError, match=r"owned|fixture"):
        core.dispatch_fixture_calibration(
            workers=1,
            output_dir=tmp_path,
            services={"run_fixture_tasks": lying_service},
        )
    external_calls: list[str] = []

    def externally_lying_service(**_: object) -> dict[str, object]:
        external_calls.append("rng")
        return dict(core.FIXTURE_ZERO_COUNTERS)

    with pytest.raises((TypeError, ValueError), match=r"owned|fixture"):
        core.dispatch_fixture_calibration(
            workers=1,
            output_dir=tmp_path,
            services={"run_fixture_tasks": externally_lying_service},
        )
    assert external_calls == []


def test_lro_3s_007_task3_smoke_cannot_reach_live_calibration_runner(tmp_path: Any) -> None:
    core = _core()
    calls: list[str] = []

    def bomb(**_: object) -> object:
        calls.append("live")
        raise AssertionError("live runner reached")

    with pytest.raises(TypeError, match="only the owned"):
        core.dispatch_fixture_calibration(
            workers=1,
            output_dir=tmp_path,
            services={
                "run_fixture_tasks": core.fixture_task_service(),
                "live_calibration_runner": bomb,
                "rng_factory": bomb,
            },
        )
    assert calls == []


def test_lro_3s_008_task4_is_first_live_benchmark_and_calibration_owner() -> None:
    core = _core()
    assert core.LIVE_CALIBRATION_OWNER == "task4"
    with pytest.raises(ValueError, match="Task 3"):
        core.validate_task3_command(("python", "runner.py", "--phase", "calibration"))
    with pytest.raises(ValueError, match="Task 3"):
        core.validate_task3_command(("python", "runner.py", "--phase=calibration"))
    core.validate_task3_command(("pytest", "-k", "fixture"))


def test_lro_3s_009_scenario_definitions_use_contract_order() -> None:
    core = _core()
    first = core.scenario_definition_bytes(core.SCENARIO_DEFINITIONS)
    second = core.scenario_definition_bytes(tuple(core.SCENARIO_DEFINITIONS))
    assert first == second
    assert core.AUTHORITY_ENUM_DOMAINS == EXPECTED_ENUM_DOMAINS
    assert core.VISUAL_SOURCE_TABLES == EXPECTED_VISUAL_SOURCE_TABLES
    assert (
        tuple(
            (path, "v3" if path == "fit_execution_evidence.csv" else "v1")
            for path in (
                "recovery_gate_config.json",
                "runtime_projection.json",
                "source_provenance.json",
                "holdout_manifest.json",
                "model_parameter_contract.csv",
                "scenario_definitions.csv",
                "fit_execution_evidence.csv",
                "replicate_recovery.csv",
                "coverage_calibration.csv",
                "latent_time_calibration.csv",
                "predictive_replicate_diagnostics.csv",
                "predictive_check_summary.csv",
                "identifiability_profiles.csv",
                "control_decision_summary.csv",
                "verification.json",
                "report.md",
                "visuals/parameter_recovery.svg",
                "visuals/coverage_calibration.svg",
                "visuals/latent_time_calibration.svg",
                "visuals/identifiability_profiles.svg",
                "visuals/control_comparison.svg",
                "visuals/review_montage.svg",
            )
        )
        == core.ARTIFACT_SCHEMA_VERSIONS
    )
    scenario_rows = tuple(asdict(row) for row in core.SCENARIO_DEFINITIONS)
    assert len(core.validate_scenario_definition_rows(scenario_rows)) == 11
    with pytest.raises(ValueError, match=r"scenario definitions|literal"):
        core.validate_scenario_definition_rows(scenario_rows[::-1])
    parameter_rows = tuple(
        {
            name: (
                "identified"
                if name in {"structural_status", "practical_status"}
                else authority[name]
            )
            for name in core.MODEL_PARAMETER_CONTRACT_HEADER
        }
        for authority in core.CONFIG_PARAMETER_ROWS
    )
    assert len(core.validate_model_parameter_contract_rows(parameter_rows)) == 5
    with pytest.raises(ValueError, match=r"parameter|authority"):
        core.validate_model_parameter_contract_rows(
            (parameter_rows[0] | {"generating_value": -5.0}, *parameter_rows[1:])
        )
    report = "\n".join(f"[{path}]({path})" for path in core.REPORT_REQUIRED_LINKS)
    core.validate_report_links(report)
    with pytest.raises(ValueError, match="report links"):
        core.validate_report_links("\n".join(report.splitlines()[:-1]))
    core.validate_visual_source_tables(EXPECTED_VISUAL_SOURCE_TABLES)
    with pytest.raises(ValueError, match="visual source"):
        core.validate_visual_source_tables(EXPECTED_VISUAL_SOURCE_TABLES[:-1])
    with pytest.raises(ValueError):
        core.scenario_definition_bytes(core.SCENARIO_DEFINITIONS[::-1])
    repo_root = Path(__file__).resolve().parents[1]
    goal = (repo_root / core.GOAL_DIRECTORY / "Goal.md").read_bytes()
    spec = (repo_root / core.AUTHORITATIVE_SPEC_RELATIVE_PATH).read_bytes()
    marker = b"## Objective"
    assert goal[goal.index(marker) :] == spec[spec.index(marker) :]
    body = goal[goal.index(marker) :].decode("utf-8")
    assert "Existing types and nullability stay unchanged" not in body
    for header in (
        core.MODEL_PARAMETER_CONTRACT_HEADER,
        core.REPLICATE_RECOVERY_HEADER,
        core.COVERAGE_CALIBRATION_HEADER,
        core.LATENT_TIME_CALIBRATION_HEADER,
        core.PREDICTIVE_REPLICATE_DIAGNOSTICS_HEADER,
        core.PREDICTIVE_CHECK_SUMMARY_HEADER,
        core.IDENTIFIABILITY_PROFILES_HEADER,
    ):
        assert ",".join(header) in body
    for required_clause in (
        "Literal enum domains shared by these tables",
        "structurally nullable",
        "zero-driver decision reads these",
        "canonical emitted rows",
        core.ACCEPTED_SOURCE_RECEIPT_FILE_SHA256,
        "git write-tree",
        "module-issued temporary fixture root",
        "Scenario/parameter truth authority",
        "schema_version = v1",
        "goal023-holdout-v1",
        "gate_family = process_oracle|observation_oracle|dense_joint",
        "Report links and visual sources",
    ):
        assert required_clause in body
    runbook = (repo_root / core.GOAL_DIRECTORY / "Runbook.md").read_text("utf-8")
    bash_blocks = re.findall(r"```bash\n(.*?)```", runbook, re.DOTALL)
    assert len(bash_blocks) == 18
    assert all("Immediately before `freeze-tracked-state`" not in block for block in bash_blocks)
    assert "Immediately before `freeze-tracked-state`" in runbook
    for block in bash_blocks:
        result = subprocess.run(("bash", "-n"), input=block, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
    exact_names = {
        "test_config_emission_fails_closed_on_identity_or_footprint_mismatch",
        "test_freeze_fails_closed_on_identity_or_footprint_mismatch",
        "test_holdout_pre_receipt_guard_fails_before_receipt_and_rng",
        "test_holdout_post_receipt_guard_failure_burns_namespace_before_rng",
        "test_holdout_success_freezes_represented_and_complete_artifact_snapshots",
        "test_holdout_and_artifact_generating_commands_are_never_retryable",
        "test_allowed_new_candidate_paths_are_hashed_but_extra_untracked_path_fails",
        "test_exact_staging_changes_only_predeclared_index_blobs",
        "test_authorized_commit_merge_and_push_transitions_are_literal",
        "test_candidate_footprint_presence_vector_is_phase_specific",
        "test_supersession_record_preserves_log_target_and_binds_live_parent",
        "test_holdout_receipt_exposure_fields_self_hash_and_later_invalidation_are_immutable",
        "test_task6_validation_dispatch_is_postholdout_only",
        "test_terminal_attestation_is_exactly_reviewed_appended_and_staged_once",
        "test_potentially_mutating_hooks_are_noops_before_freeze",
    }
    selected = tuple(
        name
        for name, value in globals().items()
        if callable(value)
        and (
            name.startswith(
                (
                    "test_lro_3a_",
                    "test_lro_3l_",
                    "test_lro_3d_",
                    "test_lro_3r_",
                    "test_lro_3s_",
                    "test_post_exposure_",
                )
            )
            or name in exact_names
        )
    )
    assert len(AMENDMENT_TEST_NAMES) == len(set(AMENDMENT_TEST_NAMES)) == 98
    assert selected == AMENDMENT_TEST_NAMES


def test_lro_3s_010_two_fixture_bundles_are_byte_identical(tmp_path: Any) -> None:
    core = _core()
    repo_root = Path(__file__).resolve().parents[1]
    canonical = repo_root / core.CANONICAL_ARTIFACT_RELATIVE_PATH
    alias = tmp_path / "canonical-alias"
    alias.symlink_to(canonical, target_is_directory=True)
    for forbidden in (canonical, alias):
        with pytest.raises(ValueError, match="canonical artifact"):
            core.issue_temporary_fixture_root(forbidden, repo_root=repo_root)
    assert not canonical.exists()
    raw_output = tmp_path / "raw-output"
    with pytest.raises(TypeError, match="module-issued"):
        core.emit_fixture_bundle(raw_output, task_results=(), workers=1)
    assert not raw_output.exists()

    first = core.issue_temporary_fixture_root(tmp_path / "first", repo_root=repo_root)
    second = core.issue_temporary_fixture_root(tmp_path / "second", repo_root=repo_root)
    core.emit_fixture_bundle(
        first, task_results=({"task_id": "b", "value": 2}, {"task_id": "a", "value": 1}), workers=1
    )
    core.emit_fixture_bundle(
        second, task_results=({"task_id": "a", "value": 1}, {"task_id": "b", "value": 2}), workers=8
    )
    assert core.artifact_snapshot(first.path).entries == core.artifact_snapshot(second.path).entries


def _envelope(core: Any, *, repo_root: Path | None = None, **updates: object) -> Any:
    root = (repo_root or Path("/tmp/goal023-envelope")).resolve()
    log_relative = f"{core.GOAL_DIRECTORY}/Log.md"
    values = {
        "repo_root": root,
        "branch": core.PINNED_BRANCH,
        "head": core.PINNED_COMMIT,
        "base": core.PINNED_COMMIT,
        "tracked": (("Goal.md", "a" * 64),),
        "staged": (("Goal.md", "a" * 40), (log_relative, "3" * 40)),
        "unstaged": (),
        "untracked": (),
        "status_entries": (("M ", "Goal.md"), ("M ", log_relative)),
        "cached_entries": (("Goal.md", "a" * 40), (log_relative, "3" * 40)),
        "analytical_entries": (("Goal.md", "a" * 64),),
        "candidate_entries": (("Goal.md", "a" * 64),),
        "log_bytes": b"parent\n",
        "preholdout_receipt_file_sha256": "b" * 64,
        "receipt_sha256": "c" * 64,
        "holdout_receipt_file_sha256": "d" * 64,
        "config_sha256": "e" * 64,
        "config_file_sha256": "f" * 64,
        "represented_artifact_set_sha256": "1" * 64,
        "artifact_set_sha256": "2" * 64,
    }
    values.update(updates)
    return core.ProvenanceEnvelope(**values)


def _reviewed_retry_transition(core: Any, failure: Any) -> tuple[Any, Any]:
    suffix = core.retry_review_log_payload(failure)
    after = replace(failure.after, log_bytes=failure.after.log_bytes + suffix)
    transition = core.validate_post_exposure_log_append(
        failure.after,
        after,
        approved_suffix=suffix,
    )
    return transition, after


def test_post_exposure_log_append_accepts_exact_provenance_suffix_and_parent() -> None:
    core = _core()
    before = _envelope(core)
    suffix = core.post_exposure_log_payload(
        before,
        record_type="provenance_review",
        disposition="REVIEW_PENDING",
    )
    after = _envelope(core, log_bytes=before.log_bytes + suffix)
    transition = core.validate_post_exposure_log_append(before, after, approved_suffix=suffix)
    assert transition.before == before and transition.after == after
    assert transition.payload["config_file_sha256"] == before.config_file_sha256
    arbitrary = b'{"analytical_payload":false}\n'
    with pytest.raises(ValueError, match="complete envelope"):
        core.validate_post_exposure_log_append(
            before,
            _envelope(core, log_bytes=before.log_bytes + arbitrary),
            approved_suffix=arbitrary,
        )


def test_post_exposure_log_append_rejects_prefix_change_or_analytical_payload() -> None:
    core = _core()
    before = _envelope(core)
    approved = core.post_exposure_log_payload(
        before,
        record_type="provenance_review",
        disposition="REVIEW_PENDING",
    )
    analytical_document = json.loads(approved)
    analytical_document["analytical_payload"] = True
    analytical = core.canonical_json_bytes(analytical_document)
    for after, suffix in (
        (_envelope(core, log_bytes=b"changed\n"), approved),
        (_envelope(core, log_bytes=before.log_bytes + b"wrong\n"), approved),
        (_envelope(core, log_bytes=before.log_bytes + analytical), analytical),
    ):
        with pytest.raises(ValueError):
            core.validate_post_exposure_log_append(before, after, approved_suffix=suffix)


def test_post_exposure_zero_exit_requires_complete_unchanged_envelope() -> None:
    core = _core()
    before = _envelope(core)
    assert (
        core.classify_post_exposure_command(before, before, exit_code=0)
        == "CONTINUE_FROZEN_CANDIDATE"
    )
    assert (
        core.classify_post_exposure_command(
            before, _envelope(core, config_sha256="0" * 64), exit_code=0
        )
        == "STOP_INVALIDATED_POST_EXPOSURE"
    )


def test_post_exposure_nonzero_without_mutation_allows_one_approved_exact_retry() -> None:
    core = _core()
    before = _envelope(core)
    valid_command = EXPECTED_NON_GENERATIVE_COMMANDS[4]
    pending = core.classify_post_exposure_command(before, before, exit_code=1)
    assert pending == "STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION"
    failure = core.record_validation_failure(valid_command, before, before, exit_code=1)
    transition, current = _reviewed_retry_transition(core, failure)
    assert (
        core.authorize_retry(
            failure=failure,
            command=valid_command,
            capture_envelope=lambda: current,
            reviewed_log_transition=transition,
        )
        == valid_command
    )
    mutated_current = replace(current, config_file_sha256="0" * 64)
    with pytest.raises(ValueError, match="current envelope"):
        core.authorize_retry(
            failure=failure,
            command=valid_command,
            capture_envelope=lambda: mutated_current,
            reviewed_log_transition=transition,
        )
    exact_failure = core.record_validation_failure(
        EXPECTED_NON_GENERATIVE_COMMANDS[1], before, before, exit_code=1
    )
    exact_transition, exact_current = _reviewed_retry_transition(core, exact_failure)
    with pytest.raises(ValueError, match="exact"):
        core.authorize_retry(
            failure=exact_failure,
            command=EXPECTED_NON_GENERATIVE_COMMANDS[2],
            capture_envelope=lambda: exact_current,
            reviewed_log_transition=exact_transition,
        )
    opaque = ("python", "-c", "open('/tmp/forbidden-output','w').write('x')")
    with pytest.raises(ValueError, match=r"registered|non.generative|command"):
        core.record_validation_failure(opaque, before, before, exit_code=1)


def test_post_exposure_second_nonmutating_nonzero_stops_without_invalidation() -> None:
    core = _core()
    before = _envelope(core)
    assert core.classify_post_exposure_command(before, before, exit_code=1, retry_count=1) == (
        "STOP_NONMUTATING_VALIDATION_FAILURE"
    )
    failure = core.record_validation_failure(
        EXPECTED_NON_GENERATIVE_COMMANDS[4],
        before,
        before,
        exit_code=1,
        retry_count=1,
    )
    transition, current = _reviewed_retry_transition(core, failure)
    with pytest.raises(ValueError):
        core.authorize_retry(
            failure=failure,
            command=EXPECTED_NON_GENERATIVE_COMMANDS[4],
            capture_envelope=lambda: current,
            reviewed_log_transition=transition,
        )


def test_post_exposure_mutation_invalidates_for_zero_or_nonzero_exit() -> None:
    core = _core()
    before = _envelope(core)
    after = _envelope(core, artifact_set_sha256="9" * 64)
    for exit_code in (0, 1):
        assert core.classify_post_exposure_command(before, after, exit_code=exit_code) == (
            "STOP_INVALIDATED_POST_EXPOSURE"
        )


def test_post_exposure_guard_detects_each_immutable_byte_class() -> None:
    core = _core()
    before = _envelope(core)
    mutations = {
        "repo_root": Path("/tmp/other-goal023-envelope"),
        "branch": "wrong",
        "head": "0" * 40,
        "base": "1" * 40,
        "tracked": (("Goal.md", "0" * 64),),
        "staged": (("Goal.md", "0" * 40),),
        "unstaged": ("Goal.md",),
        "untracked": ("extra",),
        "status_entries": ((" M", "Goal.md"),),
        "cached_entries": (("Goal.md", "0" * 40),),
        "analytical_entries": (("Goal.md", "0" * 64),),
        "candidate_entries": (("extra", "0" * 64),),
        "log_bytes": b"changed",
        "preholdout_receipt_file_sha256": "0" * 64,
        "receipt_sha256": "0" * 64,
        "holdout_receipt_file_sha256": "0" * 64,
        "config_sha256": "0" * 64,
        "config_file_sha256": "0" * 64,
        "represented_artifact_set_sha256": "0" * 64,
        "artifact_set_sha256": "0" * 64,
    }
    assert set(mutations) == set(before.__dataclass_fields__)
    for field, value in mutations.items():
        after = replace(before, **{field: value})
        assert core.envelope_changes(before, after) == (field,)


def test_post_exposure_guard_wraps_each_command_not_batch() -> None:
    core = _core()
    before = _envelope(core)
    mutated = _envelope(core, config_file_sha256="0" * 64)
    with pytest.raises(ValueError, match="command 1"):
        core.run_guarded_command_sequence(before, ((0, mutated), (0, before)))


def test_config_emission_fails_closed_on_identity_or_footprint_mismatch(
    tmp_path: Any, monkeypatch: Any
) -> None:
    core = _core()
    for index, mutation in enumerate(("branch", "head", "base", "unknown", "status", "manifest")):
        root = tmp_path / str(index)
        guard, state = _phase_tree(core, root, "config_emission")
        output = root / "artifacts" / "config.json"
        _mutate_phase_state(core, root, state, mutation)
        with pytest.raises(ValueError):
            core.guard_config_emission(
                guard,
                output,
                payload=_valid_config_payload(core, tracked_state_sha256=guard.analytical_sha256),
            )
        assert not output.exists()
    root = tmp_path / "post-create"
    guard, _ = _phase_tree(core, root, "config_emission")
    output = tmp_path / "post-create-config.json"
    real_loader = core.load_frozen_config_identity

    def reject_after_create(path: Path) -> Any:
        real_loader(path)
        raise ValueError("injected post-create verification failure")

    monkeypatch.setattr(core, "load_frozen_config_identity", reject_after_create)
    with pytest.raises(
        ValueError, match="STOP_INVALIDATED_POST_CREATE_IMMUTABLE_CONFIG"
    ) as stopped:
        core.guard_config_emission(
            guard,
            output,
            payload=_valid_config_payload(core, tracked_state_sha256=guard.analytical_sha256),
        )
    assert cast(Any, stopped.value).disposition == ("STOP_INVALIDATED_POST_CREATE_IMMUTABLE_CONFIG")
    preserved = output.read_bytes()
    assert preserved
    with pytest.raises(FileExistsError):
        core.guard_config_emission(
            guard,
            output,
            payload=_valid_config_payload(core, tracked_state_sha256=guard.analytical_sha256),
        )
    assert output.read_bytes() == preserved
    monkeypatch.setattr(core, "load_frozen_config_identity", real_loader)


def test_freeze_fails_closed_on_identity_or_footprint_mismatch(
    tmp_path: Any, monkeypatch: Any
) -> None:
    core = _core()
    for index, mutation in enumerate(("branch", "head", "base", "unknown", "status", "manifest")):
        root = tmp_path / f"repo-{index}"
        guard, state = _phase_tree(core, root, "pre_freeze")
        config_path = tmp_path / f"config-{index}.json"
        core.write_canonical_config(
            config_path,
            _valid_config_payload(core, tracked_state_sha256=guard.analytical_sha256),
        )
        config = core.load_frozen_config_identity(config_path)
        original = config_path.read_bytes()
        receipt = tmp_path / f"preholdout-{index}.json"
        _mutate_phase_state(core, root, state, mutation)
        with pytest.raises(ValueError):
            core.guard_freeze(guard, config, receipt)
        assert config_path.read_bytes() == original and not receipt.exists()
    for field in ("spec_sha256", "source_sha256"):
        root = tmp_path / f"false-freeze-{field}"
        guard, _ = _phase_tree(core, root, "pre_freeze")
        config_path = tmp_path / f"false-freeze-{field}-config.json"
        payload = _valid_config_payload(core, tracked_state_sha256=guard.analytical_sha256) | {
            field: "0" * 64
        }
        core.write_canonical_config(config_path, payload)
        receipt = tmp_path / f"false-freeze-{field}-receipt.json"
        with pytest.raises(ValueError, match="live authority"):
            core.guard_freeze(
                guard,
                core.load_frozen_config_identity(config_path),
                receipt,
            )
        assert not receipt.exists()
    root = tmp_path / "freeze-post-create"
    guard, _ = _phase_tree(core, root, "pre_freeze")
    config_path = tmp_path / "freeze-post-create-config.json"
    core.write_canonical_config(
        config_path,
        _valid_config_payload(core, tracked_state_sha256=guard.analytical_sha256),
    )
    receipt = tmp_path / "freeze-post-create-receipt.json"
    real_loader = core.load_receipt_file_identity

    def reject_after_create(path: Path) -> Any:
        real_loader(path)
        raise ValueError("injected preholdout post-create failure")

    monkeypatch.setattr(core, "load_receipt_file_identity", reject_after_create)
    with pytest.raises(
        ValueError,
        match="STOP_INVALIDATED_POST_CREATE_IMMUTABLE_PREHOLDOUT_RECEIPT",
    ) as stopped:
        core.guard_freeze(
            guard,
            core.load_frozen_config_identity(config_path),
            receipt,
        )
    assert cast(Any, stopped.value).disposition == (
        "STOP_INVALIDATED_POST_CREATE_IMMUTABLE_PREHOLDOUT_RECEIPT"
    )
    assert receipt.read_bytes()
    monkeypatch.setattr(core, "load_receipt_file_identity", real_loader)


def test_holdout_pre_receipt_guard_fails_before_receipt_and_rng(
    tmp_path: Any, monkeypatch: Any
) -> None:
    core = _core()
    calls: list[str] = []
    root = tmp_path / "repo"
    initial_guard, state = _phase_tree(core, root, "pre_receipt")
    config_path = tmp_path / "config.json"
    core.write_canonical_config(
        config_path,
        _valid_config_payload(core, tracked_state_sha256=initial_guard.analytical_sha256),
    )
    config = core.load_frozen_config_identity(config_path)
    preholdout_path = root / core.PUBLICATION_PATHS[-2]
    preholdout_path.write_bytes(
        core.canonical_json_bytes(_preholdout_payload_for_guard(config, initial_guard))
    )
    guard = core.capture_phase_guard(root, "pre_receipt", git_runner=initial_guard.git_runner)
    preholdout = core.load_receipt_file_identity(preholdout_path)
    receipt = root / core.PUBLICATION_PATHS[-1]
    state["base"] = "wrong"
    with pytest.raises(ValueError):
        core.guard_holdout_pre_receipt(
            guard,
            receipt,
            config=config,
            preholdout_receipt=preholdout,
            receipt_payload=_holdout_receipt_payload(core, config),
            rng_factory=lambda: calls.append("rng"),
        )
    assert not receipt.exists() and calls == []
    state["base"] = core.PINNED_COMMIT
    guard = core.capture_phase_guard(root, "pre_receipt", git_runner=guard.git_runner)
    with pytest.raises(ValueError, match=r"schema|receipt"):
        core.guard_holdout_pre_receipt(
            guard,
            receipt,
            config=config,
            preholdout_receipt=preholdout,
            receipt_payload={"exposed": True},
            rng_factory=lambda: calls.append("rng"),
        )
    assert not receipt.exists() and calls == []
    for field in ("spec_sha256", "source_sha256"):
        authority_root = tmp_path / f"false-authority-{field}"
        authority_initial, _ = _phase_tree(core, authority_root, "pre_receipt")
        authority_config_path = tmp_path / f"false-authority-{field}-config.json"
        authority_payload = _valid_config_payload(
            core, tracked_state_sha256=authority_initial.analytical_sha256
        ) | {field: "0" * 64}
        core.write_canonical_config(authority_config_path, authority_payload)
        authority_config = core.load_frozen_config_identity(authority_config_path)
        authority_pre_path = authority_root / core.PUBLICATION_PATHS[-2]
        authority_pre_path.write_bytes(
            core.canonical_json_bytes(
                _preholdout_payload_for_guard(authority_config, authority_initial)
            )
        )
        authority_guard = core.capture_phase_guard(
            authority_root,
            "pre_receipt",
            git_runner=authority_initial.git_runner,
        )
        authority_pre = core.load_receipt_file_identity(authority_pre_path)
        authority_receipt = authority_root / core.PUBLICATION_PATHS[-1]
        with pytest.raises(ValueError, match="live authority"):
            core.guard_holdout_pre_receipt(
                authority_guard,
                authority_receipt,
                config=authority_config,
                preholdout_receipt=authority_pre,
                receipt_payload=_holdout_receipt_payload(core, authority_config),
                rng_factory=lambda: calls.append("rng"),
            )
        assert not authority_receipt.exists() and calls == []
    post_create_root = tmp_path / "holdout-post-create"
    post_create_initial, _ = _phase_tree(core, post_create_root, "pre_receipt")
    post_create_config_path = tmp_path / "holdout-post-create-config.json"
    core.write_canonical_config(
        post_create_config_path,
        _valid_config_payload(core, tracked_state_sha256=post_create_initial.analytical_sha256),
    )
    post_create_config = core.load_frozen_config_identity(post_create_config_path)
    post_create_pre_path = post_create_root / core.PUBLICATION_PATHS[-2]
    post_create_pre_path.write_bytes(
        core.canonical_json_bytes(
            _preholdout_payload_for_guard(post_create_config, post_create_initial)
        )
    )
    post_create_guard = core.capture_phase_guard(
        post_create_root,
        "pre_receipt",
        git_runner=post_create_initial.git_runner,
    )
    post_create_pre = core.load_receipt_file_identity(post_create_pre_path)
    post_create_receipt = post_create_root / core.PUBLICATION_PATHS[-1]
    real_holdout_loader = core.load_holdout_receipt_identity

    def reject_receipt_after_create(path: Path) -> Any:
        real_holdout_loader(path)
        raise ValueError("injected receipt post-create verification failure")

    monkeypatch.setattr(core, "load_holdout_receipt_identity", reject_receipt_after_create)
    with pytest.raises(
        ValueError,
        match="STOP_INVALIDATED_POST_CREATE_IMMUTABLE_HOLDOUT_RECEIPT",
    ) as stopped:
        core.guard_holdout_pre_receipt(
            post_create_guard,
            post_create_receipt,
            config=post_create_config,
            preholdout_receipt=post_create_pre,
            receipt_payload=_holdout_receipt_payload(core, post_create_config),
            rng_factory=lambda: calls.append("rng"),
        )
    assert cast(Any, stopped.value).disposition == (
        "STOP_INVALIDATED_POST_CREATE_IMMUTABLE_HOLDOUT_RECEIPT"
    )
    preserved_receipt = post_create_receipt.read_bytes()
    assert preserved_receipt and calls == []
    monkeypatch.setattr(core, "load_holdout_receipt_identity", real_holdout_loader)
    forged_config_path = tmp_path / "forged-config.json"
    core.write_canonical_config(forged_config_path, _valid_config_payload(core))
    forged_config = core.load_frozen_config_identity(forged_config_path)
    forged_pre_path = tmp_path / "forged-preholdout.json"
    forged_pre_path.write_bytes(core.canonical_json_bytes(_preholdout_payload(core, forged_config)))
    forged_preholdout = core.load_receipt_file_identity(forged_pre_path)
    assert forged_config.payload["tracked_state_sha256"] != guard.analytical_sha256
    with pytest.raises(ValueError, match="live captured"):
        core.guard_holdout_pre_receipt(
            guard,
            receipt,
            config=forged_config,
            preholdout_receipt=forged_preholdout,
            receipt_payload=_holdout_receipt_payload(core, forged_config),
            rng_factory=lambda: calls.append("rng"),
        )
    assert not receipt.exists() and calls == []
    receipt.write_bytes(b"existing\n")
    with pytest.raises((FileExistsError, ValueError)):
        core.guard_holdout_pre_receipt(
            guard,
            receipt,
            config=config,
            preholdout_receipt=preholdout,
            receipt_payload=_holdout_receipt_payload(core, config),
            rng_factory=lambda: calls.append("rng"),
        )
    assert receipt.read_bytes() == b"existing\n" and calls == []
    for index, mutation in enumerate(("branch", "head", "base", "unknown", "status", "manifest")):
        case_root = tmp_path / f"case-{index}"
        case_guard, case_state = _phase_tree(core, case_root, "pre_receipt")
        case_config_path = tmp_path / f"case-config-{index}.json"
        core.write_canonical_config(
            case_config_path,
            _valid_config_payload(core, tracked_state_sha256=case_guard.analytical_sha256),
        )
        case_config = core.load_frozen_config_identity(case_config_path)
        case_pre_path = case_root / core.PUBLICATION_PATHS[-2]
        case_pre_path.write_bytes(
            core.canonical_json_bytes(_preholdout_payload_for_guard(case_config, case_guard))
        )
        case_guard = core.capture_phase_guard(
            case_root, "pre_receipt", git_runner=case_guard.git_runner
        )
        case_pre = core.load_receipt_file_identity(case_pre_path)
        case_receipt = case_root / core.PUBLICATION_PATHS[-1]
        _mutate_phase_state(core, case_root, case_state, mutation)
        with pytest.raises(ValueError):
            core.guard_holdout_pre_receipt(
                case_guard,
                case_receipt,
                config=case_config,
                preholdout_receipt=case_pre,
                receipt_payload=_holdout_receipt_payload(core, case_config),
                rng_factory=lambda: calls.append("rng"),
            )
        assert not case_receipt.exists() and calls == []


def test_holdout_post_receipt_guard_failure_burns_namespace_before_rng(tmp_path: Any) -> None:
    core = _core()
    calls: list[str] = []
    for field in ("spec_sha256", "source_sha256"):
        authority_root = tmp_path / f"post-false-{field}"
        authority_initial, _ = _phase_tree(core, authority_root, "post_receipt")
        authority_config_path = tmp_path / f"post-false-{field}-config.json"
        authority_payload = _valid_config_payload(
            core, tracked_state_sha256=authority_initial.analytical_sha256
        ) | {field: "0" * 64}
        core.write_canonical_config(authority_config_path, authority_payload)
        authority_config = core.load_frozen_config_identity(authority_config_path)
        authority_pre_path = authority_root / core.PUBLICATION_PATHS[-2]
        authority_pre_path.write_bytes(
            core.canonical_json_bytes(
                _preholdout_payload_for_guard(authority_config, authority_initial)
            )
        )
        authority_receipt_path = authority_root / core.PUBLICATION_PATHS[-1]
        core.write_canonical_receipt(
            authority_receipt_path,
            _holdout_receipt_payload(core, authority_config),
        )
        authority_guard = core.capture_phase_guard(
            authority_root,
            "post_receipt",
            git_runner=authority_initial.git_runner,
        )
        assert (
            core.guard_holdout_post_receipt(
                authority_guard,
                authority_receipt_path,
                config=authority_config,
                preholdout_receipt=core.load_receipt_file_identity(authority_pre_path),
                rng_factory=lambda: calls.append("rng"),
            )
            == "STOP_INVALIDATED_POST_EXPOSURE"
        )
        assert calls == []
    root = tmp_path / "repo"
    initial_guard, _ = _phase_tree(core, root, "post_receipt")
    config_path = tmp_path / "config.json"
    core.write_canonical_config(
        config_path,
        _valid_config_payload(core, tracked_state_sha256=initial_guard.analytical_sha256),
    )
    config = core.load_frozen_config_identity(config_path)
    preholdout_path = root / core.PUBLICATION_PATHS[-2]
    preholdout_path.write_bytes(
        core.canonical_json_bytes(_preholdout_payload_for_guard(config, initial_guard))
    )
    preholdout = core.load_receipt_file_identity(preholdout_path)
    receipt = root / core.PUBLICATION_PATHS[-1]
    core.write_canonical_receipt(receipt, _holdout_receipt_payload(core, config))
    guard = core.capture_phase_guard(root, "post_receipt", git_runner=initial_guard.git_runner)
    receipt.write_bytes(b"not a receipt\n")
    result = core.guard_holdout_post_receipt(
        guard,
        receipt,
        config=config,
        preholdout_receipt=preholdout,
        rng_factory=lambda: calls.append("rng"),
    )
    assert result == "STOP_INVALIDATED_POST_EXPOSURE" and calls == []
    forged_root = tmp_path / "forged-repo"
    forged_initial, _ = _phase_tree(core, forged_root, "post_receipt")
    forged_config_path = tmp_path / "forged-config.json"
    core.write_canonical_config(forged_config_path, _valid_config_payload(core))
    forged_config = core.load_frozen_config_identity(forged_config_path)
    forged_pre_path = forged_root / core.PUBLICATION_PATHS[-2]
    forged_pre_path.write_bytes(core.canonical_json_bytes(_preholdout_payload(core, forged_config)))
    forged_pre = core.load_receipt_file_identity(forged_pre_path)
    forged_receipt = forged_root / core.PUBLICATION_PATHS[-1]
    core.write_canonical_receipt(forged_receipt, _holdout_receipt_payload(core, forged_config))
    forged_guard = core.capture_phase_guard(
        forged_root, "post_receipt", git_runner=forged_initial.git_runner
    )
    assert forged_guard.analytical_sha256 != forged_config.payload["tracked_state_sha256"]
    result = core.guard_holdout_post_receipt(
        forged_guard,
        forged_receipt,
        config=forged_config,
        preholdout_receipt=forged_pre,
        rng_factory=lambda: calls.append("rng"),
    )
    assert result == "STOP_INVALIDATED_POST_EXPOSURE" and calls == []
    core.write_canonical_receipt(receipt, _holdout_receipt_payload(core, config))
    guard = core.capture_phase_guard(root, "post_receipt", git_runner=guard.git_runner)
    other_config_path = tmp_path / "other-config.json"
    other_payload = _valid_config_payload(
        core, tracked_state_sha256=initial_guard.analytical_sha256
    ) | {"source_sha256": "9" * 64}
    core.write_canonical_config(other_config_path, other_payload)
    other_config = core.load_frozen_config_identity(other_config_path)
    result = core.guard_holdout_post_receipt(
        guard,
        receipt,
        config=other_config,
        preholdout_receipt=preholdout,
        rng_factory=lambda: calls.append("rng"),
    )
    assert result == "STOP_INVALIDATED_POST_EXPOSURE" and calls == []


def test_holdout_success_freezes_represented_and_complete_artifact_snapshots(tmp_path: Any) -> None:
    core = _core()
    root = core.issue_temporary_fixture_root(
        tmp_path / "bundle", repo_root=Path(__file__).resolve().parents[1]
    )
    core.emit_fixture_bundle(root, task_results=(), workers=1)
    represented, complete = core.freeze_artifact_snapshots(root.path)
    assert len(represented["entries"]) == 21 and len(complete.entries) == 22


def test_holdout_and_artifact_generating_commands_are_never_retryable() -> None:
    core = _core()
    before = _envelope(core)
    for command in (("run", "--phase", "holdout"), ("write", "artifact")):
        with pytest.raises(ValueError, match=r"registered|non.generative|command"):
            core.record_validation_failure(command, before, before, exit_code=1)


def test_allowed_new_candidate_paths_are_hashed_but_extra_untracked_path_fails(
    tmp_path: Any,
) -> None:
    core = _core()
    fixture, state = _phase_tree(core, tmp_path, "config_emission")
    core.validate_phase_guard(fixture)
    assert all(len(digest) == 64 for _, _, digest in fixture.candidate_entries)
    state["status"] += "?? extra.tmp\n"
    with pytest.raises(ValueError, match="unknown footprint"):
        core.validate_phase_guard(fixture)


def test_exact_staging_changes_only_predeclared_index_blobs(tmp_path: Any) -> None:
    core = _core()
    (tmp_path / ".git" / "objects").mkdir(parents=True)
    blobs = {path: sha256(path.encode()).hexdigest()[:40] for path in core.STAGING_PATHS}
    write_tree = "e" * 40

    def capture(
        *,
        staged_paths: tuple[str, ...],
        blob_map: dict[str, str] = blobs,
        status_paths: tuple[str, ...] = core.STAGING_PATHS,
    ) -> Any:
        def git_runner(command: tuple[str, ...]) -> str:
            if command == ("rev-parse", "--git-common-dir"):
                return ".git\n"
            if command == ("branch", "--show-current"):
                return f"{core.PINNED_BRANCH}\n"
            if command == ("rev-parse", "HEAD"):
                return f"{core.PINNED_COMMIT}\n"
            if command[0] == "status":
                return "".join(
                    f"{'A ' if path in staged_paths else '??'} {path}\n" for path in status_paths
                )
            if command[0] == "hash-object":
                return f"{blob_map[command[-1]]}\n"
            if command[0] == "diff":
                return "".join(f"{path}\n" for path in staged_paths)
            if command[0] == "rev-parse" and command[1].startswith(":"):
                return f"{blob_map[command[1][1:]]}\n"
            if command == ("write-tree",):
                return f"{write_tree}\n"
            raise AssertionError(command)

        return core.capture_staging_state(tmp_path, git_runner=git_runner)

    before = capture(staged_paths=())
    after = capture(staged_paths=core.STAGING_PATHS)
    validated = core.validate_exact_staging(before, after)
    assert validated.write_tree == write_tree
    with pytest.raises(ValueError, match="allowlist"):
        capture(staged_paths=(), status_paths=(*core.STAGING_PATHS, "outside.txt"))
    changed = dict(blobs)
    changed[core.STAGING_PATHS[0]] = "f" * 40
    with pytest.raises(ValueError, match="worktree"):
        core.validate_exact_staging(
            before, capture(staged_paths=core.STAGING_PATHS, blob_map=changed)
        )
    with pytest.raises(ValueError, match=r"live|blob"):
        capture(
            staged_paths=core.STAGING_PATHS,
            blob_map={path: "0" * 40 for path in core.STAGING_PATHS},
        )


def test_authorized_commit_merge_and_push_transitions_are_literal(tmp_path: Any) -> None:
    core = _core()
    remote = tmp_path / "remote.git"
    canonical = tmp_path / "canonical"
    goal_worktree = tmp_path / "goal-worktree"

    def run_git(root: Path | None, *argv: str) -> str:
        result = subprocess.run(
            ("git", *argv),
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout

    def runner(root: Path) -> Any:
        return lambda argv: run_git(root, *argv)

    run_git(None, "init", "--bare", str(remote))
    run_git(None, "init", "-b", "main", str(canonical))
    run_git(canonical, "config", "user.name", "Goal 023 Test")
    run_git(canonical, "config", "user.email", "goal023@example.invalid")
    run_git(canonical, "remote", "add", "origin", str(remote))
    for relative_path in core.STAGING_PATHS:
        path = canonical / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"base:{relative_path}\n", encoding="utf-8")
    run_git(canonical, "add", "--", *core.STAGING_PATHS)
    run_git(canonical, "commit", "-m", "base")
    run_git(canonical, "push", "-u", "origin", "main")
    base = run_git(canonical, "rev-parse", "HEAD").strip()
    run_git(
        canonical,
        "worktree",
        "add",
        "-b",
        core.PINNED_BRANCH,
        str(goal_worktree),
        "main",
    )
    for relative_path in core.STAGING_PATHS:
        path = goal_worktree / relative_path
        path.write_text(f"candidate:{relative_path}\n", encoding="utf-8")

    staging_before = core.capture_staging_state(goal_worktree, git_runner=runner(goal_worktree))
    run_git(goal_worktree, "add", "--", *core.STAGING_PATHS)
    staging_after = core.capture_staging_state(goal_worktree, git_runner=runner(goal_worktree))
    staging = core.validate_exact_staging(staging_before, staging_after)
    assert staging.repo_root == goal_worktree.resolve()

    commit_before = core.capture_publication_state(goal_worktree, git_runner=runner(goal_worktree))
    run_git(goal_worktree, "commit", "-m", "approved Goal 023 candidate")
    approved = run_git(goal_worktree, "rev-parse", "HEAD").strip()
    commit_after = core.capture_publication_state(goal_worktree, git_runner=runner(goal_worktree))
    assert core.validate_publication_transition(
        "commit",
        before=commit_before,
        after=commit_after,
        approved_commit=approved,
        staging=staging,
    )

    merge_before = core.capture_publication_state(canonical, git_runner=runner(canonical))
    run_git(canonical, "merge", "--ff-only", core.PINNED_BRANCH)
    merge_after = core.capture_publication_state(canonical, git_runner=runner(canonical))
    assert canonical.resolve() != goal_worktree.resolve()
    assert merge_before.common_git_dir == commit_before.common_git_dir
    assert core.validate_publication_transition(
        "merge",
        before=merge_before,
        after=merge_after,
        approved_commit=approved,
        staging=staging,
    )

    push_before = merge_after
    run_git(canonical, "push", "origin", "main")
    push_after = core.capture_publication_state(canonical, git_runner=runner(canonical))
    assert core.validate_publication_transition(
        "push",
        before=push_before,
        after=push_after,
        approved_commit=approved,
        staging=staging,
    )
    assert (push_after.head, push_after.local_main, push_after.remote_main) == (
        approved,
        approved,
        approved,
    )
    assert commit_after.parents == (base,)

    foreign_repository = replace(merge_before, common_git_dir=tmp_path / "foreign.git")
    with pytest.raises(ValueError, match=r"repository|object|transition"):
        core.validate_publication_transition(
            "merge",
            before=foreign_repository,
            after=merge_after,
            approved_commit=approved,
            staging=staging,
        )


def test_candidate_footprint_presence_vector_is_phase_specific(tmp_path: Any) -> None:
    core = _core()
    assert core.PHASE_PRESENCE_COUNTS == {"pre_freeze": 17, "pre_receipt": 18, "post_receipt": 19}
    for phase, count in core.PHASE_PRESENCE_COUNTS.items():
        fixture, _ = _phase_tree(core, tmp_path / phase, phase)
        assert len(fixture.present_paths) == count
        core.validate_phase_guard(fixture)


def test_supersession_record_preserves_log_target_and_binds_live_parent() -> None:
    core = _core()
    log_path = (
        Path(__file__).resolve().parents[1]
        / "docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Log.md"
    )
    parent = log_path.read_bytes()
    assert len(parent.splitlines()) >= 2222
    record = core.supersession_record(parent, target_lines=(2069, 2222))
    core.validate_supersession_record(parent, record, target_lines=(2069, 2222))
    assert b"superseded_pending_amendment" in record


def test_holdout_receipt_exposure_fields_self_hash_and_later_invalidation_are_immutable(
    tmp_path: Any,
) -> None:
    core = _core()
    config_path = tmp_path / "config.json"
    core.write_canonical_config(config_path, _valid_config_payload(core))
    config = core.load_frozen_config_identity(config_path)
    path = tmp_path / "holdout_receipt.json"
    core.write_canonical_receipt(path, _holdout_receipt_payload(core, config))
    identity = core.load_holdout_receipt_identity(path)
    path.write_bytes(path.read_bytes().replace(b"false", b"true "))
    with pytest.raises(ValueError):
        core.assert_receipt_immutable(identity, path)


def test_task6_validation_dispatch_is_postholdout_only() -> None:
    core = _core()
    assert tuple(spec.argv for spec in core.NON_GENERATIVE_COMMAND_REGISTRY) == (
        EXPECTED_NON_GENERATIVE_COMMANDS
    )
    for invalid_command in (
        ("run", "--phase", "calibration"),
        ("benchmark",),
        ("regenerate",),
    ):
        with pytest.raises(ValueError):
            core.validate_task6_command(invalid_command)
    for registered_command in EXPECTED_NON_GENERATIVE_COMMANDS:
        core.validate_task6_command(registered_command)
    with pytest.raises(ValueError, match=r"registered|command"):
        core.validate_task6_command(
            ("python", "-c", "open('/tmp/forbidden-output','w').write('x')")
        )


def test_terminal_attestation_is_exactly_reviewed_appended_and_staged_once(
    tmp_path: Any,
) -> None:
    core = _core()
    before = _envelope(core, repo_root=tmp_path)
    log_path = tmp_path / core.GOAL_DIRECTORY / "Log.md"
    log_path.parent.mkdir(parents=True)
    log_path.write_bytes(before.log_bytes)
    payload = core.terminal_attestation_payload(before)
    document = json.loads(payload)
    assert document["record_type"] == "terminal_attestation"
    assert document["repository_root"] == str(tmp_path.resolve())
    assert document["log_path"] == f"{core.GOAL_DIRECTORY}/Log.md"
    assert {
        "tracked",
        "staged",
        "unstaged",
        "untracked",
        "status_entries",
        "cached_entries",
        "analytical_entries",
        "candidate_entries",
    } <= set(document)
    state: dict[str, Any] = {"envelope": before}

    def capture() -> Any:
        return state["envelope"]

    def stage_log(path: Path) -> None:
        assert path == log_path
        digest = sha256(log_path.read_bytes()).hexdigest()[:40]
        state["envelope"] = replace(
            before,
            log_bytes=log_path.read_bytes(),
            staged=(("Goal.md", "a" * 40), (f"{core.GOAL_DIRECTORY}/Log.md", digest)),
            cached_entries=(
                ("Goal.md", "a" * 40),
                (f"{core.GOAL_DIRECTORY}/Log.md", digest),
            ),
        )

    after = core.apply_terminal_attestation(
        log_path,
        before,
        payload,
        reviewed_payload=payload,
        capture_envelope=capture,
        stage_log=stage_log,
    )
    assert after == state["envelope"]
    assert core.terminal_record_count(after.log_bytes) == 1
    with pytest.raises(ValueError, match=r"once|observed"):
        core.apply_terminal_attestation(
            log_path,
            before,
            payload,
            reviewed_payload=payload,
            capture_envelope=capture,
            stage_log=stage_log,
        )
    with pytest.raises(ValueError, match=r"terminal|once|recursive"):
        core.terminal_attestation_payload(after)
    arbitrary_log = tmp_path / "arbitrary.md"
    arbitrary_root = tmp_path / "arbitrary-root"
    arbitrary_before = _envelope(core, repo_root=arbitrary_root, log_bytes=b"arbitrary-parent\n")
    arbitrary_log.parent.mkdir(parents=True, exist_ok=True)
    arbitrary_log.write_bytes(arbitrary_before.log_bytes)
    arbitrary_payload = core.terminal_attestation_payload(arbitrary_before)
    arbitrary_state: dict[str, Any] = {"envelope": arbitrary_before}

    def stage_arbitrary(path: Path) -> None:
        digest = sha256(path.read_bytes()).hexdigest()[:40]
        arbitrary_state["envelope"] = replace(
            arbitrary_before,
            log_bytes=path.read_bytes(),
            staged=(
                ("Goal.md", "a" * 40),
                (f"{core.GOAL_DIRECTORY}/Log.md", digest),
            ),
            cached_entries=(
                ("Goal.md", "a" * 40),
                (f"{core.GOAL_DIRECTORY}/Log.md", digest),
            ),
        )

    with pytest.raises(ValueError, match=r"canonical|Log"):
        core.apply_terminal_attestation(
            arbitrary_log,
            arbitrary_before,
            arbitrary_payload,
            reviewed_payload=arbitrary_payload,
            capture_envelope=lambda: arbitrary_state["envelope"],
            stage_log=stage_arbitrary,
        )
    assert arbitrary_log.read_bytes() == arbitrary_before.log_bytes

    stopped_root = tmp_path / "stopped-root"
    stopped_before = _envelope(core, repo_root=stopped_root, log_bytes=b"stopped-parent\n")
    stopped_log = stopped_root / core.GOAL_DIRECTORY / "Log.md"
    stopped_log.parent.mkdir(parents=True)
    stopped_log.write_bytes(stopped_before.log_bytes)
    stopped_payload = core.terminal_attestation_payload(stopped_before)
    stopped_state: dict[str, Any] = {"envelope": stopped_before}

    def stage_with_foreign_change(path: Path) -> None:
        digest = sha256(path.read_bytes()).hexdigest()[:40]
        stopped_state["envelope"] = replace(
            stopped_before,
            log_bytes=path.read_bytes(),
            staged=(
                ("Goal.md", "a" * 40),
                (f"{core.GOAL_DIRECTORY}/Log.md", digest),
            ),
            cached_entries=(
                ("Goal.md", "a" * 40),
                (f"{core.GOAL_DIRECTORY}/Log.md", digest),
            ),
            candidate_entries=(("Goal.md", "0" * 64),),
        )

    with pytest.raises(core.ImmutableTerminalStop) as stopped:
        core.apply_terminal_attestation(
            stopped_log,
            stopped_before,
            stopped_payload,
            reviewed_payload=stopped_payload,
            capture_envelope=lambda: stopped_state["envelope"],
            stage_log=stage_with_foreign_change,
        )
    assert stopped.value.disposition == "STOP_INVALIDATED_TERMINAL_ATTESTATION_IMMUTABLE"
    assert core.terminal_record_count(stopped_log.read_bytes()) == 1
    with pytest.raises(ValueError, match=r"terminal|once"):
        core.terminal_attestation_payload(
            replace(stopped_state["envelope"], log_bytes=stopped_log.read_bytes())
        )


def test_potentially_mutating_hooks_are_noops_before_freeze() -> None:
    core = _core()
    before = _envelope(core)
    core.validate_prefreeze_hook_noop(before, before)
    with pytest.raises(ValueError, match="RED-GREEN"):
        core.validate_prefreeze_hook_noop(before, _envelope(core, staged=(("x", "y"),)))
