#!/usr/bin/env python3
"""Capture the landing page's hotel and owner profile screenshots (light and dark).

    python3 scripts/capture_profile_screenshots.py

Starts its own copy of the app on a free local port: a temporary DATA_DIR
holding the platform's own hotel, performance, pipeline and owner data (plus
the local scraped rates and occupancy model output, if present), a
local-only demo account, and no API keys. Nothing is written to the real
data files or users, and no real user appears on screen.

For each theme it opens the La Mamounia hotel profile and the Madaef owner
profile at 1440x900 with deviceScaleFactor 2, waits for fonts, data and
charts, scrolls the page as little as possible so the bottom edge falls
between blocks (never through a row of text), checks for console errors,
spinners, toasts and a clipped theme toggle, and writes:

    static/img/product/hotel-profile-{light,dark}.webp / .png   2880x1800
    static/img/product/owner-profile-{light,dark}.webp / .png   2880x1800

These use the platform's real data, so no "Sample data" tag is added.

Operator logos come from a third-party logo CDN that refuses requests from
localhost. Those requests are blocked here so they fail at once and the page
falls back to text-only operator names, as it does whenever a logo can't load.

Requires: playwright (with Chromium) and Pillow.
"""
import os
import shutil
import sys
import tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from record_product_videos import DEMO_EMAIL, DEMO_PASS, free_port, start_server  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "static", "img", "product")
W, H, DSF, WEBP_Q = 1440, 900, 2, 90
HOTEL_ID = 58                  # La Mamounia, Marrakech
OWNER_ID = "madaef"            # Madaef, state-owned
# Local-only data files (gitignored) the profiles read when present
EXTRA_FILES = ("scraped_rates.csv", "estimated_occupancy.csv")

# Smallest scroll (within `limit`) that leaves the bottom edge of the
# visible area between blocks rather than through one.
FIT_SCROLL_JS = """
([blocks, limit]) => {
  const m = document.querySelector('.main-content');
  m.scrollTop = 0;
  const top = m.getBoundingClientRect().top, bottom = m.getBoundingClientRect().bottom;
  const els = [...document.querySelectorAll(blocks)].filter(e => e.offsetParent)
    .map(e => { const r = e.getBoundingClientRect(); return [r.top - top, r.bottom - top]; });
  const view = bottom - top;
  for (let s = 0; s <= limit; s++) {
    const edge = s + view;
    if (!els.some(([a, b]) => edge > a + 1 && edge < b - 1)) { m.scrollTop = s; return s; }
  }
  return 0;
}
"""

CHECK_JS = """
() => {
  const vis = e => e.offsetParent && getComputedStyle(e).visibility !== 'hidden';
  const busy = [...document.querySelectorAll('.bar-cal-loading, .loading, .spinner, .toast, .error-banner, .hpipe-empty')]
    .filter(vis).map(e => e.className + ': ' + e.textContent.trim().slice(0, 40));
  const t = document.getElementById('theme-toggle').getBoundingClientRect();
  const text = document.querySelector('.screen.active').innerText;
  const bad = (text.match(/\\b(NaN|undefined|null|None|Infinity)\\b|\\[object/g) || []);
  return {busy, bad, toggle: [t.left, t.right, innerWidth, !!document.getElementById('theme-toggle').offsetParent]};
}
"""

SHOTS = {
    "hotel-profile": {
        "open": f"showHotelDetail({HOTEL_ID})",
        "ready": """() => document.querySelectorAll('#hrate-calendar .bar-cal-day').length === 30
                    && document.querySelectorAll('#hocc-calendar .bar-cal-day').length === 30
                    && getComputedStyle(document.getElementById('hotel-cal-averages')).display !== 'none'""",
        "blocks": ".hotel-hd, .kpi-card, .table-card-header, .bar-calendar, .bar-cal-legend, .rate-updated-note,"
                  " .dual-cal-avg-bar, .fin-range-row, .fin-disclaimer, .chart-card-header",
        "limit": 48,           # keeps the hotel name clear of the top bar
    },
    "owner-profile": {
        "nav": "owners",       # open the Owners screen and let its list render first
        "open": f"showOwnerDetail('{OWNER_ID}')",
        "ready": """() => getComputedStyle(document.getElementById('screen-owner-detail')).display !== 'none'
                    && document.querySelectorAll('#owner-portfolio-tbody tr').length > 0
                    && [...document.querySelectorAll('#screen-owner-detail img')].every(i => i.complete)""",
        "blocks": ".brand-detail-header, .brand-about-card, .kpi-card, .brand-meta-row, .chart-card-header,"
                  " .owner-portfolio-table tr",
        "limit": 48,
    },
}


