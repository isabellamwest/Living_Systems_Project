# Data: COVID-19 first wave, United Kingdom (2020)

`owid_uk_daily_cases_per_million.csv` — from Our World in Data:
daily new confirmed COVID-19 cases per million people, United Kingdom,
1 March – 18 July 2020 (the first wave).

Columns: `Entity, Code, Day, New cases (per 1M)`.

## Source

Our World in Data — Coronavirus (COVID-19) Cases:
https://ourworldindata.org/covid-cases
(underlying data compiled from Johns Hopkins University CSSE / national reporting).

## Notes

- The series is a 7-day rolling average, not raw daily counts.
- It counts **confirmed** cases. Testing was severely limited early in the wave,
  so confirmed cases are a substantial undercount of true infections. UK
  first-wave seroprevalence was later estimated at roughly 6–7%, far above what
  the confirmed-case totals imply.

Because of this, the notebook validates the shape and timing of the reported
wave, and is explicit that the fitted reporting fraction and the model's attack
rate are not reliable estimates of true ascertainment or true attack rate.

We work per million people (model N = 1,000,000) so the model counts line up
directly with the "per 1M" series.