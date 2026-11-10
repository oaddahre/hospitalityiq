"""Sample data for the landing page's screenshots and product tour video.

    build(data_dir)   writes into a temporary DATA_DIR (never the real one)
                      a complete, fictional platform: no real hotel, owner,
                      brand or pipeline project appears anywhere in it.

- hotels.csv: 31 fictional hotels (ids 9001-9031) in nine Moroccan cities,
  under three fictional brand groups (Amberlune Hotels, Corniva Hospitality,
  Sablière Hotels) or independent. Every name is checked against the real
  hotels.csv and pipeline.csv (names, brands, brand groups): none clashes.
- owners.json: three fictional owners: "Ocre Sample Holdings" (the six
  hotels of the landing page's profile screenshots, 9001-9006), "Lune Sample
  Capital" and "Sahel Sample Family Office".
- pipeline.csv: four fictional projects.
- performance.csv: a fictional FY 2025 row per hotel (the platform shows
  these as Kodo model estimates). daily_performance.csv: header only.
- scraped_rates.csv: fictional published prices for every hotel, collected
  on each of the last 7 days for the next 30 nights, a few nights with no
  price, as the scraper writes them (7 days, like the real history so far).
- estimated_occupancy.csv: the platform's own occupancy model (the
  displayed model) run on that data, in a subprocess.

Events (events.json) are the platform's own public calendar: festivals,
holidays and school breaks, not hotel or owner records.

Every figure is a fixed function of hotel, night and collection day (a
hash, not a random draw), with weekend uplift and the real month's
seasonality, so a re-capture on the same day gives the same images.
These figures are illustrative; the landing page labels them
"Sample data: fictional hotels".
"""
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import rates_store as RS  # noqa: E402

OCRE, LUNE, SAHEL, NONE = "Ocre Sample Holdings", "Lune Sample Capital", "Sahel Sample Family Office", "Undisclosed"
OWNERS = [
    {"id": "ocre-sample", "name": OCRE, "full_name": "Ocre Sample Holdings (fictional)", "type": "Private",
     "parent": "", "headquarters": "Marrakech, Morocco", "logo_local": "",
     "description": ("A fictional owner, used only for Kodo's sample screenshots: six fictional hotels in "
                     "Marrakech, Fes and Essaouira, with illustrative published prices.")},
    {"id": "lune-sample", "name": LUNE, "full_name": "Lune Sample Capital (fictional)", "type": "Listed",
     "parent": "", "headquarters": "Casablanca, Morocco", "logo_local": "",
     "description": ("A fictional listed owner, used only for Kodo's sample video: Amberlune and Corniva "
                     "hotels across Morocco, with illustrative published prices.")},
    {"id": "sahel-sample", "name": SAHEL, "full_name": "Sahel Sample Family Office (fictional)", "type": "Family",
     "parent": "", "headquarters": "Agadir, Morocco", "logo_local": "",
     "description": ("A fictional family owner, used only for Kodo's sample video: Sablière resorts and an "
                     "independent riad, with illustrative published prices.")},
]
OWNER = OWNERS[0]

REGION = {"Marrakech": "Marrakech-Safi", "Essaouira": "Marrakech-Safi", "Fes": "Fès-Meknès",
          "Casablanca": "Grand Casablanca-Settat", "Rabat / Salé / Témara": "Rabat-Salé-Kénitra",
          "Tanger": "Tanger-Tétouan-Al Hoceima", "Tamuda Bay / Tétouan": "Tanger-Tétouan-Al Hoceima",
          "Agadir / Taghazout": "Souss-Massa", "Ouarzazate": "Drâa-Tafilalet", "Dakhla": "Dakhla-Oued Ed-Dahab"}
COORDS = {"Marrakech": (31.6295, -7.9811), "Fes": (34.0331, -5.0003), "Essaouira": (31.5085, -9.7595),
          "Casablanca": (33.5890, -7.6190), "Rabat / Salé / Témara": (34.0150, -6.8330),
          "Tanger": (35.7700, -5.8000), "Tamuda Bay / Tétouan": (35.6900, -5.3200),
          "Agadir / Taghazout": (30.4200, -9.6000), "Ouarzazate": (30.9200, -6.9000), "Dakhla": (23.7000, -15.9400)}

