"""store sale timestamps as UTC-aware PostgreSQL timestamps"""

from alembic import op


revision = "004_sale_timestamp_utc"
down_revision = "003_model_constraints"
branch_labels = None
depends_on = None


def upgrade():
    # Existing application-created sale timestamps were UTC values stored in
    # a timezone-naive column, so interpret them as UTC before changing type.
    op.execute(
        "ALTER TABLE sales "
        "ALTER COLUMN created_at TYPE TIMESTAMPTZ "
        "USING created_at AT TIME ZONE 'UTC'"
    )

    # Correct legacy rows that are ahead of the database clock. New sales are
    # created by the server and validated against UTC before insertion.
    op.execute(
        "UPDATE sales "
        "SET created_at = CURRENT_TIMESTAMP "
        "WHERE created_at > CURRENT_TIMESTAMP"
    )


def downgrade():
    op.execute(
        "ALTER TABLE sales "
        "ALTER COLUMN created_at TYPE TIMESTAMP "
        "USING created_at AT TIME ZONE 'UTC'"
    )
