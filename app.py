from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session, send_file
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
import subprocess
import sys
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

# ─── Scraper / occupancy model helpers (graceful import) ─────────────────────
try:
    from scraper import compute_hotel_financials
    from occupancy_model import OccupancyModel, estimate_occupancy, classify_hotel_type
    SCRAPER_MODULE_OK = True
except Exception:
    SCRAPER_MODULE_OK = False
    def compute_hotel_financials(*a, **kw): return {}
    def classify_hotel_type(*a, **kw): return 'city_business'
    OccupancyModel = None
    def estimate_occupancy(*a, **kw): return 0.60, {}

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY']                = os.environ.get('SECRET_KEY', 'kodo-dev-fallback-key-2026')
app.config['SESSION_PERMANENT']         = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['REMEMBER_COOKIE_DURATION']  = timedelta(days=30)
app.config['SESSION_COOKIE_SECURE']     = os.environ.get('FLASK_ENV') != 'development'
app.config['SESSION_COOKIE_HTTPONLY']   = True
app.config['SESSION_COOKIE_SAMESITE']   = 'Lax'

print(
    f"[CONFIG] Session: permanent={app.config.get('SESSION_PERMANENT')}, "
    f"lifetime={app.config.get('PERMANENT_SESSION_LIFETIME')}, "
    f"secure={app.config.get('SESSION_COOKIE_SECURE')}, "
    f"secret_key_set={bool(os.environ.get('SECRET_KEY'))}"
)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message = ""
login_manager.remember_cookie_duration = timedelta(days=30)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_FILE            = os.path.join(DATA_DIR, "news.json")
BENCH_FILE           = os.path.join(DATA_DIR, "demo_benchmarking.json")
DAILY_PERF_FILE      = os.path.join(DATA_DIR, "daily_performance.csv")
UPLOAD_LOG_FILE      = os.path.join(DATA_DIR, "upload_log.json")
CONTACT_FILE         = os.path.join(DATA_DIR, "contact_submissions.json")
USERS_FILE           = os.path.join(DATA_DIR, "users.json")
ORGS_FILE            = os.path.join(DATA_DIR, "organisations.json")

TIER_ORDER  = {"observer": 0, "benchmarker": 1, "advisory": 2}
PLAN_SEATS  = {"observer": 1, "benchmarker": 3, "advisory": 5}

_login_failures: dict = {}   # {email: {"count": int, "since": datetime}}

# ─── APScheduler — daily rate scraper at 03:00 Casablanca time ───────────────
try:
    import pytz as _tz
    from apscheduler.schedulers.background import BackgroundScheduler

    def _scheduled_scraper():
        scraper_path = os.path.join(DATA_DIR, 'scraper.py')
        subprocess.Popen([sys.executable, scraper_path])
        app.logger.info('Daily rate scraper triggered by scheduler')

    def _scheduled_occ_model():
        occ_path = os.path.join(DATA_DIR, 'occupancy_model.py')
        subprocess.Popen([sys.executable, occ_path])
        app.logger.info('Occupancy model triggered by scheduler')

    _scheduler = BackgroundScheduler(timezone=_tz.timezone('Africa/Casablanca'))
    _scheduler.add_job(
        func=_scheduled_scraper,
        trigger='cron',
        hour=3, minute=0,
        id='daily_rate_scraper',
        replace_existing=True,
    )
    _scheduler.add_job(
        func=_scheduled_occ_model,
        trigger='cron',
        hour=4, minute=0,
        id='daily_occ_model',
        replace_existing=True,
    )
    _scheduler.start()

    import atexit
    atexit.register(lambda: _scheduler.shutdown(wait=False))
except Exception as _e:
    _scheduler = None
    import logging as _logging
    _logging.getLogger(__name__).warning(f'APScheduler not started: {_e}')


# ─── User model ───────────────────────────────────────────────────────────────

class User(UserMixin):
    def __init__(self, data: dict):
        self.id                    = data["id"]
        self.email                 = data["email"]
        self.password_hash         = data.get("password_hash", "")
        self.name                  = data.get("name", "")
        self.organisation          = data.get("organisation", "")
        self.tier                  = data.get("tier", "observer")
        self.status                = data.get("status", "pending")
        self.ai_queries_used       = data.get("ai_queries_used", 0)
        self.ai_queries_reset      = data.get("ai_queries_reset", "")
        self.force_password_change = data.get("force_password_change", False)
        self.organisation_id       = data.get("organisation_id")
        self.role                  = data.get("role", "member")

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


# ─── Organisations storage ────────────────────────────────────────────────────

