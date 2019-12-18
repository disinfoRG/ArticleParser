from dotenv import load_dotenv

load_dotenv()

import os
import pugsql
from bs4 import BeautifulSoup
from readability import Document
from datetime import datetime
import logging
import jsonlines
import json

# todo:
#   extract meta?
#   logging problem

scrapper_db = pugsql.module("queries/scrapper")
scrapper_db.connect(os.getenv("SCRAPPER_DB_URL"))
parser_db = pugsql.module("queries/parser")
parser_db.connect(os.getenv("DB_URL"))


class CleanHTML:
    def __init__(self, snapshot_infos):
        self.snapshot_infos = snapshot_infos

    @staticmethod
    def clean(sn):
        doc = Document(sn["raw_data"])
        # title
        title = doc.title()

        # main body
        s = doc.summary()
        soup = BeautifulSoup(s, "html.parser")

        # date - not 100% accurate
        # guess_date = htmldate.find_date(self.raw_data)

        # article text
        text = "\n".join([" ".join(x.text.split()) for x in soup.find_all("p")])

        # links
        external_links = [x["href"] for x in soup.find_all("a", href=lambda x: x)]
        image_links = [x["data-src"] for x in soup.find_all("img")]

        return {
            "title": title,
            "publication_text": text,
            "urls": json.dumps(external_links),
            "image_urls": json.dumps(image_links),
        }

    def save(self, x):
        # to elastic search
        # r = requests.post(f"{es_url}/{index}", data=json.dumps(x))
        parser_db.create_publication(x)

    def run(self):
        current_time_str = datetime.now().strftime("%Y-%m-%dT%H:%M%S")
        logging.basicConfig(
            filename=f".log/parser_{current_time_str}.log",
            format="%(asctime)s - %(message)s",
            level=logging.INFO,
        )
        for one_snapshot_info in self.snapshot_infos:
            try:
                parsed_content = self.clean(one_snapshot_info)
            except:
                logging.error(
                    f"{str(one_snapshot_info['article_id'])}-{str(one_snapshot_info['snapshot_at'])} "
                    f"parsing failed"
                )
            else:
                content_to_save = {
                    "publication_id": one_snapshot_info["article_id"],
                    "producer_id": one_snapshot_info["site_id"],
                    "canonical_url": one_snapshot_info["url"],
                    **parsed_content,
                }
                self.save(content_to_save)


if __name__ == "__main__":
    snapshot_infos = list(scrapper_db.get_all_article_snapshots())[-20:]
    clean = CleanHTML(snapshot_infos)
    clean.run()
