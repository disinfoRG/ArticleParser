from dotenv import load_dotenv

load_dotenv()

import sys
import json
import datetime
from . import version

name = "parser.producer"


def transform_site(site):
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


def transformer(sites):
    for site in sites:
        yield transform_site(site)


def all_sites_getter(scraper_db, offset=0, limit=1000):
    return scraper_db.get_all_sites(offset=offset, limit=limit)


def site_getter(scraper_db, site_id, offset=0, limit=1):
    if offset == 0 and limit > 1:
        return [scraper_db.get_site_by_id(site_id=site_id)]
    else:
        return []


def saver(dump=False):
    if dump:

        def json_dumper(_, item):
            json.dump(vars(item), sys.stdout)

        return json_dumper

    def save_to_db(to_db, item):
        producer, site = item.item, item.original
        with to_db.transaction():
            producer_id = to_db.upsert_producer(producer)
            to_db.upsert_producer_mapping(
                site_id=site["site_id"],
                producer_id=producer_id,
                info=json.dumps(
                    {
                        "last_processed_at": int(datetime.datetime.now().timestamp()),
                        "parser": {"name": name, "version": version},
                    }
                ),
            )

    return save_to_db
