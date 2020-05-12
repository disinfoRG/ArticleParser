import pickle
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import json
import urllib.parse

scopes = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


def upload_file(service, src, dst, parent=None, file_id=None):
    dst = Path(dst)
    file_metadata = {"name": dst.name}

    f = None
    if file_id is not None:
        f = (
            service.files()
            .update(
                fileId=file_id,
                body=file_metadata,
                media_body=MediaFileUpload(src, mimetype="application/octet-stream"),
                fields="id",
            )
            .execute()
        )
    else:
        if parent is not None:
            file_metadata["parents"] = [parent]
        f = (
            service.files()
            .create(
                body=file_metadata,
                media_body=MediaFileUpload(src, mimetype="application/octet-stream"),
                fields="id",
            )
            .execute()
        )
    return f.get("id")


def get_creds(keyfile):
    return service_account.Credentials.from_service_account_file(keyfile, scopes=scopes)


class GoogleDrive:
    name: str

    def __init__(self, drive_id, name, data, service_account):
        self.name = name
        self.data = json.loads(data)
        self.service_account = service_account

    def has_producer_dir(self, producer):
        return str(producer["producer_id"]) in self.data["dirs"]["producers"]

    def get_producer_dir(self, producer):
        return self.data["dirs"]["producers"][str(producer["producer_id"])]

    def make_producer_dir(self, producer):
        creds = get_creds(self.service_account)
        service = build("drive", "v3", credentials=creds)
        parent_dir_id = None
        host = urllib.parse.urlparse(producer["url"]).netloc
        dirname = f"{producer['name']} ({host}) {producer['producer_id']}"
        if str(producer["producer_id"]) not in self.data["dirs"]["producers"]:
            r = (
                service.files()
                .create(
                    body={
                        "name": dirname,
                        "mimeType": "application/vnd.google-apps.folder",
                        "parents": [self.data["dirs"]["root"]],
                    },
                    fields="id",
                )
                .execute()
            )
            parent_dir_id = r.get("id")
            self.data["dirs"]["producers"][str(producer["producer_id"])] = parent_dir_id
            self.data["files"]["producers"][str(producer["producer_id"])] = {}
        else:
            parent_dir_id = self.data["dirs"]["producers"][str(producer["producer_id"])]
            service.files().update(fileId=parent_dir_id, name=dirname).execute()
        return parent_dir_id

    def has_producer_file(self, producer, stem):
        return stem in self.data["files"]["producers"][str(producer["producer_id"])]

    def get_producer_file(self, producer, stem):
        return self.data["files"]["producers"][str(producer["producer_id"])][stem]

    def upload(self, parent_dir_id, filename, file_id=None):
        creds = get_creds(self.service_account)
        service = build("drive", "v3", credentials=creds)
        return upload_file(
            service, filename, filename, parent=parent_dir_id, file_id=file_id
        )
