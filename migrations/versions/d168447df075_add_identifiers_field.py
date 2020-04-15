"""add identifiers field

Revision ID: d168447df075
Revises: f1a283ac7a1f
Create Date: 2020-03-12 11:03:33.237230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d168447df075"
down_revision = "f1a283ac7a1f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("producer", sa.Column("identifiers", sa.JSON, nullable=False))


def downgrade():
    op.drop_column("producer", "identifiers")
