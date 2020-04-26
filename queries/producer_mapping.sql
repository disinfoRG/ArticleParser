-- :name get_producer_id_from_sit_id :one
SELECT
  HEX(producer_id) AS producer_id
FROM producer_mapping
WHERE
  site_id = :site_id

-- :name upsert_producer_mapping :insert
INSERT INTO producer_mapping
  (site_id, producer_id, info, scraper_id)
VALUES
  (:site_id, UNHEX(:producer_id), :info, :scraper_id)
ON DUPLICATE KEY UPDATE
  info = :info
