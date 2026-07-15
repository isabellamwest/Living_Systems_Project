# Direct-contact transmission — Ebola (West Africa, 2014–2016)

## Why this case study

Ebola is the clearest example of *direct-contact* transmission: infection needs
close physical contact with an infectious person or body (caregiving, funerals).
Two features shape the modelling — a long latent period that makes the epidemic
slow, and the fact that isolating cases quickly is what actually controlled it.

## Models used

- **SIRD** (naive baseline) — recovers R0 and rough magnitude, but its only
  timescale is the infectious period, so it cannot match the shape of a
  months-long epidemic.
- **SEAIQR** — adds the exposed (latent) compartment, an asymptomatic route, and
  an isolation flow `q`. The ~11-day incubation [8] gives a realistic generation
  time, so the slow build-up is reproduced.

No vaccination model: there was no deployed Ebola vaccine during the 2014 wave.

## Data and validation (real WHO figures)

Seven cumulative milestones taken from primary WHO Disease Outbreak News / ECDC
updates (see `data/README.md` for each source). The notebook fits each model's
effective population, R0 and onset day to these figures and compares simulated
cumulative cases at each report date.

- **SEAIQR** tracks the real cumulative cases within ~10% at every 2014 milestone
  (mean error ~6%) and — without being told — places the epidemic onset within a
  few weeks of the actual WHO notification date (23 March 2014). Fitted
  R0 ≈ 1.6, inside the published 1.5–2.0 range.
- **SIRD** (mean error ~36%) cannot match the shape: its short generation time
  forces a late onset that misses the July milestone, then it saturates well
  short of the year-end total.
- Deaths, from the SEAIQR case trajectory × reported CFR (~0.40), are the right
  order of magnitude.

## The honest failure

The single-wave model plateaus near its final size while the real epidemic
dragged on through 2015 with low-level transmission and flare-ups — a
metapopulation effect a single well-mixed wave cannot represent. Both models
under-predict the November 2015 total.

## Intervention

Isolation is the control lever: an isolation rate q ≈ 0.15 pulls R0 below 1. In
the direct-contact agent model, isolating 70% of cases collapses the attack rate
from ~0.72 to ~0.25 — much stronger than isolation was for the airborne case,
because removing a contact case removes its transmission route entirely.

## Limitations

Single effective mixing population (real spread was a metapopulation with a long
2015 tail); constant parameters (no safe-burial or behaviour change over time); a
reported CFR that drifts from ~0.56 to ~0.40 over the epidemic; cumulative-only
surveillance data.
