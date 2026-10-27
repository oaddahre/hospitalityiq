#!/usr/bin/env python3
"""Record the landing page's Benchmarking product video (light and dark).

    python3 scripts/record_product_videos.py

Starts its own copy of the app on a free local port with sample data only:
a temporary DATA_DIR holding the repo's reference CSVs and the demo
benchmarking comp set, a local-only demo account, and no API keys (the
Benchmarking AI commentary is answered by a stored sample). Nothing is
written to the real data files or users.

For each theme it records the Benchmarking screen at 1280x800 with
Playwright's video recorder: the filled view (Riad Atlas in Marrakech vs
three luxury hotels), an eased cursor that switches the period to "Last 90
days" so the KPI cards update, then back to "Last 30 days" and the start
position, so the clip loops cleanly. ffmpeg then trims it, adds a grey
"Sample data" tag, and writes:

    static/img/product/video/benchmarking-{light,dark}.mp4          H.264, yuv420p, faststart
    static/img/product/video/benchmarking-{light,dark}.webm         VP9
    static/img/product/video/benchmarking-{light,dark}-poster.webp  first frame

Requires: playwright (with Chromium), Pillow, and ffmpeg with libx264 and
libvpx-vp9: the one on PATH, or else the static build from the
imageio-ffmpeg package (pip install imageio-ffmpeg).
"""
import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "static", "img", "product", "video")
FONT = os.path.join(ROOT, "static", "fonts", "SweetSansProMedium.otf")
W, H, FPS = 1280, 800, 30
MAX_BYTES = 1_200_000

DEMO_EMAIL, DEMO_PASS, DEMO_NAME = "demo@example.test", "Demo-Local-2026", "Demo Analyst"
SEED_FILES = ("hotels.csv", "performance.csv", "pipeline.csv", "owners.json",
              "demo_benchmarking.json", "news.json", "daily_performance.csv")
# Stored answer for the Benchmarking AI commentary (no live API call)
BENCH_COMMENTARY = ("Riad Atlas is priced 10% below the comp set (MAD 5,519 vs MAD 6,138) while running "
                    "almost the same occupancy (84.8% vs 85.2%), so the RevPAR gap is almost entirely rate.")

# Timeline (seconds from the start of the clip)
HOLD_START, MOVE_1, HOLD_MID, MOVE_2, HOLD_BACK, MOVE_3, HOLD_END = 1.0, 1.4, 2.2, 1.2, 0.6, 1.2, 1.0
REST = (980, 455)                      # cursor rest point, over empty space beside the comp set

CURSOR_JS = """
(() => {
  if (document.getElementById('__rec_cursor')) return;
  const c = document.createElement('div');
  c.id = '__rec_cursor';
  c.innerHTML = '<svg width="22" height="22" viewBox="0 0 22 22"><path d="M3 2 L3 18 L7.4 14 L10.4 20.6 L13.2 19.4 L10.3 12.9 L16.4 12.9 Z" fill="#1F1E1C" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  Object.assign(c.style, {position: 'fixed', left: '0', top: '0', width: '22px', height: '22px', zIndex: 2147483647,
    pointerEvents: 'none', transformOrigin: '3px 2px', filter: 'drop-shadow(0 1px 1.5px rgba(0,0,0,.25))'});
  document.body.appendChild(c);
  let x = %d, y = %d, s = 1;
  const draw = () => { c.style.transform = `translate(${x - 3}px, ${y - 2}px) scale(${s})`; };
  draw();
  const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  window.__recMove = (tx, ty, ms) => new Promise(res => {
    const x0 = x, y0 = y, t0 = performance.now();
    const step = now => { const t = Math.min(1, (now - t0) / ms), e = ease(t);
      x = x0 + (tx - x0) * e; y = y0 + (ty - y0) * e; draw();
      t < 1 ? requestAnimationFrame(step) : res(); };
    requestAnimationFrame(step);
  });
  window.__recPress = () => new Promise(res => { s = 0.82; draw(); setTimeout(() => { s = 1; draw(); res(); }, 140); });
})();
""" % REST


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


