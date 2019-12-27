"""add metadata and others

Revision ID: 0e31ae2223df
Revises: 028ba49bb4bc
Create Date: 2019-12-27 10:27:45.555021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0e31ae2223df"
down_revision = "028ba49bb4bc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("publication", sa.Column("metadata", sa.JSON))
    op.alter_column(
        "publication",
        "posted_at",
        new_column_name="published_at",
        existing_type=sa.Integer,
    )


def downgrade():
    op.alter_column(
        "publication",
        "published_at",
        new_column_name="posted_at",
        existing_type=sa.Integer,
    )
    op.drop_column("publication", "metadata")
