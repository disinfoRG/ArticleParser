#!/usr/bin/env python3

from dotenv import load_dotenv

load_dotenv()

import os
import logging
import datetime
import argparse
import pugsql
from tabulate import tabulate

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

queries = pugsql.module("queries")
queries.connect(os.getenv("DB_URL"))


def timestamp_to_string(ts):
    return datetime.datetime.fromtimestamp(ts) if ts else ""


def main(args):
    if args.command == "list":
        print(
            tabulate(
                [
                    [
                        p["producer_id"],
                        p["name"],
                        p["url"],
                        timestamp_to_string(p["first_seen_at"]),
                        timestamp_to_string(p["last_updated_at"]),
                        p["identifiers"] if p["identifiers"] != "{}" else "",
                    ]
                    for p in queries.get_producers()
                ],
                headers=[
                    "id",
                    "name",
                    "url",
                    "first seen at",
                    "last updated at",
                    "identifiers",
                ],
            )
        )
    elif args.command == "show":
        for producer_id in args.id:
            producer = queries.get_producer_by_id_with_stats(producer_id=producer_id)
            for field in ["first_seen_at", "last_updated_at"]:
                producer[field] = timestamp_to_string(producer[field])
            print(tabulate(producer.items()))
    else:
        raise RuntimeError(f"Unknown command '{args.command}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)
    cmds.add_parser("list")

    show_cmd = cmds.add_parser("show")
    show_cmd.add_argument("id", type=int, help="producer id", nargs="+")

    args = parser.parse_args()
    main(args)
