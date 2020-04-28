"""add drive table

Revision ID: e1f1c0c082fd
Revises: ed9573cc4869
Create Date: 2020-04-28 15:47:33.877459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e1f1c0c082fd"
down_revision = "ed9573cc4869"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "drive",
        sa.Column("drive_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("data", sa.JSON, nullable=False),
    )
    op.execute(
        """
        INSERT drive (drive_id, name, data) VALUES (1, "local", "{}")
        """
    )


def downgrade():
    op.drop_table("drive")
