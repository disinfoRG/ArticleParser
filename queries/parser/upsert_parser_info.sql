-- :name upsert_parser_info :insert
INSERT INTO parser_info
  (parser_name, info)
VALUES
  (:parser_name, :info)
ON DUPLICATE KEY UPDATE
  info = :info
