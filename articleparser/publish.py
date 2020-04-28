import sys
import json
import datetime
from .db import to_producer, to_publication


def process_producer_item(row):
    producer = to_producer(row)
    producer_id = str(producer.pop("producer_id"))
    del producer["scraper_id"]
    del producer["site_id"]
    data = producer.pop("data")
    return {
        **producer,
        "producer_id": producer_id,
        **data,
        **{
            col: producer[col].isoformat()
            for col in ["first_seen_at", "last_updated_at"]
            if producer[col]
        },
    }


def process_publication_item(row, full_text=False):
    publication = to_publication(row)
    publication_id = str(publication.pop("publication_id"))
    producer_id = str(publication.pop("producer_id"))
    text = publication.pop("publication_text")
    if not full_text:
        text = text[:280]
    data = publication.pop("data")
    return {
        **publication,
        "id": publication_id,
        "producer_id": producer_id,
        "text": text,
        **data,
        **{
            col: publication[col].isoformat()
            for col in ["published_at", "first_seen_at", "last_updated_at"]
            if publication[col]
        },
    }


class JsonItemSaver:
    def __init__(self, filename=None):
        self.filename = filename
        self.fh = None

    def save(self, item):
        if not self.fh:
            if self.filename:
                self.fh = open(self.filename, "w")
            else:
                self.fh = sys.stdout
        json.dump(item.item, self.fh, ensure_ascii=False)
        self.fh.write("\n")

    def close(self):
        if self.fh:
            self.fh.close()
