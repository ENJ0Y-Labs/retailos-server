"""initial RetailOS schema"""
from alembic import op
import sqlalchemy as sa

revision="001_initial_retailos"
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("users",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("name",sa.String(),nullable=False),sa.Column("email",sa.String(),nullable=False),sa.Column("password_hash",sa.String(),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False),sa.UniqueConstraint("email"))
    op.create_table("stores",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("name",sa.String(),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False))
    op.create_table("products",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("store_id",sa.Integer(),sa.ForeignKey("stores.id",ondelete="CASCADE"),nullable=False),sa.Column("name",sa.String(),nullable=False),sa.Column("price",sa.Numeric(10,2),nullable=False),sa.Column("stock_quantity",sa.Integer(),nullable=False),sa.Column("low_stock_threshold",sa.Integer()),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_table("customers",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("store_id",sa.Integer(),sa.ForeignKey("stores.id",ondelete="CASCADE"),nullable=False),sa.Column("name",sa.String(),nullable=False),sa.Column("contact",sa.String()),sa.Column("created_at",sa.DateTime(),nullable=False))
    op.create_table("sales",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("store_id",sa.Integer(),sa.ForeignKey("stores.id",ondelete="CASCADE"),nullable=False),sa.Column("customer_id",sa.Integer(),sa.ForeignKey("customers.id",ondelete="SET NULL")),sa.Column("client_transaction_id",sa.String(),unique=True),sa.Column("total_amount",sa.Numeric(12,2),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False))
    op.create_table("sale_items",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("sale_id",sa.Integer(),sa.ForeignKey("sales.id",ondelete="CASCADE"),nullable=False),sa.Column("product_id",sa.Integer(),sa.ForeignKey("products.id",ondelete="RESTRICT"),nullable=False),sa.Column("quantity",sa.Integer(),nullable=False),sa.Column("price_at_sale",sa.Numeric(10,2),nullable=False),sa.Column("total",sa.Numeric(12,2),nullable=False))
    op.create_table("inventory_movements",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("store_id",sa.Integer(),sa.ForeignKey("stores.id",ondelete="CASCADE"),nullable=False),sa.Column("product_id",sa.Integer(),sa.ForeignKey("products.id",ondelete="CASCADE"),nullable=False),sa.Column("user_id",sa.Integer(),sa.ForeignKey("users.id",ondelete="SET NULL")),sa.Column("movement_type",sa.String(),nullable=False),sa.Column("quantity_change",sa.Integer(),nullable=False),sa.Column("previous_quantity",sa.Integer(),nullable=False),sa.Column("new_quantity",sa.Integer(),nullable=False),sa.Column("reason",sa.String()),sa.Column("created_at",sa.DateTime(),nullable=False))
    op.create_table("alerts",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("store_id",sa.Integer(),sa.ForeignKey("stores.id",ondelete="CASCADE"),nullable=False),sa.Column("product_id",sa.Integer(),sa.ForeignKey("products.id",ondelete="SET NULL")),sa.Column("type",sa.String(),nullable=False),sa.Column("message",sa.String(),nullable=False),sa.Column("is_resolved",sa.Boolean(),nullable=False),sa.Column("created_at",sa.DateTime(),nullable=False))

def downgrade():
    for table in ["alerts","inventory_movements","sale_items","sales","customers","products","stores","users"]:
        op.drop_table(table)
