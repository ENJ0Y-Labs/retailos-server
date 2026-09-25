def register_and_login(client, username="dashboarduser"):
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


def create_sale(client, store_id, transaction_id):
    product = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": f"Product {transaction_id}",
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
            "client_transaction_id": transaction_id
        }
    )

    assert response.status_code == 201


def test_dashboard_returns_store_metrics(client):
    store_id = register_and_login(client)

    create_sale(client, store_id, "dashboard-sale-001")

    response = client.get(
        f"/dashboard?store_id={store_id}"
    )

    assert response.status_code == 200

    data = response.json["data"]

    assert data["products_count"] == 1
    assert data["low_stock_count"] == 0
    assert data["open_alerts_count"] == 0
    assert data["today_sales_count"] == 1
    assert data["today_sales_total"] == "5000.00"


def test_daily_summary_returns_sales(client):
    store_id = register_and_login(client)

    create_sale(client, store_id, "dashboard-sale-002")
    create_sale(client, store_id, "dashboard-sale-003")

    response = client.get(
        f"/dashboard/daily-summary?store_id={store_id}"
    )

    assert response.status_code == 200

    data = response.json["data"]

    assert data["sales_count"] == 2
    assert data["total_sales"] == "10000.00"
    assert len(data["sales"]) == 2


def test_dashboard_reflects_low_stock_products(client):
    store_id = register_and_login(client)

    response = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": "Low Stock Product",
            "price": 1000,
            "stock_quantity": 2,
            "low_stock_threshold": 5
        }
    )

    assert response.status_code == 201

    response = client.get(
        f"/dashboard?store_id={store_id}"
    )

    assert response.status_code == 200

    data = response.json["data"]

    assert data["products_count"] == 1
    assert data["low_stock_count"] == 1


def test_dashboard_requires_authentication(client):
    response = client.get("/dashboard?store_id=1")

    assert response.status_code == 401


def test_daily_summary_requires_authentication(client):
    response = client.get("/dashboard/daily-summary?store_id=1")

    assert response.status_code == 401
