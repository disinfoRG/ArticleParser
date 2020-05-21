-- :name upsert_publication_map :insert
INSERT INTO publication_map
  (article_id, snapshot_at, publication_id, version, info, scraper_id)
VALUES
  (:article_id, :snapshot_at, UNHEX(:publication_id), :version, :info, :scraper_id)
ON DUPLICATE KEY UPDATE
  info = :info

-- :name get_publications_by_parser_version :many
SELECT
  scraper_id, article_id, snapshot_at, publication_id, version, info
FROM publication_map
WHERE
  JSON_EXTRACT(info, "$.parser.version") < :version
  -- XXX old version string
  OR JSON_EXTRACT(info, "$.parser.version") = "0.9.0"

-- :name get_publications_by_parser_version_by_producer :many
SELECT p0.scraper_id, p0.article_id, p0.snapshot_at, p0.publication_id, p0.version, p0.info
FROM publication_map AS p0
JOIN publication AS p1 ON p0.publication_id = p1.publication_id AND p0.version = p1.version
WHERE
  p1.producer_id = :producer_id
  AND
  (JSON_EXTRACT(info, "$.parser.version") < :version
  -- XXX old version string
  OR JSON_EXTRACT(info, "$.parser.version") = "0.9.0")

