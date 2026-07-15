"""One house style and a handful of reusable figures.

Centralising the styling means every case study and the final synthesis share
the same colours, fonts and layout, so the repository reads as a single piece of
work rather than five separate scripts.
"""
from __future__ import annotations

from typing import Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np

from .agents import STATE_LABELS, State

# fixed palette so a compartment is always the same colour, in every notebook
PALETTE = {
    "S": "#9ABCF2",   # susceptible  - blue
    "E": "#FFB58A",   # exposed      - orange
    "A": "#937860",   # asymptomatic - brown
    "I": "#F85F64",   # infectious   - red
    "Q": "#A695DE",   # quarantined  - purple
    "R": "#5FBD8B",   # recovered    - green
    "D": "#4A4A4A",   # dead         - grey
    "V": "#97E2E0",   # vaccinated   - teal
    "B": "#CCB974",   # reservoir    - beige
    "data": "#000000",
}

_STATE_TO_KEY = {
    State.SUSCEPTIBLE: "S",
    State.INFECTIOUS: "I",
    State.RECOVERED: "R",
    State.DEAD: "D",
    State.VACCINATED: "V",
}


def use_house_style() -> None:
    """Apply the project-wide Matplotlib defaults. Call once per notebook."""
    plt.rcParams.update({
        "figure.figsize": (8, 5),
        "figure.dpi": 110,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "font.size": 11,
        "legend.frameon": False,
    })


def _colour(name: str) -> str:
    return PALETTE.get(name, "#333333")


def plot_compartments(frame, columns: Sequence[str] | None = None, *,
                      ax=None, title: str = "", per_capita: bool = False,
                      N: float | None = None):
    """Line plot of an ODE result frame (time index, compartment columns)."""
    if ax is None:
        _, ax = plt.subplots()
    columns = list(columns or frame.columns)
    for col in columns:
        y = frame[col]
        if per_capita and N:
            y = y / N
        ax.plot(frame.index, y, label=col, color=_colour(col), lw=2)
    ax.set_xlabel("time")
    ax.set_ylabel("fraction of population" if per_capita else "individuals")
    ax.set_title(title)
    ax.legend(ncol=len(columns))
    return ax


def plot_abm_ensemble(mean: np.ndarray, std: np.ndarray, *, states=None,
                      ax=None, title: str = "", band: bool = True):
    """Mean epidemic curve per state with a +/-1 s.d. Monte Carlo band."""
    if ax is None:
        _, ax = plt.subplots()
    states = states or [State.SUSCEPTIBLE, State.INFECTIOUS, State.RECOVERED]
    steps = np.arange(mean.shape[0])
    for st in states:
        key = _STATE_TO_KEY[st]
        ax.plot(steps, mean[:, st], color=_colour(key), lw=2, label=STATE_LABELS[st])
        if band:
            ax.fill_between(
                steps,
                mean[:, st] - std[:, st],
                mean[:, st] + std[:, st],
                color=_colour(key),
                alpha=0.18,
            )
    ax.set_xlabel("step")
    ax.set_ylabel("agents")
    ax.set_title(title)
    ax.legend(ncol=len(states))
    return ax


def plot_grid_snapshot(population, grid_size: int, *, ax=None, title: str = "",
                       legend: bool = True):
    """Scatter the agents on the lattice, coloured by state.

    Pass ``legend=False`` when several snapshots share one figure-level legend,
    so the key does not sit on top of the agents.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(5, 5))
    for st, key in _STATE_TO_KEY.items():
        m = population.mask(st)
        if m.any():
            ax.scatter(population.x[m], population.y[m], s=8, color=_colour(key),
                       label=STATE_LABELS[st], alpha=0.7, edgecolors="none")
    ax.set_xlim(-1, grid_size)
    ax.set_ylim(-1, grid_size)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    ax.set_title(title)
    if legend:
        ax.legend(loc="upper right", markerscale=1.5, fontsize=8)
    return ax


def plot_model_vs_data(times_model, model_curve, times_data, data_curve, *,
                       ax=None, title: str = "", model_label: str = "model",
                       data_label: str = "reported"):
    """Overlay a model prediction on observed data (the validation plot)."""
    if ax is None:
        _, ax = plt.subplots()
    ax.plot(times_model, model_curve, color=_colour("I"), lw=2, label=model_label)
    ax.scatter(times_data, data_curve, color=_colour("data"), s=22, zorder=5,
               label=data_label)
    ax.set_xlabel("time")
    ax.set_ylabel("cases")
    ax.set_title(title)
    ax.legend()
    return ax


def plot_scenarios(scenarios: Mapping[str, tuple], *, ax=None, title: str = "",
                   ylabel: str = "infectious"):
    """Overlay several (times, curve) scenarios, e.g. with vs without lockdown."""
    if ax is None:
        _, ax = plt.subplots()
    cycle = ["#C44E52", "#4C72B0", "#55A868", "#8172B3", "#DD8452"]
    for (label, (t, curve)), colour in zip(scenarios.items(), cycle):
        ax.plot(t, curve, lw=2, label=label, color=colour)
    ax.set_xlabel("time")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    return ax
