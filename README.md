# Kodo Hospitality

Morocco hotel market intelligence platform (Flask, `app.py`).

Run locally:

```
PORT=5077 python3 app.py
```

## Product media

Screenshots and videos used on the landing page live in `static/img/product/`.
They are made from the local app with sample data only (the demo benchmarking
comp set and a local-only demo account), never real users or organisations.

### Benchmarking video

```
python3 scripts/record_product_videos.py
```

One command records the Benchmarking loop in light and dark mode and writes
`static/img/product/video/benchmarking-{light,dark}.mp4`, `.webm`,
`-poster.webp` and `-poster.png`. The script starts its own copy of the app on
a free port with a temporary data folder and no API keys, then captures the
clip frame by frame (eased cursor: period to "Last 90 days" and back, so the
last frame leads back into the first):

- Capture: 1440x900 viewport at deviceScaleFactor 2, one lossless 2880x1800
  PNG per frame, 30 fps on a fixed timeline (258 frames, 8.6 s). Page time is
  virtual (Playwright's fake clock, CSS animations seeked per frame), so no
  frame is dropped or duplicated. Playwright's built-in video recorder is not
  used: its bitrate is too low for sharp text.
- Scale: "Sample data" tag added at full size, then lanczos down to 2208x1380
  (exact 16:10; yuv420p needs even sides, so not 2200x1375).
- MP4: H.264 High, yuv420p, crf 17, preset slow, BT.709, `+faststart`, no audio.
- WebM: VP9, yuv420p, crf 24, `-b:v 0`, two-pass, row-mt, no audio.
- Poster: first frame at 2208x1380, WebP quality 90 and PNG.
- Quality over size: a file over 8 MB is re-encoded at 1792x1120 rather than
  at a lower quality.

Needs Playwright with Chromium, Pillow, and ffmpeg with libx264 and
libvpx-vp9: the `ffmpeg` on PATH, or else the static build from the
`imageio-ffmpeg` package (`pip install imageio-ffmpeg`, in a virtualenv on
Homebrew Python). Add `--keep` to keep the raw recordings.
