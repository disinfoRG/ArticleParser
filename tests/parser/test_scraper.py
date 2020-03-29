import os
import unittest as t
import parser.scraper


class TestScraperDb(t.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scraper = parser.scraper.ScraperDb(
            "TestScraper",
            os.getenv("SCRAPER_DB_URL"),
            site_table_name="Site",
            article_table_name="Article",
            snapshot_table_name="Snapshot",
        )

    @classmethod
    def tearDownClass(cls):
        cls.scraper.close()

    def testConnect(self):
        self.assertTrue(self.scraper.connect)

    def testTable(self):
        self.assertEqual("Snapshot", self.scraper("snapshot").name)


class TestSDK(t.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scraper = parser.scraper.ScraperDb(
            "TestScraper",
            os.getenv("SCRAPER_DB_URL"),
            site_table_name="Site",
            article_table_name="Article",
            snapshot_table_name="Snapshot",
        )

    @classmethod
    def tearDownClass(cls):
        cls.scraper.close()

    def testGetSite(self):
        db = self.scraper
        q = db("site").select().where(db("site").c.site_id == 1)
        r = db.execute(q)
        row = r.fetchone()
        self.assertEqual(1, row["site_id"])
