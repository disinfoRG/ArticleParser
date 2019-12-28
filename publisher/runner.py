import logging


def processor(items, write, transformer):
    try:
        transformed = transformer(items)
    except Exception as e:
        logging.error(e)
    else:
        try:
            write(list(transformed))
        except Exception as e:
            logging.error(e)


def runner(from_db, getter, writer, transformer, paginate_len=100):
    offset, limit = 0, paginate_len
    writer.open()
    while True:
        items = list(getter(from_db, offset=offset, limit=limit))
        if len(items) == 0:
            break
        logging.debug(f"processing items {offset} to {offset + limit}")
        processor(items=items, write=writer.write, transformer=transformer)
        offset += limit
    writer.close()
