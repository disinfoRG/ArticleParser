#!/bin/bash

#curl -X DELETE ${SEARCH_URL}
#curl -X PUT -H "Content-Type: application/json" "${SEARCH_URL}"
curl -X PUT -H "Content-Type: application/json" "${SEARCH_URL}/_mapping/publication?pretty" -d'
{
  "properties": {
    "id": { "type": "string", "index": "not_analyzed" },
    "version": { "type": "integer" },
    "producer_id": { "type": "string", "index": "not_analyzed" },
    "canonical_url": { "type": "string", "index": "not_analyzed" },
    "title": { "type": "string", "analyzer": "smartcn" },
    "published_at": { "type": "date" },
    "first_seen_at": { "type": "date" },
    "last_updated_at": { "type": "date" },
    "author": { "type": "string", "index": "not_analyzed" },
    "connect_from": { "type": "ip" },
    "text": { "type": "string", "analyzer": "smartcn" },
    "hashtags": { "type": "string", "index": "not_analyzed" },
    "urls": { "type": "string", "index": "not_analyzed" },
    "keywords": { "type": "string", "index": "not_analyzed" },
    "tags": { "type": "string", "index": "not_analyzed" },
    "comments": {
      "type": "nested",
      "properties": {
        "id": { "type": "string", "index": "not_analyzed" },
        "reaction": { "type": "string", "index": "not_analyzed" },
        "author": { "type": "string", "index": "not_analyzed" },
        "text": { "type": "string", "analyzer": "smartcn" },
        "connect_from": { "type": "ip" }
      }
    }
  }
}
'
#curl -X GET "${SEARCH_URL}/_mapping?pretty"
