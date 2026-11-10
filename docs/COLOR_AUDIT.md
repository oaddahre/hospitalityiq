# Colour audit

Every hardcoded colour outside `static/css/tokens.css`, by file and line. Regenerate with `python3 scripts/color_audit.py`.

- **LEGACY**: an old palette value the final sweep must remove.
- **fallback**: the second argument of `var(--token, …)`; the page uses the token, the literal only applies where the token is undefined.

Total: 82 colour literals in 25 files (2 legacy).

## Per file

| File | Literals |
|---|---|
| `static/css/style.css` | 20 |
| `app.py` | 8 |
| `scripts/record_product_videos.py` | 6 |
| `generate_pdfs.py` | 4 |
| `static/css/marketing.css` | 3 |
| `static/images/news-placeholder.svg` | 3 |
| `static/css/admin.css` | 2 |
| `static/js/main.js` | 2 |
| `templates/about.html` | 2 |
| `templates/accept_invite.html` | 2 |
| `templates/account.html` | 2 |
| `templates/admin.html` | 2 |
| `templates/contact.html` | 2 |
| `templates/forgot_password.html` | 2 |
| `templates/index.html` | 2 |
| `templates/landing.html` | 2 |
| `templates/login.html` | 2 |
| `templates/methodology.html` | 2 |
| `templates/payment_pending.html` | 2 |
| `templates/privacy.html` | 2 |
| `templates/register.html` | 2 |
| `templates/reset_password.html` | 2 |
| `templates/terms.html` | 2 |
| `templates/verify_email.html` | 2 |
| `templates/verify_email_sent.html` | 2 |

## Legacy values still present

| Value | Count |
|---|---|
| `#141414` | 1 |
| `#242424` | 1 |

## Kept on purpose

| Where | Why |
|---|---|
| `app.py` `EMAIL_COLORS`, `_PALETTE_LIGHT` | Email HTML and fpdf cannot read CSS variables; these are the light-mode token values, commented with the token each one mirrors. |
| `generate_pdfs.py` constants | reportlab palette (light-mode token values) for the Data Sharing Agreement PDFs. |
| `static/js/main.js` `XLSX_COLORS` | Excel cell styles (hex without `#`, so not listed below); light-mode token values. |
| `static/css/style.css` print block | Paper is always light, so print uses the light token values even in a dark session. |
| `static/css/style.css` select chevrons (`%238A857E`) | SVG data URIs cannot read CSS variables; `--cat-6-dot` grey is 3.4:1 or more on every light and dark surface. |
| Box shadows `rgba(15,15,14,…)` | Neutral near-black shadow tint; shadows are not part of the palette and read the same in both modes. |
| `<meta name="theme-color">` `#FFFFFF` / `#000000` | Browser chrome colour; meta tags cannot use CSS variables. Values are the page colour `--bg`: pure white light / pure black dark. |
| `static/js/main.js` `withAlpha` helper | Builds `rgba()` from palette colours for canvas charts; contains no colour itself. |
| `static/images/news-placeholder.svg` (`#141414`, `#242424`, `#B87860`) | An image containing the text "KODO": per the brief, images with text are listed, not edited. Replace the file to update it. |

## `app.py`

| Line | Colour | Note | Context |
|---|---|---|---|
| 529 | `#F4F4F2` |  | `"page":      "#F4F4F2",   # --bg-alt (the email's outer band; the message card is white)` |
| 530 | `#FFFFFF` |  | `"card":      "#FFFFFF",   # --bg` |
| 531 | `#E5E3DF` |  | `"border":    "#E5E3DF",   # --border` |
| 532 | `#1F1E1C` |  | `"text":      "#1F1E1C",   # --text` |
| 533 | `#5F5B55` |  | `"text_2":    "#5F5B55",   # --text-2` |
| 534 | `#0075DE` |  | `"action":    "#0075DE",   # --action (button)` |
| 535 | `#006BCC` |  | `"link":      "#006BCC",   # --action-text (links, AA on white)` |
| 536 | `#FFFFFF` |  | `"on_action": "#FFFFFF",   # --on-action` |

## `generate_pdfs.py`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#0075DE` |  | `ACCENT    = colors.HexColor("#0075DE")   # headings, rules` |
| 18 | `#1F1E1C` |  | `TEXT      = colors.HexColor("#1F1E1C")   # body text` |
| 19 | `#5F5B55` |  | `GREY_TEXT = colors.HexColor("#5F5B55")   # secondary text` |
| 20 | `#E5E3DF` |  | `HAIRLINE  = colors.HexColor("#E5E3DF")   # thin dividers` |

## `scripts/record_product_videos.py`

| Line | Colour | Note | Context |
|---|---|---|---|
| 114 | `rgba(0, 117, 222, 0.16)` |  | `const ring = part(40, {background: 'rgba(0, 117, 222, 0.16)', border: '1px solid rgba(0, 117, 222, 0.32)'});` |
| 114 | `rgba(0, 117, 222, 0.32)` |  | `const ring = part(40, {background: 'rgba(0, 117, 222, 0.16)', border: '1px solid rgba(0, 117, 222, 0.32)'});` |
| 115 | `#0075DE` |  | `const rip = part(20, {border: '2px solid #0075DE', opacity: '0'});` |
| 116 | `#0075DE` |  | `const dot = part(20, {background: '#0075DE', border: '2px solid #FFFFFF',` |
| 116 | `#FFFFFF` |  | `const dot = part(20, {background: '#0075DE', border: '2px solid #FFFFFF',` |
| 117 | `rgba(0, 0, 0, 0.35)` |  | `boxShadow: '0 1px 3px rgba(0, 0, 0, 0.35)'});` |

