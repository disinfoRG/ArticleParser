import html
import json
import re

from bs4 import BeautifulSoup
from calmjs.parse import es5
from calmjs.parse.asttypes import Assign
from calmjs.parse.walkers import Walker

from .gatrack import parse_ga_id
from .publication import parse_external_links, parse_published_at


def parse_publication(soups):
    stash = {}
    stash["title"] = soups.body.find("title").text
    declarations = es5(soups.body.find_all("script")[-10].contents[0])
    info_node = list(
        Walker().filter(
            declarations,
            lambda x: isinstance(x, Assign) and str(x.left) == "articleInfo",
        )
    )[0]
    content_node = list(
        filter(
            lambda p: isinstance(p, Assign) and str(p.left) == "content",
            info_node.right.properties,
        )
    )[0]
    content_text = re.search(r"\'(.*)\'.slice", str(content_node.right)).group(1)

    content_soup = BeautifulSoup(json.loads(html.unescape(content_text)), "html.parser")
    stash["publication_text"] = "\n".join(content_soup.stripped_strings)
    stash["image_urls"] = [x["src"] for x in content_soup.find_all("img")]

    return {
        "version": soups.snapshot.snapshot_at,
        "site_id": soups.snapshot.site_id,
        "canonical_url": soups.snapshot.url,
        "published_at": parse_published_at(soups),
        "first_seen_at": soups.snapshot.first_seen_at,
        "last_updated_at": soups.snapshot.last_updated_at,
        "title": stash["title"],
        "publication_text": stash.get("publication_text", ""),
        "author": None,
        "connect_from": None,
        "data": {
            "urls": parse_external_links(soups),
            "image_urls": stash.get("image_urls", ""),
            "hashtags": [],
            "keywords": [],
            "tags": [],
            "metadata": {
                "metatags": soups.metatags,
                **soups.metadata,
                "ga-id": parse_ga_id(soups),
            },
            "comments": [],
        },
    }
