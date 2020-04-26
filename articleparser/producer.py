from typing import *
import logging
import json
import datetime
from uuid import uuid4
from . import scraper
from . import version
from .scraper import Site

name = "parser.producer"
logger = logging.getLogger(__name__)


def process_item(site: Site):
    return {"name": site.name, "classification": site.type, "url": site.url, "data": {}}


def saver(queries, item, scraper=None):
    producer, site = item.item, item.original
    with queries.transaction():
        existing = queries.get_producer_by_site_id(site_id=site["site_id"])
        if existing is not None:
            producer_id = existing["producer_id"]
            queries.update_producer(
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
            queries.insert_producer(producer)
            logger.debug(
                "created producer %s from site '%s' (%s)",
                producer_id,
                site["name"],
                site["site_id"],
            )

        queries.upsert_producer_mapping(
            site_id=site["site_id"],
            producer_id=producer_id,
            scraper_id=scraper["scraper_id"],
            info=json.dumps(
                {
                    "last_processed_at": int(datetime.datetime.now().timestamp()),
                    "parser": {"name": name, "version": version},
                }
            ),
        )
