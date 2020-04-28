"""scraper db table json columns

Revision ID: ed9573cc4869
Revises: d19b8343340d
Create Date: 2020-04-28 15:29:37.710199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ed9573cc4869"
down_revision = "d19b8343340d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("scraper", sa.Column("data", sa.JSON, nullable=False))
    op.execute(
        """
        UPDATE scraper
        SET data = JSON_OBJECT(
            "type", "mysql",
            "db_url_var", db_url_var,
            "site_table_name", site_table_name,
            "article_table_name", article_table_name,
            "snapshot_table_name", snapshot_table_name
        )
        """
    )
    op.drop_column("scraper", "db_url_var")
    op.drop_column("scraper", "site_table_name")
    op.drop_column("scraper", "article_table_name")
    op.drop_column("scraper", "snapshot_table_name")


def downgrade():
    op.add_column(
        "scraper", sa.Column("snapshot_table_name", sa.String(255), nullable=False)
    )
    op.add_column(
        "scraper", sa.Column("article_table_name", sa.String(255), nullable=False)
    )
    op.add_column(
        "scraper", sa.Column("site_table_name", sa.String(255), nullable=False)
    )
    op.add_column("scraper", sa.Column("db_url_var", sa.String(255), nullable=False))
    op.execute(
        """
        UPDATE scraper
        SET db_url_var = JSON_UNQUOTE(JSON_EXTRACT(data, "$.db_url_var")),
        site_table_name = JSON_UNQUOTE(JSON_EXTRACT(data, "$.site_table_name")),
        article_table_name = JSON_UNQUOTE(JSON_EXTRACT(data, "$.article_table_name")),
        snapshot_table_name = JSON_UNQUOTE(JSON_EXTRACT(data, "$.snapshot_table_name"))
        """
    )
    op.drop_column("scraper", "data")