def capture(base, mode, work):
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=DSF)
        ctx.add_init_script(f"try{{localStorage.setItem('kodo-theme','{mode}')}}catch(e){{}}")
        ctx.route("**/cdn.brandfetch.io/**", lambda r: r.abort())
        page = ctx.new_page()
        page.on("console", lambda m: problems.append(m.text)
                if m.type == "error" and "brandfetch" not in (m.location or {}).get("url", "")
                and "ERR_FAILED" not in m.text else None)
        page.on("pageerror", lambda e: problems.append(str(e)))
        page.goto(base + "/login")
        page.fill("input[type=email]", DEMO_EMAIL)
        page.fill("input[type=password]", DEMO_PASS)
        page.click("button[type=submit]")
        page.wait_for_url("**/dashboard")
        page.wait_for_load_state("networkidle")
        page.wait_for_function("typeof hotels !== 'undefined' && hotels.length > 0")
        for name, spec in SHOTS.items():
            if spec.get("nav"):
                page.evaluate(f"document.querySelector('.nav-link[data-screen=\"{spec['nav']}\"]').click()")
                page.wait_for_function("document.querySelectorAll('#owners-grid .owner-card').length > 0")
                page.wait_for_load_state("networkidle")
            page.evaluate(spec["open"])
            page.wait_for_function(spec["ready"], timeout=30000)
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(1500)                  # chart and fade-in animations
            scroll = page.evaluate(FIT_SCROLL_JS, [spec["blocks"], spec["limit"]])
            page.wait_for_timeout(300)
            c = page.evaluate(CHECK_JS)
            if c["busy"]:
                problems.append(f"{name}: visible loading/empty/error {c['busy']}")
            if c["bad"]:
                problems.append(f"{name}: bad values on screen {sorted(set(c['bad']))}")
            left, right, vw, shown = c["toggle"]
            if not shown or left < 0 or right > vw:
                problems.append(f"{name}: theme toggle clipped {c['toggle']}")
            raw = os.path.join(work, f"{name}-{mode}.png")
            page.screenshot(path=raw)
            print(f"{name}-{mode}: scrolled {scroll}px")
        browser.close()
    if problems:
        raise SystemExit(f"{mode}: " + "; ".join(problems))


def write_outputs(work, mode):
    for name in SHOTS:
        im = Image.open(os.path.join(work, f"{name}-{mode}.png")).convert("RGB")
        assert im.size == (W * DSF, H * DSF), im.size
        base = os.path.join(OUT_DIR, f"{name}-{mode}")
        im.save(base + ".png", optimize=True)
        im.save(base + ".webp", quality=WEBP_Q, method=6)
        for ext in (".webp", ".png"):
            print(f"  {name}-{mode}{ext:6} {im.size[0]}x{im.size[1]}  {os.path.getsize(base + ext) / 1e6:.2f} MB")


def main():
    work = tempfile.mkdtemp(prefix="kodo-profiles-")
    data = os.path.join(work, "data")
    os.makedirs(data)
    for name in EXTRA_FILES:
        if os.path.exists(os.path.join(ROOT, name)):
            shutil.copy2(os.path.join(ROOT, name), data)
    port = free_port()
    server = start_server(data, port, os.path.join(work, "server.log"))
    try:
        for mode in ("light", "dark"):
            capture(f"http://127.0.0.1:{port}", mode, work)
            write_outputs(work, mode)
    finally:
        server.terminate()
        server.wait()
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
