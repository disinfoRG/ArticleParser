from bs4 import BeautifulSoup
from readability import Document
import datetime
import json
import uuid
import dateparser
import extruct
import re

import logging
import readability
from parser.gatrack import parse_ga_id
import parser.ptt
import parser.scraper as scraper
from . import version

name = "parser.publication"

logger = logging.getLogger(__name__)
readability.readability.log.setLevel(logging.ERROR)


def snapshots_getter_by_article_id(scraper_db, article_id, offset=0, limit=1000):
    return scraper.get_snapshots(
        scraper_db, article_id=article_id, offset=offset, limit=limit
    )


def snapshots_getter_by_url(scraper_db, url, offset=0, limit=1000):
    return scraper.get_snapshots(scraper_db, url=url, offset=offset, limit=limit)


def snapshots_getter(scraper_db, parser_db, offset=0, limit=100):
    info = json.loads(parser_db.get_parser_info(parser_name=name)["info"])
    later_than = (
        info["last_processed_snapshot_at"]
        if "last_processed_snapshot_at" in info
        else 0
    )

    return scraper.get_snapshots(
        scraper_db, snapshot_at_later_than=later_than, offset=offset, limit=limit
    )


def snapshots_getter_by_parser_version(parser_db, version, site_id=None):
    if site_id is None:
        pubs = parser_db.get_publications_by_parser_version(version=version)
    else:
        pubs = parser_db.get_publications_by_parser_version_by_producer(
            producer_id=site_id, version=version
        )
    ids = [(p["article_id"], p["snapshot_at"]) for p in pubs]

    def get_snapshots(scraper_db, parser_db, offset=0, limit=1000):
        batch = []
        while len(ids) > 0:
            article_id, snapshot_at = ids.pop(0)
            s = scraper.get_snapshot(
                scraper_db, article_id=article_id, snapshot_at=snapshot_at
            )
            if s is not None:
                batch.append(s)
            if len(batch) == limit:
                return batch
        return batch

    return get_snapshots


