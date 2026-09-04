# server\app\services\product_service.py
from flask import session, request
from sqlalchemy.exc import IntegrityError
from server.app.models.product import Product
from server.app.utils.response import Response
from server.app.extensions import db
class ProductService:
    def __init__(self):
        pass
    def create_product(self):
        try:
            # extract input
            data = request.get_json(silent=False)

            if not isinstance(data, dict):
                code = "VALIDATION_ERROR"
                message = "invalid input data"
                fields = {
                    "payload" : "Payload must be a JSON object"
                }
                return Response.error_response(code, message, fields), 400
        
            store_id = data.get('store_id')
            name = data.get('name')
            price = data.get('price')
            stock_quantity = data.get('stock_quantity')
            low_stock_threshold = data.get('low_stock_threshold')

            if not isinstance(store_id, int) or not isinstance(name, str) or not isinstance(price, float) or not isinstance(stock_quantity, int) or not isinstance(low_stock_threshold, int):
                code = "VALIDATION ERROR"
                message = "Invalid input data"
                field = {
                    "store_id" : "Store ID must be an integer",
                    "name" : "Product name must be a string",
                    "price" : "Price must be decimal",
                    "stock_quantity" : "Stock quantity must be an integer",
                    "low_stock_threshold" : "Stock Threshold must be an integer"
                }
                return Response.error_response(code, message, field), 400

            # validate data
            if name.isalnum():
                if price >= 0:
                    if stock_quantity >= 0:
                        if low_stock_threshold >= 0:
                            if low_stock_threshold <= stock_quantity:
                                # Check if a product already exists
                                name_exists = Product.query.filter_by(store_id=store_id, name=name).first()
                                if name_exists:
                                    code = "PRODUCT_ALREADY_EXISTS"
                                    message = "Product with this name already exists"
                                    field = {
                                        "name" : "Product name must be unique within the store"
                                    }
                                    return Response.error_response(code, message, field), 400

                                # Create a new Product model instance
                                new_product = Product(
                                    store_id=store_id,
                                    name=name,
                                    price=price,
                                    stock_quantity=stock_quantity,
                                    low_stock_threshold=low_stock_threshold
                                )
                                db.session.add(new_product)
                                db.session.flush()
                                db.session.commit()

                                # return structured response
                                data = {
                                    "product": {
                                        "id": new_product.id,
                                        "store_id": new_product.store_id,
                                        "name": new_product.name,
                                        "price": new_product.price,
                                        "stock_quantity": new_product.stock_quantity,
                                        "low_stock_threshold": new_product.low_stock_threshold
                                    }
                                }
                                message = "PRODUCT_CREATED"
                                return Response.success_response(data, message), 200
                            else:
                                code = "VALIDATION_ERROR"
                                message = "Low stock threshold cannot be greater than stock quantity"
                                field = {
                                    "low_stock_threshold" : "Low stock threshold must be less than or equal to stock quantity"
                                }
                                return Response.error_response(code, message, field), 400
                        else:
                            code = "VALIDATION_ERROR"
                            message = "Low stock threshold must be non-negative"
                            field = {
                                "low_stock_threshold" : "Low stock threshold must be non-negative"
                            }
                            return Response.error_response(code, message), 400
                    else:
                        code = "VALIDATION_ERROR"
                        message = "Stock quantity must be non-negative"
                        field = {
                            "stock_quantity" : "Stock quantity must be non-negative"
                        }
                        return Response.error_response(code, message, field), 400
                else:
                    code = "VALIDATION_ERROR"
                    message = "Price must be non-negative"
                    field = {
                        "price" : "Price must be non-negative"
                    }
                    return Response.error_response(code, message, field), 400
            else:
                code = "VALIDATION_ERROR"
                message = "Name must be alphanumeric"
                field = {
                    "name" : "Name must be alphanumeric"
                }
                return Response.error_response(code, message, field), 400
        except IntegrityError:
            return Response.error_response(
                code="CONFLICT_ERROR",
                message="Database unique constraint violation",
                fields={
                    "product_name": "Product name must be unique within the store"
                }
            ), 409
        except Exception as e:
            return Response.error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                fields={
                    "error": str(e)
                }
            ), 500
    
    def get_product(self):
        try:
            data = request.get_json(silent=False)

            if not isinstance(data, dict):
                code = "VALIDATION_ERROR"
                message = "invalid input data"
                fields = {
                    "payload" : "Payload must be a JSON object"
                }
                return Response.error_response(code, message, fields), 400

            id = data.get('id')
            store_id = data.get('store_id')

            # Fetch the product from the database 
            product_exist = Product.query.filter_by(id=id, store_id=store_id).first()

            # Check if the product exists
            if not product_exist:
                code = "PRODUCT_NOT_FOUND"
                message = "Product not found"
                field = {
                    "id" : "Product with the given ID does not exist in the specified store"
                }
                return Response.error_response(code, message, field), 404
            
            # Return the found product instance
            return Response.success_response(product_exist, "PRODUCT_FOUND"), 200
        except IntegrityError:
            return Response.error_response(
                code="CONFLICT_ERROR",
                message="Database constraint violation",
                fields={
                    "product_id": "Unable to retrieve product"
                }
            ), 409
        except Exception as e:
            return Response.error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                fields={
                    "error": str(e)
                }
            ), 500

    def list_products(self):
        try:
            data = request.get_json(silent=False)

            if not isinstance(data, dict):
                code = "VALIDATION_ERROR"
                message = "invalid input data"
                fields = {
                    "payload" : "Payload must be a JSON object"
                }
                return Response.error_response(code, message, fields), 400

            store_id = data.get('store_id')

            # Fetch all products for the given store_id from the database
            product_list = Product.query.filter_by(store_id=store_id).all()

            if not product_list:
                code = "PRODUCTS_NOT_FOUND"
                message = "No products found for the given store"
                field = {
                    "store_id" : "No products found for the given store"
                }
                return Response.error_response(code, message, field), 404

            # Return the list of product instances
            return Response.success_response(product_list, "PRODUCTS_FOUND"), 200
        except IntegrityError:
            return Response.error_response(
                code="CONFLICT_ERROR",
                message="Database constraint violation",
                fields={
                    "store_id": "Unable to list products for this store"
                }
            ), 409
        except Exception as e:
            return Response.error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                fields={
                    "error": str(e)
                }
            ), 500

    def update_product(self):
        try:
            data = request.get_json(silent=False)

            if not isinstance(data, dict):
                code = "VALIDATION_ERROR"
                message = "invalid input data"
                fields = {
                    "payload" : "Payload must be a JSON object"
                }
                return Response.error_response(code, message, fields), 400

            new_id = data.get('id')
            new_store_id = data.get('store_id')
            new_name = data.get('name')
            new_price = data.get('price')
            new_stock_quantity = data.get('stock_quantity')
            new_low_stock_threshold = data.get('low_stock_threshold')

            # fetch the existing product
            product_exist = Product.query.filter_by(id=new_id, store_id=new_store_id).first()
            if not product_exist:
                code = "PRODUCT_NOT_FOUND"
                message = "Product not found"
                field = {
                    "id" : "Product with the given ID does not exist in the specified store"
                }
                return Response.error_response(code, message, field), 404

            # loop through the incoming data and update the product's attributes
            if not product_exist.name == new_name:
                name = new_name

            if not product_exist.price == new_price:
                price = new_price

            if not product_exist.stock_quantity == new_stock_quantity:
                stock_quantity = new_stock_quantity

            if not product_exist.low_stock_threshold == new_low_stock_threshold:
                low_stock_threshold = new_low_stock_threshold

            new_product = Product(
                name = name,
                price = price,
                stock_quantity = stock_quantity,
                low_stock_threshold = low_stock_threshold
            )        
            db.session.add(new_product)
            db.session.flush()
            db.session.commit()

            # return structured response
            data = {
                "product": {
                    "name": new_product.name,
                    "price": new_product.price,
                    "stock_quantity": new_product.stock_quantity,
                    "low_stock_threshold": new_product.low_stock_threshold
                }
            }
            message = "PRODUCT_UPDATED"
            return Response.success_response(data, message), 200
        except IntegrityError:
            return Response.error_response(
                code="CONFLICT_ERROR",
                message="Database unique constraint violation",
                fields={
                    "product_name": "Product name must be unique within the store"
                }
            ), 409
        except Exception as e:
            return Response.error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                fields={
                    "error": str(e)
                }
            ), 500

    def delete_product(self):
        try:
            data = request.get_json(silent=False)

            if not isinstance(data, dict):
                code = "VALIDATION_ERROR"
                message = "invalid input data"
                fields = {
                    "payload" : "Payload must be a JSON object"
                }
                return Response.error_response(code, message, fields), 400

            id = data.get('id')
            store_id = data.get('store_id')

            # fetch the existing product
            product_exist = Product.query.filter_by(id=id, store_id=store_id).first()
            if not product_exist:
                code = "PRODUCT_NOT_FOUND"
                message = "product not found"
                field = {
                    "id" : "Product with the given ID does not exist in the specified store"
                }
                return Response.error_response(code, message, field), 404

            # remove the product from the database
            db.session.delete(product_exist)
            db.session.flush()
            db.session.commit()

            # return a confirmation message
            message = "PRODUCT_DELETED"
            return Response.success_response(message=message)
        except IntegrityError:
            return Response.error_response(
                code="CONFLICT_ERROR",
                message="Database constraint violation",
                fields={
                    "product_id": "Product cannot be deleted due to related records"
                }
            ), 409
        except Exception as e:
            return Response.error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                fields={
                    "error": str(e)
                }
            ), 500

    def adjust_stock(self):
        try:
            # fetch the existing product
            data = request.get_json(silent=False)

            if not isinstance(data, dict):
                code = "VALIDATION_ERROR"
                message = "invalid input data"
                fields = {
                    "payload" : "Payload must be a JSON object"
                }
                return Response.error_response(code, message, fields), 400

            id = data.get('id')
            store_id = data.get('store_id')
            quantity_change = data.get('quantity_change')

            # validate input
            if not quantity_change >= 0:
                code = "VALIDATION_ERROR"
                message = "Additional quantity must be non-negative"
                field = {
                    "quantity_change" : "Additional quantity must be a non-negative number"
                }
                return Response.error_response(code, message, field), 400

            # fetch the existing product
            product = Product.query.filter_by(id=id, store_id=store_id).first()
            if not product:
                code = "PRODUCT_NOT_FOUND"
                message = "product not found"
                field = {
                    "id" : "Product with the given ID does not exist in the specified store"
                }
                return Response.error_response(code, message, field), 404

            # calculate the new stock level
            current_stock_quantity = product.stock_quantity

            new_stock_quantity = current_stock_quantity + quantity_change

            # Update the product's stock attribute with the new value
            new_product = Product(
                name = product.name,
                price = product.price,
                stock_quantity = new_stock_quantity,
                low_stock_threshold = product.low_stock_threshold
            )

            db.session.add(new_product)
            db.session.flush()
            db.session.commit()

            # return the updated product instance
            data = {
                "product": {
                    "name": new_product.name,
                    "price": new_product.price,
                    "stock_quantity": new_product.stock_quantity,
                    "low_stock_threshold": new_product.low_stock_threshold
                }
            }
            message = "STOCK_ADJUSTED"
            return Response.success_response(data, message), 200
        except IntegrityError:
            return Response.error_response(
                code="CONFLICT_ERROR",
                message="Database constraint violation",
                fields={
                    "quantity_change": "Unable to adjust stock for this product"
                }
            ), 409
        except Exception as e:
            return Response.error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                fields={
                    "error": str(e)
                }
            ), 500
