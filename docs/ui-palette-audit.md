# Off-palette colour audit

Every colour on screen or in the code that is not in the new palette (`docs/ui-standard.md`): black, white, grey; blue `#0075DE` only for the selected item, primary actions and focus; red/green only for up/down and errors.

Taken 25 Nov 2026, light mode, 1440 px. Two passes:
1. **On screen**: every visible element of each page or screen in a browser (text, fills, borders, SVG, chart datasets). Blue on a selected/active item or a primary button is left out (allowed). Hover states and map markers are not captured; the code pass covers them.
2. **In the code**: category tokens (`--cat-1…5`), coloured pill classes, chart/marker colours and colour literals, per file and section.

Red/green rows are listed so you can check each is an up/down change or an error; those that are stay.

## Size of the job

| Page | Off-palette elements on screen | Families |
|---|---|---|
| Platform: hotels | 590 | sky, green, orange, violet |
| Platform: brands | 162 | sky, green, orange, violet |
| Platform: tourism | 143 | blue, sky, green, orange, violet |
| Landing (/) | 85 | blue, sky, green, orange, violet |
| Platform: hotel page | 74 | blue, green, orange, violet |
| Platform: brand page | 57 | blue, sky, green, orange |
| Platform: pipeline | 44 | blue, sky, green, orange, violet |
| Platform: owners | 26 | green, orange |
| /methodology | 15 | blue, green, orange |
| admin | 11 | blue, red |
| /payment-pending | 6 | blue, green |
| /privacy | 5 | blue |
| /login | 5 | blue |
| account | 5 | blue, green, violet |
| /about | 4 | blue |
| /team | 4 | blue |
| Platform: valuation | 4 | green |
| /contact | 3 | blue |
| /register | 3 | blue |
| /terms | 2 | blue |
| /accept-invite | 2 | blue, red |
| Platform top bar and sidebar (every screen) | 2 | violet |
| Platform: dashboard (one destination) | 2 | blue |
| /forgot-password | 1 | blue |
| /reset-password | 1 | blue |
| /verify-email | 1 | blue |

The Market Overview's two blue entries are the Seasonality chart (official solid, estimate light), the allowed single-series case in the standard.

## 1. On screen, by page

### Landing (/)

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 19 | span#toggleLight.mk-toggle-opt.mk-toggle-active [color] "LIGHT"; span#lpSpotlightLabel.lp-spotlight-label [color] "Hotel Supply Database"; span.lp-section-tag [color] "01. Platform" |
| blue | `#0075DE` | 15 | div#navProgress.nav-progress [background]; span.lp-pill-dot [background]; span.lp-pill-word.lp-pill-cur [color] "data layer" |
| blue | `#E6F3FE` | 3 | span#lpHeroPill.lp-pill.lp-pill-js [background] "data layerbenchmarkmarket inde"; span.pill--blue.lp-media-pill [background] "The platform"; span.lp-bento-role [background] "Revenue managers" |
| blue | `#006DD0` | 2 | span.pill--blue.lp-media-pill [color] "The platform"; span.lp-bento-role [color] "Revenue managers" |
| sky | `#00B6FF` | 5 | span.lp-bento-role-dot [background]; span.lp-viz-on [background] |
| sky | `#0976A6` | 1 | span.lp-bento-role [color] "Management companies" |
| sky | `#E3F6FF` | 1 | span.lp-bento-role [background] "Management companies" |
| green | `#127F48` | 23 | span.pill--green.lp-media-pill [color] "Hotel profile"; span.lp-bento-role [color] "Independent owners"; span.lp-ck [color] "✓" |
| green | `#E4F8EC` | 2 | span.pill--green.lp-media-pill [background] "Hotel profile"; span.lp-bento-role [background] "Independent owners" |
| green | `#24CB71` | 2 | span.lp-bento-role-dot [background]; span.lp-viz-on [background] |
| orange | `#FF7237` | 2 | span.lp-bento-role-dot [background]; span.lp-viz-on [background] |
| orange | `#BB4A0E` | 1 | span.lp-bento-role [color] "Investors" |
| orange | `#FFEEE6` | 1 | span.lp-bento-role [background] "Investors" |
| violet | `#7B5CE0` | 4 | span.lp-bento-role-dot [background]; i [background] |
| violet | `#5B3FC4` | 2 | span.pill--violet.lp-media-pill [color] "Owner & portfolio"; span.lp-bento-role [color] "Lenders and advisors" |
| violet | `#EEE9FD` | 2 | span.pill--violet.lp-media-pill [background] "Owner & portfolio"; span.lp-bento-role [background] "Lenders and advisors" |

