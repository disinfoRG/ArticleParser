from invoke import task
from sys import platform


@task
def check(c):
    c.run("mypy .")


@task
def test(c):
    c.run("python -m unittest")
