from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Fields that were missing in your DB
    visit_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    water_entries = db.relationship("WaterData", backref="user", lazy=True, cascade="all, delete-orphan")

class WaterData(db.Model):
    __tablename__ = "water_data"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    water_type = db.Column(db.String(100), nullable=False)
    pin_id = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    ph = db.Column(db.Numeric(4, 2))
    tds = db.Column(db.Float)
    do = db.Column(db.Float)
    image_path = db.Column(db.Text) # Stores the Base64 image data
