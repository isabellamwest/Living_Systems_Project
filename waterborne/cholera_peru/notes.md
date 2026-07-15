# Waterborne transmission — cholera (Peru, 1991)

## Why this case study

Cholera is the clean example of *environmentally mediated* transmission: people
are infected by ingesting *Vibrio cholerae* from contaminated water, not
primarily by direct contact. A model that hides this behind a person-to-person
contact term can still fit the curve, but it cannot represent the interventions
that actually end cholera outbreaks — sanitation and water treatment. This is
the argument for the SIRB structure.

## Models used

- **SIR** — baseline, matched to the same R0 for comparison only.
- **SIRB** — adds an environmental reservoir `B`; the infectious shed bacteria
  into the water and susceptibles take up infection through the saturating
  dose-response `B / (κ + B)` [2].

No lockdown/vaccination models here: the meaningful controls act on the *water*,
which is exactly what the reservoir compartment exposes (reduce shedding ξ, raise
decay δ, or lower uptake β).

## Data and validation (real PAHO figures)

Weekly national incidence was not available, so instead of fitting a curve we
run the SIRB simulation with literature rates [2][4] and compare the simulated
**cumulative cases at each PAHO report date** against the real 1991 situation
reports [3].

- With the **national-aggregate R0 = 1.7** (fitted to the milestones) the
  simulation tracks the cumulative cases within ~15% through Feb–Jun, and the
  CFR-scaled death toll is the right order of magnitude.
- The **coastal literature R0 = 2.5** is clearly too fast for the national
  aggregate — it saturates months too early. Aggregating regions that ignite at
  different times lowers the *apparent* R0, which is why 1.7 < 2.5.

## The honest failure

The single-population model plateaus near its final size (~226k) while the real
epidemic climbed to 322k by year end. That gap is real: the PAHO reports
attribute the later cases to spread into new regions (Amazon basin, then
neighbouring countries), which a single well-mixed reservoir cannot represent.
Capturing it would need a metapopulation of coupled SIRB patches.

## Limitations

Perfect mixing and a single well-mixed reservoir; constant parameters (no
rainfall/temperature seasonality, which the Peru literature notes matters); an
effective mixing population that folds in reporting and exposure; and
cumulative-only surveillance data (`data/README.md`).
