# server/tests/test_products.py
def register_and_login(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "producttester",
            "email": "producttester@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": "producttester@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 200

    return response.json["data"]["user"]["store_id"]


# Check that a product can be created.
def test_create_product(client):
    store_id = register_and_login(client)

    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Rice",
            "price": 2500,
            "stock_quantity": 10,
            "low_stock_threshold": 3
        }
    )

    assert response.status_code == 201
    assert response.json["data"]["product"]["name"] == "Rice"


# Check that negative price is rejected.
def test_create_product_rejects_negative_price(client):
    store_id = register_and_login(client)

    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Rice",
            "price": -1,
            "stock_quantity": 10
        }
    )

    assert response.status_code == 400
    assert response.json["error"]["code"] == "VALIDATION_ERROR"


# Check that an omitted low stock threshold disables the low stock rule.
def test_create_product_allows_no_low_stock_threshold(client):
    store_id = register_and_login(client)

    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Rice",
            "price": 2500,
            "stock_quantity": 10
        }
    )

    assert response.status_code == 201
    assert response.json["data"]["product"]["low_stock_threshold"] is None


# Check that products are limited to the user's store.
def test_list_products_requires_store_access(client):
    first_store_id = register_and_login(client)

    response = client.post(
        "/product/create",
        json={
            "store_id": first_store_id,
            "name": "Rice",
            "price": 2500,
            "stock_quantity": 10
        }
    )

    assert response.status_code == 201

    response = client.get(
        f"/product/list?store_id={first_store_id}"
    )

    assert response.status_code == 200
    assert len(response.json["data"]["products"]) == 1
