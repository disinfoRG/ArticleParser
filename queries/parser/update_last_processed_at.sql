-- :name update_last_processed_at
UPDATE parser_info
SET info = JSON_SET(info, "$.last_processed_at", :last_processed_at)
WHERE parser_name = :parser_name
