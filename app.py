from flask import Flask, jsonify, render_template, request
import pandas as pd
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


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
        "keys", "year_opened", "status", "lat", "lng",
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
    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key — check ANTHROPIC_API_KEY in your .env file."}), 401
    except anthropic.RateLimitError:
        return jsonify({"error": "Rate limit reached. Please wait a moment and try again."}), 429
    except Exception as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
