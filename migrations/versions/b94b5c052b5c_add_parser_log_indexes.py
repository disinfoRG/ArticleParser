"""add parser log indexes

Revision ID: b94b5c052b5c
Revises: 2849266c6323
Create Date: 2020-05-25 14:45:20.433287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b94b5c052b5c"
down_revision = "2849266c6323"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ik_created_at", "parser_log", ["created_at"])


def downgrade():
    op.drop_index("ik_created_at")
