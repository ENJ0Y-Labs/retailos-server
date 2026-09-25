# migrations/versions/002_v1_alert_scope.py
"""limit V1 alerts to low stock alerts"""
from alembic import op


revision = "002_v1_alert_scope"
down_revision = "001_initial_retailos"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "check_alert_type_valid",
        "alerts",
        type_="check"
    )

    op.create_check_constraint(
        "check_alert_type_valid",
        "alerts",
        "type IN ('low_stock')"
    )


def downgrade():
    op.drop_constraint(
        "check_alert_type_valid",
        "alerts",
        type_="check"
    )

    op.create_check_constraint(
        "check_alert_type_valid",
        "alerts",
        "type IN ('low_stock', 'sales_drop', 'no_sales')"
    )
