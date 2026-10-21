"""add idempotency key to additional sale payments"""

from alembic import op
import sqlalchemy as sa


revision = "008_sale_payment_idempotency"
down_revision = "007_sale_payment_history"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sale_payments",
        sa.Column("client_transaction_id", sa.String(length=128), nullable=True),
    )
    op.create_unique_constraint(
        "uq_sale_payments_client_transaction_id",
        "sale_payments",
        ["client_transaction_id"],
    )


def downgrade():
    op.drop_constraint(
        "uq_sale_payments_client_transaction_id",
        "sale_payments",
        type_="unique",
    )
    op.drop_column("sale_payments", "client_transaction_id")
