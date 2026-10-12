"""merge migration heads

Revision ID: abcdf272a615
Revises: 004_sale_timestamp_utc
Create Date: 2026-10-12 19:56:45.036240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abcdf272a615'
down_revision = '004_sale_timestamp_utc'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
