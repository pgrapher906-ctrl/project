import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    load_dotenv()
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "smart-water-key-2026")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Database URL Logic
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    # Neon-Specific Optimization
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"sslmode": "require"}
    }

    # Init Extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    login_manager.login_view = "main.login"
    login_manager.login_message_category = "warning"

    with app.app_context():
        from app.models import User
        from app.routes import main
        app.register_blueprint(main)

        @login_manager.user_loader
        def load_user(user_id):
            # FIXED: Wrapped in try/except to prevent global crash if DB columns are missing
            try:
                return db.session.get(User, int(user_id))
            except Exception:
                db.session.rollback()
                return None

    return app
