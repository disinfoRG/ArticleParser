-- :name upsert_producer_mapping :insert
INSERT INTO producer_mapping
  (site_id, producer_id, info)
VALUES
  (:site_id, :producer_id, :info)
ON DUPLICATE KEY UPDATE
  site_id = LAST_INSERT_ID(site_id), producer_id = :producer_id, info = :info

