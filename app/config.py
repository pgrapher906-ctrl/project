import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secure_secret_key")

    # -------------------------
    # DATABASE CONFIG (NEON)
    # -------------------------
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Fix for old postgres:// format (Render compatibility)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -------------------------
    # SQLALCHEMY ENGINE OPTIONS
    # Required for Neon SSL
    # -------------------------
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {
            "sslmode": "require"
        }
    }
