import unittest as t
from pathlib import Path
from parser import Snapshot
import parser.publication as P
import parser.pttread as PTT


class PTTReadTest(t.TestCase):
    def setUp(self):
        with open(
            Path(__file__).parent / "snapshots/snapshot000098-pttread.html", "r"
        ) as fh:
            self.soups = P.parse_soups(Snapshot(raw_data=fh.read()))

    def test_parse_publication(self):
        p = PTT.parse_publication(self.soups)
        self.fail(p)
