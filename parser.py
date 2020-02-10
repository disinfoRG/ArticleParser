#!/usr/bin/env python

import argparse
import logging
from parser.runner import run_parser
import parser.db as db
import parser.producer as producer
import parser.publication as publication


def parse_all_sites(scrapper_db, parser_db):
    run_parser(
        from_db=scrapper_db,
        to_db=parser_db,
        getter=producer.all_sites_getter,
        saver=producer.saver,
        transformer=producer.transformer,
    )


def parse_site(scrapper_db, parser_db, site_id):
    run_parser(
        from_db=scrapper_db,
        to_db=parser_db,
        getter=producer.site_getter(site_id),
        saver=producer.saver,
        transformer=producer.transformer,
    )


def parse_article(scrapper_db, parser_db, article_id):
    run_parser(
        from_db=scrapper_db,
        to_db=parser_db,
        getter=publication.snapshots_getter_by_article_id(parser_db, article_id),
        saver=publication.saver(),
        transformer=publication.transformer,
        paginate_len=1000,
        limit=100,
    )


def parse_all_articles(scrapper_db, parser_db, limit):
    publication.update_parser_info(parser_db)
    run_parser(
        from_db=scrapper_db,
        to_db=parser_db,
        getter=publication.snapshots_getter(parser_db),
        saver=publication.saver(),
        transformer=publication.transformer,
        paginate_len=1000,
        limit=limit,
    )


def parse_article_by_url(scrapper_db, parser_db, url):
    run_parser(
        from_db=scrapper_db,
        to_db=parser_db,
        getter=publication.snapshots_getter_by_url(parser_db, url),
        saver=publication.saver(),
        transformer=publication.transformer,
        paginate_len=1000,
        limit=100,
    )


def main(args):
    logging.basicConfig(level=logging.INFO)

    scrapper_db = db.scrapper()
    parser_db = db.parser()

    if args.command == "producer":
        if args.id is not None:
            parse_site(scrapper_db, parser_db, args.id)
        elif args.site_id is not None:
            parse_site(scrapper_db, parser_db, args.site_id)
        else:
            parse_all_sites(scrapper_db, parser_db)
    elif args.command == "publication":
        if args.id is not None:
            parse_article(scrapper_db, parser_db, args.id)
        elif args.article_id is not None:
            parse_article(scrapper_db, parser_db, args.article_id)
        elif args.url is not None:
            parse_article_by_url(scrapper_db, parser_db, args.url)
        else:
            parse_all_articles(scrapper_db, parser_db, args.limit)
    else:
        raise Exception(f"Unknown command {args.command}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)

    prod_cmd = cmds.add_parser("producer", help="parses producers in parser db")
    prod_cmd.add_argument(
        "id", type=int, help="id of the producer to parse in parser db", nargs="?"
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

    parser.add_argument("--parser-version", help="force parser version")
    parser.add_argument(
        "--update", action="store_true", help="updates all results of old parsers"
    )
    parser.add_argument("--limit-sec", type=int, help="limit run time in seconds")
    parser.add_argument(
        "--limit", type=int, default=10000, help="limit number of entries to parse"
    )

    args = parser.parse_args()
    main(args)