# id, name, city, category, brand, brand_group, keys, year opened, base price (MAD), owner
# (brand "" = the hotel's own name: an independent)
HOTELS = [
    (9001, "Palais Ocre",              "Marrakech",             "Luxury",        "", "Independent Luxury",        57,  2016, 6200, OCRE),
    (9002, "Riad Atlas",               "Marrakech",             "Luxury",        "", "Independent Luxury",        45,  2012, 5100, OCRE),
    (9003, "Kasbah Amandier",          "Marrakech",             "Luxury",        "", "Independent Luxury",        71,  2019, 7200, OCRE),
    (9004, "Jardin des Oliviers",      "Marrakech",             "Upper Upscale", "", "Independent Upper Upscale", 55,  2010, 3900, OCRE),
    (9005, "Dar Zellige",              "Fes",                   "Upper Upscale", "", "Independent Upper Upscale", 48,  2014, 2900, OCRE),
    (9006, "Hotel Bab Sahel",          "Essaouira",             "Upscale",       "", "Independent Upscale",       64,  2008, 1900, OCRE),
    (9007, "Amberlune Marrakech",      "Marrakech",             "Luxury",        "Amberlune", "Amberlune Hotels",         118, 2018, 5600, LUNE),
    (9008, "Corniva Marrakech Gueliz", "Marrakech",             "Upscale",       "Corniva", "Corniva Hospitality",        164, 2015, 1500, LUNE),
    (9009, "Hotel Medina Palace",      "Marrakech",             "Upper Upscale", "", "Independent Upper Upscale", 28,  2011, 3400, NONE),
    (9010, "Dar Safran",               "Marrakech",             "Upscale",       "", "Independent Upscale",       28,  2013, 2600, SAHEL),
    (9011, "Corniva Lite Marrakech",   "Marrakech",             "Midscale",      "Corniva Lite", "Corniva Hospitality",   210, 2019, 780,  NONE),
    (9012, "Amberlune Casablanca",     "Casablanca",            "Luxury",        "Amberlune", "Amberlune Hotels",         160, 2021, 3900, LUNE),
    (9013, "Corniva Casablanca Marina", "Casablanca",           "Upscale",       "Corniva", "Corniva Hospitality",        220, 2017, 1650, LUNE),
    (9014, "Corniva Lite Casablanca",  "Casablanca",            "Midscale",      "Corniva Lite", "Corniva Hospitality",   180, 2020, 850,  NONE),
    (9015, "Hotel Les Arcades Blanches", "Casablanca",          "Upper Upscale", "", "Independent Upper Upscale", 96,  2009, 2100, NONE),
    (9016, "Amberlune Rabat",          "Rabat / Salé / Témara", "Luxury",        "Amberlune", "Amberlune Hotels",         102, 2022, 3600, LUNE),
    (9017, "Corniva Rabat Agdal",      "Rabat / Salé / Témara", "Upscale",       "Corniva", "Corniva Hospitality",        140, 2016, 1350, LUNE),
    (9018, "Maison Lumen",             "Rabat / Salé / Témara", "Upper Upscale", "", "Independent Upper Upscale", 60,  2018, 1900, NONE),
    (9019, "Sablière Tanger Plage",    "Tanger",                "Upper Upscale", "Sablière Resort", "Sablière Hotels",    190, 2018, 1900, SAHEL),
    (9020, "Corniva Tanger Ville",     "Tanger",                "Upscale",       "Corniva", "Corniva Hospitality",        150, 2014, 1200, NONE),
    (9021, "Villa Nerolia",            "Tanger",                "Luxury",        "", "Independent Luxury",        32,  2017, 3100, NONE),
    (9022, "Sablière Taghazout",       "Agadir / Taghazout",    "Upper Upscale", "Sablière Resort", "Sablière Hotels",    260, 2019, 2300, SAHEL),
    (9023, "Amberlune Rivage Agadir",  "Agadir / Taghazout",    "Upper Upscale", "Amberlune Rivage", "Amberlune Hotels",  240, 2016, 2400, LUNE),
    (9024, "Corniva Lite Agadir",      "Agadir / Taghazout",    "Midscale",      "Corniva Lite", "Corniva Hospitality",   200, 2012, 700,  NONE),
    (9025, "Palais Nouriya",           "Fes",                   "Luxury",        "", "Independent Luxury",        40,  2013, 3300, NONE),
    (9026, "Corniva Fes",              "Fes",                   "Upscale",       "Corniva", "Corniva Hospitality",        130, 2015, 1100, NONE),
    (9027, "Sablière Essaouira",       "Essaouira",             "Upscale",       "Sablière", "Sablière Hotels",           110, 2020, 1450, SAHEL),
    (9028, "Kasbah Ambrine",           "Ouarzazate",            "Upscale",       "", "Independent Upscale",       70,  2006, 1250, NONE),
    (9029, "Sablière Ouarzazate",      "Ouarzazate",            "Upscale",       "Sablière", "Sablière Hotels",           120, 2011, 1000, SAHEL),
    (9030, "Lagune Azura Lodge",       "Dakhla",                "Upper Upscale", "", "Independent Upper Upscale", 44,  2020, 2200, NONE),
    (9031, "Amberlune Tamuda Bay",     "Tamuda Bay / Tétouan",  "Luxury",        "Amberlune", "Amberlune Hotels",         90,  2023, 4200, LUNE),
]
PROFILE_HOTEL_ID = 9001

