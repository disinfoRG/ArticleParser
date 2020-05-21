-- :name insert_parser_log :insert
INSERT INTO parser_log
  (scraper_id, article_id, snapshot_at, data)
VALUES
  (:scraper_id, :article_id, :snapshot_at, :data)
