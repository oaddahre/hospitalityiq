"""Safe conversions for report and export code.

Missing data (None, NaN, +/-inf, empty strings, non-numeric text) never
reaches int(), round() or a format spec: it becomes `default` (None unless
given), and callers either leave that record out of the calculation or show
NA in its place.
"""
import math

NA = "n/a"

# Period line of a figure from sample (illustrative) data: never a date, never "updated"
SAMPLE_PERIOD = "Sample data · illustrative figures"


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
# PDF report. Keep the two in step.
_MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _day(d, with_year=True):
    from datetime import date, datetime
    if isinstance(d, str):
        d = datetime.strptime(d[:10], "%Y-%m-%d").date()
    elif isinstance(d, datetime):
        d = d.date()
    return f"{d.day} {_MON[d.month - 1]}" + (f" {d.year}" if with_year else "")


def day_label(d, with_year=True):
    """'2026-11-03' (or a date) -> '3 Nov 2026'."""
    return _day(d, with_year)


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
    if k == "sample":
        return SAMPLE_PERIOD
    if k == "next":
        return f"Next {p['days']} days"
    return ""


NOT_AVAILABLE = "Not available yet"


def period_caption(p, compare=None, updated=None):
    """'Last 30 days · vs comp set, same dates · updated 29 Oct 2026'."""
    label = period_label(p)
    if not label:
        return ""
    return " · ".join(x for x in (label, compare, updated and f"updated {_day(updated)}") if x)


