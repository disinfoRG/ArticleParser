import datetime
from . import Soups
import re
import bs4
from .gatrack import parse_ga_id

ip_pattern = re.compile("((?:\d+\.){3}\d+)")


def parse_external_links(soups: Soups):
    main_content = soups.body.select("#main-content")[0]
    return [
        x["href"]
        for x in main_content.find_all("a", href=lambda x: x)
        if x["href"] != soups.snapshot.url
    ]


def parse_image_links(soups: Soups):
    return [
        x.get("data-src", x.get("src", x.get("data-original", "")))
        for x in soups.summary.find_all("img")
    ]


def parse_comment(i, item):
    text = item.find(class_="push-content").text
    text = text[len(": ") :]

    ipdatetime = item.find(class_="push-ipdatetime").text.strip()
    m = ip_pattern.search(ipdatetime)

    connect_from = m.group(1) if m is not None else None
    published_at = ipdatetime[m.end(1) :].strip() if m is not None else ipdatetime

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


def parse_publication(soups: Soups):
    stash = {}
    stash["title"] = soups.body.find("h1").text
    m = re.search(r"M.(\d+).", soups.snapshot.url)
    if m is None:
        stash["published_at"] = None
    else:
        stash["published_at"] = int(m.group(1))

    header_table = soups.body.find("table", {"class": "head-tbl"})
    for row in header_table.find_all("tr"):
        tag = row.find("th").text.strip()
        value = row.find("td").text.strip()
        if tag == "作者":
            stash["author"] = value
            break

    content = soups.body.select("#main-content")[0]
    text = []
    connect_from = None
    for c in content.children:
        line = c
        if isinstance(c, bs4.element.Tag):
            line = c.text
            class_attr = c.attrs.get("class")
            if class_attr and "push" in class_attr:
                break

        if line.find("◆ From: ") == 0:
            connect_from = line[len("◆ From: ") :]
            break
        elif line.find("※ 發信站: 批踢踢實業坊(ptt.cc), 來自: ") == 0:
            m = ip_pattern.search(line)
            connect_from = m.group(1) if m is not None else None
            break
        else:
            text.append(line)

    publication_text = "".join(text)
    external_links = parse_external_links(soups)
    image_links = parse_image_links(soups)

    comments = [
        parse_comment(i, item)
        for i, item in enumerate(soups.body.select("#main-content .push"))
    ]

    ga_id = parse_ga_id(soups)

    return {
        "version": soups.snapshot.snapshot_at,
        "site_id": soups.snapshot.site_id,
        "canonical_url": soups.snapshot.url,
        "published_at": stash["published_at"],
        "first_seen_at": soups.snapshot.first_seen_at,
        "last_updated_at": soups.snapshot.last_updated_at,
        "title": stash["title"],
        "publication_text": publication_text,
        "author": stash["author"],
        "connect_from": connect_from,
        "data": {
            "urls": external_links,
            "image_urls": image_links,
            "hashtags": [],
            "keywords": [],
            "tags": [],
            "metadata": {"metatags": soups.metatags, **soups.metadata, "ga-id": ga_id},
            "comments": comments,
        },
    }
