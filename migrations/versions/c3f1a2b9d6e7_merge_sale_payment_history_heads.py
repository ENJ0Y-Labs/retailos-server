"""merge sale payment history and existing migration heads

Revision ID: c3f1a2b9d6e7
Revises: 007_sale_payment_history, 88a4acedfdcf
Create Date: 2026-10-21
"""

revision = "c3f1a2b9d6e7"
down_revision = ("007_sale_payment_history", "88a4acedfdcf")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
