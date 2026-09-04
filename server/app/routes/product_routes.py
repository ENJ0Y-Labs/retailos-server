# server\app\routes\product_routes.py
from server.app.services.product_service import ProductService
from flask import Blueprint
from server.app.middleware.auth_middleware import require_session

product = ProductService()
product_bp = Blueprint("/product", __name__)

@product_bp.route("/create", method=['POST'])
@require_session
def create_product():
    return product.create_product()

@product_bp.route("/get", method=['GET'])
@require_session
def get_product():
    return product.get_product()

@product_bp.route("/list", method=['GET'])
@require_session
def list_products():
    return product.list_products()

@product_bp.route("/update", method=['PATCH'])
@require_session
def update_product():
    return product.update_product()

@product_bp.route("delete", method=['DELETE'])
@require_session
def delete_product():
    return product.delete_product()

@product_bp.route("adjust", method=['POST'])
@require_session
def adjust_stock():
    return product.adjust_stock()