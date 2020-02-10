import pugsql
import os


def scrapper():
    db = pugsql.module("queries/scrapper")
    db.connect(os.getenv("SCRAPPER_DB_URL"))
    return db


def parser():
    db = pugsql.module("queries/parser")
    db.connect(os.getenv("DB_URL"))
    return db
