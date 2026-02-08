import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bcrypt = Bcrypt()


def create_app():
    load_dotenv()

    app = Flask(__name__)

    # ==============================
    # SECRET KEY
    # ==============================
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key")

    # ==============================
    # NEON POSTGRESQL DATABASE
    # ==============================
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Fix old postgres:// issue (Render compatibility)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://", "postgresql://", 1
            )

        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        raise RuntimeError("DATABASE_URL is not set!")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Neon requires SSL
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "connect_args": {"sslmode": "require"},
    }

    # ==============================
    # INITIALIZE EXTENSIONS
    # ==============================
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # ==============================
    # LOGIN SETTINGS
    # ==============================
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "warning"

    from app.models import User
    from app.routes import main

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(main)

    return app
