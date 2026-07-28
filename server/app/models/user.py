# server\app\models\user.py
from datetime import datetime, timezone
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime

now_utc = datetime.now(timezone.utc)
class User(db.Model):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name:Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    password_hash[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)