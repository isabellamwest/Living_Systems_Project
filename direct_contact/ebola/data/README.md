# Data: Ebola virus disease, West Africa, 2014–2016

`ebola_west_africa_who_milestones.csv` — cumulative WHO-reported
cases and deaths at seven report dates. Each row is taken from a primary WHO
Disease Outbreak News or ECDC epidemiological update. Totals are WHO's West
Africa cumulative figures (Guinea + Liberia + Sierra Leone, plus the small
numbers in other affected countries).

Columns: `date, cumulative_cases, cumulative_deaths, source`.

## The reported figures and their sources

| date | cases | deaths | source |
|---|---|---|---|
| 2014-07-23 | 1,201 | 672 | WHO Disease Outbreak News, 27 Jul 2014 |
| 2014-08-26 | 3,069 | 1,552 | WHO DON, 28 Aug 2014 / ECDC |
| 2014-10-05 | 8,032 | 3,865 | ECDC epidemiological update, 9 Oct 2014 |
| 2014-10-19 | 9,936 | 4,877 | ECDC epidemiological update, 23 Oct 2014 |
| 2014-12-17 | 18,603 | 6,915 | ECDC epidemiological update, 18 Dec 2014 |
| 2015-01-29 | 22,136 | 8,833 | ECDC epidemiological update, 29 Jan 2015 |
| 2015-11-18 | 28,598 | 11,299 | ECDC epidemiological update, 23 Nov 2015 |

## Source URLs

- WHO DON 27 Jul 2014: https://www.who.int/emergencies/disease-outbreak-news/item/2014_07_27_ebola-en
- WHO DON 28 Aug 2014: https://www.who.int/emergencies/disease-outbreak-news/item/2014_08_28_ebola-en
- ECDC updates: https://www.ecdc.europa.eu/en/news-events (epidemiological update: outbreak of Ebola virus disease in West Africa, by date)
- WHO Ebola outbreak 2014–2016 overview: https://www.who.int/emergencies/situations/ebola-outbreak-2014-2016-West-Africa

## How it is used, and the caveats

The notebook runs the SEAIQR and SIRD simulations with literature rates and
compares the simulated **cumulative cases at each report date** to these figures.

- The data is cumulative WHO surveillance; a single well-mixed model captures
  the explosive 2014 growth but under-predicts the long 2015 tail (persistent
  low-level transmission and flare-ups across a metapopulation).
- The reported case fatality ratio falls from ~0.56 to ~0.40 across the
  milestones as case outcomes are recorded, so a single constant CFR is only an
  approximation.
