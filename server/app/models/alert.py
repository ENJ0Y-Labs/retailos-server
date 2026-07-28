# server\app\models\alert.py
from server.app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Enum, Boolean, DateTime, CheckConstraint
from server.app.models.store import Store
from server.app.models.product import Product
import enum
from datetime import datetime, timezone

now_utc = datetime.now(timezone.utc)

class AlertType(enum.Enum):
    LOW_STOCK = "low_stock"
    SALES_DROP = "sales_drop"
    NO_SALES = "no_sales"

class Alert(db.Model):
    __tablename__ = "alerts"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    store_id: Mapped[str] = mapped_column(ForeignKey(Store.id, ondelete="CASCADE"))
    product_id: Mapped[str] = mapped_column(ForeignKey(Product.id, ondelete="SET NULL"))
    type: Mapped[AlertType] = mapped_column(Enum(AlertType))
    message: Mapped[str] = mapped_column(String)
    is_resolved: Mapped[bool]  = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    
    __table_args__ = {
        CheckConstraint("type IN ('low_stock', 'sales_drop', 'no_sales')", name="check_alert_type_valid"),
        CheckConstraint("is_resolved IN (0, 1)", name="check_alert_is_resolved_valid")
    }