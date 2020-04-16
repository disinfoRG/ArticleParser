import datetime
import re
from parser.gatrack import parse_ga_id

ip_pattern = re.compile("((?:\d+\.){3}\d+)")


def parse_external_links(soups):
    return [
        x["href"]
        for x in soups["summary"].find_all("a", href=lambda x: x)
        if x["href"] != soups["snapshot"]["url"]
    ]


def parse_image_links(soups):
    return [
        x.get("data-src", x.get("src", x.get("data-original", "")))
        for x in soups["summary"].find_all("img")
    ]


def parse_datetime(text):
    try:
        return datetime.datetime.strptime(text, "%Y年%m月%d日").timestamp()
    except:
        return None


def parse_comment(i, item):
    text = item.find(class_="push-content").text
    text = text[len(": ") :]

    ipdatetime = item.find(class_="push-ipdatetime").text.strip()
    m = ip_pattern.search(ipdatetime)

    connect_from = m.group(1) if m is not None else None
    published_at = ipdatetime[m.end(1):].strip() if m is not None else ipdatetime

    result = {
        "id": i,
        "reaction": item.find(class_="push-tag").text.strip(),
        "author": item.find(class_="push-userid").text,
        "text": text,
        "published_at": published_at,
    }
    if connect_from is not None:
        result["connect_from"] = connect_from

    return result


def parse_publication(soups):
    stash = {}
    stash["title"] = soups["body"].find("h1").text
    header_table = soups["body"].find("table", {"class": "head-tbl"})

    for row in header_table.find_all('tr'):
        tag = row.find("th").text.strip()
        value = row.find("td").text.strip()
        if tag == "作者":
            stash["author"] = value
        elif tag == "時間":
            stash["published_at"] = parse_datetime(value)

    content = soups["body"].select("#main-content")[0]
    text = []
    connect_from = None
    for c in content.children:
        try:
            line = c.text
        except AttributeError:
            line = c
        if line.find("◆ From: ") == 0:
            connect_from = line[len("◆ From: ") :]
            break
        elif line.find("※ 發信站: 批踢踢實業坊(ptt.cc), 來自: ") == 0:
            m = ip_pattern.search(line)
            connect_from = m.group(1) if m is not None else None
            break
        else:
            text.append(line)

        if c.next_sibling.name == "div":
            break

    publication_text = "\n".join(text)
    external_links = parse_external_links(soups)
    image_links = parse_image_links(soups)

    comments = [
        parse_comment(i, item)
        for i, item in enumerate(soups["body"].select("#main-content .push"))
    ]

    ga_id = parse_ga_id(soups)

    return {
        "publication_id": soups["snapshot"]["article_id"],
        "version": soups["snapshot"]["snapshot_at"],
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
