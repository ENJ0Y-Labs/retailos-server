# server/tests/test_sales.py
from server.app.extensions import db
from server.app.models.product import Product


# Register a user and log in.
def register_and_login(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "salesuser",
            "email": "salesuser@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": "salesuser@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 200

    return response.json["data"]["user"]["store_id"]


# Check that a sale reduces stock correctly.
def test_sale_updates_inventory_atomically(client):
    store_id = register_and_login(client)

    product = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Rice 1kg",
            "price": 2500,
            "stock_quantity": 10,
            "low_stock_threshold": 2
        }
    )

    assert product.status_code == 201

    product_id = product.json["data"]["product"]["id"]

    response = client.post(
        "/sales",
        json={
            "store_id": store_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ],
            "client_transaction_id": "test-sale-001"
        }
    )

    assert response.status_code == 201
    assert response.json["data"]["receipt"]["total_amount"] == "5000.00"

    stored = db.session.get(Product, product_id)

    assert stored.stock_quantity == 8


# Check that the same client transaction is not processed twice.
def test_duplicate_client_transaction_is_not_processed_twice(client):
    store_id = register_and_login(client)

    product = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Bread",
            "price": 1000,
            "stock_quantity": 5,
            "low_stock_threshold": 1
        }
    )

    product_id = product.json["data"]["product"]["id"]

    first = client.post(
        "/sales",
        json={
            "store_id": store_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ],
            "client_transaction_id": "same-sale"
        }
    )

    second = client.post(
        "/sales",
        json={
            "store_id": store_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ],
            "client_transaction_id": "same-sale"
        }
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert db.session.get(Product, product_id).stock_quantity == 4
