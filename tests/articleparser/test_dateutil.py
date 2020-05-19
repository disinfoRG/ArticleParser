import pytest
from articleparser.dateutil import *


def test_parserdate():
    assert parsedate("2020-11-10").day == 10
    assert parsedate("2020-11-10T09:08:07").day == 10
    assert parsedate("2020.11.10").day == 10


def test_parserdatetime():
    assert parsedatetime("2020-11-10").hour == 0
    assert parsedatetime("2020-11-10T09:08:07").hour == 9


if __name__ == "__main__":
    pytest.main([__file__])
