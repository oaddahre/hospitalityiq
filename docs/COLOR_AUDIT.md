# Colour audit

Every hardcoded colour outside `static/css/tokens.css`, by file and line. Regenerate with `python3 scripts/color_audit.py`.

- **LEGACY**: an old palette value the final sweep must remove.
- **fallback**: the second argument of `var(--token, …)`; the page uses the token, the literal only applies where the token is undefined.

Total: 991 colour literals in 24 files (381 legacy).

## Per file

| File | Literals |
|---|---|
| `static/js/main.js` | 234 |
| `static/css/style.css` | 171 |
| `static/css/marketing.css` | 148 |
| `templates/index.html` | 54 |
| `app.py` | 53 |
| `templates/accept_invite.html` | 43 |
| `templates/register.html` | 43 |
| `templates/login.html` | 40 |
| `templates/reset_password.html` | 37 |
| `templates/forgot_password.html` | 36 |
| `templates/verify_email.html` | 32 |
| `templates/payment_pending.html` | 28 |
| `templates/verify_email_sent.html` | 21 |
| `templates/account.html` | 16 |
| `static/css/admin.css` | 15 |
| `templates/contact.html` | 5 |
| `generate_pdfs.py` | 4 |
| `static/images/news-placeholder.svg` | 3 |
| `static/js/admin.js` | 2 |
| `templates/methodology.html` | 2 |
| `templates/admin.html` | 1 |
| `templates/landing.html` | 1 |
| `templates/privacy.html` | 1 |
| `templates/terms.html` | 1 |

## Legacy values still present

| Value | Count |
|---|---|
| `#4A7FA5` | 209 |
| `#F0F0EE` | 50 |
| `#242424` | 40 |
| `#0A0A0A` | 35 |
| `#141414` | 20 |
| `#3A6A8E` | 14 |
| `#4A9B6F` | 5 |
| `#F2A33D` | 4 |
| `#6B7A8D` | 3 |
| `#C05252` | 1 |

## `app.py`

