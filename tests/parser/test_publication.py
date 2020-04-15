import unittest as t
from pathlib import Path
import parser.publication as P


def load_snapshot(filename):
    file_path = Path(__file__).parent / "snapshots" / filename
    with file_path.open("r") as f:
        return {"raw_data": f.read()}


class TestParseGAID(t.TestCase):
    cases = [
        {"f": "snapshot000001.html", "ga-id": []},
        {"f": "snapshot000002.html", "ga-id": ["UA-135651881-1"]},
        {"f": "snapshot000003.html", "ga-id": ["UA-19409266-3"]},
        {"f": "snapshot000098.html", "ga-id": ["UA-32365737-1"]},
        {"f": "snapshot000099.html", "ga-id": ["UA-32365737-1"]},
        {"f": "snapshot000100.html", "ga-id": []},
        {"f": "snapshot000101.html", "ga-id": []},
        {"f": "snapshot000102.html", "ga-id": ["UA-91757317-2"]},
        {"f": "snapshot000104.html", "ga-id": []},
        {"f": "snapshot000105.html", "ga-id": []},
        {"f": "snapshot000106.html", "ga-id": []},
        {"f": "snapshot000107.html", "ga-id": []},
        {"f": "snapshot000108.html", "ga-id": []},
        {"f": "snapshot000114.html", "ga-id": []},
        {"f": "snapshot000115.html", "ga-id": []},
        {"f": "snapshot000116.html", "ga-id": ["UA-113656179-1"]},
        {"f": "snapshot000117.html", "ga-id": ["UA-56379064-19"]},
        {"f": "snapshot000119.html", "ga-id": ["UA-113511599-1"]},
        {"f": "snapshot000122.html", "ga-id": []},
        {"f": "snapshot000123.html", "ga-id": []},
        {"f": "snapshot000730.html", "ga-id": ["UA-80236651-1", "UA-80236651-3"]},
        {"f": "snapshot000731.html", "ga-id": ["UA-21332781-17"]},
        {"f": "snapshot000732.html", "ga-id": []},
        {"f": "snapshot000751.html", "ga-id": []},
        {"f": "snapshot000752.html", "ga-id": ["UA-135651881-1"]},
        {"f": "snapshot000753.html", "ga-id": []},
        {"f": "snapshot000789.html", "ga-id": ["UA-114908401-1"]},
        {"f": "snapshot001666.html", "ga-id": ["UA-1801883-33"]},
        {"f": "snapshot001667.html", "ga-id": ["UA-31425034-13"]},
        {"f": "snapshot001668.html", "ga-id": ["UA-135651881-1"]},
        {"f": "snapshot002922.html", "ga-id": []},
        {"f": "snapshot004589.html", "ga-id": []},
        {"f": "snapshot011237.html", "ga-id": []},
        {"f": "snapshot011239.html", "ga-id": []},
        {"f": "snapshot011240.html", "ga-id": []},
        {"f": "snapshot011241.html", "ga-id": []},
        {"f": "snapshot011242.html", "ga-id": []},
        {"f": "snapshot011243.html", "ga-id": []},
        {"f": "snapshot011245.html", "ga-id": ["UA-161561752-1"]},
        {"f": "snapshot011246.html", "ga-id": ["UA-161578722-1"]},
        {"f": "snapshot011247.html", "ga-id": ["UA-161511720-1"]},
        {"f": "snapshot011248.html", "ga-id": ["UA-161574581-1"]},
        {"f": "snapshot011249.html", "ga-id": ["UA-64498512-1"]},
        {"f": "snapshot011251.html", "ga-id": ["UA-161524355-1"]},
        {"f": "snapshot011252.html", "ga-id": ["UA-161418852-1"]},
    ]

    def test_parse_ga_id(self):
        for case in self.cases:
            try:
                snapshot = load_snapshot(case["f"])
                soups = P.parse_soups(snapshot)
                ga_id = P.parse_ga_id(soups)
                self.assertEqual(case["ga-id"], ga_id, case["f"])
            except Exception as e:
                self.fail(f"{e}: {case}")


