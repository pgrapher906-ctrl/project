import os
from datetime import datetime
import pytz

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from app import db, bcrypt
from app.models import User, WaterData
from app.forms import LoginForm, RegistrationForm

main = Blueprint("main", __name__)

# FIX: Vercel source folders are read-only. Use /tmp for writable operations.
UPLOAD_FOLDER = "/tmp" 
IST = pytz.timezone("Asia/Kolkata")

# ... (Splash, Register, Login, Select Water, and Dashboard routes remain the same) ...

# =====================================================
# SAVE DATA (FIXED FOR VERCEL)
# =====================================================
@main.route("/save_data", methods=["POST"])
@login_required
def save_data():
    category = session.get("water_category")

    if category not in ["ocean", "pond"]:
        flash("Please select valid water category.", "danger")
        return redirect(url_for("main.select_water"))

    data = request.form

    if not data.get("latitude") or not data.get("longitude"):
        flash("Location is required.", "danger")
        return redirect(url_for("main.dashboard"))

    if not data.get("pin_id"):
        flash("Pin ID is required.", "danger")
        return redirect(url_for("main.dashboard"))

    if not data.get("water_type"):
        flash("Please select water type.", "danger")
        return redirect(url_for("main.dashboard"))

    # This will now succeed because /tmp is writable
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    image = request.files.get("image")
    image_path = None

    if image and image.filename:
        filename = secure_filename(image.filename)
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp_str}_{filename}"

        # Saving to the writable /tmp directory
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(save_path)

        # Note: image_path saved to DB. 
        # On Vercel, this file will disappear when the function instance restarts.
        image_path = filename 

    def to_float(value):
        try:
            return float(value) if value else None
        except:
            return None

    current_time = datetime.now(IST)

    entry = WaterData(
        user_id=current_user.id,
        latitude=to_float(data.get("latitude")),
        longitude=to_float(data.get("longitude")),
        water_type=data.get("water_type"),
        pin_id=data.get("pin_id"),
        temperature=to_float(data.get("temperature")),
        ph=to_float(data.get("ph")),
        tds=to_float(data.get("tds")),
        do=to_float(data.get("do")) if category == "pond" else None,
        image_path=image_path,
        timestamp=current_time
    )

    db.session.add(entry)
    db.session.commit()

    flash("Water data saved successfully ✔", "success")
    return redirect(url_for("main.dashboard"))
