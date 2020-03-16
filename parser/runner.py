import logging


class DbDataGetter:
    def __init__(self, db, query, **kwargs):
        self.db = db
        self.query = query
        self.kwargs = kwargs

    def items(self, offset, limit):
        return self.query(self.db, offset=offset, limit=limit)


class DataSaver:
    def __init__(self, db, query):
        self.db = db
        self.query = query

    def save(self, item, original):
        self.query(item, original, self.db)


def process_each(incoming, data_saver, transformer):
    try:
        transformed = transformer(incoming)
    except Exception as e:
        logging.error(e)
    else:
        for (item, original) in zip(transformed, incoming):
            try:
                data_saver.save(item, original)
            except Exception as e:
                logging.error(e)


def run_parser(transformer, data_getter, data_saver, paginate_len=1000, limit=10000):
    offset = 0
    while True:
        page_limit = paginate_len if limit - offset > paginate_len else limit - offset
        items = list(data_getter.items(offset, page_limit))
        if len(items) == 0:
            break
        logging.info(f"processing items {offset} to {offset + page_limit}")
        process_each(incoming=items, data_saver=data_saver, transformer=transformer)
        offset += page_limit
        if offset >= limit:
            break