| Line | Colour | Note | Context |
|---|---|---|---|
| 434 | `#0A0A0A` | LEGACY | `<body style="margin:0;padding:0;background:#0A0A0A;font-family:'Manrope',sans-serif;">` |
| 435 | `#0A0A0A` | LEGACY | `<table width="100%" cellpadding="0" cellspacing="0" style="background:#0A0A0A;padding:40px 0;">` |
| 438 | `#141414` | LEGACY | `<table width="520" cellpadding="0" cellspacing="0" style="background:#141414;padding:48px;">` |
| 440 | `#242424` | LEGACY | `<td style="padding-bottom:32px;border-bottom:1px solid #242424;">` |
| 441 | `#4A7FA5` | LEGACY | `<p style="font-family:'Space Mono',monospace;font-size:12px;letter-spacing:0.2em;color:#4A7FA5;margin:0;text-t` |
| 446 | `#F0F0EE` | LEGACY | `<h1 style="font-size:24px;font-weight:800;color:#F0F0EE;margin:0 0 16px;letter-spacing:-0.02em;">Confirm your ` |
| 447 | `#888888` |  | `<p style="font-size:14px;color:#888888;line-height:1.7;margin:0;">One more step before you can log in — confir` |
| 452 | `#4A7FA5` | LEGACY | `<a href="{verify_url}" style="display:inline-block;background:#4A7FA5;color:#0A0A0A;font-family:'Space Mono',m` |
| 452 | `#0A0A0A` | LEGACY | `<a href="{verify_url}" style="display:inline-block;background:#4A7FA5;color:#0A0A0A;font-family:'Space Mono',m` |
| 456 | `#242424` | LEGACY | `<td style="border-top:1px solid #242424;padding-top:24px;">` |
| 457 | `#444444` |  | `<p style="font-size:12px;color:#444444;line-height:1.6;margin:0;">If you didn't create a Kodo account, you can` |
| 457 | `#4A7FA5` | LEGACY | `<p style="font-size:12px;color:#444444;line-height:1.6;margin:0;">If you didn't create a Kodo account, you can` |
| 510 | `#0A0A0A` | LEGACY | `<body style="margin:0;padding:0;background:#0A0A0A;font-family:'Manrope',sans-serif;">` |
| 511 | `#0A0A0A` | LEGACY | `<table width="100%" cellpadding="0" cellspacing="0" style="background:#0A0A0A;padding:40px 0;">` |
| 514 | `#141414` | LEGACY | `<table width="520" cellpadding="0" cellspacing="0" style="background:#141414;padding:48px;">` |
| 516 | `#242424` | LEGACY | `<td style="padding-bottom:32px;border-bottom:1px solid #242424;">` |
| 517 | `#4A7FA5` | LEGACY | `<p style="font-family:'Space Mono',monospace;font-size:12px;letter-spacing:0.2em;color:#4A7FA5;margin:0;text-t` |
| 522 | `#F0F0EE` | LEGACY | `<h1 style="font-size:24px;font-weight:800;color:#F0F0EE;margin:0 0 16px;letter-spacing:-0.02em;">Reset your pa` |
| 523 | `#888888` |  | `<p style="font-size:14px;color:#888888;line-height:1.7;margin:0;">We received a request to reset the password ` |
| 528 | `#4A7FA5` | LEGACY | `<a href="{reset_url}" style="display:inline-block;background:#4A7FA5;color:#0A0A0A;font-family:'Space Mono',mo` |
| 528 | `#0A0A0A` | LEGACY | `<a href="{reset_url}" style="display:inline-block;background:#4A7FA5;color:#0A0A0A;font-family:'Space Mono',mo` |
| 532 | `#242424` | LEGACY | `<td style="border-top:1px solid #242424;padding-top:24px;">` |
| 533 | `#444444` |  | `<p style="font-size:12px;color:#444444;line-height:1.6;margin:0;">If you did not request a password reset you ` |
| 533 | `#4A7FA5` | LEGACY | `<p style="font-size:12px;color:#444444;line-height:1.6;margin:0;">If you did not request a password reset you ` |
| 560 | `#0A0A0A` | LEGACY | `<body style="margin:0;padding:0;background:#0A0A0A;font-family:'Manrope',sans-serif;">` |
| 561 | `#0A0A0A` | LEGACY | `<table width="100%" cellpadding="0" cellspacing="0" style="background:#0A0A0A;padding:40px 0;">` |
| 564 | `#141414` | LEGACY | `<table width="520" cellpadding="0" cellspacing="0" style="background:#141414;padding:48px;">` |
| 566 | `#242424` | LEGACY | `<td style="padding-bottom:32px;border-bottom:1px solid #242424;">` |
| 567 | `#4A7FA5` | LEGACY | `<p style="font-family:'Space Mono',monospace;font-size:12px;letter-spacing:0.2em;color:#4A7FA5;margin:0;text-t` |
| 572 | `#F0F0EE` | LEGACY | `<h1 style="font-size:24px;font-weight:800;color:#F0F0EE;margin:0 0 16px;letter-spacing:-0.02em;">Welcome, {nam` |
| 573 | `#888888` |  | `<p style="font-size:14px;color:#888888;line-height:1.7;margin:0 0 12px;">Your account has been created. You no` |
| 574 | `#888888` |  | `<p style="font-size:14px;color:#888888;line-height:1.7;margin:0;">{status_line}</p>` |
| 579 | `#4A7FA5` | LEGACY | `<a href="https://www.kodohospitality.com/login" style="display:inline-block;background:#4A7FA5;color:#0A0A0A;f` |
| 579 | `#0A0A0A` | LEGACY | `<a href="https://www.kodohospitality.com/login" style="display:inline-block;background:#4A7FA5;color:#0A0A0A;f` |
| 586 | `#0A0A0A` | LEGACY | `<td width="33%" style="padding:16px;background:#0A0A0A;text-align:center;">` |
| 587 | `#4A7FA5` | LEGACY | `<p style="font-family:'Space Mono',monospace;font-size:18px;font-weight:400;color:#4A7FA5;margin:0 0 6px;">300` |
| 588 | `#444444` |  | `<p style="font-family:'Space Mono',monospace;font-size:8px;text-transform:uppercase;letter-spacing:0.12em;colo` |
| 590 | `#0A0A0A` | LEGACY | `<td width="33%" style="padding:16px;background:#0A0A0A;text-align:center;border-left:1px solid #141414;border-` |
| 590 | `#141414` | LEGACY | `<td width="33%" style="padding:16px;background:#0A0A0A;text-align:center;border-left:1px solid #141414;border-` |
| 590 | `#141414` | LEGACY | `<td width="33%" style="padding:16px;background:#0A0A0A;text-align:center;border-left:1px solid #141414;border-` |
| 591 | `#4A7FA5` | LEGACY | `<p style="font-family:'Space Mono',monospace;font-size:18px;font-weight:400;color:#4A7FA5;margin:0 0 6px;">23<` |
| 592 | `#444444` |  | `<p style="font-family:'Space Mono',monospace;font-size:8px;text-transform:uppercase;letter-spacing:0.12em;colo` |
| 594 | `#0A0A0A` | LEGACY | `<td width="33%" style="padding:16px;background:#0A0A0A;text-align:center;">` |
| 595 | `#4A7FA5` | LEGACY | `<p style="font-family:'Space Mono',monospace;font-size:18px;font-weight:400;color:#4A7FA5;margin:0 0 6px;">35<` |
| 596 | `#444444` |  | `<p style="font-family:'Space Mono',monospace;font-size:8px;text-transform:uppercase;letter-spacing:0.12em;colo` |
| 603 | `#242424` | LEGACY | `<td style="border-top:1px solid #242424;padding-top:24px;">` |
| 604 | `#444444` |  | `<p style="font-size:12px;color:#444444;line-height:1.6;margin:0;">Questions? Reply to this email or contact us` |
| 604 | `#4A7FA5` | LEGACY | `<p style="font-size:12px;color:#444444;line-height:1.6;margin:0;">Questions? Reply to this email or contact us` |
| 3377 | `set_text_color(255, 255, 255)` |  | `pdf.set_text_color(255, 255, 255)` |
| 3696 | `set_fill_color(10, 10, 10)` |  | `pdf.set_fill_color(10, 10, 10)` |
| 3700 | `set_text_color(255, 255, 255)` |  | `pdf.set_text_color(255, 255, 255)` |
| 3707 | `set_text_color(136, 136, 136)` |  | `pdf.set_text_color(136, 136, 136)` |
| 3710 | `set_text_color(68, 68, 68)` |  | `pdf.set_text_color(68, 68, 68)` |

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
| 200 | `#4A7FA5` | LEGACY | `border-bottom-color: #4A7FA5 !important;` |
| 264 | `#141414` | LEGACY | `border-bottom: 1px solid #141414;` |
| 334 | `#666666` |  | `color: #666666;` |
| 339 | `#F0F0EE` | LEGACY | `.nav-link:hover  { color: #F0F0EE; background: none; }` |
| 340 | `#F0F0EE` | LEGACY | `.nav-link.active { color: #F0F0EE; font-weight: 600; background: none; }` |
| 358 | `#555555` | fallback | `color: var(--text-faint, #555555);` |
| 362 | `#4A7FA5` | LEGACY | `.mk-toggle-opt.mk-toggle-active { color: #4A7FA5; }` |
| 395 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 397 | `#666666` |  | `color: #666666;` |
| 400 | `#4A7FA5` | LEGACY | `#theme-btn:hover { border-color: #4A7FA5; color: #4A7FA5; }` |
| 400 | `#4A7FA5` | LEGACY | `#theme-btn:hover { border-color: #4A7FA5; color: #4A7FA5; }` |
| 403 | `#ECECEC` |  | `body.light .navbar { border-bottom-color: #ECECEC; }` |
| 404 | `#8A8A8A` |  | `body.light .nav-link { color: #8A8A8A; }` |
| 405 | `#0A0A0A` | LEGACY | `body.light .nav-link:hover  { color: #0A0A0A; }` |
| 406 | `#0A0A0A` | LEGACY | `body.light .nav-link.active { color: #0A0A0A; font-weight: 600; }` |
| 407 | `#ECECEC` |  | `body.light .theme-toggle { border-color: #ECECEC; color: #8A8A8A; }` |
| 407 | `#8A8A8A` |  | `body.light .theme-toggle { border-color: #ECECEC; color: #8A8A8A; }` |
| 408 | `#4A7FA5` | LEGACY | `body.light .theme-toggle:hover { border-color: #4A7FA5; color: #4A7FA5; }` |
| 408 | `#4A7FA5` | LEGACY | `body.light .theme-toggle:hover { border-color: #4A7FA5; color: #4A7FA5; }` |
| 409 | `#ECECEC` |  | `body.light #theme-btn { border-color: #ECECEC; color: #8A8A8A; }` |
| 409 | `#8A8A8A` |  | `body.light #theme-btn { border-color: #ECECEC; color: #8A8A8A; }` |
| 410 | `#4A7FA5` | LEGACY | `body.light #theme-btn:hover { border-color: #4A7FA5; color: #4A7FA5; }` |
| 410 | `#4A7FA5` | LEGACY | `body.light #theme-btn:hover { border-color: #4A7FA5; color: #4A7FA5; }` |
| 411 | `#8A8A8A` |  | `body.light .nav-account { color: #8A8A8A; }` |
| 412 | `#8A8A8A` |  | `body.light .nav-logout  { color: #8A8A8A; }` |
| 432 | `#777777` |  | `.tier-badge--observer    { color: #777777; }` |
| 433 | `#999999` |  | `.tier-badge--benchmarker { color: #999999; }` |
| 524 | `#4A7FA5` | LEGACY | `.sidebar-item.active, .si.on { background: transparent; border-left-color: #4A7FA5; color: #4A7FA5; font-weigh` |
| 524 | `#4A7FA5` | LEGACY | `.sidebar-item.active, .si.on { background: transparent; border-left-color: #4A7FA5; color: #4A7FA5; font-weigh` |
| 579 | `#4A7FA5` | LEGACY | `.screen-sub-tags.accent { color: #4A7FA5; }` |
| 766 | `rgba(74,127,165,0.15)` |  | `.segment-ultra-luxury  { background: rgba(74,127,165,0.15);  color: #4A7FA5; }` |
| 766 | `#4A7FA5` | LEGACY | `.segment-ultra-luxury  { background: rgba(74,127,165,0.15);  color: #4A7FA5; }` |
| 767 | `rgba(74,127,165,0.15)` |  | `.segment-luxury        { background: rgba(74,127,165,0.15);  color: #4A7FA5; }` |
| 767 | `#4A7FA5` | LEGACY | `.segment-luxury        { background: rgba(74,127,165,0.15);  color: #4A7FA5; }` |
| 768 | `rgba(90,138,90,0.15)` |  | `.segment-upper-upscale { background: rgba(90,138,90,0.15);   color: #5A8A5A; }` |
| 768 | `#5A8A5A` |  | `.segment-upper-upscale { background: rgba(90,138,90,0.15);   color: #5A8A5A; }` |
| 769 | `rgba(100,130,180,0.15)` |  | `.segment-upscale       { background: rgba(100,130,180,0.15); color: #6482B4; }` |
| 769 | `#6482B4` |  | `.segment-upscale       { background: rgba(100,130,180,0.15); color: #6482B4; }` |
| 770 | `rgba(136,136,136,0.15)` |  | `.segment-midscale      { background: rgba(136,136,136,0.15); color: #888888; }` |
| 770 | `#888888` |  | `.segment-midscale      { background: rgba(136,136,136,0.15); color: #888888; }` |
| 771 | `rgba(100,100,100,0.12)` |  | `.segment-economy       { background: rgba(100,100,100,0.12); color: #666666; }` |
| 771 | `#666666` |  | `.segment-economy       { background: rgba(100,100,100,0.12); color: #666666; }` |
| 772 | `#5A8A5A` |  | `.status-badge { color: #5A8A5A; }` |
| 773 | `#888888` |  | `.owner-type-badge { color: #888888; }` |
| 775 | `#4A7FA5` | LEGACY | `.powered-by-kodo-badge { color: #4A7FA5; }` |
| 776 | `#888888` |  | `.data-quality-badge { color: #888888; }` |
| 781 | `#888888` |  | `.search-result-category { color: #888888; }` |
| 782 | `#888888` |  | `.bench-mode-badge { color: #888888; }` |
| 783 | `#888888` |  | `.confidence-badge { color: #888888; }` |
| 784 | `#4A7FA5` | LEGACY | `.nav-tier-badge { color: #4A7FA5; font-size: 11px !important; }` |
| 785 | `#4A7FA5` | LEGACY | `.pipeline-status-badge { color: #4A7FA5; }` |
| 1168 | `rgba(0,0,0,0.4)` |  | `box-shadow: 0 8px 32px rgba(0,0,0,0.4);` |
| 1183 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 1226 | `#0A0A0A` | LEGACY | `background: #0A0A0A;` |
| 1592 | `#5A8A5A` |  | `.status-open, .status-active { border-color: #5A8A5A; color: #5A8A5A; }` |
| 1592 | `#5A8A5A` |  | `.status-open, .status-active { border-color: #5A8A5A; color: #5A8A5A; }` |
| 1593 | `#4A7FA5` | LEGACY | `.status-construction { border-color: #4A7FA5; color: #4A7FA5; }` |
| 1593 | `#4A7FA5` | LEGACY | `.status-construction { border-color: #4A7FA5; color: #4A7FA5; }` |
| 1594 | `#666666` |  | `.status-planning { border-color: #666666; color: #666666; }` |
| 1594 | `#666666` |  | `.status-planning { border-color: #666666; color: #666666; }` |
| 1595 | `#4A7FA5` | LEGACY | `.status-pending { border-color: #4A7FA5; color: #4A7FA5; }` |
| 1595 | `#4A7FA5` | LEGACY | `.status-pending { border-color: #4A7FA5; color: #4A7FA5; }` |
| 1596 | `#C86060` |  | `.status-suspended, .status-rejected { border-color: #C86060; color: #C86060; }` |
| 1596 | `#C86060` |  | `.status-suspended, .status-rejected { border-color: #C86060; color: #C86060; }` |
| 2194 | `rgba(90,138,90,0.10)` |  | `background: rgba(90,138,90,0.10);` |
| 2196 | `rgba(90,138,90,0.25)` |  | `border: 1px solid rgba(90,138,90,0.25);` |
| 2290 | `rgba(74,127,165,0.12)` |  | `background: rgba(74,127,165,0.12);` |
| 2291 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 2326 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 2372 | `#4A7FA5` | LEGACY | `.bar-cal-day.src-manual-override  { background: #4A7FA5; color: #fff; }` |
| 2372 | `#fff` |  | `.bar-cal-day.src-manual-override  { background: #4A7FA5; color: #fff; }` |
| 2373 | `#5A8CB0` |  | `.bar-cal-day.src-live-booking      { background: #5A8CB0; color: #fff; }` |
| 2373 | `#fff` |  | `.bar-cal-day.src-live-booking      { background: #5A8CB0; color: #fff; }` |
| 2374 | `#9EC3DC` |  | `.bar-cal-day.src-recent            { background: #9EC3DC; color: #fff; }` |
| 2374 | `#fff` |  | `.bar-cal-day.src-recent            { background: #9EC3DC; color: #fff; }` |
| 2375 | `#4A7FA5` | LEGACY | `.bar-cal-day.src-live-expedia      { background: #4A7FA5; color: #fff; }` |
| 2375 | `#fff` |  | `.bar-cal-day.src-live-expedia      { background: #4A7FA5; color: #fff; }` |
| 2376 | `rgba(255,255,255,0.04)` |  | `.bar-cal-day.src-estimated         { background: rgba(255,255,255,0.04); color: var(--text-muted); border: 1px` |
| 2424 | `#4A7FA5` | LEGACY | `.dot-live-google, .dot-live-brand { background: #4A7FA5; }` |
| 2425 | `#5A8CB0` |  | `.dot-live-booking                  { background: #5A8CB0; }` |
| 2426 | `rgba(255,255,255,0.15)` |  | `.dot-estimated                     { background: rgba(255,255,255,0.15); border: 1px solid var(--border); }` |
| 2488 | `rgba(255,255,255,0.05)` |  | `background: rgba(255,255,255,0.05);` |
| 2521 | `rgba(255,255,255,0.03)` |  | `background: rgba(255,255,255,0.03);` |
| 2525 | `#6BAF7A` |  | `color: #6BAF7A;` |
| 2526 | `rgba(107,175,122,0.06)` |  | `background: rgba(107,175,122,0.06);` |
| 2527 | `rgba(107,175,122,0.2)` |  | `border-top: 1px solid rgba(107,175,122,0.2);` |
| 2549 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 2550 | `rgba(74,127,165,0.08)` |  | `background: rgba(74,127,165,0.08);` |
| 2551 | `rgba(74,127,165,0.25)` |  | `border-top: 2px solid rgba(74,127,165,0.25);` |
| 2564 | `rgba(255,255,255,0.03)` |  | `background: rgba(255,255,255,0.03);` |
| 2968 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 2988 | `#4A7FA5` | LEGACY | `border-left: 2px solid #4A7FA5;` |
| 3013 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 3080 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 3094 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 3119 | `#4A7FA5` | LEGACY | `.chat-input:focus { border-bottom-color: #4A7FA5; outline: none; }` |
| 3127 | `#4A7FA5` | LEGACY | `border: 1px solid #4A7FA5;` |
| 3129 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 3139 | `#4A7FA5` | LEGACY | `.chat-send-btn:hover, .chat-send:hover { background: #4A7FA5; color: #FFFFFF; }` |
| 3139 | `#FFFFFF` |  | `.chat-send-btn:hover, .chat-send:hover { background: #4A7FA5; color: #FFFFFF; }` |
| 3341 | `#4A7FA5` | LEGACY | `background: transparent; color: #4A7FA5; border: 1px solid #4A7FA5;` |
| 3341 | `#4A7FA5` | LEGACY | `background: transparent; color: #4A7FA5; border: 1px solid #4A7FA5;` |
| 3346 | `#666666` |  | `background: transparent; color: #666666; border: 1px solid #666666;` |
| 3346 | `#666666` |  | `background: transparent; color: #666666; border: 1px solid #666666;` |
| 3418 | `#4A7FA5` | LEGACY | `.ed-cat-pill:hover  { color: #4A7FA5; border-color: #4A7FA5; }` |
| 3418 | `#4A7FA5` | LEGACY | `.ed-cat-pill:hover  { color: #4A7FA5; border-color: #4A7FA5; }` |
| 3419 | `#4A7FA5` | LEGACY | `.ed-cat-pill.active { background: #4A7FA5; color: #fff; border-color: #4A7FA5; }` |
| 3419 | `#fff` |  | `.ed-cat-pill.active { background: #4A7FA5; color: #fff; border-color: #4A7FA5; }` |
| 3419 | `#4A7FA5` | LEGACY | `.ed-cat-pill.active { background: #4A7FA5; color: #fff; border-color: #4A7FA5; }` |
| 3449 | `#0A0A0A` | LEGACY | `color: #0A0A0A;` |
| 3586 | `#0A0A0A` | LEGACY | `font-family: 'Sweet Sans Pro', sans-serif; font-size: 16px; font-weight: 400; color: #0A0A0A;` |
| 3792 | `#0A0A0A` | LEGACY | `color: #0A0A0A;` |
| 3833 | `#4A7FA5` | LEGACY | `.bench-comp-counter--warn { color: #4A7FA5; }` |
| 3839 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 3943 | `rgba(90,138,90,0.10)` |  | `.bench-idx-green { background: rgba(90,138,90,0.10); border-color: rgba(90,138,90,0.25); }` |
| 3943 | `rgba(90,138,90,0.25)` |  | `.bench-idx-green { background: rgba(90,138,90,0.10); border-color: rgba(90,138,90,0.25); }` |
| 3945 | `rgba(200,96,96,0.10)` |  | `.bench-idx-red   { background: rgba(200,96,96,0.10); border-color: rgba(200,96,96,0.25); }` |
| 3945 | `rgba(200,96,96,0.25)` |  | `.bench-idx-red   { background: rgba(200,96,96,0.10); border-color: rgba(200,96,96,0.25); }` |
| 3995 | `#4A7FA5` | LEGACY | `border-left: 2px solid #4A7FA5;` |
| 4093 | `#4A7FA5` | LEGACY | `.list-search-input:focus { border-color: #4A7FA5; }` |
| 4115 | `#4A7FA5` | LEGACY | `.list-pill:hover { color: #4A7FA5; border-color: #4A7FA5; }` |
| 4115 | `#4A7FA5` | LEGACY | `.list-pill:hover { color: #4A7FA5; border-color: #4A7FA5; }` |
| 4116 | `#4A7FA5` | LEGACY | `.list-pill.active { background: #4A7FA5; color: #fff; border-color: #4A7FA5; }` |
| 4116 | `#fff` |  | `.list-pill.active { background: #4A7FA5; color: #fff; border-color: #4A7FA5; }` |
| 4116 | `#4A7FA5` | LEGACY | `.list-pill.active { background: #4A7FA5; color: #fff; border-color: #4A7FA5; }` |
| 4127 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 4152 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 4153 | `#4A7FA5` | LEGACY | `border: 1px solid #4A7FA5;` |
| 4162 | `#4A7FA5` | LEGACY | `.report-action:hover { background: #4A7FA5; color: #fff; }` |
| 4162 | `#fff` |  | `.report-action:hover { background: #4A7FA5; color: #fff; }` |
| 4213 | `#C05252` | LEGACY | `.insight-value.is-neg { color: #C05252; }` |
| 4214 | `#4A9B6F` | LEGACY | `.insight-value.is-pos { color: #4A9B6F; }` |
| 4252 | `rgba(74,127,165,0.08)` |  | `background: rgba(74,127,165,0.08);` |
| 4253 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 4254 | `#4A7FA5` | LEGACY | `border-color: #4A7FA5;` |
| 4326 | `rgba(0,0,0,0.6)` |  | `background: rgba(0,0,0,0.6);` |
| 4421 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 4650 | `rgba(0,0,0,0.7)` |  | `background: rgba(0,0,0,0.7);` |
| 4826 | `#fff` |  | `body { background: #fff !important; color: #000 !important; font-family: 'Sweet Sans Pro', sans-serif; }` |
| 4826 | `#000` |  | `body { background: #fff !important; color: #000 !important; font-family: 'Sweet Sans Pro', sans-serif; }` |
| 4830 | `#000` |  | `.screen-header h1 { font-size: 22px; color: #000; margin-bottom: 4px; }` |
| 4831 | `#555` |  | `.screen-header p { font-size: 11px; color: #555; margin-bottom: 20px; }` |
| 4834 | `#fff` |  | `background: #fff !important; border: 1px solid #ccc !important;` |
| 4834 | `#ccc` |  | `background: #fff !important; border: 1px solid #ccc !important;` |
| 4838 | `#333` |  | `.news-body { display: block !important; color: #333 !important; }` |
| 4839 | `#000` |  | `.news-headline { color: #000 !important; font-size: 16px; }` |
| 4840 | `#333` |  | `.news-summary { color: #333 !important; }` |
| 4841 | `#999` |  | `.news-cat { border: 1px solid #999 !important; color: #333 !important; background: #f5f5f5 !important; }` |
| 4841 | `#333` |  | `.news-cat { border: 1px solid #999 !important; color: #333 !important; background: #f5f5f5 !important; }` |
| 4841 | `#f5f5f5` |  | `.news-cat { border: 1px solid #999 !important; color: #333 !important; background: #f5f5f5 !important; }` |
| 4955 | `#fff` |  | `color: #fff;` |
| 5476 | `#4A7FA5` | LEGACY | `.val-metric-mid   { color: #4A7FA5; }` |
| 5592 | `#777777` |  | `color: #777777;` |
| 5597 | `#555555` |  | `color: #555555;` |
| 5702 | `rgba(74,127,165,0.06)` |  | `background: rgba(74,127,165,0.06);` |
| 5703 | `rgba(74,127,165,0.2)` |  | `border: 1px solid rgba(74,127,165,0.2);` |
| 5709 | `rgba(74,127,165,0.12)` |  | `background: rgba(74,127,165,0.12);` |
| 5734 | `#4A7FA5` | LEGACY | `.val-approach-card--reconciled { border-top: 2px solid #4A7FA5; }` |
| 5762 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 5768 | `#888888` |  | `color: #888888;` |
| 5816 | `rgba(90,138,90,0.20)` |  | `.val-sens-high      { background: rgba(90,138,90,0.20);  color: #5A8A5A; }` |
| 5816 | `#5A8A5A` |  | `.val-sens-high      { background: rgba(90,138,90,0.20);  color: #5A8A5A; }` |
| 5817 | `rgba(74,127,165,0.15)` |  | `.val-sens-mid-high  { background: rgba(74,127,165,0.15); color: #4A7FA5; }` |
| 5817 | `#4A7FA5` | LEGACY | `.val-sens-mid-high  { background: rgba(74,127,165,0.15); color: #4A7FA5; }` |
| 5818 | `rgba(74,127,165,0.15)` |  | `.val-sens-mid       { background: rgba(74,127,165,0.15); color: #4A7FA5; }` |
| 5818 | `#4A7FA5` | LEGACY | `.val-sens-mid       { background: rgba(74,127,165,0.15); color: #4A7FA5; }` |
| 5819 | `rgba(200,96,96,0.15)` |  | `.val-sens-low       { background: rgba(200,96,96,0.15);  color: #C86060; }` |
| 5819 | `#C86060` |  | `.val-sens-low       { background: rgba(200,96,96,0.15);  color: #C86060; }` |
| 5843 | `rgba(10,10,10,0.72)` |  | `background: rgba(10,10,10,0.72);` |
| 5884 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 5885 | `#fff` |  | `color: #fff;` |

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
| 61 | `#1A1A1A` |  | `'Zalagh Hotels Group':         { letter: 'Z',  bg: '#1A1A1A', color: '#4A7FA5' },` |
| 61 | `#4A7FA5` | LEGACY | `'Zalagh Hotels Group':         { letter: 'Z',  bg: '#1A1A1A', color: '#4A7FA5' },` |
| 62 | `#1A1A1A` |  | `'Farah Hotels':                { letter: 'F',  bg: '#1A1A1A', color: '#4A7FA5' },` |
| 62 | `#4A7FA5` | LEGACY | `'Farah Hotels':                { letter: 'F',  bg: '#1A1A1A', color: '#4A7FA5' },` |
| 63 | `#1A1A1A` |  | `'Independent Ultra Luxury':    { letter: 'UL', bg: '#1A1A1A', color: '#4A7FA5' },` |
| 63 | `#4A7FA5` | LEGACY | `'Independent Ultra Luxury':    { letter: 'UL', bg: '#1A1A1A', color: '#4A7FA5' },` |
| 64 | `#1A1A1A` |  | `'Independent Luxury':          { letter: 'IL', bg: '#1A1A1A', color: '#4A7FA5' },` |
| 64 | `#4A7FA5` | LEGACY | `'Independent Luxury':          { letter: 'IL', bg: '#1A1A1A', color: '#4A7FA5' },` |
| 65 | `#1A1A1A` |  | `'Independent Upper Upscale':   { letter: 'UU', bg: '#1A1A1A', color: '#888888' },` |
| 65 | `#888888` |  | `'Independent Upper Upscale':   { letter: 'UU', bg: '#1A1A1A', color: '#888888' },` |
| 66 | `#1A1A1A` |  | `'Independent Upscale':         { letter: 'IU', bg: '#1A1A1A', color: '#666666' },` |
| 66 | `#666666` |  | `'Independent Upscale':         { letter: 'IU', bg: '#1A1A1A', color: '#666666' },` |
| 67 | `#1A1A1A` |  | `'Independent Midscale':        { letter: 'IM', bg: '#1A1A1A', color: '#555555' },` |
| 67 | `#555555` |  | `'Independent Midscale':        { letter: 'IM', bg: '#1A1A1A', color: '#555555' },` |
| 68 | `#1A1A1A` |  | `'Independent Economy':         { letter: 'IE', bg: '#1A1A1A', color: '#444444' },` |
| 68 | `#444444` |  | `'Independent Economy':         { letter: 'IE', bg: '#1A1A1A', color: '#444444' },` |
| 70 | `#1A1A1A` |  | `'Zephyr':                      { letter: 'Z',  bg: '#1A1A1A', color: '#4A7FA5' },` |
| 70 | `#4A7FA5` | LEGACY | `'Zephyr':                      { letter: 'Z',  bg: '#1A1A1A', color: '#4A7FA5' },` |
| 98 | `#1A1A1A` |  | `return '<span style="display:inline-flex;align-items:center;justify-content:center;width:' + size + 'px;height` |
| 98 | `#4A7FA5` | LEGACY | `return '<span style="display:inline-flex;align-items:center;justify-content:center;width:' + size + 'px;height` |
| 106 | `#6B7A8D` | LEGACY | `slate:  '#6B7A8D',` |
| 107 | `#4A7FA5` | LEGACY | `blue:   '#4A7FA5',` |
| 108 | `#4A9B6F` | LEGACY | `green:  '#4A9B6F',` |
| 109 | `#F2A33D` | LEGACY | `orange: '#F2A33D',` |
| 110 | `#8A6FB0` |  | `violet: '#8A6FB0',` |
| 186 | `#4A7FA5` | LEGACY | `'Ultra Luxury': '#4A7FA5',` |
| 187 | `#6B8CAA` |  | `'Luxury':       '#6B8CAA',` |
| 188 | `#7A9CB8` |  | `'Upper Upscale':'#7A9CB8',` |
| 189 | `#8CACC5` |  | `'Upscale':      '#8CACC5',` |
| 190 | `#9EBDD0` |  | `'Midscale':     '#9EBDD0',` |
| 191 | `#B0CDDD` |  | `'Economy':      '#B0CDDD',` |
| 204 | `#AAAAAA` |  | `'Ultra Luxury': '#AAAAAA',` |
| 205 | `#999999` |  | `'Luxury': '#999999',` |
| 206 | `#888888` |  | `'Upper Upscale': '#888888',` |
| 207 | `#777777` |  | `'Upscale': '#777777',` |
| 208 | `#666666` |  | `'Midscale': '#666666',` |
| 209 | `#555555` |  | `'Economy': '#555555',` |
| 212 | `#555555` |  | `'Ultra Luxury': '#555555',` |
| 213 | `#666666` |  | `'Luxury': '#666666',` |
| 214 | `#777777` |  | `'Upper Upscale': '#777777',` |
| 215 | `#888888` |  | `'Upscale': '#888888',` |
| 216 | `#999999` |  | `'Midscale': '#999999',` |
| 217 | `#AAAAAA` |  | `'Economy': '#AAAAAA',` |
| 220 | `rgba(240,240,238,0.08)` |  | `'Ultra Luxury': 'rgba(240,240,238,0.08)',` |
| 221 | `rgba(240,240,238,0.07)` |  | `'Luxury': 'rgba(240,240,238,0.07)',` |
| 222 | `rgba(240,240,238,0.06)` |  | `'Upper Upscale': 'rgba(240,240,238,0.06)',` |
| 223 | `rgba(240,240,238,0.05)` |  | `'Upscale': 'rgba(240,240,238,0.05)',` |
| 224 | `rgba(240,240,238,0.04)` |  | `'Midscale': 'rgba(240,240,238,0.04)',` |
| 225 | `rgba(240,240,238,0.03)` |  | `'Economy': 'rgba(240,240,238,0.03)',` |
| 228 | `rgba(10,10,10,0.06)` |  | `'Ultra Luxury': 'rgba(10,10,10,0.06)',` |
| 229 | `rgba(10,10,10,0.05)` |  | `'Luxury': 'rgba(10,10,10,0.05)',` |
| 230 | `rgba(10,10,10,0.045)` |  | `'Upper Upscale': 'rgba(10,10,10,0.045)',` |
| 231 | `rgba(10,10,10,0.04)` |  | `'Upscale': 'rgba(10,10,10,0.04)',` |
| 232 | `rgba(10,10,10,0.035)` |  | `'Midscale': 'rgba(10,10,10,0.035)',` |
| 233 | `rgba(10,10,10,0.03)` |  | `'Economy': 'rgba(10,10,10,0.03)',` |
| 237 | `#777777` |  | `const color = segmentColors[segment] ¦¦ (dark ? '#777777' : '#888888');` |
| 237 | `#888888` |  | `const color = segmentColors[segment] ¦¦ (dark ? '#777777' : '#888888');` |
| 238 | `rgba(240,240,238,0.05)` |  | `const bg = segmentBg[segment] ¦¦ (dark ? 'rgba(240,240,238,0.05)' : 'rgba(10,10,10,0.04)');` |
| 238 | `rgba(10,10,10,0.04)` |  | `const bg = segmentBg[segment] ¦¦ (dark ? 'rgba(240,240,238,0.05)' : 'rgba(10,10,10,0.04)');` |
| 256 | `#141414` | LEGACY | `{"elementType":"geometry","stylers":[{"color":"#141414"}]},` |
| 257 | `#888888` |  | `{"elementType":"labels.text.fill","stylers":[{"color":"#888888"}]},` |
| 258 | `#0A0A0A` | LEGACY | `{"elementType":"labels.text.stroke","stylers":[{"color":"#0A0A0A"}]},` |
| 259 | `#242424` | LEGACY | `{"featureType":"administrative","elementType":"geometry","stylers":[{"color":"#242424"}]},` |
| 260 | `#444444` |  | `{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"color":"#444444"}]},` |
| 261 | `#4A7FA5` | LEGACY | `{"featureType":"administrative.country","elementType":"labels.text.fill","stylers":[{"color":"#4A7FA5"}]},` |
| 262 | `#242424` | LEGACY | `{"featureType":"administrative.province","elementType":"geometry.stroke","stylers":[{"color":"#242424"}]},` |
| 263 | `#888888` |  | `{"featureType":"administrative.locality","elementType":"labels.text.fill","stylers":[{"color":"#888888"}]},` |
| 264 | `#242424` | LEGACY | `{"featureType":"road","elementType":"geometry","stylers":[{"color":"#242424"}]},` |
| 265 | `#141414` | LEGACY | `{"featureType":"road","elementType":"geometry.stroke","stylers":[{"color":"#141414"}]},` |
| 266 | `#2E2E2E` |  | `{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#2E2E2E"}]},` |
| 267 | `#0A0A0A` | LEGACY | `{"featureType":"water","elementType":"geometry","stylers":[{"color":"#0A0A0A"}]},` |
| 272 | `#F5F5F5` |  | `{"elementType":"geometry","stylers":[{"color":"#F5F5F5"}]},` |
| 273 | `#616161` |  | `{"elementType":"labels.text.fill","stylers":[{"color":"#616161"}]},` |
| 274 | `#F5F5F5` |  | `{"elementType":"labels.text.stroke","stylers":[{"color":"#F5F5F5"}]},` |
| 275 | `#CCCCCC` |  | `{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"color":"#CCCCCC"}]},` |
| 276 | `#FFFFFF` |  | `{"featureType":"road","elementType":"geometry","stylers":[{"color":"#FFFFFF"}]},` |
| 277 | `#E0E0E0` |  | `{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#E0E0E0"}]},` |
| 278 | `#C9D8E8` |  | `{"featureType":"water","elementType":"geometry","stylers":[{"color":"#C9D8E8"}]},` |
| 339 | `#4A7FA5` | LEGACY | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 339 | `#6B8CAA` |  | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 339 | `#5A9AA8` |  | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 339 | `#7A6A8A` |  | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 339 | `#4A6E8A` |  | `'#4A7FA5','#6B8CAA','#5A9AA8','#7A6A8A','#4A6E8A',` |
| 340 | `#6A7A9A` |  | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 340 | `#6A8A6A` |  | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 340 | `#8A5A7A` |  | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 340 | `#9A8A5A` |  | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 340 | `#3A6A8E` | LEGACY | `'#6A7A9A','#6A8A6A','#8A5A7A','#9A8A5A','#3A6A8E',` |
| 508 | `#555555` |  | `barColor:   dark ? '#555555' : '#AAAAAA',` |
| 508 | `#AAAAAA` |  | `barColor:   dark ? '#555555' : '#AAAAAA',` |
| 509 | `#777777` |  | `barColor2:  dark ? '#777777' : '#888888',` |
| 509 | `#888888` |  | `barColor2:  dark ? '#777777' : '#888888',` |
| 510 | `#444444` |  | `barColor3:  dark ? '#444444' : '#BBBBBB',` |
| 510 | `#BBBBBB` |  | `barColor3:  dark ? '#444444' : '#BBBBBB',` |
| 511 | `#666666` |  | `barColor4:  dark ? '#666666' : '#999999',` |
| 511 | `#999999` |  | `barColor4:  dark ? '#666666' : '#999999',` |
| 512 | `#4A7FA5` | LEGACY | `hoverColor: '#4A7FA5',` |
| 513 | `rgba(85,85,85,0.10)` |  | `fillColor:  dark ? 'rgba(85,85,85,0.10)' : 'rgba(170,170,170,0.14)',` |
| 513 | `rgba(170,170,170,0.14)` |  | `fillColor:  dark ? 'rgba(85,85,85,0.10)' : 'rgba(170,170,170,0.14)',` |
| 515 | `#888888` |  | `tick:       dark ? '#888888' : '#888888',` |
| 515 | `#888888` |  | `tick:       dark ? '#888888' : '#888888',` |
| 516 | `#888888` |  | `label:      dark ? '#888888' : '#888888',` |
| 516 | `#888888` |  | `label:      dark ? '#888888' : '#888888',` |
| 517 | `#AAAAAA` |  | `catLabel:   dark ? '#AAAAAA' : '#555555',` |
| 517 | `#555555` |  | `catLabel:   dark ? '#AAAAAA' : '#555555',` |
| 518 | `#141414` | LEGACY | `tooltipBg:  dark ? '#141414' : '#FFFFFF',` |
| 518 | `#FFFFFF` |  | `tooltipBg:  dark ? '#141414' : '#FFFFFF',` |
| 519 | `#242424` | LEGACY | `tooltipBdr: dark ? '#242424' : '#E4E4E4',` |
| 519 | `#E4E4E4` |  | `tooltipBdr: dark ? '#242424' : '#E4E4E4',` |
| 520 | `#F0F0EE` | LEGACY | `tooltipTtl: dark ? '#F0F0EE' : '#1A1A1A',` |
| 520 | `#1A1A1A` |  | `tooltipTtl: dark ? '#F0F0EE' : '#1A1A1A',` |
| 521 | `#888888` |  | `tooltipBdy: dark ? '#888888' : '#888888',` |
| 521 | `#888888` |  | `tooltipBdy: dark ? '#888888' : '#888888',` |
| 594 | `rgba(240,240,238,0.5)` |  | `const color = dark ? 'rgba(240,240,238,0.5)' : 'rgba(0,0,0,0.45)';` |
| 594 | `rgba(0,0,0,0.45)` |  | `const color = dark ? 'rgba(240,240,238,0.5)' : 'rgba(0,0,0,0.45)';` |
| 784 | `#888888` |  | `color: BRAND_PALETTE[i] ¦¦ '#888888',` |
| 786 | `#444444` |  | `if (otherKeys > 0) segs.push({ name: 'Other', pct: otherKeys / total * 100, color: '#444444' });` |
| 1418 | `#888888` |  | `const dayNumCol = dark ? '#888888' : '#AAAAAA';` |
| 1418 | `#AAAAAA` |  | `const dayNumCol = dark ? '#888888' : '#AAAAAA';` |
| 1432 | `#6AAF8A` |  | `if (occ >= 80) { bg = '#6AAF8A'; col = '#0A0A0A'; fw = '600'; }` |
| 1432 | `#0A0A0A` | LEGACY | `if (occ >= 80) { bg = '#6AAF8A'; col = '#0A0A0A'; fw = '600'; }` |
| 1433 | `#3D7A5C` |  | `else if (occ >= 60) { bg = '#3D7A5C'; col = '#F0EDE6'; fw = '500'; }` |
| 1433 | `#F0EDE6` |  | `else if (occ >= 60) { bg = '#3D7A5C'; col = '#F0EDE6'; fw = '500'; }` |
| 1434 | `#2A5A3A` |  | `else if (occ >= 40) { bg = '#2A5A3A'; col = '#B0D8C0'; fw = ''; }` |
| 1434 | `#B0D8C0` |  | `else if (occ >= 40) { bg = '#2A5A3A'; col = '#B0D8C0'; fw = ''; }` |
| 1435 | `#1A2A1A` |  | `else { bg = '#1A2A1A'; col = '#6A9A7A'; border = '1px solid #2A5A3A'; }` |
| 1435 | `#6A9A7A` |  | `else { bg = '#1A2A1A'; col = '#6A9A7A'; border = '1px solid #2A5A3A'; }` |
| 1435 | `#2A5A3A` |  | `else { bg = '#1A2A1A'; col = '#6A9A7A'; border = '1px solid #2A5A3A'; }` |
| 1437 | `#B0E0C8` |  | `if (occ >= 80) { bg = '#B0E0C8'; col = '#0A4A2A'; fw = '600'; border = '1px solid #6AAF8A'; }` |
| 1437 | `#0A4A2A` |  | `if (occ >= 80) { bg = '#B0E0C8'; col = '#0A4A2A'; fw = '600'; border = '1px solid #6AAF8A'; }` |
| 1437 | `#6AAF8A` |  | `if (occ >= 80) { bg = '#B0E0C8'; col = '#0A4A2A'; fw = '600'; border = '1px solid #6AAF8A'; }` |
| 1438 | `#D0EDE0` |  | `else if (occ >= 60) { bg = '#D0EDE0'; col = '#1A5A3A'; fw = '500'; border = '1px solid #3D7A5C'; }` |
| 1438 | `#1A5A3A` |  | `else if (occ >= 60) { bg = '#D0EDE0'; col = '#1A5A3A'; fw = '500'; border = '1px solid #3D7A5C'; }` |
| 1438 | `#3D7A5C` |  | `else if (occ >= 60) { bg = '#D0EDE0'; col = '#1A5A3A'; fw = '500'; border = '1px solid #3D7A5C'; }` |
| 1439 | `#E5F5ED` |  | `else if (occ >= 40) { bg = '#E5F5ED'; col = '#2A6A4A'; border = '1px solid #9ED0B8'; }` |
| 1439 | `#2A6A4A` |  | `else if (occ >= 40) { bg = '#E5F5ED'; col = '#2A6A4A'; border = '1px solid #9ED0B8'; }` |
| 1439 | `#9ED0B8` |  | `else if (occ >= 40) { bg = '#E5F5ED'; col = '#2A6A4A'; border = '1px solid #9ED0B8'; }` |
| 1440 | `#FFFFFF` |  | `else { bg = '#FFFFFF'; col = '#8A8A8A'; border = '1px solid #ECECEC'; }` |
| 1440 | `#8A8A8A` |  | `else { bg = '#FFFFFF'; col = '#8A8A8A'; border = '1px solid #ECECEC'; }` |
| 1440 | `#ECECEC` |  | `else { bg = '#FFFFFF'; col = '#8A8A8A'; border = '1px solid #ECECEC'; }` |
| 1443 | `#181818` |  | `bg = dark ? '#181818' : '#F8F8F8';` |
| 1443 | `#F8F8F8` |  | `bg = dark ? '#181818' : '#F8F8F8';` |
| 1444 | `#444` |  | `col = dark ? '#444' : '#BBB';` |
| 1444 | `#BBB` |  | `col = dark ? '#444' : '#BBB';` |
| 1445 | `#333` |  | `border = dark ? '1px dashed #333' : '1px dashed #DDD';` |
| 1445 | `#DDD` |  | `border = dark ? '1px dashed #333' : '1px dashed #DDD';` |
| 1621 | `#4A7FA5` | LEGACY | `fillColor:   highlighted ? '#4A7FA5' : '#666666',` |
| 1621 | `#666666` |  | `fillColor:   highlighted ? '#4A7FA5' : '#666666',` |
| 1623 | `rgba(255,255,255,0.15)` |  | `strokeColor: 'rgba(255,255,255,0.15)',` |
| 2258 | `#5B8DB8` |  | `const FORECAST_BAR_COLOR = '#5B8DB8';` |
| 2393 | `#F9F6F0` |  | `pointBorderColor: '#F9F6F0', pointBorderWidth: 2,` |
| 2496 | `#4A7FA5` | LEGACY | `const color  = p.status === 'Under Construction' ? '#4A7FA5' : '#888888';` |
| 2496 | `#888888` |  | `const color  = p.status === 'Under Construction' ? '#4A7FA5' : '#888888';` |
| 2525 | `#4A7FA5` | LEGACY | `? <span style="color:#4A7FA5;font-family:'Sweet Sans Pro',sans-serif;font-size:10px;font-weight:500;white-spa` |
| 2526 | `#888888` |  | `: <span style="color:#888888;font-family:'Sweet Sans Pro',sans-serif;font-size:10px;font-weight:500;white-spa` |
| 3527 | `rgba(45,107,58,0.15)` |  | `if (modeEl) { modeEl.textContent = 'Live data available'; modeEl.style.background = 'rgba(45,107,58,0.15)'; mo` |
| 3810 | `#2A4A6B` |  | `if (adr >= 6000) return {bg:'#2A4A6B', col:'#FFFFFF',  fw:'600', border:''};` |
| 3810 | `#FFFFFF` |  | `if (adr >= 6000) return {bg:'#2A4A6B', col:'#FFFFFF',  fw:'600', border:''};` |
| 3811 | `#1A2E42` |  | `if (adr >= 4000) return {bg:'#1A2E42', col:'#8AB0D0',  fw:'500', border:''};` |
| 3811 | `#8AB0D0` |  | `if (adr >= 4000) return {bg:'#1A2E42', col:'#8AB0D0',  fw:'500', border:''};` |
| 3812 | `#0A1520` |  | `return {bg:'#0A1520', col:'#6A8AAA', fw:'', border:'1px solid #2A4A6B'};` |
| 3812 | `#6A8AAA` |  | `return {bg:'#0A1520', col:'#6A8AAA', fw:'', border:'1px solid #2A4A6B'};` |
| 3812 | `#2A4A6B` |  | `return {bg:'#0A1520', col:'#6A8AAA', fw:'', border:'1px solid #2A4A6B'};` |
| 3814 | `#D0E4F5` |  | `if (adr >= 6000) return {bg:'#D0E4F5', col:'#1A4A7A', fw:'600', border:'1px solid #5A90C8'};` |
| 3814 | `#1A4A7A` |  | `if (adr >= 6000) return {bg:'#D0E4F5', col:'#1A4A7A', fw:'600', border:'1px solid #5A90C8'};` |
| 3814 | `#5A90C8` |  | `if (adr >= 6000) return {bg:'#D0E4F5', col:'#1A4A7A', fw:'600', border:'1px solid #5A90C8'};` |
| 3815 | `#E8F2FC` |  | `if (adr >= 4000) return {bg:'#E8F2FC', col:'#2A6AAA', fw:'',    border:'1px solid #8AB8E0'};` |
| 3815 | `#2A6AAA` |  | `if (adr >= 4000) return {bg:'#E8F2FC', col:'#2A6AAA', fw:'',    border:'1px solid #8AB8E0'};` |
| 3815 | `#8AB8E0` |  | `if (adr >= 4000) return {bg:'#E8F2FC', col:'#2A6AAA', fw:'',    border:'1px solid #8AB8E0'};` |
| 3816 | `#F5F9FF` |  | `return {bg:'#F5F9FF', col:'#5A8AB0', fw:'', border:'1px solid #C0D8F0'};` |
| 3816 | `#5A8AB0` |  | `return {bg:'#F5F9FF', col:'#5A8AB0', fw:'', border:'1px solid #C0D8F0'};` |
| 3816 | `#C0D8F0` |  | `return {bg:'#F5F9FF', col:'#5A8AB0', fw:'', border:'1px solid #C0D8F0'};` |
| 3820 | `#7AB0D0` |  | `if (adr >= 6000) return {bg:'#7AB0D0', col:'#0A0A0A', fw:'600', border:''};` |
| 3820 | `#0A0A0A` | LEGACY | `if (adr >= 6000) return {bg:'#7AB0D0', col:'#0A0A0A', fw:'600', border:''};` |
| 3821 | `#4A7FA5` | LEGACY | `if (adr >= 4000) return {bg:'#4A7FA5', col:'#0A0A0A', fw:'500', border:''};` |
| 3821 | `#0A0A0A` | LEGACY | `if (adr >= 4000) return {bg:'#4A7FA5', col:'#0A0A0A', fw:'500', border:''};` |
| 3822 | `#2A5A8A` |  | `if (adr >= 2000) return {bg:'#2A5A8A', col:'#F0EDE6', fw:'', border:''};` |
| 3822 | `#F0EDE6` |  | `if (adr >= 2000) return {bg:'#2A5A8A', col:'#F0EDE6', fw:'', border:''};` |
| 3823 | `#1A2A3A` |  | `return {bg:'#1A2A3A', col:'#7A9AB5', fw:'', border:'1px solid #2A5A8A'};` |
| 3823 | `#7A9AB5` |  | `return {bg:'#1A2A3A', col:'#7A9AB5', fw:'', border:'1px solid #2A5A8A'};` |
| 3823 | `#2A5A8A` |  | `return {bg:'#1A2A3A', col:'#7A9AB5', fw:'', border:'1px solid #2A5A8A'};` |
| 3825 | `#B8D8EC` |  | `if (adr >= 6000) return {bg:'#B8D8EC', col:'#0A3050', fw:'600', border:'1px solid #7AB0D0'};` |
| 3825 | `#0A3050` |  | `if (adr >= 6000) return {bg:'#B8D8EC', col:'#0A3050', fw:'600', border:'1px solid #7AB0D0'};` |
| 3825 | `#7AB0D0` |  | `if (adr >= 6000) return {bg:'#B8D8EC', col:'#0A3050', fw:'600', border:'1px solid #7AB0D0'};` |
| 3826 | `#D8E8F2` |  | `if (adr >= 4000) return {bg:'#D8E8F2', col:'#1A4A6B', fw:'500', border:'1px solid #4A7FA5'};` |
| 3826 | `#1A4A6B` |  | `if (adr >= 4000) return {bg:'#D8E8F2', col:'#1A4A6B', fw:'500', border:'1px solid #4A7FA5'};` |
| 3826 | `#4A7FA5` | LEGACY | `if (adr >= 4000) return {bg:'#D8E8F2', col:'#1A4A6B', fw:'500', border:'1px solid #4A7FA5'};` |
| 3827 | `#EAF2F8` |  | `if (adr >= 2000) return {bg:'#EAF2F8', col:'#2A5A8A', fw:'',   border:'1px solid #9EC3DC'};` |
| 3827 | `#2A5A8A` |  | `if (adr >= 2000) return {bg:'#EAF2F8', col:'#2A5A8A', fw:'',   border:'1px solid #9EC3DC'};` |
| 3827 | `#9EC3DC` |  | `if (adr >= 2000) return {bg:'#EAF2F8', col:'#2A5A8A', fw:'',   border:'1px solid #9EC3DC'};` |
| 3828 | `#FFFFFF` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3828 | `#8A8A8A` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3828 | `#ECECEC` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3837 | `#1A4A3A` |  | `if (p >= 80) return {bg:'#1A4A3A', col:'#FFFFFF',  fw:'600', border:''};` |
| 3837 | `#FFFFFF` |  | `if (p >= 80) return {bg:'#1A4A3A', col:'#FFFFFF',  fw:'600', border:''};` |
| 3838 | `#0F2E24` |  | `if (p >= 60) return {bg:'#0F2E24', col:'#5A9A82',  fw:'500', border:''};` |
| 3838 | `#5A9A82` |  | `if (p >= 60) return {bg:'#0F2E24', col:'#5A9A82',  fw:'500', border:''};` |
| 3839 | `#051510` |  | `return {bg:'#051510', col:'#3A7A62', fw:'', border:'1px solid #1A4A3A'};` |
| 3839 | `#3A7A62` |  | `return {bg:'#051510', col:'#3A7A62', fw:'', border:'1px solid #1A4A3A'};` |
| 3839 | `#1A4A3A` |  | `return {bg:'#051510', col:'#3A7A62', fw:'', border:'1px solid #1A4A3A'};` |
| 3841 | `#D0EDE5` |  | `if (p >= 80) return {bg:'#D0EDE5', col:'#0A4A32', fw:'600', border:'1px solid #3A9A7A'};` |
| 3841 | `#0A4A32` |  | `if (p >= 80) return {bg:'#D0EDE5', col:'#0A4A32', fw:'600', border:'1px solid #3A9A7A'};` |
| 3841 | `#3A9A7A` |  | `if (p >= 80) return {bg:'#D0EDE5', col:'#0A4A32', fw:'600', border:'1px solid #3A9A7A'};` |
| 3842 | `#E5F5EF` |  | `if (p >= 60) return {bg:'#E5F5EF', col:'#1A6A4A', fw:'',    border:'1px solid #7ABDA8'};` |
| 3842 | `#1A6A4A` |  | `if (p >= 60) return {bg:'#E5F5EF', col:'#1A6A4A', fw:'',    border:'1px solid #7ABDA8'};` |
| 3842 | `#7ABDA8` |  | `if (p >= 60) return {bg:'#E5F5EF', col:'#1A6A4A', fw:'',    border:'1px solid #7ABDA8'};` |
| 3843 | `#F0FAF6` |  | `return {bg:'#F0FAF6', col:'#3A8A68', fw:'', border:'1px solid #B0D8C8'};` |
| 3843 | `#3A8A68` |  | `return {bg:'#F0FAF6', col:'#3A8A68', fw:'', border:'1px solid #B0D8C8'};` |
| 3843 | `#B0D8C8` |  | `return {bg:'#F0FAF6', col:'#3A8A68', fw:'', border:'1px solid #B0D8C8'};` |
| 3847 | `#6AAF8A` |  | `if (p >= 80) return {bg:'#6AAF8A', col:'#0A0A0A', fw:'600', border:''};` |
| 3847 | `#0A0A0A` | LEGACY | `if (p >= 80) return {bg:'#6AAF8A', col:'#0A0A0A', fw:'600', border:''};` |
| 3848 | `#3D7A5C` |  | `if (p >= 60) return {bg:'#3D7A5C', col:'#F0EDE6', fw:'500', border:''};` |
| 3848 | `#F0EDE6` |  | `if (p >= 60) return {bg:'#3D7A5C', col:'#F0EDE6', fw:'500', border:''};` |
| 3849 | `#2A5A3A` |  | `if (p >= 40) return {bg:'#2A5A3A', col:'#B0D8C0', fw:'', border:''};` |
| 3849 | `#B0D8C0` |  | `if (p >= 40) return {bg:'#2A5A3A', col:'#B0D8C0', fw:'', border:''};` |
| 3850 | `#1A2A1A` |  | `return {bg:'#1A2A1A', col:'#6A9A7A', fw:'', border:'1px solid #2A5A3A'};` |
| 3850 | `#6A9A7A` |  | `return {bg:'#1A2A1A', col:'#6A9A7A', fw:'', border:'1px solid #2A5A3A'};` |
| 3850 | `#2A5A3A` |  | `return {bg:'#1A2A1A', col:'#6A9A7A', fw:'', border:'1px solid #2A5A3A'};` |
| 3852 | `#B0E0C8` |  | `if (p >= 80) return {bg:'#B0E0C8', col:'#0A4A2A', fw:'600', border:'1px solid #6AAF8A'};` |
| 3852 | `#0A4A2A` |  | `if (p >= 80) return {bg:'#B0E0C8', col:'#0A4A2A', fw:'600', border:'1px solid #6AAF8A'};` |
| 3852 | `#6AAF8A` |  | `if (p >= 80) return {bg:'#B0E0C8', col:'#0A4A2A', fw:'600', border:'1px solid #6AAF8A'};` |
| 3853 | `#D0EDE0` |  | `if (p >= 60) return {bg:'#D0EDE0', col:'#1A5A3A', fw:'500', border:'1px solid #3D7A5C'};` |
| 3853 | `#1A5A3A` |  | `if (p >= 60) return {bg:'#D0EDE0', col:'#1A5A3A', fw:'500', border:'1px solid #3D7A5C'};` |
| 3853 | `#3D7A5C` |  | `if (p >= 60) return {bg:'#D0EDE0', col:'#1A5A3A', fw:'500', border:'1px solid #3D7A5C'};` |
| 3854 | `#E5F5ED` |  | `if (p >= 40) return {bg:'#E5F5ED', col:'#2A6A4A', fw:'',   border:'1px solid #9ED0B8'};` |
| 3854 | `#2A6A4A` |  | `if (p >= 40) return {bg:'#E5F5ED', col:'#2A6A4A', fw:'',   border:'1px solid #9ED0B8'};` |
| 3854 | `#9ED0B8` |  | `if (p >= 40) return {bg:'#E5F5ED', col:'#2A6A4A', fw:'',   border:'1px solid #9ED0B8'};` |
| 3855 | `#FFFFFF` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3855 | `#8A8A8A` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3855 | `#ECECEC` |  | `return {bg:'#FFFFFF', col:'#8A8A8A', fw:'', border:'1px solid #ECECEC'};` |
| 3908 | `#888888` |  | `const dayNumCol = dark ? '#888888' : '#AAAAAA';` |
| 3908 | `#AAAAAA` |  | `const dayNumCol = dark ? '#888888' : '#AAAAAA';` |
| 4013 | `rgba(74,127,165,0.08)` |  | `backgroundColor: 'rgba(74,127,165,0.08)', borderWidth: 2, fill: false,` |
| 4085 | `rgba(119,119,119,0.35)` |  | `dowDatasets.push({ label: 'Comp Set Avg', data: compDOW.map(avg), backgroundColor: 'rgba(119,119,119,0.35)', b` |

