#!/usr/bin/env python3
"""Record the landing page's product tour video (light and dark).

    python3 scripts/record_product_videos.py

Starts its own copy of the app on a free local port: a temporary DATA_DIR
holding the repo's reference data (hotels, performance, pipeline, owners),
a local-only demo account, and no API keys (the Benchmarking AI commentary
is answered by a stored sample).
Nothing is written to the real data files or users, and no real user,
admin page or notification appears on screen.

For each theme it records a guided tour at 1440x900 with deviceScaleFactor
2, frame by frame: 30 fps on a fixed timeline, one lossless 2880x1800 PNG
per frame. Time inside the page is virtual (Playwright's fake clock drives
timers, requestAnimationFrame and Date; CSS transitions are paused and
seeked to the same time), so every frame is exact: nothing dropped, nothing
duplicated, no dependence on machine speed, and every page is fully
rendered before its frame is taken (pending requests are awaited each
frame; a spinner, empty placeholder or error on screen stops the script).

The tour (about 34 s), with an eased cursor and eased scrolling:

    0 s   Benchmarking, comp set loaded: the KPI cards with their period lines
    3 s   period to "Last 90 days": the KPIs and charts update
    7 s   scroll through the calendars to the RevPAR trend, then the monthly
          summary table, and back to the top
    15 s  Owners in the top nav; the owners list loads
    17 s  hover and open the Madaef owner profile
    20 s  header and KPI cards, then down through the hotel portfolio
    27 s  back up, Benchmarking in the top nav, period back to "Last 30
          days", cursor home; the last 0.5 s crossfades into the first frame,
          so the loop is seamless (the last frame is frame 0)

The Benchmarking figures are the page's sample mode (bench_sample.py:
fictional hotels, illustrative figures, dates relative to the recording
day), shown with the page's own "Sample data" pills on the title, every KPI
card and every chart; the owner profile is real platform data.

ffmpeg downscales with lanczos to 2208x1380 and writes:

    static/img/product/video/benchmarking-{light,dark}.mp4          H.264 High, crf 17, yuv420p, faststart
    static/img/product/video/benchmarking-{light,dark}.webm         VP9, crf 24, two-pass
    static/img/product/video/benchmarking-{light,dark}-poster.webp  first frame, WebP q90
    static/img/product/video/benchmarking-{light,dark}-poster.png   first frame, PNG

Quality comes first: a file over 12 MB is re-encoded at 1792x1120 (the
exact-16:10 even size nearest 1800 wide) rather than at a lower quality.

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
W, H, DSF, FPS = 1440, 900, 2, 30          # viewport (CSS px), scale, frame rate
OUT_W, OUT_H = 2208, 1380                  # encoded size: exact 16:10 with even sides (yuv420p),
                                           # just over a 1100px frame at 2x
FALLBACK_W, FALLBACK_H = 1792, 1120        # used if a file comes out over MAX_BYTES (exact 16:10, even sides)
MAX_BYTES = 12_000_000
MP4_CRF, WEBM_CRF, POSTER_Q = 17, 24, 90     # best end of crf 17-19 / 24-28

DEMO_EMAIL, DEMO_PASS, DEMO_NAME = "demo@example.test", "Demo-Local-2026", "Demo Analyst"
SEED_FILES = ("hotels.csv", "performance.csv", "pipeline.csv", "owners.json",
              "news.json", "daily_performance.csv")
# Stand-in for the Benchmarking AI commentary (no live API call): one
# sentence built from the figures the page itself sends with the request,
# so it always matches the KPI cards on screen.
def bench_commentary(route):
    try:
        prompt = route.request.post_data_json["messages"][-1]["content"]
        num = r"([\d.,]+)"
        my = re.search(rf"MY: Occ {num}% \| ADR MAD {num}", prompt)
        comp = re.search(rf"COMP AVG: Occ {num}% \| ADR MAD {num}", prompt)
        name = re.search(r"^(.+?) vs comp set", prompt, re.M)[1].replace("Brief strategic commentary on ", "")
        m_occ, m_adr = float(my[1]), float(my[2].replace(",", ""))
        c_occ, c_adr = float(comp[1]), float(comp[2].replace(",", ""))
        gap = (m_adr - c_adr) / c_adr * 100
        text = (f"In this sample, {name} is priced {abs(gap):.0f}% {'below' if gap < 0 else 'above'} the comp set "
                f"(MAD {m_adr:,.0f} vs MAD {c_adr:,.0f}) while running "
                f"{'almost the same' if abs(m_occ - c_occ) < 1.5 else 'a different'} occupancy "
                f"({m_occ:.1f}% vs {c_occ:.1f}%), so the RevPAR gap is "
                f"{'almost entirely rate' if abs(m_occ - c_occ) < 1.5 else 'rate and occupancy'}.")
    except Exception:
        text = "Rate, not occupancy, drives the RevPAR gap to the comp set over this period."
    route.fulfill(json={"response": text})

PRESS_S, PRESS_SCALE = 0.14, 0.82
XFADE_S = 0.5                              # last-frame-to-first crossfade
REST = (470, 395)                          # cursor home: empty space in the My Property card
SCROLL_REST = (1352, 610)                  # where the cursor waits while Benchmarking scrolls
OWNER_REST = (1180, 185)                   # empty space right of the owner's name
OWNER_ID = "madaef"                        # Madaef: 23 hotels, the most complete owner profile

CURSOR_JS = """
(() => {
  if (document.getElementById('__rec_cursor')) return;
  const c = document.createElement('div');
  c.id = '__rec_cursor';
  c.innerHTML = '<svg width="22" height="22" viewBox="0 0 22 22"><path d="M3 2 L3 18 L7.4 14 L10.4 20.6 L13.2 19.4 L10.3 12.9 L16.4 12.9 Z" fill="#1F1E1C" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  Object.assign(c.style, {position: 'fixed', left: '0', top: '0', width: '22px', height: '22px', zIndex: 2147483647,
    pointerEvents: 'none', transformOrigin: '3px 2px', filter: 'drop-shadow(0 1px 1.5px rgba(0,0,0,.25))'});
  document.body.appendChild(c);
  window.__recSet = (x, y, s) => { c.style.transform = `translate(${x - 3}px, ${y - 2}px) scale(${s})`; };
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
    for name in SEED_FILES:
        src = os.path.join(ROOT, name)
        if os.path.exists(src):
            shutil.copy2(src, data_dir)
    env = dict(os.environ, PORT=str(port), DATA_DIR=data_dir, SEED_ADMIN_EMAIL=DEMO_EMAIL,
               SEED_ADMIN_PASS=DEMO_PASS, SEED_ADMIN_NAME=DEMO_NAME, ANTHROPIC_API_KEY="", RESEND_API_KEY="")
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
        s = PRESS_SCALE if self.i < self.press_until else 1.0
        self.page.evaluate(f"window.__recSet({x:.2f}, {y:.2f}, {s})")
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

    def click(self):
        self.page.mouse.click(*self.pos)
        self.press_until = self.i + round(PRESS_S * FPS)

    def scroll(self, target, sec):
        """Eased scroll of the platform's scroller (.main-content) to target px
        (clamped to the page). The pointer stays still, as with a trackpad."""
        top, maxs = self.page.evaluate("(() => { const m = document.querySelector('.main-content'); return [m.scrollTop, m.scrollHeight - m.clientHeight]; })()")
        target = max(0, min(target, maxs))
        n = round(sec * FPS)
        for k in range(1, n + 1):
            self.page.evaluate(f"document.querySelector('.main-content').scrollTop = {top + (target - top) * ease(k / n):.2f}")
            self.frame()

    # ── helpers ──
    def centre(self, sel):
        r = self.page.locator(sel).first.bounding_box()
        return r["x"] + r["width"] / 2, r["y"] + r["height"] / 2

    def top_of(self, sel, offset=0):
        """Scroll position that puts the element `offset` px below the top of the scroller."""
        return self.page.evaluate("""([sel, off]) => { const m = document.querySelector('.main-content'), e = document.querySelector(sel);
            return e.getBoundingClientRect().top - m.getBoundingClientRect().top + m.scrollTop - off; }""", [sel, offset])

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

