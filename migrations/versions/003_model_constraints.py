# migrations/versions/003_model_constraints.py
"""align database constraints with application models"""

from alembic import op


revision = "003_model_constraints"
down_revision = "002_v1_alert_scope"
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        "check_price_non_negative",
        "products",
        "price >= 0"
    )
    op.create_check_constraint(
        "check_stock_quantity_non_negative",
        "products",
        "stock_quantity >= 0"
    )
    op.create_check_constraint(
        "check_sale_item_quantity_positive",
        "sale_items",
        "quantity > 0"
    )
    op.create_check_constraint(
        "check_sale_item_price_non_negative",
        "sale_items",
        "price_at_sale >= 0"
    )
    op.create_check_constraint(
        "check_sale_item_total_non_negative",
        "sale_items",
        "total >= 0"
    )
    op.create_check_constraint(
        "check_alert_is_resolved_valid",
        "alerts",
        "is_resolved IN (TRUE, FALSE)"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_users_email_lower "
        "ON users (LOWER(email))"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_users_email_lower")
    op.drop_constraint(
        "check_alert_is_resolved_valid",
        "alerts",
        type_="check"
    )
    op.drop_constraint(
        "check_sale_item_total_non_negative",
        "sale_items",
        type_="check"
    )
    op.drop_constraint(
        "check_sale_item_price_non_negative",
        "sale_items",
        type_="check"
    )
    op.drop_constraint(
        "check_sale_item_quantity_positive",
        "sale_items",
        type_="check"
    )
    op.drop_constraint(
        "check_product_stock_non_negative",
        "products",
        type_="check"
    )
    op.drop_constraint(
        "check_product_price_non_negative",
        "products",
        type_="check"
    )
