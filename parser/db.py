import pugsql
import os


def parser():
    db = pugsql.module("queries/parser")
    db.connect(os.getenv("DB_URL"))
    return db
