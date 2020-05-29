"""rename parser log to parser result

Revision ID: eb812412c4b5
Revises: b94b5c052b5c
Create Date: 2020-05-29 17:38:26.626814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eb812412c4b5"
down_revision = "b94b5c052b5c"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("parser_log", "parser_result")


def downgrade():
    op.rename_table("parser_result", "parser_log")
