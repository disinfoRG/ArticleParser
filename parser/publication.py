from bs4 import BeautifulSoup
from readability import Document
import datetime
import json
import dateparser
import extruct

import logging
import readability
from parser.gatrack import parse_ga_id
import parser.ptt
from . import version

name = "parser.publication"

logger = logging.getLogger(__name__)
readability.readability.log.setLevel(logging.ERROR)


def snapshots_getter_by_article_id(scraper_db, article_id, offset=0, limit=1000):
    return scraper_db.get_article_snapshots_by_article_id(
        offset=offset, limit=limit, article_ids=[article_id]
    )


def snapshots_getter_by_url(scraper_db, url, offset=0, limit=1000):
    return scraper_db.get_article_snapshots_by_url(offset=offset, limit=limit, url=url)


def snapshots_getter(scraper_db, parser_db, offset=0, limit=100):
    info = json.loads(parser_db.get_parser_info(parser_name=name)["info"])
    later_than = (
        info["last_processed_snapshot_at"]
        if "last_processed_snapshot_at" in info
        else 0
    )

    return scraper_db.get_all_article_snapshots(
        offset=offset, limit=limit, later_than=later_than
    )


def snapshots_getter_by_parser_version(
    scraper_db, parser_db, version, offset=0, limit=1000
):
    pubs = parser_db.get_publications_by_parser_version(
        version=version, offset=0, limit=1000
    )
    ids = list(set([p["article_id"] for p in pubs]))

    return scraper_db.get_article_snapshots_by_article_id(
        offset=offset, limit=limit, article_ids=ids
    )


def parse_meta_tags(body):
    meta_property = {
        x["property"]: x["content"]
        for x in body.find_all(
            lambda tag: tag.name == "meta"
            and "property" in tag.attrs.keys()
            and "content" in tag.attrs.keys()
        )
    }
    meta_name = {
        x["name"]: x["content"]
        for x in body.find_all(
            lambda tag: tag.name == "meta"
            and "name" in tag.attrs.keys()
            and "content" in tag.attrs.keys()
        )
    }
    meta_itemprop = {
        x["itemprop"]: x["content"]
        for x in body.find_all(
            lambda tag: tag.name == "meta"
            and "itemprop" in tag.attrs.keys()
            and "content" in tag.attrs.keys()
        )
    }
    return {**meta_property, **meta_name, **meta_itemprop}


def parse_metadata(body):
    return extruct.extract(str(body))


def parse_external_links(soups):
    return [x["href"] for x in soups["summary"].find_all("a", href=lambda x: x)]


def parse_image_links(soups):
    return [
        x.get("data-src", x.get("src", x.get("data-original", "")))
        for x in soups["summary"].find_all("img")
    ]


def parse_text(soups):
    return " ".join([" ".join(x.text.split()) for x in soups["summary"].find_all("p")])


def parse_title(soups):
    return soups["doc"].title()


def parse_published_at(soups):
    published_at = None
    jsonld = soups["metadata"]["json-ld"]
    meta = soups["meta-tags"]

    def parse_published_at(jsonld):
        if "@type" in jsonld and (
            jsonld["@type"] in ["NewsArticle", "Article", "BlogPosting", "WebPage"]
        ):
            if "datePublished" in jsonld:
                d = dateparser.parse(jsonld["datePublished"])
                return d.timestamp() if d is not None else None
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
    elif "article:published_time" in meta:
        d = dateparser.parse(meta["article:published_time"])
        published_at = d.timestamp() if d is not None else None

    return published_at


def parse_soups(snapshot):
    doc = Document(snapshot["raw_data"])
    body = BeautifulSoup(snapshot["raw_data"], "html.parser")
    summary = BeautifulSoup(doc.summary(), "html.parser")
    metatags = parse_meta_tags(body)
    metadata = parse_metadata(body)
    return {
        "doc": doc,
        "body": body,
        "summary": summary,
        "meta-tags": metatags,
        "metadata": metadata,
        "snapshot": snapshot,
    }


def process(snapshot):
    soups = parse_soups(snapshot)
    if soups["snapshot"]["article_type"] == "PTT":
        return parser.ptt.parse_publication(soups)
    else:
        ga_id = parse_ga_id(soups)
        title = parse_title(soups)
        text = parse_text(soups)
        external_links = parse_external_links(soups)
        image_links = parse_image_links(soups)
        published_at = parse_published_at(soups)
        return {
            "publication_id": soups["snapshot"]["article_id"],
            "producer_id": soups["snapshot"]["site_id"],
            "canonical_url": soups["snapshot"]["url"],
            "published_at": published_at,
            "first_seen_at": soups["snapshot"]["first_seen_at"],
            "last_updated_at": soups["snapshot"]["last_updated_at"],
            "title": title,
            "publication_text": text,
            "urls": external_links,
            "image_urls": image_links,
            "hashtags": [],
            "keywords": [],
            "tags": [],
            "metadata": {
                "meta-tags": soups["meta-tags"],
                **soups["metadata"],
                "ga-id": ga_id,
            },
            "comments": [],
        }


def save_ga_id(parser_db, item):
    publication = item.item
    if "ga-id" in publication["metadata"] and len(publication["metadata"]["ga-id"]) > 0:
        ga_id = publication["metadata"]["ga-id"]
        producer = parser_db.get_producer_by_id(producer_id=publication["producer_id"])
        identifiers = json.loads(producer["identifiers"])
        if "ga-id" not in identifiers:
            logger.debug(f"add ga-id to producer {publication['producer_id']}")
            parser_db.update_producer_identifiers(
                producer_id=publication["producer_id"],
                identifiers=json.dumps({**identifiers, "ga-id": ga_id}),
            )
        else:
            if not set(ga_id) <= set(identifiers["ga-id"]):
                logger.debug(f"add ga-id to producer {publication['producer_id']}")
                parser_db.update_producer_identifiers(
                    producer_id=publication["producer_id"],
                    identifiers=json.dumps(
                        {
                            **identifiers,
                            "ga-id": list(set(ga_id + identifiers["ga-id"])),
                        }
                    ),
                )


def saver(parser_db, item):
    publication, article_snapshot = item.item, item.original
    with parser_db.transaction():
        publication_id = parser_db.upsert_publication(
            {
                **publication,
                **{
                    k: json.dumps(publication[k])
                    for k in [
                        "urls",
                        "image_urls",
                        "hashtags",
                        "keywords",
                        "tags",
                        "metadata",
                        "comments",
                    ]
                    if k in publication
                },
            }
        )
        parser_db.upsert_publication_mapping(
            article_id=article_snapshot["article_id"],
            snapshot_at=article_snapshot["snapshot_at"],
            publication_id=publication_id,
            info=json.dumps(
                {
                    "last_processed_at": int(datetime.datetime.now().timestamp()),
                    "parser": {"name": name, "version": version},
                }
            ),
        )
        parser_db.update_parser_last_processed(
            parser_name=name,
            last_processed_article_id=article_snapshot["article_id"],
            last_processed_snapshot_at=article_snapshot["snapshot_at"],
        )
        save_ga_id(parser_db, item)


def update_parser_info(db):
    db.insert_ignore_parser_info(parser_name=name, info="{}")
