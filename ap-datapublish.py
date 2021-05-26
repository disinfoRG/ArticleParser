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
import pugsql
import zipfile
from functools import partial
from articleparser.runners import run_batch, run_one_shot, QueryGetter
from articleparser.publish import (
    process_producer_item,
    process_publication_item,
    JsonItemSaver,
)
from articleparser.db import of_uuid, of_datetime, to_producer
from articleparser.drive import GoogleDrive
from articleparser.dateutil import Month, date, parse_date_range, day_start, day_end
import googleapiclient.errors

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
queries = pugsql.module("queries")


def publish_one_day(published_at: date, producer, output_dir, full_text=False):
    output = output_dir / published_at.strftime("%Y-%m-%d.jsonl")
    data_getter = QueryGetter(
        queries.get_publications_by_producer_ranged_by_published_at,
        producer_id=of_uuid(producer["producer_id"]),
        start=of_datetime(day_start(published_at)),
        end=of_datetime(day_end(published_at)),
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


def publish_one_month(
    producer, published_at: Month, output_dir, full_text: bool = False
):
    for day in published_at.iterdate():
        logger.debug(day)
        publish_one_day(day, producer, output_dir=output_dir, full_text=full_text)


def publish_null_published_at(producer, output_dir, full_text: bool = False):
    output = Path(output_dir) / "no_date.jsonl"
    data_getter = QueryGetter(
        queries.get_publications_by_producer_with_null_published_at,
        producer_id=of_uuid(producer["producer_id"]),
    )
    run_batch(
        data_getter=data_getter,
        processor=partial(process_publication_item, full_text=full_text),
        data_saver=JsonItemSaver(filename=output),
    )


def publish_to_drive(
    drive, producer, published_at: Month, full_text=False, tmp_dir="tmp"
):
    logger.debug("%s %s %s %s", drive, producer, published_at, full_text)

    tmp_dir = Path(tmp_dir)
    tmp_dir.mkdir(exist_ok=True)

    if published_at is None:
        outzip = Path("no_date.zip")
        clean_output(tmp_dir, outzip)
        publish_null_published_at(producer, output_dir=tmp_dir, full_text=full_text)
    else:
        outzip = Path(published_at.isoformat() + ".zip")
        clean_output(tmp_dir, outzip)
        publish_one_month(
            producer, published_at, output_dir=tmp_dir, full_text=full_text
        )

    if len(list(tmp_dir.iterdir())) == 0:
        logger.debug("empty archive; done")
        return

    with zipfile.ZipFile(outzip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in tmp_dir.iterdir():
            zf.write(f, arcname=f.name)

    parent_dir_id = make_parent_dir(drive, producer, exist_ok=True)
    try:
        upload_id = upload_to_drive(drive, producer, parent_dir_id, outzip)
    except googleapiclient.errors.HttpError:
        print("%s %s %s %s", drive, producer, published_at, full_text)
        print(traceback.format_exc())

    clean_output(tmp_dir, outzip)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publish datasets from parser database"
    )
    parser.add_argument(
        "-f", "--format", choices=["jsonl"], help="export format", default="jsonl"
    )
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
                    raise RuntimeError(f"non-existent drive '{args.drive}'")
                gdrive = GoogleDrive(**row, service_account=args.service_account)
                if args.published_at:
                    if not isinstance(args.published_at, Month):
                        raise RuntimeError("Google drive only stores monthly archive")
                    publish_to_drive(
                        drive=gdrive,
                        producer=producer,
                        published_at=args.published_at,
                        full_text=args.full_text,
                    )
                elif args.processed_at:
                    for (
                        row
                    ) in queries.get_published_month_by_producer_ranged_by_processed_at(
                        producer_id=of_uuid(args.producer),
                        start=of_datetime(args.processed_at.start_datetime()),
                        end=of_datetime(args.processed_at.end_datetime()),
                    ):
                        logger.debug("publishing %s", row["published_month"])
                        publish_to_drive(
                            drive=gdrive,
                            producer=producer,
                            published_at=Month.fromisoformat(row["published_month"])
                            if row["published_month"] is not None
                            else None,
                            full_text=args.full_text,
                        )
                else:
                    raise RuntimeError("no --published-at or --processed-at specified")
            else:
                if args.published_at:
                    data_getter = QueryGetter(
                        queries.get_publications_by_producer_ranged_by_published_at,
                        producer_id=of_uuid(args.producer),
                        start=of_datetime(args.published_at.start_datetime()),
                        end=of_datetime(args.published_at.end_datetime()),
                    )
                elif args.processed_at:
                    logger.debug(
                        "publications by %s processed between %s and %s",
                        args.producer,
                        args.processed_at.start,
                        args.processed_at.end,
                    )
                    data_getter = QueryGetter(
                        queries.get_publications_by_producer_ranged_by_processed_at,
                        producer_id=of_uuid(args.producer),
                        start=of_datetime(args.processed_at.start_datetime()),
                        end=of_datetime(args.processed_at.end_datetime()),
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
