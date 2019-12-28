from dotenv import load_dotenv

load_dotenv()

import os
import pugsql
import json
import jsonlines
import csv
import sys
import datetime
from runner import processor, runner
import writer

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
    "posted_at",
    "first_seen_at",
    "last_updated_at",
    "hashtags",
    "urls",
    "keywords",
    "tags",
]


def producers_getter(db, offset=0, limit=1000):
    return db.get_all_producers(offset=offset, limit=limit)


def transform_producer_json(producer):
    producer["id"] = producer.pop("producer_id")
    for json_col in ["languages", "licenses", "followership"]:
        producer.update({json_col: json.loads(producer[json_col])})
    for datetime_col in ["first_seen_at", "last_updated_at"]:
        producer.update(
            {
                datetime_col: datetime.datetime.fromtimestamp(
                    producer[datetime_col]
                ).isoformat()
                if producer[datetime_col]
                else None
            }
        )
    return producer


def transform_producer_csv(producer):
    producer = transform_producer_json(producer)
    for list_col in ["languages", "licenses"]:
        producer.update({list_col: ", ".join(producer[list_col])})
    for dict_col in ["followership"]:
        producer.update(
            {
                dict_col: ", ".join(
                    [f"{key}: {value}" for key, value in producer[dict_col]]
                )
            }
        )
    return producer


def transform_producers(format="jsonl"):
    def transformer(rows):
        if format == "jsonl":
            for p in rows:
                yield transform_producer_json(p)
        elif format == "csv":
            for p in rows:
                yield transform_producer_csv(p)

    return transformer


def publications_getter(db, offset=0, limit=1000):
    return db.get_all_publications(limit=limit, offset=offset)


def transform_publication(publication):
    publication["id"] = publication.pop("publication_id")
    publication["text"] = publication.pop("publication_text")
    for col in ["hashtags", "urls", "keywords", "tags"]:
        if publication[col] is not None:
            publication.update({col: json.loads(publication[col])})
    for datetime_col in ["posted_at", "first_seen_at", "last_updated_at"]:
        if publication[datetime_col] is not None:
            publication.update(
                {
                    datetime_col: datetime.datetime.fromtimestamp(
                        publication[datetime_col]
                    ).isoformat()
                }
            )
    return publication


def transform_publications(format="jsonl"):
    def transformer(rows):
        for p in rows:
            yield transform_publication(p)

    return transformer


if __name__ == "__main__":
    import logging
    import argparse

    logging.basicConfig(level=logging.DEBUG)

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
            transformer=transform_producers(format=args.format),
            writer=writer.fromformat(
                args.format, filename=args.output, fieldnames=producer_fieldnames
            ),
        )

    elif args.command == "publications":
        runner(
            from_db=queries,
            getter=publications_getter,
            transformer=transform_publications(format=args.format),
            writer=writer.fromformat(
                args.format, filename=args.output, fieldnames=publication_fieldnames
            ),
        )
    else:
        print(f"Unknown command '{args.command}'")
