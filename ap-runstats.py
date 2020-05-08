#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()

import os
import argparse
import sys
import logging
import traceback
import pugsql
from articleparser.dateutil import *

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
queries = pugsql.module("queries")


def run_parser_stats(queries, processed_at: DateRange):
    r = queries.compute_parser_stats(
        start=processed_at.start_timestamp(), end=processed_at.end_timestamp()
    )
    logger.debug("insert %d stats", r)


def run_publication_stats(queries, published_at: date):
    r = queries.compute_publication_stats(
        start=day_start(published_at).timestamp(), end=day_end(published_at).timestamp()
    )
    logger.debug("insert %d stats", r)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--processed-at",
        type=parse_date_range,
        help="compute stats for data processed after given time",
        required=True,
    )
    return parser.parse_args()


def main(args):
    queries.connect(os.getenv("DB_URL"))
    try:
        run_parser_stats(queries, args.processed_at)
        for row in queries.get_published_date_ranged_by_processed_at(
            start=args.processed_at.start_timestamp(),
            end=args.processed_at.end_timestamp(),
        ):
            if row["published_date"] is None:
                continue
            run_publication_stats(queries, row["published_date"])
    except:
        logger.error(traceback.format_exc())
        return -1
    finally:
        queries.disconnect()


if __name__ == "__main__":
    sys.exit(main(parse_args()))
