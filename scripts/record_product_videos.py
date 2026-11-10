#!/usr/bin/env python3
"""Record the landing page's product tour video (light and dark).

    python3 scripts/record_product_videos.py

Starts its own copy of the app on a free local port: a temporary DATA_DIR
holding only fictional sample data (sample_profiles.py: 31 fictional hotels,
three fictional brand groups and three fictional owners, a week of fictional
published prices and the platform's own occupancy model run on them), a
local-only demo account, no API keys and no data migrations. Nothing is
written to the real data files or users, and no real hotel, owner, user,
admin page or notification appears on screen. The events calendar is the
platform's own public calendar (festivals, holidays, school breaks).

For each theme it records a guided tour at 1440x900 with deviceScaleFactor
2, frame by frame: 30 fps on a fixed timeline, one lossless 2880x1800 PNG
per frame. Time inside the page is virtual (Playwright's fake clock drives
timers, requestAnimationFrame and Date; CSS transitions are paused and
seeked to the same time), so every frame is exact: nothing dropped, nothing
duplicated, no dependence on machine speed, and every page is fully
rendered before its frame is taken (pending requests are awaited each
frame; a spinner, empty placeholder or error on screen stops the script).
Loading never shows, so there are no dead moments to speed up afterwards:
the pace is set by the holds below, each long enough to read the figure
it is on.

The pointer is drawn in the page: a solid action-blue dot with a white
edge and a soft translucent ring (visible on light and dark), gliding on
an eased path, with a ripple on every click.

The tour (about 50 s):

    0 s   Dashboard: market KPI cards, then the RevPAR by destination chart
    5 s   Hotels: the Marrakech filter, then Palais Ocre
    9 s   Hotel profile: published rate calendar and modelled occupancy
          calendar, with a night's tooltip on each
    16 s  Map: the Marrakech dot and its hotel list
    21 s  Benchmarking: Palais Ocre against a comp set of six, the KPI
          cards, the published rate and modelled occupancy calendars
    29 s  Tourism (menu): the events calendar
    34 s  Brands
    38 s  Owners: the Ocre Sample Holdings profile and its portfolio
    44 s  Valuation tool: Marrakech, Luxury, Run Valuation
    50 s  back to the Dashboard, cursor home; the last 0.5 s crossfades
          into the first frame, so the loop is seamless (the last frame is
          frame 0)

The AI Analyst is left out: it needs a live API key, and the video shows
only what the platform really produces from the sample data.

ffmpeg downscales with lanczos to 1728x1080 (1080p, exact 16:10) and writes:

    static/img/product/video/product-tour-{light,dark}.mp4          H.264 High, yuv420p, faststart
    static/img/product/video/product-tour-{light,dark}.webm         VP9, two-pass
    static/img/product/video/product-tour-{light,dark}-poster.webp  first frame, WebP
    static/img/product/video/product-tour-{light,dark}-poster.png   first frame, PNG

No audio track.

Requires: playwright (with Chromium), Pillow, and ffmpeg with libx264 and
libvpx-vp9: the one on PATH, or else the static build from the
imageio-ffmpeg package (pip install imageio-ffmpeg).
"""
import argparse
import datetime
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "static", "img", "product", "video")
NAME = "product-tour"
W, H, DSF, FPS = 1440, 900, 2, 30          # viewport (CSS px), scale, frame rate
OUT_W, OUT_H = 1728, 1080                  # encoded size: 1080p, exact 16:10, even sides (yuv420p)
MP4_CRF, WEBM_CRF, POSTER_Q = 20, 31, 88

DEMO_EMAIL, DEMO_PASS, DEMO_NAME = "demo@example.test", "Demo-Local-2026", "Demo Analyst"
SEED_FILES = ("hotels.csv", "performance.csv", "pipeline.csv", "owners.json",
              "news.json", "daily_performance.csv")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sample_profiles  # noqa: E402

SUBJECT_ID = str(sample_profiles.PROFILE_HOTEL_ID)                    # Palais Ocre
COMP_IDS = ["9007", "9002", "9003", "9004", "9009", "9010"]          # six Marrakech hotels
OWNER_ID = sample_profiles.OWNER["id"]                                # Ocre Sample Holdings

PRESS_S = 0.14                             # dot pressed (scaled down) after a click
RIPPLE_S = 0.45                            # click ripple
XFADE_S = 0.5                              # last-frame-to-first crossfade
REST = (1010, 98)                          # cursor home: empty space right of the Dashboard title

