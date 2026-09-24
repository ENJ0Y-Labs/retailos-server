from flask import request
from server.app.extensions import db
from server.app.models.alert import Alert,AlertType
from server.app.models.product import Product
from server.app.utils.response import Response
from server.app.utils.store_authorization import get_authorized_store

class AlertService:
    def list_alerts(self):
        store_id=request.args.get("store_id",type=int)
        if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
        alerts=Alert.query.filter_by(store_id=store_id,is_resolved=False).order_by(Alert.created_at.desc()).all()
        return Response.success_response({"alerts":[{"id":a.id,"type":a.type.value,"message":a.message,"product_id":a.product_id,"created_at":a.created_at.isoformat()} for a in alerts]},"ALERTS_RETRIEVED"),200
    def generate_low_stock_alerts(self):
        store_id=request.args.get("store_id",type=int)
        if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
        products=Product.query.filter(Product.store_id==store_id,Product.stock_quantity<=Product.low_stock_threshold).all();created=[]
        for p in products:
            if not Alert.query.filter_by(store_id=store_id,product_id=p.id,type=AlertType.LOW_STOCK,is_resolved=False).first():
                db.session.add(Alert(store_id=store_id,product_id=p.id,type=AlertType.LOW_STOCK,message=f"{p.name} is low on stock"));created.append(p.id)
        db.session.commit();return Response.success_response({"created_alerts":created},"LOW_STOCK_ALERTS_GENERATED"),200
    def resolve_alert(self):
        store_id=request.args.get("store_id",type=int);alert_id=request.args.get("id",type=int)
        if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
        alert=Alert.query.filter_by(id=alert_id,store_id=store_id).first()
        if not alert:return Response.error_response("ALERT_NOT_FOUND","Alert not found",{}),404
        alert.is_resolved=True;db.session.commit();return Response.success_response(message="ALERT_RESOLVED"),200
