-- :name get_producer_by_id :one
SELECT
  producer_id, name, classification, url, first_seen_at, last_updated_at, identifiers
FROM producer
WHERE producer_id = :producer_id

-- :name get_producer_by_id_with_stats :one
SELECT
  producer_id, name, classification, url, first_seen_at, last_updated_at, identifiers,
  (SELECT COUNT(*) FROM publication WHERE producer_id = :producer_id) AS publication_count
FROM producer
WHERE producer_id = :producer_id
