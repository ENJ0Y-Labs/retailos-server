from datetime import datetime
from decimal import Decimal
from server.app.extensions import db
from server.app.models.store import Store
from server.app.models.customer import Customer
from server.app.utils.time import now_utc
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import ForeignKey,DateTime,Integer,Numeric,String

class Sale(db.Model):
    __tablename__="sales"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    store_id:Mapped[int]=mapped_column(ForeignKey(Store.id,ondelete="CASCADE"))
    customer_id:Mapped[int|None]=mapped_column(ForeignKey(Customer.id,ondelete="SET NULL"))
    client_transaction_id:Mapped[str|None]=mapped_column(String,unique=True)
    total_amount:Mapped[Decimal]=mapped_column(Numeric(12,2),default=0)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=now_utc)
