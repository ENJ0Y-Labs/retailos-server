# server\app\models\sale_item.py
from server.app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Integer, Numeric, CheckConstraint
from server.app.models.sale import Sale
from server.app.models.product import Product
from decimal import Decimal


class SaleItem(db.Model):
    __tablename__ = "sale_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sale_id: Mapped[str] = mapped_column(ForeignKey(Sale.id, ondelete="CASCADE"))
    product_id: Mapped[str] = mapped_column(ForeignKey(Product.id, ondelete="RESTRICT"))
    quantity: Mapped[int] = mapped_column(Integer)
    price_at_sale: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_non_negative"),
        CheckConstraint("price_at_sale >= 0", name="check_price_at_sale_non_negative"),
        CheckConstraint("total >= 0", name="check_total_non_negative")
    )