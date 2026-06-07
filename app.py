from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import anthropic
import json
import csv
import io
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "kodo-secret-2026")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["REMEMBER_COOKIE_DURATION"]   = timedelta(days=7)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message = ""

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_FILE            = os.path.join(DATA_DIR, "news.json")
BENCH_FILE           = os.path.join(DATA_DIR, "demo_benchmarking.json")
DAILY_PERF_FILE      = os.path.join(DATA_DIR, "daily_performance.csv")
UPLOAD_LOG_FILE      = os.path.join(DATA_DIR, "upload_log.json")
CONTACT_FILE         = os.path.join(DATA_DIR, "contact_submissions.json")
USERS_FILE           = os.path.join(DATA_DIR, "users.json")

TIER_ORDER = {"observer": 0, "benchmarker": 1, "advisory": 2}

_login_failures: dict = {}   # {email: {"count": int, "since": datetime}}


# ─── User model ───────────────────────────────────────────────────────────────

class User(UserMixin):
    def __init__(self, data: dict):
        self.id               = data["id"]
        self.email            = data["email"]
        self.password_hash    = data["password_hash"]
        self.name             = data.get("name", "")
        self.organisation     = data.get("organisation", "")
        self.tier             = data.get("tier", "observer")
        self.status           = data.get("status", "pending")
        self.ai_queries_used  = data.get("ai_queries_used", 0)
        self.ai_queries_reset = data.get("ai_queries_reset", "")

    def get_id(self):
        return self.id

    def is_active(self):
        return self.status == "active"


# ─── Users storage ────────────────────────────────────────────────────────────

