# Colour audit

Every hardcoded colour outside `static/css/tokens.css`, by file and line. Regenerate with `python3 scripts/color_audit.py`.

- **LEGACY**: an old palette value the final sweep must remove.
- **fallback**: the second argument of `var(--token, …)`; the page uses the token, the literal only applies where the token is undefined.

Total: 455 colour literals in 24 files (103 legacy).

## Per file

| File | Literals |
|---|---|
| `static/js/main.js` | 179 |
| `static/css/marketing.css` | 149 |
| `templates/index.html` | 36 |
| `static/css/style.css` | 34 |
| `static/css/admin.css` | 15 |
| `app.py` | 13 |
| `templates/contact.html` | 5 |
| `generate_pdfs.py` | 4 |
| `static/images/news-placeholder.svg` | 3 |
| `static/js/admin.js` | 2 |
| `templates/methodology.html` | 2 |
| `templates/accept_invite.html` | 1 |
| `templates/account.html` | 1 |
| `templates/admin.html` | 1 |
| `templates/forgot_password.html` | 1 |
| `templates/landing.html` | 1 |
| `templates/login.html` | 1 |
| `templates/payment_pending.html` | 1 |
| `templates/privacy.html` | 1 |
| `templates/register.html` | 1 |
| `templates/reset_password.html` | 1 |
| `templates/terms.html` | 1 |
| `templates/verify_email.html` | 1 |
| `templates/verify_email_sent.html` | 1 |

## Legacy values still present

| Value | Count |
|---|---|
| `#4A7FA5` | 75 |
| `#0A0A0A` | 9 |
| `#242424` | 6 |
| `#141414` | 5 |
| `#3A6A8E` | 4 |
| `#F0F0EE` | 2 |
| `#4A9B6F` | 1 |
| `#F2A33D` | 1 |

## `app.py`

| Line | Colour | Note | Context |
|---|---|---|---|
| 432 | `#F7F6F3` |  | `"page":      "#F7F6F3",   # --bg-alt` |
| 433 | `#FFFFFF` |  | `"card":      "#FFFFFF",   # --bg` |
| 434 | `#E7E4DF` |  | `"border":    "#E7E4DF",   # --border` |
| 435 | `#1F1E1C` |  | `"text":      "#1F1E1C",   # --text` |
| 436 | `#5F5B55` |  | `"text_2":    "#5F5B55",   # --text-2` |
| 437 | `#0075DE` |  | `"action":    "#0075DE",   # --action (button)` |
| 438 | `#0070D5` |  | `"link":      "#0070D5",   # --action-text (links, AA on white)` |
| 439 | `#FFFFFF` |  | `"on_action": "#FFFFFF",   # --on-action` |
| 3357 | `set_text_color(255, 255, 255)` |  | `pdf.set_text_color(255, 255, 255)` |
| 3676 | `set_fill_color(10, 10, 10)` |  | `pdf.set_fill_color(10, 10, 10)` |
| 3680 | `set_text_color(255, 255, 255)` |  | `pdf.set_text_color(255, 255, 255)` |
| 3687 | `set_text_color(136, 136, 136)` |  | `pdf.set_text_color(136, 136, 136)` |
| 3690 | `set_text_color(68, 68, 68)` |  | `pdf.set_text_color(68, 68, 68)` |

## `generate_pdfs.py`

| Line | Colour | Note | Context |
|---|---|---|---|
| 16 | `#1a3a5c` |  | `HIQ_BLUE  = colors.HexColor("#1a3a5c")` |
| 17 | `#c9a84c` |  | `HIQ_GOLD  = colors.HexColor("#c9a84c")` |
| 18 | `#f4f6f9` |  | `HIQ_LIGHT = colors.HexColor("#f4f6f9")` |
| 19 | `#555555` |  | `GREY_TEXT = colors.HexColor("#555555")` |

## `static/css/admin.css`

| Line | Colour | Note | Context |
|---|---|---|---|
| 78 | `rgba(0,0,0,0.25)` |  | `box-shadow: 0 8px 24px rgba(0,0,0,0.25);` |
| 143 | `rgba(0,0,0,0.25)` |  | `box-shadow: 0 8px 24px rgba(0,0,0,0.25);` |
| 177 | `rgba(0,0,0,0.5)` |  | `background: rgba(0,0,0,0.5);` |
| 331 | `#4A7FA5` | LEGACY | `.adm-btn-primary { background: #4A7FA5; color: #fff; border-color: #4A7FA5; }` |
| 331 | `#fff` |  | `.adm-btn-primary { background: #4A7FA5; color: #fff; border-color: #4A7FA5; }` |
| 331 | `#4A7FA5` | LEGACY | `.adm-btn-primary { background: #4A7FA5; color: #fff; border-color: #4A7FA5; }` |
| 332 | `#3A6A8E` | LEGACY | `.adm-btn-primary:hover { background: #3A6A8E; border-color: #3A6A8E; }` |
| 332 | `#3A6A8E` | LEGACY | `.adm-btn-primary:hover { background: #3A6A8E; border-color: #3A6A8E; }` |
| 333 | `#4A7FA5` | LEGACY | `.adm-btn-secondary { background: transparent; color: #4A7FA5; border-color: #4A7FA5; }` |
| 333 | `#4A7FA5` | LEGACY | `.adm-btn-secondary { background: transparent; color: #4A7FA5; border-color: #4A7FA5; }` |
| 334 | `rgba(74,127,165,0.08)` |  | `.adm-btn-secondary:hover { background: rgba(74,127,165,0.08); }` |
| 514 | `#4A7FA5` | LEGACY | `.adm-input:focus, .adm-select:focus, .adm-textarea:focus { border-color: #4A7FA5; }` |
| 547 | `#4A7FA5` | LEGACY | `.adm-dropzone.drag-over { border-color: #4A7FA5; background: var(--accent-dim); }` |
| 574 | `rgba(0,0,0,0.45)` |  | `background: rgba(0,0,0,0.45);` |
| 642 | `rgba(0,0,0,0.5)` |  | `background: rgba(0,0,0,0.5);` |

## `static/css/marketing.css`