CURSOR_JS = """
(() => {
  if (document.getElementById('__rec_cursor')) return;
  const c = document.createElement('div');
  c.id = '__rec_cursor';
  Object.assign(c.style, {position: 'fixed', left: '0', top: '0', width: '0', height: '0',
    zIndex: 2147483647, pointerEvents: 'none'});
  const part = (size, css) => { const e = document.createElement('div');
    Object.assign(e.style, {position: 'absolute', left: -size / 2 + 'px', top: -size / 2 + 'px',
      width: size + 'px', height: size + 'px', borderRadius: '50%', boxSizing: 'border-box'}, css);
    c.appendChild(e); return e; };
  // soft translucent ring, click ripple, then the solid dot with a white edge
  // ring outline at 55% so it still reads on the pure black dark-mode page
  const ring = part(40, {background: 'rgba(0, 117, 222, 0.18)', border: '1.5px solid rgba(0, 117, 222, 0.55)'});
  const rip = part(20, {border: '2px solid #0075DE', opacity: '0'});
  const dot = part(20, {background: '#0075DE', border: '2px solid #FFFFFF',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.35)'});
  document.body.appendChild(c);
  window.__recSet = (x, y, s, r) => {
    c.style.transform = `translate(${x}px, ${y}px)`;
    dot.style.transform = ring.style.transform = `scale(${s})`;
    rip.style.opacity = r < 0 ? '0' : String(0.85 * (1 - r));
    rip.style.transform = `scale(${1 + 2.2 * r})`;
  };
})();
"""

# Pause every CSS transition / animation the first time it is seen and seek
# it to the virtual time since then, so it advances exactly 1/30 s per frame.
SYNC_ANIMATIONS_JS = """
(vt) => {
  for (const a of document.getAnimations()) {
    if (a.__recStart === undefined) { a.__recStart = vt; a.pause(); }
    const t = vt - a.__recStart;
    const end = a.effect ? a.effect.getComputedTiming().endTime : Infinity;
    if (Number.isFinite(end) && t >= end) a.finish(); else a.currentTime = t;
  }
}
"""


def ease(t):
    """easeInOutCubic, the same curve as the old in-page cursor."""
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_server(data_dir, port, log_path):
    for name in SEED_FILES:                      # files already in data_dir (sample data) are kept
        src = os.path.join(ROOT, name)
        if os.path.exists(src) and not os.path.exists(os.path.join(data_dir, name)):
            shutil.copy2(src, data_dir)
    env = dict(os.environ, PORT=str(port), DATA_DIR=data_dir, SEED_ADMIN_EMAIL=DEMO_EMAIL,
               SEED_ADMIN_PASS=DEMO_PASS, SEED_ADMIN_NAME=DEMO_NAME, ANTHROPIC_API_KEY="", RESEND_API_KEY="",
               DATA_MIGRATIONS="off")       # the sample data is complete as written
    proc = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env,
                            stdout=open(log_path, "w"), stderr=subprocess.STDOUT)
    for _ in range(60):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/login", timeout=1)
            return proc
        except Exception:
            time.sleep(0.5)
    proc.kill()
    raise SystemExit(f"app did not start, see {log_path}")


