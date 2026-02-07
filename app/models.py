from datetime import datetime
from app import db
from flask_login import UserMixin


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
    last_login = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    # Server timestamp (auto captured)
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
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
    # OCEAN PARAMETERS
    # =======================
    chlorophyll = db.Column(db.Float)
    ta = db.Column(db.Float)
    dic = db.Column(db.Float)

    # =======================
    # COMMON PARAMETERS
    # =======================
    temperature = db.Column(db.Float)
    ph = db.Column(db.Float)
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
