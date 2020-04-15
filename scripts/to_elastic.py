#!/usr/bin/env python

import sys
import json

for line in sys.stdin:
    data = json.loads(line)
    print(json.dumps({"index": {"_index": "publication", "_id": data["id"]}}))
    print(line)
