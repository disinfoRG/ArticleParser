-- :name upsert_producer :insert
INSERT INTO producer
  (producer_id, name, classification, url, languages, licenses, followership, identifiers)
VALUES
  (:producer_id, :name, :classification, :url, :languages, :licenses, :followership, :identifiers)
ON DUPLICATE KEY UPDATE
  producer_id = LAST_INSERT_ID(producer_id), name = :name, classification = :classification, url = :url, identifiers = :identifiers
