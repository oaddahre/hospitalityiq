from flask import Flask, jsonify, render_template, request
import pandas as pd
import anthropic
import json
import csv
import io
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_FILE            = os.path.join(DATA_DIR, "news.json")
BENCH_FILE           = os.path.join(DATA_DIR, "demo_benchmarking.json")
DAILY_PERF_FILE      = os.path.join(DATA_DIR, "daily_performance.csv")
UPLOAD_LOG_FILE      = os.path.join(DATA_DIR, "upload_log.json")


def load_news():
    if not os.path.exists(NEWS_FILE):
        return []
    with open(NEWS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_news(articles):
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)


def admin_ok():
    expected = os.getenv("ADMIN_PASSWORD", "hiq2026")
    return request.headers.get("X-Admin-Password", "") == expected


def load_data():
    hotels = pd.read_csv(os.path.join(DATA_DIR, "hotels.csv"))
    perf = pd.read_csv(os.path.join(DATA_DIR, "performance.csv"))
    merged = hotels.merge(perf, left_on="id", right_on="hotel_id", how="left")
    return hotels, perf, merged


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    hotels, perf, merged = load_data()

    # National KPIs
    total_keys = int(hotels["keys"].sum())
    weighted_occ = float((merged["occupancy"] * merged["keys"]).sum() / merged["keys"].sum())
    weighted_adr = float((merged["adr_mad"] * merged["keys"] * merged["occupancy"]).sum() /
                         (merged["keys"] * merged["occupancy"]).sum())
    weighted_revpar = float((merged["revpar_mad"] * merged["keys"]).sum() / merged["keys"].sum())
    weighted_trevpar = float((merged["trevpar_mad"] * merged["keys"]).sum() / merged["keys"].sum())
    weighted_gop = float((merged["gop_margin"] * merged["keys"]).sum() / merged["keys"].sum())

    national_kpis = {
        "total_hotels": len(hotels),
        "total_keys": total_keys,
        "occupancy": round(weighted_occ, 4),
        "adr_mad": round(weighted_adr, 1),
        "revpar_mad": round(weighted_revpar, 1),
        "trevpar_mad": round(weighted_trevpar, 1),
        "gop_margin": round(weighted_gop, 4),
    }

    # City aggregates (keys-weighted for rate metrics)
    city_rows = []
    for city, grp in merged.groupby("city"):
        keys_sum = grp["keys"].sum()
        city_rows.append({
            "city": city,
            "hotel_count": len(grp),
            "total_keys": int(keys_sum),
            "occupancy": round(float((grp["occupancy"] * grp["keys"]).sum() / keys_sum), 4),
            "adr_mad": round(float((grp["adr_mad"] * grp["keys"] * grp["occupancy"]).sum() /
                                   (grp["keys"] * grp["occupancy"]).sum()), 1),
            "revpar_mad": round(float((grp["revpar_mad"] * grp["keys"]).sum() / keys_sum), 1),
            "trevpar_mad": round(float((grp["trevpar_mad"] * grp["keys"]).sum() / keys_sum), 1),
            "gop_margin": round(float((grp["gop_margin"] * grp["keys"]).sum() / keys_sum), 4),
        })
    city_rows.sort(key=lambda x: x["total_keys"], reverse=True)

    # Segment breakdown
    segment_rows = []
    for seg, grp in merged.groupby("category"):
        keys_sum = grp["keys"].sum()
        segment_rows.append({
            "segment": seg,
            "hotel_count": len(grp),
            "total_keys": int(keys_sum),
            "occupancy": round(float((grp["occupancy"] * grp["keys"]).sum() / keys_sum), 4),
            "adr_mad": round(float((grp["adr_mad"] * grp["keys"] * grp["occupancy"]).sum() /
                                   (grp["keys"] * grp["occupancy"]).sum()), 1),
            "revpar_mad": round(float((grp["revpar_mad"] * grp["keys"]).sum() / keys_sum), 1),
            "gop_margin": round(float((grp["gop_margin"] * grp["keys"]).sum() / keys_sum), 4),
        })
    seg_order = ["Luxury", "Upper Upscale", "Upscale", "Midscale"]
    segment_rows.sort(key=lambda x: seg_order.index(x["segment"]) if x["segment"] in seg_order else 99)

    # Brand group breakdown
    brand_rows = []
    for brand, grp in merged.groupby("brand_group"):
        keys_sum = grp["keys"].sum()
        brand_rows.append({
            "brand_group": brand,
            "hotel_count": len(grp),
            "total_keys": int(keys_sum),
            "occupancy": round(float((grp["occupancy"] * grp["keys"]).sum() / keys_sum), 4),
            "adr_mad": round(float((grp["adr_mad"] * grp["keys"] * grp["occupancy"]).sum() /
                                   (grp["keys"] * grp["occupancy"]).sum()), 1),
            "revpar_mad": round(float((grp["revpar_mad"] * grp["keys"]).sum() / keys_sum), 1),
            "gop_margin": round(float((grp["gop_margin"] * grp["keys"]).sum() / keys_sum), 4),
        })
    brand_rows.sort(key=lambda x: x["total_keys"], reverse=True)

    return jsonify({
        "national_kpis": national_kpis,
        "city_aggregates": city_rows,
        "segment_breakdown": segment_rows,
        "brand_breakdown": brand_rows,
    })


