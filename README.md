# Modelling disease transmission: agent-based vs compartmental

A from-scratch study of how infectious disease spreads under three different
transmission mechanisms — **waterborne, airborne and direct contact** — comparing
a spatial **agent-based random-walk (Monte Carlo)** simulation against a family of
**compartmental models (SIR, SIRB, SIRD, SIRDV, SEAIQR)**, and testing which model
suits which mechanism using real historical outbreaks.

Built for the *Physics of Living Systems* module (team project, 2025).
Stack: Python, NumPy, SciPy, Matplotlib, pandas.

## The idea

A plain SIR model can be *fitted* to almost any epidemic curve, but it cannot say
which intervention will work or why. This project argues that the right model is
the one whose structure mirrors the real transmission mechanism, and backs the
argument with three case studies plus a synthesis that pits one intervention
against all three mechanisms.

| folder | transmission | outbreak | models | key intervention |
|---|---|---|---|---|
| `waterborne/` | environmental reservoir | Cholera, Peru 1991 (real PAHO data) | SIR, **SIRB** | sanitation / water treatment |
| `airborne/` | respiratory / proximity | COVID-19 first wave, UK 2020 (real OWID data) | **SIRD ± lockdown, SIRDV, SEAIQR** | vaccination, lockdown, quarantine |
| `direct_contact/` | close contact | Ebola, West Africa 2014–16 (real WHO data) | SIRD, **SEAIQR** | rapid case isolation |
| `conclusion/` | — | cross-cutting synthesis | all of the above | — |

## Repository layout

```
simulation/                 shared toolkit, imported by every case study
  agents.py                 agent states + vectorised population store
  grid.py                   random-walk Monte Carlo engine (3 mechanisms)
  compartmental.py          SIR / SIRB / SIRD / SIRDV / SEAIQR (ODEs)
  interventions.py          lockdown / vaccination / quarantine
  metrics.py                R0, attack rate, peak, fit error, timing tools
  plotting.py               one house style for every figure

waterborne/cholera_peru/    notebook + data/ + notes.md
airborne/covid/             notebook + data/ + notes.md
direct_contact/ebola/       notebook + data/ + notes.md
conclusion/                 synthesis.ipynb + conclusions.md

references.md               Vancouver references, keyed to # [n] in the code
requirements.txt
```

Each case-study notebook imports the shared `simulation` package, runs its
outbreak, validates against the reported data, and ends with a short read-out.
The prose write-ups live in the per-folder `notes.md` and in
`conclusion/conclusions.md`.

## Running it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook        # then open any case-study notebook
```

The notebooks locate the shared package automatically (they walk up to the repo
root), so they can be run from their own folders in any order.

## Headline findings

- **Model structure has to match the mechanism.** Cholera needs the environmental
  reservoir (SIRB) for WASH interventions to have anywhere to act; Ebola needs the
  exposed compartment (SEAIQR) or a naive SIRD peaks months too early.
- **Interventions are not interchangeable.** Lockdown is a time-varying contact
  rate, vaccination is a new compartment, quarantine needs latent + asymptomatic
  structure — and a temporary lockdown only delays the peak while a sustained one
  suppresses it.
- **The same measure, three outcomes.** Isolating 60% of cases cuts the attack
  rate ~55% (waterborne) and ~43% (direct contact) but only ~9% (airborne),
  because an airborne source keeps transmitting from wherever it is isolated.
- The agent-based and compartmental approaches agree on epidemic shape, R0 and
  the ordering of interventions, which cross-validates both.

## A note on the data

All three case studies use **real data**, and each notebook criticises how well
the model actually reproduces it:

- **COVID-19** — Our World in Data, UK first wave (daily confirmed cases);
  criticised for being a 7-day-averaged, testing-limited undercount.
- **Cholera** — PAHO/WHO 1991 cumulative situation-report milestones.
- **Ebola** — seven cumulative milestones, each taken from a primary WHO Disease
  Outbreak News / ECDC epidemiological update (source URLs in `data/README.md`).

For cholera and Ebola, national weekly incidence was not available, so the
simulations are compared to the reported **cumulative counts at each report
date** — the approach the data supports. Every `data/README.md` records the exact
figures and their sources.
