# Colour audit

Every hardcoded colour outside `static/css/tokens.css`, by file and line. Regenerate with `python3 scripts/color_audit.py`.

- **LEGACY**: an old palette value the final sweep must remove.
- **fallback**: the second argument of `var(--token, …)`; the page uses the token, the literal only applies where the token is undefined.

Total: 223 colour literals in 24 files (67 legacy).

## Per file

| File | Literals |
|---|---|
| `static/css/marketing.css` | 149 |
| `static/css/admin.css` | 15 |
| `static/css/style.css` | 14 |
| `app.py` | 13 |
| `templates/contact.html` | 5 |
| `generate_pdfs.py` | 4 |
| `static/images/news-placeholder.svg` | 3 |
| `static/js/admin.js` | 2 |
| `static/js/main.js` | 2 |
| `templates/methodology.html` | 2 |
| `templates/accept_invite.html` | 1 |
| `templates/account.html` | 1 |
| `templates/admin.html` | 1 |
| `templates/forgot_password.html` | 1 |
| `templates/index.html` | 1 |
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
| `#4A7FA5` | 54 |
| `#3A6A8E` | 3 |
| `#0A0A0A` | 3 |
| `#141414` | 2 |
| `#242424` | 2 |
| `#F0F0EE` | 1 |
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
| 480 | `rgba()` |  | `// Hex colour + alpha → rgba() (Chart.js draws on canvas, so no CSS variables)` |
| 484 | `rgba(${(n >> 16)` |  | `return rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a});` |

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
