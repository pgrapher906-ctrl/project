from datetime import datetime
from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # IMPORTANT — change this
    password_hash = db.Column(db.String(200), nullable=False)

    # Visit tracking
    visit_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WaterData(db.Model):
    __tablename__ = "water_data"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    water_type = db.Column(db.String(100))
    pin_id = db.Column(db.String(100))

    # Ocean Parameters
    chlorophyll = db.Column(db.Float)
    ta = db.Column(db.Float)
    dic = db.Column(db.Float)

    # Common
    temperature = db.Column(db.Float)
    ph = db.Column(db.Float)
    tds = db.Column(db.Float)

    # Pond
    do = db.Column(db.Float)

    image_path = db.Column(db.String(300))
