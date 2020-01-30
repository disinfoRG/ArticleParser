import json
import datetime


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


def producers(fmt="jsonl"):
    def transformer(rows):
        if fmt == "jsonl":
            for p in rows:
                yield transform_producer_json(p)
        elif fmt == "csv":
            for p in rows:
                yield transform_producer_csv(p)

    return transformer


def transform_publication(publication):
    publication["id"] = publication.pop("publication_id")
    publication["text"] = publication.pop("publication_text")
    del publication["metadata"]
    for col in ["hashtags", "urls", "keywords", "tags"]:
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


def publications(fmt="jsonl"):
    def transformer(rows):
        for p in rows:
            yield transform_publication(p)

    return transformer
