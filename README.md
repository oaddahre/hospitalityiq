# Kodo Hospitality

Morocco hotel market intelligence platform (Flask, `app.py`).

Run locally:

```
PORT=5077 python3 app.py
```

## Product media

Screenshots and videos used on the landing page live in `static/img/product/`.
They are made from the local app with a local-only demo account and the
platform's reference data (plus the demo benchmarking comp set), never real
users or organisations.

### Hotel and owner profile screenshots

```
python3 scripts/capture_profile_screenshots.py
```

Writes `static/img/product/hotel-profile-{light,dark}` (La Mamounia) and
`owner-profile-{light,dark}` (Madaëf), each as `.webp` (quality 90) and `.png`,
2880x1800 (1440x900 at deviceScaleFactor 2). Like the video script it starts
its own copy of the app with a temporary data folder and a local-only demo
account, so no real user appears. Unlike the video these show the platform's
own hotel and owner data, so they carry no "Sample data" tag. The script waits
for fonts, data and charts, scrolls as little as possible so the bottom edge
falls between blocks, and stops on any console error, spinner, toast, bad value
(NaN, undefined, null, None) or clipped theme toggle. Operator logos from the
third-party logo CDN don't load from localhost, so the shots show those
operators as text.

### Product tour video

```
python3 scripts/record_product_videos.py
```

One command records the landing page's product tour in light and dark mode
and writes `static/img/product/video/benchmarking-{light,dark}.mp4`, `.webm`,
`-poster.webp` and `-poster.png` (same names as before, so the landing page
needs no change). The script starts its own copy of the app on a free port
with a temporary data folder, a local-only demo account and no API keys,
then captures the tour frame by frame (about 34 s, eased cursor and eased
scrolling):

1. Benchmarking with the comp set loaded; the KPI cards and their period lines.
2. Period to "Last 90 days": the KPIs and charts update.
3. Scroll through the calendars to the RevPAR trend and the monthly summary
   table, then back to the top.
4. Owners in the top nav; the list loads.
5. Hover and open the Madaëf owner profile.
6. Header and KPI cards, then down through its hotel portfolio.
7. Back to Benchmarking via the top nav, period back to "Last 30 days"; the
   last 0.5 s crossfades into the first frame, so the loop is seamless.

The Benchmarking figures are the platform's demo comp set (sample hotels,
shown as "Demo mode" on the page); the owner profile is real platform data.
No "Sample data" tag is added.

- Capture: 1440x900 viewport at deviceScaleFactor 2, one lossless 2880x1800
  PNG per frame, 30 fps on a fixed timeline. Page time is virtual
  (Playwright's fake clock, CSS animations seeked per frame), so no frame is
  dropped or duplicated, and pending requests are awaited before every frame;
  a spinner, placeholder or error on screen stops the script.
- Scale: lanczos down to 2208x1380 (exact 16:10; yuv420p needs even sides).
- MP4: H.264 High, yuv420p, crf 17, preset slow, BT.709, `+faststart`, no audio.
- WebM: VP9, yuv420p, crf 24, `-b:v 0`, two-pass, row-mt, no audio.
- Poster: first frame at 2208x1380, WebP quality 90 and PNG.
- Quality over size: a file over 12 MB is re-encoded at 1792x1120 (the
  exact-16:10 size nearest 1800 wide) rather than at a lower quality.

Needs Playwright with Chromium, Pillow, and ffmpeg with libx264 and
libvpx-vp9: the `ffmpeg` on PATH, or else the static build from the
`imageio-ffmpeg` package (`pip install imageio-ffmpeg`, in a virtualenv on
Homebrew Python). Add `--keep` to keep the raw recordings.
