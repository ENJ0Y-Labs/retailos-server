# server/tests/test_platform_admin_settings.py

from server.app.extensions import db
from server.app.models.platform_audit_log import PlatformAuditLog
from server.app.models.user import PLATFORM_ADMIN_ROLE, User


def register_admin(client, app, email="admin@example.com", password="secret123"):
    response = client.post("/auth/register", json={
        "username": "Platform Admin",
        "email": email,
        "password": password,
    })
    assert response.status_code == 201

    with app.app_context():
        user = User.query.filter_by(email=email).one()
        user.platform_role = PLATFORM_ADMIN_ROLE
        db.session.commit()
        user_id = user.id

    response = client.post("/auth/login", json={
        "email": email,
        "password": password,
    })
    assert response.status_code == 200
    return user_id


def register_second_admin(client, app, email="second-admin@example.com"):
    response = client.post("/auth/register", json={
        "username": "Second Admin",
        "email": email,
        "password": "secret123",
    })
    assert response.status_code == 201

    with app.app_context():
        user = User.query.filter_by(email=email).one()
        user.platform_role = PLATFORM_ADMIN_ROLE
        db.session.commit()
        return user.id


def test_admin_profile_endpoints_require_platform_admin(client, app):
    assert client.get("/admin/profile").status_code == 401
    assert client.patch("/admin/profile", json={"name": "New Name"}).status_code == 401

    response = client.post("/auth/register", json={
        "username": "Store Owner",
        "email": "owner@example.com",
        "password": "secret123",
    })
    assert response.status_code == 201
    assert client.post("/auth/login", json={
        "email": "owner@example.com",
        "password": "secret123",
    }).status_code == 200

    assert client.get("/admin/profile").status_code == 403
    assert client.patch("/admin/profile", json={"name": "New Name"}).status_code == 403
    assert client.post("/admin/sessions/revoke-all").status_code == 403


def test_admin_can_retrieve_and_update_only_own_display_name(client, app):
    admin_id = register_admin(client, app)

    response = client.get("/admin/profile")
    assert response.status_code == 200
    profile = response.json["data"]["user"]
    assert profile["id"] == admin_id
    assert profile["name"] == "Platform Admin"
    assert profile["email"] == "admin@example.com"
    assert profile["platform_role"] == PLATFORM_ADMIN_ROLE
    assert "password" not in response.get_data(as_text=True).lower()
    assert "session_version" not in profile

    response = client.patch("/admin/profile", json={"name": "  RetailOS Operator  "})
    assert response.status_code == 200
    assert response.json["data"]["changed"] is True
    assert response.json["data"]["user"]["name"] == "RetailOS Operator"
    assert response.json["data"]["user"]["email"] == "admin@example.com"

    user = db.session.get(User, admin_id)
    assert user.name == "RetailOS Operator"
    assert user.email == "admin@example.com"
    assert user.platform_role == PLATFORM_ADMIN_ROLE

    audit = PlatformAuditLog.query.filter_by(
        action_type="platform_admin.profile_updated",
        target_id=str(admin_id),
    ).one()
    assert audit.actor_user_id == admin_id
    assert audit.target_type == "user"
    assert audit.details == {
        "changed_fields": ["name"],
        "previous": {"name": "Platform Admin"},
        "new": {"name": "RetailOS Operator"},
    }


def test_admin_profile_rejects_identity_and_security_field_changes(client, app):
    admin_id = register_admin(client, app)

    for payload in (
        {"email": "attacker@example.com"},
        {"platform_role": "owner"},
        {"password": "newpassword123"},
        {"name": "Valid Name", "email": "changed@example.com"},
    ):
        response = client.patch("/admin/profile", json=payload)
        assert response.status_code == 400

    user = db.session.get(User, admin_id)
    assert user.name == "Platform Admin"
    assert user.email == "admin@example.com"
    assert user.platform_role == PLATFORM_ADMIN_ROLE
    assert PlatformAuditLog.query.filter_by(
        action_type="platform_admin.profile_updated"
    ).count() == 0

    for invalid_name in ("", " ", "A", "x" * 101, 123):
        response = client.patch("/admin/profile", json={"name": invalid_name})
        assert response.status_code == 400


def test_unchanged_admin_profile_does_not_create_duplicate_audit(client, app):
    admin_id = register_admin(client, app)

    response = client.patch("/admin/profile", json={"name": "Platform Admin"})
    assert response.status_code == 200
    assert response.json["data"]["changed"] is False
    assert PlatformAuditLog.query.filter_by(
        action_type="platform_admin.profile_updated",
        target_id=str(admin_id),
    ).count() == 0


def test_admin_can_revoke_only_their_own_sessions_and_action_is_audited(client, app):
    admin_id = register_admin(client, app)

    second_session = app.test_client()
    assert second_session.post("/auth/login", json={
        "email": "admin@example.com",
        "password": "secret123",
    }).status_code == 200

    other_admin = app.test_client()
    other_admin_id = register_second_admin(other_admin, app)
    assert other_admin.post("/auth/login", json={
        "email": "second-admin@example.com",
        "password": "secret123",
    }).status_code == 200

    response = client.post("/admin/sessions/revoke-all")
    assert response.status_code == 200
    assert response.json["data"] == {
        "sessions_revoked": "all",
        "login_required": True,
    }

    assert client.get("/admin/profile").status_code == 401
    assert second_session.get("/admin/profile").status_code == 401
    assert other_admin.get("/admin/profile").status_code == 200

    audit = PlatformAuditLog.query.filter_by(
        action_type="platform_admin.sessions_revoked",
        target_id=str(admin_id),
    ).one()
    assert audit.actor_user_id == admin_id
    assert audit.target_type == "user"
    assert audit.details["scope"] == "all_sessions"
    assert audit.details["session_version_after"] == audit.details["session_version_before"] + 1
    assert PlatformAuditLog.query.filter_by(
        action_type="platform_admin.sessions_revoked",
        target_id=str(other_admin_id),
    ).count() == 0


def test_admin_password_change_is_audited_and_invalidates_sessions(client, app):
    admin_id = register_admin(client, app)

    response = client.post("/auth/change-password", json={
        "current_password": "secret123",
        "new_password": "newsecret123",
    })
    assert response.status_code == 200
    assert client.get("/admin/profile").status_code == 401

    audit = PlatformAuditLog.query.filter_by(
        action_type="platform_admin.password_changed",
        target_id=str(admin_id),
    ).one()
    assert audit.actor_user_id == admin_id
    assert audit.target_type == "user"
    assert audit.details["sessions_invalidated"] is True
    assert audit.details["session_version_after"] == audit.details["session_version_before"] + 1

    login = client.post("/auth/login", json={
        "email": "admin@example.com",
        "password": "newsecret123",
    })
    assert login.status_code == 200
