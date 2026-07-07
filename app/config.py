import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(url: str) -> str:
    # Supabase/Heroku entregam a URL com o prefixo "postgres://",
    # mas o psycopg2 exige "postgresql://".
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get("DATABASE_URL", "sqlite:///database.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    PIX_KEY = os.environ.get("PIX_KEY")
    PIX_RECEIVER_NAME = os.environ.get("PIX_RECEIVER_NAME")
    PIX_RECEIVER_CITY = os.environ.get("PIX_RECEIVER_CITY")

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
