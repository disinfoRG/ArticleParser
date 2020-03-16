import datetime
from parser.gatrack import parse_ga_id


def parse_external_links(soups):
    return [x["href"] for x in soups["summary"].find_all("a", href=lambda x: x)]


def parse_image_links(soups):
    return [
        x.get("data-src", x.get("src", x.get("data-original", "")))
        for x in soups["summary"].find_all("img")
    ]


def parse_datetime(text):
    try:
        return datetime.datetime.strptime(text, "%a %b %d %H:%M:%S %Y").timestamp()
    except:
        return None


def parse_publication(soups):
    stash = {}

    for line in soups["body"].select(".article-metaline"):
        tag = line.find(class_="article-meta-tag").text
        value = line.find(class_="article-meta-value").text
        if tag == "作者":
            stash["author"] = value
        elif tag == "標題":
            stash["title"] = value
        elif tag == "時間":
            stash["published_at"] = parse_datetime(value)

    content = soups["body"].select("#main-content")[0]
    children = list(content.stripped_strings)
    board = children[3]
    text = []
    connect_from = None
    for line in children[8:]:
        if line.find("◆ From: ") == 0:
            connect_from = line[len("◆ From: ") :]
            break
        else:
            text.append(line)
    publication_text = "\n".join(text)
    external_links = parse_external_links(soups)
    image_links = parse_image_links(soups)

    comments = [
        {
            "id": i,
            "reaction": item.find(class_="push-tag").text.strip(),
            "author": item.find(class_="push-userid").text,
            "text": item.find(class_="push-content").text[1:],
            "published_at": item.find(class_="push-ipdatetime").text,
        }
        for i, item in enumerate(soups["body"].select("#main-content .push"))
    ]

    ga_id = parse_ga_id(soups)

    return {
        "publication_id": soups["snapshot"]["article_id"],
        "producer_id": soups["snapshot"]["site_id"],
        "canonical_url": soups["snapshot"]["url"],
        "published_at": stash["published_at"],
        "first_seen_at": soups["snapshot"]["first_seen_at"],
        "last_updated_at": soups["snapshot"]["last_updated_at"],
        "title": stash["title"],
        "publication_text": publication_text,
        "author": stash["author"],
        "urls": external_links,
        "image_urls": image_links,
        "hashtags": [],
        "keywords": [],
        "tags": [],
        "metadata": {
            "meta-tags": soups["meta-tags"],
            **soups["metadata"],
            "ga-id": ga_id,
        },
        "comments": comments,
        "connect_from": connect_from,
    }
