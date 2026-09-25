from server.app.extensions import db
from server.app.models.product import Product
from server.app.models.inventory_movement import InventoryMovement


def register_and_login(client, username="productuser"):
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


def create_product(
    client,
    store_id,
    name="Rice 1kg",
    price=2500,
    stock_quantity=10,
    low_stock_threshold=2
):
    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": name,
            "price": price,
            "stock_quantity": stock_quantity,
            "low_stock_threshold": low_stock_threshold
        }
    )

    assert response.status_code == 201

    return response.json["data"]["product"]["id"]


def test_create_list_and_get_product(client):
    store_id = register_and_login(client)

    product_id = create_product(
        client,
        store_id,
        name="Rice 1kg",
        price=2500,
        stock_quantity=10,
        low_stock_threshold=2
    )

    response = client.get(
        f"/product/get?store_id={store_id}&id={product_id}"
    )

    assert response.status_code == 200

    product = response.json["data"]["product"]

    assert product["id"] == product_id
    assert product["name"] == "Rice 1kg"
    assert product["price"] == "2500.00"
    assert product["stock_quantity"] == 10

    create_product(
        client,
        store_id,
        name="Bread",
        price=1000,
        stock_quantity=5,
        low_stock_threshold=1
    )

    response = client.get(
        f"/product/list?store_id={store_id}"
    )

    assert response.status_code == 200

    products = response.json["data"]["products"]

    assert len(products) == 2
    assert products[0]["name"] == "Bread"
    assert products[1]["name"] == "Rice 1kg"


def test_update_product(client):
    store_id = register_and_login(client)
    product_id = create_product(client, store_id)

    response = client.patch(
        "/product/update",
        json={
            "store_id": store_id,
            "id": product_id,
            "name": "Rice 2kg",
            "price": 4500,
            "stock_quantity": 20,
            "low_stock_threshold": 5
        }
    )

    assert response.status_code == 200

    product = response.json["data"]["product"]

    assert product["name"] == "Rice 2kg"
    assert product["price"] == "4500.00"
    assert product["stock_quantity"] == 20
    assert product["low_stock_threshold"] == 5


def test_product_validation_rejects_invalid_data(client):
    store_id = register_and_login(client)

    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "",
            "price": -100,
            "stock_quantity": -5,
            "low_stock_threshold": 2
        }
    )

    assert response.status_code == 400
    assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_adjust_stock_creates_inventory_movement(client):
    store_id = register_and_login(client)
    product_id = create_product(
        client,
        store_id,
        stock_quantity=10
    )

    response = client.post(
        "/product/adjust",
        json={
            "store_id": store_id,
            "id": product_id,
            "quantity_change": 5,
            "reason": "Restocking"
        }
    )

    assert response.status_code == 200
    assert response.json["data"]["product"]["stock_quantity"] == 15

    movement = InventoryMovement.query.filter_by(
        product_id=product_id
    ).first()

    assert movement is not None
    assert movement.quantity_change == 5
    assert movement.previous_quantity == 10
    assert movement.new_quantity == 15
    assert movement.reason == "Restocking"


def test_adjust_stock_rejects_negative_result(client):
    store_id = register_and_login(client)
    product_id = create_product(
        client,
        store_id,
        stock_quantity=5
    )

    response = client.post(
        "/product/adjust",
        json={
            "store_id": store_id,
            "id": product_id,
            "quantity_change": -6
        }
    )

    assert response.status_code == 400
    assert response.json["error"]["code"] == "INSUFFICIENT_STOCK"

    product = db.session.get(Product, product_id)

    assert product.stock_quantity == 5


def test_delete_product(client):
    store_id = register_and_login(client)
    product_id = create_product(client, store_id)

    response = client.delete(
        "/product/delete",
        json={
            "store_id": store_id,
            "id": product_id
        }
    )

    assert response.status_code == 200
    assert db.session.get(Product, product_id) is None


def test_product_access_is_store_scoped(client):
    first_store_id = register_and_login(
        client,
        username="firstproductuser"
    )

    product_id = create_product(
        client,
        first_store_id,
        name="Private Product"
    )

    second_store_id = register_and_login(
        client,
        username="secondproductuser"
    )

    response = client.get(
        f"/product/get?store_id={first_store_id}&id={product_id}"
    )

    assert response.status_code == 403

    response = client.get(
        f"/product/list?store_id={second_store_id}"
    )

    assert response.status_code == 200
    assert response.json["data"]["products"] == []


def test_products_require_authentication(client):
    response = client.get("/product/list?store_id=1")

    assert response.status_code == 401
