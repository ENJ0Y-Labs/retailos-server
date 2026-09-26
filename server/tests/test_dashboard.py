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


def create_sale(client, store_id, transaction_id, product_name=None, quantity=2):
    product = client.post(
        "/product/create",
        json={
            "store_id": store_id,
            "name": product_name or f"Product {transaction_id}",
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
                    "quantity": quantity
                }
            ],
            "client_transaction_id": transaction_id
        }
    )

    assert response.status_code == 201

    return response.json["data"]["receipt"]["sale_id"]


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


# Check that daily brief guards against division by zero.
def test_daily_brief_handles_zero_yesterday_sales(client):
    store_id = register_and_login(client)

    create_sale(client, store_id, "daily-brief-zero")

    response = client.get(
        f"/dashboard/daily-brief?store_id={store_id}"
    )

    assert response.status_code == 200

    sales = response.json["data"]["sales"]

    assert sales["yesterday_total"] == "0.00"
    assert sales["change_percent"] == "0.00"
    assert sales["status"] == "UP"


# Check daily brief percentage change, high performer and declining product.
def test_daily_brief_compares_days_and_builds_insights(client):
    store_id = register_and_login(client)

    high_performer_sale_id = create_sale(
        client, store_id, "daily-brief-high",
        product_name="Fast Product", quantity=3
    )
    create_sale(
        client, store_id, "daily-brief-decline-today",
        product_name="Declining Product", quantity=1
    )
    yesterday_decline_sale_id = create_sale(
        client, store_id, "daily-brief-decline-yesterday",
        product_name="Declining Product", quantity=2
    )

    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    yesterday_sale = db.session.get(Sale, yesterday_decline_sale_id)
    yesterday_sale.created_at = yesterday
    db.session.commit()

    response = client.get(
        f"/dashboard/daily-brief?store_id={store_id}"
    )

    assert response.status_code == 200

    data = response.json["data"]

    assert data["sales"]["today_total"] == "10000.00"
    assert data["sales"]["yesterday_total"] == "5000.00"
    assert data["sales"]["change_percent"] == "100.00"
    assert data["sales"]["status"] == "UP"

    assert data["insights"]["high_performer"]["product_name"] == "Fast Product"
    assert data["insights"]["high_performer"]["units_sold"] == 3
    assert data["insights"]["declining_product"]["product_name"] == "Declining Product"
    assert data["insights"]["declining_product"]["yesterday_units_sold"] == 2
    assert data["insights"]["declining_product"]["today_units_sold"] == 1

    assert high_performer_sale_id != yesterday_decline_sale_id
