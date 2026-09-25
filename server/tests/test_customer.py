def register_and_login(client, username="customeruser"):
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


def create_customer(client, store_id, name="John Customer"):
    response = client.post(
        "/customers",
        json={
            "store_id": store_id,
            "name": name,
            "contact": "08012345678"
        }
    )

    assert response.status_code == 201

    return response.json["data"]["customer"]["id"]


def test_create_customer(client):
    store_id = register_and_login(client)

    response = client.post(
        "/customers",
        json={
            "store_id": store_id,
            "name": "John Customer",
            "contact": "08012345678"
        }
    )

    assert response.status_code == 201
    assert response.json["data"]["customer"]["name"] == "John Customer"
    assert response.json["data"]["customer"]["contact"] == "08012345678"


def test_list_customers(client):
    store_id = register_and_login(client)

    create_customer(client, store_id, "John Customer")
    create_customer(client, store_id, "Jane Customer")

    response = client.get(
        f"/customers?store_id={store_id}"
    )

    assert response.status_code == 200

    customers = response.json["data"]["customers"]

    assert len(customers) == 2
    assert customers[0]["name"] == "Jane Customer"
    assert customers[1]["name"] == "John Customer"


def test_customer_history(client):
    store_id = register_and_login(client)
    customer_id = create_customer(client, store_id)

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

    sale = client.post(
        "/sales",
        json={
            "store_id": store_id,
            "customer_id": customer_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ],
            "client_transaction_id": "customer-history-sale"
        }
    )

    assert sale.status_code == 201

    response = client.get(
        f"/customers/history?store_id={store_id}&id={customer_id}"
    )

    assert response.status_code == 200

    customer = response.json["data"]["customer"]

    assert customer["id"] == customer_id
    assert len(customer["purchase_history"]) == 1
    assert customer["purchase_history"][0]["total_amount"] == "5000.00"
    assert customer["purchase_history"][0]["items"][0]["quantity"] == 2


def test_create_customer_requires_name(client):
    store_id = register_and_login(client)

    response = client.post(
        "/customers",
        json={
            "store_id": store_id,
            "contact": "08012345678"
        }
    )

    assert response.status_code == 400
    assert response.json["error"]["code"] == "VALIDATION_ERROR"


def test_customers_require_authentication(client):
    response = client.get("/customers?store_id=1")

    assert response.status_code == 401
