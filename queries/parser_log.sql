-- :name upsert_parser_log :insert
REPLACE parser_log
  (scraper_id, article_id, snapshot_at, data)
VALUES
  (:scraper_id, :article_id, :snapshot_at, :data)