## `templates/accept_invite.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 28 | `#0A0A0A` | LEGACY | `background: #0A0A0A;` |
| 29 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 44 | `#F0F0EE` | LEGACY | `text-decoration: none; color: #F0F0EE;` |
| 53 | `#4A7FA5` | LEGACY | `background: #4A7FA5; color: #FFFFFF;` |
| 53 | `#FFFFFF` |  | `background: #4A7FA5; color: #FFFFFF;` |
| 61 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 70 | `#141414` | LEGACY | `background: #141414;` |
| 71 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 79 | `#4A7FA5` | LEGACY | `color: #4A7FA5; margin-bottom: 10px;` |
| 84 | `#F0F0EE` | LEGACY | `letter-spacing: 0.01em; color: #F0F0EE; margin-bottom: 6px;` |
| 87 | `#888888` |  | `font-size: 0.875rem; color: #888888;` |
| 92 | `#1C1C1C` |  | `background: #1C1C1C; border: 1px solid #242424;` |
| 92 | `#242424` | LEGACY | `background: #1C1C1C; border: 1px solid #242424;` |
| 96 | `#888888` |  | `.plan-box__label { font-size: 12px; color: #888888; font-family: 'Sweet Sans Pro', sans-serif; }` |
| 103 | `#888888` |  | `.plan-badge--observer    { background: transparent; color: #888888; border: 1px solid #2E2E2E; }` |
| 103 | `#2E2E2E` |  | `.plan-badge--observer    { background: transparent; color: #888888; border: 1px solid #2E2E2E; }` |
| 104 | `#101820` |  | `.plan-badge--benchmarker { background: #101820; color: #4A7FA5; border: 1px solid #4A7FA5; }` |
| 104 | `#4A7FA5` | LEGACY | `.plan-badge--benchmarker { background: #101820; color: #4A7FA5; border: 1px solid #4A7FA5; }` |
| 104 | `#4A7FA5` | LEGACY | `.plan-badge--benchmarker { background: #101820; color: #4A7FA5; border: 1px solid #4A7FA5; }` |
| 105 | `#101820` |  | `.plan-badge--advisory    { background: #101820; color: #4A7FA5; border: 1px solid #4A7FA5; }` |
| 105 | `#4A7FA5` | LEGACY | `.plan-badge--advisory    { background: #101820; color: #4A7FA5; border: 1px solid #4A7FA5; }` |
| 105 | `#4A7FA5` | LEGACY | `.plan-badge--advisory    { background: #101820; color: #4A7FA5; border: 1px solid #4A7FA5; }` |
| 108 | `#C86060` |  | `background: transparent; border: 1px solid #C86060;` |
| 109 | `#C86060` |  | `color: #C86060; font-size: 0.8125rem;` |
| 116 | `#888888` |  | `color: #888888; margin-bottom: 6px;` |
| 122 | `#F0F0EE` | LEGACY | `color: #F0F0EE; background: #1C1C1C; border: 1px solid #242424;` |
| 122 | `#1C1C1C` |  | `color: #F0F0EE; background: #1C1C1C; border: 1px solid #242424;` |
| 122 | `#242424` | LEGACY | `color: #F0F0EE; background: #1C1C1C; border: 1px solid #242424;` |
| 125 | `#4A7FA5` | LEGACY | `.form-input:focus { border-color: #4A7FA5; background: #141414; }` |
| 125 | `#141414` | LEGACY | `.form-input:focus { border-color: #4A7FA5; background: #141414; }` |
| 126 | `#444444` |  | `.form-input::placeholder { color: #444444; }` |
| 131 | `#888888` |  | `color: #888888; background: #1C1C1C; border: 1px solid #242424; border-radius: 4px;` |
| 131 | `#1C1C1C` |  | `color: #888888; background: #1C1C1C; border: 1px solid #242424; border-radius: 4px;` |
| 131 | `#242424` | LEGACY | `color: #888888; background: #1C1C1C; border: 1px solid #242424; border-radius: 4px;` |
| 136 | `#4A7FA5` | LEGACY | `background: transparent; color: #4A7FA5;` |
| 139 | `#4A7FA5` | LEGACY | `border: 1px solid #4A7FA5; border-radius: 4px; cursor: pointer; transition: 150ms;` |
| 142 | `#4A7FA5` | LEGACY | `.btn-primary:hover { background: #4A7FA5; color: #FFFFFF; }` |
| 142 | `#FFFFFF` |  | `.btn-primary:hover { background: #4A7FA5; color: #FFFFFF; }` |
| 146 | `#C86060` |  | `font-size: 0.8125rem; color: #C86060;` |
| 150 | `#444444` |  | `.auth-note { text-align: center; padding: 20px; font-size: 0.75rem; color: #444444; font-family: 'Sweet Sans P` |
| 176 | `#888888` |  | `<p style="font-size:13px;color:#888888;margin-top:8px">` |
| 177 | `#4A7FA5` | LEGACY | `Need help? Email us at <a href="mailto:hello@kodo.ma" style="color:#4A7FA5">hello@kodo.ma</a>` |

