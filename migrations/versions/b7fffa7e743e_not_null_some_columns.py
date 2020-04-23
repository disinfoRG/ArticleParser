"""not null some columns

Revision ID: b7fffa7e743e
Revises: 148e5204c50b
Create Date: 2020-04-24 15:26:13.358363

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY


# revision identifiers, used by Alembic.
revision = "b7fffa7e743e"
down_revision = "148e5204c50b"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "producer", "name", nullable=False, type_=sa.String(255), existing_type=sa.Text
    )
    op.alter_column("producer", "url", nullable=False, existing_type=sa.String(1024))
    op.alter_column(
        "producer_mapping", "producer_id", nullable=False, existing_type=sa.BINARY(16)
    )
    op.execute("UPDATE producer_mapping SET scraper_id = 1")
    op.alter_column(
        "producer_mapping", "scraper_id", nullable=False, existing_type=sa.Integer
    )
    op.alter_column("producer_mapping", "info", nullable=False, existing_type=sa.JSON)


def downgrade():
    op.alter_column("producer_mapping", "info", nullable=True, existing_type=sa.JSON)
    op.alter_column(
        "producer_mapping", "scraper_id", nullable=True, existing_type=sa.Integer
    )
    op.alter_column(
        "producer_mapping", "producer_id", nullable=True, existing_type=sa.BINARY(16)
    )
    op.alter_column("producer", "url", nullable=True, existing_type=sa.String(1024))
    op.alter_column(
        "producer", "name", nullable=True, type_=sa.Text, existing_type=sa.String(255)
    )
