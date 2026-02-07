import os


class Config:
    # ==========================
    # SECURITY
    # ==========================
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set.")


    # ==========================
    # DATABASE CONFIG
    # ==========================
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")

    # Fix old postgres:// issue (Render compatibility)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ==========================
    # SQLALCHEMY ENGINE OPTIONS
    # Neon requires SSL
    # ==========================
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {
            "sslmode": "require"
        }
    }
