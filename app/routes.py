import base64
from datetime import datetime
import pytz
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from app import db, bcrypt
from app.models import User, WaterData
from app.forms import LoginForm, RegistrationForm

main = Blueprint("main", __name__)
IST = pytz.timezone("Asia/Kolkata")

@main.route("/")
def splash():
    return render_template("splash.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("main.register"))
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        new_user = User(username=form.username.data, email=form.email.data, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)

@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            # Update login metrics
            user.visit_count = (user.visit_count or 0) + 1
            user.last_login = datetime.now(IST)
            db.session.commit()
            login_user(user)
            return redirect(url_for("main.select_water"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html", form=form)

@main.route("/save_data", methods=["POST"])
@login_required
def save_data():
    category = session.get("water_category")
    data = request.form
    image = request.files.get("image")
    image_string = base64.b64encode(image.read()).decode('utf-8') if image else None

    entry = WaterData(
        user_id=current_user.id,
        latitude=float(data.get("latitude")),
        longitude=float(data.get("longitude")),
        water_type=data.get("water_type"),
        pin_id=data.get("pin_id"),
        temperature=float(data.get("temperature")) if data.get("temperature") else None,
        ph=float(data.get("ph")) if data.get("ph") else None,
        tds=float(data.get("tds")) if data.get("tds") else None,
        do=float(data.get("do")) if category == "pond" else None,
        image_path=image_string
    )
    db.session.add(entry)
    db.session.commit()
    flash("Data saved successfully!", "success")
    return redirect(url_for("main.dashboard"))

@main.route("/fix_my_db")
def fix_my_db():
    """Run this once in the browser to fix the 'UndefinedColumn' error."""
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS visit_count INTEGER DEFAULT 0;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;"))
            conn.commit()
        return "✅ Success! Columns added. You can now login."
    except Exception as e:
        return f"❌ Error: {e}"

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

# Add your select_water and dashboard routes here as well...
