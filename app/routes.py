import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, WaterData
from app.forms import LoginForm, RegistrationForm
from app import bcrypt

main = Blueprint('main', __name__)

UPLOAD_FOLDER = "app/static/uploads"

@main.route("/")
def home():
    return redirect(url_for("main.login"))

# ------------------ LOGIN ------------------
@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)

            # Update visit tracking
            user.visit_count = (user.visit_count or 0) + 1
            user.last_login = datetime.utcnow()
            db.session.commit()

            return redirect(url_for("main.dashboard"))
        else:
            flash("Login failed", "danger")
    return render_template("login.html", form=form)

# ------------------ REGISTER ------------------
@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Account created!", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)

# ------------------ DASHBOARD ------------------
@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# ------------------ SAVE SENSOR DATA ------------------
@main.route("/save_data", methods=["POST"])
@login_required
def save_data():
    data = request.form

    image = request.files.get("image")
    image_path = None

    if image:
        filename = secure_filename(image.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(save_path)
        image_path = f"uploads/{filename}"

    entry = WaterData(
        user_id=current_user.id,
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        water_type=data.get("water_type"),
        pin_id=data.get("pin_id"),
        chlorophyll=data.get("chlorophyll"),
        ta=data.get("ta"),
        dic=data.get("dic"),
        temperature=data.get("temperature"),
        ph=data.get("ph"),
        tds=data.get("tds"),
        do=data.get("do"),
        image_path=image_path
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"status": "success"})