### /about

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 1 | span#toggleLight.mk-toggle-opt.mk-toggle-active [color] "LIGHT" |
| blue | `#006DD0` | 1 | span.pill--blue.lp-media-pill [color] "About us" |
| blue | `#E6F3FE` | 1 | span.pill--blue.lp-media-pill [background] "About us" |
| blue | `#0075DE` | 1 | a.btn-fill [background] "Get in touch →" |

### /team

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 1 | span#toggleLight.mk-toggle-opt.mk-toggle-active [color] "LIGHT" |
| blue | `#006DD0` | 1 | span.pill--blue.lp-media-pill [color] "About us" |
| blue | `#E6F3FE` | 1 | span.pill--blue.lp-media-pill [background] "About us" |
| blue | `#0075DE` | 1 | a.btn-fill [background] "Get in touch →" |

### /contact

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 2 | span#toggleLight.mk-toggle-opt.mk-toggle-active [color] "LIGHT"; span.lp-section-tag [color] "Contact" |
| blue | `#0075DE` | 1 | button.btn-fill [background] "Send Message →" |

### /methodology

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006DD0` | 2 | span.method-source-confidence.pill--blue [color] "High Confidence"; span.method-source-confidence.pill--blue [color] "Kodo estimate" |
| blue | `#E6F3FE` | 2 | span.method-source-confidence.pill--blue [background] "High Confidence"; span.method-source-confidence.pill--blue [background] "Kodo estimate" |
| blue | `#0075DE` | 2 | a.btn-pill.btn-pill--filled-lg [background] "Get in Touch →"; a.btn-pill.btn-pill--filled-lg [border] "Get in Touch →" |
| blue | `#006BCC` | 1 | span#toggleLight.mk-toggle-opt.mk-toggle-active [color] "LIGHT" |
| green | `#127F48` | 2 | span.method-source-confidence.pill--green [color] "Highest Confidence"; span.method-source-confidence.pill--green [color] "Verified" |
| green | `#E4F8EC` | 2 | span.method-source-confidence.pill--green [background] "Highest Confidence"; span.method-source-confidence.pill--green [background] "Verified" |
| orange | `#BB4A0E` | 2 | span.method-source-confidence.pill--orange [color] "Medium Confidence"; span.method-source-confidence.pill--orange [color] "Key Count Uncertain" |
| orange | `#FFEEE6` | 2 | span.method-source-confidence.pill--orange [background] "Medium Confidence"; span.method-source-confidence.pill--orange [background] "Key Count Uncertain" |

### /terms

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 2 | span#toggleLight.mk-toggle-opt.mk-toggle-active [color] "LIGHT"; a [color] "legal@kodohospitality.com" |

### /privacy

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 5 | span#toggleLight.mk-toggle-opt.mk-toggle-active [color] "LIGHT"; a [color] "legal@kodohospitality.com" |

### /login

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 5 | a [color] "Register →"; a [color] "Reset it →"; a [color] "Terms of Service" |

### /register

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 3 | a [color] "Terms of Service"; a [color] "Privacy Policy"; a [color] "Sign in →" |

### /forgot-password

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 1 | a [color] "← Back to log in" |

### /reset-password

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 1 | a [color] "← Back to log in" |

### /accept-invite

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 1 | a [color] "hello@kodo.ma" |
| red | `#C4332F` | 1 | div.auth-error [color] "This invite link is invalid or" |

### /verify-email

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 1 | a [color] "← Back to log in" |

