#!/bin/bash

python3 scripts/to_elastic.py | curl -X POST -H "Content-Type: application/json" --data-binary "@-" "${SEARCH_URL}/_bulk?pretty"
