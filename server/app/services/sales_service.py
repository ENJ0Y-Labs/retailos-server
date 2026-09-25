# server/app/services/sales_service.py
from decimal import Decimal

from flask import request, session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from server.app.extensions import db
from server.app.models.customer import Customer
from server.app.models.inventory_movement import InventoryMovement
from server.app.models.product import Product
from server.app.models.sale import Sale
from server.app.models.sale_item import SaleItem
from server.app.utils.response import Response
from server.app.utils.store_authorization import get_authorized_store


class SalesService:
    def create_sale(self):
        data = request.get_json(silent=False)

        if not isinstance(data, dict):
            return Response.error_response(
                "VALIDATION_ERROR",
                "Invalid input data",
                {}
            ), 400

        store_id = data.get("store_id")
        items = data.get("items")
        customer_id = data.get("customer_id")
        client_transaction_id = data.get("client_transaction_id")

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        if not isinstance(items, list) or not items:
            return Response.error_response(
                "VALIDATION_ERROR",
                "At least one sale item is required",
                {}
            ), 400

        if client_transaction_id is not None:
            if not isinstance(client_transaction_id, str):
                return Response.error_response(
                    "VALIDATION_ERROR",
                    "Client transaction ID must be a string",
                    {}
                ), 400

            old_sale = Sale.query.filter_by(
                store_id=store_id,
                client_transaction_id=client_transaction_id
            ).first()

            if old_sale:
                return self._response(
                    old_sale,
                    "SALE_ALREADY_PROCESSED"
                ), 200

        if customer_id is not None:
            customer = Customer.query.filter_by(
                id=customer_id,
                store_id=store_id
            ).first()

            if not customer:
                return Response.error_response(
                    "CUSTOMER_NOT_FOUND",
                    "Customer not found",
                    {}
                ), 404

        try:
            sale = Sale(
                store_id=store_id,
                customer_id=customer_id,
                client_transaction_id=client_transaction_id,
                total_amount=Decimal("0.00")
            )

            db.session.add(sale)
            db.session.flush()

            total = Decimal("0.00")

            for item in items:
                if not isinstance(item, dict):
                    db.session.rollback()

                    return Response.error_response(
                        "VALIDATION_ERROR",
                        "Each sale item must be an object",
                        {}
                    ), 400

                product_id = item.get("product_id")
                quantity = item.get("quantity")

                if (
                    not isinstance(product_id, int)
                    or isinstance(product_id, bool)
                ):
                    db.session.rollback()

                    return Response.error_response(
                        "VALIDATION_ERROR",
                        "Product ID must be an integer",
                        {}
                    ), 400

                if (
                    not isinstance(quantity, int)
                    or isinstance(quantity, bool)
                    or quantity <= 0
                ):
                    db.session.rollback()

                    return Response.error_response(
                        "VALIDATION_ERROR",
                        "Quantity must be greater than zero",
                        {}
                    ), 400

                product = db.session.execute(
                    select(Product)
                    .where(
                        Product.id == product_id,
                        Product.store_id == store_id
                    )
                    .with_for_update()
                ).scalar_one_or_none()

                if not product:
                    db.session.rollback()

                    return Response.error_response(
                        "PRODUCT_NOT_FOUND",
                        "Product not found",
                        {}
                    ), 404

                if product.stock_quantity < quantity:
                    db.session.rollback()

                    return Response.error_response(
                        "INSUFFICIENT_STOCK",
                        "Insufficient stock",
                        {}
                    ), 400

                previous_quantity = product.stock_quantity
                product.stock_quantity -= quantity

                item_total = product.price * quantity
                total += item_total

                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    price_at_sale=product.price,
                    total=item_total
                )

                movement = InventoryMovement(
                    store_id=store_id,
                    product_id=product.id,
                    user_id=session.get("user_id"),
                    movement_type="SALE",
                    quantity_change=-quantity,
                    previous_quantity=previous_quantity,
                    new_quantity=product.stock_quantity,
                    reason=f"Sale #{sale.id}"
                )

                db.session.add(sale_item)
                db.session.add(movement)

            sale.total_amount = total

            db.session.commit()

            return self._response(
                sale,
                "SALE_CREATED"
            ), 201

        except IntegrityError:
            db.session.rollback()

            return Response.error_response(
                "CONFLICT_ERROR",
                "Sale could not be completed",
                {}
            ), 409

        except Exception:
            db.session.rollback()
            raise

    def list_sales(self):
        store_id = request.args.get("store_id", type=int)

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        sales = Sale.query.filter_by(
            store_id=store_id
        ).order_by(Sale.created_at.desc()).all()

        return Response.success_response(
            {
                "sales": [
                    {
                        "id": sale.id,
                        "customer_id": sale.customer_id,
                        "total_amount": str(sale.total_amount),
                        "created_at": sale.created_at.isoformat()
                    }
                    for sale in sales
                ]
            },
            "SALES_RETRIEVED"
        ), 200

    def get_sale(self):
        store_id = request.args.get("store_id", type=int)
        sale_id = request.args.get("id", type=int)

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        sale = Sale.query.filter_by(
            id=sale_id,
            store_id=store_id
        ).first()

        if not sale:
            return Response.error_response(
                "SALE_NOT_FOUND",
                "Sale not found",
                {}
            ), 404

        return self._response(
            sale,
            "SALE_FOUND"
        ), 200

    def receipt(self):
        store_id = request.args.get("store_id", type=int)
        sale_id = request.args.get("id", type=int)

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        sale = Sale.query.filter_by(
            id=sale_id,
            store_id=store_id
        ).first()

        if not sale:
            return Response.error_response(
                "SALE_NOT_FOUND",
                "Sale not found",
                {}
            ), 404

        return Response.success_response(
            {
                "receipt": self._receipt_data(sale)
            },
            "RECEIPT_GENERATED"
        ), 200

    def _receipt_data(self, sale):
        items = SaleItem.query.filter_by(
            sale_id=sale.id
        ).all()

        receipt_items = []

        for item in items:
            receipt_items.append(
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price_at_sale": str(item.price_at_sale),
                    "total": str(item.total)
                }
            )

        printable_lines = [
            "RetailOS Receipt",
            f"Sale: #{sale.id}",
            f"Date: {sale.created_at.isoformat()}",
            ""
        ]

        for item in receipt_items:
            printable_lines.append(
                f"Product {item['product_id']} x "
                f"{item['quantity']} = {item['total']}"
            )

        printable_lines.extend(
            [
                "",
                f"Total: {sale.total_amount}"
            ]
        )

        return {
            "sale_id": sale.id,
            "customer_id": sale.customer_id,
            "total_amount": str(sale.total_amount),
            "created_at": sale.created_at.isoformat(),
            "items": receipt_items,
            "printable_text": "\n".join(printable_lines)
        }

    def _response(self, sale, message):
        return Response.success_response(
            {
                "receipt": self._receipt_data(sale)
            },
            message
        )
