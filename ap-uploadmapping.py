#!/usr/bin/env python3

from dotenv import load_dotenv

load_dotenv()
import os
import logging
import argparse
import pugsql
import json
import pandas as pd
from uuid import UUID

from articleparser.drive import GoogleDrive

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
queries = pugsql.module("queries")


def create_producer_id_mapping(queries):
    d = list(queries.get_producers())
    df = pd.DataFrame(d)[["name", "url", "producer_id"]]
    df["producer_id"] = df["producer_id"].apply(lambda pid: str(UUID(pid)))
    df.to_csv("producers_id.csv", index=False)


def create_public_file_id_mapping(queries):
    d = queries.get_drive_by_name(name="public")
    data = json.loads(d["data"])
    producer_months = data["files"]["producers"]
    json.dump(producer_months, open("public_file_mapping.json", "w"))


def main(args):
    queries.connect(os.getenv("DB_URL"))
    create_producer_id_mapping(queries)
    create_public_file_id_mapping(queries)

    # upload to gdrive
    drive = GoogleDrive("", "", "{}", args.service_account)
    parent_dir_id = os.getenv("GDRIVE_PUBLIC_DATASETS_ID")
    drive.upload(
        parent_dir_id,
        "public_file_mapping.json",
        file_id=os.getenv("GDRIVE_PUBLIC_FILE_MAPPING_ID"),
    )
    drive.upload(
        parent_dir_id, "producers_id.csv", file_id=os.getenv("GDRIVE_PRODUCERS_CSV_ID")
    )
    queries.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--service-account",
        help="Service account file to access Google Drive",
        default="service.json",
    )

    args = parser.parse_args()
    main(args)
