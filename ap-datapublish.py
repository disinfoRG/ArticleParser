#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()
import os
import sys
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


def parse_date_range(value):
    if value.find(":") >= 0:
        start, end = value.split(":", 1)
        return (dateparser.parse(start), dateparser.parse(end))
    else:
        d = dateparser.parse(value)
        return (d, d + datetime.timedelta(days=1))


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
    )
    pub_cmd.add_argument(
        "--processed-at",
        type=parse_date_range,
        help="publish data processed after given time",
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
            if args.published_at:
                day_start = args.published_at.timestamp()
                logger.info(day_start)
                day_end = day_start + 86400
                data_getter = QueryGetter(
                    queries.get_publications_by_producer_ranged_by_published_at,
                    producer_id=of_uuid(args.producer),
                    start=day_start,
                    end=day_end,
                )
            elif args.processed_at:
                logger.debug(
                    "publications by %s processed between %s and %s",
                    args.producer,
                    args.processed_at[0],
                    args.processed_at[1],
                )
                data_getter = QueryGetter(
                    queries.get_publications_by_producer_ranged_by_processed_at,
                    producer_id=of_uuid(args.producer),
                    start=args.processed_at[0].timestamp(),
                    end=args.processed_at[1].timestamp() - 1,
                )
            run_batch(
                data_getter=data_getter,
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