## `templates/account.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 55 | `rgba(74,127,165,0.1)` |  | `background: rgba(74,127,165,0.1);` |
| 56 | `rgba(74,127,165,0.28)` |  | `border: 1px solid rgba(74,127,165,0.28);` |
| 65 | `rgba(74,127,165,0.06)` |  | `background: rgba(74,127,165,0.06);` |
| 66 | `rgba(74,127,165,0.2)` |  | `border-color: rgba(74,127,165,0.2);` |
| 67 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 132 | `#fff` |  | `background: var(--accent); color: #fff; border: none;` |
| 141 | `#ef4444` |  | `.acc-msg--err { color: #ef4444; }` |
| 248 | `rgba(0,0,0,0.5)` |  | `<div id="invite-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);` |
| 370 | `#5A8A5A` |  | `active:   '#5A8A5A',` |
| 371 | `#4A7FA5` | LEGACY | `invited:  '#4A7FA5',` |
| 372 | `#C86060` |  | `suspended:'#C86060',` |
| 373 | `#888888` |  | `}[m.status] ¦¦ '#888888';` |
| 380 | `#ef4444` |  | `onmouseenter="this.style.color='#ef4444'" onmouseleave="this.style.color='var(--text-dim)'">✕</button>` |
| 402 | `#4A7FA5` | LEGACY | `<span style="width:7px;height:7px;border-radius:50%;background:#4A7FA5;flex-shrink:0"></span>` |
| 463 | `#ef4444` |  | `el.style.color  = ok ? 'var(--green)' : '#ef4444';` |

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
| 32 | `#0A0A0A` | LEGACY | `background: #0A0A0A;` |
| 33 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 52 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 61 | `#888888` |  | `color: #888888;` |
| 64 | `#F0F0EE` | LEGACY | `.top-bar__back:hover { color: #F0F0EE; }` |
| 75 | `#141414` | LEGACY | `background: #141414;` |
| 76 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 88 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 96 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 101 | `#888888` |  | `color: #888888;` |
| 114 | `#888888` |  | `color: #888888;` |
| 122 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 123 | `#1C1C1C` |  | `background: #1C1C1C;` |
| 124 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 130 | `#4A7FA5` | LEGACY | `.form-input:focus { border-color: #4A7FA5; background: #1C1C1C; }` |
| 130 | `#1C1C1C` |  | `.form-input:focus { border-color: #4A7FA5; background: #1C1C1C; }` |
| 131 | `#444444` |  | `.form-input::placeholder { color: #444444; }` |
| 142 | `rgba(200,90,90,0.10)` |  | `background: rgba(200,90,90,0.10);` |
| 143 | `rgba(200,90,90,0.30)` |  | `border: 1px solid rgba(200,90,90,0.30);` |
| 144 | `#E07070` |  | `color: #E07070;` |
| 147 | `rgba(90,138,90,0.10)` |  | `background: rgba(90,138,90,0.10);` |
| 148 | `rgba(90,138,90,0.30)` |  | `border: 1px solid rgba(90,138,90,0.30);` |
| 149 | `#7AB07A` |  | `color: #7AB07A;` |
| 156 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 157 | `#FFFFFF` |  | `color: #FFFFFF;` |
| 163 | `#4A7FA5` | LEGACY | `border: 1px solid #4A7FA5;` |
| 169 | `#3A6A8E` | LEGACY | `.btn-primary:hover:not(:disabled) { background: #3A6A8E; border-color: #3A6A8E; }` |
| 169 | `#3A6A8E` | LEGACY | `.btn-primary:hover:not(:disabled) { background: #3A6A8E; border-color: #3A6A8E; }` |
| 170 | `#2F5670` |  | `.btn-primary:active:not(:disabled) { background: #2F5670; border-color: #2F5670; color: #FFFFFF; }` |
| 170 | `#2F5670` |  | `.btn-primary:active:not(:disabled) { background: #2F5670; border-color: #2F5670; color: #FFFFFF; }` |
| 170 | `#FFFFFF` |  | `.btn-primary:active:not(:disabled) { background: #2F5670; border-color: #2F5670; color: #FFFFFF; }` |
| 177 | `#242424` | LEGACY | `border-top: 1px solid #242424;` |
| 180 | `#888888` |  | `.auth-footer p { font-size: 0.8125rem; color: #888888; line-height: 1.6; }` |
| 181 | `#4A7FA5` | LEGACY | `.auth-footer a { color: #4A7FA5; text-decoration: none; font-weight: 500; }` |
| 188 | `#444444` |  | `color: #444444;` |

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
| 1033 | `rgba(107,122,141,0.12)` |  | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `#6B7A8D` | LEGACY | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `#6B7A8D` | LEGACY | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `rgba(74,127,165,0.12)` |  | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `#4A7FA5` | LEGACY | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `#4A7FA5` | LEGACY | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `rgba(74,155,111,0.12)` |  | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `#4A9B6F` | LEGACY | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `#4A9B6F` | LEGACY | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `rgba(242,163,61,0.12)` |  | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `#F2A33D` | LEGACY | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1033 | `#F2A33D` | LEGACY | `<div class="kpi-card"><span class="kpi-label">Portfolio Types</span><div style="display:flex;flex-wrap:wrap;ga` |
| 1553 | `#6AAF8A` |  | `<span class="bar-cal-leg-item"><span class="bar-cal-dot" style="background:#6AAF8A"></span>&gt;80%</span>` |
| 1554 | `#3D7A5C` |  | `<span class="bar-cal-leg-item"><span class="bar-cal-dot" style="background:#3D7A5C"></span>60–80%</span>` |
| 1555 | `#2A5A3A` |  | `<span class="bar-cal-leg-item"><span class="bar-cal-dot" style="background:#2A5A3A"></span>40–60%</span>` |
| 1556 | `#1A2A1A` |  | `<span class="bar-cal-leg-item"><span class="bar-cal-dot" style="background:#1A2A1A"></span>&lt;40%</span>` |
| 1713 | `#666` | fallback | `<p style="font-size:0.75rem;color:var(--text-faint,#666);margin-top:4px;">Reports generated live from current ` |
| 1802 | `rgba(0,0,0,0.45)` |  | `<div id="upgrade-modal" style="display:none;position:fixed;inset:0;z-index:2000;background:rgba(0,0,0,0.45);di` |
| 1806 | `#F0F0EE` | LEGACY | `<h2 id="upgrade-title" style="font-family:'Sweet Sans Pro',sans-serif;font-size:1.5rem;font-weight:400;letter-` |
| 1808 | `#1C1C1C` | fallback | `<div style="background:var(--surface-hover,#1C1C1C);border:1px solid var(--border);padding:16px;margin-bottom:` |
| 1818 | `#4A7FA5` | LEGACY | `<a href="/#pricing" style="flex:1;display:block;padding:11px;border-radius:999px;background:#4A7FA5;color:#fff` |
| 1818 | `#fff` |  | `<a href="/#pricing" style="flex:1;display:block;padding:11px;border-radius:999px;background:#4A7FA5;color:#fff` |