| Line | Colour | Note | Context |
|---|---|---|---|
| 59 | `#0A0A0A` | LEGACY | `--lp-bg: #0A0A0A;` |
| 60 | `#0D0D0D` |  | `--lp-bg-alt: #0D0D0D;` |
| 61 | `#080808` |  | `--lp-nav-bg: #080808;` |
| 62 | `#141414` | LEGACY | `--lp-surface: #141414;` |
| 63 | `#1A1A1A` |  | `--lp-border: #1A1A1A;` |
| 64 | `#242424` | LEGACY | `--lp-border-mid: #242424;` |
| 65 | `#161616` |  | `--lp-border-light: #161616;` |
| 66 | `#F0F0EE` | LEGACY | `--lp-text: #F0F0EE;` |
| 67 | `#666666` |  | `--lp-text-muted: #666666;` |
| 68 | `#444444` |  | `--lp-text-faint: #444444;` |
| 69 | `#2A2A2A` |  | `--lp-text-vfaint: #2A2A2A;` |
| 70 | `#161616` |  | `--lp-text-dot: #161616;` |
| 71 | `#0A0A0A` | LEGACY | `--lp-module-bg: #0A0A0A;` |
| 72 | `#0F0F0F` |  | `--lp-module-hover: #0F0F0F;` |
| 73 | `#181818` |  | `--lp-modules-gap: #181818;` |
| 74 | `#0D0D0D` |  | `--lp-panel-bg: #0D0D0D;` |
| 75 | `#1A1A1A` |  | `--lp-panel-border: #1A1A1A;` |
| 76 | `#181818` |  | `--lp-stat-border: #181818;` |
| 77 | `#161616` |  | `--lp-row-dot: #161616;` |
| 78 | `#111111` |  | `--lp-adv-border: #111111;` |
| 79 | `#0D0D0D` |  | `--lp-adv-hover: #0D0D0D;` |
| 80 | `#111111` |  | `--lp-adv-body-border: #111111;` |
| 81 | `#0F0F0F` |  | `--lp-adv-li-border: #0F0F0F;` |
| 82 | `#1A1A1A` |  | `--lp-report-border: #1A1A1A;` |
| 83 | `#0A0A0A` | LEGACY | `--lp-report-stats-bg: #0A0A0A;` |
| 84 | `#1A1A1A` |  | `--lp-pricing-border: #1A1A1A;` |
| 85 | `#111111` |  | `--lp-pricing-row-border: #111111;` |
| 88 | `#1A1A1A` |  | `--lp-audience-border: #1A1A1A;` |
| 89 | `#080808` |  | `--lp-cta-bg: #080808;` |
| 90 | `#060808` |  | `--lp-footer-bg: #060808;` |
| 91 | `#111111` |  | `--lp-footer-border: #111111;` |
| 92 | `#181818` |  | `--lp-hero-stat-border: #181818;` |
| 93 | `#181818` |  | `--lp-divider: #181818;` |
| 94 | `#333333` |  | `--lp-data-slbl: #333333;` |
| 95 | `#181818` |  | `--lp-bar-track: #181818;` |
| 96 | `#5A8A5A` |  | `--lp-ck: #5A8A5A;` |
| 97 | `#222222` |  | `--lp-ds: #222222;` |
| 98 | `#555555` |  | `--lp-btn-outline-color: #555555;` |
| 99 | `#2A2A2A` |  | `--lp-btn-outline-border: #2A2A2A;` |
| 100 | `#2A2A2A` |  | `--lp-footer-link: #2A2A2A;` |
| 101 | `#1E1E1E` |  | `--lp-footer-copy: #1E1E1E;` |
| 102 | `#555555` |  | `--lp-nav-link: #555555;` |
| 103 | `#2A2A2A` |  | `--lp-section-meta: #2A2A2A;` |
| 104 | `#444444` |  | `--lp-module-n: #444444;` |
| 105 | `#333333` |  | `--lp-adv-num: #333333;` |
| 106 | `#555555` |  | `--lp-adv-name: #555555;` |
| 107 | `#2A2A2A` |  | `--lp-adv-plus: #2A2A2A;` |
| 108 | `#444444` |  | `--lp-report-meta: #444444;` |
| 109 | `#444444` |  | `--lp-report-stat-k: #444444;` |
| 110 | `#181818` |  | `--lp-data-header-border: #181818;` |
| 111 | `#161616` |  | `--lp-data-row-border: #161616;` |
| 112 | `#1A1A1A` |  | `--lp-price-row-border: #1A1A1A;` |
| 116 | `#FFFFFF` |  | `--lp-bg: #FFFFFF;` |
| 117 | `#FFFFFF` |  | `--lp-bg-alt: #FFFFFF;` |
| 118 | `#FFFFFF` |  | `--lp-nav-bg: #FFFFFF;` |
| 119 | `#FFFFFF` |  | `--lp-surface: #FFFFFF;` |
| 120 | `#E0E0DC` |  | `--lp-border: #E0E0DC;` |
| 121 | `#DEDEDA` |  | `--lp-border-mid: #DEDEDA;` |
| 122 | `#E8E8E4` |  | `--lp-border-light: #E8E8E4;` |
| 123 | `#1A1A1A` |  | `--lp-text: #1A1A1A;` |
| 124 | `#666666` |  | `--lp-text-muted: #666666;` |
| 125 | `#888888` |  | `--lp-text-faint: #888888;` |
| 126 | `#AAAAAA` |  | `--lp-text-vfaint: #AAAAAA;` |
| 127 | `#DDDDDD` |  | `--lp-text-dot: #DDDDDD;` |
| 128 | `#FFFFFF` |  | `--lp-module-bg: #FFFFFF;` |
| 129 | `#F5F5F5` |  | `--lp-module-hover: #F5F5F5;` |
| 130 | `#DDDDD9` |  | `--lp-modules-gap: #DDDDD9;` |
| 131 | `#FFFFFF` |  | `--lp-panel-bg: #FFFFFF;` |
| 132 | `#E0E0DC` |  | `--lp-panel-border: #E0E0DC;` |
| 133 | `#E0E0DC` |  | `--lp-stat-border: #E0E0DC;` |
| 134 | `#DEDEDE` |  | `--lp-row-dot: #DEDEDE;` |
| 135 | `#E8E8E4` |  | `--lp-adv-border: #E8E8E4;` |
| 136 | `#F5F5F5` |  | `--lp-adv-hover: #F5F5F5;` |
| 137 | `#E8E8E4` |  | `--lp-adv-body-border: #E8E8E4;` |
| 138 | `#F0F0EC` |  | `--lp-adv-li-border: #F0F0EC;` |
| 139 | `#E0E0DC` |  | `--lp-report-border: #E0E0DC;` |
| 140 | `#FFFFFF` |  | `--lp-report-stats-bg: #FFFFFF;` |
| 141 | `#E0E0DC` |  | `--lp-pricing-border: #E0E0DC;` |
| 142 | `#EEEEEA` |  | `--lp-pricing-row-border: #EEEEEA;` |
| 145 | `#E0E0DC` |  | `--lp-audience-border: #E0E0DC;` |
| 146 | `#FFFFFF` |  | `--lp-cta-bg: #FFFFFF;` |
| 147 | `#FAFAFA` |  | `--lp-footer-bg: #FAFAFA;` |
| 148 | `#DDDDD9` |  | `--lp-footer-border: #DDDDD9;` |
| 149 | `#E0E0DC` |  | `--lp-hero-stat-border: #E0E0DC;` |
| 150 | `#E0E0DC` |  | `--lp-divider: #E0E0DC;` |
| 151 | `#AAAAAA` |  | `--lp-data-slbl: #AAAAAA;` |
| 152 | `#E0E0DC` |  | `--lp-bar-track: #E0E0DC;` |
| 153 | `#3A7A3A` |  | `--lp-ck: #3A7A3A;` |
| 154 | `#CCCCCC` |  | `--lp-ds: #CCCCCC;` |
| 155 | `#888888` |  | `--lp-btn-outline-color: #888888;` |
| 156 | `#CCCCCC` |  | `--lp-btn-outline-border: #CCCCCC;` |
| 157 | `#AAAAAA` |  | `--lp-footer-link: #AAAAAA;` |
| 158 | `#BBBBBB` |  | `--lp-footer-copy: #BBBBBB;` |
| 159 | `#888888` |  | `--lp-nav-link: #888888;` |
| 160 | `#AAAAAA` |  | `--lp-section-meta: #AAAAAA;` |
| 161 | `#AAAAAA` |  | `--lp-module-n: #AAAAAA;` |
| 162 | `#AAAAAA` |  | `--lp-adv-num: #AAAAAA;` |
| 163 | `#888888` |  | `--lp-adv-name: #888888;` |
| 164 | `#CCCCCC` |  | `--lp-adv-plus: #CCCCCC;` |
| 165 | `#AAAAAA` |  | `--lp-report-meta: #AAAAAA;` |
| 166 | `#AAAAAA` |  | `--lp-report-stat-k: #AAAAAA;` |
| 167 | `#E0E0DC` |  | `--lp-data-header-border: #E0E0DC;` |
| 168 | `#EEEEEA` |  | `--lp-data-row-border: #EEEEEA;` |
| 169 | `#E0E0DC` |  | `--lp-price-row-border: #E0E0DC;` |
| 176 | `#FAFAFA` | fallback | `body.lp-light .lp-plan-featured { background: var(--lp-featured-bg, #FAFAFA); }` |
| 277 | `#FFFFFF` | fallback | `color: var(--on-action, #FFFFFF);` |
| 299 | `#fff` |  | `color: #fff;` |
| 304 | `#3A6A8E` | LEGACY | `background: #3A6A8E;` |
| 398 | `#333333` |  | `color: #333333;` |
| 738 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 739 | `#4A7FA5` | LEGACY fallback | `border: 1px solid var(--lp-action-text, #4A7FA5);` |
| 746 | `#4A7FA5` | LEGACY fallback | `.mk-nav-cta:hover { background: var(--lp-action, #4A7FA5); color: var(--lp-on-action, #FFFFFF); }` |
| 746 | `#FFFFFF` | fallback | `.mk-nav-cta:hover { background: var(--lp-action, #4A7FA5); color: var(--lp-on-action, #FFFFFF); }` |
| 772 | `#4A7FA5` | LEGACY fallback | `background: var(--lp-acc-blue, #4A7FA5);` |
| 819 | `rgba(0,0,0,0.6)` | fallback | `background: var(--lp-overlay, rgba(0,0,0,0.6));` |
| 941 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 942 | `#4A7FA5` | LEGACY fallback | `border: 1px solid var(--lp-action-text, #4A7FA5);` |
| 950 | `#4A7FA5` | LEGACY fallback | `.lp-mobile-panel-register:hover { background: var(--lp-action, #4A7FA5); color: var(--lp-on-action, #FFFFFF); ` |
| 950 | `#FFFFFF` | fallback | `.lp-mobile-panel-register:hover { background: var(--lp-action, #4A7FA5); color: var(--lp-on-action, #FFFFFF); ` |
| 987 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1008 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1019 | `#4A7FA5` | LEGACY fallback | `background: var(--lp-acc-blue, #4A7FA5);` |
| 1034 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1083 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1178 | `#4A7FA5` | LEGACY fallback | `background: var(--lp-acc-blue, #4A7FA5) !important;` |
| 1198 | `#4A7FA5` | LEGACY fallback | `background: var(--lp-acc-blue, #4A7FA5);` |
| 1208 | `#4A7FA5` | LEGACY fallback | `background: var(--lp-action, #4A7FA5);` |
| 1209 | `#FFFFFF` | fallback | `color: var(--lp-on-action, #FFFFFF);` |
| 1243 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1244 | `#4A7FA5` | LEGACY fallback | `border: 1px solid var(--lp-action-text, #4A7FA5);` |
| 1253 | `#4A7FA5` | LEGACY fallback | `.btn-accent-outline:hover { background: var(--lp-action, #4A7FA5); color: var(--lp-on-action, #FFFFFF); }` |
| 1253 | `#FFFFFF` | fallback | `.btn-accent-outline:hover { background: var(--lp-action, #4A7FA5); color: var(--lp-on-action, #FFFFFF); }` |
| 1282 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1379 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1401 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1433 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1587 | `#4A7FA5` | LEGACY fallback | `background: var(--lp-acc-blue, #4A7FA5);` |
| 1602 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1618 | `#4A7FA5` | LEGACY fallback | `color: var(--lp-action-text, #4A7FA5);` |
| 1845 | `#4A7FA5` | LEGACY fallback | `border-color: var(--lp-action, #4A7FA5);` |
| 1876 | `#4A7FA5` | LEGACY fallback | `.lp-plan-featured .lp-plan-amount { color: var(--lp-action-text, #4A7FA5); }` |
| 1968 | `#888888` | fallback | `.lp-cta-signin a:hover { color: var(--lp-text-2, #888888); }` |
| 2250 | `#4A7FA5` | LEGACY fallback | `border-bottom-color: var(--lp-action, #4A7FA5) !important;` |
| 2320 | `#4A7FA5` | LEGACY fallback | `a.lp-contact-info-val:hover { color: var(--lp-action, #4A7FA5); }` |
| 2456 | `#4A7FA5` | LEGACY fallback | `border-left-color: var(--lp-acc-blue, #4A7FA5);` |
| 3147 | `rgba(15,15,14,0.6)` |  | `--lp-overlay: rgba(15,15,14,0.6);` |
| 3170 | `#4A9B6F` | LEGACY | `--lp-ck: #4A9B6F;` |
| 3230 | `rgba(31,30,28,0.35)` |  | `--lp-overlay: rgba(31,30,28,0.35);` |
| 3231 | `#2F7D55` |  | `--lp-ck: #2F7D55;` |

