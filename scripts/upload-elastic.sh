#!/bin/bash
PROCESSED_AT=${1:-$(date --date="yesterday" '+%Y-%m-%d')}

for PRODUCER_ID in $(./ap-producer.py list | tail -n +3 | sed 's/  .*//'); do
  ./ap-datapublish.py publication --full-text --producer ${PRODUCER_ID} --processed-at ${PROCESSED_AT} | scripts/to_elastic.py | curl -X POST -H "Content-Type: application/json" --data-binary "@-" "${SEARCH_URL}/_bulk?pretty"
done