## `static/css/admin.css`

| Line | Colour | Note | Context |
|---|---|---|---|
| 86 | `rgba(15,15,14,0.12)` |  | `box-shadow: 0 8px 24px rgba(15,15,14,0.12);` |
| 151 | `rgba(15,15,14,0.12)` |  | `box-shadow: 0 8px 24px rgba(15,15,14,0.12);` |

## `static/css/marketing.css`

| Line | Colour | Note | Context |
|---|---|---|---|
| 2963 | `rgba(31,30,28,.06)` |  | `box-shadow: 0 1px 2px rgba(31,30,28,.06), 0 12px 40px rgba(31,30,28,.08);` |
| 2963 | `rgba(31,30,28,.08)` |  | `box-shadow: 0 1px 2px rgba(31,30,28,.06), 0 12px 40px rgba(31,30,28,.08);` |
| 3066 | `rgba(20,19,18,.72)` |  | `.lp-lightbox::backdrop { background: rgba(20,19,18,.72); }` |

## `static/css/style.css`

| Line | Colour | Note | Context |
|---|---|---|---|
| 223 | `%238A857E` |  | `background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' view` |
| 1178 | `rgba(15,15,14,0.18)` |  | `box-shadow: 0 8px 32px rgba(15,15,14,0.18);` |
| 1469 | `%238A857E` |  | `background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' view` |
| 3834 | `rgba(31, 30, 28, 0.14)` |  | `box-shadow: 0 6px 20px rgba(31, 30, 28, 0.14), 0 1px 3px rgba(31, 30, 28, 0.08);` |
| 3834 | `rgba(31, 30, 28, 0.08)` |  | `box-shadow: 0 6px 20px rgba(31, 30, 28, 0.14), 0 1px 3px rgba(31, 30, 28, 0.08);` |
| 3846 | `rgba(0, 0, 0, 0.5)` |  | `:root[data-theme="dark"] .cal-tip { box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5), 0 1px 3px rgba(0, 0, 0, 0.4); }` |
| 3846 | `rgba(0, 0, 0, 0.4)` |  | `:root[data-theme="dark"] .cal-tip { box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5), 0 1px 3px rgba(0, 0, 0, 0.4); }` |
| 4683 | `#FFFFFF` |  | `body { background: #FFFFFF !important; color: #1F1E1C !important; font-family: 'Sweet Sans Pro', sans-serif; }` |
| 4683 | `#1F1E1C` |  | `body { background: #FFFFFF !important; color: #1F1E1C !important; font-family: 'Sweet Sans Pro', sans-serif; }` |
| 4687 | `#1F1E1C` |  | `.screen-header h1 { font-size: 22px; color: #1F1E1C; margin-bottom: 4px; }` |
| 4688 | `#5F5B55` |  | `.screen-header p { font-size: 11px; color: #5F5B55; margin-bottom: 20px; }` |
| 4691 | `#FFFFFF` |  | `background: #FFFFFF !important; border: 1px solid #E5E3DF !important;` |
| 4691 | `#E5E3DF` |  | `background: #FFFFFF !important; border: 1px solid #E5E3DF !important;` |
| 4695 | `#1F1E1C` |  | `.news-body { display: block !important; color: #1F1E1C !important; }` |
| 4696 | `#1F1E1C` |  | `.news-headline { color: #1F1E1C !important; font-size: 16px; }` |
| 4697 | `#5F5B55` |  | `.news-summary { color: #5F5B55 !important; }` |
| 4698 | `#5F5B55` |  | `.news-cat { border: none !important; color: #5F5B55 !important; background: #F1F0EE !important; }` |
| 4698 | `#F1F0EE` |  | `.news-cat { border: none !important; color: #5F5B55 !important; background: #F1F0EE !important; }` |
| 5973 | `rgba(31, 30, 28, 0.16)` |  | `box-shadow: -8px 0 32px rgba(31, 30, 28, 0.16); z-index: 7001; overflow-y: auto; padding: 16px 20px 24px; font` |
| 5985 | `rgba(0, 0, 0, 0.5)` |  | `:root[data-theme="dark"] .evc-panel { box-shadow: -8px 0 32px rgba(0, 0, 0, 0.5); }` |

## `static/images/news-placeholder.svg`

| Line | Colour | Note | Context |
|---|---|---|---|
| 2 | `#141414` | LEGACY | `<rect width="800" height="450" fill="#141414"/>` |
| 3 | `#242424` | LEGACY | `<rect x="0.5" y="0.5" width="799" height="449" fill="none" stroke="#242424"/>` |
| 4 | `#B87860` |  | `<text x="400" y="235" font-family="'Space Mono', monospace" font-size="14" letter-spacing="6" fill="#B87860" t` |

## `static/js/main.js`

| Line | Colour | Note | Context |
|---|---|---|---|
| 745 | `rgba()` |  | `// Hex colour + alpha → rgba() (Chart.js draws on canvas, so no CSS variables)` |
| 749 | `rgba(${(n >> 16)` |  | `return rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a});` |

## `templates/about.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 6 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 7 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/accept_invite.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 18 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/account.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 16 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 17 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/admin.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 18 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/contact.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 6 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 7 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/forgot_password.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 18 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/index.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 18 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/landing.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 18 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 19 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/login.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 18 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 19 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/methodology.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 18 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 19 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/payment_pending.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 18 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/privacy.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 18 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 19 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/register.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 18 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 19 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/reset_password.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 18 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/terms.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 18 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 19 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/verify_email.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 18 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |

## `templates/verify_email_sent.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 18 | `#000000` |  | `<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">` |
