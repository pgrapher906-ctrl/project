import base64
from datetime import datetime
import pytz

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from werkzeug.utils import secure_filename

from app import db, bcrypt
from app.models import User, WaterData
from app.forms import LoginForm, RegistrationForm

main = Blueprint("main", __name__)
IST = pytz.timezone("Asia/Kolkata")

# =====================================================
# SPLASH SCREEN
# =====================================================
@main.route("/")
def splash():
    return render_template("splash.html")

# =====================================================
# REGISTER
# =====================================================
@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("main.register"))

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        
        new_user = User(
            username=form.username.data, 
            email=form.email.data, 
            password_hash=hashed_pw,
            visit_count=0,
            created_at=datetime.now(IST)
        )
        
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)

# =====================================================
# LOGIN (UPDATED: SAFE MODE)
# =====================================================
@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            # 1. Log the user in FIRST (Critical Step)
            # This sets the session cookie so you are logged in even if the DB update below fails.
            login_user(user)
            
            # 2. Try to update activity safely (Prevents 500 Crash)
            try:
                user.visit_count = (user.visit_count or 0) + 1
                user.last_login = datetime.now(IST)
                db.session.commit()
            except Exception as e:
                # If DB update fails, rollback the transaction but KEEP user logged in.
                db.session.rollback()
                print(f"Warning: Could not update usage stats: {e}")
            
            return redirect(url_for("main.select_water"))
        
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)

# =====================================================
# SELECT WATER TYPE
# =====================================================
@main.route("/select_water", methods=["GET", "POST"])
@login_required
def select_water():
    if request.method == "POST":
        selected = request.form.get("water_type")
        if selected not in ["ocean", "pond"]:
            flash("Please select valid water category.", "danger")
            return redirect(url_for("main.select_water"))

        session["water_category"] = selected
        return redirect(url_for("main.dashboard"))

    return render_template("select_water.html")

# =====================================================
# DASHBOARD
# =====================================================
@main.route("/dashboard")
@login_required
def dashboard():
    category = session.get("water_category")
    if category not in ["ocean", "pond"]:
        return redirect(url_for("main.select_water"))

    return render_template("dashboard.html", category=category)

# =====================================================
# SAVE DATA
# =====================================================
@main.route("/save_data", methods=["POST"])
@login_required
def save_data():
    category = session.get("water_category")
    data = request.form
    
    # Image Processing
    image = request.files.get("image")
    image_string = None
    if image:
        image_string = base64.b64encode(image.read()).decode('utf-8')

    # Create Database Entry
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

# =====================================================
# LOGOUT
# =====================================================
@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

# =====================================================
# 🛠️ CRITICAL DATABASE FIX ROUTE
# =====================================================
@main.route("/fix_my_db")
def fix_my_db():
    """
    Run this URL once to fix 'UndefinedColumn' errors.
    It manually adds visit_count, last_login, and created_at to the database.
    """
    try:
        with db.engine.connect() as conn:
            # 1. Add visit_count
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS visit_count INTEGER DEFAULT 0;"))
            
            # 2. Add last_login
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;"))
            
            # 3. Add created_at
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();"))
            
            conn.commit()
            
        return "✅ SUCCESS! Database columns 'visit_count', 'last_login', and 'created_at' have been added. You can now Login!"
    except Exception as e:
        return f"❌ Error fixing database: {e}"
