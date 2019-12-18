from dotenv import load_dotenv

load_dotenv()

import os
import pugsql
import json
import datetime

queries = pugsql.module("queries/parser")
queries.connect(os.getenv("DB_URL"))


def rename_col(d, oldname, newname):
    d[newname] = d[oldname]
    del d[oldname]
    return d


def export_producers():

    producers = queries.get_all_producers()

    def process_producers(rows):
        def process(producer):
            rename_col(producer, "producer_id", "id")
            for json_col in ["languages", "licenses", "followership"]:
                producer.update({json_col: json.loads(producer[json_col])})
            for datetime_col in ["first_seen_at", "last_updated_at"]:
                producer.update(
                    {
                        datetime_col: datetime.datetime.fromtimestamp(
                            producer[datetime_col]
                        ).isoformat()
                    }
                )
            return producer

        for p in rows:
            yield process(p)

    producers_filename = "producers.json"

    with open(producers_filename, "w") as fp:
        json.dump(list(process_producers(producers)), fp)


def export_publications():
    publications = queries.get_all_publications()

    def process_publications(rows):
        def process(publication):
            rename_col(publication, "publication_id", "id")
            rename_col(publication, "publication_text", "text")
            for col in ["hashtags", "urls", "keywords", "tags"]:
                if publication[col] is not None:
                    publication.update({col: json.loads(publication[col])})
            for datetime_col in ["posted_at", "first_seen_at", "last_updated_at"]:
                if publication[datetime_col] is not None:
                    publication.update(
                        {
                            datetime_col: datetime.datetime.fromtimestamp(
                                publication[datetime_col]
                            ).isoformat()
                        }
                    )
            return publication

        for p in rows:
            yield process(p)

    publications_filename = "publications.json"

    with open(publications_filename, "w") as fp:
        json.dump(list(process_publications(publications)), fp)


if __name__ == "__main__":
    export_producers()
    export_publications()
