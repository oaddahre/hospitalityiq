#!/usr/bin/env python3
"""Fail if the brand name is spelled with a macron anywhere in the repo.

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


def main():
    allowed = load_allowlist()
    hits = []
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
        return 1
    print("Brand check passed: no macron spellings of the brand name.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
