from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# ==========================================
# USER TABLE
# ==========================================
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(200), nullable=False)

    # ---- User Activity Tracking ----
    visit_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime(timezone=True))

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now()
    )

    # ---- Relationship ----
    water_entries = db.relationship(
        "WaterData",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"


# ==========================================
# WATER DATA TABLE
# ==========================================
class WaterData(db.Model):
    __tablename__ = "water_data"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Auto timestamp (DB side, timezone safe)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # -----------------------
    # LOCATION
    # -----------------------
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # -----------------------
    # WATER TYPE & PIN
    # -----------------------
    water_type = db.Column(db.String(100), nullable=False)
    pin_id = db.Column(db.String(100), nullable=False)
    
    # =======================
    # COMMON PARAMETERS
    # =======================
    temperature = db.Column(db.Float)

    # 🔥 UPDATED pH FIELD (Scientific precision)
    ph = db.Column(db.Numeric(4, 2))  # Example: 7.25

    tds = db.Column(db.Float)

    # =======================
    # POND PARAMETER
    # =======================
    do = db.Column(db.Float)

    # -----------------------
    # IMAGE
    # -----------------------
    image_path = db.Column(db.String(300))

    def __repr__(self):
        return f"<WaterData {self.water_type} - {self.timestamp}>"
