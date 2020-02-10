"""add comments column

Revision ID: 2b3a6e3b7697
Revises: 2ae6e05fe201
Create Date: 2020-02-10 17:00:39.421668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2b3a6e3b7697"
down_revision = "2ae6e05fe201"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("publication", sa.Column("comments", sa.JSON))


def downgrade():
    op.drop_column("publication", "comments")