## `static/css/style.css`

| Line | Colour | Note | Context |
|---|---|---|---|
| 358 | `#555555` | fallback | `color: var(--text-faint, #555555);` |
| 1166 | `rgba(15,15,14,0.18)` |  | `box-shadow: 0 8px 32px rgba(15,15,14,0.18);` |
| 2367 | `#4A7FA5` | LEGACY | `.bar-cal-day.src-manual-override  { background: #4A7FA5; color: #fff; }` |
| 2367 | `#fff` |  | `.bar-cal-day.src-manual-override  { background: #4A7FA5; color: #fff; }` |
| 2368 | `#5A8CB0` |  | `.bar-cal-day.src-live-booking      { background: #5A8CB0; color: #fff; }` |
| 2368 | `#fff` |  | `.bar-cal-day.src-live-booking      { background: #5A8CB0; color: #fff; }` |
| 2369 | `#9EC3DC` |  | `.bar-cal-day.src-recent            { background: #9EC3DC; color: #fff; }` |
| 2369 | `#fff` |  | `.bar-cal-day.src-recent            { background: #9EC3DC; color: #fff; }` |
| 2370 | `#4A7FA5` | LEGACY | `.bar-cal-day.src-live-expedia      { background: #4A7FA5; color: #fff; }` |
| 2370 | `#fff` |  | `.bar-cal-day.src-live-expedia      { background: #4A7FA5; color: #fff; }` |
| 2371 | `rgba(255,255,255,0.04)` |  | `.bar-cal-day.src-estimated         { background: rgba(255,255,255,0.04); color: var(--text-muted); border: 1px` |
| 2419 | `#4A7FA5` | LEGACY | `.dot-live-google, .dot-live-brand { background: #4A7FA5; }` |
| 2420 | `#5A8CB0` |  | `.dot-live-booking                  { background: #5A8CB0; }` |
| 2421 | `rgba(255,255,255,0.15)` |  | `.dot-estimated                     { background: rgba(255,255,255,0.15); border: 1px solid var(--border); }` |
| 4824 | `#fff` |  | `body { background: #fff !important; color: #000 !important; font-family: 'Sweet Sans Pro', sans-serif; }` |
| 4824 | `#000` |  | `body { background: #fff !important; color: #000 !important; font-family: 'Sweet Sans Pro', sans-serif; }` |
| 4828 | `#000` |  | `.screen-header h1 { font-size: 22px; color: #000; margin-bottom: 4px; }` |
| 4829 | `#555` |  | `.screen-header p { font-size: 11px; color: #555; margin-bottom: 20px; }` |
| 4832 | `#fff` |  | `background: #fff !important; border: 1px solid #ccc !important;` |
| 4832 | `#ccc` |  | `background: #fff !important; border: 1px solid #ccc !important;` |
| 4836 | `#333` |  | `.news-body { display: block !important; color: #333 !important; }` |
| 4837 | `#000` |  | `.news-headline { color: #000 !important; font-size: 16px; }` |
| 4838 | `#333` |  | `.news-summary { color: #333 !important; }` |
| 4839 | `#999` |  | `.news-cat { border: 1px solid #999 !important; color: #333 !important; background: #f5f5f5 !important; }` |
| 4839 | `#333` |  | `.news-cat { border: 1px solid #999 !important; color: #333 !important; background: #f5f5f5 !important; }` |
| 4839 | `#f5f5f5` |  | `.news-cat { border: 1px solid #999 !important; color: #333 !important; background: #f5f5f5 !important; }` |
| 5818 | `rgba(90,138,90,0.20)` |  | `.val-sens-high      { background: rgba(90,138,90,0.20);  color: #5A8A5A; }` |
| 5818 | `#5A8A5A` |  | `.val-sens-high      { background: rgba(90,138,90,0.20);  color: #5A8A5A; }` |
| 5819 | `rgba(74,127,165,0.15)` |  | `.val-sens-mid-high  { background: rgba(74,127,165,0.15); color: #4A7FA5; }` |
| 5819 | `#4A7FA5` | LEGACY | `.val-sens-mid-high  { background: rgba(74,127,165,0.15); color: #4A7FA5; }` |
| 5820 | `rgba(74,127,165,0.15)` |  | `.val-sens-mid       { background: rgba(74,127,165,0.15); color: #4A7FA5; }` |
| 5820 | `#4A7FA5` | LEGACY | `.val-sens-mid       { background: rgba(74,127,165,0.15); color: #4A7FA5; }` |
| 5821 | `rgba(200,96,96,0.15)` |  | `.val-sens-low       { background: rgba(200,96,96,0.15);  color: #C86060; }` |
| 5821 | `#C86060` |  | `.val-sens-low       { background: rgba(200,96,96,0.15);  color: #C86060; }` |

