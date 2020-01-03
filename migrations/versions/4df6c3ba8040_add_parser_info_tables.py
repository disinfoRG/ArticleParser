"""add parser info tables

Revision ID: 4df6c3ba8040
Revises: 0e31ae2223df
Create Date: 2020-01-03 14:49:28.343403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4df6c3ba8040"
down_revision = "0e31ae2223df"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "parser_info",
        sa.Column("parser_name", sa.String(256), primary_key=True),
        sa.Column("info", sa.JSON),
    )
    op.create_table(
        "publication_mapping",
        sa.Column("article_id", sa.Integer, nullable=False),
        sa.Column("snapshot_at", sa.Integer, nullable=False),
        sa.Column("publication_id", sa.Integer, nullable=False),
        sa.Column("info", sa.JSON),
        sa.PrimaryKeyConstraint(
            "article_id", "snapshot_at", name="pk_publication_mapping"
        ),
    )
    op.create_table(
        "producer_mapping",
        sa.Column("site_id", sa.Integer, primary_key=True),
        sa.Column("producer_id", sa.Integer, nullable=False),
        sa.Column("info", sa.JSON),
    )


def downgrade():
    op.drop_table("producer_mapping")
    op.drop_table("publication_mapping")
    op.drop_table("parser_info")
