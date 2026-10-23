"""Cross-store authorization regression tests.

Every endpoint that accepts a store identifier must reject a session that does
not own that store. These tests deliberately use a valid foreign store ID so
they exercise authorization rather than malformed-input validation.
"""

import pytest


def register_and_login(client, username):
    email = f"{username}@example.com"
    registered = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "test123",
        },
    )
    assert registered.status_code == 201

    logged_in = client.post(
        "/auth/login",
        json={"email": email, "password": "test123"},
    )
    assert logged_in.status_code == 200
    return logged_in.json["data"]["user"]["store_id"]


@pytest.fixture()
def two_store_clients(app):
    owner_client = app.test_client()
    attacker_client = app.test_client()
    owner_store_id = register_and_login(owner_client, "authorization-owner")
    attacker_store_id = register_and_login(attacker_client, "authorization-attacker")
    assert owner_store_id != attacker_store_id
    return owner_client, attacker_client, owner_store_id, attacker_store_id


@pytest.mark.parametrize(
    "path",
    [
        "/product/list",
        "/product/movements",
        "/product/receivings",
        "/categories",
        "/customers",
        "/customers/owes",
        "/sales",
        "/sales/payments",
        "/sales/refunds",
        "/alerts",
        "/audit",
        "/dashboard",
        "/dashboard/rankings",
        "/dashboard/time-series",
        "/dashboard/daily-summary",
        "/dashboard/daily-brief",
    ],
)
def test_store_scoped_list_endpoints_reject_another_stores_id(two_store_clients, path):
    _, attacker, owner_store_id, _ = two_store_clients

    response = attacker.get(f"{path}?store_id={owner_store_id}")

    assert response.status_code == 403, (
        f"{path} must reject a valid store ID owned by another account; "
        f"got {response.status_code}: {response.get_json()}"
    )
    assert response.json["success"] is False
    assert response.json["error"]["code"] == "STORE_ACCESS_DENIED"


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "post",
            "/product/create",
            {
                "name": "Foreign store product",
                "price": 100,
                "opening_stock": 1,
                "low_stock_threshold": 1,
            },
        ),
        (
            "post",
            "/customers",
            {"name": "Foreign store customer", "contact": "08000000000"},
        ),
        (
            "post",
            "/categories",
            {"name": "Foreign store category", "item_type": "Physical"},
        ),
        (
            "post",
            "/sales",
            {
                "payment_method": "Cash",
                "items": [{"product_id": 1, "quantity": 1}],
                "client_transaction_id": "foreign-store-sale",
            },
        ),
        (
            "post",
            "/product/receivings",
            {
                "product_id": 1,
                "quantity": 1,
                "unit_cost": "10.00",
                "total_cost": "10.00",
                "client_transaction_id": "foreign-store-receiving",
            },
        ),
    ],
)
def test_store_scoped_create_endpoints_reject_another_stores_id(
    two_store_clients, method, path, payload
):
    _, attacker, owner_store_id, _ = two_store_clients
    request_payload = {"store_id": owner_store_id, **payload}

    response = getattr(attacker, method)(path, json=request_payload)

    assert response.status_code == 403, (
        f"{path} must reject a write targeting another account's store; "
        f"got {response.status_code}: {response.get_json()}"
    )
    assert response.json["success"] is False
    assert response.json["error"]["code"] == "STORE_ACCESS_DENIED"


def test_store_settings_cannot_be_changed_by_another_store_owner(two_store_clients):
    _, attacker, owner_store_id, _ = two_store_clients

    response = attacker.patch(
        "/settings/store",
        json={"store_id": owner_store_id, "name": "Hijacked store"},
    )

    assert response.status_code == 403
    assert response.json["success"] is False
    assert response.json["error"]["code"] == "STORE_ACCESS_DENIED"
