import re

ga_id_pat = re.compile("UA-[\d\-]+")

def parse_ga_id(soup):
    return [ x.group(0) for x in ga_id_pat.finditer(soup.text) ]
