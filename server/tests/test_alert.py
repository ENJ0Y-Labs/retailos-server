from server.app.extensions import db
from server.app.models.alert import Alert
from server.app.models.user import User


def register_and_login(client, username="alertuser"):
    email = f"{username}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "test123"
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test123"
        }
    )

    assert response.status_code == 200

    return response.json["data"]["user"]["store_id"]


def create_product(client, store_id, stock_quantity=2, low_stock_threshold=5):
    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Rice 1kg",
            "price": 2500,
            "stock_quantity": stock_quantity,
            "low_stock_threshold": low_stock_threshold
        }
    )

    assert response.status_code == 201

    return response.json["data"]["product"]["id"]


def test_generate_low_stock_alert(client):
    store_id = register_and_login(client)
    product_id = create_product(client, store_id)

    response = client.post(
        f"/alerts/generate-low-stock?store_id={store_id}"
    )

    assert response.status_code == 200
    assert response.json["data"]["created_alerts"] == [product_id]

    alert = Alert.query.filter_by(
        store_id=store_id,
        product_id=product_id
    ).first()

    assert alert is not None
    assert alert.is_resolved is False


def test_list_alerts_returns_open_alerts(client):
    store_id = register_and_login(client)
    product_id = create_product(client, store_id)

    response = client.post(
        f"/alerts/generate-low-stock?store_id={store_id}"
    )

    assert response.status_code == 200

    response = client.get(
        f"/alerts?store_id={store_id}"
    )

    assert response.status_code == 200
    assert len(response.json["data"]["alerts"]) == 1
    assert response.json["data"]["alerts"][0]["product_id"] == product_id


def test_resolve_alert(client):
    store_id = register_and_login(client)
    product_id = create_product(client, store_id)

    response = client.post(
        f"/alerts/generate-low-stock?store_id={store_id}"
    )

    assert response.status_code == 200

    alert = Alert.query.filter_by(
        store_id=store_id,
        product_id=product_id
    ).first()

    response = client.post(
        f"/alerts/resolve?store_id={store_id}&id={alert.id}"
    )

    assert response.status_code == 200

    db.session.refresh(alert)

    assert alert.is_resolved is True

    response = client.get(
        f"/alerts?store_id={store_id}"
    )

    assert response.status_code == 200
    assert response.json["data"]["alerts"] == []


def test_alerts_require_authentication(client):
    response = client.get("/alerts?store_id=1")

    assert response.status_code == 401
