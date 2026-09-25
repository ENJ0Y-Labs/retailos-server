# server/tests/test_config.py
import pytest

from server.app import create_app
from server.app.config import ProductionConfig


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
