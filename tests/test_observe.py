from __future__ import annotations

import ast
import inspect
import math
from dataclasses import FrozenInstanceError
from typing import cast

import pytest

import spatext.observe as observe_module
from spatext.observe import (
    EffectiveCountRates,
    NumericalDomainError,
    effort_scaled_mean,
    poisson_log_probability,
    state_count_log_probability,
    state_rate,
)

FROZEN_MAX_STRUCTURED_EFFORT = 1.3
FROZEN_MAX_PRESENT_RATE = 10.0
TEST_LOCAL_COMPUTATIONAL_DOMAIN_LIMIT = 1_000_000_000


def test_obs_001_effective_count_rates_are_frozen_and_state_specific() -> None:
    rates = EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)

    assert state_rate(rates=rates, state=0) == pytest.approx(4.0)
    assert state_rate(rates=rates, state=1) == pytest.approx(0.15)
    with pytest.raises(FrozenInstanceError):
        rates.lambda_present = 5.0  # type: ignore[misc]


def test_obs_002_poisson_log_probability_handles_zero_count() -> None:
    assert poisson_log_probability(count=0, mean=2.5) == pytest.approx(-2.5)


def test_obs_003_poisson_log_probability_matches_positive_count_formula() -> None:
    count = 7
    mean = 3.25
    expected = count * math.log(mean) - mean - math.lgamma(count + 1)

    assert poisson_log_probability(count=count, mean=mean) == pytest.approx(expected)


def test_obs_004_effort_scales_the_rate_for_each_state() -> None:
    rates = EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)

    assert effort_scaled_mean(effort=0.5, state=0, rates=rates) == pytest.approx(2.0)
    assert effort_scaled_mean(effort=0.5, state=1, rates=rates) == pytest.approx(0.075)


def test_obs_005_state_count_log_probability_composes_rate_effort_and_count() -> None:
    rates = EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)
    mean = effort_scaled_mean(effort=0.75, state=1, rates=rates)

    assert state_count_log_probability(
        count=2,
        effort=0.75,
        state=1,
        rates=rates,
    ) == pytest.approx(poisson_log_probability(count=2, mean=mean))


@pytest.mark.parametrize(
    ("lambda_present", "lambda_quasi", "message"),
    [
        (4.0, 0.0, "lambda_quasi must be finite and positive"),
        (4.0, -0.1, "lambda_quasi must be finite and positive"),
        (4.0, math.nan, "lambda_quasi must be finite and positive"),
        (4.0, math.inf, "lambda_quasi must be finite and positive"),
        (0.0, 0.15, "lambda_present must be finite and positive"),
        (-1.0, 0.15, "lambda_present must be finite and positive"),
        (math.nan, 0.15, "lambda_present must be finite and positive"),
        (math.inf, 0.15, "lambda_present must be finite and positive"),
        (0.15, 0.15, "lambda_present must be greater than lambda_quasi"),
        (0.10, 0.15, "lambda_present must be greater than lambda_quasi"),
    ],
)
def test_obs_006_effective_count_rates_reject_invalid_values(
    lambda_present: float,
    lambda_quasi: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message) as error:
        EffectiveCountRates(
            lambda_present=lambda_present,
            lambda_quasi=lambda_quasi,
        )
    assert type(error.value) is ValueError


@pytest.mark.parametrize("effort", [0.0, -1.0, math.nan, math.inf])
def test_obs_007_effort_must_be_finite_and_positive(effort: float) -> None:
    rates = EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)

    with pytest.raises(ValueError, match="effort must be finite and positive") as error:
        effort_scaled_mean(effort=effort, state=0, rates=rates)
    assert type(error.value) is ValueError


@pytest.mark.parametrize("count", [-1, 1.5, True])
def test_obs_008_count_must_be_an_integral_nonnegative_value(count: object) -> None:
    with pytest.raises(ValueError, match="count must be a nonnegative integer") as error:
        poisson_log_probability(count=cast(int, count), mean=1.0)
    assert type(error.value) is ValueError


