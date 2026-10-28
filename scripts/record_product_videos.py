#!/usr/bin/env python3
"""Record the landing page's Benchmarking product video (light and dark).

    python3 scripts/record_product_videos.py

Starts its own copy of the app on a free local port with sample data only:
a temporary DATA_DIR holding the repo's reference CSVs and the demo
benchmarking comp set, a local-only demo account, and no API keys (the
Benchmarking AI commentary is answered by a stored sample). Nothing is
written to the real data files or users.

For each theme it opens the Benchmarking screen (Riad Atlas in Marrakech vs
three luxury hotels) at 1440x900 with deviceScaleFactor 2 and captures the
clip frame by frame: 30 fps on a fixed timeline, one lossless 2880x1800 PNG
per frame. Time inside the page is virtual (Playwright's fake clock drives
timers, requestAnimationFrame and Date; CSS transitions are paused and
seeked to the same time), so every frame is exact: nothing dropped, nothing
duplicated, no dependence on machine speed. An eased cursor switches the
period to "Last 90 days" so the KPI cards update, then back to "Last 30
days" and its start position, so the last frame leads straight back into
the first. ffmpeg adds the grey "Sample data" tag, downscales with lanczos
to 2208x1380 and writes:

    static/img/product/video/benchmarking-{light,dark}.mp4          H.264 High, crf 17, yuv420p, faststart
    static/img/product/video/benchmarking-{light,dark}.webm         VP9, crf 24, two-pass
    static/img/product/video/benchmarking-{light,dark}-poster.webp  first frame, WebP q90
    static/img/product/video/benchmarking-{light,dark}-poster.png   first frame, PNG

Quality comes first: a file over 8 MB is re-encoded at 1792x1120 rather
than at a lower quality.

Requires: playwright (with Chromium), Pillow, and ffmpeg with libx264 and
libvpx-vp9: the one on PATH, or else the static build from the
imageio-ffmpeg package (pip install imageio-ffmpeg).
"""
import argparse
import datetime
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "static", "img", "product", "video")
FONT = os.path.join(ROOT, "static", "fonts", "SweetSansProMedium.otf")
W, H, DSF, FPS = 1440, 900, 2, 30          # viewport (CSS px), scale, frame rate
OUT_W, OUT_H = 2208, 1380                  # encoded size: exact 16:10 with even sides (yuv420p),
                                           # just over a 1100px frame at 2x
FALLBACK_W, FALLBACK_H = 1792, 1120        # used if a file comes out over MAX_BYTES
MAX_BYTES = 8_000_000
MP4_CRF, WEBM_CRF, POSTER_Q = 17, 24, 90     # best end of crf 17-19 / 24-28: the clip is mostly static UI, so files stay small

DEMO_EMAIL, DEMO_PASS, DEMO_NAME = "demo@example.test", "Demo-Local-2026", "Demo Analyst"
SEED_FILES = ("hotels.csv", "performance.csv", "pipeline.csv", "owners.json",
              "demo_benchmarking.json", "news.json", "daily_performance.csv")
# Stored answer for the Benchmarking AI commentary (no live API call)
BENCH_COMMENTARY = ("Riad Atlas is priced 10% below the comp set (MAD 5,519 vs MAD 6,138) while running "
                    "almost the same occupancy (84.8% vs 85.2%), so the RevPAR gap is almost entirely rate.")

# Timeline (seconds): hold, glide to "Last 90 days" + click, hold, glide to
# "Last 30 days" + click, hold, glide back to the rest point, hold
HOLD_START, MOVE_1, HOLD_MID, MOVE_2, HOLD_BACK, MOVE_3, HOLD_END = 1.0, 1.4, 2.2, 1.2, 0.6, 1.2, 1.0
DURATION = HOLD_START + MOVE_1 + HOLD_MID + MOVE_2 + HOLD_BACK + MOVE_3 + HOLD_END
FRAMES = round(DURATION * FPS)
PRESS_S, PRESS_SCALE = 0.14, 0.82
REST = (470, 395)                          # cursor rest point: empty space in the My Property card

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


