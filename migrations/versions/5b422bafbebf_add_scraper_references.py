"""add scraper references

Revision ID: 5b422bafbebf
Revises: 69a322b64d30
Create Date: 2020-03-27 10:11:01.267112

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5b422bafbebf"
down_revision = "69a322b64d30"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("producer_mapping", sa.Column("scraper_id", sa.Integer))
    op.add_column("publication_mapping", sa.Column("scraper_id", sa.Integer))
    op.execute("UPDATE producer_mapping SET scraper_id = 1")
    op.execute("UPDATE publication_mapping SET scraper_id = 1")


def downgrade():
    op.drop_column("publication_mapping", "scraper_id")
    op.drop_column("producer_mapping", "scraper_id")
