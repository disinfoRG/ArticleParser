import logging
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
    def __init__(self, db, query):
        self.db = db
        self.query = query

    def save(self, item):
        self.query(item, self.db)


class Item:
    def __init__(self, item, original):
        self.item = item
        self.original = original


def process_each(items, data_saver, transformer):
    try:
        transformed = transformer(items)
    except Exception as e:
        logging.error(e)
    else:
        for (t, original) in zip(transformed, items):
            item = Item(item=t, original=original)
            try:
                data_saver.save(item)
            except Exception as e:
                logging.error(e)


def run_parser(transformer, data_getter, data_saver, batch_size=1000, limit=10000):
    for offset in range(0, limit, batch_size):
        items = list(data_getter.items(offset, limit))
        if len(items) == 0:
            break
        logging.info(f"processing items {offset} to {offset + len(items)}")
        process_each(items=items, data_saver=data_saver, transformer=transformer)
