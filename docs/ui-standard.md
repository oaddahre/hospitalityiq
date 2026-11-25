# Kodo UI standard

The Market Overview (dashboard) is the reference. Every page follows this from Nov 2026; pages move over one at a time (`docs/ui-palette-audit.md` lists what is left).

Files: colours in `static/css/tokens.css` (every page loads it), shared components in `static/css/ui.css` (the platform pages only: index, account, admin; load it after the page's own stylesheet). Never write a colour value in a page stylesheet; use a token.

## Colour

Black, white and grey. **No blue anywhere on the platform** (from 25 Nov 2026, until further notice; this replaces the earlier rule that kept `#0075DE` for the selected item, primary actions and focus). Red and green only for up/down changes and errors. No category colours: segments, stages, owner types, plans and event types are never colour-coded. The old blue/green/orange/violet/sky families (`--cat-1…5`, `.pill--blue` etc.) are legacy; don't use them in new work.

- **Selected** (segmented controls, active tab, selected row or filter): inverted, black fill + white text in light mode, white fill + black text in dark mode (`--selected` / `--on-action`).
- **Primary button**: solid black + white text (white + black in dark). Secondary: outlined.
- **Links**: the text colour, underline on hover.
- **Focus**: a 2px outline in the text colour.
- **Charts, inline bars, map markers, badges, "i"**: black, white and greys. The selected map marker is black (white in dark), the others grey.
- The Kodo logo keeps its blue dot (it is the logo, not UI).

How: `ui.css` re-points the blue tokens (`--action*`, `--cat-1-*`, and the sky and violet families `--cat-5-*`, `--cat-4-*`) at black / white / grey and sets the chart series `--series-1…6` to greys, for the platform pages only. The landing page, login pages, emails, PDF reports and Excel exports still use blue until decided.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | #FFFFFF | #000000 | page; also the visible colour of every card, chart and table |
| `--card-bg` | transparent | transparent | cards, charts, tables (the page shows through) |
| `--line` (= `--border`) | #E5E3DF | #2C2C2B | 1px container edge, the hairline under a table header |
| `--text` | #1F1E1C | #F2F1EE | text, solid bars, the outlined button, the "Official" badge fill |
| `--text-2` | #5F5B55 | #A8A39C | secondary text, labels, table headers (AA) |
| `--text-3` | #948D85 | #6F6B66 | disabled / "no data" only (3:1, never body text) |
| `--row-hover` | text at 4% | text at 7% | table row and menu hover |
| `--bg-alt` | #F4F4F2 | #121212 | solid surfaces only: dropdowns (`--menu-bg`), inputs, the "Limited data" badge |
| `--pop-bg` / `--pop-text` | `--text` / `--bg` | same | tooltips (solid, inverted) |
| `--action` / `--selected` (platform) | #1F1E1C | #F2F1EE | selected fill, primary button, focus ring |
| `--on-action` (platform) | #FFFFFF | #000000 | text on a selected fill or primary button |
| `--action-text` (platform) | #1F1E1C | #F2F1EE | = text (no blue text) |
| `--series-1…6` (platform) | #1F1E1C → #C9C5BF | #F2F1EE → #4A4744 | chart series, greys only |
| `--positive` / `--negative` | #127F48 / #C4332F | #3DDC87 / #FF7B72 | up / down changes, errors |

## Type

One family, Sweet Sans Pro. Numbers use tabular figures.

| Element | Size / weight |
|---|---|
| Page title (`.k-title`) | 20px / 700 (17px under 768px) |
| One line under the title (`.k-line`) | 12px / 400, `--text-2` |
| Card or table title | 13px / 600 |
| Summary number (`.k-kpi-value`) | 26px / 400 (22px on phones) |
| Summary label, table header | 9px / 400–500, upper case, letter-spacing .08em, `--text-2` |
| Table cell | 12px / 400 (name column 500) |
| Badge, pill | 10.5px / 500 |
| Button | 11px / 500, upper case, letter-spacing .08em |
| Tooltip | 12px / 400 |

## Spacing

4px base. Page padding 28px 30px (16px gutter on phones). 22px between blocks (header, summary cards, main view). 10px between summary cards. Table cells 10px vertical, 8px horizontal (4px on phones). Card padding 16–20px.

## Page rhythm

1. **Header**: title + one line (what the page shows and the date of the data). Disclaimers once, here, in one short sentence; details go in tooltips; the footer holds the one Methodology link.
2. **Summary cards**: 3–4 numbers (`.k-kpis` > `.k-kpi`): label, number, one short line, an "i" for the rest.
3. **Filters**: one row (`.k-filters`): segmented control, selects, search.
4. **One main view**: a sortable table by default; another view (cards) as a segmented control, never stacked lists showing the same thing twice. A map is not a view: when a page has one it sits under the view, always shown, follows the filters, at a fixed height (460px, 320px on phones).
5. **Quiet links**: outlined buttons under the view.

## Components (`ui.css`)

- **Surfaces** `.k-card`: transparent, 1px `--line` edge, no fill, no shadow. Tooltips and dropdowns keep a solid surface.
- **Sortable table** `.k-table`: one hairline under the header, no row borders, 10px row spacing, `--row-hover` tint. Header buttons `.k-th-sort`, `aria-sort` on the `th` (↓ / ↑ added automatically). Numbers right-aligned (`.num`). Selected row: hover tint and a 2px edge in `--selected`.
- **Inline bars** `.k-ibar` > `span` (width = share of max): solid = official, `--est` light = estimate, no bar = limited data, `--sel` = the selected row (black / white).
- **Badges** `.k-badge`: `--official` (black fill), plain outline = Estimate, `--limited` (grey) = Limited data. One word on screen; the explanation in `data-tip`.
- **Neutral pills** `.k-pill`: outline (default, e.g. planning), `--solid` black (e.g. under construction), `--muted` grey (opened / other). Segment is plain text or an outline pill.
- **Buttons** `.k-btn`: outlined, black text and border, upper case, "Label →"; hover inverts. `.k-btn--primary`: solid black (white in dark), for the one main action. Row: `.k-btn-row`.
- **Links** `.k-link`: black text, underline on hover. Never the default browser blue.
- **"i" and tooltips** `.k-info` with `data-tip="…"`; the tooltip is `.k-tip` (KodoTip: hover, focus and tap).
- **Segmented control** `.k-seg` > `button[aria-pressed]`: outlined group, the pressed one inverted (black + white text; white + black in dark). Used for tabs, views and stage filters.
- **Filters** `.k-select`, `.k-search`: 32px pills, 1px `--line`.
- **Dropdowns** (every `select` on the platform): `appearance: none` with one grey chevron, 15px from the right edge, 38px right padding so the text never reaches it; the same in Chrome and Safari, light and dark.
- **Empty state** `.k-empty`: one short sentence, `--text-2`. **Loading**: `showLoading(el)` (the scanning line) or the card at 35% opacity.
- **Brand logo tile** `.logo-tile`: square, white in both themes, radius from the size; initials tile when there is no local logo file. Logos are local files only (`static/images/brands/`), never an outside image service.
- **Focus**: every control shows a 2px outline in the text colour on `:focus-visible`.

## Charts

Black, white and greys only. Solid `--text` = official, `--text` at ~22–30% = estimate; the selected item is the solid one, the others grey. No multi-hue series: a chart with categories uses the grey series (`--series-1…6`) and labels. Red / green only for a change up or down.

## Responsive

No sideways scroll at 1280, 1440, 1920 and 390px. Tables wrap names and hide minor columns (`.col-hide-mobile`) rather than scroll; summary cards go 4 → 2 columns under 1100px; filters stack under 768px. Check light and dark at each width before a push.
