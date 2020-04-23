"""add publication indexes

Revision ID: f13a69bef275
Revises: 05ce1d870fac
Create Date: 2020-04-23 11:37:52.681536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f13a69bef275"
down_revision = "05ce1d870fac"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ik_publication_published_at", "publication")
    op.drop_index("ik_publication_producer_id", "publication")
    op.drop_index("uq_publication_uuid", "publication")
    op.create_index(
        "ik_producer_published_at_version",
        "publication",
        ["producer_id", "published_at", "version"],
    )
    op.create_index("ik_producer_version", "publication", ["producer_id", "version"])


def downgrade():
    op.drop_index("ik_producer_version", "publication")
    op.drop_index("ik_producer_published_at_version", "publication")
    op.create_index(
        "uq_publication_uuid", "publication", ["publication_id"], unique=True
    )
    op.create_index(
        "ik_publication_producer_id", "publication", ["producer_int_id", "published_at"]
    )
    op.create_index("ik_publication_published_at", "publication", ["published_at"])