## `templates/landing.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#0075DE` |  | `<meta name="theme-color" content="#0075DE">` |

## `templates/login.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 32 | `#0A0A0A` | LEGACY | `background: #0A0A0A;` |
| 33 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 52 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 62 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 63 | `#FFFFFF` |  | `color: #FFFFFF;` |
| 80 | `#888888` |  | `color: #888888;` |
| 83 | `#F0F0EE` | LEGACY | `.top-bar__back:hover { color: #F0F0EE; }` |
| 94 | `#141414` | LEGACY | `background: #141414;` |
| 95 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 107 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 115 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 129 | `#888888` |  | `color: #888888;` |
| 137 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 138 | `#1C1C1C` |  | `background: #1C1C1C;` |
| 139 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 146 | `#4A7FA5` | LEGACY | `border-color: #4A7FA5;` |
| 147 | `#1C1C1C` |  | `background: #1C1C1C;` |
| 149 | `#444444` |  | `.form-input::placeholder { color: #444444; }` |
| 160 | `rgba(200,90,90,0.10)` |  | `background: rgba(200,90,90,0.10);` |
| 161 | `rgba(200,90,90,0.30)` |  | `border: 1px solid rgba(200,90,90,0.30);` |
| 162 | `#E07070` |  | `color: #E07070;` |
| 165 | `rgba(90,138,90,0.10)` |  | `background: rgba(90,138,90,0.10);` |
| 166 | `rgba(90,138,90,0.30)` |  | `border: 1px solid rgba(90,138,90,0.30);` |
| 167 | `#7AB07A` |  | `color: #7AB07A;` |
| 172 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 184 | `#888888` |  | `color: #888888;` |
| 192 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 193 | `#FFFFFF` |  | `color: #FFFFFF;` |
| 199 | `#4A7FA5` | LEGACY | `border: 1px solid #4A7FA5;` |
| 205 | `#3A6A8E` | LEGACY | `.btn-primary:hover { background: #3A6A8E; border-color: #3A6A8E; }` |
| 205 | `#3A6A8E` | LEGACY | `.btn-primary:hover { background: #3A6A8E; border-color: #3A6A8E; }` |
| 206 | `#2F5670` |  | `.btn-primary:active { background: #2F5670; border-color: #2F5670; color: #FFFFFF; }` |
| 206 | `#2F5670` |  | `.btn-primary:active { background: #2F5670; border-color: #2F5670; color: #FFFFFF; }` |
| 206 | `#FFFFFF` |  | `.btn-primary:active { background: #2F5670; border-color: #2F5670; color: #FFFFFF; }` |
| 212 | `#242424` | LEGACY | `border-top: 1px solid #242424;` |
| 216 | `#888888` |  | `color: #888888;` |
| 220 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 225 | `#242424` | LEGACY | `.auth-footer .divider { margin: 10px 0; border: none; border-top: 1px solid #242424; }` |
| 232 | `#444444` |  | `color: #444444;` |

