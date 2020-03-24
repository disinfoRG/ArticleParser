#!/usr/bin/env python3

from dotenv import load_dotenv

load_dotenv()

import os
import sys
import pathlib
import subprocess


def try_subcommands(skip_commands=[]):
    """
    Try passing subcommand `cmd` to `ap-cmd`.
    """
    if len(sys.argv) > 1 and sys.argv[1] not in skip_commands:
        binname = pathlib.Path(__file__)
        sub_cmd = (
            binname.parent.resolve() / f"{binname.stem}-{sys.argv[1]}{binname.suffix}"
        )
        try:
            sys.exit(subprocess.run([sub_cmd, *sys.argv[2:]]).returncode)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    try_subcommands()

    print("Usage: ap <command>")
    sys.exit(-1)