# id, name, city, category, brand, brand_group, owner, keys, opening, status, investment (MAD)
PIPELINE = [
    (1, "Amberlune Essaouira",     "Essaouira",            "Luxury",        "Amberlune", "Amberlune Hotels",  LUNE,  80,  2028, "Planning",           640000000),
    (2, "Corniva Dakhla",          "Dakhla",               "Upscale",       "Corniva", "Corniva Hospitality", NONE,  120, 2027, "Under Construction", 260000000),
    (3, "Sablière Tamuda Bay",     "Tamuda Bay / Tétouan", "Upper Upscale", "Sablière Resort", "Sablière Hotels", SAHEL, 220, 2028, "Planning",     780000000),
    (4, "Maison Lumen Marrakech",  "Marrakech",            "Upper Upscale", "Maison Lumen", "Independent Upper Upscale", NONE, 48, 2027, "Under Construction", 190000000),
]

MONTH = {1: 0.95, 2: 1.00, 3: 1.10, 4: 1.16, 5: 1.05, 6: 0.90,
         7: 0.84, 8: 0.86, 9: 0.97, 10: 1.08, 11: 1.03, 12: 1.12}
CITY_OCC = {"Marrakech": 0.72, "Casablanca": 0.66, "Rabat / Salé / Témara": 0.63, "Tanger": 0.61,
            "Agadir / Taghazout": 0.70, "Fes": 0.58, "Essaouira": 0.60, "Ouarzazate": 0.52,
            "Dakhla": 0.64, "Tamuda Bay / Tétouan": 0.55}
SCRAPE_DAYS = 7
NIGHTS = 30


