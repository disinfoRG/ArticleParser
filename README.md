
# ArticleParser

### Running

We use MySQL.  To setup database connections:

1. Copy `.env.default` to `.env`, and set `DB_URL`, `SCRAPER_DB_URL` values.  Start the MySQl connection string with `mysql+pymysql://` so that sqlalchemy uses the correct driver.

We use Python 3.7.  Install Python dependencies and run database migrations:

```sh
$ pip install pipenv
$ pipenv install
# start a shell in virtual env
$ pipenv shell
# run db migrations
$ alembic upgrade head
```

Then

```sh
$ python ./parser.py producer
$ python ./parser.py --limit 1000 publication
```

You can run these commands multiple times to parse source data in batch.  `--limit <number>` sets the number of entries to parse for each batch.

You can now export the parsed data with

```sh
$ mkdir -p datasets/publications
$ python ./publish.py -f jsonl -o datasets/producers.jsonl producers
$ python ./publish.py -f jsonl -g published_day -o datasets/publications publications
```

## Development

We use Python 3.7.  Install Python dependencies with pipenv:

```sh
$ pip install pipenv
$ pipenv install --dev
$ pipenv shell

# install pre-commit hooks before hacking for the first time
$ pre-commit install
```
