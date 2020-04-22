#!/usr/bin/env python3

from dotenv import load_dotenv

load_dotenv()
import os
import sys
import datetime
import pathlib
import logging
import argparse
import pugsql
from publisher.runner import runner
from publisher import writer
from publisher import transform

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
queries = pugsql.module("queries")

producer_fieldnames = [
    "id",
    "name",
    "identifiers",
    "classification",
    "url",
    "first_seen_at",
    "last_updated_at",
    "followership",
]

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


def producers_getter(db, offset=0, limit=1000):
    return db.get_producers_in_batch(offset=offset, limit=limit)


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
        "command",
        choices=["producer", "publication", "all"],
        help="data class to publish",
    )
    parser.add_argument(
        "-g",
        "--group-by",
        choices=["published_day", "all"],
        default="all",
        help="criteria on which data in each of the export files is grouped by",
    )
    parser.add_argument(
        "-f", "--format", choices=["csv", "jsonl"], help="export format: jsonl, csv"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="-",
        help="save to file (or directory if group by is not 'all')",
    )
    parser.add_argument("--producer", help="producer id of the publication data")
    parser.add_argument("--full-text", action="store_true", help="publish full text")
    return parser.parse_args()


def main(args):
    queries.connect(os.getenv("DB_URL"))
    try:
        if args.command == "producer":
            runner(
                from_db=queries,
                getter=producers_getter,
                transformer=transform.producers(fmt=args.format),
                writer=writer.fromformat(
                    args.format, filename=args.output, fieldnames=producer_fieldnames
                ),
            )

        elif args.command == "publication":
            if args.group_by == "all":
                runner(
                    from_db=queries,
                    getter=publications_getter(),
                    transformer=transform.publications(
                        fmt=args.format, full_text=args.full_text
                    ),
                    writer=writer.fromformat(
                        args.format,
                        filename=args.output,
                        fieldnames=publication_fieldnames,
                    ),
                )
            elif args.group_by == "published_day":
                outdir = pathlib.Path(args.output)
                pubdate_range = (
                    queries.get_publication_published_at_range_by_producer(
                        producer_id=args.producer
                    )
                    if args.producer
                    else queries.get_publication_published_at_range()
                )
                start = max(
                    datetime.datetime.fromtimestamp(pubdate_range["start"]),
                    datetime.datetime(2018, 1, 1, 0, 0, 0),
                )
                until = datetime.datetime.fromtimestamp(pubdate_range["end"])
                for day in day_range(start=start, until=until):
                    day_start = day.timestamp()
                    logger.info(day_start)
                    day_end = day_start + 86400
                    runner(
                        from_db=queries,
                        getter=publications_getter(
                            producer_id=args.producer,
                            published_at_range=(day_start, day_end),
                        ),
                        transformer=transform.publications(
                            fmt=args.format, full_text=args.full_text
                        ),
                        writer=writer.fromformat(
                            args.format,
                            filename=(
                                outdir / (day.strftime("%Y-%m-%d") + f".{args.format}")
                            ),
                            fieldnames=publication_fieldnames,
                        ),
                    )
        else:
            raise RuntimeError(f"Unknown command '{args.command}'")
    finally:
        queries.disconnect()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args))
