from server.app.models.store import Store


def register_and_login(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "subscriptionuser",
            "email": "subscriptionuser@example.com",
            "password": "test123",
        },
    )
    assert response.status_code == 201
    store_id = response.json["data"]["user"]["store_id"]
    response = client.post(
        "/auth/login",
        json={"email": "subscriptionuser@example.com", "password": "test123"},
    )
    assert response.status_code == 200
    return store_id


def test_plan_catalog_has_authoritative_prices_and_limits(client):
    response = client.get("/subscriptions/plans")
    assert response.status_code == 200
    plans = {plan["id"]: plan for plan in response.json["data"]["plans"]}
    assert plans["free"]["price"] == {
        "amount": 0, "currency": "NGN", "interval": "month"
    }
    assert plans["free"]["limits"] == {
        "products": 100, "customers": 100, "sales_per_month": 500
    }
    assert plans["pro"]["price"] == {
        "amount": 4999, "currency": "NGN", "interval": "month"
    }
    assert plans["pro"]["limits"] == {
        "products": None, "customers": None, "sales_per_month": None
    }


def test_subscription_state_requires_authenticated_store_access(client):
    response = client.get("/subscriptions?store_id=1")
    assert response.status_code == 401

    store_id = register_and_login(client)
    response = client.get(f"/subscriptions?store_id={store_id}")
    assert response.status_code == 200
    subscription = response.json["data"]["subscription"]
    assert subscription["plan"]["id"] == "free"
    assert subscription["subscription_status"] == "active"


def test_upgrade_request_stays_pending_and_does_not_grant_pro(client):
    store_id = register_and_login(client)
    response = client.post(
        "/subscriptions/change",
        json={"store_id": store_id, "plan": "pro"},
    )
    assert response.status_code == 202
    change = response.json["data"]["change"]
    assert change["target_plan"] == "pro"
    assert change["status"] == "pending"
    assert change["activation"] == "not_activated"
    assert change["price"]["amount"] == 4999
    assert response.json["data"]["billing"]["status"] == "not_configured"

    state_response = client.get(f"/subscriptions?store_id={store_id}")
    assert state_response.status_code == 200
    subscription = state_response.json["data"]["subscription"]
    assert subscription["plan"]["id"] == "free"
    assert subscription["pending_change"]["status"] == "pending"


def test_pending_change_can_be_cancelled(client):
    store_id = register_and_login(client)
    response = client.post(
        "/subscriptions/change",
        json={"store_id": store_id, "plan": "pro"},
    )
    change_id = response.json["data"]["change"]["id"]

    response = client.post(
        "/subscriptions/change/cancel",
        json={"store_id": store_id, "change_id": change_id},
    )
    assert response.status_code == 200
    assert response.json["data"]["status"] == "cancelled"
    assert Store.query.get(store_id).current_plan == "free"


def test_unknown_plan_is_rejected(client):
    store_id = register_and_login(client)
    response = client.post(
        "/subscriptions/change",
        json={"store_id": store_id, "plan": "enterprise"},
    )
    assert response.status_code == 400
    assert response.json["error"]["code"] == "INVALID_PLAN"



def test_free_plan_product_limit_is_enforced_by_server(client, monkeypatch):
    from server.app.services.subscription_service import PLAN_CATALOG

    store_id = register_and_login(client)
    monkeypatch.setitem(PLAN_CATALOG["free"]["limits"], "products", 0)
    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Limit test product",
            "price": 100,
            "opening_stock": 1,
        },
    )
    assert response.status_code == 403
    assert response.json["error"]["code"] == "PLAN_LIMIT_REACHED"


def test_free_plan_customer_limit_is_enforced_by_server(client, monkeypatch):
    from server.app.services.subscription_service import PLAN_CATALOG

    store_id = register_and_login(client)
    monkeypatch.setitem(PLAN_CATALOG["free"]["limits"], "customers", 0)
    response = client.post(
        "/customers",
        json={"store_id": store_id, "name": "Limit test customer"},
    )
    assert response.status_code == 403
    assert response.json["error"]["code"] == "PLAN_LIMIT_REACHED"
