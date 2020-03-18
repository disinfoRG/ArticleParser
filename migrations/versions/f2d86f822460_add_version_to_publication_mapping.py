"""add version to publication mapping

Revision ID: f2d86f822460
Revises: 27a3259b417b
Create Date: 2020-03-18 13:56:54.998281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2d86f822460"
down_revision = "27a3259b417b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("publication_mapping", sa.Column("version", sa.Integer))
    op.execute("UPDATE publication_mapping SET version = snapshot_at")
    op.create_index(
        "uq_publication_mapping_publication_id_version",
        "publication_mapping",
        ["publication_id", "version"],
        unique=True,
    )


def downgrade():
    op.drop_column("publication_mapping", "version")
    op.drop_index(
        "uq_publication_mapping_publication_id_version",
        table_name="publication_mapping",
    )
