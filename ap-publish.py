#!/usr/bin/env python3

from dotenv import load_dotenv

load_dotenv()
import os
import sys
import pathlib
import logging
import traceback
import argparse
from uuid import UUID
import dateparser
import datetime
import pugsql
from functools import partial
from articleparser.runners import run_batch, run_one_shot, QueryGetter
from articleparser.publish import (
    process_producer_item,
    process_publication_item,
    JsonItemSaver,
)
from articleparser.db import of_uuid

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
queries = pugsql.module("queries")

publication_fieldnames = [
    "id",
    "version",
    "identifiers",
    "producer_id",
    "canonical_url",
    "title",
    "text",
    "author",
    "published_at",
    "first_seen_at",
    "last_updated_at",
    "urls",
    "hashtags",
    "keywords",
    "reactions",
    "comments",
    "connect_from",
]


def publications_getter(producer_id=None, published_at_range=None):
    def getter(db, offset=0, limit=1000):
        if published_at_range is not None:
            start, end = published_at_range
            if producer_id is not None:
                return db.get_publications_by_producer_ranged_by_published_at(
                    producer_id=producer_id,
                    start=start,
                    end=end,
                    limit=limit,
                    offset=offset,
                )
            else:
                return db.get_publications_ranged_by_published_at(
                    start=start, end=end, limit=limit, offset=offset
                )
        else:
            if producer_id is not None:
                return db.get_publications(
                    producer_id=producer_id, limit=limit, offset=offset
                )
            else:
                return db.get_publications(limit=limit, offset=offset)

    return getter


def day_range(start=None, days=None, until=None):
    if start is None:
        start = datetime.datetime(2018, 1, 1, 0, 0, 0)
    if until is None:
        until = datetime.datetime.now()
    day = start
    step = datetime.timedelta(days=1)
    if days is None:
        while day <= until:
            yield day
            day = day + step
    else:
        for _ in range(days):
            yield day
            day = day + step
            if day > until:
                break


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publish datasets from parser database"
    )
    parser.add_argument(
        "-f", "--format", choices=["jsonl"], help="export format", default="jsonl"
    )
    parser.add_argument("-o", "--output", default="-", help="save to file")
    cmds = parser.add_subparsers(
        title="data class to publish", dest="command", required=True
    )
    prod_cmd = cmds.add_parser("producer", help="publish producer data in parser db")
    pub_cmd = cmds.add_parser(
        "publication", help="publish publication data in parse db"
    )
    pub_cmd.add_argument(
        "--published-at",
        type=dateparser.parse,
        help="publishing day of the publication to publish",
        required=True,
    )
    pub_cmd.add_argument(
        "--producer",
        type=UUID,
        help="producer id of the publication to publish",
        required=True,
    )
    pub_cmd.add_argument("--full-text", action="store_true", help="publish full text")
    return parser.parse_args()


def main(args):
    queries.connect(os.getenv("DB_URL"))
    try:
        if args.command == "producer":
            run_one_shot(
                data_getter=QueryGetter(queries.get_producers),
                processor=process_producer_item,
                data_saver=JsonItemSaver(),
            )
        elif args.command == "publication":
            day_start = args.published_at.timestamp()
            logger.info(day_start)
            day_end = day_start + 86400
            run_batch(
                data_getter=QueryGetter(
                    queries.get_publications_by_producer_ranged_by_published_at,
                    producer_id=of_uuid(args.producer),
                    start=day_start,
                    end=day_end,
                ),
                processor=partial(process_publication_item, full_text=args.full_text),
                data_saver=JsonItemSaver(),
            )
        else:
            raise RuntimeError(f"Unknown command '{args.command}'")
        return 0
    except:
        logger.error(traceback.format_exc())
        return -1
    finally:
        queries.disconnect()


if __name__ == "__main__":
    sys.exit(main(parse_args()))
