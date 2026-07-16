from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, log1p, pi
from sys import float_info

from scipy.special import gammaln  # type: ignore[import-untyped]

# Conservative exact-kernel boundary, far above all frozen Goal 023 counts and means.
_COMPUTATIONAL_DOMAIN_LIMIT = 1_000_000_000
_STIRLING_STABILITY_THRESHOLD = 10_000


class NumericalDomainError(ValueError):
    """Raised when an input exceeds the observation kernel's computational domain."""


@dataclass(frozen=True, slots=True)
class EffectiveCountRates:
    """Ordered effective count rates for present and quasi-extirpated states."""

    lambda_present: float
    lambda_quasi: float

    def __post_init__(self) -> None:
        _require_finite_positive(self.lambda_quasi, name="lambda_quasi")
        _require_finite_positive(self.lambda_present, name="lambda_present")
        if self.lambda_present <= self.lambda_quasi:
            raise ValueError("lambda_present must be greater than lambda_quasi")


def state_rate(*, rates: EffectiveCountRates, state: int) -> float:
    """Return the effective count rate for latent state 0 or 1."""

    _require_binary_state(state)
    return rates.lambda_present if state == 0 else rates.lambda_quasi


def effort_scaled_mean(*, effort: float, state: int, rates: EffectiveCountRates) -> float:
    """Return the Poisson mean for a known-effort latent-state opportunity."""

    _require_finite_positive(effort, name="effort")
    mean = effort * state_rate(rates=rates, state=state)
    if isinstance(mean, int):
        if mean > _COMPUTATIONAL_DOMAIN_LIMIT:
            raise NumericalDomainError(
                "effort-scaled mean is outside computational domain: must be finite, "
                f"positive, and no greater than {_COMPUTATIONAL_DOMAIN_LIMIT}"
            )
        mean = float(mean)
    if not isfinite(mean) or mean <= 0.0 or mean > _COMPUTATIONAL_DOMAIN_LIMIT:
        raise NumericalDomainError(
            "effort-scaled mean is outside computational domain: must be finite, positive, "
            f"and no greater than {_COMPUTATIONAL_DOMAIN_LIMIT}"
        )
    return mean


def poisson_log_probability(*, count: int, mean: float) -> float:
    """Return the scalar Poisson log probability for a validated count and mean."""

    _require_nonnegative_integer(count)
    if isinstance(mean, int) and mean > _COMPUTATIONAL_DOMAIN_LIMIT:
        raise NumericalDomainError(
            f"mean exceeds computational-domain limit {_COMPUTATIONAL_DOMAIN_LIMIT}"
        )
    _require_finite_positive(mean, name="mean")
    if mean > _COMPUTATIONAL_DOMAIN_LIMIT:
        raise NumericalDomainError(
            f"mean exceeds computational-domain limit {_COMPUTATIONAL_DOMAIN_LIMIT}"
        )
    if count == 0:
        return -mean
    if count >= _STIRLING_STABILITY_THRESHOLD and 0.5 * count <= mean <= 1.5 * count:
        return _stable_large_count_log_probability(count=count, mean=mean)
    return count * log(mean) - mean - float(gammaln(count + 1))


def state_count_log_probability(
    *,
    count: int,
    effort: float,
    state: int,
    rates: EffectiveCountRates,
) -> float:
    """Return the count log probability conditional on effort and latent state."""

    mean = effort_scaled_mean(effort=effort, state=state, rates=rates)
    return poisson_log_probability(count=count, mean=mean)


def _require_finite_positive(value: float, *, name: str) -> None:
    if isinstance(value, bool) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    if isinstance(value, int):
        if value > float_info.max:
            raise NumericalDomainError(f"{name} exceeds float computational domain")
        return
    if not isfinite(value):
        raise ValueError(f"{name} must be finite and positive")


def _require_nonnegative_integer(count: int) -> None:
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("count must be a nonnegative integer")
    if count > _COMPUTATIONAL_DOMAIN_LIMIT:
        raise NumericalDomainError(
            f"count exceeds computational-domain limit {_COMPUTATIONAL_DOMAIN_LIMIT}"
        )


def _require_binary_state(state: int) -> None:
    if isinstance(state, bool) or not isinstance(state, int) or state not in (0, 1):
        raise ValueError("state must be integer 0 or 1")


def _stable_large_count_log_probability(*, count: int, mean: float) -> float:
    relative_difference = (mean - count) / count
    deviance = count * _delta_minus_log1p(relative_difference)
    return -deviance - 0.5 * log(2.0 * pi * count) - _stirling_log_factorial_correction(count)


def _delta_minus_log1p(delta: float) -> float:
    if abs(delta) >= 0.125:
        return delta - log1p(delta)

    term = delta * delta
    total = term / 2.0
    for exponent in range(3, 33):
        term *= delta
        total += term / exponent if exponent % 2 == 0 else -term / exponent
    return total


def _stirling_log_factorial_correction(count: int) -> float:
    inverse = 1.0 / count
    inverse_squared = inverse * inverse
    return inverse * (
        1.0 / 12.0
        - inverse_squared
        * (1.0 / 360.0 - inverse_squared * (1.0 / 1260.0 - inverse_squared / 1680.0))
    )
