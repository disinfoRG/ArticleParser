import pugsql
import os


def scraper():
    db = pugsql.module("queries/scraper")
    db.connect(os.getenv("SCRAPER_DB_URL"))
    return db


def parser():
    db = pugsql.module("queries/parser")
    db.connect(os.getenv("DB_URL"))
    return db
