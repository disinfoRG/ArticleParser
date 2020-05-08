from . import Soups
from .gatrack import parse_ga_id
from . import publication as P
from calmjs.parse import es5
from calmjs.parse.asttypes import Assign
from calmjs.parse.walkers import Walker
from bs4 import BeautifulSoup
import json


def parse_publication(soups: Soups):
    stash = {}
    content = None
    target_script = None
    for script in soups.body.find_all("script"):
        try:
            if "Fusion.globalContent" in script.contents[0]:
                target_script = script.contents[0]
                break
        except:
            pass

    if target_script:
        for x in Walker().filter(
            es5(target_script), lambda node: isinstance(node, Assign)
        ):
            if str(x.left) == "Fusion.globalContent":
                content = json.loads(str(x.right))["content_elements"]
                break

        publication_text = [x["content"] for x in content if x.get("type") == "text"]
        publication_text_html = [
            x["content"] for x in content if x.get("type") == "raw_html"
        ]
        for html in publication_text_html:
            soup = BeautifulSoup(html, "html.parser")
            publication_text += list(soup.stripped_strings)
        stash["publication_text"] = "\n".join(publication_text)
        stash["image_urls"] = [x["url"] for x in content if x.get("type") == "image"]

    return {
        "version": soups.snapshot.snapshot_at,
        "site_id": soups.snapshot.site_id,
        "canonical_url": soups.snapshot.url,
        "published_at": P.parse_published_at(soups),
        "first_seen_at": soups.snapshot.first_seen_at,
        "last_updated_at": soups.snapshot.last_updated_at,
        "title": soups.body.find("title").text,
        "publication_text": stash.get("publication_text", ""),
        "author": None,
        "connect_from": None,
        "data": {
            "urls": P.parse_external_links(soups),
            "image_urls": stash.get("image_urls", []),
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
