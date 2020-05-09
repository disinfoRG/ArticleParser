"""publication use uuid

Revision ID: 05ce1d870fac
Revises: c68f35739c74
Create Date: 2020-04-17 18:17:51.482689

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY


# revision identifiers, used by Alembic.
revision = "05ce1d870fac"
down_revision = "c68f35739c74"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "publication", sa.Column("publication_uuid", BINARY(16), nullable=False)
    )
    op.execute(
        "UPDATE publication SET publication_uuid = UNHEX(REPLACE(UUID(), '-', ''))"
    )
    op.create_index(
        "uq_publication_uuid", "publication", ["publication_uuid"], unique=True
    )

    op.add_column(
        "publication_mapping", sa.Column("publication_uuid", BINARY(16), nullable=False)
    )
    op.execute(
        """UPDATE publication_mapping
               JOIN publication ON publication_mapping.publication_id = publication.publication_id
               SET publication_mapping.publication_uuid = publication.publication_uuid"""
    )
    op.create_index(
        "uq_publication_mapping_uuid",
        "publication_mapping",
        ["publication_uuid", "version"],
        unique=True,
    )

    op.alter_column(
        "publication",
        "publication_id",
        autoincrement=False,
        existing_type=sa.Integer,
        nullable=False,
    )
    op.execute(
        "ALTER TABLE publication DROP PRIMARY KEY, ADD PRIMARY KEY (publication_uuid)"
    )

    op.alter_column(
        "publication",
        "publication_id",
        new_column_name="publication_int_id",
        existing_type=sa.Integer,
    )
    op.alter_column(
        "publication",
        "publication_uuid",
        new_column_name="publication_id",
        existing_type=BINARY(16),
    )
    op.alter_column(
        "publication_mapping",
        "publication_id",
        new_column_name="publication_int_id",
        existing_type=sa.Integer,
    )
    op.alter_column(
        "publication_mapping",
        "publication_uuid",
        new_column_name="publication_id",
        existing_type=BINARY(16),
    )


def downgrade():
    op.alter_column(
        "publication_mapping",
        "publication_id",
        new_column_name="publication_uuid",
        existing_type=BINARY(16),
    )
    op.alter_column(
        "publication_mapping",
        "publication_int_id",
        new_column_name="publication_id",
        existing_type=sa.Integer,
    )
    op.alter_column(
        "publication",
        "publication_id",
        new_column_name="publication_uuid",
        existing_type=BINARY(16),
    )
    op.alter_column(
        "publication",
        "publication_int_id",
        new_column_name="publication_id",
        existing_type=sa.Integer,
    )

    op.execute(
        "ALTER TABLE publication DROP PRIMARY KEY, ADD PRIMARY KEY (publication_id)"
    )
    op.alter_column(
        "publication", "publication_id", autoincrement=True, existing_type=sa.Integer
    )

    op.drop_index("uq_publication_mapping_uuid", table_name="publication_mapping")
    op.drop_column("publication_mapping", "publication_uuid")

    op.drop_index("uq_publication_uuid", table_name="publication")
    op.drop_column("publication", "publication_uuid")
