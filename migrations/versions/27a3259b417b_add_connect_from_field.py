"""add connect from field

Revision ID: 27a3259b417b
Revises: 1e736aa49bb5
Create Date: 2020-03-16 17:16:06.391761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "27a3259b417b"
down_revision = "1e736aa49bb5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("publication", sa.Column("connect_from", sa.String(255)))


def downgrade():
    op.drop_column("publication", "connect_from")
