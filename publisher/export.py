from dotenv import load_dotenv

load_dotenv()

import os
import pugsql
import json
import jsonlines
import datetime

queries = pugsql.module("queries/parser")
queries.connect(os.getenv("DB_URL"))

producers_filename = "producers.json"
publications_filename = "publications.jsonl"


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


def transform_producer(producer):
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


def transform_producers(rows):
    for p in rows:
        yield transform_producer(p)


def producers_saver(producers):
    with open(producers_filename, mode="w") as fp:
        json.dump(producers, fp, ensure_ascii=False)


def producers_dumper(producers):
    print(json.dumps(producers, ensure_ascii=False))


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


def transform_publications(rows):
    for p in rows:
        yield transform_publication(p)


def publications_saver(publications):
    with jsonlines.open(publications_filename, mode="a") as writer:
        writer.write_all(publications)


def publications_dumper(publications):
    for p in publications:
        print(json.dumps(p, ensure_ascii=False))


if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) == 1:
        runner(
            from_db=queries,
            getter=producers_getter,
            transformer=transform_producers,
            saver=producers_saver,
        )

        runner(
            from_db=queries,
            getter=publications_getter,
            transformer=transform_publications,
            saver=publications_saver,
        )
    elif sys.argv[1] == "producers":
        runner(
            from_db=queries,
            getter=producers_getter,
            transformer=transform_producers,
            saver=producers_dumper,
        )

    elif sys.argv[1] == "publications":
        runner(
            from_db=queries,
            getter=publications_getter,
            transformer=transform_publications,
            saver=publications_dumper,
        )
    else:
        print(f"Unknown command '{sys.argv}'")