## `templates/methodology.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 304 | `#555555` |  | `<p style="font-size:12px;color:#555555;">Data is processed under a strict confidentiality agreement. Individua` |

## `templates/payment_pending.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 28 | `#0A0A0A` | LEGACY | `background: #0A0A0A;` |
| 29 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 46 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 56 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 57 | `#FFFFFF` |  | `color: #FFFFFF;` |
| 81 | `#141414` | LEGACY | `background: #141414;` |
| 82 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 94 | `rgba(90,138,90,0.12)` |  | `background: rgba(90,138,90,0.12);` |
| 95 | `rgba(90,138,90,0.30)` |  | `border: 1px solid rgba(90,138,90,0.30);` |
| 102 | `#5A8A5A` |  | `color: #5A8A5A;` |
| 111 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 119 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 124 | `#888888` |  | `color: #888888;` |
| 133 | `#1C1C1C` |  | `background: #1C1C1C;` |
| 134 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 141 | `#888888` |  | `color: #888888;` |
| 149 | `#5A8A5A` |  | `color: #5A8A5A;` |
| 157 | `#101820` |  | `background: #101820;` |
| 158 | `rgba(74,127,165,0.25)` |  | `border: 1px solid rgba(74,127,165,0.25);` |
| 170 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 177 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 182 | `#888888` |  | `color: #888888;` |
| 189 | `#242424` | LEGACY | `background: #242424;` |
| 190 | `#444444` |  | `color: #444444;` |
| 204 | `#888888` |  | `color: #888888;` |
| 209 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 219 | `#444444` |  | `color: #444444;` |