## `static/images/news-placeholder.svg`

| Line | Colour | Note | Context |
|---|---|---|---|
| 2 | `#141414` | LEGACY | `<rect width="800" height="450" fill="#141414"/>` |
| 3 | `#242424` | LEGACY | `<rect x="0.5" y="0.5" width="799" height="449" fill="none" stroke="#242424"/>` |
| 4 | `#B87860` |  | `<text x="400" y="235" font-family="'Space Mono', monospace" font-size="14" letter-spacing="6" fill="#B87860" t` |

## `static/js/admin.js`

| Line | Colour | Note | Context |
|---|---|---|---|
| 824 | `#4A7FA5` | LEGACY | `${a.featured ? '<span class="adm-row-sub" style="color:#4A7FA5">Featured</span>' : ''}` |
| 1076 | `#F2A33D` | LEGACY | `statusEl.style.color = data.scheduler_running ? 'var(--positive)' : '#F2A33D';` |

## `static/js/main.js`

| Line | Colour | Note | Context |
|---|---|---|---|
| 199 | `#4A7FA5` | LEGACY | `'Ultra Luxury': '#4A7FA5',` |
| 200 | `#6B8CAA` |  | `'Luxury':       '#6B8CAA',` |
| 201 | `#7A9CB8` |  | `'Upper Upscale':'#7A9CB8',` |
| 202 | `#8CACC5` |  | `'Upscale':      '#8CACC5',` |
| 203 | `#9EBDD0` |  | `'Midscale':     '#9EBDD0',` |
| 204 | `#B0CDDD` |  | `'Economy':      '#B0CDDD',` |
| 232 | `#141414` | LEGACY | `{"elementType":"geometry","stylers":[{"color":"#141414"}]},` |
| 233 | `#888888` |  | `{"elementType":"labels.text.fill","stylers":[{"color":"#888888"}]},` |
| 234 | `#0A0A0A` | LEGACY | `{"elementType":"labels.text.stroke","stylers":[{"color":"#0A0A0A"}]},` |
| 235 | `#242424` | LEGACY | `{"featureType":"administrative","elementType":"geometry","stylers":[{"color":"#242424"}]},` |
| 236 | `#444444` |  | `{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"color":"#444444"}]},` |
| 237 | `#4A7FA5` | LEGACY | `{"featureType":"administrative.country","elementType":"labels.text.fill","stylers":[{"color":"#4A7FA5"}]},` |
| 238 | `#242424` | LEGACY | `{"featureType":"administrative.province","elementType":"geometry.stroke","stylers":[{"color":"#242424"}]},` |
| 239 | `#888888` |  | `{"featureType":"administrative.locality","elementType":"labels.text.fill","stylers":[{"color":"#888888"}]},` |
| 240 | `#242424` | LEGACY | `{"featureType":"road","elementType":"geometry","stylers":[{"color":"#242424"}]},` |
| 241 | `#141414` | LEGACY | `{"featureType":"road","elementType":"geometry.stroke","stylers":[{"color":"#141414"}]},` |
| 242 | `#2E2E2E` |  | `{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#2E2E2E"}]},` |
| 243 | `#0A0A0A` | LEGACY | `{"featureType":"water","elementType":"geometry","stylers":[{"color":"#0A0A0A"}]},` |
| 248 | `#F5F5F5` |  | `{"elementType":"geometry","stylers":[{"color":"#F5F5F5"}]},` |
| 249 | `#616161` |  | `{"elementType":"labels.text.fill","stylers":[{"color":"#616161"}]},` |
| 250 | `#F5F5F5` |  | `{"elementType":"labels.text.stroke","stylers":[{"color":"#F5F5F5"}]},` |
| 251 | `#CCCCCC` |  | `{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"color":"#CCCCCC"}]},` |
| 252 | `#FFFFFF` |  | `{"featureType":"road","elementType":"geometry","stylers":[{"color":"#FFFFFF"}]},` |
| 253 | `#E0E0E0` |  | `{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#E0E0E0"}]},` |
| 254 | `#C9D8E8` |  | `{"featureType":"water","elementType":"geometry","stylers":[{"color":"#C9D8E8"}]},` |
| 315 | `#4A7FA5` | LEGACY | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 315 | `#6B8CAA` |  | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 315 | `#5A9AA8` |  | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 315 | `#7A6A8A` |  | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 315 | `#4A6E8A` |  | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 316 | `#6A7A9A` |  | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 316 | `#6A8A6A` |  | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 316 | `#8A5A7A` |  | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 316 | `#9A8A5A` |  | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 316 | `#3A6A8E` | LEGACY | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 484 | `#555555` |  | `barColor:   dark ? '#555555' : '#AAAAAA',` |
| 484 | `#AAAAAA` |  | `barColor:   dark ? '#555555' : '#AAAAAA',` |
| 485 | `#777777` |  | `barColor2:  dark ? '#777777' : '#888888',` |
| 485 | `#888888` |  | `barColor2:  dark ? '#777777' : '#888888',` |
| 486 | `#444444` |  | `barColor3:  dark ? '#444444' : '#BBBBBB',` |
| 486 | `#BBBBBB` |  | `barColor3:  dark ? '#444444' : '#BBBBBB',` |
| 487 | `#666666` |  | `barColor4:  dark ? '#666666' : '#999999',` |
| 487 | `#999999` |  | `barColor4:  dark ? '#666666' : '#999999',` |
| 488 | `#4A7FA5` | LEGACY | `hoverColor: '#4A7FA5',` |
| 489 | `rgba(85,85,85,0.10)` |  | `fillColor:  dark ? 'rgba(85,85,85,0.10)' : 'rgba(170,170,170,0.14)',` |
| 489 | `rgba(170,170,170,0.14)` |  | `fillColor:  dark ? 'rgba(85,85,85,0.10)' : 'rgba(170,170,170,0.14)',` |
| 491 | `#888888` |  | `tick:       dark ? '#888888' : '#888888',` |
| 491 | `#888888` |  | `tick:       dark ? '#888888' : '#888888',` |
| 492 | `#888888` |  | `label:      dark ? '#888888' : '#888888',` |
| 492 | `#888888` |  | `label:      dark ? '#888888' : '#888888',` |
| 493 | `#AAAAAA` |  | `catLabel:   dark ? '#AAAAAA' : '#555555',` |
| 493 | `#555555` |  | `catLabel:   dark ? '#AAAAAA' : '#555555',` |
| 494 | `#141414` | LEGACY | `tooltipBg:  dark ? '#141414' : '#FFFFFF',` |
| 494 | `#FFFFFF` |  | `tooltipBg:  dark ? '#141414' : '#FFFFFF',` |
| 495 | `#242424` | LEGACY | `tooltipBdr: dark ? '#242424' : '#E4E4E4',` |
| 495 | `#E4E4E4` |  | `tooltipBdr: dark ? '#242424' : '#E4E4E4',` |
| 496 | `#F0F0EE` | LEGACY | `tooltipTtl: dark ? '#F0F0EE' : '#1A1A1A',` |
| 496 | `#1A1A1A` |  | `tooltipTtl: dark ? '#F0F0EE' : '#1A1A1A',` |
| 497 | `#888888` |  | `tooltipBdy: dark ? '#888888' : '#888888',` |
| 497 | `#888888` |  | `tooltipBdy: dark ? '#888888' : '#888888',` |
| 570 | `rgba(240,240,238,0.5)` |  | `const color = dark ? 'rgba(240,240,238,0.5)' : 'rgba(0,0,0,0.45)';` |
| 570 | `rgba(0,0,0,0.45)` |  | `const color = dark ? 'rgba(240,240,238,0.5)' : 'rgba(0,0,0,0.45)';` |
| 761 | `#888888` |  | `color: BRAND_PALETTE[i] ¦¦ '#888888',` |
| 763 | `#444444` |  | `if (otherKeys > 0) segs.push({ name: 'Other', pct: otherKeys / total * 100, color: '#444444' });` |
| 1395 | `#888888` |  | `const dayNumCol = dark ? '#888888' : '#AAAAAA';` |
| 1395 | `#AAAAAA` |  | `const dayNumCol = dark ? '#888888' : '#AAAAAA';` |
| 1409 | `#6AAF8A` |  | `if (occ >= 80) { bg = '#6AAF8A'; col = '#0A0A0A'; fw = '600'; }` |
| 1409 | `#0A0A0A` | LEGACY | `if (occ >= 80) { bg = '#6AAF8A'; col = '#0A0A0A'; fw = '600'; }` |
| 1410 | `#3D7A5C` |  | `else if (occ >= 60) { bg = '#3D7A5C'; col = '#F0EDE6'; fw = '500'; }` |
| 1410 | `#F0EDE6` |  | `else if (occ >= 60) { bg = '#3D7A5C'; col = '#F0EDE6'; fw = '500'; }` |
| 1411 | `#2A5A3A` |  | `else if (occ >= 40) { bg = '#2A5A3A'; col = '#B0D8C0'; fw = ''; }` |
| 1411 | `#B0D8C0` |  | `else if (occ >= 40) { bg = '#2A5A3A'; col = '#B0D8C0'; fw = ''; }` |
| 1412 | `#1A2A1A` |  | `else { bg = '#1A2A1A'; col = '#6A9A7A'; border = '1px solid #2A5A3A'; }` |
| 1412 | `#6A9A7A` |  | `else { bg = '#1A2A1A'; col = '#6A9A7A'; border = '1px solid #2A5A3A'; }` |
| 1412 | `#2A5A3A` |  | `else { bg = '#1A2A1A'; col = '#6A9A7A'; border = '1px solid #2A5A3A'; }` |
| 1414 | `#B0E0C8` |  | `if (occ >= 80) { bg = '#B0E0C8'; col = '#0A4A2A'; fw = '600'; border = '1px solid #6AAF8A'; }` |
| 1414 | `#0A4A2A` |  | `if (occ >= 80) { bg = '#B0E0C8'; col = '#0A4A2A'; fw = '600'; border = '1px solid #6AAF8A'; }` |
| 1414 | `#6AAF8A` |  | `if (occ >= 80) { bg = '#B0E0C8'; col = '#0A4A2A'; fw = '600'; border = '1px solid #6AAF8A'; }` |
| 1415 | `#D0EDE0` |  | `else if (occ >= 60) { bg = '#D0EDE0'; col = '#1A5A3A'; fw = '500'; border = '1px solid #3D7A5C'; }` |
| 1415 | `#1A5A3A` |  | `else if (occ >= 60) { bg = '#D0EDE0'; col = '#1A5A3A'; fw = '500'; border = '1px solid #3D7A5C'; }` |
| 1415 | `#3D7A5C` |  | `else if (occ >= 60) { bg = '#D0EDE0'; col = '#1A5A3A'; fw = '500'; border = '1px solid #3D7A5C'; }` |
| 1416 | `#E5F5ED` |  | `else if (occ >= 40) { bg = '#E5F5ED'; col = '#2A6A4A'; border = '1px solid #9ED0B8'; }` |
| 1416 | `#2A6A4A` |  | `else if (occ >= 40) { bg = '#E5F5ED'; col = '#2A6A4A'; border = '1px solid #9ED0B8'; }` |
| 1416 | `#9ED0B8` |  | `else if (occ >= 40) { bg = '#E5F5ED'; col = '#2A6A4A'; border = '1px solid #9ED0B8'; }` |
| 1417 | `#FFFFFF` |  | `else { bg = '#FFFFFF'; col = '#8A8A8A'; border = '1px solid #ECECEC'; }` |
| 1417 | `#8A8A8A` |  | `else { bg = '#FFFFFF'; col = '#8A8A8A'; border = '1px solid #ECECEC'; }` |
| 1417 | `#ECECEC` |  | `else { bg = '#FFFFFF'; col = '#8A8A8A'; border = '1px solid #ECECEC'; }` |
| 1420 | `#181818` |  | `bg = dark ? '#181818' : '#F8F8F8';` |
| 1420 | `#F8F8F8` |  | `bg = dark ? '#181818' : '#F8F8F8';` |
| 1421 | `#444` |  | `col = dark ? '#444' : '#BBB';` |
| 1421 | `#BBB` |  | `col = dark ? '#444' : '#BBB';` |
| 1422 | `#333` |  | `border = dark ? '1px dashed #333' : '1px dashed #DDD';` |
| 1422 | `#DDD` |  | `border = dark ? '1px dashed #333' : '1px dashed #DDD';` |
| 1598 | `#4A7FA5` | LEGACY | `fillColor:   highlighted ? '#4A7FA5' : '#666666',` |
| 1598 | `#666666` |  | `fillColor:   highlighted ? '#4A7FA5' : '#666666',` |
| 1600 | `rgba(255,255,255,0.15)` |  | `strokeColor: 'rgba(255,255,255,0.15)',` |
| 2235 | `#5B8DB8` |  | `const FORECAST_BAR_COLOR = '#5B8DB8';` |
| 2370 | `#F9F6F0` |  | `pointBorderColor: '#F9F6F0', pointBorderWidth: 2,` |
| 2473 | `#4A7FA5` | LEGACY | `const color  = p.status === 'Under Construction' ? '#4A7FA5' : '#888888';` |
| 2473 | `#888888` |  | `const color  = p.status === 'Under Construction' ? '#4A7FA5' : '#888888';` |
| 3499 | `rgba(45,107,58,0.15)` |  | `if (modeEl) { modeEl.textContent = 'Live data available'; modeEl.style.background = 'rgba(45,107,58,0.15)'; mo` |
| 3782 | `#2A4A6B` |  | `if (adr >= 6000) return {bg:'#2A4A6B', col:'#FFFFFF',  fw:'600', border:''};` |
| 3782 | `#FFFFFF` |  | `if (adr >= 6000) return {bg:'#2A4A6B', col:'#FFFFFF',  fw:'600', border:''};` |
| 3783 | `#1A2E42` |  | `if (adr >= 4000) return {bg:'#1A2E42', col:'#8AB0D0',  fw:'500', border:''};` |
| 3783 | `#8AB0D0` |  | `if (adr >= 4000) return {bg:'#1A2E42', col:'#8AB0D0',  fw:'500', border:''};` |
| 3784 | `#0A1520` |  | `return {bg:'#0A1520', col:'#6A8AAA', fw:'', border:'1px solid #2A4A6B'};` |
| 3784 | `#6A8AAA` |  | `return {bg:'#0A1520', col:'#6A8AAA', fw:'', border:'1px solid #2A4A6B'};` |
| 3784 | `#2A4A6B` |  | `return {bg:'#0A1520', col:'#6A8AAA', fw:'', border:'1px solid #2A4A6B'};` |
| 3786 | `#D0E4F5` |  | `if (adr >= 6000) return {bg:'#D0E4F5', col:'#1A4A7A', fw:'600', border:'1px solid #5A90C8'};` |
| 3786 | `#1A4A7A` |  | `if (adr >= 6000) return {bg:'#D0E4F5', col:'#1A4A7A', fw:'600', border:'1px solid #5A90C8'};` |
| 3786 | `#5A90C8` |  | `if (adr >= 6000) return {bg:'#D0E4F5', col:'#1A4A7A', fw:'600', border:'1px solid #5A90C8'};` |
| 3787 | `#E8F2FC` |  | `if (adr >= 4000) return {bg:'#E8F2FC', col:'#2A6AAA', fw:'',    border:'1px solid #8AB8E0'};` |
| 3787 | `#2A6AAA` |  | `if (adr >= 4000) return {bg:'#E8F2FC', col:'#2A6AAA', fw:'',    border:'1px solid #8AB8E0'};` |
| 3787 | `#8AB8E0` |  | `if (adr >= 4000) return {bg:'#E8F2FC', col:'#2A6AAA', fw:'',    border:'1px solid #8AB8E0'};` |
| 3788 | `#F5F9FF` |  | `return {bg:'#F5F9FF', col:'#5A8AB0', fw:'', border:'1px solid #C0D8F0'};` |
| 3788 | `#5A8AB0` |  | `return {bg:'#F5F9FF', col:'#5A8AB0', fw:'', border:'1px solid #C0D8F0'};` |
| 3788 | `#C0D8F0` |  | `return {bg:'#F5F9FF', col:'#5A8AB0', fw:'', border:'1px solid #C0D8F0'};` |
| 3792 | `#7AB0D0` |  | `if (adr >= 6000) return {bg:'#7AB0D0', col:'#0A0A0A', fw:'600', border:''};` |
| 3792 | `#0A0A0A` | LEGACY | `if (adr >= 6000) return {bg:'#7AB0D0', col:'#0A0A0A', fw:'600', border:''};` |
| 3793 | `#4A7FA5` | LEGACY | `if (adr >= 4000) return {bg:'#4A7FA5', col:'#0A0A0A', fw:'500', border:''};` |
| 3793 | `#0A0A0A` | LEGACY | `if (adr >= 4000) return {bg:'#4A7FA5', col:'#0A0A0A', fw:'500', border:''};` |
| 3794 | `#2A5A8A` |  | `if (adr >= 2000) return {bg:'#2A5A8A', col:'#F0EDE6', fw:'', border:''};` |
| 3794 | `#F0EDE6` |  | `if (adr >= 2000) return {bg:'#2A5A8A', col:'#F0EDE6', fw:'', border:''};` |
| 3795 | `#1A2A3A` |  | `return {bg:'#1A2A3A', col:'#7A9AB5', fw:'', border:'1px solid #2A5A8A'};` |
| 3795 | `#7A9AB5` |  | `return {bg:'#1A2A3A', col:'#7A9AB5', fw:'', border:'1px solid #2A5A8A'};` |
| 3795 | `#2A5A8A` |  | `return {bg:'#1A2A3A', col:'#7A9AB5', fw:'', border:'1px solid #2A5A8A'};` |
| 3797 | `#B8D8EC` |  | `if (adr >= 6000) return {bg:'#B8D8EC', col:'#0A3050', fw:'600', border:'1px solid #7AB0D0'};` |
| 3797 | `#0A3050` |  | `if (adr >= 6000) return {bg:'#B8D8EC', col:'#0A3050', fw:'600', border:'1px solid #7AB0D0'};` |
| 3797 | `#7AB0D0` |  | `if (adr >= 6000) return {bg:'#B8D8EC', col:'#0A3050', fw:'600', border:'1px solid #7AB0D0'};` |
| 3798 | `#D8E8F2` |  | `if (adr >= 4000) return {bg:'#D8E8F2', col:'#1A4A6B', fw:'500', border:'1px solid #4A7FA5'};` |
| 3798 | `#1A4A6B` |  | `if (adr >= 4000) return {bg:'#D8E8F2', col:'#1A4A6B', fw:'500', border:'1px solid #4A7FA5'};` |
| 3798 | `#4A7FA5` | LEGACY | `if (adr >= 4000) return {bg:'#D8E8F2', col:'#1A4A6B', fw:'500', border:'1px solid #4A7FA5'};` |
| 3799 | `#EAF2F8` |  | `if (adr >= 2000) return {bg:'#EAF2F8', col:'#2A5A8A', fw:'',   border:'1px solid #9EC3DC'};` |
| 3799 | `#2A5A8A` |  | `if (adr >= 2000) return {bg:'#EAF2F8', col:'#2A5A8A', fw:'',   border:'1px solid #9EC3DC'};` |
| 3799 | `#9EC3DC` |  | `if (adr >= 2000) return {bg:'#EAF2F8', col:'#2A5A8A', fw:'',   border:'1px solid #9EC3DC'};` |
| 3800 | `#FFFFFF` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3800 | `#8A8A8A` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3800 | `#ECECEC` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3809 | `#1A4A3A` |  | `if (p >= 80) return {bg:'#1A4A3A', col:'#FFFFFF',  fw:'600', border:''};` |
| 3809 | `#FFFFFF` |  | `if (p >= 80) return {bg:'#1A4A3A', col:'#FFFFFF',  fw:'600', border:''};` |
| 3810 | `#0F2E24` |  | `if (p >= 60) return {bg:'#0F2E24', col:'#5A9A82',  fw:'500', border:''};` |
| 3810 | `#5A9A82` |  | `if (p >= 60) return {bg:'#0F2E24', col:'#5A9A82',  fw:'500', border:''};` |
| 3811 | `#051510` |  | `return {bg:'#051510', col:'#3A7A62', fw:'', border:'1px solid #1A4A3A'};` |
| 3811 | `#3A7A62` |  | `return {bg:'#051510', col:'#3A7A62', fw:'', border:'1px solid #1A4A3A'};` |
| 3811 | `#1A4A3A` |  | `return {bg:'#051510', col:'#3A7A62', fw:'', border:'1px solid #1A4A3A'};` |
| 3813 | `#D0EDE5` |  | `if (p >= 80) return {bg:'#D0EDE5', col:'#0A4A32', fw:'600', border:'1px solid #3A9A7A'};` |
| 3813 | `#0A4A32` |  | `if (p >= 80) return {bg:'#D0EDE5', col:'#0A4A32', fw:'600', border:'1px solid #3A9A7A'};` |
| 3813 | `#3A9A7A` |  | `if (p >= 80) return {bg:'#D0EDE5', col:'#0A4A32', fw:'600', border:'1px solid #3A9A7A'};` |
| 3814 | `#E5F5EF` |  | `if (p >= 60) return {bg:'#E5F5EF', col:'#1A6A4A', fw:'',    border:'1px solid #7ABDA8'};` |
| 3814 | `#1A6A4A` |  | `if (p >= 60) return {bg:'#E5F5EF', col:'#1A6A4A', fw:'',    border:'1px solid #7ABDA8'};` |
| 3814 | `#7ABDA8` |  | `if (p >= 60) return {bg:'#E5F5EF', col:'#1A6A4A', fw:'',    border:'1px solid #7ABDA8'};` |
| 3815 | `#F0FAF6` |  | `return {bg:'#F0FAF6', col:'#3A8A68', fw:'', border:'1px solid #B0D8C8'};` |
| 3815 | `#3A8A68` |  | `return {bg:'#F0FAF6', col:'#3A8A68', fw:'', border:'1px solid #B0D8C8'};` |
| 3815 | `#B0D8C8` |  | `return {bg:'#F0FAF6', col:'#3A8A68', fw:'', border:'1px solid #B0D8C8'};` |
| 3819 | `#6AAF8A` |  | `if (p >= 80) return {bg:'#6AAF8A', col:'#0A0A0A', fw:'600', border:''};` |
| 3819 | `#0A0A0A` | LEGACY | `if (p >= 80) return {bg:'#6AAF8A', col:'#0A0A0A', fw:'600', border:''};` |
| 3820 | `#3D7A5C` |  | `if (p >= 60) return {bg:'#3D7A5C', col:'#F0EDE6', fw:'500', border:''};` |
| 3820 | `#F0EDE6` |  | `if (p >= 60) return {bg:'#3D7A5C', col:'#F0EDE6', fw:'500', border:''};` |
| 3821 | `#2A5A3A` |  | `if (p >= 40) return {bg:'#2A5A3A', col:'#B0D8C0', fw:'', border:''};` |
| 3821 | `#B0D8C0` |  | `if (p >= 40) return {bg:'#2A5A3A', col:'#B0D8C0', fw:'', border:''};` |
| 3822 | `#1A2A1A` |  | `return {bg:'#1A2A1A', col:'#6A9A7A', fw:'', border:'1px solid #2A5A3A'};` |
| 3822 | `#6A9A7A` |  | `return {bg:'#1A2A1A', col:'#6A9A7A', fw:'', border:'1px solid #2A5A3A'};` |
| 3822 | `#2A5A3A` |  | `return {bg:'#1A2A1A', col:'#6A9A7A', fw:'', border:'1px solid #2A5A3A'};` |
| 3824 | `#B0E0C8` |  | `if (p >= 80) return {bg:'#B0E0C8', col:'#0A4A2A', fw:'600', border:'1px solid #6AAF8A'};` |
| 3824 | `#0A4A2A` |  | `if (p >= 80) return {bg:'#B0E0C8', col:'#0A4A2A', fw:'600', border:'1px solid #6AAF8A'};` |
| 3824 | `#6AAF8A` |  | `if (p >= 80) return {bg:'#B0E0C8', col:'#0A4A2A', fw:'600', border:'1px solid #6AAF8A'};` |
| 3825 | `#D0EDE0` |  | `if (p >= 60) return {bg:'#D0EDE0', col:'#1A5A3A', fw:'500', border:'1px solid #3D7A5C'};` |
| 3825 | `#1A5A3A` |  | `if (p >= 60) return {bg:'#D0EDE0', col:'#1A5A3A', fw:'500', border:'1px solid #3D7A5C'};` |
| 3825 | `#3D7A5C` |  | `if (p >= 60) return {bg:'#D0EDE0', col:'#1A5A3A', fw:'500', border:'1px solid #3D7A5C'};` |
| 3826 | `#E5F5ED` |  | `if (p >= 40) return {bg:'#E5F5ED', col:'#2A6A4A', fw:'',   border:'1px solid #9ED0B8'};` |
| 3826 | `#2A6A4A` |  | `if (p >= 40) return {bg:'#E5F5ED', col:'#2A6A4A', fw:'',   border:'1px solid #9ED0B8'};` |
| 3826 | `#9ED0B8` |  | `if (p >= 40) return {bg:'#E5F5ED', col:'#2A6A4A', fw:'',   border:'1px solid #9ED0B8'};` |
| 3827 | `#FFFFFF` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3827 | `#8A8A8A` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3827 | `#ECECEC` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3880 | `#888888` |  | `const dayNumCol = dark ? '#888888' : '#AAAAAA';` |
| 3880 | `#AAAAAA` |  | `const dayNumCol = dark ? '#888888' : '#AAAAAA';` |
| 3985 | `rgba(74,127,165,0.08)` |  | `backgroundColor: 'rgba(74,127,165,0.08)', borderWidth: 2, fill: false,` |
| 4057 | `rgba(119,119,119,0.35)` |  | `dowDatasets.push({ label: 'Comp Set Avg', data: compDOW.map(avg), backgroundColor: 'rgba(119,119,119,0.35)', b` |

