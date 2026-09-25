# server/tests/test_customer.py
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


# Check that a customer can be created.
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


# Check that customers can be listed.
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


# Check that customer purchase history is returned.
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


# Check that a customer name is required.
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


# Check that another store cannot access this customer's history.
def test_customer_history_is_store_scoped(client):
    first_store_id = register_and_login(
        client,
        username="firstcustomeruser"
    )
    customer_id = create_customer(client, first_store_id)

    second_store_id = register_and_login(
        client,
        username="secondcustomeruser"
    )

    response = client.get(
        f"/customers/history?store_id={first_store_id}&id={customer_id}"
    )

    assert second_store_id != first_store_id
    assert response.status_code == 403


# Check that customers require authentication.
def test_customers_require_authentication(client):
    response = client.get("/customers?store_id=1")

    assert response.status_code == 401
