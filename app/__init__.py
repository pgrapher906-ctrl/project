import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bcrypt = Bcrypt()

login_manager.login_view = "main.login"  # redirect if not logged in

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Import models
    from app.models import User
    from app.routes import main

    # ✅ USER LOADER (REQUIRED)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main)

    # ✅ CREATE TABLES AUTOMATICALLY (VERY IMPORTANT FOR YOUR CLEAN NEON DB)
    with app.app_context():
        db.create_all()

    return app
