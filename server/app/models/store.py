# server\app\models\store.py
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, DateTime
from user import User
from datetime import datetime, timezone

now_utc = datetime.now(timezone.utc)

class Store(db.Madel):
    __tablename__ = "stores"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)