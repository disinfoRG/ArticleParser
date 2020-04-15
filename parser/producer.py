import json
import datetime
import parser.scraper as scraper
from . import version

name = "parser.producer"


def process(site):
    return {
        "producer_id": site["site_id"],
        "name": site["name"],
        "classification": site["type"],
        "url": site["url"],
        "languages": json.dumps([]),
        "licenses": json.dumps([]),
        "followership": json.dumps({}),
        "identifiers": json.dumps({}),
    }


def all_sites_getter(scraper_db, offset=0, limit=1000):
    return scraper.get_sites(scraper_db, offset=offset, limit=limit).fetchall()


def site_getter(scraper_db, site_id, offset=0, limit=1):
    if offset == 0 and limit > 1:
        return [scraper.get_site(scraper_db, site_id=site_id)]
    else:
        return []


def saver(parser_db, item):
    producer, site = item.item, item.original
    with parser_db.transaction():
        producer_id = parser_db.upsert_producer(producer)
        parser_db.upsert_producer_mapping(
            site_id=site["site_id"],
            producer_id=producer_id,
            info=json.dumps(
                {
                    "last_processed_at": int(datetime.datetime.now().timestamp()),
                    "parser": {"name": name, "version": version},
                }
            ),
        )
