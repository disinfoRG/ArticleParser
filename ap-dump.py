#!/usr/bin/env python3

from dotenv import load_dotenv

load_dotenv()
import os
import sys
import logging
import argparse
import pugsql
from uuid import UUID
import dateparser
import datetime
import json
import publisher.transform

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
queries = pugsql.module("queries")


def parse_uuid(value):
    return UUID(value)


def parse_date(value):
    d = dateparser.parse(value)
    return d.date()


def uuid_to_db(u):
    return str(u).replace("-", "")


def date_to_db(d):
    return datetime.datetime.fromisoformat(str(d)).timestamp()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--producer-id",
        type=parse_uuid,
        help="id of the producer to dump publications",
        required=True,
    )
    parser.add_argument(
        "--published-at",
        type=parse_date,
        help="published date of the publications",
        required=True,
    )
    parser.add_argument("--full-text", action="store_true", help="dump full text")
    return parser.parse_args()


def main(producer_id, published_at, full_text=False):
    queries.connect(os.getenv("DB_URL"))
    try:
        producer = queries.get_producer(producer_id=uuid_to_db(producer_id))
        logger.debug(
            "dumping publication of %s published at %s", producer["name"], published_at
        )
        for p in publisher.transform.publications(full_text=full_text)(
            queries.get_publications_by_producer_published_at(
                producer_id=uuid_to_db(producer_id),
                published_at=date_to_db(published_at),
            )
        ):
            print(json.dumps(p, ensure_ascii=False))
    finally:
        queries.disconnect()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(**vars(args)))
