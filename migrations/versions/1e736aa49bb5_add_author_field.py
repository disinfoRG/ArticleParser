"""add author field

Revision ID: 1e736aa49bb5
Revises: 0fd0b3dc09e4
Create Date: 2020-03-16 17:13:29.871587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1e736aa49bb5"
down_revision = "0fd0b3dc09e4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("publication", sa.Column("author", sa.String(255)))


def downgrade():
    op.drop_column("publication", "author")
