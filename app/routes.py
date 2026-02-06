import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
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

            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html", form=form)


# ------------------ LOGOUT (FIXED) ------------------
@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


# ------------------ REGISTER ------------------
@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_pw
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


# ------------------ DASHBOARD ------------------
@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


# ------------------ SAVE SENSOR DATA ------------------
@main.route("/save_data", methods=["POST"])
@login_required
def save_data():

    data = request.form

    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    image = request.files.get("image")
    image_path = None

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(save_path)
        image_path = f"uploads/{filename}"

    # Helper function to safely convert to float
    def to_float(value):
        try:
            return float(value) if value else None
        except:
            return None

    entry = WaterData(
        user_id=current_user.id,
        latitude=to_float(data.get("latitude")),
        longitude=to_float(data.get("longitude")),
        water_type=data.get("water_type"),
        pin_id=data.get("pin_id"),
        chlorophyll=to_float(data.get("chlorophyll")),
        ta=to_float(data.get("ta")),
        dic=to_float(data.get("dic")),
        temperature=to_float(data.get("temperature")),
        ph=to_float(data.get("ph")),
        tds=to_float(data.get("tds")),
        do=to_float(data.get("do")),
        timestamp=datetime.utcnow()
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"status": "success"})