@app.route("/api/hotels")
def api_hotels():
    _, _, merged = load_data()
    cols = [
        "id", "name", "city", "region", "category", "brand", "brand_group",
        "keys", "year_opened", "status", "lat", "lng", "owner", "data_quality",
        "period", "occupancy", "adr_mad", "revpar_mad", "trevpar_mad", "gop_margin", "source",
    ]
    records = merged[cols].to_dict(orient="records")
    return jsonify(records)


def build_system_prompt():
    hotels_df, _, merged = load_data()

    tk = merged["keys"].sum()
    ok = (merged["occupancy"] * merged["keys"]).sum()

    nat_occ    = ok / tk
    nat_adr    = (merged["adr_mad"]    * merged["keys"] * merged["occupancy"]).sum() / ok
    nat_revpar = (merged["revpar_mad"] * merged["keys"]).sum() / tk
    nat_trev   = (merged["trevpar_mad"]* merged["keys"]).sum() / tk
    nat_gop    = (merged["gop_margin"] * merged["keys"]).sum() / tk

    # City breakdown
    city_rows = []
    for city, g in merged.groupby("city"):
        ctk = g["keys"].sum()
        cok = (g["occupancy"] * g["keys"]).sum()
        city_rows.append((
            city, len(g), int(ctk),
            cok / ctk,
            (g["adr_mad"] * g["keys"] * g["occupancy"]).sum() / cok,
            (g["revpar_mad"] * g["keys"]).sum() / ctk,
            (g["gop_margin"] * g["keys"]).sum() / ctk,
        ))
    city_rows.sort(key=lambda x: x[5], reverse=True)

    # Segment breakdown
    seg_order = ["Luxury", "Upper Upscale", "Upscale", "Midscale"]
    seg_rows = []
    for seg, g in merged.groupby("category"):
        stk = g["keys"].sum()
        sok = (g["occupancy"] * g["keys"]).sum()
        seg_rows.append((
            seg, len(g), int(stk),
            sok / stk,
            (g["adr_mad"] * g["keys"] * g["occupancy"]).sum() / sok,
            (g["revpar_mad"] * g["keys"]).sum() / stk,
            (g["gop_margin"] * g["keys"]).sum() / stk,
        ))
    seg_rows.sort(key=lambda x: seg_order.index(x[0]) if x[0] in seg_order else 99)

    # Brand group breakdown
    brand_rows = []
    for brand, g in merged.groupby("brand_group"):
        btk = g["keys"].sum()
        bok = (g["occupancy"] * g["keys"]).sum()
        brand_rows.append((
            brand, len(g), int(btk),
            bok / btk,
            (g["adr_mad"] * g["keys"] * g["occupancy"]).sum() / bok,
            (g["revpar_mad"] * g["keys"]).sum() / btk,
            (g["gop_margin"] * g["keys"]).sum() / btk,
        ))
    brand_rows.sort(key=lambda x: x[2], reverse=True)

    def fmt_city(r):
        return (f"  {r[0]:<14} | {r[1]:>2} hotels | {r[2]:>5,} keys | "
                f"Occ {r[3]*100:>4.1f}% | ADR {r[4]:>6,.0f} | RevPAR {r[5]:>6,.0f} | GOP {r[6]*100:>4.1f}%")

    def fmt_seg(r):
        return (f"  {r[0]:<15} | {r[1]:>2} hotels | {r[2]:>5,} keys | "
                f"Occ {r[3]*100:>4.1f}% | ADR {r[4]:>6,.0f} | RevPAR {r[5]:>6,.0f} | GOP {r[6]*100:>4.1f}%")

    def fmt_brand(r):
        return (f"  {r[0]:<32} | {r[1]:>2} hotels | {r[2]:>5,} keys | "
                f"Occ {r[3]*100:>4.1f}% | ADR {r[4]:>6,.0f} | RevPAR {r[5]:>6,.0f} | GOP {r[6]*100:>4.1f}%")

    hotel_lines = "\n".join(
        f"  {row['name']} ({row['city']}, {row['category']}, {row['brand_group']}) — "
        f"{int(row['keys'])} keys | Occ {row['occupancy']*100:.1f}% | "
        f"ADR {row['adr_mad']:,.0f} MAD | RevPAR {row['revpar_mad']:,.0f} MAD | "
        f"GOP {row['gop_margin']*100:.1f}%"
        for _, row in merged.iterrows()
    )

    return f"""You are HIQ Analyst, a Morocco hospitality market intelligence assistant built by HIQ. You have exclusive access to HIQ's proprietary database of 45 branded hotels across 7 Moroccan cities.

You serve hospitality investors, operators, developers, and consultants. Provide precise, data-driven answers. Always cite specific metrics. Use MAD (Moroccan Dirhams) for all monetary values unless asked otherwise. Approximate USD/EUR conversions: 1 USD ≈ 10 MAD, 1 EUR ≈ 11 MAD. Be analytical, concise, and professional — not conversational.

══════════════════════════════════════════════════
HIQ PROPRIETARY DATA — MOROCCO BRANDED HOTELS — 2025 FY ESTIMATES
══════════════════════════════════════════════════

NATIONAL MARKET SNAPSHOT
  Total branded hotels in database : {len(hotels_df)}
  Total keys (rooms)               : {int(tk):,}
  National occupancy               : {nat_occ*100:.1f}%
  National ADR                     : {nat_adr:,.0f} MAD
  National RevPAR                  : {nat_revpar:,.0f} MAD
  National TRevPAR                 : {nat_trev:,.0f} MAD
  National GOP margin              : {nat_gop*100:.1f}%

CITY PERFORMANCE (ranked by RevPAR)
{chr(10).join(fmt_city(r) for r in city_rows)}

SEGMENT PERFORMANCE
{chr(10).join(fmt_seg(r) for r in seg_rows)}

BRAND GROUP PERFORMANCE (ranked by total keys)
{chr(10).join(fmt_brand(r) for r in brand_rows)}

INDIVIDUAL HOTEL DETAIL
{hotel_lines}
══════════════════════════════════════════════════

Answer only from the data above. If asked about hotels, cities, or markets not in the HIQ database, state clearly that the data is not available. When making comparisons, always show both sides with specific numbers."""


