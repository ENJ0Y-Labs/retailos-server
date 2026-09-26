# server/tests/test_config.py
import pytest

from server.app import create_app
from server.app.config import Config, ProductionConfig, TestConfig


# Check that production cannot start without a database URL.
def test_production_requires_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SECRET_KEY", "production-test-secret")

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        create_app(ProductionConfig)


# Check that production accepts a configured database URL.
def test_production_accepts_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("SECRET_KEY", "production-test-secret")

    app = create_app(ProductionConfig)

    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


# Check that local development does not require HTTPS for session cookies.
def test_local_session_cookie_defaults_are_http_safe():
    class LocalConfig(Config):
        SECRET_KEY = "local-test-secret"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    app = create_app(LocalConfig)

    assert app.config["SESSION_COOKIE_SECURE"] is False
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


# Check that production keeps secure cross-site session-cookie settings.
def test_production_session_cookie_settings(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("SECRET_KEY", "production-test-secret")

    app = create_app(ProductionConfig)

    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "None"


# Check that CORS_ORIGINS controls the actual allowed origin list.
def test_cors_origins_allow_multiple_configured_origins():
    class MultiOriginConfig(TestConfig):
        CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"

    app = create_app(MultiOriginConfig)
    client = app.test_client()

    response = client.get(
        "/auth/me",
        headers={"Origin": "http://127.0.0.1:3000"}
    )

    assert response.status_code == 401
    assert response.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1:3000"

    response = client.get(
        "/auth/me",
        headers={"Origin": "https://not-allowed.example"}
    )

    assert response.status_code == 403
    assert "Access-Control-Allow-Origin" not in response.headers
