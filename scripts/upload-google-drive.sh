#!/bin/bash
DATE=${1:-"yesterday"}
PROCESSED_AT=$(date --date=$DATE '+%Y-%m-%d')

for PRODUCER_ID in $(./ap-producer.py list | tail -n +3 | sed 's/  .*//'); do
  ./ap-datapublish.py publication --full-text --producer ${PRODUCER_ID} --processed-at ${PROCESSED_AT} --drive fulltext --service-account service.json
  ./ap-datapublish.py publication --producer ${PRODUCER_ID} --processed-at ${PROCESSED_AT} --drive public --service-account service.json
done

