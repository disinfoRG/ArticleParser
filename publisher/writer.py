import csv
import jsonlines
import sys


class BaseWriter:
    def __init__(self, filename):
        self.fh = None
        self.filename = filename

    def to_stdout(self):
        return self.filename == "-"

    def open(self):
        if self.fh is not None:
            return
        if self.to_stdout():
            self.fh = sys.stdout
        else:
            self.fh = open(self.filename, "w")

    def close(self):
        if not self.to_stdout() and self.fh is not None:
            self.fh.close()


class CSV(BaseWriter):
    def __init__(self, fieldnames=[], filename="-"):
        super(CSV, self).__init__(filename)
        self.fieldnames = fieldnames
        self.writer = None

    def open(self):
        super(CSV, self).open()
        self.writer = csv.DictWriter(self.fh, self.fieldnames)
        self.writer.writeheader()

    def write(self, rows):
        self.writer.writerows(rows)


class JSONLines(BaseWriter):
    def __init__(self, filename="-"):
        super(JSONLines, self).__init__(filename)
        self.writer = None

    def open(self):
        super(JSONLines, self).open()
        self.writer = jsonlines.Writer(self.fh)

    def write(self, rows):
        self.writer.write_all(rows)


def fromformat(fmt, **args):
    if fmt == "jsonl":
        return JSONLines(filename=args["filename"])
    elif fmt == "csv":
        return CSV(filename=args["filename"], fieldnames=args["fieldnames"])
    else:
        raise f"Unknown format '{fmt}'"