BENCH_TAB = '.nav-link[data-screen="benchmarking"]:not(.mobile-menu-link)'
OWNERS_TAB = '.nav-link[data-screen="owners"]:not(.mobile-menu-link)'
OWNER_CARD = f"#owners-grid .owner-card[onclick*=\"'{OWNER_ID}'\"]"


def tour(t):
    """The scripted product tour (times are approximate starts)."""
    p = t.page
    # 0 s: Benchmarking with the comp set loaded; read the KPI cards
    t.hold(3.4)
    # 3.4 s: period to "Last 90 days": the KPI cards and charts update
    t.move('[data-brange="90"]', 1.2); t.click()
    t.hold(1.6)
    t.move(SCROLL_REST, 0.8)
    # 7 s: down through the calendars to the RevPAR trend, then the
    # monthly summary table beside the day-of-week chart, and back up
    t.scroll(t.top_of("#bench-trend-revpar-wrap", 150), 2.6)
    t.hold(1.2)
    t.scroll(t.top_of("#bench-monthly-table", 120), 1.1)
    t.hold(1.3)
    t.scroll(0, 1.8)
    # 15 s: Owners in the top nav; the owners list loads
    t.move(OWNERS_TAB, 1.1); t.click()
    t.hold(0.3)
    t.expect("document.querySelectorAll('#owners-grid .owner-card').length > 0", "owners list")
    t.hold(1.0)
    # 17.5 s: hover the owner's card, open its profile
    t.move(OWNER_CARD, 1.1)
    t.hold(0.7); t.click()
    t.hold(0.3)
    t.expect("getComputedStyle(document.getElementById('screen-owner-detail')).display !== 'none'"
             " && document.querySelectorAll('#owner-portfolio-tbody tr').length > 0", "owner profile")
    # 20 s: header and KPI cards, then down through the hotel portfolio
    t.move(OWNER_REST, 0.8)
    t.hold(1.6)
    t.scroll(10_000, 3.2)
    t.hold(1.6)
    # 27.5 s: back to the top, Benchmarking in the top nav, period back to
    # "Last 30 days", cursor to its starting point: the opening frame again
    t.scroll(0, 1.2)
    t.move(BENCH_TAB, 1.1); t.click()
    t.hold(0.6)
    t.move('[data-brange="30"]', 1.1); t.click()
    t.hold(0.5)
    t.move(REST, 1.0)
    t.hold(XFADE_S + 0.2)


