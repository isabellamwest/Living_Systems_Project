"""Preventative measures shared across the case studies.

The three measures enter the models in structurally different ways, which is
itself part of the project's argument:

    lockdown       a *time-varying* reduction of the contact rate; it plugs into
                   any compartmental model through its ``contact_scaling`` hook
                   and into the ABM through reduced movement.                # [6]
    vaccination    a *structural* change -- it needs its own compartment, which
                   is why it lives in the SIRDV model rather than as a switch.
    quarantine     also structural (isolation flow ``q`` in SEAIQR), plus an
                   ABM version where isolated agents stop walking.

This module provides the lockdown scheduler and small helpers that make the
"with vs without" notebook comparisons read cleanly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .compartmental import CompartmentalModel


@dataclass
class Lockdown:
    """A step reduction in transmission between ``start`` and ``end``.

    ``strength`` is the fractional cut in the contact rate (0.6 => contacts fall
    to 40% of baseline while active).
    """

    start: float
    end: float | None = None
    strength: float = 0.6

    def scaling(self) -> Callable[[float], float]:
        """Return a ``contact_scaling(t)`` function for a compartmental model."""
        floor = 1.0 - self.strength

        def factor(t: float) -> float:
            if t < self.start:
                return 1.0
            if self.end is not None and t > self.end:
                return 1.0
            return floor

        return factor

    def apply_to(self, model: CompartmentalModel) -> CompartmentalModel:
        """Attach this lockdown to ``model`` and return it (for chaining)."""
        model.contact_scaling = self.scaling()
        return model


def without_intervention(model: CompartmentalModel) -> CompartmentalModel:
    """Reset a model to its unmitigated baseline."""
    model.contact_scaling = lambda t: 1.0
    return model
