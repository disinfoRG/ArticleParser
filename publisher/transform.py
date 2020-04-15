import json
import datetime


def transform_producer_json(producer):
    producer["id"] = producer.pop("producer_id")
    for json_col in ["languages", "licenses", "followership", "identifiers"]:
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


def producers(fmt="jsonl"):
    def transformer(rows):
        if fmt == "jsonl":
            for p in rows:
                yield transform_producer_json(p)
        elif fmt == "csv":
            raise RuntimeError("Not implemented")

    return transformer


def transform_publication(publication, full_text=False):
    publication["id"] = publication.pop("publication_id")
    publication["text"] = publication.pop("publication_text")
    del publication["tags"]
    if not full_text:
        publication["text"] = publication["text"][:280]
    del publication["metadata"]
    for col in ["hashtags", "urls", "keywords", "comments"]:
        if publication[col] is not None:
            publication.update({col: json.loads(publication[col])})
    for datetime_col in ["published_at", "first_seen_at", "last_updated_at"]:
        if datetime_col in publication and publication[datetime_col] is not None:
            publication.update(
                {
                    datetime_col: datetime.datetime.fromtimestamp(
                        publication[datetime_col]
                    ).isoformat()
                }
            )
    return publication


def publications(fmt="jsonl", full_text=False):
    if fmt == "jsonl":

        def transformer(rows):
            for p in rows:
                yield transform_publication(p, full_text=full_text)

        return transformer
    else:
        raise RuntimeError("Not implemented")