def _noise(*key):
    """A fixed value in [-1, 1) for this key."""
    h = hashlib.sha256("|".join(map(str, key)).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 63 - 1.0


def casablanca_today():
    try:
        import pytz
        return datetime.now(pytz.timezone("Africa/Casablanca")).date()
    except Exception:
        return datetime.utcnow().date()


def _price(base, hid, night, scrape):
    """Published price, or None (no price that night: about 1 night in 15)."""
    if _noise(hid, night, "gap") > 0.87:
        return None
    weekend = night.weekday() in (4, 5)              # Fri, Sat nights
    p = base * MONTH[night.month] * (1.12 if weekend else 1.0)
    p *= 1 + 0.08 * _noise(hid, night, "night") + 0.02 * _noise(hid, night, scrape, "day")
    return int(round(p / 10) * 10)


def _check_names():
    real = set()
    for name, cols in (("hotels.csv", ("name", "brand", "brand_group")), ("pipeline.csv", ("name", "brand", "brand_group"))):
        with open(os.path.join(ROOT, name), encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                real.update(r[c].strip().lower() for c in cols if r.get(c))
    ours = {h[1] for h in HOTELS} | {h[4] for h in HOTELS if h[4]} | {p[1] for p in PIPELINE} \
        | {h[5] for h in HOTELS if not h[5].startswith("Independent")} | {o["name"] for o in OWNERS}
    clash = sorted(n for n in ours if n.lower() in real)
    if clash:
        raise SystemExit(f"Sample names clash with real records: {clash}")


def _write_csv(path, fields, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def build(data_dir, today=None):
    today = today or casablanca_today()
    _check_names()

    # Hotels
    with open(os.path.join(ROOT, "hotels.csv"), encoding="utf-8", newline="") as f:
        fields = next(csv.reader(f))
    rows = []
    for hid, name, city, cat, brand, group, keys, opened, _, owner in HOTELS:
        lat, lng = COORDS[city]
        rows.append({**{k: "" for k in fields}, "id": hid, "name": name, "city": city, "region": REGION[city],
                     "category": cat, "brand": brand or name, "brand_group": group, "keys": keys,
                     "year_opened": opened, "year_opened_verified": "verified", "status": "Open",
                     "lat": f"{lat + 0.004 * _noise(hid, 'lat'):.6f}", "lng": f"{lng + 0.004 * _noise(hid, 'lng'):.6f}",
                     "owner": owner, "data_quality": "verified", "notes": "Fictional sample hotel"})
    _write_csv(os.path.join(data_dir, "hotels.csv"), fields, rows)

    # Owners
    owners = [{**o, "hotels": [{"name": h[1], "brand_group": h[5], "city": h[2]} for h in HOTELS if h[9] == o["name"]]}
              for o in OWNERS]
    with open(os.path.join(data_dir, "owners.json"), "w", encoding="utf-8") as f:
        json.dump(owners, f, ensure_ascii=False, indent=2)

    # Pipeline
    with open(os.path.join(ROOT, "pipeline.csv"), encoding="utf-8", newline="") as f:
        fields = next(csv.reader(f))
    _write_csv(os.path.join(data_dir, "pipeline.csv"), fields, [
        {"id": pid, "name": name, "city": city, "region": REGION[city], "category": cat, "brand": brand,
         "brand_group": group, "owner": owner, "keys": keys, "expected_opening": year, "status": status,
         "investment_mad": inv, "lat": f"{COORDS[city][0] + 0.01 * _noise(pid, 'plat'):.4f}",
         "lng": f"{COORDS[city][1] + 0.01 * _noise(pid, 'plng'):.4f}", "notes": "Fictional sample project"}
        for pid, name, city, cat, brand, group, owner, keys, year, status, inv in PIPELINE])

    # FY 2025 model estimates (shown by the platform as Kodo model estimates)
    with open(os.path.join(ROOT, "performance.csv"), encoding="utf-8", newline="") as f:
        fields = next(csv.reader(f))
    perf = []
    for hid, name, city, cat, *_, base, owner in HOTELS:
        occ = round(min(0.88, max(0.42, CITY_OCC[city] + 0.05 * _noise(hid, "occ"))), 2)
        adr = int(round(base * 0.9 / 50) * 50)
        perf.append({"hotel_id": hid, "period": "2025FY", "occupancy": occ, "adr_mad": adr,
                     "revpar_mad": int(round(occ * adr)), "trevpar_mad": int(round(occ * adr * 1.45)),
                     "gop_margin": round(0.36 + 0.04 * _noise(hid, "gop"), 2), "source": "HIQ Estimate"})
    _write_csv(os.path.join(data_dir, "performance.csv"), fields, perf)
    with open(os.path.join(ROOT, "daily_performance.csv"), encoding="utf-8", newline="") as f:
        fields = next(csv.reader(f))
    _write_csv(os.path.join(data_dir, "daily_performance.csv"), fields, [])

    # Published prices: collected daily for the last 7 days, next 30 nights each
    rates = []
    for d in range(SCRAPE_DAYS - 1, -1, -1):
        scrape = today - timedelta(days=d)
        for hid, name, city, *_, base, owner in HOTELS:
            for n in range(1, NIGHTS + 1):
                night = scrape + timedelta(days=n)
                p = _price(base, hid, night, scrape)
                rates.append({"hotel_id": hid, "hotel_name": name, "city": city,
                              "scrape_date": scrape.isoformat(), "stay_date": night.isoformat(),
                              "rate_mad": p or "", "rate_eur": round(p / 10.8, 2) if p else "",
                              "source": "live_dataforseo" if p else "unavailable",
                              "data_quality": "name_matched" if p else "unavailable", "rooms_left": "",
                              "availability_signal": "available" if p else "unknown",
                              "scrape_status": "success" if p else "failed"})
    RS.append(data_dir, [{k: str(v) for k, v in r.items()} for r in rates], env={})

    # The occupancy model on that data (its own process: it reads DATA_DIR at import)
    env = {**os.environ, "DATA_DIR": data_dir}
    for k in ("ANTHROPIC_API_KEY", "DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD", "RESEND_API_KEY"):
        env.pop(k, None)
    subprocess.run([sys.executable, "-c", "import occupancy_model as m; m.recent_model().run()"],
                   cwd=ROOT, env=env, check=True, stdout=subprocess.DEVNULL)
    return today


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if not out or os.path.abspath(out) == ROOT:
        raise SystemExit("usage: python3 scripts/sample_profiles.py <empty temporary folder>")
    os.makedirs(out, exist_ok=True)
    print("sample data for", build(out), "in", out)