@app.route("/api/chat", methods=["POST"])
def api_chat():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    messages = payload.get("messages", [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return jsonify({
            "error": "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
        }), 503

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=build_system_prompt(),
            messages=messages,
        )
        return jsonify({"response": response.content[0].text})
    except anthropic.AuthenticationError as e:
        print(f"[ERROR] AuthenticationError — status={e.status_code} body={e.body}")
        return jsonify({"error": "Invalid API key — check ANTHROPIC_API_KEY in your .env file."}), 401
    except anthropic.RateLimitError as e:
        print(f"[ERROR] RateLimitError — status={e.status_code} body={e.body}")
        return jsonify({"error": "Rate limit reached. Please wait a moment and try again."}), 429
    except anthropic.APIStatusError as e:
        print(f"[ERROR] APIStatusError — type={type(e).__name__} status={e.status_code} body={e.body}")
        return jsonify({"error": f"Anthropic API error {e.status_code}: {e.message}"}), 502
    except Exception as e:
        print(f"[ERROR] Unexpected error — type={type(e).__name__} detail={e}")
        return jsonify({"error": f"API error: {str(e)}"}), 500


@app.route("/api/test-key")
def api_test_key():
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return jsonify({"set": False, "preview": None})
    return jsonify({"set": True, "preview": api_key[:10] + "..."})


@app.route("/api/pipeline")
def api_pipeline():
    pipeline_file = os.path.join(DATA_DIR, "pipeline.csv")
    df = pd.read_csv(pipeline_file)
    df["keys"] = df["keys"].astype(int)
    df["expected_opening"] = df["expected_opening"].astype(int)
    df["investment_mad"] = df["investment_mad"].astype(int)
    df["lat"] = df["lat"].astype(float)
    df["lng"] = df["lng"].astype(float)
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/news")
def api_news():
    articles = [a for a in load_news() if a.get("published")]
    articles.sort(key=lambda a: a.get("date", ""), reverse=True)
    return jsonify(articles)


@app.route("/api/benchmarking")
def api_benchmarking():
    if not os.path.exists(BENCH_FILE):
        return jsonify({"error": "Benchmark data not found"}), 404
    with open(BENCH_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


def load_upload_log():
    if not os.path.exists(UPLOAD_LOG_FILE):
        return []
    with open(UPLOAD_LOG_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_upload_log(log):
    with open(UPLOAD_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)


@app.route("/admin")
def admin_page():
    return render_template("admin.html")


@app.route("/admin/news", methods=["POST"])
def admin_news_create():
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    articles = load_news()
    new_id = max((a["id"] for a in articles), default=0) + 1
    article = {
        "id": new_id,
        "headline": data.get("headline", ""),
        "summary": data.get("summary", ""),
        "body": data.get("body", ""),
        "category": data.get("category", "Market"),
        "author": data.get("author", "HIQ Editorial"),
        "date": data.get("date", ""),
        "published": bool(data.get("published", False)),
    }
    articles.append(article)
    save_news(articles)
    return jsonify(article), 201


@app.route("/admin/news/<int:article_id>", methods=["PUT"])
def admin_news_update(article_id):
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    articles = load_news()
    for i, a in enumerate(articles):
        if a["id"] == article_id:
            articles[i].update({
                "headline":  data.get("headline",  a["headline"]),
                "summary":   data.get("summary",   a["summary"]),
                "body":      data.get("body",       a["body"]),
                "category":  data.get("category",  a["category"]),
                "author":    data.get("author",     a["author"]),
                "date":      data.get("date",       a["date"]),
                "published": bool(data.get("published", a["published"])),
            })
            save_news(articles)
            return jsonify(articles[i])
    return jsonify({"error": "Not found"}), 404


@app.route("/admin/news/<int:article_id>", methods=["DELETE"])
def admin_news_delete(article_id):
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    articles = load_news()
    filtered = [a for a in articles if a["id"] != article_id]
    if len(filtered) == len(articles):
        return jsonify({"error": "Not found"}), 404
    save_news(filtered)
    return jsonify({"ok": True})


@app.route("/admin/upload-performance", methods=["POST"])
def admin_upload_performance():
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    hotel_id   = data.get("hotel_id", "").strip()
    hotel_name = data.get("hotel_name", hotel_id)
    rows_raw   = data.get("rows", [])

    if not hotel_id:
        return jsonify({"error": "hotel_id required"}), 400
    if not rows_raw:
        return jsonify({"error": "No rows provided"}), 400

    required = {"date", "occupancy", "adr", "rooms_sold", "rooms_revenue"}
    validated = []
    errors = []
    for i, row in enumerate(rows_raw):
        missing = required - set(row.keys())
        if missing:
            errors.append(f"Row {i+1}: missing {', '.join(missing)}")
            continue
        try:
            validated.append({
                "hotel_id":      hotel_id,
                "date":          row["date"],
                "occupancy":     float(row["occupancy"]),
                "adr":           float(row["adr"]),
                "rooms_sold":    int(row["rooms_sold"]),
                "rooms_revenue": float(row["rooms_revenue"]),
            })
        except (ValueError, TypeError) as e:
            errors.append(f"Row {i+1}: {e}")

    if not validated:
        return jsonify({"error": "No valid rows", "details": errors}), 400

    # Write to daily_performance.csv
    file_exists = os.path.exists(DAILY_PERF_FILE)
    with open(DAILY_PERF_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["hotel_id","date","occupancy","adr","rooms_sold","rooms_revenue"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(validated)

    # Log the upload
    dates = sorted(r["date"] for r in validated)
    log = load_upload_log()
    log.insert(0, {
        "id":          len(log) + 1,
        "hotel_id":    hotel_id,
        "hotel_name":  hotel_name,
        "date_from":   dates[0],
        "date_to":     dates[-1],
        "rows":        len(validated),
        "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "errors":      errors,
    })
    save_upload_log(log[:50])  # keep last 50

    return jsonify({
        "ok": True,
        "rows_ingested": len(validated),
        "errors": errors,
        "date_range": f"{dates[0]} → {dates[-1]}",
    }), 201


@app.route("/admin/recent-uploads")
def admin_recent_uploads():
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(load_upload_log()[:20])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
