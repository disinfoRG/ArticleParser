-- :name get_publications :many
SELECT
  HEX(publication_id) AS publication_id,
  version,
  HEX(producer_id) AS producer_id,
  canonical_url, title, publication_text, author, connect_from,
  published_at, first_seen_at, last_updated_at,
  data
FROM publication
LIMIT :limit
OFFSET :offset

-- :name get_publications_ranged_by_published_at :many
SELECT
  HEX(publication_id) AS publication_id,
  version,
  HEX(producer_id) AS producer_id,
  canonical_url, title, publication_text, author, connect_from,
  published_at, first_seen_at, last_updated_at,
  data
FROM publication
WHERE
  published_at BETWEEN :start AND :end
LIMIT :limit
OFFSET :offset

-- :name get_publications_by_producer_ranged_by_published_at :many
SELECT
  HEX(publication_id) AS publication_id,
  version,
  HEX(producer_id) AS producer_id,
  canonical_url, title, publication_text, author, connect_from,
  published_at, first_seen_at, last_updated_at,
  data
FROM publication
WHERE
  producer_id = UNHEX(:producer_id)
  AND published_at BETWEEN :start AND :end
LIMIT :limit
OFFSET :offset

-- :name get_publications_by_producer_ranged_by_processed_at :many
SELECT
  HEX(P.publication_id) AS publication_id,
  P.version AS version,
  HEX(producer_id) AS producer_id,
  canonical_url, title, publication_text, author, connect_from,
  published_at, first_seen_at, last_updated_at,
  data
FROM publication_mapping as PM
  JOIN publication as P
  ON PM.publication_id = P.publication_id AND PM.version = P.version
WHERE
  P.producer_id = UNHEX(:producer_id)
  AND JSON_EXTRACT(PM.info, "$.last_processed_at") BETWEEN :start AND :end
LIMIT :limit
OFFSET :offset

-- :name get_published_date_by_producer_ranged_by_processed_at :many
SELECT
  DISTINCT(DATE(FROM_UNIXTIME(P.published_at))) AS published_date
FROM publication_mapping as PM
  JOIN publication as P
  ON PM.publication_id = P.publication_id AND PM.version = P.version
WHERE
  P.producer_id = UNHEX(:producer_id)
  AND JSON_EXTRACT(PM.info, "$.last_processed_at") BETWEEN :start AND :end

-- :name get_publications_by_producer_published_at :many
SELECT
  HEX(publication_id) AS publication_id,
  version,
  HEX(producer_id) AS producer_id,
  canonical_url, title, publication_text, author, connect_from,
  published_at, first_seen_at, last_updated_at,
  data
FROM publication
WHERE
  producer_id = UNHEX(:producer_id)
  AND published_at BETWEEN :published_at AND (:published_at + 86399)

-- :name get_publication_published_at_range :one
SELECT
  MIN(published_at) as start, MAX(published_at) as end
FROM publication

-- :name get_publication_published_at_range_by_producer :one
SELECT
  MIN(published_at) as start, MAX(published_at) as end
FROM publication
WHERE
  producer_id = UNHEX(:producer_id)

-- :name get_publication_by_article_id :many
SELECT
  HEX(P.publication_id) AS publication_id,
  P.version AS version,
  HEX(producer_id) AS producer_id,
  canonical_url, title, publication_text, author, connect_from,
  published_at, first_seen_at, last_updated_at,
  data
FROM publication_mapping as PM
  JOIN publication as P
  ON PM.publication_id = P.publication_id AND PM.version = P.version
WHERE PM.article_id = :article_id
ORDER BY P.version ASC

-- :name get_publication_id_by_article_id :one
SELECT DISTINCT(HEX(publication_id)) AS publication_id
FROM publication_mapping
WHERE article_id = :article_id

-- :name insert_publication :insert
INSERT INTO publication
  (publication_id, version, producer_id, canonical_url, title, publication_text, published_at, first_seen_at, last_updated_at, author, connect_from, data)
VALUES
  (UNHEX(:publication_id), :version, UNHEX(:producer_id), :canonical_url, :title, :publication_text, :published_at, :first_seen_at, :last_updated_at, :author, :connect_from, :data)

-- :name update_publication :affected
UPDATE publication
SET
  canonical_url = :canonical_url, title = :title, publication_text = :publication_text, published_at = :published_at, first_seen_at = :first_seen_at, last_updated_at = :last_updated_at, author = :author, connect_from = :connect_from, data = :data
WHERE
  publication_id = UNHEX(:publication_id) AND version = :version
