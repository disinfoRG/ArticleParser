from dotenv import load_dotenv

load_dotenv()

import os
import datetime
import pathlib
import pugsql
from publisher.runner import runner
from publisher import writer
from publisher import transform

queries = pugsql.module("queries/parser")
queries.connect(os.getenv("DB_URL"))

producer_fieldnames = [
    "id",
    "name",
    "canonical_url",
    "classification",
    "languages",
    "licenses",
    "first_seen_at",
    "last_updated_at",
    "followership",
]

publication_fieldnames = [
    "id",
    "producer_id",
    "canonical_url",
    "title",
    "text",
    "language",
    "license",
    "published_at",
    "first_seen_at",
    "last_updated_at",
    "hashtags",
    "urls",
    "keywords",
    "tags",
]


def producers_getter(db, offset=0, limit=1000):
    return db.get_all_producers(offset=offset, limit=limit)


def publications_getter(published_at_range=None):
    def getter(db, offset=0, limit=1000):
        if published_at_range is not None:
            start, end = published_at_range
            return db.get_publications_by_published_at(
                start=start, end=end, limit=limit, offset=offset
            )
        else:
            return db.get_all_publications(limit=limit, offset=offset)

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


if __name__ == "__main__":
    import logging
    import argparse

    logging.basicConfig(level=os.getenv("LOG_LEVEL", default="ERROR"))

    def parse_args():
        parser = argparse.ArgumentParser(
            description="Export datasets from parser database"
        )
        parser.add_argument(
            "command",
            choices=["producers", "publications"],
            help="one of: producers, publications",
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
        return parser.parse_args()

    args = parse_args()

    if args.command == "producers":
        runner(
            from_db=queries,
            getter=producers_getter,
            transformer=transform.producers(fmt=args.format),
            writer=writer.fromformat(
                args.format, filename=args.output, fieldnames=producer_fieldnames
            ),
        )

    elif args.command == "publications":
        if args.group_by == "all":
            runner(
                from_db=queries,
                getter=publications_getter(),
                transformer=transform.publications(fmt=args.format),
                writer=writer.fromformat(
                    args.format, filename=args.output, fieldnames=publication_fieldnames
                ),
            )
        elif args.group_by == "published_day":
            outdir = pathlib.Path(args.output)
            for day in day_range():
                start = day.timestamp()
                end = start + 86400
                runner(
                    from_db=queries,
                    getter=publications_getter(published_at_range=(start, end)),
                    transformer=transform.publications(fmt=args.format),
                    writer=writer.fromformat(
                        args.format,
                        filename=(
                            outdir / (day.strftime("%Y-%m-%d") + f".{args.format}")
                        ),
                        fieldnames=publication_fieldnames,
                    ),
                )
    else:
        print(f"Unknown command '{args.command}'")