### Platform: pipeline

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#0075DE` | 4 | canvas#chart-pipeline-proj [chart backgroundColor]; canvas#chart-pipeline-city [chart backgroundColor]; canvas#chart-pipeline-year [chart backgroundColor] |
| sky | `#0976A6` | 7 | span.segment-badge.pill--sky [color] "UPPER UPSCALE" |
| sky | `#E3F6FF` | 7 | span.segment-badge.pill--sky [background] "UPPER UPSCALE" |
| green | `#127F48` | 9 | span.segment-badge.pill--green [color] "UPSCALE" |
| green | `#E4F8EC` | 9 | span.segment-badge.pill--green [background] "UPSCALE" |
| orange | `#FF7237` | 2 | span.screen-header-legend-dot [background]; span.seg-dot [background] |
| orange | `#BB4A0E` | 2 | span.segment-badge.pill--orange [color] "MIDSCALE" |
| orange | `#FFEEE6` | 2 | span.segment-badge.pill--orange [background] "MIDSCALE" |
| violet | `#5B3FC4` | 1 | span.segment-badge.pill--violet [color] "ULTRA LUXURY" |
| violet | `#EEE9FD` | 1 | span.segment-badge.pill--violet [background] "ULTRA LUXURY" |

### Platform: hotels

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| sky | `#0976A6` | 80 | span.segment-badge.pill--sky [color] "UPPER UPSCALE" |
| sky | `#E3F6FF` | 80 | span.segment-badge.pill--sky [background] "UPPER UPSCALE" |
| green | `#127F48` | 138 | span.segment-badge.pill--green [color] "UPSCALE"; span.logo-tile.logo-tile--initials [color] "M"; span.logo-tile.logo-tile--initials [color] "O" |
| green | `#E4F8EC` | 138 | span.segment-badge.pill--green [background] "UPSCALE"; span.logo-tile.logo-tile--initials [background] "M"; span.logo-tile.logo-tile--initials [background] "O" |
| orange | `#BB4A0E` | 68 | span.segment-badge.pill--orange [color] "MIDSCALE" |
| orange | `#FFEEE6` | 68 | span.segment-badge.pill--orange [background] "MIDSCALE" |
| violet | `#5B3FC4` | 9 | span.segment-badge.pill--violet [color] "ULTRA LUXURY"; span.logo-tile.logo-tile--initials [color] "RM"; span.logo-tile.logo-tile--initials [color] "BW" |
| violet | `#EEE9FD` | 9 | span.segment-badge.pill--violet [background] "ULTRA LUXURY"; span.logo-tile.logo-tile--initials [background] "RM"; span.logo-tile.logo-tile--initials [background] "BW" |

### Platform: brands

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| sky | `#0976A6` | 22 | span.brn-seg-pill.pill--sky [color] "Upper Upscale" |
| sky | `#E3F6FF` | 22 | span.brn-seg-pill.pill--sky [background] "Upper Upscale" |
| sky | `#00B6FF` | 2 | div.brn-mkt-seg [background]; span.brn-mkt-dot [background] |
| green | `#127F48` | 34 | span.brn-seg-pill.pill--green [color] "Upscale"; span.logo-tile.logo-tile--initials [color] "M"; span.logo-tile.logo-tile--initials [color] "O" |
| green | `#E4F8EC` | 34 | span.brn-seg-pill.pill--green [background] "Upscale"; span.logo-tile.logo-tile--initials [background] "M"; span.logo-tile.logo-tile--initials [background] "O" |
| green | `#24CB71` | 4 | div.brn-mkt-seg [background]; span.brn-mkt-dot [background] |
| orange | `#BB4A0E` | 12 | span.brn-seg-pill.pill--orange [color] "Midscale" |
| orange | `#FFEEE6` | 12 | span.brn-seg-pill.pill--orange [background] "Midscale" |
| orange | `#FF7237` | 2 | div.brn-mkt-seg [background]; span.brn-mkt-dot [background] |
| violet | `#5B3FC4` | 8 | span.brn-seg-pill.pill--violet [color] "Ultra Luxury"; span.logo-tile.logo-tile--initials [color] "RM"; span.logo-tile.logo-tile--initials [color] "BW" |
| violet | `#EEE9FD` | 8 | span.brn-seg-pill.pill--violet [background] "Ultra Luxury"; span.logo-tile.logo-tile--initials [background] "RM"; span.logo-tile.logo-tile--initials [background] "BW" |
| violet | `#7B5CE0` | 2 | div.brn-mkt-seg [background]; span.brn-mkt-dot [background] |