def timeline(p90, p30):
    """Cursor position and scale at time t, plus the timed events."""
    t1 = HOLD_START
    t2 = t1 + MOVE_1                       # arrive on "Last 90 days", click
    t3 = t2 + HOLD_MID
    t4 = t3 + MOVE_2                       # arrive on "Last 30 days", click
    t5 = t4 + HOLD_BACK
    t6 = t5 + MOVE_3                       # back at rest
    legs = [(t1, t2, REST, p90), (t3, t4, p90, p30), (t5, t6, p30, REST)]

    def cursor(t):
        pos = REST
        for a, b, src, dst in legs:
            if t >= b:
                pos = dst
            elif t >= a:
                e = ease((t - a) / (b - a))
                pos = (src[0] + (dst[0] - src[0]) * e, src[1] + (dst[1] - src[1]) * e)
                break
            else:
                break
        pressed = any(c <= t < c + PRESS_S for c in (t2, t4))
        return pos, PRESS_SCALE if pressed else 1.0

    events = [(t2, "click", p90), (t4, "click", p30), (t6, "rest", REST)]
    return cursor, events


def record(base, mode, frames_dir):
    """Capture FRAMES + 1 PNG frames (the extra one is the loop point, used only for checking)."""
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=DSF)
        ctx.add_init_script(f"try{{localStorage.setItem('kodo-theme','{mode}')}}catch(e){{}}")
        page = ctx.new_page()
        page.clock.install()               # fake timers; time still flows until paused below
        page.on("console", lambda m: problems.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: problems.append(str(e)))
        pending = set()
        page.on("request", lambda r: pending.add(r))
        page.on("requestfinished", lambda r: pending.discard(r))
        page.on("requestfailed", lambda r: pending.discard(r))
        page.route("**/api/chat", lambda r: r.fulfill(json={"response": BENCH_COMMENTARY}))

        page.goto(base + "/login")
        page.fill("input[type=email]", DEMO_EMAIL)
        page.fill("input[type=password]", DEMO_PASS)
        page.click("button[type=submit]")
        page.wait_for_selector('.nav-link[data-screen="benchmarking"]')
        page.wait_for_timeout(2500)
        page.evaluate("document.querySelector('.nav-link[data-screen=\"benchmarking\"]').click()")
        page.wait_for_selector(".bench-kpi-grid .kpi-card, .bench-kpi-grid > *")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)        # charts and their entry animations finish
        page.evaluate("document.fonts.ready")
        page.mouse.move(*REST)
        page.evaluate(CURSOR_JS)
        page.evaluate("document.activeElement && document.activeElement.blur()")

        def settle():
            for _ in range(500):
                if not pending:
                    return
                page.wait_for_timeout(10)
            problems.append(f"requests still pending: {[r.url for r in pending]}")

        # Freeze page time; from here it only moves 1/30 s per frame
        now = page.evaluate("Date.now()")
        page.clock.pause_at(datetime.datetime.fromtimestamp((now + 500) / 1000))
        page.clock.run_for(1000)
        settle()
        page.evaluate(SYNC_ANIMATIONS_JS, 0)

        visible = page.evaluate("""() => [...document.querySelectorAll('.bench-loading, .spinner, .loading, .chat-msg-error')]
                                    .filter(e => e.offsetParent).map(e => e.className)""")
        if visible:
            problems.append(f"loading/error visible: {visible}")
        toggle = page.evaluate("(() => { const r = document.getElementById('theme-toggle').getBoundingClientRect(); return [r.left, r.right, r.width]; })()")
        if toggle[0] < 0 or toggle[1] > W or toggle[2] <= 0:
            problems.append(f"theme toggle clipped: {toggle}")

        def centre(sel):
            r = page.locator(sel).bounding_box()
            return r["x"] + r["width"] / 2, r["y"] + r["height"] / 2

        cursor, events = timeline(centre('[data-brange="90"]'), centre('[data-brange="30"]'))
        clock_ms = 0
        for i in range(FRAMES + 1):
            t = i / FPS
            target = round(t * 1000)
            if target > clock_ms:
                page.clock.run_for(target - clock_ms)
                clock_ms = target
            while events and events[0][0] <= t + 1e-9:
                _, kind, xy = events.pop(0)
                page.mouse.move(*xy)
                if kind == "click":
                    page.mouse.click(*xy)
                else:
                    page.evaluate("document.activeElement && document.activeElement.blur()")
            settle()
            page.evaluate(SYNC_ANIMATIONS_JS, target)
            (x, y), s = cursor(t)
            page.evaluate(f"window.__recSet({x:.2f}, {y:.2f}, {s})")
            page.screenshot(path=os.path.join(frames_dir, f"{i:04d}.png"))
        ctx.close()
        browser.close()
    if problems:
        raise SystemExit(f"{mode}: " + "; ".join(problems))
    return check_frames(frames_dir)


