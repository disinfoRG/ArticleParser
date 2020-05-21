"""fix publication primary key

Revision ID: 2849266c6323
Revises: 4588812811ae
Create Date: 2020-05-21 19:08:38.371821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2849266c6323"
down_revision = "4588812811ae"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE publication DROP PRIMARY KEY, ADD PRIMARY KEY (publication_id, version)"
    )


def downgrade():
    op.execute(
        "ALTER TABLE publication DROP PRIMARY KEY, ADD PRIMARY KEY (publication_id)"
    )
