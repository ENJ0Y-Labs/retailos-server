# server/app/services/insight_service.py
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func

from server.app.extensions import db
from server.app.models.alert import Alert
from server.app.models.product import Product
from server.app.models.sale import Sale
from server.app.models.sale_item import SaleItem
from server.app.utils.response import Response
from server.app.utils.store_authorization import get_authorized_store


class InsightService:
    def _sales_total(self, store_id, date):
        return Sale.query.filter(
            Sale.store_id == store_id,
            func.date(Sale.created_at) == date
        ).with_entities(
            func.coalesce(func.sum(Sale.total_amount), 0)
        ).scalar()

    def dashboard(self, store_id):
        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        today = datetime.now(timezone.utc).date()
        sales = Sale.query.filter(
            Sale.store_id == store_id,
            func.date(Sale.created_at) == today
        )
        total = self._sales_total(store_id, today)

        return Response.success_response(
            {
                "products_count": Product.query.filter_by(store_id=store_id).count(),
                "low_stock_count": Product.query.filter(
                    Product.store_id == store_id,
                    Product.low_stock_threshold.is_not(None),
                    Product.stock_quantity <= Product.low_stock_threshold
                ).count(),
                "open_alerts_count": Alert.query.filter_by(
                    store_id=store_id,
                    is_resolved=False
                ).count(),
                "today_sales_count": sales.count(),
                "today_sales_total": str(total)
            },
            "DASHBOARD_RETRIEVED"
        ), 200

    def daily_summary(self, store_id):
        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        today = datetime.now(timezone.utc).date()
        sales = Sale.query.filter(
            Sale.store_id == store_id,
            func.date(Sale.created_at) == today
        ).order_by(Sale.created_at.asc()).all()

        total = sum(
            (sale.total_amount for sale in sales),
            Decimal("0.00")
        )

        return Response.success_response(
            {
                "date": today.isoformat(),
                "sales_count": len(sales),
                "total_sales": str(total),
                "sales": [
                    {
                        "id": sale.id,
                        "total_amount": str(sale.total_amount),
                        "created_at": sale.created_at.isoformat()
                    }
                    for sale in sales
                ]
            },
            "DAILY_SUMMARY_RETRIEVED"
        ), 200

    def daily_brief(self, store_id):
        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        today_total = Decimal(str(self._sales_total(store_id, today)))
        yesterday_total = Decimal(str(self._sales_total(store_id, yesterday)))

        if yesterday_total != 0:
            change = ((today_total - yesterday_total) / yesterday_total) * 100
        else:
            change = Decimal("0.00")

        alerts = Alert.query.filter_by(
            store_id=store_id,
            is_resolved=False
        ).order_by(Alert.created_at.desc()).all()

        low_stock = Product.query.filter(
            Product.store_id == store_id,
            Product.low_stock_threshold.is_not(None),
            Product.stock_quantity <= Product.low_stock_threshold
        ).all()

        item_totals = SaleItem.query.join(Sale).filter(
            Sale.store_id == store_id,
            func.date(Sale.created_at) == today
        ).with_entities(
            SaleItem.product_id,
            func.sum(SaleItem.quantity).label("quantity")
        ).group_by(
            SaleItem.product_id
        ).order_by(
            func.sum(SaleItem.quantity).desc()
        ).all()

        high_performer = None

        if item_totals:
            product = db.session.get(Product, item_totals[0].product_id)

            if product:
                high_performer = {
                    "product_id": product.id,
                    "product_name": product.name,
                    "units_sold": int(item_totals[0].quantity)
                }

        if today_total > yesterday_total:
            status = "UP"
        elif today_total < yesterday_total:
            status = "DOWN"
        else:
            status = "STEADY"

        return Response.success_response(
            {
                "date": today.isoformat(),
                "sales": {
                    "today_total": str(today_total),
                    "yesterday_total": str(yesterday_total),
                    "change_percent": str(change.quantize(Decimal("0.01"))),
                    "status": status
                },
                "alerts": [
                    {
                        "id": alert.id,
                        "type": alert.type.value,
                        "message": alert.message,
                        "product_id": alert.product_id
                    }
                    for alert in alerts
                ],
                "insights": {
                    "restock_recommendations": [
                        {
                            "product_id": product.id,
                            "product_name": product.name,
                            "stock_quantity": product.stock_quantity,
                            "low_stock_threshold": product.low_stock_threshold
                        }
                        for product in low_stock
                    ],
                    "high_performer": high_performer
                }
            },
            "DAILY_BRIEF_RETRIEVED"
        ), 200
