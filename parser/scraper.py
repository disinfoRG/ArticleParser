import sqlalchemy as sa


class ScraperDb:
    engine: sa.engine.Engine

    def __init__(
        self, name, db_url, site_table_name, article_table_name, snapshot_table_name
    ):
        self.engine = sa.create_engine(db_url)
        self.metadata = sa.MetaData(bind=self.engine)
        self.metadata.reflect()
        self._conn = None
        self.table_names = {
            "site": site_table_name,
            "article": article_table_name,
            "snapshot": snapshot_table_name,
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


def get_snapshots(db, article_id=None, snapshot_at=None, site_id=None, url=None):
    """
    Get data of snapshots.
    """


def get_snapshot(db, article_id, snapshot_at):
    """
    Get data of a snapshot by its article id and snapshot time.
    """


def get_sites(db):
    """
    Get data of all sites.
    """


def get_site(db, site_id):
    """
    Get data of one site by its id.
    """
