import logging
import traceback

logger = logging.getLogger(__name__)


def processor(items, write, transformer):
    try:
        transformed = transformer(items)
    except Exception as e:
        logger.error(traceback.format_exc())
    else:
        try:
            write(list(transformed))
        except Exception as e:
            logger.error(traceback.format_exc())


def runner(from_db, getter, writer, transformer, batch_size=100):
    offset, limit = 0, batch_size
    while True:
        items = list(getter(from_db, offset=offset, limit=limit))
        if len(items) == 0:
            break
        writer.open()
        logger.debug("Processing items %d to %d.", offset, offset + limit)
        processor(items=items, write=writer.write, transformer=transformer)
        offset += limit
    writer.close()
