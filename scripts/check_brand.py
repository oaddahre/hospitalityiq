#!/usr/bin/env python3
"""Fail if the brand name is spelled with a macron anywhere in the repo, or
if the logo is not the current one (Nov 2026, slanted-dot "kodo."):
  - the files in static/images/brand (LOGO_FILES) must exist
  - nothing may point to the old logo or favicons (OLD_LOGO: static/img/brand,
    kodo-logo-dark/-light, favicon-light/-dark)
  - every page template (one with <head>) must include _favicon.html

Usage: python3 scripts/check_brand.py
Exits 1 and prints file:line for every match; exits 0 when clean.
Exceptions go in scripts/brand_allowlist.txt, one per line, either a path
("docs/history.md") or a single line ("docs/history.md:12"). Lines starting
with # are comments.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWLIST = os.path.join(ROOT, "scripts", "brand_allowlist.txt")

# Every way the macron can be written: precomposed, o + combining macron
# (U+0304), HTML entities and JS/Python escapes. Built from escapes so this
# file never contains the old spelling itself.
O_MACRON = (
    "(?:ō|Ō|[oO]̄|&#333;|&#332;|&#x14[dDcC];|&[oO]macr;"
    "|\\\\u014[dDcC]|\\\\x\\{14[dDcC]\\})"
)
BRAND = re.compile("[Kk]" + O_MACRON + "[Dd]" + O_MACRON)

BINARY_EXT = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".mp4", ".mov",
              ".otf", ".ttf", ".woff", ".woff2", ".pdf", ".xlsx", ".zip")


def repo_files():
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return [f for f in out.splitlines() if f]
    except (OSError, subprocess.CalledProcessError):
        files = []
        for d, dirs, names in os.walk(ROOT):
            dirs[:] = [x for x in dirs if x not in (".git", "node_modules", "__pycache__", ".venv", "venv")]
            files += [os.path.relpath(os.path.join(d, n), ROOT) for n in names]
        return files


def load_allowlist():
    allowed = set()
    if os.path.exists(ALLOWLIST):
        with open(ALLOWLIST, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    allowed.add(line)
    return allowed


LOGO_DIR = os.path.join("static", "images", "brand")
LOGO_FILES = ("kodo-logo-black.svg", "kodo-logo-white.svg", "kodo-logo-black-800.png", "kodo-logo-white-800.png",
              "favicon.svg", "favicon.ico", "favicon-16.png", "favicon-32.png", "favicon-192.png", "favicon-512.png",
              "apple-touch-icon.png", "site.webmanifest", "og-image.png")
OLD_LOGO = re.compile(r"img/brand/|kodo-logo-(?:dark|light)\b|favicon-(?:light|dark)\b")
SELF = os.path.join("scripts", "check_brand.py")


def logo_problems(files, allowed):
    out = [f"{os.path.join(LOGO_DIR, f)}: missing" for f in LOGO_FILES if not os.path.exists(os.path.join(ROOT, LOGO_DIR, f))]
    for rel in files:
        if rel.lower().endswith(BINARY_EXT) or rel in allowed or rel == SELF or rel.startswith("_handoff/"):
            continue
        try:
            with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                text = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if OLD_LOGO.search(line) and f"{rel}:{n}" not in allowed:
                out.append(f"{rel}:{n}: old logo or favicon: {line.strip()[:100]}")
        if rel.startswith("templates/") and rel.endswith(".html") and "<head>" in text and '{% include "_favicon.html" %}' not in text:
            out.append(f"{rel}: no {{% include \"_favicon.html\" %}} in its <head>")
    return out


def main():
    allowed = load_allowlist()
    hits = []
    logo = logo_problems(repo_files(), allowed)
    for rel in repo_files():
        if rel.lower().endswith(BINARY_EXT) or rel in allowed:
            continue
        path = os.path.join(ROOT, rel)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            if BRAND.search(line) and f"{rel}:{n}" not in allowed:
                hits.append(f"{rel}:{n}: {line.strip()[:120]}")
    if hits:
        print(f"Brand check failed: {len(hits)} line(s) spell the brand with a macron (use 'Kodo'):")
        print("\n".join(hits))
    if logo:
        print(f"Brand check failed: {len(logo)} logo problem(s):")
        print("\n".join(logo))
    if hits or logo:
        return 1
    print("Brand check passed: no macron spellings of the brand name; the current logo and favicon everywhere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
