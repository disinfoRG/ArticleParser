-- :name upsert_parser_log :insert
REPLACE parser_log
  (parser_name, created_at, scraper_id, article_id, snapshot_at, data)
VALUES
  (:parser_name, :created_at, :scraper_id, :article_id, :snapshot_at, :data)
