"""add scraper table

Revision ID: 69a322b64d30
Revises: afdac32d3727
Create Date: 2020-03-27 09:52:22.509131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "69a322b64d30"
down_revision = "afdac32d3727"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "scraper",
        sa.Column("scraper_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("scraper_name", sa.String(255), nullable=False, unique=True),
        sa.Column("db_url_var", sa.String(255), nullable=False),
        sa.Column("site_table_name", sa.String(255), nullable=False),
        sa.Column("article_table_name", sa.String(255), nullable=False),
        sa.Column("snapshot_table_name", sa.String(255), nullable=False),
    )
    op.execute(
        "INSERT INTO scraper (scraper_id, scraper_name, db_url_var, site_table_name, article_table_name, snapshot_table_name) VALUES (1, 'ZeroScraper', 'SCRAPER_DB_URL', 'Site', 'Article', 'ArticleSnapshot')"
    )


def downgrade():
    op.drop_table("scraper")
