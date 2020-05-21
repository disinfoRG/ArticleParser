"""add parser log table

Revision ID: 4588812811ae
Revises: af45865d1033
Create Date: 2020-05-21 17:29:05.459691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4588812811ae"
down_revision = "af45865d1033"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "parser_log",
        sa.Column("parser_name", sa.String(256), nullable=False),
        sa.Column("created_at", sa.Integer, nullable=False),
        sa.Column("scraper_id", sa.Integer, nullable=False),
        sa.Column("article_id", sa.Integer, nullable=False),
        sa.Column("snapshot_at", sa.Integer, nullable=False),
        sa.Column("data", sa.JSON, nullable=False),
        sa.PrimaryKeyConstraint("scraper_id", "article_id", "snapshot_at"),
    )


def downgrade():
    op.drop_table("parser_log")
