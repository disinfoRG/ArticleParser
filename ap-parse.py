#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()
import os
import sys
import traceback
import argparse
import logging
from uuid import UUID
from functools import partial
from articleparser.runners import (
    run_parser,
    run_in_one_shot,
    DbGetter,
    DbSaver,
    JsonSaver,
)
from articleparser import version
from articleparser import db
import articleparser.producer as producer
import articleparser.publication as publication
import articleparser.scraper as scraper

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

import json


def get_all_unprocessed_articles(scraper_db, parser_db, args):
    publication.update_parser_info(parser_db)
    info = json.loads(parser_db.get_parser_info(parser_name=publication.name)["info"])
    later_than = (
        info["last_processed_snapshot_at"]
        if "last_processed_snapshot_at" in info
        else 0
    )

    return DbGetter(
        scraper_db, scraper.get_snapshots, snapshot_at_later_than=later_than
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


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dump",
        action="store_true",
        help="dump parsed data to STDOUT instead of write it to db",
    )
    parser.add_argument(
        "--scraper-name", default="ZeroScraper", help="name of upstream scraper to use"
    )

    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)

    prod_cmd = cmds.add_parser("producer", help="parses producers in parser db")
    prod_cmd.add_argument(
        "id", type=UUID, help="id of the producer to parse in parser db", nargs="?"
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
    pub_cmd.add_argument("--url", help="url the article to parse in news db", nargs="?")
    pub_cmd.add_argument(
        "--site-id", type=int, help="parse all articles of this site", nargs="?"
    )
    pub_cmd.add_argument(
        "--update",
        action="store_true",
        help="update publications; do not parse new articles",
    )
    pub_cmd.add_argument("--parser", type=str, help="parser to use", default="default")
    pub_cmd.add_argument(
        "--limit", type=int, default=100000, help="limit number of entries to parse"
    )

    return parser.parse_args()


def main(args):
    parser_db = db.module("queries")
    parser_db.connect(os.getenv("DB_URL"))
    try:
        scraper_db = get_scraper(parser_db, "ZeroScraper")

        if args.command == "producer":
            if args.id is not None:
                p = db.to_producer(
                    parser_db.get_producer(producer_id=db.of_uuid(args.id))
                )
                data_getter = DbGetter(
                    scraper_db, scraper.get_site, site_id=p["site_id"]
                )
            elif args.site_id is not None:
                data_getter = DbGetter(
                    scraper_db, scraper.get_site, site_id=args.site_id
                )
            else:
                data_getter = DbGetter(scraper_db, scraper.get_sites)

            data_saver = (
                DbSaver(parser_db, producer.saver) if not args.dump else JsonSaver()
            )
            run_in_one_shot(
                data_getter=data_getter,
                data_saver=data_saver,
                processor=producer.process_item,
            )

        elif args.command == "publication":
            if args.id is not None:
                raise RuntimeError("Unimplemented")
            elif args.article_id is not None:
                data_getter = DbGetter(
                    scraper_db, scraper.get_snapshots, article_id=args.article_id
                )
            elif args.url is not None:
                data_getter = DbGetter(scraper_db, scraper.get_snapshots, url=url)
            elif args.site_id is not None:
                data_getter = DbGetter(
                    scraper_db, scraper.get_snapshots, site_id=args.site_id
                )
            elif args.update:
                raise RuntimeError("Unimplementde")
            else:
                data_getter = get_all_unprocessed_articles(
                    scraper_db, parser_db, args=args
                )
            run_parser(
                data_getter=data_getter,
                data_saver=DbSaver(parser_db, publication.saver)
                if not args.dump
                else JsonSaver(),
                processor=partial(publication.process_item, parser=args.parser),
                batch_size=1000,
                limit=args.limit,
            )
        else:
            raise RuntimeError(f"Unknown command '{args.command}'")
        return 0
    except:
        logger.error(traceback.format_exc())
        return -1
    finally:
        parser_db.disconnect()


if __name__ == "__main__":
    sys.exit(main(parse_args()))
