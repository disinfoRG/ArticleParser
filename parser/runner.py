import logging


def processor(items, to_db, saver, transformer):
    try:
        transformed = transformer(items)
    except Exception as e:
        logging.error(e)
    else:
        for (item, original) in zip(transformed, items):
            try:
                saver(item, original, to_db)
            except Exception as e:
                logging.error(e)


def run_parser(from_db, to_db, getter, saver, transformer, paginate_len=100):
    offset, limit = 0, paginate_len
    while True:
        items = list(getter(from_db, offset=offset, limit=limit))
        if len(items) == 0:
            break
        logging.info(f"processing items {offset} to {offset + limit}")
        processor(items=items, to_db=to_db, transformer=transformer, saver=saver)
        offset += limit
