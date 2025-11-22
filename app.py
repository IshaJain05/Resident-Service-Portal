from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, date as date_cls
import json, os, random, string

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"

# ----------------- Config -----------------
DATA_FILE = os.path.join(os.path.dirname(__file__), "residents.json")
ADMIN_PASSWORD = "admin123"  # demo-only; change later

# ----------------- Data helpers -----------------
def load_residents():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {r["resident_id"]: r for r in data}

def save_residents(residents_index):
    data = list(residents_index.values())
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

RESIDENTS = load_residents()
BOOKINGS = []

SERVICES = [
    {"key": "plumber",     "name": "Plumber",     "desc": "Leaks, taps, bathroom fixes",     "icon": "🔧"},
    {"key": "electrician", "name": "Electrician", "desc": "Wiring, switches, fittings",       "icon": "💡"},
    {"key": "carpenter",   "name": "Carpenter",   "desc": "Repairs, shelves, doors",          "icon": "🪚"},
    {"key": "cleaning",    "name": "Cleaning",    "desc": "Deep clean, housekeeping",         "icon": "🧼"},
    {"key": "pest",        "name": "Pest Control","desc": "Cockroaches, termites",            "icon": "🐜"},
    {"key": "hvac",        "name": "HVAC",        "desc": "AC servicing & maintenance",       "icon": "❄️"},
    {"key": "security",    "name": "Security",    "desc": "Visitor/guard assistance",         "icon": "🛡️"},
]
TIME_SLOTS = ["09:00","10:00","11:00","12:00","14:00","15:00","16:00","17:00"]

def generate_temp_password():
    return "".join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))

# ----------------- Resident auth & dashboard -----------------
@app.route("/")
def index():
    if "resident_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.post("/login")
def login():
    rid = request.form.get("resident_id","").strip()
    pwd = request.form.get("password","").strip()
    resident = RESIDENTS.get(rid)
    if not resident:
        flash("Invalid Resident ID.", "error")
        return redirect(url_for("index"))
    if pwd != resident.get("password"):
        flash("Incorrect password.", "error")
        return redirect(url_for("index"))
    session["resident_id"] = rid
    session["name"] = resident["name"]
    return redirect(url_for("dashboard"))

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.post("/reset-password")
def reset_password():
    rid = request.form.get("resident_id_reset","").strip()
    phone = request.form.get("phone_reset","").strip()
    resident = RESIDENTS.get(rid)
    if not resident or resident.get("phone") != phone:
        flash("Resident ID and phone do not match.", "error")
        return redirect(url_for("index"))
    new_pwd = generate_temp_password()
    resident["password"] = new_pwd
    save_residents(RESIDENTS)
    flash(f"Temporary password for {rid} is: {new_pwd}", "info")
    return redirect(url_for("index"))

@app.get("/dashboard")
def dashboard():
    if "resident_id" not in session:
        return redirect(url_for("index"))
    rid = session["resident_id"]
    resident = RESIDENTS.get(rid)
    my_bookings = [b for b in BOOKINGS if b["resident_id"] == rid]
    today_str = date_cls.today().isoformat()
    return render_template(
        "dashboard.html",
        user=resident,
        services=SERVICES,
        time_slots=TIME_SLOTS,
        bookings=my_bookings,
        today=today_str
    )

@app.post("/book")
def book():
    if "resident_id" not in session:
        return redirect(url_for("index"))
    service_key = request.form.get("service_key")
    date_val    = request.form.get("date")
    time        = request.form.get("time")
    notes       = request.form.get("notes","").strip()
    rid         = session["resident_id"]

    svc = next((s for s in SERVICES if s["key"] == service_key), None)
    if not svc or not date_val or not time:
        flash("Please select service, date and time.", "error")
        return redirect(url_for("dashboard"))

    try:
        if datetime.fromisoformat(date_val).date() < date_cls.today():
            flash("Date cannot be in the past.", "error")
            return redirect(url_for("dashboard"))
    except Exception:
        flash("Invalid date.", "error")
        return redirect(url_for("dashboard"))

    if time not in TIME_SLOTS:
        flash("Please choose a valid time slot.", "error")
        return redirect(url_for("dashboard"))

    for b in BOOKINGS:
        if b["resident_id"] == rid and b["service_key"] == service_key and b["date"] == date_val and b["time"] == time:
            flash("You already requested this slot for the selected service.", "error")
            return redirect(url_for("dashboard"))

    booking = {
        "id": f"B{len(BOOKINGS)+1:04d}",
        "resident_id": rid,
        "service_key": service_key,
        "service_name": svc["name"],
        "date": date_val,
        "time": time,
        "notes": notes,
        "created_at": datetime.utcnow().isoformat(),
        "status": "Requested",
    }
    BOOKINGS.append(booking)
    flash(f"Booking requested: {svc['name']} on {date_val} at {time}.", "success")
    return redirect(url_for("dashboard"))

# ----------------- Admin preview (demo) -----------------
@app.get("/admin")
def admin_home():
    if not session.get("is_admin"):
        return render_template("admin_login.html")

    rows = []
    for b in BOOKINGS:
        resident = RESIDENTS.get(b["resident_id"], {})
        rows.append({
            "id": b["id"],
            "resident_name": resident.get("name", "Unknown"),
            "resident_id": b["resident_id"],
            "building": resident.get("building", ""),
            "flat": f'F{resident.get("floor","")} • {resident.get("flat","")}',
            "service": b["service_name"],
            "date": b["date"],
            "time": b["time"],
            "status": b["status"],
            "notes": b.get("notes",""),
        })
    rows.sort(key=lambda r: r["id"], reverse=True)
    STATUSES = ["Requested", "In Progress", "Completed", "Cancelled"]
    return render_template("admin.html", rows=rows, statuses=STATUSES)

@app.post("/admin/login")
def admin_login():
    pwd = request.form.get("password","")
    if pwd == ADMIN_PASSWORD:
        session["is_admin"] = True
        flash("Admin login successful.", "success")
        return redirect(url_for("admin_home"))
    flash("Invalid admin password.", "error")
    return redirect(url_for("admin_home"))

@app.post("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Logged out of admin.", "info")
    return redirect(url_for("admin_home"))

@app.post("/admin/status/<bid>")
def admin_update_status(bid):
    if not session.get("is_admin"):
        flash("Admin access required.", "error")
        return redirect(url_for("admin_home"))
    new_status = request.form.get("status","").strip()
    updated = False
    for b in BOOKINGS:
        if b["id"] == bid:
            b["status"] = new_status or b["status"]
            updated = True
            break
    if updated:
        flash(f"Booking {bid} updated to {new_status}.", "success")
    else:
        flash("Booking not found.", "error")
    return redirect(url_for("admin_home"))

# ----------------- Run -----------------
if __name__ == "__main__":
    app.run(debug=True)
