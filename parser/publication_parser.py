from dotenv import load_dotenv

load_dotenv()

from bs4 import BeautifulSoup
from readability import Document
import json

import logging
import readability
import datetime

readability.readability.log.setLevel(logging.ERROR)


def snapshots_getter(scrapper_db, offset=0, limit=1000):
    return scrapper_db.get_all_article_snapshots(offset=offset, limit=limit)


def transform_snapshot(sn):
    doc = Document(sn["raw_data"])

    try:
        title = doc.title()

        # main body
        s = doc.summary()
        soup = BeautifulSoup(s, "html.parser")

        # date - not 100% accurate
        # guess_date = htmldate.find_date(self.raw_data)

        # article text
        text = "\n".join([" ".join(x.text.split()) for x in soup.find_all("p")])

        # meta tag
        soup = BeautifulSoup(sn["raw_data"], "html.parser")
        # meta property
        meta_property = {
            x["property"]: x["content"]
            for x in soup.find_all(
                lambda tag: tag.name == "meta"
                and "property" in tag.attrs.keys()
                and "content" in tag.attrs.keys()
            )
        }
        meta_name = {
            x["name"]: x["content"]
            for x in soup.find_all(
                lambda tag: tag.name == "meta"
                and "name" in tag.attrs.keys()
                and "content" in tag.attrs.keys()
            )
        }
        meta_itemprop = {
            x["itemprop"]: x["content"]
            for x in soup.find_all(
                lambda tag: tag.name == "meta"
                and "itemprop" in tag.attrs.keys()
                and "content" in tag.attrs.keys()
            )
        }

        # json ld
        try:
            jsonld = json.loads(
                soup.find("script", {"type": "application/ld+json"}).text
            )
        except AttributeError:
            jsonld = {}

        # content
        doc = Document(sn["raw_data"])
        # title
        title = doc.title()

        # main body
        s = doc.summary()
        soup = BeautifulSoup(s, "html.parser")

        # article text
        text = " ".join([" ".join(x.text.split()) for x in soup.find_all("p")])

        # links
        external_links = [x["href"] for x in soup.find_all("a", href=lambda x: x)]
        image_links = [
            x.get("data-src", x.get("src", x.get("data-original", "")))
            for x in soup.find_all("img")
        ]

        published_at = None

        def parse_published_at(jsonld):
            if "@type" in jsonld and (
                jsonld["@type"] == "NewsArticle" or jsonld["@type"] == "Article"
            ):
                if "datePublished" in jsonld:
                    return datetime.datetime.fromisoformat(
                        jsonld["datePublished"]
                    ).timestamp()
            return None

        def lookup_published_at(items):
            for item in items:
                r = parse_published_at(item)
                if r is not None:
                    return r

        if isinstance(jsonld, list):
            published_at = lookup_published_at(jsonld)
        elif "@type" in jsonld:
            published_at = parse_published_at(jsonld)
        elif "@graph" in jsonld:
            published_at = lookup_published_at(jsonld["@graph"])

        return {
            "publication_id": sn["article_id"],
            "producer_id": sn["site_id"],
            "canonical_url": sn["url"],
            "published_at": published_at,
            "first_seen_at": sn["first_seen_at"],
            "last_updated_at": sn["last_updated_at"],
            "title": title,
            "publication_text": text,
            "urls": json.dumps(external_links),
            "image_urls": json.dumps(image_links),
            "hashtags": "[]",
            "keywords": "[]",
            "tags": "[]",
            "metadata": json.dumps(
                {
                    "meta": {**meta_itemprop, **meta_property, **meta_name},
                    "json-ld": jsonld,
                }
            ),
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
