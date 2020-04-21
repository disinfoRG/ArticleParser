from typing import Any, NamedTuple

version = 3


class Snapshot(NamedTuple):
    site_id: int
    url: str
    raw_data: str
    snapshot_at: int
    first_seen_at: int
    last_updated_at: int
    article_type: str


class Soups(NamedTuple):
    doc: Any
    body: Any
    summary: Any
    metatags: Any
    metadata: Any
    snapshot: Snapshot