class Tour:
    """Frame-by-frame recorder for one theme: every step below advances page
    time by whole frames (1/30 s) and captures each one."""

    def __init__(self, page, frames_dir, problems):
        self.page, self.dir, self.problems = page, frames_dir, problems
        self.i = 0                         # next frame index
        self.clock_ms = 0
        self.pos = REST                    # drawn cursor (and real mouse) position
        self.press_until = -1
        self.click_at = None               # frame of the last click (ripple)
        self.pending = set()
        page.on("request", lambda r: self.pending.add(r))
        page.on("requestfinished", lambda r: self.pending.discard(r))
        page.on("requestfailed", lambda r: self.pending.discard(r))

    # ── one frame ──
    def settle(self):
        for _ in range(1000):
            if not self.pending:
                return
            self.page.wait_for_timeout(10)
        self.problems.append(f"requests still pending: {[r.url for r in self.pending]}")

    def frame(self):
        target = round(self.i / FPS * 1000)
        if target > self.clock_ms:
            self.page.clock.run_for(target - self.clock_ms)
            self.clock_ms = target
        self.settle()
        self.page.evaluate(SYNC_ANIMATIONS_JS, target)
        busy = self.page.evaluate(BUSY_JS)
        if busy:
            self.problems.append(f"frame {self.i}: loading/error on screen {busy}")
        x, y = self.pos
        s = 0.82 if self.i < self.press_until else 1.0
        r = -1 if self.click_at is None else (self.i - self.click_at) / (RIPPLE_S * FPS)
        self.page.evaluate(f"window.__recSet({x:.2f}, {y:.2f}, {s}, {r if 0 <= r < 1 else -1:.3f})")
        self.page.screenshot(path=os.path.join(self.dir, f"{self.i:04d}.png"))
        self.i += 1

    # ── steps ──
    def hold(self, sec):
        for _ in range(round(sec * FPS)):
            self.frame()

    def move(self, target, sec):
        """Eased glide to target (x, y) or a CSS selector's centre. The real
        mouse follows, so hover states match the drawn cursor."""
        if isinstance(target, str):
            target = self.centre(target)
        src, n = self.pos, round(sec * FPS)
        for k in range(1, n + 1):
            e = ease(k / n)
            self.pos = (src[0] + (target[0] - src[0]) * e, src[1] + (target[1] - src[1]) * e)
            self.page.mouse.move(*self.pos)
            self.frame()

    def click(self, real=True):
        """Click where the cursor is (real=False: only the press and ripple,
        for a native select whose value is then set directly)."""
        if real:
            self.page.mouse.click(*self.pos)
        self.press_until = self.i + round(PRESS_S * FPS)
        self.click_at = self.i

    def go(self, target, sec=0.6, hold=0.0):
        """Glide to target and click it."""
        self.move(target, sec)
        self.click()
        self.hold(hold)

    def scroll(self, target, sec, scroller=".main-content"):
        """Eased scroll of a scroller (the platform's .main-content by default)
        to target px (clamped). The pointer stays still, as with a trackpad."""
        top, maxs = self.page.evaluate("(s) => { const m = document.querySelector(s); return [m.scrollTop, m.scrollHeight - m.clientHeight]; }", scroller)
        target = max(0, min(target, maxs))
        n = round(sec * FPS)
        for k in range(1, n + 1):
            self.page.evaluate("([s, y]) => { document.querySelector(s).scrollTop = y; }",
                               [scroller, round(top + (target - top) * ease(k / n), 2)])
            self.frame()

    # ── helpers ──
    def centre(self, sel):
        r = self.page.locator(sel).first.bounding_box()
        return r["x"] + r["width"] / 2, r["y"] + r["height"] / 2

    def map_dot(self, city):
        """Screen position of a city's dot on the Map, from the map's own
        projection (the overlay added before recording, MAP_OVERLAY_JS)."""
        return tuple(self.page.evaluate("""(city) => {
            const e = hotelMarkers.find(x => x.city === city);
            const pt = window.__recOverlay.getProjection().fromLatLngToContainerPixel(e.marker.getPosition());
            const r = document.getElementById('map-container').getBoundingClientRect();
            return [r.left + pt.x, r.top + pt.y]; }""", city))

    def top_of(self, sel, offset=0):
        """Scroll position that puts the element `offset` px below the top of the scroller."""
        return self.page.evaluate("""([sel, off]) => { const m = document.querySelector('.main-content'), e = document.querySelector(sel);
            return e.getBoundingClientRect().top - m.getBoundingClientRect().top + m.scrollTop - off; }""", [sel, offset])

    def ready(self, js, what):
        """Before the next frame: wait (real time, page clock still) until the
        page has rendered what a click asked for, e.g. a profile's fetched data."""
        try:
            self.page.wait_for_function(js, timeout=10000)
        except Exception:
            self.problems.append(f"frame {self.i}: {what} not rendered")

    def expect(self, js, what):
        if not self.page.evaluate(js):
            self.problems.append(f"frame {self.i}: {what} not rendered")


# Loading spinners, empty "will appear" placeholders and error states that
# are inside the visible part of the page
BUSY_JS = """
() => [...document.querySelectorAll('.kodo-loader, .bench-loading, .spinner, .chat-msg-error, .toast, .error-banner')]
  .filter(e => { if (!e.offsetParent) return false; const r = e.getBoundingClientRect();
                 return r.bottom > 48 && r.top < innerHeight && r.width > 0; })
  .map(e => e.className)
"""

# An empty overlay on the Map, only for its projection (lat/lng to pixels)
MAP_OVERLAY_JS = """
() => new Promise(done => {
  const o = new google.maps.OverlayView();
  o.onAdd = () => {}; o.onRemove = () => {};
  o.draw = () => { window.__recOverlay = o; done(); };
  o.setMap(googleMap);
})
"""


