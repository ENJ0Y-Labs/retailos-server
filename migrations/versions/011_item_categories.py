"""add store-scoped item categories

Revision ID: 011_item_categories
Revises: 010_stock_receivings
"""
from alembic import op
import sqlalchemy as sa


revision = "011_item_categories"
down_revision = "010_stock_receivings"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column("item_type", sa.String(length=20), nullable=False),
        sa.CheckConstraint(
            "item_type IN ('Physical', 'Service')",
            name="check_category_item_type",
        ),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "store_id", "item_type", "name",
            name="uq_category_store_type_name",
        ),
    )
    op.create_index(
        "uq_category_store_type_name_ci",
        "categories",
        ["store_id", "item_type", sa.text("lower(name)")],
        unique=True,
    )
    op.add_column(
        "products",
        sa.Column("category_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_products_category_id_categories",
        "products",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint(
        "fk_products_category_id_categories",
        "products",
        type_="foreignkey",
    )
    op.drop_column("products", "category_id")
    op.drop_index("uq_category_store_type_name_ci", table_name="categories")
    op.drop_table("categories")
