# server\tests\conftest.py
import pytest
from server.app import create_app
from server.app.config import TestConfig
from server.app.extensions import db

@pytest.fixture()
def app(db):
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()