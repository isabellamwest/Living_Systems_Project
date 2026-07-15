# Conclusions

## The question

The project set out to compare two ways of simulating an epidemic — an
agent-based random walk and a family of compartmental models — and to work out
which compartmental model suits which *mode* of transmission: waterborne,
airborne, and direct contact. Rather than defaulting to SIR everywhere, each
case study was chosen to expose a different piece of model structure.

## What each case study showed

**Waterborne — cholera (Peru 1991, real PAHO data).** A plain SIR can be tuned to
the cholera curve, but it hides the mechanism. The SIRB model keeps an explicit
environmental reservoir, and that reservoir is the only place where the
real-world controls act: sanitation lowers shedding, water treatment raises
bacterial decay, and an alternative water source lowers uptake. Each collapses
the attack rate in the model; none of them is even expressible in a plain SIR.
Validated against the PAHO cumulative milestones, the model with a
national-aggregate R0 ≈ 1.7 tracks the reported case counts within ~15% through
the first half of 1991, but under-predicts the year-end total — the later cases
came from geographic spread into new regions, which a single well-mixed reservoir
cannot capture (a metapopulation of coupled patches would).

**Airborne — COVID-19 (first wave, real UK data).** This is the case where all
three interventions are meaningful, and each needs different structure. Lockdown
is a time-varying contact rate — a temporary one only delays the peak, a
sustained one suppresses it. Vaccination is a new compartment (SIRDV). Quarantine
needs a latent period and an asymptomatic route (SEAIQR) to be modelled honestly,
because silent transmission sets a floor on how well isolation can do. Fitted to
the real OWID series, an *unmitigated* SIRD matches poorly (R² ≈ 0.4); adding the
actual UK lockdown date lifts it to R² ≈ 0.9 with the peak within a couple of
days of 24 April — direct evidence the intervention shaped the wave. The fit is
honest about timing and shape only: confirmed cases are a 7-day-averaged
undercount, so the model's ~50% attack rate sits well above the ~6–7% measured
seroprevalence.

**Direct contact — Ebola (West Africa 2014–16, real WHO data).** A naive SIRD
gets Ebola's R0 and rough magnitude but cannot match the *shape* of a
months-long epidemic, because it lacks the long incubation period. Restoring the
exposed compartment (SEAIQR) recovers the slow build-up: fitted to seven WHO
cumulative milestones it tracks the reported cases to ~6% and places the onset
within weeks of the real WHO notification date, against ~36% error for SIRD.
Isolation is the control lever — an isolation rate of about 0.15 pulls R0 below 1.

## The cross-cutting result

The synthesis notebook applies a single intervention — isolating 60% of cases —
across all three agent-based mechanisms:

| mechanism | attack-rate reduction from isolation |
|---|---|
| waterborne | ~55% |
| direct contact | ~43% |
| airborne | ~9% |

Isolation is powerful exactly when transmission depends on the infectious
individual moving or making contact (direct contact, and shedding into new
locations for waterborne), and weak for airborne spread, where a stationary
isolated source still infects nearby agents. The same measure, three very
different outcomes — which is the whole argument for matching model structure to
transmission mechanism.

## Agent-based vs compartmental

The two approaches agree on the headline behaviour — epidemic shape, the ordering
of interventions, and roughly where R0 sits — which is the main validation of
each against the other. They differ where it matters conceptually: the
compartmental models assume perfect mixing and give fast, smooth, repeatable
answers and closed-form reproduction numbers; the agent model relaxes mixing,
exposes spatial structure and stochastic variation between runs, and is where
"isolation stops a moving source" emerges naturally. Neither is *the* model — the
compartmental models are for quantities and interventions, the agent model is
for mechanism and space.

## Limitations and next steps

Every model here uses constant parameters and a single well-mixed population (or
one lattice). All three studies are validated against real data — OWID UK
confirmed cases, and PAHO (cholera) and WHO/ECDC (Ebola) cumulative
situation-report milestones, with the reporting caveats noted above. The obvious
extensions are seasonality (rainfall/temperature forcing for cholera),
metapopulation structure for Ebola across the three countries, behavioural
feedback for COVID-19, and formal parameter inference rather than the
single-scale fits used here.
