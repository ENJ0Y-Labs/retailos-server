# server\app\models\sale.py
from server.app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, DateTime
from server.app.models.store import Store
from datetime import datetime
from server.app.utils.time import now_utc

class Sale(db.Model):
    __tablename__ = "sales"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(ForeignKey(Store.id, ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)