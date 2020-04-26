"""drop int id from mappings

Revision ID: bb6f94e272dd
Revises: 40f27d0c0f69
Create Date: 2020-04-26 23:40:07.560650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bb6f94e272dd"
down_revision = "40f27d0c0f69"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index(
        "uq_publication_mapping_publication_id_version",
        table_name="publication_mapping",
    )
    op.drop_index(
        "ik_publication_mapping_publication_id", table_name="publication_mapping"
    )
    op.drop_column("publication_mapping", "publication_int_id")
    op.drop_column("producer_mapping", "producer_int_id")


def downgrade():
    op.add_column("producer_mapping", sa.Column("producer_int_id", sa.Integer))
    op.add_column("publication_mapping", sa.Column("publication_int_id", sa.Integer))
    op.create_index(
        "ik_publication_mapping_publication_id",
        "publication_mapping",
        ["publication_id"],
    )
    op.create_index(
        "uq_publication_mapping_publication_id_version",
        "publication_mapping",
        ["publication_id", "version"],
        unique=True,
    )
