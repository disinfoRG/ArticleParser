-- :name create_ignore_parser_info :insert
INSERT IGNORE INTO parser_info
  (parser_name, info)
VALUES
  (:parser_name, :info)
