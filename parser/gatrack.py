from . import Soups
import re

ga_id_pat = re.compile("UA-[\d\-]+")


def parse_ga_id(soups: Soups):
    return list(set([x.group(0) for x in ga_id_pat.finditer(soups.snapshot.raw_data)]))
