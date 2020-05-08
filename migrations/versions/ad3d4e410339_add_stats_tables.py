"""add stats tables

Revision ID: ad3d4e410339
Revises: e1f1c0c082fd
Create Date: 2020-05-08 17:25:35.508997

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY


# revision identifiers, used by Alembic.
revision = "ad3d4e410339"
down_revision = "e1f1c0c082fd"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "parser_stats",
        sa.Column("parser_name", sa.String(255), nullable=False),
        sa.Column("processed_date", sa.Date, nullable=False),
        sa.Column("producer_id", BINARY(16), nullable=False),
        sa.Column("processed_count", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("parser_name", "processed_date", "producer_id"),
    )
    op.create_table(
        "publication_stats",
        sa.Column("published_date", sa.Date, nullable=False),
        sa.Column("producer_id", BINARY(16), nullable=False),
        sa.Column("published_count", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("published_date", "producer_id"),
    )


def downgrade():
    op.drop_table("publication_stats")
    op.drop_table("parser_stats")
