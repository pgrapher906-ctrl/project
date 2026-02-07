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


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Safety fallback (in case ENV not loaded on Render)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Login settings
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "warning"

    # Import models & routes AFTER init
    from app.models import User
    from app.routes import main

    # User loader (SQLAlchemy 2.0 safe)
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(main)

    # Auto create tables (only if not exists)
    with app.app_context():
        db.create_all()

    return app
