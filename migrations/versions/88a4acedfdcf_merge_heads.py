"""merge heads

Revision ID: 88a4acedfdcf
Revises: 004_product_type, 009_sale_base_quantity_deducted, abcdf272a615
Create Date: 2026-10-12 20:41:35.568492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88a4acedfdcf'
down_revision = ('004_product_type', '009_sale_base_quantity_deducted', 'abcdf272a615')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