def load_orgs_db() -> dict:
    if not os.path.exists(ORGS_FILE):
        return {"organisations": []}
    with open(ORGS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_orgs_db(db: dict):
    with open(ORGS_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def find_org_by_id(org_id: str) -> dict | None:
    if not org_id:
        return None
    db = load_orgs_db()
    for o in db["organisations"]:
        if o["id"] == org_id:
            return o
    return None


def org_members(org_id: str) -> list[dict]:
    db = load_users_db()
    return [u for u in db["users"] if u.get("organisation_id") == org_id
            and u.get("status") not in ("removed",)]


def recalc_seats(org_id: str):
    if not org_id:
        return
    db = load_orgs_db()
    for o in db["organisations"]:
        if o["id"] == org_id:
            active = [m for m in org_members(org_id)
                      if m.get("status") in ("active", "invited")]
            o["seats_used"] = len(active)
            break
    save_orgs_db(db)


def effective_tier(user) -> str:
    """Org plan takes precedence over individual tier when org is active."""
    if getattr(user, "organisation_id", None):
        org = find_org_by_id(user.organisation_id)
        if org and org.get("status") == "active":
            return org["plan"]
    return user.tier


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
        "id":               str(uuid.uuid5(uuid.NAMESPACE_URL, email)),
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


def ensure_seed_org():
    """Create the default Kōdō org for the seed admin if not already present."""
    email = os.getenv("SEED_ADMIN_EMAIL", "").strip()
    if not email:
        return
    admin_user = find_user_by_email(email)
    if not admin_user:
        return
    org_db = load_orgs_db()
    # If admin already points to an existing org, nothing to do
    if admin_user.organisation_id:
        if any(o["id"] == admin_user.organisation_id for o in org_db["organisations"]):
            return
    # Reuse existing ID if admin_user has one (but org was wiped), else generate
    org_id = admin_user.organisation_id or str(uuid.uuid4())
    org_db["organisations"].append({
        "id":            org_id,
        "name":          "Kōdō Hospitality",
        "plan":          "advisory",
        "seats_total":   5,
        "seats_used":    1,
        "owner_id":      admin_user.id,
        "status":        "active",
        "created_at":    datetime.utcnow().strftime("%Y-%m-%d"),
        "billing_email": email,
    })
    save_orgs_db(org_db)
    update_user_field(admin_user.id, {"organisation_id": org_id, "role": "owner"})
    print(f"[SEED] Created org 'Kōdō Hospitality' for {email}")


ensure_seed_org()


@login_manager.user_loader
def load_user(uid):
    return find_user_by_id(uid)


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.before_request
def access_gate():
    if not current_user.is_authenticated:
        return
    # Org suspension gate
    if current_user.organisation_id:
        org = find_org_by_id(current_user.organisation_id)
        if org and org.get("status") == "suspended":
            if request.endpoint not in ("logout", "static", "login_page"):
                logout_user()
                return redirect(url_for("login_page"))
    # Force-password-change gate
    if getattr(current_user, "force_password_change", False):
        allowed = {"account_page", "account_change_password", "logout", "static"}
        if request.endpoint and request.endpoint not in allowed:
            return redirect(url_for("account_page"))


# ─── Tier access ──────────────────────────────────────────────────────────────

def tier_required(required: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "unauthenticated"}), 401
            if TIER_ORDER.get(effective_tier(current_user), 0) < TIER_ORDER.get(required, 0):
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
        if not current_user.is_authenticated or effective_tier(current_user) != "advisory":
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
                    org = find_org_by_id(user.organisation_id) if user.organisation_id else None
                    if org and org.get("status") == "suspended":
                        error = "Your organisation account has been suspended. Contact support."
                    else:
                        _login_failures.pop(email, None)
                        login_user(user, remember=True)
                        if user.force_password_change:
                            return redirect(url_for("account_page"))
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
            reg_tier = request.form.get("tier", "observer")
            if reg_tier not in ("observer", "benchmarker"):
                reg_tier = "observer"
            is_observer = reg_tier == "observer"
            new_user_data = {
                "id":               str(uuid.uuid4()),
                "email":            email,
                "password_hash":    generate_password_hash(password),
                "name":             name,
                "organisation":     org,
                "tier":             reg_tier,
                "status":           "active" if is_observer else "pending_approval",
                "created_at":       datetime.utcnow().strftime("%Y-%m-%d"),
                "approved_at":      datetime.utcnow().strftime("%Y-%m-%d") if is_observer else None,
                "invited_by":       "self",
                "ai_queries_used":  0,
                "ai_queries_reset": datetime.utcnow().strftime("%Y-%m"),
            }
            db = load_users_db()
            db["users"].append(new_user_data)
            save_users_db(db)
            if is_observer:
                login_user(User(new_user_data), remember=True)
                return redirect(url_for("index"))
            return redirect(url_for("payment_pending"))

    return render_template("register.html", error=error)


@app.route("/payment-pending")
def payment_pending():
    return render_template("payment_pending.html")


@app.route("/accept-invite", methods=["GET"])
def accept_invite_page():
    token = request.args.get("token", "").strip()
    if not token:
        return render_template("accept_invite.html", error="Invalid invite link.", org=None, invited_email="")
    db = load_users_db()
    invited = next((u for u in db["users"] if u.get("invite_token") == token), None)
    if not invited:
        return render_template("accept_invite.html", error="This invite link is invalid or has already been used.", org=None, invited_email="")
    if invited.get("invite_expires"):
        try:
            if datetime.utcnow() > datetime.strptime(invited["invite_expires"], "%Y-%m-%dT%H:%M:%S"):
                return render_template("accept_invite.html", error="This invite link has expired. Ask your organisation owner to resend it.", org=None, invited_email="")
        except ValueError:
            pass
    org = find_org_by_id(invited.get("organisation_id"))
    return render_template("accept_invite.html", error=None, org=org,
                           invited_email=invited["email"], token=token)


@app.route("/accept-invite", methods=["POST"])
def accept_invite():
    data       = request.get_json(silent=True) or {}
    token      = (data.get("token") or "").strip()
    name       = (data.get("name") or "").strip()
    password   = data.get("password", "")
    confirm_pw = data.get("confirm_password", "")

    if not token:
        return jsonify({"error": "Missing token."}), 400
    if not name:
        return jsonify({"error": "Full name is required."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400
    if password != confirm_pw:
        return jsonify({"error": "Passwords do not match."}), 400

    db = load_users_db()
    for u in db["users"]:
        if u.get("invite_token") == token:
            if u.get("invite_expires"):
                try:
                    if datetime.utcnow() > datetime.strptime(u["invite_expires"], "%Y-%m-%dT%H:%M:%S"):
                        return jsonify({"error": "Invite has expired."}), 400
                except ValueError:
                    pass
            u["name"]          = name
            u["password_hash"] = generate_password_hash(password)
            u["status"]        = "active"
            u["approved_at"]   = datetime.utcnow().strftime("%Y-%m-%d")
            u["invite_token"]  = None
            u["invite_expires"]= None
            save_users_db(db)
            recalc_seats(u.get("organisation_id"))
            login_user(User(u), remember=True)
            return jsonify({"ok": True})

    return jsonify({"error": "Invalid or already-used invite token."}), 400


# ─── App routes ───────────────────────────────────────────────────────────────

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/dashboard")
@login_required
def index():
    return render_template("index.html")


@app.route("/account")
@login_required
def account_page():
    return render_template("account.html", user=current_user)


@app.route("/account/change-password", methods=["POST"])
@login_required
def account_change_password():
    data       = request.get_json(silent=True) or {}
    current_pw = data.get("current_password", "")
    new_pw     = data.get("new_password", "")
    confirm_pw = data.get("confirm_password", "")

    if not check_password_hash(current_user.password_hash, current_pw):
        return jsonify({"error": "Current password is incorrect."}), 400
    if len(new_pw) < 8:
        return jsonify({"error": "New password must be at least 8 characters."}), 400
    if new_pw != confirm_pw:
        return jsonify({"error": "Passwords do not match."}), 400

    update_user_field(current_user.id, {
        "password_hash":         generate_password_hash(new_pw),
        "force_password_change": False,
    })
    return jsonify({"ok": True})


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


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ─── API routes ───────────────────────────────────────────────────────────────

@app.route("/api/me")
@login_required
def api_me():
    eff_tier = effective_tier(current_user)
    limits   = {"observer": 10, "benchmarker": None, "advisory": None}
    org      = find_org_by_id(current_user.organisation_id) if current_user.organisation_id else None
    return jsonify({
        "id":               current_user.id,
        "name":             current_user.name,
        "email":            current_user.email,
        "tier":             eff_tier,
        "role":             current_user.role,
        "organisation":     current_user.organisation,
        "organisation_id":  current_user.organisation_id,
        "org_name":         org["name"] if org else None,
        "ai_queries_used":  current_user.ai_queries_used,
        "ai_queries_limit": limits.get(eff_tier),
    })


# ─── Organisation API routes ──────────────────────────────────────────────────

@app.route("/api/organisation")
@login_required
def api_organisation():
    if not current_user.organisation_id:
        return jsonify({"error": "Not in an organisation"}), 404
    org = find_org_by_id(current_user.organisation_id)
    if not org:
        return jsonify({"error": "Organisation not found"}), 404
    safe_members = [
        {k: v for k, v in m.items() if k not in ("password_hash", "invite_token")}
        for m in org_members(current_user.organisation_id)
    ]
    return jsonify({"organisation": org, "members": safe_members})


@app.route("/api/organisation/members")
@login_required
def api_org_members():
    if not current_user.organisation_id:
        return jsonify([])
    safe = [
        {k: v for k, v in m.items() if k not in ("password_hash", "invite_token")}
        for m in org_members(current_user.organisation_id)
    ]
    return jsonify(safe)


@app.route("/api/organisation/invite", methods=["POST"])
@login_required
def api_org_invite():
    if not current_user.organisation_id:
        return jsonify({"error": "Not in an organisation"}), 400
    if current_user.role != "owner":
        return jsonify({"error": "Only organisation owners can invite members"}), 403
    org = find_org_by_id(current_user.organisation_id)
    if not org:
        return jsonify({"error": "Organisation not found"}), 404

    data  = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if find_user_by_email(email):
        return jsonify({"error": "A user with this email already exists"}), 409

    seats_limit = org.get("seats_total") or PLAN_SEATS.get(org["plan"], 1)
    active_count = len([m for m in org_members(current_user.organisation_id)
                        if m.get("status") in ("active", "invited")])
    if active_count >= seats_limit:
        return jsonify({"error": f"No seats available. Your plan allows {seats_limit} seats."}), 400

    token   = str(uuid.uuid4())
    expires = (datetime.utcnow() + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
    db = load_users_db()
    new_member = {
        "id":                    str(uuid.uuid4()),
        "email":                 email,
        "password_hash":         "",
        "name":                  "",
        "organisation":          org["name"],
        "organisation_id":       current_user.organisation_id,
        "role":                  "member",
        "tier":                  org["plan"],
        "status":                "invited",
        "created_at":            datetime.utcnow().strftime("%Y-%m-%d"),
        "approved_at":           None,
        "invited_by":            current_user.id,
        "invite_token":          token,
        "invite_expires":        expires,
        "ai_queries_used":       0,
        "ai_queries_reset":      datetime.utcnow().strftime("%Y-%m"),
        "force_password_change": False,
    }
    db["users"].append(new_member)
    save_users_db(db)
    recalc_seats(current_user.organisation_id)
    return jsonify({"invite_url": f"/accept-invite?token={token}", "email": email}), 201


@app.route("/api/organisation/members/<uid>", methods=["DELETE"])
@login_required
def api_org_remove_member(uid):
    if current_user.role != "owner":
        return jsonify({"error": "Only owners can remove members"}), 403
    if not current_user.organisation_id:
        return jsonify({"error": "Not in an organisation"}), 400
    if uid == current_user.id:
        return jsonify({"error": "Cannot remove yourself"}), 400
    db = load_users_db()
    for u in db["users"]:
        if u["id"] == uid and u.get("organisation_id") == current_user.organisation_id:
            if u.get("role") == "owner":
                return jsonify({"error": "Cannot remove the organisation owner"}), 400
            u["status"] = "removed"
            save_users_db(db)
            recalc_seats(current_user.organisation_id)
            return jsonify({"ok": True})
    return jsonify({"error": "Member not found in your organisation"}), 404


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
    safe = [{k: v for k, v in u.items() if k != "password_hash"} for u in db["users"]]
    safe.sort(key=lambda u: u.get("created_at") or "", reverse=True)
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
        "id":                    str(uuid.uuid4()),
        "email":                 email,
        "password_hash":         generate_password_hash(temp_password),
        "name":                  name,
        "organisation":          org,
        "tier":                  tier,
        "status":                "active",
        "created_at":            datetime.utcnow().strftime("%Y-%m-%d"),
        "approved_at":           datetime.utcnow().strftime("%Y-%m-%d"),
        "invited_by":            "admin",
        "ai_queries_used":       0,
        "ai_queries_reset":      datetime.utcnow().strftime("%Y-%m"),
        "force_password_change": True,
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
            if "status" in data and data["status"] in ("active", "suspended", "pending_payment", "pending", "pending_approval", "rejected"):
                u["status"] = data["status"]
                if data["status"] == "active" and not u.get("approved_at"):
                    u["approved_at"] = datetime.utcnow().strftime("%Y-%m-%d")
            save_users_db(db)
            return jsonify({k: v for k, v in u.items() if k != "password_hash"})
    return jsonify({"error": "Not found"}), 404


@app.route("/admin/users/<uid>/reset-password", methods=["POST"])
def admin_users_reset_password(uid):
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    db = load_users_db()
    for u in db["users"]:
        if u["id"] == uid:
            temp_password = f"Kodo{uuid.uuid4().hex[:8]}!"
            u["password_hash"] = generate_password_hash(temp_password)
            save_users_db(db)
            print(f"[ADMIN] Password reset for {u['email']}")
            return jsonify({"temp_password": temp_password})
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


# ─── Admin: organisations ─────────────────────────────────────────────────────

@app.route("/admin/organisations")
def admin_orgs_list():
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    db = load_orgs_db()
    result = []
    for o in db["organisations"]:
        owner = find_user_by_id(o.get("owner_id", ""))
        recalc_seats(o["id"])
        result.append({
            **o,
            "owner_name":  owner.name  if owner else "—",
            "owner_email": owner.email if owner else "—",
        })
    result.sort(key=lambda o: o.get("created_at") or "", reverse=True)
    return jsonify(result)


@app.route("/admin/organisations/<org_id>", methods=["PUT"])
def admin_orgs_update(org_id):
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    db   = load_orgs_db()
    for o in db["organisations"]:
        if o["id"] == org_id:
            if "seats_total" in data:
                try:
                    o["seats_total"] = max(1, int(data["seats_total"]))
                except (ValueError, TypeError):
                    return jsonify({"error": "Invalid seats_total"}), 400
            if "status" in data and data["status"] in ("active", "suspended"):
                o["status"] = data["status"]
            if "plan" in data and data["plan"] in TIER_ORDER:
                o["plan"] = data["plan"]
                udb = load_users_db()
                for u in udb["users"]:
                    if u.get("organisation_id") == org_id:
                        u["tier"] = data["plan"]
                save_users_db(udb)
            save_orgs_db(db)
            return jsonify(o)
    return jsonify({"error": "Not found"}), 404


@app.route("/admin/organisations/<org_id>/members")
def admin_org_members(org_id):
    if not admin_ok():
        return jsonify({"error": "Unauthorized"}), 401
    safe = [
        {k: v for k, v in m.items() if k not in ("password_hash", "invite_token")}
        for m in org_members(org_id)
    ]
    return jsonify(safe)


# ─── Reports ──────────────────────────────────────────────────────────────────

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False
    FPDF = None

_report_cache: dict = {}
CACHE_TTL = 86400  # 24 hours

REPORT_CITIES = [
    "Casablanca", "Rabat / Salé / Témara", "Marrakech",
    "Agadir / Taghazout", "Tanger", "Fes", "Tamuda Bay / Tétouan",
]
REPORT_PERIODS = ["Q3 2026", "Q4 2026", "Annual 2026"]

SEGMENT_ORDER = ["Ultra Luxury", "Luxury", "Upper Upscale", "Upscale", "Midscale", "Budget"]
CAP_RATES = {
    "Ultra Luxury": 0.060, "Luxury": 0.065, "Upper Upscale": 0.070,
    "Upscale": 0.075, "Midscale": 0.085, "Budget": 0.095,
}

CITY_SEASON_TYPE = {
    "Casablanca": "business", "Rabat / Salé / Témara": "business",
    "Marrakech": "cultural", "Agadir / Taghazout": "coastal",
    "Tanger": "coastal", "Fes": "cultural",
    "Tamuda Bay / Tétouan": "coastal", "Morocco": "default",
}
SEASONALITY_PROFILES = {
    "default":  [65, 65, 70, 75, 73, 70, 68, 68, 74, 80, 74, 67],
    "coastal":  [55, 58, 65, 72, 80, 88, 95, 95, 82, 72, 60, 55],
    "cultural": [72, 75, 82, 88, 80, 68, 65, 65, 78, 88, 82, 75],
    "business": [68, 70, 75, 78, 75, 72, 65, 62, 75, 82, 78, 68],
}
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ── PDF layout / colour constants ──────────────────────────────────────────────
_LM, _RM = 20, 20
_TM, _BM = 15, 15
_PW = 210 - _LM - _RM

_TERRA = (160, 104, 72)
_DARK  = (10, 10, 10)
_MUTED = (106, 106, 106)
_LGRAY = (248, 248, 248)
_BORD  = (232, 232, 232)
_WHITE = (255, 255, 255)
_GREEN = (45, 107, 58)
_AMBER = (184, 146, 42)
_RED   = (139, 58, 58)


def _s(text: str) -> str:
    """Transliterate to latin-1 safe string for fpdf2 core fonts."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", str(text))
    return "".join(c for c in nfkd if ord(c) < 256)


if FPDF is not None:
    class KodoPDF(FPDF):
        def __init__(self, city: str, period: str):
            super().__init__(orientation="P", unit="mm", format="A4")
            self.set_margins(_LM, _TM, _RM)
            self.set_auto_page_break(auto=True, margin=_BM + 8)
            self._city   = _s(city)
            self._period = _s(period)

        def add_content_page(self):
            self.add_page()

        def header(self):
            if self.page_no() <= 1:
                return
            self.set_y(8)
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*_TERRA)
            self.cell(30, 5, "KODO", ln=0)
            self.set_font("Helvetica", "", 7)
            self.set_text_color(*_MUTED)
            title = f"{self._city} Hotel Market  |  {self._period}"
            self.cell(_PW - 40, 5, title, align="C", ln=0)
            self.set_font("Helvetica", "", 7)
            self.set_text_color(*_MUTED)
            self.cell(10, 5, str(self.page_no() - 1), align="R", ln=1)
            self.set_draw_color(*_BORD)
            self.set_line_width(0.3)
            self.line(_LM, 14, 210 - _RM, 14)
            self.set_y(17)

        def footer(self):
            if self.page_no() <= 1:
                return
            self.set_y(-12)
            self.set_draw_color(*_BORD)
            self.set_line_width(0.3)
            self.line(_LM, self.get_y(), 210 - _RM, self.get_y())
            self.set_y(-10)
            self.set_font("Helvetica", "", 6)
            self.set_text_color(*_MUTED)
            self.cell(_PW, 4, "Confidential - For Kodo Subscribers Only  -  kodohospitality.com", align="C")

        def section_title(self, num: str, title: str):
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*_TERRA)
            self.cell(18, 6, num + "  |", ln=0)
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(*_DARK)
            self.cell(_PW - 18, 6, "  " + title, ln=1)
            self.set_draw_color(*_TERRA)
            self.set_line_width(0.5)
            self.line(_LM, self.get_y(), _LM + 40, self.get_y())
            self.ln(4)

        def body_text(self, txt: str, w: float = 0):
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*_DARK)
            self.multi_cell(w or _PW, 5, _s(txt), ln=1)
            self.ln(2)

        def kpi_row(self, label: str, value: str):
            self.set_font("Helvetica", "", 8)
            self.set_text_color(*_MUTED)
            self.cell(_PW * 0.55, 6, label, ln=0)
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*_DARK)
            self.cell(_PW * 0.45, 6, value, align="R", ln=1)
            self.set_draw_color(*_BORD)
            self.set_line_width(0.2)
            self.line(_LM, self.get_y(), _LM + _PW, self.get_y())

        def table_header(self, cols: list, widths: list):
            self.set_fill_color(*_DARK)
            self.set_text_color(*_WHITE)
            self.set_font("Helvetica", "B", 7)
            for col, w in zip(cols, widths):
                align = "R" if col not in ("Segment", "Hotel", "Name", "Brand", "Category",
                                            "Owner", "Brand Group", "Status") else "L"
                self.cell(w, 6, col, border=0, fill=True, align=align)
            self.ln()

        def table_row(self, vals: list, widths: list, fill: bool = False, bold: bool = False):
            self.set_fill_color(*(_LGRAY if fill else _WHITE))
            self.set_text_color(*_DARK)
            self.set_font("Helvetica", "B" if bold else "", 7)
            for i, (v, w) in enumerate(zip(vals, widths)):
                align = "L" if i == 0 else "R"
                self.cell(w, 5.5, _s(str(v)), border=0, fill=True, align=align)
            self.ln()

        def bar_chart(self, items: list, label_key: str, value_key: str,
                      max_val: float, bar_h: float = 4.5, bar_max_w: float = 80):
            for i, item in enumerate(items[:8]):
                label = _s(str(item[label_key]))[:30]
                val   = item[value_key]
                pct   = val / max_val if max_val else 0
                bw    = bar_max_w * pct
                self.set_font("Helvetica", "", 7)
                self.set_text_color(*_DARK)
                self.cell(60, bar_h, label, ln=0)
                self.set_fill_color(*_TERRA)
                self.rect(self.get_x(), self.get_y() + 0.8, max(bw, 1), bar_h - 1.6, "F")
                self.set_x(self.get_x() + bar_max_w + 2)
                self.set_font("Helvetica", "B", 7)
                self.set_text_color(*_MUTED)
                self.cell(18, bar_h, f"{val:,}", align="R", ln=1)

        def rating_box(self, rating: str):
            color = _GREEN if rating == "OUTPERFORM" else (_RED if rating == "UNDERPERFORM" else _AMBER)
            bx = _LM + _PW - 55
            by = self.get_y()
            self.set_fill_color(*color)
            self.rect(bx, by, 55, 12, "F")
            self.set_xy(bx, by + 2)
            self.set_font("Helvetica", "", 6)
            self.set_text_color(*_WHITE)
            self.cell(55, 4, "MARKET RATING", align="C", ln=1)
            self.set_x(bx)
            self.set_font("Helvetica", "B", 9)
            self.cell(55, 5, rating, align="C", ln=1)
            self.ln(2)

        def risk_item(self, num: int, text: str, color: tuple):
            x, y = self.get_x(), self.get_y()
            self.set_fill_color(*color)
            self.rect(x, y, 2, 10, "F")
            self.set_xy(x + 4, y)
            self.set_font("Helvetica", "B", 7)
            self.set_text_color(*color)
            self.cell(8, 5, f"0{num}", ln=0)
            self.set_font("Helvetica", "", 7)
            self.set_text_color(*_DARK)
            self.multi_cell(_PW - 12, 5, _s(text), ln=1)
            self.ln(1)

        def kpi_boxes(self, items: list):
            n  = len(items)
            bw = _PW / n
            bh = 18
            by = self.get_y()
            for i, (label, value) in enumerate(items):
                bx = _LM + i * bw
                self.set_fill_color(*_LGRAY)
                self.set_draw_color(*_BORD)
                self.rect(bx, by, bw - 1, bh, "FD")
                self.set_xy(bx + 2, by + 3)
                self.set_font("Helvetica", "B", 11)
                self.set_text_color(*_DARK)
                self.cell(bw - 4, 7, str(value), align="C", ln=1)
                self.set_x(bx + 2)
                self.set_font("Helvetica", "", 6)
                self.set_text_color(*_MUTED)
                self.cell(bw - 4, 4, label, align="C", ln=1)
            self.set_y(by + bh + 3)

else:
    KodoPDF = None


def compute_city_report_data(city: str, period: str) -> dict:
    _, _, merged = load_data()
    pipeline_df = pd.read_csv(os.path.join(DATA_DIR, "pipeline.csv"))

    if city == "Morocco":
        ch = merged.copy()
        cp = pipeline_df.copy()
    else:
        ch = merged[merged["city"] == city].copy()
        cp = pipeline_df[pipeline_df["city"] == city].copy()

    ch = ch.dropna(subset=["occupancy", "adr_mad", "revpar_mad"])

    # ── market overview ──
    total_hotels = len(ch)
    total_keys   = int(ch["keys"].sum())

    keys_by_seg = {}
    for seg in SEGMENT_ORDER:
        k = int(ch[ch["category"] == seg]["keys"].sum())
        if k > 0:
            keys_by_seg[seg] = k

    brand_stats = []
    for bg, g in ch.groupby("brand_group"):
        brand_stats.append({
            "name": bg, "hotels": len(g), "keys": int(g["keys"].sum()),
            "market_share": round(int(g["keys"].sum()) / total_keys * 100, 1) if total_keys else 0,
        })
    brand_stats.sort(key=lambda x: -x["keys"])

    owner_stats = []
    for ow, g in ch.groupby("owner"):
        owner_stats.append({
            "owner": ow, "hotels": len(g), "keys": int(g["keys"].sum()),
            "market_share": round(int(g["keys"].sum()) / total_keys * 100, 1) if total_keys else 0,
        })
    owner_stats.sort(key=lambda x: -x["keys"])

    avg_yr = round(ch["year_opened"].mean(), 0) if not ch.empty else 0
    newest = ch.loc[ch["year_opened"].idxmax(), "name"] if not ch.empty else "—"
    oldest = ch.loc[ch["year_opened"].idxmin(), "name"] if not ch.empty else "—"

    # ── performance ──
    def wavg(col, weight_col="keys"):
        w = ch[weight_col].fillna(0)
        if w.sum() == 0:
            return 0.0
        return float((ch[col] * w).sum() / w.sum())

    overall_occ  = wavg("occupancy")
    overall_adr  = wavg("adr_mad")
    overall_rev  = wavg("revpar_mad")
    overall_gop  = wavg("gop_margin")
    overall_trev = wavg("trevpar_mad")

    seg_perf = []
    for seg in SEGMENT_ORDER:
        sg = ch[ch["category"] == seg]
        if sg.empty:
            continue
        w = sg["keys"].fillna(0)
        ws = w.sum()
        def swavg(col):
            return float((sg[col] * w).sum() / ws) if ws > 0 else 0.0
        s_rev = swavg("revpar_mad")
        seg_perf.append({
            "segment": seg, "hotels": len(sg), "keys": int(sg["keys"].sum()),
            "occupancy": swavg("occupancy"), "adr": swavg("adr_mad"),
            "revpar": s_rev, "gop_margin": swavg("gop_margin"),
            "trevpar": swavg("trevpar_mad"),
            "revpar_index": round(s_rev / overall_rev * 100, 1) if overall_rev else 100,
        })

    top10 = ch.nlargest(min(10, len(ch)), "revpar_mad")[
        ["name", "category", "keys", "occupancy", "adr_mad", "revpar_mad"]
    ].to_dict(orient="records")

    est_rooms_rev = total_keys * 365 * overall_rev / 1_000_000
    est_total_rev = total_keys * 365 * overall_trev / 1_000_000
    est_gop       = est_total_rev * overall_gop

    # ── pipeline ──
    pip_projects = []
    for _, r in cp.iterrows():
        pip_projects.append({
            "name": r.get("name",""), "brand": r.get("brand",""),
            "category": r.get("category",""), "keys": int(r.get("keys",0)),
            "opening": int(r.get("expected_opening",0)),
            "status": r.get("status",""), "investment_mad": int(r.get("investment_mad",0)),
        })
    pip_projects.sort(key=lambda x: x["opening"])

    pip_total_keys = sum(p["keys"] for p in pip_projects)
    pip_total_inv  = sum(p["investment_mad"] for p in pip_projects) / 1_000_000_000
    pip_by_year: dict = {}
    for p in pip_projects:
        yr = str(p["opening"])
        pip_by_year[yr] = pip_by_year.get(yr, 0) + p["keys"]

    ratio = pip_total_keys / total_keys if total_keys else 0
    supply_risk = "High" if ratio > 0.20 else ("Medium" if ratio > 0.10 else "Low")

    # ── asset values ──
    asset_rows = []
    for sp in seg_perf:
        cap         = CAP_RATES.get(sp["segment"], 0.075)
        annual_trev = sp["trevpar"] * 365
        ebitda_per_key   = annual_trev * sp["gop_margin"]
        ffe_per_key      = annual_trev * 0.035
        mgmt_per_key     = annual_trev * 0.025
        noi_per_key      = ebitda_per_key - ffe_per_key - mgmt_per_key
        value_per_key_mad_m = (noi_per_key / cap) / 1_000_000 if cap else 0
        asset_rows.append({
            "segment":         sp["segment"],
            "revpar":          sp["revpar"],
            "ebitda_per_key":  ebitda_per_key,
            "ffe_per_key":     ffe_per_key,
            "mgmt_per_key":    mgmt_per_key,
            "noi_per_key":     noi_per_key,
            "cap_rate":        cap,
            "value_per_key":   value_per_key_mad_m,
        })

    # ── seasonality ──
    season_type = CITY_SEASON_TYPE.get(city, "default")
    season_vals = SEASONALITY_PROFILES[season_type]

    # ── hotel directory ──
    dir_cols = ["name", "brand_group", "category", "keys", "year_opened",
                "owner", "occupancy", "adr_mad", "revpar_mad"]
    directory = ch[dir_cols].sort_values("revpar_mad", ascending=False).to_dict(orient="records")

    return {
        "city": city, "period": period,
        "generated_at": datetime.utcnow(),
        "generated_date": datetime.utcnow().strftime("%d %B %Y"),
        "market_overview": {
            "total_hotels": total_hotels, "total_keys": total_keys,
            "keys_by_segment": keys_by_seg, "brand_groups": brand_stats[:8],
            "ownership": owner_stats[:6], "avg_year_opened": int(avg_yr),
            "newest_hotel": newest, "oldest_hotel": oldest,
        },
        "performance": {
            "overall": {
                "occupancy": overall_occ, "adr": overall_adr,
                "revpar": overall_rev, "gop_margin": overall_gop, "trevpar": overall_trev,
            },
            "by_segment": seg_perf,
            "top_10_revpar": top10,
            "est_rooms_revenue_mad_m": round(est_rooms_rev, 1),
            "est_total_revenue_mad_m": round(est_total_rev, 1),
            "est_gop_mad_m": round(est_gop, 1),
        },
        "pipeline": {
            "projects": pip_projects, "total_projects": len(pip_projects),
            "total_keys": pip_total_keys, "total_investment_mad_b": round(pip_total_inv, 2),
            "by_year": pip_by_year, "supply_risk": supply_risk,
        },
        "asset_values": asset_rows,
        "seasonality": {"months": MONTHS, "values": season_vals},
        "directory": directory,
    }


def generate_ai_narrative(report_data: dict) -> dict:
    placeholder = {
        "executive_summary": "The market demonstrates resilient performance fundamentals, supported by continued demand from both leisure and corporate segments. Key indicators reflect stable occupancy trends and improving rate discipline across branded properties. The competitive landscape continues to evolve with measured supply additions that maintain market equilibrium.",
        "market_commentary": "Supply dynamics remain disciplined, with limited new inventory entering the market over the near term. Demand drivers include growing inbound tourism, domestic corporate travel, and expanding MICE activity. Upper upscale and luxury segments outperform on a RevPAR index basis, reflecting the premium positioning of recently opened branded properties. Midscale and budget segments provide volume support to overall market occupancy.",
        "investment_perspective": "The market presents compelling risk-adjusted returns for institutional investors, supported by stable cash flow generation and improving operational efficiency. Asset values benefit from a constrained development pipeline and growing brand presence. Cap rate compression is anticipated in the luxury segment as institutional capital targets quality branded assets.",
        "key_demand_drivers": [
            "Growing inbound leisure tourism from European and Gulf source markets, supported by improving air route connectivity",
            "Expanding domestic corporate travel and MICE activity driven by ongoing business investment in the region",
            "Government-backed infrastructure investment and national tourism promotion programmes supporting long-term demand growth",
        ],
        "key_risks": [
            "Currency volatility and MAD exchange rate fluctuations may impact international visitor spending and operator profitability",
            "New supply pipeline, while currently constrained, could create localised pockets of oversupply in specific segments",
            "Global macroeconomic uncertainty and potential slowdown in European source markets may moderate leisure demand growth",
        ],
        "key_opportunities": [
            "Premium leisure demand from European and Gulf markets creates significant upside for luxury and upper upscale positioning",
            "Infrastructure investment and improving air connectivity support sustained demand growth across segments",
            "Limited branded midscale supply relative to demand presents development opportunities with strong stabilised returns",
        ],
    }

    try:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            return placeholder

        city    = report_data["city"]
        period  = report_data["period"]
        perf    = report_data["performance"]["overall"]
        mo      = report_data["market_overview"]
        pip     = report_data["pipeline"]

        prompt = f"""You are a senior hotel market analyst at Kōdō, Morocco's leading hospitality intelligence firm. Write institutional-grade market analysis in the style of JLL Hotels & Hospitality or Deloitte Real Estate. Be precise, data-driven, and professional. Use MAD for currency.

Market: {city} Hotel Market | Period: {period}
Total Hotels: {mo['total_hotels']} | Total Keys: {mo['total_keys']:,}
Avg Occupancy: {perf['occupancy']*100:.1f}% | Avg ADR: MAD {perf['adr']:,.0f} | Avg RevPAR: MAD {perf['revpar']:,.0f} | Avg GOP Margin: {perf['gop_margin']*100:.1f}%
Pipeline: {pip['total_projects']} projects, {pip['total_keys']:,} keys, Supply Risk: {pip['supply_risk']}
Est. Total Revenue: MAD {report_data['performance']['est_total_revenue_mad_m']:.0f}M | Est. GOP: MAD {report_data['performance']['est_gop_mad_m']:.0f}M

Generate a JSON response with exactly these keys:
- "executive_summary": 140-160 word paragraph, overall market health and key trends
- "market_commentary": 190-210 word paragraph, supply dynamics and demand drivers
- "investment_perspective": 140-160 word paragraph, asset values and investment attractiveness
- "key_demand_drivers": array of exactly 3 strings, each a one-sentence specific demand driver for this market
- "key_risks": array of exactly 3 strings, each a one-sentence specific risk
- "key_opportunities": array of exactly 3 strings, each a one-sentence specific opportunity

Return ONLY valid JSON, no markdown fences."""

        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        import json as _json
        text = msg.content[0].text.strip()
        return _json.loads(text)
    except Exception as e:
        app.logger.warning(f"AI narrative generation failed: {e}")
        return placeholder


def generate_pdf_report(data: dict, ai_narrative: dict) -> bytes:
    """Build a professional A4 PDF report using fpdf2."""
    mo     = data["market_overview"]
    perf   = data["performance"]
    pip    = data["pipeline"]
    ai     = ai_narrative
    city   = data["city"]
    period = data["period"]
    rating = data.get("market_rating", "NEUTRAL")

    pdf = KodoPDF(city, period)

    # ─── COVER PAGE ───────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(*_DARK)
    pdf.rect(0, 0, 210, 117, "F")
    pdf.set_xy(_LM, 28)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*_WHITE)
    pdf.cell(0, 12, "KODO", ln=1)
    pdf.set_x(_LM)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_TERRA)
    pdf.cell(0, 5, "HOSPITALITY INTELLIGENCE", ln=1)
    pdf.set_draw_color(*_TERRA)
    pdf.set_line_width(0.8)
    pdf.line(_LM, 60, _LM + 50, 60)
    pdf.set_xy(_LM, 126)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(*_DARK)
    pdf.cell(0, 14, _s(city), ln=1)
    pdf.set_x(_LM)
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(*_MUTED)
    pdf.cell(0, 8, "Hotel Market Report  |  " + _s(period), ln=1)
    pdf.ln(8)
    o = perf["overall"]
    pdf.kpi_boxes([
        ("Total Hotels",  str(mo["total_hotels"])),
        ("Total Keys",    f"{mo['total_keys']:,}"),
        ("Avg Occupancy", f"{o['occupancy']*100:.0f}%"),
        ("Avg RevPAR",    f"MAD {o['revpar']:,.0f}"),
    ])
    pdf.set_xy(_LM, 275)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*_MUTED)
    pdf.cell(_PW, 5, "Confidential - For Kodo Subscribers Only  -  kodohospitality.com", align="C")

    # ─── S1: EXECUTIVE SUMMARY ───────────────────────────────────────────────
    pdf.add_content_page()
    pdf.section_title("01", "EXECUTIVE SUMMARY")
    pdf.body_text(ai.get("executive_summary", ""))
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_DARK)
    pdf.cell(_PW, 5, "Market at a Glance", ln=1)
    pdf.ln(1)
    pdf.kpi_row("Total Hotels", str(mo["total_hotels"]))
    pdf.kpi_row("Total Keys", f"{mo['total_keys']:,}")
    pdf.kpi_row("Weighted Avg Occupancy", f"{o['occupancy']*100:.1f}%")
    pdf.kpi_row("Weighted Avg ADR", f"MAD {o['adr']:,.0f}")
    pdf.kpi_row("Weighted Avg RevPAR", f"MAD {o['revpar']:,.0f}")
    pdf.kpi_row("Weighted Avg GOP Margin", f"{o['gop_margin']*100:.1f}%")
    pdf.ln(6)
    pdf.rating_box(rating)

    # ─── S2: MARKET OVERVIEW ─────────────────────────────────────────────────
    pdf.add_content_page()
    pdf.section_title("02", "MARKET OVERVIEW")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_DARK)
    pdf.cell(_PW, 5, "Supply Breakdown by Segment", ln=1)
    pdf.ln(1)
    cols = ["Segment", "Hotels", "Keys", "Mkt Share %", "Avg Year"]
    cw   = [60, 25, 30, 35, 20]
    pdf.table_header(cols, cw)
    total_keys_mo = mo["total_keys"] or 1
    for i, sp in enumerate(perf["by_segment"]):
        seg_keys = sp["keys"]
        seg_yr   = ""
        ch_seg = [h for h in data["directory"] if h.get("category") == sp["segment"]]
        if ch_seg:
            yrs = [h.get("year_opened", 0) for h in ch_seg if h.get("year_opened")]
            seg_yr = str(int(sum(yrs) / len(yrs))) if yrs else ""
        pdf.table_row([
            sp["segment"], sp["hotels"], f"{seg_keys:,}",
            f"{seg_keys/total_keys_mo*100:.1f}%", seg_yr,
        ], cw, fill=(i % 2 == 1))
    pdf.ln(6)

    brands = mo["brand_groups"]
    if brands:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_DARK)
        pdf.cell(_PW, 5, "Brand Group Distribution (by Keys)", ln=1)
        pdf.ln(1)
        pdf.bar_chart(brands, "name", "keys", brands[0]["keys"] or 1)
        pdf.ln(4)

    owners = mo["ownership"]
    if owners:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_DARK)
        pdf.cell(_PW, 5, "Ownership Structure (by Keys)", ln=1)
        pdf.ln(1)
        pdf.bar_chart(owners, "owner", "keys", owners[0]["keys"] or 1)

    # ─── S3: PERFORMANCE ANALYSIS ────────────────────────────────────────────
    pdf.add_content_page()
    pdf.section_title("03", "PERFORMANCE ANALYSIS")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_DARK)
    pdf.cell(_PW, 5, "Performance by Segment", ln=1)
    pdf.ln(1)
    cols = ["Segment", "Hotels", "Occ %", "ADR (MAD)", "RevPAR", "GOP %", "Index"]
    cw   = [48, 18, 18, 24, 24, 18, 20]
    pdf.table_header(cols, cw)
    for i, sp in enumerate(perf["by_segment"]):
        pdf.table_row([
            sp["segment"], sp["hotels"],
            f"{sp['occupancy']*100:.1f}%",
            f"{sp['adr']:,.0f}",
            f"{sp['revpar']:,.0f}",
            f"{sp['gop_margin']*100:.1f}%",
            f"{sp['revpar_index']:.0f}",
        ], cw, fill=(i % 2 == 1))
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_DARK)
    pdf.cell(_PW, 5, "Top Hotels by RevPAR", ln=1)
    pdf.ln(1)
    cols = ["Name", "Category", "Keys", "Occ %", "ADR", "RevPAR"]
    cw   = [58, 32, 16, 16, 22, 22]
    pdf.table_header(cols, cw)
    for i, h in enumerate(perf["top_10_revpar"]):
        pdf.table_row([
            str(h.get("name", ""))[:35],
            h.get("category", ""),
            f"{int(h.get('keys', 0)):,}",
            f"{h.get('occupancy', 0)*100:.1f}%",
            f"{h.get('adr_mad', 0):,.0f}",
            f"{h.get('revpar_mad', 0):,.0f}",
        ], cw, fill=(i % 2 == 1))
    pdf.ln(5)

    pdf.kpi_boxes([
        ("Est. Rooms Revenue", f"MAD {perf['est_rooms_revenue_mad_m']:.0f}M"),
        ("Est. Total Revenue",  f"MAD {perf['est_total_revenue_mad_m']:.0f}M"),
        ("Est. GOP",            f"MAD {perf['est_gop_mad_m']:.0f}M"),
    ])

    # ─── S4: DEMAND DRIVERS ──────────────────────────────────────────────────
    pdf.add_content_page()
    pdf.section_title("04", "DEMAND DRIVERS")
    pdf.body_text(ai.get("market_commentary", ""))
    pdf.ln(2)

    demand_drivers = ai.get("key_demand_drivers", [])
    if demand_drivers:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_DARK)
        pdf.cell(_PW, 5, "Key Demand Drivers", ln=1)
        pdf.ln(1)
        for i, driver in enumerate(demand_drivers[:3]):
            pdf.risk_item(i + 1, driver, _TERRA)
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_DARK)
    pdf.cell(_PW, 5, "Seasonality Index (Estimated Occupancy %)", ln=1)
    pdf.ln(1)
    months = data["seasonality"]["months"]
    vals   = data["seasonality"]["values"]
    cw_s   = [_PW / 12] * 12
    pdf.table_header(months, cw_s)
    pdf.set_fill_color(*_LGRAY)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*_DARK)
    for v in vals:
        pdf.cell(_PW / 12, 5.5, str(v), fill=True, align="C")
    pdf.ln()

    # ─── S5: PIPELINE ────────────────────────────────────────────────────────
    pdf.add_content_page()
    pdf.section_title("05", "PIPELINE & SUPPLY OUTLOOK")
    if pip["projects"]:
        cols = ["Name", "Brand", "Category", "Keys", "Opening", "Status", "Inv (MMAD)"]
        cw   = [48, 28, 28, 14, 16, 22, 14]
        pdf.table_header(cols, cw)
        for i, p in enumerate(pip["projects"]):
            inv_m = f"{p['investment_mad']//1_000_000:,}" if p.get("investment_mad") else "-"
            pdf.table_row([
                str(p.get("name", ""))[:28],
                str(p.get("brand", ""))[:16],
                p.get("category", ""),
                f"{p['keys']:,}",
                str(p.get("opening", "")),
                p.get("status", ""),
                inv_m,
            ], cw, fill=(i % 2 == 1))
        pdf.ln(4)
    else:
        pdf.body_text("No pipeline projects currently tracked for this market.")
        pdf.ln(2)

    risk_col = _GREEN if pip["supply_risk"] == "Low" else (_RED if pip["supply_risk"] == "High" else _AMBER)
    pdf.set_fill_color(*risk_col)
    pdf.set_text_color(*_WHITE)
    bx, by = _LM, pdf.get_y()
    pdf.rect(bx, by, _PW, 14, "F")
    pdf.set_xy(bx, by + 2)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(_PW, 4, "SUPPLY RISK ASSESSMENT", align="C", ln=1)
    pdf.set_x(bx)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(_PW, 5, pip["supply_risk"].upper(), align="C", ln=1)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*_MUTED)
    ratio_pct = (pip["total_keys"] / mo["total_keys"] * 100) if mo["total_keys"] else 0
    pdf.cell(_PW, 5,
        f"{pip['total_projects']} projects  |  {pip['total_keys']:,} keys in pipeline  "
        f"|  {ratio_pct:.1f}% of existing supply",
        align="C", ln=1)

    # ─── S6: INVESTMENT PERSPECTIVE ──────────────────────────────────────────
    pdf.add_content_page()
    pdf.section_title("06", "INVESTMENT PERSPECTIVE")
    pdf.body_text(ai.get("investment_perspective", ""))
    pdf.ln(2)

    if data["asset_values"]:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_DARK)
        pdf.cell(_PW, 5, "Indicative Asset Value Estimates (NOI-based)", ln=1)
        pdf.ln(1)
        cols = ["Segment", "RevPAR", "EBITDA/Key", "FF&E/Key", "Mgmt/Key", "NOI/Key", "Cap", "Value/Key (MMAD)"]
        cw   = [34, 20, 22, 18, 18, 22, 14, 22]
        pdf.table_header(cols, cw)
        for i, av in enumerate(data["asset_values"]):
            pdf.table_row([
                av["segment"],
                f"{av['revpar']:,.0f}",
                f"{av['ebitda_per_key']:,.0f}",
                f"({av['ffe_per_key']:,.0f})",
                f"({av['mgmt_per_key']:,.0f})",
                f"{av['noi_per_key']:,.0f}",
                f"{av['cap_rate']*100:.1f}%",
                f"{av['value_per_key']:.2f}",
            ], cw, fill=(i % 2 == 1))
        pdf.ln(5)

    risks = ai.get("key_risks", [])
    opps  = ai.get("key_opportunities", [])
    if risks:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_DARK)
        pdf.cell(_PW, 5, "Key Risks", ln=1)
        pdf.ln(1)
        for i, r in enumerate(risks[:3]):
            pdf.risk_item(i + 1, r, _RED)
    pdf.ln(2)
    if opps:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_DARK)
        pdf.cell(_PW, 5, "Key Opportunities", ln=1)
        pdf.ln(1)
        for i, op in enumerate(opps[:3]):
            pdf.risk_item(i + 1, op, _GREEN)

    # ─── S7: HOTEL DIRECTORY ────────────────────────────────────────────────
    pdf.add_content_page()
    pdf.section_title("07", "HOTEL DIRECTORY")
    cols = ["Name", "Brand Group", "Category", "Keys", "Yr", "Occ %", "ADR", "RevPAR"]
    cw   = [50, 30, 28, 14, 12, 14, 18, 18]
    pdf.set_font("Helvetica", "", 6)
    pdf.set_auto_page_break(auto=True, margin=_BM + 8)
    pdf.table_header(cols, cw)
    for i, h in enumerate(data["directory"]):
        occ = h.get("occupancy") or 0
        pdf.table_row([
            str(h.get("name", ""))[:32],
            str(h.get("brand_group", ""))[:18],
            h.get("category", ""),
            f"{int(h.get('keys', 0)):,}",
            str(int(h.get("year_opened", 0))) if h.get("year_opened") else "-",
            f"{occ*100:.0f}%",
            f"{h.get('adr_mad', 0):,.0f}",
            f"{h.get('revpar_mad', 0):,.0f}",
        ], cw, fill=(i % 2 == 1))

    # ─── BACK PAGE ───────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(*_DARK)
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_xy(0, 110)
    pdf.set_font("Helvetica", "B", 48)
    pdf.set_text_color(*_WHITE)
    pdf.cell(210, 20, "KODO", align="C", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*_TERRA)
    pdf.cell(210, 8, "HOSPITALITY INTELLIGENCE", align="C", ln=1)
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(210, 6, "kodohospitality.com", align="C", ln=1)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(210, 5, f"Generated {data['generated_date']}  |  Confidential", align="C", ln=1)

    return bytes(pdf.output())


@app.route("/api/reports/available")
@login_required
def api_reports_available():
    _, _, merged = load_data()
    city_meta = []
    for c in REPORT_CITIES:
        ch = merged[merged["city"] == c]
        city_meta.append({"city": c, "hotels": len(ch), "keys": int(ch["keys"].sum())})
    # national
    city_meta.append({"city": "Morocco", "hotels": len(merged), "keys": int(merged["keys"].sum())})
    return jsonify({"cities": city_meta, "periods": REPORT_PERIODS, "national": True})


@app.route("/api/reports/generate", methods=["POST"])
@login_required
@tier_required("benchmarker")
def api_reports_generate():
    if not PDF_AVAILABLE:
        return jsonify({"error": "PDF generation temporarily unavailable", "fallback": True}), 503

    body   = request.get_json(silent=True) or {}
    city   = body.get("city", "").strip()
    period = body.get("period", "").strip()

    valid_cities = REPORT_CITIES + ["Morocco"]
    if city not in valid_cities:
        return jsonify({"error": f"Unknown city: {city}"}), 400
    if period not in REPORT_PERIODS:
        return jsonify({"error": f"Unknown period: {period}"}), 400

    safe_city   = city.replace(" / ", "-").replace(" ", "-")
    safe_period = period.replace(" ", "-")
    filename    = f"Kodo_{safe_city}_{safe_period}.pdf"

    cache_key = f"{city}|{period}"
    now = datetime.utcnow().timestamp()
    if cache_key in _report_cache:
        cached_pdf, cached_at = _report_cache[cache_key]
        if now - cached_at < CACHE_TTL:
            buf = io.BytesIO(cached_pdf)
            buf.seek(0)
            return send_file(buf, mimetype="application/pdf",
                             as_attachment=True, download_name=filename)

    try:
        app.logger.info(f"Generating report: {city} | {period}")
        report_data = compute_city_report_data(city, period)
        narrative   = generate_ai_narrative(report_data)

        _, _, merged = load_data()
        national_revpar = float(merged["revpar_mad"].mean()) if not merged.empty else 1
        city_revpar     = report_data["performance"]["overall"]["revpar"]
        if city_revpar >= national_revpar * 1.10:
            report_data["market_rating"] = "OUTPERFORM"
        elif city_revpar <= national_revpar * 0.90:
            report_data["market_rating"] = "UNDERPERFORM"
        else:
            report_data["market_rating"] = "NEUTRAL"

        pdf_bytes = generate_pdf_report(report_data, narrative)
        _report_cache[cache_key] = (pdf_bytes, now)

        buf = io.BytesIO(pdf_bytes)
        buf.seek(0)
        return send_file(buf, mimetype="application/pdf",
                         as_attachment=True, download_name=filename)
    except Exception as e:
        app.logger.error(f"Report generation error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ─── Rate Intelligence API ────────────────────────────────────────────────────

RATES_CSV_PATH    = os.path.join(DATA_DIR, 'scraped_rates.csv')
SCRAPER_LOG_PATH  = os.path.join(DATA_DIR, 'scraper_log.json')
PROGRESS_PATH     = os.path.join(DATA_DIR, 'scraper_progress.json')
SCRAPER_LOG_TXT   = os.path.join(DATA_DIR, 'scraper_log.txt')
OCCUPANCY_CSV_PATH = os.path.join(DATA_DIR, 'estimated_occupancy.csv')


def _read_rates_csv():
    rows = []
    if not os.path.exists(RATES_CSV_PATH):
        return rows
    try:
        with open(RATES_CSV_PATH, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
    except Exception:
        pass
    return rows


def _write_rates_csv(rows):
    if not rows:
        return
    fieldnames = [
        'hotel_id', 'hotel_name', 'city', 'scrape_date', 'stay_date',
        'rate_mad', 'rate_eur', 'source', 'data_quality', 'rooms_left',
        'availability_signal', 'scrape_status',
    ]
    with open(RATES_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


@app.route('/api/rates')
@login_required
def api_rates():
    hotel_id = request.args.get('hotel_id', '').strip()
    city     = request.args.get('city', '').strip()
    days     = int(request.args.get('days', 30))

    rows = _read_rates_csv()
    today = datetime.utcnow()
    cutoff = (today - timedelta(days=days)).strftime('%Y-%m-%d')

    filtered = [r for r in rows if r.get('scrape_date', '') >= cutoff]
    if hotel_id:
        filtered = [r for r in filtered if str(r.get('hotel_id', '')) == str(hotel_id)]
    elif city:
        filtered = [r for r in filtered if r.get('city', '').lower() == city.lower()]

    filtered.sort(key=lambda r: r.get('stay_date', ''))

    # If no scraped data, fall back to estimated rates from performance.csv
    if not filtered and hotel_id:
        try:
            hotels_df, perf_df, merged = load_data()
            h_row = merged[merged['id'].astype(str) == str(hotel_id)]
            if not h_row.empty:
                h = h_row.iloc[0]
                adr = float(h.get('adr_mad', 0) or 0)
                for offset in [1, 7, 14, 21, 30]:
                    stay = (today + timedelta(days=offset)).strftime('%Y-%m-%d')
                    filtered.append({
                        'hotel_id': hotel_id,
                        'hotel_name': h.get('name', ''),
                        'city': h.get('city', ''),
                        'scrape_date': today.strftime('%Y-%m-%d'),
                        'stay_date': stay,
                        'rate_mad': str(round(adr)),
                        'rate_eur': str(round(adr / 10.8)),
                        'source': 'estimated',
                        'data_quality': 'estimated',
                        'rooms_left': '',
                        'availability_signal': 'estimated',
                        'scrape_status': 'estimated',
                    })
        except Exception as e:
            app.logger.warning(f'Rate fallback failed: {e}')

    # Source breakdown
    source_counts = {}
    for r in filtered:
        src = r.get('source', 'unknown')
        source_counts[src] = source_counts.get(src, 0) + 1

    last_scraped = max((r.get('scrape_date', '') for r in filtered), default=None)

    return jsonify({
        'rates': filtered,
        'count': len(filtered),
        'last_scraped': last_scraped,
        'source_breakdown': source_counts,
    })


@app.route('/api/scraper/run', methods=['POST'])
@login_required
def api_scraper_run():
    if not admin_ok():
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        scraper_path = os.path.join(DATA_DIR, 'scraper.py')
        subprocess.Popen([sys.executable, scraper_path])
        return jsonify({'status': 'started', 'message': 'Scraper started in background'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scraper/status')
@login_required
def api_scraper_status():
    stats = {}
    if os.path.exists(SCRAPER_LOG_PATH):
        try:
            with open(SCRAPER_LOG_PATH) as f:
                stats = json.load(f)
        except Exception:
            pass

    progress = {}
    if os.path.exists(PROGRESS_PATH):
        try:
            with open(PROGRESS_PATH) as f:
                progress = json.load(f)
        except Exception:
            pass

    today = datetime.utcnow().strftime('%Y-%m-%d')
    done_today  = sum(1 for v in progress.values() if v.get('status', '').startswith(f'done_{today}'))
    error_count = sum(1 for v in progress.values() if v.get('status') == 'error')

    rows = _read_rates_csv()
    live_sources = {'live_google', 'live_brand', 'live_booking', 'live_expedia'}
    hotels_with_live = len({r['hotel_id'] for r in rows
                            if r.get('source') in live_sources and r.get('scrape_date') >= today})
    hotels_estimated = len({r['hotel_id'] for r in rows
                            if r.get('source') == 'estimated' and r.get('scrape_date') >= today})

    # Source breakdown from last 24h
    src_counts: dict = {}
    for r in rows:
        if r.get('scrape_date', '') >= today:
            src = r.get('source', 'unknown')
            src_counts[src] = src_counts.get(src, 0) + 1

    # Last 30 log lines
    log_tail = []
    if os.path.exists(SCRAPER_LOG_TXT):
        try:
            with open(SCRAPER_LOG_TXT) as f:
                log_tail = f.readlines()[-30:]
        except Exception:
            pass

    return jsonify({
        'last_run':          stats.get('end_time') or stats.get('start_time'),
        'hotels_total':      stats.get('total', 0),
        'hotels_scraped':    stats.get('scraped', 0),
        'hotels_failed':     stats.get('failed', 0),
        'done_today':        done_today,
        'error_count':       error_count,
        'hotels_with_live':  hotels_with_live,
        'hotels_estimated':  hotels_estimated,
        'source_breakdown':  src_counts,
        'log_tail':          ''.join(log_tail),
        'scheduler_running': _scheduler is not None and _scheduler.running if _scheduler else False,
    })


@app.route('/api/scraper/override', methods=['POST'])
@login_required
def api_scraper_override():
    if not admin_ok():
        return jsonify({'error': 'Unauthorized'}), 401

    body      = request.get_json(silent=True) or {}
    hotel_id  = str(body.get('hotel_id', '')).strip()
    stay_date = str(body.get('stay_date', '')).strip()
    rate_mad  = body.get('rate_mad')
    note      = str(body.get('note', '')).strip()

    if not hotel_id or not stay_date or rate_mad is None:
        return jsonify({'error': 'hotel_id, stay_date, rate_mad required'}), 400

    try:
        rate_mad = float(rate_mad)
    except Exception:
        return jsonify({'error': 'rate_mad must be numeric'}), 400

    # Resolve hotel name from hotels.csv
    hotel_name, city = '', ''
    try:
        hotels_df, _, _ = load_data()
        h_row = hotels_df[hotels_df['id'].astype(str) == hotel_id]
        if not h_row.empty:
            hotel_name = h_row.iloc[0]['name']
            city       = h_row.iloc[0]['city']
    except Exception:
        pass

    today = datetime.utcnow().strftime('%Y-%m-%d')
    row = {
        'hotel_id': hotel_id, 'hotel_name': hotel_name, 'city': city,
        'scrape_date': today, 'stay_date': stay_date,
        'rate_mad': str(round(rate_mad)), 'rate_eur': str(round(rate_mad / 10.8)),
        'source': 'manual_override', 'data_quality': 'manual_override',
        'rooms_left': '', 'availability_signal': 'available',
        'scrape_status': 'success',
    }
    fieldnames = [
        'hotel_id', 'hotel_name', 'city', 'scrape_date', 'stay_date',
        'rate_mad', 'rate_eur', 'source', 'data_quality', 'rooms_left',
        'availability_signal', 'scrape_status',
    ]
    file_exists = os.path.exists(RATES_CSV_PATH)
    with open(RATES_CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    app.logger.info(f'Manual override: hotel {hotel_id} | {stay_date} | MAD {rate_mad} | {note}')
    return jsonify({'status': 'saved', 'row': row})


@app.route('/api/financials/<hotel_id>')
@login_required
def api_financials(hotel_id):
    try:
        hotels_df, perf_df, merged = load_data()
        h_row = merged[merged['id'].astype(str) == str(hotel_id)]
        if h_row.empty:
            return jsonify({'error': 'Hotel not found'}), 404

        h         = h_row.iloc[0]
        hotel     = h.to_dict()
        occupancy = float(h.get('occupancy', 0) or 0)
        adr_mad   = float(h.get('adr_mad', 0) or 0)

        # Prefer scraped BAR rate if available (latest scrape_date, nearest stay_date)
        rows = _read_rates_csv()
        live_rows = [r for r in rows
                     if str(r.get('hotel_id', '')) == str(hotel_id)
                     and r.get('source', '') in {'live_google', 'live_brand', 'live_booking', 'live_expedia'}
                     and r.get('rate_mad')]
        if live_rows:
            live_rows.sort(key=lambda r: (r.get('scrape_date', ''), r.get('stay_date', '')), reverse=True)
            try:
                adr_mad = float(live_rows[0]['rate_mad'])
            except Exception:
                pass

        financials = compute_hotel_financials(hotel, occupancy, adr_mad)
        financials['hotel_id']   = hotel_id
        financials['hotel_name'] = h.get('name', '')
        financials['occupancy']  = occupancy
        financials['adr_used']   = adr_mad
        financials['adr_source'] = 'live_scrape' if live_rows else 'kodo_estimate'
        return jsonify(financials)
    except Exception as e:
        app.logger.error(f'Financials error for {hotel_id}: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/scraper/download-rates')
@login_required
def api_scraper_download_rates():
    if not admin_ok():
        return jsonify({'error': 'Unauthorized'}), 401
    if not os.path.exists(RATES_CSV_PATH):
        return jsonify({'status': 'no rates found — scraper has not run yet'})
    return send_file(RATES_CSV_PATH, mimetype='text/csv',
                     as_attachment=True, download_name='kodo_scraped_rates.csv')


@app.route('/api/scraper/download-log')
@login_required
def api_scraper_download_log():
    if not admin_ok():
        return jsonify({'error': 'Unauthorized'}), 401
    if not os.path.exists(SCRAPER_LOG_PATH):
        return jsonify({'status': 'no log found — scraper has not run yet'})
    return send_file(SCRAPER_LOG_PATH, mimetype='application/json',
                     as_attachment=True, download_name='kodo_scraper_log.json')


# ─── Occupancy Model API ──────────────────────────────────────────────────────

def _read_occupancy_csv():
    rows = []
    if not os.path.exists(OCCUPANCY_CSV_PATH):
        return rows
    try:
        with open(OCCUPANCY_CSV_PATH, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
    except Exception:
        pass
    return rows


@app.route('/api/occupancy/<hotel_id>')
@login_required
def api_occupancy_hotel(hotel_id):
    try:
        rows = _read_occupancy_csv()
        hotel_rows = [r for r in rows if r.get('hotel_id') == str(hotel_id)]

        if not hotel_rows:
            # Fall back to live estimation if no pre-computed data
            if not SCRAPER_MODULE_OK or OccupancyModel is None:
                return jsonify({'error': 'Occupancy model not available'}), 503
            hotels_df, perf_df, merged = load_data()
            h_row = merged[merged['id'].astype(str) == str(hotel_id)]
            if h_row.empty:
                return jsonify({'error': 'Hotel not found'}), 404
            h          = h_row.iloc[0].to_dict()
            model      = OccupancyModel()
            today      = datetime.utcnow()
            estimates  = []
            for offset in range(1, 31):
                stay_dt  = today + timedelta(days=offset)
                stay_str = stay_dt.strftime('%Y-%m-%d')
                scraped_bar, rooms_left = model.get_scraped_data_for_date(str(hotel_id), stay_str)
                baseline_adr = float(h.get('adr_mad', 0) or 0)
                occ, breakdown = estimate_occupancy(
                    h, stay_dt,
                    scraped_bar=scraped_bar,
                    rooms_left=rooms_left,
                    baseline_adr=baseline_adr,
                )
                adr_used     = scraped_bar or baseline_adr
                est_revpar   = round(adr_used * occ, 0) if adr_used else None
                estimates.append({
                    'date':                stay_str,
                    'estimated_occupancy': round(occ * 100, 1),
                    'scraped_bar':         round(scraped_bar, 0) if scraped_bar else None,
                    'estimated_revpar':    est_revpar,
                    'confidence':          breakdown['confidence'],
                    'breakdown':           breakdown,
                })
            hotel_name  = h.get('name', '')
            model_run   = today.strftime('%Y-%m-%d')
        else:
            hotel_rows.sort(key=lambda r: r.get('date', ''))
            hotel_name = hotel_rows[0].get('hotel_name', '') if hotel_rows else ''
            model_run  = hotel_rows[0].get('model_run_date', '') if hotel_rows else ''
            estimates  = []
            for r in hotel_rows:
                estimates.append({
                    'date':                r.get('date'),
                    'estimated_occupancy': float(r.get('estimated_occupancy', 0)),
                    'scraped_bar':         float(r['scraped_bar']) if r.get('scraped_bar') else None,
                    'estimated_revpar':    float(r['estimated_revpar']) if r.get('estimated_revpar') else None,
                    'confidence':          r.get('confidence', 'low'),
                    'breakdown': {
                        'base':                    float(r.get('base_occ', 0)),
                        'rate_adjustment':         float(r.get('rate_adj', 0)),
                        'dow_adjustment':          float(r.get('dow_adj', 0)),
                        'seasonality_adjustment':  float(r.get('season_adj', 0)),
                        'availability_adjustment': float(r.get('avail_adj', 0)),
                        'event_adjustment':        float(r.get('event_adj', 0)),
                    },
                })

        occs   = [e['estimated_occupancy'] for e in estimates]
        revs   = [e['estimated_revpar'] for e in estimates if e.get('estimated_revpar')]
        avg_occ   = round(sum(occs) / len(occs), 1) if occs else None
        avg_revpar = round(sum(revs) / len(revs), 0) if revs else None
        conf_counts = {'high': 0, 'medium': 0, 'low': 0}
        for e in estimates:
            conf_counts[e.get('confidence', 'low')] = conf_counts.get(e.get('confidence', 'low'), 0) + 1

        return jsonify({
            'hotel_id':          hotel_id,
            'hotel_name':        hotel_name,
            'estimates':         estimates,
            'avg_occupancy_30d': avg_occ,
            'avg_revpar_30d':    avg_revpar,
            'confidence_counts': conf_counts,
            'model_run_date':    model_run,
        })
    except Exception as e:
        app.logger.error(f'Occupancy hotel error {hotel_id}: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/occupancy/city/<path:city>')
@login_required
def api_occupancy_city(city):
    try:
        rows = _read_occupancy_csv()
        city_rows = [r for r in rows if r.get('city') == city]

        by_date: dict = {}
        by_seg: dict  = {}
        for r in city_rows:
            d   = r.get('date', '')
            seg = r.get('category', 'Unknown')
            occ = float(r.get('estimated_occupancy', 0))
            if d:
                if d not in by_date:
                    by_date[d] = []
                by_date[d].append(occ)
            if seg not in by_seg:
                by_seg[seg] = []
            by_seg[seg].append(occ)

        by_date_list = sorted([
            {'date': d, 'avg_occupancy': round(sum(v) / len(v), 1)}
            for d, v in by_date.items()
        ], key=lambda x: x['date'])

        all_occs = [o for lst in by_date.values() for o in lst]
        avg_occ  = round(sum(all_occs) / len(all_occs), 1) if all_occs else None

        model_run = city_rows[0].get('model_run_date', '') if city_rows else ''

        return jsonify({
            'city':              city,
            'avg_occupancy_30d': avg_occ,
            'by_segment':        {seg: round(sum(v)/len(v), 1) for seg, v in by_seg.items()},
            'by_date':           by_date_list,
            'model_run_date':    model_run,
        })
    except Exception as e:
        app.logger.error(f'Occupancy city error {city}: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/occupancy/run', methods=['POST'])
@login_required
def api_occupancy_run():
    if not admin_ok():
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        occ_path = os.path.join(DATA_DIR, 'occupancy_model.py')
        subprocess.Popen([sys.executable, occ_path])
        return jsonify({'status': 'started', 'message': 'Occupancy model started in background'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/occupancy/status')
@login_required
def api_occupancy_status():
    if not admin_ok():
        return jsonify({'error': 'Unauthorized'}), 401
    rows = _read_occupancy_csv()
    if not rows:
        return jsonify({
            'has_data': False,
            'model_run_date': None,
            'total_estimates': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'hotels_covered': 0,
        })
    model_run = rows[0].get('model_run_date', '') if rows else ''
    hotels_covered = len({r.get('hotel_id') for r in rows})
    high   = sum(1 for r in rows if r.get('confidence') == 'high')
    medium = sum(1 for r in rows if r.get('confidence') == 'medium')
    low    = sum(1 for r in rows if r.get('confidence') == 'low')
    return jsonify({
        'has_data':          True,
        'model_run_date':    model_run,
        'total_estimates':   len(rows),
        'high_confidence':   high,
        'medium_confidence': medium,
        'low_confidence':    low,
        'hotels_covered':    hotels_covered,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
