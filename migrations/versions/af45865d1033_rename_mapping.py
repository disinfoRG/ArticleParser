"""rename mapping

Revision ID: af45865d1033
Revises: 6d1fceb43afe
Create Date: 2020-05-21 17:05:44.701530

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY

# revision identifiers, used by Alembic.
revision = "af45865d1033"
down_revision = "6d1fceb43afe"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("publication_mapping", "publication_map")
    op.rename_table("producer_mapping", "producer_map")


def downgrade():
    op.rename_table("producer_map", "producer_mapping")
    op.rename_table("publication_map", "publication_mapping")
