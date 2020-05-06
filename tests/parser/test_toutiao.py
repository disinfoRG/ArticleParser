import unittest as t
from pathlib import Path
from articleparser import Snapshot
import articleparser.publication as P
import articleparser.toutiao as toutiao


class ToutiaoTest(t.TestCase):
    def setUp(self):
        with open(Path(__file__).parent / "snapshots/snapshot000015.html", "r") as fh:
            self.soups = P.parse_soups(
                Snapshot(
                    site_id=0,
                    url="https://www.toutiao.com/a6822529318262931976/",
                    snapshot_at=0,
                    first_seen_at=0,
                    last_updated_at=0,
                    raw_data=fh.read(),
                    article_type="Article",
                )
            )

    def test_parse_publication(self):
        p = toutiao.parse_publication(self.soups)
        self.assertEqual("下周重磅日程：海外复工进展，美国4月非农，中国4月外贸数据", p["title"])
        self.assertEqual(
            0, p["publication_text"].find("下周海外复工全面铺开，需重点关注经济恢复情况。美国4月非农可能出现史上最糟表现")
        )
        self.assertTrue("周五（5月8日），京东、野村控股发财报，优步、前程无忧可能发财报" in p["publication_text"])
        self.assertIsNone(p["connect_from"])
        self.assertTrue(
            "http://p1.pstatp.com/large/pgc-image/RxuYT5uEi54PUz"
            in p["data"]["image_urls"]
        )