def record(base, mode, work):
    """Record one theme; return (raw video path, clip start offset in seconds)."""
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Log in and open Benchmarking in an unrecorded context first, so the
        # recording starts on the finished view
        ctx = browser.new_context(viewport={"width": W, "height": H}, record_video_dir=work,
                                  record_video_size={"width": W, "height": H})
        ctx.add_init_script(f"try{{localStorage.setItem('kodo-theme','{mode}')}}catch(e){{}}")
        page = ctx.new_page()
        page_born = time.monotonic()
        page.on("console", lambda m: problems.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: problems.append(str(e)))
        page.route("**/api/chat", lambda r: r.fulfill(json={"response": BENCH_COMMENTARY}))
        page.goto(base + "/login")
        page.fill("input[type=email]", DEMO_EMAIL)
        page.fill("input[type=password]", DEMO_PASS)
        page.click("button[type=submit]")
        page.wait_for_selector('.nav-link[data-screen="benchmarking"]')
        page.wait_for_timeout(2500)
        page.evaluate("document.querySelector('.nav-link[data-screen=\"benchmarking\"]').click()")
        page.wait_for_selector(".bench-kpi-grid .kpi-card, .bench-kpi-grid > *")
        page.wait_for_timeout(3000)
        page.evaluate("document.fonts.ready")
        page.mouse.move(*REST)
        page.evaluate(CURSOR_JS)
        visible = page.evaluate("""() => [...document.querySelectorAll('.bench-loading, .spinner, .loading, .chat-msg-error')]
                                    .filter(e => e.offsetParent).map(e => e.className)""")
        if visible:
            problems.append(f"loading/error visible: {visible}")
        toggle = page.evaluate("(() => { const r = document.getElementById('theme-toggle').getBoundingClientRect(); return [r.left, r.right]; })()")
        if toggle[0] < 0 or toggle[1] > W:
            problems.append(f"theme toggle clipped: {toggle}")

        def centre(sel):
            r = page.locator(sel).bounding_box()
            return r["x"] + r["width"] / 2, r["y"] + r["height"] / 2

        def move(xy, secs):
            # the overlay glides (eased, in-page); the real pointer follows on arrival for hover states
            page.evaluate(f"window.__recMove({xy[0]}, {xy[1]}, {int(secs * 1000)})")
            page.mouse.move(*xy)

        def click(xy):
            page.evaluate("window.__recPress()")
            page.mouse.click(*xy)

        p90, p30 = centre('[data-brange="90"]'), centre('[data-brange="30"]')
        page.wait_for_timeout(400)
        t_start = time.monotonic() - page_born
        page.wait_for_timeout(HOLD_START * 1000)
        move(p90, MOVE_1); click(p90)
        page.wait_for_timeout(HOLD_MID * 1000)
        move(p30, MOVE_2); click(p30)
        page.wait_for_timeout(HOLD_BACK * 1000)
        move(REST, MOVE_3)
        page.evaluate("document.activeElement && document.activeElement.blur()")
        page.wait_for_timeout(HOLD_END * 1000 + 600)
        video = page.video.path()
        ctx.close()
        browser.close()
    if problems:
        raise SystemExit(f"{mode}: " + "; ".join(problems))
    return video, t_start


def tag_png(mode, path):
    """Grey "Sample data" pill (tokens.css grey family), placed top-right beside the page title."""
    tint, text, dot, line = {"light": ((241, 240, 238), (95, 91, 85), (138, 133, 126), (231, 228, 223)),
                             "dark": ((53, 52, 49), (168, 163, 156), (138, 133, 126), (46, 45, 43))}[mode]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 12)
    label, track = "SAMPLE DATA", 1.2
    tw = sum(d.textlength(ch, font=f) + track for ch in label)
    pad, h, dd, gap = 11, 26, 5, 6
    w = int(pad * 2 + dd + gap + tw)
    x1, y0 = W - 30, 80
    x0, y1 = x1 - w, y0 + h
    d.rounded_rectangle((x0, y0, x1, y1), radius=h // 2, fill=tint, outline=line, width=1)
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


def ffmpeg(*args):
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def encode(raw, start, mode, work):
    dur = HOLD_START + MOVE_1 + HOLD_MID + MOVE_2 + HOLD_BACK + MOVE_3 + HOLD_END
    tag = os.path.join(work, f"tag-{mode}.png")
    tag_png(mode, tag)
    # Lossless intermediate: trimmed, 30 fps, tag overlaid
    master = os.path.join(work, f"master-{mode}.mkv")
    ffmpeg("-ss", f"{start:.3f}", "-i", raw, "-i", tag, "-t", f"{dur:.3f}",
           "-filter_complex", f"[0:v]fps={FPS},scale={W}:{H}:flags=lanczos[v];[v][1:v]overlay=0:0,format=yuv420p",
           "-an", "-c:v", "libx264", "-qp", "0", "-preset", "veryfast", master)
    base = os.path.join(OUT_DIR, f"benchmarking-{mode}")
    for crf in (28, 30, 32, 34):
        ffmpeg("-i", master, "-an", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p",
               "-profile:v", "high", "-movflags", "+faststart", base + ".mp4")
        if os.path.getsize(base + ".mp4") < MAX_BYTES:
            break
    for crf in (36, 40, 44):
        ffmpeg("-i", master, "-an", "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", str(crf), "-row-mt", "1",
               "-deadline", "good", "-cpu-used", "2", "-pix_fmt", "yuv420p", base + ".webm")
        if os.path.getsize(base + ".webm") < MAX_BYTES:
            break
    poster_png = os.path.join(work, f"poster-{mode}.png")
    ffmpeg("-i", master, "-frames:v", "1", poster_png)
    Image.open(poster_png).save(base + "-poster.webp", "WEBP", quality=82, method=6)
    sizes = {ext: os.path.getsize(base + ext) for ext in (".mp4", ".webm", "-poster.webp")}
    for ext, n in sizes.items():
        if n >= MAX_BYTES:
            raise SystemExit(f"{base}{ext} is {n} bytes, over the limit")
    return dur, sizes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--keep", action="store_true", help="keep the temporary work folder")
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
            raw, start = record(f"http://127.0.0.1:{port}", mode, work)
            dur, sizes = encode(raw, start, mode, work)
            print(f"benchmarking-{mode}: {dur:.1f}s  " + "  ".join(f"{k} {v / 1024:.0f} KB" for k, v in sizes.items()))
    finally:
        server.terminate()
        if args.keep:
            print("work folder:", work)
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
