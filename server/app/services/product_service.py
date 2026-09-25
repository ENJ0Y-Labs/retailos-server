from decimal import Decimal
from flask import session,request
from sqlalchemy.exc import IntegrityError
from server.app.models.product import Product
from server.app.models.inventory_movement import InventoryMovement
from server.app.utils.response import Response
from server.app.utils.store_authorization import get_authorized_store
from server.app.extensions import db
from server.app.utils.validators import validate_required_string,validate_non_negative_number,validate_positive_integer

class ProductService:
    def __init__(self):
        pass
    def _data(self,p):
        return {"id":p.id,"store_id":p.store_id,"name":p.name,"price":str(p.price),"stock_quantity":p.stock_quantity,"low_stock_threshold":p.low_stock_threshold,"created_at":p.created_at.isoformat(),"updated_at":p.updated_at.isoformat()}
    def _get_data(self):
        data=request.get_json(silent=False)
        if not isinstance(data,dict): return None,Response.error_response("VALIDATION_ERROR","Invalid input data",{"payload":"Payload must be a JSON object"}),400
        return data,None,None
    def create_product(self):
        try:
            data,error,status=self._get_data()
            if error:return error,status
            store_id,name,price=data.get("store_id"),data.get("name"),data.get("price")
            stock,threshold=data.get("stock_quantity",0),data.get("low_stock_threshold",0)
            fields={}
            if not isinstance(store_id,int):fields["store_id"]="Store ID must be an integer"
            elif not get_authorized_store(store_id):fields["store_id"]="You do not have access to this store"
            e=validate_required_string(name,"Product name")
            if e:fields["name"]=e
            e=validate_non_negative_number(price,"Price")
            if e:fields["price"]=e
            e=validate_positive_integer(stock,"Stock quantity",True)
            if e:fields["stock_quantity"]=e
            e=validate_positive_integer(threshold,"Low stock threshold",True)
            if e:fields["low_stock_threshold"]=e
            if fields:return Response.error_response("VALIDATION_ERROR","Invalid input data",fields),400
            product=Product(store_id=store_id,name=name.strip(),price=Decimal(str(price)),stock_quantity=stock,low_stock_threshold=threshold)
            db.session.add(product);db.session.commit()
            return Response.success_response({"product":self._data(product)},"PRODUCT_CREATED"),201
        except IntegrityError:
            db.session.rollback();return Response.error_response("CONFLICT_ERROR","Product could not be created",{}),409
    def get_product(self):
        product_id=request.args.get("id",type=int);store_id=request.args.get("store_id",type=int)
        if not product_id or not store_id:return Response.error_response("VALIDATION_ERROR","Product ID and store ID are required",{}),400
        if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
        product=Product.query.filter_by(id=product_id,store_id=store_id).first()
        if not product:return Response.error_response("PRODUCT_NOT_FOUND","Product not found",{}),404
        return Response.success_response({"product":self._data(product)},"PRODUCT_FOUND"),200
    def list_products(self):
        store_id=request.args.get("store_id",type=int)
        if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
        products=Product.query.filter_by(store_id=store_id).order_by(Product.name.asc()).all()
        return Response.success_response({"products":[self._data(p) for p in products]},"PRODUCTS_RETRIEVED"),200
    def update_product(self):
        try:
            data,error,status=self._get_data()
            if error:return error,status
            store_id,product_id=data.get("store_id"),data.get("id")
            if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
            product=Product.query.filter_by(id=product_id,store_id=store_id).first()
            if not product:return Response.error_response("PRODUCT_NOT_FOUND","Product not found",{}),404
            fields={}
            if "name" in data:
                e=validate_required_string(data["name"],"Product name")
                if e:fields["name"]=e
                else:product.name=data["name"].strip()
            if "price" in data:
                e=validate_non_negative_number(data["price"],"Price")
                if e:fields["price"]=e
                else:product.price=Decimal(str(data["price"]))
            if "stock_quantity" in data:
                e=validate_positive_integer(data["stock_quantity"],"Stock quantity",True)
                if e:fields["stock_quantity"]=e
                else:product.stock_quantity=data["stock_quantity"]
            if "low_stock_threshold" in data:
                e=validate_positive_integer(data["low_stock_threshold"],"Low stock threshold",True)
                if e:fields["low_stock_threshold"]=e
                else:product.low_stock_threshold=data["low_stock_threshold"]
            if fields:return Response.error_response("VALIDATION_ERROR","Invalid input data",fields),400
            db.session.commit();return Response.success_response({"product":self._data(product)},"PRODUCT_UPDATED"),200
        except IntegrityError:
            db.session.rollback();return Response.error_response("CONFLICT_ERROR","Product could not be updated",{}),409
    def delete_product(self):
        data,error,status=self._get_data()
        if error:return error,status
        store_id,product_id=data.get("store_id"),data.get("id")
        if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
        product=Product.query.filter_by(id=product_id,store_id=store_id).first()
        if not product:return Response.error_response("PRODUCT_NOT_FOUND","Product not found",{}),404
        try:
            db.session.delete(product);db.session.commit();return Response.success_response(message="PRODUCT_DELETED"),200
        except IntegrityError:
            db.session.rollback();return Response.error_response("CONFLICT_ERROR","Product cannot be deleted because it has related records",{}),409
    def adjust_stock(self):
        data,error,status=self._get_data()
        if error:return error,status
        store_id,product_id=data.get("store_id"),data.get("id");change=data.get("quantity_change")
        if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
        if not isinstance(change,int) or isinstance(change,bool):return Response.error_response("VALIDATION_ERROR","Invalid input data",{"quantity_change":"Quantity change must be an integer"}),400
        product=Product.query.filter_by(id=product_id,store_id=store_id).first()
        if not product:return Response.error_response("PRODUCT_NOT_FOUND","Product not found",{}),404
        new_quantity=product.stock_quantity+change
        if new_quantity<0:return Response.error_response("INSUFFICIENT_STOCK","Stock quantity cannot become negative",{}),400
        previous=product.stock_quantity;product.stock_quantity=new_quantity
        db.session.add(InventoryMovement(store_id=store_id,product_id=product.id,user_id=session.get("user_id"),movement_type="ADJUSTMENT",quantity_change=change,previous_quantity=previous,new_quantity=new_quantity,reason=data.get("reason","Manual stock adjustment")))
        db.session.commit();return Response.success_response({"product":self._data(product)},"STOCK_ADJUSTED"),200