@pytest.mark.parametrize("mean", [0.0, -1.0, math.nan, math.inf])
def test_obs_009_poisson_mean_must_be_finite_and_positive(mean: float) -> None:
    with pytest.raises(ValueError, match="mean must be finite and positive") as error:
        poisson_log_probability(count=0, mean=mean)
    assert type(error.value) is ValueError


@pytest.mark.parametrize("state", [-1, 2, True, 0.0])
def test_obs_010_state_must_be_zero_or_one(state: object) -> None:
    rates = EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)

    with pytest.raises(ValueError, match="state must be integer 0 or 1") as error:
        state_rate(rates=rates, state=cast(int, state))
    assert type(error.value) is ValueError


def test_obs_011_valid_boundary_values_remain_numerically_stable() -> None:
    rates = EffectiveCountRates(lambda_present=0.25, lambda_quasi=0.01)
    effort = 1e-300
    expected = math.log(effort) + math.log(rates.lambda_quasi) - effort * rates.lambda_quasi

    log_probability = state_count_log_probability(
        count=1,
        effort=effort,
        state=1,
        rates=rates,
    )

    assert math.isfinite(log_probability)
    assert log_probability == pytest.approx(expected)


def test_obs_012_observation_kernel_does_not_import_synthetic_modules() -> None:
    assert _imports_spatext_synth("from spatext import synth")
    assert _imports_spatext_synth("from spatext.synth import medium")
    assert _imports_spatext_synth("import spatext.synth.medium")
    assert not _imports_spatext_synth(inspect.getsource(observe_module))


def test_obs_013_poisson_log_probability_rejects_count_above_computational_domain() -> None:
    with pytest.raises(
        ValueError,
        match="count exceeds computational-domain limit 1000000000",
    ) as error:
        poisson_log_probability(count=10**15, mean=1.0)
    _assert_numerical_domain_error(error.value)


def test_obs_014_poisson_log_probability_rejects_mean_above_computational_domain() -> None:
    with pytest.raises(
        ValueError,
        match="mean exceeds computational-domain limit 1000000000",
    ) as error:
        poisson_log_probability(count=1, mean=1_000_000_001.0)
    _assert_numerical_domain_error(error.value)


def test_obs_015_effort_scaled_mean_rejects_overflowed_product() -> None:
    rates = EffectiveCountRates(lambda_present=1e308, lambda_quasi=1e307)

    with pytest.raises(
        ValueError, match="effort-scaled mean is outside computational domain"
    ) as error:
        effort_scaled_mean(effort=10.0, state=0, rates=rates)
    _assert_numerical_domain_error(error.value)


def test_obs_016_effort_scaled_mean_rejects_underflowed_product() -> None:
    rates = EffectiveCountRates(lambda_present=0.25, lambda_quasi=0.01)

    with pytest.raises(
        ValueError, match="effort-scaled mean is outside computational domain"
    ) as error:
        effort_scaled_mean(effort=math.ulp(0.0), state=1, rates=rates)
    _assert_numerical_domain_error(error.value)


def test_obs_017_oversized_python_integer_mean_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="mean exceeds computational-domain limit 1000000000",
    ) as error:
        poisson_log_probability(count=1, mean=cast(float, 10**400))
    _assert_numerical_domain_error(error.value)


def test_obs_018_oversized_python_integer_effort_raises_value_error() -> None:
    rates = EffectiveCountRates(lambda_present=4.0, lambda_quasi=0.15)

    with pytest.raises(ValueError, match="effort exceeds float computational domain") as error:
        effort_scaled_mean(effort=cast(float, 10**400), state=0, rates=rates)
    _assert_numerical_domain_error(error.value)


@pytest.mark.parametrize(
    ("lambda_present", "lambda_quasi", "message"),
    [
        (cast(float, 10**400), 0.15, "lambda_present exceeds float computational domain"),
        (4.0, cast(float, 10**400), "lambda_quasi exceeds float computational domain"),
    ],
)
def test_obs_019_oversized_python_integer_rate_raises_value_error(
    lambda_present: float,
    lambda_quasi: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message) as error:
        EffectiveCountRates(
            lambda_present=lambda_present,
            lambda_quasi=lambda_quasi,
        )
    _assert_numerical_domain_error(error.value)


