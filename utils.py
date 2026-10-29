"""Safe conversions for report and export code.

Missing data (None, NaN, +/-inf, empty strings, non-numeric text) never
reaches int(), round() or a format spec: it becomes `default` (None unless
given), and callers either leave that record out of the calculation or show
NA in its place.
"""
import math

NA = "n/a"


def safe_float(value, default=None):
    """float(value), or `default` when value is missing or not a finite number."""
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, str):
        value = value.strip().replace(",", "")
        if not value:
            return default
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    return f if math.isfinite(f) else default


def safe_int(value, default=None):
    """int(value) (truncating, like int()), or `default` when value is missing."""
    f = safe_float(value)
    return default if f is None else int(f)


def safe_text(value, default=NA):
    """str(value) for labels, or `default` for None / NaN / blank."""
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return default
    s = str(value).strip()
    return s if s and s.lower() not in ("nan", "none") else default


def fmt_num(value, spec=",.0f", scale=1, prefix="", suffix="", na=NA):
    """Format a number for display, e.g. fmt_num(0.712, ".1f", 100, suffix="%") -> "71.2%".
    Missing values give `na`."""
    f = safe_float(value)
    if f is None:
        return na
    return f"{prefix}{f * scale:{spec}}{suffix}"


# ─── Period labels ──────────────────────────────────────────────────────────
# Same wording as KodoPeriod in static/js/main.js (KPI cards and Excel
# exports), so a figure carries the same period caption on screen and in the
# PDF report. Keep the two in step. A past full year is never a headline
# figure: headlines with only such data show NOT_AVAILABLE and
# period_last_known(); the old figures appear as period_history().
_MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _day(d, with_year=True):
    from datetime import date, datetime
    if isinstance(d, str):
        d = datetime.strptime(d[:10], "%Y-%m-%d").date()
    elif isinstance(d, datetime):
        d = d.date()
    return f"{d.day} {_MON[d.month - 1]}" + (f" {d.year}" if with_year else "")


def period_label(p):
    """'FY 2025', '2025', 'Sep 2026', 'Last 12 months to Sep 2026', 'Summer 2026',
    'Last 30 days', '30 days to 1 Jun 2026', '4 Mar – 1 Jun 2026', 'As of 28 Oct 2026',
    '2026 forecast'; '' for None or an unknown kind."""
    if not p:
        return ""
    k = p.get("kind")
    if k == "fy":
        return f"FY {p['year']}"
    if k == "year":
        return str(p["year"])
    if k == "month":
        return f"{_MON[p['month'] - 1]} {p['year']}"
    if k == "ltm":
        return f"Last 12 months to {_MON[p['month'] - 1]} {p['year']}"
    if k == "season":
        return f"{p['season']} {p['year']}"
    if k == "days":
        return f"Last {p['days']} days"
    if k == "window":
        return f"{p['days']} days to {_day(p['end'])}"
    if k == "range":
        same_year = str(p["start"])[:4] == str(p["end"])[:4]
        return f"{_day(p['start'], not same_year)} – {_day(p['end'])}"
    if k == "asof":
        return f"As of {_day(p['date'])}"
    if k == "forecast":
        return f"{p['year']} forecast"
    if k == "multi":
        return " / ".join(period_label(x) for x in p["parts"])
    return ""


NOT_AVAILABLE = "Not available yet"


def period_caption(p, compare=None, updated=None):
    """'Last 30 days · vs comp set, same dates · updated 29 Oct 2026'."""
    label = period_label(p)
    if not label:
        return ""
    return " · ".join(x for x in (label, compare, updated and f"updated {_day(updated)}") if x)


def period_history(p):
    """'History · FY 2025'."""
    return f"History · {period_label(p)}" if p else ""


def period_last_known(p):
    """'Last known figure: FY 2025'."""
    return f"Last known figure: {period_label(p)}" if p else ""


def period_from_data(code):
    """Period code as stored in the data files ('2025FY', '2025', '2026E', '2026-09') → period dict."""
    import re
    s = str(code or "").strip()
    m = re.match(r"^(\d{4})\s*FY$", s, re.I) or re.match(r"^FY\s*(\d{4})$", s, re.I)
    if m:
        return {"kind": "fy", "year": int(m.group(1))}
    m = re.match(r"^(\d{4})E$", s, re.I)
    if m:
        return {"kind": "forecast", "year": int(m.group(1))}
    if re.match(r"^\d{4}$", s):
        return {"kind": "year", "year": int(s)}
    m = re.match(r"^(\d{4})-(\d{2})$", s)
    if m:
        return {"kind": "month", "year": int(m.group(1)), "month": int(m.group(2))}
    return None


def period_of_codes(codes):
    """Period of a set of rows from their period codes ('multi' when they differ); None if none parse."""
    parts = [p for p in (period_from_data(c) for c in sorted({str(c) for c in codes if c and str(c) != "nan"})) if p]
    if not parts:
        return None
    return parts[0] if len(parts) == 1 else {"kind": "multi", "parts": parts}