### Platform: owners

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| green | `#127F48` | 10 | span.owner-type-badge.pill--green [color] "Private" |
| green | `#E4F8EC` | 10 | span.owner-type-badge.pill--green [background] "Private" |
| orange | `#BB4A0E` | 3 | span.owner-type-badge.pill--orange [color] "Family"; span.owner-type-badge.pill--orange [color] "Family-Owned" |
| orange | `#FFEEE6` | 3 | span.owner-type-badge.pill--orange [background] "Family"; span.owner-type-badge.pill--orange [background] "Family-Owned" |

### Platform: tourism

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#0075DE` | 10 | canvas#chart-tour-arrivals [chart Official]; canvas#chart-tour-transport [chart Air]; canvas#chart-tour-origins [chart backgroundColor] |
| sky | `#0976A6` | 36 | span.pill--sky.tour-fc-pill [color] "Kodo estimate and forecast · n"; span.tour-fc-value [color] "21.6M"; span.tour-fc-value [color] "48.8M" |
| sky | `#00B6FF` | 14 | span.chart-dot-legend-dot.tour-dot-estimate [border]; span.chart-dot-legend-dot.tour-dot-forecast [border]; span.tour-tag.tour-tag--fc [border] "fcst." |
| sky | `#E3F6FF` | 7 | span.pill--sky.tour-fc-pill [background] "Kodo estimate and forecast · n"; button.pill--sky.evc-pill [background] "Music×"; button.evcal-bar.pill--sky [background] "Festival des Andalousies Atlan" |
| sky | `#00B6FF @0.12` | 2 | canvas#chart-tour-arrivals [chart Kodo]; canvas#chart-tour-revenue [chart Kodo] |
| sky | `#00B6FF @0.28` | 2 | canvas#chart-tour-arrivals [chart Kodo]; canvas#chart-tour-revenue [chart Kodo] |
| sky | `#00B6FF @0.16` | 1 | canvas#chart-tour-season [chart 2027F range] |
| green | `#127F48` | 8 | span#tour-kpi-arrivals-delta.kpi-delta.up [color] "+14% vs 2024"; span#tour-kpi-nights-delta.kpi-delta.up [color] "+9% vs 2024"; span#tour-kpi-revenue-delta.kpi-delta.up [color] "+21% vs 2024" |
| green | `#E4F8EC` | 8 | span#tour-kpi-arrivals-delta.kpi-delta.up [background] "+14% vs 2024"; span#tour-kpi-nights-delta.kpi-delta.up [background] "+9% vs 2024"; span#tour-kpi-revenue-delta.kpi-delta.up [background] "+21% vs 2024" |
| green | `#24CB71` | 2 | canvas#chart-tour-transport [chart Sea]; canvas#chart-tour-tesmre [chart MRE] |
| orange | `#BB4A0E` | 21 | button.pill--orange.evc-pill [color] "Arts and culture×"; button.pill--orange.evc-pill [color] "Film×"; button.pill--orange.evc-pill [color] "Moussem and tradition×" |
| orange | `#FFEEE6` | 21 | button.pill--orange.evc-pill [background] "Arts and culture×"; button.pill--orange.evc-pill [background] "Film×"; button.pill--orange.evc-pill [background] "Moussem and tradition×" |
| orange | `#FF7237` | 1 | canvas#chart-tour-transport [chart Land] |
| violet | `#5B3FC4` | 5 | button.pill--violet.evc-pill [color] "Public holiday×"; button.pill--violet.evc-pill [color] "Religious×"; span.pill--violet.evc-pill [color] "Moon-dependent" |
| violet | `#EEE9FD` | 5 | button.pill--violet.evc-pill [background] "Public holiday×"; button.pill--violet.evc-pill [background] "Religious×"; span.pill--violet.evc-pill [background] "Moon-dependent" |

