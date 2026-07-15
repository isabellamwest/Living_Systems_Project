"""Random-walk Monte Carlo (agent-based) epidemic engine.

Every individual is an agent that performs a random walk on an ``L x L``
lattice. On each step the agent may move, may infect (or be infected by) other
agents according to the chosen transmission mechanism, and may progress out of
the infectious state (recover, or die). Running many independent replicates and
averaging gives the Monte Carlo estimate of the epidemic curve.

Three mechanisms are supported, matching the three case studies:

    'contact'     susceptible must share a cell with an infectious agent
    'airborne'    infection from any infectious agent within a fixed radius
    'waterborne'  infection mediated by a shared environmental reservoir; the
                  infectious shed bacteria into the local water and uptake
                  follows a saturating dose-response B / (kappa + B)   # [2]

The parameters below are dimensionless per-step quantities; each case study
maps them onto the biology of its outbreak.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Literal

import numpy as np

from .agents import Population, State

Mechanism = Literal["contact", "airborne", "waterborne"]


@dataclass
class ABMParams:
    """Per-step parameters for the random-walk model."""

    # transmission (interpretation depends on the mechanism)
    infect_prob: float = 0.35        # per-contact infection probability
    radius: float = 2.0              # airborne interaction radius (cells)
    shed_rate: float = 1.0           # waterborne: bacteria added per infectious agent
    decay: float = 0.30              # waterborne: fractional bacterial decay per step   # [2]
    kappa: float = 5.0               # waterborne: half-saturation dose                   # [2]

    # natural history
    recovery_prob: float = 0.10      # per-step probability an infectious agent resolves
    cfr: float = 0.0                 # case fatality ratio applied at resolution

    # movement
    step_prob: float = 0.8           # probability an agent attempts to move each step


@dataclass
class InterventionSettings:
    """ABM-side switches for the three preventative measures.

    Kept separate from :class:`ABMParams` so a case study can sweep an
    intervention on/off without touching the epidemiological parameters.
    """

    vaccinated_fraction: float = 0.0            # immunised before the outbreak
    lockdown_start: int | None = None           # step at which mixing drops
    lockdown_step_prob: float = 0.15            # reduced movement under lockdown   # [6]
    quarantine_fraction: float = 0.0            # fraction of cases isolated
    quarantine_delay: int = 3                   # steps from infection to isolation


@dataclass
class Snapshot:
    """A single frame of the simulation, yielded by :meth:`RandomWalkModel.run`."""

    t: int
    counts: np.ndarray
    population: Population
    reservoir: np.ndarray | None = None


class RandomWalkModel:
    """Agent-based random-walk epidemic on a periodic lattice."""

    def __init__(
        self,
        grid_size: int,
        n_agents: int,
        mechanism: Mechanism,
        params: ABMParams,
        interventions: InterventionSettings | None = None,
        n_infected: int = 5,
        seed: int | None = None,
    ) -> None:
        self.L = grid_size
        self.n_agents = n_agents
        self.mechanism = mechanism
        self.params = params
        self.interventions = interventions or InterventionSettings()
        self.n_infected = n_infected
        self.rng = np.random.default_rng(seed)

        self.pop = Population.seeded(n_agents, grid_size, n_infected, self.rng)
        self._apply_precampaign_vaccination()

        # environmental reservoir (only used by the waterborne mechanism)
        self.reservoir = np.zeros((grid_size, grid_size), dtype=float)
        # agents flagged for isolation, resolved after the quarantine delay
        self._isolated = np.zeros(n_agents, dtype=bool)

    # ------------------------------------------------------------------ setup
    def _apply_precampaign_vaccination(self) -> None:
        frac = self.interventions.vaccinated_fraction
        if frac <= 0:
            return
        susceptible = np.where(self.pop.mask(State.SUSCEPTIBLE))[0]
        n_vax = int(round(frac * susceptible.size))
        if n_vax:
            chosen = self.rng.choice(susceptible, size=n_vax, replace=False)
            self.pop.state[chosen] = State.VACCINATED

    # --------------------------------------------------------------- movement
    def _current_step_prob(self, t: int) -> float:
        lock = self.interventions.lockdown_start
        if lock is not None and t >= lock:
            return self.interventions.lockdown_step_prob
        return self.params.step_prob

    def _move(self, t: int) -> None:
        """Random walk with periodic boundaries; isolated agents stay put."""
        moving = self.rng.random(self.n_agents) < self._current_step_prob(t)
        moving &= ~self._isolated
        # one of the four von Neumann neighbours (0..3) chosen per moving agent
        directions = self.rng.integers(0, 4, size=self.n_agents)
        dx = np.where(moving & (directions == 0), 1, 0) + np.where(moving & (directions == 1), -1, 0)
        dy = np.where(moving & (directions == 2), 1, 0) + np.where(moving & (directions == 3), -1, 0)
        self.pop.x = (self.pop.x + dx) % self.L
        self.pop.y = (self.pop.y + dy) % self.L

    # ---------------------------------------------------------- transmission
    def _new_infections_contact(self) -> np.ndarray:
        """Person-to-person: infection needs a shared cell.

        Built by bucketing agents into their cell and, for every cell that
        holds at least one infectious and one susceptible agent, drawing
        infections. The explicit dictionary pass is easy to read and fast
        enough at the populations used here.
        """
        susceptible = self.pop.mask(State.SUSCEPTIBLE)
        infectious = self.pop.mask(State.INFECTIOUS)
        if not infectious.any():
            return np.zeros(self.n_agents, dtype=bool)

        cell_id = self.pop.x * self.L + self.pop.y
        occupants: dict[int, list[int]] = {}
        for idx in range(self.n_agents):
            occupants.setdefault(int(cell_id[idx]), []).append(idx)

        new_infection = np.zeros(self.n_agents, dtype=bool)
        p = self.params.infect_prob
        for members in occupants.values():
            members = np.asarray(members)
            n_inf = int(infectious[members].sum())
            if n_inf == 0:
                continue
            targets = members[susceptible[members]]
            if targets.size == 0:
                continue
            # probability of at least one successful contact from n_inf sources
            prob = 1.0 - (1.0 - p) ** n_inf
            hits = self.rng.random(targets.size) < prob
            new_infection[targets[hits]] = True
        return new_infection

    def _new_infections_airborne(self) -> np.ndarray:
        """Proximity route: any infectious agent within ``radius`` can infect.

        Neighbour counts come from a vectorised pairwise distance between the
        susceptible and infectious agents (with the periodic minimum-image
        convention), which is the numerically heavy part of the model.
        """
        susceptible = np.where(self.pop.mask(State.SUSCEPTIBLE))[0]
        infectious = np.where(self.pop.mask(State.INFECTIOUS))[0]
        new_infection = np.zeros(self.n_agents, dtype=bool)
        if susceptible.size == 0 or infectious.size == 0:
            return new_infection

        sx, sy = self.pop.x[susceptible], self.pop.y[susceptible]
        ix, iy = self.pop.x[infectious], self.pop.y[infectious]

        # minimum-image separation on the periodic lattice
        dx = np.abs(sx[:, None] - ix[None, :])
        dy = np.abs(sy[:, None] - iy[None, :])
        dx = np.minimum(dx, self.L - dx)
        dy = np.minimum(dy, self.L - dy)
        within = (dx * dx + dy * dy) <= self.params.radius ** 2

        n_contacts = within.sum(axis=1)
        prob = 1.0 - (1.0 - self.params.infect_prob) ** n_contacts
        hits = self.rng.random(susceptible.size) < prob
        new_infection[susceptible[hits]] = True
        return new_infection

    def _new_infections_waterborne(self) -> np.ndarray:
        """Environmental route via a shared, decaying bacterial reservoir. # [2]

        Infectious agents shed into the water at their cell; the reservoir
        decays each step; susceptibles take up infection through the saturating
        dose-response ``B / (kappa + B)``.
        """
        # decay, then shedding by the currently infectious
        self.reservoir *= (1.0 - self.params.decay)
        infectious = np.where(self.pop.mask(State.INFECTIOUS))[0]
        if infectious.size:
            np.add.at(
                self.reservoir,
                (self.pop.x[infectious], self.pop.y[infectious]),
                self.params.shed_rate,
            )

        susceptible = np.where(self.pop.mask(State.SUSCEPTIBLE))[0]
        new_infection = np.zeros(self.n_agents, dtype=bool)
        if susceptible.size == 0:
            return new_infection

        local_dose = self.reservoir[self.pop.x[susceptible], self.pop.y[susceptible]]
        dose_response = local_dose / (self.params.kappa + local_dose)     # [2]
        prob = self.params.infect_prob * dose_response
        hits = self.rng.random(susceptible.size) < prob
        new_infection[susceptible[hits]] = True
        return new_infection

    def _new_infections(self) -> np.ndarray:
        if self.mechanism == "contact":
            return self._new_infections_contact()
        if self.mechanism == "airborne":
            return self._new_infections_airborne()
        if self.mechanism == "waterborne":
            return self._new_infections_waterborne()
        raise ValueError(f"unknown mechanism: {self.mechanism!r}")

    # ------------------------------------------------------------ progression
    def _progress(self) -> None:
        """Advance infectious agents: isolate, then resolve to R or D."""
        infectious = self.pop.mask(State.INFECTIOUS)
        self.pop.infected_for[infectious] += 1

        # quarantine: a fraction of cases stop moving after a detection delay
        q = self.interventions.quarantine_fraction
        if q > 0:
            due = infectious & (self.pop.infected_for == self.interventions.quarantine_delay)
            due_idx = np.where(due)[0]
            if due_idx.size:
                isolate = self.rng.random(due_idx.size) < q
                self._isolated[due_idx[isolate]] = True

        # resolution: each infectious agent recovers (or dies) with a per-step rate
        resolving = infectious & (self.rng.random(self.n_agents) < self.params.recovery_prob)
        resolving_idx = np.where(resolving)[0]
        if resolving_idx.size:
            dies = self.rng.random(resolving_idx.size) < self.params.cfr
            self.pop.state[resolving_idx[dies]] = State.DEAD
            self.pop.state[resolving_idx[~dies]] = State.RECOVERED
            self._isolated[resolving_idx] = False

    # --------------------------------------------------------------- stepping
    def step(self, t: int) -> None:
        self._move(t)
        newly = self._new_infections()
        self.pop.state[newly] = State.INFECTIOUS
        self._progress()

    def run(self, n_steps: int) -> Iterator[Snapshot]:
        """Yield a :class:`Snapshot` at each step (state 0 first, then 1..n)."""
        reservoir = self.reservoir if self.mechanism == "waterborne" else None
        yield Snapshot(0, self.pop.counts(), self.pop, reservoir)
        for t in range(1, n_steps + 1):
            self.step(t)
            reservoir = self.reservoir if self.mechanism == "waterborne" else None
            yield Snapshot(t, self.pop.counts(), self.pop, reservoir)

    def simulate(self, n_steps: int) -> np.ndarray:
        """Run once and return the ``(n_steps + 1, len(State))`` count series."""
        return np.array([snap.counts for snap in self.run(n_steps)])


def run_ensemble(
    n_runs: int,
    n_steps: int,
    *,
    grid_size: int,
    n_agents: int,
    mechanism: Mechanism,
    params: ABMParams,
    interventions: InterventionSettings | None = None,
    n_infected: int = 5,
    base_seed: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Monte Carlo average of the epidemic curve over ``n_runs`` replicates.

    Returns the per-step mean and standard deviation of the state counts, each
    of shape ``(n_steps + 1, len(State))``. Distinct seeds keep the replicates
    independent while the whole ensemble stays reproducible from ``base_seed``.
    """
    runs = np.empty((n_runs, n_steps + 1, len(State)))
    for r in range(n_runs):
        model = RandomWalkModel(
            grid_size=grid_size,
            n_agents=n_agents,
            mechanism=mechanism,
            params=params,
            interventions=interventions,
            n_infected=n_infected,
            seed=base_seed + r,
        )
        runs[r] = model.simulate(n_steps)
    return runs.mean(axis=0), runs.std(axis=0)
