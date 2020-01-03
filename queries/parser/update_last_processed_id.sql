-- :name update_last_processed
UPDATE parser_info
SET info = JSON_SET(
  JSON_SET(info, "$.last_processed_article_id", :last_processed_article_id),
  "$.last_processed_snapshot_at", :last_processed_snapshot_at)
WHERE parser_name = :parser_name

