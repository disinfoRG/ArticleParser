from dotenv import load_dotenv

load_dotenv()

from bs4 import BeautifulSoup
from readability import Document
import json

import logging
import readability

readability.readability.log.setLevel(logging.ERROR)


def snapshots_getter(scrapper_db, offset=0, limit=1000):
    return scrapper_db.get_all_article_snapshots(offset=offset, limit=limit)


def transform_snapshot(sn):
    doc = Document(sn["raw_data"])

    try:
        # title
        title = doc.title()

        # main body
        s = doc.summary()
        soup = BeautifulSoup(s, "html.parser")

        # date - not 100% accurate
        # guess_date = htmldate.find_date(self.raw_data)

        # article text
        text = "\n".join([" ".join(x.text.split()) for x in soup.find_all("p")])

        # links
        external_links = [x["href"] for x in soup.find_all("a", href=lambda x: x)]
        image_links = [x["data-src"] if "data-src" in x else x["src"] for x in soup.find_all("img")]

        return {
            "publication_id": sn["article_id"],
            "producer_id": sn["site_id"],
            "canonical_url": sn["url"],
            "first_seen_at": sn["first_seen_at"],
            "last_updated_at": sn["last_updated_at"],
            "title": title,
            "publication_text": text,
            "urls": json.dumps(external_links),
            "image_urls": json.dumps(image_links),
            "hashtags": "[]",
            "keywords": "[]",
            "tags": "[]",
        }
    except Exception as e:
        logging.error(e)


def transformer(snapshots):
    for snapshot in snapshots:
        logging.debug(f"transform snapshot {snapshot['article_id']}")
        yield transform_snapshot(snapshot)


def saver():
    save_log_period = 1000
    save_count = 0

    def publication_saver(publication, parser_db):
        nonlocal save_count
        nonlocal save_log_period
        if save_count == save_log_period:
            logging.info(f"save publication {publication['publication_id']}")
            save_count = 0
        parser_db.upsert_publication(publication)
        save_count = save_count + 1

    return publication_saver


if __name__ == "__main__":
    from runner import run_parser
    import os
    import pugsql
    import logging

    logging.basicConfig(level=os.getenv("LOG_LEVEL", default="ERROR"))

    scrapper_db = pugsql.module("queries/scrapper")
    scrapper_db.connect(os.getenv("SCRAPPER_DB_URL"))
    parser_db = pugsql.module("queries/parser")
    parser_db.connect(os.getenv("DB_URL"))

    run_parser(
        from_db=scrapper_db,
        to_db=parser_db,
        getter=snapshots_getter,
        saver=saver(),
        transformer=transformer,
        paginate_len=1000,
    )
