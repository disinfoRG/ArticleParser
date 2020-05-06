#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()
import os
import sys
import logging
import traceback
import argparse
from pathlib import Path
from uuid import UUID
import dateparser
import pugsql
import zipfile
from functools import partial
from articleparser.runners import run_batch, run_one_shot, QueryGetter
from articleparser.publish import (
    process_producer_item,
    process_publication_item,
    JsonItemSaver,
)
from articleparser.db import of_uuid, of_date, to_producer
from articleparser.drive import GoogleDrive
from articleparser.dateutil import *

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
queries = pugsql.module("queries")


def parse_date_range(value):
    if value.find(":") >= 0:
        start, end = value.split(":", 1)
        return (dateparser.parse(start), dateparser.parse(end))
    else:
        d = dateparser.parse(value)
        return (d, d + timedelta(days=1))


def publish_one_day(published_at, producer, output_dir, full_text=False):
    output = output_dir / published_at.strftime("%Y-%m-%d.jsonl")
    data_getter = QueryGetter(
        queries.get_publications_by_producer_ranged_by_published_at,
        producer_id=of_uuid(producer["producer_id"]),
        start=of_date(published_at),
        end=of_date(published_at) + 86400 - 1,
    )
    run_batch(
        data_getter=data_getter,
        processor=partial(process_publication_item, full_text=full_text),
        data_saver=JsonItemSaver(filename=output),
    )


def clean_output(output_dir, outzip):
    for f in output_dir.iterdir():
        f.unlink()
    if outzip.exists():
        outzip.unlink()


def make_parent_dir(drive, producer, exist_ok=True):
    parent_dir_id = None
    if not drive.has_producer_dir(producer):
        if not exist_ok:
            raise RuntimeError(
                f"producer does not have an upload dir: {producer['producer_id']}"
            )
        parent_dir_id = drive.make_producer_dir(producer)
        r = queries.update_drive_producer_dir_id(
            name=drive.name,
            producer_id=str(producer["producer_id"]),
            dir_id=parent_dir_id,
        )
        logger.debug("%d", r)
    else:
        parent_dir_id = drive.get_producer_dir(producer)
    return parent_dir_id


def upload_to_drive(drive, producer, parent_dir_id, outzip):
    upload_id = None
    if not drive.has_producer_file(producer, outzip.stem):
        upload_id = drive.upload(parent_dir_id, filename=outzip)
        logger.debug("%s %s %s", parent_dir_id, upload_id, outzip.stem)
        r = queries.update_drive_file_id(
            name=drive.name,
            producer_id=str(producer["producer_id"]),
            filename=outzip.stem,
            file_id=upload_id,
        )
        logger.debug("%d", r)
    else:
        upload_id = drive.upload(
            parent_dir_id,
            filename=outzip,
            file_id=drive.get_producer_file(producer, outzip.stem),
        )
    return upload_id


def publish_to_drive(drive, producer, published_at, full_text=False, tmp_dir="tmp"):
    logger.debug("%s %s %s %s", drive, producer, published_at, full_text)

    tmp_dir = Path(tmp_dir)
    tmp_dir.mkdir(exist_ok=True)
    outzip = Path(published_at.strftime("%Y-%m-%d.zip"))
    clean_output(tmp_dir, outzip)

    publish_one_day(published_at, producer, output_dir=tmp_dir, full_text=full_text)

    with zipfile.ZipFile(outzip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in tmp_dir.iterdir():
            zf.write(f, arcname=f.name)

    parent_dir_id = make_parent_dir(drive, producer, exist_ok=True)
    upload_id = upload_to_drive(drive, producer, parent_dir_id, outzip)

    clean_output(tmp_dir, outzip)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publish datasets from parser database"
    )
    parser.add_argument(
        "-f", "--format", choices=["jsonl"], help="export format", default="jsonl"
    )
    parser.add_argument("-o", "--output", default="-", help="save to file")
    cmds = parser.add_subparsers(
        title="data class to publish", dest="command", required=True
    )
    prod_cmd = cmds.add_parser("producer", help="publish producer data in parser db")
    pub_cmd = cmds.add_parser(
        "publication", help="publish publication data in parse db"
    )
    pub_cmd.add_argument(
        "--producer",
        type=UUID,
        help="producer id of the publication to publish",
        required=True,
    )
    pub_cmd.add_argument("--full-text", action="store_true", help="publish full text")
    pub_cmd.add_argument(
        "--published-at",
        type=parse_date_range,
        help="publishing day of the publication to publish",
    )
    pub_cmd.add_argument(
        "--drive", help="Google Drive name to publish datasets", default="local"
    )
    pub_cmd.add_argument(
        "--service-account", help="Service account file to access Google Drive"
    )
    pub_cmd.add_argument(
        "--processed-at",
        type=parse_date_range,
        help="publish data processed after given time",
    )
    return parser.parse_args()


def main(args):
    queries.connect(os.getenv("DB_URL"))
    try:
        if args.command == "producer":
            run_one_shot(
                data_getter=QueryGetter(queries.get_producers),
                processor=process_producer_item,
                data_saver=JsonItemSaver(),
            )
        elif args.command == "publication":
            producer = to_producer(
                queries.get_producer(producer_id=of_uuid(args.producer))
            )
            if args.drive and args.drive != "local":
                row = queries.get_drive_by_name(name=args.drive)
                if row is None:
                    raise RuntimeError(f"non-existent drive '{drive}'")
                gdrive = GoogleDrive(**row, service_account=args.service_account)
                if args.published_at:
                    publish_to_drive(
                        drive=gdrive,
                        producer=producer,
                        published_at=args.published_at[0],
                        full_text=args.full_text,
                    )
                elif args.processed_at:
                    for (
                        row
                    ) in queries.get_published_date_by_producer_ranged_by_processed_at(
                        producer_id=of_uuid(args.producer),
                        start=args.processed_at[0].timestamp(),
                        end=args.processed_at[1].timestamp() - 1,
                    ):
                        publish_to_drive(
                            drive=gdrive,
                            producer=producer,
                            published_at=row["published_date"],
                            full_text=args.full_text,
                        )
                else:
                    raise RuntimeError("no --published-at or --processed-at specified")
            else:
                if args.published_at:
                    data_getter = QueryGetter(
                        queries.get_publications_by_producer_ranged_by_published_at,
                        producer_id=of_uuid(args.producer),
                        start=args.published_at[0].timestamp(),
                        end=args.published_at[1].timestamp() - 1,
                    )
                elif args.processed_at:
                    logger.debug(
                        "publications by %s processed between %s and %s",
                        args.producer,
                        args.processed_at[0],
                        args.processed_at[1],
                    )
                    data_getter = QueryGetter(
                        queries.get_publications_by_producer_ranged_by_processed_at,
                        producer_id=of_uuid(args.producer),
                        start=args.processed_at[0].timestamp(),
                        end=args.processed_at[1].timestamp() - 1,
                    )
                else:
                    raise RuntimeError("no --published-at or --processed-at specified")
                run_batch(
                    data_getter=data_getter,
                    processor=partial(
                        process_publication_item, full_text=args.full_text
                    ),
                    data_saver=JsonItemSaver(),
                )
        else:
            raise RuntimeError(f"unknown command '{args.command}'")
        return 0
    except:
        logger.error(traceback.format_exc())
        return -1
    finally:
        queries.disconnect()


if __name__ == "__main__":
    sys.exit(main(parse_args()))
