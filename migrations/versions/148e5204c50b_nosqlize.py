"""nosqlize

Revision ID: 148e5204c50b
Revises: f13a69bef275
Create Date: 2020-04-23 17:53:15.887359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "148e5204c50b"
down_revision = "f13a69bef275"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("publication", "publication_int_id")
    op.drop_column("publication", "producer_int_id")
    op.add_column("publication", sa.Column("data", sa.JSON))
    op.execute(
        """
        UPDATE publication
            SET data = JSON_OBJECT(
            "hashtags", JSON_EXTRACT(hashtags, "$"),
            "urls", JSON_EXTRACT(urls, "$"),
            "keywords", JSON_EXTRACT(keywords, "$"),
            "tags", JSON_EXTRACT(tags, "$"),
            "metadata", JSON_EXTRACT(metadata, "$"),
            "comments", JSON_EXTRACT(comments, "$")
        )
        """
    )
    op.drop_column("publication", "hashtags")
    op.drop_column("publication", "urls")
    op.drop_column("publication", "keywords")
    op.drop_column("publication", "tags")
    op.drop_column("publication", "metadata")
    op.drop_column("publication", "comments")
    op.drop_column("publication", "license")
    op.drop_column("publication", "language")

    op.drop_column("producer", "producer_int_id")
    op.add_column("producer", sa.Column("data", sa.JSON))
    op.drop_column("producer", "languages")
    op.drop_column("producer", "licenses")
    op.execute(
        """
        UPDATE producer
            SET data = JSON_OBJECT(
            "followership", JSON_EXTRACT(followership, "$"),
            "identifiers", JSON_EXTRACT(identifiers, "$")
        )
        """
    )
    op.drop_column("producer", "followership")
    op.drop_column("producer", "identifiers")


def downgrade():
    op.add_column("producer", sa.Column("identifiers", sa.JSON))
    op.add_column("producer", sa.Column("followership", sa.JSON))
    op.execute(
        """
        UPDATE producer SET
        followership = JSON_EXTRACT(data, "$.followership"),
        identifiers = JSON_EXTRACT(data, "$.identifiers")
        """
    )
    op.add_column("producer", sa.Column("licenses", sa.JSON))
    op.add_column("producer", sa.Column("languages", sa.JSON))
    op.drop_column("producer", "data")
    op.add_column("producer", sa.Column("producer_int_id", sa.Integer))

    op.add_column("publication", sa.Column("language", sa.String(256)))
    op.add_column("publication", sa.Column("license", sa.String(256)))
    op.add_column("publication", sa.Column("comments", sa.JSON))
    op.add_column("publication", sa.Column("metadata", sa.JSON))
    op.add_column("publication", sa.Column("tags", sa.JSON))
    op.add_column("publication", sa.Column("keywords", sa.JSON))
    op.add_column("publication", sa.Column("urls", sa.JSON))
    op.add_column("publication", sa.Column("hashtags", sa.JSON))
    op.execute(
        """
        UPDATE publication SET
        hashtags = JSON_EXTRACT(data, "$.hashtags"),
        urls = JSON_EXTRACT(data, "$.urls"),
        keywords = JSON_EXTRACT(data, "$.keywords"),
        tags = JSON_EXTRACT(data, "$.tags"),
        metadata = JSON_EXTRACT(data, "$.metadata"),
        comments = JSON_EXTRACT(data, "$.comments")
        """
    )
    op.drop_column("publication", "data")
    op.add_column("publication", sa.Column("producer_int_id", sa.Integer))
    op.add_column("publication", sa.Column("publication_int_id", sa.Integer))
