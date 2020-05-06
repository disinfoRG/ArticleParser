"""
Various enhancements to the standard `datetime` module.
"""
from datetime import *
import calendar
import re


def day_start(day: date) -> datetime:
    return datetime.combine(day, datetime.min.time())


def day_end(day: date) -> datetime:
    return datetime.combine(day, datetime.max.time())


class DateRange:
    """
    A range of dates
    """

    start: date
    end: date

    def __init__(self, start: date, end: date):
        self.start = start
        self.end = end

    def __repr__(self):
        return "DateRange(%s, %s)" % (repr(self.start), repr(self.end))

    def start_datetime(self):
        return day_start(self.start)

    def start_timestamp(self):
        return self.start_datetime().timestamp()

    def end_datetime(self):
        return day_end(self.end)

    def end_timestamp(self):
        return self.end_datetime().timestamp()

    def iterdate(self, step_days=1):
        step = timedelta(days=step_days)
        day = self.start
        while day <= self.end:
            yield day
            day = day + step


class Month(DateRange):
    isoformat_pat = re.compile("^(\d{4})-(\d{2})$")

    def __init__(self, year: int, month: int):
        self.start = date(year=year, month=month, day=1)
        self.end = self.start + timedelta(days=calendar.monthrange(year, month)[1] - 1)

    def __repr__(self):
        return "Month(%s, %s)" % (self.start.year, self.start.month)

    @classmethod
    def fromisoformat(cls, value):
        m = cls.isoformat_pat.match(value)
        if m is None:
            raise ValueError(f"unknown month format {value}")
        return Month(year=int(m.group(1)), month=int(m.group(2)))

    def isoformat(self):
        return "%04d-%02d" % (self.start.year, self.start.month)
