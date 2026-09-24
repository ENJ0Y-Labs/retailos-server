from datetime import datetime
from server.app.extensions import db
from server.app.models.store import Store
from server.app.utils.time import now_utc
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,ForeignKey,DateTime,Integer

class Customer(db.Model):
    __tablename__="customers"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    store_id:Mapped[int]=mapped_column(ForeignKey(Store.id,ondelete="CASCADE"))
    name:Mapped[str]=mapped_column(String)
    contact:Mapped[str|None]=mapped_column(String)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=now_utc)
