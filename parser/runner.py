import logging
import json
import sys
from functools import partial
import traceback


logger = logging.getLogger(__name__)


class DbGetter:
    def __init__(self, db, query, **kwargs):
        self.db = db
        if len(kwargs) != 0:
            self.query = partial(query, **kwargs)
        else:
            self.query = query

    def batches(self, batch_size=1000, limit=10000):
        for offset in range(0, limit, batch_size):
            yield self.query(
                self.db,
                offset=offset,
                limit=batch_size if offset + batch_size < limit else limit - offset,
            )


class DbSaver:
    def __init__(self, db, query, log_interval=1000):
        self.db = db
        self.query = query
        self.log_interval = log_interval
        self.count = 0

    def save(self, item):
        self.query(self.db, item)
        self.count += 1
        if self.count % self.log_interval == 0:
            logger.info("Save item %d.", self.count)


class Item:
    def __init__(self, item, original):
        self.item = item
        self.original = original


class JsonSaver:
    def save(self, item):
        json.dump(vars(item), sys.stdout, ensure_ascii=False)


def process_items(items, processor, data_saver):
    count = 0
    for original in items:
        try:
            item = processor(original)
            data_saver.save(Item(item=item, original=dict(original)))
            count += 1
        except Exception as e:
            logger.error("Error processing item %d:", original["article_id"])
            logger.error(traceback.format_exc())
    return count


def run_parser(data_getter, processor, data_saver, batch_size=1000, limit=10000):
    for i, batch in enumerate(data_getter.batches(limit=limit, batch_size=batch_size)):
        batch = list(batch)
        if len(batch) == 0:
            break
        count = process_items(items=batch, processor=processor, data_saver=data_saver)
        logger.info("Processed %d items starting from item %d.", count, i * batch_size)
