#!/usr/bin/env python3

from dotenv import load_dotenv

load_dotenv()

import os
import argparse
import logging
from uuid import UUID
import pugsql
from parser.runner import run_parser, DbGetter, DbSaver, JsonSaver
from parser import version
import parser.producer as producer
import parser.publication as publication
import parser.scraper as scraper

logger = logging.getLogger(__name__)


def parse_article(scraper_db, parser_db, article_id, args):
    run_parser(
        data_getter=DbGetter(
            scraper_db,
            publication.snapshots_getter_by_article_id,
            article_id=article_id,
        ),
        data_saver=DbSaver(parser_db, publication.saver)
        if not args.dump
        else JsonSaver(),
        processor=publication.process,
        batch_size=1000,
        limit=args.limit,
    )


def parse_all_articles(scraper_db, parser_db, args):
    publication.update_parser_info(parser_db)
    run_parser(
        data_getter=DbGetter(
            scraper_db, publication.snapshots_getter, parser_db=parser_db
        ),
        data_saver=DbSaver(parser_db, publication.saver)
        if not args.dump
        else JsonSaver(),
        processor=publication.process,
        batch_size=1000,
        limit=args.limit,
    )


def parse_all_old_articles(scraper_db, parser_db, args):
    run_parser(
        data_getter=DbGetter(
            scraper_db,
            publication.snapshots_getter_by_parser_version(
                parser_db=parser_db, site_id=args.site_id, version=version
            ),
            parser_db=parser_db,
        ),
        data_saver=DbSaver(parser_db, publication.saver)
        if not args.dump
        else JsonSaver(),
        processor=publication.process,
        batch_size=1000,
        limit=args.limit,
    )


def parse_article_by_url(scraper_db, parser_db, url, args):
    run_parser(
        data_getter=DbGetter(scraper_db, publication.snapshots_getter_by_url, url=url),
        data_saver=DbSaver(parser_db, publication.saver)
        if not args.dump
        else JsonSaver(),
        processor=publication.process,
        batch_size=1000,
        limit=args.limit,
    )


def parse_article_by_site(scraper_db, parser_db, site_id, args):
    run_parser(
        data_getter=DbGetter(
            scraper_db, publication.snapshots_getter_by_site, site_id=site_id
        ),
        data_saver=DbSaver(parser_db, publication.saver)
        if not args.dump
        else JsonSaver(),
        processor=publication.process,
        batch_size=1000,
        limit=args.limit,
    )


def get_scraper(db, scraper_name):
    sc = db.get_scraper_by_name(scraper_name=scraper_name)
    return scraper.ScraperDb(
        sc["scraper_name"],
        os.getenv(sc["db_url_var"]),
        site_table_name=sc["site_table_name"],
        article_table_name=sc["article_table_name"],
        snapshot_table_name=sc["snapshot_table_name"],
    )


def main(args):
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

    parser_db = pugsql.module("queries")
    parser_db.connect(os.getenv("DB_URL"))
    scraper_db = get_scraper(parser_db, "ZeroScraper")

    if args.command == "producer":
        data_saver = (
            DbSaver(parser_db, producer.saver) if not args.dump else JsonSaver()
        )
        processor = producer.process
        data_getter = None
        if args.id is not None:
            p = parser_db.get_producer(producer_id=args.id)
            data_getter = DbGetter(
                scraper_db, producer.site_getter, site_id=p["site_id"]
            )
        elif args.site_id is not None:
            data_getter = DbGetter(
                scraper_db, producer.site_getter, site_id=args.site_id
            )
        else:
            data_getter = DbGetter(scraper_db, producer.all_sites_getter)
        run_parser(
            data_getter=data_getter,
            data_saver=data_saver,
            processor=processor,
            limit=args.limit,
        )
    elif args.command == "publication":
        if args.id is not None:
            parse_article(scraper_db, parser_db, args.id, args=args)
        elif args.article_id is not None:
            parse_article(scraper_db, parser_db, args.article_id, args=args)
        elif args.url is not None:
            parse_article_by_url(scraper_db, parser_db, args.url, args=args)
        elif args.update:
            parse_all_old_articles(scraper_db, parser_db, args=args)
        elif args.site_id is not None:
            parse_article_by_site(scraper_db, parser_db, args.site_id, args=args)
        else:
            parse_all_articles(scraper_db, parser_db, args=args)
    else:
        raise Exception(f"Unknown command {args.command}")


def parse_args():
    parser = argparse.ArgumentParser()

    # XXX not implemented
    # parser.add_argument("--limit-sec", type=int, help="limit run time in seconds")
    parser.add_argument(
        "--limit", type=int, default=10000, help="limit number of entries to parse"
    )
    parser.add_argument(
        "--dump",
        action="store_true",
        help="dump data in STDOUT in JSON instead of writing to db",
    )
    parser.add_argument(
        "--scraper", default="ZeroScraper", help="name of scraper upstream to use"
    )

    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)

    def uuid(value):
        u = UUID(value)
        return str(u).replace("-", "")

    prod_cmd = cmds.add_parser("producer", help="parses producers in parser db")
    prod_cmd.add_argument(
        "id", type=uuid, help="id of the producer to parse in parser db", nargs="?"
    )
    prod_cmd.add_argument(
        "--site-id", type=int, help="id of the site to parse in news db", nargs="?"
    )

    pub_cmd = cmds.add_parser("publication", help="parses publications in parser db")
    pub_cmd.add_argument(
        "id", type=int, help="id of the publication to parse in parser db", nargs="?"
    )
    pub_cmd.add_argument(
        "--article-id", type=int, help="id the article to parse in news db", nargs="?"
    )
    pub_cmd.add_argument(
        "--site-id", type=int, help="parse all articles of this site", nargs="?"
    )
    pub_cmd.add_argument("--url", help="url the article to parse in news db", nargs="?")
    pub_cmd.add_argument(
        "--update",
        action="store_true",
        help="updates all publications parsed by older parsers",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
