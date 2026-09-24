from datetime import datetime,timezone
from sqlalchemy import func
from server.app.models.sale import Sale
from server.app.models.product import Product
from server.app.models.alert import Alert
from server.app.utils.response import Response
from server.app.utils.store_authorization import get_authorized_store

class InsightService:
    def dashboard(self,store_id):
        if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
        today=datetime.now(timezone.utc).date()
        sales=Sale.query.filter(Sale.store_id==store_id,func.date(Sale.created_at)==today)
        total=sales.with_entities(func.coalesce(func.sum(Sale.total_amount),0)).scalar()
        return Response.success_response({
            "products_count":Product.query.filter_by(store_id=store_id).count(),
            "low_stock_count":Product.query.filter(Product.store_id==store_id,Product.stock_quantity<=Product.low_stock_threshold).count(),
            "open_alerts_count":Alert.query.filter_by(store_id=store_id,is_resolved=False).count(),
            "today_sales_count":sales.count(),
            "today_sales_total":str(total)
        },"DASHBOARD_RETRIEVED"),200

    def daily_summary(self,store_id):
        if not get_authorized_store(store_id):return Response.error_response("STORE_ACCESS_DENIED","You do not have access to this store",{}),403
        today=datetime.now(timezone.utc).date()
        sales=Sale.query.filter(Sale.store_id==store_id,func.date(Sale.created_at)==today).order_by(Sale.created_at.asc()).all()
        total=sum((s.total_amount for s in sales),0)
        return Response.success_response({"date":today.isoformat(),"sales_count":len(sales),"total_sales":str(total),"sales":[{"id":s.id,"total_amount":str(s.total_amount),"created_at":s.created_at.isoformat()} for s in sales]},"DAILY_SUMMARY_RETRIEVED"),200
