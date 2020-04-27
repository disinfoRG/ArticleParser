#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()
import os
import sys
import json
import re

m = re.compile("\/([^:\/]+)(:\d+)?$").search(os.getenv("SEARCH_URL"))
if m is None:
    print("Unrecognized SEARCH_URL")
    sys.exit(-1)
index = m.group(1)
for line in sys.stdin:
    data = json.loads(line)
    print(
        json.dumps(
            {"index": {"_index": index, "_type": "publication", "_id": data["id"]}}
        )
    )
    del data["metadata"]
    print(json.dumps(data, ensure_ascii=False))
