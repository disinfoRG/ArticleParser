import unittest as t
from pathlib import Path
from articleparser import Snapshot
import articleparser.publication as P
import articleparser.appledaily as appledaily


def load_snapshot(filename):
    file_path = Path(__file__).parent / "snapshots" / filename
    with file_path.open("r") as fh:
        return Snapshot(
            site_id=0,
            url="",
            snapshot_at=0,
            first_seen_at=0,
            last_updated_at=0,
            raw_data=fh.read(),
            article_type="Article",
        )


class AppledailyTest(t.TestCase):
    def test_parse_publication1(self):
        snapshot = load_snapshot("snapshot000104.html")
        soups = P.parse_soups(snapshot)
        p = appledaily.parse_publication(soups)
        self.assertEqual("9個QA解答《蘋果》訂閱問題　客服電話電郵看這裡 ｜ 蘋果新聞網 ｜ 蘋果日報 ", p["title"])
        self.assertEqual(
            0, p["publication_text"].find("《蘋果新聞網》每月只要120元，比一碗牛肉麵還便宜，即可無限暢覽；")
        )
        self.assertTrue("如有疑問歡迎來電或請來信，我們竭誠為您服務。" in p["publication_text"])
        self.assertIsNone(p["connect_from"])

    def test_parse_publication2(self):
        snapshot = load_snapshot("snapshot000104-2.html")
        soups = P.parse_soups(snapshot)
        p = appledaily.parse_publication(soups)
        self.assertEqual("【名醫家惡火】賴宅有無裝設住警器　火調報告1個月出爐 ｜ 蘋果新聞網 ｜ 蘋果日報 ", p["title"])
        self.assertEqual(0, p["publication_text"].find("高醫前院長賴文德位於高雄住家昨發生惡火，夫妻雖幸運獲救"))
        self.assertTrue("火場內部隔間裝潢與堆放雜物，才會導致火勢來得迅速猛烈，難以逃生" in p["publication_text"])
        self.assertTrue(
            "https://arc-photo-appledaily.s3.amazonaws.com/ap-ne-1-prod/public/3XOWF3QRUZJYODGW6YYFO4CLSA.jpg"
            in p["data"]["image_urls"]
        )

    def test_parse_publication3(self):
        snapshot = load_snapshot("snapshot000104-3.html")
        soups = P.parse_soups(snapshot)
        p = appledaily.parse_publication(soups)
        self.assertEqual("【暖心文】專營「不賺錢路線」　花蓮鳳榮行動超市駛進偏鄉 ｜ 蘋果新聞網 ｜ 蘋果日報 ", p["title"])
        self.assertEqual(p["publication_text"], "")
        self.assertEqual(p["data"]["image_urls"], [])
