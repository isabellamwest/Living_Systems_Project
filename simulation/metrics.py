"""Outbreak summary statistics, model-fit measures and timing helpers.

Kept model-agnostic: everything here works on plain time series (a NumPy array
or a pandas Series), so the same functions score the ABM, the ODE models and the
real data on equal footing.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Iterator

import numpy as np
import pandas as pd


class ModelError(Exception):
    """Raised when a series is malformed or two series cannot be compared."""


# --------------------------------------------------------------- timing tools
def timed(func: Callable) -> Callable:
    """Decorator: print how long ``func`` took. Handy for the profiling notes."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timing] {func.__name__} took {elapsed:.3f} s")
        return result

    return wrapper


@contextmanager
def timing(label: str = "block") -> Iterator[None]:
    """Context manager version of :func:`timed` for arbitrary code blocks."""
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"[timing] {label} took {time.perf_counter() - start:.3f} s")


# ----------------------------------------------------------- outbreak metrics
@dataclass
class OutbreakSummary:
    """Headline numbers describing a single epidemic curve."""

    peak_value: float
    peak_time: float
    attack_rate: float
    final_size: float

    def as_series(self) -> pd.Series:
        return pd.Series(self.__dict__)


def _as_array(series) -> np.ndarray:
    arr = np.asarray(series, dtype=float)
    if arr.ndim != 1:
        raise ModelError(f"expected a 1-D series, got shape {arr.shape}")
    return arr


def peak(infectious, times=None) -> tuple[float, float]:
    """Return (peak value, time of peak) of an infectious-prevalence curve."""
    infectious = _as_array(infectious)
    k = int(np.argmax(infectious))
    peak_time = float(k if times is None else np.asarray(times)[k])
    return float(infectious[k]), peak_time


def attack_rate(susceptible, population: float) -> float:
    """Fraction of the population ever infected = 1 - S_end / N."""
    susceptible = _as_array(susceptible)
    return 1.0 - susceptible[-1] / population


def final_size(recovered, deaths=None) -> float:
    """Cumulative number removed by the end of the outbreak (R + D)."""
    total = _as_array(recovered)[-1]
    if deaths is not None:
        total += _as_array(deaths)[-1]
    return float(total)


def summarise(susceptible, infectious, recovered, population, deaths=None,
              times=None) -> OutbreakSummary:
    """Bundle the four headline metrics for one outbreak."""
    peak_value, peak_time = peak(infectious, times)
    return OutbreakSummary(
        peak_value=peak_value,
        peak_time=peak_time,
        attack_rate=attack_rate(susceptible, population),
        final_size=final_size(recovered, deaths),
    )


# --------------------------------------------------------------- fit measures
def rmse(model, observed) -> float:
    """Root-mean-square error between a model curve and observed data.

    The two series are aligned by resampling the (usually finer) model curve
    onto the observed sampling points before comparison.
    """
    model = _as_array(model)
    observed = _as_array(observed)
    if model.size != observed.size:
        grid_obs = np.linspace(0.0, 1.0, observed.size)
        grid_mod = np.linspace(0.0, 1.0, model.size)
        model = np.interp(grid_obs, grid_mod, model)
    return float(np.sqrt(np.mean((model - observed) ** 2)))


def normalised_rmse(model, observed) -> float:
    """RMSE divided by the mean of the observations (scale-free goodness of fit)."""
    observed = _as_array(observed)
    denom = np.mean(observed)
    if denom == 0:
        raise ModelError("cannot normalise against all-zero observations")
    return rmse(model, observed) / denom


def r0_from_growth(infectious, gamma: float, window: slice = slice(1, 10),
                   dt: float = 1.0) -> float:
    """Empirical R0 for the ABM from the early exponential growth rate.

    Fits a straight line to ``log I`` over the early ``window`` to get the
    growth rate r, then uses the SIR relation ``R0 = 1 + r / gamma``. This is
    deliberately the simple estimator a student reaches for first; it is only
    valid while the population is still almost entirely susceptible.
    """
    infectious = _as_array(infectious)
    segment = infectious[window]
    steps = np.arange(segment.size) * dt
    positive = segment > 0
    if positive.sum() < 2:
        raise ModelError("not enough non-zero points to estimate growth")
    slope = np.polyfit(steps[positive], np.log(segment[positive]), 1)[0]
    return 1.0 + slope / gamma


# ---------------------------------------------------------------- table maker
def comparison_table(rows: dict[str, OutbreakSummary]) -> pd.DataFrame:
    """Stack several :class:`OutbreakSummary` objects into one labelled table."""
    return pd.DataFrame({name: s.as_series() for name, s in rows.items()}).T