def tab(screen):
    return f'.nav-link[data-screen="{screen}"]:not(.mobile-menu-link)'


OWNER_CARD = f"#owners-grid .owner-card[onclick*=\"'{OWNER_ID}'\"]"
HOTEL_ROW = f'#hotels-table tbody tr[onclick="showHotelDetail({SUBJECT_ID})"]'
CITY = "Marrakech"


def tour(t):
    """The scripted product tour (times are approximate starts)."""
    p = t.page
    # 0 s: Dashboard, the market KPI cards, then RevPAR by destination
    t.hold(2.2)
    t.scroll(t.top_of("#chart-revpar", 150), 0.7)
    t.hold(1.3)
    # 4 s: Hotels, filtered to Marrakech, then Palais Ocre
    t.go(tab("hotels"), 0.7, 0.5)
    t.go(f'#hotels-city-pills .pill[data-hcity="{CITY}"]', 0.6, 0.9)
    t.go(HOTEL_ROW, 0.6)
    t.ready("document.querySelectorAll('#hrate-calendar .bar-cal-day').length === 30"
             " && document.querySelectorAll('#hocc-calendar .bar-cal-day').length === 30", "hotel calendars")
    t.hold(0.2)
    # 9 s: hotel profile: KPI cards, a night on each calendar (tooltips)
    t.move((1180, 120), 0.5)
    t.hold(1.0)
    t.move("#hrate-calendar .bar-cal-day:nth-child(17)", 0.6)
    t.hold(1.5)
    t.move("#hocc-calendar .bar-cal-day:nth-child(17)", 0.6)
    t.hold(1.5)
    # 15 s: Map, the Marrakech dot and its hotels
    t.go(tab("map"), 0.7, 0.6)
    t.go(t.map_dot(CITY), 0.6, 0.2)
    t.expect("!!document.getElementById('map-city-panel')", "city panel")
    t.move((900, 150), 0.5)
    t.hold(1.4)
    # 20 s: Benchmarking: Palais Ocre against its comp set
    t.go(tab("benchmarking"), 0.7, 0.2)
    t.expect("document.querySelectorAll('#rb-rate-grid .bench-cal-day, #rb-rate-grid [class*=cal]').length > 0", "rate calendar")
    t.move((1180, 150), 0.5)
    t.hold(1.8)
    t.scroll(t.top_of("#rb-rate-grid", 130), 0.8)
    t.hold(1.3)
    t.scroll(t.top_of("#rb-occ-grid", 330), 0.7)      # the calendar, not the AI insights box below
    t.hold(1.0)
    # 29 s: the events calendar (Tourism, from the menu)
    t.go("#mobileMenuBtn", 0.6, 0.35)
    t.go('.mobile-menu-link[data-screen="tourism"]', 0.5, 0.2)
    t.scroll(t.top_of("#evcal", 70), 0.9)
    t.move((1200, 560), 0.5)
    t.hold(1.6)
    # 34 s: Brands
    t.go(tab("brands"), 0.7, 1.6)
    t.scroll(330, 0.6)
    t.hold(0.7)
    # 38 s: Owners: Ocre Sample Holdings
    t.go(tab("owners"), 0.7, 0.5)
    t.go(OWNER_CARD, 0.6)
    t.ready("getComputedStyle(document.getElementById('screen-owner-detail')).display !== 'none'"
             " && document.querySelectorAll('#owner-portfolio-tbody tr').length > 0", "owner profile")
    t.hold(0.2)
    t.move((1180, 190), 0.5)
    t.hold(1.6)
    t.scroll(t.top_of("#owner-portfolio-title", 300), 0.7)
    t.hold(1.0)
    # 44 s: Valuation tool: Marrakech, Luxury, run
    t.go(tab("valuation"), 0.7, 0.4)
    for sel, value in (("#val-p-city", CITY), ("#val-p-segment", "Luxury")):
        t.move(sel, 0.5)
        t.click(real=False)
        p.select_option(sel, value)
        t.hold(0.35)
    # the Run button to just above the page footer, then click it
    t.scroll(p.evaluate("""(() => { const pn = document.getElementById('val-input-panel');
        return pn.scrollTop + document.getElementById('val-run-btn').getBoundingClientRect().top - 740; })()"""),
             0.6, "#val-input-panel")
    t.go("#val-run-btn", 0.5)
    t.ready("getComputedStyle(document.getElementById('val-results')).display !== 'none'", "valuation results")
    t.hold(0.1)
    p.evaluate("document.getElementById('val-output-panel').scrollTop = 0")   # results from the top
    t.hold(0.1)
    t.move((900, 300), 0.5)
    t.hold(2.2)
    # 50 s: back to the Dashboard, cursor home: the opening frame again
    t.go(tab("dashboard"), 0.7, 0.4)
    t.move(REST, 0.6)
    t.hold(XFADE_S + 0.3)


