# server/tests/test_auth.py
import pytest
from server.app.models.user import User
from server.app.extensions import db

@pytest.fixture()
def register_new_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser1",
            "email": "testuser1@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 200

    yield response.json

    # Delete the test user from the database here.
    user = User.query.filter_by(
        email="testuser1@example.com"
    ).first()
    
    if user:
        db.session.delete(user)
        db.session.commit()


@pytest.fixture()
def login_user(client, register_new_user):
    if not register_new_user:
        pytest.skip("User registration failed, skipping login test.")

    response = client.post(
        "/auth/login",
        json={
            "email": "testuser1@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 200
    
# successful register/login
def test_register_new_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser1",
            "email": "testuser1@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 200

    yield response.json

    # Delete the test user from the database here.
    user = User.query.filter_by(
        email="testuser1@example.com"
    ).first()
    
    if user:
        db.session.delete(user)
        db.session.commit()


def test_login_user(client, register_new_user):
    if not register_new_user:
        pytest.skip("User registration failed, skipping login test.")

    response = client.post(
        "/auth/login",
        json={
            "email": "testuser1@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 200


def test_logout_user(client, login_user):
    if not login_user:
        pytest.skip("User login failed, skipping logout test.")

    response = client.post("/auth/logout")

    assert response.status_code == 200

# duplicate email
def test_register_duplicate_email(client):
    try:
        response = client.post(
            "/auth/register",
            json={
                "username": "testuser1",
                "email": "testuser@example.com",
                "password": "test123"
            }
        )
        response2 = client.post(
            "/auth/register",
            json={
                "username": "testuser2",
                "email": "testuser@example.com",
                "password": "test456"
            }
        )
        
        assert response.status_code == 200
        assert response2.status_code == 400
            
    finally:
        user = User.query.filter_by(
            email="testuser@example.com"
        ).first()
        
        if user:
            db.session.delete(user)
            db.session.commit()
    
# wrong password
def test_wrong_password(client, test_register_new_user):
    if not test_register_new_user:
        pytest.skip("User registration failed, skipping wrong password test.")
        
    response = client.post(
        "/auth/login",
        json={
            "email" : "testuser1@example.com",
            "password" : "test456"
        }
    )
    
    assert response.status_code == 401
    
# access-denied on protected routes.
def test_unauthorized_access(client):
    response = client.post("/auth/logout")
    
    assert response.status_code == 401