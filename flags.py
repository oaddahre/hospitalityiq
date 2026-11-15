"""Feature flags for changes to figures clients see. Each is a Railway
variable, off unless set to on (read on every call: no restart needed).
Nothing behind a flag changes a visible number while the flag is off; the
admin's Data health page shows each flag and what it would change.

  CONFIDENCE_UI     confidence labels on modelled figures; figures below the
                    agreed level greyed ("limited data") or hidden
                    ("insufficient data"); no occupancy shown for a hotel
                    with no price history
  QUALITY_RANGES    the v2 occupancy model leaves out prices that failed the
                    data-quality checks and widens the range where history
                    is short or the night's price is doubtful
  VALUATION_V2      the corrected valuation engine (F&B and other
                    departmental costs, capex in MAD million, IRR terminal
                    timing, levered equity multiple, range from the
                    sensitivity of the main inputs)
"""
import os

FLAGS = {
    'CONFIDENCE_UI': 'Confidence labels; low-confidence figures greyed or hidden',
    'QUALITY_RANGES': 'Occupancy model ignores failed prices and widens thin-data ranges',
    'VALUATION_V2': 'Corrected valuation engine, ranges from input sensitivity',
}


def on(name, env=os.environ):
    return str(env.get(name, '')).strip().lower() in ('on', '1', 'true', 'yes')


def all_flags(env=os.environ):
    return {k: on(k, env) for k in FLAGS}