def check_frames(frames_dir):
    """Every frame present at full size; the loop point matches frame 0."""
    names = sorted(os.listdir(frames_dir))
    if len(names) != FRAMES + 1:
        raise SystemExit(f"expected {FRAMES + 1} frames, found {len(names)}")
    for n in (names[0], names[len(names) // 2], names[-1]):
        if Image.open(os.path.join(frames_dir, n)).size != (W * DSF, H * DSF):
            raise SystemExit(f"{n} is not {W * DSF}x{H * DSF}")
    first = Image.open(os.path.join(frames_dir, names[0])).convert("RGB")
    loop = Image.open(os.path.join(frames_dir, names[-1])).convert("RGB")
    diff = ImageChops.difference(first, loop)
    if diff.getbbox():
        raise SystemExit(f"loop point differs from frame 0 in {diff.getbbox()} "
                         f"(mean {sum(ImageStat.Stat(diff).mean) / 3:.3f})")
    os.remove(os.path.join(frames_dir, names[-1]))   # the loop point is frame 0 again
    return FRAMES


def tag_png(mode, path):
    """Grey "Sample data" pill (tokens.css grey family), top-right beside the page title, drawn at DSF."""
    tint, text, dot, line = {"light": ((241, 240, 238), (95, 91, 85), (138, 133, 126), (231, 228, 223)),
                             "dark": ((53, 52, 49), (168, 163, 156), (138, 133, 126), (46, 45, 43))}[mode]
    k = DSF
    img = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 12 * k)
    label, track = "SAMPLE DATA", 1.2 * k
    tw = sum(d.textlength(ch, font=f) + track for ch in label)
    pad, h, dd, gap = 11 * k, 26 * k, 5 * k, 6 * k
    w = int(pad * 2 + dd + gap + tw)
    x1, y0 = (W - 30) * k, 76 * k
    x0, y1 = x1 - w, y0 + h
    d.rounded_rectangle((x0, y0, x1, y1), radius=h // 2, fill=tint, outline=line, width=k)
    cy = (y0 + y1) / 2
    d.ellipse((x0 + pad, cy - dd / 2, x0 + pad + dd, cy + dd / 2), fill=dot)
    x = x0 + pad + dd + gap
    for ch in label:
        d.text((x, cy), ch, font=f, fill=text, anchor="lm")
        x += d.textlength(ch, font=f) + track
    img.save(path)


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
    tag = os.path.join(work, f"tag-{mode}.png")
    tag_png(mode, tag)
    src = ["-framerate", str(FPS), "-i", os.path.join(frames_dir, "%04d.png"), "-i", tag]
    base = os.path.join(OUT_DIR, f"benchmarking-{mode}")

    def chain(w, h, yuv=True):
        # tag on the 2880x1800 frames, then lanczos down; BT.709 for the video files
        f = f"[0:v][1:v]overlay=0:0,scale={w}:{h}:flags=lanczos+accurate_rnd+full_chroma_int"
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
