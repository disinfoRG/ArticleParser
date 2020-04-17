"""producer use uuid

Revision ID: c68f35739c74
Revises: 5b422bafbebf
Create Date: 2020-04-17 12:19:06.625723

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BINARY


# revision identifiers, used by Alembic.
revision = "c68f35739c74"
down_revision = "5b422bafbebf"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("producer", sa.Column("producer_uuid", BINARY(16), nullable=False))
    op.execute("UPDATE producer SET producer_uuid = UNHEX(REPLACE(UUID(), '-', ''))")
    op.create_index("uq_producer_uuid", "producer", ["producer_uuid"], unique=True)

    op.add_column(
        "producer_mapping", sa.Column("producer_uuid", BINARY(16), nullable=False)
    )
    op.execute(
        """UPDATE producer_mapping
               JOIN producer ON producer_mapping.producer_id = producer.producer_id
               SET producer_mapping.producer_uuid = producer.producer_uuid"""
    )
    op.create_index(
        "uq_producer_mapping_uuid", "producer_mapping", ["producer_uuid"], unique=True
    )

    op.add_column("publication", sa.Column("producer_uuid", BINARY(16), nullable=False))
    op.execute(
        """UPDATE publication
               JOIN producer ON publication.producer_id = producer.producer_id
               SET publication.producer_uuid = producer.producer_uuid"""
    )

    op.alter_column(
        "producer", "producer_id", autoincrement=False, existing_type=sa.Integer
    )
    op.execute("ALTER TABLE producer DROP PRIMARY KEY, ADD PRIMARY KEY (producer_uuid)")
    op.alter_column(
        "producer",
        "producer_id",
        new_column_name="producer_int_id",
        existing_type=sa.Integer,
    )
    op.alter_column(
        "producer",
        "producer_uuid",
        new_column_name="producer_id",
        existing_type=BINARY(16),
    )
    op.alter_column(
        "producer_mapping",
        "producer_id",
        new_column_name="producer_int_id",
        existing_type=sa.Integer,
    )
    op.alter_column(
        "producer_mapping",
        "producer_uuid",
        new_column_name="producer_id",
        existing_type=BINARY(16),
    )
    op.alter_column(
        "publication",
        "producer_id",
        new_column_name="producer_int_id",
        existing_type=sa.Integer,
    )
    op.alter_column(
        "publication",
        "producer_uuid",
        new_column_name="producer_id",
        existing_type=BINARY(16),
    )


def downgrade():
    op.alter_column(
        "publication",
        "producer_id",
        new_column_name="producer_uuid",
        existing_type=BINARY(16),
    )
    op.alter_column(
        "publication",
        "producer_int_id",
        new_column_name="producer_id",
        existing_type=sa.Integer,
    )
    op.alter_column(
        "producer_mapping",
        "producer_id",
        new_column_name="producer_uuid",
        existing_type=BINARY(16),
    )
    op.alter_column(
        "producer_mapping",
        "producer_int_id",
        new_column_name="producer_id",
        existing_type=sa.Integer,
    )
    op.alter_column(
        "producer",
        "producer_id",
        new_column_name="producer_uuid",
        existing_type=BINARY(16),
    )
    op.alter_column(
        "producer",
        "producer_int_id",
        new_column_name="producer_id",
        existing_type=sa.Integer,
    )
    op.execute("ALTER TABLE producer DROP PRIMARY KEY, ADD PRIMARY KEY (producer_id)")
    op.alter_column(
        "producer", "producer_id", autoincrement=True, existing_type=sa.Integer
    )

    op.drop_column("publication", "producer_uuid")

    op.drop_index("uq_producer_mapping_uuid", table_name="producer_mapping")
    op.drop_column("producer_mapping", "producer_uuid")

    op.drop_index("uq_producer_uuid", table_name="producer")
    op.drop_column("producer", "producer_uuid")
