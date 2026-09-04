# server\app\services\product_service.py
from flask import session, request
from server.app.models.product import Product
from server.app.utils.response import Response
from server.app.extensions import db
class ProductService:
    def __init__(self):
        pass
    def create_product(self):
        # extract input
        data = request.get_json(silent=False)
        store_id = data.get('store_id')
        name = data.get('name')
        price = data.get('price')
        stock_quantity = data.get('stock_quantity')
        low_stock_threshold = data.get('low_stock_threshold')

        if not isinstance(store_id, int) or not isinstance(name, str) or not isinstance(price, float) or not isinstance(stock_quantity, int) or not isinstance(low_stock_threshold, int):
            code = "VALIDATION ERROR"
            message = "Invalid input data"
            field = [
                "store_id" : "Store ID must be an integer",
                "name" : "Product name must be a string",
                "price" : "Price must be decimal",
                "stock_quantity" : "Stock quantity must be an integer",
                "low_stock_threshold" : "Stock Threshold must be an integer"
            ]
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
                                return Response.error_response(code, message), 400

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
                            return Response.error_response(code, message), 400
                    else:
                        code = "VALIDATION_ERROR"
                        message = "Low stock threshold must be non-negative"
                        return Response.error_response(code, message), 400
                else:
                    code = "VALIDATION_ERROR"
                    message = "Stock quantity must be non-negative"
                    return Response.error_response(code, message), 400
            else:
                code = "VALIDATION_ERROR"
                message = "Price must be non-negative"
                return Response.error_response(code, message), 400
        else:
            code = "VALIDATION_ERROR"
            message = "Name must be alphanumeric"
            return Response.error_response(code, message), 400
    
    def get_product(self):
        data = request.get_json(silent=False)

        id = data.get('id')
        store_id = data.get('store_id')

        # Fetch the product from the database 
        product_exist = Product.query.filter_by(id=id, store_id=store_id).first()

        # Check if the product exists
        if not product_exist:
            code = "PRODUCT_NOT_FOUND"
            message = "Product not found"
            return Response.error_response(code, message), 404
        
        # Return the found product instance
        return Response.success_response(product_exist, "PRODUCT_FOUND"), 200

    def list_products(self):
        data = request.get_json(silent=False)

        store_id = data.get('store_id')

        # Fetch all products for the given store_id from the database
        product_list = Product.query.filter_by(store_id=store_id).all()

        if not product_list:
            code = "PRODUCTS_NOT_FOUND"
            message = "No products found for the given store"
            return Response.error_response(code, message), 404

        # Return the list of product instances
        return Response.success_response(product_list, "PRODUCTS_FOUND"), 200

    def update_product(self):
        data = request.get_json(silent=False)

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
            return Response.error_response(code, message), 404

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

    def delete_product(self):
        data = request.get_json(silent=False)

        id = data.get('id')
        store_id = data.get('store_id')

        # fetch the existing product
        product_exist = Product.query.filter_by(id=id, store_id=store_id).first()
        if not product_exist:
            code = "PRODUCT_NOT_FOUND"
            message = "product not found"

            return Response.error_response(code, message), 404

        # remove the product from the database
        db.session.delete(product_exist)
        db.session.flush()
        db.session.commit()

        # return a confirmation message
        message = "PRODUCT_DELETED"
        return Response.success_response(message=message)

    def adjust_stock(self):
        # fetch the existing product
        data = request.get_json(silent=False)

        id = data.get('id')
        store_id = data.get('store_id')
        quantity_change = data.get('quantity_change')

        # validate input
        if not quantity_change >= 0:
            code = "VALIDATION_ERROR"
            message = "Additional quantity must ne non-negative"

            return Response.error_response(code, message), 400

        # fetch the existing product
        product = Product.query.filter_by(id=id, store_id=store_id).first()
        if not product:
            code = "PRODUCT_NOT_FOUND"
            message = "product not found"

            return Response.error_response(code, message), 404

        # calculate the new stock level
        current_stock_quantity = product.stock_quantity

        new_stock_quantity = current_stock_quantity + quantity_change

        # Update the product's stock attribute with the new value
        new_product = Product(
            name = product.name,
            price = product.price
            stock_quantity = new_stock_quantity
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
