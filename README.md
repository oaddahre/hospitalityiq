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
`static/img/product/video/benchmarking-{light,dark}.mp4`, `.webm` and
`-poster.webp`. The script starts its own copy of the app on a free port with
a temporary data folder and no API keys, records 1280x800 with Playwright
(eased cursor: period to "Last 90 days" and back, so the clip loops), adds the
"Sample data" tag, and encodes H.264 and VP9 at 30 fps, each file under 1.2 MB.

Needs Playwright with Chromium, Pillow, and ffmpeg with libx264 and
libvpx-vp9: the `ffmpeg` on PATH, or else the static build from the
`imageio-ffmpeg` package (`pip install imageio-ffmpeg`, in a virtualenv on
Homebrew Python). Add `--keep` to keep the raw recordings.