def load_users_db() -> dict:
    if not os.path.exists(USERS_FILE):
        return {"users": []}
    with open(USERS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_users_db(db: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def find_user_by_id(uid: str) -> User | None:
    db = load_users_db()
    for u in db["users"]:
        if u["id"] == uid:
            return User(u)
    return None


def find_user_by_email(email: str) -> User | None:
    db = load_users_db()
    for u in db["users"]:
        if u["email"].lower() == email.lower():
            return User(u)
    return None


def update_user_field(uid: str, fields: dict):
    db = load_users_db()
    for u in db["users"]:
        if u["id"] == uid:
            u.update(fields)
            break
    save_users_db(db)


def ensure_seed_user():
    """Create the admin user from env vars if users.json doesn't exist or is empty."""
    email    = os.getenv("SEED_ADMIN_EMAIL", "").strip()
    password = os.getenv("SEED_ADMIN_PASS",  "").strip()
    name     = os.getenv("SEED_ADMIN_NAME",  "Admin").strip()
    if not email or not password:
        return
    db = load_users_db()
    if any(u["email"].lower() == email.lower() for u in db["users"]):
        return
    db["users"].append({
        "id":               str(uuid.uuid4()),
        "email":            email,
        "password_hash":    generate_password_hash(password),
        "name":             name,
        "organisation":     "Kōdō Hospitality",
        "tier":             "advisory",
        "status":           "active",
        "created_at":       datetime.utcnow().strftime("%Y-%m-%d"),
        "approved_at":      datetime.utcnow().strftime("%Y-%m-%d"),
        "invited_by":       "seed",
        "ai_queries_used":  0,
        "ai_queries_reset": datetime.utcnow().strftime("%Y-%m"),
    })
    save_users_db(db)
    print(f"[SEED] Created admin user: {email}")


ensure_seed_user()


@login_manager.user_loader
def load_user(uid):
    return find_user_by_id(uid)


# ─── Tier access ──────────────────────────────────────────────────────────────

def tier_required(required: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "unauthenticated"}), 401
            if TIER_ORDER.get(current_user.tier, 0) < TIER_ORDER.get(required, 0):
                labels = {"benchmarker": "Benchmarker", "advisory": "Advisory"}
                return jsonify({
                    "error": "upgrade_required",
                    "message": f"This feature requires the {labels.get(required, required)} plan",
                    "upgrade_url": "/pricing",
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def advisory_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tier != "advisory":
            return jsonify({"error": "Forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper


# ─── Existing helpers ─────────────────────────────────────────────────────────

def load_news():
    if not os.path.exists(NEWS_FILE):
        return []
    with open(NEWS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_news(articles):
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)


def load_contacts():
    if not os.path.exists(CONTACT_FILE):
        return []
    with open(CONTACT_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_contacts(contacts):
    with open(CONTACT_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


def admin_ok():
    expected = (os.getenv("ADMIN_PASSWORD") or "hiq2026").strip()
    provided = request.headers.get("X-Admin-Password", "").strip()
    return bool(provided) and provided == expected


# TEMPORARY DEBUG — remove after confirming Railway env var is correct
@app.route("/api/check-admin-password")
def debug_admin_password():
    raw = os.getenv("ADMIN_PASSWORD")
    if raw is None:
        return jsonify({"set": False, "note": "ADMIN_PASSWORD not found in environment — falling back to default 'hiq2026'"})
    stripped = raw.strip()
    return jsonify({
        "set": True,
        "length": len(stripped),
        "preview": stripped[:3] + "***",
        "had_whitespace": raw != stripped,
    })


def load_data():
    hotels = pd.read_csv(os.path.join(DATA_DIR, "hotels.csv"))
    perf   = pd.read_csv(os.path.join(DATA_DIR, "performance.csv"))
    merged = hotels.merge(perf, left_on="id", right_on="hotel_id", how="left")
    return hotels, perf, merged


# ─── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        email    = (request.form.get("email", "") or "").strip().lower()
        password = request.form.get("password", "") or ""

        # Rate-limit: 5 failures per 15 min
        rec = _login_failures.get(email, {"count": 0, "since": datetime.utcnow()})
        if rec["count"] >= 5 and (datetime.utcnow() - rec["since"]).seconds < 900:
            error = "Too many failed attempts. Please try again in 15 minutes."
        else:
            user = find_user_by_email(email)
            if user and check_password_hash(user.password_hash, password):
                if user.status not in ("active",):
                    error = "Your account is pending activation. Check your email or contact support."
                else:
                    _login_failures.pop(email, None)
                    login_user(user, remember=True)
                    next_url = request.args.get("next") or url_for("index")
                    return redirect(next_url)
            else:
                rec["count"] = rec.get("count", 0) + 1
                if rec["count"] == 1:
                    rec["since"] = datetime.utcnow()
                _login_failures[email] = rec
                error = "Incorrect email or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("landing"))


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        name     = (request.form.get("name", "") or "").strip()
        email    = (request.form.get("email", "") or "").strip().lower()
        org      = (request.form.get("organisation", "") or "").strip()
        password = request.form.get("password", "") or ""
        confirm  = request.form.get("confirm_password", "") or ""
        agreed   = request.form.get("terms") == "on"

        if not name or not email or not password:
            error = "Name, email and password are required."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif not agreed:
            error = "You must agree to the Terms of Service."
        elif find_user_by_email(email):
            error = "An account with this email already exists."
        else:
            db = load_users_db()
            db["users"].append({
                "id":               str(uuid.uuid4()),
                "email":            email,
                "password_hash":    generate_password_hash(password),
                "name":             name,
                "organisation":     org,
                "tier":             "observer",
                "status":           "pending_payment",
                "created_at":       datetime.utcnow().strftime("%Y-%m-%d"),
                "approved_at":      None,
                "invited_by":       "self",
                "ai_queries_used":  0,
                "ai_queries_reset": datetime.utcnow().strftime("%Y-%m"),
            })
            save_users_db(db)
            return redirect(url_for("payment_pending"))

    return render_template("register.html", error=error)


@app.route("/payment-pending")
def payment_pending():
    return render_template("payment_pending.html")


# ─── App routes ───────────────────────────────────────────────────────────────

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/dashboard")
@login_required
def index():
    return render_template("index.html")


@app.route("/team")
def team():
    return render_template("team.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        contacts = load_contacts()
        submission = {
            "id": len(contacts) + 1,
            "name": data.get("name", ""),
            "email": data.get("email", ""),
            "organisation": data.get("organisation", ""),
            "role": data.get("role", ""),
            "message": data.get("message", ""),
            "submitted_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }
        contacts.insert(0, submission)
        save_contacts(contacts)
        return jsonify({"ok": True}), 201
    return render_template("contact.html")


# ─── API routes ───────────────────────────────────────────────────────────────

@app.route("/api/me")
@login_required
def api_me():
    limits = {"observer": 10, "benchmarker": None, "advisory": None}
    return jsonify({
        "id":               current_user.id,
        "name":             current_user.name,
        "email":            current_user.email,
        "tier":             current_user.tier,
        "organisation":     current_user.organisation,
        "ai_queries_used":  current_user.ai_queries_used,
        "ai_queries_limit": limits.get(current_user.tier),
    })


@app.route("/api/data")
@login_required
def api_data():
    hotels, perf, merged = load_data()

    total_keys      = int(hotels["keys"].sum())
    weighted_occ    = float((merged["occupancy"] * merged["keys"]).sum() / merged["keys"].sum())
    weighted_adr    = float((merged["adr_mad"] * merged["keys"] * merged["occupancy"]).sum() /
                            (merged["keys"] * merged["occupancy"]).sum())
    weighted_revpar = float((merged["revpar_mad"] * merged["keys"]).sum() / merged["keys"].sum())
    weighted_trevpar= float((merged["trevpar_mad"] * merged["keys"]).sum() / merged["keys"].sum())
    weighted_gop    = float((merged["gop_margin"] * merged["keys"]).sum() / merged["keys"].sum())

    national_kpis = {
        "total_hotels":  len(hotels),
        "total_keys":    total_keys,
        "occupancy":     round(weighted_occ, 4),
        "adr_mad":       round(weighted_adr, 1),
        "revpar_mad":    round(weighted_revpar, 1),
        "trevpar_mad":   round(weighted_trevpar, 1),
        "gop_margin":    round(weighted_gop, 4),
    }

    city_rows = []
    for city, grp in merged.groupby("city"):
        keys_sum = grp["keys"].sum()
        city_rows.append({
            "city":        city,
            "hotel_count": len(grp),
            "total_keys":  int(keys_sum),
            "occupancy":   round(float((grp["occupancy"] * grp["keys"]).sum() / keys_sum), 4),
            "adr_mad":     round(float((grp["adr_mad"] * grp["keys"] * grp["occupancy"]).sum() /
                                       (grp["keys"] * grp["occupancy"]).sum()), 1),
            "revpar_mad":  round(float((grp["revpar_mad"] * grp["keys"]).sum() / keys_sum), 1),
            "trevpar_mad": round(float((grp["trevpar_mad"] * grp["keys"]).sum() / keys_sum), 1),
            "gop_margin":  round(float((grp["gop_margin"] * grp["keys"]).sum() / keys_sum), 4),
        })
    city_rows.sort(key=lambda x: x["total_keys"], reverse=True)

    segment_rows = []
    for seg, grp in merged.groupby("category"):
        keys_sum = grp["keys"].sum()
        segment_rows.append({
            "segment":     seg,
            "hotel_count": len(grp),
            "total_keys":  int(keys_sum),
            "occupancy":   round(float((grp["occupancy"] * grp["keys"]).sum() / keys_sum), 4),
            "adr_mad":     round(float((grp["adr_mad"] * grp["keys"] * grp["occupancy"]).sum() /
                                       (grp["keys"] * grp["occupancy"]).sum()), 1),
            "revpar_mad":  round(float((grp["revpar_mad"] * grp["keys"]).sum() / keys_sum), 1),
            "gop_margin":  round(float((grp["gop_margin"] * grp["keys"]).sum() / keys_sum), 4),
        })
    seg_order = ["Luxury", "Upper Upscale", "Upscale", "Midscale"]
    segment_rows.sort(key=lambda x: seg_order.index(x["segment"]) if x["segment"] in seg_order else 99)

    brand_rows = []
    for brand, grp in merged.groupby("brand_group"):
        keys_sum = grp["keys"].sum()
        brand_rows.append({
            "brand_group": brand,
            "hotel_count": len(grp),
            "total_keys":  int(keys_sum),
            "occupancy":   round(float((grp["occupancy"] * grp["keys"]).sum() / keys_sum), 4),
            "adr_mad":     round(float((grp["adr_mad"] * grp["keys"] * grp["occupancy"]).sum() /
                                       (grp["keys"] * grp["occupancy"]).sum()), 1),
            "revpar_mad":  round(float((grp["revpar_mad"] * grp["keys"]).sum() / keys_sum), 1),
            "gop_margin":  round(float((grp["gop_margin"] * grp["keys"]).sum() / keys_sum), 4),
        })
    brand_rows.sort(key=lambda x: x["total_keys"], reverse=True)

    return jsonify({
        "national_kpis":    national_kpis,
        "city_aggregates":  city_rows,
        "segment_breakdown": segment_rows,
        "brand_breakdown":  brand_rows,
    })


@app.route("/api/hotels")
@login_required
def api_hotels():
    _, _, merged = load_data()
    cols = [
        "id", "name", "city", "region", "category", "brand", "brand_group",
        "keys", "year_opened", "status", "lat", "lng", "owner", "data_quality",
        "period", "occupancy", "adr_mad", "revpar_mad", "trevpar_mad", "gop_margin", "source",
    ]
    # For observer tier, hide financial detail columns (still return them but frontend handles display)
    records = merged[cols].to_dict(orient="records")
    return jsonify(records)


@app.route("/api/pipeline")
@login_required
@tier_required("benchmarker")
def api_pipeline():
    pipeline_file = os.path.join(DATA_DIR, "pipeline.csv")
    df = pd.read_csv(pipeline_file)
    df["keys"]              = df["keys"].astype(int)
    df["expected_opening"]  = df["expected_opening"].astype(int)
    df["investment_mad"]    = df["investment_mad"].astype(int)
    df["lat"]               = df["lat"].astype(float)
    df["lng"]               = df["lng"].astype(float)
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/news")
@login_required
def api_news():
    articles = [a for a in load_news() if a.get("published")]
    articles.sort(key=lambda a: a.get("date", ""), reverse=True)
    return jsonify(articles)


@app.route("/api/benchmarking")
@login_required
@tier_required("benchmarker")
def api_benchmarking():
    if not os.path.exists(BENCH_FILE):
        return jsonify({"error": "Benchmark data not found"}), 404
    with open(BENCH_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/api/test-key")
@login_required
def api_test_key():
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return jsonify({"set": False, "preview": None})
    return jsonify({"set": True, "preview": api_key[:10] + "..."})


def build_system_prompt():
    hotels_df, _, merged = load_data()

    tk = merged["keys"].sum()
    ok = (merged["occupancy"] * merged["keys"]).sum()

    nat_occ    = ok / tk
    nat_adr    = (merged["adr_mad"]    * merged["keys"] * merged["occupancy"]).sum() / ok
    nat_revpar = (merged["revpar_mad"] * merged["keys"]).sum() / tk
    nat_trev   = (merged["trevpar_mad"]* merged["keys"]).sum() / tk
    nat_gop    = (merged["gop_margin"] * merged["keys"]).sum() / tk

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

    return f"""You are Kōdō Analyst, a Morocco hospitality market intelligence assistant built by Kōdō. You have exclusive access to Kōdō's proprietary database of {len(hotels_df)} branded hotels across {hotels_df['city'].nunique()} Moroccan cities.

You serve hospitality investors, operators, developers, and consultants. Provide precise, data-driven answers. Always cite specific metrics. Use MAD (Moroccan Dirhams) for all monetary values unless asked otherwise. Approximate USD/EUR conversions: 1 USD ≈ 10 MAD, 1 EUR ≈ 11 MAD. Be analytical, concise, and professional — not conversational.

══════════════════════════════════════════════════
KŌDŌ PROPRIETARY DATA — MOROCCO BRANDED HOTELS — 2025 FY ESTIMATES
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

Answer only from the data above. If asked about hotels, cities, or markets not in the Kōdō database, state clearly that the data is not available. When making comparisons, always show both sides with specific numbers."""


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    # Observer tier: 10 queries/month
    if current_user.tier == "observer":
        now_month = datetime.utcnow().strftime("%Y-%m")
        db = load_users_db()
        user_rec = next((u for u in db["users"] if u["id"] == current_user.id), None)
        if user_rec:
            if user_rec.get("ai_queries_reset", "") != now_month:
                user_rec["ai_queries_used"]  = 0
                user_rec["ai_queries_reset"] = now_month
                save_users_db(db)
            if user_rec.get("ai_queries_used", 0) >= 10:
                return jsonify({
                    "error": "upgrade_required",
                    "message": "Observer plan includes 10 AI queries per month. Upgrade to Benchmarker for unlimited access.",
                    "upgrade_url": "/pricing",
                }), 403

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

        # Increment observer query counter
        if current_user.tier == "observer":
            update_user_field(current_user.id, {
                "ai_queries_used":  (current_user.ai_queries_used or 0) + 1,
                "ai_queries_reset": datetime.utcnow().strftime("%Y-%m"),
            })

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


# ─── Admin routes ─────────────────────────────────────────────────────────────

@app.route("/admin")
@login_required
def admin_page():
    if current_user.tier != "advisory":
        return redirect(url_for("index"))
    return render_template("admin.html")


@app.route("/admin/news", methods=["POST"])
def admin_news_create():
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    articles = load_news()
    new_id = max((a["id"] for a in articles), default=0) + 1
    article = {
        "id":        new_id,
        "headline":  data.get("headline", ""),
        "summary":   data.get("summary", ""),
        "body":      data.get("body", ""),
        "category":  data.get("category", "Market"),
        "author":    data.get("author", "Kōdō Editorial"),
        "date":      data.get("date", ""),
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


# ─── Admin: user management ───────────────────────────────────────────────────

@app.route("/admin/users")
def admin_users_list():
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    db = load_users_db()
    # Strip password hashes before returning
    safe = []
    for u in db["users"]:
        safe.append({k: v for k, v in u.items() if k != "password_hash"})
    return jsonify(safe)


@app.route("/admin/users", methods=["POST"])
def admin_users_create():
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    name  = (data.get("name", "") or "").strip()
    email = (data.get("email", "") or "").strip().lower()
    org   = (data.get("organisation", "") or "").strip()
    tier  = data.get("tier", "observer")

    if not name or not email:
        return jsonify({"error": "name and email required"}), 400
    if find_user_by_email(email):
        return jsonify({"error": "Email already exists"}), 409

    temp_password = f"Kodo{uuid.uuid4().hex[:8]}!"
    print(f"[ADMIN] Created user {email} — temp password: {temp_password}")

    db = load_users_db()
    new_user = {
        "id":               str(uuid.uuid4()),
        "email":            email,
        "password_hash":    generate_password_hash(temp_password),
        "name":             name,
        "organisation":     org,
        "tier":             tier,
        "status":           "active",
        "created_at":       datetime.utcnow().strftime("%Y-%m-%d"),
        "approved_at":      datetime.utcnow().strftime("%Y-%m-%d"),
        "invited_by":       "admin",
        "ai_queries_used":  0,
        "ai_queries_reset": datetime.utcnow().strftime("%Y-%m"),
    }
    db["users"].append(new_user)
    save_users_db(db)

    result = {k: v for k, v in new_user.items() if k != "password_hash"}
    result["temp_password"] = temp_password
    return jsonify(result), 201


@app.route("/admin/users/<uid>", methods=["PUT"])
def admin_users_update(uid):
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    db   = load_users_db()
    for u in db["users"]:
        if u["id"] == uid:
            if "tier" in data and data["tier"] in TIER_ORDER:
                u["tier"] = data["tier"]
            if "status" in data and data["status"] in ("active", "suspended", "pending_payment", "pending"):
                u["status"] = data["status"]
                if data["status"] == "active" and not u.get("approved_at"):
                    u["approved_at"] = datetime.utcnow().strftime("%Y-%m-%d")
            save_users_db(db)
            return jsonify({k: v for k, v in u.items() if k != "password_hash"})
    return jsonify({"error": "Not found"}), 404


# ─── Admin: data ingestion ────────────────────────────────────────────────────

def load_upload_log():
    if not os.path.exists(UPLOAD_LOG_FILE):
        return []
    with open(UPLOAD_LOG_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_upload_log(log):
    with open(UPLOAD_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)


@app.route("/admin/upload-performance", methods=["POST"])
def admin_upload_performance():
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401

    data       = request.get_json(silent=True) or {}
    hotel_id   = data.get("hotel_id", "").strip()
    hotel_name = data.get("hotel_name", hotel_id)
    rows_raw   = data.get("rows", [])

    if not hotel_id:
        return jsonify({"error": "hotel_id required"}), 400
    if not rows_raw:
        return jsonify({"error": "No rows provided"}), 400

    required  = {"date", "occupancy", "adr", "rooms_sold", "rooms_revenue"}
    validated = []
    errors    = []
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

    file_exists = os.path.exists(DAILY_PERF_FILE)
    with open(DAILY_PERF_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["hotel_id","date","occupancy","adr","rooms_sold","rooms_revenue"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(validated)

    dates = sorted(r["date"] for r in validated)
    log   = load_upload_log()
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
    save_upload_log(log[:50])

    return jsonify({
        "ok":           True,
        "rows_ingested": len(validated),
        "errors":       errors,
        "date_range":   f"{dates[0]} → {dates[-1]}",
    }), 201


@app.route("/admin/recent-uploads")
def admin_recent_uploads():
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(load_upload_log()[:20])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
