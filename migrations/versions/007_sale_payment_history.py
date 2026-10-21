"""add payment history for existing sales"""

from alembic import op
import sqlalchemy as sa

revision = "007_sale_payment_history"
down_revision = "006_customer_sale_balances"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sale_payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sale_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="check_sale_payment_amount_positive"),
        sa.CheckConstraint(
            "payment_method IN ('Cash', 'Transfer', 'POS')",
            name="check_sale_payment_method_valid",
        ),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sale_payments_sale_id", "sale_payments", ["sale_id"])

    # Preserve the recorded paid amount for existing sales as an initial history entry.
    op.execute(
        "INSERT INTO sale_payments (sale_id, amount, payment_method, created_at) "
        "SELECT id, amount_paid, payment_method, created_at FROM sales WHERE amount_paid > 0"
    )


def downgrade():
    op.drop_index("ix_sale_payments_sale_id", table_name="sale_payments")
    op.drop_table("sale_payments")
