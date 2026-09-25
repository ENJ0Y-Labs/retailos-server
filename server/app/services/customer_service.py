# server/app/services/customer_service.py
from flask import request

from server.app.extensions import db
from server.app.models.customer import Customer
from server.app.models.sale import Sale
from server.app.models.sale_item import SaleItem
from server.app.utils.response import Response
from server.app.utils.store_authorization import get_authorized_store
from server.app.utils.validators import validate_required_string


class CustomerService:
    def list_customers(self):
        store_id = request.args.get("store_id", type=int)

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        customers = Customer.query.filter_by(
            store_id=store_id
        ).order_by(Customer.name.asc()).all()

        return Response.success_response(
            {
                "customers": [
                    {
                        "id": customer.id,
                        "name": customer.name,
                        "contact": customer.contact,
                        "created_at": customer.created_at.isoformat()
                    }
                    for customer in customers
                ]
            },
            "CUSTOMERS_RETRIEVED"
        ), 200

    def create_customer(self):
        data = request.get_json(silent=False)

        if not isinstance(data, dict):
            return Response.error_response(
                "VALIDATION_ERROR",
                "Invalid input data",
                {}
            ), 400

        store_id = data.get("store_id")
        name = data.get("name")
        contact = data.get("contact")

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

        error = validate_required_string(
            name,
            "Customer name"
        )

        if error:
            return Response.error_response(
                "VALIDATION_ERROR",
                "Invalid input data",
                {
                    "name": error
                }
            ), 400

        customer = Customer(
            store_id=store_id,
            name=name.strip(),
            contact=contact
        )

        db.session.add(customer)
        db.session.commit()

        return Response.success_response(
            {
                "customer": {
                    "id": customer.id,
                    "name": customer.name,
                    "contact": customer.contact
                }
            },
            "CUSTOMER_CREATED"
        ), 201

    def get_customer_history(self):
        customer_id = request.args.get("id", type=int)
        store_id = request.args.get("store_id", type=int)

        if not get_authorized_store(store_id):
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {}
            ), 403

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

        sales = Sale.query.filter_by(
            customer_id=customer.id,
            store_id=store_id
        ).order_by(Sale.created_at.desc()).all()

        history = []

        for sale in sales:
            items = SaleItem.query.filter_by(
                sale_id=sale.id
            ).all()

            history.append(
                {
                    "sale_id": sale.id,
                    "total_amount": str(sale.total_amount),
                    "created_at": sale.created_at.isoformat(),
                    "items": [
                        {
                            "product_id": item.product_id,
                            "quantity": item.quantity,
                            "total": str(item.total)
                        }
                        for item in items
                    ]
                }
            )

        return Response.success_response(
            {
                "customer": {
                    "id": customer.id,
                    "name": customer.name,
                    "contact": customer.contact,
                    "purchase_history": history
                }
            },
            "CUSTOMER_HISTORY_RETRIEVED"
        ), 200
