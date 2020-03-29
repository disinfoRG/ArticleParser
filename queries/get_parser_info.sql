-- :name get_parser_info :one
SELECT info
FROM parser_info
WHERE parser_name = :parser_name
