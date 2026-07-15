# Modelling disease transmission: agent-based and compartmental approaches

This repository compares two ways of simulating an epidemic. The first is a
spatial agent-based random walk (a Monte Carlo simulation on a lattice); the
second is a family of compartmental ODE models (SIR, SIRB, SIRD, SIRDV, SEAIQR).
Using three real historical outbreaks, it examines which compartmental model is
appropriate for each of three transmission mechanisms: waterborne, airborne, and
direct contact.

Coursework for the Physics of Living Systems module (team project, 2025).
Written in Python with NumPy, SciPy, Matplotlib and pandas.

## Motivation

A compartmental model can be fitted to almost any epidemic curve, so a good fit
is not on its own evidence that the model is the right one. The question that
matters in practice, which intervention will work and why, depends on whether the
model's structure reflects the actual route of transmission. The three case
studies develop this point, and the final synthesis tests it directly by applying
one intervention across all three mechanisms.

## Case studies

| directory | transmission | outbreak | models | main intervention |
|---|---|---|---|---|
| `waterborne/` | environmental reservoir | Cholera, Peru 1991 (PAHO data) | SIR, SIRB | sanitation / water treatment |
| `airborne/` | respiratory | COVID-19 first wave, UK 2020 (OWID data) | SIRD, SIRDV, SEAIQR | vaccination, lockdown, quarantine |
| `direct_contact/` | close contact | Ebola, West Africa 2014–16 (WHO data) | SIRD, SEAIQR | case isolation |
| `conclusion/` | — | cross-cutting synthesis | all of the above | — |

## Repository structure

```
simulation/                 shared package, imported by every case study
  agents.py                 agent states and the vectorised population store
  grid.py                   random-walk Monte Carlo engine (three mechanisms)
  compartmental.py          SIR / SIRB / SIRD / SIRDV / SEAIQR (ODEs)
  interventions.py          lockdown, vaccination, quarantine
  metrics.py                R0, attack rate, peak, fit error, timing helpers
  plotting.py               shared figure style

waterborne/cholera_peru/    notebook, data/, notes.md
airborne/covid/             notebook, data/, notes.md
direct_contact/ebola/       notebook, data/, notes.md
conclusion/                 synthesis.ipynb, conclusions.md

references.md               Vancouver references, keyed to the # [n] markers in the code
requirements.txt
```

Each case-study notebook imports the shared `simulation` package, runs its
outbreak, compares the result against the reported data, and closes with a short
discussion. The longer write-ups are in the per-folder `notes.md` files and in
`conclusion/conclusions.md`.

## Requirements and usage

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

The notebooks find the shared package by walking up to the repository root, so
they can be run from their own folders and in any order.

## Methods

The agent-based model places individuals on a periodic lattice and moves them by
a random walk. Three infection rules are implemented: direct contact requires
sharing a cell, airborne transmission acts within a radius, and waterborne
transmission is mediated by a shed-and-decay environmental reservoir with a
saturating dose-response. Averaging over independent replicates gives the Monte
Carlo estimate of the epidemic curve.

The compartmental models share one base class and are integrated with
`scipy.integrate.solve_ivp`. Each carries a closed-form basic reproduction number
derived by the next-generation-matrix method, so R0 is never hard-coded. Lockdown
enters as a time-varying contact rate, while vaccination and quarantine require
their own compartments (SIRDV and SEAIQR respectively).

## Results

The main results are consistent across the three case studies:

- The model has to match the mechanism. Cholera needs the environmental reservoir
  of SIRB before sanitation and water treatment can be represented at all; Ebola
  needs the latent compartment of SEAIQR, without which a naive SIRD reproduces
  the reproduction number but not the months-long timescale.
- Interventions are not interchangeable switches. Lockdown is a temporary
  reduction in contact rate, vaccination removes susceptibles into a new
  compartment, and quarantine acts on the reproduction number through case
  isolation. A temporary lockdown delays the peak; a sustained one suppresses it.
- The synthesis applies the same measure, isolating 60% of cases, to all three
  agent-based mechanisms. It removes roughly 55% of the attack rate for waterborne
  and 43% for direct contact, but only about 9% for airborne, because an isolated
  airborne source keeps infecting nearby agents.

The agent-based and compartmental approaches agree on epidemic shape, on R0, and
on the ordering of interventions, which is the main check of each against the
other.

## Data

Each case study is validated against real surveillance data:

- COVID-19: Our World in Data, UK first wave, daily confirmed cases.
- Cholera: PAHO/WHO 1991 cumulative situation-report figures.
- Ebola: cumulative case and death counts from WHO Disease Outbreak News and ECDC
  epidemiological updates.

National weekly incidence was not available for cholera or Ebola, so those
simulations are compared against the reported cumulative counts at each report
date. The notebooks are explicit about what the data cannot show: confirmed cases
undercount true infections, and a single well-mixed model cannot capture the
geographic spread that drove the later stages of both epidemics. Each
`data/README.md` lists the exact figures and their sources.
