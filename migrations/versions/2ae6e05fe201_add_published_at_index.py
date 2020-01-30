"""add published at index

Revision ID: 2ae6e05fe201
Revises: 4df6c3ba8040
Create Date: 2020-01-30 12:04:11.885385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2ae6e05fe201"
down_revision = "4df6c3ba8040"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ik_publication_published_at", "publication", ["published_at"])


def downgrade():
    op.drop_index("ik_publication_published_at")
