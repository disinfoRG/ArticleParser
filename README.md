
# ArticleParser

### Running

We use MySQL.  To setup database connections:

1. Copy `.env.default` to `.env`, and set `DB_URL` value.  Start the MySQl connection string with `mysql+pymysql://` so that sqlalchemy uses the correct driver.

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
$ python parser/producer_parser.py
$ python parser/publication_parser.py
$ python publisher/export.py
```

This is currently a one-shot process: there is no tracking of entity IDs and you have to truncate the parser database every time before you run it.

## Development

We use Python 3.7.  Install Python dependencies with pipenv:

```sh
$ pip install pipenv
$ pipenv install --dev
$ pipenv shell

# install pre-commit hooks before hacking for the first time
$ pre-commit install
```
