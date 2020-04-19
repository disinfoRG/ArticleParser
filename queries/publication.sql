-- :name get_publications :many
SELECT
  HEX(publication_id) AS publication_id,
  version,
  HEX(producer_id) AS producer_id,
  canonical_url, title, publication_text, language, license,
  published_at, first_seen_at, last_updated_at,
  hashtags, urls, keywords, tags, metadata, comments,
  author, connect_from
FROM publication
LIMIT :limit
OFFSET :offset

-- :name get_publications_ranged_by_published_at :many
SELECT
  HEX(publication_id) AS publication_id,
  version,
  HEX(producer_id) AS producer_id,
  canonical_url, title, publication_text, language, license,
  published_at, first_seen_at, last_updated_at,
  hashtags, urls, keywords, tags, metadata, comments,
  author, connect_from
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
  canonical_url, title, publication_text, language, license,
  published_at, first_seen_at, last_updated_at,
  hashtags, urls, keywords, tags, metadata, comments,
  author, connect_from
FROM publication
WHERE
  producer_id = UNHEX(:producer_id)
  AND published_at BETWEEN :start AND :end
LIMIT :limit
OFFSET :offset

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
  canonical_url, title, publication_text, language, license,
  published_at, first_seen_at, last_updated_at,
  hashtags, urls, keywords, tags, metadata, comments,
  author, connect_from
FROM publication_mapping as PM
  JOIN publication as P
  ON PM.publication_id = P.publication_id AND PM.version = P.version
WHERE PM.article_id = :article_id
ORDER BY P.version ASC

-- :name get_publication_id_by_article_id :one
SELECT DISTINCT(HEX(publication_id))
FROM publication_mapping
WHERE article_id = UNHEX(:article_id)

-- :name insert_publication :insert
INSERT INTO publication
  (publication_id, producer_id, canonical_url, title, publication_text, published_at, first_seen_at, last_updated_at, urls, hashtags, keywords, tags, metadata, comments, version, author, connect_from)
VALUES
  (UNHEX(:publication_id), UNHEX(:producer_id), :canonical_url, :title, :publication_text, :published_at, :first_seen_at, :last_updated_at, :urls, :hashtags, :keywords, :tags, :metadata, :comments, :version, :author, :connect_from)

-- :name update_publication :affected
UPDATE publication
SET
  canonical_url = :canonical_url, title = :title, publication_text = :publication_text, published_at = :published_at, first_seen_at = :first_seen_at, last_updated_at = :last_updated_at, urls = :urls, hashtags = :hashtags, keywords = :keywords, tags = :tags, metadata = :metadata, comments = :comments, author = :author, connect_from = :connect_from
WHERE
  publication_id = UNHEX(:publication_id) AND version = :version
