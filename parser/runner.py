import logging
import json
import sys
from functools import partial


class DbDataGetter:
    def __init__(self, db, query, **kwargs):
        self.db = db
        if len(kwargs) != 0:
            self.query = partial(query, **kwargs)
        else:
            self.query = query

    def items(self, offset, limit):
        return self.query(self.db, offset=offset, limit=limit)


class DataSaver:
    def __init__(self, db, query, info_interval=1000):
        self.db = db
        self.query = query
        self._info_interval = info_interval
        self._count = 0

    def save(self, item):
        self.query(self.db, item)
        self._count += 1
        if self._count % self._info_interval == 0:
            logging.info(f"save item {self._count}")
            logging.debug(vars(item))


class Item:
    def __init__(self, item, original):
        self.item = item
        self.original = original


class JsonSaver:
    def save(self, item):
        json.dump(vars(item), sys.stdout)


def process_each(items, data_saver, processor):
    for original in items:
        try:
            item = processor(original)
            data_saver.save(Item(item=item, original=original))
        except Exception as e:
            logging.error(e)


def run_parser(processor, data_getter, data_saver, batch_size=1000, limit=10000):
    for offset in range(0, limit, batch_size):
        items = list(data_getter.items(offset, limit))
        if len(items) == 0:
            break
        logging.info(f"processing items {offset} to {offset + len(items)}")
        process_each(items=items, data_saver=data_saver, processor=processor)
