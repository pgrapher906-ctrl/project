from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    visit_count = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.Date, nullable=True)
    last_login_time = db.Column(db.Time, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    water_data = db.relationship('WaterData', backref='user', lazy=True)

class WaterData(db.Model):
    __tablename__ = 'water_data'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_type = db.Column(db.String(64), nullable=False)
    water_type = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    pin_id = db.Column(db.String(32), nullable=False)
    image_path = db.Column(db.String(256), nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    pH = db.Column(db.Float, nullable=True)
    DO = db.Column(db.Float, nullable=True)
    TDS = db.Column(db.Float, nullable=True)
    chlorophyll = db.Column(db.Float, nullable=True)
    TA = db.Column(db.Float, nullable=True)
    DIC = db.Column(db.Float, nullable=True)

