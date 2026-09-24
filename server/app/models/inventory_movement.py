from datetime import datetime
from server.app.extensions import db
from server.app.models.product import Product
from server.app.models.store import Store
from server.app.models.user import User
from server.app.utils.time import now_utc
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,ForeignKey,DateTime,Integer

class InventoryMovement(db.Model):
    __tablename__="inventory_movements"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    store_id:Mapped[int]=mapped_column(ForeignKey(Store.id,ondelete="CASCADE"))
    product_id:Mapped[int]=mapped_column(ForeignKey(Product.id,ondelete="CASCADE"))
    user_id:Mapped[int|None]=mapped_column(ForeignKey(User.id,ondelete="SET NULL"))
    movement_type:Mapped[str]=mapped_column(String)
    quantity_change:Mapped[int]=mapped_column(Integer)
    previous_quantity:Mapped[int]=mapped_column(Integer)
    new_quantity:Mapped[int]=mapped_column(Integer)
    reason:Mapped[str|None]=mapped_column(String)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=now_utc)
