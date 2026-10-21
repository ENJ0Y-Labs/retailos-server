from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from server.app.extensions import db
from server.app.models.sale import Sale
from server.app.utils.time import now_utc


class SalePayment(db.Model):
    __tablename__ = "sale_payments"
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_sale_payment_amount_positive"),
        CheckConstraint(
            "payment_method IN ('Cash', 'Transfer', 'POS')",
            name="check_sale_payment_method_valid",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey(Sale.id, ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