def test_obs_020_computational_domain_limit_is_accepted_with_stable_log_probability() -> None:
    count = 1_000_000_000
    mean = float(count)
    expected = -0.5 * math.log(2.0 * math.pi * count) - 1.0 / (12.0 * count)

    log_probability = poisson_log_probability(count=count, mean=mean)

    assert math.isfinite(log_probability)
    assert log_probability == pytest.approx(expected, rel=0.0, abs=1e-12)


def test_obs_021_numerical_domain_error_is_public_and_subclasses_value_error() -> None:
    exception_type = getattr(observe_module, "NumericalDomainError", None)

    assert isinstance(exception_type, type)
    assert issubclass(exception_type, ValueError)
    assert exception_type is not ValueError


def test_obs_022_invalid_scientific_parameters_are_not_numerical_domain_errors() -> None:
    with pytest.raises(ValueError, match="greater than") as ordering_error:
        EffectiveCountRates(lambda_present=0.15, lambda_quasi=0.15)
    with pytest.raises(ValueError, match="finite and positive") as nonfinite_error:
        EffectiveCountRates(lambda_present=4.0, lambda_quasi=math.inf)

    assert type(ordering_error.value) is ValueError
    assert type(nonfinite_error.value) is ValueError


def test_obs_023_domain_failures_raise_instead_of_returning_probability_sentinels() -> None:
    rates = EffectiveCountRates(lambda_present=0.25, lambda_quasi=0.01)

    with pytest.raises(ValueError) as count_error:
        poisson_log_probability(count=1_000_000_001, mean=1.0)
    with pytest.raises(ValueError) as product_error:
        effort_scaled_mean(effort=math.ulp(0.0), state=1, rates=rates)

    _assert_numerical_domain_error(count_error.value)
    _assert_numerical_domain_error(product_error.value)


def test_obs_024_frozen_exact_model_mean_is_far_inside_computational_domain() -> None:
    maximum_frozen_mean = FROZEN_MAX_STRUCTURED_EFFORT * FROZEN_MAX_PRESENT_RATE

    assert maximum_frozen_mean == pytest.approx(13.0)
    assert TEST_LOCAL_COMPUTATIONAL_DOMAIN_LIMIT / maximum_frozen_mean >= 1_000_000


def test_obs_025_source_uses_computational_domain_terminology() -> None:
    source = inspect.getsource(observe_module)

    assert "_COMPUTATIONAL_DOMAIN_LIMIT" in source
    assert "_REPRESENTABILITY_LIMIT" not in source
    assert "representable" not in source


def test_obs_026_integer_product_above_float_domain_raises_numerical_domain_error() -> None:
    rates = EffectiveCountRates(lambda_present=10**308, lambda_quasi=1)

    with pytest.raises(
        NumericalDomainError,
        match="effort-scaled mean is outside computational domain",
    ):
        effort_scaled_mean(effort=10, state=0, rates=rates)


def test_obs_027_valid_integer_product_is_returned_as_float() -> None:
    rates = EffectiveCountRates(lambda_present=10, lambda_quasi=1)

    mean = effort_scaled_mean(effort=3, state=0, rates=rates)

    assert mean == pytest.approx(30.0)
    assert type(mean) is float


def _assert_numerical_domain_error(error: BaseException) -> None:
    assert isinstance(error, ValueError)
    assert type(error).__name__ == "NumericalDomainError"


def _imports_spatext_synth(source: str) -> bool:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(
            alias.name == "spatext.synth" or alias.name.startswith("spatext.synth.")
            for alias in node.names
        ):
            return True
        if not isinstance(node, ast.ImportFrom) or node.module is None:
            continue
        if node.module == "spatext" and any(alias.name == "synth" for alias in node.names):
            return True
        if node.module == "spatext.synth" or node.module.startswith("spatext.synth."):
            return True
    return False
