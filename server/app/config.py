# server/app/config.py
import os


def normalize_database_url(database_url):
    if not database_url:
        return database_url

    if database_url.startswith("postgresql://"):
        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    if database_url.startswith("postgres://"):
        return database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )

    return database_url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.environ.get(
            "DATABASE_URL",
            "sqlite:///store.db"
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get(
        "SESSION_COOKIE_SECURE",
        "false"
    ).lower() == "true"
    SESSION_COOKIE_SAMESITE = os.environ.get(
        "SESSION_COOKIE_SAMESITE",
        "Lax"
    )
    SESSION_COOKIE_PARTITIONED = os.environ.get(
        "SESSION_COOKIE_PARTITIONED",
        "false"
    ).lower() == "true"
    FRONTEND_URL = os.environ.get(
        "FRONTEND_URL",
        "http://localhost:3000"
    ).rstrip("/")
    TESTING = False
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        FRONTEND_URL
    )


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_PARTITIONED = True


class TestConfig(Config):
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"
    FRONTEND_URL = "http://localhost:3000"
    CORS_ORIGINS = "http://localhost:3000"
