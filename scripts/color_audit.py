#!/usr/bin/env python3
"""Write docs/COLOR_AUDIT.md: every hardcoded colour outside static/css/tokens.css.

Usage: python3 scripts/color_audit.py
Lists hex / rgb() / hsl() literals (and fpdf RGB calls in Python) by file and line,
flagging the legacy values the palette sweep must remove.
"""
import os
import re
import subprocess
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "COLOR_AUDIT.md")
SKIP = {"static/css/tokens.css", "docs/COLOR_AUDIT.md", "scripts/color_audit.py", "scripts/check_brand.py"}
EXT = (".css", ".js", ".html", ".py", ".svg")
COLOR = re.compile(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b(?![0-9A-Fa-f])|rgba?\([^)]*\)|hsla?\([^)]*\)")
FPDF = re.compile(r"set_(?:fill|text|draw)_color\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)")
LEGACY = {"#4A7FA5", "#3A6F99", "#5B94BD", "#376A92", "#6A9ABC", "#3A6A8E", "#0A0A0A", "#141414",
          "#242424", "#F0F0EE", "#4A9B6F", "#C05252", "#6B7A8D", "#F2A33D"}


def files():
    out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split("\n")
    return sorted(f for f in out if f.endswith(EXT) and f not in SKIP and not f.startswith("static/fonts"))


def main():
    rows, per_file, legacy = [], Counter(), Counter()
    for rel in files():
        try:
            lines = open(os.path.join(ROOT, rel), encoding="utf-8").read().split("\n")
        except (OSError, UnicodeDecodeError):
            continue
        for n, line in enumerate(lines, 1):
            found = COLOR.findall(line) + (FPDF.findall(line) if rel.endswith(".py") else [])
            # var(--token, #fallback) is a token use; its fallback only serves other pages
            for c in found:
                fallback = re.search(r"var\(--[\w-]+,\s*" + re.escape(c), line) is not None
                is_legacy = c.upper() in LEGACY or re.sub(r"\s", "", c) in ("rgba(74,127,165", )
                rows.append((rel, n, c, "fallback" if fallback else "", "LEGACY" if is_legacy else "", line.strip()[:110]))
                per_file[rel] += 1
                if is_legacy:
                    legacy[c.upper()] += 1
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# Colour audit\n\n")
        f.write("Every hardcoded colour outside `static/css/tokens.css`, by file and line. "
                "Regenerate with `python3 scripts/color_audit.py`.\n\n")
        f.write("- **LEGACY**: an old palette value the final sweep must remove.\n")
        f.write("- **fallback**: the second argument of `var(--token, …)`; the page uses the token, "
                "the literal only applies where the token is undefined.\n\n")
        f.write(f"Total: {len(rows)} colour literals in {len(per_file)} files "
                f"({sum(legacy.values())} legacy).\n\n## Per file\n\n| File | Literals |\n|---|---|\n")
        for rel, c in per_file.most_common():
            f.write(f"| `{rel}` | {c} |\n")
        f.write("\n## Legacy values still present\n\n| Value | Count |\n|---|---|\n")
        for c, n in legacy.most_common():
            f.write(f"| `{c}` | {n} |\n")
        cur = None
        for rel, n, c, fb, lg, ctx in rows:
            if rel != cur:
                f.write(f"\n## `{rel}`\n\n| Line | Colour | Note | Context |\n|---|---|---|---|\n")
                cur = rel
            note = " ".join(x for x in (lg, fb) if x)
            f.write(f"| {n} | `{c}` | {note} | `{ctx.replace('|', '¦').replace('`', '')}` |\n")
    print(f"Wrote {os.path.relpath(OUT, ROOT)}: {len(rows)} literals in {len(per_file)} files, {sum(legacy.values())} legacy")


if __name__ == "__main__":
    main()
