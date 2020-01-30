from dotenv import load_dotenv

load_dotenv()

import os
import pugsql
from runner import runner
import writer
import transform

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


def publications_getter(db, offset=0, limit=1000):
    return db.get_all_publications(limit=limit, offset=offset)


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
            "-f", "--format", choices=["csv", "jsonl"], help="export format: jsonl, csv"
        )
        parser.add_argument("-o", "--output", default="-", help="save to file")
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
        runner(
            from_db=queries,
            getter=publications_getter,
            transformer=transform.publications(fmt=args.format),
            writer=writer.fromformat(
                args.format, filename=args.output, fieldnames=publication_fieldnames
            ),
        )
    else:
        print(f"Unknown command '{args.command}'")
