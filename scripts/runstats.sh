#!/bin/bash
DATE=${1:-"yesterday"}
PROCESSED_AT=$(date --date=$DATE '+%Y-%m-%d')

./ap-runstats.py --processed-at ${PROCESSED_AT}
