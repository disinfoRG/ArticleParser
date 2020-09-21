import unittest as t
from pathlib import Path

import articleparser.fb as fb
import articleparser.publication as P
from articleparser import Snapshot


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


class FbTest(t.TestCase):
    def test_parse_publication1(self):
        snapshot = load_snapshot("fbsnapshot001.html")
        soups = P.parse_soups(snapshot)
        p = fb.parse_publication(soups)
        self.assertTrue(p["data"]["hashtags"] == list())
        self.assertEqual(
            "難怪-為什麼我總是聽不懂總統府的發言，原來是請一個渣男在靠北。 講的畜語害我都聽不懂。 我好生氣喔~ 但請國人別忘記蔡政府要國人吃含瘦肉精豬肉嘿。 花錢又傷身，毒害台灣。",
            p["publication_text"],
        )
        self.assertTrue(
            "https://scontent.ftpe8-3.fna.fbcdn.net/v/t1.0-0/p526x296/118825781_3662271600473224_4051157518986893414_o.jpg?_nc_cat=102&_nc_sid=110474&_nc_ohc=pXGE2gwr6BQAX-U0Mo8&_nc_ht=scontent.ftpe8-3.fna&tp=6&oh=2fe62327647a337d3490dfb5accb746c&oe=5F8E2CB2"
            in p["data"]["image_urls"]
        )
        self.assertEqual("1K", p["data"]["reactions"]["shares"])

    def test_parse_publication2(self):
        snapshot = load_snapshot("fbsnapshot002.html")
        soups = P.parse_soups(snapshot)
        p = fb.parse_publication(soups)
        self.assertTrue("吸毒" in p["data"]["hashtags"])
        self.assertTrue("喪屍" in p["data"]["hashtags"])
        self.assertEqual("這對夫妻也太沒責任感了吧！ # 吸毒 # 喪屍", p["publication_text"])
        self.assertEqual("1", p["data"]["reactions"]["shares"])
        self.assertTrue("https://kairos.news/135385" in p["data"]["urls"])
