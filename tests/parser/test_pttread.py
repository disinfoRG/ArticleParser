import unittest as t
from pathlib import Path
from articleparser import Snapshot
import articleparser.publication as P
import articleparser.pttread as PTT


class PTTReadTest(t.TestCase):
    def setUp(self):
        with open(
            Path(__file__).parent / "snapshots/snapshot000098-pttread.html", "r"
        ) as fh:
            self.soups = P.parse_soups(
                Snapshot(
                    site_id=0,
                    url="https://www.ptt.cc/bbs/Gossiping/M.1582843734.A.FB5.html",
                    snapshot_at=0,
                    first_seen_at=0,
                    last_updated_at=0,
                    raw_data=fh.read(),
                    article_type="PTT",
                )
            )

    def test_parse_publication(self):
        p = PTT.parse_publication(self.soups)
        self.assertEqual("lpbrother", p["author"])
        self.assertEqual("Re: [問卦] 女生說只喝2500塊以上的酒是啥意思", p["title"])
        self.assertEqual(0, p["publication_text"].find("借八卦板高人氣問一下，\n為啥台灣產的威士忌都特別貴"))
        self.assertIsNone(p["connect_from"])
        self.assertEqual(1582843734, p["published_at"])
