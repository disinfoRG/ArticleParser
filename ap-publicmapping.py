#!/usr/bin/env python3

from dotenv import load_dotenv

load_dotenv()
import os
import logging
import argparse
import pugsql
import json
from articleparser.drive import GoogleDrive

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
queries = pugsql.module("queries")


def main(args):
    drive_name = "public"
    queries.connect(os.getenv("DB_URL"))
    d = queries.get_drive_by_name(name=drive_name)
    data = json.loads(d["data"])
    producer_months = data["files"]["producers"]
    json.dump(producer_months, open("public_file_mapping.json", "w"))

    # upload to gdrive
    drive = GoogleDrive("", drive_name, "{}", args.service_account)
    drive.upload(args.parent_dir_id, "public_file_mapping.json", file_id=args.file_id)
    queries.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--service-account",
        help="Service account file to access Google Drive",
        default="service.json",
    )
    parser.add_argument(
        "--parent-dir-id",
        help="id of drive folder to store output",
        default=os.getenv("GDRIVE_PUBLIC_DATASETS_ID"),
    )
    parser.add_argument(
        "--file-id",
        help="id of file in drive",
        default=os.getenv("GDRIVE_PUBLIC_FILE_MAPPING_ID"),
    )
    args = parser.parse_args()
    main(args)
