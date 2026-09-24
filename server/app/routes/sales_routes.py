from flask import Blueprint
from server.app.middleware.auth_middleware import require_session
from server.app.services.sales_service import SalesService

sales=SalesService()
sales_bp=Blueprint("sales",__name__)

@sales_bp.route("",methods=["POST"])
@require_session
def create_sale():return sales.create_sale()

@sales_bp.route("",methods=["GET"])
@require_session
def list_sales():return sales.list_sales()

@sales_bp.route("/get",methods=["GET"])
@require_session
def get_sale():return sales.get_sale()

@sales_bp.route("/receipt",methods=["GET"])
@require_session
def receipt():return sales.receipt()
