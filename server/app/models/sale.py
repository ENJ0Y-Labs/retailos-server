# server\app\models\sale.py
from server.app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, DateTime
from server.app.models.store import Store
from datetime import datetime, timezone

now_utc = datetime.now(timezone.utc)

class Sale(db.Model):
    __tablename__ = "sales"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    store_id: Mapped[str] = mapped_column(ForeignKey(Store.id, ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)