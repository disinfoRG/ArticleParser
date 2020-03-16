#!/usr/bin/env python

import sys
import pathlib
import subprocess
import argparse
import logging
from parser.runner import run_parser, DbDataGetter, DataSaver
from parser import version
import parser.db as db
import parser.producer as producer
import parser.publication as publication


def parse_all_sites(scrapper_db, parser_db, dump=False):
    run_parser(
        data_getter=DbDataGetter(scrapper_db, producer.all_sites_getter),
        data_saver=DataSaver(parser_db, producer.saver(dump)),
        transformer=producer.transformer,
    )


def parse_site(scrapper_db, parser_db, site_id, dump=False):
    run_parser(
        data_getter=DbDataGetter(scrapper_db, producer.site_getter(site_id)),
        data_saver=DataSaver(parser_db, producer.saver(dump)),
        transformer=producer.transformer,
    )


def parse_article(scrapper_db, parser_db, article_id, dump=False):
    run_parser(
        data_getter=DbDataGetter(
            scrapper_db,
            publication.snapshots_getter_by_article_id(parser_db, article_id),
        ),
        data_saver=DataSaver(parser_db, publication.saver(dump)),
        transformer=publication.transformer,
        paginate_len=1000,
        limit=100,
    )


def parse_all_articles(scrapper_db, parser_db, limit, dump=False):
    publication.update_parser_info(parser_db)
    run_parser(
        data_getter=DbDataGetter(scrapper_db, publication.snapshots_getter(parser_db)),
        data_saver=DataSaver(parser_db, publication.saver(dump)),
        transformer=publication.transformer,
        paginate_len=1000,
        limit=limit,
    )


def parse_all_old_articles(scrapper_db, parser_db, limit, dump=False):
    run_parser(
        data_getter=DbDataGetter(
            scrapper_db,
            publication.snapshots_getter_by_parser_version(parser_db, version=version),
        ),
        data_saver=DataSaver(parser_db, publication.saver(dump)),
        transformer=publication.transformer,
        paginate_len=1000,
        limit=limit,
    )


def parse_article_by_url(scrapper_db, parser_db, url, dump=False):
    run_parser(
        data_getter=DbDataGetter(
            scrapper_db, publication.snapshots_getter_by_url(parser_db, url)
        ),
        data_saver=DataSaver(parser_db, publication.saver(dump)),
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
            parse_site(scrapper_db, parser_db, args.id, dump=args.dump)
        elif args.site_id is not None:
            parse_site(scrapper_db, parser_db, args.site_id, dump=args.dump)
        else:
            parse_all_sites(scrapper_db, parser_db, dump=args.dump)
    elif args.command == "publication":
        if args.id is not None:
            parse_article(scrapper_db, parser_db, args.id, dump=args.dump)
        elif args.article_id is not None:
            parse_article(scrapper_db, parser_db, args.article_id, dump=args.dump)
        elif args.url is not None:
            parse_article_by_url(scrapper_db, parser_db, args.url, dump=args.dump)
        elif args.update:
            parse_all_old_articles(scrapper_db, parser_db, args.limit, dump=args.dump)
        else:
            parse_all_articles(scrapper_db, parser_db, args.limit, dump=args.dump)
    else:
        raise Exception(f"Unknown command {args.command}")


def try_subcommands(skip_commands=[]):
    """
    Try passing subcommand `cmd` to `parse-cmd`.
    """
    if len(sys.argv) > 1 and sys.argv not in skip_commands:
        binname = pathlib.Path(__file__)
        sub_cmd = (
            binname.parent.resolve() / f"{binname.stem}-{sys.argv[1]}{binname.suffix}"
        )
        try:
            sys.exit(subprocess.run([sub_cmd, *sys.argv[2:]]).returncode)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    try_subcommands(skip_commands=["producer", "publication"])

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

    parser.add_argument(
        "--update", action="store_true", help="updates all results of old parsers"
    )
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

    args = parser.parse_args()
    main(args)
