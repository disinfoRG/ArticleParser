"""add scraper id to mapping primary key

Revision ID: 6d1fceb43afe
Revises: ad3d4e410339
Create Date: 2020-05-11 11:42:25.435017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6d1fceb43afe"
down_revision = "ad3d4e410339"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE producer_mapping DROP PRIMARY KEY, ADD PRIMARY KEY (scraper_id, site_id)"
    )
    op.execute(
        "ALTER TABLE publication_mapping DROP PRIMARY KEY, ADD PRIMARY KEY (scraper_id, article_id, snapshot_at)"
    )


def downgrade():
    op.execute(
        "ALTER TABLE producer_mapping DROP PRIMARY KEY, ADD PRIMARY KEY (site_id)"
    )
    op.execute(
        "ALTER TABLE publication_mapping DROP PRIMARY KEY, ADD PRIMARY KEY (article_id, snapshot_at)"
    )
