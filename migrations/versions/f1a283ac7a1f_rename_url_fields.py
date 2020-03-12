"""rename url fields

Revision ID: f1a283ac7a1f
Revises: 2b3a6e3b7697
Create Date: 2020-03-12 10:58:59.834206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f1a283ac7a1f"
down_revision = "2b3a6e3b7697"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "producer",
        "canonical_url",
        new_column_name="url",
        existing_type=sa.String(1024),
    )


def downgrade():
    op.alter_column(
        "producer",
        "url",
        new_column_name="canonical_url",
        existing_type=sa.String(1024),
    )
