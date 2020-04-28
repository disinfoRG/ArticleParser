import pickle
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


def list_files(service):
    results = (
        service.files()
        .list(pageSize=20, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
        print("No files found.")
    else:
        print("Files:")
        for item in items:
            print("{0} ({1})".format(item["name"], item["id"]))


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


def get_creds(credentials_path="credentials.json", saved_token_path="token.pickle"):
    creds = None
    saved_token = Path(saved_token_path)
    if saved_token.exists():
        with saved_token.open("rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with saved_token.open("wb") as token:
            pickle.dump(creds, token)
    return creds


class GoogleDrive:
    name: str

    def __init__(self, drive_id, name, data):
        self.name = name
        self.data = json.loads(data)

    def has_producer_dir(self, producer):
        return str(producer["producer_id"]) in self.data["dirs"]["producers"]

    def get_producer_dir(self, producer):
        return self.data["dirs"]["producers"][str(producer["producer_id"])]

    def make_producer_dir(self, producer):
        creds = get_creds()
        service = build("drive", "v3", credentials=creds)
        parent_dir_id = None
        if str(producer["producer_id"]) not in self.data["dirs"]["producers"]:
            r = (
                service.files()
                .create(
                    body={
                        "name": f"{producer['producer_id']}-{producer['name']}",
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
        return parent_dir_id

    def has_producer_file(self, producer, stem):
        return stem in self.data["files"]["producers"][str(producer["producer_id"])]

    def get_producer_file(self, producer, stem):
        return self.data["files"]["producers"][str(producer["producer_id"])][stem]

    def upload(self, parent_dir_id, filename, file_id=None):
        creds = get_creds()
        service = build("drive", "v3", credentials=creds)
        return upload_file(
            service, filename, filename, parent=parent_dir_id, file_id=file_id
        )
