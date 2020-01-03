-- :name upsert_producer :insert
INSERT INTO producer
  (producer_id, name, classification, canonical_url, languages, licenses, followership)
VALUES
  (:producer_id, :name, :classification, :canonical_url, :languages, :licenses, :followership)
ON DUPLICATE KEY UPDATE
  producer_id = LAST_INSERT_ID(producer_id), name = :name, classification = :classification, canonical_url = :canonical_url
