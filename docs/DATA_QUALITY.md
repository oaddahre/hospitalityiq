# Data quality, confidence and real figures

Principle: never show a number with more certainty than the data supports.
Client screens never name the data provider; confidence and quality words
are generic ("observed", "modelled", "limited data"). Admin screens name
providers.

## Real data only (what clients may see)

1. **BAR (published rate), observed:** each hotel's average over the nights since 3 November 2026 (the last price seen before each night), from 7 priced nights (`live_kpis.observed_bar`). A group's BAR is the plain average of its hotels' BAR, "limited data" under 3 hotels (`app.group_bar`, `KodoBar` in main.js). Never called ADR.
2. **Official tourism figures.**
3. **Database facts:** hotels, owners, brands, pipeline, events.
4. **Kodo estimates, always labelled:** occupancy model (next 30 nights), Rooms RevPAR = BAR × modelled occupancy, tourism 2026E and 2027F, the valuation tool.

`performance.csv` (the old FY 2025 estimates) is never read for clients; it stays an internal input of occupancy model v1. Where nothing real exists yet, pages say "Collecting data since 3 November". Reports exist only for periods real data covers (`app.report_periods`). `tests/test_real_data_only.py` enforces all of this. The LIVE_FIGURES flag is retired: its behaviour is the only mode.

## What runs, and when

| When | What |
| --- | --- |
| After every occupancy model run (04:00, and after each scraper run) | `data_quality.run()` |
| 05:00 | `data_quality.run()` again, then the sanity check: one email to `SANITY_EMAIL` (default admin@kodohospitality.com; `off` stops it), only when something is wrong, at most once a day |
| Admin → Data health → Run checks now | `data_quality.run()` |
| First model run of each month, or Run calibration now | `occupancy_model.maybe_calibrate()` |

## Files (DATA_DIR)

- **`rate_quality.csv`:** one row per hotel and night, from the first price to 30 nights ahead. Columns: `status`, `rate_mad`, `scrape_date`, `score` (0–1), `flags`.
- **`data_health.json`:** everything on the Data health page. Per hotel: coverage, history, quality, Google ID and master-data issues, confidence and its reasons, and the model rules that apply. It also holds cities, plausibility, the effect of the new hotels, the problems found and the thresholds.
- **`monthly_performance.csv` and `daily_performance.csv`:** figures reported by hotels (Admin → Uploads). They are confidential: they feed the calibration only.
- **`calibration_results.json`:** model error by hotel, city, month and hotel type, for nights and months separately. It also holds the school-holiday test.
- **`room_count_sources.csv`** (in the repo): whether each room count has a source: `sourced`, `no_source_on_file`, `uncertain` or `press_only`.

## Night status

| Status | Meaning |
| --- | --- |
| `priced` | price from the latest lookup that covered the night |
| `sold_out` | missing from 2 successful lookups in a row while the nights around it were priced |
| `sold_out_candidate` | the same pattern, seen in one lookup only |
| `no_price` | the lookup worked but returned no price, with no sold-out pattern |
| `closed_or_unknown` | 5 or more nights in a row without a price |
| `failed` | the lookup failed: no ID, no result, no match, an error, or another currency |
| `not_checked` | no lookup covered the night |

## Price flags

Each flag takes its penalty off a score of 1. A night counts as covered from a score of 0.5.

| Flag | Rule | Penalty |
| --- | --- | --- |
| `outlier_self` | more than 2.5× above or below the hotel's own median (needs 7 prices) | 0.5 |
| `outlier_peer` | more than 3× from the median of the same city and segment that night (needs 3 hotels) | 0.4 |
| `jump` | the same night moved more than 1.6× between two lookups | 0.2 |
| `flat` | every night of a lookup at one identical price (14 or more nights) | 0.3 |
| `stale` | the latest price of a future night is more than 7 days old | 0.2 |
| `currency` | outside 150–80,000 MAD, a euro figure that doesn't match, or about 10.8× below the hotel's own or its peers' level | 0.7 |

## Confidence

Confidence is set per hotel, for modelled figures. Group levels (city, brand, owner, market) are weighted by rooms.

| Level | Needs |
| --- | --- |
| `insufficient` | no price history, or under 30% coverage and under 7 days of history |
| `low` | below medium |
| `medium` | 50% of the next 30 nights usable, 14 days of history, price quality 0.7 |
| `high` | 80% coverage, 28 days of history, quality 0.85, and a calibration error within 8 pts against figures the hotel reported |

Proposed display (with the CONFIDENCE_UI flag):

- **Medium and high:** shown normally.
- **Low:** greyed, with "Limited data".
- **Insufficient:** hidden ("Insufficient data").
- **Hotels with no price history:** no occupancy at all.

## Flags (`flags.py`, Railway variables, off unless set to on)

| Flag | Changes |
| --- | --- |
| `CONFIDENCE_UI` | confidence line on the KPI cards; low greyed, insufficient hidden; no occupancy without price history |
| `QUALITY_RANGES` | v2 leaves out prices scoring under 0.5; range +2 pts under 14 days of history, +2 pts when price quality is under 0.7 |
| `VALUATION_V2` | corrected valuation engine (`static/js/valuation_engine.js`, see its header), range from the sensitivity of occupancy ±5 pts and cap rate ±0.5 pt, assumptions listed |

With every flag off, the pages are unchanged. This was checked by comparing every card, table header, row and chart unit on six screens and the valuation tool, against the previous code on the same data.

## Plausibility

The model's average for a whole year without price signals (its prior) is compared, by city, with:

- the official annual occupancy of classified accommodation (2025)
- Kodo's 2026E and 2027F

A gap over 8 pts is flagged, with its likely causes. Nothing is recalibrated automatically. Official city occupancy is annual only, so no monthly target is invented.

## Hotel templates

`static/downloads/`: English and French templates, as CSV and Excel, plus `README_hotel_figures.txt`. The admin's Uploads section reads CSV (comma or semicolon) and Excel in the browser. The server checks every value (`hotel_figures.validate`) and answers with numbered errors.

## Tests

- **`tests/test_data_quality.py`:** checks on a test data directory with planted problems (`tests/quality_fixture.py`).
- **`tests/test_model_stability.py`:** one missing night, one outlier, one hotel removed, and repeat runs.
- **`tests/test_hotel_figures.py`:** template intake and validation.
- **`tests/test_valuation_engine.py`:** valuation results checked against hand-worked numbers.
- **`tests/test_flags_and_labels.py`:** flags off change nothing, no provider names reach clients, and the sanity email rules.
