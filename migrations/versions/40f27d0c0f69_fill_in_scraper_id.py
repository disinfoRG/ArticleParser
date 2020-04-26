"""fill in scraper id

Revision ID: 40f27d0c0f69
Revises: b7fffa7e743e
Create Date: 2020-04-26 23:31:12.636857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "40f27d0c0f69"
down_revision = "b7fffa7e743e"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE publication_mapping SET scraper_id = 1")
    op.alter_column(
        "publication_mapping", "scraper_id", nullable=False, existing_type=sa.Integer
    )
    op.execute("UPDATE producer_mapping SET scraper_id = 1")


def downgrade():
    op.alter_column(
        "publication_mapping", "scraper_id", nullable=True, existing_type=sa.Integer
    )
