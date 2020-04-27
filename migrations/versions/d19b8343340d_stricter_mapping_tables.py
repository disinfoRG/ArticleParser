"""stricter mapping tables

Revision ID: d19b8343340d
Revises: bb6f94e272dd
CZreate Date: 2020-04-27 17:02:13.187904

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY


# revision identifiers, used by Alembic.
revision = "d19b8343340d"
down_revision = "bb6f94e272dd"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "producer_mapping", "site_id", autoincrement=False, existing_type=sa.Integer
    )
    op.alter_column(
        "publication_mapping", "info", nullable=False, existing_type=sa.JSON
    )
    op.alter_column(
        "publication_mapping", "version", nullable=False, existing_type=sa.Integer
    )
    op.execute("DELETE FROM publication_mapping WHERE publication_id IS NULL")
    op.alter_column(
        "publication_mapping",
        "publication_id",
        nullable=False,
        existing_type=BINARY(16),
    )


def downgrade():
    op.alter_column(
        "publication_mapping", "publication_id", nullable=True, existing_type=BINARY(16)
    )
    op.alter_column(
        "publication_mapping", "version", nullable=True, existing_type=sa.Integer
    )
    op.alter_column("publication_mapping", "info", nullable=True, existing_type=sa.JSON)
    op.alter_column(
        "producer_mapping", "site_id", autoincrement=True, existing_type=sa.Integer
    )
