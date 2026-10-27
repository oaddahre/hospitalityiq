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
