import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db, bcrypt
from app.models import User, WaterData
from app.forms import LoginForm, RegistrationForm

import pytz

main = Blueprint("main", __name__)

UPLOAD_FOLDER = "app/static/uploads"


# =========================
# HOME
# =========================
@main.route("/")
def home():
    return redirect(url_for("main.login"))


# =========================
# REGISTER  ✅ ADDED
# =========================
@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered.", "danger")
            return redirect(url_for("main.register"))

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_pw,
            visit_count=0
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


# =========================
# LOGIN
# =========================
@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)

            user.visit_count = (user.visit_count or 0) + 1
            user.last_login = datetime.now(pytz.timezone("Asia/Kolkata"))
            db.session.commit()

            return redirect(url_for("main.select_water"))

        flash("Invalid email or password", "danger")

    return render_template("login.html", form=form)


# =========================
# WATER SELECTION PAGE
# =========================
@main.route("/select_water", methods=["GET", "POST"])
@login_required
def select_water():

    if request.method == "POST":
        selected = request.form.get("water_type")

        if selected not in ["ocean", "pond"]:
            flash("Please select valid water category.", "danger")
            return redirect(url_for("main.select_water"))

        session["water_type"] = selected
        return redirect(url_for("main.dashboard"))

    return render_template("select_water.html")


# =========================
# DASHBOARD
# =========================
@main.route("/dashboard")
@login_required
def dashboard():

    water_type = session.get("water_type")

    if water_type not in ["ocean", "pond"]:
        return redirect(url_for("main.select_water"))

    return render_template("dashboard.html", water_type=water_type)


# =========================
# LOGOUT
# =========================
@main.route("/logout")
@login_required
def logout():
    session.pop("water_type", None)
    logout_user()
    return redirect(url_for("main.login"))


# =========================
# SAVE DATA
# =========================
@main.route("/save_data", methods=["POST"])
@login_required
def save_data():

    water_type = session.get("water_type")

    if water_type not in ["ocean", "pond"]:
        flash("Water type not selected.", "danger")
        return redirect(url_for("main.select_water"))

    data = request.form

    if not data.get("latitude") or not data.get("longitude"):
        flash("Location is required.", "danger")
        return redirect(url_for("main.dashboard"))

    if not data.get("pin_id"):
        flash("Pin ID is required.", "danger")
        return redirect(url_for("main.dashboard"))

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    image = request.files.get("image")
    image_path = None

    if image and image.filename:
        filename = secure_filename(image.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(save_path)
        image_path = f"uploads/{filename}"

    def to_float(value):
        try:
            return float(value) if value else None
        except:
            return None

    ist = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(ist)

    entry = WaterData(
        user_id=current_user.id,
        latitude=to_float(data.get("latitude")),
        longitude=to_float(data.get("longitude")),
        water_type=water_type,
        pin_id=data.get("pin_id"),

        chlorophyll=to_float(data.get("chlorophyll")) if water_type == "ocean" else None,
        ta=to_float(data.get("ta")) if water_type == "ocean" else None,
        dic=to_float(data.get("dic")) if water_type == "ocean" else None,

        temperature=to_float(data.get("temperature")),
        ph=to_float(data.get("ph")),
        tds=to_float(data.get("tds")),
        do=to_float(data.get("do")) if water_type == "pond" else None,

        image_path=image_path,
        timestamp=current_time
    )

    db.session.add(entry)
    db.session.commit()

    flash("Water data saved successfully ✔", "success")
    return redirect(url_for("main.dashboard"))
