from flask import Blueprint
from server.app.middleware.auth_middleware import require_session
from server.app.services.customer_service import CustomerService

customer=CustomerService()
customer_bp=Blueprint("customer",__name__)

@customer_bp.route("",methods=["GET"])
@require_session
def list_customers():return customer.list_customers()

@customer_bp.route("",methods=["POST"])
@require_session
def create_customer():return customer.create_customer()

@customer_bp.route("/history",methods=["GET"])
@require_session
def customer_history():return customer.get_customer_history()
