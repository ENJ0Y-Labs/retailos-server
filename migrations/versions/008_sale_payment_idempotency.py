"""add idempotency key to additional sale payments"""

from alembic import op
import sqlalchemy as sa


revision = "008_sale_payment_idempotency"
down_revision = "007_sale_payment_history"
branch_labels = None
depends_on = None


def upgrade():
    # Batch mode supports SQLite test/development databases as well as PostgreSQL.
    with op.batch_alter_table("sale_payments") as batch_op:
        batch_op.add_column(
            sa.Column("client_transaction_id", sa.String(length=128), nullable=True),
        )
        batch_op.create_unique_constraint(
            "uq_sale_payments_client_transaction_id",
            ["client_transaction_id"],
        )


def downgrade():
    with op.batch_alter_table("sale_payments") as batch_op:
        batch_op.drop_constraint(
            "uq_sale_payments_client_transaction_id",
            type_="unique",
        )
        batch_op.drop_column("client_transaction_id")
