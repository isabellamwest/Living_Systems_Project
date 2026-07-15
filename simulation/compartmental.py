"""Compartmental (mean-field) epidemic models.

These are the deterministic counterpart to the agent-based engine: instead of
tracking individuals they track the *fraction* of the population in each
compartment through a system of ODEs, integrated with SciPy. Every model shares
one base class so they can be swapped freely in the case-study notebooks and
compared against the ABM and the real data.

Models
------
    SIR       classic susceptible-infectious-recovered                     # [1]
    SIRB      SIR + environmental bacterial reservoir (cholera)            # [2]
    SIRD      SIR + disease-induced death
    SIRDV     SIRD + leaky vaccination
    SEAIQR    exposed + asymptomatic + quarantine structure

Every model exposes a closed-form basic reproduction number ``r0()`` derived
with the next-generation-matrix method, so the notebooks never have to hard-code
one.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp


class CompartmentalModel(ABC):
    """Base class handling integration; subclasses supply the biology."""

    #: human-readable names of the compartments, in state-vector order
    compartments: Sequence[str]

    def __init__(self, N: float) -> None:
        self.N = float(N)
        # lockdown and other time-varying contact changes hook in here; the
        # default is a constant scaling of 1.0 (no intervention).
        self.contact_scaling: Callable[[float], float] = lambda t: 1.0

    # ------------------------------------------------------------ to override
    @abstractmethod
    def derivatives(self, t: float, y: np.ndarray) -> np.ndarray:
        """Right-hand side of the ODE system."""

    @abstractmethod
    def r0(self) -> float:
        """Basic reproduction number at the disease-free equilibrium."""

    # ------------------------------------------------------------- integration
    def simulate(
        self,
        y0: Sequence[float],
        t_end: float,
        n_points: int = 400,
    ) -> pd.DataFrame:
        """Integrate from ``y0`` over ``[0, t_end]`` and return a tidy frame.

        The returned :class:`pandas.DataFrame` is indexed by time and has one
        column per compartment, which is what the plotting and metric helpers
        expect throughout the project.
        """
        t_eval = np.linspace(0.0, t_end, n_points)
        solution = solve_ivp(
            self.derivatives,
            (0.0, t_end),
            list(y0),
            t_eval=t_eval,
            method="RK45",
            rtol=1e-8,
            atol=1e-8,
        )
        if not solution.success:                                  # pragma: no cover
            raise RuntimeError(f"integration failed: {solution.message}")
        frame = pd.DataFrame(solution.y.T, columns=list(self.compartments))
        frame.insert(0, "t", solution.t)
        return frame.set_index("t")


# --------------------------------------------------------------------------- SIR
@dataclass
class SIRParams:
    beta: float      # effective contact rate
    gamma: float     # recovery rate (1 / infectious period)


class SIR(CompartmentalModel):
    """Textbook density-dependent SIR model. # [1]"""

    compartments = ("S", "I", "R")

    def __init__(self, params: SIRParams, N: float) -> None:
        super().__init__(N)
        self.p = params

    def derivatives(self, t: float, y: np.ndarray) -> np.ndarray:
        S, I, R = y
        beta = self.p.beta * self.contact_scaling(t)
        new_infections = beta * S * I / self.N
        return np.array([
            -new_infections,
            new_infections - self.p.gamma * I,
            self.p.gamma * I,
        ])

    def r0(self) -> float:
        return self.p.beta / self.p.gamma


# -------------------------------------------------------------------------- SIRB
@dataclass
class SIRBParams:
    beta: float      # uptake rate from the reservoir
    gamma: float     # recovery rate
    xi: float        # shedding rate of bacteria by the infectious   # [2]
    delta: float     # bacterial decay rate in the environment       # [2]
    kappa: float     # half-saturation dose (50% infection)          # [2]


class SIRB(CompartmentalModel):
    """SIR with an explicit environmental reservoir B (cholera). # [2]

    Force of infection saturates with dose: ``lambda = beta * B / (kappa + B)``.
    """

    compartments = ("S", "I", "R", "B")

    def __init__(self, params: SIRBParams, N: float) -> None:
        super().__init__(N)
        self.p = params

    def derivatives(self, t: float, y: np.ndarray) -> np.ndarray:
        S, I, R, B = y
        beta = self.p.beta * self.contact_scaling(t)
        force = beta * B / (self.p.kappa + B)
        new_infections = force * S
        return np.array([
            -new_infections,
            new_infections - self.p.gamma * I,
            self.p.gamma * I,
            self.p.xi * I - self.p.delta * B,
        ])

    def r0(self) -> float:
        # next-generation matrix over (I, B) linearised at B -> 0   # [2]
        p = self.p
        return (p.beta * p.xi * self.N) / (p.kappa * p.gamma * p.delta)