class TestParseFBID(t.TestCase):
    cases = [
        {"f": "snapshot000001.html", "fb:app_id": ""},
        {"f": "snapshot000002.html", "fb:app_id": ""},
        {"f": "snapshot000003.html", "fb:app_id": ""},
        {"f": "snapshot000098.html", "fb:app_id": ""},
        {"f": "snapshot000099.html", "fb:app_id": ""},
        {"f": "snapshot000100.html", "fb:app_id": "1379575469016080"},
        {"f": "snapshot000101.html", "fb:app_id": "1057196854300149"},
        {"f": "snapshot000102.html", "fb:app_id": "146858218737386"},
        {"f": "snapshot000104.html", "fb:app_id": "244889285591923"},
        {"f": "snapshot000105.html", "fb:app_id": "350231215126101"},
        {"f": "snapshot000106.html", "fb:app_id": "140490219413038"},
        {"f": "snapshot000107.html", "fb:app_id": "524202197752727"},
        {"f": "snapshot000108.html", "fb:app_id": "137747556917027"},
        {"f": "snapshot000114.html", "fb:app_id": ""},
        {"f": "snapshot000115.html", "fb:app_id": ""},
        {"f": "snapshot000116.html", "fb:app_id": "1670584986525771"},
        {"f": "snapshot000117.html", "fb:app_id": "1649125262076241"},
        {"f": "snapshot000119.html", "fb:app_id": ""},
        {"f": "snapshot000122.html", "fb:app_id": "1953515198281701"},
        {"f": "snapshot000123.html", "fb:app_id": ""},
        {"f": "snapshot000730.html", "fb:app_id": "125239581431127"},
        {"f": "snapshot000731.html", "fb:app_id": "1433963440163679"},
        {"f": "snapshot000732.html", "fb:app_id": ""},
        {"f": "snapshot000751.html", "fb:app_id": ""},
        {"f": "snapshot000752.html", "fb:app_id": ""},
        {"f": "snapshot000753.html", "fb:app_id": ""},
        {"f": "snapshot000789.html", "fb:app_id": ""},
        {"f": "snapshot001666.html", "fb:app_id": "1612170172377312"},
        {"f": "snapshot001667.html", "fb:app_id": "1048004538606594"},
        {"f": "snapshot001668.html", "fb:app_id": ""},
        {"f": "snapshot002922.html", "fb:app_id": ""},
        {"f": "snapshot004589.html", "fb:app_id": ""},
        {"f": "snapshot011237.html", "fb:app_id": "1385360291698338"},
        {"f": "snapshot011239.html", "fb:app_id": ""},
        {"f": "snapshot011240.html", "fb:app_id": "175313259598308"},
        {"f": "snapshot011241.html", "fb:app_id": "917307478388825"},
        {"f": "snapshot011242.html", "fb:app_id": "444539738978688"},
        {"f": "snapshot011243.html", "fb:app_id": ""},
        {"f": "snapshot011245.html", "fb:app_id": ""},
        {"f": "snapshot011246.html", "fb:app_id": ""},
        {"f": "snapshot011247.html", "fb:app_id": ""},
        {"f": "snapshot011248.html", "fb:app_id": ""},
        {"f": "snapshot011249.html", "fb:app_id": "179670249110775"},
        {"f": "snapshot011251.html", "fb:app_id": ""},
        {"f": "snapshot011252.html", "fb:app_id": ""},
    ]

    def test_parse_fb_app_id(self):
        for case in self.cases:
            try:
                snapshot = load_snapshot(case["f"])
                soups = P.parse_soups(snapshot)
                if "fb:app_id" in soups["meta-tags"]:
                    fb_app_id = soups["meta-tags"]["fb:app_id"]
                    self.assertEqual(case["fb:app_id"], fb_app_id, case["f"])
                else:
                    self.assertEqual(case["fb:app_id"], "", case["f"])
            except Exception as e:
                self.fail(f"{e}: {case}")


class TestPublishedAt(t.TestCase):
    cases = [
        {"f": "snapshot000001.html", "published_at": 1585140802},
        {"f": "snapshot000002.html", "published_at": 1583486880},
        {"f": "snapshot000003.html", "published_at": 1585411200},
        {"f": "snapshot000098.html", "published_at": None},
        {"f": "snapshot000099.html", "published_at": None},
        {"f": "snapshot000100.html", "published_at": 1577271070},
        {"f": "snapshot000101.html", "published_at": 1585125960},
        {"f": "snapshot000102.html", "published_at": 1575084600},
        {"f": "snapshot000104.html", "published_at": None},
        {"f": "snapshot000105.html", "published_at": 1586482453},
        {"f": "snapshot000106.html", "published_at": 1583787541},
        {"f": "snapshot000107.html", "published_at": 1585133580},
        {"f": "snapshot000108.html", "published_at": 1585126841},
        {"f": "snapshot000114.html", "published_at": None},
        {"f": "snapshot000115.html", "published_at": 1585131779},
        {"f": "snapshot000116.html", "published_at": 1584979200},
        {"f": "snapshot000117.html", "published_at": None},
        {"f": "snapshot000119.html", "published_at": 1585670874},
        {"f": "snapshot000122.html", "published_at": None},
        {"f": "snapshot000123.html", "published_at": None},
        {"f": "snapshot000730.html", "published_at": 1585142100},
        {"f": "snapshot000731.html", "published_at": 1585136223},
        {"f": "snapshot000732.html", "published_at": None},
        {"f": "snapshot000751.html", "published_at": 1585139301},
        {"f": "snapshot000752.html", "published_at": 1583486880},
        {"f": "snapshot000753.html", "published_at": 1371917717},
        {"f": "snapshot000789.html", "published_at": 1585670960},
        {"f": "snapshot001666.html", "published_at": 1585194982},
        {"f": "snapshot001667.html", "published_at": 1585671773},
        {"f": "snapshot001668.html", "published_at": 1583486880},
        {"f": "snapshot002922.html", "published_at": None},
        {"f": "snapshot004589.html", "published_at": 1585152000},
        {"f": "snapshot011237.html", "published_at": 1585131060},
        {"f": "snapshot011239.html", "published_at": 1585152000},
        {"f": "snapshot011240.html", "published_at": 1585130771},
        {"f": "snapshot011241.html", "published_at": 1585120838},
        {"f": "snapshot011242.html", "published_at": 1585144854},
        {"f": "snapshot011243.html", "published_at": 1582473600},
        {"f": "snapshot011245.html", "published_at": 1585477428},
        {"f": "snapshot011246.html", "published_at": 1585478020},
        {"f": "snapshot011247.html", "published_at": 1585475578},
        {"f": "snapshot011248.html", "published_at": 1585469282},
        {"f": "snapshot011249.html", "published_at": 1585477667},
        {"f": "snapshot011251.html", "published_at": 1586315444},
        {"f": "snapshot011252.html", "published_at": 1586310388},
    ]

    def test_parse_published_at(self):
        for case in self.cases:
            try:
                snapshot = load_snapshot(case["f"])
                soups = P.parse_soups(snapshot)
                published_at = P.parse_published_at(soups)
                self.assertEqual(case["published_at"], published_at, case["f"])
            except Exception as e:
                self.fail(f"{e}: {case}")
