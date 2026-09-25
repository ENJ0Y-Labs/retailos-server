# server/tests/test_alerts.py
from server.app.extensions import db
from server.app.models.alert import Alert


def register_and_login(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "alerttester",
            "email": "alerttester@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": "alerttester@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 200

    return response.json["data"]["user"]["store_id"]


# Check that a sale automatically creates a low-stock alert.
def test_sale_triggers_low_stock_alert(client):
    store_id = register_and_login(client)

    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Bread",
            "price": 1200,
            "stock_quantity": 2,
            "low_stock_threshold": 2
        }
    )

    assert response.status_code == 201
    product_id = response.json["data"]["product"]["id"]

    response = client.post(
        "/sales",
        json={
            "store_id": store_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ]
        }
    )

    assert response.status_code == 201

    alert = Alert.query.filter_by(
        store_id=store_id,
        product_id=product_id,
        is_resolved=False
    ).first()

    assert alert is not None


# Check that an alert can be deleted.
def test_delete_alert(client):
    store_id = register_and_login(client)

    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Bread",
            "price": 1200,
            "stock_quantity": 1,
            "low_stock_threshold": 2
        }
    )

    product_id = response.json["data"]["product"]["id"]

    response = client.post(
        f"/alerts/generate-low-stock?store_id={store_id}"
    )

    assert response.status_code == 200

    alert = Alert.query.filter_by(
        store_id=store_id,
        product_id=product_id
    ).first()

    assert alert is not None

    response = client.delete(
        f"/alerts/delete?store_id={store_id}&id={alert.id}"
    )

    assert response.status_code == 200
    assert db.session.get(Alert, alert.id) is None