def snapshots_getter_by_site(scraper_db, site_id, offset=0, limit=1000):
    return scraper.get_snapshots(
        scraper_db, site_id=site_id, offset=offset, limit=limit
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


def parse_metadata(raw_data):
    return extruct.extract(raw_data)


def parse_external_links(soups):
    return [
        x["href"]
        for x in soups["summary"].find_all("a", href=lambda x: x)
        if x["href"] != soups["snapshot"]["url"]
    ]


def parse_image_links(soups):
    return [
        x.get("data-src", x.get("src", x.get("data-original", "")))
        for x in soups["summary"].find_all("img")
    ]


def parse_text(soups):
    return " ".join([" ".join(x.text.split()) for x in soups["summary"].find_all("p")])


def parse_title(soups):
    return soups["doc"].title()


def parse_published_at_from_jsonld(jsonld):
    def parse_(jsonld):
        if "@type" in jsonld and (
            jsonld["@type"]
            in [
                "NewsArticle",
                "Article",
                "BlogPosting",
                "SocialMediaPosting",
                "WebPage",
            ]
        ):
            if "datePublished" in jsonld:
                return dateparser.parse(jsonld["datePublished"])
        if "pubDate" in jsonld:
            return dateparser.parse(jsonld["pubDate"])
        return None

    for item in jsonld:
        r = parse_(item)
        if r is not None:
            return r
    return None


def parse_published_at_from_microdata(microdata):
    def parse_(microdata):
        if "type" in microdata and (
            microdata["type"]
            in [
                f"http://schema.org/{c}"
                for c in [
                    "NewsArticle",
                    "Article",
                    "BlogPosting",
                    "SocialMediaPosting",
                    "WebPage",
                ]
            ]
        ):
            for prop in ["datePublished", "dateModified"]:
                if prop in microdata["properties"]:
                    return dateparser.parse(microdata["properties"][prop])
        return None

    for item in microdata:
        r = parse_(item)
        if r is not None:
            return r
    return None


def parse_published_at_from_rdfa(rdfa):
    def parse_(rdfa):
        if "article:published_time" in rdfa:
            for item in rdfa["article:published_time"]:
                if "@value" in item:
                    return dateparser.parse(item["@value"])
        return None

    for item in rdfa:
        r = parse_(item)
        if r is not None:
            return r
    return None


def parse_published_at_from_opengraph(og):
    def parse_(og):
        for prop in og["properties"]:
            if prop[0] == "article:published_time":
                return dateparser.parse(prop[1])
        return None

    for item in og:
        r = parse_(item)
        if r is not None:
            return r
    return None


def parse_published_at_from_text(soups):
    dt_pat = re.compile("(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
    m = dt_pat.match(str(soups["body"]))
    if m is not None:
        return dateparser.parse(m.group(1))
    return None


def parse_published_at_from_meta_tags(soups):
    for tag_name in [
        "article:published_time",
        "datePublished",
        "publishdate",
        "pubdate",
    ]:
        if tag_name in soups["meta-tags"]:
            d = dateparser.parse(soups["meta-tags"][tag_name])
            if d is not None:
                return d
    return None


def parse_published_at(soups):
    published_at = None

    d = parse_published_at_from_meta_tags(soups)
    if d is not None:
        return d.timestamp()

    d = parse_published_at_from_jsonld(soups["metadata"]["json-ld"])
    if d is not None:
        return d.timestamp()

    d = parse_published_at_from_rdfa(soups["metadata"]["rdfa"])
    if d is not None:
        return d.timestamp()

    d = parse_published_at_from_microdata(soups["metadata"]["microdata"])
    if d is not None:
        return d.timestamp()

    d = parse_published_at_from_opengraph(soups["metadata"]["opengraph"])
    if d is not None:
        return d.timestamp()

    d = parse_published_at_from_text(soups)
    if d is not None:
        published_at = d.timestamp()

    ## <https://www.chinapress.com.my/>
    tags = soups["body"].find_all(id="article_datetime")
    if len(tags) > 0:
        d = dateparser.parse(tags[0].get_text())
        if d is not None:
            published_at = d.timestamp()

    return published_at


def parse_soups(snapshot):
    doc = Document(snapshot["raw_data"])
    body = BeautifulSoup(snapshot["raw_data"], "html.parser")
    summary = BeautifulSoup(doc.summary(), "html.parser")
    metatags = parse_meta_tags(body)
    metadata = parse_metadata(snapshot["raw_data"])
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
            "version": soups["snapshot"]["snapshot_at"],
            "site_id": soups["snapshot"]["site_id"],
            "canonical_url": soups["snapshot"]["url"],
            "published_at": published_at,
            "first_seen_at": soups["snapshot"]["first_seen_at"],
            "last_updated_at": soups["snapshot"]["last_updated_at"],
            "title": title,
            "publication_text": text,
            "author": None,
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
            "connect_from": None,
        }


def save_ga_id(parser_db, publication):
    if "ga-id" in publication["metadata"] and len(publication["metadata"]["ga-id"]) > 0:
        ga_id = publication["metadata"]["ga-id"]
        producer = parser_db.get_producer(producer_id=publication["producer_id"])
        identifiers = json.loads(producer["identifiers"])
        if "ga-id" not in identifiers:
            logger.debug("Add ga-id to producer %s.", publication["producer_id"])
            parser_db.update_producer_identifiers(
                producer_id=publication["producer_id"],
                identifiers=json.dumps({**identifiers, "ga-id": ga_id}),
            )
        else:
            if not set(ga_id) <= set(identifiers["ga-id"]):
                logger.debug("Add ga-id to producer %s.", publication["producer_id"])
                parser_db.update_producer_identifiers(
                    producer_id=publication["producer_id"],
                    identifiers=json.dumps(
                        {
                            **identifiers,
                            "ga-id": list(set(ga_id + identifiers["ga-id"])),
                        }
                    ),
                )


def save_producer_active_dates(parser_db, publication):
    if publication["published_at"] is not None:
        logger.debug("Set active dates for %s.", publication["producer_id"])
        parser_db.update_producer_active_dates(
            producer_id=publication["producer_id"],
            published_at=publication["published_at"],
        )


def is_updated(exist_pub, new_pub):
    for field in [
        "title",
        "publication_text",
        "published_at",
        "comments",
        "hashtags",
        "urls",
        "keywords",
        "tags",
        "metadata",
        "author",
        "connect_from",
    ]:
        if exist_pub[field] != new_pub[field]:
            return True
    return False


def to_publication(row):
    return {
        **row,
        **{
            field: json.loads(row[field])
            for field in [
                "urls",
                "hashtags",
                "keywords",
                "tags",
                "metadata",
                "comments",
            ]
            if row[field]
        },
    }


def is_new_version(existing, publication):
    for old_version in existing:
        old_version = to_publication(old_version)
        if not is_updated(old_version, publication):
            return False
    return True


def saver(parser_db, item):
    publication, article_snapshot = item.item, item.original
    producer = parser_db.get_producer_by_site_id(site_id=publication["site_id"])
    publication["producer_id"] = producer["producer_id"]
    del publication["site_id"]
    with parser_db.transaction():
        publication_id = parser_db.get_publication_id_by_article_id(
            article_id=article_snapshot["article_id"]
        )
        if publication_id is None:
            existing_pub = parser_db.get_publication_by_article_id(
                article_id=article_snapshot["article_id"]
            )
            if is_new_version(existing_pub, publication):
                logger.debug(
                    "Saving publication of article %d.", article_snapshot["article_id"]
                )
                publication_id = str(uuid.uuid4()).replace("-", "")
                parser_db.insert_publication(
                    **{
                        **publication,
                        **{
                            k: json.dumps(publication[k], ensure_ascii=False)
                            for k in [
                                "urls",
                                "hashtags",
                                "keywords",
                                "tags",
                                "metadata",
                                "comments",
                            ]
                            if k in publication
                        },
                    },
                    publication_id=publication_id,
                )
            else:
                logger.debug(
                    "Skipping publication of article %d because content unchanged.",
                    article_snapshot["article_id"],
                )
        else:
            parser_db.update_publication(**publication, publication_id=publication_id)

        parser_db.upsert_publication_mapping(
            article_id=article_snapshot["article_id"],
            snapshot_at=article_snapshot["snapshot_at"],
            publication_id=publication_id,
            version=publication["version"],
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
        save_ga_id(parser_db, publication)
        save_producer_active_dates(parser_db, publication)


def update_parser_info(db):
    db.insert_ignore_parser_info(parser_name=name, info="{}")
