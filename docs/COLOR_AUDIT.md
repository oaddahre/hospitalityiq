# Colour audit

Every hardcoded colour outside `static/css/tokens.css`, by file and line. Regenerate with `python3 scripts/color_audit.py`.

- **LEGACY**: an old palette value the final sweep must remove.
- **fallback**: the second argument of `var(--token, …)`; the page uses the token, the literal only applies where the token is undefined.

Total: 67 colour literals in 23 files (2 legacy).

## Per file

| File | Literals |
|---|---|
| `static/css/style.css` | 14 |
| `app.py` | 8 |
| `generate_pdfs.py` | 4 |
| `static/images/news-placeholder.svg` | 3 |
| `static/css/admin.css` | 2 |
| `static/js/main.js` | 2 |
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
| `templates/team.html` | 2 |
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
| `<meta name="theme-color">` `#FFFFFF` / `#191918` | Browser chrome colour; meta tags cannot use CSS variables. Values are `--bg` light / dark. |
| `static/js/main.js` `withAlpha` helper | Builds `rgba()` from palette colours for canvas charts; contains no colour itself. |
| `static/images/news-placeholder.svg` (`#141414`, `#242424`, `#B87860`) | An image containing the text "KODO": per the brief, images with text are listed, not edited. Replace the file to update it. |

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

## `generate_pdfs.py`

| Line | Colour | Note | Context |
|---|---|---|---|
| 17 | `#0075DE` |  | `ACCENT    = colors.HexColor("#0075DE")   # headings, rules` |
| 18 | `#1F1E1C` |  | `TEXT      = colors.HexColor("#1F1E1C")   # body text` |
| 19 | `#5F5B55` |  | `GREY_TEXT = colors.HexColor("#5F5B55")   # secondary text` |
| 20 | `#E7E4DF` |  | `HAIRLINE  = colors.HexColor("#E7E4DF")   # thin dividers` |

## `static/css/admin.css`

| Line | Colour | Note | Context |
|---|---|---|---|
| 78 | `rgba(15,15,14,0.12)` |  | `box-shadow: 0 8px 24px rgba(15,15,14,0.12);` |
| 143 | `rgba(15,15,14,0.12)` |  | `box-shadow: 0 8px 24px rgba(15,15,14,0.12);` |

## `static/css/style.css`

| Line | Colour | Note | Context |
|---|---|---|---|
| 223 | `%238A857E` |  | `background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' view` |
| 1166 | `rgba(15,15,14,0.18)` |  | `box-shadow: 0 8px 32px rgba(15,15,14,0.18);` |
| 1457 | `%238A857E` |  | `background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' view` |
| 4826 | `#FFFFFF` |  | `body { background: #FFFFFF !important; color: #1F1E1C !important; font-family: 'Sweet Sans Pro', sans-serif; }` |
| 4826 | `#1F1E1C` |  | `body { background: #FFFFFF !important; color: #1F1E1C !important; font-family: 'Sweet Sans Pro', sans-serif; }` |
| 4830 | `#1F1E1C` |  | `.screen-header h1 { font-size: 22px; color: #1F1E1C; margin-bottom: 4px; }` |
| 4831 | `#5F5B55` |  | `.screen-header p { font-size: 11px; color: #5F5B55; margin-bottom: 20px; }` |
| 4834 | `#FFFFFF` |  | `background: #FFFFFF !important; border: 1px solid #E7E4DF !important;` |
| 4834 | `#E7E4DF` |  | `background: #FFFFFF !important; border: 1px solid #E7E4DF !important;` |
| 4838 | `#1F1E1C` |  | `.news-body { display: block !important; color: #1F1E1C !important; }` |
| 4839 | `#1F1E1C` |  | `.news-headline { color: #1F1E1C !important; font-size: 16px; }` |
| 4840 | `#5F5B55` |  | `.news-summary { color: #5F5B55 !important; }` |
| 4841 | `#5F5B55` |  | `.news-cat { border: none !important; color: #5F5B55 !important; background: #F1F0EE !important; }` |
| 4841 | `#F1F0EE` |  | `.news-cat { border: none !important; color: #5F5B55 !important; background: #F1F0EE !important; }` |

## `static/images/news-placeholder.svg`

| Line | Colour | Note | Context |
|---|---|---|---|
| 2 | `#141414` | LEGACY | `<rect width="800" height="450" fill="#141414"/>` |
| 3 | `#242424` | LEGACY | `<rect x="0.5" y="0.5" width="799" height="449" fill="none" stroke="#242424"/>` |
| 4 | `#B87860` |  | `<text x="400" y="235" font-family="'Space Mono', monospace" font-size="14" letter-spacing="6" fill="#B87860" t` |

## `static/js/main.js`

| Line | Colour | Note | Context |
|---|---|---|---|
| 480 | `rgba()` |  | `// Hex colour + alpha → rgba() (Chart.js draws on canvas, so no CSS variables)` |
| 484 | `rgba(${(n >> 16)` |  | `return rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a});` |

## `templates/accept_invite.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 12 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/account.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 12 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/admin.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 13 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/contact.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 6 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 7 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/forgot_password.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 12 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/index.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 13 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/landing.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 13 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/login.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 12 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/methodology.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 13 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/payment_pending.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 12 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/privacy.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 13 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/register.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 12 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/reset_password.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 12 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/team.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 6 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 7 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/terms.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 12 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 13 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/verify_email.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 12 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |

## `templates/verify_email_sent.html`

| Line | Colour | Note | Context |
|---|---|---|---|
| 11 | `#FFFFFF` |  | `<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">` |
| 12 | `#191918` |  | `<meta name="theme-color" content="#191918" media="(prefers-color-scheme: dark)">` |