## `templates/privacy.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/register.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 32 | `#0A0A0A` | LEGACY | `background: #0A0A0A;` |
| 33 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 51 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 61 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 62 | `#FFFFFF` |  | `color: #FFFFFF;` |
| 79 | `#888888` |  | `color: #888888;` |
| 82 | `#F0F0EE` | LEGACY | `.top-bar__back:hover { color: #F0F0EE; }` |
| 92 | `#141414` | LEGACY | `background: #141414;` |
| 93 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 105 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 113 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 118 | `#888888` |  | `color: #888888;` |
| 138 | `#888888` |  | `color: #888888;` |
| 146 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 147 | `#1C1C1C` |  | `background: #1C1C1C;` |
| 148 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 155 | `#4A7FA5` | LEGACY | `border-color: #4A7FA5;` |
| 156 | `#1C1C1C` |  | `background: #1C1C1C;` |
| 158 | `#444444` |  | `.form-input::placeholder { color: #444444; }` |
| 161 | `rgba(200,90,90,0.10)` |  | `background: rgba(200,90,90,0.10);` |
| 162 | `rgba(200,90,90,0.30)` |  | `border: 1px solid rgba(200,90,90,0.30);` |
| 163 | `#E07070` |  | `color: #E07070;` |
| 182 | `#4A7FA5` | LEGACY | `accent-color: #4A7FA5;` |
| 188 | `#888888` |  | `color: #888888;` |
| 192 | `#4A7FA5` | LEGACY | `.checkbox-row a { color: #4A7FA5; text-decoration: none; }` |
| 197 | `#1C1C1C` |  | `background: #1C1C1C;` |
| 198 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 209 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 216 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 222 | `#888888` |  | `color: #888888;` |
| 227 | `#5A8A5A` |  | `color: #5A8A5A;` |
| 234 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 235 | `#FFFFFF` |  | `color: #FFFFFF;` |
| 241 | `#4A7FA5` | LEGACY | `border: 1px solid #4A7FA5;` |
| 246 | `#3A6A8E` | LEGACY | `.btn-primary:hover { background: #3A6A8E; border-color: #3A6A8E; }` |
| 246 | `#3A6A8E` | LEGACY | `.btn-primary:hover { background: #3A6A8E; border-color: #3A6A8E; }` |
| 250 | `#444444` |  | `color: #444444;` |
| 257 | `#242424` | LEGACY | `border-top: 1px solid #242424;` |
| 261 | `#888888` |  | `color: #888888;` |
| 264 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 274 | `#444444` |  | `color: #444444;` |
| 307 | `#888888` |  | `<p class="plan-box__price">MAD 990 <span style="font-size:0.875rem;font-weight:400;color:#888888;">/ month</sp` |

