"""Agent states and the population data store used by the ABM engine.

The random-walk model tracks tens of thousands of individuals, so the
population is held as a small bundle of NumPy arrays (structure-of-arrays)
rather than a list of Python objects. This keeps every per-step operation
vectorisable while still reading like the biology.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

import numpy as np


class State(IntEnum):
    """Disease states an agent can hold on the grid.

    Integer values double as row indices when we tally the population, so the
    ordering here also fixes the ordering of the returned time series.
    """

    SUSCEPTIBLE = 0
    INFECTIOUS = 1
    RECOVERED = 2
    DEAD = 3
    VACCINATED = 4


# convenient short aliases (used heavily inside the hot loop)
S = State.SUSCEPTIBLE
I = State.INFECTIOUS
R = State.RECOVERED
D = State.DEAD
V = State.VACCINATED

STATE_LABELS = {
    State.SUSCEPTIBLE: "Susceptible",
    State.INFECTIOUS: "Infectious",
    State.RECOVERED: "Recovered",
    State.DEAD: "Dead",
    State.VACCINATED: "Vaccinated",
}


@dataclass
class Population:
    """Structure-of-arrays container for one grid population.

    Attributes
    ----------
    x, y
        Integer lattice coordinates of every agent, shape (n_agents,).
    state
        Current :class:`State` of every agent, shape (n_agents,).
    infected_for
        Number of steps each agent has been infectious (0 otherwise). Used to
        drive recovery/quarantine timers without a per-agent Python object.
    """

    x: np.ndarray
    y: np.ndarray
    state: np.ndarray
    infected_for: np.ndarray

    @classmethod
    def seeded(
        cls,
        n_agents: int,
        grid_size: int,
        n_infected: int,
        rng: np.random.Generator,
    ) -> "Population":
        """Scatter ``n_agents`` uniformly on the lattice and seed the outbreak."""
        x = rng.integers(0, grid_size, size=n_agents)
        y = rng.integers(0, grid_size, size=n_agents)
        state = np.full(n_agents, State.SUSCEPTIBLE, dtype=np.int8)

        seed_idx = rng.choice(n_agents, size=n_infected, replace=False)
        state[seed_idx] = State.INFECTIOUS

        infected_for = np.zeros(n_agents, dtype=np.int32)
        return cls(x=x, y=y, state=state, infected_for=infected_for)

    def __len__(self) -> int:
        return self.state.size

    def counts(self) -> np.ndarray:
        """Return the tally of each :class:`State`, length ``len(State)``."""
        return np.bincount(self.state, minlength=len(State))

    def mask(self, state: State) -> np.ndarray:
        """Boolean mask selecting every agent in ``state``."""
        return self.state == state