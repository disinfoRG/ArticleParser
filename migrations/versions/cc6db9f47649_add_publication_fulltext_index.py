"""add publication fulltext index

Revision ID: cc6db9f47649
Revises: 2b3a6e3b7697
Create Date: 2020-02-17 15:38:14.792276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cc6db9f47649"
down_revision = "2b3a6e3b7697"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ik_publication_title_text",
        "publication",
        ["title", "publication_text"],
        mysql_prefix="FULLTEXT",
        mysql_with_parser="ngram",
    )


def downgrade():
    op.drop_index("ik_publication_title_text", table_name="publication")
