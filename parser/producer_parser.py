from dotenv import load_dotenv

load_dotenv()

import json

name = "producer_parser"
version = "1.0.0"


def transform_site(site):
    return {
        "producer_id": site["site_id"],
        "name": site["name"],
        "classification": site["type"],
        "canonical_url": site["url"],
        "languages": json.dumps([]),
        "licenses": json.dumps([]),
        "followership": json.dumps({}),
    }


def transformer(sites):
    for site in sites:
        yield transform_site(site)


def sites_getter(scrapper_db, offset=0, limit=1000):
    return scrapper_db.get_all_sites(offset=offset, limit=limit)


def producer_saver(producer, to_db):
    return to_db.upsert_producer(producer)


if __name__ == "__main__":
    from runner import run_parser
    import os
    import pugsql
    import logging

    logging.basicConfig(level=logging.ERROR)

    scrapper_db = pugsql.module("queries/scrapper")
    scrapper_db.connect(os.getenv("SCRAPPER_DB_URL"))
    parser_db = pugsql.module("queries/parser")
    parser_db.connect(os.getenv("DB_URL"))

    run_parser(
        from_db=scrapper_db,
        to_db=parser_db,
        getter=sites_getter,
        saver=producer_saver,
        transformer=transformer,
    )
