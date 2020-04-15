"""add version

Revision ID: 5ed8782dcdd3
Revises: d168447df075
Create Date: 2020-03-12 13:00:27.594946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5ed8782dcdd3"
down_revision = "d168447df075"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("publication", sa.Column("version", sa.Integer, nullable=False))
    op.execute("UPDATE publication SET version = last_updated_at")
    op.execute(
        "ALTER TABLE publication DROP PRIMARY KEY, ADD PRIMARY KEY (publication_id, version)"
    )


def downgrade():
    op.execute(
        "ALTER TABLE publication DROP PRIMARY KEY, ADD PRIMARY KEY (publication_id)"
    )
    op.drop_column("publication", "version")
