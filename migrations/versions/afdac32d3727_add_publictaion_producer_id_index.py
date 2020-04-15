"""add publictaion producer id index

Revision ID: afdac32d3727
Revises: f2d86f822460
Create Date: 2020-03-19 17:33:08.530519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "afdac32d3727"
down_revision = "f2d86f822460"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ik_publication_producer_id", "publication", ["producer_id", "published_at"]
    )


def downgrade():
    op.drop_index("ik_publication_producer_id", table_name="publication")
