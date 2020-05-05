import os
import unittest as t
import articleparser.scraper as scraper


class TestScraperDb(t.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = scraper.ScraperDb(
            "TestScraper",
            os.getenv("SCRAPER_DB_URL"),
            site_table_name="Site",
            article_table_name="Article",
            snapshot_table_name="ArticleSnapshot",
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def testConnect(self):
        self.assertTrue(self.db.connect)

    def testTable(self):
        self.assertEqual("ArticleSnapshot", self.db("snapshot").name)


class TestSDK(t.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = scraper.ScraperDb(
            "TestScraper",
            os.getenv("SCRAPER_DB_URL"),
            site_table_name="Site",
            article_table_name="Article",
            snapshot_table_name="ArticleSnapshot",
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def testGetSite(self):
        self.assertIsNone(scraper.get_site(self.db, 1337))
        site = scraper.get_site(self.db, 1)
        self.assertEqual(1, site["site_id"])

    def testGetSites(self):
        sites = scraper.get_sites(self.db).fetchall()
        self.assertTrue(len(sites) > 0)

    def testGetSnapshot(self):
        snapshot = scraper.get_snapshot(self.db, article_id=1, snapshot_at=0)
        self.assertIsNone(snapshot)

    def testGetSnapshots(self):
        for snapshot in scraper.get_snapshots(self.db, site_id=1).fetchall():
            self.assertEqual(1, snapshot["site_id"])

        for snapshot in scraper.get_snapshots(
            self.db, article_ids=[1, 2, 3]
        ).fetchall():
            self.assertTrue(snapshot["article_id"] in [1, 2, 3])