### Platform: valuation

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| green | `#127F48` | 2 | span#val-q-gop-margin.val-metric-value.val-metric-good [color] "54.5%"; span#val-q-noi-margin.val-metric-value.val-metric-good [color] "50.0%" |
| green | `#E4F8EC` | 2 | span#val-q-gop-margin.val-metric-value.val-metric-good [background] "54.5%"; span#val-q-noi-margin.val-metric-value.val-metric-good [background] "50.0%" |

### Platform top bar and sidebar (every screen)

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| violet | `#5B3FC4` | 1 | span#tier-badge.tier-badge.tier-badge--advisory [color] "Advisory" |
| violet | `#EEE9FD` | 1 | span#tier-badge.tier-badge.tier-badge--advisory [background] "Advisory" |

### Platform: dashboard (one destination)

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#0075DE` | 1 | canvas#chart-season [chart Official] |
| blue | `#0075DE @0.30` | 1 | canvas#chart-season [chart Estimate] |

### Platform: brand page

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#0075DE` | 1 | canvas#chart-brand-revpar [chart backgroundColor] |
| sky | `#0976A6` | 7 | span.segment-badge.pill--sky [color] "UPPER UPSCALE" |
| sky | `#E3F6FF` | 7 | span.segment-badge.pill--sky [background] "UPPER UPSCALE" |
| green | `#127F48` | 5 | span.segment-badge.pill--green [color] "UPSCALE" |
| green | `#E4F8EC` | 5 | span.segment-badge.pill--green [background] "UPSCALE" |
| orange | `#BB4A0E` | 16 | span.segment-badge.pill--orange [color] "MIDSCALE" |
| orange | `#FFEEE6` | 16 | span.segment-badge.pill--orange [background] "MIDSCALE" |

### Platform: hotel page

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#0075DE` | 1 | canvas#chart-hotel-city [chart backgroundColor] |
| green | `#127F48` | 3 | span#hotel-hd-status.hotel-status-badge.pill--green [color] "Open"; span.pill--green [color] "+MAD 4,712"; span.pill--green [color] "+9.0 pts" |
| green | `#E4F8EC` | 3 | span#hotel-hd-status.hotel-status-badge.pill--green [background] "Open"; span.pill--green [background] "+MAD 4,712"; span.pill--green [background] "+9.0 pts" |
| orange | `#FF7237` | 2 | span.bar-cal-leg-ev [background] |
| orange | `#BB4A0E` | 1 | span.pill--orange.evc-pill [color] "Estimated" |
| orange | `#FFEEE6` | 1 | span.pill--orange.evc-pill [background] "Estimated" |
| violet | `#5B3FC4` | 41 | div.bar-cal-dn [color] "Fri 27"; div.bar-cal-rate [color] "12.2k"; div.bar-cal-dn [color] "Sat 28" |
| violet | `#EEE9FD` | 22 | div.bar-cal-day.src-live-google [background] "Fri 27 12.2k"; div.bar-cal-day.src-live-google [background] "Sat 28 11.5k"; div.bar-cal-day.src-live-google [background] "Sun 29 11.5k" |

### account

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#0075DE` | 2 | button#save-btn.acc-btn [background] "Save password"; button.acc-btn [background] "+ Invite member" |
| green | `#24CB71` | 1 | span [background] |
| violet | `#5B3FC4` | 1 | span.tier-badge.tier-badge--advisory [color] "Advisory" |
| violet | `#EEE9FD` | 1 | span.tier-badge.tier-badge--advisory [background] "Advisory" |

### admin

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#0075DE` | 10 | button.list-pill [border] "Users"; button.list-pill [border] "Organisations"; button.list-pill [border] "News" |
| red | `#C4332F` | 1 | span.adm-row-meta [color] "News has zero articles" |

### /payment-pending

| Family | Colour | Elements | Where (examples) |
|---|---|---|---|
| blue | `#006BCC` | 2 | a [color] "hello@kodo.ma"; a [color] "Sign in →" |
| blue | `#E6F3FE` | 1 | div.coming-soon [background] "Stripe Payment · Coming Soon S" |
| blue | `#006DD0` | 1 | p.coming-soon__label [color] "Stripe Payment · Coming Soon" |
| green | `#127F48` | 1 | div.check-icon [color] "✓" |
| green | `#E4F8EC` | 1 | div.check-icon [background] "✓" |

