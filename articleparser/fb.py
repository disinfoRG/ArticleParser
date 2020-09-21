import datetime
import re
from .gatrack import parse_ga_id
from . import Soups, Snapshot


def parse_comments(soup):
    return ""


def parse_hashtags(soups):
    stash = []
    hashtag_elems = soups.body.find_all(
        lambda tag: tag.name == "a"
        and "href" in tag.attrs.keys()
        and "hashtag" in tag.attrs["href"]
    )
    hashtag_links = [h["href"] for h in hashtag_elems]
    for hlink in hashtag_links:
        try:
            hashtag = re.search(r"hashtag/(.*)\?", hlink).group(1)
        except:
            pass
        else:
            stash.append(hashtag)
    return stash


def parse_reactions(soups):
    shares_elem = soups.body.find("a", {"data-testid": "UFI2SharesCount/root"})
    shares = shares_elem.text.split(" ")[0]
    print(shares)

    return {"shares": shares}


def parse_publication(soups: Soups):
    stash = {}
    post = soups.body.find("div", {"data-testid": "post_message"})
    stash["published_at"] = soups.body.find("abbr")["data-utime"]
    stash["publication_text"] = " ".join(list(post.stripped_strings))
    external_links = [x.get("href") for x in soups.body.find_all("a")]

    image_links = [x.get("src") for x in soups.body.find_all("img")[1:]]
    comments = parse_comments(soups.body)
    ga_id = parse_ga_id(soups)
    hashtags = parse_hashtags(soups.body)
    reactions = parse_reactions(soups.body)
    return {
        "version": soups.snapshot.snapshot_at,
        "site_id": soups.snapshot.site_id,
        "canonical_url": soups.snapshot.url,
        "published_at": stash["published_at"],
        "first_seen_at": soups.snapshot.first_seen_at,
        "last_updated_at": soups.snapshot.last_updated_at,
        "title": "",
        "publication_text": stash["publication_text"],
        "author": "",
        "connect_from": "",
        "data": {
            "urls": external_links,
            "image_urls": image_links,
            "hashtags": hashtags,
            "keywords": [],
            "tags": [],
            "metadata": {"metatags": soups.metatags, **soups.metadata, "ga-id": ga_id},
            "comments": comments,
            "reactions": reactions,
        },
    }
