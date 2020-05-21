-- :name get_producers :many
SELECT
  HEX(producer.producer_id) AS producer_id,
  name, classification, url, first_seen_at, last_updated_at, data,
  scraper_id, site_id
FROM producer
JOIN producer_map ON producer.producer_id = producer_map.producer_id

-- :name get_producer :one
SELECT
  HEX(producer.producer_id) AS producer_id,
  name, classification, url, first_seen_at, last_updated_at, data,
  scraper_id, site_id
FROM producer
JOIN producer_map ON producer.producer_id = producer_map.producer_id
WHERE producer.producer_id = UNHEX(:producer_id)

-- :name get_producer_by_site_id :one
SELECT
  HEX(producer.producer_id) AS producer_id,
  name, classification, url, first_seen_at, last_updated_at, data,
  scraper_id, site_id
FROM producer
JOIN producer_map ON producer.producer_id = producer_map.producer_id
WHERE producer_map.site_id = :site_id

-- :name get_producer_with_stats :one
SELECT
  HEX(producer.producer_id) AS producer_id,
  name, classification, url, first_seen_at, last_updated_at, data,
  scraper_id, site_id,
  (SELECT COUNT(*) FROM publication WHERE producer_id = UNHEX(:producer_id)) AS publication_count
FROM producer
JOIN producer_map ON producer.producer_id = producer_map.producer_id
WHERE producer.producer_id = UNHEX(:producer_id)

-- :name insert_producer :insert
INSERT INTO producer
  (producer_id, name, classification, url, data)
VALUES
  (UNHEX(REPLACE(:producer_id, '-', '')), :name, :classification, :url, :data)

-- :name update_producer :affected
UPDATE producer
SET
  name = :name,
  classification = :classification,
  url = :url
WHERE producer_id = UNHEX(:producer_id)

-- :name update_producer_identifiers :affected
-- UPDATE producer
-- SET
--   identifiers = :identifiers
-- WHERE producer_id = UNHEX(:producer_id)

-- :name update_producer_active_dates :affected
UPDATE producer
SET
  first_seen_at = LEAST(COALESCE(first_seen_at, :published_at), :published_at),
  last_updated_at = GREATEST(COALESCE(last_updated_at, :published_at), :published_at)
WHERE producer_id = UNHEX(:producer_id)