# -------------------------------------------------------------------------- SIRD
@dataclass
class SIRDParams:
    beta: float
    gamma: float     # recovery rate
    mu: float        # disease-induced death rate


class SIRD(CompartmentalModel):
    """SIR with a fatal outcome, splitting removals into R and D."""

    compartments = ("S", "I", "R", "D")

    def __init__(self, params: SIRDParams, N: float) -> None:
        super().__init__(N)
        self.p = params

    def derivatives(self, t: float, y: np.ndarray) -> np.ndarray:
        S, I, R, D = y
        beta = self.p.beta * self.contact_scaling(t)
        new_infections = beta * S * I / self.N
        return np.array([
            -new_infections,
            new_infections - (self.p.gamma + self.p.mu) * I,
            self.p.gamma * I,
            self.p.mu * I,
        ])

    def r0(self) -> float:
        return self.p.beta / (self.p.gamma + self.p.mu)


# ------------------------------------------------------------------------- SIRDV
@dataclass
class SIRDVParams:
    beta: float
    gamma: float
    mu: float
    nu: float          # per-capita vaccination rate of susceptibles
    efficacy: float    # vaccine efficacy in [0, 1]; leaky if < 1


class SIRDV(CompartmentalModel):
    """SIRD with a rolling, leaky vaccination campaign.

    Susceptibles are vaccinated at rate ``nu``; vaccinated individuals can still
    be infected but at a reduced rate ``(1 - efficacy)``.
    """

    compartments = ("S", "V", "I", "R", "D")

    def __init__(self, params: SIRDVParams, N: float) -> None:
        super().__init__(N)
        self.p = params

    def derivatives(self, t: float, y: np.ndarray) -> np.ndarray:
        S, V, I, R, D = y
        beta = self.p.beta * self.contact_scaling(t)
        infect_S = beta * S * I / self.N
        infect_V = (1.0 - self.p.efficacy) * beta * V * I / self.N
        return np.array([
            -infect_S - self.p.nu * S,
            self.p.nu * S - infect_V,
            infect_S + infect_V - (self.p.gamma + self.p.mu) * I,
            self.p.gamma * I,
            self.p.mu * I,
        ])

    def r0(self) -> float:
        # at introduction the population is fully susceptible; vaccination acts
        # on the *effective* reproduction number as the campaign rolls out.
        return self.p.beta / (self.p.gamma + self.p.mu)


# ------------------------------------------------------------------------ SEAIQR
@dataclass
class SEAIQRParams:
    beta: float
    sigma: float       # progression rate out of exposed (1 / incubation)   # [5]
    gamma: float       # recovery rate
    rho: float         # fraction of infections that become symptomatic
    eta: float         # relative infectiousness of asymptomatics
    q: float           # isolation (quarantine) rate of symptomatic cases


class SEAIQR(CompartmentalModel):
    """Exposed + asymptomatic + quarantine model.

    Captures a latent period, a silent asymptomatic route, and case isolation --
    the structure needed to reason about quarantine as an intervention.
    """

    compartments = ("S", "E", "A", "I", "Q", "R")

    def __init__(self, params: SEAIQRParams, N: float) -> None:
        super().__init__(N)
        self.p = params

    def derivatives(self, t: float, y: np.ndarray) -> np.ndarray:
        S, E, A, I, Q, R = y
        p = self.p
        beta = p.beta * self.contact_scaling(t)
        force = beta * (I + p.eta * A) / self.N
        new_exposed = force * S
        return np.array([
            -new_exposed,
            new_exposed - p.sigma * E,
            (1.0 - p.rho) * p.sigma * E - p.gamma * A,
            p.rho * p.sigma * E - (p.gamma + p.q) * I,
            p.q * I - p.gamma * Q,
            p.gamma * (A + I + Q),
        ])

    def r0(self) -> float:
        # next-generation matrix over (E, A, I, Q); contributions from the
        # asymptomatic and symptomatic routes add.
        p = self.p
        asymptomatic = p.beta * p.eta * (1.0 - p.rho) / p.gamma
        symptomatic = p.beta * p.rho / (p.gamma + p.q)
        return asymptomatic + symptomatic
