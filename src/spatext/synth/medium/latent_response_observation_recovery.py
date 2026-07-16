from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from functools import cache, lru_cache
from hashlib import sha256
from itertools import pairwise
from json import dumps, loads
from math import isfinite, sqrt
from pathlib import Path
from tempfile import gettempdir
from typing import Protocol, cast

import numpy as np
import scipy.optimize  # type: ignore[import-untyped]
from numpy.typing import NDArray
from scipy.special import gammaln, logsumexp  # type: ignore[import-untyped]
from scipy.stats import kstwo  # type: ignore[import-untyped]

from spatext.observe import (
    EffectiveCountRates,
    effort_scaled_mean,
    poisson_log_probability,
    state_count_log_probability,
)

type FloatArray = NDArray[np.float64]
type IntArray = NDArray[np.int64]
type BoolArray = NDArray[np.bool_]

MODEL_TIMES = tuple(range(0, 121, 6))
ALPHA_SUPPORT = (-10.0, -2.0)
BETA_DRIVER_SUPPORT = (-3.0, 3.0)
BETA_QUALITY_SUPPORT = (-2.0, 2.0)
LAMBDA_QUASI_SUPPORT = (0.01, 1.0)
LAMBDA_PRESENT_SUPPORT = (0.25, 10.0)
RATE_ORDER_GAP = 1e-9
COORDINATE_PROJECTION_TOLERANCE = 1e-12
START_DEDUPLICATION_TOLERANCE = 1e-10
AUDIT_CENTRAL_DIFFERENCE_FRACTION = 1e-5
NATURAL_PARAMETER_SUPPORT_WIDTHS = (8.0, 6.0, 4.0, 0.99, 9.75)
AUDIT_CENTRAL_DIFFERENCE_STEPS = (8e-5, 6e-5, 4e-5, 9.9e-6, 9.75e-5)
INVERSE_AUDIT_RMSE_THRESHOLD = 5e-5
INVERSE_AUDIT_DISTANCE_THRESHOLD = 0.01
INVERSE_AUDIT_REQUIRED_SUCCESSES = 12
PROFILE_LR_CUTOFF = 2.705543454095404
PROFILE_LR_DELTA_TOLERANCE = 1e-8 * (1.0 + PROFILE_LR_CUTOFF)
PROFILE_ROOT_TOLERANCE_FRACTION = 1e-5
PROFILE_ROOT_MAX_ITERATIONS = 100
PROFILE_STEP_FRACTION = 0.02
PROFILE_STEP_GROWTH = 1.6
PROFILE_MLE_INTERIOR_FRACTION = 0.01
MASTER_SEED = 20260711
PINNED_BRANCH = "codex/spatext-goal023-latent-response-observation-gate"
PINNED_COMMIT = "53462d0365babf2c8070714a930f69b4071af276"
ANALYTICAL_PATHS = (
    "AGENTS.md",
    "README.md",
    "docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Goal.md",
    "docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Plan.md",
    "docs/goals/023-synth-medium-latent-response-observation-recovery-gate/Runbook.md",
    "docs/goals/023-synth-medium-latent-response-observation-recovery-gate/source_digest_receipt.json",
    "pyproject.toml",
    "scripts/run_synth_medium_latent_response_observation_recovery.py",
    "spec/report_log.md",
    "spec/synth_medium_latent_response_observation_recovery_gate.md",
    "src/spatext/observe.py",
    "src/spatext/synth/medium/__init__.py",
    "src/spatext/synth/medium/latent_response_observation_recovery.py",
    "tests/test_observe.py",
    "tests/test_synth_medium_latent_response_observation_recovery.py",
    "uv.lock",
)
GOAL_DIRECTORY = "docs/goals/023-synth-medium-latent-response-observation-recovery-gate"
AUTHORITATIVE_SPEC_RELATIVE_PATH = "spec/synth_medium_latent_response_observation_recovery_gate.md"
SOURCE_RECEIPT_RELATIVE_PATH = f"{GOAL_DIRECTORY}/source_digest_receipt.json"
ACCEPTED_SOURCE_RECEIPT_FILE_SHA256 = (
    "5bfa92c88e04164c37abfeb0717d598d07885db7588963bcc3e2823af7f59ceb"
)
CANONICAL_ARTIFACT_RELATIVE_PATH = "artifacts/synth_medium_latent_response_observation_recovery"
CONFIG_SCHEMA_VERSION = "v1"
GENERATED_ARTIFACT_SCHEMA_VERSION = "v1"
PREHOLDOUT_RECEIPT_SCHEMA_VERSION = "v1"
HOLDOUT_RECEIPT_SCHEMA_VERSION = "v1"
HOLDOUT_SEED_NAMESPACE = "goal023-holdout-v1"
TERMINAL_RECORD_TYPE = "terminal_attestation"
PUBLICATION_PATHS = (
    *ANALYTICAL_PATHS,
    f"{GOAL_DIRECTORY}/Log.md",
    f"{GOAL_DIRECTORY}/preholdout_state_receipt.json",
    f"{GOAL_DIRECTORY}/holdout_receipt.json",
)
PHASE_PRESENCE_COUNTS = {"pre_freeze": 17, "pre_receipt": 18, "post_receipt": 19}

_HALTON_BASES = (2, 3, 5, 7, 11)
_OPTIMIZATION_COORDINATE_SUPPORTS = (
    ALPHA_SUPPORT,
    BETA_DRIVER_SUPPORT,
    BETA_QUALITY_SUPPORT,
    (0.0, 1.0),
    (0.0, 1.0),
)

RNG_PAYLOAD_KEYS = frozenset(
    {
        "goal",
        "master_seed",
        "scenario_id",
        "split",
        "replicate_index",
        "component",
        "draw_index",
    }
)

NESTED_SCENARIOS = (
    "process_oracle_observed_transition",
    "observation_oracle_fixed_transition",
    "dense_count_exact_model",
    "structured_imperfect_effort",
)
NONNESTED_SCENARIOS = (
    "sparse_expected_failure",
    "zero_driver_effect_negative_control",
    "permuted_arrival_alignment_stress",
    "no_emission_contrast_negative_control",
    "informative_dropout_misspecification_stress",
    "goal018_continuous_abundance_stress",
    "spatial_frailty_stress",
)
SCENARIO_IDS = NESTED_SCENARIOS + NONNESTED_SCENARIOS
RNG_COMPONENTS = (
    "schedule",
    "process",
    "observation",
    "dropout",
    "frailty",
    "predictive_reference",
    "bootstrap",
    "pit_randomization",
)

_MAX_CELL_ID = 6047
_MAX_INTERVAL_COUNT = 20
_ROW_BANDS = frozenset({"north_band", "middle_band", "south_band"})
_DRAW_COMPONENTS = frozenset({"predictive_reference", "bootstrap"})
_COUNT_SCENARIOS = frozenset(SCENARIO_IDS) - {"process_oracle_observed_transition"}
_DESIGN_CONDITION_LIMIT = 1e8
_OPTIMIZER_KINDS = frozenset({"process_oracle", "observation_oracle", "joint"})
FIT_FAILURE_CLASSES = (
    "preflight_or_input_failure",
    "potential_rank_gate_failure",
    "potential_condition_gate_failure",
    "optimizer_or_nonfinite_failure",
    "plugin_rank_gate_failure",
    "plugin_condition_gate_failure",
    "oracle_rank_gate_failure",
    "oracle_condition_gate_failure",
    "equal_rate_noninterior_failure",
)
FIT_FAILURE_TRANSITION_TABLE = (
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
_FROZEN_AUDIT_RECOVERY_COUNTS = {
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
_FROZEN_AUDIT_DIAGNOSTIC_ROWS = {
    "dense": 219450,
    "structured": 114950,
    "sparse": 15672,
}
_PARAMETER_SUPPORTS = {
    "alpha": ALPHA_SUPPORT,
    "beta_driver": BETA_DRIVER_SUPPORT,
    "beta_quality": BETA_QUALITY_SUPPORT,
    "lambda_quasi": LAMBDA_QUASI_SUPPORT,
    "lambda_present": LAMBDA_PRESENT_SUPPORT,
}
_FIT_PARAMETER_SUPPORTS = _PARAMETER_SUPPORTS | {"lambda_equal": (0.01, 10.0)}
_PROFILE_ROOT_TOLERANCES = {
    "alpha": 8e-5,
    "beta_driver": 6e-5,
    "beta_quality": 4e-5,
    "lambda_quasi": 9.9e-6,
    "lambda_present": 9.75e-5,
}
_OPTIMIZER_PARAMETER_NAMES = {
    "process_oracle": ("alpha", "beta_driver", "beta_quality"),
    "observation_oracle": ("lambda_quasi", "lambda_present"),
    "joint": (
        "alpha",
        "beta_driver",
        "beta_quality",
        "lambda_quasi",
        "lambda_present",
    ),
}


class ProcessRandomGenerator(Protocol):
    def random(
        self,
        *,
        size: tuple[int, int],
        dtype: type[np.float64],
    ) -> FloatArray: ...


class ObservationRandomGenerator(Protocol):
    def poisson(self, lam: FloatArray) -> IntArray: ...


class LikelihoodEvaluationError(ValueError):
    """Raised when an exact likelihood evaluation leaves the finite domain."""


class ProfileEvaluationError(ValueError):
    """Raised when a cached profile point cannot provide a finite root value."""


class _ProfileMaximumInvalidation(ProfileEvaluationError):
    pass


@dataclass(frozen=True, slots=True)
class OrderedRateFractions:
    """Validated unit-box coordinates for the ordered effective-rate map."""

    p_frac: float
    q_frac: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "p_frac", _canonical_unit_fraction(self.p_frac, "p_frac"))
        object.__setattr__(self, "q_frac", _canonical_unit_fraction(self.q_frac, "q_frac"))


@dataclass(frozen=True, slots=True)
class RngPayload:
    """Validated canonical substream identity for a non-holdout draw."""

    goal: str
    master_seed: int
    scenario_id: str
    split: str
    replicate_index: int
    component: str
    draw_index: int | None

    def __post_init__(self) -> None:
        _validate_rng_payload_fields(self)

    def as_dict(self) -> dict[str, object]:
        return {
            "goal": self.goal,
            "master_seed": self.master_seed,
            "scenario_id": self.scenario_id,
            "split": self.split,
            "replicate_index": self.replicate_index,
            "component": self.component,
            "draw_index": self.draw_index,
        }


@dataclass(frozen=True, slots=True)
class ScenarioScheduleDefinition:
    scenario_id: str
    schedule_id: str
    effort_rule: str


@dataclass(frozen=True, slots=True)
class DesignCell:
    """Truth-free canonical cell covariates used by schedules and diagnostics."""

    cell_id: int
    standardized_quality: float
    predator_arrival_time: float | None
    row_band: str

    def __post_init__(self) -> None:
        _validate_cell_id(self.cell_id)
        object.__setattr__(
            self,
            "standardized_quality",
            _canonical_standardized_quality(self.standardized_quality),
        )
        object.__setattr__(
            self,
            "predator_arrival_time",
            _canonical_arrival_time(self.predator_arrival_time),
        )
        if type(self.row_band) is not str or self.row_band not in _ROW_BANDS:
            raise ValueError("row_band must be north_band, middle_band, or south_band")


@dataclass(frozen=True, slots=True)
class ScheduledOpportunity:
    """One truth-independent opportunity in canonical cell-time order."""

    cell_id: int
    time: int
    effort: float
    standardized_quality: float
    predator_arrival_time: float | None

    def __post_init__(self) -> None:
        _validate_cell_id(self.cell_id)
        _validate_model_time(self.time)
        object.__setattr__(self, "effort", _canonical_effort(self.effort))
        object.__setattr__(
            self,
            "standardized_quality",
            _canonical_standardized_quality(self.standardized_quality),
        )
        object.__setattr__(
            self,
            "predator_arrival_time",
            _canonical_arrival_time(self.predator_arrival_time),
        )


@dataclass(frozen=True, slots=True)
class ProcessSimulationTruth:
    """Evaluator-only arrays from one fully consumed latent-process draw."""

    cell_ids: IntArray
    states: FloatArray
    transition_times: FloatArray

    def __post_init__(self) -> None:
        _validate_process_simulation_truth(self)
        object.__setattr__(self, "cell_ids", _immutable_int_array(self.cell_ids))
        object.__setattr__(self, "states", _immutable_float_array(self.states))
        object.__setattr__(
            self,
            "transition_times",
            _immutable_float_array(self.transition_times),
        )


@dataclass(frozen=True, slots=True)
class DesignDiagnostic:
    provenance: str
    role: str
    n_rows: int
    n_columns: int
    rank: int
    condition_number: float
    passed: bool
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        validate_design_diagnostic(self)


def validate_design_diagnostic(diagnostic: DesignDiagnostic) -> None:
    """Enforce the single rank/condition/pass algebra for typed diagnostics."""

    if type(diagnostic) is not DesignDiagnostic:
        raise TypeError("design diagnostic must be an exact DesignDiagnostic")
    if type(diagnostic.provenance) is not str or not diagnostic.provenance:
        raise ValueError("design provenance must be a nonempty string")
    if type(diagnostic.role) is not str or not diagnostic.role:
        raise ValueError("design role must be a nonempty string")
    if type(diagnostic.n_rows) is not int or diagnostic.n_rows <= 0:
        raise ValueError("design row dimension must be a positive integer")
    if type(diagnostic.n_columns) is not int or diagnostic.n_columns <= 0:
        raise ValueError("design column dimension must be a positive integer")
    if (
        type(diagnostic.rank) is not int
        or diagnostic.rank < 0
        or diagnostic.rank > min(diagnostic.n_rows, diagnostic.n_columns)
    ):
        raise ValueError("design rank must be an integer within its dimensions")
    condition = diagnostic.condition_number
    if type(condition) not in (int, float) or np.isnan(float(condition)):
        raise ValueError("design condition must be a builtin non-NaN number")
    full_rank = (
        diagnostic.n_rows >= diagnostic.n_columns and diagnostic.rank == diagnostic.n_columns
    )
    if full_rank:
        if not isfinite(float(condition)) or float(condition) < 1.0:
            raise ValueError("full-rank design condition must be finite and at least one")
    elif float(condition) != float("inf"):
        raise ValueError("rank-deficient design condition must be positive infinity")
    expected_pass = full_rank and float(condition) < _DESIGN_CONDITION_LIMIT
    if type(diagnostic.passed) is not bool or diagnostic.passed is not expected_pass:
        raise ValueError("design pass must derive from rank and condition")
    if expected_pass:
        if diagnostic.failure_reason is not None:
            raise ValueError("passing design must have null failure reason")
    elif type(diagnostic.failure_reason) is not str or not diagnostic.failure_reason:
        raise ValueError("failed design must have a nonempty failure reason")


def _diagnostic_matches_gate_failure(
    diagnostic: DesignDiagnostic | None,
    failure_class: str,
) -> bool:
    if type(diagnostic) is not DesignDiagnostic or diagnostic.passed:
        return False
    if failure_class.endswith("rank_gate_failure"):
        return (
            diagnostic.rank < diagnostic.n_columns
            and diagnostic.condition_number == float("inf")
            and diagnostic.failure_reason == "rank_deficient"
        )
    if failure_class.endswith("condition_gate_failure"):
        return (
            diagnostic.rank == diagnostic.n_columns
            and diagnostic.condition_number >= _DESIGN_CONDITION_LIMIT
            and diagnostic.failure_reason == "condition_limit_failed"
        )
    return False


_ANALYST_FIT_FRAME_ISSUER = object()


@dataclass(frozen=True, slots=True, init=False)
class AnalystFitFrame:
    """Module-issued canonical analyst fit-cell identity frame."""

    scenario_id: str
    frame_role: str
    cell_ids: tuple[int, ...]
    cell_count: int
    cell_sha256: str
    _issuer: object = field(repr=False, compare=False)

    def __init__(self) -> None:
        raise TypeError("AnalystFitFrame values must be issued by issue_analyst_fit_frame")


@dataclass(frozen=True, slots=True)
class AuditDesign:
    """Count-free canonical schedule arrays for structural numerical audits."""

    schedule_id: str
    cell_ids: IntArray
    standardized_quality: FloatArray
    predator_arrival_time: FloatArray
    opportunity_cell_index: IntArray
    opportunity_time_index: IntArray
    efforts: FloatArray

    def __post_init__(self) -> None:
        _validate_audit_design(self)
        object.__setattr__(self, "cell_ids", _immutable_int_array(self.cell_ids))
        object.__setattr__(
            self,
            "standardized_quality",
            _immutable_float_array(self.standardized_quality),
        )
        object.__setattr__(
            self,
            "predator_arrival_time",
            _immutable_float_array(self.predator_arrival_time),
        )
        object.__setattr__(
            self,
            "opportunity_cell_index",
            _immutable_int_array(self.opportunity_cell_index),
        )
        object.__setattr__(
            self,
            "opportunity_time_index",
            _immutable_int_array(self.opportunity_time_index),
        )
        object.__setattr__(self, "efforts", _immutable_float_array(self.efforts))


@dataclass(frozen=True, slots=True)
class OptimizerStartResult:
    """Immutable outcome from one frozen L-BFGS-B start."""

    start_index: int
    start_coordinates: FloatArray
    succeeded: bool
    coordinates: FloatArray | None
    objective_value: float | None
    log_likelihood: float | None
    failure_reason: str | None

    def __post_init__(self) -> None:
        _validate_optimizer_start_result(self)
        object.__setattr__(
            self,
            "start_coordinates",
            _immutable_float_array(self.start_coordinates),
        )
        if self.coordinates is not None:
            object.__setattr__(
                self,
                "coordinates",
                _immutable_float_array(self.coordinates),
            )


@dataclass(frozen=True, slots=True)
class MultiStartFitResult:
    """Deterministically ranked eight-start fit classification."""

    optimizer_kind: str
    attempts: tuple[OptimizerStartResult, ...]
    ranked_successes: tuple[OptimizerStartResult, ...]
    converged: bool
    converged_start_count: int
    best_start_index: int | None
    best_coordinates: FloatArray | None
    best_log_likelihood: float | None
    failure_reason: str | None

    def __post_init__(self) -> None:
        _validate_optimizer_kind(self.optimizer_kind)
        if type(self.attempts) is not tuple or type(self.ranked_successes) is not tuple:
            raise ValueError("optimizer attempts and ranked successes must be tuples")
        if type(self.converged) is not bool:
            raise ValueError("converged must be bool")
        if type(self.converged_start_count) is not int:
            raise ValueError("converged_start_count must be int")
        if self.converged_start_count != len(self.ranked_successes):
            raise ValueError("converged_start_count must match ranked successes")
        if self.best_coordinates is not None:
            object.__setattr__(
                self,
                "best_coordinates",
                _immutable_float_array(self.best_coordinates),
            )


@dataclass(frozen=True, slots=True)
class InverseAuditSearchResult:
    """One classified inverse search from a frozen positive-index start."""

    start_index: int
    start_coordinates: FloatArray
    succeeded: bool
    natural_parameters: FloatArray | None
    rmse: float | None
    scaled_distance: float | None
    recovered: bool
    collision: bool
    failure_reason: str | None

    def __post_init__(self) -> None:
        _validate_inverse_audit_search_result(self)
        object.__setattr__(
            self,
            "start_coordinates",
            _immutable_float_array(self.start_coordinates),
        )
        if self.natural_parameters is not None:
            object.__setattr__(
                self,
                "natural_parameters",
                _immutable_float_array(self.natural_parameters),
            )


@dataclass(frozen=True, slots=True)
class CanonicalInverseAuditResult:
    schedule_id: str
    target_id: str
    local_diagnostic: DesignDiagnostic
    searches: tuple[InverseAuditSearchResult, ...]
    successful_search_count: int
    recovery_count: int
    collision_count: int
    passed: bool
    failure_reason: str | None


@dataclass(frozen=True, slots=True, init=False)
class NineAuditPreflightResult:
    audits: tuple[CanonicalInverseAuditResult, ...]
    passed: bool
    estimation_authorized: bool
    failure_reason: str | None

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError(
            "NineAuditPreflightResult values are issued only by run_nine_audit_preflight"
        )

    def __post_init__(self) -> None:
        if type(self.audits) is not tuple or any(
            type(audit) is not CanonicalInverseAuditResult for audit in self.audits
        ):
            raise ValueError("preflight audits must be exact canonical audit records")
        if type(self.passed) is not bool or type(self.estimation_authorized) is not bool:
            raise ValueError("preflight pass and authorization fields must be bool")
        if self.passed != self.estimation_authorized:
            raise ValueError("preflight authorization must equal its pass state")
        if not self.passed:
            if type(self.failure_reason) is not str or not self.failure_reason:
                raise ValueError("failed preflight must propagate one explicit reason")
            return
        if self.failure_reason is not None:
            raise ValueError("passed preflight cannot contain a failure reason")

        expected_keys = tuple(_FROZEN_AUDIT_RECOVERY_COUNTS)
        observed_keys = tuple((audit.schedule_id, audit.target_id) for audit in self.audits)
        if observed_keys != expected_keys:
            raise ValueError("authorized preflight requires a complete nine-audit record")
        for audit in self.audits:
            key = (audit.schedule_id, audit.target_id)
            diagnostic = audit.local_diagnostic
            if (
                type(diagnostic) is not DesignDiagnostic
                or diagnostic.provenance
                != f"canonical_noncollision_audit:{audit.schedule_id}:{audit.target_id}"
                or diagnostic.role != "SUPPORTING-LOCAL-NONCOLLISION"
                or diagnostic.n_rows != _FROZEN_AUDIT_DIAGNOSTIC_ROWS[audit.schedule_id]
                or diagnostic.n_columns != 5
                or diagnostic.rank != 5
                or not isfinite(diagnostic.condition_number)
                or diagnostic.condition_number >= _DESIGN_CONDITION_LIMIT
                or not diagnostic.passed
            ):
                raise ValueError("authorized preflight requires all nine local audit gates")
            if (
                type(audit.searches) is not tuple
                or len(audit.searches) != 16
                or any(type(search) is not InverseAuditSearchResult for search in audit.searches)
                or tuple(search.start_index for search in audit.searches) != tuple(range(1, 17))
            ):
                raise ValueError("authorized preflight requires 16 classified searches per audit")
            successful_count = sum(search.succeeded for search in audit.searches)
            recovery_count = sum(search.recovered for search in audit.searches)
            collision_count = sum(search.collision for search in audit.searches)
            if (
                type(audit.successful_search_count) is not int
                or audit.successful_search_count != successful_count
                or audit.successful_search_count < INVERSE_AUDIT_REQUIRED_SUCCESSES
                or type(audit.recovery_count) is not int
                or audit.recovery_count != recovery_count
                or audit.recovery_count != _FROZEN_AUDIT_RECOVERY_COUNTS[key]
                or type(audit.collision_count) is not int
                or audit.collision_count != collision_count
                or audit.collision_count != 0
                or type(audit.passed) is not bool
                or not audit.passed
                or audit.failure_reason is not None
            ):
                raise ValueError("authorized preflight differs from the frozen nine-audit frontier")


_ISSUED_NINE_AUDIT_PREFLIGHTS: dict[int, NineAuditPreflightResult] = {}


def _new_nine_audit_preflight_result(
    *,
    audits: tuple[CanonicalInverseAuditResult, ...],
    passed: bool,
    estimation_authorized: bool,
    failure_reason: str | None,
) -> NineAuditPreflightResult:
    result = object.__new__(NineAuditPreflightResult)
    object.__setattr__(result, "audits", audits)
    object.__setattr__(result, "passed", passed)
    object.__setattr__(result, "estimation_authorized", estimation_authorized)
    object.__setattr__(result, "failure_reason", failure_reason)
    result.__post_init__()
    _ISSUED_NINE_AUDIT_PREFLIGHTS[id(result)] = result
    return result


def _nine_audit_preflight_is_authorized(
    preflight: NineAuditPreflightResult,
) -> bool:
    if type(preflight) is not NineAuditPreflightResult:
        raise TypeError("preflight must be NineAuditPreflightResult")
    if _ISSUED_NINE_AUDIT_PREFLIGHTS.get(id(preflight)) is not preflight:
        return False
    try:
        preflight.__post_init__()
    except AttributeError, TypeError, ValueError:
        return False
    return preflight.passed and preflight.estimation_authorized


@dataclass(frozen=True, slots=True)
class RankFailureFixtureResult:
    fixture_id: str
    diagnostic: DesignDiagnostic
    process_derivative_max_abs: float | None
    inverse_search_attempted: bool
    control_passed: bool

    def __post_init__(self) -> None:
        if type(self.fixture_id) is not str or not self.fixture_id:
            raise ValueError("fixture_id must be a nonempty string")
        if type(self.diagnostic) is not DesignDiagnostic:
            raise TypeError("diagnostic must be DesignDiagnostic")
        if self.process_derivative_max_abs is not None and (
            not isfinite(self.process_derivative_max_abs) or self.process_derivative_max_abs < 0.0
        ):
            raise ValueError("process_derivative_max_abs must be finite and nonnegative")
        if type(self.inverse_search_attempted) is not bool:
            raise ValueError("inverse_search_attempted must be bool")
        if type(self.control_passed) is not bool:
            raise ValueError("control_passed must be bool")


@dataclass(frozen=True, slots=True)
class ProfileNuisanceStart:
    source: str
    source_order: int
    coordinates: FloatArray

    def __post_init__(self) -> None:
        if type(self.source) is not str or not self.source:
            raise ValueError("profile start source must be nonempty")
        if type(self.source_order) is not int or self.source_order < 0:
            raise ValueError("profile start source_order must be nonnegative")
        if (
            type(self.coordinates) is not np.ndarray
            or self.coordinates.dtype != np.float64
            or self.coordinates.ndim != 1
            or not np.all(np.isfinite(self.coordinates))
        ):
            raise ValueError("profile start coordinates must be finite float64")
        object.__setattr__(self, "coordinates", _immutable_float_array(self.coordinates))


@dataclass(frozen=True, slots=True)
class ProfilePointResult:
    parameter_name: str
    target_value: float
    side: str
    succeeded: bool
    log_likelihood: float | None
    nuisance_coordinates: FloatArray | None
    natural_parameters: FloatArray | None
    selected_source: str | None
    selected_source_order: int | None
    failure_reason: str | None

    def __post_init__(self) -> None:
        if self.nuisance_coordinates is not None:
            object.__setattr__(
                self,
                "nuisance_coordinates",
                _immutable_float_array(self.nuisance_coordinates),
            )
        if self.natural_parameters is not None:
            object.__setattr__(
                self,
                "natural_parameters",
                _immutable_float_array(self.natural_parameters),
            )


@dataclass(frozen=True, slots=True)
class ProfileSideResult:
    side: str
    points: tuple[ProfilePointResult, ...]
    crossed_cutoff: bool
    open_side: bool
    interval_endpoint: float | None
    bracket: tuple[float, float] | None


@dataclass(frozen=True, slots=True)
class ParameterProfileResult:
    optimizer_kind: str
    parameter_name: str
    mle: float
    support: tuple[float, float]
    llmax: float
    lower: ProfileSideResult
    upper: ProfileSideResult
    practically_identifiable: bool
    global_fit_valid: bool
    failure_reason: str | None


@dataclass(frozen=True, slots=True)
class JointFitResult:
    converged: bool
    parameters: JointParameters | None
    multistart: MultiStartFitResult | None
    potential_diagnostic: DesignDiagnostic | None
    plugin_diagnostic: DesignDiagnostic | None
    fit_frame: AnalystFitFrame
    fit_frame_cell_count: int
    fit_frame_sha256: str
    failure_class: str | None
    failure_reason: str | None

    def __post_init__(self) -> None:
        if type(self.converged) is not bool:
            raise ValueError("joint-fit converged must be bool")
        _validate_analyst_fit_frame(self.fit_frame)
        if (
            type(self.fit_frame_cell_count) is not int
            or self.fit_frame_cell_count != self.fit_frame.cell_count
            or type(self.fit_frame_sha256) is not str
            or self.fit_frame_sha256 != self.fit_frame.cell_sha256
        ):
            raise ValueError("joint fit must carry its issued fit-frame count and digest")
        if self.multistart is not None and (
            type(self.multistart) is not MultiStartFitResult
            or self.multistart.optimizer_kind != "joint"
        ):
            raise TypeError("joint-fit multistart must have joint optimizer kind")
        for diagnostic, provenance, role in (
            (
                self.potential_diagnostic,
                "potential_design",
                "ANALYST-PREFLIGHT",
            ),
            (
                self.plugin_diagnostic,
                "joint_plugin_smoothed_at_risk",
                "ANALYST-JOINT-PRACTICAL",
            ),
        ):
            if diagnostic is None:
                continue
            validate_design_diagnostic(diagnostic)
            if (
                type(diagnostic) is not DesignDiagnostic
                or diagnostic.provenance != provenance
                or diagnostic.role != role
                or diagnostic.n_columns != 3
                or diagnostic.n_rows != self.fit_frame.cell_count * _MAX_INTERVAL_COUNT
                or type(diagnostic.passed) is not bool
                or (
                    not diagnostic.passed
                    and (
                        type(diagnostic.failure_reason) is not str or not diagnostic.failure_reason
                    )
                )
            ):
                raise ValueError("joint fit carries malformed typed design evidence")
        if self.converged:
            if (
                type(self.parameters) is not JointParameters
                or self.multistart is None
                or not self.multistart.converged
                or self.potential_diagnostic is None
                or not self.potential_diagnostic.passed
                or self.plugin_diagnostic is None
                or not self.plugin_diagnostic.passed
                or self.failure_class is not None
                or self.failure_reason is not None
            ):
                raise ValueError("converged joint fit must have two passing designs and parameters")
            return
        if (
            self.parameters is not None
            or self.failure_class not in FIT_FAILURE_CLASSES
            or type(self.failure_reason) is not str
            or not self.failure_reason
        ):
            raise ValueError(
                "failed joint fit must reject parameters and propagate one typed failure"
            )
        failure_class = self.failure_class
        if failure_class == "preflight_or_input_failure":
            if any(
                value is not None
                for value in (
                    self.multistart,
                    self.potential_diagnostic,
                    self.plugin_diagnostic,
                )
            ):
                raise ValueError("preflight/input failure cannot carry evaluated fit evidence")
            return
        if failure_class in {
            "potential_rank_gate_failure",
            "potential_condition_gate_failure",
        }:
            if (
                self.multistart is not None
                or self.plugin_diagnostic is not None
                or not _diagnostic_matches_gate_failure(self.potential_diagnostic, failure_class)
            ):
                raise ValueError("potential-gate failure forbids optimizer and downstream evidence")
            return
        if failure_class == "optimizer_or_nonfinite_failure":
            if (
                self.potential_diagnostic is None
                or not self.potential_diagnostic.passed
                or self.multistart is None
                or self.multistart.converged
                or self.plugin_diagnostic is None
                or self.plugin_diagnostic.rank != 0
                or self.plugin_diagnostic.condition_number != float("inf")
                or self.plugin_diagnostic.failure_reason != "joint_fit_failed_or_nonfinite"
            ):
                raise ValueError(
                    "joint optimizer failure requires passing potential and rank-zero plug-in"
                )
            return
        if failure_class in {
            "plugin_rank_gate_failure",
            "plugin_condition_gate_failure",
        }:
            if (
                self.potential_diagnostic is None
                or not self.potential_diagnostic.passed
                or self.multistart is None
                or not self.multistart.converged
                or not _diagnostic_matches_gate_failure(self.plugin_diagnostic, failure_class)
            ):
                raise ValueError(
                    "plug-in gate failure requires a converged optimizer and matching diagnostic"
                )
            return
        raise ValueError("failure class is not applicable to a joint fit")


@dataclass(frozen=True, slots=True)
class ProcessOracleFitResult:
    converged: bool
    parameters: ProcessParameters | None
    multistart: MultiStartFitResult | None
    at_risk_diagnostic: DesignDiagnostic | None
    failure_class: str | None
    failure_reason: str | None

    def __post_init__(self) -> None:
        if type(self.converged) is not bool:
            raise ValueError("process-oracle converged must be bool")
        if self.multistart is not None and (
            type(self.multistart) is not MultiStartFitResult
            or self.multistart.optimizer_kind != "process_oracle"
        ):
            raise TypeError("process-oracle multistart must have process_oracle kind")
        if self.at_risk_diagnostic is not None and (
            type(self.at_risk_diagnostic) is not DesignDiagnostic
            or self.at_risk_diagnostic.provenance != "process_oracle_truth_at_risk"
            or self.at_risk_diagnostic.role != "ORACLE-BENCHMARK-ONLY"
            or self.at_risk_diagnostic.n_columns != 3
        ):
            raise TypeError("process-oracle fit requires its distinct at-risk diagnostic")
        if self.at_risk_diagnostic is not None:
            validate_design_diagnostic(self.at_risk_diagnostic)
        if self.converged:
            if (
                type(self.parameters) is not ProcessParameters
                or self.multistart is None
                or not self.multistart.converged
                or self.at_risk_diagnostic is None
                or not self.at_risk_diagnostic.passed
                or self.failure_class is not None
                or self.failure_reason is not None
            ):
                raise ValueError("converged process-oracle fit must be complete and valid")
            return
        if (
            self.parameters is not None
            or self.failure_class not in FIT_FAILURE_CLASSES
            or type(self.failure_reason) is not str
            or not self.failure_reason
        ):
            raise ValueError("failed process-oracle fit must propagate one typed failure")
        failure_class = self.failure_class
        if failure_class == "preflight_or_input_failure":
            if self.multistart is not None or self.at_risk_diagnostic is not None:
                raise ValueError("preflight/input process failure cannot carry fit evidence")
            return
        if failure_class in {
            "oracle_rank_gate_failure",
            "oracle_condition_gate_failure",
        }:
            if self.multistart is not None or not _diagnostic_matches_gate_failure(
                self.at_risk_diagnostic, failure_class
            ):
                raise ValueError(
                    "process design-gate failure requires its matching oracle diagnostic"
                )
            return
        if failure_class == "optimizer_or_nonfinite_failure":
            diagnostic = self.at_risk_diagnostic
            if (
                self.multistart is None
                or self.multistart.converged
                or diagnostic is None
                or diagnostic.rank != 0
                or diagnostic.condition_number != float("inf")
                or diagnostic.failure_reason != "process_oracle_fit_failed_or_nonfinite"
            ):
                raise ValueError(
                    "process optimizer failure requires a rank-zero process diagnostic"
                )
            return
        raise ValueError("failure class is not applicable to a process-oracle fit")


@dataclass(frozen=True, slots=True)
class ObservationOracleFitResult:
    converged: bool
    rates: EffectiveCountRates | None
    multistart: MultiStartFitResult | None
    failure_class: str | None
    failure_reason: str | None

    def __post_init__(self) -> None:
        if type(self.converged) is not bool:
            raise ValueError("observation-oracle converged must be bool")
        if self.multistart is not None and (
            type(self.multistart) is not MultiStartFitResult
            or self.multistart.optimizer_kind != "observation_oracle"
        ):
            raise TypeError("observation-oracle multistart must have observation_oracle kind")
        if self.converged:
            if (
                type(self.rates) is not EffectiveCountRates
                or self.multistart is None
                or not self.multistart.converged
                or self.failure_class is not None
                or self.failure_reason is not None
            ):
                raise ValueError("converged observation-oracle fit must be complete and valid")
            return
        if (
            self.rates is not None
            or self.failure_class
            not in {
                "preflight_or_input_failure",
                "optimizer_or_nonfinite_failure",
            }
            or type(self.failure_reason) is not str
            or not self.failure_reason
        ):
            raise ValueError("failed observation-oracle fit must propagate one typed failure")
        if self.failure_class == "preflight_or_input_failure":
            if self.multistart is not None:
                raise ValueError("preflight/input observation failure forbids optimizer evidence")
        elif self.multistart is None or self.multistart.converged:
            raise ValueError("observation optimizer failure requires a failed multistart")


@dataclass(frozen=True, slots=True)
class AlignmentFrame:
    score_cell_ids: tuple[int, ...]
    fit_cell_ids: tuple[int, ...]


_SCENARIO_SCHEDULE_DEFINITIONS = (
    ScenarioScheduleDefinition(
        "process_oracle_observed_transition",
        "process_truth",
        "not_applicable",
    ),
    ScenarioScheduleDefinition(
        "observation_oracle_fixed_transition",
        "structured_12",
        "structured",
    ),
    ScenarioScheduleDefinition("dense_count_exact_model", "dense_6", "unit"),
    ScenarioScheduleDefinition(
        "structured_imperfect_effort",
        "structured_12",
        "structured",
    ),
    ScenarioScheduleDefinition("sparse_expected_failure", "sparse_24", "sparse"),
    ScenarioScheduleDefinition("zero_driver_effect_negative_control", "dense_6", "unit"),
    ScenarioScheduleDefinition(
        "permuted_arrival_alignment_stress",
        "structured_12",
        "structured",
    ),
    ScenarioScheduleDefinition(
        "no_emission_contrast_negative_control",
        "dense_6",
        "unit",
    ),
    ScenarioScheduleDefinition(
        "informative_dropout_misspecification_stress",
        "structured_12",
        "structured",
    ),
    ScenarioScheduleDefinition(
        "goal018_continuous_abundance_stress",
        "structured_12",
        "structured",
    ),
    ScenarioScheduleDefinition(
        "spatial_frailty_stress",
        "structured_12",
        "structured",
    ),
)


def ordered_rates_from_fractions(
    p_frac: float,
    q_frac: float,
) -> EffectiveCountRates:
    """Map the frozen unit-box coordinates to strictly ordered natural rates."""

    fractions = OrderedRateFractions(p_frac=p_frac, q_frac=q_frac)
    lambda_present = (
        LAMBDA_PRESENT_SUPPORT[0]
        + (LAMBDA_PRESENT_SUPPORT[1] - LAMBDA_PRESENT_SUPPORT[0]) * fractions.p_frac
    )
    q_upper = min(LAMBDA_QUASI_SUPPORT[1], lambda_present - RATE_ORDER_GAP)
    lambda_quasi = LAMBDA_QUASI_SUPPORT[0] + (q_upper - LAMBDA_QUASI_SUPPORT[0]) * fractions.q_frac
    return EffectiveCountRates(
        lambda_present=lambda_present,
        lambda_quasi=lambda_quasi,
    )


def ordered_rate_fractions_from_natural(
    lambda_present: float,
    lambda_quasi: float,
) -> OrderedRateFractions:
    """Invert the frozen ordered-rate map without clipping invalid rates."""

    present = _canonical_bounded_float(
        lambda_present,
        support=LAMBDA_PRESENT_SUPPORT,
        name="lambda_present",
    )
    quasi = _canonical_bounded_float(
        lambda_quasi,
        support=LAMBDA_QUASI_SUPPORT,
        name="lambda_quasi",
    )
    q_upper = min(LAMBDA_QUASI_SUPPORT[1], present - RATE_ORDER_GAP)
    if quasi > q_upper:
        raise ValueError("natural rates violate the strict computational ordering gap")
    p_frac = (present - LAMBDA_PRESENT_SUPPORT[0]) / (
        LAMBDA_PRESENT_SUPPORT[1] - LAMBDA_PRESENT_SUPPORT[0]
    )
    q_frac = (quasi - LAMBDA_QUASI_SUPPORT[0]) / (q_upper - LAMBDA_QUASI_SUPPORT[0])
    return OrderedRateFractions(p_frac=p_frac, q_frac=q_frac)


def rates_with_fixed_lambda_present(
    lambda_present: float,
    q_frac: float,
) -> EffectiveCountRates:
    """Apply the literal conditional nuisance map with present rate fixed."""

    present = _canonical_bounded_float(
        lambda_present,
        support=LAMBDA_PRESENT_SUPPORT,
        name="lambda_present",
    )
    fraction = _canonical_unit_fraction(q_frac, "q_frac")
    q_upper = min(LAMBDA_QUASI_SUPPORT[1], present - RATE_ORDER_GAP)
    if q_upper < LAMBDA_QUASI_SUPPORT[0]:
        raise ValueError("fixed lambda_present cannot preserve ordered rate supports")
    quasi = LAMBDA_QUASI_SUPPORT[0] + (q_upper - LAMBDA_QUASI_SUPPORT[0]) * fraction
    return EffectiveCountRates(lambda_present=present, lambda_quasi=quasi)


def rates_with_fixed_lambda_quasi(
    lambda_quasi: float,
    p_frac: float,
) -> EffectiveCountRates:
    """Apply the literal conditional nuisance map with quasi rate fixed."""

    quasi = _canonical_bounded_float(
        lambda_quasi,
        support=LAMBDA_QUASI_SUPPORT,
        name="lambda_quasi",
    )
    fraction = _canonical_unit_fraction(p_frac, "p_frac")
    p_lower = max(LAMBDA_PRESENT_SUPPORT[0], quasi + RATE_ORDER_GAP)
    if p_lower > LAMBDA_PRESENT_SUPPORT[1]:
        raise ValueError("fixed lambda_quasi cannot preserve ordered rate supports")
    present = p_lower + (LAMBDA_PRESENT_SUPPORT[1] - p_lower) * fraction
    return EffectiveCountRates(lambda_present=present, lambda_quasi=quasi)


def project_unit_coordinate(value: float) -> float:
    """Clip only unit-box roundoff within the frozen projection tolerance."""

    coordinate = _canonical_numeric_float(value, name="coordinate")
    if (
        coordinate < -COORDINATE_PROJECTION_TOLERANCE
        or coordinate > 1.0 + COORDINATE_PROJECTION_TOLERANCE
    ):
        raise ValueError("coordinate is outside the permitted projection tolerance")
    return min(max(coordinate, 0.0), 1.0)


def deduplicate_coordinate_starts(
    starts: tuple[FloatArray, ...],
) -> tuple[FloatArray, ...]:
    """Retain the first start within the frozen max-coordinate threshold."""

    if type(starts) is not tuple:
        raise ValueError("starts must be a tuple")
    retained: list[FloatArray] = []
    shape: tuple[int, ...] | None = None
    for start in starts:
        if (
            type(start) is not np.ndarray
            or start.dtype != np.float64
            or start.ndim != 1
            or not np.all(np.isfinite(start))
        ):
            raise ValueError("starts must contain finite one-dimensional float64 arrays")
        if shape is None:
            shape = start.shape
        elif start.shape != shape:
            raise ValueError("coordinate starts must share one shape")
        if any(
            float(np.max(np.abs(start - previous))) <= START_DEDUPLICATION_TOLERANCE
            for previous in retained
        ):
            continue
        retained.append(_immutable_float_array(start))
    return tuple(retained)


def halton_optimization_starts(count: int) -> FloatArray:
    """Return the frozen positive-index eight- or sixteen-row start table."""

    if type(count) is not int or count not in (8, 16):
        raise ValueError("Halton start count must be exactly 8 or 16")
    starts = np.empty((count, len(_HALTON_BASES)), dtype=np.float64)
    for row, index in enumerate(range(1, count + 1)):
        for column, (base, support) in enumerate(
            zip(_HALTON_BASES, _OPTIMIZATION_COORDINATE_SUPPORTS, strict=True)
        ):
            unit = 0.05 + 0.90 * _radical_inverse(index, base)
            starts[row, column] = support[0] + (support[1] - support[0]) * unit
    return _immutable_float_array(starts)


def global_optimization_starts() -> FloatArray:
    return halton_optimization_starts(8)


def process_oracle_optimization_starts() -> FloatArray:
    return _immutable_float_array(halton_optimization_starts(8)[:, :3])


def observation_oracle_optimization_starts() -> FloatArray:
    return _immutable_float_array(halton_optimization_starts(8)[:, 3:5])


def validate_rng_payload(payload: object) -> RngPayload:
    """Validate an exact non-holdout RNG payload before any RNG construction."""

    if type(payload) is not dict:
        raise TypeError("RNG payload must be an exact dict")
    raw = cast(dict[object, object], payload)
    if set(raw) != RNG_PAYLOAD_KEYS:
        missing = sorted(RNG_PAYLOAD_KEYS - set(raw))
        extra = sorted(str(key) for key in set(raw) - RNG_PAYLOAD_KEYS)
        raise ValueError(f"RNG payload keys must be exact; missing={missing}, extra={extra}")

    goal = raw["goal"]
    master_seed = raw["master_seed"]
    scenario_id = raw["scenario_id"]
    split = raw["split"]
    replicate_index = raw["replicate_index"]
    component = raw["component"]
    draw_index = raw["draw_index"]
    if type(goal) is not str:
        raise ValueError("goal must be the string 023")
    if type(master_seed) is not int:
        raise ValueError(f"master_seed must be the integer {MASTER_SEED}")
    if type(scenario_id) is not str:
        raise ValueError("scenario_id must be a canonical scenario")
    if type(split) is not str:
        raise ValueError("split must be development, calibration, or holdout")
    if type(replicate_index) is not int:
        raise ValueError("replicate_index must be a zero-based integer")
    if type(component) is not str:
        raise ValueError("component must be a canonical component")
    if draw_index is not None and type(draw_index) is not int:
        raise ValueError("draw_index must be a zero-based integer or null")
    return RngPayload(
        goal=goal,
        master_seed=master_seed,
        scenario_id=scenario_id,
        split=split,
        replicate_index=replicate_index,
        component=component,
        draw_index=draw_index,
    )


def canonical_rng_payload_json(payload: object) -> str:
    """Return compact sorted-key ASCII JSON for one validated payload."""

    validated = validate_rng_payload(payload)
    return dumps(
        validated.as_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def rng_payload_sha256(payload: object) -> str:
    canonical = canonical_rng_payload_json(payload)
    return sha256(canonical.encode("ascii")).hexdigest()


def rng_entropy_words(payload: object) -> tuple[int, ...]:
    canonical = canonical_rng_payload_json(payload)
    digest = sha256(canonical.encode("ascii")).digest()
    return tuple(int.from_bytes(digest[offset : offset + 4], "big") for offset in range(0, 32, 4))


def rng_from_payload(payload: object) -> np.random.Generator:
    """Construct the frozen SeedSequence/PCG64DXSM generator after validation."""

    entropy_words = rng_entropy_words(payload)
    seed_sequence = np.random.SeedSequence(entropy_words)
    return np.random.Generator(np.random.PCG64DXSM(seed_sequence))


def scenario_schedule_definition(scenario_id: str) -> ScenarioScheduleDefinition:
    if type(scenario_id) is not str:
        raise ValueError("scenario_id must be a canonical scenario")
    for definition in _SCENARIO_SCHEDULE_DEFINITIONS:
        if definition.scenario_id == scenario_id:
            return definition
    raise ValueError("scenario_id must be a canonical scenario")


def structured_effort(standardized_quality: float) -> float:
    quality = _canonical_standardized_quality(standardized_quality)
    return 0.7 + 0.6 * min(max((quality + 2.0) / 4.0, 0.0), 1.0)


def sparse_frame_cell_ids(cells: tuple[DesignCell, ...]) -> tuple[int, ...]:
    canonical_cells = _canonical_design_cells(cells)
    retained_count = int(np.floor(0.25 * len(canonical_cells)))
    ranked = sorted(
        canonical_cells,
        key=lambda cell: (
            sha256(f"023|sparse_expected_failure|cell_id={cell.cell_id}".encode("ascii")).digest(),
            cell.cell_id,
        ),
    )
    return tuple(sorted(cell.cell_id for cell in ranked[:retained_count]))


def alignment_frame(cells: tuple[DesignCell, ...]) -> AlignmentFrame:
    canonical_cells = _canonical_design_cells(cells)
    score_count = int(np.floor(0.20 * len(canonical_cells)))
    ranked = sorted(
        canonical_cells,
        key=lambda cell: (
            sha256(f"023|alignment_score|cell_id={cell.cell_id}".encode("ascii")).digest(),
            cell.cell_id,
        ),
    )
    score_set = {cell.cell_id for cell in ranked[:score_count]}
    return AlignmentFrame(
        score_cell_ids=tuple(cell.cell_id for cell in canonical_cells if cell.cell_id in score_set),
        fit_cell_ids=tuple(
            cell.cell_id for cell in canonical_cells if cell.cell_id not in score_set
        ),
    )


def quality_quintile_labels(cells: tuple[DesignCell, ...]) -> tuple[str, ...]:
    canonical_cells = _canonical_design_cells(cells)
    if not canonical_cells:
        return ()
    ranked_indices = sorted(
        range(len(canonical_cells)),
        key=lambda index: (
            canonical_cells[index].standardized_quality,
            canonical_cells[index].cell_id,
        ),
    )
    labels = [""] * len(canonical_cells)
    for rank, cell_index in enumerate(ranked_indices):
        quintile = min(5, 1 + (5 * rank) // len(canonical_cells))
        labels[cell_index] = f"q{quintile}"
    return tuple(labels)


def permute_arrival_within_blocks(cells: tuple[DesignCell, ...]) -> FloatArray:
    canonical_cells = _canonical_design_cells(cells)
    quintiles = quality_quintile_labels(canonical_cells)
    original = np.asarray(
        [
            np.nan if cell.predator_arrival_time is None else cell.predator_arrival_time
            for cell in canonical_cells
        ],
        dtype=np.float64,
    )
    permuted = np.empty(len(canonical_cells), dtype=np.float64)
    blocks: dict[tuple[str, str], list[int]] = {}
    for index, (cell, quintile) in enumerate(zip(canonical_cells, quintiles, strict=True)):
        blocks.setdefault((cell.row_band, quintile), []).append(index)
    for indices in blocks.values():
        indices.sort(key=lambda index: canonical_cells[index].cell_id)
        shift = max(1, len(indices) // 2)
        for target_position, target_index in enumerate(indices):
            source_index = indices[(target_position + shift) % len(indices)]
            permuted[target_index] = original[source_index]
    return _immutable_float_array(permuted)


def build_canonical_schedule(
    cells: tuple[DesignCell, ...],
    scenario_id: str,
) -> tuple[ScheduledOpportunity, ...]:
    """Build a truth-independent schedule in integer cell/time order."""

    canonical_cells = _canonical_design_cells(cells)
    definition = scenario_schedule_definition(scenario_id)
    if definition.schedule_id == "process_truth":
        return ()
    selected_cells = canonical_cells
    if definition.schedule_id == "sparse_24":
        selected_ids = set(sparse_frame_cell_ids(canonical_cells))
        selected_cells = tuple(cell for cell in canonical_cells if cell.cell_id in selected_ids)
    times = {
        "dense_6": MODEL_TIMES,
        "structured_12": tuple(range(0, 121, 12)),
        "sparse_24": tuple(range(0, 121, 24)),
    }[definition.schedule_id]
    opportunities: list[ScheduledOpportunity] = []
    for cell in selected_cells:
        if definition.effort_rule == "structured":
            effort = structured_effort(cell.standardized_quality)
        elif definition.effort_rule == "sparse":
            effort = 0.6
        else:
            effort = 1.0
        opportunities.extend(
            ScheduledOpportunity(
                cell_id=cell.cell_id,
                time=time,
                effort=effort,
                standardized_quality=cell.standardized_quality,
                predator_arrival_time=cell.predator_arrival_time,
            )
            for time in times
        )
    return tuple(opportunities)


def audit_design_from_schedule(
    schedule: tuple[ScheduledOpportunity, ...],
    *,
    schedule_id: str,
) -> AuditDesign:
    """Pack one canonical count-free opportunity schedule for repeated audits."""

    canonical = _canonical_schedule(schedule)
    if not canonical:
        raise ValueError("audit schedule must contain at least one opportunity")
    if type(schedule_id) is not str or not schedule_id:
        raise ValueError("schedule_id must be a nonempty string")
    cell_ids: list[int] = []
    qualities: list[float] = []
    arrivals: list[float] = []
    cell_index_by_id: dict[int, int] = {}
    opportunity_cell_indices = np.empty(len(canonical), dtype=np.int64)
    opportunity_time_indices = np.empty(len(canonical), dtype=np.int64)
    efforts = np.empty(len(canonical), dtype=np.float64)
    for opportunity_index, opportunity in enumerate(canonical):
        if opportunity.cell_id not in cell_index_by_id:
            cell_index_by_id[opportunity.cell_id] = len(cell_ids)
            cell_ids.append(opportunity.cell_id)
            qualities.append(opportunity.standardized_quality)
            arrival = opportunity.predator_arrival_time
            arrivals.append(float(arrival) if arrival is not None and isfinite(arrival) else np.nan)
        opportunity_cell_indices[opportunity_index] = cell_index_by_id[opportunity.cell_id]
        opportunity_time_indices[opportunity_index] = opportunity.time // 6
        efforts[opportunity_index] = opportunity.effort
    return AuditDesign(
        schedule_id=schedule_id,
        cell_ids=np.asarray(cell_ids, dtype=np.int64),
        standardized_quality=np.asarray(qualities, dtype=np.float64),
        predator_arrival_time=np.asarray(arrivals, dtype=np.float64),
        opportunity_cell_index=opportunity_cell_indices,
        opportunity_time_index=opportunity_time_indices,
        efforts=efforts,
    )


def simulate_latent_process(
    cells: tuple[DesignCell, ...],
    parameters: ProcessParameters,
    generator: ProcessRandomGenerator,
) -> ProcessSimulationTruth:
    """Simulate all process uniforms first, including post-absorption entries."""

    canonical_cells = _canonical_design_cells(cells)
    if not canonical_cells:
        raise ValueError("cells must contain at least one canonical passable cell")
    if type(parameters) is not ProcessParameters:
        raise TypeError("parameters must be ProcessParameters")
    uniforms = generator.random(
        size=(len(canonical_cells), _MAX_INTERVAL_COUNT),
        dtype=np.float64,
    )
    _validate_uniform_draws(uniforms, expected_shape=(len(canonical_cells), 20))

    qualities = np.asarray(
        [cell.standardized_quality for cell in canonical_cells],
        dtype=np.float64,
    )
    arrivals = np.asarray(
        [
            np.nan if cell.predator_arrival_time is None else cell.predator_arrival_time
            for cell in canonical_cells
        ],
        dtype=np.float64,
    )
    endpoints = np.asarray(MODEL_TIMES[1:], dtype=np.float64)
    driver = np.zeros((len(canonical_cells), _MAX_INTERVAL_COUNT), dtype=np.float64)
    finite_arrival = np.isfinite(arrivals)
    driver[finite_arrival] = np.maximum(
        (endpoints[np.newaxis, :] - arrivals[finite_arrival, np.newaxis]) / 30.0,
        0.0,
    )
    eta = (
        parameters.alpha
        + parameters.beta_driver * driver
        + parameters.beta_quality * qualities[:, np.newaxis]
    )
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        hazards = -np.expm1(-np.exp(eta))
    _require_finite_array(eta, name="process simulation eta")
    _require_finite_array(hazards, name="process simulation hazard")
    events = uniforms < hazards
    states = np.zeros((len(canonical_cells), len(MODEL_TIMES)), dtype=np.float64)
    states[:, 1:] = np.maximum.accumulate(events, axis=1).astype(np.float64)
    has_event = np.any(events, axis=1)
    first_event_index = np.argmax(events, axis=1)
    transition_times = np.full(len(canonical_cells), np.nan, dtype=np.float64)
    transition_times[has_event] = endpoints[first_event_index[has_event]]
    return ProcessSimulationTruth(
        cell_ids=np.asarray([cell.cell_id for cell in canonical_cells], dtype=np.int64),
        states=states,
        transition_times=transition_times,
    )


def simulate_observation_histories(
    schedule: tuple[ScheduledOpportunity, ...],
    process_result: ProcessSimulationTruth,
    rates: EffectiveCountRates,
    generator: ObservationRandomGenerator,
) -> tuple[AnalystHistory, ...]:
    """Draw every scheduled count in one canonical vectorized Poisson call."""

    canonical_schedule = _canonical_schedule(schedule)
    if type(process_result) is not ProcessSimulationTruth:
        raise TypeError("process_result must be ProcessSimulationTruth")
    canonical_rates = _canonical_effective_rates(rates)
    truth_row_by_cell = {
        int(cell_id): index for index, cell_id in enumerate(process_result.cell_ids)
    }
    means = np.empty(len(canonical_schedule), dtype=np.float64)
    for index, opportunity in enumerate(canonical_schedule):
        if opportunity.cell_id not in truth_row_by_cell:
            raise ValueError("schedule cell_ids must exist in process_result")
        truth_row = truth_row_by_cell[opportunity.cell_id]
        state_value = process_result.states[truth_row, opportunity.time // 6]
        if state_value not in (0.0, 1.0):
            raise ValueError("process_result states must be binary")
        means[index] = effort_scaled_mean(
            effort=opportunity.effort,
            state=int(state_value),
            rates=canonical_rates,
        )
    counts = generator.poisson(means)
    _validate_poisson_draws(counts, expected_shape=(len(canonical_schedule),))

    opportunities_by_cell: dict[int, list[CountOpportunity]] = {}
    metadata_by_cell: dict[int, tuple[float, float | None]] = {}
    for scheduled, count in zip(canonical_schedule, counts, strict=True):
        opportunities_by_cell.setdefault(scheduled.cell_id, []).append(
            CountOpportunity(
                time=scheduled.time,
                count=int(count),
                effort=scheduled.effort,
            )
        )
        metadata_by_cell[scheduled.cell_id] = (
            scheduled.standardized_quality,
            scheduled.predator_arrival_time,
        )
    return tuple(
        AnalystHistory(
            cell_id=cell_id,
            standardized_quality=metadata_by_cell[cell_id][0],
            predator_arrival_time=metadata_by_cell[cell_id][1],
            opportunities=tuple(opportunities_by_cell[cell_id]),
        )
        for cell_id in opportunities_by_cell
    )


def svd_rank_condition(matrix: FloatArray) -> tuple[int, float]:
    """Apply the frozen generalized SVD rank and condition convention."""

    if type(matrix) is not np.ndarray or matrix.dtype != np.float64 or matrix.ndim != 2:
        raise ValueError("matrix must be an exact two-dimensional float64 ndarray")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("matrix must contain only finite float64 values")
    n_rows, n_columns = matrix.shape
    if n_rows == 0 or n_columns == 0:
        raise ValueError("matrix must contain at least one row and one column")
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    singular_max = float(singular_values[0])
    tolerance = max(n_rows, n_columns) * np.finfo(np.float64).eps * singular_max
    rank = int(np.count_nonzero(singular_values > tolerance))
    condition = singular_max / float(singular_values[-1]) if rank == n_columns else float("inf")
    return rank, condition


def matrix_rank_diagnostic(
    matrix: FloatArray,
    *,
    required_columns: int,
    provenance: str,
    role: str,
) -> DesignDiagnostic:
    """Apply one generalized rank/condition gate to three- or five-column matrices."""

    if type(required_columns) is not int or required_columns < 1:
        raise ValueError("required_columns must be a positive integer")
    if type(matrix) is not np.ndarray or matrix.ndim != 2 or matrix.shape[1] != required_columns:
        raise ValueError("matrix column count must equal required_columns")
    if type(provenance) is not str or not provenance:
        raise ValueError("provenance must be a nonempty string")
    if type(role) is not str or not role:
        raise ValueError("role must be a nonempty string")
    rank, condition = svd_rank_condition(matrix)
    passed = rank == required_columns and condition < _DESIGN_CONDITION_LIMIT
    failure_reason = None
    if not passed:
        failure_reason = "rank_deficient" if rank != required_columns else "condition_limit_failed"
    return DesignDiagnostic(
        provenance=provenance,
        role=role,
        n_rows=matrix.shape[0],
        n_columns=matrix.shape[1],
        rank=rank,
        condition_number=condition,
        passed=passed,
        failure_reason=failure_reason,
    )


def potential_design_diagnostic(cells: tuple[DesignCell, ...]) -> DesignDiagnostic:
    matrix = _potential_design_matrix(_canonical_design_cells(cells))
    return _design_diagnostic(
        matrix,
        provenance="potential_design",
        role="ANALYST-PREFLIGHT",
    )


def process_oracle_truth_at_risk_diagnostic(
    cells: tuple[DesignCell, ...],
    process_result: ProcessSimulationTruth,
) -> DesignDiagnostic:
    canonical_cells = _canonical_design_cells(cells)
    _require_truth_alignment(canonical_cells, process_result)
    full_matrix = _potential_design_matrix(canonical_cells).reshape(
        len(canonical_cells),
        _MAX_INTERVAL_COUNT,
        3,
    )
    at_risk = process_result.states[:, :-1] == 0.0
    matrix = np.asarray(full_matrix[at_risk], dtype=np.float64)
    return _design_diagnostic(
        matrix,
        provenance="process_oracle_truth_at_risk",
        role="ORACLE-BENCHMARK-ONLY",
    )


def joint_plugin_at_risk_weights(
    histories: tuple[AnalystHistory, ...],
    parameters: JointParameters,
) -> FloatArray:
    canonical_histories = _canonical_analyst_histories(histories)
    if type(parameters) is not JointParameters:
        raise TypeError("parameters must be JointParameters")
    batch = analyst_batch_from_histories(canonical_histories)
    path_weights = batched_joint_path_posterior_weights(batch, parameters)
    weights = np.empty(
        (len(canonical_histories), _MAX_INTERVAL_COUNT),
        dtype=np.float64,
    )
    weights[:, 0] = 1.0
    for interval_index in range(1, _MAX_INTERVAL_COUNT):
        weights[:, interval_index] = path_weights[:, interval_index:].sum(
            axis=1,
            dtype=np.float64,
        )
    _require_finite_array(weights, name="joint plugin at-risk weight")
    if np.any(weights < 0.0) or np.any(weights > 1.0):
        raise LikelihoodEvaluationError("joint plugin at-risk weights are outside [0, 1]")
    return _immutable_float_array(weights)


def joint_plugin_smoothed_at_risk_diagnostic(
    histories: tuple[AnalystHistory, ...],
    parameters: JointParameters | None,
) -> DesignDiagnostic:
    canonical_histories = _canonical_analyst_histories(histories)
    if parameters is None:
        return DesignDiagnostic(
            provenance="joint_plugin_smoothed_at_risk",
            role="ANALYST-JOINT-PRACTICAL",
            n_rows=len(canonical_histories) * _MAX_INTERVAL_COUNT,
            n_columns=3,
            rank=0,
            condition_number=float("inf"),
            passed=False,
            failure_reason="joint_fit_failed_or_nonfinite",
        )
    weights = joint_plugin_at_risk_weights(canonical_histories, parameters)
    design = _analyst_history_design_matrix(canonical_histories)
    weighted = design * np.sqrt(weights.reshape(-1, 1))
    return _design_diagnostic(
        np.asarray(weighted, dtype=np.float64),
        provenance="joint_plugin_smoothed_at_risk",
        role="ANALYST-JOINT-PRACTICAL",
    )


@dataclass(frozen=True, slots=True)
class ProcessParameters:
    """Natural-space cloglog process parameters on their frozen supports."""

    alpha: float
    beta_driver: float
    beta_quality: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "alpha",
            _canonical_bounded_float(self.alpha, support=ALPHA_SUPPORT, name="alpha"),
        )
        object.__setattr__(
            self,
            "beta_driver",
            _canonical_bounded_float(
                self.beta_driver,
                support=BETA_DRIVER_SUPPORT,
                name="beta_driver",
            ),
        )
        object.__setattr__(
            self,
            "beta_quality",
            _canonical_bounded_float(
                self.beta_quality,
                support=BETA_QUALITY_SUPPORT,
                name="beta_quality",
            ),
        )


@dataclass(frozen=True, slots=True)
class JointParameters:
    """Natural-space process and ordered observation parameters."""

    alpha: float
    beta_driver: float
    beta_quality: float
    lambda_quasi: float
    lambda_present: float

    def __post_init__(self) -> None:
        canonical_values = {
            "alpha": _canonical_bounded_float(
                self.alpha,
                support=ALPHA_SUPPORT,
                name="alpha",
            ),
            "beta_driver": _canonical_bounded_float(
                self.beta_driver,
                support=BETA_DRIVER_SUPPORT,
                name="beta_driver",
            ),
            "beta_quality": _canonical_bounded_float(
                self.beta_quality,
                support=BETA_QUALITY_SUPPORT,
                name="beta_quality",
            ),
            "lambda_quasi": _canonical_bounded_float(
                self.lambda_quasi,
                support=LAMBDA_QUASI_SUPPORT,
                name="lambda_quasi",
            ),
            "lambda_present": _canonical_bounded_float(
                self.lambda_present,
                support=LAMBDA_PRESENT_SUPPORT,
                name="lambda_present",
            ),
        }
        for name, value in canonical_values.items():
            object.__setattr__(self, name, value)
        if self.lambda_present <= self.lambda_quasi:
            raise ValueError("lambda_present must be greater than lambda_quasi")

    @property
    def process(self) -> ProcessParameters:
        return ProcessParameters(self.alpha, self.beta_driver, self.beta_quality)

    @property
    def rates(self) -> EffectiveCountRates:
        return EffectiveCountRates(
            lambda_present=self.lambda_present,
            lambda_quasi=self.lambda_quasi,
        )


def canonical_audit_vector(
    design: AuditDesign,
    parameters: JointParameters,
) -> FloatArray:
    """Return canonical log1p-mean then log-zero-probability audit blocks."""

    if type(design) is not AuditDesign:
        raise TypeError("design must be AuditDesign")
    if type(parameters) is not JointParameters:
        raise TypeError("parameters must be JointParameters")
    natural = np.asarray(
        (
            parameters.alpha,
            parameters.beta_driver,
            parameters.beta_quality,
            parameters.lambda_quasi,
            parameters.lambda_present,
        ),
        dtype=np.float64,
    )
    return _audit_vector_from_natural_values(design, natural, require_ordering=True)


def scaled_audit_jacobian(
    design: AuditDesign,
    parameters: JointParameters,
) -> FloatArray:
    """Compute the frozen natural-space central-difference scaled Jacobian."""

    if type(design) is not AuditDesign:
        raise TypeError("design must be AuditDesign")
    if type(parameters) is not JointParameters:
        raise TypeError("parameters must be JointParameters")
    return _scaled_audit_jacobian_from_natural_values(
        design,
        _joint_parameter_vector(parameters),
        require_ordering=True,
    )


def canonical_audit_jacobian_diagnostic(
    design: AuditDesign,
    parameters: JointParameters,
) -> DesignDiagnostic:
    target_id = _canonical_audit_target_id(parameters)
    jacobian = scaled_audit_jacobian(design, parameters)
    return matrix_rank_diagnostic(
        jacobian,
        required_columns=5,
        provenance=f"canonical_noncollision_audit:{design.schedule_id}:{target_id}",
        role="SUPPORTING-LOCAL-NONCOLLISION",
    )


def inverse_audit_rmse(candidate: FloatArray, target: FloatArray) -> float:
    if (
        type(candidate) is not np.ndarray
        or type(target) is not np.ndarray
        or candidate.dtype != np.float64
        or target.dtype != np.float64
        or candidate.ndim != 1
        or candidate.shape != target.shape
        or candidate.size == 0
        or not np.all(np.isfinite(candidate))
        or not np.all(np.isfinite(target))
    ):
        raise ValueError("inverse audit vectors must be aligned finite float64 vectors")
    difference = candidate - target
    value = float(np.sqrt(np.mean(np.square(difference), dtype=np.float64)))
    return _require_finite_likelihood(value)


def scaled_natural_parameter_distance(
    candidate: JointParameters,
    target: JointParameters,
) -> float:
    candidate_values = _joint_parameter_vector(candidate)
    target_values = _joint_parameter_vector(target)
    scaled = np.abs(candidate_values - target_values) / np.asarray(
        NATURAL_PARAMETER_SUPPORT_WIDTHS,
        dtype=np.float64,
    )
    value = float(np.max(scaled))
    return _require_finite_likelihood(value)


def inverse_solution_is_recovery(rmse: float, scaled_distance: float) -> bool:
    residual = _canonical_nonnegative_float(rmse, name="rmse")
    distance = _canonical_nonnegative_float(
        scaled_distance,
        name="scaled_distance",
    )
    return residual <= INVERSE_AUDIT_RMSE_THRESHOLD and distance < (
        INVERSE_AUDIT_DISTANCE_THRESHOLD
    )


def inverse_solution_is_collision(rmse: float, scaled_distance: float) -> bool:
    residual = _canonical_nonnegative_float(rmse, name="rmse")
    distance = _canonical_nonnegative_float(
        scaled_distance,
        name="scaled_distance",
    )
    return residual <= INVERSE_AUDIT_RMSE_THRESHOLD and distance >= (
        INVERSE_AUDIT_DISTANCE_THRESHOLD
    )


def canonical_audit_targets() -> tuple[JointParameters, ...]:
    return (
        JointParameters(-6.0, 1.25, -0.60, 0.15, 4.0),
        JointParameters(-5.0, 0.50, 0.50, 0.30, 2.50),
        JointParameters(-7.0, -0.50, -1.00, 0.60, 6.00),
    )


def run_canonical_inverse_audit(
    design: AuditDesign,
    target: JointParameters,
) -> CanonicalInverseAuditResult:
    """Run one frozen 16-start local/noncollision audit after its rank gate."""

    if type(design) is not AuditDesign:
        raise TypeError("design must be AuditDesign")
    if type(target) is not JointParameters:
        raise TypeError("target must be JointParameters")
    target_id = _canonical_audit_target_id(target)
    if target_id == "custom":
        raise ValueError("inverse audit target must be canonical A, B, or C")
    local_diagnostic = canonical_audit_jacobian_diagnostic(design, target)
    if not local_diagnostic.passed:
        return CanonicalInverseAuditResult(
            schedule_id=design.schedule_id,
            target_id=target_id,
            local_diagnostic=local_diagnostic,
            searches=(),
            successful_search_count=0,
            recovery_count=0,
            collision_count=0,
            passed=False,
            failure_reason="canonical_local_rank_or_condition_failure",
        )
    target_vector = canonical_audit_vector(design, target)
    bounds = optimization_bounds("joint")

    def objective(coordinates: FloatArray) -> float:
        natural = optimization_coordinates_to_natural("joint", coordinates)
        if type(natural) is not JointParameters:
            raise TypeError("joint inverse coordinates did not map to JointParameters")
        candidate_vector = canonical_audit_vector(design, natural)
        return inverse_audit_rmse(candidate_vector, target_vector)

    starts = halton_optimization_starts(16)
    optimizer_attempts = tuple(
        _run_frozen_lbfgsb_start(
            objective,
            starts[start_index - 1],
            bounds=bounds,
            natural_validator=lambda values: optimization_coordinates_to_natural(
                "joint",
                values,
            ),
            start_index=start_index,
        )
        for start_index in range(1, 17)
    )
    searches = tuple(
        _classify_inverse_optimizer_attempt(attempt, target=target)
        for attempt in optimizer_attempts
    )
    successful_count = sum(search.succeeded for search in searches)
    recovery_count = sum(search.recovered for search in searches)
    collision_count = sum(search.collision for search in searches)
    failure_reason = inverse_audit_failure_reason(
        local_diagnostic,
        successful_count,
        recovery_count,
        collision_count,
    )
    return CanonicalInverseAuditResult(
        schedule_id=design.schedule_id,
        target_id=target_id,
        local_diagnostic=local_diagnostic,
        searches=searches,
        successful_search_count=successful_count,
        recovery_count=recovery_count,
        collision_count=collision_count,
        passed=failure_reason is None,
        failure_reason=failure_reason,
    )


def run_nine_audit_preflight(
    designs: tuple[AuditDesign, ...],
) -> NineAuditPreflightResult:
    """Run the complete count-free nine-audit gate before any estimation."""

    if type(designs) is not tuple or len(designs) != 3:
        raise ValueError("designs must contain canonical dense, structured, and sparse designs")
    if tuple(design.schedule_id for design in designs) != (
        "dense",
        "structured",
        "sparse",
    ):
        raise ValueError("designs must be ordered dense, structured, sparse")
    audits = tuple(
        run_canonical_inverse_audit(design, target)
        for design in designs
        for target in canonical_audit_targets()
    )
    observed_counts = {
        (audit.schedule_id, audit.target_id): audit.recovery_count for audit in audits
    }
    if not all(audit.passed for audit in audits):
        failure_reason = "one_or_more_canonical_inverse_audits_failed"
    elif observed_counts != _FROZEN_AUDIT_RECOVERY_COUNTS:
        failure_reason = "canonical_inverse_recovery_counts_differ_from_frozen_frontier"
    elif any(audit.collision_count for audit in audits):
        failure_reason = "canonical_inverse_collision_detected"
    else:
        failure_reason = None
    passed = failure_reason is None
    return _new_nine_audit_preflight_result(
        audits=audits,
        passed=passed,
        estimation_authorized=passed,
        failure_reason=failure_reason,
    )


def equal_emission_fixture(design: AuditDesign) -> RankFailureFixtureResult:
    """Evaluate the real dense design at unrestricted lambda_equal = 1."""

    if type(design) is not AuditDesign or design.schedule_id != "dense":
        raise ValueError("equal_emission_fixture requires the canonical dense design")
    lambda_equal = 1.0
    natural = np.asarray(
        (-6.0, 1.25, -0.60, lambda_equal, lambda_equal),
        dtype=np.float64,
    )
    jacobian = _scaled_audit_jacobian_from_natural_values(
        design,
        natural,
        require_ordering=False,
    )
    diagnostic = matrix_rank_diagnostic(
        jacobian,
        required_columns=5,
        provenance="equal_emission_fixture",
        role="EXPECTED-RANK-FAILURE-CONTROL",
    )
    return RankFailureFixtureResult(
        fixture_id="equal_emission_fixture",
        diagnostic=diagnostic,
        process_derivative_max_abs=float(np.max(np.abs(jacobian[:, :3]))),
        inverse_search_attempted=False,
        control_passed=diagnostic.rank < 5,
    )


def deficient_design_fixture() -> RankFailureFixtureResult:
    schedule = tuple(
        ScheduledOpportunity(
            cell_id=cell_id,
            time=time,
            effort=1.0,
            standardized_quality=0.0,
            predator_arrival_time=None,
        )
        for cell_id in range(32)
        for time in MODEL_TIMES
    )
    design = audit_design_from_schedule(schedule, schedule_id="deficient_design_fixture")
    diagnostic = canonical_audit_jacobian_diagnostic(
        design,
        canonical_audit_targets()[0],
    )
    return RankFailureFixtureResult(
        fixture_id="deficient_design_fixture",
        diagnostic=DesignDiagnostic(
            provenance="deficient_design_fixture",
            role="EXPECTED-RANK-FAILURE-CONTROL",
            n_rows=diagnostic.n_rows,
            n_columns=diagnostic.n_columns,
            rank=diagnostic.rank,
            condition_number=diagnostic.condition_number,
            passed=diagnostic.passed,
            failure_reason=diagnostic.failure_reason,
        ),
        process_derivative_max_abs=None,
        inverse_search_attempted=False,
        control_passed=diagnostic.rank < 5,
    )


def absent_state_support_fixture() -> RankFailureFixtureResult:
    schedule = tuple(
        ScheduledOpportunity(
            cell_id=cell_id,
            time=0,
            effort=1.0,
            standardized_quality=0.0,
            predator_arrival_time=None,
        )
        for cell_id in range(32)
    )
    design = audit_design_from_schedule(schedule, schedule_id="absent_state_support_fixture")
    diagnostic = canonical_audit_jacobian_diagnostic(
        design,
        canonical_audit_targets()[0],
    )
    return RankFailureFixtureResult(
        fixture_id="absent_state_support_fixture",
        diagnostic=DesignDiagnostic(
            provenance="absent_state_support_fixture",
            role="EXPECTED-RANK-FAILURE-CONTROL",
            n_rows=diagnostic.n_rows,
            n_columns=diagnostic.n_columns,
            rank=diagnostic.rank,
            condition_number=diagnostic.condition_number,
            passed=diagnostic.passed,
            failure_reason=diagnostic.failure_reason,
        ),
        process_derivative_max_abs=None,
        inverse_search_attempted=False,
        control_passed=diagnostic.rank < 5,
    )


def inverse_audit_failure_reason(
    local_diagnostic: DesignDiagnostic,
    successful_search_count: int,
    recovery_count: int,
    collision_count: int,
) -> str | None:
    if type(local_diagnostic) is not DesignDiagnostic:
        raise TypeError("local_diagnostic must be DesignDiagnostic")
    counts = (successful_search_count, recovery_count, collision_count)
    if any(type(value) is not int or value < 0 or value > 16 for value in counts):
        raise ValueError("inverse audit counts must be integers from 0 to 16")
    if recovery_count > successful_search_count or collision_count > successful_search_count:
        raise ValueError("inverse audit classifications cannot exceed successful searches")
    if not local_diagnostic.passed:
        return "canonical_local_rank_or_condition_failure"
    if successful_search_count < INVERSE_AUDIT_REQUIRED_SUCCESSES:
        return "fewer_than_twelve_of_sixteen_inverse_searches_succeeded"
    if recovery_count < 1:
        return "no_inverse_search_recovered_target"
    if collision_count:
        return "inverse_audit_collision_detected"
    return None


def profile_nuisance_bounds(
    optimizer_kind: str,
    parameter_name: str,
    target_value: float,
) -> tuple[tuple[float, float], ...]:
    kind = _validate_profile_target(optimizer_kind, parameter_name)
    target = _canonical_profile_target(parameter_name, target_value)
    if kind == "process_oracle":
        target_index = _OPTIMIZER_PARAMETER_NAMES[kind].index(parameter_name)
        return tuple(
            bound for index, bound in enumerate(optimization_bounds(kind)) if index != target_index
        )
    if parameter_name == "lambda_present":
        rates_with_fixed_lambda_present(target, 0.0)
        rate_bounds = ((0.0, 1.0),)
    elif parameter_name == "lambda_quasi":
        rates_with_fixed_lambda_quasi(target, 0.0)
        rate_bounds = ((0.0, 1.0),)
    else:
        target_index = ("alpha", "beta_driver", "beta_quality").index(parameter_name)
        process_bounds = tuple(
            bound
            for index, bound in enumerate(
                (ALPHA_SUPPORT, BETA_DRIVER_SUPPORT, BETA_QUALITY_SUPPORT)
            )
            if index != target_index
        )
        return (*process_bounds, (0.0, 1.0), (0.0, 1.0))
    if kind == "observation_oracle":
        return rate_bounds
    return (ALPHA_SUPPORT, BETA_DRIVER_SUPPORT, BETA_QUALITY_SUPPORT, *rate_bounds)


def profile_nuisance_to_natural(
    optimizer_kind: str,
    parameter_name: str,
    target_value: float,
    nuisance_coordinates: FloatArray,
) -> ProcessParameters | EffectiveCountRates | JointParameters:
    kind = _validate_profile_target(optimizer_kind, parameter_name)
    target = _canonical_profile_target(parameter_name, target_value)
    bounds = profile_nuisance_bounds(kind, parameter_name, target)
    nuisance = _canonical_optimization_coordinates(
        nuisance_coordinates,
        bounds=bounds,
    )
    if kind == "process_oracle":
        values = _insert_fixed_value(
            nuisance,
            index=_OPTIMIZER_PARAMETER_NAMES[kind].index(parameter_name),
            value=target,
        )
        return ProcessParameters(*map(float, values))
    if parameter_name == "lambda_present":
        rates = rates_with_fixed_lambda_present(target, float(nuisance[-1]))
    elif parameter_name == "lambda_quasi":
        rates = rates_with_fixed_lambda_quasi(target, float(nuisance[-1]))
    else:
        target_index = ("alpha", "beta_driver", "beta_quality").index(parameter_name)
        process_values = _insert_fixed_value(
            nuisance[:2],
            index=target_index,
            value=target,
        )
        rates = ordered_rates_from_fractions(
            float(nuisance[-2]),
            float(nuisance[-1]),
        )
        return JointParameters(
            alpha=float(process_values[0]),
            beta_driver=float(process_values[1]),
            beta_quality=float(process_values[2]),
            lambda_quasi=rates.lambda_quasi,
            lambda_present=rates.lambda_present,
        )
    if kind == "observation_oracle":
        return rates
    return JointParameters(
        alpha=float(nuisance[0]),
        beta_driver=float(nuisance[1]),
        beta_quality=float(nuisance[2]),
        lambda_quasi=rates.lambda_quasi,
        lambda_present=rates.lambda_present,
    )


def project_natural_to_profile_nuisance(
    optimizer_kind: str,
    parameter_name: str,
    target_value: float,
    natural: ProcessParameters | EffectiveCountRates | JointParameters,
) -> FloatArray:
    kind = _validate_profile_target(optimizer_kind, parameter_name)
    target = _canonical_profile_target(parameter_name, target_value)
    _validate_natural_type_for_optimizer(kind, natural)
    if kind == "process_oracle":
        process_parameters = cast(ProcessParameters, natural)
        values = np.asarray(
            (
                process_parameters.alpha,
                process_parameters.beta_driver,
                process_parameters.beta_quality,
            ),
            dtype=np.float64,
        )
        target_index = _OPTIMIZER_PARAMETER_NAMES[kind].index(parameter_name)
        return _immutable_float_array(np.delete(values, target_index))
    rates = (
        natural.rates if type(natural) is JointParameters else cast(EffectiveCountRates, natural)
    )
    if parameter_name == "lambda_present":
        q_upper = min(LAMBDA_QUASI_SUPPORT[1], target - RATE_ORDER_GAP)
        fraction = (rates.lambda_quasi - LAMBDA_QUASI_SUPPORT[0]) / (
            q_upper - LAMBDA_QUASI_SUPPORT[0]
        )
        rate_nuisance = project_unit_coordinate(fraction)
    elif parameter_name == "lambda_quasi":
        p_lower = max(LAMBDA_PRESENT_SUPPORT[0], target + RATE_ORDER_GAP)
        fraction = (rates.lambda_present - p_lower) / (LAMBDA_PRESENT_SUPPORT[1] - p_lower)
        rate_nuisance = project_unit_coordinate(fraction)
    else:
        joint = cast(JointParameters, natural)
        fractions = ordered_rate_fractions_from_natural(
            joint.lambda_present,
            joint.lambda_quasi,
        )
        process_values = np.asarray(
            (joint.alpha, joint.beta_driver, joint.beta_quality),
            dtype=np.float64,
        )
        target_index = ("alpha", "beta_driver", "beta_quality").index(parameter_name)
        return _immutable_float_array(
            np.concatenate(
                (
                    np.delete(process_values, target_index),
                    np.asarray((fractions.p_frac, fractions.q_frac), dtype=np.float64),
                )
            )
        )
    rate_array = np.asarray((rate_nuisance,), dtype=np.float64)
    if kind == "observation_oracle":
        return _immutable_float_array(rate_array)
    joint = cast(JointParameters, natural)
    process_array = np.asarray(
        (joint.alpha, joint.beta_driver, joint.beta_quality),
        dtype=np.float64,
    )
    return _immutable_float_array(np.concatenate((process_array, rate_array)))


def build_profile_nuisance_starts(
    optimizer_kind: str,
    parameter_name: str,
    target_value: float,
    *,
    global_natural: ProcessParameters | EffectiveCountRates | JointParameters,
    nearest_natural: ProcessParameters | EffectiveCountRates | JointParameters | None,
) -> tuple[ProfileNuisanceStart, ...]:
    kind = _validate_profile_target(optimizer_kind, parameter_name)
    candidates: list[
        tuple[
            str,
            int,
            ProcessParameters | EffectiveCountRates | JointParameters,
        ]
    ] = [("global_mle", 0, global_natural)]
    if nearest_natural is not None:
        candidates.append(("nearest_same_side", 1, nearest_natural))
    for row, coordinates in enumerate(optimization_starts(kind), start=1):
        candidates.append(
            (
                f"frozen_start_{row}",
                row + 1,
                optimization_coordinates_to_natural(kind, coordinates),
            )
        )
    retained: list[ProfileNuisanceStart] = []
    for source, source_order, natural in candidates:
        try:
            projected = project_natural_to_profile_nuisance(
                kind,
                parameter_name,
                target_value,
                natural,
            )
        except ValueError:
            continue
        if any(
            float(np.max(np.abs(projected - previous.coordinates))) <= START_DEDUPLICATION_TOLERANCE
            for previous in retained
        ):
            continue
        retained.append(
            ProfileNuisanceStart(
                source=source,
                source_order=source_order,
                coordinates=projected,
            )
        )
        if len(retained) == 8:
            break
    return tuple(retained)


def adaptive_profile_target_values(
    parameter_name: str,
    mle: float,
    side: str,
) -> tuple[float, ...]:
    support = _parameter_support(parameter_name)
    mle_value = _canonical_bounded_float(mle, support=support, name="mle")
    if type(side) is not str or side not in {"lower", "upper"}:
        raise ValueError("profile side must be lower or upper")
    bound = support[0] if side == "lower" else support[1]
    direction = -1.0 if side == "lower" else 1.0
    width = support[1] - support[0]
    distance_to_bound = abs(mle_value - bound)
    values: list[float] = []
    step_index = 0
    while True:
        distance = min(
            distance_to_bound,
            PROFILE_STEP_FRACTION * width * PROFILE_STEP_GROWTH**step_index,
        )
        value = bound if distance == distance_to_bound else mle_value + direction * distance
        if not values or value != values[-1]:
            values.append(value)
        if distance == distance_to_bound:
            break
        step_index += 1
    return tuple(values)


def profile_root_value(llmax: float, profile_log_likelihood: float) -> float:
    maximum = _canonical_numeric_float(llmax, name="llmax")
    profile = _canonical_numeric_float(
        profile_log_likelihood,
        name="profile_log_likelihood",
    )
    return 2.0 * (maximum - profile) - PROFILE_LR_CUTOFF


def profile_log_likelihood_exceeds_global_maximum(
    profile_log_likelihood: float,
    llmax: float,
) -> bool:
    return _profile_exceeds_llmax(profile_log_likelihood, llmax)


def practical_identifiability_classification(
    parameter_name: str,
    mle: float,
    *,
    lower_endpoint: float | None,
    upper_endpoint: float | None,
    lower_crossed: bool,
    upper_crossed: bool,
) -> bool:
    support = _parameter_support(parameter_name)
    mle_value = _canonical_bounded_float(mle, support=support, name="mle")
    if type(lower_crossed) is not bool or type(upper_crossed) is not bool:
        raise ValueError("profile crossing indicators must be bool")
    if lower_endpoint is None or upper_endpoint is None:
        return False
    lower = _canonical_bounded_float(
        lower_endpoint,
        support=support,
        name="lower_endpoint",
    )
    upper = _canonical_bounded_float(
        upper_endpoint,
        support=support,
        name="upper_endpoint",
    )
    if lower > mle_value or upper < mle_value:
        raise ValueError("profile endpoints must bracket the MLE")
    width = support[1] - support[0]
    interior = (
        mle_value > support[0] + PROFILE_MLE_INTERIOR_FRACTION * width
        and mle_value < support[1] - PROFILE_MLE_INTERIOR_FRACTION * width
    )
    return lower_crossed and upper_crossed and interior


def profiled_parameter_names(optimizer_kind: str) -> tuple[str, ...]:
    if optimizer_kind == "equal_emission_control":
        return ()
    kind = _validate_optimizer_kind(optimizer_kind)
    return _OPTIMIZER_PARAMETER_NAMES[kind]


def _profile_parameter(
    global_fit: MultiStartFitResult,
    parameter_name: str,
    objective: Callable[[object], float],
) -> ParameterProfileResult:
    """Run one frozen adaptive natural-space profile behind typed public adapters."""

    if type(global_fit) is not MultiStartFitResult:
        raise TypeError("global_fit must be MultiStartFitResult")
    kind = _validate_profile_target(global_fit.optimizer_kind, parameter_name)
    if (
        not global_fit.converged
        or global_fit.best_coordinates is None
        or global_fit.best_log_likelihood is None
    ):
        raise ValueError("global fit must be finite and converged before profiling")
    global_natural = optimization_coordinates_to_natural(
        kind,
        global_fit.best_coordinates,
    )
    mle = _natural_parameter_value(global_natural, parameter_name)
    support = _parameter_support(parameter_name)
    llmax = global_fit.best_log_likelihood
    cache: dict[float, ProfilePointResult] = {}
    lower, lower_invalidation = _run_profile_side(
        kind,
        parameter_name,
        mle,
        "lower",
        llmax,
        global_natural,
        objective,
        cache,
    )
    if lower_invalidation is not None:
        return ParameterProfileResult(
            optimizer_kind=kind,
            parameter_name=parameter_name,
            mle=mle,
            support=support,
            llmax=llmax,
            lower=lower,
            upper=_empty_profile_side("upper"),
            practically_identifiable=False,
            global_fit_valid=False,
            failure_reason=lower_invalidation,
        )
    upper, upper_invalidation = _run_profile_side(
        kind,
        parameter_name,
        mle,
        "upper",
        llmax,
        global_natural,
        objective,
        cache,
    )
    if upper_invalidation is not None:
        return ParameterProfileResult(
            optimizer_kind=kind,
            parameter_name=parameter_name,
            mle=mle,
            support=support,
            llmax=llmax,
            lower=lower,
            upper=upper,
            practically_identifiable=False,
            global_fit_valid=False,
            failure_reason=upper_invalidation,
        )
    practical = practical_identifiability_classification(
        parameter_name,
        mle,
        lower_endpoint=lower.interval_endpoint,
        upper_endpoint=upper.interval_endpoint,
        lower_crossed=lower.crossed_cutoff and not lower.open_side,
        upper_crossed=upper.crossed_cutoff and not upper.open_side,
    )
    return ParameterProfileResult(
        optimizer_kind=kind,
        parameter_name=parameter_name,
        mle=mle,
        support=support,
        llmax=llmax,
        lower=lower,
        upper=upper,
        practically_identifiable=practical,
        global_fit_valid=True,
        failure_reason=None,
    )


def optimization_starts(optimizer_kind: str) -> FloatArray:
    kind = _validate_optimizer_kind(optimizer_kind)
    if kind == "process_oracle":
        return process_oracle_optimization_starts()
    if kind == "observation_oracle":
        return observation_oracle_optimization_starts()
    return global_optimization_starts()


def optimization_bounds(optimizer_kind: str) -> tuple[tuple[float, float], ...]:
    kind = _validate_optimizer_kind(optimizer_kind)
    if kind == "process_oracle":
        return (ALPHA_SUPPORT, BETA_DRIVER_SUPPORT, BETA_QUALITY_SUPPORT)
    if kind == "observation_oracle":
        return ((0.0, 1.0), (0.0, 1.0))
    return (
        ALPHA_SUPPORT,
        BETA_DRIVER_SUPPORT,
        BETA_QUALITY_SUPPORT,
        (0.0, 1.0),
        (0.0, 1.0),
    )


def optimization_coordinates_to_natural(
    optimizer_kind: str,
    coordinates: FloatArray,
) -> ProcessParameters | EffectiveCountRates | JointParameters:
    kind = _validate_optimizer_kind(optimizer_kind)
    canonical = _canonical_optimization_coordinates(
        coordinates,
        bounds=optimization_bounds(kind),
    )
    if kind == "process_oracle":
        return ProcessParameters(
            alpha=float(canonical[0]),
            beta_driver=float(canonical[1]),
            beta_quality=float(canonical[2]),
        )
    if kind == "observation_oracle":
        return ordered_rates_from_fractions(
            p_frac=float(canonical[0]),
            q_frac=float(canonical[1]),
        )
    rates = ordered_rates_from_fractions(
        p_frac=float(canonical[3]),
        q_frac=float(canonical[4]),
    )
    return JointParameters(
        alpha=float(canonical[0]),
        beta_driver=float(canonical[1]),
        beta_quality=float(canonical[2]),
        lambda_quasi=rates.lambda_quasi,
        lambda_present=rates.lambda_present,
    )


def _run_optimizer_start(
    optimizer_kind: str,
    objective: Callable[[FloatArray], float],
    *,
    start_index: int,
    x0: FloatArray,
) -> OptimizerStartResult:
    """Run one global/oracle start through the shared frozen adapter."""

    kind = _validate_optimizer_kind(optimizer_kind)
    bounds = optimization_bounds(kind)
    canonical_start = _canonical_optimization_coordinates(x0, bounds=bounds)
    return _run_frozen_lbfgsb_start(
        objective,
        canonical_start,
        bounds=bounds,
        natural_validator=lambda values: optimization_coordinates_to_natural(kind, values),
        start_index=start_index,
    )


def _run_multistart_optimization(
    optimizer_kind: str,
    objective: Callable[[FloatArray], float],
) -> MultiStartFitResult:
    """Attempt all eight frozen starts and apply the replicate convergence rule."""

    kind = _validate_optimizer_kind(optimizer_kind)
    starts = optimization_starts(kind)
    attempts = tuple(
        _run_optimizer_start(
            kind,
            objective,
            start_index=start_index,
            x0=starts[start_index - 1],
        )
        for start_index in range(1, 9)
    )
    return classify_multistart_attempts(kind, attempts)


def best_two_log_likelihoods_agree(best: float, second: float) -> bool:
    best_value = _canonical_numeric_float(best, name="best_log_likelihood")
    second_value = _canonical_numeric_float(second, name="second_log_likelihood")
    if second_value > best_value:
        raise ValueError("best log likelihood must be at least the second")
    tolerance = 1e-6 * (1.0 + abs(best_value))
    return bool(second_value >= best_value - tolerance)


def classify_multistart_attempts(
    optimizer_kind: str,
    attempts: tuple[OptimizerStartResult, ...],
) -> MultiStartFitResult:
    kind = _validate_optimizer_kind(optimizer_kind)
    if type(attempts) is not tuple or len(attempts) != 8:
        raise ValueError("multistart classification requires exactly eight attempts")
    if tuple(attempt.start_index for attempt in attempts) != tuple(range(1, 9)):
        raise ValueError("multistart attempts must retain start indices 1 through 8")
    successes = tuple(
        sorted(
            (attempt for attempt in attempts if attempt.succeeded),
            key=lambda attempt: (
                -cast(float, attempt.log_likelihood),
                attempt.start_index,
            ),
        )
    )
    success_count = len(successes)
    best = successes[0] if successes else None
    agreement = success_count >= 2 and best_two_log_likelihoods_agree(
        cast(float, successes[0].log_likelihood),
        cast(float, successes[1].log_likelihood),
    )
    converged = success_count >= 6 and agreement
    if success_count < 6:
        failure_reason = "fewer_than_six_of_eight_starts_converged"
    elif not agreement:
        failure_reason = "best_two_log_likelihoods_disagree"
    else:
        failure_reason = None
    return MultiStartFitResult(
        optimizer_kind=kind,
        attempts=attempts,
        ranked_successes=successes,
        converged=converged,
        converged_start_count=success_count,
        best_start_index=best.start_index if best is not None else None,
        best_coordinates=best.coordinates if best is not None else None,
        best_log_likelihood=best.log_likelihood if best is not None else None,
        failure_reason=failure_reason,
    )


@dataclass(frozen=True, slots=True)
class CountOpportunity:
    """One retained analyst-visible count opportunity."""

    time: int
    count: int
    effort: float

    def __post_init__(self) -> None:
        _validate_model_time(self.time)
        if type(self.count) is not int:
            raise ValueError("count must be a nonnegative integer")
        poisson_log_probability(count=self.count, mean=1.0)
        object.__setattr__(self, "effort", _canonical_effort(self.effort))


@dataclass(frozen=True, slots=True)
class AnalystHistory:
    """Truth-free input accepted by the deployable joint likelihood."""

    cell_id: int
    standardized_quality: float
    predator_arrival_time: float | None
    opportunities: tuple[CountOpportunity, ...]

    def __post_init__(self) -> None:
        _validate_cell_id(self.cell_id)
        object.__setattr__(
            self,
            "standardized_quality",
            _canonical_standardized_quality(self.standardized_quality),
        )
        object.__setattr__(
            self,
            "predator_arrival_time",
            _canonical_arrival_time(self.predator_arrival_time),
        )
        object.__setattr__(self, "opportunities", _canonical_opportunities(self.opportunities))


@dataclass(frozen=True, slots=True)
class AnalystBatch:
    """Canonical truth-free arrays used only by the vectorized analyst kernel."""

    cell_ids: IntArray
    standardized_quality: FloatArray
    predator_arrival_time: FloatArray
    counts: IntArray
    efforts: FloatArray
    retained_mask: BoolArray

    def __post_init__(self) -> None:
        _validate_analyst_batch(self)
        object.__setattr__(self, "cell_ids", _immutable_int_array(self.cell_ids))
        object.__setattr__(
            self,
            "standardized_quality",
            _immutable_float_array(self.standardized_quality),
        )
        object.__setattr__(
            self,
            "predator_arrival_time",
            _immutable_float_array(self.predator_arrival_time),
        )
        object.__setattr__(self, "counts", _immutable_int_array(self.counts))
        object.__setattr__(self, "efforts", _immutable_float_array(self.efforts))
        object.__setattr__(self, "retained_mask", _immutable_bool_array(self.retained_mask))


@dataclass(frozen=True, slots=True)
class ProcessOracleOutcome:
    """Oracle-only observed event or right-censor outcome for one cell."""

    cell_id: int
    standardized_quality: float
    predator_arrival_time: float | None
    transition_time: int | None

    def __post_init__(self) -> None:
        _validate_cell_id(self.cell_id)
        object.__setattr__(
            self,
            "standardized_quality",
            _canonical_standardized_quality(self.standardized_quality),
        )
        object.__setattr__(
            self,
            "predator_arrival_time",
            _canonical_arrival_time(self.predator_arrival_time),
        )
        _validate_transition_time(self.transition_time)


@dataclass(frozen=True, slots=True)
class ObservationOracleHistory:
    """Oracle-only retained counts paired with fixed post-transition states."""

    cell_id: int
    opportunities: tuple[CountOpportunity, ...]
    states: tuple[int, ...]

    def __post_init__(self) -> None:
        _validate_cell_id(self.cell_id)
        opportunities = _canonical_opportunities(self.opportunities)
        if type(self.states) is not tuple:
            raise ValueError("states must be a tuple")
        states = tuple(state for state in self.states)
        if len(states) != len(opportunities):
            raise ValueError("states must align one-to-one with opportunities")
        previous_state = 0
        for opportunity, state in zip(opportunities, states, strict=True):
            _validate_state(state)
            if opportunity.time == 0 and state != 0:
                raise ValueError("t0 state must be present")
            if state < previous_state:
                raise ValueError("observation-oracle states must be absorbing")
            previous_state = state
        object.__setattr__(self, "opportunities", opportunities)
        object.__setattr__(self, "states", states)


@dataclass(frozen=True, slots=True)
class LatentProcessTruth:
    """Evaluator-only latent transition truth, never accepted by joint APIs."""

    cell_id: int
    transition_time: int | None

    def __post_init__(self) -> None:
        _validate_cell_id(self.cell_id)
        _validate_transition_time(self.transition_time)

    def state_at(self, time: int) -> int:
        _validate_model_time(time)
        if time == 0 or self.transition_time is None:
            return 0
        return int(time >= self.transition_time)


@dataclass(frozen=True, slots=True)
class ProcessLogPrimitives:
    """Stable interval-level process terms on a prefix of the model grid."""

    interval_end_times: tuple[int, ...]
    driver: FloatArray
    eta: FloatArray
    log_survival: FloatArray
    log_hazard: FloatArray

    def __post_init__(self) -> None:
        if type(self.interval_end_times) is not tuple:
            raise ValueError("interval_end_times must be a tuple")
        interval_count = len(self.interval_end_times)
        _validate_interval_count(interval_count)
        if self.interval_end_times != MODEL_TIMES[1 : interval_count + 1]:
            raise ValueError("interval_end_times must be an exact prefix of t1..t20")
        for endpoint in self.interval_end_times:
            _validate_model_time(endpoint)
        expected_shape = (interval_count,)
        for name in ("driver", "eta", "log_survival", "log_hazard"):
            values = getattr(self, name)
            if type(values) is not np.ndarray:
                raise TypeError(f"{name} must be an exact numpy.ndarray")
            if values.dtype != np.float64 or values.shape != expected_shape:
                raise ValueError(f"{name} must be float64 with shape {expected_shape}")
            _require_finite_array(values, name=name)
            object.__setattr__(self, name, _immutable_float_array(values))


def process_log_primitives(
    *,
    standardized_quality: float,
    predator_arrival_time: float | None,
    parameters: ProcessParameters,
    interval_count: int = _MAX_INTERVAL_COUNT,
) -> ProcessLogPrimitives:
    """Build stable cloglog process terms without materializing probabilities."""

    canonical_quality = _canonical_standardized_quality(standardized_quality)
    canonical_arrival = _canonical_arrival_time(predator_arrival_time)
    _validate_interval_count(interval_count)
    if type(parameters) is not ProcessParameters:
        raise TypeError("parameters must be ProcessParameters")

    interval_end_times = MODEL_TIMES[1 : interval_count + 1]
    time_values = np.asarray(interval_end_times, dtype=np.float64)
    if canonical_arrival is None or not isfinite(canonical_arrival):
        driver = np.zeros(interval_count, dtype=np.float64)
    else:
        driver = np.maximum((time_values - canonical_arrival) / 30.0, 0.0)
    eta = (
        parameters.alpha
        + parameters.beta_driver * driver
        + parameters.beta_quality * canonical_quality
    )
    with np.errstate(over="ignore", under="ignore", divide="ignore", invalid="ignore"):
        exponentiated_eta = np.exp(eta)
        log_survival = -exponentiated_eta
        log_hazard = np.log(-np.expm1(-exponentiated_eta))
    _require_finite_array(driver, name="driver")
    _require_finite_array(eta, name="eta")
    _require_finite_array(log_survival, name="log_survival")
    _require_finite_array(log_hazard, name="log_hazard")
    return ProcessLogPrimitives(
        interval_end_times=interval_end_times,
        driver=driver,
        eta=eta,
        log_survival=log_survival,
        log_hazard=log_hazard,
    )


def hazard_probabilities(primitives: ProcessLogPrimitives) -> FloatArray:
    """Materialize hazards only for diagnostics or direct probability checks."""

    if type(primitives) is not ProcessLogPrimitives:
        raise TypeError("primitives must be ProcessLogPrimitives")
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        hazards = -np.expm1(-np.exp(primitives.eta))
    _require_finite_array(hazards, name="hazard")
    if np.any(hazards <= 0.0) or np.any(hazards > 1.0):
        raise LikelihoodEvaluationError("hazard probabilities are outside (0, 1]")
    return _immutable_float_array(hazards)


def transition_log_path_masses(primitives: ProcessLogPrimitives) -> FloatArray:
    """Return event-at-each-endpoint and final-censor log path masses."""

    if type(primitives) is not ProcessLogPrimitives:
        raise TypeError("primitives must be ProcessLogPrimitives")
    interval_count = len(primitives.interval_end_times)
    log_masses = np.empty(interval_count + 1, dtype=np.float64)
    cumulative_log_survival = 0.0
    for index in range(interval_count):
        log_masses[index] = cumulative_log_survival + primitives.log_hazard[index]
        cumulative_log_survival += primitives.log_survival[index]
    log_masses[-1] = cumulative_log_survival
    _require_finite_array(log_masses, name="transition path mass")
    return _immutable_float_array(log_masses)


def process_oracle_log_likelihood(
    outcome: ProcessOracleOutcome,
    parameters: ProcessParameters,
    *,
    interval_count: int = _MAX_INTERVAL_COUNT,
) -> float:
    """Return the exact event or right-censor process-oracle log likelihood."""

    if type(outcome) is not ProcessOracleOutcome:
        raise TypeError("outcome must be ProcessOracleOutcome")
    primitives = process_log_primitives(
        standardized_quality=outcome.standardized_quality,
        predator_arrival_time=outcome.predator_arrival_time,
        parameters=parameters,
        interval_count=interval_count,
    )
    log_masses = transition_log_path_masses(primitives)
    if outcome.transition_time is None:
        value = float(log_masses[-1])
    else:
        if outcome.transition_time > primitives.interval_end_times[-1]:
            raise ValueError("transition_time is outside requested process horizon")
        value = float(log_masses[outcome.transition_time // 6 - 1])
    return _require_finite_likelihood(value)


def observation_oracle_log_likelihood(
    history: ObservationOracleHistory,
    rates: EffectiveCountRates,
) -> float:
    """Sum shared Poisson-kernel terms conditional on fixed oracle states."""

    if type(history) is not ObservationOracleHistory:
        raise TypeError("history must be ObservationOracleHistory")
    canonical_rates = _canonical_effective_rates(rates)
    value = 0.0
    for opportunity, state in zip(history.opportunities, history.states, strict=True):
        value += state_count_log_probability(
            count=opportunity.count,
            effort=opportunity.effort,
            state=state,
            rates=canonical_rates,
        )
    return _require_finite_likelihood(value)


def joint_log_likelihood_enumeration(
    history: AnalystHistory,
    parameters: JointParameters,
    *,
    interval_count: int = _MAX_INTERVAL_COUNT,
) -> float:
    """Marginalize event and censor paths by direct stable enumeration."""

    path_terms = _joint_log_path_terms(history, parameters, interval_count=interval_count)
    value = float(logsumexp(path_terms))
    return _require_finite_likelihood(value)


def joint_log_likelihood_forward(
    history: AnalystHistory,
    parameters: JointParameters,
    *,
    interval_count: int = _MAX_INTERVAL_COUNT,
) -> float:
    """Marginalize the same model with an independent two-state recursion."""

    _validate_joint_inputs(history, parameters, interval_count=interval_count)
    primitives = process_log_primitives(
        standardized_quality=history.standardized_quality,
        predator_arrival_time=history.predator_arrival_time,
        parameters=parameters.process,
        interval_count=interval_count,
    )
    opportunity_by_time = {opportunity.time: opportunity for opportunity in history.opportunities}

    log_present = 0.0
    baseline_opportunity = opportunity_by_time.get(0)
    if baseline_opportunity is not None:
        log_present += _emission_log_probability(
            baseline_opportunity,
            state=0,
            rates=parameters.rates,
        )
    log_quasi = -np.inf

    for index, endpoint in enumerate(primitives.interval_end_times):
        transitioned = log_present + primitives.log_hazard[index]
        stayed_present = log_present + primitives.log_survival[index]
        stayed_quasi = log_quasi
        next_quasi = float(logsumexp(np.asarray((stayed_quasi, transitioned), dtype=np.float64)))
        next_present = float(stayed_present)

        opportunity = opportunity_by_time.get(endpoint)
        if opportunity is not None:
            next_present += _emission_log_probability(
                opportunity,
                state=0,
                rates=parameters.rates,
            )
            next_quasi += _emission_log_probability(
                opportunity,
                state=1,
                rates=parameters.rates,
            )
        log_present = next_present
        log_quasi = next_quasi

    value = float(logsumexp(np.asarray((log_present, log_quasi), dtype=np.float64)))
    return _require_finite_likelihood(value)


def joint_path_posterior_weights(
    history: AnalystHistory,
    parameters: JointParameters,
    *,
    interval_count: int = _MAX_INTERVAL_COUNT,
) -> FloatArray:
    """Return normalized analyst-only event/censor path weights."""

    path_terms = _joint_log_path_terms(history, parameters, interval_count=interval_count)
    normalizer = float(logsumexp(path_terms))
    _require_finite_likelihood(normalizer)
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        weights = np.exp(path_terms - normalizer)
    _require_finite_array(weights, name="joint path posterior weight")
    total = float(weights.sum(dtype=np.float64))
    if not isfinite(total) or total <= 0.0:
        raise LikelihoodEvaluationError("joint path posterior weights have nonfinite total")
    weights = weights / total
    return _immutable_float_array(weights)


def analyst_batch_from_histories(
    histories: tuple[AnalystHistory, ...],
) -> AnalystBatch:
    """Pack canonical analyst histories into fixed-grid vectorized arrays."""

    canonical = _canonical_analyst_histories(histories)
    cell_count = len(canonical)
    cell_ids = np.empty(cell_count, dtype=np.int64)
    qualities = np.empty(cell_count, dtype=np.float64)
    arrivals = np.empty(cell_count, dtype=np.float64)
    counts = np.zeros((cell_count, len(MODEL_TIMES)), dtype=np.int64)
    efforts = np.zeros((cell_count, len(MODEL_TIMES)), dtype=np.float64)
    retained = np.zeros((cell_count, len(MODEL_TIMES)), dtype=np.bool_)
    for row, history in enumerate(canonical):
        cell_ids[row] = history.cell_id
        qualities[row] = history.standardized_quality
        arrival = history.predator_arrival_time
        arrivals[row] = float(arrival) if arrival is not None and isfinite(arrival) else np.nan
        for opportunity in history.opportunities:
            column = opportunity.time // 6
            counts[row, column] = opportunity.count
            efforts[row, column] = opportunity.effort
            retained[row, column] = True
    return AnalystBatch(
        cell_ids=cell_ids,
        standardized_quality=qualities,
        predator_arrival_time=arrivals,
        counts=counts,
        efforts=efforts,
        retained_mask=retained,
    )


def batched_joint_cell_log_likelihoods(
    batch: AnalystBatch,
    parameters: JointParameters,
    *,
    interval_count: int = _MAX_INTERVAL_COUNT,
) -> FloatArray:
    """Return one independently vectorized marginal log likelihood per cell."""

    path_terms = _batched_joint_log_path_terms(
        batch,
        parameters,
        interval_count=interval_count,
    )
    values = np.asarray(logsumexp(path_terms, axis=1), dtype=np.float64)
    _require_finite_array(values, name="batched joint cell log likelihood")
    return _immutable_float_array(values)


def batched_joint_log_likelihood(
    batch: AnalystBatch,
    parameters: JointParameters,
    *,
    interval_count: int = _MAX_INTERVAL_COUNT,
) -> float:
    """Sum vectorized cell likelihoods in canonical cell order."""

    values = batched_joint_cell_log_likelihoods(
        batch,
        parameters,
        interval_count=interval_count,
    )
    return _require_finite_likelihood(float(values.sum(dtype=np.float64)))


def batched_joint_path_posterior_weights(
    batch: AnalystBatch,
    parameters: JointParameters,
    *,
    interval_count: int = _MAX_INTERVAL_COUNT,
) -> FloatArray:
    """Normalize the vectorized event/censor paths independently by cell."""

    path_terms = _batched_joint_log_path_terms(
        batch,
        parameters,
        interval_count=interval_count,
    )
    normalizers = np.asarray(logsumexp(path_terms, axis=1, keepdims=True), dtype=np.float64)
    _require_finite_array(normalizers, name="batched joint path normalizer")
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        weights = np.exp(path_terms - normalizers)
    totals = weights.sum(axis=1, keepdims=True, dtype=np.float64)
    if not np.all(np.isfinite(totals)) or np.any(totals <= 0.0):
        raise LikelihoodEvaluationError("batched joint path weights have nonfinite totals")
    weights = weights / totals
    _require_finite_array(weights, name="batched joint path posterior weight")
    return _immutable_float_array(np.asarray(weights, dtype=np.float64))


def fit_process_oracle_outcomes(
    outcomes: tuple[ProcessOracleOutcome, ...],
    *,
    preflight: NineAuditPreflightResult,
) -> ProcessOracleFitResult:
    """Fit the process oracle only through its distinct typed outcome surface."""

    if not _nine_audit_preflight_is_authorized(preflight):
        return ProcessOracleFitResult(
            converged=False,
            parameters=None,
            multistart=None,
            at_risk_diagnostic=None,
            failure_class="preflight_or_input_failure",
            failure_reason="nine_audit_preflight_not_authorized",
        )
    canonical = _canonical_process_oracle_outcomes(outcomes)
    if not canonical:
        return ProcessOracleFitResult(
            converged=False,
            parameters=None,
            multistart=None,
            at_risk_diagnostic=None,
            failure_class="preflight_or_input_failure",
            failure_reason="process_oracle_outcomes_empty",
        )
    diagnostic = _process_oracle_outcome_at_risk_diagnostic(canonical)
    if not diagnostic.passed:
        return ProcessOracleFitResult(
            converged=False,
            parameters=None,
            multistart=None,
            at_risk_diagnostic=diagnostic,
            failure_class=(
                "oracle_rank_gate_failure"
                if diagnostic.rank < diagnostic.n_columns
                else "oracle_condition_gate_failure"
            ),
            failure_reason="process_oracle_truth_at_risk_gate_failed",
        )

    def objective(coordinates: FloatArray) -> float:
        natural = optimization_coordinates_to_natural("process_oracle", coordinates)
        if type(natural) is not ProcessParameters:
            raise TypeError("process-oracle coordinates did not map to ProcessParameters")
        return -_process_oracle_log_likelihood_sum(canonical, natural)

    multistart = _run_multistart_optimization("process_oracle", objective)
    if not multistart.converged or multistart.best_coordinates is None:
        failed_diagnostic = DesignDiagnostic(
            provenance="process_oracle_truth_at_risk",
            role="ORACLE-BENCHMARK-ONLY",
            n_rows=diagnostic.n_rows,
            n_columns=3,
            rank=0,
            condition_number=float("inf"),
            passed=False,
            failure_reason="process_oracle_fit_failed_or_nonfinite",
        )
        return ProcessOracleFitResult(
            converged=False,
            parameters=None,
            multistart=multistart,
            at_risk_diagnostic=failed_diagnostic,
            failure_class="optimizer_or_nonfinite_failure",
            failure_reason=multistart.failure_reason or "process_oracle_multistart_fit_failed",
        )
    natural = optimization_coordinates_to_natural(
        "process_oracle",
        multistart.best_coordinates,
    )
    if type(natural) is not ProcessParameters:
        raise TypeError("process-oracle best coordinates did not map to ProcessParameters")
    return ProcessOracleFitResult(
        converged=True,
        parameters=natural,
        multistart=multistart,
        at_risk_diagnostic=diagnostic,
        failure_class=None,
        failure_reason=None,
    )


def fit_observation_oracle_histories(
    histories: tuple[ObservationOracleHistory, ...],
    *,
    preflight: NineAuditPreflightResult,
) -> ObservationOracleFitResult:
    """Fit fixed-state observations only through their distinct oracle surface."""

    if not _nine_audit_preflight_is_authorized(preflight):
        return ObservationOracleFitResult(
            converged=False,
            rates=None,
            multistart=None,
            failure_class="preflight_or_input_failure",
            failure_reason="nine_audit_preflight_not_authorized",
        )
    canonical = _canonical_observation_oracle_histories(histories)
    if not canonical:
        return ObservationOracleFitResult(
            converged=False,
            rates=None,
            multistart=None,
            failure_class="preflight_or_input_failure",
            failure_reason="observation_oracle_histories_empty",
        )

    def objective(coordinates: FloatArray) -> float:
        natural = optimization_coordinates_to_natural("observation_oracle", coordinates)
        if type(natural) is not EffectiveCountRates:
            raise TypeError("observation-oracle coordinates did not map to EffectiveCountRates")
        return -_observation_oracle_log_likelihood_sum(canonical, natural)

    multistart = _run_multistart_optimization("observation_oracle", objective)
    if not multistart.converged or multistart.best_coordinates is None:
        return ObservationOracleFitResult(
            converged=False,
            rates=None,
            multistart=multistart,
            failure_class="optimizer_or_nonfinite_failure",
            failure_reason=multistart.failure_reason or "observation_oracle_multistart_fit_failed",
        )
    natural = optimization_coordinates_to_natural(
        "observation_oracle",
        multistart.best_coordinates,
    )
    if type(natural) is not EffectiveCountRates:
        raise TypeError("observation-oracle best coordinates did not map to EffectiveCountRates")
    return ObservationOracleFitResult(
        converged=True,
        rates=natural,
        multistart=multistart,
        failure_class=None,
        failure_reason=None,
    )


def fit_joint_analyst_histories(
    histories: tuple[AnalystHistory, ...],
    *,
    fit_frame: AnalystFitFrame,
    preflight: NineAuditPreflightResult,
) -> JointFitResult:
    """Fit only analyst-visible histories after the complete audit authorization."""

    if not _nine_audit_preflight_is_authorized(preflight):
        return JointFitResult(
            converged=False,
            parameters=None,
            multistart=None,
            potential_diagnostic=None,
            plugin_diagnostic=None,
            fit_frame=fit_frame,
            fit_frame_cell_count=fit_frame.cell_count,
            fit_frame_sha256=fit_frame.cell_sha256,
            failure_class="preflight_or_input_failure",
            failure_reason="nine_audit_preflight_not_authorized",
        )
    canonical_histories = _canonical_analyst_histories(histories)
    _require_analyst_fit_frame_alignment(canonical_histories, fit_frame)
    potential = matrix_rank_diagnostic(
        _analyst_history_design_matrix(canonical_histories),
        required_columns=3,
        provenance="potential_design",
        role="ANALYST-PREFLIGHT",
    )
    if not potential.passed:
        return JointFitResult(
            converged=False,
            parameters=None,
            multistart=None,
            potential_diagnostic=potential,
            plugin_diagnostic=None,
            fit_frame=fit_frame,
            fit_frame_cell_count=fit_frame.cell_count,
            fit_frame_sha256=fit_frame.cell_sha256,
            failure_class=(
                "potential_rank_gate_failure"
                if potential.rank < potential.n_columns
                else "potential_condition_gate_failure"
            ),
            failure_reason="potential_design_gate_failed",
        )
    batch = analyst_batch_from_histories(canonical_histories)

    def objective(coordinates: FloatArray) -> float:
        natural = optimization_coordinates_to_natural("joint", coordinates)
        if type(natural) is not JointParameters:
            raise TypeError("joint coordinates did not map to JointParameters")
        return -batched_joint_log_likelihood(batch, natural)

    multistart = _run_multistart_optimization("joint", objective)
    if not multistart.converged or multistart.best_coordinates is None:
        plugin = joint_plugin_smoothed_at_risk_diagnostic(canonical_histories, None)
        return JointFitResult(
            converged=False,
            parameters=None,
            multistart=multistart,
            potential_diagnostic=potential,
            plugin_diagnostic=plugin,
            fit_frame=fit_frame,
            fit_frame_cell_count=fit_frame.cell_count,
            fit_frame_sha256=fit_frame.cell_sha256,
            failure_class="optimizer_or_nonfinite_failure",
            failure_reason=multistart.failure_reason or "joint_multistart_fit_failed",
        )
    natural = optimization_coordinates_to_natural("joint", multistart.best_coordinates)
    if type(natural) is not JointParameters:
        raise TypeError("joint best coordinates did not map to JointParameters")
    plugin = joint_plugin_smoothed_at_risk_diagnostic(canonical_histories, natural)
    if not plugin.passed:
        return JointFitResult(
            converged=False,
            parameters=None,
            multistart=multistart,
            potential_diagnostic=potential,
            plugin_diagnostic=plugin,
            fit_frame=fit_frame,
            fit_frame_cell_count=fit_frame.cell_count,
            fit_frame_sha256=fit_frame.cell_sha256,
            failure_class=(
                "plugin_rank_gate_failure"
                if plugin.rank < plugin.n_columns
                else "plugin_condition_gate_failure"
            ),
            failure_reason="joint_plugin_design_gate_failed",
        )
    return JointFitResult(
        converged=True,
        parameters=natural,
        multistart=multistart,
        potential_diagnostic=potential,
        plugin_diagnostic=plugin,
        fit_frame=fit_frame,
        fit_frame_cell_count=fit_frame.cell_count,
        fit_frame_sha256=fit_frame.cell_sha256,
        failure_class=None,
        failure_reason=None,
    )


def profile_process_oracle_outcomes(
    outcomes: tuple[ProcessOracleOutcome, ...],
    fit: ProcessOracleFitResult,
    parameter_name: str,
    *,
    preflight: NineAuditPreflightResult,
) -> ParameterProfileResult:
    """Profile one process parameter from exact typed oracle outcomes."""

    if not _nine_audit_preflight_is_authorized(preflight):
        raise ValueError("complete nine-audit preflight must authorize profiling")
    canonical = _canonical_process_oracle_outcomes(outcomes)
    if type(fit) is not ProcessOracleFitResult:
        raise TypeError("fit must be ProcessOracleFitResult")
    fit.__post_init__()
    if not fit.converged or fit.multistart is None:
        raise ValueError("process-oracle fit must be converged before profiling")

    def objective(parameters: object) -> float:
        if type(parameters) is not ProcessParameters:
            raise TypeError("process-oracle profile requires ProcessParameters")
        return -_process_oracle_log_likelihood_sum(canonical, parameters)

    return _profile_parameter(fit.multistart, parameter_name, objective)


def profile_observation_oracle_histories(
    histories: tuple[ObservationOracleHistory, ...],
    fit: ObservationOracleFitResult,
    parameter_name: str,
    *,
    preflight: NineAuditPreflightResult,
) -> ParameterProfileResult:
    """Profile one rate from exact typed fixed-state oracle histories."""

    if not _nine_audit_preflight_is_authorized(preflight):
        raise ValueError("complete nine-audit preflight must authorize profiling")
    canonical = _canonical_observation_oracle_histories(histories)
    if type(fit) is not ObservationOracleFitResult:
        raise TypeError("fit must be ObservationOracleFitResult")
    fit.__post_init__()
    if not fit.converged or fit.multistart is None:
        raise ValueError("observation-oracle fit must be converged before profiling")

    def objective(parameters: object) -> float:
        if type(parameters) is not EffectiveCountRates:
            raise TypeError("observation-oracle profile requires EffectiveCountRates")
        return -_observation_oracle_log_likelihood_sum(canonical, parameters)

    return _profile_parameter(fit.multistart, parameter_name, objective)


def profile_joint_analyst_histories(
    histories: tuple[AnalystHistory, ...],
    fit: JointFitResult,
    parameter_name: str,
    *,
    preflight: NineAuditPreflightResult,
) -> ParameterProfileResult:
    """Profile one joint parameter from analyst-only batched histories."""

    if not _nine_audit_preflight_is_authorized(preflight):
        raise ValueError("complete nine-audit preflight must authorize profiling")
    canonical = _canonical_analyst_histories(histories)
    if type(fit) is not JointFitResult:
        raise TypeError("fit must be JointFitResult")
    fit.__post_init__()
    _require_analyst_fit_frame_alignment(canonical, fit.fit_frame)
    if (
        not fit.converged
        or type(fit.parameters) is not JointParameters
        or type(fit.multistart) is not MultiStartFitResult
        or not fit.multistart.converged
        or type(fit.potential_diagnostic) is not DesignDiagnostic
        or not fit.potential_diagnostic.passed
        or type(fit.plugin_diagnostic) is not DesignDiagnostic
        or not fit.plugin_diagnostic.passed
        or fit.failure_reason is not None
    ):
        raise ValueError("joint fit and analyst design gates must pass before profiling")
    batch = analyst_batch_from_histories(canonical)

    def objective(parameters: object) -> float:
        if type(parameters) is not JointParameters:
            raise TypeError("joint profile requires JointParameters")
        return -batched_joint_log_likelihood(batch, parameters)

    return _profile_parameter(fit.multistart, parameter_name, objective)


def _joint_log_path_terms(
    history: AnalystHistory,
    parameters: JointParameters,
    *,
    interval_count: int,
) -> FloatArray:
    _validate_joint_inputs(history, parameters, interval_count=interval_count)
    primitives = process_log_primitives(
        standardized_quality=history.standardized_quality,
        predator_arrival_time=history.predator_arrival_time,
        parameters=parameters.process,
        interval_count=interval_count,
    )
    path_terms = transition_log_path_masses(primitives).copy()
    for path_index in range(interval_count + 1):
        transition_time = (
            primitives.interval_end_times[path_index] if path_index < interval_count else None
        )
        for opportunity in history.opportunities:
            state = _path_state_at(opportunity.time, transition_time=transition_time)
            path_terms[path_index] += _emission_log_probability(
                opportunity,
                state=state,
                rates=parameters.rates,
            )
    _require_finite_array(path_terms, name="joint log path term")
    return _immutable_float_array(path_terms)


def _batched_joint_log_path_terms(
    batch: AnalystBatch,
    parameters: JointParameters,
    *,
    interval_count: int,
) -> FloatArray:
    if type(batch) is not AnalystBatch:
        raise TypeError("batch must be AnalystBatch")
    if type(parameters) is not JointParameters:
        raise TypeError("parameters must be JointParameters")
    _validate_interval_count(interval_count)
    if np.any(batch.retained_mask[:, interval_count + 1 :]):
        raise ValueError("batch contains an opportunity after requested process horizon")

    cell_count = len(batch.cell_ids)
    endpoints = np.asarray(MODEL_TIMES[1 : interval_count + 1], dtype=np.float64)
    driver = np.zeros((cell_count, interval_count), dtype=np.float64)
    finite_arrival = np.isfinite(batch.predator_arrival_time)
    driver[finite_arrival] = np.maximum(
        (endpoints[np.newaxis, :] - batch.predator_arrival_time[finite_arrival, np.newaxis]) / 30.0,
        0.0,
    )
    eta = (
        parameters.alpha
        + parameters.beta_driver * driver
        + parameters.beta_quality * batch.standardized_quality[:, np.newaxis]
    )
    with np.errstate(over="ignore", under="ignore", divide="ignore", invalid="ignore"):
        exp_eta = np.exp(eta)
        log_survival = -exp_eta
        log_hazard = np.log(-np.expm1(-exp_eta))
    _require_finite_array(eta, name="batched joint eta")
    _require_finite_array(log_survival, name="batched joint log survival")
    _require_finite_array(log_hazard, name="batched joint log hazard")

    survival_prefix = np.zeros((cell_count, interval_count + 1), dtype=np.float64)
    survival_prefix[:, 1:] = np.cumsum(log_survival, axis=1, dtype=np.float64)
    process_terms = np.empty((cell_count, interval_count + 1), dtype=np.float64)
    process_terms[:, :interval_count] = survival_prefix[:, :interval_count] + log_hazard
    process_terms[:, -1] = survival_prefix[:, -1]

    time_slice = slice(0, interval_count + 1)
    mask = batch.retained_mask[:, time_slice]
    counts = batch.counts[:, time_slice]
    efforts = batch.efforts[:, time_slice]
    present_emission = np.zeros(mask.shape, dtype=np.float64)
    quasi_emission = np.zeros(mask.shape, dtype=np.float64)
    if np.any(mask):
        retained_counts = counts[mask]
        retained_efforts = efforts[mask]
        present_emission[mask] = _vectorized_poisson_log_probability(
            retained_counts,
            retained_efforts * parameters.lambda_present,
        )
        quasi_emission[mask] = _vectorized_poisson_log_probability(
            retained_counts,
            retained_efforts * parameters.lambda_quasi,
        )
    total_present = present_emission.sum(axis=1, dtype=np.float64)
    differences = quasi_emission[:, 1:] - present_emission[:, 1:]
    suffix_differences = np.flip(
        np.cumsum(np.flip(differences, axis=1), axis=1, dtype=np.float64),
        axis=1,
    )
    emission_terms = np.empty_like(process_terms)
    emission_terms[:, :interval_count] = total_present[:, np.newaxis] + suffix_differences
    emission_terms[:, -1] = total_present
    path_terms = process_terms + emission_terms
    _require_finite_array(path_terms, name="batched joint log path term")
    return _immutable_float_array(path_terms)


def _vectorized_poisson_log_probability(counts: IntArray, means: FloatArray) -> FloatArray:
    if np.any(means <= 0.0) or np.any(means > 1_000_000_000) or not np.all(np.isfinite(means)):
        raise LikelihoodEvaluationError("batched Poisson mean is outside computational domain")
    values = (
        counts.astype(np.float64) * np.log(means) - means - gammaln(counts.astype(np.float64) + 1.0)
    )
    values = np.asarray(values, dtype=np.float64)
    _require_finite_array(values, name="batched Poisson log probability")
    return values


def _emission_log_probability(
    opportunity: CountOpportunity,
    *,
    state: int,
    rates: EffectiveCountRates,
) -> float:
    value = state_count_log_probability(
        count=opportunity.count,
        effort=opportunity.effort,
        state=state,
        rates=rates,
    )
    return _require_finite_likelihood(value)


def _path_state_at(time: int, *, transition_time: int | None) -> int:
    if time == 0 or transition_time is None:
        return 0
    return int(time >= transition_time)


def _validate_joint_inputs(
    history: AnalystHistory,
    parameters: JointParameters,
    *,
    interval_count: int,
) -> None:
    if type(history) is not AnalystHistory:
        raise TypeError("history must be AnalystHistory")
    if type(parameters) is not JointParameters:
        raise TypeError("parameters must be JointParameters")
    _validate_interval_count(interval_count)
    process_horizon = MODEL_TIMES[interval_count]
    if history.opportunities and history.opportunities[-1].time > process_horizon:
        raise ValueError("history contains an opportunity after requested process horizon")


def _validate_rng_payload_fields(payload: RngPayload) -> None:
    if type(payload.goal) is not str or payload.goal != "023":
        raise ValueError("goal must be the string 023")
    if type(payload.master_seed) is not int or payload.master_seed != MASTER_SEED:
        raise ValueError(f"master_seed must be the integer {MASTER_SEED}")
    if type(payload.scenario_id) is not str or payload.scenario_id not in SCENARIO_IDS:
        raise ValueError("scenario_id must be a canonical scenario")
    if type(payload.split) is not str or payload.split not in {
        "development",
        "calibration",
        "holdout",
    }:
        raise ValueError("split must be development, calibration, or holdout")
    if payload.split == "holdout":
        raise ValueError("holdout payload construction remains locked before immutable freeze")
    if type(payload.component) is not str or payload.component not in RNG_COMPONENTS:
        raise ValueError("component must be a canonical component")
    if type(payload.replicate_index) is not int:
        raise ValueError("replicate_index must be a zero-based integer")
    if payload.draw_index is not None and type(payload.draw_index) is not int:
        raise ValueError("draw_index must be a zero-based integer or null")

    if payload.component in _DRAW_COMPONENTS:
        if (
            type(payload.draw_index) is not int
            or payload.draw_index < 0
            or payload.draw_index > 198
        ):
            raise ValueError("draw_index must be an integer from 0 to 198")
    elif payload.draw_index is not None:
        raise ValueError("base component payloads require draw_index null")

    if payload.component == "bootstrap":
        if (
            payload.scenario_id != "no_emission_contrast_negative_control"
            or payload.split != "development"
            or payload.draw_index != 0
            or payload.replicate_index < 0
            or payload.replicate_index > 23
        ):
            raise ValueError("bootstrap payload is outside the timing-only development exception")
        return

    allowed_components = {"process"}
    if payload.scenario_id in _COUNT_SCENARIOS:
        allowed_components.update(
            {
                "schedule",
                "observation",
                "pit_randomization",
                "predictive_reference",
            }
        )
    if payload.scenario_id == "informative_dropout_misspecification_stress":
        allowed_components.add("dropout")
    if payload.scenario_id == "spatial_frailty_stress":
        allowed_components.add("frailty")
    if payload.component not in allowed_components:
        raise ValueError("component is not valid for scenario_id")

    if payload.split == "calibration":
        if payload.scenario_id not in NESTED_SCENARIOS:
            raise ValueError("scenario_id has no calibration split")
        replicate_limit = 24
    elif payload.scenario_id == "no_emission_contrast_negative_control" and payload.component in {
        "process",
        "observation",
    }:
        replicate_limit = 24
    else:
        replicate_limit = 12
    if payload.replicate_index < 0 or payload.replicate_index >= replicate_limit:
        raise ValueError(
            f"replicate_index must be from 0 to {replicate_limit - 1} for this partition"
        )


def _canonical_design_cells(cells: tuple[DesignCell, ...]) -> tuple[DesignCell, ...]:
    if type(cells) is not tuple:
        raise ValueError("cells must be a tuple")
    canonical: list[DesignCell] = []
    previous_cell_id = -1
    for cell in cells:
        if type(cell) is not DesignCell:
            raise TypeError("cells must contain exact DesignCell values")
        if cell.cell_id <= previous_cell_id:
            raise ValueError("cells must be strictly sorted by cell_id")
        previous_cell_id = cell.cell_id
        canonical.append(
            DesignCell(
                cell_id=cell.cell_id,
                standardized_quality=cell.standardized_quality,
                predator_arrival_time=cell.predator_arrival_time,
                row_band=cell.row_band,
            )
        )
    return tuple(canonical)


def _canonical_schedule(
    schedule: tuple[ScheduledOpportunity, ...],
) -> tuple[ScheduledOpportunity, ...]:
    if type(schedule) is not tuple:
        raise ValueError("schedule must be a tuple")
    canonical: list[ScheduledOpportunity] = []
    previous_key = (-1, -1)
    metadata_by_cell: dict[int, tuple[float, float | None]] = {}
    for opportunity in schedule:
        if type(opportunity) is not ScheduledOpportunity:
            raise TypeError("schedule must contain exact ScheduledOpportunity values")
        key = (opportunity.cell_id, opportunity.time)
        if key <= previous_key:
            raise ValueError("schedule must be in canonical opportunity order")
        previous_key = key
        metadata = (
            opportunity.standardized_quality,
            opportunity.predator_arrival_time,
        )
        if (
            opportunity.cell_id in metadata_by_cell
            and metadata_by_cell[opportunity.cell_id] != metadata
        ):
            raise ValueError("cell covariates must be constant across scheduled opportunities")
        metadata_by_cell[opportunity.cell_id] = metadata
        canonical.append(
            ScheduledOpportunity(
                cell_id=opportunity.cell_id,
                time=opportunity.time,
                effort=opportunity.effort,
                standardized_quality=opportunity.standardized_quality,
                predator_arrival_time=opportunity.predator_arrival_time,
            )
        )
    return tuple(canonical)


def _validate_uniform_draws(values: object, *, expected_shape: tuple[int, int]) -> None:
    if (
        type(values) is not np.ndarray
        or values.dtype != np.float64
        or values.shape != expected_shape
        or not values.flags.c_contiguous
    ):
        raise ValueError(f"process uniforms must be C-order float64 with shape {expected_shape}")
    if not np.all(np.isfinite(values)) or np.any(values < 0.0) or np.any(values >= 1.0):
        raise ValueError("process uniforms must be finite values in [0, 1)")


def _validate_poisson_draws(values: object, *, expected_shape: tuple[int, ...]) -> None:
    if (
        type(values) is not np.ndarray
        or values.shape != expected_shape
        or not np.issubdtype(values.dtype, np.integer)
        or not values.flags.c_contiguous
    ):
        raise ValueError(
            f"Poisson draws must be a C-order integer array with shape {expected_shape}"
        )
    for value in values:
        poisson_log_probability(count=int(value), mean=1.0)


def _validate_process_simulation_truth(result: ProcessSimulationTruth) -> None:
    if (
        type(result.cell_ids) is not np.ndarray
        or result.cell_ids.dtype != np.int64
        or result.cell_ids.ndim != 1
    ):
        raise ValueError("cell_ids must be a one-dimensional int64 ndarray")
    cell_count = len(result.cell_ids)
    if (
        type(result.states) is not np.ndarray
        or result.states.dtype != np.float64
        or result.states.shape != (cell_count, len(MODEL_TIMES))
    ):
        raise ValueError(f"states must be float64 with shape ({cell_count}, {len(MODEL_TIMES)})")
    if (
        type(result.transition_times) is not np.ndarray
        or result.transition_times.dtype != np.float64
        or result.transition_times.shape != (cell_count,)
    ):
        raise ValueError(f"transition_times must be float64 with shape ({cell_count},)")
    if cell_count and (
        np.any(np.diff(result.cell_ids) <= 0)
        or np.any(result.cell_ids < 0)
        or np.any(result.cell_ids > _MAX_CELL_ID)
    ):
        raise ValueError("cell_ids must be unique, sorted, and inside the canonical domain")
    if not np.all(np.isfinite(result.states)) or np.any(
        (result.states != 0.0) & (result.states != 1.0)
    ):
        raise ValueError("states must contain only finite binary float64 values")
    if np.any(result.states[:, 0] != 0.0) or np.any(np.diff(result.states, axis=1) < 0.0):
        raise ValueError("states must start present and remain absorbing")
    for row, transition_time in enumerate(result.transition_times):
        if np.isnan(transition_time):
            if np.any(result.states[row] != 0.0):
                raise ValueError("censored transition_times must align with all-present states")
            continue
        if not np.isfinite(transition_time) or float(transition_time) not in MODEL_TIMES[1:]:
            raise ValueError("transition_times must be t1..t20 or NaN censoring")
        transition_index = int(transition_time // 6)
        expected = np.zeros(len(MODEL_TIMES), dtype=np.float64)
        expected[transition_index:] = 1.0
        if not np.array_equal(result.states[row], expected):
            raise ValueError("transition_times must align with post-transition states")


def _validate_analyst_batch(batch: AnalystBatch) -> None:
    if (
        type(batch.cell_ids) is not np.ndarray
        or batch.cell_ids.dtype != np.int64
        or batch.cell_ids.ndim != 1
    ):
        raise ValueError("batch cell_ids must be a one-dimensional int64 ndarray")
    cell_count = len(batch.cell_ids)
    if cell_count and (
        np.any(np.diff(batch.cell_ids) <= 0)
        or np.any(batch.cell_ids < 0)
        or np.any(batch.cell_ids > _MAX_CELL_ID)
    ):
        raise ValueError("batch cell_ids must be unique, sorted, and canonical")
    for name in ("standardized_quality", "predator_arrival_time"):
        values = getattr(batch, name)
        if (
            type(values) is not np.ndarray
            or values.dtype != np.float64
            or values.shape != (cell_count,)
        ):
            raise ValueError(f"batch {name} must be float64 with shape ({cell_count},)")
    if not np.all(np.isfinite(batch.standardized_quality)):
        raise ValueError("batch standardized_quality must be finite")
    if np.any(np.isinf(batch.predator_arrival_time)):
        raise ValueError("batch predator_arrival_time must be finite or NaN")
    expected_shape = (cell_count, len(MODEL_TIMES))
    if (
        type(batch.counts) is not np.ndarray
        or batch.counts.dtype != np.int64
        or batch.counts.shape != expected_shape
    ):
        raise ValueError(f"batch counts must be int64 with shape {expected_shape}")
    if (
        type(batch.efforts) is not np.ndarray
        or batch.efforts.dtype != np.float64
        or batch.efforts.shape != expected_shape
    ):
        raise ValueError(f"batch efforts must be float64 with shape {expected_shape}")
    if (
        type(batch.retained_mask) is not np.ndarray
        or batch.retained_mask.dtype != np.bool_
        or batch.retained_mask.shape != expected_shape
    ):
        raise ValueError(f"batch retained_mask must be bool with shape {expected_shape}")
    if np.any(batch.counts < 0) or np.any(batch.counts > 1_000_000_000):
        raise ValueError("batch counts are outside the computational domain")
    if not np.all(np.isfinite(batch.efforts)) or np.any(batch.efforts < 0.0):
        raise ValueError("batch efforts must be finite and nonnegative")
    if np.any(batch.efforts[batch.retained_mask] <= 0.0):
        raise ValueError("retained batch efforts must be positive")
    if np.any(batch.counts[~batch.retained_mask] != 0) or np.any(
        batch.efforts[~batch.retained_mask] != 0.0
    ):
        raise ValueError("unretained batch entries must have zero count and effort")


def _validate_audit_design(design: AuditDesign) -> None:
    if type(design.schedule_id) is not str or not design.schedule_id:
        raise ValueError("audit schedule_id must be a nonempty string")
    if (
        type(design.cell_ids) is not np.ndarray
        or design.cell_ids.dtype != np.int64
        or design.cell_ids.ndim != 1
        or len(design.cell_ids) == 0
    ):
        raise ValueError("audit cell_ids must be a nonempty one-dimensional int64 array")
    cell_count = len(design.cell_ids)
    if (
        np.any(np.diff(design.cell_ids) <= 0)
        or np.any(design.cell_ids < 0)
        or np.any(design.cell_ids > _MAX_CELL_ID)
    ):
        raise ValueError("audit cell_ids must be unique, sorted, and canonical")
    for name in ("standardized_quality", "predator_arrival_time"):
        values = getattr(design, name)
        if (
            type(values) is not np.ndarray
            or values.dtype != np.float64
            or values.shape != (cell_count,)
        ):
            raise ValueError(f"audit {name} must be float64 with shape ({cell_count},)")
    if not np.all(np.isfinite(design.standardized_quality)):
        raise ValueError("audit standardized_quality must be finite")
    if np.any(np.isinf(design.predator_arrival_time)):
        raise ValueError("audit predator_arrival_time must be finite or NaN")
    opportunity_count = len(design.efforts)
    if opportunity_count == 0:
        raise ValueError("audit design must contain opportunities")
    for name in ("opportunity_cell_index", "opportunity_time_index"):
        values = getattr(design, name)
        if (
            type(values) is not np.ndarray
            or values.dtype != np.int64
            or values.shape != (opportunity_count,)
        ):
            raise ValueError(f"audit {name} must be int64 with shape ({opportunity_count},)")
    if (
        type(design.efforts) is not np.ndarray
        or design.efforts.dtype != np.float64
        or design.efforts.shape != (opportunity_count,)
        or not np.all(np.isfinite(design.efforts))
        or np.any(design.efforts <= 0.0)
    ):
        raise ValueError("audit efforts must be finite positive float64 values")
    if np.any(design.opportunity_cell_index < 0) or np.any(
        design.opportunity_cell_index >= cell_count
    ):
        raise ValueError("audit opportunity cell index is outside the design")
    if np.any(design.opportunity_time_index < 0) or np.any(
        design.opportunity_time_index >= len(MODEL_TIMES)
    ):
        raise ValueError("audit opportunity time index is outside the model grid")
    canonical_keys = (
        design.opportunity_cell_index * len(MODEL_TIMES) + design.opportunity_time_index
    )
    if np.any(np.diff(canonical_keys) <= 0):
        raise ValueError("audit opportunities must be in canonical cell-time order")
    if not np.array_equal(
        np.unique(design.opportunity_cell_index),
        np.arange(cell_count, dtype=np.int64),
    ):
        raise ValueError("every audit cell must have at least one opportunity")


def _require_truth_alignment(
    cells: tuple[DesignCell, ...],
    process_result: ProcessSimulationTruth,
) -> None:
    if type(process_result) is not ProcessSimulationTruth:
        raise TypeError("process_result must be ProcessSimulationTruth")
    expected = np.asarray([cell.cell_id for cell in cells], dtype=np.int64)
    if not np.array_equal(process_result.cell_ids, expected):
        raise ValueError("process_result cell_ids must exactly align with cells")


def _potential_design_matrix(cells: tuple[DesignCell, ...]) -> FloatArray:
    matrix = np.empty((len(cells) * _MAX_INTERVAL_COUNT, 3), dtype=np.float64)
    row = 0
    for cell in cells:
        for endpoint in MODEL_TIMES[1:]:
            if cell.predator_arrival_time is None or not isfinite(cell.predator_arrival_time):
                driver = 0.0
            else:
                driver = max((endpoint - cell.predator_arrival_time) / 30.0, 0.0)
            matrix[row] = (1.0, driver, cell.standardized_quality)
            row += 1
    return matrix


def _canonical_process_oracle_outcomes(
    outcomes: tuple[ProcessOracleOutcome, ...],
) -> tuple[ProcessOracleOutcome, ...]:
    if type(outcomes) is not tuple:
        raise ValueError("process-oracle outcomes must be a tuple")
    previous_cell_id = -1
    for outcome in outcomes:
        if type(outcome) is not ProcessOracleOutcome:
            raise TypeError("outcomes must contain exact ProcessOracleOutcome values")
        if outcome.cell_id <= previous_cell_id:
            raise ValueError("process-oracle outcomes must be strictly sorted by cell_id")
        previous_cell_id = outcome.cell_id
    return outcomes


def _process_oracle_outcome_at_risk_diagnostic(
    outcomes: tuple[ProcessOracleOutcome, ...],
) -> DesignDiagnostic:
    rows: list[tuple[float, float, float]] = []
    for outcome in outcomes:
        for endpoint in MODEL_TIMES[1:]:
            if outcome.transition_time is not None and endpoint > outcome.transition_time:
                break
            arrival = outcome.predator_arrival_time
            driver = (
                0.0
                if arrival is None or not isfinite(arrival)
                else max((endpoint - arrival) / 30.0, 0.0)
            )
            rows.append((1.0, driver, outcome.standardized_quality))
    matrix = np.asarray(rows, dtype=np.float64)
    return _design_diagnostic(
        matrix,
        provenance="process_oracle_truth_at_risk",
        role="ORACLE-BENCHMARK-ONLY",
    )


def _process_oracle_log_likelihood_sum(
    outcomes: tuple[ProcessOracleOutcome, ...],
    parameters: ProcessParameters,
) -> float:
    value = 0.0
    for outcome in outcomes:
        value += process_oracle_log_likelihood(outcome, parameters)
    return _require_finite_likelihood(value)


def _canonical_observation_oracle_histories(
    histories: tuple[ObservationOracleHistory, ...],
) -> tuple[ObservationOracleHistory, ...]:
    if type(histories) is not tuple:
        raise ValueError("observation-oracle histories must be a tuple")
    previous_cell_id = -1
    for history in histories:
        if type(history) is not ObservationOracleHistory:
            raise TypeError("histories must contain exact ObservationOracleHistory values")
        if history.cell_id <= previous_cell_id:
            raise ValueError("observation-oracle histories must be strictly sorted by cell_id")
        previous_cell_id = history.cell_id
    return histories


def _observation_oracle_log_likelihood_sum(
    histories: tuple[ObservationOracleHistory, ...],
    rates: EffectiveCountRates,
) -> float:
    value = 0.0
    for history in histories:
        value += observation_oracle_log_likelihood(history, rates)
    return _require_finite_likelihood(value)


def _canonical_analyst_histories(
    histories: tuple[AnalystHistory, ...],
) -> tuple[AnalystHistory, ...]:
    if type(histories) is not tuple:
        raise ValueError("histories must be a tuple")
    previous_cell_id = -1
    for history in histories:
        if type(history) is not AnalystHistory:
            raise TypeError("histories must contain exact AnalystHistory values")
        if history.cell_id <= previous_cell_id:
            raise ValueError("histories must be strictly sorted by cell_id")
        previous_cell_id = history.cell_id
    return histories


def _analyst_history_design_matrix(histories: tuple[AnalystHistory, ...]) -> FloatArray:
    matrix = np.empty((len(histories) * _MAX_INTERVAL_COUNT, 3), dtype=np.float64)
    row = 0
    for history in histories:
        for endpoint in MODEL_TIMES[1:]:
            if history.predator_arrival_time is None or not isfinite(history.predator_arrival_time):
                driver = 0.0
            else:
                driver = max((endpoint - history.predator_arrival_time) / 30.0, 0.0)
            matrix[row] = (1.0, driver, history.standardized_quality)
            row += 1
    return matrix


def _design_diagnostic(
    matrix: FloatArray,
    *,
    provenance: str,
    role: str,
) -> DesignDiagnostic:
    return matrix_rank_diagnostic(
        matrix,
        required_columns=matrix.shape[1],
        provenance=provenance,
        role=role,
    )


def _audit_vector_from_natural_values(
    design: AuditDesign,
    natural: FloatArray,
    *,
    require_ordering: bool,
) -> FloatArray:
    values = _canonical_audit_natural_values(
        natural,
        require_ordering=require_ordering,
    )
    alpha, beta_driver, beta_quality, lambda_quasi, lambda_present = values
    if lambda_present == lambda_quasi:
        log1p_mu = np.log1p(design.efforts * lambda_present)
        log_p0 = -design.efforts * lambda_present
        vector = np.concatenate((log1p_mu, log_p0)).astype(np.float64, copy=False)
        _require_finite_array(vector, name="equal-emission audit vector")
        return _immutable_float_array(vector)
    cell_count = len(design.cell_ids)
    endpoints = np.asarray(MODEL_TIMES[1:], dtype=np.float64)
    driver = np.zeros((cell_count, _MAX_INTERVAL_COUNT), dtype=np.float64)
    finite_arrival = np.isfinite(design.predator_arrival_time)
    driver[finite_arrival] = np.maximum(
        (endpoints[np.newaxis, :] - design.predator_arrival_time[finite_arrival, np.newaxis])
        / 30.0,
        0.0,
    )
    eta = alpha + beta_driver * driver + beta_quality * design.standardized_quality[:, np.newaxis]
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        log_survival_intervals = -np.exp(eta)
    _require_finite_array(eta, name="audit eta")
    _require_finite_array(log_survival_intervals, name="audit interval log survival")
    log_survival_grid = np.zeros((cell_count, len(MODEL_TIMES)), dtype=np.float64)
    log_survival_grid[:, 1:] = np.cumsum(
        log_survival_intervals,
        axis=1,
        dtype=np.float64,
    )
    log_survival = log_survival_grid[
        design.opportunity_cell_index,
        design.opportunity_time_index,
    ]
    log_one_minus_survival = _stable_log_one_minus_exp(log_survival)

    log_rate = np.asarray(
        logsumexp(
            np.stack(
                (
                    log_survival + np.log(lambda_present),
                    log_one_minus_survival + np.log(lambda_quasi),
                )
            ),
            axis=0,
        ),
        dtype=np.float64,
    )
    log_mu = np.log(design.efforts) + log_rate
    log1p_mu = np.asarray(np.logaddexp(0.0, log_mu), dtype=np.float64)
    log_p0 = np.asarray(
        logsumexp(
            np.stack(
                (
                    log_survival - design.efforts * lambda_present,
                    log_one_minus_survival - design.efforts * lambda_quasi,
                )
            ),
            axis=0,
        ),
        dtype=np.float64,
    )
    vector = np.concatenate((log1p_mu, log_p0)).astype(np.float64, copy=False)
    _require_finite_array(vector, name="canonical audit vector")
    return _immutable_float_array(vector)


def _scaled_audit_jacobian_from_natural_values(
    design: AuditDesign,
    center: FloatArray,
    *,
    require_ordering: bool,
) -> FloatArray:
    if type(design) is not AuditDesign:
        raise TypeError("design must be AuditDesign")
    canonical_center = _canonical_audit_natural_values(
        center,
        require_ordering=require_ordering,
    )
    row_count = 2 * len(design.efforts)
    jacobian = np.empty((row_count, 5), dtype=np.float64)
    for column, (step, width) in enumerate(
        zip(
            AUDIT_CENTRAL_DIFFERENCE_STEPS,
            NATURAL_PARAMETER_SUPPORT_WIDTHS,
            strict=True,
        )
    ):
        plus = canonical_center.copy()
        minus = canonical_center.copy()
        plus[column] += step
        minus[column] -= step
        plus_vector = _audit_vector_from_natural_values(
            design,
            plus,
            require_ordering=require_ordering,
        )
        minus_vector = _audit_vector_from_natural_values(
            design,
            minus,
            require_ordering=require_ordering,
        )
        jacobian[:, column] = (plus_vector - minus_vector) / (2.0 * step) * width
    _require_finite_array(jacobian, name="scaled audit Jacobian")
    return _immutable_float_array(jacobian)


def _canonical_audit_natural_values(
    natural: object,
    *,
    require_ordering: bool,
) -> FloatArray:
    if (
        type(natural) is not np.ndarray
        or natural.dtype != np.float64
        or natural.shape != (5,)
        or not np.all(np.isfinite(natural))
    ):
        raise ValueError("audit natural parameters must be a finite float64 five-vector")
    rate_supports = (
        (LAMBDA_QUASI_SUPPORT, LAMBDA_PRESENT_SUPPORT)
        if require_ordering
        else ((0.01, 10.0), (0.01, 10.0))
    )
    supports = (
        ALPHA_SUPPORT,
        BETA_DRIVER_SUPPORT,
        BETA_QUALITY_SUPPORT,
        *rate_supports,
    )
    for value, support in zip(natural, supports, strict=True):
        if value < support[0] or value > support[1]:
            raise ValueError("audit natural parameter is outside its frozen support")
    if require_ordering and natural[4] <= natural[3]:
        raise ValueError("audit natural rates must be strictly ordered")
    return _immutable_float_array(natural)


def _stable_log_one_minus_exp(log_probability: FloatArray) -> FloatArray:
    if np.any(log_probability > 0.0) or not np.all(np.isfinite(log_probability)):
        raise LikelihoodEvaluationError("log survival must be finite and nonpositive")
    result = np.empty_like(log_probability, dtype=np.float64)
    threshold = -np.log(2.0)
    lower = log_probability < threshold
    with np.errstate(divide="ignore", invalid="ignore"):
        result[lower] = np.log1p(-np.exp(log_probability[lower]))
        result[~lower] = np.log(-np.expm1(log_probability[~lower]))
    if np.any(np.isnan(result)) or np.any(result > 0.0):
        raise LikelihoodEvaluationError("log one-minus-survival is invalid")
    return result


def _canonical_audit_target_id(parameters: JointParameters) -> str:
    values = (
        parameters.alpha,
        parameters.beta_driver,
        parameters.beta_quality,
        parameters.lambda_quasi,
        parameters.lambda_present,
    )
    targets = {
        (-6.0, 1.25, -0.60, 0.15, 4.0): "A",
        (-5.0, 0.50, 0.50, 0.30, 2.50): "B",
        (-7.0, -0.50, -1.00, 0.60, 6.00): "C",
    }
    return targets.get(values, "custom")


def _joint_parameter_vector(parameters: JointParameters) -> FloatArray:
    if type(parameters) is not JointParameters:
        raise TypeError("parameters must be JointParameters")
    return _immutable_float_array(
        np.asarray(
            (
                parameters.alpha,
                parameters.beta_driver,
                parameters.beta_quality,
                parameters.lambda_quasi,
                parameters.lambda_present,
            ),
            dtype=np.float64,
        )
    )


def _classify_inverse_optimizer_attempt(
    attempt: OptimizerStartResult,
    *,
    target: JointParameters,
) -> InverseAuditSearchResult:
    if not attempt.succeeded or attempt.coordinates is None:
        return InverseAuditSearchResult(
            start_index=attempt.start_index,
            start_coordinates=attempt.start_coordinates,
            succeeded=False,
            natural_parameters=None,
            rmse=None,
            scaled_distance=None,
            recovered=False,
            collision=False,
            failure_reason=attempt.failure_reason,
        )
    natural = optimization_coordinates_to_natural("joint", attempt.coordinates)
    if type(natural) is not JointParameters:
        raise TypeError("joint inverse result did not map to JointParameters")
    natural_vector = _joint_parameter_vector(natural)
    rmse = cast(float, attempt.objective_value)
    distance = scaled_natural_parameter_distance(natural, target)
    return InverseAuditSearchResult(
        start_index=attempt.start_index,
        start_coordinates=attempt.start_coordinates,
        succeeded=True,
        natural_parameters=natural_vector,
        rmse=rmse,
        scaled_distance=distance,
        recovered=inverse_solution_is_recovery(rmse, distance),
        collision=inverse_solution_is_collision(rmse, distance),
        failure_reason=None,
    )


def _run_profile_side(
    optimizer_kind: str,
    parameter_name: str,
    mle: float,
    side: str,
    llmax: float,
    global_natural: ProcessParameters | EffectiveCountRates | JointParameters,
    objective: Callable[[object], float],
    cache: dict[float, ProfilePointResult],
) -> tuple[ProfileSideResult, str | None]:
    evaluation_order: list[float] = []
    successful: list[
        tuple[
            float,
            ProcessParameters | EffectiveCountRates | JointParameters,
        ]
    ] = [(mle, global_natural)]

    def evaluate(target_value: float) -> ProfilePointResult:
        if target_value in cache:
            return cache[target_value]
        nearest_natural = min(
            successful,
            key=lambda item: (abs(item[0] - target_value), item[0]),
        )[1]
        point = _evaluate_profile_point(
            optimizer_kind,
            parameter_name,
            target_value,
            side,
            objective,
            global_natural=global_natural,
            nearest_natural=nearest_natural,
        )
        cache[target_value] = point
        evaluation_order.append(target_value)
        if point.succeeded and point.natural_parameters is not None:
            successful.append(
                (
                    target_value,
                    _natural_from_parameter_vector(
                        optimizer_kind,
                        point.natural_parameters,
                    ),
                )
            )
        return point

    inward_value = mle
    inward_root = -PROFILE_LR_CUTOFF
    endpoint: float | None = None
    bracket: tuple[float, float] | None = None
    crossed = False
    open_side = True
    for target_value in adaptive_profile_target_values(parameter_name, mle, side):
        point = evaluate(target_value)
        if not point.succeeded or point.log_likelihood is None:
            continue
        if _profile_exceeds_llmax(point.log_likelihood, llmax):
            return (
                ProfileSideResult(
                    side=side,
                    points=tuple(cache[value] for value in evaluation_order),
                    crossed_cutoff=False,
                    open_side=True,
                    interval_endpoint=None,
                    bracket=None,
                ),
                "profile_log_likelihood_exceeds_global_maximum",
            )
        current_root = profile_root_value(llmax, point.log_likelihood)
        if inward_root <= 0.0 and current_root >= 0.0:
            bracket = (
                min(inward_value, target_value),
                max(inward_value, target_value),
            )

            def root_function(value: float) -> float:
                root_point = evaluate(float(value))
                if not root_point.succeeded or root_point.log_likelihood is None:
                    raise ProfileEvaluationError("profile root point failed")
                if _profile_exceeds_llmax(root_point.log_likelihood, llmax):
                    raise _ProfileMaximumInvalidation(
                        "profile log likelihood exceeds global maximum"
                    )
                return profile_root_value(llmax, root_point.log_likelihood)

            try:
                endpoint = float(
                    scipy.optimize.brentq(
                        root_function,
                        bracket[0],
                        bracket[1],
                        xtol=_PROFILE_ROOT_TOLERANCES[parameter_name],
                        maxiter=PROFILE_ROOT_MAX_ITERATIONS,
                    )
                )
            except _ProfileMaximumInvalidation:
                return (
                    ProfileSideResult(
                        side=side,
                        points=tuple(cache[value] for value in evaluation_order),
                        crossed_cutoff=False,
                        open_side=True,
                        interval_endpoint=None,
                        bracket=bracket,
                    ),
                    "profile_log_likelihood_exceeds_global_maximum",
                )
            except ProfileEvaluationError, ValueError, RuntimeError:
                endpoint = None
                bracket = None
                break
            crossed = True
            open_side = False
            break
        if current_root < 0.0:
            inward_value = target_value
            inward_root = current_root
    return (
        ProfileSideResult(
            side=side,
            points=tuple(cache[value] for value in evaluation_order),
            crossed_cutoff=crossed,
            open_side=open_side,
            interval_endpoint=endpoint,
            bracket=bracket,
        ),
        None,
    )


def _evaluate_profile_point(
    optimizer_kind: str,
    parameter_name: str,
    target_value: float,
    side: str,
    objective: Callable[[object], float],
    *,
    global_natural: ProcessParameters | EffectiveCountRates | JointParameters,
    nearest_natural: ProcessParameters | EffectiveCountRates | JointParameters | None,
) -> ProfilePointResult:
    starts = build_profile_nuisance_starts(
        optimizer_kind,
        parameter_name,
        target_value,
        global_natural=global_natural,
        nearest_natural=nearest_natural,
    )
    bounds = profile_nuisance_bounds(
        optimizer_kind,
        parameter_name,
        target_value,
    )

    def nuisance_objective(coordinates: FloatArray) -> float:
        natural = profile_nuisance_to_natural(
            optimizer_kind,
            parameter_name,
            target_value,
            coordinates,
        )
        return float(objective(natural))

    attempts = tuple(
        _run_frozen_lbfgsb_start(
            nuisance_objective,
            start.coordinates,
            bounds=bounds,
            natural_validator=lambda values: profile_nuisance_to_natural(
                optimizer_kind,
                parameter_name,
                target_value,
                values,
            ),
            start_index=index,
        )
        for index, start in enumerate(starts, start=1)
    )
    successful = tuple(
        sorted(
            (attempt for attempt in attempts if attempt.succeeded),
            key=lambda attempt: (
                -cast(float, attempt.log_likelihood),
                starts[attempt.start_index - 1].source_order,
            ),
        )
    )
    if not successful:
        return ProfilePointResult(
            parameter_name=parameter_name,
            target_value=target_value,
            side=side,
            succeeded=False,
            log_likelihood=None,
            nuisance_coordinates=None,
            natural_parameters=None,
            selected_source=None,
            selected_source_order=None,
            failure_reason="all_profile_nuisance_starts_failed",
        )
    best = successful[0]
    coordinates = cast(FloatArray, best.coordinates)
    selected = starts[best.start_index - 1]
    natural = profile_nuisance_to_natural(
        optimizer_kind,
        parameter_name,
        target_value,
        coordinates,
    )
    return ProfilePointResult(
        parameter_name=parameter_name,
        target_value=target_value,
        side=side,
        succeeded=True,
        log_likelihood=best.log_likelihood,
        nuisance_coordinates=coordinates,
        natural_parameters=_natural_parameter_vector_for_kind(optimizer_kind, natural),
        selected_source=selected.source,
        selected_source_order=selected.source_order,
        failure_reason=None,
    )


def _profile_exceeds_llmax(profile_log_likelihood: float, llmax: float) -> bool:
    profile = _canonical_numeric_float(
        profile_log_likelihood,
        name="profile_log_likelihood",
    )
    maximum = _canonical_numeric_float(llmax, name="llmax")
    tolerance = 1e-6 * (1.0 + abs(maximum))
    return profile > maximum + tolerance


def _empty_profile_side(side: str) -> ProfileSideResult:
    return ProfileSideResult(
        side=side,
        points=(),
        crossed_cutoff=False,
        open_side=True,
        interval_endpoint=None,
        bracket=None,
    )


def _run_frozen_lbfgsb_start(
    objective: Callable[[FloatArray], float],
    x0: FloatArray,
    *,
    bounds: tuple[tuple[float, float], ...],
    natural_validator: Callable[[FloatArray], object],
    start_index: int,
) -> OptimizerStartResult:
    if type(start_index) is not int or start_index < 1:
        raise ValueError("start_index must be a positive integer")
    canonical_start = _canonical_optimization_coordinates(x0, bounds=bounds)
    invalid_evaluation = False

    def guarded_objective(coordinates: FloatArray) -> float:
        nonlocal invalid_evaluation
        try:
            value = float(objective(np.asarray(coordinates, dtype=np.float64)))
        except Exception:
            invalid_evaluation = True
            raise
        if not isfinite(value):
            invalid_evaluation = True
            return float("inf")
        return value

    try:
        result = scipy.optimize.minimize(
            guarded_objective,
            canonical_start.copy(),
            method="L-BFGS-B",
            jac="3-point",
            bounds=bounds,
            options={
                "ftol": 1e-12,
                "gtol": 1e-6,
                "maxiter": 1000,
                "maxfun": 20000,
                "maxls": 50,
                "finite_diff_rel_step": 1e-5,
            },
        )
    except Exception as error:
        return _failed_optimizer_start(
            start_index,
            canonical_start,
            f"objective_or_optimizer_exception:{type(error).__name__}",
        )
    if invalid_evaluation:
        return _failed_optimizer_start(
            start_index,
            canonical_start,
            "invalid_or_nonfinite_objective_evaluation",
        )
    if not bool(getattr(result, "success", False)):
        return _failed_optimizer_start(
            start_index,
            canonical_start,
            "optimizer_success_false",
        )
    if getattr(result, "status", None) != 0:
        return _failed_optimizer_start(
            start_index,
            canonical_start,
            "optimizer_status_nonzero",
        )
    try:
        objective_value = float(result.fun)
    except AttributeError, TypeError, ValueError, OverflowError:
        return _failed_optimizer_start(
            start_index,
            canonical_start,
            "invalid_result_objective",
        )
    if not isfinite(objective_value):
        return _failed_optimizer_start(
            start_index,
            canonical_start,
            "invalid_result_objective",
        )
    try:
        coordinates = _canonical_optimization_coordinates(result.x, bounds=bounds)
        natural_validator(coordinates)
    except AttributeError, TypeError, ValueError, LikelihoodEvaluationError:
        return _failed_optimizer_start(
            start_index,
            canonical_start,
            "invalid_result_coordinates_or_natural_map",
        )
    return OptimizerStartResult(
        start_index=start_index,
        start_coordinates=canonical_start,
        succeeded=True,
        coordinates=coordinates,
        objective_value=objective_value,
        log_likelihood=-objective_value,
        failure_reason=None,
    )


def _failed_optimizer_start(
    start_index: int,
    start_coordinates: FloatArray,
    reason: str,
) -> OptimizerStartResult:
    return OptimizerStartResult(
        start_index=start_index,
        start_coordinates=start_coordinates,
        succeeded=False,
        coordinates=None,
        objective_value=None,
        log_likelihood=None,
        failure_reason=reason,
    )


def _validate_optimizer_start_result(result: OptimizerStartResult) -> None:
    if type(result.start_index) is not int or result.start_index < 1:
        raise ValueError("optimizer start_index must be a positive integer")
    if (
        type(result.start_coordinates) is not np.ndarray
        or result.start_coordinates.dtype != np.float64
        or result.start_coordinates.ndim != 1
        or not np.all(np.isfinite(result.start_coordinates))
    ):
        raise ValueError("optimizer start_coordinates must be finite float64")
    if type(result.succeeded) is not bool:
        raise ValueError("optimizer succeeded must be bool")
    if result.succeeded:
        if (
            type(result.coordinates) is not np.ndarray
            or result.coordinates.dtype != np.float64
            or result.coordinates.shape != result.start_coordinates.shape
            or not np.all(np.isfinite(result.coordinates))
        ):
            raise ValueError("successful optimizer coordinates must be finite float64")
        if result.objective_value is None or result.log_likelihood is None:
            raise ValueError("successful optimizer result must contain finite values")
        if not isfinite(result.objective_value) or not isfinite(result.log_likelihood):
            raise ValueError("successful optimizer result must contain finite values")
        if result.failure_reason is not None:
            raise ValueError("successful optimizer result cannot have a failure reason")
    elif (
        result.coordinates is not None
        or result.objective_value is not None
        or result.log_likelihood is not None
        or type(result.failure_reason) is not str
        or not result.failure_reason
    ):
        raise ValueError("failed optimizer result must propagate one explicit reason")


def _validate_inverse_audit_search_result(result: InverseAuditSearchResult) -> None:
    if type(result.start_index) is not int or result.start_index < 1:
        raise ValueError("inverse search start_index must be positive")
    if (
        type(result.start_coordinates) is not np.ndarray
        or result.start_coordinates.dtype != np.float64
        or result.start_coordinates.shape != (5,)
        or not np.all(np.isfinite(result.start_coordinates))
    ):
        raise ValueError("inverse search start coordinates must be finite float64")
    if type(result.succeeded) is not bool:
        raise ValueError("inverse search succeeded must be bool")
    if type(result.recovered) is not bool or type(result.collision) is not bool:
        raise ValueError("inverse search classifications must be bool")
    if result.recovered and result.collision:
        raise ValueError("inverse search cannot be both recovery and collision")
    if result.succeeded:
        if (
            type(result.natural_parameters) is not np.ndarray
            or result.natural_parameters.dtype != np.float64
            or result.natural_parameters.shape != (5,)
            or not np.all(np.isfinite(result.natural_parameters))
            or result.rmse is None
            or result.scaled_distance is None
            or not isfinite(result.rmse)
            or result.rmse < 0.0
            or not isfinite(result.scaled_distance)
            or result.scaled_distance < 0.0
            or result.failure_reason is not None
        ):
            raise ValueError("successful inverse search must contain finite classified values")
    elif (
        result.natural_parameters is not None
        or result.rmse is not None
        or result.scaled_distance is not None
        or result.recovered
        or result.collision
        or type(result.failure_reason) is not str
        or not result.failure_reason
    ):
        raise ValueError("failed inverse search must propagate one explicit reason")


def _canonical_optimization_coordinates(
    values: object,
    *,
    bounds: tuple[tuple[float, float], ...],
) -> FloatArray:
    if (
        type(values) is not np.ndarray
        or values.dtype != np.float64
        or values.shape != (len(bounds),)
        or not np.all(np.isfinite(values))
    ):
        raise ValueError("optimizer coordinates must be a finite float64 vector")
    for value, bound in zip(values, bounds, strict=True):
        if value < bound[0] or value > bound[1]:
            raise ValueError("optimizer coordinate is outside its frozen bound")
    return _immutable_float_array(values)


def _validate_profile_target(optimizer_kind: object, parameter_name: object) -> str:
    kind = _validate_optimizer_kind(optimizer_kind)
    if type(parameter_name) is not str or parameter_name not in _OPTIMIZER_PARAMETER_NAMES[kind]:
        raise ValueError("profile target is not applicable to optimizer kind")
    return kind


def _parameter_support(parameter_name: object) -> tuple[float, float]:
    if type(parameter_name) is not str or parameter_name not in _PARAMETER_SUPPORTS:
        raise ValueError("profile target must be a frozen parameter")
    return _PARAMETER_SUPPORTS[parameter_name]


def _canonical_profile_target(parameter_name: str, target_value: object) -> float:
    return _canonical_bounded_float(
        target_value,
        support=_parameter_support(parameter_name),
        name="profile target",
    )


def _insert_fixed_value(values: FloatArray, *, index: int, value: float) -> FloatArray:
    inserted = np.insert(values, index, value).astype(np.float64, copy=False)
    return _immutable_float_array(inserted)


def _validate_natural_type_for_optimizer(
    optimizer_kind: str,
    natural: object,
) -> None:
    expected = {
        "process_oracle": ProcessParameters,
        "observation_oracle": EffectiveCountRates,
        "joint": JointParameters,
    }[optimizer_kind]
    if type(natural) is not expected:
        raise TypeError(f"natural value must be {expected.__name__} for {optimizer_kind}")


def _natural_parameter_value(
    natural: ProcessParameters | EffectiveCountRates | JointParameters,
    parameter_name: str,
) -> float:
    if not hasattr(natural, parameter_name):
        raise ValueError("natural value does not contain profile target")
    return float(getattr(natural, parameter_name))


def _natural_parameter_vector_for_kind(
    optimizer_kind: str,
    natural: ProcessParameters | EffectiveCountRates | JointParameters,
) -> FloatArray:
    kind = _validate_optimizer_kind(optimizer_kind)
    _validate_natural_type_for_optimizer(kind, natural)
    return _immutable_float_array(
        np.asarray(
            tuple(
                _natural_parameter_value(natural, name) for name in _OPTIMIZER_PARAMETER_NAMES[kind]
            ),
            dtype=np.float64,
        )
    )


def _natural_from_parameter_vector(
    optimizer_kind: str,
    values: FloatArray,
) -> ProcessParameters | EffectiveCountRates | JointParameters:
    kind = _validate_optimizer_kind(optimizer_kind)
    expected_shape = (len(_OPTIMIZER_PARAMETER_NAMES[kind]),)
    if (
        type(values) is not np.ndarray
        or values.dtype != np.float64
        or values.shape != expected_shape
        or not np.all(np.isfinite(values))
    ):
        raise ValueError("natural parameter vector has invalid shape or values")
    if kind == "process_oracle":
        return ProcessParameters(*map(float, values))
    if kind == "observation_oracle":
        return EffectiveCountRates(
            lambda_quasi=float(values[0]),
            lambda_present=float(values[1]),
        )
    return JointParameters(
        alpha=float(values[0]),
        beta_driver=float(values[1]),
        beta_quality=float(values[2]),
        lambda_quasi=float(values[3]),
        lambda_present=float(values[4]),
    )


def _validate_optimizer_kind(value: object) -> str:
    if type(value) is not str or value not in _OPTIMIZER_KINDS:
        raise ValueError("optimizer kind must be process_oracle, observation_oracle, or joint")
    return value


def _canonical_bounded_float(
    value: object,
    *,
    support: tuple[float, float],
    name: str,
) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be finite and within support {support}")
    numeric = cast(int | float, value)
    if numeric < support[0] or numeric > support[1]:
        raise ValueError(f"{name} must be finite and within support {support}")
    canonical = float(numeric)
    if not isfinite(canonical):
        raise ValueError(f"{name} must be finite and within support {support}")
    return canonical


def _canonical_numeric_float(value: object, *, name: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a finite built-in number")
    canonical = float(cast(int | float, value))
    if not isfinite(canonical):
        raise ValueError(f"{name} must be a finite built-in number")
    return canonical


def _canonical_nonnegative_float(value: object, *, name: str) -> float:
    canonical = _canonical_numeric_float(value, name=name)
    if canonical < 0.0:
        raise ValueError(f"{name} must be nonnegative")
    return canonical


def _radical_inverse(index: int, base: int) -> float:
    inverse = 0.0
    factor = 1.0 / base
    remaining = index
    while remaining:
        remaining, digit = divmod(remaining, base)
        inverse += digit * factor
        factor /= base
    return inverse


def _canonical_unit_fraction(value: object, name: str) -> float:
    canonical = _canonical_numeric_float(value, name=name)
    if canonical < 0.0 or canonical > 1.0:
        raise ValueError(f"{name} must be within [0, 1]")
    return canonical


def _validate_cell_id(cell_id: int) -> None:
    if type(cell_id) is not int or cell_id < 0 or cell_id > _MAX_CELL_ID:
        raise ValueError(f"cell_id must be an integer from 0 to {_MAX_CELL_ID}")


def _canonical_standardized_quality(value: object) -> float:
    if type(value) not in (int, float):
        raise ValueError("standardized_quality must be finite")
    numeric = cast(int | float, value)
    try:
        canonical = float(numeric)
    except OverflowError as error:
        raise ValueError("standardized_quality must be finite") from error
    if not isfinite(canonical):
        raise ValueError("standardized_quality must be finite")
    return canonical


def _canonical_arrival_time(value: object) -> float | None:
    if value is None:
        return None
    if type(value) not in (int, float):
        raise ValueError("predator_arrival_time must be numeric or None")
    numeric = cast(int | float, value)
    if type(numeric) is int:
        if numeric < MODEL_TIMES[0]:
            raise ValueError("finite predator_arrival_time must be nonnegative")
        return float(numeric)
    canonical = float(numeric)
    if isfinite(canonical) and canonical < MODEL_TIMES[0]:
        raise ValueError("finite predator_arrival_time must be nonnegative")
    return canonical


def _validate_transition_time(value: int | None) -> None:
    if value is None:
        return
    if type(value) is not int or value not in MODEL_TIMES[1:]:
        raise ValueError("transition_time must be one of t1..t20 or None for censoring")


def _validate_model_time(time: int) -> None:
    if type(time) is not int or time not in MODEL_TIMES:
        raise ValueError("time must be one of the model times 0, 6, ..., 120")


def _validate_interval_count(interval_count: int) -> None:
    if (
        type(interval_count) is not int
        or interval_count < 1
        or interval_count > _MAX_INTERVAL_COUNT
    ):
        raise ValueError("interval_count must be an integer from 1 to 20")


def _canonical_effort(effort: object) -> float:
    if type(effort) not in (int, float):
        raise ValueError("effort must be finite and positive")
    numeric = cast(int | float, effort)
    try:
        canonical = float(numeric)
    except OverflowError as error:
        raise ValueError("effort must be finite and positive") from error
    if canonical <= 0.0 or not isfinite(canonical):
        raise ValueError("effort must be finite and positive")
    return canonical


def _canonical_opportunities(
    opportunities: tuple[CountOpportunity, ...],
) -> tuple[CountOpportunity, ...]:
    if type(opportunities) is not tuple:
        raise ValueError("opportunities must be a tuple")
    canonical: list[CountOpportunity] = []
    previous_time = -1
    for opportunity in opportunities:
        if type(opportunity) is not CountOpportunity:
            raise TypeError("opportunities must contain CountOpportunity values")
        if opportunity.time <= previous_time:
            raise ValueError("opportunity times must be strictly increasing")
        previous_time = opportunity.time
        canonical.append(
            CountOpportunity(
                time=opportunity.time,
                count=opportunity.count,
                effort=opportunity.effort,
            )
        )
    return tuple(canonical)


def _validate_state(state: int) -> None:
    if type(state) is not int or state not in (0, 1):
        raise ValueError("state must be integer 0 or 1")


def _canonical_effective_rates(rates: EffectiveCountRates) -> EffectiveCountRates:
    if type(rates) is not EffectiveCountRates:
        raise TypeError("rates must be EffectiveCountRates")
    lambda_present = _canonical_positive_float(rates.lambda_present, name="lambda_present")
    lambda_quasi = _canonical_positive_float(rates.lambda_quasi, name="lambda_quasi")
    return EffectiveCountRates(
        lambda_present=lambda_present,
        lambda_quasi=lambda_quasi,
    )


def _canonical_positive_float(value: object, *, name: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be finite and positive")
    numeric = cast(int | float, value)
    try:
        canonical = float(numeric)
    except OverflowError as error:
        raise ValueError(f"{name} must be finite and positive") from error
    if canonical <= 0.0 or not isfinite(canonical):
        raise ValueError(f"{name} must be finite and positive")
    return canonical


def _immutable_float_array(values: FloatArray) -> FloatArray:
    canonical = np.ascontiguousarray(values, dtype=np.float64)
    immutable = np.frombuffer(canonical.tobytes(order="C"), dtype=np.float64)
    return immutable.reshape(canonical.shape)


def _immutable_int_array(values: IntArray) -> IntArray:
    canonical = np.ascontiguousarray(values, dtype=np.int64)
    immutable = np.frombuffer(canonical.tobytes(order="C"), dtype=np.int64)
    return immutable.reshape(canonical.shape)


def _immutable_bool_array(values: BoolArray) -> BoolArray:
    canonical = np.ascontiguousarray(values, dtype=np.bool_)
    immutable = np.frombuffer(canonical.tobytes(order="C"), dtype=np.bool_)
    return immutable.reshape(canonical.shape)


def _require_finite_array(values: FloatArray, *, name: str) -> None:
    if not np.all(np.isfinite(values)):
        raise LikelihoodEvaluationError(f"{name} contains nonfinite values")


def _require_finite_likelihood(value: float) -> float:
    if not isfinite(value):
        raise LikelihoodEvaluationError("likelihood evaluation is nonfinite")
    return value


# Integrated pre-Task-3 contract surfaces. These literal registries keep
# downstream writers and reducers independent of incidental disk contents.
@dataclass(frozen=True, slots=True)
class ScenarioDefinition:
    scenario_id: str
    scenario_role: str
    generation_model: str
    fit_model: str
    schedule_id: str
    effort_rule: str
    development_replicates: int
    calibration_replicates: int
    holdout_replicates: int
    expected_behavior: str
    truth_access_class: str
    transportability_class: str
    fit_scope: str
    primary_fit_variant: str
    comparator_fit_variant: str | None


@dataclass(frozen=True, slots=True)
class ScenarioEvidence:
    scenario_id: str
    truth_access_class: str
    fit_scope: str
    primary_fit_variant: str
    comparator_fit_variant: str | None
    latent_time_applicable: bool
    latent_time_sample_size: int


@dataclass(frozen=True, slots=True)
class ReplicateTask:
    scenario_id: str
    split_id: str
    replicate_id: int

    @property
    def task_id(self) -> str:
        return (
            f"scenario={self.scenario_id}|split={self.split_id}|replicate={self.replicate_id:04d}"
        )


@dataclass(frozen=True, slots=True)
class ScenarioReplicateResult:
    task: ReplicateTask
    recovery_rows: tuple[dict[str, object], ...]
    latent_time_rows: tuple[dict[str, object], ...]
    profile_rows: tuple[dict[str, object], ...]
    predictive_rows: tuple[dict[str, object], ...]
    control_rows: tuple[dict[str, object], ...]
    fit_succeeded: bool
    failure_reason: str | None


@dataclass(frozen=True, slots=True)
class RuntimeTaskUnit:
    task_id: str
    scenario_id: str
    benchmark_split: str
    benchmark_replicate_first: int
    benchmark_replicate_last: int
    measured_duration_seconds: float
    calibration_repeat_count: int
    holdout_repeat_count: int
    includes_profiles: bool
    predictive_reference_count: int
    scientific_row: bool


@dataclass(frozen=True, slots=True)
class TrackedStateManifest:
    entries: tuple[tuple[str, str], ...]
    tracked_state_sha256: str


@dataclass(frozen=True, slots=True)
class ArtifactSnapshot:
    entries: tuple[tuple[str, str], ...]
    artifact_set_sha256: str


@dataclass(frozen=True, slots=True)
class ProvenanceEnvelope:
    repo_root: Path
    branch: str
    head: str
    base: str
    tracked: tuple[tuple[str, str], ...]
    staged: tuple[tuple[str, str], ...]
    unstaged: tuple[str, ...]
    untracked: tuple[str, ...]
    status_entries: tuple[tuple[str, str], ...]
    cached_entries: tuple[tuple[str, str], ...]
    analytical_entries: tuple[tuple[str, str], ...]
    candidate_entries: tuple[tuple[str, str], ...]
    log_bytes: bytes
    preholdout_receipt_file_sha256: str
    receipt_sha256: str
    holdout_receipt_file_sha256: str
    config_sha256: str
    config_file_sha256: str
    represented_artifact_set_sha256: str
    artifact_set_sha256: str


@dataclass(frozen=True, slots=True)
class FrozenConfigIdentity:
    path: Path
    payload: Mapping[str, object]
    config_sha256: str
    config_file_sha256: str
    canonical_bytes: bytes


@dataclass(frozen=True, slots=True)
class HoldoutReceiptIdentity:
    path: Path
    payload: Mapping[str, object]
    receipt_sha256: str
    holdout_receipt_file_sha256: str
    canonical_bytes: bytes


@dataclass(frozen=True, slots=True)
class ReceiptFileIdentity:
    path: Path
    file_sha256: str
    canonical_bytes: bytes


@dataclass(frozen=True, slots=True)
class LiveAuthorityIdentity:
    spec_sha256: str
    source_sha256: str
    source_receipt_file_sha256: str


class ImmutablePostCreateStop(ValueError):
    def __init__(self, disposition: str, path: Path, file_sha256: str) -> None:
        self.disposition = disposition
        self.path = path
        self.file_sha256 = file_sha256
        super().__init__(f"{disposition}: preserved {path} at {file_sha256}")


class ImmutableTerminalStop(ValueError):
    def __init__(self, disposition: str, path: Path, file_sha256: str) -> None:
        self.disposition = disposition
        self.path = path
        self.file_sha256 = file_sha256
        super().__init__(f"{disposition}: terminal record preserved at {path} ({file_sha256})")


@dataclass(frozen=True, slots=True)
class PhaseGuardState:
    phase: str
    repo_root: Path
    git_runner: Callable[[tuple[str, ...]], str]
    branch: str
    head: str
    base: str
    status_entries: tuple[tuple[str, str, str], ...]
    analytical_entries: tuple[tuple[str, str], ...]
    analytical_sha256: str
    candidate_entries: tuple[tuple[str, str, str], ...]
    present_paths: tuple[str, ...]
    absent_paths: tuple[str, ...]


_FIXTURE_TASK_SERVICE_TOKEN = object()
_FIXTURE_OUTPUT_ROOT_TOKEN = object()


@dataclass(frozen=True, slots=True)
class FixtureTaskService:
    _token: object

    def run(self, *, workers: int, output_dir: Path) -> dict[str, object]:
        del workers, output_dir
        if self._token is not _FIXTURE_TASK_SERVICE_TOKEN:
            raise TypeError("fixture task service is not owned by this module")
        return dict(FIXTURE_ZERO_COUNTERS)


def fixture_task_service() -> FixtureTaskService:
    return FixtureTaskService(_FIXTURE_TASK_SERVICE_TOKEN)


_STAGING_CAPTURE_TOKEN = object()
_VALIDATED_STAGING_TOKEN = object()
_PUBLICATION_CAPTURE_TOKEN = object()
_VALIDATION_FAILURE_TOKEN = object()
_REVIEWED_LOG_TRANSITION_TOKEN = object()
_VALIDATED_SCIENCE_BUNDLE_TOKEN = object()


@dataclass(frozen=True, slots=True)
class TemporaryFixtureRoot:
    path: Path
    repo_root: Path
    canonical_artifact_path: Path
    _token: object


@dataclass(frozen=True, slots=True)
class CapturedStagingState:
    repo_root: Path
    common_git_dir: Path
    branch: str
    head: str
    status_entries: tuple[tuple[str, str], ...]
    worktree_blobs: tuple[tuple[str, str], ...]
    index_blobs: tuple[tuple[str, str], ...]
    write_tree: str | None
    _token: object


@dataclass(frozen=True, slots=True)
class ValidatedStagingIdentity:
    repo_root: Path
    common_git_dir: Path
    goal_branch: str
    base_commit: str
    index_blobs: tuple[tuple[str, str], ...]
    write_tree: str
    _token: object


@dataclass(frozen=True, slots=True)
class ValidationCommandSpec:
    command_class: str
    argv: tuple[str, ...]
    phase: str | None
    reviewed_disposition: str


@dataclass(frozen=True, slots=True)
class ValidationFailureRecord:
    command_spec: ValidationCommandSpec
    before: ProvenanceEnvelope
    after: ProvenanceEnvelope
    exit_code: int
    retry_count: int
    _token: object

    @property
    def command(self) -> tuple[str, ...]:
        return self.command_spec.argv


@dataclass(frozen=True, slots=True)
class ReviewedLogTransition:
    before: ProvenanceEnvelope
    after: ProvenanceEnvelope
    approved_suffix: bytes
    payload: Mapping[str, object]
    _token: object


@dataclass(frozen=True, slots=True)
class CapturedPublicationState:
    repo_root: Path
    common_git_dir: Path
    branch: str
    head: str
    tree: str
    parents: tuple[str, ...]
    local_main: str
    remote_main: str
    _token: object


@dataclass(frozen=True, slots=True)
class LatentTransitionDiagnostics:
    observed_values: dict[str, float]
    expected_values: dict[str, float]
    errors: dict[str, float]
    sample_size: int


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    recommendation_rank: int
    recommendation_class: str
    reason: str
    reasons: tuple[str, ...] = ()
    transportability_class: str = "scheduled_count_only_point_process_bridge_required"


@dataclass(frozen=True, slots=True)
class PredictiveScenarioState:
    predictive_complete_finite: bool
    predictive_pass: bool
    finite_rule_fired: bool
    scientific_warning_available: bool
    forced_warning: bool


@dataclass(frozen=True, slots=True)
class CanonicalPredictiveOpportunity:
    """One canonical scheduled opportunity plus keyed retention state."""

    cell_id: int
    time: int
    effort: float
    quality_stratum: str
    time_band: str
    keep_key: str
    kept: bool

    def __post_init__(self) -> None:
        _validate_cell_id(self.cell_id)
        _validate_model_time(self.time)
        object.__setattr__(self, "effort", _canonical_effort(self.effort))
        if self.quality_stratum not in {f"q{index}" for index in range(1, 6)}:
            raise ValueError("predictive quality stratum must be q1 through q5")
        if self.time_band not in {"early", "middle", "late"}:
            raise ValueError("predictive time-band label must be early, middle, or late")
        expected_key = f"cell_id={self.cell_id}|time={self.time}"
        if self.keep_key != expected_key:
            raise ValueError("predictive keep key must derive from exact cell/time identity")
        if type(self.kept) is not bool:
            raise ValueError("predictive keep state must be bool")


_PREDICTIVE_FRAME_ISSUER = object()


@dataclass(frozen=True, slots=True, init=False)
class PredictiveOpportunityFrameEvidence:
    scenario_id: str
    split_id: str
    replicate_id: int
    frame_role: str
    opportunities: tuple[CanonicalPredictiveOpportunity, ...]
    opportunity_count: int
    stratum_counts: tuple[int, ...]
    opportunity_frame_sha256: str
    dropout_mask_sha256: str | None
    _issuer: object = field(repr=False, compare=False)

    def __init__(self) -> None:
        raise TypeError(
            "PredictiveOpportunityFrameEvidence must be issued from a canonical schedule"
        )


@dataclass(frozen=True, slots=True)
class ValidatedScienceBundle:
    scenario_results: tuple[tuple[str, str], ...]
    control_rows: tuple[dict[str, object], ...]
    recommendation: RecommendationResult
    design_rows: tuple[dict[str, object], ...]
    design_evidence_sha256: str
    predictive_states: tuple[tuple[str, PredictiveScenarioState], ...]
    _token: object


RECOMMENDATION_CLASSES = (
    "model_contract_failed",
    "process_observation_confounded",
    "observation_limited_but_calibrated",
    "latent_response_observation_gate_passed",
)
FIT_SCOPES = ("replicate", "scenario_shared", "bootstrap_shared")
FIT_VARIANTS = (
    "canonical",
    "correct_alignment",
    "permuted_alignment",
    "equal_rate",
    "ordered_emission",
)
FIT_DERIVED_PRIMARY_KEYS = {
    "replicate_recovery.csv": (
        "scenario_id",
        "split_id",
        "replicate_id",
        "fit_variant",
        "parameter_id",
    ),
    "coverage_calibration.csv": ("scenario_id", "split_id", "fit_variant", "parameter_id"),
    "latent_time_calibration.csv": (
        "scenario_id",
        "split_id",
        "replicate_id",
        "fit_variant",
        "metric_id",
    ),
    "predictive_replicate_diagnostics.csv": (
        "scenario_id",
        "split_id",
        "replicate_id",
        "fit_variant",
        "stratum_type",
        "stratum_value",
        "metric_id",
    ),
    "predictive_check_summary.csv": (
        "scenario_id",
        "split_id",
        "fit_variant",
        "stratum_type",
        "stratum_value",
        "metric_id",
    ),
    "identifiability_profiles.csv": (
        "scenario_id",
        "split_id",
        "replicate_id",
        "fit_variant",
        "parameter_id",
        "grid_index",
    ),
}
FIT_PARAMETER_IDS = {
    "process_oracle_observed_transition": ("alpha", "beta_driver", "beta_quality"),
    "observation_oracle_fixed_transition": ("lambda_quasi", "lambda_present"),
}
ORDERED_PARAMETER_IDS = (
    "alpha",
    "beta_driver",
    "beta_quality",
    "lambda_quasi",
    "lambda_present",
)
SCENARIO_PARAMETER_TRUTH_ROWS = (
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
        for parameter_id in ORDERED_PARAMETER_IDS
    ),
    ("spatial_frailty_stress", "alpha", -6.0),
    ("spatial_frailty_stress", "beta_driver", 1.25),
    ("spatial_frailty_stress", "beta_quality", -0.60),
    ("spatial_frailty_stress", "lambda_quasi", 0.15),
    ("spatial_frailty_stress", "lambda_present", 4.0),
)
_SCENARIO_PARAMETER_TRUTH = {
    (scenario_id, parameter_id): truth
    for scenario_id, parameter_id, truth in SCENARIO_PARAMETER_TRUTH_ROWS
}
EQUAL_EMISSION_STATUS_ROWS = (
    {
        "parameter_id": "alpha",
        "structural_status": "unidentified",
        "practical_status": "unidentified",
    },
    {
        "parameter_id": "beta_driver",
        "structural_status": "unidentified",
        "practical_status": "unidentified",
    },
    {
        "parameter_id": "beta_quality",
        "structural_status": "unidentified",
        "practical_status": "unidentified",
    },
    {
        "parameter_id": "lambda_quasi",
        "structural_status": "unidentified",
        "practical_status": "unidentified",
    },
    {
        "parameter_id": "lambda_present",
        "structural_status": "identified",
        "practical_status": "not_applicable",
    },
    {
        "parameter_id": "lambda_equal",
        "structural_status": "identified",
        "practical_status": "identified",
    },
)
LATENT_PATH_VALUES = tuple(range(6, 127, 6))
LATENT_CENSOR_LABEL_IS_BIOLOGICAL = False
LATENT_METRIC_IDS = (
    "transition_brier",
    "transition_interval_score",
    "transition_median_absolute_error",
)
ARTIFACT_PATHS = (
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
FIT_EXECUTION_EVIDENCE_SCHEMA_VERSION = "v3"
ARTIFACT_SCHEMA_VERSIONS = tuple(
    (
        path,
        FIT_EXECUTION_EVIDENCE_SCHEMA_VERSION
        if path == "fit_execution_evidence.csv"
        else GENERATED_ARTIFACT_SCHEMA_VERSION,
    )
    for path in ARTIFACT_PATHS
)
REPORT_REQUIRED_LINKS = ARTIFACT_PATHS[:15]
VISUAL_SOURCE_TABLES = (
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
STAGING_PATHS = (
    "AGENTS.md",
    "README.md",
    "pyproject.toml",
    "uv.lock",
    "spec/report_log.md",
    "spec/synth_medium_latent_response_observation_recovery_gate.md",
    "src/spatext/observe.py",
    "src/spatext/synth/medium/__init__.py",
    "src/spatext/synth/medium/latent_response_observation_recovery.py",
    "scripts/run_synth_medium_latent_response_observation_recovery.py",
    "tests/test_observe.py",
    "tests/test_synth_medium_latent_response_observation_recovery.py",
    f"{GOAL_DIRECTORY}/Goal.md",
    f"{GOAL_DIRECTORY}/Plan.md",
    f"{GOAL_DIRECTORY}/Runbook.md",
    f"{GOAL_DIRECTORY}/Log.md",
    f"{GOAL_DIRECTORY}/source_digest_receipt.json",
    f"{GOAL_DIRECTORY}/preholdout_state_receipt.json",
    f"{GOAL_DIRECTORY}/holdout_receipt.json",
)
FIXTURE_ZERO_COUNTERS = {
    "holdout_payload_instantiated": False,
    "scientific_rows_emitted": False,
    "rng_factory_call_count": 0,
    "canonical_output_write_count": 0,
}
LIVE_CALIBRATION_OWNER = "task4"
MODEL_PARAMETER_CONTRACT_HEADER = (
    "parameter_id",
    "role",
    "units",
    "transform",
    "lower_bound",
    "upper_bound",
    "generating_value",
    "fitted_scenarios",
    "structural_status",
    "practical_status",
    "interpretation",
)
FIT_EXECUTION_EVIDENCE_HEADER = (
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
FIT_EVIDENCE_ROW_TYPES = ("fit_result", "design_diagnostic")
DESIGN_KINDS = ("potential", "oracle", "plugin")
DESIGN_LABELS = {
    "potential": ("potential_design", "ANALYST-PREFLIGHT"),
    "oracle": ("process_oracle_truth_at_risk", "ORACLE-BENCHMARK-ONLY"),
    "plugin": ("joint_plugin_smoothed_at_risk", "ANALYST-JOINT-PRACTICAL"),
}
DESIGN_FAILURE_CODES = frozenset(
    {
        "rank_deficient",
        "condition_limit_failed",
        "joint_fit_failed_or_nonfinite",
        "not_evaluated_potential_failed",
        "process_oracle_fit_failed_or_nonfinite",
    }
)
_FIT_RESULT_ONLY_FIELDS = FIT_EXECUTION_EVIDENCE_HEADER[8:24]
_DESIGN_ONLY_FIELDS = FIT_EXECUTION_EVIDENCE_HEADER[25:]


def required_design_kinds(scenario_id: str, fit_variant: str) -> tuple[str, ...]:
    if scenario_id not in SCENARIO_IDS or fit_variant not in FIT_VARIANTS:
        raise ValueError("design applicability requires a registered scenario and variant")
    registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
    if fit_variant not in {registry.primary_fit_variant, registry.comparator_fit_variant}:
        raise ValueError("design applicability requires a registered scenario variant")
    if scenario_id == "process_oracle_observed_transition":
        return ("potential", "oracle")
    if scenario_id == "observation_oracle_fixed_transition" or fit_variant == "equal_rate":
        return ("potential",)
    return ("potential", "plugin")


def permitted_persisted_fit_failure_classes(
    scenario_id: str,
    fit_variant: str,
) -> tuple[str, ...]:
    """Return the closed failure-class set for one persisted fit identity."""

    required = required_design_kinds(scenario_id, fit_variant)
    classes = ["potential_rank_gate_failure", "potential_condition_gate_failure"]
    if fit_variant == "equal_rate":
        classes.append("equal_rate_noninterior_failure")
    elif scenario_id == "process_oracle_observed_transition":
        classes.extend(
            (
                "optimizer_or_nonfinite_failure",
                "oracle_rank_gate_failure",
                "oracle_condition_gate_failure",
            )
        )
    elif scenario_id == "observation_oracle_fixed_transition":
        classes.append("optimizer_or_nonfinite_failure")
    elif "plugin" in required:
        classes.extend(
            (
                "optimizer_or_nonfinite_failure",
                "plugin_rank_gate_failure",
                "plugin_condition_gate_failure",
            )
        )
    return tuple(classes)


def expected_potential_design_rows(scenario_id: str) -> int:
    if scenario_id not in SCENARIO_IDS:
        raise ValueError("design row authority requires a registered scenario")
    if scenario_id == "permuted_arrival_alignment_stress":
        return 4180 * _MAX_INTERVAL_COUNT
    return (1306 if scenario_id == "sparse_expected_failure" else 5225) * _MAX_INTERVAL_COUNT


SCENARIO_DEFINITIONS_HEADER = (
    "scenario_id",
    "scenario_role",
    "generation_model",
    "fit_model",
    "schedule_id",
    "effort_rule",
    "development_replicates",
    "calibration_replicates",
    "holdout_replicates",
    "expected_behavior",
    "truth_access_class",
    "transportability_class",
    "fit_scope",
    "primary_fit_variant",
    "comparator_fit_variant",
)
REPLICATE_RECOVERY_HEADER = (
    "scenario_id",
    "split_id",
    "replicate_id",
    "fit_variant",
    "parameter_id",
    "truth_value",
    "estimate",
    "interval_lower",
    "interval_upper",
    "interval_width",
    "converged",
    "converged_start_count",
    "at_boundary",
    "profile_two_sided",
    "truth_in_interval",
    "log_likelihood",
    "signed_error",
    "absolute_error",
    "gate_result",
)
COVERAGE_CALIBRATION_HEADER = (
    "scenario_id",
    "split_id",
    "fit_variant",
    "parameter_id",
    "replicate_count",
    "converged_count",
    "coverage_count",
    "coverage_fraction",
    "acceptance_lower_count",
    "acceptance_upper_count",
    "median_signed_error",
    "median_absolute_error",
    "median_interval_width",
    "maximum_absolute_error",
    "maximum_interval_width",
    "gate_result",
)
LATENT_TIME_CALIBRATION_HEADER = (
    "scenario_id",
    "split_id",
    "replicate_id",
    "fit_variant",
    "metric_id",
    "sample_size",
    "fit_succeeded",
    "diagnostic_available",
    "observed_value",
    "expected_value",
    "error",
    "gate_result",
)
CONTROL_DECISION_SUMMARY_HEADER = (
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
CONFIG_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "spec_sha256",
        "config_sha256",
        "source_sha256",
        "tracked_state_sha256",
        "model",
        "estimator",
        "parameters",
        "scenarios",
        "seed_partitions",
        "gates",
        "artifact_manifest",
        "boundary_labels",
    }
)
MODEL_CONFIG_KEYS = frozenset(
    {
        "time_grid",
        "hazard_link",
        "hazard_equation",
        "observation_distribution",
        "analyst_fields",
        "oracle_fields",
        "conditionally_independent_cells",
    }
)
ESTIMATOR_CONFIG_KEYS = frozenset(
    {
        "method",
        "optimizer",
        "deterministic_starts",
        "convergence_tolerance",
        "profile_level",
        "lr_cutoff",
        "root_tolerance_fraction",
        "root_max_iterations",
    }
)
SEED_PARTITION_KEYS = frozenset(
    {
        "master_seed",
        "nested_development_replicates",
        "nested_calibration_replicates",
        "nested_holdout_replicates",
        "sparse_development_replicates",
        "sparse_holdout_replicates",
        "control_development_replicates",
        "control_holdout_replicates",
        "predictive_reference_draws",
        "equal_emission_bootstrap_bundles",
    }
)
GATE_CONFIG_KEYS = frozenset(
    {
        "coverage_level",
        "coverage_familywise_alpha",
        "coverage_gate_count",
        "negative_false_positive_rate",
        "sparse_coverage_replicates",
        "sparse_coverage_alpha",
        "profile_width_limits",
        "absolute_error_limits",
        "convergence_limits",
        "pit_familywise_alpha",
        "alignment_logscore_fraction",
        "alignment_correlation_limit",
        "silent_misspecification_rule",
    }
)
BOUNDARY_LABEL_KEYS = frozenset(
    {
        "synthetic_only",
        "scheduled_count_only",
        "fixed_arrival_surface",
        "no_spread_parameter_fit",
        "no_abc_mcmc_or_posterior",
        "no_real_data",
        "no_remote_compute",
        "no_production_adoption",
    }
)
MODEL_PARAMETER_CONFIG_FIELDS = tuple(
    name
    for name in MODEL_PARAMETER_CONTRACT_HEADER
    if name not in {"structural_status", "practical_status"}
)
CONFIG_PARAMETER_ROWS = (
    {
        "parameter_id": "alpha",
        "role": "baseline_cloglog_hazard_intercept",
        "units": "log_hazard",
        "transform": "identity_natural_space",
        "lower_bound": -10.0,
        "upper_bound": -2.0,
        "generating_value": -6.0,
        "fitted_scenarios": "|".join(
            scenario_id
            for scenario_id in SCENARIO_IDS
            if scenario_id != "observation_oracle_fixed_transition"
        ),
        "interpretation": "conditional baseline quasi-extirpation hazard",
    },
    {
        "parameter_id": "beta_driver",
        "role": "scaled_time_since_arrival_effect",
        "units": "log_hazard_per_scaled_time",
        "transform": "identity_natural_space",
        "lower_bound": -3.0,
        "upper_bound": 3.0,
        "generating_value": 1.25,
        "fitted_scenarios": "|".join(
            scenario_id
            for scenario_id in SCENARIO_IDS
            if scenario_id != "observation_oracle_fixed_transition"
        ),
        "interpretation": "conditional association with time since fixed predator arrival",
    },
    {
        "parameter_id": "beta_quality",
        "role": "standardized_habitat_quality_effect",
        "units": "log_hazard_per_quality_sd",
        "transform": "identity_natural_space",
        "lower_bound": -2.0,
        "upper_bound": 2.0,
        "generating_value": -0.60,
        "fitted_scenarios": "|".join(
            scenario_id
            for scenario_id in SCENARIO_IDS
            if scenario_id != "observation_oracle_fixed_transition"
        ),
        "interpretation": "conditional association with standardized habitat quality",
    },
    {
        "parameter_id": "lambda_quasi",
        "role": "quasi_extirpated_effective_count_rate",
        "units": "counts_per_effort",
        "transform": "ordered_rate_natural_space",
        "lower_bound": 0.01,
        "upper_bound": 1.0,
        "generating_value": 0.15,
        "fitted_scenarios": "|".join(
            scenario_id
            for scenario_id in SCENARIO_IDS
            if scenario_id != "process_oracle_observed_transition"
        ),
        "interpretation": "effective count rate after quasi-extirpation",
    },
    {
        "parameter_id": "lambda_present",
        "role": "present_effective_count_rate",
        "units": "counts_per_effort",
        "transform": "ordered_rate_natural_space",
        "lower_bound": 0.25,
        "upper_bound": 10.0,
        "generating_value": 4.0,
        "fitted_scenarios": "|".join(
            scenario_id
            for scenario_id in SCENARIO_IDS
            if scenario_id != "process_oracle_observed_transition"
        ),
        "interpretation": "effective count rate while present",
    },
)
FROZEN_MODEL_CONFIG = {
    "time_grid": list(MODEL_TIMES),
    "hazard_link": "complementary_log_log",
    "hazard_equation": "1-exp(-exp(alpha+beta_driver*G_xt+beta_quality*Q_x))",
    "observation_distribution": "Poisson(E_xt*lambda_state)",
    "analyst_fields": [
        "cell_id",
        "standardized_quality",
        "predator_arrival_time",
        "time",
        "count",
        "effort",
    ],
    "oracle_fields": ["transition_time", "latent_state"],
    "conditionally_independent_cells": True,
}
FROZEN_ESTIMATOR_CONFIG = {
    "method": "exact_discrete_transition_marginal_likelihood",
    "optimizer": "L-BFGS-B",
    "deterministic_starts": 8,
    "convergence_tolerance": 1e-6,
    "profile_level": 0.90,
    "lr_cutoff": PROFILE_LR_CUTOFF,
    "root_tolerance_fraction": PROFILE_ROOT_TOLERANCE_FRACTION,
    "root_max_iterations": PROFILE_ROOT_MAX_ITERATIONS,
}
FROZEN_SEED_PARTITIONS = {
    "master_seed": MASTER_SEED,
    "nested_development_replicates": 12,
    "nested_calibration_replicates": 24,
    "nested_holdout_replicates": 48,
    "sparse_development_replicates": 12,
    "sparse_holdout_replicates": 24,
    "control_development_replicates": 12,
    "control_holdout_replicates": 24,
    "predictive_reference_draws": 199,
    "equal_emission_bootstrap_bundles": 199,
}
FROZEN_GATE_CONFIG = {
    "coverage_level": 0.90,
    "coverage_familywise_alpha": 0.05,
    "coverage_gate_count": 15,
    "negative_false_positive_rate": 0.10,
    "sparse_coverage_replicates": 24,
    "sparse_coverage_alpha": 0.05,
    "profile_width_limits": {
        "alpha": 2.0,
        "beta_driver": 1.0,
        "beta_quality": 1.0,
        "lambda_quasi": 0.30,
        "lambda_present": 1.50,
    },
    "absolute_error_limits": {
        "alpha": 0.40,
        "beta_driver": 0.20,
        "beta_quality": 0.20,
        "lambda_quasi": 0.05,
        "lambda_present": 0.40,
    },
    "convergence_limits": {
        "process_oracle_observed_transition": 0.95,
        "observation_oracle_fixed_transition": 0.95,
        "dense_count_exact_model": 0.95,
        "structured_imperfect_effort": 0.90,
    },
    "pit_familywise_alpha": 0.01,
    "alignment_logscore_fraction": 0.90,
    "alignment_correlation_limit": 0.25,
    "silent_misspecification_rule": "narrow_wrong_requires_available_scientific_warning",
}
FROZEN_BOUNDARY_LABELS = {name: True for name in BOUNDARY_LABEL_KEYS}
PREDICTIVE_REPLICATE_DIAGNOSTICS_HEADER = (
    "scenario_id",
    "split_id",
    "replicate_id",
    "fit_variant",
    "stratum_type",
    "stratum_value",
    "metric_id",
    "sample_size",
    "opportunity_frame_count",
    "opportunity_frame_sha256",
    "dropout_mask_sha256",
    "fit_succeeded",
    "diagnostic_available",
    "observed_value",
    "reference_mean",
    "reference_sd",
    "reference_mcse",
    "standardized_residual",
    "standardized_residual_nonfinite",
    "randomized_pit",
)
PREDICTIVE_CHECK_SUMMARY_HEADER = (
    "scenario_id",
    "split_id",
    "fit_variant",
    "stratum_type",
    "stratum_value",
    "metric_id",
    "replicate_count",
    "diagnostic_count",
    "failed_fit_count",
    "mean_standardized_residual",
    "stouffer_z",
    "ks_statistic",
    "raw_p",
    "holm_adjusted_p",
    "warning",
    "gate_result",
)
IDENTIFIABILITY_PROFILES_HEADER = (
    "scenario_id",
    "split_id",
    "replicate_id",
    "fit_variant",
    "parameter_id",
    "grid_index",
    "parameter_value",
    "profile_log_likelihood",
    "likelihood_ratio_delta",
    "nuisance_converged",
    "inside_interval",
)
PREDICTIVE_STRATA = (
    ("all", "all"),
    *(("habitat_quality_quintile", f"q{index}") for index in range(1, 6)),
    ("time_band", "early"),
    ("time_band", "middle"),
    ("time_band", "late"),
)
PREDICTIVE_METRICS = ("mean_count", "zero_fraction", "variance_to_mean")
AUTHORITY_ENUM_DOMAINS = {
    "scenario_role": ("oracle", "exact_joint", "expected_failure", "negative_control", "stress"),
    "generation_model": (
        "exact_binary",
        "zero_driver",
        "equal_emission",
        "informative_dropout",
        "continuous_abundance",
        "spatial_frailty",
    ),
    "fit_model": (
        "process_oracle",
        "observation_oracle",
        "ordered_joint",
        "equal_emission_joint",
    ),
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
SCENARIO_GATE_FAMILY = dict(
    zip(SCENARIO_IDS, AUTHORITY_ENUM_DOMAINS["gate_family"][:11], strict=True)
)
HOLDOUT_RECEIPT_KEYS = frozenset(
    {
        "schema_version",
        "spec_sha256",
        "config_sha256",
        "source_sha256",
        "tracked_state_sha256",
        "seed_namespace",
        "receipt_sha256",
        "exposed",
        "invalidated",
        "no_contract_change",
    }
)
SOURCE_RECEIPT_KEYS = frozenset(
    {
        "schema_version",
        "serialization_contract",
        "source_commit",
        "parameter_set_id",
        "landscape_sha256",
        "arrival_sha256",
        "independent_check_landscape_sha256",
        "independent_check_arrival_sha256",
        "passed",
    }
)
PREHOLDOUT_RECEIPT_KEYS = frozenset(
    {
        "schema_version",
        "spec_sha256",
        "config_sha256",
        "source_sha256",
        "tracked_state_sha256",
        "tracked_file_manifest",
    }
)
RUNTIME_PROJECTION_KEYS = frozenset(
    {
        "schema_version",
        "workers",
        "safety_factor",
        "measured_task_units",
        "equal_bootstrap_task_unit",
        "calibration_task_durations",
        "holdout_task_durations",
        "calibration_worker_loads",
        "holdout_worker_loads",
        "projected_calibration_seconds",
        "projected_holdout_seconds",
        "holdout_payload_instantiated",
        "scientific_rows_emitted",
        "passed",
    }
)
SOURCE_PROVENANCE_KEYS = frozenset(
    {
        "schema_version",
        "source_commit",
        "parameter_set_id",
        "source_apis",
        "expected_counts",
        "reconciled_counts",
        "landscape_sha256",
        "arrival_sha256",
        "passed",
    }
)
SOURCE_COUNT_KEYS = frozenset(
    {
        "landscape_cell_count",
        "passable_cell_count",
        "water_cell_count",
        "final_colonized_passable_count",
        "finite_prey_extirpation_count",
    }
)
VERIFICATION_KEYS = frozenset(
    {
        "schema_version",
        "spec_sha256",
        "config_sha256",
        "source_sha256",
        "checks",
        "recommendation_class",
        "transportability_class",
        "boundary_labels",
        "passed",
    }
)
ARTIFACT_MANIFEST_DETAIL_KEYS = frozenset(
    {"schema_version", "entries", "represented_artifact_set_sha256"}
)
SCENARIO_CHECK_DETAIL_KEYS = frozenset({"decision_row_id", "gate_result", "reason"})
PARAMETER_STATUS_CHECK_DETAIL_KEYS = frozenset({"decision_row_ids", "status_rows_sha256"})
FINAL_CHECK_DETAIL_KEYS = frozenset(
    {
        "decision_row_id",
        "recommendation_rank",
        "recommendation_class",
        "reason",
        "transportability_class",
    }
)
TRACKED_STATE_CHECK_DETAIL_KEYS = frozenset(
    {
        "tracked_state_sha256",
        "runtime_projection_passed",
        "source_provenance_passed",
        "holdout_manifest_exposed",
    }
)
RUNTIME_TASK_UNIT_KEYS = frozenset(
    field.name for field in RuntimeTaskUnit.__dataclass_fields__.values()
)
EQUAL_BOOTSTRAP_TASK_KEYS = frozenset(
    {
        "task_id",
        "benchmark_split",
        "bundle_index",
        "pseudo_replicate_first",
        "pseudo_replicate_last",
        "measured_duration_seconds",
        "calibration_repeat_count",
        "holdout_repeat_count",
        "scientific_row",
    }
)
RUNTIME_SAFETY_FACTOR = 1.20
RUNTIME_PROJECTION_LIMIT_SECONDS = 1500.0
RUNTIME_TASK_UNIT_AUTHORITY = tuple(
    {
        "task_id": f"benchmark|scenario={scenario_id}",
        "scenario_id": scenario_id,
        "benchmark_split": "calibration" if scenario_id in NESTED_SCENARIOS else "development",
        "benchmark_replicate_first": 0,
        "benchmark_replicate_last": (
            23 if scenario_id == "no_emission_contrast_negative_control" else 0
        ),
        "calibration_repeat_count": 24 if scenario_id in NESTED_SCENARIOS else 0,
        "holdout_repeat_count": (
            1
            if scenario_id == "no_emission_contrast_negative_control"
            else 48
            if scenario_id in NESTED_SCENARIOS
            else 24
        ),
        "includes_profiles": scenario_id != "no_emission_contrast_negative_control",
        "predictive_reference_count": (
            0 if scenario_id == "process_oracle_observed_transition" else 199
        ),
        "scientific_row": scenario_id != "no_emission_contrast_negative_control",
    }
    for scenario_id in SCENARIO_IDS
)
EQUAL_BOOTSTRAP_RUNTIME_AUTHORITY = {
    "task_id": (
        "benchmark|scenario=no_emission_contrast_negative_control|component=bootstrap|bundle=0000"
    ),
    "benchmark_split": "development",
    "bundle_index": 0,
    "pseudo_replicate_first": 0,
    "pseudo_replicate_last": 23,
    "calibration_repeat_count": 0,
    "holdout_repeat_count": 199,
    "scientific_row": False,
}
CSV_HEADERS = {
    "model_parameter_contract.csv": MODEL_PARAMETER_CONTRACT_HEADER,
    "scenario_definitions.csv": SCENARIO_DEFINITIONS_HEADER,
    "fit_execution_evidence.csv": FIT_EXECUTION_EVIDENCE_HEADER,
    "replicate_recovery.csv": REPLICATE_RECOVERY_HEADER,
    "coverage_calibration.csv": COVERAGE_CALIBRATION_HEADER,
    "latent_time_calibration.csv": LATENT_TIME_CALIBRATION_HEADER,
    "predictive_replicate_diagnostics.csv": PREDICTIVE_REPLICATE_DIAGNOSTICS_HEADER,
    "predictive_check_summary.csv": PREDICTIVE_CHECK_SUMMARY_HEADER,
    "identifiability_profiles.csv": IDENTIFIABILITY_PROFILES_HEADER,
    "control_decision_summary.csv": CONTROL_DECISION_SUMMARY_HEADER,
}


SCENARIO_EVIDENCE_REGISTRY = (
    ScenarioEvidence(
        "process_oracle_observed_transition",
        "oracle_only",
        "replicate",
        "canonical",
        None,
        True,
        5225,
    ),
    ScenarioEvidence(
        "observation_oracle_fixed_transition",
        "oracle_only",
        "replicate",
        "canonical",
        None,
        False,
        0,
    ),
    ScenarioEvidence(
        "dense_count_exact_model", "analyst_firewalled", "replicate", "canonical", None, True, 5225
    ),
    ScenarioEvidence(
        "structured_imperfect_effort",
        "analyst_firewalled",
        "replicate",
        "canonical",
        None,
        True,
        5225,
    ),
    ScenarioEvidence(
        "sparse_expected_failure", "analyst_firewalled", "replicate", "canonical", None, True, 1306
    ),
    ScenarioEvidence(
        "zero_driver_effect_negative_control",
        "analyst_firewalled",
        "replicate",
        "canonical",
        None,
        True,
        5225,
    ),
    ScenarioEvidence(
        "permuted_arrival_alignment_stress",
        "stress_evaluator_only",
        "replicate",
        "permuted_alignment",
        "correct_alignment",
        True,
        1045,
    ),
    ScenarioEvidence(
        "no_emission_contrast_negative_control",
        "analyst_firewalled",
        "scenario_shared",
        "equal_rate",
        "ordered_emission",
        False,
        0,
    ),
    ScenarioEvidence(
        "informative_dropout_misspecification_stress",
        "stress_evaluator_only",
        "replicate",
        "canonical",
        None,
        True,
        5225,
    ),
    ScenarioEvidence(
        "goal018_continuous_abundance_stress",
        "stress_evaluator_only",
        "replicate",
        "canonical",
        None,
        False,
        0,
    ),
    ScenarioEvidence(
        "spatial_frailty_stress",
        "stress_evaluator_only",
        "replicate",
        "canonical",
        None,
        True,
        5225,
    ),
)
SCENARIO_LOCAL_REASONS = {
    "process_oracle_observed_transition": (
        "pass",
        "contract_failure:process_oracle_failed",
    ),
    "observation_oracle_fixed_transition": (
        "pass",
        "contract_failure:observation_oracle_failed",
    ),
    "dense_count_exact_model": (
        "pass",
        "contract_failure:dense_evidence_invalid",
        "confounding:dense_joint_failed",
    ),
    "structured_imperfect_effort": (
        "pass",
        "contract_failure:structured_not_calibrated",
        "confounding:structured_estimand_unidentified",
        "structured_limitation:structured_precision_recovery_failed",
    ),
    "sparse_expected_failure": ("pass", "contract_failure:sparse_honesty_failed"),
    "zero_driver_effect_negative_control": (
        "pass",
        "contract_failure:zero_driver_unavailable",
        "confounding:zero_driver_false_signal",
    ),
    "permuted_arrival_alignment_stress": (
        "pass",
        "contract_failure:alignment_contract_or_availability_failed",
        "contract_failure:alignment_silent_misspecification",
        "confounding:arrival_alignment_not_discriminated",
    ),
    "no_emission_contrast_negative_control": (
        "pass",
        "contract_failure:equal_emission_control_failed",
    ),
    "informative_dropout_misspecification_stress": (
        "pass",
        "contract_failure:informative_dropout_unavailable",
        "contract_failure:informative_dropout_silent_misspecification",
    ),
    "goal018_continuous_abundance_stress": (
        "pass",
        "contract_failure:continuous_abundance_unavailable",
        "contract_failure:continuous_abundance_silent_misspecification",
    ),
    "spatial_frailty_stress": (
        "pass",
        "contract_failure:spatial_frailty_unavailable",
        "contract_failure:spatial_frailty_silent_misspecification",
    ),
}
SCENARIO_EVIDENCE_FIELDS = {
    "process_oracle_observed_transition": frozenset(
        {
            "schema_valid",
            "design_pass",
            "fit_available",
            "convergence_pass",
            "coverage_pass",
            "recovery_pass",
        }
    ),
    "observation_oracle_fixed_transition": frozenset(
        {
            "schema_valid",
            "design_pass",
            "fit_available",
            "convergence_pass",
            "coverage_pass",
            "recovery_pass",
        }
    ),
    "dense_count_exact_model": frozenset(
        {
            "schema_valid",
            "fit_available",
            "predictive_available",
            "plugin_available",
            "convergence_pass",
            "coverage_pass",
            "recovery_pass",
            "predictive_pass",
            "identified",
        }
    ),
    "structured_imperfect_effort": frozenset(
        {
            "schema_valid",
            "fit_available",
            "predictive_available",
            "plugin_available",
            "convergence_pass",
            "coverage_pass",
            "recovery_pass",
            "predictive_pass",
            "identified",
            "plugin_rank",
            "plugin_condition",
        }
    ),
    "sparse_expected_failure": frozenset(
        {
            "schema_valid",
            "fit_available",
            "predictive_available",
            "plugin_available",
            "predictive_pass",
            "sparse_coverage_pass",
            "sparse_width_pass",
        }
    ),
    "zero_driver_effect_negative_control": frozenset(
        {
            "schema_valid",
            "fit_available",
            "predictive_available",
            "predictive_pass",
            "plugin_available",
            "decidable_intervals",
            "zero_exclusions",
        }
    ),
    "permuted_arrival_alignment_stress": frozenset(
        {
            "schema_valid",
            "fit_available",
            "predictive_available",
            "plugin_available",
            "warning_available",
            "warning_forced",
            "alignment_correlation",
            "alignment_pairs",
            "alignment_wins",
        }
    ),
    "no_emission_contrast_negative_control": frozenset(
        {
            "schema_valid",
            "fit_available",
            "bootstrap_available",
            "equal_p",
            "equal_refits",
            "equal_status_rows",
        }
    ),
    "informative_dropout_misspecification_stress": frozenset(
        {
            "schema_valid",
            "fit_available",
            "predictive_available",
            "plugin_available",
            "warning_available",
            "warning_forced",
            "narrow_wrong",
        }
    ),
    "goal018_continuous_abundance_stress": frozenset(
        {
            "schema_valid",
            "fit_available",
            "predictive_available",
            "plugin_available",
            "warning_available",
            "warning_forced",
        }
    ),
    "spatial_frailty_stress": frozenset(
        {
            "schema_valid",
            "fit_available",
            "predictive_available",
            "plugin_available",
            "warning_available",
            "warning_forced",
            "narrow_wrong",
        }
    ),
}
LATENT_APPLICABILITY = tuple(
    (row.scenario_id, row.latent_time_applicable, row.latent_time_sample_size)
    for row in SCENARIO_EVIDENCE_REGISTRY
)


SCENARIO_DEFINITIONS = tuple(
    ScenarioDefinition(
        scenario_id=row.scenario_id,
        scenario_role=(
            "oracle"
            if row.truth_access_class == "oracle_only"
            else "stress"
            if row.truth_access_class == "stress_evaluator_only"
            else "expected_failure"
            if row.scenario_id == "sparse_expected_failure"
            else "negative_control"
            if "negative_control" in row.scenario_id
            else "exact_joint"
        ),
        generation_model=(
            "zero_driver"
            if row.scenario_id == "zero_driver_effect_negative_control"
            else "equal_emission"
            if row.scenario_id == "no_emission_contrast_negative_control"
            else "informative_dropout"
            if row.scenario_id == "informative_dropout_misspecification_stress"
            else "continuous_abundance"
            if row.scenario_id == "goal018_continuous_abundance_stress"
            else "spatial_frailty"
            if row.scenario_id == "spatial_frailty_stress"
            else "exact_binary"
        ),
        fit_model=(
            "process_oracle"
            if row.scenario_id == "process_oracle_observed_transition"
            else "observation_oracle"
            if row.scenario_id == "observation_oracle_fixed_transition"
            else "equal_emission_joint"
            if row.scenario_id == "no_emission_contrast_negative_control"
            else "ordered_joint"
        ),
        schedule_id=next(
            definition.schedule_id
            for definition in _SCENARIO_SCHEDULE_DEFINITIONS
            if definition.scenario_id == row.scenario_id
        ),
        effort_rule=next(
            definition.effort_rule
            for definition in _SCENARIO_SCHEDULE_DEFINITIONS
            if definition.scenario_id == row.scenario_id
        ),
        development_replicates=12,
        calibration_replicates=24 if row.scenario_id in NESTED_SCENARIOS else 0,
        holdout_replicates=48 if row.scenario_id in NESTED_SCENARIOS else 24,
        expected_behavior=(
            "recover"
            if row.scenario_id in NESTED_SCENARIOS[:4]
            else "weaken_honestly"
            if row.scenario_id == "sparse_expected_failure"
            else "no_false_signal"
            if row.scenario_id == "zero_driver_effect_negative_control"
            else "unidentifiable"
            if row.scenario_id == "no_emission_contrast_negative_control"
            else "predictive_warning"
        ),
        truth_access_class=row.truth_access_class,
        transportability_class="scheduled_count_only_point_process_bridge_required",
        fit_scope=row.fit_scope,
        primary_fit_variant=row.primary_fit_variant,
        comparator_fit_variant=row.comparator_fit_variant,
    )
    for row in SCENARIO_EVIDENCE_REGISTRY
)


def validate_scenario_definition_rows(
    rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    validated = tuple(dict(row) for row in rows)
    if any(tuple(row) != SCENARIO_DEFINITIONS_HEADER for row in rows):
        raise ValueError("scenario definitions have the wrong literal header or order")
    if validated != tuple(asdict(row) for row in SCENARIO_DEFINITIONS):
        raise ValueError("scenario definitions must reproduce the complete literal rows")
    return validated


def validate_model_parameter_contract_rows(
    rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    if len(rows) != len(CONFIG_PARAMETER_ROWS) or any(
        tuple(row) != MODEL_PARAMETER_CONTRACT_HEADER for row in rows
    ):
        raise ValueError("model parameter contract has the wrong literal schema")
    validated: list[dict[str, object]] = []
    statuses = {"identified", "unidentified", "not_applicable"}
    for row, authority in zip(rows, CONFIG_PARAMETER_ROWS, strict=True):
        if any(row[name] != authority[name] for name in MODEL_PARAMETER_CONFIG_FIELDS):
            raise ValueError("model parameter contract differs from literal parameter authority")
        if row["structural_status"] not in statuses or row["practical_status"] not in statuses:
            raise ValueError("model parameter status is outside its literal domain")
        validated.append(dict(row))
    return tuple(validated)


def validate_equal_emission_status_rows(
    rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    validated = tuple(dict(row) for row in rows)
    if validated != EQUAL_EMISSION_STATUS_ROWS:
        raise ValueError("equal-emission status evidence must contain the six literal rows")
    return validated


def validate_report_links(report_text: str) -> None:
    if type(report_text) is not str:
        raise TypeError("report text must be string")
    positions = tuple(report_text.find(f"]({path})") for path in REPORT_REQUIRED_LINKS)
    if any(position < 0 for position in positions) or positions != tuple(sorted(positions)):
        raise ValueError("report links must contain the complete literal evidence order")


def validate_visual_source_tables(
    bindings: Sequence[tuple[str, Sequence[str]]],
) -> None:
    canonical = tuple((path, tuple(sources)) for path, sources in bindings)
    if canonical != VISUAL_SOURCE_TABLES:
        raise ValueError("visual source tables differ from the literal registry")


def validate_scenario_registry(rows: Sequence[ScenarioEvidence]) -> tuple[str, ...]:
    canonical = SCENARIO_EVIDENCE_REGISTRY
    if tuple(rows) != canonical:
        raise ValueError("scenario registry must be the literal ordered mapping")
    truth_classes = {"oracle_only", "analyst_firewalled", "stress_evaluator_only"}
    if any(row.truth_access_class not in truth_classes for row in rows):
        raise ValueError("unknown truth access class")
    return tuple(row.scenario_id for row in rows)


def _contains_forbidden_key(value: object, forbidden: frozenset[str]) -> bool:
    if isinstance(value, Mapping):
        return any(
            key in forbidden or _contains_forbidden_key(item, forbidden)
            for key, item in value.items()
        )
    if isinstance(value, (tuple, list)):
        return any(_contains_forbidden_key(item, forbidden) for item in value)
    return False


def validate_analyst_fit_payload(payload: Mapping[str, object]) -> None:
    forbidden = frozenset({"original_alignment", "dropout_state", "goal018_abundance", "frailty"})
    if _contains_forbidden_key(payload, forbidden):
        raise ValueError("truth firewall violation")


def validate_control_fit_payload(payload: Mapping[str, object]) -> None:
    forbidden = frozenset({"generating_zero_label", "generating_equal_label"})
    if _contains_forbidden_key(payload, forbidden):
        raise ValueError("control truth cannot enter fit construction")


def validate_fit_execution_row(row: Mapping[str, object]) -> dict[str, object]:
    if set(row) != set(FIT_EXECUTION_EVIDENCE_HEADER):
        raise ValueError("fit execution row has the wrong schema")
    result = dict(row)
    scenario_id = result["scenario_id"]
    if scenario_id not in SCENARIO_IDS:
        raise ValueError("unknown scenario_id")
    if result["split_id"] not in ("development", "calibration", "holdout"):
        raise ValueError("unknown split_id")
    _split_replicate_count(scenario_id, result["split_id"])
    if result["fit_scope"] not in FIT_SCOPES or result["fit_variant"] not in FIT_VARIANTS:
        raise ValueError("unknown fit identity")
    if type(result["fit_index"]) is not int or result["fit_index"] < 0:
        raise ValueError("fit_index must be a nonnegative integer")
    for name in ("source_replicate_first", "source_replicate_last", "source_replicate_count"):
        if type(result[name]) is not int or cast(int, result[name]) < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    scope = result["fit_scope"]
    fit_index = result["fit_index"]
    first = cast(int, result["source_replicate_first"])
    last = cast(int, result["source_replicate_last"])
    count = cast(int, result["source_replicate_count"])
    if scope == "replicate" and (fit_index != first or fit_index != last or count != 1):
        raise ValueError("replicate identity requires matching indices and source count one")
    if scope == "scenario_shared":
        expected_last = 11 if result["split_id"] == "development" else 23
        if scenario_id != "no_emission_contrast_negative_control" or (
            fit_index,
            first,
            last,
            count,
        ) != (0, 0, expected_last, expected_last + 1):
            raise ValueError("scenario-shared fit identity is invalid")
    if scope == "bootstrap_shared" and (
        scenario_id != "no_emission_contrast_negative_control"
        or result["split_id"] != "holdout"
        or not 0 <= fit_index <= 198
        or (first, last, count) != (0, 23, 24)
    ):
        raise ValueError("bootstrap-shared fit identity is invalid")
    registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
    if scope != registry.fit_scope and not (
        scenario_id == "no_emission_contrast_negative_control" and scope == "bootstrap_shared"
    ):
        raise ValueError("fit scope is inconsistent with the scenario registry")
    if scope == "replicate" and fit_index >= _split_replicate_count(
        scenario_id, result["split_id"]
    ):
        raise ValueError("fit_index is outside the frozen split frame")
    permitted_variants = {registry.primary_fit_variant, registry.comparator_fit_variant}
    if result["fit_variant"] not in permitted_variants:
        raise ValueError("fit variant is not registered for scenario")
    row_type = result["evidence_row_type"]
    if row_type not in FIT_EVIDENCE_ROW_TYPES:
        raise ValueError("fit execution evidence_row_type is not literal")
    if row_type == "design_diagnostic":
        if any(result[name] is not None for name in _FIT_RESULT_ONLY_FIELDS):
            raise ValueError("design diagnostic row must leave all fit-result fields null")
        design_kind = result["design_kind"]
        if design_kind not in required_design_kinds(scenario_id, result["fit_variant"]):
            raise ValueError("design kind is not applicable to this scenario and variant")
        expected_provenance, expected_role = DESIGN_LABELS[design_kind]
        if (
            result["design_provenance"] != expected_provenance
            or result["design_role"] != expected_role
        ):
            raise ValueError("design provenance or role differs from literal authority")
        n_rows = result["design_n_rows"]
        maximum_rows = expected_potential_design_rows(scenario_id)
        if type(n_rows) is not int or n_rows < 1:
            raise ValueError("design row count must be a positive integer")
        if design_kind == "oracle":
            if n_rows > maximum_rows:
                raise ValueError("oracle design row count exceeds its potential frame")
        elif n_rows != maximum_rows:
            raise ValueError("potential and plugin design row counts must equal their exact frame")
        if result["design_n_columns"] != 3:
            raise ValueError("applicable design diagnostics require exactly three columns")
        issued_frame = issue_analyst_fit_frame(scenario_id)
        expected_frame_count = issued_frame.cell_count
        expected_frame_sha256 = issued_frame.cell_sha256
        if (
            result["design_frame_cell_count"] != expected_frame_count
            or result["design_frame_sha256"] != expected_frame_sha256
        ):
            raise ValueError("design diagnostic is not bound to its exact canonical cell frame")
        rank = result["design_rank"]
        if type(rank) is not int or not 0 <= rank <= min(n_rows, 3):
            raise ValueError("design rank must be within its persisted row/column dimensions")
        condition = result["design_condition_number"]
        if condition is not None and (
            type(condition) not in (int, float)
            or not isfinite(float(cast(float, condition)))
            or float(cast(float, condition)) < 1.0
        ):
            raise ValueError("design condition must be finite, at least one, or null")
        if rank < 3 and condition is not None:
            raise ValueError("rank-deficient design condition must serialize as null")
        expected_pass = (
            n_rows >= 3
            and rank == 3
            and condition is not None
            and float(cast(float, condition)) < 1e8
        )
        if (
            type(result["design_passed"]) is not bool
            or result["design_passed"] is not expected_pass
        ):
            raise ValueError("design pass must derive from rank and the open condition boundary")
        failure_code = result["design_failure_code"]
        if expected_pass:
            if failure_code is not None:
                raise ValueError("passing design diagnostic must have null failure code")
        else:
            if failure_code not in DESIGN_FAILURE_CODES:
                raise ValueError("failed design diagnostic requires a typed failure code")
            if rank < 3 and failure_code not in {
                "rank_deficient",
                "joint_fit_failed_or_nonfinite",
                "not_evaluated_potential_failed",
                "process_oracle_fit_failed_or_nonfinite",
            }:
                raise ValueError("rank-deficient design carries the wrong failure code")
            if rank == 3 and condition is not None and failure_code != "condition_limit_failed":
                raise ValueError("condition-boundary design carries the wrong failure code")
            if failure_code in {
                "joint_fit_failed_or_nonfinite",
                "not_evaluated_potential_failed",
                "process_oracle_fit_failed_or_nonfinite",
            } and (rank != 0 or condition is not None):
                raise ValueError("not-evaluated design state requires rank zero and null condition")
            if design_kind == "potential" and failure_code not in {
                "rank_deficient",
                "condition_limit_failed",
            }:
                raise ValueError("potential design carries a downstream failure code")
        return result
    if any(result[name] is not None for name in _DESIGN_ONLY_FIELDS):
        raise ValueError("fit-result row must leave all design diagnostic fields null")
    if type(result["fit_succeeded"]) is not bool:
        raise ValueError("fit_succeeded must be bool")
    succeeded = result["fit_succeeded"]
    if succeeded:
        if result["fit_failure_class"] is not None or result["failure_code"] is not None:
            raise ValueError("successful row must have null failure class and code")
        if result["log_likelihood"] is None or not isfinite(
            float(cast(float, result["log_likelihood"]))
        ):
            raise ValueError("successful row requires finite log likelihood")
        if result["fit_variant"] == "equal_rate":
            if any(
                result[name] is not None
                for name in (
                    "converged_start_count",
                    "best_start_index",
                    "best_two_log_likelihoods_agree",
                )
            ):
                raise ValueError("closed-form equal-rate fit has null start fields")
        else:
            if (
                type(result["converged_start_count"]) is not int
                or not 6 <= result["converged_start_count"] <= 8
            ):
                raise ValueError("successful multistart requires at least six starts")
            if (
                type(result["best_start_index"]) is not int
                or not 1 <= result["best_start_index"] <= 8
            ):
                raise ValueError("successful multistart requires a valid best start")
            if result["best_two_log_likelihoods_agree"] is not True:
                raise ValueError("successful multistart requires best-two agreement")
        accepted_parameters = (
            ("lambda_equal",)
            if result["fit_variant"] == "equal_rate"
            else FIT_PARAMETER_IDS.get(scenario_id, ORDERED_PARAMETER_IDS)
        )
        estimate_fields = {
            "alpha": "alpha_estimate",
            "beta_driver": "beta_driver_estimate",
            "beta_quality": "beta_quality_estimate",
            "lambda_quasi": "lambda_quasi_estimate",
            "lambda_present": "lambda_present_estimate",
            "lambda_equal": "lambda_equal_estimate",
        }
        boundary_parameters: list[str] = []
        for parameter_id, field_name in estimate_fields.items():
            value = result[field_name]
            if parameter_id in accepted_parameters:
                if type(value) not in (int, float) or not isfinite(float(cast(float, value))):
                    raise ValueError(f"successful fit requires finite {field_name}")
                lower, upper = _FIT_PARAMETER_SUPPORTS[parameter_id]
                numeric = float(cast(float, value))
                if not lower <= numeric <= upper:
                    raise ValueError(
                        f"successful {parameter_id} estimate is outside its natural support"
                    )
                if numeric in (lower, upper):
                    boundary_parameters.append(parameter_id)
            elif value is not None:
                raise ValueError(f"successful fit cannot populate {field_name}")
        actual_boundary_ids = tuple(boundary_parameters)
        if result["fit_variant"] == "equal_rate" and actual_boundary_ids:
            raise ValueError("equal-rate MLE must be finite and strictly interior")
        if type(result["at_boundary"]) is not bool:
            raise ValueError("successful fit requires a typed boundary state")
        boundary_ids = result["boundary_parameter_ids"]
        expected_boundary_ids = "|".join(actual_boundary_ids) or None
        if result["at_boundary"] is not bool(actual_boundary_ids) or (
            boundary_ids != expected_boundary_ids
        ):
            raise ValueError(
                "boundary state and parameter identities must match natural-support boundaries"
            )
        quasi = result["lambda_quasi_estimate"]
        present = result["lambda_present_estimate"]
        if (
            quasi is not None
            and present is not None
            and not float(cast(float, quasi)) < float(cast(float, present))
        ):
            raise ValueError("successful ordered fit requires strict rate ordering")
        if scenario_id == "permuted_arrival_alignment_stress":
            score = result["heldout_log_score"]
            if type(score) not in (int, float) or not isfinite(float(cast(float, score))):
                raise ValueError("arrival fit requires a finite fixed-frame heldout score")
        elif result["heldout_log_score"] is not None:
            raise ValueError("heldout score is only permitted for the arrival stress")
    if not succeeded:
        failure_class = result["fit_failure_class"]
        if failure_class not in permitted_persisted_fit_failure_classes(
            scenario_id, result["fit_variant"]
        ):
            raise ValueError("failed row requires an applicable typed fit failure class")
        if type(result["failure_code"]) is not str or not result["failure_code"]:
            raise ValueError("failed row requires failure_code")
        if (
            result["failure_code"] == "equal_rate_mle_noninterior"
            and failure_class != "equal_rate_noninterior_failure"
        ):
            raise ValueError("equal-rate boundary code requires its typed failure class")
        if (
            failure_class == "equal_rate_noninterior_failure"
            and result["failure_code"] != "equal_rate_mle_noninterior"
        ):
            raise ValueError("equal-rate noninterior failure requires its literal code")
        for name in (
            "alpha_estimate",
            "beta_driver_estimate",
            "beta_quality_estimate",
            "lambda_quasi_estimate",
            "lambda_present_estimate",
            "lambda_equal_estimate",
            "log_likelihood",
            "heldout_log_score",
        ):
            if result[name] is not None:
                raise ValueError("failed row cannot carry accepted estimates")
        if result["at_boundary"] is not None or result["boundary_parameter_ids"] is not None:
            raise ValueError("failed row cannot carry accepted boundary fields")
        count_value = result["converged_start_count"]
        if count_value is not None and (type(count_value) is not int or not 0 <= count_value <= 8):
            raise ValueError("failed row has invalid converged_start_count")
        best_index = result["best_start_index"]
        if best_index is not None and (type(best_index) is not int or not 1 <= best_index <= 8):
            raise ValueError("failed row has invalid best_start_index")
        best_two_agree = result["best_two_log_likelihoods_agree"]
        if best_two_agree is not None and type(best_two_agree) is not bool:
            raise ValueError("failed row best-two agreement must be bool or null")
        optimizer_fields = (
            result["converged_start_count"],
            result["best_start_index"],
            result["best_two_log_likelihoods_agree"],
        )
        if failure_class in {
            "potential_rank_gate_failure",
            "potential_condition_gate_failure",
            "oracle_rank_gate_failure",
            "oracle_condition_gate_failure",
            "equal_rate_noninterior_failure",
        } and any(value is not None for value in optimizer_fields):
            raise ValueError("pre-optimizer or closed-form failure forbids optimizer fields")
        if failure_class in {
            "plugin_rank_gate_failure",
            "plugin_condition_gate_failure",
        } and (
            type(count_value) is not int
            or not 6 <= count_value <= 8
            or type(best_index) is not int
            or not 1 <= best_index <= 8
            or best_two_agree is not True
        ):
            raise ValueError("plug-in gate failure requires a successful optimizer result")
        if failure_class == "optimizer_or_nonfinite_failure":
            if count_value is None:
                if best_index is not None or best_two_agree is not None:
                    raise ValueError("absent optimizer count requires null companion fields")
            elif count_value == 0 and best_index is not None:
                raise ValueError("zero successful starts cannot identify a best start")
            elif count_value > 0 and best_index is None:
                raise ValueError("positive successful starts require a best start index")
            if best_two_agree is True and (count_value or 0) < 2:
                raise ValueError("best-two agreement requires at least two successful starts")
    return result


def validate_fit_execution_rows(
    rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    validated = tuple(validate_fit_execution_row(row) for row in rows)
    keys = tuple(_fit_execution_evidence_sort_key(row) for row in validated)
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate fit execution evidence primary key")
    if keys != tuple(sorted(keys)):
        raise ValueError("fit execution evidence rows must be sorted by the literal key")
    return validated


def _fit_execution_evidence_sort_key(row: Mapping[str, object]) -> tuple[object, ...]:
    row_type = cast(str, row["evidence_row_type"])
    design_kind = row["design_kind"]
    return (
        cast(str, row["scenario_id"]),
        cast(str, row["split_id"]),
        cast(str, row["fit_scope"]),
        cast(str, row["fit_variant"]),
        cast(int, row["fit_index"]),
        FIT_EVIDENCE_ROW_TYPES.index(row_type),
        -1 if design_kind is None else DESIGN_KINDS.index(cast(str, design_kind)),
    )


def _partition_fit_execution_evidence(
    rows: Sequence[Mapping[str, object]],
) -> tuple[tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    validated = validate_fit_execution_rows(rows)
    fits = tuple(row for row in validated if row["evidence_row_type"] == "fit_result")
    designs = tuple(row for row in validated if row["evidence_row_type"] == "design_diagnostic")
    return fits, designs


def _fit_result_identity(row: Mapping[str, object]) -> tuple[object, ...]:
    return tuple(
        row[name] for name in ("scenario_id", "split_id", "fit_scope", "fit_variant", "fit_index")
    )


def _expected_design_identity_frame(
    fit_rows: Sequence[Mapping[str, object]],
) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (
            *_fit_result_identity(row),
            design_kind,
        )
        for row in fit_rows
        for design_kind in required_design_kinds(
            cast(str, row["scenario_id"]), cast(str, row["fit_variant"])
        )
    )


def validate_fit_design_state_machine(
    fit_rows: Sequence[Mapping[str, object]],
    design_rows: Sequence[Mapping[str, object]],
) -> None:
    """Reject impossible persisted fit/design combinations before reduction."""

    validated_fits = tuple(validate_fit_execution_row(row) for row in fit_rows)
    validated_designs = tuple(validate_fit_execution_row(row) for row in design_rows)
    if any(row["evidence_row_type"] != "fit_result" for row in validated_fits) or any(
        row["evidence_row_type"] != "design_diagnostic" for row in validated_designs
    ):
        raise ValueError("fit/design state machine received the wrong evidence row type")
    fit_lookup = {_fit_result_identity(row): row for row in validated_fits}
    design_lookup = {
        (*_fit_result_identity(row), cast(str, row["design_kind"])): row
        for row in validated_designs
    }
    expected_design_keys = {
        (*_fit_result_identity(row), design_kind)
        for row in validated_fits
        for design_kind in required_design_kinds(
            cast(str, row["scenario_id"]), cast(str, row["fit_variant"])
        )
    }
    if (
        len(fit_lookup) != len(validated_fits)
        or len(design_lookup) != len(validated_designs)
        or set(design_lookup) != expected_design_keys
    ):
        raise ValueError("fit/design state machine requires one exact diagnostic frame")

    def require_state(diagnostic: Mapping[str, object], state: str) -> None:
        rank = diagnostic["design_rank"]
        condition = diagnostic["design_condition_number"]
        code = diagnostic["design_failure_code"]
        passed = diagnostic["design_passed"]
        matches = False
        if state == "pass":
            matches = passed is True and rank == 3 and code is None
        elif state == "rank_deficient":
            matches = (
                passed is False
                and type(rank) is int
                and rank < 3
                and condition is None
                and code == "rank_deficient"
            )
        elif state == "condition_limit_failed":
            matches = (
                passed is False
                and rank == 3
                and type(condition) in (int, float)
                and float(cast(float, condition)) >= _DESIGN_CONDITION_LIMIT
                and code == "condition_limit_failed"
            )
        elif state == "not_evaluated_potential_failed":
            matches = (
                passed is False
                and rank == 0
                and condition is None
                and code == "not_evaluated_potential_failed"
            )
        elif state == "joint_fit_failed_or_nonfinite":
            matches = (
                passed is False
                and rank == 0
                and condition is None
                and code == "joint_fit_failed_or_nonfinite"
            )
        elif state == "process_oracle_fit_failed_or_nonfinite":
            matches = (
                passed is False
                and rank == 0
                and condition is None
                and code == "process_oracle_fit_failed_or_nonfinite"
            )
        if not matches:
            raise ValueError(f"fit/design transition contradiction: expected {state} diagnostic")

    for identity, fit in fit_lookup.items():
        required = required_design_kinds(
            cast(str, fit["scenario_id"]), cast(str, fit["fit_variant"])
        )
        diagnostics = {kind: design_lookup[(*identity, kind)] for kind in required}
        potential = diagnostics["potential"]
        fit_succeeded = cast(bool, fit["fit_succeeded"])
        if fit_succeeded:
            for diagnostic in diagnostics.values():
                require_state(diagnostic, "pass")
            continue
        failure_class = cast(str, fit["fit_failure_class"])
        if failure_class in {
            "potential_rank_gate_failure",
            "potential_condition_gate_failure",
        }:
            require_state(
                potential,
                "rank_deficient"
                if failure_class == "potential_rank_gate_failure"
                else "condition_limit_failed",
            )
            for kind in required:
                if kind != "potential":
                    require_state(diagnostics[kind], "not_evaluated_potential_failed")
            continue
        require_state(potential, "pass")
        if failure_class == "optimizer_or_nonfinite_failure":
            if "plugin" in diagnostics:
                require_state(diagnostics["plugin"], "joint_fit_failed_or_nonfinite")
            if "oracle" in diagnostics:
                require_state(diagnostics["oracle"], "process_oracle_fit_failed_or_nonfinite")
            continue
        if failure_class in {
            "plugin_rank_gate_failure",
            "plugin_condition_gate_failure",
        }:
            require_state(
                diagnostics["plugin"],
                "rank_deficient"
                if failure_class == "plugin_rank_gate_failure"
                else "condition_limit_failed",
            )
            continue
        if failure_class in {
            "oracle_rank_gate_failure",
            "oracle_condition_gate_failure",
        }:
            require_state(
                diagnostics["oracle"],
                "rank_deficient"
                if failure_class == "oracle_rank_gate_failure"
                else "condition_limit_failed",
            )
            continue
        if failure_class == "equal_rate_noninterior_failure":
            if required != ("potential",):
                raise ValueError("equal-rate failure transition has downstream diagnostics")
            continue
        raise ValueError("fit/design state machine encountered an unhandled failure class")


def validate_complete_fit_execution_frame(
    rows: Sequence[Mapping[str, object]], *, scenario_id: str, split_id: str
) -> tuple[dict[str, object], ...]:
    expected_count = _split_replicate_count(scenario_id, split_id)
    registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
    validated, _designs = _partition_fit_execution_evidence(rows)
    if any(row["scenario_id"] != scenario_id or row["split_id"] != split_id for row in validated):
        raise ValueError("complete fit frame contains a foreign scenario or split")
    if registry.fit_scope == "replicate":
        variants = tuple(
            variant
            for variant in (registry.primary_fit_variant, registry.comparator_fit_variant)
            if variant is not None
        )
        observed = {
            (cast(int, row["fit_index"]), cast(str, row["fit_variant"])) for row in validated
        }
        expected = {(index, variant) for index in range(expected_count) for variant in variants}
        if observed != expected or len(validated) != len(expected):
            raise ValueError("complete fit frame is missing or duplicates a canonical fit identity")
    elif scenario_id == "no_emission_contrast_negative_control":
        if split_id not in ("development", "holdout"):
            raise ValueError("equal-emission shared fit has no calibration split")
        expected_variants = {"equal_rate", "ordered_emission"}
        if (
            len(validated) != 2
            or {cast(str, row["fit_variant"]) for row in validated} != expected_variants
            or any(row["fit_scope"] != "scenario_shared" for row in validated)
        ):
            raise ValueError("complete equal-emission frame requires one shared fit pair")
    else:
        raise ValueError("unknown complete fit-frame scope")
    return validated


def validate_arrival_fit_pairs(
    rows: Sequence[Mapping[str, object]],
    *,
    fit_cell_ids: Sequence[int],
    score_cell_ids: Sequence[int],
    required_split_id: str | None = None,
) -> int:
    fit_ids = tuple(fit_cell_ids)
    score_ids = tuple(score_cell_ids)
    canonical_fit_ids, canonical_score_ids = authoritative_alignment_frame_cell_ids()
    if fit_ids != canonical_fit_ids or score_ids != canonical_score_ids:
        raise ValueError("arrival fit and score frames must be the fixed disjoint 4180/1045 frames")
    validated = tuple(validate_fit_execution_row(row) for row in rows)
    grouped: dict[tuple[str, int], list[str]] = {}
    split_ids: set[str] = set()
    for row in validated:
        if row.get("scenario_id") != "permuted_arrival_alignment_stress":
            raise ValueError("arrival pair contains another scenario")
        split_id = cast(str, row["split_id"])
        if split_id == "calibration":
            raise ValueError("arrival scenario has no calibration split")
        split_ids.add(split_id)
        key = (cast(str, row["split_id"]), cast(int, row["fit_index"]))
        grouped.setdefault(key, []).append(cast(str, row["fit_variant"]))
    if any(len(variants) != len(set(variants)) for variants in grouped.values()):
        raise ValueError("duplicate arrival fit row")
    if (
        len(split_ids) != 1
        or not grouped
        or any(
            set(variants) != {"correct_alignment", "permuted_alignment"}
            for variants in grouped.values()
        )
    ):
        raise ValueError("arrival fit pair is incomplete")
    split_id = next(iter(split_ids))
    if required_split_id is not None and split_id != required_split_id:
        raise ValueError(f"arrival fit pair frame must use {required_split_id} only")
    expected_count = _split_replicate_count("permuted_arrival_alignment_stress", split_id)
    if set(grouped) != {(split_id, index) for index in range(expected_count)}:
        raise ValueError("arrival fit pair frame is incomplete")
    return len(grouped)


def validate_primary_fit_variant(table: str, scenario_id: str, fit_variant: str) -> None:
    if table not in FIT_DERIVED_PRIMARY_KEYS:
        raise ValueError("unknown fit-derived table")
    registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
    if fit_variant != registry.primary_fit_variant:
        raise ValueError("comparator fit variant cannot enter a primary science table")


def recompute_equal_emission_bootstrap(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validated = tuple(validate_fit_execution_row(row) for row in rows)
    observed_rows = tuple(row for row in validated if row["fit_scope"] == "scenario_shared")
    if len(observed_rows) != 2 or {cast(str, row["fit_variant"]) for row in observed_rows} != {
        "equal_rate",
        "ordered_emission",
    }:
        raise ValueError("one complete observed shared fit pair is required")
    if any(row["fit_succeeded"] is not True for row in observed_rows):
        raise ValueError("observed shared fits must both succeed")
    if any(
        row["split_id"] != "holdout"
        or row["source_replicate_first"] != 0
        or row["source_replicate_last"] != 23
        or row["source_replicate_count"] != 24
        for row in observed_rows
    ):
        raise ValueError("observed shared fit pair must use the same complete holdout split")
    observed_by_variant = {cast(str, row["fit_variant"]): row for row in observed_rows}
    observed_statistic = 2.0 * (
        float(cast(float, observed_by_variant["ordered_emission"]["log_likelihood"]))
        - float(cast(float, observed_by_variant["equal_rate"]["log_likelihood"]))
    )
    pairs: dict[int, dict[str, Mapping[str, object]]] = {}
    for row in validated:
        if row.get("fit_scope") != "bootstrap_shared":
            continue
        if (
            row["split_id"] != "holdout"
            or row["source_replicate_first"] != 0
            or row["source_replicate_last"] != 23
            or row["source_replicate_count"] != 24
        ):
            raise ValueError("bootstrap pairs must reconstruct the same complete holdout source")
        index = cast(int, row["fit_index"])
        variant = cast(str, row["fit_variant"])
        if variant in pairs.setdefault(index, {}):
            raise ValueError("duplicate equal-emission bootstrap row")
        pairs[index][variant] = row
    if tuple(sorted(pairs)) != tuple(range(199)) or any(
        set(pair) != {"equal_rate", "ordered_emission"} for pair in pairs.values()
    ):
        raise ValueError("exactly 199 complete bootstrap pairs are required")
    if any(row["fit_succeeded"] is not True for pair in pairs.values() for row in pair.values()):
        raise ValueError("all equal-emission bootstrap fits must succeed")
    statistics = tuple(
        2.0
        * (
            float(cast(float, pair["ordered_emission"]["log_likelihood"]))
            - float(cast(float, pair["equal_rate"]["log_likelihood"]))
        )
        for _, pair in sorted(pairs.items())
    )
    p_value = (1 + sum(value >= observed_statistic for value in statistics)) / 200.0
    return {
        "bootstrap_replicates": 199,
        "observed_statistic": observed_statistic,
        "statistics": statistics,
        "p_value": p_value,
    }


def validate_primary_science_foreign_keys(
    table: str,
    science_rows: Sequence[Mapping[str, object]],
    fit_rows: Sequence[Mapping[str, object]],
    *,
    source_rows: Sequence[Mapping[str, object]] | None = None,
) -> None:
    if table not in FIT_DERIVED_PRIMARY_KEYS:
        raise ValueError("unknown primary science table")
    validated_fits, _designs = _partition_fit_execution_evidence(fit_rows)
    fit_lookup: dict[tuple[object, object, object, object], dict[str, object]] = {}
    shared_fit_lookup: dict[tuple[object, object, object], dict[str, object]] = {}
    for fit in validated_fits:
        if fit["fit_scope"] == "scenario_shared":
            shared_key = (fit["scenario_id"], fit["split_id"], fit["fit_variant"])
            if shared_key in shared_fit_lookup:
                raise ValueError("primary science foreign key resolves to duplicate shared fits")
            shared_fit_lookup[shared_key] = fit
            continue
        if fit["fit_scope"] != "replicate":
            continue
        key = (fit["scenario_id"], fit["split_id"], fit["fit_index"], fit["fit_variant"])
        if key in fit_lookup:
            raise ValueError("primary science foreign key resolves to duplicate fit rows")
        fit_lookup[key] = fit

    def matching_fit(row: Mapping[str, object]) -> dict[str, object]:
        scenario_id = cast(str, row["scenario_id"])
        validate_primary_fit_variant(table, scenario_id, cast(str, row["fit_variant"]))
        if scenario_id == "no_emission_contrast_negative_control":
            if table != "predictive_replicate_diagnostics.csv":
                raise ValueError("equal emission has no fit-derived primary science rows")
            shared_key = (row["scenario_id"], row["split_id"], row["fit_variant"])
            if shared_key not in shared_fit_lookup:
                raise ValueError("equal predictive row does not resolve to one shared fit")
            return shared_fit_lookup[shared_key]
        key = (
            row["scenario_id"],
            row["split_id"],
            row.get("replicate_id"),
            row["fit_variant"],
        )
        if key not in fit_lookup:
            raise ValueError("primary science foreign key must resolve to exactly one fit row")
        return fit_lookup[key]

    if table == "replicate_recovery.csv":
        validated_rows = validate_replicate_recovery_rows(science_rows)
        estimate_fields = {
            "alpha": "alpha_estimate",
            "beta_driver": "beta_driver_estimate",
            "beta_quality": "beta_quality_estimate",
            "lambda_quasi": "lambda_quasi_estimate",
            "lambda_present": "lambda_present_estimate",
        }
        for row in validated_rows:
            fit = matching_fit(row)
            parameter_id = cast(str, row["parameter_id"])
            if parameter_id not in FIT_PARAMETER_IDS.get(
                cast(str, row["scenario_id"]), ORDERED_PARAMETER_IDS
            ):
                raise ValueError("science row parameter is not fitted by its scenario")
            expected_estimate = fit[estimate_fields[parameter_id]]
            if (
                row["converged"] is not fit["fit_succeeded"]
                or row["converged_start_count"] != fit["converged_start_count"]
                or row["at_boundary"] != fit["at_boundary"]
                or row["estimate"] != expected_estimate
                or row["log_likelihood"] != fit["log_likelihood"]
            ):
                raise ValueError("recovery row does not reconcile to complete fit evidence")
        return

    if table == "latent_time_calibration.csv":
        latent_groups: dict[tuple[object, ...], list[Mapping[str, object]]] = {}
        for latent_row in science_rows:
            latent_key = tuple(
                latent_row.get(name)
                for name in ("scenario_id", "split_id", "replicate_id", "fit_variant")
            )
            latent_groups.setdefault(latent_key, []).append(latent_row)
        for latent_group in latent_groups.values():
            validate_latent_diagnostic_rows(latent_group)
            latent_fit = matching_fit(latent_group[0])
            if any(
                latent_row["fit_succeeded"] is not latent_fit["fit_succeeded"]
                for latent_row in latent_group
            ):
                raise ValueError("latent fit status does not reconcile to fit evidence")
        if sum(len(group) for group in latent_groups.values()) != len(science_rows):
            raise ValueError("latent science rows are incomplete")
        return

    if table == "predictive_replicate_diagnostics.csv":
        predictive_groups: dict[tuple[object, ...], list[Mapping[str, object]]] = {}
        for predictive_row in science_rows:
            predictive_key = tuple(
                predictive_row.get(name)
                for name in ("scenario_id", "split_id", "replicate_id", "fit_variant")
            )
            predictive_groups.setdefault(predictive_key, []).append(predictive_row)
        for predictive_group in predictive_groups.values():
            validate_predictive_replicate_rows(predictive_group)
            predictive_fit = matching_fit(predictive_group[0])
            if any(
                predictive_row["fit_succeeded"] is not predictive_fit["fit_succeeded"]
                for predictive_row in predictive_group
            ):
                raise ValueError("predictive fit status does not reconcile to fit evidence")
        return

    if table == "identifiability_profiles.csv":
        validate_identifiability_profile_rows(science_rows, fit_rows=validated_fits)
        return

    if source_rows is None:
        raise ValueError("summary science reconciliation requires complete source rows")
    if table == "coverage_calibration.csv":
        validate_coverage_summary_rows(
            science_rows,
            recovery_rows=source_rows,
            fit_rows=validated_fits,
        )
        return
    validate_predictive_summary_rows(
        science_rows,
        predictive_rows=source_rows,
        fit_rows=validated_fits,
    )


def _split_replicate_count(scenario_id: str, split_id: str) -> int:
    if scenario_id not in SCENARIO_IDS:
        raise ValueError("unknown scenario_id")
    if split_id == "development":
        return 12
    if split_id == "calibration":
        if scenario_id not in NESTED_SCENARIOS:
            raise ValueError("nonnested scenario has no calibration split")
        return 24
    if split_id == "holdout":
        return 48 if scenario_id in NESTED_SCENARIOS else 24
    raise ValueError("unknown split_id")


def scenario_split_ids(scenario_id: str) -> tuple[str, ...]:
    if scenario_id not in SCENARIO_IDS:
        raise ValueError("unknown scenario_id")
    return (
        ("development", "calibration", "holdout")
        if scenario_id in NESTED_SCENARIOS
        else ("development", "holdout")
    )


def science_identity_frames() -> dict[str, tuple[tuple[object, ...], ...]]:
    fit: list[tuple[object, ...]] = []
    recovery: list[tuple[object, ...]] = []
    coverage: list[tuple[object, ...]] = []
    latent: list[tuple[object, ...]] = []
    predictive: list[tuple[object, ...]] = []
    for scenario_id in SCENARIO_IDS:
        registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
        for split_id in scenario_split_ids(scenario_id):
            count = _split_replicate_count(scenario_id, split_id)
            if registry.fit_scope == "scenario_shared":
                for variant in ("equal_rate", "ordered_emission"):
                    fit.append((scenario_id, split_id, "scenario_shared", variant, 0))
                if split_id == "holdout":
                    for fit_index in range(199):
                        for variant in ("equal_rate", "ordered_emission"):
                            fit.append(
                                (
                                    scenario_id,
                                    split_id,
                                    "bootstrap_shared",
                                    variant,
                                    fit_index,
                                )
                            )
            else:
                variants = tuple(
                    variant
                    for variant in (registry.primary_fit_variant, registry.comparator_fit_variant)
                    if variant is not None
                )
                for replicate_id in range(count):
                    for variant in variants:
                        fit.append((scenario_id, split_id, "replicate", variant, replicate_id))
                    for parameter_id in FIT_PARAMETER_IDS.get(scenario_id, ORDERED_PARAMETER_IDS):
                        recovery.append(
                            (
                                scenario_id,
                                split_id,
                                replicate_id,
                                registry.primary_fit_variant,
                                parameter_id,
                            )
                        )
                    latent.append(
                        (scenario_id, split_id, replicate_id, registry.primary_fit_variant)
                    )
                for parameter_id in FIT_PARAMETER_IDS.get(scenario_id, ORDERED_PARAMETER_IDS):
                    coverage.append(
                        (scenario_id, split_id, registry.primary_fit_variant, parameter_id)
                    )
            if scenario_id != "process_oracle_observed_transition":
                for replicate_id in range(count):
                    predictive.append(
                        (scenario_id, split_id, replicate_id, registry.primary_fit_variant)
                    )
    return {
        "fit": tuple(sorted(fit)),
        "recovery": tuple(sorted(recovery)),
        "coverage": tuple(sorted(coverage)),
        "latent": tuple(sorted(latent)),
        "predictive": tuple(sorted(predictive)),
        "predictive_summary": tuple(
            sorted({(scenario, split, variant) for scenario, split, _, variant in predictive})
        ),
    }


@lru_cache(maxsize=1)
def authoritative_source_design_cells() -> tuple[DesignCell, ...]:
    from spatext.synth.medium.spread_impact import build_synth_medium_spread_impact_review_pack

    spread = build_synth_medium_spread_impact_review_pack()
    passable_rows = tuple(
        sorted(
            (row for row in spread.cell_truth_rows if row.landscape_cell.passability != "water"),
            key=lambda row: row.landscape_cell.cell_id,
        )
    )
    quality = np.asarray([row.landscape_cell.quality for row in passable_rows], dtype=np.float64)
    standardized = (quality - quality.mean()) / quality.std(ddof=0)
    cells = tuple(
        DesignCell(
            cell_id=row.landscape_cell.cell_id,
            standardized_quality=float(standardized[index]),
            predator_arrival_time=row.predator_arrival_time,
            row_band=row.landscape_cell.row_band,
        )
        for index, row in enumerate(passable_rows)
    )
    if len(cells) != 5225:
        raise ValueError("source design-cell authority is not the exact 5,225-cell frame")
    return cells


@lru_cache(maxsize=1)
def authoritative_passable_cell_ids() -> tuple[int, ...]:
    from spatext.synth.medium.landscape import build_synth_medium_landscape

    landscape = build_synth_medium_landscape()
    cell_ids = tuple(
        sorted(cell.cell_id for cell in landscape.cells if cell.passability != "water")
    )
    if len(cell_ids) != 5225 or len(set(cell_ids)) != 5225:
        raise ValueError("Goal 017 passable-cell authority is not the exact 5,225-cell frame")
    return cell_ids


@lru_cache(maxsize=1)
def authoritative_sparse_cell_ids() -> tuple[int, ...]:
    ranked = sorted(
        authoritative_passable_cell_ids(),
        key=lambda cell_id: (
            sha256(f"023|sparse_expected_failure|cell_id={cell_id}".encode("ascii")).digest(),
            cell_id,
        ),
    )
    return tuple(sorted(ranked[:1306]))


@lru_cache(maxsize=1)
def authoritative_alignment_frame_cell_ids() -> tuple[tuple[int, ...], tuple[int, ...]]:
    passable = authoritative_passable_cell_ids()
    ranked = sorted(
        passable,
        key=lambda cell_id: (
            sha256(f"023|alignment_score|cell_id={cell_id}".encode("ascii")).digest(),
            cell_id,
        ),
    )
    score_set = frozenset(ranked[:1045])
    score_ids = tuple(cell_id for cell_id in passable if cell_id in score_set)
    fit_ids = tuple(cell_id for cell_id in passable if cell_id not in score_set)
    if len(fit_ids) != 4180 or len(score_ids) != 1045:
        raise ValueError("alignment authority is not the exact 4,180/1,045 frame")
    return fit_ids, score_ids


@cache
def authoritative_fit_cell_ids(scenario_id: str) -> tuple[int, ...]:
    """Return the exact registered analyst fit-cell IDs for one scenario."""

    if scenario_id == "permuted_arrival_alignment_stress":
        return authoritative_alignment_frame_cell_ids()[0]
    if scenario_id == "sparse_expected_failure":
        return authoritative_sparse_cell_ids()
    if scenario_id in SCENARIO_IDS:
        return authoritative_passable_cell_ids()
    raise ValueError("analyst fit frame requires a registered scenario")


def cell_identity_sha256(cell_ids: Sequence[int]) -> str:
    canonical = tuple(cell_ids)
    if not canonical or any(type(cell_id) is not int for cell_id in canonical):
        raise ValueError("cell identity digest requires nonempty builtin integer IDs")
    if tuple(sorted(canonical)) != canonical or len(set(canonical)) != len(canonical):
        raise ValueError("cell identity digest requires unique sorted IDs")
    payload = "".join(f"cell_id={cell_id}\n" for cell_id in canonical).encode("ascii")
    return sha256(payload).hexdigest()


@cache
def issue_analyst_fit_frame(scenario_id: str) -> AnalystFitFrame:
    """Issue a typed fit frame from the scenario's exact canonical IDs."""

    cell_ids = authoritative_fit_cell_ids(scenario_id)
    frame = object.__new__(AnalystFitFrame)
    object.__setattr__(frame, "scenario_id", scenario_id)
    object.__setattr__(frame, "frame_role", "analyst_fit")
    object.__setattr__(frame, "cell_ids", cell_ids)
    object.__setattr__(frame, "cell_count", len(cell_ids))
    object.__setattr__(frame, "cell_sha256", cell_identity_sha256(cell_ids))
    object.__setattr__(frame, "_issuer", _ANALYST_FIT_FRAME_ISSUER)
    _validate_analyst_fit_frame(frame)
    return frame


def _validate_analyst_fit_frame(frame: AnalystFitFrame) -> None:
    if type(frame) is not AnalystFitFrame or frame._issuer is not _ANALYST_FIT_FRAME_ISSUER:
        raise TypeError("fit frame must be an exact module-issued AnalystFitFrame")
    expected_ids = authoritative_fit_cell_ids(frame.scenario_id)
    if (
        frame.frame_role != "analyst_fit"
        or type(frame.cell_ids) is not tuple
        or frame.cell_ids != expected_ids
        or type(frame.cell_count) is not int
        or frame.cell_count != len(expected_ids)
        or type(frame.cell_sha256) is not str
        or frame.cell_sha256 != cell_identity_sha256(expected_ids)
    ):
        raise ValueError("analyst fit frame does not match canonical scenario authority")


def _require_analyst_fit_frame_alignment(
    histories: tuple[AnalystHistory, ...],
    frame: AnalystFitFrame,
) -> None:
    _validate_analyst_fit_frame(frame)
    history_ids = tuple(history.cell_id for history in histories)
    if history_ids != frame.cell_ids:
        raise ValueError("analyst histories do not match the issued canonical fit frame")


def joint_fit_design_frame_identity(result: JointFitResult) -> tuple[int, str]:
    """Return persisted frame fields only from a validated issued fit result."""

    if type(result) is not JointFitResult:
        raise TypeError("design frame identity requires an exact JointFitResult")
    result.__post_init__()
    return result.fit_frame_cell_count, result.fit_frame_sha256


def persisted_design_frame_identity(
    scenario_id: str,
    fit_variant: str,
    *,
    joint_fit_result: JointFitResult | None,
) -> tuple[int, str]:
    """Resolve persisted design identity from typed execution authority."""

    required = required_design_kinds(scenario_id, fit_variant)
    if "plugin" in required:
        if type(joint_fit_result) is not JointFitResult:
            raise TypeError("joint design persistence requires its exact JointFitResult")
        if joint_fit_result.fit_frame.scenario_id != scenario_id:
            raise ValueError("joint result frame belongs to a different scenario")
        return joint_fit_design_frame_identity(joint_fit_result)
    if joint_fit_result is not None:
        raise ValueError("non-joint design persistence cannot accept a joint result")
    frame = issue_analyst_fit_frame(scenario_id)
    return frame.cell_count, frame.cell_sha256


@cache
def authoritative_design_frame_identity(scenario_id: str) -> tuple[int, str]:
    cell_ids = authoritative_fit_cell_ids(scenario_id)
    return len(cell_ids), cell_identity_sha256(cell_ids)


def _predictive_time_band(time: int) -> str:
    if 0 <= time <= 36:
        return "early"
    if 42 <= time <= 78:
        return "middle"
    if 84 <= time <= 120:
        return "late"
    raise ValueError("predictive opportunity time is outside the frozen bands")


@cache
def _predictive_opportunity_records(
    scenario_id: str,
) -> tuple[tuple[int, int, float, str, str], ...]:
    if scenario_id not in SCENARIO_IDS or scenario_id == "process_oracle_observed_transition":
        raise ValueError("predictive opportunity records require an applicable scenario")
    cells = authoritative_source_design_cells()
    quintiles = quality_quintile_labels(cells)
    quintile_by_id = {
        cell.cell_id: quintile for cell, quintile in zip(cells, quintiles, strict=True)
    }
    if scenario_id == "permuted_arrival_alignment_stress":
        selected_ids = frozenset(authoritative_alignment_frame_cell_ids()[1])
    elif scenario_id == "sparse_expected_failure":
        selected_ids = frozenset(authoritative_sparse_cell_ids())
    else:
        selected_ids = frozenset(authoritative_passable_cell_ids())
    schedule = build_canonical_schedule(cells, scenario_id)
    return tuple(
        (
            opportunity.cell_id,
            opportunity.time,
            opportunity.effort,
            quintile_by_id[opportunity.cell_id],
            _predictive_time_band(opportunity.time),
        )
        for opportunity in schedule
        if opportunity.cell_id in selected_ids
    )


def _predictive_stratum_counts(
    records: Sequence[CanonicalPredictiveOpportunity],
) -> tuple[int, ...]:
    counts: dict[tuple[str, str], int] = {stratum: 0 for stratum in PREDICTIVE_STRATA}
    for record in records:
        if not record.kept:
            continue
        counts[("all", "all")] += 1
        counts[("habitat_quality_quintile", record.quality_stratum)] += 1
        counts[("time_band", record.time_band)] += 1
    return tuple(counts[stratum] for stratum in PREDICTIVE_STRATA)


def canonical_predictive_opportunity_serialization(
    *,
    scenario_id: str,
    split_id: str,
    replicate_id: int,
    frame_role: str,
    opportunities: tuple[CanonicalPredictiveOpportunity, ...],
) -> bytes:
    """Serialize every predictive semantic field in exact canonical order."""

    if type(opportunities) is not tuple or not opportunities:
        raise ValueError("predictive serialization requires a nonempty opportunity tuple")
    previous_key = (-1, -1)
    payload = bytearray(
        _predictive_serialization_header(scenario_id, split_id, replicate_id, frame_role)
    )
    for opportunity in opportunities:
        if type(opportunity) is not CanonicalPredictiveOpportunity:
            raise TypeError(
                "predictive serialization requires exact CanonicalPredictiveOpportunity values"
            )
        opportunity.__post_init__()
        key = (opportunity.cell_id, opportunity.time)
        if key <= previous_key:
            raise ValueError("predictive opportunities must be in unique canonical order")
        previous_key = key
        payload.extend(_canonical_predictive_opportunity_line(opportunity))
    return bytes(payload)


def canonical_predictive_opportunity_sha256(
    *,
    scenario_id: str,
    split_id: str,
    replicate_id: int,
    frame_role: str,
    opportunities: tuple[CanonicalPredictiveOpportunity, ...],
) -> str:
    return sha256(
        canonical_predictive_opportunity_serialization(
            scenario_id=scenario_id,
            split_id=split_id,
            replicate_id=replicate_id,
            frame_role=frame_role,
            opportunities=opportunities,
        )
    ).hexdigest()


def _predictive_dropout_mask_sha256(
    opportunities: tuple[CanonicalPredictiveOpportunity, ...],
) -> str:
    payload = "".join(
        f"keep_key={opportunity.keep_key}|kept={int(opportunity.kept)}\n"
        for opportunity in opportunities
    ).encode("ascii")
    return sha256(payload).hexdigest()


_PREDICTIVE_FRAME_REGISTRY: dict[tuple[str, str, int, str], PredictiveOpportunityFrameEvidence] = {}
_VALIDATED_PREDICTIVE_FRAME_IDS: set[int] = set()


@cache
def _fully_retained_predictive_opportunities(
    scenario_id: str,
) -> tuple[CanonicalPredictiveOpportunity, ...]:
    return tuple(
        CanonicalPredictiveOpportunity(
            cell_id=cell_id,
            time=time,
            effort=effort,
            quality_stratum=quality_stratum,
            time_band=time_band,
            keep_key=f"cell_id={cell_id}|time={time}",
            kept=True,
        )
        for cell_id, time, effort, quality_stratum, time_band in (
            _predictive_opportunity_records(scenario_id)
        )
    )


@cache
def _fully_retained_predictive_counts(scenario_id: str) -> tuple[int, ...]:
    return _predictive_stratum_counts(_fully_retained_predictive_opportunities(scenario_id))


def _canonical_predictive_opportunity_line(
    opportunity: CanonicalPredictiveOpportunity,
) -> bytes:
    return (
        "|".join(
            (
                f"cell_id={opportunity.cell_id}",
                f"time={opportunity.time}",
                f"effort_hex={opportunity.effort.hex()}",
                f"quality_stratum={opportunity.quality_stratum}",
                f"time_band={opportunity.time_band}",
                f"keep_key={opportunity.keep_key}",
                f"kept={int(opportunity.kept)}",
            )
        )
        + "\n"
    ).encode("ascii")


@cache
def _fully_retained_predictive_body(scenario_id: str) -> bytes:
    return b"".join(
        _canonical_predictive_opportunity_line(opportunity)
        for opportunity in _fully_retained_predictive_opportunities(scenario_id)
    )


def _predictive_serialization_header(
    scenario_id: str,
    split_id: str,
    replicate_id: int,
    frame_role: str,
) -> bytes:
    return (
        f"scenario_id={scenario_id}\n"
        f"split_id={split_id}\n"
        f"replicate_id={replicate_id}\n"
        f"frame_role={frame_role}\n"
    ).encode("ascii")


def _issued_predictive_frame_sha256(
    *,
    scenario_id: str,
    split_id: str,
    replicate_id: int,
    frame_role: str,
    opportunities: tuple[CanonicalPredictiveOpportunity, ...],
) -> str:
    hasher = sha256(
        _predictive_serialization_header(scenario_id, split_id, replicate_id, frame_role)
    )
    if opportunities is _fully_retained_predictive_opportunities(scenario_id):
        hasher.update(_fully_retained_predictive_body(scenario_id))
    else:
        for opportunity in opportunities:
            hasher.update(_canonical_predictive_opportunity_line(opportunity))
    return hasher.hexdigest()


def _validate_predictive_opportunity_frame(
    frame: PredictiveOpportunityFrameEvidence,
) -> None:
    if (
        type(frame) is not PredictiveOpportunityFrameEvidence
        or frame._issuer is not _PREDICTIVE_FRAME_ISSUER
    ):
        raise TypeError("predictive frame must be an exact module-issued value")
    if id(frame) in _VALIDATED_PREDICTIVE_FRAME_IDS:
        return
    if frame.scenario_id not in SCENARIO_IDS or frame.scenario_id == (
        "process_oracle_observed_transition"
    ):
        raise ValueError("predictive opportunity frame requires an applicable scenario")
    attempted = _split_replicate_count(frame.scenario_id, frame.split_id)
    if type(frame.replicate_id) is not int or not 0 <= frame.replicate_id < attempted:
        raise ValueError("predictive opportunity frame replicate is outside the frozen split")
    expected_role = "score" if frame.scenario_id == "permuted_arrival_alignment_stress" else "fit"
    if frame.frame_role != expected_role:
        raise ValueError("predictive opportunity frame uses the wrong fit/score role")
    base_records = _predictive_opportunity_records(frame.scenario_id)
    if len(frame.opportunities) != len(base_records):
        raise ValueError("predictive frame is missing or adds canonical opportunities")
    for opportunity, base in zip(frame.opportunities, base_records, strict=True):
        cell_id, time, effort, quality_stratum, time_band = base
        if (
            opportunity.cell_id,
            opportunity.time,
            opportunity.effort,
            opportunity.quality_stratum,
            opportunity.time_band,
            opportunity.keep_key,
        ) != (
            cell_id,
            time,
            effort,
            quality_stratum,
            time_band,
            f"cell_id={cell_id}|time={time}",
        ):
            raise ValueError("predictive frame differs from canonical schedule semantics")
    retained_count = sum(opportunity.kept for opportunity in frame.opportunities)
    counts = _predictive_stratum_counts(frame.opportunities)
    if (
        type(frame.opportunity_count) is not int
        or frame.opportunity_count != retained_count
        or frame.opportunity_count < 2
        or type(frame.stratum_counts) is not tuple
        or frame.stratum_counts != counts
        or any(value < 2 for value in counts)
    ):
        raise ValueError("predictive opportunity counts must derive from retained objects")
    digest = _issued_predictive_frame_sha256(
        scenario_id=frame.scenario_id,
        split_id=frame.split_id,
        replicate_id=frame.replicate_id,
        frame_role=frame.frame_role,
        opportunities=frame.opportunities,
    )
    if frame.opportunity_frame_sha256 != digest:
        raise ValueError("predictive frame digest does not match canonical serialization")
    if frame.scenario_id == "informative_dropout_misspecification_stress":
        if frame.dropout_mask_sha256 != _predictive_dropout_mask_sha256(frame.opportunities):
            raise ValueError("dropout mask digest does not match keyed keep states")
    elif frame.dropout_mask_sha256 is not None or any(
        not opportunity.kept for opportunity in frame.opportunities
    ):
        raise ValueError("non-dropout predictive frames must retain every opportunity")
    _VALIDATED_PREDICTIVE_FRAME_IDS.add(id(frame))


def _issue_predictive_opportunity_frame(
    *,
    scenario_id: str,
    split_id: str,
    replicate_id: int,
    keep_by_key: Mapping[str, bool] | None,
) -> PredictiveOpportunityFrameEvidence:
    if scenario_id not in SCENARIO_IDS or scenario_id == "process_oracle_observed_transition":
        raise ValueError("predictive opportunity frame requires an applicable scenario")
    attempted = _split_replicate_count(scenario_id, split_id)
    if type(replicate_id) is not int or not 0 <= replicate_id < attempted:
        raise ValueError("predictive opportunity frame replicate is outside the frozen split")
    records = _predictive_opportunity_records(scenario_id)
    keys = tuple(f"cell_id={cell_id}|time={time}" for cell_id, time, *_rest in records)
    if scenario_id == "informative_dropout_misspecification_stress":
        if (
            type(keep_by_key) is not dict
            or set(keep_by_key) != set(keys)
            or any(
                type(key) is not str or type(value) is not bool
                for key, value in keep_by_key.items()
            )
        ):
            raise ValueError("dropout adapter requires one exact keyed bool state per opportunity")
    elif keep_by_key is not None:
        raise ValueError("non-dropout predictive adapter cannot accept a dropout mask")
    opportunities = (
        _fully_retained_predictive_opportunities(scenario_id)
        if keep_by_key is None
        else tuple(
            CanonicalPredictiveOpportunity(
                cell_id=cell_id,
                time=time,
                effort=effort,
                quality_stratum=quality_stratum,
                time_band=time_band,
                keep_key=key,
                kept=keep_by_key[key],
            )
            for (cell_id, time, effort, quality_stratum, time_band), key in zip(
                records, keys, strict=True
            )
        )
    )
    frame_role = "score" if scenario_id == "permuted_arrival_alignment_stress" else "fit"
    frame = object.__new__(PredictiveOpportunityFrameEvidence)
    object.__setattr__(frame, "scenario_id", scenario_id)
    object.__setattr__(frame, "split_id", split_id)
    object.__setattr__(frame, "replicate_id", replicate_id)
    object.__setattr__(frame, "frame_role", frame_role)
    object.__setattr__(frame, "opportunities", opportunities)
    opportunity_count = (
        len(opportunities) if keep_by_key is None else sum(row.kept for row in opportunities)
    )
    stratum_counts = (
        _fully_retained_predictive_counts(scenario_id)
        if keep_by_key is None
        else _predictive_stratum_counts(opportunities)
    )
    if opportunity_count < 2 or any(value < 2 for value in stratum_counts):
        raise ValueError("predictive opportunity strata require at least two retained rows")
    object.__setattr__(frame, "opportunity_count", opportunity_count)
    object.__setattr__(frame, "stratum_counts", stratum_counts)
    object.__setattr__(
        frame,
        "opportunity_frame_sha256",
        _issued_predictive_frame_sha256(
            scenario_id=scenario_id,
            split_id=split_id,
            replicate_id=replicate_id,
            frame_role=frame_role,
            opportunities=opportunities,
        ),
    )
    object.__setattr__(
        frame,
        "dropout_mask_sha256",
        _predictive_dropout_mask_sha256(opportunities)
        if scenario_id == "informative_dropout_misspecification_stress"
        else None,
    )
    object.__setattr__(frame, "_issuer", _PREDICTIVE_FRAME_ISSUER)
    _VALIDATED_PREDICTIVE_FRAME_IDS.add(id(frame))
    _PREDICTIVE_FRAME_REGISTRY[
        (scenario_id, split_id, replicate_id, frame.opportunity_frame_sha256)
    ] = frame
    return frame


def predictive_opportunity_frame_from_schedule(
    *,
    scenario_id: str,
    split_id: str,
    replicate_id: int,
    schedule: tuple[ScheduledOpportunity, ...],
    keep_by_key: Mapping[str, bool] | None = None,
) -> PredictiveOpportunityFrameEvidence:
    """Adapt one realized production schedule into the canonical metric frame."""

    canonical_schedule = _canonical_schedule(schedule)
    expected_schedule = build_canonical_schedule(authoritative_source_design_cells(), scenario_id)
    if canonical_schedule != expected_schedule:
        raise ValueError("predictive schedule differs in size, identity, effort, or covariates")
    _split_replicate_count(scenario_id, split_id)
    if type(replicate_id) is not int or not 0 <= replicate_id < _split_replicate_count(
        scenario_id, split_id
    ):
        raise ValueError("predictive replicate is outside the frozen split frame")
    return _issue_predictive_opportunity_frame(
        scenario_id=scenario_id,
        split_id=split_id,
        replicate_id=replicate_id,
        keep_by_key=keep_by_key,
    )


def predictive_metrics_from_opportunity_frame(
    frame: PredictiveOpportunityFrameEvidence,
    observed_counts_by_key: Mapping[str, int],
) -> tuple[dict[str, object], ...]:
    """Calculate all 27 metrics from the retained objects authenticated by frame."""

    _validate_predictive_opportunity_frame(frame)
    retained = tuple(row for row in frame.opportunities if row.kept)
    retained_keys = {row.keep_key for row in retained}
    if type(observed_counts_by_key) is not dict or set(observed_counts_by_key) != retained_keys:
        raise ValueError("predictive counts must key exactly the retained opportunity objects")
    if any(
        type(key) is not str or type(value) is not int or value < 0
        for key, value in observed_counts_by_key.items()
    ):
        raise ValueError("predictive observed counts must be keyed nonnegative integers")
    rows: list[dict[str, object]] = []
    for stratum_type, stratum_value in PREDICTIVE_STRATA:
        selected = tuple(
            opportunity
            for opportunity in retained
            if stratum_type == "all"
            or (
                stratum_type == "habitat_quality_quintile"
                and opportunity.quality_stratum == stratum_value
            )
            or (stratum_type == "time_band" and opportunity.time_band == stratum_value)
        )
        values = np.asarray(
            [observed_counts_by_key[row.keep_key] for row in selected], dtype=np.float64
        )
        if len(values) < 2:
            raise ValueError("predictive metric strata require at least two opportunities")
        mean_count = float(values.mean(dtype=np.float64))
        metrics = {
            "mean_count": mean_count,
            "zero_fraction": float(np.count_nonzero(values == 0.0) / len(values)),
            "variance_to_mean": (
                0.0
                if mean_count == 0.0
                else float(values.var(ddof=1, dtype=np.float64) / mean_count)
            ),
        }
        for metric_id in PREDICTIVE_METRICS:
            rows.append(
                {
                    "stratum_type": stratum_type,
                    "stratum_value": stratum_value,
                    "metric_id": metric_id,
                    "sample_size": len(values),
                    "observed_value": metrics[metric_id],
                    "opportunity_frame_count": frame.opportunity_count,
                    "opportunity_frame_sha256": frame.opportunity_frame_sha256,
                    "dropout_mask_sha256": frame.dropout_mask_sha256,
                }
            )
    return tuple(rows)


@cache
def deterministic_predictive_opportunity_frame(
    scenario_id: str,
    split_id: str,
    replicate_id: int,
) -> PredictiveOpportunityFrameEvidence:
    """Issue fixture-only evidence without constructing a production RNG or payload."""

    records = _predictive_opportunity_records(scenario_id)
    keep_by_key: dict[str, bool] | None = None
    if scenario_id == "informative_dropout_misspecification_stress":
        keep_by_key = {}
        for cell_id, time, _effort, _quintile, _time_band in records:
            key = (
                f"023|fixture_dropout_mask|{split_id}|{replicate_id}|cell_id={cell_id}|time={time}"
            ).encode("ascii")
            keep = sha256(key).digest()[0] >= 64
            keep_by_key[f"cell_id={cell_id}|time={time}"] = keep
    return _issue_predictive_opportunity_frame(
        scenario_id=scenario_id,
        split_id=split_id,
        replicate_id=replicate_id,
        keep_by_key=keep_by_key,
    )


@lru_cache(maxsize=1)
def authoritative_alignment_correlation() -> float:
    cells = authoritative_source_design_cells()
    original = np.asarray([cell.predator_arrival_time for cell in cells], dtype=np.float64)
    permuted = permute_arrival_within_blocks(cells)
    correlation = float(np.corrcoef(original, permuted)[0, 1])
    if len(cells) != 5225 or not isfinite(correlation) or abs(correlation) > 0.25:
        raise ValueError("canonical alignment correlation does not satisfy frozen authority")
    return correlation


def authoritative_latent_cell_ids(scenario_id: str) -> tuple[int, ...]:
    if scenario_id not in SCENARIO_IDS:
        raise ValueError("unknown scenario_id")
    if scenario_id == "sparse_expected_failure":
        return authoritative_sparse_cell_ids()
    if scenario_id == "permuted_arrival_alignment_stress":
        return authoritative_alignment_frame_cell_ids()[1]
    registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
    if not registry.latent_time_applicable:
        return ()
    return authoritative_passable_cell_ids()


def censor_transition_index(transition_time: int | None) -> int:
    if transition_time is None:
        return 21
    if type(transition_time) is not int or transition_time not in MODEL_TIMES[1:]:
        raise ValueError("transition_time must be a six-unit event endpoint or None")
    return transition_time // 6


def _latent_quantile(probabilities: FloatArray, quantile: float) -> float:
    cumulative = np.cumsum(probabilities, dtype=np.float64)
    return float(LATENT_PATH_VALUES[int(np.flatnonzero(cumulative >= quantile)[0])])


def _ordinary_median(values: FloatArray) -> float:
    ordered = np.sort(values)
    middle = ordered.size // 2
    if ordered.size % 2:
        return float(ordered[middle])
    return float((ordered[middle - 1] + ordered[middle]) / 2.0)


def latent_quantiles(probabilities: FloatArray) -> tuple[float, float, float]:
    if not isinstance(probabilities, np.ndarray) or probabilities.dtype != np.float64:
        raise ValueError("latent probabilities must be float64")
    if probabilities.shape != (21,) or not np.isfinite(probabilities).all():
        raise ValueError("latent probabilities must contain 21 finite values")
    if (probabilities < 0).any() or abs(float(probabilities.sum()) - 1.0) > 1e-12:
        raise ValueError("latent probabilities must be normalized")
    normalized = probabilities / probabilities.sum()
    return tuple(_latent_quantile(normalized, q) for q in (0.05, 0.50, 0.95))  # type: ignore[return-value]


def ordinary_median(values: FloatArray) -> float:
    return _ordinary_median(values)


def build_process_oracle_probabilities(
    *,
    analyst_visible: Mapping[str, object],
    builder: Callable[[Mapping[str, object]], FloatArray],
) -> FloatArray:
    validate_analyst_fit_payload(analyst_visible)
    probabilities = builder(analyst_visible)
    if not isinstance(probabilities, np.ndarray) or probabilities.dtype != np.float64:
        raise ValueError("process oracle builder must return float64 path probabilities")
    return probabilities


def evaluate_latent_transition_diagnostics(
    *,
    cell_ids: Sequence[int],
    path_probabilities: FloatArray,
    truth_transition_times: Sequence[int | None],
    evaluator_cell_ids: Sequence[int] | None = None,
) -> LatentTransitionDiagnostics:
    ids = tuple(cell_ids)
    if ids != tuple(sorted(ids)) or any(type(value) is not int for value in ids):
        raise ValueError("cell_ids must be sorted exact integers")
    if len(set(ids)) != len(ids) or not ids:
        raise ValueError("cell_ids must be unique and nonempty")
    if evaluator_cell_ids is not None and tuple(evaluator_cell_ids) != ids:
        raise ValueError("analyst and evaluator cell IDs must match exactly")
    if not isinstance(path_probabilities, np.ndarray) or path_probabilities.dtype != np.float64:
        raise ValueError("path_probabilities must be a float64 ndarray")
    if path_probabilities.shape != (len(ids), 21) or len(truth_transition_times) != len(ids):
        raise ValueError("latent frames have incompatible shapes")
    if not np.isfinite(path_probabilities).all() or (path_probabilities < 0).any():
        raise ValueError("path probabilities must be finite and nonnegative")
    row_sums = cast(FloatArray, np.sum(path_probabilities, axis=1, dtype=np.float64))
    if np.any(row_sums <= 0) or np.any(np.abs(row_sums - 1.0) > 1e-12):
        raise ValueError("path probability rows must sum to one within tolerance")
    normalized = path_probabilities / row_sums[:, None]
    truth: IntArray = np.asarray(
        tuple(censor_transition_index(value) for value in truth_transition_times), dtype=np.int64
    )
    cumulative = np.cumsum(normalized[:, :20], axis=1)
    indicators = truth[:, None] <= np.arange(1, 21, dtype=np.int64)[None, :]
    observed_brier = float(np.mean((cumulative - indicators) ** 2))
    expected_brier = float(np.mean(cumulative * (1.0 - cumulative)))
    interval_observed = np.empty(len(ids), dtype=np.float64)
    interval_expected = np.empty(len(ids), dtype=np.float64)
    median_observed = np.empty(len(ids), dtype=np.float64)
    median_expected = np.empty(len(ids), dtype=np.float64)
    for index, probabilities in enumerate(normalized):
        lower = _latent_quantile(probabilities, 0.05)
        upper = _latent_quantile(probabilities, 0.95)
        median = _latent_quantile(probabilities, 0.50)

        def interval_loss(
            value: float, *, lower_bound: float = lower, upper_bound: float = upper
        ) -> float:
            return (
                0.05 * (upper_bound - lower_bound)
                + max(lower_bound - value, 0.0)
                + max(value - upper_bound, 0.0)
            )

        truth_value = float(LATENT_PATH_VALUES[truth[index] - 1])
        interval_observed[index] = interval_loss(truth_value)
        interval_expected[index] = sum(
            float(probability) * interval_loss(value)
            for probability, value in zip(probabilities, LATENT_PATH_VALUES, strict=True)
        )
        median_observed[index] = abs(truth_value - median)
        median_expected[index] = sum(
            float(probability) * abs(value - median)
            for probability, value in zip(probabilities, LATENT_PATH_VALUES, strict=True)
        )
    observed = {
        "transition_brier": observed_brier,
        "transition_interval_score": float(np.mean(interval_observed)),
        "transition_median_absolute_error": _ordinary_median(median_observed),
    }
    expected = {
        "transition_brier": expected_brier,
        "transition_interval_score": float(np.mean(interval_expected)),
        "transition_median_absolute_error": _ordinary_median(median_expected),
    }
    errors = {name: observed[name] - expected[name] for name in observed}
    return LatentTransitionDiagnostics(observed, expected, errors, len(ids))


def build_latent_diagnostic_rows(
    *,
    scenario_id: str,
    split_id: str,
    replicate_id: int,
    fit_succeeded: bool | None,
    cell_ids: Sequence[int] | None = None,
    path_probabilities: FloatArray | None = None,
    truth_transition_times: Sequence[int | None] | None = None,
    evaluator_cell_ids: Sequence[int] | None = None,
    prerequisite_valid: bool = False,
) -> tuple[dict[str, object], ...]:
    if scenario_id not in SCENARIO_IDS or split_id not in ("development", "calibration", "holdout"):
        raise ValueError("unknown latent diagnostic identity")
    if type(replicate_id) is not int or replicate_id < 0:
        raise ValueError("replicate_id must be nonnegative")
    if replicate_id >= _split_replicate_count(scenario_id, split_id):
        raise ValueError("replicate_id is outside the frozen split frame")
    registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
    if not registry.latent_time_applicable:
        status: bool | None = None
        available = False
        gate_result = "not_applicable"
        diagnostics = None
    else:
        if type(fit_succeeded) is not bool:
            raise ValueError("applicable latent diagnostic requires literal fit status")
        status = fit_succeeded
        available = False
        gate_result = "diagnostic"
        diagnostics = None
        if (
            fit_succeeded
            and prerequisite_valid
            and cell_ids is not None
            and (path_probabilities is not None and truth_transition_times is not None)
            and evaluator_cell_ids is not None
        ):
            try:
                canonical_ids = authoritative_latent_cell_ids(scenario_id)
                if (
                    len(canonical_ids) != registry.latent_time_sample_size
                    or tuple(cell_ids) != canonical_ids
                    or tuple(evaluator_cell_ids) != canonical_ids
                ):
                    raise ValueError("latent cell frame does not match frozen authority")
                diagnostics = evaluate_latent_transition_diagnostics(
                    cell_ids=cell_ids,
                    path_probabilities=path_probabilities,
                    truth_transition_times=truth_transition_times,
                    evaluator_cell_ids=evaluator_cell_ids,
                )
            except TypeError, ValueError, IndexError:
                diagnostics = None
            available = diagnostics is not None
    rows: list[dict[str, object]] = []
    for metric_id in LATENT_METRIC_IDS:
        rows.append(
            {
                "scenario_id": scenario_id,
                "split_id": split_id,
                "replicate_id": replicate_id,
                "fit_variant": registry.primary_fit_variant,
                "metric_id": metric_id,
                "sample_size": registry.latent_time_sample_size,
                "fit_succeeded": status,
                "diagnostic_available": available,
                "observed_value": diagnostics.observed_values[metric_id]
                if diagnostics is not None
                else None,
                "expected_value": diagnostics.expected_values[metric_id]
                if diagnostics is not None
                else None,
                "error": diagnostics.errors[metric_id] if diagnostics is not None else None,
                "gate_result": gate_result,
            }
        )
    return tuple(rows)


def validate_latent_diagnostic_rows(rows: Sequence[Mapping[str, object]]) -> None:
    if len(rows) != 3 or tuple(row.get("metric_id") for row in rows) != LATENT_METRIC_IDS:
        raise ValueError("latent artifact schema requires exactly three ordered metric rows")
    if any(tuple(row) != LATENT_TIME_CALIBRATION_HEADER for row in rows):
        raise ValueError("latent artifact schema has wrong columns or order")
    first = rows[0]
    identity = (
        first["scenario_id"],
        first["split_id"],
        first["replicate_id"],
        first["fit_variant"],
    )
    if any(
        (row["scenario_id"], row["split_id"], row["replicate_id"], row["fit_variant"]) != identity
        for row in rows
    ):
        raise ValueError("latent artifact schema has mixed identities")
    scenario_id, split_id, replicate_id, fit_variant = identity
    if scenario_id not in SCENARIO_IDS or split_id not in ("development", "calibration", "holdout"):
        raise ValueError("latent artifact schema has an unknown identity")
    if type(replicate_id) is not int or not 0 <= replicate_id < _split_replicate_count(
        scenario_id, split_id
    ):
        raise ValueError("latent artifact replicate is outside the frozen frame")
    registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
    if fit_variant != registry.primary_fit_variant:
        raise ValueError("latent artifact uses a non-primary fit variant")
    for row in rows:
        if type(row["sample_size"]) is not int or row["sample_size"] != (
            registry.latent_time_sample_size if registry.latent_time_applicable else 0
        ):
            raise ValueError("latent artifact sample size is inconsistent with the fixed frame")
        available = row["diagnostic_available"]
        if type(available) is not bool:
            raise ValueError("latent artifact availability must be bool")
        numeric_names = ("observed_value", "expected_value", "error")
        if not registry.latent_time_applicable:
            if (
                row["fit_succeeded"] is not None
                or available
                or row["gate_result"] != "not_applicable"
                or any(row[name] is not None for name in numeric_names)
            ):
                raise ValueError("latent inapplicable row has an invalid typed state")
            continue
        if type(row["fit_succeeded"]) is not bool or row["gate_result"] != "diagnostic":
            raise ValueError("latent applicable row has an invalid typed state")
        if available:
            if row["fit_succeeded"] is not True:
                raise ValueError("available latent diagnostic requires a successful fit")
            if any(
                type(row[name]) not in (int, float) or not isfinite(float(cast(float, row[name])))
                for name in numeric_names
            ):
                raise ValueError("available latent diagnostic requires finite values")
            observed = float(cast(float, row["observed_value"]))
            expected = float(cast(float, row["expected_value"]))
            error = float(cast(float, row["error"]))
            upper = 1.0 if row["metric_id"] == "transition_brier" else 120.0
            if not 0.0 <= observed <= upper or not 0.0 <= expected <= upper:
                raise ValueError("latent diagnostic value is outside its canonical domain")
            if abs(error - (observed - expected)) > 1e-12:
                raise ValueError("latent diagnostic error is inconsistent")
        elif any(row[name] is not None for name in numeric_names):
            raise ValueError("unavailable latent diagnostic must have null values")


def validate_no_latent_thresholds(config: Mapping[str, object]) -> None:
    forbidden = frozenset({"latent_time_thresholds", "latent_pass_count", "latent_threshold"})
    if _contains_forbidden_key(config, forbidden):
        raise ValueError("latent threshold objects and pass counts are forbidden")


def summarize_attempted_recovery(
    rows: Sequence[Mapping[str, object]],
    *,
    fit_rows: Sequence[Mapping[str, object]],
    attempted: int,
    support_width: float,
) -> dict[str, object]:
    validated = validate_replicate_recovery_rows(rows)
    if not validated:
        raise ValueError("missing recovery row is a contract failure")
    identity = tuple(
        validated[0][name] for name in ("scenario_id", "split_id", "fit_variant", "parameter_id")
    )
    if any(
        tuple(row[name] for name in ("scenario_id", "split_id", "fit_variant", "parameter_id"))
        != identity
        for row in validated
    ):
        raise ValueError("recovery summary requires one complete scenario/split/parameter frame")
    scenario_id, split_id, _, parameter_id = identity
    expected_attempted = _split_replicate_count(cast(str, scenario_id), cast(str, split_id))
    lower_support, upper_support = _FIT_PARAMETER_SUPPORTS[cast(str, parameter_id)]
    expected_support_width = upper_support - lower_support
    if (
        type(attempted) is not int
        or attempted != expected_attempted
        or not _same_number(support_width, expected_support_width)
    ):
        raise ValueError("recovery summary split count or natural support width is not literal")
    validate_primary_science_foreign_keys("replicate_recovery.csv", validated, fit_rows)
    ids = tuple(cast(int, row["replicate_id"]) for row in validated)
    if (
        len(validated) != attempted
        or tuple(sorted(ids)) != tuple(range(attempted))
        or len(set(ids)) != attempted
    ):
        raise ValueError("missing recovery row is a contract failure")
    converged_rows = tuple(row for row in validated if row["converged"] is True)
    widths = np.asarray(
        [
            float(cast(float, row["interval_width"]))
            if row["converged"] is True
            and row["profile_two_sided"] is True
            and row["interval_width"] is not None
            else support_width
            for row in validated
        ],
        dtype=np.float64,
    )
    truth_free = cast(str, scenario_id) == "goal018_continuous_abundance_stress"
    errors = (
        np.asarray([], dtype=np.float64)
        if truth_free
        else np.asarray(
            [
                float(cast(float, row["absolute_error"]))
                if row["converged"] is True and row["absolute_error"] is not None
                else support_width
                for row in validated
            ],
            dtype=np.float64,
        )
    )
    signed = np.asarray(
        [
            float(cast(float, row["signed_error"]))
            for row in converged_rows
            if row["signed_error"] is not None
        ],
        dtype=np.float64,
    )
    if (
        not np.isfinite(widths).all()
        or (widths < 0.0).any()
        or (errors.size and (not np.isfinite(errors).all() or (errors < 0.0).any()))
        or (signed.size and not np.isfinite(signed).all())
    ):
        raise ValueError("recovery summaries require finite nonnegative widths and errors")
    covered = sum(
        row["converged"] is True
        and row["profile_two_sided"] is True
        and row["truth_in_interval"] is True
        for row in validated
    )
    return {
        "replicate_count": attempted,
        "converged_count": len(converged_rows),
        "coverage_count": covered,
        "median_signed_error": _ordinary_median(signed) if signed.size else None,
        "median_absolute_error": _ordinary_median(errors) if errors.size else None,
        "maximum_absolute_error": float(errors.max()) if errors.size else None,
        "median_interval_width": _ordinary_median(widths),
        "maximum_interval_width": float(widths.max()),
    }


def nested_gate(*, coverage_count: int, converged_count: int, minimum_converged: int) -> bool:
    return 36 <= coverage_count <= 48 and converged_count >= minimum_converged


def sparse_honesty(
    *,
    coverage_count: int,
    sparse_width: float,
    structured_width: float,
    predictive_pass: bool,
    descriptive_error: float | None = None,
) -> bool:
    del descriptive_error
    return predictive_pass and 18 <= coverage_count <= 24 and sparse_width >= structured_width


def interval_excludes_zero(lower: float, upper: float) -> bool:
    return lower > 0.0 or upper < 0.0


def zero_driver_decision(
    intervals: Sequence[tuple[float | None, float | None] | None],
) -> str:
    if len(intervals) != 24:
        return "contract_failure:zero_driver_unavailable"
    decidable: list[tuple[float, float]] = []
    for interval in intervals:
        if interval is None or interval[0] is None or interval[1] is None:
            return "contract_failure:zero_driver_unavailable"
        lower, upper = float(interval[0]), float(interval[1])
        if not isfinite(lower) or not isfinite(upper) or lower > upper:
            return "contract_failure:zero_driver_unavailable"
        decidable.append((lower, upper))
    exclusions = sum(interval_excludes_zero(lower, upper) for lower, upper in decidable)
    return "pass" if exclusions <= 6 else "confounding:zero_driver_false_signal"


def summarize_stress_recovery(
    rows: Sequence[Mapping[str, object]],
    *,
    fit_rows: Sequence[Mapping[str, object]],
    support_width: float,
) -> dict[str, object]:
    summary = summarize_attempted_recovery(
        rows,
        fit_rows=fit_rows,
        attempted=24,
        support_width=support_width,
    )
    return summary | {
        "attempted_replicates": 24,
        "acceptance_lower_count": None,
        "acceptance_upper_count": None,
        "gate_result": "diagnostic" if summary["converged_count"] == 24 else "warning",
    }


def continuous_abundance_recovery_row(
    *, estimate: float | None, interval: tuple[float, float] | None
) -> dict[str, object]:
    return {
        "truth_value": None,
        "estimate": estimate,
        "interval_lower": interval[0] if interval is not None else None,
        "interval_upper": interval[1] if interval is not None else None,
        "interval_width": interval[1] - interval[0] if interval is not None else None,
        "truth_in_interval": None,
        "signed_error": None,
        "absolute_error": None,
    }


def _same_number(left: object, right: object) -> bool:
    if type(left) not in (int, float) or type(right) not in (int, float):
        return False
    left_value = float(cast(float, left))
    right_value = float(cast(float, right))
    return isfinite(left_value) and isfinite(right_value) and left_value == right_value


def validate_replicate_recovery_row(row: Mapping[str, object]) -> dict[str, object]:
    if tuple(row) != REPLICATE_RECOVERY_HEADER:
        raise ValueError("replicate recovery row has the wrong literal schema")
    result = dict(row)
    scenario_id = result["scenario_id"]
    split_id = result["split_id"]
    replicate_id = result["replicate_id"]
    if scenario_id not in SCENARIO_IDS or type(split_id) is not str:
        raise ValueError("replicate recovery row has an unknown scenario or split")
    if type(replicate_id) is not int or not 0 <= replicate_id < _split_replicate_count(
        scenario_id, split_id
    ):
        raise ValueError("replicate recovery row is outside its frozen split frame")
    registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
    if result["fit_variant"] != registry.primary_fit_variant:
        raise ValueError("replicate recovery row does not use the primary fit variant")
    permitted_parameters = FIT_PARAMETER_IDS.get(scenario_id, ORDERED_PARAMETER_IDS)
    parameter_id = result["parameter_id"]
    if parameter_id not in permitted_parameters:
        raise ValueError("replicate recovery parameter is not fitted by its scenario")
    truth_key = (scenario_id, parameter_id)
    if truth_key not in _SCENARIO_PARAMETER_TRUTH:
        raise ValueError("replicate recovery row has no scenario/parameter truth authority")
    authoritative_truth = _SCENARIO_PARAMETER_TRUTH[truth_key]
    if authoritative_truth is None:
        if result["truth_value"] is not None:
            raise ValueError("truth-free continuous-abundance row must have null truth")
    elif not _same_number(result["truth_value"], authoritative_truth):
        raise ValueError("replicate recovery truth differs from frozen authority")
    if result["gate_result"] not in {
        "pass",
        "fail",
        "diagnostic",
        "warning",
        "not_applicable",
    }:
        raise ValueError("replicate recovery gate_result is outside its enum")
    for name in (
        "truth_value",
        "estimate",
        "interval_lower",
        "interval_upper",
        "interval_width",
        "log_likelihood",
        "signed_error",
        "absolute_error",
    ):
        value = result[name]
        if value is not None and (
            type(value) not in (int, float) or not isfinite(float(cast(float, value)))
        ):
            raise ValueError(f"replicate recovery {name} must be finite or null")
    if type(result["converged"]) is not bool or type(result["profile_two_sided"]) is not bool:
        raise ValueError("replicate recovery convergence/profile states must be bool")
    if result["at_boundary"] is not None and type(result["at_boundary"]) is not bool:
        raise ValueError("replicate recovery at_boundary must be bool or null")
    if result["truth_in_interval"] is not None and type(result["truth_in_interval"]) is not bool:
        raise ValueError("replicate recovery truth_in_interval must be bool or null")
    start_count = result["converged_start_count"]
    if start_count is not None and (type(start_count) is not int or not 0 <= start_count <= 8):
        raise ValueError("replicate recovery converged_start_count is invalid")
    if result["converged"] is False:
        if (
            any(
                result[name] is not None
                for name in (
                    "estimate",
                    "interval_lower",
                    "interval_upper",
                    "interval_width",
                    "at_boundary",
                    "truth_in_interval",
                    "log_likelihood",
                    "signed_error",
                    "absolute_error",
                )
            )
            or result["profile_two_sided"] is not False
        ):
            raise ValueError("failed recovery row carries accepted scientific evidence")
        return result
    if (
        type(start_count) is not int
        or not 6 <= start_count <= 8
        or result["estimate"] is None
        or result["log_likelihood"] is None
        or type(result["at_boundary"]) is not bool
    ):
        raise ValueError("converged recovery row lacks complete fit evidence")
    estimate = float(cast(float, result["estimate"]))
    lower_support, upper_support = _FIT_PARAMETER_SUPPORTS[parameter_id]
    if not lower_support <= estimate <= upper_support:
        raise ValueError("replicate recovery estimate is outside natural support")
    if result["at_boundary"] is not (estimate in (lower_support, upper_support)):
        raise ValueError("replicate recovery boundary state contradicts its estimate")
    lower = result["interval_lower"]
    upper = result["interval_upper"]
    if lower is not None and upper is not None:
        lower_value = float(cast(float, lower))
        upper_value = float(cast(float, upper))
        if (
            lower_value > upper_value
            or lower_value < lower_support
            or upper_value > upper_support
            or not lower_value <= estimate <= upper_value
            or not _same_number(result["interval_width"], upper_value - lower_value)
            or result["profile_two_sided"] is not True
        ):
            raise ValueError("replicate recovery interval algebra is inconsistent")
        if float(cast(float, result["interval_width"])) < 0.0:
            raise ValueError("replicate recovery interval width cannot be negative")
        truth = result["truth_value"]
        if truth is None:
            if result["truth_in_interval"] is not None:
                raise ValueError("truth-free recovery interval has a truth classification")
        elif result["truth_in_interval"] is not (
            lower_value <= float(cast(float, truth)) <= upper_value
        ):
            raise ValueError("replicate recovery truth interval algebra is inconsistent")
    elif (
        result["interval_width"] is not None
        or result["profile_two_sided"] is not False
        or result["truth_in_interval"] is not None
    ):
        raise ValueError("open recovery interval has contradictory interval algebra")
    truth = authoritative_truth
    if truth is None:
        if result["signed_error"] is not None or result["absolute_error"] is not None:
            raise ValueError("truth-free recovery row cannot carry errors")
    else:
        signed_error = estimate - float(truth)
        if not _same_number(result["signed_error"], signed_error) or not _same_number(
            result["absolute_error"], abs(signed_error)
        ):
            raise ValueError("replicate recovery error algebra is inconsistent")
    return result


def validate_replicate_recovery_rows(
    rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    validated = tuple(validate_replicate_recovery_row(row) for row in rows)
    key_names = FIT_DERIVED_PRIMARY_KEYS["replicate_recovery.csv"]
    keys = tuple(tuple(row[name] for name in key_names) for row in validated)
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate replicate recovery primary key")
    if keys != tuple(sorted(keys)):
        raise ValueError("replicate recovery rows must use the literal sort key")
    return validated


def validate_identifiability_profile_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    fit_rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    if not rows or any(tuple(row) != IDENTIFIABILITY_PROFILES_HEADER for row in rows):
        raise ValueError("identifiability profiles have the wrong literal schema")
    validated_fits = tuple(validate_fit_execution_row(row) for row in fit_rows)
    fit_lookup = {
        (fit["scenario_id"], fit["split_id"], fit["fit_index"], fit["fit_variant"]): fit
        for fit in validated_fits
        if fit["fit_scope"] == "replicate"
    }
    if len(fit_lookup) != sum(fit["fit_scope"] == "replicate" for fit in validated_fits):
        raise ValueError("profile fit evidence contains a duplicate replicate identity")
    validated = tuple(dict(row) for row in rows)
    keys = tuple(
        tuple(row[name] for name in FIT_DERIVED_PRIMARY_KEYS["identifiability_profiles.csv"])
        for row in validated
    )
    if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
        raise ValueError("profile rows must have unique sorted literal keys")
    groups: dict[tuple[str, str, int, str, str], list[dict[str, object]]] = {}
    for row in validated:
        scenario_id = cast(str, row["scenario_id"])
        split_id = cast(str, row["split_id"])
        replicate_id = row["replicate_id"]
        fit_variant = cast(str, row["fit_variant"])
        parameter_id = cast(str, row["parameter_id"])
        validate_primary_fit_variant("identifiability_profiles.csv", scenario_id, fit_variant)
        if parameter_id not in FIT_PARAMETER_IDS.get(scenario_id, ORDERED_PARAMETER_IDS):
            raise ValueError("profile parameter is not fitted by its scenario")
        if type(replicate_id) is not int or not 0 <= replicate_id < _split_replicate_count(
            scenario_id, split_id
        ):
            raise ValueError("profile replicate is outside its literal split frame")
        key = (scenario_id, split_id, replicate_id, fit_variant)
        if key not in fit_lookup:
            raise ValueError("profile row does not resolve to exactly one fit row")
        grid_index = row["grid_index"]
        parameter_value = row["parameter_value"]
        if type(grid_index) is not int or grid_index < 0:
            raise ValueError("profile grid_index must be a nonnegative integer")
        if type(parameter_value) not in (int, float) or not isfinite(
            float(cast(float, parameter_value))
        ):
            raise ValueError("profile parameter value must be finite")
        lower, upper = _FIT_PARAMETER_SUPPORTS[parameter_id]
        if not lower <= float(cast(float, parameter_value)) <= upper:
            raise ValueError("profile parameter value is outside natural support")
        if type(row["nuisance_converged"]) is not bool:
            raise ValueError("profile nuisance status must be bool")
        if row["nuisance_converged"] is False:
            if any(
                row[name] is not None
                for name in (
                    "profile_log_likelihood",
                    "likelihood_ratio_delta",
                    "inside_interval",
                )
            ):
                raise ValueError("failed profile point carries accepted likelihood evidence")
        else:
            fit = fit_lookup[key]
            profile_likelihood = row["profile_log_likelihood"]
            delta = row["likelihood_ratio_delta"]
            if (
                fit["fit_succeeded"] is not True
                or type(profile_likelihood) not in (int, float)
                or type(delta) not in (int, float)
                or not isfinite(float(cast(float, profile_likelihood)))
                or not isfinite(float(cast(float, delta)))
                or float(cast(float, delta)) < 0.0
                or not _same_number(
                    delta,
                    2.0
                    * (
                        float(cast(float, fit["log_likelihood"]))
                        - float(cast(float, profile_likelihood))
                    ),
                )
                or row["inside_interval"] is not (float(cast(float, delta)) <= PROFILE_LR_CUTOFF)
            ):
                raise ValueError("profile likelihood/delta evidence does not reconcile to fit")
        group_key = (scenario_id, split_id, replicate_id, fit_variant, parameter_id)
        groups.setdefault(group_key, []).append(row)
    estimate_fields = {
        "alpha": "alpha_estimate",
        "beta_driver": "beta_driver_estimate",
        "beta_quality": "beta_quality_estimate",
        "lambda_quasi": "lambda_quasi_estimate",
        "lambda_present": "lambda_present_estimate",
    }
    for profile_group_key, group in groups.items():
        indices = tuple(cast(int, row["grid_index"]) for row in group)
        values = tuple(float(cast(float, row["parameter_value"])) for row in group)
        if indices != tuple(range(len(group))) or any(
            left >= right for left, right in pairwise(values)
        ):
            raise ValueError("profile grid must be contiguous and strictly ordered")
        fit = fit_lookup[profile_group_key[:4]]
        parameter_id = profile_group_key[4]
        if fit["fit_succeeded"] is True:
            mle = fit[estimate_fields[parameter_id]]
            if (
                sum(
                    row["nuisance_converged"] is True
                    and _same_number(row["parameter_value"], mle)
                    and _same_number(row["likelihood_ratio_delta"], 0.0)
                    for row in group
                )
                != 1
            ):
                raise ValueError("profile grid must contain exactly one fit-bound MLE point")
        elif any(row["nuisance_converged"] is True for row in group):
            raise ValueError("failed fit cannot have a successful profile point")
    return validated


def derive_profile_interval_from_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    fit_row: Mapping[str, object],
) -> tuple[float | None, float | None, bool]:
    fit = validate_fit_execution_row(fit_row)
    validated = validate_identifiability_profile_rows(rows, fit_rows=(fit,))
    identities = {
        tuple(
            row[name]
            for name in ("scenario_id", "split_id", "replicate_id", "fit_variant", "parameter_id")
        )
        for row in validated
    }
    if len(identities) != 1:
        raise ValueError("profile interval reconstruction requires exactly one profile group")
    identity = next(iter(identities))
    if identity[:4] != (
        fit["scenario_id"],
        fit["split_id"],
        fit["fit_index"],
        fit["fit_variant"],
    ):
        raise ValueError("profile interval group does not bind its exact fit identity")
    parameter_id = cast(str, identity[4])
    estimate_field = {
        "alpha": "alpha_estimate",
        "beta_driver": "beta_driver_estimate",
        "beta_quality": "beta_quality_estimate",
        "lambda_quasi": "lambda_quasi_estimate",
        "lambda_present": "lambda_present_estimate",
    }[parameter_id]
    if fit["fit_succeeded"] is not True:
        raise ValueError("failed fit has no authoritative profile interval")
    mle = float(cast(float, fit[estimate_field]))
    lower_support, upper_support = _FIT_PARAMETER_SUPPORTS[parameter_id]

    def endpoint(side: str) -> float | None:
        side_rows = tuple(
            row
            for row in validated
            if (
                float(cast(float, row["parameter_value"])) < mle
                if side == "lower"
                else float(cast(float, row["parameter_value"])) > mle
            )
        )
        if not side_rows:
            raise ValueError("complete profile group requires evidence on both MLE sides")
        root_rows = tuple(
            row
            for row in side_rows
            if row["nuisance_converged"] is True
            and row["likelihood_ratio_delta"] is not None
            and abs(float(cast(float, row["likelihood_ratio_delta"])) - PROFILE_LR_CUTOFF)
            <= PROFILE_LR_DELTA_TOLERANCE
        )
        if len(root_rows) > 1:
            raise ValueError("profile side contains multiple emitted LR root points")
        support = lower_support if side == "lower" else upper_support
        if root_rows:
            root = root_rows[0]
            root_value = float(cast(float, root["parameter_value"]))
            outward = tuple(
                row
                for row in side_rows
                if row["nuisance_converged"] is True
                and row["likelihood_ratio_delta"] is not None
                and (
                    float(cast(float, row["parameter_value"])) < root_value
                    if side == "lower"
                    else float(cast(float, row["parameter_value"])) > root_value
                )
                and float(cast(float, row["likelihood_ratio_delta"])) > PROFILE_LR_CUTOFF
            )
            if not outward and root_value != support:
                raise ValueError("profile LR root lacks its outward sign-changing bracket point")
            return root_value
        support_rows = tuple(
            row for row in side_rows if _same_number(row["parameter_value"], support)
        )
        if len(support_rows) != 1:
            raise ValueError("open profile side must reach its literal support bound")
        if any(
            row["nuisance_converged"] is True
            and row["likelihood_ratio_delta"] is not None
            and float(cast(float, row["likelihood_ratio_delta"]))
            > PROFILE_LR_CUTOFF + PROFILE_LR_DELTA_TOLERANCE
            for row in side_rows
        ):
            raise ValueError("profile side crosses the LR cutoff without an emitted Brent root")
        return None

    lower = endpoint("lower")
    upper = endpoint("upper")
    return lower, upper, lower is not None and upper is not None


def validate_recovery_profile_reconciliation(
    recovery_rows: Sequence[Mapping[str, object]],
    profile_rows: Sequence[Mapping[str, object]],
    fit_rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    fits, _designs = _partition_fit_execution_evidence(fit_rows)
    recovery = validate_replicate_recovery_rows(recovery_rows)
    validate_primary_science_foreign_keys("replicate_recovery.csv", recovery, fits)
    profiles = (
        validate_identifiability_profile_rows(profile_rows, fit_rows=fits) if profile_rows else ()
    )
    fit_lookup = {
        (fit["scenario_id"], fit["split_id"], fit["fit_index"], fit["fit_variant"]): fit
        for fit in fits
        if fit["fit_scope"] == "replicate"
    }
    profile_groups: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in profiles:
        key = tuple(
            row[name]
            for name in ("scenario_id", "split_id", "replicate_id", "fit_variant", "parameter_id")
        )
        profile_groups.setdefault(key, []).append(row)
    recovery_keys = {
        tuple(
            row[name]
            for name in ("scenario_id", "split_id", "replicate_id", "fit_variant", "parameter_id")
        )
        for row in recovery
    }
    if set(profile_groups) - recovery_keys:
        raise ValueError("profile table contains a foreign or orphan recovery identity")
    descriptive = {
        "permuted_arrival_alignment_stress",
        "informative_dropout_misspecification_stress",
        "goal018_continuous_abundance_stress",
        "spatial_frailty_stress",
    }
    for row in recovery:
        key = tuple(
            row[name]
            for name in ("scenario_id", "split_id", "replicate_id", "fit_variant", "parameter_id")
        )
        fit_key = (key[0], key[1], key[2], key[3])
        fit = fit_lookup[fit_key]
        group = profile_groups.get(key)
        if fit["fit_succeeded"] is not True:
            if group:
                raise ValueError("failed fit cannot have an accepted profile group")
            expected_failed_gate = "warning" if row["scenario_id"] in descriptive else "fail"
            if row["gate_result"] != expected_failed_gate:
                raise ValueError("failed recovery row gate does not derive from fit availability")
            continue
        if not group:
            raise ValueError("successful required fit is missing its complete profile group")
        lower, upper, two_sided = derive_profile_interval_from_rows(group, fit_row=fit)
        if not (
            (row["interval_lower"] is None and lower is None)
            or _same_number(row["interval_lower"], lower)
        ) or not (
            (row["interval_upper"] is None and upper is None)
            or _same_number(row["interval_upper"], upper)
        ):
            raise ValueError("recovery interval endpoints do not derive from profile roots")
        truth = row["truth_value"]
        if two_sided:
            if lower is None or upper is None:
                raise ValueError("two-sided profile interval lacks a finite endpoint")
            expected_width = upper - lower
            expected_coverage = (
                None if truth is None else lower <= float(cast(float, truth)) <= upper
            )
        else:
            expected_width = None
            expected_coverage = None
        expected_gate = (
            "diagnostic" if row["scenario_id"] in descriptive else "pass" if two_sided else "fail"
        )
        if (
            row["profile_two_sided"] is not two_sided
            or not (
                (row["interval_width"] is None and expected_width is None)
                or _same_number(row["interval_width"], expected_width)
            )
            or row["truth_in_interval"] is not expected_coverage
            or row["gate_result"] != expected_gate
        ):
            raise ValueError(
                "recovery interval algebra or gate does not derive from profile evidence"
            )
    return recovery


def validate_coverage_summary_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    recovery_rows: Sequence[Mapping[str, object]],
    fit_rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    if not rows or any(tuple(row) != COVERAGE_CALIBRATION_HEADER for row in rows):
        raise ValueError("coverage summary has the wrong literal schema")
    validated_recovery = validate_replicate_recovery_rows(recovery_rows)
    validated = tuple(dict(row) for row in rows)
    keys = tuple(
        tuple(row[name] for name in FIT_DERIVED_PRIMARY_KEYS["coverage_calibration.csv"])
        for row in validated
    )
    if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
        raise ValueError("coverage summary keys must be unique and sorted")
    for row in validated:
        identity = tuple(
            row[name] for name in ("scenario_id", "split_id", "fit_variant", "parameter_id")
        )
        source = tuple(
            source_row
            for source_row in validated_recovery
            if tuple(
                source_row[name]
                for name in ("scenario_id", "split_id", "fit_variant", "parameter_id")
            )
            == identity
        )
        scenario_id, split_id, fit_variant, parameter_id = identity
        attempted = _split_replicate_count(cast(str, scenario_id), cast(str, split_id))
        expected_fit_rows = tuple(
            fit
            for fit in fit_rows
            if fit.get("scenario_id") == scenario_id
            and fit.get("split_id") == split_id
            and fit.get("fit_variant") == fit_variant
        )
        support = _FIT_PARAMETER_SUPPORTS[cast(str, parameter_id)]
        summary = summarize_attempted_recovery(
            source,
            fit_rows=expected_fit_rows,
            attempted=attempted,
            support_width=support[1] - support[0],
        )
        truth_free = scenario_id == "goal018_continuous_abundance_stress"
        expected_coverage_count = None if truth_free else summary["coverage_count"]
        expected_fraction = None if truth_free else cast(int, summary["coverage_count"]) / attempted
        bounds: tuple[int | None, int | None]
        if scenario_id in NESTED_SCENARIOS and split_id == "holdout":
            bounds = (36, 48)
        elif scenario_id == "sparse_expected_failure" and split_id == "holdout":
            bounds = (18, 24)
        else:
            bounds = (None, None)
        expected_fields = {
            "replicate_count": attempted,
            "converged_count": summary["converged_count"],
            "coverage_count": expected_coverage_count,
            "coverage_fraction": expected_fraction,
            "acceptance_lower_count": bounds[0],
            "acceptance_upper_count": bounds[1],
            "median_signed_error": summary["median_signed_error"],
            "median_absolute_error": summary["median_absolute_error"],
            "median_interval_width": summary["median_interval_width"],
            "maximum_absolute_error": summary["maximum_absolute_error"],
            "maximum_interval_width": summary["maximum_interval_width"],
        }
        if any(row[name] != value for name, value in expected_fields.items()):
            raise ValueError("coverage summary does not recompute from complete recovery evidence")
        if scenario_id in NESTED_SCENARIOS and split_id == "holdout":
            convergence_limit = cast(Mapping[str, float], FROZEN_GATE_CONFIG["convergence_limits"])[
                scenario_id
            ]
            minimum_converged = int(np.ceil(attempted * convergence_limit))
            width_limit = cast(Mapping[str, float], FROZEN_GATE_CONFIG["profile_width_limits"])[
                cast(str, parameter_id)
            ]
            error_limit = cast(Mapping[str, float], FROZEN_GATE_CONFIG["absolute_error_limits"])[
                cast(str, parameter_id)
            ]
            gate_pass = (
                nested_gate(
                    coverage_count=cast(int, summary["coverage_count"]),
                    converged_count=cast(int, summary["converged_count"]),
                    minimum_converged=minimum_converged,
                )
                and cast(float, summary["median_interval_width"]) <= width_limit
                and cast(float, summary["median_absolute_error"]) <= error_limit
            )
            expected_gate = "pass" if gate_pass else "fail"
        elif scenario_id == "sparse_expected_failure" and split_id == "holdout":
            expected_gate = "pass" if 18 <= cast(int, summary["coverage_count"]) <= 24 else "fail"
        else:
            complete = all(
                source_row["converged"] is True and source_row["profile_two_sided"] is True
                for source_row in source
            )
            expected_gate = "diagnostic" if complete else "warning"
        if row["gate_result"] != expected_gate:
            raise ValueError("coverage summary gate result does not recompute from source rows")
    return validated


def reconcile_control_summary(
    *,
    fit_rows: Sequence[Mapping[str, object]],
    zero_recovery_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validated = tuple(validate_fit_execution_row(row) for row in fit_rows)
    permitted_scenarios = {
        "zero_driver_effect_negative_control",
        "permuted_arrival_alignment_stress",
        "no_emission_contrast_negative_control",
    }
    if any(row["scenario_id"] not in permitted_scenarios for row in validated):
        raise ValueError("control summary contains a foreign fit scenario")
    zero_fits = tuple(
        row for row in validated if row["scenario_id"] == "zero_driver_effect_negative_control"
    )
    if len(zero_fits) != 24:
        raise ValueError("zero-driver denominator requires 24 primary fit rows")
    zero_fit_by_index: dict[int, Mapping[str, object]] = {}
    for row in zero_fits:
        index = cast(int, row["fit_index"])
        if (
            row["split_id"] != "holdout"
            or row["fit_scope"] != "replicate"
            or row["fit_variant"] != "canonical"
            or index in zero_fit_by_index
        ):
            raise ValueError("zero-driver fit identity is incomplete or duplicated")
        zero_fit_by_index[index] = row
    if set(zero_fit_by_index) != set(range(24)):
        raise ValueError("zero-driver fit frame must contain holdout replicates 0 through 23")
    recovery_rows = validate_replicate_recovery_rows(zero_recovery_rows)
    if len(recovery_rows) != 24:
        raise ValueError("zero-driver recovery frame requires exactly 24 canonical rows")
    recovery_by_index: dict[int, Mapping[str, object]] = {}
    for row in recovery_rows:
        recovery_index = row["replicate_id"]
        if (
            row["scenario_id"] != "zero_driver_effect_negative_control"
            or row["split_id"] != "holdout"
            or row["fit_variant"] != "canonical"
            or row["parameter_id"] != "beta_driver"
            or type(recovery_index) is not int
            or not 0 <= recovery_index < 24
            or recovery_index in recovery_by_index
        ):
            raise ValueError("zero-driver recovery identity is incomplete or duplicated")
        recovery_by_index[recovery_index] = row
    if set(recovery_by_index) != set(range(24)):
        raise ValueError("zero-driver recovery frame must contain holdout replicates 0 through 23")
    arrival_rows = tuple(
        row for row in validated if row["scenario_id"] == "permuted_arrival_alignment_stress"
    )
    fit_cell_ids, score_cell_ids = authoritative_alignment_frame_cell_ids()
    try:
        arrival_count = validate_arrival_fit_pairs(
            arrival_rows,
            fit_cell_ids=fit_cell_ids,
            score_cell_ids=score_cell_ids,
            required_split_id="holdout",
        )
    except ValueError as error:
        raise ValueError(
            "control summary denominator requires 24 complete arrival holdout pairs"
        ) from error
    if arrival_count != 24:
        raise ValueError("control summary denominator requires 24 complete arrival holdout pairs")
    grouped: dict[int, dict[str, Mapping[str, object]]] = {}
    for row in arrival_rows:
        index = cast(int, row["fit_index"])
        variant = cast(str, row["fit_variant"])
        if variant in grouped.setdefault(index, {}):
            raise ValueError("control summary contains a duplicate arrival fit")
        grouped[index][variant] = row
    if tuple(sorted(grouped)) != tuple(range(24)) or any(
        set(pair) != {"correct_alignment", "permuted_alignment"} for pair in grouped.values()
    ):
        raise ValueError("control summary denominator does not contain 24 complete arrival pairs")
    for pair in grouped.values():
        source_identity = tuple(
            pair["correct_alignment"][name]
            for name in (
                "split_id",
                "source_replicate_first",
                "source_replicate_last",
                "source_replicate_count",
            )
        )
        if source_identity != tuple(
            pair["permuted_alignment"][name]
            for name in (
                "split_id",
                "source_replicate_first",
                "source_replicate_last",
                "source_replicate_count",
            )
        ):
            raise ValueError("arrival variants do not share one holdout source identity")
    bootstrap = recompute_equal_emission_bootstrap(
        tuple(
            row
            for row in validated
            if row["scenario_id"] == "no_emission_contrast_negative_control"
        )
    )
    zero_evaluable = 0
    canonical_zero_intervals: list[tuple[float | None, float | None] | None] = []
    for index in range(24):
        fit = zero_fit_by_index[index]
        recovery = recovery_by_index[index]
        if (
            recovery["converged"] is not fit["fit_succeeded"]
            or recovery["converged_start_count"] != fit["converged_start_count"]
            or recovery["at_boundary"] != fit["at_boundary"]
            or recovery["estimate"] != fit["beta_driver_estimate"]
            or recovery["log_likelihood"] != fit["log_likelihood"]
        ):
            raise ValueError("zero-driver recovery row does not reconcile to fit evidence")
        interval = (
            (recovery["interval_lower"], recovery["interval_upper"])
            if recovery["interval_lower"] is not None and recovery["interval_upper"] is not None
            else None
        )
        finite_interval = False
        canonical_interval: tuple[float | None, float | None] | None = None
        if interval is not None:
            interval_lower = float(cast(float, interval[0]))
            interval_upper = float(cast(float, interval[1]))
            finite_interval = (
                isfinite(interval_lower)
                and isfinite(interval_upper)
                and interval_lower <= interval_upper
            )
            if finite_interval:
                canonical_interval = (interval_lower, interval_upper)
        if finite_interval != (recovery["profile_two_sided"] is True):
            raise ValueError("zero-driver recovery availability contradicts its interval")
        if fit["fit_succeeded"] is not True and finite_interval:
            raise ValueError("failed zero-driver fit cannot carry a decidable recovery interval")
        zero_evaluable += int(fit["fit_succeeded"] is True and finite_interval)
        canonical_zero_intervals.append(canonical_interval)
    arrival_evaluable = sum(
        pair["correct_alignment"]["fit_succeeded"] is True
        and pair["permuted_alignment"]["fit_succeeded"] is True
        for pair in grouped.values()
    )
    arrival_wins = sum(
        pair["correct_alignment"]["fit_succeeded"] is True
        and pair["permuted_alignment"]["fit_succeeded"] is True
        and float(cast(float, pair["correct_alignment"]["heldout_log_score"]))
        > float(cast(float, pair["permuted_alignment"]["heldout_log_score"]))
        for pair in grouped.values()
    )
    zero_exclusions = sum(
        interval is not None
        and interval[0] is not None
        and interval[1] is not None
        and interval_excludes_zero(float(interval[0]), float(interval[1]))
        for interval in canonical_zero_intervals
    )
    return {
        "zero_attempted": len(recovery_rows),
        "zero_evaluable": zero_evaluable,
        "zero_event_count": zero_exclusions,
        "zero_decision": zero_driver_decision(tuple(canonical_zero_intervals)),
        "arrival_attempted": 24,
        "arrival_evaluable": arrival_evaluable,
        "arrival_wins": arrival_wins,
        "arrival_event_count": arrival_wins,
        "bootstrap_converged_count": cast(int, bootstrap["bootstrap_replicates"]),
        "bootstrap_failed_count": 0,
        "equal_test_statistic": bootstrap["observed_statistic"],
        "equal_p_value": bootstrap["p_value"],
    }


def validate_control_decision_rows(
    rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    if len(rows) != 18 or any(tuple(row) != CONTROL_DECISION_SUMMARY_HEADER for row in rows):
        raise ValueError("control decision summary requires the literal 24-column 18-row schema")
    validated = tuple(dict(row) for row in rows)
    expected_ids = tuple(
        sorted(
            (
                "final_decision",
                *(f"scenario_gate|{scenario_id}" for scenario_id in SCENARIO_IDS),
                *(
                    f"parameter_status|no_emission_contrast_negative_control|{row['parameter_id']}"
                    for row in EQUAL_EMISSION_STATUS_ROWS
                ),
            )
        )
    )
    if tuple(cast(str, row["decision_row_id"]) for row in validated) != expected_ids:
        raise ValueError("control decision rows must contain the exact lexical ID frame")
    numeric_fields = (
        "test_statistic",
        "bootstrap_replicates",
        "bootstrap_converged_count",
        "bootstrap_failed_count",
        "p_value",
        "alignment_correlation",
        "attempted_replicates",
        "evaluable_replicates",
        "event_count",
        "acceptance_lower_count",
        "acceptance_upper_count",
        "recommendation_rank",
    )
    status_by_parameter = {row["parameter_id"]: row for row in EQUAL_EMISSION_STATUS_ROWS}
    for row in validated:
        if (
            row["decision_row_type"] not in {"scenario_gate", "parameter_status", "final_decision"}
            or row["gate_family"] not in AUTHORITY_ENUM_DOMAINS["gate_family"]
            or row["gate_result"] not in {"pass", "fail", "diagnostic", "warning"}
            or type(row["silent_misspecification_failure"]) is not bool
            or row["transportability_class"] != "scheduled_count_only_point_process_bridge_required"
            or type(row["interpretation"]) is not str
            or not row["interpretation"]
        ):
            raise ValueError("control decision row has invalid literal enums or required fields")
        for name in numeric_fields:
            value = row[name]
            if value is not None and (
                type(value) not in (int, float) or not isfinite(float(cast(float, value)))
            ):
                raise ValueError("control decision numeric field must be finite or null")
        row_type = row["decision_row_type"]
        if row_type == "parameter_status":
            parameter_id = row["parameter_id"]
            if type(parameter_id) is not str:
                raise ValueError("parameter-status row requires a string parameter_id")
            authority = status_by_parameter.get(parameter_id)
            if (
                row["decision_row_id"]
                != f"parameter_status|no_emission_contrast_negative_control|{parameter_id}"
                or row["scenario_id"] != "no_emission_contrast_negative_control"
                or authority is None
                or row["structural_status"] != authority["structural_status"]
                or row["practical_status"] != authority["practical_status"]
                or row["gate_family"] != "parameter_status"
                or row["gate_result"] != "diagnostic"
                or row["recommendation_class"] is not None
                or any(row[name] is not None for name in numeric_fields)
            ):
                raise ValueError("equal-emission parameter-status row is not literal")
            continue
        if row_type == "final_decision":
            rank = row["recommendation_rank"]
            if (
                row["decision_row_id"] != "final_decision"
                or row["scenario_id"] is not None
                or row["parameter_id"] is not None
                or row["structural_status"] is not None
                or row["practical_status"] is not None
                or row["gate_family"] != "final_recommendation"
                or type(rank) is not int
                or not 1 <= rank <= 4
                or row["recommendation_class"] != RECOMMENDATION_CLASSES[rank - 1]
                or any(
                    row[name] is not None
                    for name in numeric_fields
                    if name != "recommendation_rank"
                )
            ):
                raise ValueError("final control decision row is not literal")
            continue
        scenario_id = row["scenario_id"]
        if (
            scenario_id not in SCENARIO_IDS
            or row["decision_row_id"] != f"scenario_gate|{scenario_id}"
            or row["parameter_id"] is not None
            or row["structural_status"] is not None
            or row["practical_status"] is not None
            or row["gate_family"] != SCENARIO_GATE_FAMILY[scenario_id]
            or row["recommendation_rank"] is not None
            or row["recommendation_class"] is not None
        ):
            raise ValueError("scenario control decision row is not literal")
        if scenario_id == "zero_driver_effect_negative_control":
            if (
                row["attempted_replicates"] != 24
                or type(row["evaluable_replicates"]) is not int
                or not 0 <= row["evaluable_replicates"] <= 24
                or type(row["event_count"]) is not int
                or not 0 <= row["event_count"] <= row["evaluable_replicates"]
                or (row["acceptance_lower_count"], row["acceptance_upper_count"]) != (0, 6)
                or any(
                    row[name] is not None
                    for name in (
                        "test_statistic",
                        "bootstrap_replicates",
                        "bootstrap_converged_count",
                        "bootstrap_failed_count",
                        "p_value",
                        "alignment_correlation",
                    )
                )
            ):
                raise ValueError("zero-driver control row does not reproduce canonical evidence")
        elif scenario_id == "permuted_arrival_alignment_stress":
            correlation = row["alignment_correlation"]
            if (
                row["attempted_replicates"] != 24
                or type(row["evaluable_replicates"]) is not int
                or not 0 <= row["evaluable_replicates"] <= 24
                or type(row["event_count"]) is not int
                or not 0 <= row["event_count"] <= row["evaluable_replicates"]
                or (row["acceptance_lower_count"], row["acceptance_upper_count"]) != (22, 24)
                or type(correlation) not in (int, float)
                or abs(float(cast(float, correlation))) > 0.25
            ):
                raise ValueError("arrival control row does not reproduce canonical evidence")
        elif scenario_id == "no_emission_contrast_negative_control":
            basic_invalid = (
                row["attempted_replicates"] != 24
                or row["evaluable_replicates"] not in (0, 24)
                or row["bootstrap_replicates"] != 199
                or type(row["bootstrap_converged_count"]) is not int
                or type(row["bootstrap_failed_count"]) is not int
                or row["bootstrap_converged_count"] + row["bootstrap_failed_count"] != 199
                or row["alignment_correlation"] is not None
                or row["acceptance_lower_count"] is not None
                or row["acceptance_upper_count"] is not None
            )
            complete = row["evaluable_replicates"] == 24 and row["bootstrap_failed_count"] == 0
            if complete:
                numeric_invalid = (
                    type(row["event_count"]) is not int
                    or not 0 <= row["event_count"] <= 199
                    or not _same_number(row["p_value"], (1 + row["event_count"]) / 200.0)
                    or type(row["test_statistic"]) not in (int, float)
                )
            else:
                numeric_invalid = (
                    row["event_count"] is not None
                    or row["p_value"] is not None
                    or (row["evaluable_replicates"] == 0 and row["test_statistic"] is not None)
                    or (
                        row["evaluable_replicates"] == 24
                        and type(row["test_statistic"]) not in (int, float)
                    )
                    or row["gate_result"] != "fail"
                )
            if basic_invalid or numeric_invalid:
                raise ValueError("equal-emission control row does not reproduce canonical evidence")
        elif any(row[name] is not None for name in numeric_fields):
            raise ValueError("non-control scenario row has undeclared numeric evidence")
    return validated


def validate_control_decision_reconciliation(
    rows: Sequence[Mapping[str, object]],
    *,
    fit_rows: Sequence[Mapping[str, object]],
    zero_recovery_rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    validated = validate_control_decision_rows(rows)
    evidence = reconcile_control_summary(
        fit_rows=fit_rows,
        zero_recovery_rows=zero_recovery_rows,
    )
    by_id = {cast(str, row["decision_row_id"]): row for row in validated}
    zero = by_id["scenario_gate|zero_driver_effect_negative_control"]
    arrival = by_id["scenario_gate|permuted_arrival_alignment_stress"]
    equal = by_id["scenario_gate|no_emission_contrast_negative_control"]
    expected_zero = (
        evidence["zero_attempted"],
        evidence["zero_evaluable"],
        evidence["zero_event_count"],
        0,
        6,
    )
    if (
        tuple(
            zero[name]
            for name in (
                "attempted_replicates",
                "evaluable_replicates",
                "event_count",
                "acceptance_lower_count",
                "acceptance_upper_count",
            )
        )
        != expected_zero
    ):
        raise ValueError("zero-driver decision row does not reconcile to emitted fit/profile rows")
    expected_arrival = (
        evidence["arrival_attempted"],
        evidence["arrival_evaluable"],
        evidence["arrival_event_count"],
        22,
        24,
    )
    if (
        tuple(
            arrival[name]
            for name in (
                "attempted_replicates",
                "evaluable_replicates",
                "event_count",
                "acceptance_lower_count",
                "acceptance_upper_count",
            )
        )
        != expected_arrival
    ):
        raise ValueError("arrival decision row does not reconcile to emitted fit pairs")
    equal_event_count = round(cast(float, evidence["equal_p_value"]) * 200.0 - 1.0)
    expected_equal = (
        24,
        24,
        199,
        evidence["bootstrap_converged_count"],
        evidence["bootstrap_failed_count"],
        equal_event_count,
    )
    if (
        tuple(
            equal[name]
            for name in (
                "attempted_replicates",
                "evaluable_replicates",
                "bootstrap_replicates",
                "bootstrap_converged_count",
                "bootstrap_failed_count",
                "event_count",
            )
        )
        != expected_equal
        or not _same_number(equal["test_statistic"], evidence["equal_test_statistic"])
        or not _same_number(equal["p_value"], evidence["equal_p_value"])
    ):
        raise ValueError("equal-emission decision row does not reconcile to emitted refit pairs")
    if not _same_number(arrival["alignment_correlation"], authoritative_alignment_correlation()):
        raise ValueError("arrival decision correlation does not reconcile to canonical source")
    scenario_rows = tuple(row for row in validated if row["decision_row_type"] == "scenario_gate")
    for row in scenario_rows:
        expected_silent = cast(str, row["interpretation"]).endswith("_silent_misspecification")
        if row["silent_misspecification_failure"] is not expected_silent:
            raise ValueError("scenario silent-misspecification state is contradictory")
    final = by_id["final_decision"]
    all_scenarios_pass = all(row["gate_result"] == "pass" for row in scenario_rows)
    if (final["gate_result"] == "pass") is not all_scenarios_pass or (
        final["recommendation_rank"] == 4
    ) is not all_scenarios_pass:
        raise ValueError("final recommendation does not reconcile to scenario gates")
    return validated


def failed_predictive_rows(
    *,
    scenario_id: str,
    split_id: str,
    replicate_id: int,
    opportunity_frame: PredictiveOpportunityFrameEvidence,
) -> tuple[dict[str, object], ...]:
    if scenario_id not in SCENARIO_IDS:
        raise ValueError("unknown predictive scenario")
    if type(replicate_id) is not int or not 0 <= replicate_id < _split_replicate_count(
        scenario_id, split_id
    ):
        raise ValueError("predictive replicate is outside the frozen split frame")
    if type(opportunity_frame) is not PredictiveOpportunityFrameEvidence or (
        opportunity_frame.scenario_id,
        opportunity_frame.split_id,
        opportunity_frame.replicate_id,
    ) != (scenario_id, split_id, replicate_id):
        raise ValueError("predictive opportunity frame must match the exact replicate identity")
    _validate_predictive_opportunity_frame(opportunity_frame)
    sample_sizes = dict(zip(PREDICTIVE_STRATA, opportunity_frame.stratum_counts, strict=True))
    return tuple(
        {
            "scenario_id": scenario_id,
            "split_id": split_id,
            "replicate_id": replicate_id,
            "fit_variant": SCENARIO_EVIDENCE_REGISTRY[
                SCENARIO_IDS.index(scenario_id)
            ].primary_fit_variant,
            "stratum_type": stratum_type,
            "stratum_value": stratum_value,
            "metric_id": metric,
            "sample_size": sample_sizes[(stratum_type, stratum_value)],
            "opportunity_frame_count": opportunity_frame.opportunity_count,
            "opportunity_frame_sha256": opportunity_frame.opportunity_frame_sha256,
            "dropout_mask_sha256": opportunity_frame.dropout_mask_sha256,
            "fit_succeeded": False,
            "diagnostic_available": False,
            "observed_value": None,
            "reference_mean": None,
            "reference_sd": None,
            "reference_mcse": None,
            "standardized_residual": None,
            "standardized_residual_nonfinite": False,
            "randomized_pit": None,
        }
        for stratum_type, stratum_value in PREDICTIVE_STRATA
        for metric in PREDICTIVE_METRICS
    )


def validate_predictive_replicate_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    opportunity_frame: PredictiveOpportunityFrameEvidence | None = None,
) -> None:
    if len(rows) != 27 or any(
        tuple(row) != PREDICTIVE_REPLICATE_DIAGNOSTICS_HEADER for row in rows
    ):
        raise ValueError("predictive artifact requires the literal 20-column 27-row schema")
    expected_cells = tuple(
        (stratum_type, stratum_value, metric)
        for stratum_type, stratum_value in PREDICTIVE_STRATA
        for metric in PREDICTIVE_METRICS
    )
    cells = tuple((row["stratum_type"], row["stratum_value"], row["metric_id"]) for row in rows)
    if cells != expected_cells:
        raise ValueError("predictive artifact does not contain the exact ordered 27 cells")
    first = rows[0]
    identity = tuple(
        first[name] for name in ("scenario_id", "split_id", "replicate_id", "fit_variant")
    )
    scenario_id, split_id, replicate_id, fit_variant = identity
    if scenario_id not in SCENARIO_IDS:
        raise ValueError("predictive artifact has an unknown scenario")
    if type(split_id) is not str:
        raise ValueError("predictive artifact split must be string")
    if type(replicate_id) is not int or not 0 <= replicate_id < _split_replicate_count(
        scenario_id, split_id
    ):
        raise ValueError("predictive artifact replicate is outside the frozen frame")
    registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
    if fit_variant != registry.primary_fit_variant:
        raise ValueError("predictive artifact uses a non-primary fit variant")
    if opportunity_frame is None:
        digest = first["opportunity_frame_sha256"]
        if type(digest) is not str:
            raise ValueError("predictive opportunity digest must be a string")
        registry_key = (
            scenario_id,
            split_id,
            replicate_id,
            digest,
        )
        expected_frame = _PREDICTIVE_FRAME_REGISTRY.get(registry_key)
        if expected_frame is None:
            expected_frame = deterministic_predictive_opportunity_frame(
                scenario_id, split_id, replicate_id
            )
    else:
        expected_frame = opportunity_frame
    _validate_predictive_opportunity_frame(expected_frame)
    if (
        expected_frame.scenario_id,
        expected_frame.split_id,
        expected_frame.replicate_id,
    ) != (scenario_id, split_id, replicate_id):
        raise ValueError("predictive opportunity frame belongs to another replicate")
    expected_counts = dict(zip(PREDICTIVE_STRATA, expected_frame.stratum_counts, strict=True))
    for row in rows:
        if (
            tuple(row[name] for name in ("scenario_id", "split_id", "replicate_id", "fit_variant"))
            != identity
        ):
            raise ValueError("predictive artifact contains mixed identities")
        stratum = (cast(str, row["stratum_type"]), cast(str, row["stratum_value"]))
        if row["sample_size"] != expected_counts[stratum]:
            raise ValueError(
                "predictive sample_size must equal its exact opportunity stratum count"
            )
        if (
            row["opportunity_frame_count"] != expected_frame.opportunity_count
            or row["opportunity_frame_sha256"] != expected_frame.opportunity_frame_sha256
            or row["dropout_mask_sha256"] != expected_frame.dropout_mask_sha256
        ):
            raise ValueError("predictive opportunity frame or dropout mask binding is invalid")
        if type(row["fit_succeeded"]) is not bool or type(row["diagnostic_available"]) is not bool:
            raise ValueError("predictive fit and availability states must be bool")
        if type(row["standardized_residual_nonfinite"]) is not bool:
            raise ValueError("predictive nonfinite flag must be bool")
        available = row["diagnostic_available"]
        if available:
            required_finite = (
                "observed_value",
                "reference_mean",
                "reference_sd",
                "reference_mcse",
                "randomized_pit",
            )
            if row["fit_succeeded"] is not True or any(
                type(row[name]) not in (int, float) or not isfinite(float(cast(float, row[name])))
                for name in required_finite
            ):
                raise ValueError("available predictive row requires finite base diagnostics")
            metric_id = cast(str, row["metric_id"])
            observed = float(cast(float, row["observed_value"]))
            reference_mean = float(cast(float, row["reference_mean"]))
            for value in (observed, reference_mean):
                valid_domain = 0.0 <= value <= 1.0 if metric_id == "zero_fraction" else value >= 0.0
                if not valid_domain:
                    raise ValueError("predictive metric value is outside its literal domain")
            reference_sd = float(cast(float, row["reference_sd"]))
            reference_mcse = float(cast(float, row["reference_mcse"]))
            if reference_sd < 0.0:
                raise ValueError("predictive reference SD is outside its literal domain")
            if not _same_number(reference_mcse, reference_sd / sqrt(199.0)):
                raise ValueError("predictive reference MCSE does not reproduce SD/sqrt(199)")
            randomized_pit = float(cast(float, row["randomized_pit"]))
            if not 0.0 <= randomized_pit <= 1.0:
                raise ValueError("randomized PIT must be in [0, 1]")
            residual = row["standardized_residual"]
            nonfinite = row["standardized_residual_nonfinite"]
            if reference_sd == 0.0:
                if observed == reference_mean:
                    if not _same_number(residual, 0.0) or nonfinite is not False:
                        raise ValueError("zero-SD predictive residual algebra is inconsistent")
                elif residual is not None or nonfinite is not True:
                    raise ValueError("nonfinite predictive residual state is inconsistent")
            else:
                with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
                    expected_residual = float(
                        np.float64(observed - reference_mean) / np.float64(reference_sd)
                    )
                if isfinite(expected_residual):
                    if not _same_number(residual, expected_residual) or nonfinite is not False:
                        raise ValueError("predictive standardized residual algebra is inconsistent")
                elif residual is not None or nonfinite is not True:
                    raise ValueError("nonfinite predictive residual state is inconsistent")
        else:
            numeric_fields = (
                "observed_value",
                "reference_mean",
                "reference_sd",
                "reference_mcse",
                "standardized_residual",
                "randomized_pit",
            )
            if (
                row["fit_succeeded"] is not False
                or any(row[name] is not None for name in numeric_fields)
                or row["standardized_residual_nonfinite"] is not False
            ):
                raise ValueError("unavailable predictive row requires typed failed-fit nulls")


def validate_predictive_warning_binding(
    rows: Sequence[Mapping[str, object]], *, warning: bool
) -> None:
    if type(warning) is not bool:
        raise ValueError("predictive warning must be bool")
    validate_predictive_replicate_rows(rows)
    warning_required = any(
        row["fit_succeeded"] is not True
        or row["diagnostic_available"] is not True
        or row["standardized_residual_nonfinite"] is True
        for row in rows
    )
    if warning_required and warning is not True:
        raise ValueError("predictive warning is mandatory for unavailable or nonfinite evidence")


def predictive_warning_required(
    *,
    incomplete_or_nonfinite: bool,
    holm_adjusted_p: float | None,
    stouffer_z: float | None,
) -> bool:
    if type(incomplete_or_nonfinite) is not bool:
        raise ValueError("predictive warning completeness state must be bool")
    for name, value in (("holm_adjusted_p", holm_adjusted_p), ("stouffer_z", stouffer_z)):
        if value is not None and (type(value) not in (int, float) or not isfinite(float(value))):
            raise ValueError(f"predictive {name} must be finite or null")
    return (
        incomplete_or_nonfinite
        or holm_adjusted_p is None
        or float(holm_adjusted_p) < cast(float, FROZEN_GATE_CONFIG["pit_familywise_alpha"])
        or stouffer_z is None
        or abs(float(stouffer_z)) > 3.0
    )


def validate_predictive_summary_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    predictive_rows: Sequence[Mapping[str, object]],
    fit_rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    if len(rows) != 27 or any(tuple(row) != PREDICTIVE_CHECK_SUMMARY_HEADER for row in rows):
        raise ValueError("predictive summary requires the literal 16-column 27-row schema")
    expected_cells = tuple(
        (stratum_type, stratum_value, metric_id)
        for stratum_type, stratum_value in PREDICTIVE_STRATA
        for metric_id in PREDICTIVE_METRICS
    )
    if (
        tuple((row["stratum_type"], row["stratum_value"], row["metric_id"]) for row in rows)
        != expected_cells
    ):
        raise ValueError("predictive summary is missing or reorders its 27 literal cells")
    identity = tuple(rows[0][name] for name in ("scenario_id", "split_id", "fit_variant"))
    if any(
        tuple(row[name] for name in ("scenario_id", "split_id", "fit_variant")) != identity
        for row in rows
    ):
        raise ValueError("predictive summary contains mixed identities")
    scenario_id, split_id, _fit_variant = identity
    attempted = _split_replicate_count(cast(str, scenario_id), cast(str, split_id))
    source_groups: dict[int, list[Mapping[str, object]]] = {}
    for source_row in predictive_rows:
        if (
            tuple(source_row.get(name) for name in ("scenario_id", "split_id", "fit_variant"))
            != identity
        ):
            raise ValueError("predictive summary source contains a foreign identity")
        replicate_id = source_row.get("replicate_id")
        if type(replicate_id) is not int:
            raise ValueError("predictive source replicate_id must be int")
        source_groups.setdefault(replicate_id, []).append(source_row)
    if set(source_groups) != set(range(attempted)):
        raise ValueError("predictive summary source does not contain the complete split frame")
    for source_group in source_groups.values():
        validate_predictive_replicate_rows(source_group)
    validate_primary_science_foreign_keys(
        "predictive_replicate_diagnostics.csv", predictive_rows, fit_rows
    )
    source_by_cell = {
        cell: tuple(
            next(
                source_row
                for source_row in source_groups[replicate_id]
                if (
                    source_row["stratum_type"],
                    source_row["stratum_value"],
                    source_row["metric_id"],
                )
                == cell
            )
            for replicate_id in range(attempted)
        )
        for cell in expected_cells
    }
    computed: list[dict[str, object]] = []
    raw_values: list[float | None] = []
    for cell in expected_cells:
        source = source_by_cell[cell]
        available = tuple(row for row in source if row["diagnostic_available"] is True)
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
        stouffer = float(residuals.sum() / sqrt(float(residuals.size))) if residuals.size else None
        if pits.size:
            ordered = np.sort(pits)
            pit_indices = np.arange(1, pits.size + 1, dtype=np.float64)
            ks_statistic = float(
                max(
                    np.max(pit_indices / pits.size - ordered),
                    np.max(ordered - (pit_indices - 1.0) / pits.size),
                )
            )
            raw_p = float(kstwo.sf(ks_statistic, pits.size))
        else:
            ks_statistic = None
            raw_p = None
        warning = (
            len(available) != attempted
            or any(row["fit_succeeded"] is not True for row in source)
            or any(row["standardized_residual_nonfinite"] is True for row in source)
            or mean_residual is None
            or stouffer is None
            or raw_p is None
        )
        computed.append(
            {
                "replicate_count": attempted,
                "diagnostic_count": len(available),
                "failed_fit_count": sum(row["fit_succeeded"] is False for row in source),
                "mean_standardized_residual": mean_residual,
                "stouffer_z": stouffer,
                "ks_statistic": ks_statistic,
                "raw_p": raw_p,
                "warning": warning,
            }
        )
        raw_values.append(raw_p)
    adjusted: list[float | None] = [None] * len(raw_values)
    finite_order = sorted(
        (index for index, value in enumerate(raw_values) if value is not None),
        key=lambda index: (cast(float, raw_values[index]), index),
    )
    running = 0.0
    for rank, cell_index in enumerate(finite_order):
        running = max(
            running,
            (len(raw_values) - rank) * cast(float, raw_values[cell_index]),
        )
        adjusted[cell_index] = min(1.0, running)
    for cell_index, (row, expected) in enumerate(zip(rows, computed, strict=True)):
        expected["holm_adjusted_p"] = adjusted[cell_index]
        adjusted_p = adjusted[cell_index]
        stouffer_z = expected["stouffer_z"]
        expected["warning"] = predictive_warning_required(
            incomplete_or_nonfinite=expected["warning"] is True,
            holm_adjusted_p=adjusted_p,
            stouffer_z=cast(float | None, stouffer_z),
        )
        expected["gate_result"] = "fail" if expected["warning"] is True else "pass"
        for name, value in expected.items():
            if value is None:
                if row[name] is not None:
                    raise ValueError("predictive summary nullable aggregate is contradictory")
            elif type(value) is float:
                if not _same_number(row[name], value):
                    raise ValueError("predictive summary numeric algebra does not reproduce")
            elif row[name] != value:
                raise ValueError("predictive summary counts/warning/gate do not reproduce")
    return tuple(dict(row) for row in rows)


def reconstruct_predictive_scenario_state(
    *,
    predictive_rows: Sequence[Mapping[str, object]],
    predictive_summary_rows: Sequence[Mapping[str, object]],
) -> PredictiveScenarioState:
    if not predictive_rows or not predictive_summary_rows:
        return PredictiveScenarioState(False, False, False, False, False)
    complete_finite = all(
        row["fit_succeeded"] is True
        and row["diagnostic_available"] is True
        and row["standardized_residual_nonfinite"] is False
        and row["standardized_residual"] is not None
        for row in predictive_rows
    ) and all(
        row["diagnostic_count"] == row["replicate_count"]
        and row["failed_fit_count"] == 0
        and row["mean_standardized_residual"] is not None
        and row["stouffer_z"] is not None
        and row["ks_statistic"] is not None
        and row["raw_p"] is not None
        and row["holm_adjusted_p"] is not None
        for row in predictive_summary_rows
    )
    finite_rule_fired = any(
        (
            row["holm_adjusted_p"] is not None
            and float(cast(float, row["holm_adjusted_p"]))
            < cast(float, FROZEN_GATE_CONFIG["pit_familywise_alpha"])
        )
        or (row["stouffer_z"] is not None and abs(float(cast(float, row["stouffer_z"]))) > 3.0)
        for row in predictive_summary_rows
    )
    forced_warning = not complete_finite
    scientific_warning_available = complete_finite and finite_rule_fired
    return PredictiveScenarioState(
        predictive_complete_finite=complete_finite,
        predictive_pass=complete_finite and not finite_rule_fired,
        finite_rule_fired=finite_rule_fired,
        scientific_warning_available=scientific_warning_available,
        forced_warning=forced_warning,
    )


def _is_true(evidence: Mapping[str, object], key: str) -> bool:
    return evidence.get(key) is True


def _required_available(evidence: Mapping[str, object]) -> bool:
    return all(
        _is_true(evidence, key)
        for key in ("schema_valid", "fit_available", "predictive_available", "plugin_available")
    )


def _contract_reason_for_scenario(scenario_id: str) -> str:
    return next(
        reason
        for reason in SCENARIO_LOCAL_REASONS[scenario_id]
        if reason.startswith("contract_failure:")
    )


def _validate_scenario_evidence(scenario_id: str, evidence: Mapping[str, object]) -> str | None:
    contract_reason = _contract_reason_for_scenario(scenario_id)
    if set(evidence) != SCENARIO_EVIDENCE_FIELDS[scenario_id]:
        return contract_reason
    bool_fields = {
        name
        for name in evidence
        if name
        not in {
            "plugin_rank",
            "plugin_condition",
            "decidable_intervals",
            "zero_exclusions",
            "alignment_correlation",
            "alignment_pairs",
            "alignment_wins",
            "equal_p",
            "equal_refits",
            "equal_status_rows",
        }
    }
    if any(type(evidence[name]) is not bool for name in bool_fields):
        return contract_reason
    for name in (
        "plugin_rank",
        "decidable_intervals",
        "zero_exclusions",
        "alignment_pairs",
        "alignment_wins",
        "equal_refits",
    ):
        if name in evidence and type(evidence[name]) is not int:
            return contract_reason
    for name in ("plugin_condition", "alignment_correlation", "equal_p"):
        if name in evidence and (
            type(evidence[name]) not in (int, float)
            or not isfinite(float(cast(float, evidence[name])))
        ):
            return contract_reason
    if "plugin_rank" in evidence and evidence["plugin_rank"] != 3:
        return contract_reason
    if "plugin_condition" in evidence and float(cast(float, evidence["plugin_condition"])) < 1.0:
        return contract_reason
    if (
        "decidable_intervals" in evidence
        and not 0 <= cast(int, evidence["decidable_intervals"]) <= 24
    ):
        return contract_reason
    if "zero_exclusions" in evidence and not 0 <= cast(int, evidence["zero_exclusions"]) <= 24:
        return contract_reason
    if "alignment_pairs" in evidence and not 0 <= cast(int, evidence["alignment_pairs"]) <= 24:
        return contract_reason
    if "alignment_wins" in evidence and not 0 <= cast(int, evidence["alignment_wins"]) <= 24:
        return contract_reason
    if "equal_p" in evidence and not 0.0 <= float(cast(float, evidence["equal_p"])) <= 1.0:
        return contract_reason
    if "equal_status_rows" in evidence:
        status_rows = evidence["equal_status_rows"]
        if not isinstance(status_rows, Sequence) or isinstance(status_rows, (str, bytes)):
            return contract_reason
        try:
            validate_equal_emission_status_rows(cast(Sequence[Mapping[str, object]], status_rows))
        except TypeError, ValueError:
            return contract_reason
    if evidence.get("fit_available") is False and any(
        evidence.get(name) is True
        for name in ("convergence_pass", "coverage_pass", "recovery_pass", "identified")
    ):
        return contract_reason
    if evidence.get("predictive_available") is False and (
        evidence.get("predictive_pass") is True or evidence.get("warning_available") is True
    ):
        return contract_reason
    if evidence.get("plugin_available") is False and (
        evidence.get("plugin_rank") is not None or evidence.get("plugin_condition") is not None
    ):
        return contract_reason
    return None


def reduce_scenario(scenario_id: str, evidence: Mapping[str, object]) -> str:
    if scenario_id not in SCENARIO_IDS:
        return "contract_failure:unknown_scenario"
    evidence_failure = _validate_scenario_evidence(scenario_id, evidence)
    if evidence_failure is not None:
        return evidence_failure
    if scenario_id in SCENARIO_IDS[:2]:
        if not all(
            _is_true(evidence, key)
            for key in (
                "schema_valid",
                "design_pass",
                "fit_available",
                "convergence_pass",
                "coverage_pass",
                "recovery_pass",
            )
        ):
            suffix = (
                "process_oracle_failed"
                if scenario_id == SCENARIO_IDS[0]
                else "observation_oracle_failed"
            )
            return f"contract_failure:{suffix}"
        return "pass"
    if scenario_id == "dense_count_exact_model":
        if not all(
            _is_true(evidence, key)
            for key in ("schema_valid", "fit_available", "predictive_available", "plugin_available")
        ):
            return "contract_failure:dense_evidence_invalid"
        if not all(
            _is_true(evidence, key)
            for key in (
                "convergence_pass",
                "coverage_pass",
                "recovery_pass",
                "predictive_pass",
                "identified",
            )
        ):
            return "confounding:dense_joint_failed"
        return "pass"
    if scenario_id == "structured_imperfect_effort":
        condition = evidence.get("plugin_condition")
        if (
            not all(
                _is_true(evidence, key)
                for key in (
                    "schema_valid",
                    "fit_available",
                    "convergence_pass",
                    "coverage_pass",
                    "predictive_available",
                    "predictive_pass",
                    "plugin_available",
                )
            )
            or type(evidence.get("plugin_rank")) is not int
            or cast(int, evidence["plugin_rank"]) < 3
            or type(condition) not in (int, float)
            or not isfinite(float(cast(float, condition)))
            or float(cast(float, condition)) >= 1e8
        ):
            return "contract_failure:structured_not_calibrated"
        if not _is_true(evidence, "identified"):
            return "confounding:structured_estimand_unidentified"
        if not _is_true(evidence, "recovery_pass"):
            return "structured_limitation:structured_precision_recovery_failed"
        return "pass"
    if scenario_id == "sparse_expected_failure":
        if not all(
            _is_true(evidence, key)
            for key in (
                "schema_valid",
                "fit_available",
                "predictive_available",
                "plugin_available",
                "predictive_pass",
                "sparse_coverage_pass",
                "sparse_width_pass",
            )
        ):
            return "contract_failure:sparse_honesty_failed"
        return "pass"
    if scenario_id == "zero_driver_effect_negative_control":
        if (
            not _required_available(evidence)
            or not _is_true(evidence, "predictive_pass")
            or evidence.get("decidable_intervals") != 24
        ):
            return "contract_failure:zero_driver_unavailable"
        exclusions = evidence.get("zero_exclusions")
        if type(exclusions) is not int or not 0 <= exclusions <= 24:
            return "contract_failure:zero_driver_unavailable"
        return "pass" if exclusions <= 6 else "confounding:zero_driver_false_signal"
    if scenario_id == "permuted_arrival_alignment_stress":
        correlation = evidence.get("alignment_correlation")
        if (
            not _required_available(evidence)
            or type(correlation) not in (int, float)
            or not isfinite(float(cast(float, correlation)))
            or abs(float(cast(float, correlation))) > 0.25
            or evidence.get("alignment_pairs") != 24
        ):
            return "contract_failure:alignment_contract_or_availability_failed"
        if not _is_true(evidence, "warning_available") or _is_true(evidence, "warning_forced"):
            return "contract_failure:alignment_silent_misspecification"
        wins = evidence.get("alignment_wins")
        if type(wins) is not int or not 0 <= wins <= 24:
            return "contract_failure:alignment_contract_or_availability_failed"
        return "pass" if wins >= 22 else "confounding:arrival_alignment_not_discriminated"
    if scenario_id == "no_emission_contrast_negative_control":
        p_value = evidence.get("equal_p")
        if (
            not _is_true(evidence, "schema_valid")
            or not _is_true(evidence, "fit_available")
            or not _is_true(evidence, "bootstrap_available")
            or evidence.get("equal_refits") != 199
            or type(p_value) not in (int, float)
            or not isfinite(float(cast(float, p_value)))
            or float(cast(float, p_value)) < 0.05
        ):
            return "contract_failure:equal_emission_control_failed"
        return "pass"
    stress_reason = {
        "informative_dropout_misspecification_stress": "informative_dropout",
        "goal018_continuous_abundance_stress": "continuous_abundance",
        "spatial_frailty_stress": "spatial_frailty",
    }[scenario_id]
    if not _required_available(evidence):
        return f"contract_failure:{stress_reason}_unavailable"
    if scenario_id == "goal018_continuous_abundance_stress":
        return (
            "pass"
            if _is_true(evidence, "warning_available") and not _is_true(evidence, "warning_forced")
            else ("contract_failure:continuous_abundance_silent_misspecification")
        )
    if _is_true(evidence, "warning_forced") or (
        _is_true(evidence, "narrow_wrong") and not _is_true(evidence, "warning_available")
    ):
        return f"contract_failure:{stress_reason}_silent_misspecification"
    return "pass"


def reduce_recommendation(
    scenario_results: Mapping[str, str],
    *,
    global_contract_pass: bool = True,
    latent_rows: Sequence[Mapping[str, object]] | None = None,
) -> RecommendationResult:
    del latent_rows
    if (
        set(scenario_results) != set(SCENARIO_IDS)
        or not global_contract_pass
        or any(
            type(scenario_results[scenario_id]) is not str
            or scenario_results[scenario_id] not in SCENARIO_LOCAL_REASONS[scenario_id]
            for scenario_id in SCENARIO_IDS
        )
    ):
        return RecommendationResult(
            1,
            RECOMMENDATION_CLASSES[0],
            "incomplete_or_contradictory_decision_vector",
            ("incomplete_or_contradictory_decision_vector",),
        )
    values = tuple(scenario_results[scenario_id] for scenario_id in SCENARIO_IDS)
    reasons = tuple(value for value in values if value != "pass")
    contract_reasons = tuple(value for value in reasons if value.startswith("contract_failure:"))
    if contract_reasons:
        return RecommendationResult(1, RECOMMENDATION_CLASSES[0], contract_reasons[0], reasons)
    confounding_reasons = tuple(value for value in reasons if value.startswith("confounding:"))
    if confounding_reasons:
        return RecommendationResult(2, RECOMMENDATION_CLASSES[1], confounding_reasons[0], reasons)
    if (
        values[2] == "pass"
        and values[3].startswith("structured_limitation:")
        and all(value == "pass" for value in values[:3] + values[4:])
    ):
        return RecommendationResult(
            3, RECOMMENDATION_CLASSES[2], "structured_precision_recovery_failed", reasons
        )
    if all(value == "pass" for value in values):
        return RecommendationResult(4, RECOMMENDATION_CLASSES[3], "all_required_gates_pass", ())
    return RecommendationResult(
        1, RECOMMENDATION_CLASSES[0], "incomplete_or_contradictory_decision_vector", reasons
    )


def _equal_control_evidence(fit_rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    rows = tuple(
        row
        for row in fit_rows
        if row["scenario_id"] == "no_emission_contrast_negative_control"
        and row["split_id"] == "holdout"
    )
    observed = {
        cast(str, row["fit_variant"]): row for row in rows if row["fit_scope"] == "scenario_shared"
    }
    if set(observed) != {"equal_rate", "ordered_emission"} or len(observed) != 2:
        raise ValueError("equal control requires one complete observed shared pair")
    pairs: dict[int, dict[str, Mapping[str, object]]] = {}
    for row in rows:
        if row["fit_scope"] != "bootstrap_shared":
            continue
        index = cast(int, row["fit_index"])
        variant = cast(str, row["fit_variant"])
        if variant in pairs.setdefault(index, {}):
            raise ValueError("equal control contains a duplicate bootstrap fit")
        pairs[index][variant] = row
    if tuple(sorted(pairs)) != tuple(range(199)) or any(
        set(pair) != {"equal_rate", "ordered_emission"} for pair in pairs.values()
    ):
        raise ValueError("equal control requires 199 complete bootstrap fit pairs")
    observed_available = all(row["fit_succeeded"] is True for row in observed.values())
    observed_statistic = (
        2.0
        * (
            float(cast(float, observed["ordered_emission"]["log_likelihood"]))
            - float(cast(float, observed["equal_rate"]["log_likelihood"]))
        )
        if observed_available
        else None
    )
    statistics: list[float] = []
    for pair in pairs.values():
        if all(row["fit_succeeded"] is True for row in pair.values()):
            statistics.append(
                2.0
                * (
                    float(cast(float, pair["ordered_emission"]["log_likelihood"]))
                    - float(cast(float, pair["equal_rate"]["log_likelihood"]))
                )
            )
    converged = len(statistics)
    event_count = (
        sum(value >= observed_statistic for value in statistics)
        if observed_statistic is not None and converged == 199
        else None
    )
    p_value = (1 + event_count) / 200.0 if event_count is not None else None
    return {
        "attempted_replicates": 24,
        "evaluable_replicates": 24 if observed_available else 0,
        "test_statistic": observed_statistic,
        "bootstrap_replicates": 199,
        "bootstrap_converged_count": converged,
        "bootstrap_failed_count": 199 - converged,
        "event_count": event_count,
        "p_value": p_value,
    }


def _zero_arrival_control_evidence(
    fit_rows: Sequence[Mapping[str, object]],
    recovery_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    zero_fits = {
        cast(int, row["fit_index"]): row
        for row in fit_rows
        if row["scenario_id"] == "zero_driver_effect_negative_control"
        and row["split_id"] == "holdout"
        and row["fit_variant"] == "canonical"
    }
    zero_rows = {
        cast(int, row["replicate_id"]): row
        for row in recovery_rows
        if row["scenario_id"] == "zero_driver_effect_negative_control"
        and row["split_id"] == "holdout"
        and row["parameter_id"] == "beta_driver"
    }
    if set(zero_fits) != set(range(24)) or set(zero_rows) != set(range(24)):
        raise ValueError("zero control requires the complete 24-attempt holdout frame")
    intervals: list[tuple[float | None, float | None] | None] = []
    for index in range(24):
        fit = zero_fits[index]
        row = zero_rows[index]
        intervals.append(
            (
                cast(float, row["interval_lower"]),
                cast(float, row["interval_upper"]),
            )
            if fit["fit_succeeded"] is True
            and row["profile_two_sided"] is True
            and row["interval_lower"] is not None
            and row["interval_upper"] is not None
            else None
        )
    zero_evaluable = sum(interval is not None for interval in intervals)
    zero_events = sum(
        interval is not None
        and interval_excludes_zero(float(cast(float, interval[0])), float(cast(float, interval[1])))
        for interval in intervals
    )

    arrival_rows = tuple(
        row
        for row in fit_rows
        if row["scenario_id"] == "permuted_arrival_alignment_stress"
        and row["split_id"] == "holdout"
    )
    fit_ids, score_ids = authoritative_alignment_frame_cell_ids()
    validate_arrival_fit_pairs(
        arrival_rows,
        fit_cell_ids=fit_ids,
        score_cell_ids=score_ids,
        required_split_id="holdout",
    )
    arrival_pairs: dict[int, dict[str, Mapping[str, object]]] = {}
    for row in arrival_rows:
        arrival_pairs.setdefault(cast(int, row["fit_index"]), {})[cast(str, row["fit_variant"])] = (
            row
        )
    arrival_evaluable = sum(
        pair["correct_alignment"]["fit_succeeded"] is True
        and pair["permuted_alignment"]["fit_succeeded"] is True
        for pair in arrival_pairs.values()
    )
    arrival_wins = sum(
        pair["correct_alignment"]["fit_succeeded"] is True
        and pair["permuted_alignment"]["fit_succeeded"] is True
        and float(cast(float, pair["correct_alignment"]["heldout_log_score"]))
        > float(cast(float, pair["permuted_alignment"]["heldout_log_score"]))
        for pair in arrival_pairs.values()
    )
    return {
        "zero_attempted": 24,
        "zero_evaluable": zero_evaluable,
        "zero_event_count": zero_events,
        "arrival_attempted": 24,
        "arrival_evaluable": arrival_evaluable,
        "arrival_event_count": arrival_wins,
        "alignment_correlation": authoritative_alignment_correlation(),
    }


def _control_decision_rows_from_results(
    scenario_results: Mapping[str, str],
    *,
    zero_arrival: Mapping[str, object],
    equal: Mapping[str, object],
) -> tuple[dict[str, object], ...]:
    recommendation = reduce_recommendation(scenario_results)

    def empty_row() -> dict[str, object]:
        row: dict[str, object] = {name: None for name in CONTROL_DECISION_SUMMARY_HEADER}
        row["silent_misspecification_failure"] = False
        row["transportability_class"] = recommendation.transportability_class
        return row

    rows: list[dict[str, object]] = []
    for scenario_id in SCENARIO_IDS:
        reason = scenario_results[scenario_id]
        row = empty_row()
        row.update(
            decision_row_id=f"scenario_gate|{scenario_id}",
            decision_row_type="scenario_gate",
            scenario_id=scenario_id,
            gate_family=SCENARIO_GATE_FAMILY[scenario_id],
            gate_result="pass" if reason == "pass" else "fail",
            silent_misspecification_failure=reason.endswith("_silent_misspecification"),
            interpretation=reason,
        )
        if scenario_id == "zero_driver_effect_negative_control":
            row.update(
                attempted_replicates=zero_arrival["zero_attempted"],
                evaluable_replicates=zero_arrival["zero_evaluable"],
                event_count=zero_arrival["zero_event_count"],
                acceptance_lower_count=0,
                acceptance_upper_count=6,
            )
        elif scenario_id == "permuted_arrival_alignment_stress":
            row.update(
                alignment_correlation=zero_arrival["alignment_correlation"],
                attempted_replicates=zero_arrival["arrival_attempted"],
                evaluable_replicates=zero_arrival["arrival_evaluable"],
                event_count=zero_arrival["arrival_event_count"],
                acceptance_lower_count=22,
                acceptance_upper_count=24,
            )
        elif scenario_id == "no_emission_contrast_negative_control":
            row.update(equal)
        rows.append(row)
    for status in EQUAL_EMISSION_STATUS_ROWS:
        row = empty_row()
        parameter_id = status["parameter_id"]
        row.update(
            decision_row_id=(
                f"parameter_status|no_emission_contrast_negative_control|{parameter_id}"
            ),
            decision_row_type="parameter_status",
            scenario_id="no_emission_contrast_negative_control",
            parameter_id=parameter_id,
            structural_status=status["structural_status"],
            practical_status=status["practical_status"],
            gate_family="parameter_status",
            gate_result="diagnostic",
            interpretation="equal_emission_parameter_status",
        )
        rows.append(row)
    final = empty_row()
    final.update(
        decision_row_id="final_decision",
        decision_row_type="final_decision",
        gate_family="final_recommendation",
        gate_result="pass" if recommendation.recommendation_rank == 4 else "fail",
        recommendation_rank=recommendation.recommendation_rank,
        recommendation_class=recommendation.recommendation_class,
        interpretation=recommendation.reason,
    )
    rows.append(final)
    return tuple(sorted(rows, key=lambda row: cast(str, row["decision_row_id"])))


def _reconcile_complete_science_tables(
    *,
    fit_rows: Sequence[Mapping[str, object]],
    recovery_rows: Sequence[Mapping[str, object]],
    profile_rows: Sequence[Mapping[str, object]],
    coverage_rows: Sequence[Mapping[str, object]],
    latent_rows: Sequence[Mapping[str, object]],
    predictive_rows: Sequence[Mapping[str, object]],
    predictive_summary_rows: Sequence[Mapping[str, object]],
) -> tuple[
    tuple[dict[str, object], ...],
    dict[str, str],
    RecommendationResult,
    tuple[dict[str, object], ...],
    dict[str, PredictiveScenarioState],
]:
    frames = science_identity_frames()
    fits, designs = _partition_fit_execution_evidence(fit_rows)
    fit_keys = tuple(
        tuple(
            row[name]
            for name in ("scenario_id", "split_id", "fit_scope", "fit_variant", "fit_index")
        )
        for row in fits
    )
    if fit_keys != frames["fit"]:
        raise ValueError("complete science bundle fit identity frame is missing, extra, or foreign")
    design_keys = tuple((*_fit_result_identity(row), row["design_kind"]) for row in designs)
    expected_design_keys = _expected_design_identity_frame(fits)
    if design_keys != expected_design_keys:
        raise ValueError(
            "complete science bundle design identity frame is missing, duplicate, or foreign"
        )
    validate_fit_design_state_machine(fits, designs)
    fit_lookup = {
        (
            row["scenario_id"],
            row["split_id"],
            row["fit_scope"],
            row["fit_variant"],
            row["fit_index"],
        ): row
        for row in fits
    }

    recovery = validate_replicate_recovery_rows(recovery_rows)
    recovery_keys = tuple(
        tuple(
            row[name]
            for name in ("scenario_id", "split_id", "replicate_id", "fit_variant", "parameter_id")
        )
        for row in recovery
    )
    if recovery_keys != frames["recovery"]:
        raise ValueError("complete science bundle recovery identity frame is incomplete")
    profiles = (
        validate_identifiability_profile_rows(profile_rows, fit_rows=fits) if profile_rows else ()
    )
    profile_group_keys = {
        tuple(
            row[name]
            for name in ("scenario_id", "split_id", "replicate_id", "fit_variant", "parameter_id")
        )
        for row in profiles
    }
    successful_profile_keys = {
        key
        for key in recovery_keys
        if fit_lookup[(key[0], key[1], "replicate", key[3], key[2])]["fit_succeeded"] is True
    }
    if profile_group_keys != successful_profile_keys:
        raise ValueError("complete science bundle profile groups do not match successful fits")
    validate_recovery_profile_reconciliation(recovery, profiles, fits)

    coverage = validate_coverage_summary_rows(coverage_rows, recovery_rows=recovery, fit_rows=fits)
    coverage_keys = tuple(
        tuple(row[name] for name in ("scenario_id", "split_id", "fit_variant", "parameter_id"))
        for row in coverage
    )
    if coverage_keys != frames["coverage"]:
        raise ValueError("complete science bundle coverage identity frame is incomplete")

    latent_groups: dict[tuple[object, ...], list[Mapping[str, object]]] = {}
    for row in latent_rows:
        key = tuple(
            row.get(name) for name in ("scenario_id", "split_id", "replicate_id", "fit_variant")
        )
        latent_groups.setdefault(key, []).append(row)
    if tuple(latent_groups) != frames["latent"]:
        raise ValueError("complete science bundle latent identity frame is incomplete")
    for key, group in latent_groups.items():
        validate_latent_diagnostic_rows(group)
        scenario_id = cast(str, key[0])
        registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
        fit = fit_lookup[(key[0], key[1], "replicate", key[3], key[2])]
        expected_status = fit["fit_succeeded"] if registry.latent_time_applicable else None
        if any(row["fit_succeeded"] is not expected_status for row in group):
            raise ValueError("latent diagnostic status does not reconcile to its exact fit")

    predictive_groups: dict[tuple[object, ...], list[Mapping[str, object]]] = {}
    for row in predictive_rows:
        key = tuple(
            row.get(name) for name in ("scenario_id", "split_id", "replicate_id", "fit_variant")
        )
        predictive_groups.setdefault(key, []).append(row)
    if tuple(predictive_groups) != frames["predictive"]:
        raise ValueError("complete science bundle predictive identity frame is incomplete")
    for key, group in predictive_groups.items():
        validate_predictive_replicate_rows(group)
        scope = (
            "scenario_shared" if key[0] == "no_emission_contrast_negative_control" else "replicate"
        )
        fit_index = 0 if scope == "scenario_shared" else key[2]
        fit = fit_lookup[(key[0], key[1], scope, key[3], fit_index)]
        if any(row["fit_succeeded"] is not fit["fit_succeeded"] for row in group):
            raise ValueError("predictive diagnostic status does not reconcile to its exact fit")

    summary_groups: dict[tuple[object, ...], list[Mapping[str, object]]] = {}
    for row in predictive_summary_rows:
        key = tuple(row.get(name) for name in ("scenario_id", "split_id", "fit_variant"))
        summary_groups.setdefault(key, []).append(row)
    if tuple(summary_groups) != frames["predictive_summary"]:
        raise ValueError("complete science bundle predictive summary frame is incomplete")
    for key, group in summary_groups.items():
        source = tuple(
            row
            for identity, rows_for_identity in predictive_groups.items()
            if (identity[0], identity[1], identity[3]) == key
            for row in rows_for_identity
        )
        validate_predictive_summary_rows(group, predictive_rows=source, fit_rows=fits)

    zero_arrival = _zero_arrival_control_evidence(fits, recovery)
    equal = _equal_control_evidence(fits)
    coverage_by_scenario = {
        scenario_id: tuple(
            row
            for row in coverage
            if row["scenario_id"] == scenario_id and row["split_id"] == "holdout"
        )
        for scenario_id in SCENARIO_IDS
    }
    predictive_by_scenario = {
        scenario_id: tuple(
            row
            for row in predictive_summary_rows
            if row["scenario_id"] == scenario_id and row["split_id"] == "holdout"
        )
        for scenario_id in SCENARIO_IDS
    }
    design_by_scenario = {
        scenario_id: tuple(
            row
            for row in designs
            if row["scenario_id"] == scenario_id and row["split_id"] == "holdout"
        )
        for scenario_id in SCENARIO_IDS
    }

    def required_fit_available(scenario_id: str) -> bool:
        registry = SCENARIO_EVIDENCE_REGISTRY[SCENARIO_IDS.index(scenario_id)]
        if registry.fit_scope == "scenario_shared":
            return cast(int, equal["evaluable_replicates"]) == 24
        return all(
            row["fit_succeeded"] is True
            for row in fits
            if row["scenario_id"] == scenario_id and row["split_id"] == "holdout"
        )

    predictive_state_by_scenario = {
        scenario_id: reconstruct_predictive_scenario_state(
            predictive_rows=tuple(
                row
                for identity, group in predictive_groups.items()
                if identity[0] == scenario_id and identity[1] == "holdout"
                for row in group
            ),
            predictive_summary_rows=predictive_by_scenario[scenario_id],
        )
        for scenario_id in SCENARIO_IDS
    }

    scenario_results: dict[str, str] = {}
    structured_width = next(
        cast(float, row["median_interval_width"])
        for row in coverage_by_scenario["structured_imperfect_effort"]
        if row["parameter_id"] == "beta_driver"
    )
    sparse_width = next(
        cast(float, row["median_interval_width"])
        for row in coverage_by_scenario["sparse_expected_failure"]
        if row["parameter_id"] == "beta_driver"
    )
    for scenario_id in SCENARIO_IDS:
        fit_available = required_fit_available(scenario_id)
        predictive_state = predictive_state_by_scenario[scenario_id]
        prediction_available = predictive_state.predictive_complete_finite
        prediction_pass = predictive_state.predictive_pass
        warning_available = predictive_state.scientific_warning_available
        warning_forced = predictive_state.forced_warning
        holdout_coverage = coverage_by_scenario[scenario_id]
        convergence_limit = cast(Mapping[str, float], FROZEN_GATE_CONFIG["convergence_limits"]).get(
            scenario_id
        )
        convergence_pass = bool(holdout_coverage) and (
            convergence_limit is None
            or all(
                cast(int, row["converged_count"]) / cast(int, row["replicate_count"])
                >= convergence_limit
                for row in holdout_coverage
            )
        )
        coverage_pass = bool(holdout_coverage) and all(
            row["gate_result"] == "pass" for row in holdout_coverage
        )
        identified = fit_available and all(
            row["profile_two_sided"] is True
            for row in recovery
            if row["scenario_id"] == scenario_id and row["split_id"] == "holdout"
        )
        scenario_designs = design_by_scenario[scenario_id]
        potential_rows = tuple(row for row in scenario_designs if row["design_kind"] == "potential")
        potential_available = bool(potential_rows) and all(
            row["design_passed"] is True for row in potential_rows
        )
        fit_available = fit_available and potential_available
        design_pass = bool(scenario_designs) and all(
            row["design_passed"] is True for row in scenario_designs
        )
        plugin_rows = tuple(row for row in scenario_designs if row["design_kind"] == "plugin")
        plugin_available = bool(plugin_rows) and all(
            row["design_passed"] is True for row in plugin_rows
        )
        plugin_rank = (
            min(cast(int, row["design_rank"]) for row in plugin_rows) if plugin_available else None
        )
        plugin_condition = (
            max(cast(float, row["design_condition_number"]) for row in plugin_rows)
            if plugin_available
            else None
        )
        evidence: dict[str, object]
        if scenario_id in SCENARIO_IDS[:2]:
            evidence = {
                "schema_valid": True,
                "design_pass": design_pass,
                "fit_available": fit_available,
                "convergence_pass": convergence_pass,
                "coverage_pass": coverage_pass,
                "recovery_pass": coverage_pass,
            }
        elif scenario_id == "dense_count_exact_model":
            evidence = {
                "schema_valid": True,
                "fit_available": fit_available,
                "predictive_available": prediction_available,
                "plugin_available": plugin_available,
                "convergence_pass": convergence_pass,
                "coverage_pass": coverage_pass,
                "recovery_pass": coverage_pass,
                "predictive_pass": prediction_pass,
                "identified": identified,
            }
        elif scenario_id == "structured_imperfect_effort":
            evidence = {
                "schema_valid": True,
                "fit_available": fit_available,
                "predictive_available": prediction_available,
                "plugin_available": plugin_available,
                "convergence_pass": convergence_pass,
                "coverage_pass": coverage_pass,
                "recovery_pass": coverage_pass,
                "predictive_pass": prediction_pass,
                "identified": identified,
                "plugin_rank": plugin_rank,
                "plugin_condition": plugin_condition,
            }
        elif scenario_id == "sparse_expected_failure":
            sparse_row = next(
                row for row in holdout_coverage if row["parameter_id"] == "beta_driver"
            )
            evidence = {
                "schema_valid": True,
                "fit_available": fit_available,
                "predictive_available": prediction_available,
                "plugin_available": plugin_available,
                "predictive_pass": prediction_pass,
                "sparse_coverage_pass": sparse_row["gate_result"] == "pass",
                "sparse_width_pass": sparse_width >= structured_width,
            }
        elif scenario_id == "zero_driver_effect_negative_control":
            evidence = {
                "schema_valid": True,
                "fit_available": fit_available,
                "predictive_available": prediction_available,
                "predictive_pass": prediction_pass,
                "plugin_available": plugin_available,
                "decidable_intervals": zero_arrival["zero_evaluable"],
                "zero_exclusions": zero_arrival["zero_event_count"],
            }
        elif scenario_id == "permuted_arrival_alignment_stress":
            evidence = {
                "schema_valid": True,
                "fit_available": fit_available,
                "predictive_available": prediction_available,
                "plugin_available": plugin_available,
                "warning_available": warning_available,
                "warning_forced": warning_forced,
                "alignment_correlation": zero_arrival["alignment_correlation"],
                "alignment_pairs": zero_arrival["arrival_evaluable"],
                "alignment_wins": zero_arrival["arrival_event_count"],
            }
        elif scenario_id == "no_emission_contrast_negative_control":
            evidence = {
                "schema_valid": True,
                "fit_available": fit_available and design_pass,
                "bootstrap_available": equal["bootstrap_failed_count"] == 0,
                "equal_p": equal["p_value"],
                "equal_refits": equal["bootstrap_converged_count"],
                "equal_status_rows": EQUAL_EMISSION_STATUS_ROWS,
            }
        else:
            known_truth = scenario_id != "goal018_continuous_abundance_stress"
            narrow_wrong = known_truth and any(
                row["converged"] is True
                and row["profile_two_sided"] is True
                and row["truth_in_interval"] is False
                and cast(float, row["interval_width"])
                <= cast(Mapping[str, float], FROZEN_GATE_CONFIG["profile_width_limits"])[
                    cast(str, row["parameter_id"])
                ]
                for row in recovery
                if row["scenario_id"] == scenario_id and row["split_id"] == "holdout"
            )
            evidence = {
                "schema_valid": True,
                "fit_available": fit_available,
                "predictive_available": prediction_available,
                "plugin_available": plugin_available,
                "warning_available": warning_available,
                "warning_forced": warning_forced,
            }
            if known_truth:
                evidence["narrow_wrong"] = narrow_wrong
        scenario_results[scenario_id] = reduce_scenario(scenario_id, evidence)
    controls = _control_decision_rows_from_results(
        scenario_results, zero_arrival=zero_arrival, equal=equal
    )
    return (
        controls,
        scenario_results,
        reduce_recommendation(scenario_results),
        designs,
        predictive_state_by_scenario,
    )


def recompute_control_decision_rows(
    *,
    fit_rows: Sequence[Mapping[str, object]],
    recovery_rows: Sequence[Mapping[str, object]],
    profile_rows: Sequence[Mapping[str, object]],
    coverage_rows: Sequence[Mapping[str, object]],
    latent_rows: Sequence[Mapping[str, object]],
    predictive_rows: Sequence[Mapping[str, object]],
    predictive_summary_rows: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], ...]:
    controls, _, _, _, _ = _reconcile_complete_science_tables(
        fit_rows=fit_rows,
        recovery_rows=recovery_rows,
        profile_rows=profile_rows,
        coverage_rows=coverage_rows,
        latent_rows=latent_rows,
        predictive_rows=predictive_rows,
        predictive_summary_rows=predictive_summary_rows,
    )
    return controls


def validate_science_bundle(
    *,
    fit_rows: Sequence[Mapping[str, object]],
    recovery_rows: Sequence[Mapping[str, object]],
    profile_rows: Sequence[Mapping[str, object]],
    coverage_rows: Sequence[Mapping[str, object]],
    latent_rows: Sequence[Mapping[str, object]],
    predictive_rows: Sequence[Mapping[str, object]],
    predictive_summary_rows: Sequence[Mapping[str, object]],
    control_rows: Sequence[Mapping[str, object]],
) -> ValidatedScienceBundle:
    (
        expected,
        scenario_results,
        recommendation,
        designs,
        predictive_states,
    ) = _reconcile_complete_science_tables(
        fit_rows=fit_rows,
        recovery_rows=recovery_rows,
        profile_rows=profile_rows,
        coverage_rows=coverage_rows,
        latent_rows=latent_rows,
        predictive_rows=predictive_rows,
        predictive_summary_rows=predictive_summary_rows,
    )
    validated_controls = validate_control_decision_rows(control_rows)
    if validated_controls != expected:
        raise ValueError(
            "control decisions do not equal the complete science-bundle reconstruction"
        )
    return ValidatedScienceBundle(
        tuple((scenario_id, scenario_results[scenario_id]) for scenario_id in SCENARIO_IDS),
        expected,
        recommendation,
        designs,
        sha256(canonical_json_bytes({"rows": list(designs)})).hexdigest(),
        tuple((scenario_id, predictive_states[scenario_id]) for scenario_id in SCENARIO_IDS),
        _VALIDATED_SCIENCE_BUNDLE_TOKEN,
    )


def canonical_json_bytes(payload: Mapping[str, object]) -> bytes:
    return (
        dumps(
            dict(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
        )
        + "\n"
    ).encode("ascii")


def _file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _digest_lines(entries: Sequence[tuple[str, str]]) -> str:
    return sha256(
        "".join(f"{digest}  {path}\n" for path, digest in entries).encode("utf-8")
    ).hexdigest()


def expected_artifact_manifest() -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "path": path,
            "role": "visual" if path.startswith("visuals/") else "root",
            "required": True,
            "sha256": None,
        }
        for path in ARTIFACT_PATHS
    )


def validate_expected_artifact_manifest(entries: Sequence[Mapping[str, object]]) -> None:
    if tuple(dict(entry) for entry in entries) != expected_artifact_manifest():
        raise ValueError("artifact_manifest must be the literal ordered 22-entry registry")


def validate_source_provenance_document(payload: Mapping[str, object]) -> None:
    document = _require_exact_mapping(payload, SOURCE_PROVENANCE_KEYS, name="source provenance")
    expected_counts = {
        "landscape_cell_count": 6048,
        "passable_cell_count": 5225,
        "water_cell_count": 823,
        "final_colonized_passable_count": 4605,
        "finite_prey_extirpation_count": 4289,
    }
    if (
        document["schema_version"] != GENERATED_ARTIFACT_SCHEMA_VERSION
        or document["source_commit"] != PINNED_COMMIT
        or document["parameter_set_id"] != "balanced_corridor_detour_v2"
        or document["source_apis"]
        != [
            "spatext.synth.medium.landscape.build_synth_medium_landscape",
            "spatext.synth.medium.spread_impact.build_synth_medium_spread_impact_review_pack",
        ]
        or document["passed"] is not True
    ):
        raise ValueError("source provenance literals do not match external authority")
    for name in ("expected_counts", "reconciled_counts"):
        counts = _require_exact_mapping(document[name], SOURCE_COUNT_KEYS, name=name)
        if dict(counts) != expected_counts or any(
            type(value) is not int for value in counts.values()
        ):
            raise ValueError("source provenance counts do not match literal authority")
    if (
        _require_sha256(document["landscape_sha256"], name="landscape_sha256")
        != "53900537f590feb14c76a6e3936a4ec1047dd59b503b2bb3236c015d2859403a"
        or _require_sha256(document["arrival_sha256"], name="arrival_sha256")
        != "5f05f4306cda88cdf38027fdfe030ff05956cabaea848d6a7454c717c668f4ba"
    ):
        raise ValueError("source provenance hashes do not match accepted source authority")


def _runtime_task_durations(
    measured_units: Sequence[Mapping[str, object]],
    equal_bootstrap_unit: Mapping[str, object],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    calibration: list[dict[str, object]] = []
    holdout: list[dict[str, object]] = []
    for unit in measured_units:
        scenario_id = cast(str, unit["scenario_id"])
        duration = float(cast(float, unit["measured_duration_seconds"]))
        for replicate_id in range(cast(int, unit["calibration_repeat_count"])):
            calibration.append(
                {
                    "task_id": (f"calibration|scenario={scenario_id}|replicate={replicate_id:04d}"),
                    "duration_seconds": duration,
                }
            )
        if scenario_id == "no_emission_contrast_negative_control":
            holdout.append(
                {
                    "task_id": (
                        "holdout|scenario=no_emission_contrast_negative_control|bundle=0000"
                    ),
                    "duration_seconds": duration,
                }
            )
            bootstrap_duration = float(
                cast(float, equal_bootstrap_unit["measured_duration_seconds"])
            )
            for draw_index in range(cast(int, equal_bootstrap_unit["holdout_repeat_count"])):
                holdout.append(
                    {
                        "task_id": (
                            "holdout|scenario=no_emission_contrast_negative_control|"
                            f"component=bootstrap|draw={draw_index:04d}"
                        ),
                        "duration_seconds": bootstrap_duration,
                    }
                )
            continue
        for replicate_id in range(cast(int, unit["holdout_repeat_count"])):
            holdout.append(
                {
                    "task_id": f"holdout|scenario={scenario_id}|replicate={replicate_id:04d}",
                    "duration_seconds": duration,
                }
            )
    if len(calibration) != 96 or len(holdout) != 536:
        raise ValueError("runtime expansion does not reproduce the literal 96/536 task frame")
    return calibration, holdout


def deterministic_lpt_worker_loads(
    task_durations: Sequence[Mapping[str, object]], *, workers: int = 8
) -> list[float]:
    if type(workers) is not int or workers != 8:
        raise ValueError("runtime LPT requires exactly eight workers")
    ordered: list[tuple[str, float]] = []
    for item in task_durations:
        duration = _require_exact_mapping(
            item, frozenset({"task_id", "duration_seconds"}), name="runtime task duration"
        )
        task_id = duration["task_id"]
        seconds = _require_finite_number(duration["duration_seconds"], name="duration_seconds")
        if type(task_id) is not str or not task_id or seconds <= 0.0:
            raise ValueError("runtime task duration must have a stable ID and positive seconds")
        ordered.append((task_id, seconds))
    if len({task_id for task_id, _ in ordered}) != len(ordered):
        raise ValueError("runtime task duration IDs must be unique")
    loads = [0.0] * workers
    for _task_id, seconds in sorted(ordered, key=lambda item: (-item[1], item[0])):
        worker_index = min(range(workers), key=lambda index: (loads[index], index))
        loads[worker_index] += seconds
    return loads


def build_runtime_projection_document(
    *,
    measured_duration_seconds: Mapping[str, float],
    equal_bootstrap_duration_seconds: float,
) -> dict[str, object]:
    if set(measured_duration_seconds) != set(SCENARIO_IDS):
        raise ValueError("runtime measured durations require the exact scenario frame")
    measured_units: list[dict[str, object]] = []
    for authority in RUNTIME_TASK_UNIT_AUTHORITY:
        scenario_id = cast(str, authority["scenario_id"])
        duration = _require_finite_number(
            measured_duration_seconds[scenario_id], name="measured_duration_seconds"
        )
        if duration <= 0.0:
            raise ValueError("runtime measured duration must be positive")
        measured_units.append(dict(authority) | {"measured_duration_seconds": duration})
    equal_duration = _require_finite_number(
        equal_bootstrap_duration_seconds, name="equal bootstrap duration"
    )
    if equal_duration <= 0.0:
        raise ValueError("equal bootstrap duration must be positive")
    equal_unit = dict(EQUAL_BOOTSTRAP_RUNTIME_AUTHORITY) | {
        "measured_duration_seconds": equal_duration
    }
    calibration, holdout = _runtime_task_durations(measured_units, equal_unit)
    calibration_loads = deterministic_lpt_worker_loads(calibration)
    holdout_loads = deterministic_lpt_worker_loads(holdout)
    projected_calibration = RUNTIME_SAFETY_FACTOR * max(calibration_loads)
    projected_holdout = RUNTIME_SAFETY_FACTOR * max(holdout_loads)
    passed = (
        projected_calibration <= RUNTIME_PROJECTION_LIMIT_SECONDS
        and projected_holdout <= RUNTIME_PROJECTION_LIMIT_SECONDS
    )
    return {
        "schema_version": GENERATED_ARTIFACT_SCHEMA_VERSION,
        "workers": 8,
        "safety_factor": RUNTIME_SAFETY_FACTOR,
        "measured_task_units": measured_units,
        "equal_bootstrap_task_unit": equal_unit,
        "calibration_task_durations": calibration,
        "holdout_task_durations": holdout,
        "calibration_worker_loads": calibration_loads,
        "holdout_worker_loads": holdout_loads,
        "projected_calibration_seconds": projected_calibration,
        "projected_holdout_seconds": projected_holdout,
        "holdout_payload_instantiated": False,
        "scientific_rows_emitted": False,
        "passed": passed,
    }


def validate_runtime_projection_document(payload: Mapping[str, object]) -> None:
    document = _require_exact_mapping(payload, RUNTIME_PROJECTION_KEYS, name="runtime projection")
    measured = document["measured_task_units"]
    if not isinstance(measured, list) or len(measured) != len(SCENARIO_IDS):
        raise ValueError("runtime projection requires the literal measured task registry")
    durations: dict[str, float] = {}
    for item, authority in zip(measured, RUNTIME_TASK_UNIT_AUTHORITY, strict=True):
        unit = _require_exact_mapping(item, RUNTIME_TASK_UNIT_KEYS, name="measured task unit")
        duration = _require_finite_number(
            unit["measured_duration_seconds"], name="measured_duration_seconds"
        )
        without_duration = dict(unit)
        without_duration.pop("measured_duration_seconds")
        if duration <= 0.0 or without_duration != authority:
            raise ValueError("runtime measured task unit differs from literal authority")
        durations[cast(str, authority["scenario_id"])] = duration
    equal = _require_exact_mapping(
        document["equal_bootstrap_task_unit"],
        EQUAL_BOOTSTRAP_TASK_KEYS,
        name="equal bootstrap task unit",
    )
    equal_duration = _require_finite_number(
        equal["measured_duration_seconds"], name="equal bootstrap duration"
    )
    equal_without_duration = dict(equal)
    equal_without_duration.pop("measured_duration_seconds")
    if equal_duration <= 0.0 or equal_without_duration != EQUAL_BOOTSTRAP_RUNTIME_AUTHORITY:
        raise ValueError("equal bootstrap runtime unit differs from literal authority")
    expected = build_runtime_projection_document(
        measured_duration_seconds=durations,
        equal_bootstrap_duration_seconds=equal_duration,
    )
    if dict(document) != expected:
        raise ValueError("runtime task expansion, LPT loads, projection, or passed state differs")


def validate_holdout_manifest_document(payload: Mapping[str, object]) -> None:
    _validate_holdout_receipt_schema(payload)


def validate_artifact_manifest_details(payload: Mapping[str, object]) -> dict[str, object]:
    document = _require_exact_mapping(
        payload, ARTIFACT_MANIFEST_DETAIL_KEYS, name="artifact manifest details"
    )
    if document["schema_version"] != GENERATED_ARTIFACT_SCHEMA_VERSION:
        raise ValueError("artifact manifest details schema version is not literal")
    entries = document["entries"]
    represented_paths = tuple(path for path in ARTIFACT_PATHS if path != "verification.json")
    if not isinstance(entries, list) or len(entries) != len(represented_paths):
        raise ValueError("artifact manifest details require the exact 21 represented entries")
    canonical_entries: list[tuple[str, str]] = []
    for item, expected_path in zip(entries, represented_paths, strict=True):
        entry = _require_exact_mapping(
            item, frozenset({"path", "sha256"}), name="artifact manifest entry"
        )
        if entry["path"] != expected_path:
            raise ValueError("artifact manifest details path order is not literal")
        canonical_entries.append(
            (expected_path, _require_sha256(entry["sha256"], name="artifact sha256"))
        )
    represented = _require_sha256(
        document["represented_artifact_set_sha256"],
        name="represented_artifact_set_sha256",
    )
    if _digest_lines(canonical_entries) != represented:
        raise ValueError("artifact manifest represented digest does not reproduce")
    return {
        "schema_version": GENERATED_ARTIFACT_SCHEMA_VERSION,
        "entries": [{"path": path, "sha256": digest} for path, digest in canonical_entries],
        "represented_artifact_set_sha256": represented,
    }


def build_verification_document(
    *,
    config_payload: Mapping[str, object],
    runtime_projection: Mapping[str, object],
    source_provenance: Mapping[str, object],
    holdout_manifest: Mapping[str, object],
    artifact_manifest_details: Mapping[str, object],
    artifact_root: Path,
    science_bundle: ValidatedScienceBundle,
) -> dict[str, object]:
    _validate_config_schema(config_payload)
    config_without_hash = dict(config_payload)
    config_hash = _require_sha256(config_without_hash.pop("config_sha256"), name="config_sha256")
    if sha256(canonical_json_bytes(config_without_hash)).hexdigest() != config_hash:
        raise ValueError("verification config self-hash does not reproduce")
    validate_runtime_projection_document(runtime_projection)
    validate_source_provenance_document(source_provenance)
    validate_holdout_manifest_document(holdout_manifest)
    holdout_without_hash = dict(holdout_manifest)
    receipt_hash = _require_sha256(
        holdout_without_hash.pop("receipt_sha256"), name="receipt_sha256"
    )
    if sha256(canonical_json_bytes(holdout_without_hash)).hexdigest() != receipt_hash:
        raise ValueError("verification holdout receipt self-hash does not reproduce")
    details = validate_artifact_manifest_details(artifact_manifest_details)
    if not isinstance(artifact_root, Path):
        raise TypeError("verification artifact root must be a Path")
    live_details = build_artifact_manifest_document(artifact_root.resolve())
    if live_details != details:
        raise ValueError("verification artifact manifest details do not match live artifact bytes")
    if (
        type(science_bundle) is not ValidatedScienceBundle
        or science_bundle._token is not _VALIDATED_SCIENCE_BUNDLE_TOKEN
    ):
        raise TypeError("verification requires a module-issued validated science bundle")
    for name in ("spec_sha256", "source_sha256", "tracked_state_sha256"):
        if holdout_manifest[name] != config_payload[name]:
            raise ValueError("verification holdout/config provenance bindings differ")
    if holdout_manifest["config_sha256"] != config_hash:
        raise ValueError("verification holdout config hash binding differs")
    reconstructed_source_sha256 = sha256(
        (
            f"landscape_sha256={source_provenance['landscape_sha256']}\n"
            f"arrival_sha256={source_provenance['arrival_sha256']}\n"
        ).encode()
    ).hexdigest()
    if reconstructed_source_sha256 != config_payload["source_sha256"]:
        raise ValueError("verification source provenance does not bind config source hash")

    scenario_results = dict(science_bundle.scenario_results)
    predictive_states = dict(science_bundle.predictive_states)
    controls = {cast(str, row["decision_row_id"]): row for row in science_bundle.control_rows}
    checks: list[dict[str, object]] = []
    for scenario_id in SCENARIO_IDS:
        row = controls[f"scenario_gate|{scenario_id}"]
        reason = scenario_results[scenario_id]
        predictive_state = predictive_states[scenario_id]
        checks.append(
            {
                "name": SCENARIO_GATE_FAMILY[scenario_id],
                "passed": row["gate_result"] == "pass",
                "details": {
                    "decision_row_id": row["decision_row_id"],
                    "gate_result": row["gate_result"],
                    "reason": reason,
                    "design_evidence_sha256": science_bundle.design_evidence_sha256,
                    "design_row_count": len(science_bundle.design_rows),
                    "predictive_complete_finite": (predictive_state.predictive_complete_finite),
                    "predictive_pass": predictive_state.predictive_pass,
                    "finite_rule_fired": predictive_state.finite_rule_fired,
                    "scientific_warning_available": (predictive_state.scientific_warning_available),
                    "forced_warning": predictive_state.forced_warning,
                },
            }
        )
    status_ids = tuple(
        f"parameter_status|no_emission_contrast_negative_control|{row['parameter_id']}"
        for row in EQUAL_EMISSION_STATUS_ROWS
    )
    status_digest = sha256(
        canonical_json_bytes({"rows": [dict(row) for row in EQUAL_EMISSION_STATUS_ROWS]})
    ).hexdigest()
    checks.append(
        {
            "name": "parameter_status",
            "passed": all(status_id in controls for status_id in status_ids),
            "details": {
                "decision_row_ids": list(status_ids),
                "status_rows_sha256": status_digest,
            },
        }
    )
    final = controls["final_decision"]
    checks.append(
        {
            "name": "final_recommendation",
            "passed": final["gate_result"] == "pass",
            "details": {
                "decision_row_id": "final_decision",
                "recommendation_rank": final["recommendation_rank"],
                "recommendation_class": final["recommendation_class"],
                "reason": final["interpretation"],
                "transportability_class": final["transportability_class"],
            },
        }
    )
    checks.append({"name": "artifact_manifest", "passed": True, "details": details})
    tracked_details = {
        "tracked_state_sha256": config_payload["tracked_state_sha256"],
        "runtime_projection_passed": runtime_projection["passed"],
        "source_provenance_passed": source_provenance["passed"],
        "holdout_manifest_exposed": holdout_manifest["exposed"],
    }
    checks.append(
        {
            "name": "tracked_state",
            "passed": all(
                value is True
                for key, value in tracked_details.items()
                if key != "tracked_state_sha256"
            ),
            "details": tracked_details,
        }
    )
    return {
        "schema_version": GENERATED_ARTIFACT_SCHEMA_VERSION,
        "spec_sha256": config_payload["spec_sha256"],
        "config_sha256": config_hash,
        "source_sha256": config_payload["source_sha256"],
        "checks": checks,
        "recommendation_class": final["recommendation_class"],
        "transportability_class": final["transportability_class"],
        "boundary_labels": dict(FROZEN_BOUNDARY_LABELS),
        "passed": all(check["passed"] is True for check in checks),
    }


def validate_verification_document(
    payload: Mapping[str, object],
    *,
    config_payload: Mapping[str, object],
    runtime_projection: Mapping[str, object],
    source_provenance: Mapping[str, object],
    holdout_manifest: Mapping[str, object],
    artifact_manifest_details: Mapping[str, object],
    artifact_root: Path,
    science_bundle: ValidatedScienceBundle,
) -> None:
    document = _require_exact_mapping(payload, VERIFICATION_KEYS, name="verification")
    expected = build_verification_document(
        config_payload=config_payload,
        runtime_projection=runtime_projection,
        source_provenance=source_provenance,
        holdout_manifest=holdout_manifest,
        artifact_manifest_details=artifact_manifest_details,
        artifact_root=artifact_root,
        science_bundle=science_bundle,
    )
    if dict(document) != expected:
        raise ValueError("verification checks, details, recommendation, or passed state differ")


def _artifact_disk_paths(output_dir: Path) -> tuple[str, ...]:
    paths: list[str] = []
    if not output_dir.is_dir():
        return ()
    for path in output_dir.rglob("*"):
        if path.is_dir() and not path.is_symlink():
            continue
        paths.append(path.relative_to(output_dir).as_posix())
    return tuple(sorted(paths))


def _require_regular_nonempty(path: Path, *, relative_path: str) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"missing, nonregular, or zero-byte artifact: {relative_path}")


def build_artifact_manifest_document(output_dir: Path) -> dict[str, object]:
    disk_paths = _artifact_disk_paths(output_dir)
    represented_paths = tuple(
        sorted(path for path in ARTIFACT_PATHS if path != "verification.json")
    )
    if disk_paths not in (represented_paths, tuple(sorted(ARTIFACT_PATHS))):
        raise ValueError("represented artifact directory is not the exact 22-file set")
    entries: list[dict[str, str]] = []
    for relative_path in ARTIFACT_PATHS:
        if relative_path == "verification.json":
            continue
        path = output_dir / relative_path
        _require_regular_nonempty(path, relative_path=relative_path)
        entries.append({"path": relative_path, "sha256": _file_digest(path)})
    represented = _digest_lines(tuple((entry["path"], entry["sha256"]) for entry in entries))
    return {
        "schema_version": GENERATED_ARTIFACT_SCHEMA_VERSION,
        "entries": entries,
        "represented_artifact_set_sha256": represented,
    }


def artifact_snapshot(output_dir: Path) -> ArtifactSnapshot:
    if _artifact_disk_paths(output_dir) != tuple(sorted(ARTIFACT_PATHS)):
        raise ValueError("artifact snapshot does not match the exact 22-file set")
    for relative_path in ARTIFACT_PATHS:
        _require_regular_nonempty(output_dir / relative_path, relative_path=relative_path)
    entries = tuple(
        (relative_path, _file_digest(output_dir / relative_path))
        for relative_path in sorted(ARTIFACT_PATHS)
    )
    if tuple(path for path, _ in entries) != tuple(sorted(ARTIFACT_PATHS)):
        raise ValueError("artifact snapshot does not match the exact 22-file set")
    return ArtifactSnapshot(entries, _digest_lines(entries))


def write_canonical_config(path: Path, payload: Mapping[str, object]) -> None:
    _, canonical = _canonical_config_document(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical)


def _canonical_config_document(
    payload: Mapping[str, object],
) -> tuple[dict[str, object], bytes]:
    without_hash = dict(payload)
    without_hash.pop("config_sha256", None)
    complete = dict(without_hash)
    complete["config_sha256"] = sha256(canonical_json_bytes(without_hash)).hexdigest()
    _validate_config_schema(complete)
    return complete, canonical_json_bytes(complete)


def _require_sha256(value: object, *, name: str) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be a lowercase SHA-256")
    return value


def _require_exact_mapping(
    value: object, keys: frozenset[str], *, name: str
) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise ValueError(f"{name} schema is incomplete or has undeclared fields")
    return cast(Mapping[str, object], value)


def _require_finite_number(value: object, *, name: str) -> float:
    if type(value) not in (int, float) or not isfinite(float(cast(float, value))):
        raise ValueError(f"{name} must be finite")
    return float(cast(float, value))


def capture_live_authority(repo_root: Path) -> LiveAuthorityIdentity:
    root = repo_root.resolve()
    spec_path = root / AUTHORITATIVE_SPEC_RELATIVE_PATH
    receipt_path = root / SOURCE_RECEIPT_RELATIVE_PATH
    _require_regular_nonempty(spec_path, relative_path=AUTHORITATIVE_SPEC_RELATIVE_PATH)
    _require_regular_nonempty(receipt_path, relative_path=SOURCE_RECEIPT_RELATIVE_PATH)
    spec_sha256 = _file_digest(spec_path)
    receipt_bytes = receipt_path.read_bytes()
    receipt_file_sha256 = sha256(receipt_bytes).hexdigest()
    if receipt_file_sha256 != ACCEPTED_SOURCE_RECEIPT_FILE_SHA256:
        raise ValueError("live source receipt file SHA does not match accepted authority")
    try:
        raw = loads(receipt_bytes.decode("utf-8"))
    except (UnicodeError, ValueError) as error:
        raise ValueError("accepted source receipt is not parseable JSON") from error
    receipt = _require_exact_mapping(raw, SOURCE_RECEIPT_KEYS, name="source receipt")
    if (
        receipt["schema_version"] != "1.0"
        or receipt["source_commit"] != PINNED_COMMIT
        or receipt["parameter_set_id"] != "balanced_corridor_detour_v2"
        or type(receipt["serialization_contract"]) is not str
        or not receipt["serialization_contract"]
        or receipt["passed"] is not True
    ):
        raise ValueError("accepted source receipt literals do not match live authority")
    landscape_sha256 = _require_sha256(receipt["landscape_sha256"], name="source landscape_sha256")
    arrival_sha256 = _require_sha256(receipt["arrival_sha256"], name="source arrival_sha256")
    if (
        receipt["independent_check_landscape_sha256"] != landscape_sha256
        or receipt["independent_check_arrival_sha256"] != arrival_sha256
    ):
        raise ValueError("source receipt independent hashes do not reconcile")
    source_sha256 = sha256(
        f"landscape_sha256={landscape_sha256}\narrival_sha256={arrival_sha256}\n".encode()
    ).hexdigest()
    return LiveAuthorityIdentity(spec_sha256, source_sha256, receipt_file_sha256)


def _validate_config_live_authority(
    current: PhaseGuardState, payload: Mapping[str, object]
) -> LiveAuthorityIdentity:
    authority = capture_live_authority(current.repo_root)
    if (
        payload.get("spec_sha256") != authority.spec_sha256
        or payload.get("source_sha256") != authority.source_sha256
    ):
        raise ValueError("config does not match freshly reconstructed live authority")
    analytical = dict(current.analytical_entries)
    if (
        analytical.get(AUTHORITATIVE_SPEC_RELATIVE_PATH) != authority.spec_sha256
        or analytical.get(SOURCE_RECEIPT_RELATIVE_PATH) != authority.source_receipt_file_sha256
    ):
        raise ValueError("captured analytical manifest does not bind live authority files")
    return authority


def _validate_config_schema(payload: Mapping[str, object]) -> None:
    _require_exact_mapping(payload, CONFIG_TOP_LEVEL_KEYS, name="config")
    if payload["schema_version"] != CONFIG_SCHEMA_VERSION:
        raise ValueError("config schema_version must equal the literal v1 authority")
    for name in ("spec_sha256", "config_sha256", "source_sha256", "tracked_state_sha256"):
        _require_sha256(payload[name], name=name)
    model = _require_exact_mapping(payload["model"], MODEL_CONFIG_KEYS, name="model")
    if dict(model) != FROZEN_MODEL_CONFIG:
        raise ValueError("model must reproduce the complete literal frozen configuration")
    estimator = _require_exact_mapping(
        payload["estimator"], ESTIMATOR_CONFIG_KEYS, name="estimator"
    )
    if dict(estimator) != FROZEN_ESTIMATOR_CONFIG:
        raise ValueError("estimator must reproduce the complete literal frozen configuration")
    parameters = payload["parameters"]
    if (
        not isinstance(parameters, list)
        or not all(isinstance(item, Mapping) for item in parameters)
        or tuple(dict(cast(Mapping[str, object], item)) for item in parameters)
        != CONFIG_PARAMETER_ROWS
        or any(
            set(cast(Mapping[str, object], item)) != set(MODEL_PARAMETER_CONFIG_FIELDS)
            for item in parameters
        )
    ):
        raise ValueError("parameters must reproduce the complete literal ordered rows")
    scenarios = payload["scenarios"]
    expected_scenarios = [asdict(row) for row in SCENARIO_DEFINITIONS]
    if scenarios != expected_scenarios:
        raise ValueError("scenarios must reproduce the literal registry and schema")
    seeds = _require_exact_mapping(
        payload["seed_partitions"], SEED_PARTITION_KEYS, name="seed_partitions"
    )
    if dict(seeds) != FROZEN_SEED_PARTITIONS:
        raise ValueError("seed partitions must reproduce the complete literal configuration")
    gates = _require_exact_mapping(payload["gates"], GATE_CONFIG_KEYS, name="gates")
    if dict(gates) != FROZEN_GATE_CONFIG:
        raise ValueError("gates must reproduce the complete literal frozen configuration")
    manifest = payload["artifact_manifest"]
    if not isinstance(manifest, list):
        raise ValueError("artifact_manifest schema must be a list")
    validate_expected_artifact_manifest(cast(Sequence[Mapping[str, object]], manifest))
    labels = _require_exact_mapping(
        payload["boundary_labels"], BOUNDARY_LABEL_KEYS, name="boundary_labels"
    )
    if dict(labels) != FROZEN_BOUNDARY_LABELS:
        raise ValueError("boundary labels must reproduce the literal frozen configuration")
    validate_no_latent_thresholds(payload)


def _validate_holdout_receipt_schema(payload: Mapping[str, object]) -> None:
    _require_exact_mapping(payload, HOLDOUT_RECEIPT_KEYS, name="holdout receipt")
    if (
        payload["schema_version"] != HOLDOUT_RECEIPT_SCHEMA_VERSION
        or payload["seed_namespace"] != HOLDOUT_SEED_NAMESPACE
    ):
        raise ValueError("holdout receipt schema version or seed namespace is not literal")
    for name in (
        "spec_sha256",
        "config_sha256",
        "source_sha256",
        "tracked_state_sha256",
        "receipt_sha256",
    ):
        _require_sha256(payload[name], name=name)
    if (
        payload["exposed"] is not True
        or payload["invalidated"] is not False
        or payload["no_contract_change"] is not True
    ):
        raise ValueError("holdout receipt exposure fields are invalid")


def _validate_preholdout_receipt_schema(payload: Mapping[str, object]) -> None:
    _require_exact_mapping(payload, PREHOLDOUT_RECEIPT_KEYS, name="preholdout receipt")
    if payload["schema_version"] != PREHOLDOUT_RECEIPT_SCHEMA_VERSION:
        raise ValueError("preholdout receipt schema_version must equal literal v1")
    for name in ("spec_sha256", "config_sha256", "source_sha256", "tracked_state_sha256"):
        _require_sha256(payload[name], name=name)
    manifest = payload["tracked_file_manifest"]
    if not isinstance(manifest, list) or len(manifest) != len(ANALYTICAL_PATHS):
        raise ValueError("preholdout tracked manifest is incomplete")
    entries: list[tuple[str, str]] = []
    for item in manifest:
        mapping = _require_exact_mapping(
            item, frozenset({"path", "sha256"}), name="tracked manifest entry"
        )
        if type(mapping["path"]) is not str:
            raise ValueError("tracked manifest path must be string")
        entries.append(
            (
                mapping["path"],
                _require_sha256(mapping["sha256"], name="tracked manifest sha256"),
            )
        )
    if tuple(entries) != tuple(sorted(entries)) or tuple(path for path, _ in entries) != tuple(
        sorted(ANALYTICAL_PATHS)
    ):
        raise ValueError("preholdout tracked manifest paths are not literal and sorted")
    if _digest_lines(entries) != payload["tracked_state_sha256"]:
        raise ValueError("preholdout tracked-state digest mismatch")


def load_frozen_config_identity(path: Path) -> FrozenConfigIdentity:
    canonical_bytes = path.read_bytes()
    raw = loads(canonical_bytes.decode("ascii"))
    if type(raw) is not dict or type(raw.get("config_sha256")) is not str:
        raise ValueError("config must contain an embedded config_sha256")
    payload = cast(dict[str, object], raw)
    if canonical_bytes != canonical_json_bytes(payload):
        raise ValueError("config bytes are not canonical")
    without_hash = dict(payload)
    embedded = cast(str, without_hash.pop("config_sha256"))
    if embedded != sha256(canonical_json_bytes(without_hash)).hexdigest():
        raise ValueError("config self-hash mismatch")
    _validate_config_schema(payload)
    return FrozenConfigIdentity(
        path, payload, embedded, sha256(canonical_bytes).hexdigest(), canonical_bytes
    )


def require_frozen_config_identity(value: object) -> FrozenConfigIdentity:
    if type(value) is not FrozenConfigIdentity:
        raise TypeError("phase boundary requires FrozenConfigIdentity")
    return value


def write_canonical_receipt(
    path: Path, payload: Mapping[str, object], *, exclusive: bool = False
) -> None:
    without_hash = dict(payload)
    without_hash.pop("receipt_sha256", None)
    complete = dict(without_hash)
    complete["receipt_sha256"] = sha256(canonical_json_bytes(without_hash)).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    canonical = canonical_json_bytes(complete)
    if exclusive:
        with path.open("xb") as stream:
            stream.write(canonical)
    else:
        path.write_bytes(canonical)


def load_holdout_receipt_identity(path: Path) -> HoldoutReceiptIdentity:
    canonical_bytes = path.read_bytes()
    raw = loads(canonical_bytes.decode("ascii"))
    if type(raw) is not dict or canonical_bytes != canonical_json_bytes(raw):
        raise ValueError("holdout receipt bytes are not canonical")
    payload = cast(dict[str, object], raw)
    without_hash = dict(payload)
    embedded = without_hash.pop("receipt_sha256", None)
    if (
        type(embedded) is not str
        or embedded != sha256(canonical_json_bytes(without_hash)).hexdigest()
    ):
        raise ValueError("holdout receipt self-hash mismatch")
    _validate_holdout_receipt_schema(payload)
    return HoldoutReceiptIdentity(
        path, payload, embedded, sha256(canonical_bytes).hexdigest(), canonical_bytes
    )


def load_receipt_file_identity(path: Path) -> ReceiptFileIdentity:
    canonical_bytes = path.read_bytes()
    raw = loads(canonical_bytes.decode("ascii"))
    if type(raw) is not dict or canonical_bytes != canonical_json_bytes(raw):
        raise ValueError("receipt file bytes are not canonical")
    _validate_preholdout_receipt_schema(cast(dict[str, object], raw))
    return ReceiptFileIdentity(path, sha256(canonical_bytes).hexdigest(), canonical_bytes)


def require_phase_identities(
    config: object, preholdout_receipt: object, holdout_receipt: object
) -> tuple[FrozenConfigIdentity, ReceiptFileIdentity | None, HoldoutReceiptIdentity | None]:
    if type(config) is not FrozenConfigIdentity:
        raise TypeError("phase boundary requires FrozenConfigIdentity")
    if preholdout_receipt is not None and type(preholdout_receipt) is not ReceiptFileIdentity:
        raise TypeError("phase boundary requires ReceiptFileIdentity")
    if holdout_receipt is not None and type(holdout_receipt) is not HoldoutReceiptIdentity:
        raise TypeError("phase boundary requires HoldoutReceiptIdentity")
    try:
        loaded_config = load_frozen_config_identity(config.path)
    except OSError as error:
        raise ValueError(
            "phase config identity was not produced by the validated loader"
        ) from error
    if loaded_config != config:
        raise ValueError("phase config identity was not produced by the validated canonical loader")
    loaded_preholdout: ReceiptFileIdentity | None = None
    if preholdout_receipt is not None:
        loaded_preholdout = load_receipt_file_identity(preholdout_receipt.path)
        if loaded_preholdout != preholdout_receipt:
            raise ValueError("phase preholdout identity was not validated from current bytes")
    loaded_holdout: HoldoutReceiptIdentity | None = None
    if holdout_receipt is not None:
        loaded_holdout = load_holdout_receipt_identity(holdout_receipt.path)
        if loaded_holdout != holdout_receipt:
            raise ValueError("phase holdout identity was not validated from current bytes")
    for receipt in (
        cast(Mapping[str, object], loads(loaded_preholdout.canonical_bytes))
        if loaded_preholdout is not None
        else None,
        loaded_holdout.payload if loaded_holdout is not None else None,
    ):
        if receipt is not None and any(
            receipt[name] != loaded_config.payload[name]
            for name in ("spec_sha256", "config_sha256", "source_sha256", "tracked_state_sha256")
        ):
            raise ValueError("config and receipt cross-binding mismatch")
    return loaded_config, loaded_preholdout, loaded_holdout


def validate_task3_command(command: Sequence[str]) -> None:
    phase = _parsed_phase(command)
    if phase in ("runtime-benchmark", "calibration", "freeze-tracked-state", "holdout"):
        raise ValueError("Task 3 cannot own production calibration or holdout")


def _parsed_phase(command: Sequence[str]) -> str | None:
    phase: str | None = None
    index = 0
    while index < len(command):
        token = command[index]
        if token == "--phase":
            if index + 1 >= len(command) or phase is not None:
                raise ValueError("command has a malformed or duplicate --phase")
            phase = command[index + 1]
            index += 2
            continue
        if token.startswith("--phase="):
            if phase is not None or token == "--phase=":
                raise ValueError("command has a malformed or duplicate --phase")
            phase = token.split("=", 1)[1]
        index += 1
    return phase


_REVIEWED_TRANSIENT_DISPOSITION = "TRANSIENT_VALIDATION_FAILURE_RETRY_APPROVED"
NON_GENERATIVE_COMMAND_REGISTRY = (
    ValidationCommandSpec(
        "static_diff", ("git", "diff", "--check"), None, _REVIEWED_TRANSIENT_DISPOSITION
    ),
    ValidationCommandSpec(
        "format_check",
        ("uv", "run", "ruff", "format", "--check", "."),
        None,
        _REVIEWED_TRANSIENT_DISPOSITION,
    ),
    ValidationCommandSpec(
        "lint_check",
        ("uv", "run", "ruff", "check", "."),
        None,
        _REVIEWED_TRANSIENT_DISPOSITION,
    ),
    ValidationCommandSpec(
        "type_check",
        ("uv", "run", "mypy", "src", "tests"),
        None,
        _REVIEWED_TRANSIENT_DISPOSITION,
    ),
    ValidationCommandSpec(
        "test_check", ("uv", "run", "pytest"), None, _REVIEWED_TRANSIENT_DISPOSITION
    ),
    ValidationCommandSpec("build_check", ("uv", "build"), None, _REVIEWED_TRANSIENT_DISPOSITION),
    ValidationCommandSpec(
        "hook_check",
        ("uv", "run", "pre-commit", "run", "--all-files"),
        None,
        _REVIEWED_TRANSIENT_DISPOSITION,
    ),
    ValidationCommandSpec(
        "frozen_verify",
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
        "verify",
        _REVIEWED_TRANSIENT_DISPOSITION,
    ),
    ValidationCommandSpec(
        "tracked_state_verify",
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
        "verify-tracked-state",
        _REVIEWED_TRANSIENT_DISPOSITION,
    ),
    ValidationCommandSpec(
        "receipt_hash_read",
        (
            "shasum",
            "-a",
            "256",
            f"{GOAL_DIRECTORY}/holdout_receipt.json",
        ),
        None,
        _REVIEWED_TRANSIENT_DISPOSITION,
    ),
    ValidationCommandSpec(
        "ignored_status_read",
        ("git", "status", "--ignored", "--short", "artifacts", "dist"),
        None,
        _REVIEWED_TRANSIENT_DISPOSITION,
    ),
    ValidationCommandSpec(
        "repository_status_read",
        ("git", "status", "--short", "--branch", "--untracked-files=all"),
        None,
        _REVIEWED_TRANSIENT_DISPOSITION,
    ),
)
_NON_GENERATIVE_COMMAND_BY_ARGV = {spec.argv: spec for spec in NON_GENERATIVE_COMMAND_REGISTRY}


def resolve_non_generative_command(command: Sequence[str]) -> ValidationCommandSpec:
    argv = tuple(command)
    spec = _NON_GENERATIVE_COMMAND_BY_ARGV.get(argv)
    if spec is None:
        raise ValueError("command is not in the closed non-generative registry")
    if _parsed_phase(argv) != spec.phase:
        raise ValueError("registered command phase does not match parsed argv")
    return spec


def scenario_definition_bytes(rows: Sequence[ScenarioDefinition]) -> bytes:
    if tuple(rows) != SCENARIO_DEFINITIONS:
        raise ValueError("scenario definitions must use literal contract order")
    return canonical_json_bytes({"rows": [asdict(row) for row in rows]})


def issue_temporary_fixture_root(path: Path, *, repo_root: Path) -> TemporaryFixtureRoot:
    root = repo_root.resolve()
    resolved = path.resolve()
    canonical = (root / CANONICAL_ARTIFACT_RELATIVE_PATH).resolve()
    if resolved == canonical or canonical in resolved.parents:
        raise ValueError("fixture output cannot use the canonical artifact path or an alias")
    temporary_base = Path(gettempdir()).resolve()
    if resolved == temporary_base or temporary_base not in resolved.parents:
        raise ValueError("fixture output must be a dedicated temporary path")
    if path.is_symlink() or path.exists():
        raise ValueError("temporary fixture root must be a new non-symlink path")
    return TemporaryFixtureRoot(
        resolved,
        root,
        canonical,
        _FIXTURE_OUTPUT_ROOT_TOKEN,
    )


def _require_temporary_fixture_root(value: object) -> TemporaryFixtureRoot:
    if type(value) is not TemporaryFixtureRoot or value._token is not _FIXTURE_OUTPUT_ROOT_TOKEN:
        raise TypeError("fixture emission requires a module-issued temporary fixture root")
    current_canonical = (value.repo_root / CANONICAL_ARTIFACT_RELATIVE_PATH).resolve()
    current_path = value.path.resolve()
    temporary_base = Path(gettempdir()).resolve()
    if (
        current_canonical != value.canonical_artifact_path
        or current_path != value.path
        or current_path == current_canonical
        or current_canonical in current_path.parents
        or temporary_base not in current_path.parents
    ):
        raise ValueError("fixture root changed identity or aliases the canonical artifact path")
    if value.path.exists() or value.path.is_symlink():
        raise FileExistsError(value.path)
    return value


def emit_fixture_bundle(
    output_root: TemporaryFixtureRoot,
    *,
    task_results: Sequence[Mapping[str, object]],
    workers: int,
) -> ArtifactSnapshot:
    output_dir = _require_temporary_fixture_root(output_root).path
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError("workers must be in 1..8")
    ordered_tasks = sorted((dict(row) for row in task_results), key=lambda row: str(row["task_id"]))
    common = canonical_json_bytes({"fixture_only": True, "task_results": ordered_tasks})
    for relative_path in ARTIFACT_PATHS:
        if relative_path == "verification.json":
            continue
        path = output_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(relative_path.encode("ascii") + b"\n" + common)
    verification = build_artifact_manifest_document(output_dir)
    (output_dir / "verification.json").write_bytes(canonical_json_bytes(verification))
    return artifact_snapshot(output_dir)


def envelope_changes(before: ProvenanceEnvelope, after: ProvenanceEnvelope) -> tuple[str, ...]:
    return tuple(
        name
        for name in before.__dataclass_fields__
        if getattr(before, name) != getattr(after, name)
    )


def classify_post_exposure_command(
    before: ProvenanceEnvelope,
    after: ProvenanceEnvelope,
    *,
    exit_code: int,
    retry_count: int = 0,
) -> str:
    if envelope_changes(before, after):
        return "STOP_INVALIDATED_POST_EXPOSURE"
    if exit_code == 0:
        return "CONTINUE_FROZEN_CANDIDATE"
    if retry_count == 0:
        return "STOP_NONMUTATING_VALIDATION_FAILURE_PENDING_DISPOSITION"
    return "STOP_NONMUTATING_VALIDATION_FAILURE"


def _post_exposure_log_document(
    before: ProvenanceEnvelope,
    *,
    record_type: str,
    disposition: str,
) -> dict[str, object]:
    if (
        type(record_type) is not str
        or not record_type
        or type(disposition) is not str
        or not disposition
    ):
        raise ValueError("Log record type and disposition must be nonempty strings")
    return {
        "record_type": record_type,
        "disposition": disposition,
        "writer_role": "provenance_writer",
        "reviewer_role": "independent_reviewer",
        "analytical_payload": False,
        "parent_line_count": len(before.log_bytes.splitlines()),
        "parent_byte_count": len(before.log_bytes),
        "parent_sha256": sha256(before.log_bytes).hexdigest(),
        "repository_root": str(before.repo_root.resolve()),
        "log_path": f"{GOAL_DIRECTORY}/Log.md",
        "branch": before.branch,
        "head": before.head,
        "base": before.base,
        "tracked": [list(item) for item in before.tracked],
        "staged": [list(item) for item in before.staged],
        "unstaged": list(before.unstaged),
        "untracked": list(before.untracked),
        "status_entries": [list(item) for item in before.status_entries],
        "cached_entries": [list(item) for item in before.cached_entries],
        "analytical_entries": [list(item) for item in before.analytical_entries],
        "candidate_entries": [list(item) for item in before.candidate_entries],
        "analytical_sha256": _digest_lines(before.analytical_entries),
        "preholdout_receipt_file_sha256": before.preholdout_receipt_file_sha256,
        "receipt_sha256": before.receipt_sha256,
        "holdout_receipt_file_sha256": before.holdout_receipt_file_sha256,
        "config_sha256": before.config_sha256,
        "config_file_sha256": before.config_file_sha256,
        "represented_artifact_set_sha256": before.represented_artifact_set_sha256,
        "artifact_set_sha256": before.artifact_set_sha256,
    }


def post_exposure_log_payload(
    before: ProvenanceEnvelope,
    *,
    record_type: str,
    disposition: str,
) -> bytes:
    return canonical_json_bytes(
        _post_exposure_log_document(
            before,
            record_type=record_type,
            disposition=disposition,
        )
    )


def retry_review_log_payload(failure: ValidationFailureRecord) -> bytes:
    if (
        type(failure) is not ValidationFailureRecord
        or failure._token is not _VALIDATION_FAILURE_TOKEN
    ):
        raise TypeError("retry review requires a module-issued failure record")
    payload = _post_exposure_log_document(
        failure.after,
        record_type="retry_authorization",
        disposition="TRANSIENT_VALIDATION_FAILURE_RETRY_APPROVED",
    )
    payload.update(
        {
            "command_class": failure.command_spec.command_class,
            "failed_command": list(failure.command),
            "failed_phase": failure.command_spec.phase,
            "failed_exit_code": failure.exit_code,
            "failed_retry_count": failure.retry_count,
            "reviewed_disposition": failure.command_spec.reviewed_disposition,
        }
    )
    return canonical_json_bytes(payload)


def validate_post_exposure_log_append(
    before: ProvenanceEnvelope,
    after: ProvenanceEnvelope,
    *,
    approved_suffix: bytes,
) -> ReviewedLogTransition:
    if not after.log_bytes.startswith(before.log_bytes) or (
        after.log_bytes[len(before.log_bytes) :] != approved_suffix
    ):
        raise ValueError("Log append must preserve exact prefix and approved suffix")
    changes = envelope_changes(before, after)
    if changes != ("log_bytes",):
        raise ValueError("Log append changed another immutable envelope member")
    try:
        raw = loads(approved_suffix.decode("utf-8"))
    except (UnicodeError, ValueError) as error:
        raise ValueError("Log suffix does not contain complete envelope JSON") from error
    if type(raw) is not dict or canonical_json_bytes(raw) != approved_suffix:
        raise ValueError("Log suffix is not a canonical complete envelope record")
    payload = cast(dict[str, object], raw)
    record_type = payload.get("record_type")
    disposition = payload.get("disposition")
    if type(record_type) is not str or type(disposition) is not str:
        raise ValueError("Log suffix lacks complete envelope record identity")
    expected = _post_exposure_log_document(
        before,
        record_type=record_type,
        disposition=disposition,
    )
    if record_type == "retry_authorization":
        retry_keys = {
            "command_class",
            "failed_command",
            "failed_phase",
            "failed_exit_code",
            "failed_retry_count",
            "reviewed_disposition",
        }
        if (
            set(payload) != set(expected) | retry_keys
            or not isinstance(payload.get("failed_command"), list)
            or not payload["failed_command"]
            or not all(
                type(value) is str for value in cast(list[object], payload["failed_command"])
            )
            or type(payload.get("failed_exit_code")) is not int
            or type(payload.get("failed_retry_count")) is not int
            or type(payload.get("command_class")) is not str
            or payload.get("failed_phase") not in (None, "verify", "verify-tracked-state")
            or payload.get("reviewed_disposition") != _REVIEWED_TRANSIENT_DISPOSITION
        ):
            raise ValueError("retry Log suffix lacks complete failed-command bindings")
        expected.update({name: payload[name] for name in retry_keys})
    if payload != expected or payload.get("analytical_payload") is not False:
        raise ValueError("Log suffix does not bind the complete envelope")
    return ReviewedLogTransition(
        before,
        after,
        approved_suffix,
        payload,
        _REVIEWED_LOG_TRANSITION_TOKEN,
    )


def record_validation_failure(
    command: Sequence[str],
    before: ProvenanceEnvelope,
    after: ProvenanceEnvelope,
    *,
    exit_code: int,
    retry_count: int = 0,
) -> ValidationFailureRecord:
    canonical_command = tuple(command)
    command_spec = resolve_non_generative_command(canonical_command)
    if (
        not canonical_command
        or type(exit_code) is not int
        or exit_code == 0
        or type(retry_count) is not int
        or retry_count < 0
        or envelope_changes(before, after)
    ):
        raise ValueError("validation failure must be nonzero with an unchanged envelope")
    return ValidationFailureRecord(
        command_spec,
        before,
        after,
        exit_code,
        retry_count,
        _VALIDATION_FAILURE_TOKEN,
    )


def authorize_retry(
    *,
    failure: ValidationFailureRecord,
    command: Sequence[str],
    capture_envelope: Callable[[], ProvenanceEnvelope],
    reviewed_log_transition: ReviewedLogTransition,
) -> tuple[str, ...]:
    canonical_command = tuple(command)
    command_spec = resolve_non_generative_command(canonical_command)
    current = capture_envelope()
    if type(current) is not ProvenanceEnvelope:
        raise TypeError("retry authorization requires a fresh captured current envelope")
    if (
        type(failure) is not ValidationFailureRecord
        or failure._token is not _VALIDATION_FAILURE_TOKEN
        or failure.command_spec != command_spec
        or failure.retry_count != 0
        or failure.exit_code == 0
        or envelope_changes(failure.before, failure.after)
    ):
        raise ValueError("retry lacks exact failed-command and envelope authorization")
    if (
        type(reviewed_log_transition) is not ReviewedLogTransition
        or reviewed_log_transition._token is not _REVIEWED_LOG_TRANSITION_TOKEN
        or reviewed_log_transition.before != failure.after
        or reviewed_log_transition.after != current
        or reviewed_log_transition.approved_suffix != retry_review_log_payload(failure)
    ):
        raise ValueError("retry current envelope lacks the sole reviewed Log-only transition")
    validated_transition = validate_post_exposure_log_append(
        reviewed_log_transition.before,
        reviewed_log_transition.after,
        approved_suffix=reviewed_log_transition.approved_suffix,
    )
    if validated_transition.payload != reviewed_log_transition.payload:
        raise ValueError("retry reviewed Log transition payload changed after validation")
    return canonical_command


def run_guarded_command_sequence(
    initial: ProvenanceEnvelope,
    results: Sequence[tuple[int, ProvenanceEnvelope]],
) -> None:
    current = initial
    for index, (exit_code, after) in enumerate(results, start=1):
        disposition = classify_post_exposure_command(current, after, exit_code=exit_code)
        if disposition != "CONTINUE_FROZEN_CANDIDATE":
            raise ValueError(f"command {index} failed its individual envelope")
        current = after


def _normalize_phase(phase: str) -> str:
    normalized = "pre_freeze" if phase == "config_emission" else phase
    if normalized not in PHASE_PRESENCE_COUNTS:
        raise ValueError("unknown provenance phase")
    return normalized


def _parse_porcelain_status(raw: str) -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if len(line) < 4 or line[2] != " ":
            raise ValueError("Git status porcelain record is malformed")
        code = line[:2]
        path = line[3:]
        if not path or " -> " in path or code == "!!":
            raise ValueError("renamed, ignored, or empty Git status paths are not permitted")
        entries.append((code, path))
    if len(entries) != len(set(entries)) or len({path for _, path in entries}) != len(entries):
        raise ValueError("Git status contains duplicate records or paths")
    return tuple(entries)


def _disk_identity(repo_root: Path, relative_path: str) -> str:
    path = repo_root / relative_path
    if not path.exists():
        return "ABSENT"
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"candidate path is nonregular: {relative_path}")
    return _file_digest(path)


def capture_phase_guard(
    repo_root: Path,
    phase: str,
    *,
    git_runner: Callable[[tuple[str, ...]], str],
) -> PhaseGuardState:
    normalized = _normalize_phase(phase)
    root = repo_root.resolve()
    branch = git_runner(("branch", "--show-current")).strip()
    head = git_runner(("rev-parse", "HEAD")).strip()
    base = git_runner(("rev-parse", "origin/main")).strip()
    parsed_status = _parse_porcelain_status(
        git_runner(("status", "--porcelain=v1", "--untracked-files=all"))
    )
    unknown = tuple(path for _, path in parsed_status if path not in PUBLICATION_PATHS)
    if unknown:
        raise ValueError(f"unknown footprint path: {unknown[0]}")
    if any(code != "??" and code[0] != " " for code, _ in parsed_status):
        raise ValueError("phase guard requires an empty Git index")
    analytical_entries = tuple(
        sorted((path, _disk_identity(root, path)) for path in ANALYTICAL_PATHS)
    )
    if any(digest == "ABSENT" for _, digest in analytical_entries):
        raise ValueError("literal analytical manifest is incomplete")
    candidate_entries = tuple(
        (code, path, _disk_identity(root, path)) for code, path in parsed_status
    )
    count = PHASE_PRESENCE_COUNTS[normalized]
    expected_present = PUBLICATION_PATHS[:count]
    expected_absent = PUBLICATION_PATHS[count:]
    if any(_disk_identity(root, path) == "ABSENT" for path in expected_present) or any(
        _disk_identity(root, path) != "ABSENT" for path in expected_absent
    ):
        raise ValueError("phase-specific presence vector mismatch")
    return PhaseGuardState(
        normalized,
        root,
        git_runner,
        branch,
        head,
        base,
        tuple((code, path, _disk_identity(root, path)) for code, path in parsed_status),
        analytical_entries,
        _digest_lines(analytical_entries),
        candidate_entries,
        expected_present,
        expected_absent,
    )


def validate_phase_guard(guard: object) -> PhaseGuardState:
    if type(guard) is not PhaseGuardState:
        raise TypeError("phase guard requires injected real disk/Git state capture")
    if (guard.branch, guard.head, guard.base) != (PINNED_BRANCH, PINNED_COMMIT, PINNED_COMMIT):
        raise ValueError("identity or analytical manifest mismatch")
    current = capture_phase_guard(guard.repo_root, guard.phase, git_runner=guard.git_runner)
    comparable_fields = (
        "branch",
        "head",
        "base",
        "status_entries",
        "analytical_entries",
        "analytical_sha256",
        "candidate_entries",
        "present_paths",
        "absent_paths",
    )
    if any(getattr(current, name) != getattr(guard, name) for name in comparable_fields):
        raise ValueError("phase guard state changed after capture")
    return current


def _preholdout_payload(identity: ReceiptFileIdentity) -> Mapping[str, object]:
    payload = loads(identity.canonical_bytes.decode("ascii"))
    if type(payload) is not dict:
        raise ValueError("preholdout receipt payload is not an object")
    return cast(Mapping[str, object], payload)


def _validate_live_phase_bindings(
    current: PhaseGuardState,
    config: FrozenConfigIdentity,
    preholdout_receipt: ReceiptFileIdentity | None = None,
    holdout_payload: Mapping[str, object] | None = None,
) -> None:
    authority = _validate_config_live_authority(current, config.payload)
    if config.payload["tracked_state_sha256"] != current.analytical_sha256:
        raise ValueError("config tracked state does not match live captured analytical state")
    expected_manifest = [
        {"path": path, "sha256": digest} for path, digest in current.analytical_entries
    ]
    if preholdout_receipt is not None:
        preholdout = _preholdout_payload(preholdout_receipt)
        if (
            preholdout["tracked_state_sha256"] != current.analytical_sha256
            or preholdout["tracked_file_manifest"] != expected_manifest
            or preholdout["spec_sha256"] != authority.spec_sha256
            or preholdout["source_sha256"] != authority.source_sha256
            or any(
                preholdout[name] != config.payload[name]
                for name in ("spec_sha256", "config_sha256", "source_sha256")
            )
        ):
            raise ValueError(
                "preholdout receipt does not match live authority and captured analytical state"
            )
    if holdout_payload is not None:
        if (
            holdout_payload["tracked_state_sha256"] != current.analytical_sha256
            or holdout_payload["spec_sha256"] != authority.spec_sha256
            or holdout_payload["source_sha256"] != authority.source_sha256
        ):
            raise ValueError(
                "holdout receipt does not match live authority and captured analytical state"
            )
        if any(
            holdout_payload[name] != config.payload[name]
            for name in ("spec_sha256", "config_sha256", "source_sha256")
        ):
            raise ValueError("holdout receipt does not cross-bind to the frozen config")
        if preholdout_receipt is not None:
            preholdout = _preholdout_payload(preholdout_receipt)
            if any(
                holdout_payload[name] != preholdout[name]
                for name in (
                    "spec_sha256",
                    "config_sha256",
                    "source_sha256",
                    "tracked_state_sha256",
                )
            ):
                raise ValueError("holdout receipt does not cross-bind to preholdout state")


def guard_config_emission(
    guard: PhaseGuardState, output: Path, *, payload: Mapping[str, object]
) -> FrozenConfigIdentity:
    current = validate_phase_guard(guard)
    if output.exists():
        raise FileExistsError(output)
    complete, canonical = _canonical_config_document(payload)
    _validate_config_live_authority(current, complete)
    if complete["tracked_state_sha256"] != current.analytical_sha256:
        raise ValueError("config tracked state does not match live captured analytical state")
    current = validate_phase_guard(guard)
    _validate_config_live_authority(current, complete)
    if complete["tracked_state_sha256"] != current.analytical_sha256:
        raise ValueError("config tracked state changed immediately before exclusive creation")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(canonical)
    try:
        identity = load_frozen_config_identity(output)
        _validate_live_phase_bindings(current, identity)
        return identity
    except Exception as error:
        raise ImmutablePostCreateStop(
            "STOP_INVALIDATED_POST_CREATE_IMMUTABLE_CONFIG",
            output,
            _file_digest(output),
        ) from error


def guard_freeze(
    guard: PhaseGuardState,
    config: FrozenConfigIdentity,
    receipt: Path,
) -> ReceiptFileIdentity:
    current = validate_phase_guard(guard)
    validated_config, _, _ = require_phase_identities(config, None, None)
    _validate_live_phase_bindings(current, validated_config)
    if receipt.exists():
        raise FileExistsError(receipt)
    payload = {
        "schema_version": PREHOLDOUT_RECEIPT_SCHEMA_VERSION,
        "spec_sha256": validated_config.payload["spec_sha256"],
        "config_sha256": validated_config.config_sha256,
        "source_sha256": validated_config.payload["source_sha256"],
        "tracked_state_sha256": current.analytical_sha256,
        "tracked_file_manifest": [
            {"path": path, "sha256": digest} for path, digest in current.analytical_entries
        ],
    }
    _validate_preholdout_receipt_schema(payload)
    current = validate_phase_guard(guard)
    _validate_live_phase_bindings(current, validated_config)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with receipt.open("xb") as stream:
        stream.write(canonical_json_bytes(payload))
    try:
        identity = load_receipt_file_identity(receipt)
        _validate_live_phase_bindings(current, validated_config, identity)
        return identity
    except Exception as error:
        raise ImmutablePostCreateStop(
            "STOP_INVALIDATED_POST_CREATE_IMMUTABLE_PREHOLDOUT_RECEIPT",
            receipt,
            _file_digest(receipt),
        ) from error


def guard_holdout_pre_receipt(
    guard: PhaseGuardState,
    receipt: Path,
    *,
    config: FrozenConfigIdentity,
    preholdout_receipt: ReceiptFileIdentity,
    receipt_payload: Mapping[str, object],
    rng_factory: Callable[[], object],
) -> HoldoutReceiptIdentity:
    del rng_factory
    current = validate_phase_guard(guard)
    validated_config, validated_preholdout, _ = require_phase_identities(
        config, preholdout_receipt, None
    )
    if validated_preholdout is None:
        raise ValueError("preholdout receipt identity is required before receipt creation")
    _validate_live_phase_bindings(current, validated_config, validated_preholdout)
    if receipt.exists():
        raise FileExistsError(receipt)
    without_hash = dict(receipt_payload)
    without_hash.pop("receipt_sha256", None)
    complete = dict(without_hash)
    complete["receipt_sha256"] = sha256(canonical_json_bytes(without_hash)).hexdigest()
    _validate_holdout_receipt_schema(complete)
    _validate_live_phase_bindings(current, validated_config, validated_preholdout, complete)
    canonical = canonical_json_bytes(complete)
    current = validate_phase_guard(guard)
    _validate_live_phase_bindings(current, validated_config, validated_preholdout, complete)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with receipt.open("xb") as stream:
        stream.write(canonical)
    try:
        identity = load_holdout_receipt_identity(receipt)
        require_phase_identities(validated_config, validated_preholdout, identity)
        _validate_live_phase_bindings(
            current,
            validated_config,
            validated_preholdout,
            identity.payload,
        )
        return identity
    except Exception as error:
        raise ImmutablePostCreateStop(
            "STOP_INVALIDATED_POST_CREATE_IMMUTABLE_HOLDOUT_RECEIPT",
            receipt,
            _file_digest(receipt),
        ) from error


def guard_holdout_post_receipt(
    guard: PhaseGuardState,
    receipt: Path,
    *,
    config: FrozenConfigIdentity,
    preholdout_receipt: ReceiptFileIdentity,
    rng_factory: Callable[[], object],
) -> str:
    try:
        current = validate_phase_guard(guard)
        holdout = load_holdout_receipt_identity(receipt)
        validated_config, validated_preholdout, validated_holdout = require_phase_identities(
            config, preholdout_receipt, holdout
        )
        if validated_preholdout is None or validated_holdout is None:
            raise ValueError("complete receipt identities are required after exposure")
        _validate_live_phase_bindings(
            current,
            validated_config,
            validated_preholdout,
            validated_holdout.payload,
        )
    except OSError, TypeError, ValueError, UnicodeError:
        return "STOP_INVALIDATED_POST_EXPOSURE"
    try:
        current = validate_phase_guard(guard)
        validated_config, validated_preholdout, validated_holdout = require_phase_identities(
            config, preholdout_receipt, holdout
        )
        if validated_preholdout is None or validated_holdout is None:
            raise ValueError("complete receipt identities are required immediately before RNG")
        _validate_live_phase_bindings(
            current,
            validated_config,
            validated_preholdout,
            validated_holdout.payload,
        )
    except OSError, TypeError, ValueError, UnicodeError:
        return "STOP_INVALIDATED_POST_EXPOSURE"
    rng_factory()
    return "CONTINUE_FROZEN_CANDIDATE"


def freeze_artifact_snapshots(output_dir: Path) -> tuple[dict[str, object], ArtifactSnapshot]:
    represented = build_artifact_manifest_document(output_dir)
    complete = artifact_snapshot(output_dir)
    return represented, complete


def _require_git_oid(value: object, *, name: str) -> str:
    if (
        type(value) is not str
        or len(value) != 40
        or value == "0" * 40
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be a lowercase Git object SHA")
    return value


def _resolve_git_common_dir(repo_root: Path, raw: str) -> Path:
    value = raw.strip()
    if not value:
        raise ValueError("Git common directory query returned an empty path")
    path = Path(value)
    resolved = (path if path.is_absolute() else repo_root / path).resolve()
    if not resolved.is_dir() or not (resolved / "objects").is_dir():
        raise ValueError("Git common directory does not expose a live object store")
    return resolved


def capture_staging_state(
    repo_root: Path, *, git_runner: Callable[[tuple[str, ...]], str]
) -> CapturedStagingState:
    root = repo_root.resolve()
    common_git_dir = _resolve_git_common_dir(root, git_runner(("rev-parse", "--git-common-dir")))
    branch = git_runner(("branch", "--show-current")).strip()
    head = _require_git_oid(git_runner(("rev-parse", "HEAD")).strip(), name="staging HEAD")
    if not branch:
        raise ValueError("staging capture requires a named branch")
    status = _parse_porcelain_status(
        git_runner(("status", "--porcelain=v1", "--untracked-files=all"))
    )
    if set(path for _, path in status) != set(STAGING_PATHS):
        raise ValueError("live candidate does not reproduce the literal staging allowlist")
    worktree_blobs = tuple(
        (
            path,
            _require_git_oid(
                git_runner(("hash-object", "--", path)).strip(),
                name=f"worktree blob {path}",
            ),
        )
        for path in STAGING_PATHS
    )
    staged_paths = tuple(
        line
        for line in git_runner(
            ("diff", "--cached", "--name-only", "--diff-filter=ACMR")
        ).splitlines()
        if line
    )
    if len(staged_paths) != len(set(staged_paths)) or any(
        path not in STAGING_PATHS for path in staged_paths
    ):
        raise ValueError("live index contains a path outside the literal staging allowlist")
    index_blobs = tuple(
        (
            path,
            _require_git_oid(
                git_runner(("rev-parse", f":{path}")).strip(),
                name=f"index blob {path}",
            ),
        )
        for path in STAGING_PATHS
        if path in staged_paths
    )
    write_tree = (
        _require_git_oid(git_runner(("write-tree",)).strip(), name="captured index tree")
        if set(staged_paths) == set(STAGING_PATHS)
        else None
    )
    return CapturedStagingState(
        root,
        common_git_dir,
        branch,
        head,
        status,
        worktree_blobs,
        index_blobs,
        write_tree,
        _STAGING_CAPTURE_TOKEN,
    )


def validate_exact_staging(
    before: CapturedStagingState,
    after: CapturedStagingState,
) -> ValidatedStagingIdentity:
    if (
        type(before) is not CapturedStagingState
        or type(after) is not CapturedStagingState
        or before._token is not _STAGING_CAPTURE_TOKEN
        or after._token is not _STAGING_CAPTURE_TOKEN
    ):
        raise TypeError("exact staging requires captured live Git/worktree state")
    if before.repo_root != after.repo_root or before.index_blobs or before.write_tree is not None:
        raise ValueError("exact staging must start from the captured empty index")
    if (
        before.common_git_dir != after.common_git_dir
        or before.branch != after.branch
        or before.head != after.head
    ):
        raise ValueError("exact staging changed repository, branch, or HEAD identity")
    if before.worktree_blobs != after.worktree_blobs:
        raise ValueError("exact staging changed a live worktree blob")
    if tuple(path for path, _ in before.worktree_blobs) != STAGING_PATHS:
        raise ValueError("captured worktree does not match the literal staging allowlist")
    if after.index_blobs != before.worktree_blobs:
        raise ValueError("live index differs from the frozen literal blob map")
    if after.write_tree is None:
        raise ValueError("exact staging did not capture the live git write-tree identity")
    if tuple(path for _, path in before.status_entries) != tuple(
        path for _, path in after.status_entries
    ):
        raise ValueError("exact staging changed the live candidate footprint")
    if any(code[1] != " " or code[0] not in {"A", "M"} for code, _ in after.status_entries):
        raise ValueError("exact staging did not produce index-only literal-path status")
    return ValidatedStagingIdentity(
        after.repo_root,
        after.common_git_dir,
        after.branch,
        after.head,
        after.index_blobs,
        after.write_tree,
        _VALIDATED_STAGING_TOKEN,
    )


def capture_publication_state(
    repo_root: Path, *, git_runner: Callable[[tuple[str, ...]], str]
) -> CapturedPublicationState:
    root = repo_root.resolve()
    common_git_dir = _resolve_git_common_dir(root, git_runner(("rev-parse", "--git-common-dir")))
    branch = git_runner(("branch", "--show-current")).strip()
    head = _require_git_oid(git_runner(("rev-parse", "HEAD")).strip(), name="HEAD")
    tree = _require_git_oid(git_runner(("rev-parse", "HEAD^{tree}")).strip(), name="HEAD tree")
    parent_line = git_runner(("rev-list", "--parents", "-n", "1", "HEAD")).strip().split()
    if not parent_line or parent_line[0] != head:
        raise ValueError("publication parent query does not identify captured HEAD")
    parents = tuple(_require_git_oid(value, name="commit parent") for value in parent_line[1:])
    local_main = _require_git_oid(
        git_runner(("rev-parse", "refs/heads/main")).strip(), name="local main"
    )
    remote_main = _require_git_oid(
        git_runner(("rev-parse", "refs/remotes/origin/main")).strip(),
        name="remote main",
    )
    return CapturedPublicationState(
        root,
        common_git_dir,
        branch,
        head,
        tree,
        parents,
        local_main,
        remote_main,
        _PUBLICATION_CAPTURE_TOKEN,
    )


def validate_publication_transition(
    transition: str,
    *,
    before: CapturedPublicationState,
    after: CapturedPublicationState,
    approved_commit: str,
    staging: ValidatedStagingIdentity,
) -> bool:
    approved_commit = _require_git_oid(approved_commit, name="approved commit")
    if (
        type(before) is not CapturedPublicationState
        or type(after) is not CapturedPublicationState
        or before._token is not _PUBLICATION_CAPTURE_TOKEN
        or after._token is not _PUBLICATION_CAPTURE_TOKEN
        or type(staging) is not ValidatedStagingIdentity
        or staging._token is not _VALIDATED_STAGING_TOKEN
        or before.common_git_dir != staging.common_git_dir
        or after.common_git_dir != staging.common_git_dir
        or approved_commit == staging.base_commit
    ):
        raise ValueError(
            "publication transition requires one captured repository/common object store"
        )
    approved_tree = _require_git_oid(staging.write_tree, name="validated staged tree")
    for label, state in (("before", before), ("after", after)):
        if type(state.branch) is not str or not state.branch:
            raise ValueError(f"{label} publication branch must be a live named ref")
        _require_git_oid(state.head, name=f"{label} HEAD")
        _require_git_oid(state.tree, name=f"{label} tree")
        _require_git_oid(state.local_main, name=f"{label} local main")
        _require_git_oid(state.remote_main, name=f"{label} remote main")
        for parent in state.parents:
            _require_git_oid(parent, name=f"{label} parent")
    base = _require_git_oid(staging.base_commit, name="validated staging base")
    if transition == "commit":
        valid = (
            before.repo_root == staging.repo_root
            and after.repo_root == staging.repo_root
            and before.branch == staging.goal_branch
            and before.head == base
            and before.local_main == base
            and before.remote_main == base
            and after.branch == staging.goal_branch
            and after.head == approved_commit
            and after.tree == approved_tree
            and after.parents == (base,)
            and after.local_main == base
            and after.remote_main == base
        )
    elif transition == "merge":
        valid = (
            before.repo_root == after.repo_root
            and before.repo_root != staging.repo_root
            and before.branch == "main"
            and (before.head, before.local_main, before.remote_main) == (base, base, base)
            and after.branch == "main"
            and after.head == approved_commit
            and after.local_main == approved_commit
            and after.remote_main == base
            and after.tree == approved_tree
            and after.parents == (base,)
        )
    elif transition == "push":
        valid = (
            before.repo_root == after.repo_root
            and before.repo_root != staging.repo_root
            and before.branch == "main"
            and before.head == approved_commit
            and before.local_main == approved_commit
            and before.remote_main == base
            and before.tree == approved_tree
            and before.parents == (base,)
            and after.branch == "main"
            and after.head == approved_commit
            and after.tree == approved_tree
            and after.parents == (base,)
            and after.local_main == approved_commit
            and after.remote_main == approved_commit
        )
    else:
        valid = False
    if not valid:
        raise ValueError(
            "publication ref/parent transition does not match the validated staged tree"
        )
    return True


def supersession_record(parent: bytes, *, target_lines: tuple[int, int]) -> bytes:
    lines = parent.splitlines(keepends=True)
    start, end = target_lines
    if start < 1 or end > len(lines) or start > end:
        raise ValueError("invalid supersession target")
    target_sha = sha256(b"".join(lines[start - 1 : end])).hexdigest()
    return (
        f"parent_line_count: {len(lines)}\n"
        f"parent_byte_count: {len(parent)}\n"
        f"parent_sha256: {sha256(parent).hexdigest()}\n"
        f"target_lines: {start}-{end}\n"
        f"target_sha256: {target_sha}\n"
        "status: superseded_pending_amendment\n"
    ).encode("ascii")


def validate_supersession_record(
    parent: bytes, record: bytes, *, target_lines: tuple[int, int]
) -> None:
    if record != supersession_record(parent, target_lines=target_lines):
        raise ValueError("supersession record does not bind the live parent and target")


def assert_receipt_immutable(identity: HoldoutReceiptIdentity, path: Path) -> None:
    if path != identity.path or path.read_bytes() != identity.canonical_bytes:
        raise ValueError("holdout receipt changed after exposure")
    loaded = load_holdout_receipt_identity(path)
    if loaded != identity:
        raise ValueError("holdout receipt identity changed")


def validate_task6_command(command: Sequence[str]) -> None:
    resolve_non_generative_command(command)


def terminal_record_count(log_bytes: bytes) -> int:
    count = 0
    for line in log_bytes.splitlines():
        try:
            value = loads(line.decode("utf-8"))
        except UnicodeError, ValueError:
            continue
        if isinstance(value, Mapping) and value.get("record_type") == TERMINAL_RECORD_TYPE:
            count += 1
    return count


def terminal_attestation_payload(before: ProvenanceEnvelope) -> bytes:
    if type(before) is not ProvenanceEnvelope:
        raise TypeError("terminal attestation requires a captured provenance envelope")
    if terminal_record_count(before.log_bytes) != 0:
        raise ValueError("terminal attestation is exact-once and cannot be recursively parented")
    if before.log_bytes and not before.log_bytes.endswith(b"\n"):
        raise ValueError("terminal attestation parent must end at a complete Log line")
    return post_exposure_log_payload(
        before,
        record_type=TERMINAL_RECORD_TYPE,
        disposition="ACCEPT",
    )


def _terminal_mapping_transition(
    before: tuple[tuple[str, str], ...],
    after: tuple[tuple[str, str], ...],
    *,
    log_relative: str,
) -> bool:
    before_map = dict(before)
    after_map = dict(after)
    return (
        set(before_map) == set(after_map)
        and log_relative in before_map
        and before_map[log_relative] != after_map[log_relative]
        and all(before_map[path] == after_map[path] for path in before_map if path != log_relative)
    )


def _validate_terminal_after(
    before: ProvenanceEnvelope,
    after: ProvenanceEnvelope,
    *,
    expected_log: bytes,
) -> None:
    log_relative = f"{GOAL_DIRECTORY}/Log.md"
    immutable_fields = (
        "repo_root",
        "branch",
        "head",
        "base",
        "tracked",
        "unstaged",
        "untracked",
        "analytical_entries",
        "candidate_entries",
        "preholdout_receipt_file_sha256",
        "receipt_sha256",
        "holdout_receipt_file_sha256",
        "config_sha256",
        "config_file_sha256",
        "represented_artifact_set_sha256",
        "artifact_set_sha256",
    )
    if any(getattr(before, name) != getattr(after, name) for name in immutable_fields):
        raise ValueError("terminal attestation changed a non-Log envelope member")
    if after.log_bytes != expected_log or terminal_record_count(after.log_bytes) != 1:
        raise ValueError("terminal attestation Log bytes are not one durable terminal record")
    if not _terminal_mapping_transition(
        before.staged, after.staged, log_relative=log_relative
    ) or not _terminal_mapping_transition(
        before.cached_entries, after.cached_entries, log_relative=log_relative
    ):
        raise ValueError("terminal attestation did not update the exact Log index/cached blob")
    if dict(after.staged)[log_relative] != dict(after.cached_entries)[log_relative]:
        raise ValueError("terminal attestation staged and cached Log blobs disagree")
    before_status = dict((path, code) for code, path in before.status_entries)
    after_status = dict((path, code) for code, path in after.status_entries)
    if (
        set(before_status) != set(after_status)
        or log_relative not in after_status
        or after_status[log_relative] not in {"A ", "M "}
        or any(
            before_status[path] != after_status[path]
            for path in before_status
            if path != log_relative
        )
    ):
        raise ValueError("terminal attestation porcelain status transition is not literal")


def apply_terminal_attestation(
    log_path: Path,
    before: ProvenanceEnvelope,
    payload: bytes,
    *,
    reviewed_payload: bytes,
    capture_envelope: Callable[[], ProvenanceEnvelope],
    stage_log: Callable[[Path], None],
) -> ProvenanceEnvelope:
    if payload != reviewed_payload or payload != terminal_attestation_payload(before):
        raise ValueError("terminal attestation must be reviewed and appended exactly once")
    expected_path = (before.repo_root.resolve() / GOAL_DIRECTORY / "Log.md").absolute()
    if log_path.is_symlink() or log_path.absolute() != expected_path:
        raise ValueError("terminal attestation requires the exact canonical Goal 023 Log path")
    observed_before = capture_envelope()
    if (
        type(observed_before) is not ProvenanceEnvelope
        or observed_before != before
        or log_path.read_bytes() != before.log_bytes
        or terminal_record_count(before.log_bytes) != 0
    ):
        raise ValueError("terminal attestation requires the observed unchanged Log/index envelope")
    with log_path.open("ab") as stream:
        stream.write(payload)
    expected_log = before.log_bytes + payload
    try:
        if log_path.read_bytes() != expected_log or terminal_record_count(expected_log) != 1:
            raise ValueError("terminal attestation append was not observed exactly once")
        stage_log(log_path)
        observed_after = capture_envelope()
        if type(observed_after) is not ProvenanceEnvelope:
            raise TypeError("terminal attestation requires a captured post-append envelope")
        _validate_terminal_after(before, observed_after, expected_log=expected_log)
        return observed_after
    except Exception as error:
        raise ImmutableTerminalStop(
            "STOP_INVALIDATED_TERMINAL_ATTESTATION_IMMUTABLE",
            log_path,
            _file_digest(log_path),
        ) from error


def validate_prefreeze_hook_noop(before: ProvenanceEnvelope, after: ProvenanceEnvelope) -> None:
    if envelope_changes(before, after):
        raise ValueError("mutating hook returns candidate to pre-freeze RED-GREEN work")


def dispatch_fixture_calibration(
    *, workers: int, output_dir: Path, services: Mapping[str, object]
) -> dict[str, object]:
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError("workers must be an integer from 1 through 8")
    if set(services) != {"run_fixture_tasks"}:
        raise TypeError("fixture calibration accepts only the owned fixture task service")
    service = services["run_fixture_tasks"]
    if type(service) is not FixtureTaskService or service._token is not _FIXTURE_TASK_SERVICE_TOKEN:
        raise TypeError("fixture calibration requires the owned fixture task service")
    before_paths = _fixture_directory_snapshot(output_dir)
    result = service.run(workers=workers, output_dir=output_dir)
    if type(result) is not dict:
        raise TypeError("fixture task service must return a dictionary")
    after_paths = _fixture_directory_snapshot(output_dir)
    if (
        before_paths != after_paths
        or result != FIXTURE_ZERO_COUNTERS
        or result.get("scientific_rows") not in (None, (), [])
        or result.get("holdout_payload") is not None
    ):
        raise ValueError("fixture calibration performed an observed forbidden side effect")
    return dict(FIXTURE_ZERO_COUNTERS)


def _fixture_directory_snapshot(output_dir: Path) -> tuple[tuple[str, str], ...]:
    if not output_dir.exists():
        return ()
    return tuple(
        (path.relative_to(output_dir).as_posix(), _file_digest(path))
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and not path.is_symlink()
    )
