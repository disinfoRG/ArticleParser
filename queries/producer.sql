-- :name get_producers_in_batch :many
SELECT
  HEX(producer_id) AS producer_id,
  name, classification, url, first_seen_at, last_updated_at, languages, licenses, followership, identifiers
FROM producer
LIMIT :limit
OFFSET :offset

-- :name get_producers :many
SELECT
  HEX(producer.producer_id) AS producer_id,
  producer_mapping.site_id AS site_id,
  name, classification, url, first_seen_at, last_updated_at, identifiers
FROM producer
JOIN producer_mapping ON producer.producer_id = producer_mapping.producer_id

-- :name get_producer :one
SELECT
  HEX(producer.producer_id) AS producer_id,
  producer_mapping.site_id AS site_id,
  name, classification, url, first_seen_at, last_updated_at, identifiers
FROM producer
JOIN producer_mapping ON producer.producer_id = producer_mapping.producer_id
WHERE producer.producer_id = UNHEX(:producer_id)

-- :name get_producer_by_site_id :one
SELECT
  HEX(producer.producer_id) AS producer_id,
  producer_mapping.site_id AS site_id,
  name, classification, url, first_seen_at, last_updated_at, identifiers
FROM producer
JOIN producer_mapping ON producer.producer_id = producer_mapping.producer_id
WHERE producer_mapping.site_id = :site_id

-- :name get_producer_with_stats :one
SELECT
  HEX(producer.producer_id) AS producer_id,
  producer_mapping.site_id AS site_id,
  name, classification, url, first_seen_at, last_updated_at, identifiers,
  (SELECT COUNT(*) FROM publication WHERE producer_id = :producer_id) AS publication_count
FROM producer
JOIN producer_mapping ON producer.producer_id = producer_mapping.producer_id
WHERE producer.producer_id = UNHEX(:producer_id)

-- :name insert_producer :insert
INSERT INTO producer
  (producer_id, name, classification, url, languages, licenses, followership, identifiers)
VALUES
  (UNHEX(REPLACE(:producer_id, '-', '')), :name, :classification, :url, :languages, :licenses, :followership, :identifiers)

-- :name update_producer :affected
UPDATE producer
SET
  name = :name,
  classification = :classification,
  url = :url
WHERE producer_id = UNHEX(:producer_id)

-- :name update_producer_identifiers :affected
UPDATE producer
SET
  identifiers = :identifiers
WHERE producer_id = UNHEX(:producer_id)

-- :name update_producer_active_dates :affected
UPDATE producer
SET
  first_seen_at = LEAST(COALESCE(first_seen_at, :published_at), :published_at),
  last_updated_at = GREATEST(COALESCE(last_updated_at, :published_at), :published_at)
WHERE producer_id = UNHEX(:producer_id)
