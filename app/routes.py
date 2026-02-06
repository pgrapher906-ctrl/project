import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db, bcrypt
from app.models import User, WaterData
from app.forms import LoginForm, RegistrationForm

main = Blueprint('main', __name__)

UPLOAD_FOLDER = "app/static/uploads"


# ------------------ HOME ------------------
@main.route("/")
def home():
    return redirect(url_for("main.login"))


# ------------------ LOGIN ------------------
@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)

            # Update visit tracking
            user.visit_count = (user.visit_count or 0) + 1
            user.last_login = datetime.utcnow()
            db.session.commit()

            # 👉 Go to water selection page
            return redirect(url_for("main.select_water"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html", form=form)


# ------------------ SELECT WATER TYPE ------------------
@main.route("/select_water", methods=["GET", "POST"])
@login_required
def select_water():

    if request.method == "POST":
        selected_type = request.form.get("water_type")

        if selected_type not in ["ocean", "pond"]:
            flash("Please select valid water type", "danger")
            return redirect(url_for("main.select_water"))

        session["water_type"] = selected_type
        return redirect(url_for("main.dashboard"))

    return render_template("select_water.html")


# ------------------ DASHBOARD ------------------
@main.route("/dashboard")
@login_required
def dashboard():

    water_type = session.get("water_type")

    if not water_type:
        return redirect(url_for("main.select_water"))

    return render_template(
        "dashboard.html",
        user=current_user,
        water_type=water_type
    )


# ------------------ LOGOUT ------------------
@main.route("/logout")
@login_required
def logout():
    session.pop("water_type", None)  # clear selection
    logout_user()
    return redirect(url_for("main.login"))


# ------------------ SAVE SENSOR DATA ------------------
@main.route("/save_data", methods=["POST"])
@login_required
def save_data():

    water_type = session.get("water_type")

    if not water_type:
        return jsonify({"error": "Water type not selected"}), 400

    data = request.form

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    image = request.files.get("image")
    image_path = None

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(save_path)
        image_path = f"uploads/{filename}"

    def to_float(value):
        try:
            return float(value) if value else None
        except:
            return None

    entry = WaterData(
        user_id=current_user.id,
        latitude=to_float(data.get("latitude")),
        longitude=to_float(data.get("longitude")),
        water_type=water_type,
        pin_id=data.get("pin_id"),

        # Ocean
        chlorophyll=to_float(data.get("chlorophyll")) if water_type == "ocean" else None,
        ta=to_float(data.get("ta")) if water_type == "ocean" else None,
        dic=to_float(data.get("dic")) if water_type == "ocean" else None,

        # Common
        temperature=to_float(data.get("temperature")),
        ph=to_float(data.get("ph")),
        tds=to_float(data.get("tds")),

        # Pond
        do=to_float(data.get("do")) if water_type == "pond" else None,

        image_path=image_path,
        timestamp=datetime.utcnow()
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"status": "success"})