## `templates/accept_invite.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/account.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/admin.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/contact.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 155 | `#5A8A5A` |  | `<span style="font-family:'Sweet Sans Pro',sans-serif;font-size:9px;text-transform:uppercase;letter-spacing:0.1` |
| 161 | `#C86060` |  | `<span style="font-family:'Sweet Sans Pro',sans-serif;font-size:9px;text-transform:uppercase;letter-spacing:0.1` |
| 192 | `#4A7FA5` | LEGACY | `<span style="font-family:'Sweet Sans Pro',sans-serif;font-size:8px;color:#4A7FA5;flex-shrink:0;padding-top:2px` |
| 196 | `#4A7FA5` | LEGACY | `<span style="font-family:'Sweet Sans Pro',sans-serif;font-size:8px;color:#4A7FA5;flex-shrink:0;padding-top:2px` |
| 200 | `#4A7FA5` | LEGACY | `<span style="font-family:'Sweet Sans Pro',sans-serif;font-size:8px;color:#4A7FA5;flex-shrink:0;padding-top:2px` |

## `templates/forgot_password.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/index.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 120 | `#6B8CAA` |  | `<span class="seg-pip" style="background:#6B8CAA"></span>Luxury` |
| 123 | `#7A9CB8` |  | `<span class="seg-pip" style="background:#7A9CB8"></span>Upper Upscale` |
| 126 | `#8CACC5` |  | `<span class="seg-pip" style="background:#8CACC5"></span>Upscale` |
| 129 | `#9EBDD0` |  | `<span class="seg-pip" style="background:#9EBDD0"></span>Midscale` |
| 239 | `#666666` |  | `<span class="map-legend-dot-slot"><span class="map-legend-dot" style="width:8px;height:8px;background:#666666;` |
| 243 | `#666666` |  | `<span class="map-legend-dot-slot"><span class="map-legend-dot" style="width:12px;height:12px;background:#66666` |
| 247 | `#666666` |  | `<span class="map-legend-dot-slot"><span class="map-legend-dot" style="width:16px;height:16px;background:#66666` |
| 251 | `#666666` |  | `<span class="map-legend-dot-slot"><span class="map-legend-dot" style="width:20px;height:20px;background:#66666` |
| 255 | `#4A7FA5` | LEGACY | `<span class="map-legend-dot-slot"><span class="map-legend-dot" style="width:10px;height:10px;background:#4A7FA` |
| 267 | `#4A7FA5` | LEGACY | `<span class="screen-header-legend-item"><span class="screen-header-legend-dot" style="background:#4A7FA5;"></s` |
| 268 | `#888888` |  | `<span class="screen-header-legend-item"><span class="screen-header-legend-dot" style="background:#888888;"></s` |
| 301 | `#4A7FA5` | LEGACY | `<span class="seg-dot" style="background:#4A7FA5"></span>Under Construction` |
| 304 | `#666666` |  | `<span class="seg-dot" style="background:#666666"></span>Planning` |
| 367 | `#4A7FA5` | LEGACY | `<span class="pipeline-legend-dot" style="background:#4A7FA5;"></span>` |
| 371 | `#888888` |  | `<span class="pipeline-legend-dot" style="background:#888888;"></span>` |
| 596 | `#1A2A3A` |  | `<span class="cal-legend-dot" style="background:#1A2A3A"></span>` |
| 600 | `#2A5A8A` |  | `<span class="cal-legend-dot" style="background:#2A5A8A"></span>` |
| 604 | `#4A7FA5` | LEGACY | `<span class="cal-legend-dot" style="background:#4A7FA5"></span>` |
| 608 | `#7AB0D0` |  | `<span class="cal-legend-dot" style="background:#7AB0D0"></span>` |
| 612 | `#4A7FA5` | LEGACY | `<span class="cal-legend-dot" style="background:#4A7FA5"></span>` |
| 616 | `#2A4A6B` |  | `<span class="cal-legend-dot" style="background:#2A4A6B"></span>` |
| 641 | `#1A2A1A` |  | `<span class="cal-legend-dot" style="background:#1A2A1A"></span>` |
| 645 | `#2A5A3A` |  | `<span class="cal-legend-dot" style="background:#2A5A3A"></span>` |
| 649 | `#3D7A5C` |  | `<span class="cal-legend-dot" style="background:#3D7A5C"></span>` |
| 653 | `#6AAF8A` |  | `<span class="cal-legend-dot" style="background:#6AAF8A"></span>` |
| 657 | `#6AAF8A` |  | `<span class="cal-legend-dot" style="background:#6AAF8A"></span>` |
| 661 | `#1A4A3A` |  | `<span class="cal-legend-dot" style="background:#1A4A3A"></span>` |
| 789 | `#4A7FA5` | LEGACY | `<span class="chart-dot-legend-item"><span class="chart-dot-legend-dot" style="background:#4A7FA5;"></span>ONMT` |
| 790 | `#5B8DB8` |  | `<span class="chart-dot-legend-item"><span class="chart-dot-legend-dot" style="background:#5B8DB8;"></span>2026` |
| 841 | `#4A7FA5` | LEGACY | `<span class="chart-dot-legend-item"><span class="chart-dot-legend-dot" style="background:#4A7FA5;"></span>ONMT` |
| 842 | `#5B8DB8` |  | `<span class="chart-dot-legend-item"><span class="chart-dot-legend-dot" style="background:#5B8DB8;"></span>2026` |
| 1553 | `#6AAF8A` |  | `<span class="bar-cal-leg-item"><span class="bar-cal-dot" style="background:#6AAF8A"></span>&gt;80%</span>` |
| 1554 | `#3D7A5C` |  | `<span class="bar-cal-leg-item"><span class="bar-cal-dot" style="background:#3D7A5C"></span>60–80%</span>` |
| 1555 | `#2A5A3A` |  | `<span class="bar-cal-leg-item"><span class="bar-cal-dot" style="background:#2A5A3A"></span>40–60%</span>` |
| 1556 | `#1A2A1A` |  | `<span class="bar-cal-leg-item"><span class="bar-cal-dot" style="background:#1A2A1A"></span>&lt;40%</span>` |

## `templates/landing.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#0075DE` |  | `<meta name="theme-color" content="#0075DE">` |

## `templates/login.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/methodology.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 304 | `#555555` |  | `<p style="font-size:12px;color:#555555;">Data is processed under a strict confidentiality agreement. Individua` |

## `templates/payment_pending.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/privacy.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/register.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/reset_password.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/terms.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/verify_email.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/verify_email_sent.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
