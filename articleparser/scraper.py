from typing import *
import sqlalchemy as sa
from sqlalchemy import sql
import zlib


class Site(NamedTuple):
    site_id: int
    type: str
    name: str
    url: str
    config: str
    is_active: Optional[int]
    airtable_id: str
    site_info: str
    last_crawled_at: Optional[int]


class ScraperDb:
    engine: sa.engine.Engine

    def __init__(self, name, db_url, data):
        site_table_name, article_table_name, snapshot_table_name = (
            data["site_table_name"],
            data["article_table_name"],
            data["snapshot_table_name"],
        )
        self.engine = sa.create_engine(db_url)
        self.metadata = sa.MetaData(bind=self.engine)
        self.metadata.reflect()
        self._conn = None
        self.table_names = {
            "site": data["site_table_name"],
            "article": data["article_table_name"],
            "snapshot": data["snapshot_table_name"],
        }

    @property
    def connect(self):
        """
        Db connection
        """
        if self._conn is None:
            self._conn = self.engine.connect()
        return self._conn

    def __call__(self, table: str):
        """
        Get a db table by name.
        """
        return sa.Table(self.table_names[table], self.metadata)

    def execute(self, query):
        """
        Execute a query.
        """
        return self.connect.execute(query)

    def begin(self):
        """
        Start a db trascation.
        """
        self.connect.begin()

    def close(self):
        """
        Close db connection
        """
        self.connect.close()


def query_snapshot(db, limit=10000, offset=0):
    return (
        sql.select(
            [
                db("snapshot").c.article_id,
                db("snapshot").c.snapshot_at,
                db("snapshot").c.raw_data,
                db("article").c.site_id,
                db("article").c.url,
                db("article").c.first_snapshot_at.label("first_seen_at"),
                db("article").c.last_snapshot_at.label("last_updated_at"),
                db("article").c.article_type,
            ]
        )
        .select_from(
            db("snapshot").join(
                db("article"), db("snapshot").c.article_id == db("article").c.article_id
            )
        )
        .limit(limit)
        .offset(offset)
    )


def get_snapshots(
    db,
    article_id=None,
    article_ids=None,
    snapshot_at_later_than=None,
    site_id=None,
    url=None,
    limit=10000,
    offset=0,
):
    """
    Get data of snapshots as a result set.
    """
    clauses = []
    if article_id is not None:
        clauses.append(db("snapshot").c.article_id == article_id)
    if article_ids is not None:
        clauses.append(db("snapshot").c.article_id.in_(article_ids))
    if snapshot_at_later_than is not None:
        clauses.append(db("snapshot").c.snapshot_at > snapshot_at_later_than)
    if site_id is not None:
        clauses.append(db("article").c.site_id == site_id)
    if url is not None:
        clauses.append(db("article").c.url_hash == zlib.crc32(url.encode("utf-8")))
        clauses.append(db("article").c.url == url)
    return query_snapshot(db).where(sql.and_(*clauses))


def get_snapshot(db, article_id, snapshot_at):
    """
    Get data of a snapshot by its article id and snapshot time.

    Get `None` if there is no such a snapshot.
    """
    query = query_snapshot(db).where(
        (db("snapshot").c.article_id == article_id)
        & (db("snapshot").c.snapshot_at == snapshot_at)
    )
    result = db.execute(query)
    return result.fetchone()


def get_sites(db):
    return db("site").select()


def get_site(db, site_id):
    return get_sites(db).where(db("site").c.site_id == site_id)