def record(base, mode, frames_dir):
    """Capture the tour; returns the number of frames."""
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=DSF)
        ctx.add_init_script(f"try{{localStorage.setItem('kodo-theme','{mode}')}}catch(e){{}}")
        ctx.route("**/cdn.brandfetch.io/**", lambda r: r.abort())   # no third-party logos
        page = ctx.new_page()
        page.clock.install()               # fake timers; time still flows until paused below
        page.on("console", lambda m: problems.append(m.text)
                if m.type == "error" and "api/chat" not in (m.location or {}).get("url", "")
                and "SERVICE UNAVAILABLE" not in m.text else None)
        page.on("pageerror", lambda e: problems.append(str(e)))
        # No AI key here: answer the Benchmarking insights request at once
        # (the tour stops above that panel)
        page.route("**/api/chat", lambda r: r.fulfill(status=503, json={"error": "AI is not configured"}))
        t = Tour(page, frames_dir, problems)

        page.goto(base + "/login")
        page.fill("input[type=email]", DEMO_EMAIL)
        page.fill("input[type=password]", DEMO_PASS)
        page.click("button[type=submit]")
        page.wait_for_url("**/dashboard")
        page.wait_for_load_state("networkidle")
        status = page.evaluate("""(b) => fetch('/api/benchmarking/compset', {method: 'POST',
            headers: {'Content-Type': 'application/json'}, body: JSON.stringify(b)}).then(r => r.status)""",
                               {"subject_id": SUBJECT_ID, "comp_ids": COMP_IDS})
        if status != 200:
            raise SystemExit(f"comp set not saved: HTTP {status}")
        # Visit every screen once so its data, map tiles and charts are
        # loaded: each then appears in the frame after its click
        for screen in ("map", "hotels", "benchmarking", "tourism", "brands", "owners", "valuation", "dashboard"):
            page.evaluate(f"document.querySelector('.nav-link[data-screen=\"{screen}\"]').click()")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)
            if screen == "map":
                page.evaluate(MAP_OVERLAY_JS)
        page.evaluate("showHotelDetail(%s)" % SUBJECT_ID)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        page.evaluate(f"document.querySelector('{tab('dashboard')}').click()")
        page.evaluate("document.querySelector('.main-content').scrollTop = 0")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)        # charts and their entry animations finish
        page.evaluate("document.fonts.ready")
        page.mouse.move(*REST)
        page.evaluate(CURSOR_JS)
        page.evaluate("document.activeElement && document.activeElement.blur()")

        # Freeze page time; from here it only moves 1/30 s per frame
        now = page.evaluate("Date.now()")
        page.clock.pause_at(datetime.datetime.fromtimestamp((now + 500) / 1000))
        page.clock.run_for(1000)
        t.settle()
        page.evaluate(SYNC_ANIMATIONS_JS, 0)
        toggle = page.evaluate("(() => { const r = document.getElementById('theme-toggle').getBoundingClientRect(); return [r.left, r.right, r.width]; })()")
        if toggle[0] < 0 or toggle[1] > W or toggle[2] <= 0:
            problems.append(f"theme toggle clipped: {toggle}")

        tour(t)
        ctx.close()
        browser.close()
    if problems:
        raise SystemExit(f"{mode}: " + "; ".join(problems[:12]))
    return crossfade(frames_dir, t.i)


