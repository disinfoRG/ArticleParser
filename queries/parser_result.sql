-- :name save_parser_result :insert
REPLACE parser_result
  (parser_name, created_at, scraper_id, article_id, snapshot_at, data)
VALUES
  (:parser_name, :created_at, :scraper_id, :article_id, :snapshot_at, :data)
