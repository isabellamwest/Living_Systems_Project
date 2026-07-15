"""Shared modelling toolkit for the epidemic transmission project.

The package is deliberately split so that every case study (waterborne,
airborne, direct-contact) imports the *same* engine and only supplies its own
parameters and data:

    agents          agent state definitions and the vectorised population store
    grid            random-walk Monte Carlo (agent-based) engine
    compartmental   SIR / SIRB / SIRD / SIRDV / SEAIQR ODE models
    interventions   lockdown, vaccination and quarantine
    metrics         R0, attack rate, peak, fit error, timing helpers
    plotting        one consistent house style for every figure
"""
from . import agents, compartmental, grid, interventions, metrics, plotting

__all__ = [
    "agents",
    "compartmental",
    "grid",
    "interventions",
    "metrics",
    "plotting",
]

__version__ = "1.0"
