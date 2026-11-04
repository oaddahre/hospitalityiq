# Events database

One list of every event that can move hotel demand in Morocco: public and
religious holidays, school holidays in Morocco and the source markets,
festivals, sport, trade fairs and congresses. It feeds:

- the **Events calendar** on the Tourism screen (month and agenda views,
  filters, busy-week strip, detail panel, .ics and CSV export);
- the **event markers** on the hotel profile's rate and occupancy calendars
  and on the Benchmarking calendars, and the hotel's **Next 90 days** strip;
- the **occupancy model** (v1 and v2), through `event_points()` in
  `occupancy_model.py`.

## Where it lives

| File | Where | What |
|---|---|---|
| `events.json` | repo (deploys with the code) | the researched base list |
| `event_overrides.json` | `DATA_DIR` (survives deploys) | events added, edited or hidden in the admin |
| `event_changes.log` | `DATA_DIR` | one JSON line per admin change (who, when, what) |
| `model_holidays.json` | repo | **internal, never displayed:** school holidays in the source markets (France, UK, Spain, Germany, Netherlands, Belgium, UAE, Saudi Arabia), read by the occupancy model only |

`events_db.load_events()` merges the first two files; every page reads
that. The occupancy model reads `events_db.load_model_events()`: the same
events plus the internal list. `/api/events` never includes the internal
list, so it appears on no page, filter, marker or export. It has no admin
editor: edit it in the repo, in the same format (`kodo-model-holidays-1`,
same fields), and run the check below.

## Display labels

Stored values stay lower-case (`high`, `moon`, `one-off`…). What users read
comes from one map, `events_db.LABELS` (type, impact, date status,
recurrence, effect, precision), which `/api/events` and `/api/admin/events`
send as `labels`; the calendar, markers, detail panel, exports and the admin
editor all use it.

## Format (`kodo-events-1`)

```json
{"format": "kodo-events-1", "updated": "2026-11-03", "events": [ { … } ]}
```

| Field | Meaning |
|---|---|
| `id` | unique, e.g. `mawazine-rhythms-of-the-world-2027-06` (slug of the name + start month, + city when two share a name) |
| `name` | event name |
| `type` | `holiday`, `religious`, `school_ma`, `holiday_abroad`, `diaspora`, `music`, `film`, `arts`, `moussem`, `sport`, `business` (`school_abroad` only in `model_holidays.json`) |
| `city` | the city as the platform names it (`Rabat / Salé / Témara`, `Agadir / Taghazout`…), a town (`Kelaat M'Gouna`), or `National` |
| `market` | the hotel city it affects when `city` is a town without hotels (e.g. `Ouarzazate` for Kelaat M'Gouna); empty = none |
| `venue` | venue, if known |
| `start`, `end` | first and last day, `YYYY-MM-DD`, inclusive |
| `precision` | `day`, or `month` when only the month is known (shown as "dates to be announced", not counted in the model) |
| `recurrence` | `annual`, `biennial` or `one-off` |
| `impact` | `high`, `medium` or `low` for hotels in its market |
| `impact_reason` | one line: why it matters for hotels |
| `effect` | `up`, `down` (e.g. Ramadan) or `mixed` (Eid: business down, leisure up) |
| `attendance` | published attendance, with its year and who said it |
| `date_status` | `confirmed` (organiser or official body), `announced` (reputable press or listings, not yet the organiser), `estimated` (from a pattern), `moon` (moon-dependent Islamic date) |
| `date_basis` | required for `estimated` and `moon`: what the date is based on |
| `model` | `false` for events shown but not counted in the model (summer holidays and Marhaba, already in the monthly seasonality) |
| `model_kind` | optional pattern with its own point table: `ramadan`, `eid_fitr`, `eid_adha`, `ma_school`, `aefe_school` |
| `markets` | source markets for holidays abroad (`FR`, `UK`, `ES`, `DE`, `NL`, `BE`, `AE`, `SA`) |
| `description` | short note |
| `source` | link to the source used |
| `checked` | date the source was last checked |

## Adding or updating events

**In the admin (production):** Admin → Events. Add, edit or hide an event;
the change is saved in `event_overrides.json` on that server, takes effect
at once (the platform and the next model run) and is logged. Hiding keeps
the event (and its history) but removes it from every page and the model.

**In the repo (for everyone, with the next deploy):** edit `events.json`
(keep it sorted by start date), then run

```
python3 scripts/check_events.py
```

which checks every field, the ids and the date bases in both files. Rules:

- Never invent a date. If the organiser hasn't published it, use the last
  edition's pattern with `date_status: "estimated"` and say so in
  `date_basis`, or leave the event out.
- Once an organiser publishes the dates, update `start`/`end`, set
  `date_status` to `confirmed`, update `source` and `checked`.
- A recurring event gets one entry per edition (2026 and 2027 are separate
  rows), so past editions keep their real dates.
- Admin overrides win over `events.json` for the same id. To fold an admin
  change into the repo, copy it into `events.json` and remove it from
  `event_overrides.json` (or leave it: it changes nothing once equal).

## How the model uses it

See the commented config block `EVENT_PTS` in `occupancy_model.py`. In short:
points by group (business, leisure, holiday, abroad), impact tier and hotel
type; the four patterns in `EVENT_KIND_PTS` keep their own table; a city
factor for small or large hotel stocks; `estimated` dates count 0.6× and
widen the v2 range by 2 points (`moon` 0.85× and 1 point); all events of a
night together are capped at ±15 points. **These sizes are judgement, not
measured**, until the monthly calibration has enough real nights.