def record(base, mode, frames_dir):
    """Capture the tour; returns the number of frames."""
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=DSF)
        ctx.add_init_script(f"try{{localStorage.setItem('kodo-theme','{mode}')}}catch(e){{}}")
        # Operator logos come from a third-party CDN that refuses localhost:
        # fail them at once so the owner profile shows the text names
        ctx.route("**/cdn.brandfetch.io/**", lambda r: r.abort())
        page = ctx.new_page()
        page.clock.install()               # fake timers; time still flows until paused below
        page.on("console", lambda m: problems.append(m.text)
                if m.type == "error" and "ERR_FAILED" not in m.text and "brandfetch" not in (m.location or {}).get("url", "") else None)
        page.on("pageerror", lambda e: problems.append(str(e)))
        page.route("**/api/chat", bench_commentary)
        t = Tour(page, frames_dir, problems)

        page.goto(base + "/login")
        page.fill("input[type=email]", DEMO_EMAIL)
        page.fill("input[type=password]", DEMO_PASS)
        page.click("button[type=submit]")
        page.wait_for_selector(BENCH_TAB)
        page.wait_for_timeout(2500)
        # Visit Owners once first so its data and logos are cached: the list
        # then appears in the frame after the click, with no spinner
        page.evaluate(f"document.querySelector('{OWNERS_TAB}').click()")
        page.wait_for_selector(OWNER_CARD)
        page.wait_for_load_state("networkidle")
        page.evaluate(f"document.querySelector('{BENCH_TAB}').click()")
        page.wait_for_selector("#bench-kpi-grid .kpi-period")
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
    base = os.path.join(OUT_DIR, f"benchmarking-{mode}")

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

    sizes_used = {}
    for ext, fn in ((".mp4", mp4), (".webm", webm)):
        fn(OUT_W, OUT_H)
        sizes_used[ext] = (OUT_W, OUT_H)
        if os.path.getsize(base + ext) > MAX_BYTES:
            fn(FALLBACK_W, FALLBACK_H)     # resolution goes down before quality does
            sizes_used[ext] = (FALLBACK_W, FALLBACK_H)

    poster_png = base + "-poster.png"
    ffmpeg(*src, "-filter_complex", chain(OUT_W, OUT_H, yuv=False), "-frames:v", "1", poster_png)
    Image.open(poster_png).save(base + "-poster.webp", "WEBP", quality=POSTER_Q, method=6)
    sizes_used["-poster.webp"] = sizes_used["-poster.png"] = (OUT_W, OUT_H)
    return {ext: (os.path.getsize(base + ext), sizes_used[ext]) for ext in sizes_used}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--keep", action="store_true", help="keep the temporary work folder (frames, logs)")
    args = ap.parse_args()
    if not FFMPEG:
        raise SystemExit("ffmpeg not found: install it, or pip install imageio-ffmpeg")
    os.makedirs(OUT_DIR, exist_ok=True)
    work = tempfile.mkdtemp(prefix="kodo-video-")
    data_dir = os.path.join(work, "data")
    os.makedirs(data_dir)
    port = free_port()
    server = start_server(data_dir, port, os.path.join(work, "server.log"))
    try:
        for mode in ("light", "dark"):
            frames_dir = os.path.join(work, f"frames-{mode}")
            os.makedirs(frames_dir)
            n = record(f"http://127.0.0.1:{port}", mode, frames_dir)
            out = encode(frames_dir, mode, work)
            print(f"benchmarking-{mode}: {n} frames, {n / FPS:.2f}s")
            for ext, (size, (w, h)) in out.items():
                rate = f"  {size * 8 / (n / FPS) / 1e6:.1f} Mbit/s" if ext in (".mp4", ".webm") else ""
                print(f"  {ext:13} {w}x{h}  {size / 1e6:.2f} MB{rate}")
    finally:
        server.terminate()
        if args.keep:
            print("work folder:", work)
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
