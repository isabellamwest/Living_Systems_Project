# Airborne transmission — COVID-19 (UK first wave, 2020, real data)

## Why this case study

COVID-19 is the case where all three interventions are meaningful, so it carries
the intervention comparison for the whole project. The point is that lockdown,
vaccination and quarantine are not interchangeable switches — each enters an
epidemic model through a different piece of structure.

## Models used

- **SIRD** — baseline with a fatal outcome; R0 = 2.7.
- **SIRD + lockdown** — lockdown is a time-varying contact rate, applied
  through the model's `contact_scaling` hook [6]. No new compartment.
- **SIRDV** — vaccination is structural: vaccinated people are a distinct group
  who can still be infected but at a reduced rate, so they need their own
  compartment.
- **SEAIQR** — quarantine needs a latent (exposed) period and an
  asymptomatic route to be modelled honestly; the isolation rate `q` then lowers
  R0 directly. Incubation from [5].

## What the results show

- **Lockdown**: a temporary lockdown flattens and delays the peak but the
  epidemic rebounds on release (deaths barely change); a sustained one suppresses
  it (deaths fall ~3×). Timing is critical — a lockdown starting after the peak
  does almost nothing.
- **Vaccination**: removes susceptibles permanently; a fast enough campaign
  prevents most of the wave.
- **Quarantine**: the only lever that pushes R0 below 1 without confining
  everyone — but undetected asymptomatic spread sets a floor on how well it can
  do, which is exactly why the SEAIQR structure is needed.
- The **agent-based** airborne run (proximity infection within a radius)
  reproduces the same ranking of interventions spatially.

## Validation (against real UK data)

Uses the real Our World in Data series (UK daily confirmed cases per million,
7-day average, Mar–Jul 2020). We fit two models and criticise both:

- **Unmitigated SIRD** fits poorly (R² ≈ 0.4) — with no intervention it grows too
  fast and overshoots the observed peak.
- **SIRD + the real UK lockdown** (23 March, day 22), fitting R0 and one
  contact-reduction number, lifts the fit to R² ≈ 0.9 and lands the peak within a
  couple of days of the observed 24 April peak.

When the real lockdown is added, the fit goes from R² ≈ 0.4 to ≈ 0.9. This shows that that intervention significantly shaped the wave.

## Limitations

Two are specific to the data and are the reason the fit is honest about timing
but not magnitude:

- the series is a **7-day rolling average of confirmed cases**, and early testing
  was severely limited, so it undercounts true infections;
- consequently the model's fitted **attack rate (~50%) is far above the ~6–7%
  first-wave seroprevalence later estimated for the UK — we validate reported
  dynamics, not the absolute number infected.

Model-side: constant R0 between interventions (no behavioural feedback or
variants); homogeneous mixing in the ODEs; a simple leaky-vaccine model; and
isolation of the source helps less for an airborne agent than a contact one.