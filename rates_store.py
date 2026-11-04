"""Scraped rates: the one place that decides which published price a night
shows.

A night is looked up every day from 30 days ahead, so scraped_rates.csv
holds many prices for it (one per scrape day). Every page and model uses
the LATEST one: the most recent scrape_date; on the same scrape day, the
source the scraper trusts most (live sources first, then a manual price).
"""

# Same scrape day: higher wins (as the hotel profile always ranked them)
SOURCE_PRIORITY = {'live_dataforseo': 5, 'live_brand': 5, 'manual_override': 4, 'live_booking': 3,
                   'estimated': 1, 'unavailable': 0}


def _key(r):
    return (r.get('scrape_date') or '', SOURCE_PRIORITY.get(r.get('source'), 0))


def latest_per_night(rows, by=('hotel_id', 'stay_date')):
    """{(hotel_id, stay_date): row}: the latest observation of each night."""
    out = {}
    for r in rows:
        k = tuple(str(r.get(f, '')) for f in by)
        cur = out.get(k)
        if cur is None or _key(r) > _key(cur):
            out[k] = r
    return out


def last_before_night(rows):
    """{(hotel_id, stay_date): row}: the last price observed BEFORE each
    night (scrape_date earlier than the stay date): its last published rate."""
    return latest_per_night([r for r in rows if (r.get('scrape_date') or '') < (r.get('stay_date') or '')])
