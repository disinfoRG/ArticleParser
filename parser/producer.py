import logging
import json
import datetime
from uuid import uuid4
import parser.scraper as scraper
from . import version

name = "parser.producer"
logger = logging.getLogger(__name__)


def process(site):
    return {
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
        existing = parser_db.get_producer_by_site_id(site_id=site["site_id"])
        if existing is not None:
            producer_id = existing["producer_id"]
            parser_db.update_producer(
                **{k: producer[k] for k in ["name", "classification", "url"]},
                producer_id=producer_id,
            )
            logger.debug(
                "updated producer %s from site '%s' (%s)",
                producer_id,
                site["name"],
                site["site_id"],
            )
        else:
            producer_id = producer["producer_id"] = str(uuid4()).replace("-", "")
            parser_db.insert_producer(producer)
            logger.debug(
                "created producer %s from site '%s' (%s)",
                producer_id,
                site["name"],
                site["site_id"],
            )

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
