#!/bin/bash

INDEX=publication

curl -X PUT "${SEARCH_URL}/${INDEX}"
curl -X POST -H "Content-Type: application/json" "${SEARCH_URL}/${INDEX}/_mapping?pretty" -d'
{
  "properties": {
    "id": { "type": "keyword" },
    "producer_id": { "type": "keyword" },
    "canonical_url": { "type": "keyword" },
    "title": { "type": "text", "analyzer": "smartcn" },
    "language": { "type": "keyword" },
    "license": { "type": "keyword" },
    "published_at": { "type": "date" },
    "first_seen_at": { "type": "date" },
    "last_updated_at": { "type": "date" },
    "hashtags": { "type": "keyword" },
    "urls": { "type": "keyword" },
    "keywords": { "type": "keyword" },
    "comments": {
      "type": "nested",
      "properties": {
        "id": { "type": "keyword" },
        "reaction": { "type": "keyword" },
        "author": { "type": "keyword" },
        "text": { "type": "text", "analyzer": "smartcn" },
        "connect_from": { "type": "ip" }
      }
    },
    "version": { "type": "integer" },
    "author": { "type": "keyword" },
    "connect_from": { "type": "ip" },
    "text": { "type": "text", "analyzer": "smartcn" }
  }
}
'
curl -X GET "${SEARCH_URL}/${INDEX}/_mapping?pretty"
