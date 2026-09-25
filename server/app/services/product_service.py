# server/app/services/product_service.py
from decimal import Decimal

from flask import request, session
from sqlalchemy.exc import IntegrityError

from server.app.extensions import db
from server.app.models.inventory_movement import InventoryMovement
from server.app.models.product import Product
from server.app.utils.response import Response
from server.app.utils.store_authorization import get_authorized_store
from server.app.utils.validators import (
    validate_non_negative_number,
    validate_positive_integer,
    validate_required_string
)


class ProductService:
    def _data(self, product):
        return {
            "id": product.id,
            "store_id": product.store_id,
            "name": product.name,
            "price": str(product.price),
            "stock_quantity": product.stock_quantity,
            "low_stock_threshold": product.low_stock_threshold,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }

    def _movement_data(self, movement):
        return {
            "id": movement.id,
            "store_id": movement.store_id,
            "product_id": movement.product_id,
            "user_id": movement.user_id,
            "movement_type": movement.movement_type,
            "quantity_change": movement.quantity_change,
            "previous_quantity": movement.previous_quantity,
            "new_quantity": movement.new_quantity,
            "reason": movement.reason,
            "created_at": movement.created_at.isoformat()
        }

    def _get_data(self):
        data = request.get_json(silent=False)

        if not isinstance(data, dict):
            return (
                None,
                Response.error_response(
                    "VALIDATION_ERROR",
                    "Invalid input data",
                    {
                        "payload": "Payload must be a JSON object"
                    }
                ),
                400
            )

        return data, None, None

    def create_product(self):
        try:
            data, error, status = self._get_data()

            if error:
                return error, status

            store_id = data.get("store_id")
            name = data.get("name")
            price = data.get("price")
            stock = data.get("stock_quantity", 0)
            threshold = data.get("low_stock_threshold", 0)

            fields = {}

            if not isinstance(store_id, int):
                fields["store_id"] = "Store ID must be an integer"
            elif not get_authorized_store(store_id):
                fields["store_id"] = "You do not have access to this store"

            error = validate_required_string(name, "Product name")

            if error:
                fields["name"] = error

            error = validate_non_negative_number(price, "Price")

            if error:
                fields["price"] = error

            error = validate_positive_integer(
                stock,
                "Stock quantity",
                True
            )

            if error:
                fields["stock_quantity"] = error

            error = validate_positive_integer(
                threshold,
                "Low stock threshold",
                True
            )

            if error:
                fields["low_stock_threshold"] = error

            if fields:
                return Response.error_response(
                    "VALIDATION_ERROR",
                    "Invalid input data",
                    fields
                ), 400

            product = Product(
                store_id=store_id,
                name=name.strip(),
                price=Decimal(str(price)),
                stock_quantity=stock,
                low_stock_threshold=threshold
            )

            db.session.add(product)
            db.session.commit()

            return Response.success_response(
                {
                    "product": self._data(product)
                },
                "PRODUCT_CREATED"
            ), 201

        except IntegrityError:
            db.session.rollback()

            return Response.error_response(
                "CONFLICT_ERROR",
                "Product could not be created",
                {}
            ), 409

    def get_product(self):
        product_id = request.args.get("id", type=int)
        store_id = request.args.get("store_id", type=int)

        if not product_id or not store_id:
            return Response.error_response(
                "VALIDATION_ERROR",
                "Product ID and store ID are required",
                {}
            ), 400

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        product = Product.query.filter_by(
            id=product_id,
            store_id=store_id
        ).first()

        if not product:
            return Response.error_response(
                "PRODUCT_NOT_FOUND",
                "Product not found",
                {}
            ), 404

        return Response.success_response(
            {
                "product": self._data(product)
            },
            "PRODUCT_FOUND"
        ), 200

    def list_products(self):
        store_id = request.args.get("store_id", type=int)

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        products = Product.query.filter_by(
            store_id=store_id
        ).order_by(Product.name.asc()).all()

        return Response.success_response(
            {
                "products": [
                    self._data(product)
                    for product in products
                ]
            },
            "PRODUCTS_RETRIEVED"
        ), 200

    def update_product(self):
        try:
            data, error, status = self._get_data()

            if error:
                return error, status

            store_id = data.get("store_id")
            product_id = data.get("id")

            if not get_authorized_store(store_id):
                return Response.error_response(
                    "STORE_ACCESS_DENIED",
                    "You do not have access to this store",
                    {}
                ), 403

            product = Product.query.filter_by(
                id=product_id,
                store_id=store_id
            ).first()

            if not product:
                return Response.error_response(
                    "PRODUCT_NOT_FOUND",
                    "Product not found",
                    {}
                ), 404

            fields = {}

            if "name" in data:
                error = validate_required_string(
                    data["name"],
                    "Product name"
                )

                if error:
                    fields["name"] = error
                else:
                    product.name = data["name"].strip()

            if "price" in data:
                error = validate_non_negative_number(
                    data["price"],
                    "Price"
                )

                if error:
                    fields["price"] = error
                else:
                    product.price = Decimal(str(data["price"]))

            if "stock_quantity" in data:
                error = validate_positive_integer(
                    data["stock_quantity"],
                    "Stock quantity",
                    True
                )

                if error:
                    fields["stock_quantity"] = error
                else:
                    product.stock_quantity = data["stock_quantity"]

            if "low_stock_threshold" in data:
                error = validate_positive_integer(
                    data["low_stock_threshold"],
                    "Low stock threshold",
                    True
                )

                if error:
                    fields["low_stock_threshold"] = error
                else:
                    product.low_stock_threshold = data["low_stock_threshold"]

            if fields:
                return Response.error_response(
                    "VALIDATION_ERROR",
                    "Invalid input data",
                    fields
                ), 400

            db.session.commit()

            return Response.success_response(
                {
                    "product": self._data(product)
                },
                "PRODUCT_UPDATED"
            ), 200

        except IntegrityError:
            db.session.rollback()

            return Response.error_response(
                "CONFLICT_ERROR",
                "Product could not be updated",
                {}
            ), 409

    def delete_product(self):
        data, error, status = self._get_data()

        if error:
            return error, status

        store_id = data.get("store_id")
        product_id = data.get("id")

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        product = Product.query.filter_by(
            id=product_id,
            store_id=store_id
        ).first()

        if not product:
            return Response.error_response(
                "PRODUCT_NOT_FOUND",
                "Product not found",
                {}
            ), 404

        try:
            db.session.delete(product)
            db.session.commit()

            return Response.success_response(
                message="PRODUCT_DELETED"
            ), 200

        except IntegrityError:
            db.session.rollback()

            return Response.error_response(
                "CONFLICT_ERROR",
                "Product cannot be deleted because it has related records",
                {}
            ), 409

    def adjust_stock(self):
        data, error, status = self._get_data()

        if error:
            return error, status

        store_id = data.get("store_id")
        product_id = data.get("id")
        quantity_change = data.get("quantity_change")

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        if (
            not isinstance(quantity_change, int)
            or isinstance(quantity_change, bool)
        ):
            return Response.error_response(
                "VALIDATION_ERROR",
                "Invalid input data",
                {
                    "quantity_change": "Quantity change must be an integer"
                }
            ), 400

        product = Product.query.filter_by(
            id=product_id,
            store_id=store_id
        ).first()

        if not product:
            return Response.error_response(
                "PRODUCT_NOT_FOUND",
                "Product not found",
                {}
            ), 404

        new_quantity = product.stock_quantity + quantity_change

        if new_quantity < 0:
            return Response.error_response(
                "INSUFFICIENT_STOCK",
                "Stock quantity cannot become negative",
                {}
            ), 400

        previous_quantity = product.stock_quantity
        product.stock_quantity = new_quantity

        movement = InventoryMovement(
            store_id=store_id,
            product_id=product.id,
            user_id=session.get("user_id"),
            movement_type="ADJUSTMENT",
            quantity_change=quantity_change,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reason=data.get(
                "reason",
                "Manual stock adjustment"
            )
        )

        db.session.add(movement)
        db.session.commit()

        return Response.success_response(
            {
                "product": self._data(product)
            },
            "STOCK_ADJUSTED"
        ), 200

    def list_inventory_movements(self):
        store_id = request.args.get("store_id", type=int)
        product_id = request.args.get("product_id", type=int)

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        query = InventoryMovement.query.filter_by(
            store_id=store_id
        )

        if product_id:
            product = Product.query.filter_by(
                id=product_id,
                store_id=store_id
            ).first()

            if not product:
                return Response.error_response(
                    "PRODUCT_NOT_FOUND",
                    "Product not found",
                    {}
                ), 404

            query = query.filter_by(product_id=product_id)

        movements = query.order_by(
            InventoryMovement.created_at.desc()
        ).all()

        return Response.success_response(
            {
                "movements": [
                    self._movement_data(movement)
                    for movement in movements
                ]
            },
            "INVENTORY_MOVEMENTS_RETRIEVED"
        ), 200
