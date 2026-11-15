# Brand: logo and icons

**Logo (Nov 2026):** the slanted-dot wordmark "kodo.".

- **Colours:** black #000000, white #FFFFFF, blue #0075DE. The dot is always blue.
- **Sources:** `_handoff/kodo_logo/` (README.txt there).
- **Site copies:** `static/images/brand/`.
- **Format:** every SVG is outlined paths, so no font is needed.

| Where | File | Notes |
| --- | --- | --- |
| Every page header, footer, mobile menu, admin | `kodo-logo-black.svg` (light mode, `.logo-light`), `kodo-logo-white.svg` (dark mode, `.logo-dark`) | Both are in the page; `tokens.css` shows the one for `<html data-theme>`. Height `--nav-logo-h`: 26 px, or 22 px under 768 px. Login, register and the other account pages use 28 px. Never under 20 px. Alt text "Kodo Hospitality" |
| Favicon and app icons, every page | `templates/_favicon.html` | `favicon.svg` (dark browsers get the inverted square), `favicon.ico` (16/32/48), `favicon-32.png`, `favicon-16.png`, `apple-touch-icon.png`, `site.webmanifest` (192 and 512 icons). Bump `?v=` when the icons change. `/favicon.ico` serves the same .ico |
| Emails | `https://www.kodohospitality.com/static/images/brand/kodo-logo-black-800.png` | 80 × 26 px, absolute URL (`EMAIL_LOGO_URL` in app.py). Emails are light only |
| PDF reports | `kodo-logo-black-800.png` (`_PDF_LOGO`) | Aspect 800:260 |
| Social sharing (Open Graph, Twitter) | `og-image.png`, 1200 × 630 | `templates/_social.html`, on the public pages |

`scripts/check_brand.py` fails if a logo file is missing, if anything still points to the old logo or favicons (`static/img/brand`, `kodo-logo-dark` and `kodo-logo-light`, `favicon-light` and `favicon-dark`), or if a page template does not include `_favicon.html`.

The landing page screenshots and the product video show the platform header. Re-take them after any logo change:

- `scripts/capture_profile_screenshots.py`
- `scripts/record_product_videos.py`
