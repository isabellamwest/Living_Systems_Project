# Data: cholera, Peru (national), 1991

`peru_cholera_1991_paho.csv` — **real data** from the PAHO/WHO 1991 situation
reports: cumulative suspected cases, hospitalisations and deaths at six report
dates through 1991.

Columns: `date, day_of_year, cumulative_cases, hospitalisations, cumulative_deaths`
(`day_of_year` has 1 January = 1).

## The reported figures

| date | cumulative cases | hospitalisations | cumulative deaths |
|---|---|---|---|
| 14 Feb | 11,085 | 2,450 | 77 |
| 28 Feb | 44,834 | 14,357 | 194 |
| 31 Mar | 118,574 | 42,122 | 812 |
| 30 Jun | 224,248 | 83,521 | 2,143 |
| 15 Aug | 246,246 | 91,424 | 2,416 |
| 31 Dec | 322,568 | 119,063 | 2,906 |

Year-end case fatality ratio ≈ 0.9%.

## Source

Pan American Health Organization (PAHO) / WHO — cholera in the Americas, 1991
epidemiological situation reports. See also:

- Ries AA, Vugia DJ, Beingolea L, et al. Cholera in Piura, Peru: a modern urban
  epidemic. J Infect Dis. 1992;166(6):1429–1433. [3]
- Fung IC-H. Cholera transmission dynamic models for public health
  practitioners. Emerg Themes Epidemiol. 2014;11(1):1. [4]

## How it is used, and the key caveat

The notebook does **not** fit a weekly incidence curve (weekly national data was
not available); instead it runs the SIRB simulation with literature rates and
compares the simulated **cumulative cases at each report date** to these figures.

The data is *national and cumulative*. A single well-mixed model captures the
explosive coastal first wave but under-predicts the year-end total, because the
later cases came from geographic spread into new regions (the PAHO notes flag the
Amazon basin and multi-country spread) — a metapopulation effect outside a
single-patch model. This is discussed explicitly in the notebook.
