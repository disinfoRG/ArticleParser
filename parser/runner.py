import logging


class DbDataGetter:
    def __init__(self, db, query, **kwargs):
        self.db = db
        self.query = query
        self.kwargs = kwargs

    def items(self, offset, limit):
        return list(self.query(self.db, offset=offset, limit=limit))


def process_each(incoming, to_db, saver, transformer):
    try:
        transformed = transformer(incoming)
    except Exception as e:
        logging.error(e)
    else:
        for (item, original) in zip(transformed, incoming):
            try:
                saver(item, original, to_db)
            except Exception as e:
                logging.error(e)


def run_parser(to_db, saver, transformer, data_getter, paginate_len=100, limit=10000):
    offset = 0
    while True:
        page_limit = paginate_len if limit - offset > paginate_len else limit - offset
        items = data_getter.items(offset, page_limit)
        if len(items) == 0:
            break
        logging.info(f"processing items {offset} to {offset + page_limit}")
        process_each(incoming=items, to_db=to_db, transformer=transformer, saver=saver)
        offset += page_limit
        if offset >= limit:
            break