Nothing off-palette on screen (first view): Platform: dashboard, Platform: map, Platform: benchmarking, Platform: reports, Platform: news, Platform: ai. Map markers, Benchmarking results, Reports and the AI analyst only show colour after an action; see the code pass.

## 2. In the code, by file

| File | Off-palette uses | Main kinds (count) | Sections |
|---|---|---|---|
| `static/css/admin.css` | 17 | var --negative (8), var --negative-tint (2), var --negative-muted (1), var --positive-tint (1), var --positive (1), green token (1) | Buttons — pills; Data health (data_quality.py); Filters; Generic dropdown menu item — shared by t; Toasts |
| `static/css/marketing.css` | 21 | blue token (4), green token (4), orange token (4), violet token (4), sky token (4), var --positive (1) |  |
| `static/css/style.css` | 103 | sky token (16), var --negative (14), blue token (14), var --positive (8), var --accent-dim (6), violet token (5) | Benchmarking screen; Buttons — pill shape, orange reserved fo; Chat messages: terminal style (no bubble; Coloured labels; Colours: platform variables mapped onto ; Compact text badges/pills; Destinati |
| `static/js/admin.js` | 38 | var --negative (22), var --positive (8), green pill (3), orange pill (3), red pill (2) | DATA HEALTH (data_quality.py); Events (events.json + this server's chan; NEWS; ORGANISATIONS; OVERVIEW; RATES / SCRAPER; UPLOADS; USERS |
| `static/js/main.js` | 22 | blue token (7), green pill (5), red pill (4), blue pill (3), orange pill (2), sky pill (1) | BAR (published rate) since 3 November 20; Benchmarking: rate benchmark (real mode); Constants; Editorial / News screen; Hotel rate calendar: "Next 30 nights", o; Live readouts (before Run Valuation);  |
| `templates/about.html` | 1 | blue pill (1) |  |
| `templates/accept_invite.html` | 3 | var --negative (2), var --negative-tint (1) |  |
| `templates/account.html` | 9 | var --negative (3), var --positive (2), orange token (2), blue token (1), green token (1) | Password form; Team section; Welcome banner |
| `templates/contact.html` | 2 | var --positive (1), var --negative (1) |  |
| `templates/forgot_password.html` | 4 | var --negative-tint (1), var --negative (1), var --positive-tint (1), var --positive (1) | Status messages |
| `templates/index.html` | 23 | blue token (5), green token (5), blue pill (4), orange token (3), green pill (3), sky token (1) |  |
| `templates/landing.html` | 3 | blue pill (1), green pill (1), violet pill (1) |  |
| `templates/login.html` | 4 | var --negative-tint (1), var --negative (1), var --positive-tint (1), var --positive (1) | Error / success |
| `templates/methodology.html` | 6 | blue pill (2), orange pill (2), green pill (2) |  |
| `templates/payment_pending.html` | 4 | var --positive (2), var --positive-tint (1), blue token (1) | Check icon; Coming soon box; Features list |
| `templates/register.html` | 3 | var --negative-tint (1), var --negative (1), var --positive (1) | Plan info box |
| `templates/reset_password.html` | 4 | var --negative-tint (1), var --negative (1), var --positive-tint (1), var --positive (1) |  |
| `templates/verify_email.html` | 4 | var --negative-tint (1), var --negative (1), var --positive-tint (1), var --positive (1) |  |

Also in `static/js/main.js`, by mapping rather than literal: `SEGMENT_FAMILY` (segment pills and chart colours on Hotels, Brands, Pipeline, Map, brand and hotel pages), `OWNER_TYPE_FAMILY` (owner type pills), `brandInitials` (initials tiles tinted in 6 families), pipeline status pills and markers (blue / orange / grey), the tourism chart series (sky / green / orange), the rate calendar source colours (violet), the events calendar categories, and the plan badges (`[data-plan]`: blue Benchmarker, violet Advisory).
