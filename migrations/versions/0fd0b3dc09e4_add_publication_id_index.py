"""add publication id index

Revision ID: 0fd0b3dc09e4
Revises: 5ed8782dcdd3
Create Date: 2020-03-12 13:20:13.045994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0fd0b3dc09e4"
down_revision = "5ed8782dcdd3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ik_publication_mapping_publication_id",
        "publication_mapping",
        ["publication_id"],
    )


def downgrade():
    op.drop_index(
        "ik_publication_mapping_publication_id", table_name="publication_mapping"
    )
