-- :name get_producers :many
SELECT
  producer_id, name, classification, url, first_seen_at, last_updated_at, identifiers
FROM producer
