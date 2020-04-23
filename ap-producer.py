#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()
import os
import sys
import logging
import traceback
import datetime
import argparse
from uuid import UUID
from articleparser import db
from tabulate import tabulate

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

queries = db.module("queries")


def main(args):
    queries.connect(os.getenv("DB_URL"))
    try:
        if args.command == "list":
            print(
                tabulate(
                    [
                        [
                            p["producer_id"],
                            p["site_id"],
                            p["name"],
                            p["url"],
                            p["first_seen_at"],
                            p["last_updated_at"],
                            p["data"]["identifiers"],
                        ]
                        for p in db.to_producers(queries.get_producers())
                    ],
                    headers=[
                        "id",
                        "site id",
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
                data = queries.get_producer_with_stats(
                    producer_id=db.of_uuid(producer_id)
                )
                print(tabulate(db.to_producer(data).items()))
        else:
            raise RuntimeError(f"Unknown command '{args.command}'")
        return 0
    except:
        logger.error(traceback.format_exc())
        return -1
    finally:
        queries.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)
    cmds.add_parser("list")

    def uuid(value):
        u = UUID(value)
        return str(u).replace("-", "")

    show_cmd = cmds.add_parser("show")
    show_cmd.add_argument("id", type=UUID, help="producer id", nargs="+")

    args = parser.parse_args()
    sys.exit(main(args))