def crossfade(frames_dir, n):
    """Blend the last XFADE_S seconds into frame 0, so the loop is seamless:
    the last frame is frame 0 itself. Returns the frame count."""
    names = sorted(os.listdir(frames_dir))
    if len(names) != n:
        raise SystemExit(f"expected {n} frames, found {len(names)}")
    for nm in (names[0], names[n // 2], names[-1]):
        if Image.open(os.path.join(frames_dir, nm)).size != (W * DSF, H * DSF):
            raise SystemExit(f"{nm} is not {W * DSF}x{H * DSF}")
    first = Image.open(os.path.join(frames_dir, names[0])).convert("RGB")
    end = Image.open(os.path.join(frames_dir, names[-1])).convert("RGB")
    diff = ImageChops.difference(first, end)
    print(f"  end state vs frame 0 before the crossfade: mean difference "
          f"{sum(ImageStat.Stat(diff).mean) / 3:.3f}/255, box {diff.getbbox()}")
    k = round(XFADE_S * FPS)
    for j in range(1, k + 1):
        path = os.path.join(frames_dir, names[n - k - 1 + j])
        Image.blend(Image.open(path).convert("RGB"), first, j / k).save(path, compress_level=1)
    if ImageChops.difference(first, Image.open(os.path.join(frames_dir, names[-1])).convert("RGB")).getbbox():
        raise SystemExit("last frame does not match frame 0 after the crossfade")
    return n


def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


FFMPEG = find_ffmpeg()


def ffmpeg(*args, cwd=None):
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", *args], check=True, cwd=cwd)


def encode(frames_dir, mode, work):
    src = ["-framerate", str(FPS), "-i", os.path.join(frames_dir, "%04d.png")]
    base = os.path.join(OUT_DIR, f"{NAME}-{mode}")

    def chain(w, h, yuv=True):
        # lanczos down from the 2880x1800 frames; BT.709 for the video files
        f = f"[0:v]scale={w}:{h}:flags=lanczos+accurate_rnd+full_chroma_int"
        return f + (":out_color_matrix=bt709:out_range=tv,format=yuv420p" if yuv else ",format=rgb24")

    color = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]

    def mp4(w, h):
        ffmpeg(*src, "-filter_complex", chain(w, h), "-an", "-c:v", "libx264", "-profile:v", "high",
               "-preset", "slow", "-crf", str(MP4_CRF), "-pix_fmt", "yuv420p", "-r", str(FPS), *color,
               "-movflags", "+faststart", base + ".mp4")

    def webm(w, h):
        common = [*src, "-filter_complex", chain(w, h), "-an", "-c:v", "libvpx-vp9", "-b:v", "0",
                  "-crf", str(WEBM_CRF), "-pix_fmt", "yuv420p", "-row-mt", "1", "-r", str(FPS), *color,
                  "-passlogfile", os.path.join(work, f"vp9-{mode}")]
        ffmpeg(*common, "-pass", "1", "-deadline", "good", "-cpu-used", "4", "-f", "null", os.devnull)
        ffmpeg(*common, "-pass", "2", "-deadline", "good", "-cpu-used", "1", "-auto-alt-ref", "1",
               "-lag-in-frames", "25", base + ".webm")

    mp4(OUT_W, OUT_H)
    webm(OUT_W, OUT_H)
    poster_png = base + "-poster.png"
    ffmpeg(*src, "-filter_complex", chain(OUT_W, OUT_H, yuv=False), "-frames:v", "1", poster_png)
    Image.open(poster_png).save(base + "-poster.webp", "WEBP", quality=POSTER_Q, method=6)
    return {ext: os.path.getsize(base + ext) for ext in (".mp4", ".webm", "-poster.webp", "-poster.png")}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--keep", action="store_true", help="keep the temporary work folder (frames, logs)")
    ap.add_argument("--modes", default="light,dark", help="themes to record (default: light,dark)")
    args = ap.parse_args()
    if not FFMPEG:
        raise SystemExit("ffmpeg not found: install it, or pip install imageio-ffmpeg")
    os.makedirs(OUT_DIR, exist_ok=True)
    work = tempfile.mkdtemp(prefix="kodo-video-")
    data_dir = os.path.join(work, "data")
    os.makedirs(data_dir)
    sample_profiles.build(data_dir)
    port = free_port()
    server = start_server(data_dir, port, os.path.join(work, "server.log"))
    try:
        for mode in args.modes.split(","):
            frames_dir = os.path.join(work, f"frames-{mode}")
            os.makedirs(frames_dir)
            n = record(f"http://127.0.0.1:{port}", mode, frames_dir)
            out = encode(frames_dir, mode, work)
            print(f"{NAME}-{mode}: {n} frames, {n / FPS:.2f}s, {OUT_W}x{OUT_H}")
            for ext, size in out.items():
                rate = f"  {size * 8 / (n / FPS) / 1e6:.1f} Mbit/s" if ext in (".mp4", ".webm") else ""
                print(f"  {ext:13} {size / 1e6:.2f} MB{rate}")
    finally:
        server.terminate()
        if args.keep:
            print("work folder:", work)
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
