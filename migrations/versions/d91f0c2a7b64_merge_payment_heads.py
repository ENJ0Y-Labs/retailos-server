"""merge payment idempotency and existing migration heads

This merge revision joins the additional-payment idempotency migration with
the migration already present on the target repository branch. It deliberately
does not change the schema.
"""

revision = "d91f0c2a7b64"
down_revision = ("008_sale_payment_idempotency", "c3f1a2b9d6e7")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