## `templates/reset_password.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 32 | `#0A0A0A` | LEGACY | `background: #0A0A0A;` |
| 33 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 46 | `#F0F0EE` | LEGACY | `.top-bar__logo { display: flex; align-items: center; gap: 8px; text-decoration: none; color: #F0F0EE; }` |
| 48 | `#888888` |  | `.top-bar__back { font-size: 13px; color: #888888; text-decoration: none; }` |
| 49 | `#F0F0EE` | LEGACY | `.top-bar__back:hover { color: #F0F0EE; }` |
| 59 | `#141414` | LEGACY | `background: #141414;` |
| 60 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 72 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 80 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 83 | `#888888` |  | `.auth-sub { font-size: 0.875rem; color: #888888; line-height: 1.6; margin-bottom: 28px; }` |
| 92 | `#888888` |  | `color: #888888;` |
| 100 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 101 | `#1C1C1C` |  | `background: #1C1C1C;` |
| 102 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 108 | `#4A7FA5` | LEGACY | `.form-input:focus { border-color: #4A7FA5; background: #1C1C1C; }` |
| 108 | `#1C1C1C` |  | `.form-input:focus { border-color: #4A7FA5; background: #1C1C1C; }` |
| 109 | `#444444` |  | `.form-input::placeholder { color: #444444; }` |
| 119 | `rgba(200,90,90,0.10)` |  | `background: rgba(200,90,90,0.10);` |
| 120 | `rgba(200,90,90,0.30)` |  | `border: 1px solid rgba(200,90,90,0.30);` |
| 121 | `#E07070` |  | `color: #E07070;` |
| 124 | `rgba(90,138,90,0.10)` |  | `background: rgba(90,138,90,0.10);` |
| 125 | `rgba(90,138,90,0.30)` |  | `border: 1px solid rgba(90,138,90,0.30);` |
| 126 | `#7AB07A` |  | `color: #7AB07A;` |
| 128 | `#4A7FA5` | LEGACY | `.auth-success a { color: #4A7FA5; font-weight: 600; }` |
| 134 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 135 | `#FFFFFF` |  | `color: #FFFFFF;` |
| 143 | `#4A7FA5` | LEGACY | `border: 1px solid #4A7FA5;` |
| 149 | `#3A6A8E` | LEGACY | `.btn-primary:hover:not(:disabled) { background: #3A6A8E; border-color: #3A6A8E; }` |
| 149 | `#3A6A8E` | LEGACY | `.btn-primary:hover:not(:disabled) { background: #3A6A8E; border-color: #3A6A8E; }` |
| 150 | `#2F5670` |  | `.btn-primary:active:not(:disabled) { background: #2F5670; border-color: #2F5670; color: #FFFFFF; }` |
| 150 | `#2F5670` |  | `.btn-primary:active:not(:disabled) { background: #2F5670; border-color: #2F5670; color: #FFFFFF; }` |
| 150 | `#FFFFFF` |  | `.btn-primary:active:not(:disabled) { background: #2F5670; border-color: #2F5670; color: #FFFFFF; }` |
| 156 | `#242424` | LEGACY | `border-top: 1px solid #242424;` |
| 159 | `#888888` |  | `.auth-footer p { font-size: 0.8125rem; color: #888888; line-height: 1.6; }` |
| 160 | `#4A7FA5` | LEGACY | `.auth-footer a { color: #4A7FA5; text-decoration: none; font-weight: 500; }` |
| 163 | `#444444` |  | `.auth-note { text-align: center; padding: 20px; font-size: 0.75rem; color: #444444; }` |

## `templates/terms.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |

## `templates/verify_email.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 32 | `#0A0A0A` | LEGACY | `background: #0A0A0A;` |
| 33 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 51 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 54 | `#888888` |  | `.top-bar__back { font-size: 13px; color: #888888; text-decoration: none; }` |
| 55 | `#F0F0EE` | LEGACY | `.top-bar__back:hover { color: #F0F0EE; }` |
| 65 | `#141414` | LEGACY | `background: #141414;` |
| 66 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 79 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 87 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 92 | `#888888` |  | `color: #888888;` |
| 104 | `#888888` |  | `color: #888888;` |
| 112 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 113 | `#1C1C1C` |  | `background: #1C1C1C;` |
| 114 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 120 | `#4A7FA5` | LEGACY | `.form-input:focus { border-color: #4A7FA5; }` |
| 121 | `#444444` |  | `.form-input::placeholder { color: #444444; }` |
| 132 | `rgba(200,90,90,0.10)` |  | `background: rgba(200,90,90,0.10);` |
| 133 | `rgba(200,90,90,0.30)` |  | `border: 1px solid rgba(200,90,90,0.30);` |
| 134 | `#E07070` |  | `color: #E07070;` |
| 137 | `rgba(90,138,90,0.10)` |  | `background: rgba(90,138,90,0.10);` |
| 138 | `rgba(90,138,90,0.30)` |  | `border: 1px solid rgba(90,138,90,0.30);` |
| 139 | `#7AB07A` |  | `color: #7AB07A;` |
| 145 | `#4A7FA5` | LEGACY | `background: #4A7FA5;` |
| 146 | `#FFFFFF` |  | `color: #FFFFFF;` |
| 152 | `#4A7FA5` | LEGACY | `border: 1px solid #4A7FA5;` |
| 158 | `#3A6A8E` | LEGACY | `.btn-primary:hover:not(:disabled) { background: #3A6A8E; border-color: #3A6A8E; }` |
| 158 | `#3A6A8E` | LEGACY | `.btn-primary:hover:not(:disabled) { background: #3A6A8E; border-color: #3A6A8E; }` |
| 164 | `#242424` | LEGACY | `border-top: 1px solid #242424;` |
| 167 | `#888888` |  | `.auth-footer p { font-size: 0.8125rem; color: #888888; line-height: 1.6; }` |
| 168 | `#4A7FA5` | LEGACY | `.auth-footer a { color: #4A7FA5; text-decoration: none; font-weight: 500; }` |
| 175 | `#444444` |  | `color: #444444;` |

## `templates/verify_email_sent.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#4A7FA5` | LEGACY | `<meta name="theme-color" content="#4A7FA5">` |
| 32 | `#0A0A0A` | LEGACY | `background: #0A0A0A;` |
| 33 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 51 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 54 | `#888888` |  | `.top-bar__back { font-size: 13px; color: #888888; text-decoration: none; }` |
| 55 | `#F0F0EE` | LEGACY | `.top-bar__back:hover { color: #F0F0EE; }` |
| 65 | `#141414` | LEGACY | `background: #141414;` |
| 66 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 79 | `#4A7FA5` | LEGACY | `color: #4A7FA5;` |
| 87 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 92 | `#888888` |  | `color: #888888;` |
| 98 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 109 | `#F0F0EE` | LEGACY | `color: #F0F0EE;` |
| 115 | `#242424` | LEGACY | `border: 1px solid #242424;` |
| 122 | `#4A7FA5` | LEGACY | `.btn-secondary:hover { border-color: #4A7FA5; color: #4A7FA5; }` |
| 122 | `#4A7FA5` | LEGACY | `.btn-secondary:hover { border-color: #4A7FA5; color: #4A7FA5; }` |
| 126 | `#444444` |  | `color: #444444;` |
| 134 | `#242424` | LEGACY | `border-top: 1px solid #242424;` |
| 137 | `#888888` |  | `.auth-footer p { font-size: 0.8125rem; color: #888888; line-height: 1.6; }` |
| 138 | `#4A7FA5` | LEGACY | `.auth-footer a { color: #4A7FA5; text-decoration: none; font-weight: 500; }` |
| 145 | `#444444` |  | `color: #444444;` |
