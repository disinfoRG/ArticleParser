from dotenv import load_dotenv

load_dotenv()

import os
import pugsql
import json
import jsonlines
import csv
import sys
import datetime

queries = pugsql.module("queries/parser")
queries.connect(os.getenv("DB_URL"))


def processor(items, saver, transformer):
    try:
        transformed = transformer(items)
    except Exception as e:
        logging.error(e)
    else:
        try:
            saver(list(transformed))
        except Exception as e:
            logging.error(e)


def runner(from_db, getter, saver, transformer, paginate_len=100):
    offset, limit = 0, paginate_len
    while True:
        items = list(getter(from_db, offset=offset, limit=limit))
        if len(items) == 0:
            break
        logging.debug(f"processing items {offset} to {offset + limit}")
        processor(items=items, saver=saver, transformer=transformer)
        offset += limit


def rename_col(d, oldname, newname):
    try:
        d[newname] = d[oldname]
        del d[oldname]
        return d
    except Exception as e:
        print(f"Cannot rename column '{oldname}' to '{newname}': {d}")


def producers_getter(db, offset=0, limit=1000):
    return db.get_all_producers(offset=offset, limit=limit)


def transform_producer_json(producer):
    rename_col(producer, "producer_id", "id")
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


def transform_producers(format="json"):
    def transformer(rows):
        if format == "json":
            for p in rows:
                yield transform_producer_json(p)
        elif format == "csv":
            for p in rows:
                yield transform_producer_csv(p)

    return transformer


def producers_saver(filename, format="json"):
    def saver(producers):
        with open(filename, mode="w") as fp:
            if format == "json":
                json.dump(producers, fp, ensure_ascii=False)
            elif format == "csv":
                producers_saver_csv(producers, fp)

    return saver


def producers_saver_csv(producers, fp):
    fieldnames = [
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
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()
    for p in producers:
        writer.writerow(p)


def producers_dumper(format="json"):
    def dumper_csv(producers):
        producers_saver_csv(producers, sys.stdout)

    def dumper_json(producers):
        print(json.dumps(producers, ensure_ascii=False))

    return dumper_json if format == "json" else dumper_csv


def publications_getter(db, offset=0, limit=1000):
    return db.get_all_publications(limit=limit, offset=offset)


def transform_publication(publication):
    rename_col(publication, "publication_id", "id")
    rename_col(publication, "publication_text", "text")
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


def transform_publications(format="json"):
    def transformer(rows):
        for p in rows:
            yield transform_publication(p)

    return transformer


def publications_saver(filename, format="json"):
    def saver(publications):
        if format == "json":
            with jsonlines.open(filename, mode="a") as writer:
                writer.write_all(publications)
        elif format == "csv":
            publications_saver_csv(publications, fp)

    return saver


def publications_saver_csv(publications, fp):
    fieldnames = [
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
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()
    for p in publications:
        writer.writerow(p)


def publications_dumper(format="json"):
    def dumper_csv(publications):
        publications_saver_csv(publications, sys.stdout)

    def dumper_json(publications):
        for p in publications:
            print(json.dumps(p, ensure_ascii=False))

    return dumper_json if format == "json" else dumper_csv


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
            "-f",
            "--format",
            choices=["csv", "json"],
            help="export format: json (jsonl), csv",
        )
        parser.add_argument("-o", "--output", help="save to file")
        return parser.parse_args()

    args = parse_args()

    if args.command == "producers":
        runner(
            from_db=queries,
            getter=producers_getter,
            transformer=transform_producers(format=args.format),
            saver=producers_dumper(format=args.format)
            if args.output is None
            else producers_saver(filename=args.output, format=args.format),
        )

    elif args.command == "publications":
        runner(
            from_db=queries,
            getter=publications_getter,
            transformer=transform_publications(format=args.format),
            saver=publications_dumper(format=args.format)
            if args.output is None
            else publications_saver(filename=args.output, format=args.format),
        )
    else:
        print(f"Unknown command '{args.command}'")
